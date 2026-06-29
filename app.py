"""
Premsons Motors - Task Management Dashboard
Excel-Integrated Version (Two-Way Sync)

- Dashboard reads from Excel file
- Dashboard writes to Excel file
- Update Excel manually → Refresh dashboard to see changes
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from pathlib import Path
import hashlib
import io
import os

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Premsons Task Dashboard", page_icon="🚗", layout="wide")

# Excel file path - change this to your file location
EXCEL_FILE = Path("premsons_tasks.xlsx")

DEFAULT_PASSWORD = "premsons@123"
ADMIN_PASSWORD = "admin@123"

# ═══════════════════════════════════════════════════════════════════════════════
# DOER DATA (Used only for initial setup)
# ═══════════════════════════════════════════════════════════════════════════════

DOERS_DATA = [
    {"user_id": "PS1", "name": "PS1", "department": "SALES", "email": "vivek.premsons@gmail.com"},
    {"user_id": "PS2", "name": "PS2", "department": "SALES", "email": "rajk7233@gmail.com"},
    {"user_id": "PSD", "name": "PSD", "department": "SALES", "email": "guptaamar.n.s@gmail.com"},
    {"user_id": "PSB", "name": "PSB", "department": "SALES", "email": "arenar2@premsonsmotor.com"},
    {"user_id": "PSHAZ", "name": "PSHAZ", "department": "SALES", "email": "premsonshzbsm@premsonsmotor.com"},
    {"user_id": "PSDEO", "name": "PSDEO", "department": "SALES", "email": "ruralarena@premsonsmotor.com"},
    {"user_id": "PSO", "name": "PSO", "department": "SALES", "email": "arenapso@premsonsmotor.com"},
    {"user_id": "51NA", "name": "51NA", "department": "SALES", "email": "nexamainroad@premsonsmotor.com"},
    {"user_id": "51NC", "name": "51NC", "department": "SALES", "email": "smnexabariaturoad@premsonsmotor.com"},
    {"user_id": "HAZARIBAGH", "name": "HAZARIBAGH", "department": "SALES", "email": "premsonshzbsm@premsonsmotor.com"},
    {"user_id": "DEOGHAR", "name": "DEOGHAR", "department": "SALES", "email": "nexadeoghar@premsonsmotor.com"},
    {"user_id": "DALTONGANJ", "name": "DALTONGANJ", "department": "SALES", "email": "nexadaltonganj@premsonsmotor.com"},
    {"user_id": "BIRSA_CHOWK", "name": "BIRSA CHOWK", "department": "SALES", "email": "nexaranchirural@premsonsmotor.com"},
    {"user_id": "RAHUL", "name": "RAHUL", "department": "HR", "email": "premsons.hr@gmail.com"},
    {"user_id": "RANJEET", "name": "RANJEET", "department": "HR", "email": "ranjeet.premsons@gmail.com"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# EXCEL FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_initial_excel():
    """Create Excel file with initial data if it doesn't exist."""
    if EXCEL_FILE.exists():
        return
    
    # Create users
    users_data = []
    hashed_pwd = hash_password(DEFAULT_PASSWORD)
    
    for doer in DOERS_DATA:
        users_data.append({
            "user_id": doer["user_id"],
            "name": doer["name"],
            "department": doer["department"],
            "email": doer["email"].lower(),
            "password_hash": hashed_pwd,
            "role": "doer"
        })
    
    users_data.append({
        "user_id": "ADMIN",
        "name": "Administrator",
        "department": "ADMIN",
        "email": "admin@premsonsmotor.com",
        "password_hash": hash_password(ADMIN_PASSWORD),
        "role": "admin"
    })
    
    users_df = pd.DataFrame(users_data)
    
    # Create sample tasks
    import random
    sample_tasks = [
        "Daily sales report submission",
        "Customer follow-up calls",
        "Vehicle delivery coordination",
        "Showroom inventory check",
        "Service appointment scheduling",
        "Test drive appointments",
        "Customer feedback collection",
    ]
    
    tasks_data = []
    task_counter = 1
    today = datetime.now().date()
    
    for doer in DOERS_DATA:
        if doer["department"] == "SALES":
            for i in range(random.randint(2, 4)):
                due_offset = random.randint(-2, 5)
                status = "completed" if due_offset < -1 and random.random() > 0.4 else "pending"
                
                tasks_data.append({
                    "task_id": f"T{task_counter:04d}",
                    "user_id": doer["user_id"],
                    "task_title": random.choice(sample_tasks),
                    "description": f"Daily task for {doer['name']}",
                    "assigned_date": today - timedelta(days=3),
                    "due_date": today + timedelta(days=due_offset),
                    "status": status,
                    "completed_date": (today + timedelta(days=due_offset - 1)) if status == "completed" else None
                })
                task_counter += 1
    
    tasks_df = pd.DataFrame(tasks_data)
    
    # Save to Excel
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        users_df.to_excel(writer, sheet_name='users', index=False)
        tasks_df.to_excel(writer, sheet_name='tasks', index=False)
    
    print(f"✅ Created Excel file: {EXCEL_FILE}")

def read_users_from_excel():
    """Read users from Excel file."""
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='users')
        return df
    except Exception as e:
        st.error(f"Error reading users: {e}")
        return pd.DataFrame()

def read_tasks_from_excel():
    """Read tasks from Excel file."""
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='tasks')
        # Convert date columns
        for col in ['assigned_date', 'due_date', 'completed_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error reading tasks: {e}")
        return pd.DataFrame()

def save_to_excel(users_df, tasks_df):
    """Save both dataframes back to Excel."""
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
            users_df.to_excel(writer, sheet_name='users', index=False)
            tasks_df.to_excel(writer, sheet_name='tasks', index=False)
        return True
    except Exception as e:
        st.error(f"Error saving to Excel: {e}")
        return False

def save_tasks_to_excel(tasks_df):
    """Save only tasks, preserving users sheet."""
    try:
        users_df = read_users_from_excel()
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
            users_df.to_excel(writer, sheet_name='users', index=False)
            tasks_df.to_excel(writer, sheet_name='tasks', index=False)
        return True
    except Exception as e:
        st.error(f"Error saving tasks: {e}")
        return False

def get_next_task_id():
    """Generate next task ID."""
    tasks_df = read_tasks_from_excel()
    if tasks_df.empty:
        return "T0001"
    
    # Extract numbers from task IDs
    task_nums = tasks_df["task_id"].str.extract(r"T(\d+)")[0].dropna().astype(int)
    if task_nums.empty:
        return "T0001"
    
    max_num = task_nums.max()
    return f"T{max_num + 1:04d}"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def authenticate_user(email, password):
    """Authenticate user from Excel."""
    users_df = read_users_from_excel()
    user_row = users_df[users_df["email"] == email.lower().strip()]
    
    if user_row.empty:
        return None
    
    user = user_row.iloc[0]
    if hash_password(password) == user["password_hash"]:
        return {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "department": user["department"],
            "role": user["role"]
        }
    return None

def update_task_status(task_id, new_status):
    """Update task status in Excel."""
    tasks_df = read_tasks_from_excel()
    
    mask = tasks_df["task_id"] == task_id
    tasks_df.loc[mask, "status"] = new_status
    
    if new_status == "completed":
        tasks_df.loc[mask, "completed_date"] = datetime.now()
    else:
        tasks_df.loc[mask, "completed_date"] = pd.NaT
    
    save_tasks_to_excel(tasks_df)

def add_task(user_id, title, description, due_date):
    """Add new task to Excel."""
    tasks_df = read_tasks_from_excel()
    new_id = get_next_task_id()
    
    new_task = pd.DataFrame([{
        "task_id": new_id,
        "user_id": user_id,
        "task_title": title,
        "description": description,
        "assigned_date": datetime.now(),
        "due_date": datetime.combine(due_date, datetime.min.time()),
        "status": "pending",
        "completed_date": None
    }])
    
    tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
    save_tasks_to_excel(tasks_df)
    return new_id

def add_bulk_tasks(tasks_list):
    """Add multiple tasks to Excel."""
    tasks_df = read_tasks_from_excel()
    count = 0
    
    for task in tasks_list:
        new_id = get_next_task_id()
        new_task = pd.DataFrame([{
            "task_id": new_id,
            "user_id": task["user_id"],
            "task_title": task["task_title"],
            "description": task.get("description", ""),
            "assigned_date": datetime.now(),
            "due_date": pd.to_datetime(task["due_date"]),
            "status": "pending",
            "completed_date": None
        }])
        tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
        count += 1
    
    save_tasks_to_excel(tasks_df)
    return count

def delete_task(task_id):
    """Delete a task from Excel."""
    tasks_df = read_tasks_from_excel()
    tasks_df = tasks_df[tasks_df["task_id"] != task_id]
    save_tasks_to_excel(tasks_df)

def calculate_performance_score(tasks_df):
    """Calculate performance score (-100 to 0)."""
    if tasks_df.empty:
        return 0.0
    
    score = 0.0
    now = datetime.now()
    
    for _, task in tasks_df.iterrows():
        if task["status"] == "completed":
            continue
        
        due_date = task["due_date"]
        if pd.isna(due_date):
            continue
        
        if due_date < now:
            days_overdue = (now - due_date).days
            score -= 10 + (days_overdue * 5)
        else:
            score -= 2
    
    return max(score, -100.0)

def get_completion_stats(tasks_df):
    """Get completion statistics."""
    total = len(tasks_df)
    if total == 0:
        return {"total": 0, "completed": 0, "pending": 0, "overdue": 0, "completion_rate": 100.0}
    
    completed = len(tasks_df[tasks_df["status"] == "completed"])
    pending = len(tasks_df[tasks_df["status"] == "pending"])
    overdue = len(tasks_df[(tasks_df["status"] != "completed") & (tasks_df["due_date"] < datetime.now())])
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "completion_rate": round((completed / total) * 100, 1)
    }

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZE
# ═══════════════════════════════════════════════════════════════════════════════

# Create Excel file if not exists
create_initial_excel()

# Session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def login_page():
    st.title("🚗 Premsons Motors — Task Management")
    
    # Show Excel file status
    if EXCEL_FILE.exists():
        file_time = datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE))
        st.caption(f"📁 Excel File: `{EXCEL_FILE}` | Last modified: {file_time.strftime('%d %b %Y %H:%M')}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Login")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary", use_container_width=True):
            user = authenticate_user(email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid email or password")
        
        st.markdown("---")
        with st.expander("📋 Demo Credentials"):
            st.code("""
Admin:
  Email: admin@premsonsmotor.com
  Password: admin@123

Doers:
  Email: vivek.premsons@gmail.com
  Password: premsons@123
  
  (All doers use password: premsons@123)
            """)

# ═══════════════════════════════════════════════════════════════════════════════
# DOER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def doer_dashboard():
    user = st.session_state.user
    
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.title(f"📋 My Tasks")
        st.caption(f"**{user['name']}** | {user['department']}")
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Show Excel file info
    if EXCEL_FILE.exists():
        file_time = datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE))
        st.caption(f"📁 Data from: `{EXCEL_FILE}` | Last updated: {file_time.strftime('%d %b %Y %H:%M')}")
    
    col1, col2 = st.columns([2, 2])
    with col1:
        filter_date = st.date_input("📅 Filter by date", value=date.today())
    with col2:
        view_all = st.checkbox("Show all tasks")
    
    # Read fresh data from Excel
    all_tasks = read_tasks_from_excel()
    my_tasks = all_tasks[all_tasks["user_id"] == user["user_id"]].copy()
    
    if not view_all:
        my_tasks = my_tasks[my_tasks["due_date"].dt.date == filter_date]
    
    my_tasks = my_tasks.sort_values("due_date")
    
    stats = get_completion_stats(my_tasks)
    score = calculate_performance_score(my_tasks)
    
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", stats["total"])
    col2.metric("✅ Done", stats["completed"])
    col3.metric("⏳ Pending", stats["pending"])
    col4.metric("⚠️ Overdue", stats["overdue"])
    
    score_icon = "🟢" if score >= -20 else "🟡" if score >= -50 else "🔴"
    col5.metric(f"{score_icon} Score", f"{score:.0f}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stats["completion_rate"],
            title={"text": "Completion %"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2ecc71"},
                "steps": [
                    {"range": [0, 50], "color": "#ffebee"},
                    {"range": [50, 80], "color": "#fff8e1"},
                    {"range": [80, 100], "color": "#e8f5e9"}
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if stats["total"] > 0:
            fig = px.pie(
                values=[stats["completed"], stats["pending"]],
                names=["Completed", "Pending"],
                color_discrete_sequence=["#2ecc71", "#e74c3c"],
                hole=0.4
            )
            fig.update_layout(height=250, margin=dict(t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📝 Tasks")
    
    if my_tasks.empty:
        st.info("No tasks found for selected date.")
    else:
        for idx, task in my_tasks.iterrows():
            is_overdue = task["status"] == "pending" and pd.notna(task["due_date"]) and task["due_date"].date() < date.today()
            icon = "✅" if task["status"] == "completed" else "🔴" if is_overdue else "⏳"
            due_str = task["due_date"].strftime("%d %b %Y") if pd.notna(task["due_date"]) else "N/A"
            
            with st.expander(f"{icon} {task['task_title']} — Due: {due_str}"):
                st.write(f"**Task ID:** {task['task_id']}")
                st.write(f"**Description:** {task['description']}")
                st.write(f"**Status:** {task['status'].upper()}")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if task["status"] == "pending":
                        if st.button("✅ Complete", key=f"c_{task['task_id']}"):
                            update_task_status(task["task_id"], "completed")
                            st.rerun()
                    else:
                        if st.button("↩️ Reopen", key=f"r_{task['task_id']}"):
                            update_task_status(task["task_id"], "pending")
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def admin_dashboard():
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.title("📊 Administrator Dashboard")
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Show Excel file info
    if EXCEL_FILE.exists():
        file_time = datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE))
        st.caption(f"📁 Data from: `{EXCEL_FILE}` | Last updated: {file_time.strftime('%d %b %Y %H:%M')}")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "👥 Employee Reports", 
        "➕ Add Task", 
        "📤 CSV Upload",
        "📥 Export"
    ])
    
    # Read fresh data from Excel
    users_df = read_users_from_excel()
    tasks_df = read_tasks_from_excel()
    doers = users_df[users_df["role"] == "doer"]
    
    tasks_with_info = tasks_df.merge(users_df[["user_id", "name", "department"]], on="user_id", how="left")
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1: Overview
    # ─────────────────────────────────────────────────────────────────────────
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            dept_options = ["All"] + list(doers["department"].unique())
            selected_dept = st.selectbox("Department", dept_options)
        
        with col2:
            if selected_dept == "All":
                filtered_doers = doers
            else:
                filtered_doers = doers[doers["department"] == selected_dept]
            
            doer_options = ["All"] + filtered_doers["user_id"].tolist()
            selected_doer = st.selectbox("Employee", doer_options)
        
        with col3:
            start_date = st.date_input("From", value=date.today() - timedelta(days=30))
        with col4:
            end_date = st.date_input("To", value=date.today() + timedelta(days=7))
        
        filtered_tasks = tasks_with_info.copy()
        
        if selected_dept != "All":
            filtered_tasks = filtered_tasks[filtered_tasks["department"] == selected_dept]
        if selected_doer != "All":
            filtered_tasks = filtered_tasks[filtered_tasks["user_id"] == selected_doer]
        
        if not filtered_tasks.empty:
            filtered_tasks = filtered_tasks[
                (filtered_tasks["due_date"].dt.date >= start_date) &
                (filtered_tasks["due_date"].dt.date <= end_date)
            ]
        
        stats = get_completion_stats(filtered_tasks)
        
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📋 Total", stats["total"])
        col2.metric("✅ Completed", stats["completed"])
        col3.metric("⏳ Pending", stats["pending"])
        col4.metric("⚠️ Overdue", stats["overdue"])
        col5.metric("📊 Rate", f"{stats['completion_rate']}%")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Daily Trend")
            if not filtered_tasks.empty:
                daily = filtered_tasks.copy()
                daily["date"] = daily["due_date"].dt.date
                trend = daily.groupby(["date", "status"]).size().unstack(fill_value=0).reset_index()
                
                fig = px.bar(trend, x="date", y=[c for c in trend.columns if c != "date"],
                            barmode="stack", color_discrete_map={"completed": "#2ecc71", "pending": "#e74c3c"})
                fig.update_layout(height=300, xaxis_title="", yaxis_title="Tasks")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Performance Ranking")
            if not filtered_tasks.empty:
                perf_data = []
                for uid in filtered_tasks["user_id"].unique():
                    user_tasks = filtered_tasks[filtered_tasks["user_id"] == uid]
                    score = calculate_performance_score(user_tasks)
                    name = user_tasks["name"].iloc[0] if "name" in user_tasks.columns else uid
                    perf_data.append({"Employee": name, "Score": score})
                
                perf_df = pd.DataFrame(perf_data).sort_values("Score", ascending=True)
                
                fig = px.bar(perf_df, x="Score", y="Employee", orientation="h",
                            color="Score", color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
                            range_color=[-100, 0])
                fig.update_layout(height=300, xaxis_range=[-100, 0])
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚠️ Overdue Tasks")
        
        overdue = filtered_tasks[
            (filtered_tasks["status"] == "pending") &
            (filtered_tasks["due_date"] < datetime.now())
        ].copy()
        
        if not overdue.empty:
            overdue["days_overdue"] = (datetime.now() - overdue["due_date"]).dt.days
            display = overdue[["task_id", "user_id", "name", "task_title", "due_date", "days_overdue"]].copy()
            display.columns = ["Task ID", "User ID", "Employee", "Task", "Due Date", "Days Late"]
            display["Due Date"] = pd.to_datetime(display["Due Date"]).dt.strftime("%d %b %Y")
            st.dataframe(display, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No overdue tasks!")
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2: Employee Reports
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("👥 Individual Employee Reports")
        
        for dept in doers["department"].unique():
            st.markdown(f"### 🏢 {dept} Department")
            
            dept_doers = doers[doers["department"] == dept]
            
            for _, doer in dept_doers.iterrows():
                user_tasks = tasks_with_info[tasks_with_info["user_id"] == doer["user_id"]]
                
                user_stats = get_completion_stats(user_tasks)
                user_score = calculate_performance_score(user_tasks)
                
                icon = "🟢" if user_score >= -20 else "🟡" if user_score >= -50 else "🔴"
                
                with st.expander(f"{icon} {doer['name']} ({doer['user_id']}) — Score: {user_score:.0f}"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total", user_stats["total"])
                    col2.metric("Done", user_stats["completed"])
                    col3.metric("Pending", user_stats["pending"])
                    col4.metric("Rate", f"{user_stats['completion_rate']}%")
                    
                    if not user_tasks.empty:
                        st.dataframe(
                            user_tasks[["task_id", "task_title", "due_date", "status"]],
                            use_container_width=True, hide_index=True
                        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3: Add Single Task
    # ─────────────────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("➕ Create New Task")
        
        with st.form("new_task"):
            col1, col2 = st.columns(2)
            
            with col1:
                dept = st.selectbox("Department", doers["department"].unique(), key="add_dept")
                dept_doers = doers[doers["department"] == dept]
                assignee = st.selectbox("Assign To", dept_doers["user_id"].tolist(),
                                       format_func=lambda x: f"{dept_doers[dept_doers['user_id']==x]['name'].values[0]} ({x})",
                                       key="add_assignee")
            
            with col2:
                title = st.text_input("Task Title")
                due = st.date_input("Due Date", min_value=date.today(), key="add_due")
            
            desc = st.text_area("Description")
            
            if st.form_submit_button("Create Task", type="primary"):
                if title.strip():
                    task_id = add_task(assignee, title.strip(), desc, due)
                    st.success(f"✅ Task **{task_id}** created!")
                    st.rerun()
                else:
                    st.error("Enter task title")
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4: CSV Bulk Upload
    # ─────────────────────────────────────────────────────────────────────────
    with tab4:
        st.subheader("📤 Bulk Upload Tasks via CSV")
        
        st.markdown("**📋 Valid Employee IDs:**")
        st.dataframe(doers[["user_id", "name", "department"]], use_container_width=True, hide_index=True, height=200)
        
        st.markdown("---")
        
        sample_csv = """user_id,task_title,description,due_date
PS1,Daily Sales Report,Submit sales numbers,2026-07-01
PS2,Customer Follow-up,Call pending leads,2026-07-02
PSD,Inventory Check,Verify stock,2026-07-03"""
        
        st.download_button("📥 Download CSV Template", sample_csv, "tasks_template.csv", "text/csv")
        
        uploaded_file = st.file_uploader("📁 Upload CSV File", type=["csv"])
        
        if uploaded_file:
            try:
                upload_df = pd.read_csv(uploaded_file)
                
                required_cols = ["user_id", "task_title", "due_date"]
                missing = [c for c in required_cols if c not in upload_df.columns]
                
                if missing:
                    st.error(f"Missing columns: {', '.join(missing)}")
                else:
                    if "description" not in upload_df.columns:
                        upload_df["description"] = ""
                    
                    valid_ids = set(doers["user_id"].tolist())
                    upload_df["valid"] = upload_df["user_id"].isin(valid_ids)
                    
                    valid_tasks = upload_df[upload_df["valid"]]
                    invalid_tasks = upload_df[~upload_df["valid"]]
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total", len(upload_df))
                    col2.metric("✅ Valid", len(valid_tasks))
                    col3.metric("❌ Invalid", len(invalid_tasks))
                    
                    if not invalid_tasks.empty:
                        st.warning(f"Invalid user_ids: {invalid_tasks['user_id'].tolist()}")
                    
                    if not valid_tasks.empty:
                        st.dataframe(valid_tasks[["user_id", "task_title", "due_date"]], hide_index=True)
                        
                        if st.button("🚀 Import Tasks", type="primary"):
                            tasks_list = valid_tasks.to_dict('records')
                            count = add_bulk_tasks(tasks_list)
                            st.success(f"✅ Imported {count} tasks!")
                            st.balloons()
                            st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 5: Export Data
    # ─────────────────────────────────────────────────────────────────────────
    with tab5:
        st.subheader("📥 Export Data")
        
        st.markdown(f"**📁 Excel File Location:** `{EXCEL_FILE.absolute()}`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Download Excel")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                users_df.to_excel(writer, sheet_name='users', index=False)
                tasks_df.to_excel(writer, sheet_name='tasks', index=False)
            
            st.download_button(
                "📥 Download Excel",
                buffer.getvalue(),
                f"premsons_data_{date.today()}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.markdown("### Download CSV")
            st.download_button(
                "📥 Download Tasks CSV",
                tasks_df.to_csv(index=False),
                f"tasks_{date.today()}.csv",
                "text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        st.info("""
        **💡 How to update data via Excel:**
        1. Open the Excel file: `premsons_tasks.xlsx`
        2. Edit the `tasks` sheet (add/modify/delete rows)
        3. Save the Excel file
        4. Click **🔄 Refresh** on the dashboard
        """)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    if not st.session_state.authenticated:
        login_page()
    elif st.session_state.user["role"] == "admin":
        admin_dashboard()
    else:
        doer_dashboard()

if __name__ == "__main__":
    main()
