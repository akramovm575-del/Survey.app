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

st.set_page_config(page_title="Peer Social Support Survey",
                   page_icon="🤝", layout="centered")

# ── All 10 variable types ────────────────────────────────────
survey_title   = "Peer Social Support Survey"    # str
version        = 1.0                              # float
question_count = 15                               # int
survey_active  = True                             # bool
score_ranges   = [0, 13, 25, 37, 43, 49, 55]     # list
state_labels   = (                                # tuple
    "Very Low Support", "Low Support",
    "Moderate Support", "Good Support",
    "Strong Support", "Excellent Support",
    "Outstanding Support"
)
valid_choices  = range(1, 6)                      # range
results_store  = {}                               # dict
completed_ids  = set()                            # set
locked_fields  = frozenset({"title", "version"})  # frozenset

# ── Questions embedded in code ───────────────────────────────
QUESTIONS = [
    {"text": "My friends help me when I face academic difficulties.",
     "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "I feel comfortable sharing personal problems with my close friends.",
     "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "Having supportive friends motivates me to do better academically.",
     "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "I find it hard to find a friend I can open up to about my struggles.",
     "options": ["Always (4)", "Often (3)", "Sometimes (2)", "Rarely (1)", "Never (0)"],
     "scores": [4, 3, 2, 1, 0]},
    {"text": "Arguments or conflicts with friends distract me from my studies.",
     "options": ["Always (4)", "Often (3)", "Sometimes (2)", "Rarely (1)", "Never (0)"],
     "scores": [4, 3, 2, 1, 0]},
    {"text": "My friends cheer me up when I feel like giving up on my studies.",
     "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "I feel emotionally stable when I have strong friendships.",
     "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "I talk about academic challenges with my close friends.",
     "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "Unresolved conflicts with peers make me feel anxious and unfocused.",
     "options": ["Not at all (0)", "Slightly (1)", "Moderately (2)", "Significantly (3)", "Extremely (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "My friends help me feel like I belong at university.",
     "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "I feel lonely and isolated when I lack close friendships.",
     "options": ["Always (4)", "Often (3)", "Sometimes (2)", "Rarely (1)", "Never (0)"],
     "scores": [4, 3, 2, 1, 0]},
    {"text": "Talking to friends about my worries improves how I feel emotionally.",
     "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "Friendship conflicts reduce my desire to attend or engage with classes.",
     "options": ["Not at all (0)", "Slightly (1)", "Moderately (2)", "Significantly (3)", "Extremely (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "I feel safe being honest and vulnerable with my closest friends.",
     "options": ["Never (0)", "Rarely (1)", "Sometimes (2)", "Often (3)", "Always (4)"],
     "scores": [0, 1, 2, 3, 4]},
    {"text": "Overall, my friendships have a positive effect on my academic performance.",
     "options": ["Strongly disagree (0)", "Disagree (1)", "Neutral (2)", "Agree (3)", "Strongly agree (4)"],
     "scores": [0, 1, 2, 3, 4]},
]


# ── FUNCTION 1: Load questions from external file ────────────
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
    day, month, year = int(dob[:2]), int(dob[3:5]), int(dob[6:])
    return 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2010


# ── FUNCTION 4: Validate student ID ─────────────────────────
def validate_sid(sid):
    return sid.isdigit() and len(sid) >= 4


# ── FUNCTION 5: Interpret total score ────────────────────────
def interpret_score(score):
    # if / elif / else conditional statements
    if score <= 12:
        label, advice, color = ("Very Low Peer Support & Poor Adjustment",
            "Very limited support network. High risk of emotional difficulties.", "#ef4444")
    elif score <= 24:
        label, advice, color = ("Low Peer Support & Mild Adjustment Issues",
            "Limited friendships affecting emotional balance.", "#f97316")
    elif score <= 36:
        label, advice, color = ("Moderate Peer Support & Moderate Adjustment",
            "Some supportive friendships. Occasional emotional challenges.", "#eab308")
    elif score <= 42:
        label, advice, color = ("Good Peer Support & Good Adjustment",
            "Healthy peer network with positive effects on wellbeing.", "#22c55e")
    elif score <= 48:
        label, advice, color = ("Strong Peer Support & Strong Adjustment",
            "Strong friendships supporting academic and emotional health.", "#16a34a")
    elif score <= 54:
        label, advice, color = ("Excellent Peer Support & Excellent Adjustment",
            "Excellent friendship quality and consistent academic performance.", "#15803d")
    else:
        label, advice, color = ("Outstanding Peer Support & Outstanding Adjustment",
            "Exceptional peer relationships. Model support environment.", "#166534")
    return {"label": label, "advice": advice, "color": color}


# ── FUNCTION 6: Build TXT download content ──────────────────
def build_txt(record):
    lines = ["=" * 50, f"  {survey_title} - Results", "=" * 50]
    for key, val in record.items():
        lines.append(f"  {key}: {val}")
    lines.append("=" * 50)
    return "\n".join(lines)


# ── FUNCTION 7: Build CSV download content ──────────────────
def build_csv(record):
    buf    = io.StringIO()
    flat   = {k: v for k, v in record.items() if k != "answers"}
    writer = csv.DictWriter(buf, fieldnames=flat.keys())
    writer.writeheader()
    writer.writerow(flat)
    return buf.getvalue()


# ════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
.stApp { background-color: #f8fafc; }
.hdr {
    background: linear-gradient(135deg,#1e3a8a,#2563eb);
    color:white; padding:24px 28px; border-radius:12px;
    margin-bottom:20px; text-align:center;
}
.hdr h2 { margin:0; font-size:22px; }
.hdr p  { margin:5px 0 0; font-size:12px; opacity:.85; }
.card {
    background:white; border-radius:12px;
    padding:22px 26px; margin-bottom:14px;
    box-shadow:0 2px 8px rgba(0,0,0,.07);
}
.qcard {
    background:white; border-left:5px solid #2563eb;
    border-radius:10px; padding:20px 24px; margin-bottom:12px;
    box-shadow:0 2px 6px rgba(0,0,0,.06);
}
.qnum { color:#2563eb; font-size:11px; font-weight:700;
        letter-spacing:1px; text-transform:uppercase; }
.qtxt { font-size:16px; font-weight:600; color:#1e293b; margin-top:4px; }
.rbox {
    background:white; border-radius:14px; padding:28px;
    text-align:center; box-shadow:0 4px 16px rgba(0,0,0,.10);
    margin-bottom:16px;
}
.rscore { font-size:50px; font-weight:800; color:#1e3a8a; }
div[data-testid="stButton"]>button {
    border-radius:8px !important; font-weight:600 !important;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════
defaults = {
    "page": "home", "questions": load_questions(),
    "current_q": 0,  "answers": [],
    "p_name": "",    "p_dob": "", "p_sid": "",
    "result": {},    "error": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── shared header ─────────────────────────────────────────────
st.markdown(f"""
<div class="hdr">
  <h2>🤝 {survey_title}</h2>
  <p>Fundamentals of Programming, 4BUIS008C &nbsp;|&nbsp; v{version}</p>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════
if st.session_state.page == "home":

    st.markdown("""
    <div class="card">
      <h3 style="color:#1e3a8a;margin-top:0">Welcome!</h3>
      <p style="color:#475569;font-size:15px">
        This survey explores how peer friendships influence your academic
        motivation and emotional wellbeing. It contains <b>15 questions</b>
        and takes about <b>3–5 minutes</b>. Please answer honestly.
      </p>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("📝  Start New Survey", use_container_width=True):
        st.session_state.page  = "info"
        st.session_state.error = ""
        st.rerun()
    if c2.button("📂  Load Existing Results", use_container_width=True):
        st.session_state.page = "load"
        st.rerun()

    st.divider()
    st.markdown("#### 📊 Possible Psychological States")

    states_info = [
        ("0 – 12",  "🔴", "Very Low Peer Support & Poor Adjustment"),
        ("13 – 24", "🟠", "Low Peer Support & Mild Adjustment Issues"),
        ("25 – 36", "🟡", "Moderate Peer Support & Moderate Adjustment"),
        ("37 – 42", "🟢", "Good Peer Support & Good Adjustment"),
        ("43 – 48", "🟢", "Strong Peer Support & Strong Adjustment"),
        ("49 – 54", "🟢", "Excellent Peer Support & Excellent Adjustment"),
        ("55 – 60", "🏆", "Outstanding Peer Support & Outstanding Adjustment"),
    ]
    # for loop — display all 7 states
    for score_range, emoji, label in states_info:
        st.markdown(f"**{score_range}** &nbsp; {emoji} &nbsp; {label}")


# ════════════════════════════════════════════════════════════
# PAGE: INFO
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "info":

    st.markdown("### 👤 Participant Information")
    st.caption("All fields are required. Please fill in your details carefully.")

    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = ""

    name = st.text_input("Full Name",
                         value=st.session_state.p_name,
                         placeholder="e.g. Sarah O'Connor")
    dob  = st.text_input("Date of Birth (DD/MM/YYYY)",
                         value=st.session_state.p_dob,
                         placeholder="e.g. 15/03/2004")
    sid  = st.text_input("Student ID (digits only)",
                         value=st.session_state.p_sid,
                         placeholder="e.g. 220012")

    c1, c2 = st.columns(2)
    confirm = c1.button("✅  Confirm & Continue", use_container_width=True)
    go_home = c2.button("🏠  Back to Home",       use_container_width=True)

    if go_home:
        st.session_state.page = "home"
        st.rerun()

    if confirm:
        # conditional statements — validate inputs
        errors = []
        if not validate_name(name):
            errors.append("Invalid name. Use letters, spaces, hyphens or apostrophes only.")
        if not validate_dob(dob):
            errors.append("Invalid date. Use DD/MM/YYYY format (e.g. 15/03/2004).")
        if not validate_sid(sid):
            errors.append("Student ID must be digits only (min 4 digits).")

        if errors:
            st.error("❌ " + "  |  ".join(errors))
        else:
            st.session_state.p_name = name
            st.session_state.p_dob  = dob
            st.session_state.p_sid  = sid
            st.session_state.page   = "ready"
            st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE: READY TO START
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "ready":

    st.markdown(f"""
    <div class="card">
      <h3 style="color:#1e3a8a;margin-top:0">✅ Ready to Start?</h3>
      <p style="font-size:15px;color:#334155">
        Hello, <b>{st.session_state.p_name}</b>!
        Your details have been saved. You are about to begin the survey.
      </p>
      <p style="font-size:14px;color:#64748b">
        📋 &nbsp;<b>{question_count} questions</b>
        &nbsp;|&nbsp; ⏱ About 3–5 minutes
        &nbsp;|&nbsp; ❗ You must answer every question to proceed
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:12px 0">
      <p style="font-size:13px;color:#94a3b8;margin:0">
        <b>Name:</b> {st.session_state.p_name} &nbsp;|&nbsp;
        <b>DOB:</b> {st.session_state.p_dob} &nbsp;|&nbsp;
        <b>ID:</b> {st.session_state.p_sid}
      </p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    if c1.button("🚀  Start Survey",  use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers   = []
        st.session_state.page      = "survey"
        st.rerun()
    if c2.button("✏️  Edit Details",  use_container_width=True):
        st.session_state.page = "info"
        st.rerun()
    if c3.button("🏠  Back to Home", use_container_width=True):
        st.session_state.page   = "home"
        st.session_state.p_name = ""
        st.session_state.p_dob  = ""
        st.session_state.p_sid  = ""
        st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE: SURVEY — one question at a time
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "survey":

    questions = st.session_state.questions
    current   = st.session_state.current_q   # int
    total_qs  = len(questions)                # int
    q         = questions[current]

    # progress bar
    progress = current / total_qs             # float
    st.markdown(
        f"<p style='color:#64748b;font-size:13px;margin-bottom:4px'>"
        f"Question {current + 1} of {total_qs}</p>",
        unsafe_allow_html=True)
    st.progress(progress)

    # question card
    st.markdown(f"""
    <div class="qcard">
      <div class="qnum">Question {current + 1} of {total_qs}</div>
      <div class="qtxt">{q['text']}</div>
    </div>""", unsafe_allow_html=True)

    # answer options — key changes each question so it always resets
    choice = st.radio("Select your answer:", options=q["options"],
                      index=None, key=f"q_{current}",
                      label_visibility="collapsed")

    st.write("")
    btn_label = "➡️  Next Question" if current < total_qs - 1 else "✅  Finish Survey"

    c1, c2, c3 = st.columns([3, 1, 1])

    if c1.button(btn_label, use_container_width=True):
        if choice is None:
            # blocks if no answer selected — equivalent to while loop validation
            st.error("❌ Please select an answer before continuing.")
        else:
            idx   = q["options"].index(choice)
            score = q["scores"][idx]
            st.session_state.answers.append(score)
            st.session_state.current_q += 1
            if st.session_state.current_q >= total_qs:
                st.session_state.page = "result"
            st.rerun()

    if c2.button("🔄 Restart", use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers   = []
        st.rerun()

    if c3.button("🏠 Home", use_container_width=True):
        st.session_state.page      = "home"
        st.session_state.current_q = 0
        st.session_state.answers   = []
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
    results_store[st.session_state.p_sid] = record

    st.markdown(f"""
    <div class="rbox">
      <p style="color:#64748b;margin:0;font-size:14px">Your Result</p>
      <div class="rscore">{total} / {question_count * 4}</div>
      <p style="color:#94a3b8;font-size:15px;margin:2px 0 12px">{percentage}%</p>
      <p style="font-size:18px;font-weight:700;color:{interp['color']};margin:0">
        {interp['label']}
      </p>
      <p style="font-size:14px;color:#475569;margin-top:8px">{interp['advice']}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card" style="font-size:14px;color:#475569">
      <b>Name:</b> {record['name']} &nbsp;|&nbsp;
      <b>ID:</b> {record['student_id']} &nbsp;|&nbsp;
      <b>DOB:</b> {record['date_of_birth']} &nbsp;|&nbsp;
      <b>Submitted:</b> {record['submitted']}
    </div>""", unsafe_allow_html=True)

    st.markdown("#### 💾 Download Your Results")
    ca, cb, cc = st.columns(3)
    ca.download_button("⬇ JSON",
        json.dumps(record, indent=2, ensure_ascii=False),
        file_name=f"result_{record['student_id']}.json",
        mime="application/json", use_container_width=True)
    cb.download_button("⬇ CSV", build_csv(record),
        file_name=f"result_{record['student_id']}.csv",
        mime="text/csv", use_container_width=True)
    cc.download_button("⬇ TXT", build_txt(record),
        file_name=f"result_{record['student_id']}.txt",
        mime="text/plain", use_container_width=True)

    st.write("")
    c1, c2 = st.columns(2)
    if c1.button("📝  Take Survey Again", use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers   = []
        st.session_state.page      = "info"
        st.rerun()
    if c2.button("🏠  Back to Home", use_container_width=True):
        for k in ["p_name", "p_dob", "p_sid", "answers"]:
            st.session_state[k] = "" if k != "answers" else []
        st.session_state.current_q = 0
        st.session_state.page      = "home"
        st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE: LOAD EXISTING RESULTS
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "load":

    st.markdown("### 📂 Load Existing Results")
    st.caption("Upload a previously saved result file to view it again.")

    uploaded = st.file_uploader("Upload result file", type=["json", "csv", "txt"])

    if uploaded is not None:
        try:
            if uploaded.name.endswith(".json"):
                data   = json.load(uploaded)
                total  = int(data.get("total_score", 0))
                interp = interpret_score(total)
                st.markdown(f"""
                <div class="rbox">
                  <p style="color:#64748b;margin:0;font-size:14px">Loaded Result</p>
                  <div class="rscore">{total} / {question_count * 4}</div>
                  <p style="font-size:18px;font-weight:700;
                     color:{interp['color']};margin:8px 0 4px">
                    {data.get('state','')}
                  </p>
                  <p style="font-size:14px;color:#475569">
                    {data.get('advice','')}
                  </p>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card" style="font-size:14px;color:#475569">
                  <b>Name:</b> {data.get('name','?')} &nbsp;|&nbsp;
                  <b>ID:</b> {data.get('student_id','?')} &nbsp;|&nbsp;
                  <b>Submitted:</b> {data.get('submitted','?')}
                </div>""", unsafe_allow_html=True)

            elif uploaded.name.endswith(".csv"):
                content = uploaded.read().decode("utf-8")
                data    = next(csv.DictReader(io.StringIO(content)))
                st.success("File loaded successfully!")
                for key, val in data.items():
                    st.markdown(f"**{key}:** {val}")

            elif uploaded.name.endswith(".txt"):
                st.text(uploaded.read().decode("utf-8"))

        except Exception as e:
            st.error(f"Error reading file: {e}")

    if st.button("🏠  Back to Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()


# ── FOOTER ────────────────────────────────────────────────────
st.divider()
st.markdown(
    f"<p style='text-align:center;color:#94a3b8;font-size:12px'>"
    f"{survey_title} &nbsp;|&nbsp; 4BUIS008C &nbsp;|&nbsp; "
    f"v{version} &nbsp;|&nbsp; Built with Streamlit</p>",
    unsafe_allow_html=True)
