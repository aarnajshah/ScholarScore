"""Reusable ML + College Scorecard functions for ScholarScore.

This is adapted from the separate classroom demo. It classifies broad
COLLEGE selectivity; it does not predict whether a student will be admitted.
"""
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

API_URL = "https://api.data.gov/ed/collegescorecard/v1/schools.json"

def create_selectivity_group(rate):
    if rate < 10: return "Highly Selective"
    if rate < 30: return "Selective"
    if rate < 70: return "Moderately Selective"
    return "Broad Access"

def fetch_training_data(api_key, per_page=100):
    if not api_key:
        return None
    params = {
        "api_key": api_key,
        "per_page": per_page,
        "fields": "school.name,latest.admissions.admission_rate.overall,latest.admissions.sat_scores.average.overall,latest.student.size",
    }
    r = requests.get(API_URL, params=params, timeout=20)
    r.raise_for_status()
    df = pd.DataFrame(r.json().get("results", []))
    if df.empty: return None
    df = df.rename(columns={
        "school.name":"college_name",
        "latest.admissions.admission_rate.overall":"acceptance_rate",
        "latest.admissions.sat_scores.average.overall":"sat_average",
        "latest.student.size":"student_size",
    })
    df = df.dropna(subset=["acceptance_rate","sat_average","student_size"]).copy()
    if len(df) < 10: return None
    df["acceptance_rate"] = df["acceptance_rate"].astype(float) * 100
    return df

def train_college_model(api_key):
    df = fetch_training_data(api_key)
    if df is None:
        return None
    df["selectivity_group"] = df["acceptance_rate"].apply(create_selectivity_group)
    # Acceptance rate created the label, so it is intentionally excluded from X.
    X = df[["sat_average", "student_size"]]
    y = df["selectivity_group"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=42)
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    return {"model": model, "accuracy": round(accuracy*100,1), "rows": len(df)}

def search_scorecard(api_key, name):
    if not api_key:
        return {"error":"College Scorecard API key is missing. Add it to .env."}
    params = {
        "api_key": api_key, "school.name": name, "per_page": 10,
        "fields": "school.name,school.city,school.state,latest.admissions.admission_rate.overall,latest.admissions.sat_scores.average.overall,latest.student.size",
    }
    try:
        r = requests.get(API_URL, params=params, timeout=15)
        r.raise_for_status()
        results = r.json().get("results", [])
    except requests.RequestException as exc:
        return {"error": f"College Scorecard request failed: {exc}"}
    if not results: return {"error":"No matching college found."}
    c = results[0]
    rate = c.get("latest.admissions.admission_rate.overall")
    return {
        "name": c.get("school.name"), "city": c.get("school.city"), "state": c.get("school.state"),
        "acceptance_rate": round(rate*100,1) if rate is not None else None,
        "sat_average": c.get("latest.admissions.sat_scores.average.overall"),
        "student_size": c.get("latest.student.size"),
    }

def classify(model_info, sat_average, student_size):
    if not model_info or sat_average is None or student_size is None:
        return "Not enough data"
    row = pd.DataFrame([{"sat_average": float(sat_average), "student_size": float(student_size)}])
    return model_info["model"].predict(row)[0]
