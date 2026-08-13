import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_report(**overrides):
    payload = {
        "location": "Off-Campus Residence - Block A",
        "category": "electrical",
        "description": "The corridor light is not working and students cannot see safely.",
        "urgency": "high",
        "affects_multiple_people": True,
        "safety_risk": True,
    }
    payload.update(overrides)
    return client.post("/api/reports", json=payload)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_report_calculates_priority():
    response = create_report()
    assert response.status_code == 201
    data = response.json()
    assert data["reference"].startswith("RL-")
    assert data["priority_label"] == "critical"
    assert data["status"] == "submitted"


def test_duplicate_report_is_rejected():
    assert create_report().status_code == 201
    response = create_report()
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "DUPLICATE_REPORT"


def test_invalid_status_transition_is_rejected():
    report = create_report().json()
    response = client.patch(f"/api/reports/{report['id']}/status", json={"status": "resolved"})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_STATUS_TRANSITION"


def test_report_can_be_resolved_reopened_and_rated():
    report = create_report().json()
    report_id = report["id"]
    for next_status in ("received", "assigned", "in_progress", "resolved"):
        response = client.patch(f"/api/reports/{report_id}/status", json={"status": next_status})
        assert response.status_code == 200
    feedback = client.post(f"/api/reports/{report_id}/feedback", json={"rating": 4, "comment": "Resolved correctly."})
    assert feedback.status_code == 201
    reopened = client.post(f"/api/reports/{report_id}/reopen")
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "reopened"


def test_dashboard_counts_reports():
    report = create_report().json()
    for next_status in ("received", "assigned", "in_progress", "resolved"):
        client.patch(f"/api/reports/{report['id']}/status", json={"status": next_status})
    response = client.get("/api/reports/dashboard/summary")
    assert response.status_code == 200
    assert response.json()["total_reports"] == 1
    assert response.json()["resolved_reports"] == 1


def test_short_description_is_rejected():
    response = create_report(description="Too short")
    assert response.status_code == 422


def test_missing_report_returns_structured_error():
    response = client.get("/api/reports/9999")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "REPORT_NOT_FOUND"
