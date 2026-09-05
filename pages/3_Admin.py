import streamlit as st
from modules.auth import is_user_logged_in, get_current_user, logout
from modules.database import (
    get_scheduled_interviews_by_admin,
    get_scheduled_interviews_for_user,
    schedule_interview,
    update_scheduled_interview_status,
    get_user_results,
    get_user_info,
    get_all_user_stats,
    get_all_users,
    update_user_role,
    get_user_interview_count
)
from modules.email_service import send_scheduled_interview_notification

st.set_page_config(page_title="Interviewer Panel | Interview Simulator", page_icon="🔧", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* ── ANIMATIONS ── */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes cardSlideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,188,212,0.7); }
    50% { box-shadow: 0 0 0 10px rgba(0,188,212,0); }
}

    .stApp {
        background: linear-gradient(160deg, #ffffff 0%, #e0f7fa 50%, #b2ebf2 100%);
        color: #1a1a1a;
    }
    header { visibility: hidden; }
    [data-testid="collapsedControl"] { visibility: hidden; }
    [data-testid="stSidebarNav"] { display: none; }
    .stSidebar { display: none; }
    .block-container { padding: 3rem 4rem !important; max-width: 1400px !important; margin: 0 auto !important; }
    h1, h2, h3, h4, h5, h6 { letter-spacing: -0.5px !important; line-height: 1.3 !important; color: #0d1117 !important; }
    
    .admin-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .admin-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0097a7 0%, #00bcd4 50%, #00838f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    
    .admin-card {
        background: white;
        border-radius: 16px;
        padding: 1.8rem;
        border: 1px solid #e8f4f8;
        box-shadow: 0 8px 32px rgba(0,97,167,0.08);
        margin-bottom: 1.2rem;
        animation: cardSlideIn 0.6s ease-out;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    .admin-card:hover {
        box-shadow: 0 12px 40px rgba(0,188,212,0.15);
        transform: translateY(-6px);
        border-color: #b2ebf2;
    }
    
    .schedule-form {
        background: white;
        border-radius: 16px;
        padding: 2.2rem;
        border: 1px solid #e8f4f8;
        box-shadow: 0 8px 32px rgba(0,97,167,0.08);
        animation: slideInDown 0.6s ease-out;
    }
    
    .interview-item {
        background: white;
        border-radius: 14px;
        padding: 1.4rem;
        border-left: 4px solid #00bcd4;
        box-shadow: 0 8px 24px rgba(0,97,167,0.08);
        margin-bottom: 1.2rem;
        animation: cardSlideIn 0.6s ease-out;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    .interview-item:hover {
        box-shadow: 0 12px 35px rgba(0,188,212,0.15);
        transform: translateX(8px);
        border-left-color: #0097a7;
    }
    
    .status-pending {
        background: #fff3cd;
        color: #856404;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    .status-completed {
        background: #d4edda;
        color: #155724;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    /* Form Input Styling */
    .stTextInput > div > div > input {
        background-color: #f8fbfd !important;
        color: #0d1117 !important;
        border: 1.5px solid #d0e8f0 !important;
        border-radius: 10px !important;
        padding: 0.85rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0097a7 !important;
        box-shadow: 0 0 0 4px rgba(0,188,212,0.15) !important;
        background-color: white !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #f8fbfd !important;
        color: #0d1117 !important;
        border: 1.5px solid #d0e8f0 !important;
        border-radius: 10px !important;
        padding: 0.85rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        font-weight: 500 !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #999 !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #0097a7 !important;
        box-shadow: 0 0 0 4px rgba(0,188,212,0.15) !important;
        background-color: white !important;
    }
    
    /* Label Styling */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stDateInput > label, .stTimeInput > label {
        color: #0097a7 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: color 0.3s ease !important;
        letter-spacing: 0.3px !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #f8fbfd !important;
        border: 1px solid #e8f4f8 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        box-shadow: 0 2px 8px rgba(0,97,167,0.04) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: white !important;
        border-color: #d0e8f0 !important;
        box-shadow: 0 4px 16px rgba(0,188,212,0.12) !important;
    }
    
    .streamlit-expanderHeader p {
        color: #0097a7 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Expander Content */
    .streamlit-expanderContent {
        background-color: #fafcfd !important;
        border: 1px solid #e8f4f8 !important;
        border-top: none !important;
        border-bottom-left-radius: 10px !important;
        border-bottom-right-radius: 10px !important;
    }
    
    /* Metric Styling */
    .stMetricValue {
        color: #0097a7 !important;
        font-weight: 700 !important;
    }
    
    .stMetricLabel {
        color: #00838f !important;
        font-weight: 600 !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #0097a7 !important;
        font-weight: 600 !important;
    }
    
    /* Heading Styling */
    h1, h2, h3, h4, h5, h6 {
        color: #0097a7 !important;
    }
    
    /* Text Styling for Visibility */
    .stText, p {
        color: #1a1a1a !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 6px 20px rgba(0,188,212,0.25) !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0097a7 0%, #00838f 100%) !important;
        box-shadow: 0 10px 30px rgba(0,188,212,0.35) !important;
        transform: translateY(-3px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(0,188,212,0.25) !important;
    }
    
    .stButton > button:focus {
        box-shadow: 0 0 0 4px rgba(0,188,212,0.2), 0 6px 20px rgba(0,188,212,0.25) !important;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div > div {
        background-color: #f8fbfd !important;
        border: 1.5px solid #d0e8f0 !important;
        border-radius: 10px !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    }
    
    .stSelectbox > div > div:hover > div {
        border-color: #00bcd4 !important;
        box-shadow: 0 2px 8px rgba(0,188,212,0.1) !important;
    }
    
    .stSelectbox > div > div > div > button {
        color: #0d1117 !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox [data-testid="stSelectboxOptions"] {
        background-color: white !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #f8fbfd !important;
    }
    
    /* Date Input Styling */
    .stDateInput > div > div > input {
        background-color: #f8fbfd !important;
        color: #0d1117 !important;
        border: 1.5px solid #d0e8f0 !important;
        border-radius: 10px !important;
        padding: 0.85rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        font-weight: 500 !important;
    }
    
    .stDateInput > div > div > input:focus {
        border-color: #0097a7 !important;
        box-shadow: 0 0 0 4px rgba(0,188,212,0.15) !important;
        background-color: white !important;
    }
    
    /* Time Input Styling */
    .stTimeInput > div > div > input {
        background-color: #f8fbfd !important;
        color: #0d1117 !important;
        border: 1.5px solid #d0e8f0 !important;
        border-radius: 10px !important;
        padding: 0.85rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        font-weight: 500 !important;
    }
    
    .stTimeInput > div > div > input:focus {
        border-color: #0097a7 !important;
        box-shadow: 0 0 0 4px rgba(0,188,212,0.15) !important;
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Check if user is logged in
if not is_user_logged_in():
    st.error("❌ Please log in first")
    st.info("Go back to the home page and log in as Interviewer to access the interviewer panel")
    if st.button("← Back to Home"):
        st.switch_page("app.py")
    st.stop()

user = get_current_user()

# Check if user is interviewer
if user['role'] != 'interviewer':
    st.error("❌ Access Denied")
    st.write(f"This page is only accessible to interviewers. Your current role is: **{user['role'].upper()}**")
    if st.button("← Back to Home"):
        st.switch_page("app.py")
    st.stop()

# Interviewer Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="admin-header"><div class="admin-title">🔧 Interviewer Panel</div></div>', unsafe_allow_html=True)
    st.markdown(f"**Interviewer Email:** {user['email']}")
with col2:
    if st.button("Logout", key="logout_btn"):
        logout()
        st.rerun()

st.markdown("---")

# Main tabs
tab1, tab2, tab3 = st.tabs(["📅 Schedule Interviews", "📋 View Scheduled", "📊 Results Dashboard"])

with tab1:
    st.markdown("<h2 style='color: #0097a7;'>Schedule Interview for Employee</h2>", unsafe_allow_html=True)
    
    # Initialize session state for form inputs
    if 'user_email_input' not in st.session_state:
        st.session_state.user_email_input = ""
    if 'user_name_input' not in st.session_state:
        st.session_state.user_name_input = ""
    if 'notes_input' not in st.session_state:
        st.session_state.notes_input = ""
    
    st.markdown("""
    <div class="schedule-form">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        user_email = st.text_input(
            "👤 User Email",
            value=st.session_state.user_email_input,
            placeholder="user@gmail.com",
            help="Email of the user you want to schedule interview for"
        )
    with col2:
        user_name = st.text_input(
            "📝 User Name",
            value=st.session_state.user_name_input,
            placeholder="John Doe",
            help="Full name of the user"
        )
    
    interview_type = st.selectbox(
        "🎯 Interview Type",
        ["Practice", "Scheduled", "Technical Round", "HR Round"],
        help="Type of interview to schedule"
    )
    
    notes = st.text_area(
        "📌 Interview Notes (Optional)",
        value=st.session_state.notes_input,
        placeholder="Add any specific instructions or focus areas...",
        help="Any notes or instructions for the user"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        schedule_button = st.button("✅ Schedule Interview", use_container_width=True, key="schedule_btn")
        
        if schedule_button:
            # Debug: Log what we're receiving
            st.write("🔍 **DEBUG INFO:**")
            st.write(f"- User Email: `{user_email}`")
            st.write(f"- User Name: `{user_name}`")
            st.write(f"- Interview Type: `{interview_type}`")
            st.write(f"- Notes: `{notes}`")
            st.write(f"- Admin Email: `{user['email']}`")
            st.write(f"- Admin Name: `{user['name']}`")
            
            if not user_email or not user_name:
                st.error("⚠️ Please fill in user email and name")
            else:
                with st.spinner("⏳ Scheduling interview and sending notifications..."):
                    try:
                        print(f"\n{'='*60}")
                        print(f"SCHEDULING INTERVIEW")
                        print(f"{'='*60}")
                        print(f"Admin Email: {user['email']}")
                        print(f"User Email: {user_email.lower()}")
                        print(f"User Name: {user_name}")
                        print(f"Interview Type: {interview_type}")
                        print(f"Notes: {notes}")
                        
                        # Database operation
                        schedule_interview(user['email'], user_email.lower(), user_name, notes)
                        print("✅ Interview scheduled in database")
                        
                        # Send to user
                        print(f"\nSending notification to user: {user_email.lower()}")
                        user_email_ok, user_msg = send_scheduled_interview_notification(
                            user_email=user_email.lower(),
                            user_name=user_name,
                            admin_name=user['name'],
                            interview_type=interview_type,
                            notes=notes
                        )
                        print(f"User email result: {user_email_ok} - {user_msg}")
                        
                        # Send to admin
                        print(f"\nSending notification to admin: {user['email']}")
                        admin_email_ok, admin_msg = send_scheduled_interview_notification(
                            user_email=user['email'],
                            user_name=f"{user_name} (Interview Scheduled)",
                            admin_name=user['name'],
                            interview_type=interview_type,
                            notes=f"You scheduled an interview for {user_name} ({user_email})\n\nNotes: {notes}" if notes else f"You scheduled an interview for {user_name} ({user_email})"
                        )
                        print(f"Admin email result: {admin_email_ok} - {admin_msg}")
                        print(f"{'='*60}\n")
                        
                        # Display results AFTER processing
                        st.success(f"✅ Interview scheduled successfully for **{user_name}**!")
                        
                        if user_email_ok:
                            st.info(f"📧 Notification sent to user: {user_email}")
                        else:
                            st.warning(f"⚠️ Failed to send user email: {user_msg}")
                        
                        if admin_email_ok:
                            st.info(f"📧 Confirmation sent to admin: {user['email']}")
                        else:
                            st.warning(f"⚠️ Failed to send admin email: {admin_msg}")
                        
                        st.balloons()
                        
                        # Clear form
                        st.session_state.user_email_input = ""
                        st.session_state.user_name_input = ""
                        st.session_state.notes_input = ""
                        
                    except Exception as e:
                        import traceback
                        error_trace = traceback.format_exc()
                        print(f"❌ ERROR: {str(e)}")
                        print(error_trace)
                        st.error(f"❌ Error scheduling interview: {str(e)}")
                        st.error(f"Details: {error_trace}")
                st.info("✅ Interview scheduled! Page will refresh in 3 seconds...")
                import time
                time.sleep(3)
                st.rerun()
    
    with col2:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.session_state.user_email_input = ""
            st.session_state.user_name_input = ""
            st.session_state.notes_input = ""
            st.rerun()

with tab2:
    st.markdown("<h2 style='color: #0097a7;'>Scheduled Interviews</h2>", unsafe_allow_html=True)
    
    scheduled = get_scheduled_interviews_by_admin(user['email'])
    
    if scheduled:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Scheduled", len(scheduled))
        with col2:
            pending = sum(1 for s in scheduled if s['status'] == 'pending')
            st.metric("Pending", pending)
        with col3:
            completed = sum(1 for s in scheduled if s['status'] == 'completed')
            st.metric("Completed", completed)
        
        st.markdown("---")
        
        for interview in scheduled:
            status_badge = f"<span class='status-{interview['status']}'>{interview['status'].upper()}</span>"
            
            # Get latest results for this user if interview is completed
            latest_result = None
            if interview['status'] == 'completed':
                user_results = get_user_results(interview['user_email'])
                if user_results:
                    latest_result = user_results[0]  # Most recent result
            
            result_info = f"<br><strong>📊 Score: {latest_result['overall_score']:.1f}%</strong><br><small style='color: #0097a7;'>Completed: {latest_result['date']}</small>" if latest_result else ""
            
            st.markdown(f"""
            <div class="interview-item">
                <strong>👤 {interview['user_name']}</strong><br>
                <small style='color: #666;'>{interview['user_email']}</small><br>
                <small style='color: #666;'>📅 Scheduled: {interview['scheduled_at']}</small><br>
                Status: {status_badge}
                {result_info}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if interview['notes']:
                    st.caption(f"📌 Notes: {interview['notes']}")
            
            with col2:
                if st.button("👁️ View Results", key=f"view_results_{interview['id']}"):
                    st.session_state.selected_interview_email = interview['user_email']
                    st.rerun()
            
            with col3:
                if interview['status'] == 'pending':
                    if st.button("✅ Mark Completed", key=f"mark_completed_{interview['id']}"):
                        update_scheduled_interview_status(interview['id'], 'completed')
                        st.success("Interview marked as completed!")
                        st.rerun()
    else:
        st.info("📭 No scheduled interviews yet")

with tab3:
    st.markdown("<h2 style='color: #0097a7;'>Results Dashboard</h2>", unsafe_allow_html=True)
    
    # Show results for selected user
    if 'selected_interview_email' in st.session_state:
        selected_email = st.session_state.selected_interview_email
        user_info = get_user_info(selected_email)
        
        if user_info:
            st.markdown("---")
            st.markdown(f"### Results for {user_info['name']}")
            st.markdown(f"**Email:** {user_info['email']}")
            
            stats = get_all_user_stats(selected_email)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Attempts", stats['total_attempts'])
            with col2:
                st.metric("Avg Score", f"{stats['avg_score']}%")
            with col3:
                st.metric("Best Score", f"{stats['best_score']}%")
            with col4:
                st.metric("Worst Score", f"{stats['worst_score']}%")
            
            results = get_user_results(selected_email)
            
            if results:
                st.markdown("#### Interview History")
                for idx, result in enumerate(results):
                    with st.expander(f"Interview #{idx + 1} - {result['date']} - Score: {result['overall_score']}%"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Score:** {result['overall_score']}%")
                            st.markdown(f"**Questions:** {result['questions_count']}")
                        with col2:
                            st.markdown(f"**Date:** {result['date']}")
                        
                        if result['feedback']:
                            st.markdown("**Feedback:**")
                            st.write(result['feedback'])
            else:
                st.info("No interview results available for this user yet")
        
        if st.button("← Back to Interviews"):
            del st.session_state.selected_interview_email
            st.rerun()
    else:
        st.info("Select a user from the 'View Scheduled' tab to see their results")

st.markdown("---")

st.markdown("<h2 style='color: #0097a7;'>🚀 Quick Actions</h2>", unsafe_allow_html=True)

qaction_tab1, qaction_tab2, qaction_tab3 = st.tabs(["👥 View All Users", "📈 Analytics", "⚙️ Manage Users"])

# Tab 1: View All Users
with qaction_tab1:
    st.markdown("<h3>All Users in System</h3>", unsafe_allow_html=True)
    
    all_users = get_all_users()
    
    if all_users:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            role_filter = st.selectbox("Filter by Role:", ["All", "interviewer", "employee"], key="user_role_filter")
        with col2:
            search_query = st.text_input("Search by email or name:", key="user_search")
        
        # Apply filters
        filtered_users = all_users
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u['role'] == role_filter]
        if search_query:
            search_lower = search_query.lower()
            filtered_users = [u for u in filtered_users if search_lower in u['email'].lower() or (u['name'] and search_lower in u['name'].lower())]
        
        if filtered_users:
            # Display as table
            st.markdown("""
            <style>
                .user-card {
                    background: white;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                    border-left: 4px solid #00bcd4;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                .user-email { color: #0097a7; font-weight: 600; }
                .user-role { 
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }
                .role-interviewer { background: #c8e6c9; color: #2e7d32; }
                .role-employee { background: #bbdefb; color: #1565c0; }
            </style>
            """, unsafe_allow_html=True)
            
            for user in filtered_users:
                interview_count = get_user_interview_count(user['email'])
                role_badge = f'<span class="user-role role-{user["role"]}">{user["role"].upper()}</span>'
                
                st.markdown(f"""
                <div class="user-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div class="user-email">{user['email']}</div>
                            <div style="color: #666; font-size: 14px;">Name: {user['name'] or 'N/A'}</div>
                            <div style="color: #999; font-size: 12px;">Joined: {user['created_at'][:10]}</div>
                        </div>
                        <div style="text-align: right;">
                            {role_badge}
                            <div style="color: #0097a7; font-weight: 600; margin-top: 8px;">{interview_count} interviews</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.success(f"✅ Total users found: {len(filtered_users)}")
        else:
            st.info("No users found matching your filters")
    else:
        st.info("No users in the system yet")

# Tab 2: Analytics
with qaction_tab2:
    st.markdown("<h3>System Analytics</h3>", unsafe_allow_html=True)
    
    all_users = get_all_users()
    interviewer_count = sum(1 for u in all_users if u['role'] == 'interviewer')
    employee_count = sum(1 for u in all_users if u['role'] == 'employee')
    
    # Key Metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Total Users", len(all_users))
    with metric_col2:
        st.metric("Interviewer Accounts", interviewer_count)
    with metric_col3:
        st.metric("Employees", employee_count)
    with metric_col4:
        scheduled_count = len(get_scheduled_interviews_by_admin(user['email']))
        st.metric("Your Scheduled", scheduled_count)
    
    st.markdown("---")
    
    # User Interview Statistics
    st.markdown("<h4>Interview Statistics</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top Active Users**")
        user_interview_counts = []
        for usr in all_users:
            count = get_user_interview_count(usr['email'])
            if count > 0:
                user_interview_counts.append({
                    'email': usr['email'],
                    'name': usr['name'] or usr['email'].split('@')[0],
                    'interviews': count
                })
        
        if user_interview_counts:
            user_interview_counts.sort(key=lambda x: x['interviews'], reverse=True)
            for i, usr_data in enumerate(user_interview_counts[:5], 1):
                st.write(f"{i}. **{usr_data['name']}** - {usr_data['interviews']} interviews")
        else:
            st.info("No interviews completed yet")
    
    with col2:
        st.markdown("**User Distribution**")
        dist_data = {
            'Interviewers': interviewer_count,
            'Employees': employee_count
        }
        if sum(dist_data.values()) > 0:
            st.bar_chart(dist_data)
        else:
            st.info("No user distribution data available")

# Tab 3: Manage Users
with qaction_tab3:
    st.markdown("<h3>Manage User Roles</h3>", unsafe_allow_html=True)
    
    all_users = get_all_users()
    
    if all_users:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_user_email = st.selectbox(
                "Select user to manage:",
                options=[u['email'] for u in all_users],
                format_func=lambda x: f"{x} ({[u['name'] or 'N/A' for u in all_users if u['email'] == x][0]})",
                key="manage_user_select"
            )
        
        # Get selected user details
        selected_user = next((u for u in all_users if u['email'] == selected_user_email), None)
        
        if selected_user:
            with col2:
                st.markdown("**Current Role**")
                st.info(selected_user['role'].upper())
            
            st.markdown("---")
            
            # Show user details
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Email:** {selected_user['email']}")
                st.markdown(f"**Name:** {selected_user['name'] or 'Not set'}")
            with col2:
                st.markdown(f"**Joined:** {selected_user['created_at'][:10]}")
                interview_count = get_user_interview_count(selected_user['email'])
                st.markdown(f"**Interviews:** {interview_count}")
            
            st.markdown("---")
            
            # Role management
            st.markdown("**Change User Role**")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_role = st.selectbox(
                    "New Role:",
                    ["employee", "interviewer"],
                    index=0 if selected_user['role'] == 'employee' else 1,
                    key="new_role_select"
                )
            
            with col2:
                if st.button("✅ Update Role", use_container_width=True):
                    if new_role != selected_user['role']:
                        try:
                            update_user_role(selected_user_email, new_role)
                            st.success(f"✅ Role updated to **{new_role.upper()}**")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating role: {str(e)}")
                    else:
                        st.warning("⚠️ New role is same as current role")
            
            with col3:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
    else:
        st.info("No users available to manage")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align:center; color:#9aa7ad; font-size:0.8rem; margin-top:2rem; padding-bottom:1rem;">
  © 2026 AI Interview Simulator • Admin Panel
</div>
""", unsafe_allow_html=True)
