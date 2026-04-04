# ============================================================
# Student ID  : 00024431
# Student     : Muhammadsodik Akramov
# Course      : Fundamentals of Programming, 4BUIS008C
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

# -------- REQUIRED VARIABLE TYPES --------
survey_title   = "Peer Social Support Survey"    # str
version        = 1.0                              # float
question_count = 20                               # int
survey_active  = True                             # bool
score_ranges   = [0, 16, 33, 49, 57, 65, 73]     # list
state_labels   = (                                # tuple
    "Very Low", "Low", "Moderate", "Good",
    "Strong", "Excellent", "Outstanding"
)
valid_choices  = range(1, 6)                      # range
results_store  = {}                               # dict
completed_ids  = set()                            # set
locked_fields  = frozenset({"title", "version"})  # frozenset

# -------- QUESTIONS --------
QUESTIONS = [
    {"q": "My friends help me when I face academic difficulties.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "I feel comfortable sharing personal problems with my close friends.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "Having supportive friends motivates me to do better academically.",
     "opts": [("Strongly disagree", 0), ("Disagree", 1), ("Neutral", 2), ("Agree", 3), ("Strongly agree", 4)]},
    {"q": "I find it hard to find a friend I can open up to about my struggles.",
     "opts": [("Always", 4), ("Often", 3), ("Sometimes", 2), ("Rarely", 1), ("Never", 0)]},
    {"q": "Arguments or conflicts with friends distract me from my studies.",
     "opts": [("Always", 4), ("Often", 3), ("Sometimes", 2), ("Rarely", 1), ("Never", 0)]},
    {"q": "My friends cheer me up when I feel like giving up on my studies.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "I feel emotionally stable when I have strong friendships.",
     "opts": [("Strongly disagree", 0), ("Disagree", 1), ("Neutral", 2), ("Agree", 3), ("Strongly agree", 4)]},
    {"q": "I talk about academic challenges with my close friends.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "Unresolved conflicts with peers make me feel anxious and unfocused.",
     "opts": [("Not at all", 0), ("Slightly", 1), ("Moderately", 2), ("Significantly", 3), ("Extremely", 4)]},
    {"q": "My friends help me feel like I belong at university.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "I feel lonely and isolated when I lack close friendships.",
     "opts": [("Always", 4), ("Often", 3), ("Sometimes", 2), ("Rarely", 1), ("Never", 0)]},
    {"q": "Talking to friends about my worries improves how I feel emotionally.",
     "opts": [("Strongly disagree", 0), ("Disagree", 1), ("Neutral", 2), ("Agree", 3), ("Strongly agree", 4)]},
    {"q": "Friendship conflicts reduce my desire to attend or engage with classes.",
     "opts": [("Not at all", 0), ("Slightly", 1), ("Moderately", 2), ("Significantly", 3), ("Extremely", 4)]},
    {"q": "I feel safe being honest and vulnerable with my closest friends.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "Overall, my friendships have a positive effect on my academic performance.",
     "opts": [("Strongly disagree", 0), ("Disagree", 1), ("Neutral", 2), ("Agree", 3), ("Strongly agree", 4)]},
    {"q": "My friends encourage me to attend classes and keep up with coursework.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "I feel understood and accepted by my peer group at university.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "Peer pressure from friends negatively affects my study habits.",
     "opts": [("Always", 4), ("Often", 3), ("Sometimes", 2), ("Rarely", 1), ("Never", 0)]},
    {"q": "I can rely on my friends for emotional support during stressful times.",
     "opts": [("Never", 0), ("Rarely", 1), ("Sometimes", 2), ("Often", 3), ("Always", 4)]},
    {"q": "My friendships help me develop better communication and social skills.",
     "opts": [("Strongly disagree", 0), ("Disagree", 1), ("Neutral", 2), ("Agree", 3), ("Strongly agree", 4)]},
]

# -------- FUNCTIONS --------
def load_questions():
    if os.path.exists("questions.json"):
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return QUESTIONS

def validate_name(name):
    name = name.strip()
    return len(name) >= 2 and not any(c.isdigit() for c in name)

def validate_dob(dob):
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", dob):
        return False
    day, month, year = int(dob[:2]), int(dob[3:5]), int(dob[6:])
    return 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2010

def validate_sid(sid):
    return sid.isdigit() and len(sid) >= 4

def interpret_score(score):
    if score <= 15:
        label, advice = ("Very Low Peer Support & Poor Adjustment",
            "Very limited support. High risk of emotional difficulties.")
    elif score <= 32:
        label, advice = ("Low Peer Support & Mild Adjustment Issues",
            "Limited friendships affecting emotional balance.")
    elif score <= 48:
        label, advice = ("Moderate Peer Support & Moderate Adjustment",
            "Some support present. Occasional emotional challenges.")
    elif score <= 56:
        label, advice = ("Good Peer Support & Good Adjustment",
            "Healthy peer network with positive effects on wellbeing.")
    elif score <= 64:
        label, advice = ("Strong Peer Support & Strong Adjustment",
            "Strong friendships supporting academic and emotional health.")
    elif score <= 72:
        label, advice = ("Excellent Peer Support & Excellent Adjustment",
            "Excellent friendship quality and consistent performance.")
    else:
        label, advice = ("Outstanding Peer Support & Outstanding Adjustment",
            "Exceptional peer relationships. Model support environment.")
    return label, advice

def build_csv(record):
    buf    = io.StringIO()
    flat   = {k: v for k, v in record.items() if k != "answers"}
    writer = csv.DictWriter(buf, fieldnames=flat.keys())
    writer.writeheader()
    writer.writerow(flat)
    return buf.getvalue()

def build_txt(record):
    lines = ["=" * 50, f"  {survey_title} - Results", "=" * 50]
    for k, v in record.items():
        lines.append(f"  {k}: {v}")
    lines.append("=" * 50)
    return "\n".join(lines)

# -------- SESSION STATE --------
defaults = {
    "page": "home", "questions": load_questions(),
    "current_q": 0,  "answers": [],
    "p_given": "",   "p_surname": "",
    "p_dob": "",     "p_sid": "",
    "result": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------- HEADER --------
st.markdown(f"""
<div style="background:#1E3A8A;color:white;padding:20px 24px;
border-radius:10px;margin-bottom:20px;text-align:center">
<h2 style="margin:0;font-size:22px">🤝 {survey_title}</h2>
<p style="margin:4px 0 0;font-size:12px;opacity:.85">
Fundamentals of Programming, 4BUIS008C &nbsp;|&nbsp;
Muhammadsodik Akramov &nbsp;|&nbsp; ID: 00024431 &nbsp;|&nbsp; v{version}
</p></div>""", unsafe_allow_html=True)

# ======================================================
# PAGE: HOME
# ======================================================
if st.session_state.page == "home":

    st.markdown("### Welcome!")
    st.write("This survey explores how peer friendships influence "
             "your academic motivation and emotional wellbeing. "
             f"It contains **{question_count} questions** and takes about **3–5 minutes**.")

    c1, c2 = st.columns(2)
    if c1.button("📝  Start New Survey", use_container_width=True):
        st.session_state.page = "info"
        st.rerun()
    if c2.button("📂  Load Existing Results", use_container_width=True):
        st.session_state.page = "load"
        st.rerun()

    st.divider()
    st.markdown("#### Possible Psychological States")
    states_info = [
        ("0 – 15",  "Very Low Peer Support & Poor Adjustment"),
        ("16 – 32", "Low Peer Support & Mild Adjustment Issues"),
        ("33 – 48", "Moderate Peer Support & Moderate Adjustment"),
        ("49 – 56", "Good Peer Support & Good Adjustment"),
        ("57 – 64", "Strong Peer Support & Strong Adjustment"),
        ("65 – 72", "Excellent Peer Support & Excellent Adjustment"),
        ("73 – 80", "Outstanding Peer Support & Outstanding Adjustment"),
    ]
    # for loop — display all states
    for score_range, label in states_info:
        st.markdown(f"**{score_range}** — {label}")

# ======================================================
# PAGE: INFO
# ======================================================
elif st.session_state.page == "info":

    st.markdown("### 👤 Participant Information")

    c1, c2 = st.columns(2)
    given   = c1.text_input("Given Name",
                             value=st.session_state.p_given,
                             placeholder="e.g. Sarah")
    surname = c2.text_input("Surname",
                             value=st.session_state.p_surname,
                             placeholder="e.g. Smith")
    dob = st.text_input("Date of Birth (DD/MM/YYYY)",
                        value=st.session_state.p_dob,
                        placeholder="e.g. 15/03/2004")
    sid = st.text_input("Student ID (digits only)",
                        value=st.session_state.p_sid,
                        placeholder="e.g. 220012")

    ca, cb = st.columns(2)
    confirm  = ca.button("✅  Confirm & Continue", use_container_width=True)
    go_home  = cb.button("🏠  Back to Home",       use_container_width=True)

    if go_home:
        st.session_state.page = "home"
        st.rerun()

    if confirm:
        errors = []
        # conditional statements — validate inputs
        if not validate_name(given):
            errors.append("Invalid given name.")
        if not validate_name(surname):
            errors.append("Invalid surname.")
        if not validate_dob(dob):
            errors.append("Invalid date — use DD/MM/YYYY.")
        if not validate_sid(sid):
            errors.append("Student ID must be digits only (min 4).")
        if errors:
            st.error("❌  " + "   |   ".join(errors))
        else:
            st.session_state.p_given   = given
            st.session_state.p_surname = surname
            st.session_state.p_dob     = dob
            st.session_state.p_sid     = sid
            st.session_state.page      = "ready"
            st.rerun()

# ======================================================
# PAGE: READY
# ======================================================
elif st.session_state.page == "ready":

    name = f"{st.session_state.p_given} {st.session_state.p_surname}"
    st.markdown(f"### ✅ Ready to Start?")
    st.markdown(f"Hello, **{name}**! You are about to begin the survey.")
    st.markdown(f"📋 **{question_count} questions** &nbsp;|&nbsp; "
                f"⏱ About 3–5 minutes &nbsp;|&nbsp; "
                f"❗ Answer every question")
    st.caption(f"Name: {name}   |   DOB: {st.session_state.p_dob}"
               f"   |   ID: {st.session_state.p_sid}")

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
        st.session_state.page    = "home"
        st.session_state.p_given = st.session_state.p_surname = ""
        st.session_state.p_dob   = st.session_state.p_sid = ""
        st.rerun()

# ======================================================
# PAGE: SURVEY — one question at a time
# ======================================================
elif st.session_state.page == "survey":

    questions = st.session_state.questions
    current   = st.session_state.current_q
    total     = len(questions)              # int
    q         = questions[current]

    progress = current / total              # float
    st.markdown(f"**Question {current + 1} of {total}**")
    st.progress(progress)

    st.markdown(f"### {q['q']}")

    opts   = [o[0] for o in q["opts"]]
    choice = st.radio("Select your answer:", opts,
                      index=None, key=f"q_{current}",
                      label_visibility="collapsed")

    btn_label = "➡️  Next" if current < total - 1 else "✅  Finish"
    c1, c2 = st.columns([3, 1])

    if c1.button(btn_label, use_container_width=True):
        if choice is None:
            st.error("❌ Please select an answer before continuing.")
        else:
            score = q["opts"][opts.index(choice)][1]
            st.session_state.answers.append(score)
            st.session_state.current_q += 1
            if st.session_state.current_q >= total:
                st.session_state.page = "result"
            st.rerun()

    if c2.button("🏠 Home", use_container_width=True):
        st.session_state.page      = "home"
        st.session_state.current_q = 0
        st.session_state.answers   = []
        st.rerun()

# ======================================================
# PAGE: RESULT
# ======================================================
elif st.session_state.page == "result":

    answers    = st.session_state.answers
    total      = sum(answers)                                    # int
    percentage = round((total / (question_count * 4)) * 100, 1) # float
    label, advice = interpret_score(total)

    record = {
        "given_name":    st.session_state.p_given,
        "surname":       st.session_state.p_surname,
        "date_of_birth": st.session_state.p_dob,
        "student_id":    st.session_state.p_sid,
        "submitted":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_score":   total,
        "percentage":    percentage,
        "state":         label,
        "advice":        advice,
        "answers":       answers,
        "version":       version
    }
    results_store[st.session_state.p_sid] = record

    st.markdown("### 🏆 Your Results")
    c1, c2 = st.columns(2)
    c1.metric("Total Score", f"{total} / {question_count * 4}")
    c2.metric("Percentage",  f"{percentage}%")

    st.markdown(f"**State:** {label}")
    st.info(advice)

    st.caption(f"Name: {record['given_name']} {record['surname']}   |   "
               f"ID: {record['student_id']}   |   Submitted: {record['submitted']}")

    st.divider()
    st.markdown("#### 💾 Download Your Results")
    ca, cb, cc = st.columns(3)
    ca.download_button("⬇ JSON",
        json.dumps(record, indent=2),
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
    if c1.button("📝  New Survey", use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.answers   = []
        st.session_state.page      = "info"
        st.rerun()
    if c2.button("🏠  Back to Home", use_container_width=True):
        for k in ["p_given","p_surname","p_dob","p_sid","answers"]:
            st.session_state[k] = [] if k == "answers" else ""
        st.session_state.current_q = 0
        st.session_state.page      = "home"
        st.rerun()

# ======================================================
# PAGE: LOAD
# ======================================================
elif st.session_state.page == "load":

    st.markdown("### 📂 Load Existing Results")
    uploaded = st.file_uploader("Upload result file",
                                type=["json", "csv", "txt"])
    if uploaded:
        try:
            if uploaded.name.endswith(".json"):
                data  = json.load(uploaded)
                total = int(data.get("total_score", 0))
                lbl, adv = interpret_score(total)
                st.metric("Total Score",
                          f"{total} / {question_count * 4}")
                st.markdown(f"**State:** {data.get('state','')}")
                st.info(data.get("advice", ""))
                st.caption(f"Name: {data.get('given_name','')} "
                           f"{data.get('surname','')}   |   "
                           f"ID: {data.get('student_id','')}   |   "
                           f"Submitted: {data.get('submitted','')}")
            elif uploaded.name.endswith(".csv"):
                content = uploaded.read().decode("utf-8")
                data    = next(csv.DictReader(io.StringIO(content)))
                for k, v in data.items():
                    st.markdown(f"**{k}:** {v}")
            else:
                st.text(uploaded.read().decode("utf-8"))
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("🏠  Back to Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

# -------- FOOTER --------
st.divider()
st.caption(f"{survey_title}  |  4BUIS008C  |  "
           f"Muhammadsodik Akramov  |  00024431  |  v{version}")
