import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000") 

st.set_page_config(
    page_title="Employee & Payroll Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Button Styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Form Container Styling */
    div[data-testid="stForm"] {
        border: 1px solid #f0f2f6;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        background-color: #ffffff;
    }
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        padding-bottom: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-size: 16px;
        font-weight: 500;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("💼 Workspace OS")
    st.markdown("Employee & Payroll Management System") 
    st.divider()
    st.caption(f"Connected to API: `{API_URL}`")

# Create tabs mirroring the 3-table API architecture[cite: 1]
tab_depts, tab_emps, tab_payroll = st.tabs(
    [
        "🏢 Departments",
        "👨‍💼 Employees",
        "🧾 Payroll & Payslips"
    ]
) 

# ==================== TAB 1: DEPARTMENTS ====================
with tab_depts:
    st.header("🏢 Department Management")
    st.markdown("Manage organizational structures and leadership.")
    st.write("---")
    
    col1, col2 = st.columns([1.2, 2])

    with col1:
        st.subheader("➕ Add New Department")
        with st.form("add_dept_form", clear_on_submit=True):
            dept_name = st.text_input("Department Name", placeholder="e.g. Engineering")
            manager_name = st.text_input("Manager Name", placeholder="e.g. Jane Doe")
            submit_dept = st.form_submit_button("Create Department", type="primary")

            if submit_dept:
                if not dept_name.strip() or not manager_name.strip(): 
                    st.warning("Please fill in all fields.")
                else:
                    with st.spinner("Creating department..."):
                        payload = {"name": dept_name, "manager_name": manager_name} 
                        try:
                            res = requests.post(f"{API_URL}/departments", json=payload, timeout=5) 
                            if res.status_code == 201: 
                                st.toast("Department created successfully!", icon="✅")
                                st.rerun() 
                            else:
                                st.error(res.json().get("detail", "Error creating department.")) 
                        except requests.exceptions.RequestException:
                            st.error("Cannot connect to server. Please check your API.") 

    with col2:
        st.subheader("📋 Active Departments")
        try:
            res = requests.get(f"{API_URL}/departments", timeout=5) 
            if res.status_code == 200: 
                depts = res.json() 
                if depts:
                    df_depts = pd.DataFrame(depts)
                    st.metric("Total Departments", len(df_depts))
                    st.dataframe(df_depts, use_container_width=True, hide_index=True)
                else:
                    st.info("No departments currently exist in the system.")
            else:
                st.error("Failed to fetch departments.") 
        except requests.exceptions.RequestException:
            st.error("Cannot connect to server.") 


# ==================== TAB 2: EMPLOYEES ====================
with tab_emps:
    st.header("👨‍💼 Employee Directory")
    st.write("---")
    
    emp_tab1, emp_tab2, emp_tab3, emp_tab4 = st.tabs(
        ["📋 View Directory", "➕ Onboard Employee", "✏️ Update Profile", "🗑️ Offboard Employee"]
    )

    # 1. View All Employees
    with emp_tab1:
        try:
            with st.spinner("Loading directory..."):
                res = requests.get(f"{API_URL}/employees", timeout=5) 
                if res.status_code == 200: 
                    emps = res.json() 
                    if emps:
                        df_emps = pd.DataFrame(emps)
                        st.metric("Total Active Employees", len(df_emps))
                        st.dataframe(df_emps, use_container_width=True, hide_index=True)
                    else:
                        st.info("The employee directory is empty.")
                else:
                    st.error("Failed to load employees.") 
        except requests.exceptions.RequestException:
            st.error("Cannot connect to server.") 

    # 2. Add Employee
    with emp_tab2:
        dept_options = {}
        try:
            d_res = requests.get(f"{API_URL}/departments", timeout=5) 
            if d_res.status_code == 200: 
                dept_options = {d["name"]: d["id"] for d in d_res.json()} 
        except requests.exceptions.RequestException:
            st.sidebar.error("Cannot fetch departments. Employee onboarding may be limited.")

        with st.form("add_emp_form", clear_on_submit=True):
            st.subheader("Personal & Professional Details")
            col_a, col_b = st.columns(2)
            
            with col_a:
                emp_name = st.text_input("Full Name") 
                emp_email = st.text_input("Work Email")
                emp_date = st.date_input("Joining Date") 
                
            with col_b:
                emp_desig = st.text_input("Designation") 
                emp_salary = st.number_input("Base Salary (₹)", min_value=1.0, step=1000.0) 
                selected_dept = st.selectbox("Assign Department", ["None"] + list(dept_options.keys())) 
            
            submit_emp = st.form_submit_button("Onboard Employee", type="primary")

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
                    with st.spinner("Processing onboard request..."):
                        try:
                            res = requests.post(f"{API_URL}/employees", json=payload, timeout=5) 
                            if res.status_code == 201: 
                                st.success("Employee onboarded successfully!")
                                st.json(res.json(), expanded=False)
                            else:
                                st.error(res.json().get("detail", "Error creating employee.")) 
                        except requests.exceptions.RequestException:
                            st.error("Cannot connect to server.") 

    # 3. Update Employee
    with emp_tab3:
        col_search, col_form = st.columns([1, 2])
        
        with col_search:
            update_id = st.number_input("Enter Employee ID", min_value=1, step=1, key="up_id") 
            if st.button("Fetch Profile"):
                with st.spinner("Searching..."):
                    try:
                        res = requests.get(f"{API_URL}/employees/{update_id}", timeout=5) 
                        if res.status_code == 200: 
                            st.session_state["emp_data"] = res.json() 
                        else:
                            st.error("Employee not found.") 
                            st.session_state.pop("emp_data", None) 
                    except requests.exceptions.RequestException:
                        st.error("Cannot connect to server.") 

        with col_form:
            if "emp_data" in st.session_state:
                data = st.session_state["emp_data"] 
                with st.form("update_emp_form"):
                    st.subheader(f"Updating Profile: {data['name']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        u_name = st.text_input("Name", value=data["name"]) 
                        u_email = st.text_input("Email", value=data["email"]) 
                    with c2:
                        u_desig = st.text_input("Designation", value=data["designation"]) 
                        u_salary = st.number_input("Salary (₹)", value=float(data["salary"])) 
                    
                    try:
                        d_res = requests.get(f"{API_URL}/departments", timeout=5) 
                        dept_opts = {d["name"]: d["id"] for d in d_res.json()} if d_res.status_code == 200 else {} 
                    except:
                        dept_opts = {}

                    u_dept = st.selectbox("Department", ["None"] + list(dept_opts.keys())) 
                    
                    if st.form_submit_button("Save Changes", type="primary"):
                        payload = {
                            "name": u_name,
                            "email": u_email,
                            "designation": u_desig,
                            "salary": float(u_salary),
                            "joining_date": data["joining_date"],
                            "department_id": dept_opts.get(u_dept)
                        } 
                        with st.spinner("Saving modifications..."):
                            try:
                                res = requests.put(f"{API_URL}/employees/{update_id}", json=payload, timeout=5) 
                                if res.status_code == 200: 
                                    st.success("Profile updated successfully!")
                                    st.session_state.pop("emp_data", None) 
                                else:
                                    st.error(res.json().get("detail", "Update failed.")) 
                            except requests.exceptions.RequestException:
                                st.error("Cannot connect to server.") 
            else:
                st.info("Enter an Employee ID on the left to load their profile.")

    # 4. Delete Employee
    with emp_tab4:
        st.warning("⚠️ Offboarding is irreversible. Please verify the Employee ID before proceeding.")
        del_id = st.number_input("Employee ID to Offboard", min_value=1, step=1, key="del_id") 
        if st.button("Permanently Delete Profile", type="primary"):
            with st.spinner("Deleting record..."):
                try:
                    res = requests.delete(f"{API_URL}/employees/{del_id}", timeout=5) 
                    if res.status_code == 200: 
                        st.success(res.json().get("message", "Profile successfully deleted.")) 
                    else:
                        st.error(res.json().get("detail", "Failed to delete profile.")) 
                except requests.exceptions.RequestException:
                    st.error("Cannot connect to server.") 


# ==================== TAB 3: PAYROLL ====================
with tab_payroll:
    st.header("🧾 Payroll Processing")
    st.write("---")
    
    col_proc, col_hist = st.columns([1.2, 2])

    with col_proc:
        st.subheader("⚙️ Generate Payslip")
        
        emp_options = {}
        try:
            e_res = requests.get(f"{API_URL}/employees", timeout=5) 
            if e_res.status_code == 200: 
                emp_options = {f"{e['name']} (ID: {e['id']})": e["id"] for e in e_res.json()} 
        except:
            pass

        with st.form("generate_payslip_form", clear_on_submit=True):
            selected_emp = st.selectbox("Target Employee", list(emp_options.keys())) 
            
            c1, c2 = st.columns(2)
            with c1:
                pay_month = st.number_input("Billing Month (1-12)", min_value=1, max_value=12, value=10) 
            with c2:
                pay_year = st.number_input("Billing Year", min_value=2000, max_value=2100, value=2026) 
                
            deductions = st.number_input("Tax / Deductions (₹)", min_value=0.0, step=50.0, value=0.0) 

            if st.form_submit_button("Process Payroll", type="primary"):
                if not selected_emp: 
                    st.warning("Please select an employee.")
                else:
                    emp_id = emp_options[selected_emp] 
                    payload = {
                        "month": int(pay_month),
                        "year": int(pay_year),
                        "deductions": float(deductions)
                    } 
                    with st.spinner("Processing financial records..."):
                        try:
                            res = requests.post(f"{API_URL}/payslips/generate/{emp_id}", json=payload, timeout=5) 
                            if res.status_code == 201: 
                                st.success("Payslip successfully generated!")
                                st.json(res.json(), expanded=False)
                            else:
                                st.error(res.json().get("detail", "Failed to generate payslip.")) 
                        except requests.exceptions.RequestException:
                            st.error("Cannot connect to server.") 

    with col_hist:
        st.subheader("📜 Historical Records")
        view_filter = st.radio("Display Mode", ["Aggregate View", "Employee Specific"], horizontal=True) 
        
        if view_filter == "Aggregate View": 
            with st.spinner("Retrieving payroll history..."):
                try:
                    res = requests.get(f"{API_URL}/payslips", timeout=5) 
                    if res.status_code == 200: 
                        slips = res.json() 
                        if slips:
                            st.dataframe(pd.DataFrame(slips), use_container_width=True, hide_index=True)
                        else:
                            st.info("No payslip records found in the system.")
                except requests.exceptions.RequestException:
                    st.error("Cannot connect to server.") 
        else:
            filter_emp_id = st.number_input("Target Employee ID", min_value=1, step=1) 
            if st.button("Fetch Employee Ledger"):
                with st.spinner("Retrieving specific records..."):
                    try:
                        res = requests.get(f"{API_URL}/payslips/{filter_emp_id}", timeout=5) 
                        if res.status_code == 200: 
                            slips = res.json() 
                            if slips:
                                st.dataframe(pd.DataFrame(slips), use_container_width=True, hide_index=True)
                            else:
                                st.info("No payslip records found for this employee ID.")
                    except requests.exceptions.RequestException:
                        st.error("Cannot connect to server.") 