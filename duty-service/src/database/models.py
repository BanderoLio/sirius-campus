from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
import enum
from src.database import Base


class DutyStatusEnum(str, enum.Enum):
    pending = "pending"
    active = "active"
    accepted = "accepted"
    overdue = "overdue"


class ReportStatusEnum(str, enum.Enum):
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"


class DutySchedule(Base):
    __tablename__ = "duty_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    room_id = Column(UUID(as_uuid=True), nullable=False)
    duty_date = Column(Date, nullable=False)
    assigned_by = Column(UUID(as_uuid=True), nullable=False)
    status = Column(SQLEnum(DutyStatusEnum), default=DutyStatusEnum.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    reports = relationship("DutyReport", back_populates="schedule", cascade="all, delete-orphan")


class DutyReport(Base):
    __tablename__ = "duty_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("duty_schedules.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(SQLEnum(ReportStatusEnum), default=ReportStatusEnum.submitted, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reject_reason = Column(Text, nullable=True)

    schedule = relationship("DutySchedule", back_populates="reports")
    images = relationship("DutyReportImage", back_populates="report", cascade="all, delete-orphan")


class DutyReportImage(Base):
    __tablename__ = "duty_report_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("duty_reports.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), nullable=False)
    photo_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    report = relationship("DutyReport", back_populates="images")


class DutyCategory(Base):
    __tablename__ = "duty_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
