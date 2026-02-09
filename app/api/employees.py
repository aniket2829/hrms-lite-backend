from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])

class EmployeeCreate(BaseModel):
    employee_id: str
    full_name: str
    email: str
    department: str


class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    present_days: int = 0
    absent_days: int = 0


class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True


@router.get("", response_model=EmployeeListResponse)
def get_all_employees(db: Session = Depends(get_db)):
    """Get all employees with their attendance statistics."""
    service = EmployeeService(db)
    employees = service.get_all_employees()
    return EmployeeListResponse(
        employees=[EmployeeResponse(**emp) for emp in employees],
        total=len(employees)
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new employee."""
    service = EmployeeService(db)
    employee = service.create_employee(
        employee_id=employee_data.employee_id,
        full_name=employee_data.full_name,
        email=employee_data.email,
        department=employee_data.department
    )
    
    return EmployeeResponse(
        id=employee.id,
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        email=employee.email,
        department=employee.department,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
        present_days=0,
        absent_days=0
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific employee by UUID."""
    service = EmployeeService(db)
    employee_data = service.get_employee_with_stats(employee_id)
    
    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found"
        )
    
    return EmployeeResponse(**employee_data)


@router.delete("/{employee_id}", response_model=MessageResponse)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Delete an employee by UUID."""
    service = EmployeeService(db)
    service.delete_employee(employee_id)
    
    return MessageResponse(
        message="Employee deleted successfully",
        success=True
    )
