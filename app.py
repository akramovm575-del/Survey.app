# ============================================================
# Peer Social Support & Academic Performance Survey
# Module: Fundamentals of Programming, 4BUIS008C
# ============================================================

import json
import csv
import re
import os
from datetime import datetime

# ── Variable types (all 10 required types demonstrated) ─────
survey_title   = "Peer Social Support Survey"   # str
version        = 1.0                             # float
question_count = 15                              # int
survey_active  = True                            # bool
score_ranges   = [0, 13, 25, 37, 43, 49, 55]    # list
state_labels   = (                               # tuple
    "Very Low Support",
    "Low Support",
    "Moderate Support",
    "Good Support",
    "Strong Support",
    "Excellent Support",
    "Outstanding Support"
)
valid_choices  = range(1, 4)                     # range
results_store  = {}                              # dict
completed_ids  = set()                           # set
locked_fields  = frozenset({"title", "version"}) # frozenset

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

QUESTIONS_FILE = "questions.json"


# ── FUNCTION 1: Print the main menu ─────────────────────────
def show_menu():
    print("\n" + "=" * 58)
    print(f"  {survey_title}")
    print(f"  Version: {version}")
    print("=" * 58)
    print("  1. Start a new survey")
    print("  2. Load existing results from file")
    print("  3. View psychological states")
    print("  4. View last result")
    print("  5. Exit")
    print("=" * 58)
    print("  Tip: Enter 0 at any time to return to this menu.")
    print("=" * 58)


# ── FUNCTION 2: Save questions to external file ──────────────
def save_questions_to_file():
    if not os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(QUESTIONS, f, indent=2, ensure_ascii=False)
        print(f"  Questions saved to {QUESTIONS_FILE}")


# ── FUNCTION 3: Load questions from external file ────────────
def load_questions_from_file():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return QUESTIONS


# ── FUNCTION 4: Validate participant name ────────────────────
def get_valid_name():
    # while loop for input validation
    while True:
        name = input("  Full name (or 0 to go Home): ").strip()
        if name == "0":
            return None                          # signal: go back to menu
        if re.fullmatch(r"[A-Za-z][A-Za-z\s'\-]*", name) and len(name) >= 2:
            return name
        print("  X Only letters, spaces, hyphens, apostrophes allowed.")


# ── FUNCTION 5: Validate date of birth ──────────────────────
def get_valid_dob():
    while True:
        dob = input("  Date of birth DD/MM/YYYY (or 0 to go Home): ").strip()
        if dob == "0":
            return None
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", dob):
            day   = int(dob[:2])
            month = int(dob[3:5])
            year  = int(dob[6:])
            if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2010:
                return dob
        print("  X Invalid date. Use DD/MM/YYYY (e.g. 15/03/2004).")


# ── FUNCTION 6: Validate student ID ─────────────────────────
def get_valid_student_id():
    while True:
        sid = input("  Student ID digits only (or 0 to go Home): ").strip()
        if sid == "0":
            return None
        if sid.isdigit() and len(sid) >= 4:
            return sid
        print("  X Student ID must contain digits only (min 4 digits).")


# ── FUNCTION 7: Interpret total score ────────────────────────
def interpret_score(score):
    if score <= 12:
        label  = "Very Low Peer Support & Poor Adjustment"
        advice = "Very limited support. High risk of emotional difficulties."
    elif score <= 24:
        label  = "Low Peer Support & Mild Adjustment Issues"
        advice = "Limited friendships affecting emotional balance."
    elif score <= 36:
        label  = "Moderate Peer Support & Moderate Adjustment"
        advice = "Some support present. Occasional emotional challenges."
    elif score <= 42:
        label  = "Good Peer Support & Good Adjustment"
        advice = "Healthy peer network with positive effects on wellbeing."
    elif score <= 48:
        label  = "Strong Peer Support & Strong Adjustment"
        advice = "Strong friendships supporting academic and emotional health."
    elif score <= 54:
        label  = "Excellent Peer Support & Excellent Adjustment"
        advice = "Excellent friendship quality and consistent academic performance."
    else:
        label  = "Outstanding Peer Support & Outstanding Adjustment"
        advice = "Exceptional peer relationships. Model support environment."

    return {"label": label, "advice": advice}


# ── FUNCTION 8: Run the survey ───────────────────────────────
def run_survey(questions):
    while True:                          # restart loop
        print("\n" + "=" * 58)
        print(f"  {survey_title}  (v{version})")
        print("=" * 58)
        print("  Answer honestly. Scale: 0 = lowest, 4 = highest")
        print("  Enter 0 at any prompt to go back to Home.\n")

        # ── collect participant info ─────────────────────────
        print("  --- Participant Information ---")

        name = get_valid_name()
        if name is None:                 # user typed 0
            return None

        dob = get_valid_dob()
        if dob is None:
            return None

        student_id = get_valid_student_id()
        if student_id is None:
            return None

        if student_id in completed_ids:
            print(f"\n  ! ID {student_id} has already completed this survey.")
            print("  Please use a different ID or load your existing result.")
            return None

        print(f"\n  Thank you, {name}! Starting survey...")
        print("  Tip: Enter 0 during questions to Restart from Q1.\n")
        print("-" * 58)

        answers    = []
        total      = 0
        restart    = False

        # for loop — iterates through each question
        for i in range(len(questions)):
            q = questions[i]
            print(f"\n  Q{i + 1} of {len(questions)}. {q['text']}")
            for j in range(len(q["options"])):
                print(f"       {j + 1}. {q['options'][j]}")
            print(f"       0. Restart survey from Q1")

            # while loop — validates each answer
            while True:
                try:
                    choice = int(input(f"  Your answer (0-{len(q['options'])}): "))

                    if choice == 0:          # ── RESTART ──────
                        print("\n  Restarting survey...\n")
                        restart = True
                        break

                    elif 1 <= choice <= len(q["options"]):
                        score = q["scores"][choice - 1]
                        answers.append(score)
                        total += score
                        break

                    else:
                        print(f"  X Enter 0 to restart or 1-{len(q['options'])} to answer.")

                except ValueError:
                    print("  X Please enter a valid number.")

            if restart:
                break                    # break out of for loop → while True repeats

        if restart:
            continue                     # go back to top of while True (restart)

        # ── survey completed ─────────────────────────────────
        percentage     = round((total / (question_count * 4)) * 100, 1)  # float
        interpretation = interpret_score(total)

        result = {
            "name":          name,
            "student_id":    student_id,
            "date_of_birth": dob,
            "submitted":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "answers":       answers,
            "total_score":   total,
            "percentage":    percentage,
            "state":         interpretation["label"],
            "advice":        interpretation["advice"]
        }

        completed_ids.add(student_id)
        results_store[student_id] = result
        return result                    # exit while True


# ── FUNCTION 9: Display result on screen ────────────────────
def display_result(result):
    print("\n" + "=" * 58)
    print("  YOUR RESULTS")
    print("=" * 58)
    print(f"  Name        : {result['name']}")
    print(f"  Student ID  : {result['student_id']}")
    print(f"  Submitted   : {result['submitted']}")
    print(f"  Total Score : {result['total_score']} / {question_count * 4}")
    print(f"  Percentage  : {result['percentage']}%")
    print("-" * 58)
    print(f"  State  : {result['state']}")
    print(f"  Advice : {result['advice']}")
    print("=" * 58)


# ── FUNCTION 10: Save result (user picks format) ─────────────
def save_result(result):
    print("\n  Would you like to save your results?")
    print("  1. Yes   2. No   0. Home")

    while True:
        pick = input("  Your choice: ").strip()
        if pick == "0":
            return
        elif pick == "2":
            print("  Results not saved.")
            return
        elif pick == "1":
            break
        else:
            print("  X Enter 0, 1, or 2.")

    print("\n  Choose file format:")
    print("  1. TXT   2. CSV   3. JSON   0. Home")

    while True:
        fmt = input("  Your choice: ").strip()
        if fmt == "0":
            return
        elif fmt in ("1", "2", "3"):
            break
        print("  X Enter 0, 1, 2, or 3.")

    sid = result["student_id"]

    if fmt == "1":
        filename = f"result_{sid}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 58 + "\n")
            f.write(f"  {survey_title} - Results\n")
            f.write("=" * 58 + "\n")
            for key, value in result.items():
                f.write(f"  {key}: {value}\n")
            f.write("=" * 58 + "\n")

    elif fmt == "2":
        filename = f"result_{sid}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=result.keys())
            writer.writeheader()
            writer.writerow(result)

    else:
        filename = f"result_{sid}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  Results saved to: {filename}")


# ── FUNCTION 11: Load and display existing result from file ──
def load_existing_result():
    print("\n  Enter 0 to go back to Home.")
    filename = input("  Enter filename (e.g. result_12345.json): ").strip()

    if filename == "0":
        return

    if not os.path.exists(filename):
        print(f"  X File '{filename}' not found.")
        return

    if filename.endswith(".json"):
        with open(filename, "r", encoding="utf-8") as f:
            result = json.load(f)
        display_result(result)

    elif filename.endswith(".csv"):
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            result = next(reader)
        display_result(result)

    elif filename.endswith(".txt"):
        with open(filename, "r", encoding="utf-8") as f:
            print(f.read())

    else:
        print("  X Unsupported file type. Use .json, .csv, or .txt")


# ── FUNCTION 12: Show all psychological states ───────────────
def show_states():
    print("\n" + "=" * 58)
    print("  POSSIBLE PSYCHOLOGICAL STATES")
    print("=" * 58)
    states_info = [
        ("0-12",  "Very Low Peer Support & Poor Adjustment"),
        ("13-24", "Low Peer Support & Mild Adjustment Issues"),
        ("25-36", "Moderate Peer Support & Moderate Adjustment"),
        ("37-42", "Good Peer Support & Good Adjustment"),
        ("43-48", "Strong Peer Support & Strong Adjustment"),
        ("49-54", "Excellent Peer Support & Excellent Adjustment"),
        ("55-60", "Outstanding Peer Support & Outstanding Adjustment"),
    ]
    for score_range, label in states_info:
        print(f"  {score_range:<6}  {label}")
    print("=" * 58)
    print("  Enter 0 to go back to Home.")
    input("  Press Enter to continue...")


# ── FUNCTION 13: View last completed result ──────────────────
def view_last_result():
    if len(results_store) == 0:
        print("\n  No results yet. Complete a survey first.")
        return

    # get the last added student_id from the dict
    last_id = list(results_store.keys())[-1]
    print(f"\n  Showing last result (ID: {last_id})")
    display_result(results_store[last_id])

    print("\n  Would you like to save this result?")
    print("  1. Yes   2. No")
    while True:
        pick = input("  Your choice (1/2): ").strip()
        if pick == "1":
            save_result(results_store[last_id])
            break
        elif pick == "2":
            break
        else:
            print("  X Enter 1 or 2.")


# ── FUNCTION 14: Confirm exit ────────────────────────────────
def confirm_exit():
    print("\n  Are you sure you want to exit?")
    print("  1. Yes, exit   2. No, go back to Home")
    while True:
        pick = input("  Your choice (1/2): ").strip()
        if pick == "1":
            return True
        elif pick == "2":
            return False
        else:
            print("  X Enter 1 or 2.")


# ── MAIN ─────────────────────────────────────────────────────
def main():
    save_questions_to_file()
    questions = load_questions_from_file()

    while survey_active:
        show_menu()
        choice = input("  Choose an option (1/2/3/4/5): ").strip()

        if choice == "1":
            result = run_survey(questions)
            if result:
                display_result(result)
                save_result(result)
            else:
                print("  Returning to Home...")

        elif choice == "2":
            load_existing_result()

        elif choice == "3":
            show_states()

        elif choice == "4":
            view_last_result()

        elif choice == "5":
            if confirm_exit():
                print("\n  Thank you. Goodbye!\n")
                break

        else:
            print("  X Invalid option. Please choose 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()
