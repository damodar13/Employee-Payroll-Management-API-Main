from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    manager_name = Column(String, nullable=False)

    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    designation = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    joining_date = Column(Date, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)

    department = relationship("Department", back_populates="employees")
    payslips = relationship("Payslip", back_populates="employee")


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    basic = Column(Float, nullable=False)
    deductions = Column(Float, nullable=False)
    net_pay = Column(Float, nullable=False)

    employee = relationship("Employee", back_populates="payslips")

    __table_args__ = (
        UniqueConstraint('employee_id', 'month', 'year', name='_employee_month_year_uc'),
    )