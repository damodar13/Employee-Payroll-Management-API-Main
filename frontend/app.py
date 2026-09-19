import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

API_URL = os.getenv("API__URL","http://127.0.0.1:8000")



st.set_page_config(
    page_title="Employee & Payroll Portal",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Employee & Payroll Management System")

# Create tabs mirroring your 3-table API architecture
tab_depts, tab_emps, tab_payroll = st.tabs(
    [
        "🏢 Departments",
        "👨💼 Employees",
        "🧾 Payroll & Payslips"
    ]
)

# ==================== TAB 1: DEPARTMENTS ====================
with tab_depts:
    st.subheader("🏢 Department Management")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Add Department")
        with st.form("add_dept_form"):
            dept_name = st.text_input("Department Name")
            manager_name = st.text_input("Manager Name")
            submit_dept = st.form_submit_button("Create Department")

            if submit_dept:
                if not dept_name.strip() or not manager_name.strip():
                    st.warning("Please fill in all fields.")
                else:
                    payload = {"name": dept_name, "manager_name": manager_name}
                    try:
                        res = requests.post(f"{API_URL}/departments", json=payload, timeout=5)
                        if res.status_code == 201:
                            st.success("Department created!")
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Error creating department."))
                    except requests.exceptions.RequestException:
                        st.error("Cannot connect to server.")

    with col2:
        st.markdown("### 📋 All Departments")
        try:
            res = requests.get(f"{API_URL}/departments", timeout=5)
            if res.status_code == 200:
                depts = res.json()
                if depts:
                    st.dataframe(pd.DataFrame(depts), use_container_width=True)
                else:
                    st.info("No departments found.")
            else:
                st.error("Failed to fetch departments.")
        except requests.exceptions.RequestException:
            st.error("Cannot connect to server.")


# ==================== TAB 2: EMPLOYEES ====================
with tab_emps:
    st.subheader("👨💼 Employee Management")
    
    emp_tab1, emp_tab2, emp_tab3, emp_tab4 = st.tabs(
        ["View All", "Add Employee", "Update Employee", "Delete Employee"]
    )

    # 1. View All Employees
    with emp_tab1:
        try:
            res = requests.get(f"{API_URL}/employees", timeout=5)
            if res.status_code == 200:
                emps = res.json()
                if emps:
                    st.dataframe(pd.DataFrame(emps), use_container_width=True)
                else:
                    st.info("No employees found.")
            else:
                st.error("Failed to load employees.")
        except requests.exceptions.RequestException:
            st.error("Cannot connect to server.")

    # 2. Add Employee
    with emp_tab2:
        # Fetch departments for selectbox
        dept_options = {}
        try:
            d_res = requests.get(f"{API_URL}/departments", timeout=5)
            if d_res.status_code == 200:
                dept_options = {d["name"]: d["id"] for d in d_res.json()}
        except requests.exceptions.RequestException:
            pass

        with st.form("add_emp_form"):
            emp_name = st.text_input("Full Name")
            emp_email = st.text_input("Email")
            emp_desig = st.text_input("Designation")
            emp_salary = st.number_input("Salary (₹)", min_value=1.0, step=1000.0)
            emp_date = st.date_input("Joining Date")
            
            selected_dept = st.selectbox("Department", ["None"] + list(dept_options.keys()))
            submit_emp = st.form_submit_button("Add Employee")

            if submit_emp:
                if not emp_name or not emp_email or not emp_desig:
                    st.warning("Please complete all required fields.")
                else:
                    payload = {
                        "name": emp_name,
                        "email": emp_email,
                        "designation": emp_desig,
                        "salary": float(emp_salary),
                        "joining_date": str(emp_date),
                        "department_id": dept_options.get(selected_dept)
                    }
                    try:
                        res = requests.post(f"{API_URL}/employees", json=payload, timeout=5)
                        if res.status_code == 201:
                            st.success("Employee created successfully!")
                            st.json(res.json())
                        else:
                            st.error(res.json().get("detail", "Error creating employee."))
                    except requests.exceptions.RequestException:
                        st.error("Cannot connect to server.")

    # 3. Update Employee
    with emp_tab3:
        update_id = st.number_input("Employee ID", min_value=1, step=1, key="up_id")
        if st.button("Fetch Employee"):
            try:
                res = requests.get(f"{API_URL}/employees/{update_id}", timeout=5)
                if res.status_code == 200:
                    st.session_state["emp_data"] = res.json()
                else:
                    st.error("Employee not found.")
                    st.session_state.pop("emp_data", None)
            except requests.exceptions.RequestException:
                st.error("Cannot connect to server.")

        if "emp_data" in st.session_state:
            data = st.session_state["emp_data"]
            with st.form("update_emp_form"):
                u_name = st.text_input("Name", value=data["name"])
                u_email = st.text_input("Email", value=data["email"])
                u_desig = st.text_input("Designation", value=data["designation"])
                u_salary = st.number_input("Salary", value=float(data["salary"]))
                
                # Retrieve dept map
                try:
                    d_res = requests.get(f"{API_URL}/departments", timeout=5)
                    dept_options = {d["name"]: d["id"] for d in d_res.json()} if d_res.status_code == 200 else {}
                except:
                    dept_options = {}

                u_dept = st.selectbox("Department ID", ["None"] + list(dept_options.keys()))
                
                if st.form_submit_button("Update Details"):
                    payload = {
                        "name": u_name,
                        "email": u_email,
                        "designation": u_desig,
                        "salary": float(u_salary),
                        "joining_date": data["joining_date"],
                        "department_id": dept_options.get(u_dept)
                    }
                    try:
                        res = requests.put(f"{API_URL}/employees/{update_id}", json=payload, timeout=5)
                        if res.status_code == 200:
                            st.success("Employee updated successfully!")
                            st.session_state.pop("emp_data", None)
                        else:
                            st.error(res.json().get("detail", "Update failed."))
                    except requests.exceptions.RequestException:
                        st.error("Cannot connect to server.")

    # 4. Delete Employee
    with emp_tab4:
        del_id = st.number_input("Employee ID to Delete", min_value=1, step=1, key="del_id")
        if st.button("Delete Employee", type="primary"):
            try:
                res = requests.delete(f"{API_URL}/employees/{del_id}", timeout=5)
                if res.status_code == 200:
                    st.success(res.json().get("message", "Deleted."))
                else:
                    st.error(res.json().get("detail", "Failed to delete."))
            except requests.exceptions.RequestException:
                st.error("Cannot connect to server.")


# ==================== TAB 3: PAYROLL ====================
with tab_payroll:
    st.subheader("🧾 Payroll & Payslips")
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ⚙️ Generate Payslip")
        
        # Load employees for dropdown
        emp_options = {}
        try:
            e_res = requests.get(f"{API_URL}/employees", timeout=5)
            if e_res.status_code == 200:
                emp_options = {f"{e['name']} (ID: {e['id']})": e["id"] for e in e_res.json()}
        except:
            pass

        with st.form("generate_payslip_form"):
            selected_emp = st.selectbox("Select Employee", list(emp_options.keys()))
            pay_month = st.number_input("Month (1-12)", min_value=1, max_value=12, value=9)
            pay_year = st.number_input("Year", min_value=2000, max_value=2100, value=2026)
            deductions = st.number_input("Deductions ($)", min_value=0.0, step=50.0, value=0.0)

            if st.form_submit_button("Generate Payslip"):
                if not selected_emp:
                    st.warning("Select an employee.")
                else:
                    emp_id = emp_options[selected_emp]
                    payload = {
                        "month": int(pay_month),
                        "year": int(pay_year),
                        "deductions": float(deductions)
                    }
                    try:
                        res = requests.post(f"{API_URL}/payslips/generate/{emp_id}", json=payload, timeout=5)
                        if res.status_code == 201:
                            st.success("Payslip generated successfully!")
                            st.json(res.json())
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Failed to generate payslip."))
                    except requests.exceptions.RequestException:
                        st.error("Cannot connect to server.")

    with col2:
        st.markdown("### 📜 Payslip Records")
        view_filter = st.radio("View", ["All Payslips", "By Employee ID"], horizontal=True)
        
        if view_filter == "All Payslips":
            try:
                res = requests.get(f"{API_URL}/payslips", timeout=5)
                if res.status_code == 200:
                    slips = res.json()
                    if slips:
                        st.dataframe(pd.DataFrame(slips), use_container_width=True)
                    else:
                        st.info("No payslips found.")
            except requests.exceptions.RequestException:
                st.error("Cannot connect to server.")
        else:
            filter_emp_id = st.number_input("Filter by Employee ID", min_value=1, step=1)
            if st.button("Fetch Records"):
                try:
                    res = requests.get(f"{API_URL}/payslips/{filter_emp_id}", timeout=5)
                    if res.status_code == 200:
                        slips = res.json()
                        if slips:
                            st.dataframe(pd.DataFrame(slips), use_container_width=True)
                        else:
                            st.info("No payslips found for this employee.")
                except requests.exceptions.RequestException:
                    st.error("Cannot connect to server.")