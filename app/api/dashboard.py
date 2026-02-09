from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..services.employee_service import EmployeeService
from ..services.attendance_service import AttendanceService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    total_employees: int
    marked_today: int
    present_today: int
    absent_today: int
    unmarked_today: int
    attendance_rate: float


@router.get("", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    attendance_service = AttendanceService(db)
    
    stats = attendance_service.get_today_attendance_count()
    
    return DashboardStats(**stats)
