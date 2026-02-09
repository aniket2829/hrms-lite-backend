from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class AttendanceStatusEnum(str, Enum):
    """Attendance status enum for API."""
    PRESENT = "present"
    ABSENT = "absent"


class AttendanceCreate(BaseModel):
    """Schema for marking attendance."""
    
    employee_id: str = Field(
        ...,
        description="Employee's UUID"
    )
    date: date = Field(
        ...,
        description="Attendance date"
    )
    status: AttendanceStatusEnum = Field(
        ...,
        description="Attendance status (present/absent)"
    )


class AttendanceResponse(BaseModel):
    """Schema for attendance response."""
    
    id: str
    employee_id: str
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    date: date
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class AttendanceListResponse(BaseModel):
    """Schema for list of attendance records."""
    
    records: List["AttendanceResponse"]
    total: int


class AttendanceStats(BaseModel):
    """Schema for attendance statistics."""
    
    employee_id: str
    employee_name: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float


class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    
    total_employees: int
    total_attendance_today: int
    present_today: int
    absent_today: int
    attendance_rate_today: float
