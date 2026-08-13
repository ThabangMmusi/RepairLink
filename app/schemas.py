from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ReportCategory, ReportStatus, Urgency


class ReportCreate(BaseModel):
    location: str = Field(min_length=3, max_length=160)
    category: ReportCategory
    description: str = Field(min_length=20, max_length=2000)
    urgency: Urgency = Urgency.MEDIUM
    affects_multiple_people: bool = False
    safety_risk: bool = False


class StatusUpdate(BaseModel):
    status: ReportStatus
    note: str = Field(default="", max_length=500)


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=500)


class ReportUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    previous_status: ReportStatus | None
    new_status: ReportStatus
    note: str
    created_at: datetime


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rating: int
    comment: str
    created_at: datetime


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    location: str
    category: ReportCategory
    description: str
    urgency: Urgency
    affects_multiple_people: bool
    safety_risk: bool
    priority_score: int
    priority_label: str
    status: ReportStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class ReportDetail(ReportResponse):
    updates: list[ReportUpdateResponse] = []
    feedback: FeedbackResponse | None = None


class DashboardSummary(BaseModel):
    total_reports: int
    open_reports: int
    resolved_reports: int
    reopened_reports: int
    average_feedback_rating: float | None


class MessageResponse(BaseModel):
    message: str
