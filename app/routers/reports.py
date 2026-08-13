from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Feedback, MaintenanceReport, ReportStatus
from app.schemas import (
    DashboardSummary,
    FeedbackCreate,
    FeedbackResponse,
    ReportCreate,
    ReportDetail,
    ReportResponse,
    StatusUpdate,
)
from app.services.report_service import calculate_priority, can_transition, find_recent_duplicate

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_report_or_404(db: Session, report_id: int) -> MaintenanceReport:
    statement = (
        select(MaintenanceReport)
        .options(selectinload(MaintenanceReport.updates), selectinload(MaintenanceReport.feedback))
        .where(MaintenanceReport.id == report_id)
    )
    report = db.scalar(statement)
    if not report:
        raise HTTPException(status_code=404, detail={"code": "REPORT_NOT_FOUND", "message": "Report not found."})
    return report


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, db: Session = Depends(get_db)) -> MaintenanceReport:
    duplicate = find_recent_duplicate(db, payload.location, payload.category)
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "DUPLICATE_REPORT",
                "message": f"A similar open report already exists: {duplicate.reference}.",
            },
        )

    score, label = calculate_priority(payload.urgency, payload.safety_risk, payload.affects_multiple_people)
    report = MaintenanceReport(
        reference=f"RL-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')[-12:]}",
        priority_score=score,
        priority_label=label,
        **payload.model_dump(),
    )
    db.add(report)
    db.flush()
    from app.models import ReportUpdate

    db.add(ReportUpdate(report_id=report.id, new_status=ReportStatus.SUBMITTED, note="Report submitted by student."))
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=list[ReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    status_filter: ReportStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[MaintenanceReport]:
    statement = select(MaintenanceReport).order_by(MaintenanceReport.created_at.desc()).limit(limit)
    if status_filter:
        statement = statement.where(MaintenanceReport.status == status_filter)
    return list(db.scalars(statement).all())


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(report_id: int, db: Session = Depends(get_db)) -> MaintenanceReport:
    return get_report_or_404(db, report_id)


@router.patch("/{report_id}/status", response_model=ReportResponse)
def update_status(report_id: int, payload: StatusUpdate, db: Session = Depends(get_db)) -> MaintenanceReport:
    report = get_report_or_404(db, report_id)
    if not can_transition(report.status, payload.status):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_STATUS_TRANSITION",
                "message": f"Cannot move a report from {report.status.value} to {payload.status.value}.",
            },
        )

    from app.models import ReportUpdate

    previous = report.status
    report.status = payload.status
    if payload.status == ReportStatus.RESOLVED:
        report.resolved_at = datetime.now(UTC).replace(tzinfo=None)
    elif payload.status == ReportStatus.REOPENED:
        report.resolved_at = None
    db.add(ReportUpdate(report_id=report.id, previous_status=previous, new_status=payload.status, note=payload.note))
    db.commit()
    db.refresh(report)
    return report


@router.post("/{report_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def add_feedback(report_id: int, payload: FeedbackCreate, db: Session = Depends(get_db)) -> Feedback:
    report = get_report_or_404(db, report_id)
    if report.status != ReportStatus.RESOLVED:
        raise HTTPException(status_code=422, detail={"code": "REPORT_NOT_RESOLVED", "message": "Feedback can be added only after resolution."})
    if report.feedback:
        raise HTTPException(status_code=409, detail={"code": "FEEDBACK_EXISTS", "message": "Feedback already exists for this report."})
    feedback = Feedback(report_id=report.id, **payload.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.post("/{report_id}/reopen", response_model=ReportResponse)
def reopen_report(report_id: int, db: Session = Depends(get_db)) -> MaintenanceReport:
    return update_status(report_id, StatusUpdate(status=ReportStatus.REOPENED, note="Student reported that the issue remains unresolved."), db)


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    total = db.scalar(select(func.count(MaintenanceReport.id))) or 0
    resolved = db.scalar(select(func.count(MaintenanceReport.id)).where(MaintenanceReport.status == ReportStatus.RESOLVED)) or 0
    reopened = db.scalar(select(func.count(MaintenanceReport.id)).where(MaintenanceReport.status == ReportStatus.REOPENED)) or 0
    average = db.scalar(select(func.avg(Feedback.rating)))
    return DashboardSummary(total_reports=total, open_reports=total - resolved, resolved_reports=resolved, reopened_reports=reopened, average_feedback_rating=round(float(average), 2) if average is not None else None)
