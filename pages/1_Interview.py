import streamlit as st
import threading
import time
import numpy as np
from PIL import Image
from modules.resume_parser import parse_resume
from modules.question_gen import generate_questions
from modules.speech_to_text import record_and_transcribe
from modules.emotion_detect import analyze_emotion_from_image
from modules.auth import is_user_logged_in, get_current_user

st.set_page_config(page_title="Interview Room", page_icon="🎤", layout="wide", initial_sidebar_state="collapsed")

# Check if user is logged in
if not is_user_logged_in():
    st.error("❌ Please log in first")
    if st.button("← Back to Home"):
        st.switch_page("app.py")
    st.stop()

user = get_current_user()

# Check if this is a new interview session
# If interview was previously saved, clear the old data for a fresh start
if st.session_state.get('interview_saved', False):
    # Clear interview-related session state for new interview
    keys_to_clear = [
        'resume_text', 'all_rounds_data', 'current_round', 'q_index',
        'current_emotion', 'emotion_scores', 'emotion_data', 'interview_saved', 'email_sent',
        'last_file', 'evaluation_cache'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* ── ANIMATIONS ── */
@keyframes cardFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(100px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,188,212,0.7); }
    50% { box-shadow: 0 0 0 10px rgba(0,188,212,0); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(0,188,212,0.5); }
    50% { box-shadow: 0 0 20px rgba(0,188,212,0.8); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes staggerFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

*, *::before, *::after { box-sizing: border-box; }
body, .stApp { font-family: 'DM Sans', sans-serif; background: #f0f4f8; color: #0d1117; }
header { visibility: hidden; }
/* Hide sidebar */
[data-testid="collapsedControl"] { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none; }
.stSidebar { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Professional Typography */
h1, h2, h3, h4, h5, h6 { letter-spacing: -0.5px !important; line-height: 1.3 !important; color: #0d1117 !important; }
p { line-height: 1.6 !important; }

/* ── TOPBAR ── */
.topbar {
    background: white;
    height: 60px;
    padding: 0 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e2e8f0;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
    animation: slideInRight 0.5s ease-out;
}
.topbar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #00bcd4;
    letter-spacing: -0.3px;
    transition: all 0.3s ease;
}

.topbar-logo:hover {
    color: #0097a7;
    text-shadow: 0 0 10px rgba(0,188,212,0.3);
}
.prog-wrap { display: flex; align-items: center; gap: 0; flex-direction: column; }
.prog-step {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.7rem; font-weight: 600; color: #a0aec0;
    padding: 8px 12px;
    width: 100%;
    justify-content: center;
    flex-direction: column;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.prog-step.done { 
    color: #0097a7; 
    transform: scale(1.05);
}
.prog-step.active { 
    color: #00bcd4; 
    font-weight: 700;
    animation: glow 1.5s ease-in-out infinite;
}
.prog-step-num {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 800;
    background: #e2e8f0; color: #a0aec0;
    margin-bottom: 4px;
    transition: all 0.3s ease;
}
.prog-step.done .prog-step-num { 
    background: #e0f7fa; 
    color: #0097a7; 
    transform: scale(1.1);
}
.prog-step.active .prog-step-num { 
    background: #00bcd4; 
    color: white;
    box-shadow: 0 0 15px rgba(0,188,212,0.4);
}
.prog-divider { display: none; }
.live-pill {
    display: flex; align-items: center; gap: 7px;
    background: #fff5f5; border: 1px solid #fed7d7;
    border-radius: 20px; padding: 5px 14px;
    font-size: 0.73rem; font-weight: 700; color: #e53e3e;
    letter-spacing: 0.5px;
}
.live-dot { width: 7px; height: 7px; background: #e53e3e; border-radius: 50%; animation: blink 1.2s infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.15;} }

/* ── BODY ── */
.body-wrap { display: flex; gap: 16px; padding: 16px; height: calc(100vh - 60px); overflow: hidden; }

/* ── CAMERA PANEL ── */
.cam-panel {
    flex: 1.5;
    background: white;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 16px rgba(0,0,0,0.05);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}
.cam-header {
    padding: 14px 18px;
    border-bottom: 1px solid #f0f4f8;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.cam-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    font-weight: 800;
    color: #2d3748;
    letter-spacing: 0.3px;
}
.rec-indicator {
    display: flex; align-items: center; gap: 6px;
    background: #fff5f5; border: 1px solid #fed7d7;
    border-radius: 8px; padding: 4px 10px;
    font-size: 0.7rem; font-weight: 700; color: #e53e3e;
}
.cam-body { flex: 1; background: #0a0e14; position: relative; }
.cam-footer {
    padding: 12px 18px;
    border-top: 1px solid #f0f4f8;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.emo-current {
    font-size: 0.82rem; font-weight: 700;
    color: #0097a7;
}
.emo-strip { display: flex; gap: 5px; }
.emo-chip {
    background: #f0f4f8; border: 1px solid #e2e8f0;
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.7rem; color: #718096; font-weight: 500;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    cursor: pointer;
}
.emo-chip.on {
    background: #e0f7fa; border-color: #00bcd4;
    color: #0097a7; font-weight: 700;
    animation: glow 1.5s ease-in-out infinite;
    box-shadow: 0 0 15px rgba(0,188,212,0.3);
}

/* ── RIGHT PANEL ── */
.right-col { flex: 1; display: flex; flex-direction: column; gap: 12px; overflow-y: auto; }

/* CARD */
.card {
    background: white;
    border-radius: 18px;
    border: 1px solid #e8f4f8;
    box-shadow: 0 8px 32px rgba(0,97,167,0.08);
    overflow: hidden;
    animation: cardFadeIn 0.6s ease-out;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 40px rgba(0,188,212,0.12);
    border-color: #b2ebf2;
}
.card-header {
    padding: 14px 20px;
    border-bottom: 1px solid #f0f4f8;
    display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(135deg, #f8fbfd 0%, #f4f9fc 100%);
}
.card-title {
    font-size: 0.75rem; font-weight: 700;
    color: #0097a7; letter-spacing: 1.5px; text-transform: uppercase;
}
.card-body { padding: 14px 18px; }

/* ROUND BADGE */
.round-badge {
    display: inline-block;
    background: #e0f7fa;
    border: 1px solid #b2ebf2;
    color: #0097a7;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    margin-right: 8px;
}

/* Q CARD INNER */
.q-inner {
    background: linear-gradient(135deg, #f0fafa, #e8f9fc);
    border-radius: 10px;
    border: 1px solid #b2ebf2;
    padding: 14px;
    margin-bottom: 10px;
}
.q-badge {
    display: inline-flex; align-items: center; gap: 6px;
    margin-bottom: 8px;
}
.q-num-badge {
    font-size: 0.65rem; font-weight: 800; color: #00bcd4;
    letter-spacing: 1px; text-transform: uppercase;
}
.diff-tag { font-size: 0.62rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; }
.diff-easy { background: #e6fffa; color: #00897b; }
.diff-medium { background: #fffde7; color: #f57f17; }
.diff-hard { background: #fce4ec; color: #c62828; }
.q-text-inner { font-size: 0.93rem; font-weight: 500; color: #1a202c; line-height: 1.7; }

/* STATUS CHIP */
.chip-ok {
    display: flex; align-items: center; gap: 8px;
    background: #f0fff4; border: 1px solid #c6f6d5;
    border-radius: 8px; padding: 8px 14px;
    font-size: 0.82rem; font-weight: 600; color: #276749;
}
.chip-pass {
    display: flex; align-items: center; gap: 8px;
    background: #fffde7; border: 1px solid #ffe082;
    border-radius: 8px; padding: 8px 14px;
    font-size: 0.82rem; font-weight: 600; color: #b7791f;
}
.dot-g { width: 8px; height: 8px; background: #48bb78; border-radius: 50%; flex-shrink: 0; }

/* TRANSCRIPT */
.transcript {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-left: 3px solid #00bcd4;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; font-size: 0.82rem;
    color: #4a5568; font-style: italic; line-height: 1.7;
    margin-top: 10px; max-height: 80px; overflow-y: auto;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #00bcd4, #0097a7) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 0.65rem 1rem !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(0,188,212,0.25) !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.2px !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    box-shadow: 0 8px 25px rgba(0,188,212,0.4) !important;
    transform: translateY(-2px) scale(1.02) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
    box-shadow: 0 2px 8px rgba(0,188,212,0.3) !important;
}
.stButton > button:disabled {
    background: #e2e8f0 !important;
    color: #a0aec0 !important;
    box-shadow: none !important;
    transform: none !important;
    opacity: 0.6 !important;
}

/* TEXT AREA */
textarea {
    border-radius: 12px !important;
    border: 1.5px solid #d0e8f0 !important;
    font-family: 'Monaco', 'Consolas', monospace !important;
    font-size: 0.9rem !important;
    padding: 14px !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    background: #f8fbfd !important;
    color: #1a202c !important;
}
textarea:focus {
    border-color: #0097a7 !important;
    box-shadow: 0 0 0 4px rgba(0,188,212,0.15) !important;
    background: white !important;
    color: #0d1117 !important;
}

/* File uploader */
[data-testid="stFileUploader"] > div {
    background: #f8fafc !important;
    border: 2px dashed #b2ebf2 !important;
    border-radius: 12px !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
}
[data-testid="stFileUploader"] > div:hover { 
    border-color: #00bcd4 !important; 
    background: #f0fafa !important;
    box-shadow: 0 0 15px rgba(0,188,212,0.1) !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploader"] button {
    color: #00bcd4 !important;
    font-weight: 700 !important;
}
[data-testid="stFileUploader"] button:hover {
    color: #0097a7 !important;
}

/* Camera input */
[data-testid="stCameraInput"] video { border-radius: 0 !important; }
[data-testid="stCameraInput"] > div {
    border: none !important;
    border-radius: 0 !important;
    background: #0a0e14 !important;
    padding: 0 !important;
}
[data-testid="stCameraInput"] button { display: none !important; }
[data-testid="stCameraInput"] label { display: none !important; }

/* Button Styling */
.stButton > button {
    background: linear-gradient(90deg, #00bcd4, #0097a7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 12px rgba(0,188,212,0.3) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #0097a7, #00838f) !important;
    box-shadow: 0 6px 16px rgba(0,188,212,0.4) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(0,188,212,0.3) !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: #b2ebf2; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────
ROUNDS = ["🧠 Aptitude", "💻 Technical", "🔧 Coding", "👔 HR"]
ROUND_TYPES = ["aptitude", "technical", "coding", "hr"]
QUESTIONS_PER_ROUND = 3

for k, v in [
    ('current_round', 0),
    ('q_index', 0),
    ('session_start', time.time()),
    ('current_emotion', 'neutral'),
    ('emotion_scores', {}),
    ('emotion_data', {}),  # Store aggregated emotion data per round
    ('all_rounds_data', {}),
    ('interview_saved', False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# Initialize round data structure if needed
if 'all_rounds_data' not in st.session_state or not st.session_state['all_rounds_data']:
    st.session_state['all_rounds_data'] = {
        'aptitude': {'questions': [], 'answers': []},
        'technical': {'questions': [], 'answers': []},
        'coding': {'questions': [], 'answers': []},
        'hr': {'questions': [], 'answers': []}
    }

# Initialize emotion data per round if needed
if 'emotion_data' not in st.session_state or not st.session_state['emotion_data']:
    st.session_state['emotion_data'] = {
        'aptitude': [],
        'technical': [],
        'coding': [],
        'hr': []
    }

# Calculate variables used throughout the page
resume_uploaded = 'resume_text' in st.session_state
current_round = st.session_state.get('current_round', 0)
current_round_type = ROUND_TYPES[current_round]
round_data = st.session_state['all_rounds_data'][current_round_type]
total_q = len(round_data.get('questions', []))
answered_cnt = len([a for a in round_data.get('answers', []) if a is not None])

# ── TOPBAR ────────────────────────────────────────────────────
# This will be recalculated after resume upload in the RIGHT COLUMN section
def make_progress_bar(current_round):
    progress_steps = []
    for i, round_name in enumerate(ROUNDS):
        is_done = len(st.session_state['all_rounds_data'][ROUND_TYPES[i]]['answers']) > 0
        is_active = i == current_round
        status = 'done' if is_done else ('active' if is_active else '')
        
        step_html = f'<div class="prog-step {status}"><div class="prog-step-num">{"✓" if is_done else str(i+1)}</div>{round_name}</div>'
        progress_steps.append(step_html)
        if i < len(ROUNDS) - 1:
            progress_steps.append('<div class="prog-divider"></div>')
    return ''.join(progress_steps)

progress_html = make_progress_bar(st.session_state.get('current_round', 0))

st.markdown(f"""
<div style="padding:12px 20px 8px; background:transparent;">
    <div class="topbar">
            <div class="topbar-logo">AI Interview</div>
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="background: #00bcd4; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700;">{user['role'].upper()}</span>
                <div class="live-pill"><div class="live-dot"></div>Live session</div>
            </div>
    </div>
    <div style="max-width:1100px; margin:12px auto 0;">
        <div style="background:white; border-radius:12px; padding:8px 12px; border:1px solid #eef6f7; box-shadow:0 6px 18px rgba(2,6,23,0.03);">
            <div style="display:flex; align-items:center; justify-content:center; gap:18px;">
                {progress_html}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Add exit button
col1, col2 = st.columns([10, 1])
with col2:
    if st.button("← Exit", key="exit_interview"):
        st.switch_page("app.py")

# ── LAYOUT ───────────────────────────────────────────────────
cam_col, right_col = st.columns([1.5, 1])

# ════════════════════════════════
# CAMERA PANEL
# ════════════════════════════════
with cam_col:
        current_emotion = st.session_state.get('current_emotion', 'neutral')

        # Coding round: textarea replaces live video in left column
        if current_round_type == "coding":
            st.markdown("""
            <div style="background:white; border-radius:18px; border:1px solid #e2e8f0; box-shadow:0 2px 16px rgba(0,0,0,0.05); overflow:hidden;">
                <div style="padding:12px 16px; border-bottom:1px solid #f0f4f8;">
                    <div style="font-family:'Syne',sans-serif; font-size:0.85rem; font-weight:800; color:#2d3748;">Code Editor</div>
                </div>
                <div style="padding:0px 0px; background:#f8fafc;">
            """, unsafe_allow_html=True)
            code_answer = st.text_area("", height=280, key=f"coding_answer_left_{st.session_state.get('q_index', 0)}", placeholder="Write your code here...", label_visibility="collapsed")
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:white; border-radius:18px 18px 0 0;
                                    border:1px solid #e2e8f0; border-bottom:none;
                                    padding:12px 18px; display:flex;
                                    align-items:center; justify-content:space-between;
                                    box-shadow:0 2px 16px rgba(0,0,0,0.05);">
                            <div style="font-family:'Syne',sans-serif; font-size:0.85rem;
                                                                            font-weight:800; color:#2d3748;">
                            Live Camera (Optional)
                    </div>
                <div class="rec-indicator">
                    <div class="live-dot"></div> EMOTION DETECTION
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Use Streamlit's built-in camera input
            camera_image = st.camera_input("camera", label_visibility="hidden")

            if camera_image is not None:
                    try:
                            img = Image.open(camera_image)
                            img_array = np.array(img)
                            emotion, emotion_scores = analyze_emotion_from_image(img_array)
                            st.session_state['current_emotion'] = emotion
                            if emotion_scores:
                                    st.session_state['emotion_scores'] = emotion_scores
                                    # Store emotion scores for this round
                                    if current_round_type not in st.session_state['emotion_data']:
                                        st.session_state['emotion_data'][current_round_type] = []
                                    st.session_state['emotion_data'][current_round_type].append(emotion_scores)
                            current_emotion = emotion
                    except Exception as e:
                            print(f"Error processing camera image: {str(e)}")
                            current_emotion = st.session_state.get('current_emotion', 'neutral')

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# Question navigator
if total_q > 0:
        st.markdown("""
        <div style="background:white; border-radius:14px; border:1px solid #e2e8f0;
                    padding:14px 16px; box-shadow:0 2px 12px rgba(0,0,0,0.04);">
          <div style="font-size:0.68rem;font-weight:700;color:#2d3748;
                      letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;">
            Question Navigator
          </div>
        """, unsafe_allow_html=True)

        chip_cols = st.columns(total_q)
        for i in range(total_q):
            with chip_cols[i]:
                is_cur  = i == st.session_state.get('q_index', 0)
                is_done = i < len(round_data.get('answers', [])) and round_data['answers'][i] is not None
                bg    = "#00bcd4" if is_cur  else ("#e0f7fa" if is_done else "#f8fafc")
                color = "white"   if is_cur  else ("#0097a7" if is_done else "#2d3748")
                bdr   = "#00bcd4" if is_cur  else ("#b2ebf2" if is_done else "#e2e8f0")
                lbl   = "✓" if is_done else str(i+1)
                st.markdown(f"""
                <div style="background:{bg};color:{color};border:2px solid {bdr};
                            border-radius:10px;padding:8px 4px;text-align:center;
                            font-size:0.8rem;font-weight:700;">
                  Q{lbl}
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════
# RIGHT — Controls
# ════════════════════════════════
with right_col:

    # ── Resume Upload ─────────────────────────────────────────
    st.markdown("""
    <div class="card">
      <div class="card-header">
        <span class="card-title">Resume</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div style="padding:12px 18px 14px; background:white; border-radius:0 0 16px 16px; border:1px solid #e2e8f0; border-top:none; margin-top:-4px;">', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
        if pdf_file:
            if 'resume_text' not in st.session_state or st.session_state.get('last_file') != pdf_file.name:
                with st.spinner("📖 Parsing resume..."):
                    try:
                        resume_text = parse_resume(pdf_file)
                        st.session_state['resume_text'] = resume_text
                        st.session_state['last_file'] = pdf_file.name
                    except Exception as e:
                        st.error(f"Error parsing resume: {str(e)}")
                        st.stop()
                
                # Generate questions for all rounds
                with st.spinner("🧠 Generating interview questions..."):
                    try:
                        for i, round_type in enumerate(ROUND_TYPES):
                            questions_text = generate_questions(resume_text, round_type, QUESTIONS_PER_ROUND)
                            # Parse questions more robustly
                            questions = []
                            for line in questions_text.split('\n'):
                                line = line.strip()
                                # Remove numbering like "1.", "2.", etc.
                                if line and not line.startswith('#'):
                                    # Remove leading numbers and dots
                                    if line and line[0].isdigit():
                                        line = line.lstrip('0123456789. ').strip()
                                    if line:
                                        questions.append(line)
                            st.session_state['all_rounds_data'][round_type]['questions'] = questions[:QUESTIONS_PER_ROUND]
                    except Exception as e:
                        st.error(f"Error generating questions: {str(e)}")
                        st.stop()
                
                # Force rerun to update the UI with questions
                st.rerun()
            
            st.markdown(f"""
            <div class="chip-ok" style="margin-top:8px;">
              <div class="dot-g"></div>
              Resume uploaded • Questions ready
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if resume_uploaded and total_q > 0:
        questions = round_data['questions']
        q_idx = st.session_state.get('q_index', 0)
        sel_q = questions[q_idx]

        # ── Round Info ────────────────────────────────────────
        st.markdown(f"""
        <div class="card" style="margin-top:10px;">
          <div class="card-body" style="padding: 12px 18px;">
            <span class="round-badge">{ROUNDS[current_round]}</span>
            <span style="font-size:0.75rem; color:#2d3748;">Round {current_round+1} of {len(ROUNDS)}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Question Card ────────────────────────────────────
        st.markdown(f"""
                <div class="card" style="margin-top:10px;">
                    <div class="card-header">
                        <span class="card-title">Question</span>
                        <span style="font-size:0.72rem;font-weight:600;color:#2d3748;">
                            {answered_cnt} / {total_q} answered
                        </span>
                    </div>
          <div class="card-body">
            <div class="q-inner">
              <div class="q-badge">
                <span class="q-num-badge">Q {q_idx+1} of {len(questions)}</span>
              </div>
              <div class="q-text-inner">{sel_q}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Prev / Next
        pc, nc = st.columns(2)
        with pc:
            if st.button("← Prev", disabled=(q_idx == 0)):
                st.session_state['q_index'] = q_idx - 1
                st.rerun()
        with nc:
            if st.button("Next →", disabled=(q_idx == len(questions)-1)):
                st.session_state['q_index'] = q_idx + 1
                st.rerun()

        # ── Answer Card ──────────────────────────────────────
        st.markdown("""
                <div class="card" style="margin-top:10px;">
                    <div class="card-header">
                        <span class="card-title">Answer</span>
                    </div>
                </div>
        """, unsafe_allow_html=True)


        with st.container():
            st.markdown('<div style="padding:14px 18px; background:white; border-radius:0 0 16px 16px; border:1px solid #e2e8f0; border-top:none; margin-top:-4px;">', unsafe_allow_html=True)

            is_answered = q_idx < len(round_data.get('answers', [])) and round_data['answers'][q_idx] is not None

            if current_round_type == "coding":
                # Coding round: Save and Skip buttons
                st.markdown("<div style='display:flex; gap:8px;'>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Save Answer", use_container_width=True, key="save_coding_btn"):
                        if len(round_data['answers']) <= q_idx:
                            round_data['answers'].extend([None] * (q_idx + 1))
                        round_data['answers'][q_idx] = {
                            'answer': code_answer,
                            'emotion': None,
                            'emotion_scores': None
                        }
                        st.success("Answer saved!")
                        st.rerun()
                with col2:
                    if st.button("⏭ Skip", use_container_width=True, key="skip_coding_btn"):
                        if len(round_data['answers']) <= q_idx:
                            round_data['answers'].extend([None] * (q_idx + 1))
                        round_data['answers'][q_idx] = {'answer': 'SKIPPED', 'emotion': None, 'emotion_scores': None}
                        if q_idx < len(questions) - 1:
                            st.session_state['q_index'] = q_idx + 1
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # ...existing code for other rounds (recording)
                ANSWER_TIME = 60
                if is_answered:
                    st.markdown("""
                    <div class="chip-ok">
                      <div class="dot-g"></div>Answer recorded ✓
                    </div>""", unsafe_allow_html=True)
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    if st.button("🔁 Re-record Answer"):
                        round_data['answers'][q_idx] = None
                        st.rerun()
                else:
                    if st.button("🔴 Start Recording (60 seconds)"):
                        with st.status("🎙️ Recording your answer...", expanded=True) as status:
                            timer_ph = st.empty()
                            answer_result = [None]
                            recording_done = [False]

                            def do_record():
                                answer_result[0] = record_and_transcribe()
                                recording_done[0] = True

                            rec_thread = threading.Thread(target=do_record)
                            rec_thread.start()

                            start_t = time.time()
                            while not recording_done[0]:
                                rem = max(0, ANSWER_TIME - int(time.time() - start_t))
                                pct = int((rem / ANSWER_TIME) * 100)
                                bar_c = "#00bcd4" if rem > 20 else ("#ffc107" if rem > 10 else "#ff4444")
                                timer_ph.markdown(f"""
                                <div style="text-align:center; padding:10px 0;">
                                  <div style="font-size:3.2rem; font-weight:900;
                                              color:{bar_c}; line-height:1; font-family:'Syne',sans-serif;">
                                    {rem}
                                  </div>
                                  <div style="font-size:0.72rem; color:#2d3748;
                                              letter-spacing:1px; margin:4px 0 10px;">SECONDS REMAINING</div>
                                  <div style="background:#f0f4f8; border-radius:99px;
                                              height:6px; overflow:hidden;">
                                    <div style="width:{pct}%; height:100%; border-radius:99px;
                                                background:{bar_c}; transition:width 1s linear;"></div>
                                  </div>
                                  <div style="font-size:0.72rem; color:#2d3748; margin-top:8px;">
                                    🎤 Speak clearly · Stops after 5 seconds of silence
                                  </div>
                                </div>
                                """, unsafe_allow_html=True)
                                time.sleep(1)
                                if rem == 0:
                                    break

                            rec_thread.join()
                            answer_text = answer_result[0] or "No answer recorded."
                            
                            # Store answer
                            if len(round_data['answers']) <= q_idx:
                                round_data['answers'].extend([None] * (q_idx + 1))
                            round_data['answers'][q_idx] = {
                                'answer': answer_text,
                                'emotion': st.session_state.get('current_emotion', 'neutral'),
                                'emotion_scores': st.session_state.get('emotion_scores', {})
                            }
                            
                            status.update(label="✅ Answer saved!", state="complete")
                        st.rerun()

                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    if st.button("⏭ Skip Question"):
                        if len(round_data['answers']) <= q_idx:
                            round_data['answers'].extend([None] * (q_idx + 1))
                        round_data['answers'][q_idx] = {'answer': 'SKIPPED', 'emotion': 'neutral', 'emotion_scores': {}}
                        if q_idx < len(questions) - 1:
                            st.session_state['q_index'] = q_idx + 1
                        st.rerun()

                # Transcript
                if q_idx < len(round_data.get('answers', [])) and round_data['answers'][q_idx] and round_data['answers'][q_idx]['answer'] != 'SKIPPED':
                    st.markdown(f"""
                    <div style="font-size:0.65rem;font-weight:700;color:#2d3748;
                                letter-spacing:1.5px;text-transform:uppercase;margin:12px 0 4px;">
                      Your Answer
                    </div>
                    <div class="transcript">"{round_data['answers'][q_idx]['answer']}"</div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # ── Round Navigation ──────────────────────────────────
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        nav_col1, nav_col2 = st.columns(2)
        
        with nav_col1:
            if st.button("← Previous Round", disabled=(current_round == 0)):
                st.session_state['current_round'] = current_round - 1
                st.session_state['q_index'] = 0
                st.rerun()
        
        with nav_col2:
            if answered_cnt == total_q:
                if current_round == len(ROUNDS) - 1:
                    if st.button("📊 View Results →"):
                        st.switch_page("pages/2_Results.py")
                else:
                    if st.button("Next Round →"):
                        st.session_state['current_round'] = current_round + 1
                        st.session_state['q_index'] = 0
                        st.rerun()
            else:
                st.button("Next Round →", disabled=True)

    elif resume_uploaded:
                st.markdown("""
                <div class="card" style="margin-top:10px; text-align:center; padding:3rem 1rem;">
                    <div style="font-size:3rem; margin-bottom:12px;">⏳</div>
                    <div style="font-family:'Syne',sans-serif; font-size:1rem;
                                            color:#00bcd4; font-weight:700;">Generating questions…</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
                <div class="card" style="margin-top:10px; text-align:center; padding:3rem 1rem;">
                    <div style="font-size:3rem; margin-bottom:12px;">📄</div>
                    <div style="font-family:'Syne',sans-serif; font-size:1rem;
                                            color:#00bcd4; font-weight:700;">Upload your PDF resume to begin</div>
                    <div style="font-size:0.9rem; color:#2d3748; margin-top:8px;">
                        You will be asked questions across four rounds: Aptitude, Technical, Coding and HR
                    </div>
                </div>
        """, unsafe_allow_html=True)
