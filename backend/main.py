from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import Base, engine, get_db
from models import Department, Employee, Payslip
from schemas import (
    DepartmentCreate, DepartmentResponse,
    EmployeeCreate, EmployeeResponse,
    PayslipCreate, PayslipResponse
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee & Payroll Management API")

# ==================== DEPARTMENTS ====================

@app.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    new_dept = Department(**dept.model_dump())
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

@app.get("/departments", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@app.get("/departments/{id}", response_model=DepartmentResponse)
def get_department(id: int, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(Department.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept

# ==================== EMPLOYEES ====================

@app.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    if emp.department_id:
        dept = db.query(Department).filter(Department.id == emp.department_id).first()
        if not dept:
            raise HTTPException(status_code=400, detail="Department ID does not exist")
            
    existing_emp = db.query(Employee).filter(Employee.email == emp.email).first()
    if existing_emp:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_emp = Employee(**emp.model_dump())
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@app.get("/employees", response_model=List[EmployeeResponse])
def list_employees(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Employee)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    return query.all()

@app.get("/employees/{id}", response_model=EmployeeResponse)
def get_employee(id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.put("/employees/{id}", response_model=EmployeeResponse)
def update_employee(id: int, emp_data: EmployeeCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if emp_data.department_id:
        dept = db.query(Department).filter(Department.id == emp_data.department_id).first()
        if not dept:
            raise HTTPException(status_code=400, detail="Department ID does not exist")

    for key, value in emp_data.model_dump().items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)
    return emp

@app.delete("/employees/{id}", status_code=status.HTTP_200_OK)
def delete_employee(id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": f"Employee {id} deleted successfully. Historical payslips preserved."}

# ==================== PAYROLL ====================

@app.post("/payslips/generate/{employee_id}", response_model=PayslipResponse, status_code=status.HTTP_201_CREATED)
def generate_payslip(employee_id: int, payroll: PayslipCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing_payslip = db.query(Payslip).filter(
        Payslip.employee_id == employee_id,
        Payslip.month == payroll.month,
        Payslip.year == payroll.year
    ).first()

    if existing_payslip:
        raise HTTPException(
            status_code=400,
            detail=f"Payslip already generated for employee {employee_id} for {payroll.month}/{payroll.year}"
        )

    basic = emp.salary
    net_pay = basic - payroll.deductions

    new_payslip = Payslip(
        employee_id=employee_id,
        month=payroll.month,
        year=payroll.year,
        basic=basic,
        deductions=payroll.deductions,
        net_pay=net_pay
    )

    db.add(new_payslip)
    db.commit()
    db.refresh(new_payslip)
    return new_payslip

@app.get("/payslips/{employee_id}", response_model=List[PayslipResponse])
def get_employee_payslips(employee_id: int, db: Session = Depends(get_db)):
    payslips = db.query(Payslip).filter(Payslip.employee_id == employee_id).all()
    return payslips

@app.get("/payslips", response_model=List[PayslipResponse])
def list_all_payslips(db: Session = Depends(get_db)):
    return db.query(Payslip).all()