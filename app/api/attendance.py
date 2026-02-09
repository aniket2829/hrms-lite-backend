from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

from ..database import get_db
from ..services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])

class AttendanceStatusEnum(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"


class AttendanceCreate(BaseModel):
    employee_id: str
    date: date
    status: AttendanceStatusEnum


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    date: date
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AttendanceListResponse(BaseModel):
    records: List[AttendanceResponse]
    total: int



class AttendanceStats(BaseModel):
    employee_id: str
    employee_name: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float


@router.get("/today")
def get_today_attendance(db: Session = Depends(get_db)):
    """Get all attendance records for today."""
    service = AttendanceService(db)
    today = date.today()
    records = service.get_all_attendance(start_date=today, end_date=today)
    
    return {
        "attendance": records,
        "total": len(records)
    }



@router.get("", response_model=AttendanceListResponse)
def get_all_attendance(
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """Get all attendance records with optional date filtering."""
    service = AttendanceService(db)
    records = service.get_all_attendance(start_date, end_date)
    
    return AttendanceListResponse(
        records=[AttendanceResponse(**rec) for rec in records],
        total=len(records)
    )


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def mark_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db)
):
    """Mark attendance for an employee."""
    service = AttendanceService(db)
    result = service.mark_attendance(
        employee_id=attendance_data.employee_id,
        attendance_date=attendance_data.date,
        status_value=attendance_data.status.value
    )
    return AttendanceResponse(**result)


@router.get("/employee/{employee_id}", response_model=AttendanceListResponse)
def get_employee_attendance(
    employee_id: str,
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """Get attendance records for a specific employee."""
    service = AttendanceService(db)
    records = service.get_attendance_by_employee(employee_id, start_date, end_date)
    
    return AttendanceListResponse(
        records=[AttendanceResponse(**rec) for rec in records],
        total=len(records)
    )


@router.get("/stats/{employee_id}", response_model=AttendanceStats)
def get_attendance_stats(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get attendance statistics for a specific employee."""
    service = AttendanceService(db)
    stats = service.get_attendance_stats(employee_id)
    return AttendanceStats(**stats)
