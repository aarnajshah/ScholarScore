from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import os
from dotenv import load_dotenv
from model_service import train_college_model, search_scorecard, classify

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
COLLEGE_DATA_PATH = BASE_DIR / "data" / "colleges.json"
load_dotenv(BASE_DIR / ".env")
API_KEY = os.getenv("COLLEGE_SCORECARD_API_KEY")
try:
    ML_MODEL = train_college_model(API_KEY)
except Exception as exc:
    print(f"ML model unavailable: {exc}")
    ML_MODEL = None


def load_colleges():
    """Load the local demonstration college dataset."""
    with open(COLLEGE_DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def _text_quality(text):
    text = (text or "").strip().lower()
    words = text.split()
    action_words = ["built", "created", "led", "organized", "improved", "designed", "helped", "researched", "developed", "taught", "started", "solved", "mentored", "raised", "increased", "founded"]
    hits = sum(1 for word in action_words if word in text)
    return clamp((len(words) / 45) * 65 + hits * 7)


def calculate_student_score(profile):
    """Transparent educational 0-100 profile score using the detailed form."""
    gpa = float(profile.get("gpa", 0) or 0)
    test_score = float(profile.get("test_score", 0) or 0)
    rigor = float(profile.get("course_rigor", 0) or 0)
    courses = profile.get("courses", []) or []
    ap_exams = profile.get("ap_exams", []) or []
    activities = profile.get("activities", []) or []
    service = profile.get("service", []) or []
    leadership = profile.get("leadership", []) or []
    awards = profile.get("awards", []) or []
    essay = (profile.get("essay", "") or "").strip()

    # Academics: GPA + testing + rigor + evidence of advanced coursework.
    gpa_score = clamp((gpa / 4.0) * 100)
    test_component = clamp((test_score / 1600) * 100) if test_score else 70
    advanced_courses = sum(1 for c in courses if c.get("level") in {"Honors", "AP", "IB", "Dual Enrollment"})
    ap_good = sum(1 for x in ap_exams if float(x.get("score", 0) or 0) >= 4)
    coursework_score = clamp(advanced_courses * 12 + ap_good * 8)
    academic_score = gpa_score * .52 + test_component * .23 + clamp(rigor * 20) * .15 + coursework_score * .10

    # Involvement rewards sustained commitment, responsibility and described impact—not just item count.
    activity_points = 0
    for x in activities[:15]:
        hrs=float(x.get("hours_week",0) or 0); weeks=float(x.get("weeks_year",0) or 0); years=float(x.get("years",0) or 0); lead=float(x.get("leadership",0) or 0)
        commitment=clamp((hrs*weeks*max(years,1))/18)
        activity_points += commitment*.45 + clamp(years*25)*.20 + clamp(lead*33.3)*.15 + _text_quality(x.get("description"))*.20
    activity_score = clamp(activity_points / max(1, min(len(activities), 5))) if activities else 0

    service_hours=sum(float(x.get("hours",0) or 0) for x in service[:15])
    service_text=" ".join(x.get("description","") for x in service[:15])
    service_score=clamp(service_hours/1.5)*.65 + _text_quality(service_text)*.35 if service else 0

    leadership_points=[]
    for x in leadership[:15]:
        years=float(x.get("years",0) or 0); people=float(x.get("people_led",0) or 0)
        leadership_points.append(clamp(years*25)*.35 + clamp(people*5)*.20 + _text_quality(x.get("description"))*.45)
    leadership_score=sum(leadership_points)/len(leadership_points) if leadership_points else 0
    involvement_score = activity_score*.55 + leadership_score*.30 + service_score*.15

    # Awards use recognition level plus explanation, capped at 15 entries.
    award_points=[]
    for x in awards[:15]:
        level=float(x.get("level",1) or 1)
        award_points.append(clamp(level/6*100)*.75 + _text_quality(x.get("description"))*.25)
    achievement_score = clamp((sum(sorted(award_points, reverse=True)[:6]) / max(1, min(len(award_points),6))) if award_points else 0)

    word_count=len(essay.split())
    essay_score=clamp((word_count/300)*65 + _text_quality(essay)*.35)

    total = academic_score*.45 + involvement_score*.30 + achievement_score*.10 + essay_score*.15
    breakdown={"academic":round(academic_score),"involvement":round(involvement_score),"achievements":round(achievement_score),"essay":round(essay_score)}
    return round(clamp(total)), breakdown

def compare_to_college(student_score, profile, college):
    """
    Compare the student's score to a college benchmark.

    The output is a planning estimate, not an acceptance probability.
    """
    benchmark = college["benchmark_score"]
    score_gap = student_score - benchmark

    student_gpa = float(profile.get("gpa", 0) or 0)
    student_test = float(profile.get("test_score", 0) or 0)

    gpa_alignment = clamp(100 - abs(student_gpa - college["avg_gpa"]) * 35)
    test_alignment = clamp(100 - abs(student_test - college["avg_test_score"]) / 4)
    profile_alignment = clamp(50 + score_gap * 3)

    fit_score = round(
        profile_alignment * 0.50
        + gpa_alignment * 0.30
        + test_alignment * 0.20
    )

    if score_gap >= 8:
        category = "Above sample benchmark"
        message = "Your current profile score is above this app's sample benchmark."
    elif score_gap >= -5:
        category = "Near sample benchmark"
        message = "Your current profile score is close to this app's sample benchmark."
    else:
        category = "Below sample benchmark"
        message = "Your current profile score is below this app's sample benchmark."

    return {
        "college": college["name"],
        "college_score": benchmark,
        "student_score": student_score,
        "fit_score": fit_score,
        "category": category,
        "message": message,
        "acceptance_rate": college["acceptance_rate"],
        "avg_gpa": college["avg_gpa"],
        "avg_test_score": college["avg_test_score"],
        "disclaimer": (
            "This is an educational estimate based on sample historical data. "
            "It is not an official admission probability."
        )
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/colleges")
def colleges():
    query = request.args.get("q", "").lower().strip()
    college_list = load_colleges()

    if query:
        college_list = [
            college for college in college_list
            if query in college["name"].lower()
        ]

    return jsonify(college_list)


@app.route("/api/score", methods=["POST"])
def score():
    payload = request.get_json() or {}
    profile = payload.get("profile", {})
    selected_colleges = payload.get("colleges", [])

    student_score, breakdown = calculate_student_score(profile)
    all_colleges = load_colleges()
    college_lookup = {college["name"]: college for college in all_colleges}

    comparisons = []
    for college_name in selected_colleges:
        college = college_lookup.get(college_name)
        if college:
            comparisons.append(compare_to_college(student_score, profile, college))

    return jsonify({
        "student_score": student_score,
        "breakdown": breakdown,
        "comparisons": comparisons,
        "model_note": (
            "ScholarScore uses a transparent weighted scoring model and basic "
            "NLP-style essay analysis. It does not replace an admissions counselor."
        )
    })


@app.route("/api/scorecard")
def scorecard_lookup():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "Enter a college name."}), 400
    result = search_scorecard(API_KEY, name)
    if "error" in result:
        return jsonify(result), 400
    result["ml_classification"] = classify(ML_MODEL, result.get("sat_average"), result.get("student_size"))
    result["model_accuracy"] = ML_MODEL["accuracy"] if ML_MODEL else None
    result["model_rows"] = ML_MODEL["rows"] if ML_MODEL else None
    result["note"] = "The ML result is a broad college selectivity classification, not an individual admission prediction."
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
