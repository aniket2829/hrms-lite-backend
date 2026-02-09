from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class Employee(Base):
    """Employee database model."""
    
    __tablename__ = "employees"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    attendance_records = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Employee(id={self.id}, employee_id={self.employee_id}, name={self.full_name})>"
