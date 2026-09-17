from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# ==================== DEPARTMENTS ====================

class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    manager_name: str = Field(..., min_length=2, max_length=100)

class DepartmentResponse(DepartmentCreate):
    id: int

    class Config:
        from_attributes = True

# ==================== EMPLOYEES ====================

class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str 
    designation: str = Field(..., min_length=2)
    salary: float = Field(..., gt=0)
    joining_date: date
    department_id: Optional[int] = None

class EmployeeResponse(EmployeeCreate):
    id: int

    class Config:
        from_attributes = True

# ==================== PAYROLL ====================

class PayslipCreate(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)
    deductions: float = Field(default=0.0, ge=0)

class PayslipResponse(BaseModel):
    id: int
    employee_id: Optional[int]
    month: int
    year: int
    basic: float
    deductions: float
    net_pay: float

    class Config:
        from_attributes = True