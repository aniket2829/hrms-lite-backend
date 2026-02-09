from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmployeeCreate(BaseModel):
    """Schema for creating a new employee."""
    employee_id: str
    full_name: str
    email: str
    department: str


class EmployeeResponse(BaseModel):
    """Schema for employee response."""
    id: str
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    present_days: int = 0
    absent_days: int = 0
    
    model_config = {"from_attributes": True}


class EmployeeListResponse(BaseModel):
    """Schema for list of employees response."""
    employees: List[EmployeeResponse]
    total: int
