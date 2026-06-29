"""
Premsons Motors - Task Management Dashboard
Deployed on Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import hashlib
import json
import os

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Premsons Task Dashboard", page_icon="🚗", layout="wide")

DEFAULT_PASSWORD = "premsons@123"
ADMIN_PASSWORD = "admin@123"

# ═══════════════════════════════════════════════════════════════════════════════
# DOER DATA
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
# DATA MANAGEMENT (Using Session State for Cloud)
# ═══════════════════════════════════════════════════════════════════════════════

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_data():
    """Initialize data in session state."""
    if "data_initialized" in st.session_state:
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
    
    st.session_state.users_df = pd.DataFrame(users_data)
    
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
        "Monthly target review",
    ]
    
    tasks_data = []
    task_counter = 1
    today = datetime.now().date()
    
    for doer in DOERS_DATA:
        if doer["department"] == "SALES":
            for i in range(random.randint(3, 5)):
                due_offset = random.randint(-3, 5)
                status = "completed" if due_offset < -1 and random.random() > 0.4 else "pending"
                
                tasks_data.append({
                    "task_id": f"T{task_counter:04d}",
                    "user_id": doer["user_id"],
                    "task_title": random.choice(sample_tasks),
                    "description": f"Daily task for {doer['name']}",
                    "assigned_date": pd.Timestamp(today - timedelta(days=3)),
                    "due_date": pd.Timestamp(today + timedelta(days=due_offset)),
                    "status": status,
                    "completed_date": pd.Timestamp(today + timedelta(days=due_offset - 1)) if status == "completed" else pd.NaT
                })
                task_counter += 1
    
    st.session_state.tasks_df = pd.DataFrame(tasks_data)
    st.session_state.data_initialized = True

def get_users():
    return st.session_state.users_df

def get_tasks():
    return st.session_state.tasks_df

def update_task_status(task_id, new_status):
    mask = st.session_state.tasks_df["task_id"] == task_id
    st.session_state.tasks_df.loc[mask, "status"] = new_status
    if new_status == "completed":
        st.session_state.tasks_df.loc[mask, "completed_date"] = pd.Timestamp(datetime.now())
    else:
        st.session_state.tasks_df.loc[mask, "completed_date"] = pd.NaT

def add_task(user_id, title, description, due_date):
    tasks_df = st.session_state.tasks_df
    
    if tasks_df.empty:
        new_id = "T0001"
    else:
        max_num = tasks_df["task_id"].str.extract(r"T(\d+)")[0].astype(int).max()
        new_id = f"T{max_num + 1:04d}"
    
    new_task = pd.DataFrame([{
        "task_id": new_id,
        "user_id": user_id,
        "task_title": title,
        "description": description,
        "assigned_date": pd.Timestamp(datetime.now()),
        "due_date": pd.Timestamp(datetime.combine(due_date, datetime.min.time())),
        "status": "pending",
        "completed_date": pd.NaT
    }])
    
    st.session_state.tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
    return new_id

def authenticate_user(email, password):
    users_df = get_users()
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

def calculate_performance_score(tasks_df):
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

initialize_data()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def login_page():
    st.title("🚗 Premsons Motors — Task Management")
    
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
    
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title(f"📋 My Tasks")
        st.caption(f"**{user['name']}** | {user['department']}")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    col1, col2 = st.columns([2, 2])
    with col1:
        filter_date = st.date_input("📅 Filter by date", value=date.today())
    with col2:
        view_all = st.checkbox("Show all tasks")
    
    all_tasks = get_tasks()
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
        st.info("No tasks found.")
    else:
        for idx, task in my_tasks.iterrows():
            is_overdue = task["status"] == "pending" and pd.notna(task["due_date"]) and task["due_date"].date() < date.today()
            icon = "✅" if task["status"] == "completed" else "🔴" if is_overdue else "⏳"
            due_str = task["due_date"].strftime("%d %b") if pd.notna(task["due_date"]) else "N/A"
            
            with st.expander(f"{icon} {task['task_title']} — Due: {due_str}"):
                st.write(f"**Description:** {task['description']}")
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if task["status"] == "pending":
                        if st.button("✅ Complete", key=f"c_{task['task_id']}_{idx}"):
                            update_task_status(task["task_id"], "completed")
                            st.rerun()
                    else:
                        if st.button("↩️ Reopen", key=f"r_{task['task_id']}_{idx}"):
                            update_task_status(task["task_id"], "pending")
                            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def admin_dashboard():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("📊 Administrator Dashboard")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "👥 Employee Reports", "➕ Assign Tasks", "📥 Export Data"])
    
    users_df = get_users()
    tasks_df = get_tasks()
    doers = users_df[users_df["role"] == "doer"]
    
    tasks_with_info = tasks_df.merge(users_df[["user_id", "name", "department"]], on="user_id", how="left")
    
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
            end_date = st.date_input("To", value=date.today())
        
        filtered_tasks = tasks_with_info.copy()
        
        if selected_dept != "All":
            filtered_tasks = filtered_tasks[filtered_tasks["department"] == selected_dept]
        if selected_doer != "All":
            filtered_tasks = filtered_tasks[filtered_tasks["user_id"] == selected_doer]
        
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
            display = overdue[["user_id", "name", "task_title", "due_date", "days_overdue"]].copy()
            display.columns = ["ID", "Employee", "Task", "Due Date", "Days Late"]
            display["Due Date"] = pd.to_datetime(display["Due Date"]).dt.strftime("%d %b %Y")
            st.dataframe(display, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No overdue tasks!")
    
    with tab2:
        st.subheader("👥 Individual Reports")
        
        for dept in doers["department"].unique():
            st.markdown(f"### 🏢 {dept}")
            
            dept_doers = doers[doers["department"] == dept]
            
            for _, doer in dept_doers.iterrows():
                user_tasks = tasks_with_info[tasks_with_info["user_id"] == doer["user_id"]]
                
                if user_tasks.empty:
                    continue
                
                user_stats = get_completion_stats(user_tasks)
                user_score = calculate_performance_score(user_tasks)
                
                icon = "🟢" if user_score >= -20 else "🟡" if user_score >= -50 else "🔴"
                
                with st.expander(f"{icon} {doer['name']} ({doer['user_id']}) — Score: {user_score:.0f}"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total", user_stats["total"])
                    col2.metric("Done", user_stats["completed"])
                    col3.metric("Pending", user_stats["pending"])
                    col4.metric("Rate", f"{user_stats['completion_rate']}%")
                    
                    st.dataframe(
                        user_tasks[["task_title", "due_date", "status"]],
                        use_container_width=True, hide_index=True
                    )
    
    with tab3:
        st.subheader("➕ Create New Task")
        
        with st.form("new_task"):
            col1, col2 = st.columns(2)
            
            with col1:
                dept = st.selectbox("Department", doers["department"].unique(), key="new_dept")
                dept_doers = doers[doers["department"] == dept]
                assignee = st.selectbox("Assign To", dept_doers["user_id"].tolist(),
                                       format_func=lambda x: f"{dept_doers[dept_doers['user_id']==x]['name'].values[0]} ({x})",
                                       key="new_assignee")
            
            with col2:
                title = st.text_input("Task Title")
                due = st.date_input("Due Date", min_value=date.today(), key="new_due")
            
            desc = st.text_area("Description")
            
            if st.form_submit_button("Create Task", type="primary"):
                if title and assignee:
                    task_id = add_task(assignee, title, desc, due)
                    st.success(f"✅ Task {task_id} created!")
                else:
                    st.error("Fill all required fields")
    
    with tab4:
        st.subheader("📥 Export Data to Excel")
        
        import io
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            users_df.to_excel(writer, sheet_name='users', index=False)
            tasks_df.to_excel(writer, sheet_name='tasks', index=False)
        
        st.download_button(
            label="📥 Download Excel File",
            data=buffer.getvalue(),
            file_name="premsons_tasks_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.info("Download the Excel file to keep a backup of all data.")

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
