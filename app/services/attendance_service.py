from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import HTTPException, status

from ..models.attendance import Attendance, AttendanceStatus
from ..models.employee import Employee


class AttendanceService:
    """Service class for attendance operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def _format_record(self, record: Attendance) -> Dict[str, Any]:
        """Format attendance record to dictionary."""
        return {
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": record.employee.full_name if record.employee else None,
            "employee_code": record.employee.employee_id if record.employee else None,
            "date": record.date,
            "status": record.status,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }
    
    def get_all_attendance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get all attendance records with optional date filter."""
        query = self.db.query(Attendance).options(joinedload(Attendance.employee))
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        records = query.order_by(Attendance.date.desc()).all()
        return [self._format_record(record) for record in records]
    
    def get_attendance_by_employee(
        self,
        employee_uuid: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get attendance records for a specific employee."""
        # Verify employee exists roughly
        # Actually, if we query directly and return empty list, it's fine. 
        # But standard REST often returns 404 for sub-resource of non-existent parent.
        employee = self.db.query(Employee).filter(Employee.id == employee_uuid).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_uuid}' not found"
            )
        
        query = (
            self.db.query(Attendance)
            .options(joinedload(Attendance.employee))
            .filter(Attendance.employee_id == employee_uuid)
        )
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        records = query.order_by(Attendance.date.desc()).all()
        return [self._format_record(record) for record in records]
    
    def mark_attendance(self, employee_id: str, attendance_date: date, status_value: str) -> Dict[str, Any]:
        """Mark attendance for an employee."""
        # Verify employee exists
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_id}' not found"
            )
        
        # Check existing using UniqueConstraint logic effectively
        existing = self.db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.date == attendance_date
        ).first()
        
        if existing:
            existing.status = status_value
            self.db.commit()
            self.db.refresh(existing)
            return self._format_record(existing)
        
        try:
            attendance = Attendance(
                employee_id=employee_id,
                date=attendance_date,
                status=status_value
            )
            self.db.add(attendance)
            self.db.commit()
            self.db.refresh(attendance)
            # We need to refresh or manually set employee for formatting if joinedload isn't used here 
            # (which it isn't, but relation is loaded on access if session is open)
            return self._format_record(attendance)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendance for this date already exists"
            )
    
    def get_attendance_stats(self, employee_uuid: str) -> Dict[str, Any]:
        """Get attendance statistics for an employee."""
        employee = self.db.query(Employee).filter(Employee.id == employee_uuid).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_uuid}' not found"
            )
        
        total_records = self.db.query(func.count(Attendance.id)).filter(
            Attendance.employee_id == employee_uuid
        ).scalar() or 0
        
        present_count = self.db.query(func.count(Attendance.id)).filter(
            Attendance.employee_id == employee_uuid,
            Attendance.status == AttendanceStatus.PRESENT.value
        ).scalar() or 0
        
        absent_count = self.db.query(func.count(Attendance.id)).filter(
            Attendance.employee_id == employee_uuid,
            Attendance.status == AttendanceStatus.ABSENT.value
        ).scalar() or 0
        
        attendance_percentage = (present_count / total_records * 100) if total_records > 0 else 0.0
        
        return {
            "employee_id": employee_uuid,
            "employee_name": employee.full_name,
            "total_days": total_records,
            "present_days": present_count,
            "absent_days": absent_count,
            "attendance_percentage": round(attendance_percentage, 2)
        }
    
    def get_today_attendance_count(self) -> Dict[str, Any]:
        """Get today's attendance summary."""
        today = date.today()
        
        # Use simple queries to avoid potential SQLAlchemy version issues with case()
        total_employees = self.db.query(func.count(Employee.id)).scalar() or 0
        
        present_today = self.db.query(func.count(Attendance.id)).filter(
            Attendance.date == today,
            Attendance.status == AttendanceStatus.PRESENT.value
        ).scalar() or 0
        
        absent_today = self.db.query(func.count(Attendance.id)).filter(
            Attendance.date == today,
            Attendance.status == AttendanceStatus.ABSENT.value
        ).scalar() or 0
        
        marked_today = present_today + absent_today
        
        return {
            "total_employees": total_employees,
            "marked_today": marked_today,
            "present_today": present_today,
            "absent_today": absent_today,
            "unmarked_today": total_employees - marked_today,
            "attendance_rate": round((present_today / total_employees * 100) if total_employees > 0 else 0, 2)
        }
