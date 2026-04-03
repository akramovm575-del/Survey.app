# ============================================================
# Peer Social Support Survey — Streamlit Web App
# Module: Fundamentals of Programming, 4BUIS008C
# ============================================================

import streamlit as st
import json
import csv
import io
import re
import os
from datetime import datetime

# ── Variable types (all 10 required types) ───────────────────
survey_title   = "Peer Social Support Survey"     # str
version        = 1.0                               # float
question_count = 15                                # int
survey_active  = True                              # bool
score_ranges   = [0, 13, 25, 37, 43, 49, 55]      # list
state_labels   = (                                 # tuple
    "Very Low Support",
    "Low Support",
    "Moderate Support",
    "Good Support",
    "Strong Support",
    "Excellent Support",
    "Outstanding Support"
)
valid_choices  = range(1, 6)                       # range
results_store  = {}                                # dict
completed_ids  = set()                             # set
locked_fields  = frozenset({"title", "version"})   # frozenset

# ── Questions embedded in code ───────────────────────────────
QUESTIONS = [
    {
        "text": "My friends help me when I face academic difficulties.",
        "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "I feel comfortable sharing personal problems with my close friends.",
        "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "Having supportive friends motivates me to do better academically.",
        "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "I find it hard to find a friend I can open up to about my struggles.",
        "options": ["Always (4)", "Often (3)", "Sometimes (2)", "Rarely (1)", "Never (0)"],
        "scores": [4, 3, 2, 1, 0]
    },
    {
        "text": "Arguments or conflicts with friends distract me from my studies.",
        "options": ["Always (4)", "Often (3)", "Sometimes (2)", "Rarely (1)", "Never (0)"],
        "scores": [4, 3, 2, 1, 0]
    },
    {
        "text": "My friends cheer me up when I feel like giving up on my studies.",
        "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "I feel emotionally stable when I have strong friendships.",
        "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "I talk about academic challenges with my close friends.",
        "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "Unresolved conflicts with peers make me feel anxious and unfocused.",
        "options": ["Not at all (0)", "Slightly (1)", "Moderately (2)", "Significantly (3)", "Extremely (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "My friends help me feel like I belong at university.",
        "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "I feel lonely and isolated when I lack close friendships.",
        "options": ["Always (4)", "Often (3)", "Sometimes (2)", "Rarely (1)", "Never (0)"],
        "scores": [4, 3, 2, 1, 0]
    },
    {
        "text": "Talking to friends about my worries improves how I feel emotionally.",
        "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "Friendship conflicts reduce my desire to attend or engage with classes.",
        "options": ["Not at all (0)", "Slightly (1)", "Moderately (2)", "Significantly (3)", "Extremely (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "I feel safe being honest and vulnerable with my closest friends.",
        "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
    {
        "text": "Overall, my friendships have a positive effect on my academic performance.",
        "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
        "scores": [0, 1, 2, 3, 4]
    },
]


# ── FUNCTION 1: Load questions from file or use embedded ─────
def load_questions():
    if os.path.exists("questions.json"):
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return QUESTIONS


# ── FUNCTION 2: Validate name ────────────────────────────────
def validate_name(name):
    return (bool(re.fullmatch(r"[A-Za-z][A-Za-z\s'\-]*", name.strip()))
            and len(name.strip()) >= 2)


# ── FUNCTION 3: Validate date of birth ──────────────────────
def validate_dob(dob):
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", dob):
        return False
    day   = int(dob[:2])
    month = int(dob[3:5])
    year  = int(dob[6:])
    return 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2010


# ── FUNCTION 4: Validate student ID ─────────────────────────
def validate_sid(sid):
    return sid.isdigit() and len(sid) >= 4


# ── FUNCTION 5: Interpret total score ────────────────────────
def interpret_score(score):
    if score <= 12:
        label  = "Very Low Peer Support & Poor Adjustment"
        advice = "Very limited support network. High risk of emotional difficulties."
        emoji  = "🔴"
    elif score <= 24:
        label  = "Low Peer Support & Mild Adjustment Issues"
        advice = "Limited friendships affecting emotional balance."
        emoji  = "🟠"
    elif score <= 36:
        label  = "Moderate Peer Support & Moderate Adjustment"
        advice = "Some supportive friendships. Occasional emotional challenges."
        emoji  = "🟡"
    elif score <= 42:
        label  = "Good Peer Support & Good Adjustment"
        advice = "Healthy peer network with positive effects on wellbeing."
        emoji  = "🟢"
    elif score <= 48:
        label  = "Strong Peer Support & Strong Adjustment"
        advice = "Strong friendships supporting academic and emotional health."
        emoji  = "🟢"
    elif score <= 54:
        label  = "Excellent Peer Support & Excellent Adjustment"
        advice = "Excellent friendship quality and consistent academic performance."
        emoji  = "🟢"
    else:
        label  = "Outstanding Peer Support & Outstanding Adjustment"
        advice = "Exceptional peer relationships. Model support environment."
        emoji  = "🏆"
    return {"label": label, "advice": advice, "emoji": emoji}


# ── FUNCTION 6: Build downloadable TXT content ───────────────
def build_txt(record):
    lines = ["=" * 50, f"  {survey_title} - Results", "=" * 50]
    for key, val in record.items():
        lines.append(f"  {key}: {val}")
    lines.append("=" * 50)
    return "\n".join(lines)


# ── FUNCTION 7: Build downloadable CSV content ───────────────
def build_csv(record):
    buf    = io.StringIO()
    flat   = {k: v for k, v in record.items() if k != "answers"}
    writer = csv.DictWriter(buf, fieldnames=flat.keys())
    writer.writeheader()
    writer.writerow(flat)
    return buf.getvalue()


# ════════════════════════════════════════════════════════════
# PAGE CONFIG & CUSTOM CSS
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title=survey_title,
    page_icon="🤝",
    layout="centered"
)

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #F0F4F8; }

    /* Header banner */
    .survey-header {
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        color: white;
        padding: 28px 32px;
        border-radius: 14px;
        margin-bottom: 24px;
        text-align: center;
    }
    .survey-header h1 { font-size: 26px; margin: 0; }
    .survey-header p  { font-size: 13px; margin: 6px 0 0; opacity: 0.85; }

    /* Info card */
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }

    /* Question card */
    .q-card {
        background: white;
        border-left: 5px solid #2563eb;
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .q-number {
        color: #2563eb;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .q-text {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0;
    }

    /* Progress bar custom */
    .progress-label {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 4px;
    }

    /* Result card */
    .result-card {
        background: white;
        border-radius: 14px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.10);
        margin-bottom: 20px;
    }
    .result-score {
        font-size: 52px;
        font-weight: 800;
        color: #1e3a8a;
        margin: 8px 0;
    }
    .result-state {
        font-size: 18px;
        font-weight: 700;
        color: #16a34a;
        margin-bottom: 8px;
    }
    .result-advice {
        font-size: 14px;
        color: #475569;
    }

    /* Home button styling */
    div[data-testid="stButton"] button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SESSION STATE — tracks which page user is on
# ════════════════════════════════════════════════════════════
if "page" not in st.session_state:
    st.session_state.page = "home"

if "questions" not in st.session_state:
    st.session_state.questions = load_questions()

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "result" not in st.session_state:
    st.session_state.result = {}

if "p_name" not in st.session_state:
    st.session_state.p_name = ""

if "p_dob" not in st.session_state:
    st.session_state.p_dob = ""

if "p_sid" not in st.session_state:
    st.session_state.p_sid = ""


# ── helper: go to a page ─────────────────────────────────────
def go_to(page):
    st.session_state.page = page


# ── helper: reset survey completely ─────────────────────────
def reset_survey():
    st.session_state.current_q = 0
    st.session_state.answers   = []
    st.session_state.result    = {}
    st.session_state.p_name    = ""
    st.session_state.p_dob     = ""
    st.session_state.p_sid     = ""
    go_to("home")


# ── SHARED HEADER ────────────────────────────────────────────
st.markdown(f"""
<div class="survey-header">
    <h1>🤝 {survey_title}</h1>
    <p>Module: Fundamentals of Programming, 4BUIS008C &nbsp;|&nbsp; v{version}</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════
if st.session_state.page == "home":

    st.markdown("""
    <div class="info-card">
        <h3 style="color:#1e3a8a; margin-top:0">Welcome!</h3>
        <p style="color:#475569; font-size:15px">
        This survey explores how peer friendships influence your academic
        motivation and emotional wellbeing. It contains <strong>15 questions</strong>
        and takes about <strong>3–5 minutes</strong> to complete.
        Please answer all questions honestly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝  Start New Survey", use_container_width=True):
            go_to("info")
            st.rerun()
    with col2:
        if st.button("📂  Load Existing Results", use_container_width=True):
            go_to("load")
            st.rerun()

    st.divider()

    # Psychological states table on home page
    st.markdown("#### 📊 Possible Psychological States")
    states_data = [
        ("0 – 12",  "🔴", "Very Low Peer Support & Poor Adjustment"),
        ("13 – 24", "🟠", "Low Peer Support & Mild Adjustment Issues"),
        ("25 – 36", "🟡", "Moderate Peer Support & Moderate Adjustment"),
        ("37 – 42", "🟢", "Good Peer Support & Good Adjustment"),
        ("43 – 48", "🟢", "Strong Peer Support & Strong Adjustment"),
        ("49 – 54", "🟢", "Excellent Peer Support & Excellent Adjustment"),
        ("55 – 60", "🏆", "Outstanding Peer Support & Outstanding Adjustment"),
    ]

    # for loop — display all states
    for score_range, emoji, label in states_data:
        st.markdown(
            f"**{score_range}** &nbsp; {emoji} &nbsp; {label}"
        )


# ════════════════════════════════════════════════════════════
# PAGE: INFO (participant details)
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "info":

    st.markdown("### 👤 Participant Information")
    st.markdown(
        "<p style='color:#64748b'>Please fill in your details carefully. "
        "All fields are required.</p>",
        unsafe_allow_html=True
    )

    with st.form("info_form"):
        name = st.text_input(
            "Full Name",
            placeholder="e.g. Sarah O'Connor",
            help="Letters, spaces, hyphens and apostrophes only"
        )
        dob = st.text_input(
            "Date of Birth (DD/MM/YYYY)",
            placeholder="e.g. 15/03/2004"
        )
        sid = st.text_input(
            "Student ID",
            placeholder="e.g. 220012",
            help="Digits only, minimum 4 digits"
        )

        col1, col2 = st.columns(2)
        submitted  = col1.form_submit_button(
            "✅  Confirm Details", use_container_width=True
        )
        go_back    = col2.form_submit_button(
            "🏠  Home", use_container_width=True
        )

    if go_back:
        go_to("home")
        st.rerun()

    if submitted:
        # conditional statements — validate all inputs
        errors = []
        if not validate_name(name):
            errors.append("❌ Invalid name. Use letters, spaces, hyphens, or apostrophes only.")
        if not validate_dob(dob):
            errors.append("❌ Invalid date. Use DD/MM/YYYY format (e.g. 15/03/2004).")
        if not validate_sid(sid):
            errors.append("❌ Student ID must contain digits only (minimum 4 digits).")
        if sid in completed_ids:
            errors.append(f"❌ ID {sid} has already completed this survey.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            # save to session
            st.session_state.p_name = name
            st.session_state.p_dob  = dob
            st.session_state.p_sid  = sid
            go_to("ready")
            st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE: READY (confirmation before starting)
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "ready":

    st.markdown(f"""
    <div class="info-card">
        <h3 style="color:#1e3a8a; margin-top:0">✅ Ready to Start?</h3>
        <p style="font-size:15px; color:#334155">
            Hello, <strong>{st.session_state.p_name}</strong>!
            Your details have been saved. You are about to begin the survey.
        </p>
        <p style="font-size:14px; color:#64748b">
            📋 &nbsp; <strong>{question_count} questions</strong> &nbsp;|&nbsp;
            ⏱ &nbsp; Takes about 3–5 minutes &nbsp;|&nbsp;
            ❗ &nbsp; You must answer every question
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀  Start Survey", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.answers   = []
            go_to("survey")
            st.rerun()
    with col2:
        if st.button("✏️  Edit Details", use_container_width=True):
            go_to("info")
            st.rerun()
    with col3:
        if st.button("🏠  Home", use_container_width=True):
            reset_survey()
            st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE: SURVEY (one question at a time)
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "survey":

    questions  = st.session_state.questions
    current    = st.session_state.current_q
    total_qs   = len(questions)             # int
    q          = questions[current]

    # progress bar
    progress = (current) / total_qs        # float
    st.markdown(
        f"<p class='progress-label'>Question {current + 1} of {total_qs}</p>",
        unsafe_allow_html=True
    )
    st.progress(progress)

    # question card
    st.markdown(f"""
    <div class="q-card">
        <div class="q-number">Question {current + 1} of {total_qs}</div>
        <div class="q-text">{q['text']}</div>
    </div>
    """, unsafe_allow_html=True)

    # radio buttons for answer options
    answer_key = f"answer_{current}"
    choice = st.radio(
        "Select your answer:",
        options=q["options"],
        index=None,
        key=answer_key,
        label_visibility="collapsed"
    )

    st.write("")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("➡️  Next Question" if current < total_qs - 1
                     else "✅  Finish Survey",
                     use_container_width=True):
            # while loop equivalent — block if no answer chosen
            if choice is None:
                st.error("❌ Please select an answer before continuing.")
            else:
                idx   = q["options"].index(choice)
                score = q["scores"][idx]
                st.session_state.answers.append(score)
                st.session_state.current_q += 1

                if st.session_state.current_q >= total_qs:
                    go_to("result")
                st.rerun()

    with col2:
        if st.button("🔄  Restart", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.answers   = []
            st.rerun()

    with col3:
        if st.button("🏠  Home", use_container_width=True):
            reset_survey()
            st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE: RESULT
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "result":

    answers    = st.session_state.answers
    total      = sum(answers)                                    # int
    percentage = round((total / (question_count * 4)) * 100, 1) # float
    interp     = interpret_score(total)

    record = {
        "name":          st.session_state.p_name,
        "student_id":    st.session_state.p_sid,
        "date_of_birth": st.session_state.p_dob,
        "submitted":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_score":   total,
        "percentage":    percentage,
        "state":         interp["label"],
        "advice":        interp["advice"],
        "answers":       answers,
        "version":       version
    }

    completed_ids.add(st.session_state.p_sid)
    results_store[st.session_state.p_sid] = record

    # result card
    st.markdown(f"""
    <div class="result-card">
        <div style="font-size:20px; color:#64748b">Your Result</div>
        <div class="result-score">{total} / {question_count * 4}</div>
        <div style="font-size:16px; color:#94a3b8; margin-bottom:12px">
            {percentage}% &nbsp;|&nbsp; {interp['emoji']}
        </div>
        <div class="result-state">{interp['label']}</div>
        <div class="result-advice">{interp['advice']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-card">
        <b>Name:</b> {record['name']} &nbsp;|&nbsp;
        <b>ID:</b> {record['student_id']} &nbsp;|&nbsp;
        <b>DOB:</b> {record['date_of_birth']} &nbsp;|&nbsp;
        <b>Submitted:</b> {record['submitted']}
    </div>
    """, unsafe_allow_html=True)

    # download section
    st.markdown("#### 💾 Download Your Results")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.download_button(
            "⬇ Download JSON",
            json.dumps(record, indent=2, ensure_ascii=False),
            file_name=f"result_{record['student_id']}.json",
            mime="application/json",
            use_container_width=True
        )
    with col_b:
        st.download_button(
            "⬇ Download CSV",
            build_csv(record),
            file_name=f"result_{record['student_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_c:
        st.download_button(
            "⬇ Download TXT",
            build_txt(record),
            file_name=f"result_{record['student_id']}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝  Take Survey Again", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.answers   = []
            go_to("info")
            st.rerun()
    with col2:
        if st.button("🏠  Back to Home", use_container_width=True):
            reset_survey()
            st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE: LOAD EXISTING RESULTS
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "load":

    st.markdown("### 📂 Load Existing Results")
    st.markdown(
        "<p style='color:#64748b'>Upload a previously saved result file "
        "to view your results again.</p>",
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "Upload your result file",
        type=["json", "csv", "txt"]
    )

    if uploaded is not None:
        try:
            if uploaded.name.endswith(".json"):
                data = json.load(uploaded)
                total_s = int(data.get("total_score", 0))
                pct     = data.get("percentage", 0)
                interp  = interpret_score(total_s)

                st.markdown(f"""
                <div class="result-card">
                    <div style="font-size:18px; color:#64748b">Loaded Result</div>
                    <div class="result-score">{total_s} / {question_count * 4}</div>
                    <div style="font-size:15px; color:#94a3b8; margin-bottom:10px">
                        {pct}% &nbsp; {interp['emoji']}
                    </div>
                    <div class="result-state">{data.get('state','')}</div>
                    <div class="result-advice">{data.get('advice','')}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="info-card">
                    <b>Name:</b> {data.get('name','?')} &nbsp;|&nbsp;
                    <b>ID:</b> {data.get('student_id','?')} &nbsp;|&nbsp;
                    <b>Submitted:</b> {data.get('submitted','?')}
                </div>
                """, unsafe_allow_html=True)

            elif uploaded.name.endswith(".csv"):
                content = uploaded.read().decode("utf-8")
                reader  = csv.DictReader(io.StringIO(content))
                data    = next(reader)
                st.success("File loaded successfully!")
                for key, val in data.items():
                    st.markdown(f"**{key}:** {val}")

            elif uploaded.name.endswith(".txt"):
                st.text(uploaded.read().decode("utf-8"))

        except Exception as e:
            st.error(f"Error reading file: {e}")

    if st.button("🏠  Back to Home", use_container_width=True):
        go_to("home")
        st.rerun()


# ── FOOTER ────────────────────────────────────────────────────
st.divider()
st.markdown(
    f"<p style='text-align:center; color:#94a3b8; font-size:12px'>"
    f"{survey_title} &nbsp;|&nbsp; 4BUIS008C &nbsp;|&nbsp; v{version} &nbsp;|&nbsp; Built with Streamlit</p>",
    unsafe_allow_html=True
)
