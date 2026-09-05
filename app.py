import streamlit as st
from modules.auth import init_session_state, login_as_guest, login_with_google, logout, is_user_logged_in, get_current_user
from modules.database import get_user_results, get_all_user_stats, get_or_create_user

st.set_page_config(page_title="AI Interview Simulator", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state
init_session_state()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* ── ANIMATIONS ── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-50px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(50px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(0,188,212,0.5); }
    50% { box-shadow: 0 0 20px rgba(0,188,212,0.8); }
}

@keyframes staggerFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

    .stApp {
        background: linear-gradient(160deg, #ffffff 0%, #e0f7fa 50%, #b2ebf2 100%);
        color: #1a1a1a;
    }
    header { visibility: hidden; }
    /* Hide sidebar */
    [data-testid="collapsedControl"] { visibility: hidden; }
    [data-testid="stSidebarNav"] { display: none; }
    .stSidebar { display: none; }
    .block-container { padding: 3rem 4rem !important; max-width: 1400px !important; margin: 0 auto !important; }
    h1, h2, h3, h4, h5, h6 { letter-spacing: -0.5px !important; line-height: 1.3 !important; }
    p { line-height: 1.6 !important; }

    .hero-title {
        text-align: center;
        font-size: 3.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0097a7 0%, #00bcd4 50%, #00838f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        padding-top: 2rem;
        animation: slideInLeft 0.8s ease-out;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    .hero-sub {
        text-align: center;
        color: #4a5568;
        font-size: 1.25rem;
        margin-bottom: 3rem;
        animation: slideInRight 0.8s ease-out 0.2s backwards;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    
    /* Login Card Styles */
    .login-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 3rem 0;
        flex-wrap: wrap;
    }
    
    .login-card {
        background: white;
        border-radius: 18px;qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
        padding: 2.5rem 2rem;
        border: 1px solid #e8f4f8;
        box-shadow: 0 8px 32px rgba(0,97,167,0.08);
        text-align: center;
        min-width: 300px;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        animation: staggerFadeIn 0.6s ease-out;
    }
    
    .login-card:hover {
        border-color: #b2ebf2;
        box-shadow: 0 16px 48px rgba(0,188,212,0.15);
        transform: translateY(-12px);
    }
    
    .login-card-icon {
        font-size: 3.2rem;
        margin-bottom: 1.2rem;
        display: inline-block;
        background: linear-gradient(135deg, #e0f7fa, #b2ebf2);
        padding: 1rem;
        border-radius: 16px;
    }
    
    .login-card-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0d1117;
        margin-bottom: 0.75rem;
        letter-spacing: -0.3px;
    }
    
    .login-card-desc {
        font-size: 0.95rem;
        color: #4a5568;
        margin-bottom: 1.8rem;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #0097a7 0%, #00bcd4 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2.2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 6px 20px rgba(0,188,212,0.25) !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 12px 35px rgba(0,188,212,0.35) !important;
        transform: translateY(-4px) scale(1.02) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.97) !important;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        border: 1px solid #e8f4f8;
        box-shadow: 0 8px 24px rgba(0,97,167,0.08);
        height: 100%;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        animation: staggerFadeIn 0.6s ease-out;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 16px 40px rgba(0,188,212,0.18);
        border-color: #b2ebf2;
    }
    .feature-icon { 
        font-size: 2.8rem; 
        margin-bottom: 1rem; 
        display: inline-block;
        background: linear-gradient(135deg, #e0f7fa, #b2ebf2);
        padding: 0.8rem;
        border-radius: 14px;
    }
    .feature-title { font-size: 1.15rem; font-weight: 700; color: #0d1117; margin-bottom: 0.75rem; letter-spacing: -0.3px; }
    .feature-desc { font-size: 0.95rem; color: #4a5568; line-height: 1.6; font-weight: 500; }
    
    /* User Profile Section */
    .user-profile-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid #e0f7fa;
        box-shadow: 0 2px 10px rgba(0,188,212,0.08);
    }
    
    .user-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .user-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #00bcd4;
    }
    
    .user-details h2 {
        margin: 0;
        color: #0097a7;
        font-size: 1.2rem;
    }
    
    .user-details p {
        margin: 0;
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0097a7;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #00838f;
        font-weight: 600;
    }
    
    /* History Section */
    .history-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        border: 1px solid #e0f7fa;
        box-shadow: 0 2px 10px rgba(0,188,212,0.08);
    }
    
    .history-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0097a7;
        margin-bottom: 1rem;
    }
    
    .history-item {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .history-date {
        color: #666;
        font-size: 0.9rem;
    }
    
    .history-score {
        background: linear-gradient(90deg, #00bcd4, #0097a7);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
    }
    
    hr { border-color: rgba(0,188,212,0.2); }
    
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
    
    .stTextInput > div > div > input:focus {
        border-color: #0097a7 !important;
        box-shadow: 0 0 0 4px rgba(0,188,212,0.15) !important;
        background-color: white !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: #1a1a1a !important;
        border: 2px solid #00bcd4 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #0097a7 !important;
        box-shadow: 0 0 0 3px rgba(0,188,212,0.1) !important;
    }
    
    /* Label Styling */
    .stTextInput > label, .stTextArea > label {
        color: #0097a7 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Metric Styling */
    [data-testid="stMetricContainer"] {
        background-color: #f0f9fb !important;
        border: 2px solid #00bcd4 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #0097a7 !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #00838f !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    
    /* Info Box Styling */
    [data-testid="stAlert"] {
        background-color: #e8f5e9 !important;
        color: #1b5e20 !important;
        border: 2px solid #4caf50 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    [data-testid="stAlert"] p {
        color: #1b5e20 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Expander Styling */
    [data-testid="stExpander"] {
        border: 2px solid #00bcd4 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    [data-testid="stExpander"] > div:first-child {
        background-color: #e0f7fa !important;
        border-bottom: 2px solid #00bcd4 !important;
    }
    
    [data-testid="stExpander"] > div:first-child p {
        color: #0097a7 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stExpanderContent"] {
        background-color: #ffffff !important;
        padding: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Show login/guest screen if not logged in
if not is_user_logged_in():
    # Hero
    st.markdown('<div class="hero-title">AI Interview Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Practice smarter · get AI feedback · prepare with confidence</div>', unsafe_allow_html=True)
    
    # Login Options
    st.markdown("---")
    st.markdown('<h3 style="text-align: center; color: #0097a7; margin-bottom: 2rem;">Get Started</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # Google Login
        st.markdown("""
        <div class="login-card">
            <div class="login-card-icon">🔐</div>
            <div class="login-card-title">Login with Google</div>
            <div class="login-card-desc">Sign in securely with your Google account to save your interview results</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔗 Continue with Google", key="google_login", use_container_width=True):
            st.session_state.show_google_input = True
            st.rerun()
    
    with col2:
        # Guest Login
        st.markdown("""
        <div class="login-card">
            <div class="login-card-icon">👤</div>
            <div class="login-card-title">Continue as Guest</div>
            <div class="login-card-desc">Take the interview without saving results (no account needed)</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start as Guest", key="guest_login", use_container_width=True):
            login_as_guest()
            st.session_state.show_interview_features = True
            st.rerun()
    
    # Google Email Input (shown when user clicks Google login)
    if st.session_state.get('show_google_input', False):
        st.markdown("---")
        st.markdown("### Google Login")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            email = st.text_input("Enter your Gmail address:", placeholder="your.email@gmail.com")
        with col2:
            manual_login = st.button("Sign In", key="manual_google_signin")
        
        if manual_login and email:
            email = email.lower().strip()  # Normalize email
            if '@gmail.com' in email or '@google.com' in email:
                # Show role selection dialog
                st.session_state.show_role_selection = True
                st.session_state.google_email = email
                st.session_state.google_name = email.split('@')[0].replace('.', ' ').title()
                st.session_state.show_google_input = False
                st.rerun()
            else:
                st.error("Please enter a valid Gmail address")
        
        if st.button("Cancel", key="cancel_google"):
            st.session_state.show_google_input = False
            st.rerun()
    
    # Role Selection (shown after Google login email entry)
    if st.session_state.get('show_role_selection', False):
        st.markdown("---")
        st.markdown("### Select Your Role")
        st.info("Choose your role to get started:")
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("""
            <div class="login-card">
                <div class="login-card-icon">👨‍💼</div>
                <div class="login-card-title">Interviewer</div>
                <div class="login-card-desc">Schedule interviews for employees and view their results</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue as Interviewer", key="role_interviewer", use_container_width=True):
                email = st.session_state.google_email
                name = st.session_state.google_name
                get_or_create_user(email, name, None, role='interviewer')
                login_with_google(email, name, None, role='interviewer')
                st.session_state.show_role_selection = False
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="login-card">
                <div class="login-card-icon">👤</div>
                <div class="login-card-title">Employee</div>
                <div class="login-card-desc">Practice interviews and get AI feedback</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue as Employee", key="role_employee", use_container_width=True):
                email = st.session_state.google_email
                name = st.session_state.google_name
                get_or_create_user(email, name, None, role='employee')
                login_with_google(email, name, None, role='employee')
                st.session_state.show_role_selection = False
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.get('show_interview_features', False):
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Cards (visible when logged in or on initial page)
    if st.session_state.get('show_interview_features', False) or not st.session_state.get('show_google_input', False):
        st.markdown("<h3 style='text-align: center; color: #0097a7; margin-top: 3rem;'>What You'll Get</h3>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Resume Parsing</div>
                <div class="feature-desc">Upload a PDF resume — AI extracts skills and experience</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">❓</div>
                <div class="feature-title">Smart Questions</div>
                <div class="feature-desc">Personalized interview questions generated from your profile</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📹</div>
                <div class="feature-title">Emotion Detection</div>
                <div class="feature-desc">Optional live camera analysis for nonverbal feedback</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Instant Feedback</div>
                <div class="feature-desc">Receive concise scores and actionable tips after each round</div>
            </div>""", unsafe_allow_html=True)

else:
    # User is logged in - show their dashboard
    user = get_current_user()
    
    # Top bar with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        role_badge = f"<span style='background: #00bcd4; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700; margin-left: 0.5rem;'>{user['role'].upper()}</span>"
        st.markdown(f"<h1 style='color: #0097a7; margin-bottom: 0;'>Welcome, {user['name']}! 👋 {role_badge}</h1>", unsafe_allow_html=True)
        if not user['is_guest']:
            st.markdown(f"<p style='color: #666; margin: 0;'>{user['email']}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #666; margin: 0;'>Guest User - Results won't be saved</p>", unsafe_allow_html=True)
    
    with col2:
        if st.button("Logout", key="logout_btn"):
            logout()
            st.rerun()
    
    st.markdown("---")
    
    # Show different dashboard based on user role
    if user['role'] == 'interviewer':
        # INTERVIEWER DASHBOARD
        st.markdown("<h2 style='color: #0097a7;'>📋 Interviewer Dashboard</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Schedule Interviews", "Scheduled Interviews"])
        
        with tab1:
            st.markdown("#### Schedule an Interview for an Employee")
            
            col1, col2 = st.columns(2)
            with col1:
                user_email = st.text_input("Employee Email:")
                user_name = st.text_input("Employee Name:")
            with col2:
                notes = st.text_area("Interview Notes (optional):")
            
            if st.button("📅 Schedule Interview", use_container_width=True):
                if user_email and user_name:
                    from modules.database import schedule_interview
                    schedule_interview(user['email'], user_email, user_name, notes)
                    st.success(f"✅ Interview scheduled for {user_name}!")
                    st.rerun()
                else:
                    st.error("Please fill in employee email and name")
        
        with tab2:
            st.markdown("#### Interviews Scheduled by You")
            from modules.database import get_scheduled_interviews_by_admin
            
            scheduled = get_scheduled_interviews_by_admin(user['email'])
            if scheduled:
                for idx, interview in enumerate(scheduled):
                    with st.expander(f"📝 {interview['user_name']} ({interview['user_email']}) - {interview['status'].upper()}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Scheduled Date", interview['scheduled_at'][:10])
                        with col2:
                            st.metric("Status", interview['status'])
                        with col3:
                            if interview['notes']:
                                st.info(f"Notes: {interview['notes']}")
            else:
                st.info("No scheduled interviews yet")
        
        st.markdown("---")
        
        st.markdown("<h2 style='color: #0097a7;'>🚀 Quick Actions</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 View All Users", use_container_width=True):
                st.switch_page("pages/3_Admin.py")
        with col2:
            if st.button("📈 Analytics", use_container_width=True):
                st.switch_page("pages/3_Admin.py")
        with col3:
            if st.button("👥 Manage Users", use_container_width=True):
                st.switch_page("pages/3_Admin.py")
    
    else:
        # EMPLOYEE DASHBOARD
        # Show previous interview results if not guest
        if not user['is_guest']:
            # Get user stats
            stats = get_all_user_stats(user['email'])
            
            if stats['total_attempts'] > 0:
                # Stats Grid
                st.markdown('<div style="margin-bottom: 2rem;">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{stats['total_attempts']}</div>
                        <div class="stat-label">Total Attempts</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{stats['avg_score']}</div>
                        <div class="stat-label">Average Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{stats['best_score']}</div>
                        <div class="stat-label">Best Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{stats['worst_score']}</div>
                        <div class="stat-label">Worst Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Previous Results
                results = get_user_results(user['email'])
                if results:
                    st.markdown('<div class="history-section">', unsafe_allow_html=True)
                    st.markdown('<div class="history-title">📋 Previous Interview Attempts</div>', unsafe_allow_html=True)
                    
                    for idx, result in enumerate(results[:5]):  # Show last 5 attempts
                        st.markdown(f"""
                        <div class="history-item">
                            <div>
                                <strong>Interview #{len(results) - idx}</strong><br>
                                <small class="history-date">{result['date']}</small>
                            </div>
                            <div class="history-score">{result['overall_score']:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Show scheduled interviews from interviewers
        from modules.database import get_scheduled_interviews_for_user
        scheduled = get_scheduled_interviews_for_user(user['email'])
        if scheduled:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #0097a7;'>📅 Interviews Scheduled for You</h3>", unsafe_allow_html=True)
            for interview in scheduled:
                with st.expander(f"📝 Scheduled by {interview['scheduled_by']} - {interview['status'].upper()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Scheduled Date", interview['scheduled_at'][:10])
                        st.metric("Status", interview['status'])
                    with col2:
                        if interview['notes']:
                            st.info(f"Notes: {interview['notes']}")
                    
                    if interview['status'] == 'pending':
                        if st.button("▶️ Start Scheduled Interview", key=f"start_{interview['id']}", use_container_width=True):
                            st.switch_page("pages/1_Interview.py")
        
        # Start Interview Button
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Practice Interview", key="start_interview", use_container_width=True):
                st.switch_page("pages/1_Interview.py")
    
    st.markdown("---")
    
    # Feature Cards
    st.markdown("<h3 style='text-align: center; color: #0097a7; margin-bottom: 2rem;'>How It Works</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Resume Parsing</div>
            <div class="feature-desc">Upload a PDF resume — AI extracts skills and experience</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">❓</div>
            <div class="feature-title">Smart Questions</div>
            <div class="feature-desc">Personalized interview questions generated from your profile</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📹</div>
            <div class="feature-title">Emotion Detection</div>
            <div class="feature-desc">Optional live camera analysis for nonverbal feedback</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Instant Feedback</div>
            <div class="feature-desc">Receive concise scores and actionable tips after each round</div>
        </div>""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; color:#9aa7ad; font-size:0.8rem; margin-top:2.5rem; padding-bottom:1rem;">
  © 2026 AI Interview Simulator • Built for practice and preparation
</div>
""", unsafe_allow_html=True)
