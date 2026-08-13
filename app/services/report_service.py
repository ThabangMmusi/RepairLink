from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MaintenanceReport, ReportCategory, ReportStatus, Urgency

URGENCY_POINTS = {
    Urgency.LOW: 1,
    Urgency.MEDIUM: 2,
    Urgency.HIGH: 3,
    Urgency.CRITICAL: 4,
}

ALLOWED_TRANSITIONS: dict[ReportStatus, set[ReportStatus]] = {
    ReportStatus.SUBMITTED: {ReportStatus.RECEIVED, ReportStatus.ASSIGNED, ReportStatus.IN_PROGRESS},
    ReportStatus.RECEIVED: {ReportStatus.ASSIGNED, ReportStatus.IN_PROGRESS},
    ReportStatus.ASSIGNED: {ReportStatus.IN_PROGRESS},
    ReportStatus.IN_PROGRESS: {ReportStatus.RESOLVED},
    ReportStatus.RESOLVED: {ReportStatus.REOPENED},
    ReportStatus.REOPENED: {ReportStatus.IN_PROGRESS, ReportStatus.RESOLVED},
}


def calculate_priority(urgency: Urgency, safety_risk: bool, affects_multiple_people: bool) -> tuple[int, str]:
    score = URGENCY_POINTS[urgency]
    score += 3 if safety_risk else 0
    score += 2 if affects_multiple_people else 0
    label = "critical" if score >= 7 else "high" if score >= 5 else "normal"
    return score, label


def find_recent_duplicate(db: Session, location: str, category: ReportCategory) -> MaintenanceReport | None:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=24)
    statement = (
        select(MaintenanceReport)
        .where(MaintenanceReport.location == location)
        .where(MaintenanceReport.category == category)
        .where(MaintenanceReport.created_at >= cutoff)
        .where(MaintenanceReport.status != ReportStatus.RESOLVED)
        .order_by(MaintenanceReport.created_at.desc())
    )
    return db.scalar(statement)


def can_transition(current: ReportStatus, target: ReportStatus) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())
