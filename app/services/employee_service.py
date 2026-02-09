from sqlalchemy.orm import Session
from sqlalchemy import func, case
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from ..models.employee import Employee
from ..models.attendance import Attendance, AttendanceStatus


class EmployeeService:
    """Service class for employee operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Get all employees with attendance statistics."""
        employees = self.db.query(Employee).order_by(Employee.created_at.desc()).all()
        
        result = []
        for emp in employees:
            present_days = self.db.query(func.count(Attendance.id)).filter(
                Attendance.employee_id == emp.id,
                Attendance.status == AttendanceStatus.PRESENT.value
            ).scalar() or 0
            
            absent_days = self.db.query(func.count(Attendance.id)).filter(
                Attendance.employee_id == emp.id,
                Attendance.status == AttendanceStatus.ABSENT.value
            ).scalar() or 0
            
            result.append({
                "id": emp.id,
                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "email": emp.email,
                "department": emp.department,
                "created_at": emp.created_at,
                "updated_at": emp.updated_at,
                "present_days": present_days,
                "absent_days": absent_days
            })
        
        return result
    
    def get_employee_with_stats(self, employee_uuid: str) -> Optional[Dict[str, Any]]:
        """Get employee by UUID with attendance statistics."""
        emp = self.db.query(Employee).filter(Employee.id == employee_uuid).first()
        if not emp:
            return None
            
        present_days = self.db.query(func.count(Attendance.id)).filter(
            Attendance.employee_id == emp.id,
            Attendance.status == AttendanceStatus.PRESENT.value
        ).scalar() or 0
        
        absent_days = self.db.query(func.count(Attendance.id)).filter(
            Attendance.employee_id == emp.id,
            Attendance.status == AttendanceStatus.ABSENT.value
        ).scalar() or 0
        
        return {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "email": emp.email,
            "department": emp.department,
            "created_at": emp.created_at,
            "updated_at": emp.updated_at,
            "present_days": present_days,
            "absent_days": absent_days
        }

    def get_employee_by_id(self, employee_uuid: str) -> Optional[Employee]:
        """Get employee by UUID."""
        return self.db.query(Employee).filter(Employee.id == employee_uuid).first()
    
    def get_employee_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by employee ID."""
        return self.db.query(Employee).filter(Employee.employee_id == employee_id.upper()).first()
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email."""
        return self.db.query(Employee).filter(Employee.email == email.lower()).first()
    
    def create_employee(self, employee_id: str, full_name: str, email: str, department: str) -> Employee:
        """Create a new employee."""
        # Simple validation
        if self.get_employee_by_employee_id(employee_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with ID '{employee_id}' already exists"
            )
        
        if self.get_employee_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email '{email}' already exists"
            )
        
        try:
            employee = Employee(
                employee_id=employee_id.upper(),
                full_name=full_name,
                email=email.lower(),
                department=department
            )
            self.db.add(employee)
            self.db.commit()
            self.db.refresh(employee)
            return employee
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee with this ID or email already exists"
            )
    
    def delete_employee(self, employee_uuid: str) -> bool:
        """Delete an employee by UUID."""
        employee = self.get_employee_by_id(employee_uuid)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_uuid}' not found"
            )
        
        self.db.delete(employee)
        self.db.commit()
        return True
    
    def get_total_count(self) -> int:
        """Get total number of employees."""
        return self.db.query(func.count(Employee.id)).scalar() or 0
