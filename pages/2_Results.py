import streamlit as st
import json
from datetime import datetime
from modules.evaluator import evaluate_answer
from modules.auth import is_user_logged_in, get_current_user
from modules.database import save_interview_result, get_or_create_user, update_scheduled_interview_status_by_user
from modules.email_service import send_interview_results_email

st.set_page_config(page_title="Results | AI Simulator", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

/* ── ANIMATIONS ── */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes countUp {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes cardFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(0,188,212,0.5); }
    50% { box-shadow: 0 0 20px rgba(0,188,212,0.8); }
}

*, *::before, *::after { box-sizing: border-box; }
body, .stApp { font-family: 'DM Sans', sans-serif; background: #f4fbfc; color: #0d1117; }
header { visibility: hidden; }
/* Hide sidebar */
[data-testid="collapsedControl"] { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none; }
.stSidebar { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Professional Typography */
h1, h2, h3, h4, h5, h6 { letter-spacing: -0.5px !important; line-height: 1.3 !important; color: #0d1117 !important; }
p { line-height: 1.6 !important; }

/* TOPBAR */
.topbar {
    background: white; height: 56px; padding: 0 28px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 2px solid #e0f7fa; margin-bottom: 0;
}
.topbar-logo { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; color:#00bcd4; }

/* PAGE BODY */
.page-body { padding: 24px 32px; }

/* SUMMARY BANNER */
.summary-banner {
    background: white;
    border-radius: 16px;
    border: 1px solid #e0f7fa;
    box-shadow: 0 4px 20px rgba(0,188,212,0.07);
    padding: 24px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    animation: slideDown 0.6s ease-out;
}
.banner-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #0d1117;
    margin-bottom: 4px;
}
.banner-sub { font-size: 0.88rem; color: #718096; }
.banner-stats { display: flex; gap: 16px; }
.bstat {
    background: #f4fbfc;
    border: 1px solid #e0f7fa;
    border-radius: 12px;
    padding: 12px 20px;
    text-align: center;
    min-width: 90px;
}
.bstat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00bcd4, #0097a7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.bstat-label { font-size: 0.72rem; color: #a0aec0; font-weight: 600; margin-top: 4px; letter-spacing: 0.5px; }

/* ROUND RESULTS */
.round-section {
    border-radius: 14px;
    border: 1px solid #e0f7fa;
    background: white;
    margin-bottom: 20px;
    overflow: hidden;
}
.round-header {
    background: linear-gradient(135deg, #f0fafa, #e0f7fa);
    padding: 16px 20px;
    border-bottom: 1px solid #e0f7fa;
}
.round-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    color: #0097a7;
    margin-bottom: 4px;
}
.round-stats {
    display: flex;
    gap: 16px;
    margin-top: 12px;
}
.round-stat-item {
    background: white;
    border: 1px solid #b2ebf2;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #0097a7;
}

/* OVERALL SCORES */
.scores-row { display: flex; gap: 14px; margin-bottom: 24px; flex-wrap: wrap; }
.score-card {
    flex: 1;
    min-width: 150px;
    background: white;
    border-radius: 16px;
    border: 1px solid #e8f4f8;
    box-shadow: 0 8px 24px rgba(0,97,167,0.08);
    padding: 20px;
    text-align: center;
    animation: countUp 0.6s ease-out;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.score-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 35px rgba(0,188,212,0.15);
    border-color: #b2ebf2;
}
.score-icon { font-size: 1.8rem; margin-bottom: 6px; }
.score-num {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00bcd4, #0097a7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}
.score-label { font-size: 0.78rem; color: #718096; font-weight: 600; margin-top: 6px; letter-spacing: 0.5px; }

/* QUESTION CARD */
.q-result-card {
    background: white;
    border-radius: 16px;
    border: 1px solid #e8f4f8;
    box-shadow: 0 8px 24px rgba(0,97,167,0.08);
    margin-bottom: 18px;
    overflow: hidden;
    animation: cardFadeIn 0.6s ease-out;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.q-result-card:hover {
    box-shadow: 0 12px 35px rgba(0,188,212,0.12);
    transform: translateY(-4px);
    border-color: #b2ebf2;
}
.q-result-header {
    background: linear-gradient(135deg, #f0fafa, #e0f7fa);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e0f7fa;
}
.q-result-num {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 800;
    color: #00bcd4;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.q-result-text {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1a202c;
    flex: 1;
    margin: 0 16px;
    line-height: 1.5;
}
.q-mini-scores { display: flex; gap: 8px; flex-wrap: wrap; }
.mini-score {
    background: white;
    border: 1px solid #b2ebf2;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #0097a7;
    white-space: nowrap;
}
.q-result-body { padding: 16px 20px; }
.answer-box {
    background: #f4fbfc;
    border-left: 3px solid #00bcd4;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #2d3748;
    font-style: italic;
    line-height: 1.7;
    margin-bottom: 14px;
}
.feedback-row { display: flex; gap: 12px; flex-wrap: wrap; }
.strength-box {
    flex: 1;
    min-width: 200px;
    background: #f0fff4;
    border: 1px solid #c6f6d5;
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 0.82rem;
    color: #276749;
    line-height: 1.6;
}
.improve-box {
    flex: 1;
    min-width: 200px;
    background: #fffde7;
    border: 1px solid #fff176;
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 0.82rem;
    color: #7a4f00;
    line-height: 1.6;
}
.feedback-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.strength-label { color: #276749; }
.improve-label { color: #b7791f; }

/* OVERALL RESULT */
.overall-result {
    background: white;
    border-radius: 16px;
    border: 2px solid #00bcd4;
    padding: 28px;
    text-align: center;
    margin-bottom: 24px;
}
.final-score {
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00bcd4, #0097a7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 8px;
}
.final-label {
    font-size: 1rem;
    font-weight: 700;
    color: #0097a7;
    margin-bottom: 16px;
}
.final-status {
    font-size: 1.2rem;
    color: #1a202c;
    font-weight: 600;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #00bcd4, #0097a7) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 0.65rem 2rem !important; font-weight: 700 !important;
    font-size: 0.92rem !important; box-shadow: 0 4px 14px rgba(0,188,212,0.28) !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
}
.stButton > button:hover { 
    box-shadow: 0 8px 25px rgba(0,188,212,0.4) !important; 
    transform: translateY(-3px) scale(1.02) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #0d1117;
    margin: 24px 0 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e0f7fa;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: #b2ebf2; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── TOPBAR ────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-logo">Interview Results</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="page-body">', unsafe_allow_html=True)

# Check if we have interview data
if 'all_rounds_data' not in st.session_state or not st.session_state.get('resume_text'):
    st.markdown("""
    <div style="text-align:center; padding:3rem 1rem;">
        <div style="font-size:3rem; margin-bottom:12px;">📄</div>
        <div style="font-family:'Syne',sans-serif; font-size:1rem;
                    color:#00bcd4; font-weight:700;">No interview data found</div>
        <div style="font-size:0.9rem; color:#2d3748; margin-top:8px;">
            Please complete the interview first
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

ROUNDS = ["🧠 Aptitude", "💻 Technical", "🔧 Coding", "👔 HR"]
ROUND_TYPES = ["aptitude", "technical", "coding", "hr"]

all_rounds_data = st.session_state['all_rounds_data']
resume_text = st.session_state.get('resume_text', '')

# Results pages rerun whenever a user interacts with Streamlit. Keep each model
# response for this interview so reruns do not repeat API calls or change scores.
evaluation_cache = st.session_state.setdefault('evaluation_cache', {})
questions_count = sum(
    len(round_data.get('questions', []))
    for round_data in all_rounds_data.values()
)

# Calculate scores for each round
round_scores = {}
all_evaluations = {}

for round_type in ROUND_TYPES:
    round_data = all_rounds_data[round_type]
    questions = round_data.get('questions', [])
    answers = round_data.get('answers', [])
    
    evaluations = []
    scores = []
    
    for i, question in enumerate(questions):
        if i < len(answers) and answers[i] and answers[i].get('answer') != 'SKIPPED':
            answer_text = answers[i].get('answer', '')
            cache_key = f"{round_type}:{i}:{question}:{answer_text}"
            if cache_key not in evaluation_cache:
                evaluation_cache[cache_key] = evaluate_answer(
                    question, answer_text, round_type
                )
            eval_text = evaluation_cache[cache_key]
            evaluations.append(eval_text)
            
            try:
                # Parse JSON response and extract scores
                cleaned_eval_text = eval_text.strip()
                if cleaned_eval_text.startswith("```"):
                    cleaned_eval_text = cleaned_eval_text.split("\n", 1)[-1]
                    cleaned_eval_text = cleaned_eval_text.rsplit("```", 1)[0].strip()
                eval_json = json.loads(cleaned_eval_text)
                avg_score = (eval_json.get('score1', 0) + eval_json.get('score2', 0) + eval_json.get('score3', 0)) / 3
                scores.append(avg_score)
            except (json.JSONDecodeError, TypeError, ValueError):
                scores.append(0)
    
    round_scores[round_type] = {
        'scores': scores,
        'evaluations': evaluations,
        'average': sum(scores) / len(scores) if scores else 0
    }
    all_evaluations[round_type] = evaluations

# Calculate overall score
all_scores = []
for round_type in ROUND_TYPES:
    if round_scores[round_type]['scores']:
        all_scores.extend(round_scores[round_type]['scores'])

overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

# Save results to database if user is logged in (only once per interview)
if is_user_logged_in():
    user = get_current_user()
    if not user['is_guest']:
        # Check if we've already saved this interview to prevent duplicates
        if not st.session_state.get('interview_saved', False):
            try:
                # Normalize email
                user_email = user['email'].lower().strip()
                
                # Get or create user in database
                get_or_create_user(user_email, user['name'], user['picture'])
                
                # Prepare feedback summary
                feedback_summary = "Interview completed. "
                if overall_score >= 8:
                    feedback_summary += "Excellent performance!"
                elif overall_score >= 6:
                    feedback_summary += "Good performance, room for improvement."
                else:
                    feedback_summary += "Keep practicing to improve your scores."
                
                # Check if this interview was scheduled by an admin
                from modules.database import get_admin_for_scheduled_interview
                admin_info = get_admin_for_scheduled_interview(user_email)
                scheduled_by = admin_info['email'] if admin_info else None
                
                # Save the interview result
                save_interview_result(
                    email=user_email,
                    questions_count=questions_count,
                    overall_score=overall_score,
                    feedback=feedback_summary,
                    resume_data={'text': resume_text[:500]},  # Store first 500 chars of resume
                    answers=all_rounds_data,
                    emotion_data=st.session_state.get('emotion_data', {}),
                    scheduled_by=scheduled_by
                )
                
                # Automatically update scheduled interview status to completed
                if admin_info:
                    try:
                        update_scheduled_interview_status_by_user(user_email, 'completed')
                    except Exception as e:
                        print(f"Could not update scheduled interview status: {str(e)}")
                
                
                # Send email with results to user
                try:
                    email_success, email_message = send_interview_results_email(
                        recipient_email=user_email,
                        user_name=user['name'],
                        overall_score=overall_score,
                        feedback=feedback_summary,
                        interview_data={
                            'questions_count': questions_count,
                            'date': datetime.now().strftime('%B %d, %Y at %I:%M %p')
                        }
                    )
                    if email_success:
                        st.session_state.email_sent = True
                except Exception as e:
                    print(f"Email sending error: {str(e)}")
                    st.session_state.email_sent = False
                
                # Send email with results to admin if interview was scheduled
                if admin_info:
                    try:
                        admin_email_success, admin_email_message = send_interview_results_email(
                            recipient_email=admin_info['email'],
                            user_name=f"{user['name']} (Interview Report)",
                            overall_score=overall_score,
                            feedback=feedback_summary,
                            interview_data={
                                'questions_count': questions_count,
                                'date': datetime.now().strftime('%B %d, %Y at %I:%M %p')
                            }
                        )
                        if admin_email_success:
                            st.success(f"✅ Results also sent to admin {admin_info['name']}", icon="✅")
                    except Exception as e:
                        print(f"Admin email sending error: {str(e)}")
                        st.warning(f"Could not send results to admin: {str(e)}")
                
                # Mark as saved to prevent duplicate saves
                st.session_state.interview_saved = True
            except Exception as e:
                st.warning(f"Could not save results: {str(e)}")

# Display overall result banner
st.markdown("""
<div class="overall-result">
""", unsafe_allow_html=True)

st.markdown(f'<div class="final-score">{overall_score:.1f}/10</div>', unsafe_allow_html=True)
st.markdown('<div class="final-label">OVERALL INTERVIEW SCORE</div>', unsafe_allow_html=True)

# Show save status
if is_user_logged_in():
    user = get_current_user()
    if not user['is_guest']:
        st.markdown('<div style="text-align: center; font-size: 0.85rem; color: #10b981; margin-top: 8px;">✓ Results saved to your account</div>', unsafe_allow_html=True)
        
        # Show email status
        if st.session_state.get('email_sent', False):
            st.markdown('<div style="text-align: center; font-size: 0.85rem; color: #10b981; margin-top: 4px;">✓ Results emailed to your inbox</div>', unsafe_allow_html=True)
        elif st.session_state.get('interview_saved', False):
            st.markdown('<div style="text-align: center; font-size: 0.85rem; color: #f59e0b; margin-top: 4px;">⚠ Email notification could not be sent (check your email config)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center; font-size: 0.85rem; color: #f59e0b; margin-top: 8px;">⚠ Results not saved (Guest mode)</div>', unsafe_allow_html=True)

# Determine result status
if overall_score >= 8:
    status = "🎉 Excellent Performance!"
    color = "#10b981"
elif overall_score >= 6:
    status = "✅ Good Performance!"
    color = "#3b82f6"
elif overall_score >= 4:
    status = "⚠️ Average Performance"
    color = "#f59e0b"
else:
    status = "❌ Needs Improvement"
    color = "#ef4444"

st.markdown(f'<div class="final-status" style="color:{color};">{status}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Calculate and display emotion metrics
from modules.emotion_detect import calculate_emotion_metrics

emotion_data = st.session_state.get('emotion_data', {})
emotion_metrics = {'engagement': 0, 'confidence': 0, 'stress': 0}

# Calculate metrics from all emotion data collected during interview
all_emotion_scores = []
for round_type in ROUND_TYPES:
    if emotion_data.get(round_type):
        all_emotion_scores.extend(emotion_data[round_type])

if all_emotion_scores:
    emotion_metrics = calculate_emotion_metrics(all_emotion_scores)

# Display emotion metrics if available
if all_emotion_scores:
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Emotional Intelligence Analysis</div>', unsafe_allow_html=True)
    
    metric_cols = st.columns(3)
    
    with metric_cols[0]:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-icon">💪</div>
            <div class="score-num">{emotion_metrics['confidence']:.0f}</div>
            <div class="score-label">Confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[1]:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-icon">🎯</div>
            <div class="score-num">{emotion_metrics['engagement']:.0f}</div>
            <div class="score-label">Engagement</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[2]:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-icon">😰</div>
            <div class="score-num">{emotion_metrics['stress']:.0f}</div>
            <div class="score-label">Stress Level</div>
        </div>
        """, unsafe_allow_html=True)

# Display round scores
st.markdown('<div class="section-title">Round Breakdown</div>', unsafe_allow_html=True)

score_cols = st.columns(4)
for i, (col, round_type) in enumerate(zip(score_cols, ROUND_TYPES)):
    with col:
        avg_score = round_scores[round_type]['average']
        st.markdown(f"""
        <div class="score-card">
            <div class="score-icon">{'🧠' if round_type == 'aptitude' else ('💻' if round_type == 'technical' else ('🔧' if round_type == 'coding' else '👔'))}</div>
            <div class="score-num">{avg_score:.1f}</div>
            <div class="score-label">{ROUNDS[i].split()[1]}</div>
        </div>
        """, unsafe_allow_html=True)

# Display detailed results for each round
for i, round_type in enumerate(ROUND_TYPES):
    st.markdown(f'<div class="section-title">{ROUNDS[i]} Round</div>', unsafe_allow_html=True)
    
    round_data = all_rounds_data[round_type]
    questions = round_data.get('questions', [])
    answers = round_data.get('answers', [])
    evaluations = round_scores[round_type]['evaluations']
    
    for q_idx, question in enumerate(questions):
        if q_idx < len(answers) and answers[q_idx]:
            answer_data = answers[q_idx]
            answer_text = answer_data.get('answer', '')
            
            if answer_text != 'SKIPPED':
                st.markdown(f"""
                <div class="q-result-card">
                    <div class="q-result-header">
                        <span class="q-result-num">Q {q_idx + 1}</span>
                        <span class="q-result-text">{question}</span>
                    </div>
                    <div class="q-result-body">
                        <div style="margin-bottom:12px;">
                            <div style="font-size:0.7rem;font-weight:700;color:#2d3748;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">Your Answer</div>
                            <div class="answer-box">"{answer_text}"</div>
                        </div>
                """, unsafe_allow_html=True)
                
                # Parse and display evaluation
                if q_idx < len(evaluations):
                    try:
                        eval_json = json.loads(evaluations[q_idx])
                        
                        # Display scores
                        st.markdown(f"""
                        <div style="margin-bottom:12px;">
                            <div class="q-mini-scores">
                                <div class="mini-score">{eval_json.get('score1_name', 'Score 1')}: {eval_json.get('score1', 0)}/10</div>
                                <div class="mini-score">{eval_json.get('score2_name', 'Score 2')}: {eval_json.get('score2', 0)}/10</div>
                                <div class="mini-score">{eval_json.get('score3_name', 'Score 3')}: {eval_json.get('score3', 0)}/10</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display feedback
                        strengths = eval_json.get('strengths', [])
                        improvements = eval_json.get('improvements', [])
                        
                        if strengths or improvements:
                            st.markdown('<div class="feedback-row">', unsafe_allow_html=True)
                            
                            if strengths:
                                st.markdown(f"""
                                <div class="strength-box">
                                    <div class="feedback-label strength-label">✓ Strengths</div>
                                    {'<br>'.join(['• ' + s for s in strengths])}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            if improvements:
                                st.markdown(f"""
                                <div class="improve-box">
                                    <div class="feedback-label improve-label">⚡ Areas to Improve</div>
                                    {'<br>'.join(['• ' + imp for imp in improvements])}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    except:
                        st.markdown(f'<div style="color:#666; font-size:0.9rem;">{evaluations[q_idx][:200]}...</div>', unsafe_allow_html=True)
                
                st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Bottom action buttons
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Retake Interview"):
        st.session_state.clear()
        st.switch_page("pages/1_Interview.py")
with col2:
    st.download_button(
        label="Download Report",
        data=f"Interview Results\nOverall Score: {overall_score:.1f}/10",
        file_name="interview_report.txt"
    )
with col3:
    if st.button("Home"):
        st.switch_page("app.py")
