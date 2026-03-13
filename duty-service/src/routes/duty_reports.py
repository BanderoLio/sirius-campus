from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
from datetime import datetime

from src.database import get_db
from src.database.models import DutyReport, ReportStatusEnum
from src.schemas import (
    DutyReportResponse,
    DutyReportCreate,
    DutyReportUpdate,
    DutyReportPatch,
    DutyReportListResponse,
    DutyReportDetailResponse,
)

router = APIRouter(prefix="/duties/reports", tags=["Duty Reports"])


@router.get("", response_model=DutyReportListResponse)
async def get_reports(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    schedule_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutyReport)
    
    if schedule_id:
        query = query.where(DutyReport.schedule_id == schedule_id)
    if status:
        query = query.where(DutyReport.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    pages = (total + size - 1) // size if total > 0 else 0
    
    return DutyReportListResponse(
        items=[DutyReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=DutyReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: DutyReportCreate,
    db: AsyncSession = Depends(get_db),
):
    user_id = UUID("550e8400-e29b-41d4-a716-446655440200")
    
    report = DutyReport(
        schedule_id=report_data.schedule_id,
        user_id=user_id,
        status=ReportStatusEnum.submitted,
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return DutyReportResponse.model_validate(report)


@router.get("/{report_id}", response_model=DutyReportDetailResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutyReport).options(selectinload(DutyReport.images)).where(DutyReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return DutyReportDetailResponse.model_validate(report)


@router.put("/{report_id}", response_model=DutyReportResponse)
async def update_report(
    report_id: UUID,
    report_data: DutyReportUpdate,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutyReport).where(DutyReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.schedule_id = report_data.schedule_id
    report.status = report_data.status
    
    await db.commit()
    await db.refresh(report)
    
    return DutyReportResponse.model_validate(report)


@router.patch("/{report_id}", response_model=DutyReportResponse)
async def patch_report(
    report_id: UUID,
    report_data: DutyReportPatch,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutyReport).where(DutyReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report_data.status:
        report.status = report_data.status
        if report_data.status == ReportStatusEnum.accepted:
            report.reviewed_at = datetime.utcnow()
            report.reviewed_by = UUID("550e8400-e29b-41d4-a716-446655440300")
        elif report_data.status == ReportStatusEnum.rejected:
            report.reviewed_at = datetime.utcnow()
            report.reviewed_by = UUID("550e8400-e29b-41d4-a716-446655440300")
            if report_data.reject_reason:
                report.reject_reason = report_data.reject_reason
    
    await db.commit()
    await db.refresh(report)
    
    return DutyReportResponse.model_validate(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutyReport).where(DutyReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    await db.delete(report)
    await db.commit()
