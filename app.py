# ============================================================
# Peer Social Support Survey — Streamlit Web App
# Module: Fundamentals of Programming, 4BUIS008C
# ============================================================

import streamlit as st
import json
import csv
import re
import os
from datetime import datetime

# ── Variable types (all 10 required types) ───────────────────
survey_title   = "Peer Social Support Survey"      # str
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
valid_choices  = range(1, 4)                       # range
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


# ── FUNCTION 1: Validate name ────────────────────────────────
def validate_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z\s'\-]*", name.strip())) and len(name.strip()) >= 2


# ── FUNCTION 2: Validate date of birth ──────────────────────
def validate_dob(dob: str) -> bool:
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", dob):
        return False
    day   = int(dob[:2])
    month = int(dob[3:5])
    year  = int(dob[6:])
    return 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2010


# ── FUNCTION 3: Validate student ID ─────────────────────────
def validate_sid(sid: str) -> bool:
    return sid.isdigit() and len(sid) >= 4


# ── FUNCTION 4: Interpret score → psychological state ────────
def interpret_score(score: int) -> dict:
    if score <= 12:
        label  = "Very Low Peer Support & Poor Adjustment"
        advice = "Very limited support network. High risk of emotional difficulties and low motivation."
        color  = "red"
    elif score <= 24:
        label  = "Low Peer Support & Mild Adjustment Issues"
        advice = "Limited friendships affecting emotional balance. Try to build closer peer connections."
        color  = "orange"
    elif score <= 36:
        label  = "Moderate Peer Support & Moderate Adjustment"
        advice = "Some supportive friendships. Occasional emotional and academic challenges present."
        color  = "yellow"
    elif score <= 42:
        label  = "Good Peer Support & Good Adjustment"
        advice = "Healthy peer network with positive effects on motivation and wellbeing."
        color  = "lightgreen"
    elif score <= 48:
        label  = "Strong Peer Support & Strong Adjustment"
        advice = "Strong friendships supporting academic success and emotional stability."
        color  = "green"
    elif score <= 54:
        label  = "Excellent Peer Support & Excellent Adjustment"
        advice = "Excellent friendship quality. High motivation and consistent academic performance."
        color  = "green"
    else:
        label  = "Outstanding Peer Support & Outstanding Adjustment"
        advice = "Exceptional peer relationships. A model support environment for academic success."
        color  = "green"
    return {"label": label, "advice": advice, "color": color}


# ── FUNCTION 5: Load questions from file if available ────────
def load_questions():
    if os.path.exists("questions.json"):
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return QUESTIONS


# ── STREAMLIT APP ─────────────────────────────────────────────
st.set_page_config(page_title=survey_title, page_icon="🤝", layout="centered")

st.title(f"🤝 {survey_title}")
st.caption(f"Module: Fundamentals of Programming, 4BUIS008C  |  v{version}")
st.info("This survey explores how peer friendships influence your academic motivation and emotional adjustment. Please answer all questions honestly.")

questions = load_questions()

# ── Tabs: New Survey / Load Results ──────────────────────────
tab1, tab2, tab3 = st.tabs(["📝 New Survey", "📂 Load Results", "📊 Psychological States"])

# ════════════════════════════════════════════════════════════
# TAB 1 — NEW SURVEY
# ════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Participant Information")

    name       = st.text_input("Full Name", placeholder="e.g. Sarah O'Connor")
    dob        = st.text_input("Date of Birth (DD/MM/YYYY)", placeholder="e.g. 15/03/2004")
    student_id = st.text_input("Student ID (digits only)", placeholder="e.g. 220012")

    st.divider()
    st.subheader("Survey Questions")
    st.caption("For each question, select the answer that best describes your experience.")

    answers     = []
    total_score = 0

    # for loop — display all questions
    for i in range(len(questions)):
        q      = questions[i]
        opts   = q["options"]
        choice = st.selectbox(f"Q{i + 1}. {q['text']}", opts, key=f"q{i}", index=None, placeholder="Select an answer...")
        if choice is not None:
            idx   = opts.index(choice)
            score = q["scores"][idx]
            answers.append(score)
            total_score += score

    st.divider()

    if st.button("✅ Submit Survey", use_container_width=True):

        # Validate inputs using conditionals
        errors = []

        if not validate_name(name):
            errors.append("❌ Invalid name. Use letters, spaces, hyphens, or apostrophes only.")
        if not validate_dob(dob):
            errors.append("❌ Invalid date of birth. Use DD/MM/YYYY format (e.g. 15/03/2004).")
        if not validate_sid(student_id):
            errors.append("❌ Student ID must contain digits only (minimum 4 digits).")
        if len(answers) < question_count:
            errors.append(f"❌ Please answer all {question_count} questions before submitting.")

        if errors:
            for err in errors:
                st.error(err)

        else:
            result       = interpret_score(total_score)
            percentage   = round((total_score / (question_count * 4)) * 100, 1)  # float

            st.success("Survey submitted successfully!")
            st.markdown(f"### 🏆 Your Result")

            col1, col2 = st.columns(2)
            col1.metric("Total Score", f"{total_score} / {question_count * 4}")
            col2.metric("Percentage", f"{percentage}%")

            st.markdown(f"**Psychological State:** {result['label']}")
            st.info(f"💬 {result['advice']}")

            # Build record dict
            record = {
                "name":        name,
                "student_id":  student_id,
                "dob":         dob,
                "submitted":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_score": total_score,
                "percentage":  percentage,
                "state":       result["label"],
                "advice":      result["advice"],
                "answers":     answers,
                "version":     version
            }

            results_store[student_id] = record

            # Download buttons
            st.divider()
            st.subheader("💾 Download Your Results")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                json_str = json.dumps(record, indent=2, ensure_ascii=False)
                st.download_button("⬇ JSON", json_str,
                                   file_name=f"result_{student_id}.json",
                                   mime="application/json",
                                   use_container_width=True)

            with col_b:
                import io
                csv_buf = io.StringIO()
                flat    = {k: v for k, v in record.items() if k != "answers"}
                writer  = csv.DictWriter(csv_buf, fieldnames=flat.keys())
                writer.writeheader()
                writer.writerow(flat)
                st.download_button("⬇ CSV", csv_buf.getvalue(),
                                   file_name=f"result_{student_id}.csv",
                                   mime="text/csv",
                                   use_container_width=True)

            with col_c:
                txt_lines = [
                    "=" * 50,
                    f"  {survey_title} - Results",
                    "=" * 50,
                ]
                for key, val in record.items():
                    txt_lines.append(f"  {key}: {val}")
                txt_lines.append("=" * 50)
                txt_str = "\n".join(txt_lines)
                st.download_button("⬇ TXT", txt_str,
                                   file_name=f"result_{student_id}.txt",
                                   mime="text/plain",
                                   use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — LOAD RESULTS
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Load Existing Results")
    st.caption("Upload a previously saved result file (JSON or CSV) to view it again.")

    uploaded = st.file_uploader("Upload result file", type=["json", "csv", "txt"])

    if uploaded is not None:
        if uploaded.name.endswith(".json"):
            data = json.load(uploaded)
            st.success("File loaded successfully!")
            col1, col2 = st.columns(2)
            col1.metric("Total Score", f"{data.get('total_score', '?')} / {question_count * 4}")
            col2.metric("Percentage",  f"{data.get('percentage', '?')}%")
            st.markdown(f"**Name:** {data.get('name', '?')}")
            st.markdown(f"**Student ID:** {data.get('student_id', '?')}")
            st.markdown(f"**Submitted:** {data.get('submitted', '?')}")
            st.markdown(f"**State:** {data.get('state', '?')}")
            st.info(data.get('advice', ''))

        elif uploaded.name.endswith(".csv"):
            import io
            content = uploaded.read().decode("utf-8")
            reader  = csv.DictReader(io.StringIO(content))
            data    = next(reader)
            st.success("File loaded successfully!")
            st.markdown(f"**Name:** {data.get('name', '?')}")
            st.markdown(f"**Total Score:** {data.get('total_score', '?')}")
            st.markdown(f"**State:** {data.get('state', '?')}")

        elif uploaded.name.endswith(".txt"):
            content = uploaded.read().decode("utf-8")
            st.text(content)

# ════════════════════════════════════════════════════════════
# TAB 3 — PSYCHOLOGICAL STATES TABLE
# ════════════════════════════════════════════════════════════
with tab3:
    st.subheader("All Possible Psychological States")
    st.caption(f"Based on total score out of {question_count * 4} points")

    states_data = [
        ("0 – 12",  "Very Low Peer Support & Poor Adjustment",        "High risk of emotional difficulties and low motivation."),
        ("13 – 24", "Low Peer Support & Mild Adjustment Issues",       "Limited friendships affecting emotional balance."),
        ("25 – 36", "Moderate Peer Support & Moderate Adjustment",     "Some support present; occasional emotional challenges."),
        ("37 – 42", "Good Peer Support & Good Adjustment",             "Healthy peer network with positive effects on wellbeing."),
        ("43 – 48", "Strong Peer Support & Strong Adjustment",         "Strong friendships supporting academic and emotional health."),
        ("49 – 54", "Excellent Peer Support & Excellent Adjustment",   "Excellent friendship quality and academic performance."),
        ("55 – 60", "Outstanding Peer Support & Outstanding Adjustment","Exceptional peer relationships and support environment."),
    ]

    # for loop — display states table
    for score_range, label, description in states_data:
        with st.expander(f"Score {score_range}  —  {label}"):
            st.write(description)

st.divider()
st.caption(f"{survey_title}  |  4BUIS008C  |  v{version}  |  Built with Streamlit")
