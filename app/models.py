from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReportCategory(StrEnum):
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FURNITURE = "furniture"
    SECURITY = "security"
    INTERNET = "internet"
    CLEANING = "cleaning"
    OTHER = "other"


class Urgency(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportStatus(StrEnum):
    SUBMITTED = "submitted"
    RECEIVED = "received"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REOPENED = "reopened"


class MaintenanceReport(Base):
    __tablename__ = "maintenance_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    location: Mapped[str] = mapped_column(String(160), index=True)
    category: Mapped[ReportCategory] = mapped_column(Enum(ReportCategory), index=True)
    description: Mapped[str] = mapped_column(Text)
    urgency: Mapped[Urgency] = mapped_column(Enum(Urgency), index=True)
    affects_multiple_people: Mapped[bool] = mapped_column(Boolean, default=False)
    safety_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    priority_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    priority_label: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.SUBMITTED, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    updates: Mapped[list["ReportUpdate"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    feedback: Mapped["Feedback | None"] = relationship(back_populates="report", cascade="all, delete-orphan", uselist=False)


class ReportUpdate(Base):
    __tablename__ = "report_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("maintenance_reports.id"), index=True)
    previous_status: Mapped[ReportStatus | None] = mapped_column(Enum(ReportStatus), nullable=True)
    new_status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus))
    note: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    report: Mapped[MaintenanceReport] = relationship(back_populates="updates")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("maintenance_reports.id"), unique=True, index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    report: Mapped[MaintenanceReport] = relationship(back_populates="feedback")
