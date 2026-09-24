from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import datetime, date as date_type
from groq import Groq
import requests
import os
import pandas as pd

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-this")
CORS(app, supports_credentials=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///advisor.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ---- MODELS ----

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    github_username = db.Column(db.String(100))
    linkedin_headline = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.String(50))
    study_hours = db.Column(db.Float)
    sleep_hours = db.Column(db.Float)
    topics_studied = db.Column(db.String(300))
    tasks_completed = db.Column(db.String(500))

class LinkedInProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    headline = db.Column(db.String(200))
    has_profile_photo = db.Column(db.Boolean, default=False)
    has_summary = db.Column(db.Boolean, default=False)
    num_skills = db.Column(db.Integer, default=0)
    num_connections = db.Column(db.Integer, default=0)
    num_experiences = db.Column(db.Integer, default=0)
    num_endorsements = db.Column(db.Integer, default=0)
    linkedin_score = db.Column(db.Float, default=0)

# ---- HELPER FUNCTIONS ----

def calculate_github_score(profile_data, contribution_data):
    score = 0
    repos = profile_data.get("public_repos", 0)
    score += min(repos, 20) * 1.5
    followers = profile_data.get("followers", 0)
    score += min(followers, 50) * 0.3
    if profile_data.get("bio"):
        score += 10
    created_at = profile_data.get("created_at")
    if created_at:
        created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        years = (datetime.now() - created_date).days / 365
        score += min(years, 10) * 2
    if contribution_data:
        avg_contributions = contribution_data.get("average_contributions_per_year", 0)
        score += min(avg_contributions, 100) * 0.25
    return round(min(score, 100), 1)


def calculate_linkedin_score(data):
    score = 0
    if data.get("headline"):
        score += 10
    if data.get("has_profile_photo"):
        score += 15
    if data.get("has_summary"):
        score += 15
    skills = data.get("num_skills", 0)
    score += min(skills, 20) * 1
    connections = data.get("num_connections", 0)
    score += min(connections, 500) * 0.04
    experiences = data.get("num_experiences", 0)
    score += min(experiences, 5) * 3
    endorsements = data.get("num_endorsements", 0)
    score += min(endorsements, 25) * 0.2
    return round(min(score, 100), 1)


def get_contributions_for_year(username, year):
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    variables = {
        "login": username,
        "from": f"{year}-01-01T00:00:00Z",
        "to": f"{year}-12-31T23:59:59Z"
    }
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )
    if response.status_code != 200:
        return None
    data = response.json()
    user_data = data.get("data", {}).get("user")
    if not user_data:
        return None
    return user_data["contributionsCollection"]["contributionCalendar"]["totalContributions"]


def get_github_contributions(username):
    profile_url = f"https://api.github.com/users/{username}"
    profile_response = requests.get(profile_url)
    if profile_response.status_code != 200:
        return None
    profile_data = profile_response.json()
    created_at = profile_data.get("created_at")
    avatar_url = profile_data.get("avatar_url")
    joined_year = int(created_at[:4]) if created_at else datetime.now().year
    current_year = datetime.now().year
    yearly_data = {}
    for year in range(joined_year, current_year + 1):
        total = get_contributions_for_year(username, year)
        yearly_data[str(year)] = total if total is not None else 0
    total_all_years = sum(yearly_data.values())
    num_years = len(yearly_data)
    average_per_year = round(total_all_years / num_years, 1) if num_years else 0
    return {
        "avatar_url": avatar_url,
        "yearly_contributions": yearly_data,
        "total_contributions_all_time": total_all_years,
        "average_contributions_per_year": average_per_year
    }


def analyze_patterns(user_id):
    logs = HabitLog.query.filter_by(user_id=user_id).all()

    if len(logs) < 3:
        return None

    data = []
    for log in logs:
        data.append({
            "date": log.date,
            "day_of_week": log.date.strftime("%A"),
            "study_hours": log.study_hours or 0,
            "sleep_hours": log.sleep_hours or 0,
            "mood": log.mood
        })
    df = pd.DataFrame(data)

    mood_score_map = {
        "motivated": 5,
        "happy": 5,
        "slightly tired": 3,
        "tired": 2,
        "stressed": 1
    }
    df["mood_score"] = df["mood"].map(mood_score_map).fillna(3)

    weekday_avg = df.groupby("day_of_week")["mood_score"].mean().sort_values()
    worst_day = weekday_avg.index[0]
    best_day = weekday_avg.index[-1]

    correlation = df["study_hours"].corr(df["mood_score"])

    insights = {
        "worst_day": worst_day,
        "best_day": best_day,
        "study_mood_correlation": round(correlation, 2) if not pd.isna(correlation) else 0,
        "weekday_breakdown": weekday_avg.round(2).to_dict()
    }

    return insights


def build_user_context(user_id):
    user = User.query.get(user_id)
    if not user:
        return None

    logs = HabitLog.query.filter_by(user_id=user_id).order_by(HabitLog.date.desc()).limit(7).all()
    context_lines = [f"Student name: {user.name}"]

    if logs:
        context_lines.append("\nRecent daily activity (most recent first):")
        for log in logs:
            context_lines.append(
                f"- {log.date}: mood={log.mood}, study={log.study_hours}h, sleep={log.sleep_hours}h, "
                f"topics={log.topics_studied}, tasks={log.tasks_completed}"
            )
        total_sleep = sum(l.sleep_hours or 0 for l in logs)
        total_study = sum(l.study_hours or 0 for l in logs)
        avg_sleep = round(total_sleep / len(logs), 1)
        avg_study = round(total_study / len(logs), 1)
        context_lines.append(f"\nAverage sleep (last {len(logs)} days): {avg_sleep}h")
        context_lines.append(f"Average study hours: {avg_study}h")

    linkedin = LinkedInProfile.query.filter_by(user_id=user_id).order_by(LinkedInProfile.id.desc()).first()
    if linkedin:
        context_lines.append(f"\nLinkedIn digital presence score: {linkedin.linkedin_score}/100")
        context_lines.append(f"LinkedIn headline: {linkedin.headline}")
        context_lines.append(f"LinkedIn skills listed: {linkedin.num_skills}, connections: {linkedin.num_connections}, experience entries: {linkedin.num_experiences}")

    if user.github_username:
        github_data = get_github_contributions(user.github_username)
        profile_url = f"https://api.github.com/users/{user.github_username}"
        profile_response = requests.get(profile_url)
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            score = calculate_github_score(profile_data, github_data)
            context_lines.append(f"\nGitHub digital presence score: {score}/100")
            context_lines.append(f"GitHub public repos: {profile_data.get('public_repos')}, followers: {profile_data.get('followers')}")
            if github_data:
                context_lines.append(f"GitHub average contributions/year: {github_data.get('average_contributions_per_year')}")

    patterns = analyze_patterns(user_id)
    if patterns:
        context_lines.append(f"\nPattern analysis:")
        context_lines.append(f"Weakest day historically: {patterns['worst_day']}")
        context_lines.append(f"Strongest day historically: {patterns['best_day']}")
        context_lines.append(f"Correlation between study hours and mood/performance: {patterns['study_mood_correlation']} (closer to 1 = more study hours strongly linked to better mood)")

    return "\n".join(context_lines)

# ---- AUTH ROUTES ----

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    name = data.get("name")

    if not username or not password or not name:
        return jsonify({"error": "username, password, and name are required"}), 400

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({"error": "Username already taken"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
        username=username,
        password_hash=password_hash,
        name=name,
        github_username=data.get("github_username")
    )
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({"message": "Signup successful", "user_id": new_user.id, "name": new_user.name}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user.id

    return jsonify({"message": "Login successful", "user_id": user.id, "name": user.name})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"})


@app.route("/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "github_username": user.github_username
    })

# ---- CORE ROUTES ----

@app.route("/api/health")
def health():
    return {"message": "Student Advisor backend is running"}

@app.route("/github/<username>")
def github_stats(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "User not found"}), 404
    data = response.json()
    result = {
        "username": data.get("login"),
        "name": data.get("name"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "following": data.get("following"),
        "bio": data.get("bio"),
        "created_at": data.get("created_at")
    }
    return jsonify(result)

@app.route("/test-contributions/<username>")
def test_contributions(username):
    result = get_github_contributions(username)
    return jsonify(result)

@app.route("/digital-presence/<username>")
def digital_presence(username):
    profile_url = f"https://api.github.com/users/{username}"
    profile_response = requests.get(profile_url)
    if profile_response.status_code != 200:
        return jsonify({"error": "User not found"}), 404
    profile_data = profile_response.json()
    contribution_data = get_github_contributions(username)
    score = calculate_github_score(profile_data, contribution_data)
    result = {
        "username": profile_data.get("login"),
        "name": profile_data.get("name"),
        "bio": profile_data.get("bio"),
        "public_repos": profile_data.get("public_repos"),
        "followers": profile_data.get("followers"),
        "avatar_url": profile_data.get("avatar_url"),
        "yearly_contributions": contribution_data.get("yearly_contributions") if contribution_data else {},
        "average_contributions_per_year": contribution_data.get("average_contributions_per_year") if contribution_data else 0,
        "digital_presence_score": score
    }
    return jsonify(result)

@app.route("/linkedin/<int:user_id>", methods=["POST"])
def submit_linkedin(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    score = calculate_linkedin_score(data)
    profile = LinkedInProfile(
        user_id=user_id,
        headline=data.get("headline"),
        has_profile_photo=data.get("has_profile_photo", False),
        has_summary=data.get("has_summary", False),
        num_skills=data.get("num_skills", 0),
        num_connections=data.get("num_connections", 0),
        num_experiences=data.get("num_experiences", 0),
        num_endorsements=data.get("num_endorsements", 0),
        linkedin_score=score
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({"message": "LinkedIn profile saved", "linkedin_score": score}), 201

@app.route("/linkedin/<int:user_id>", methods=["GET"])
def get_linkedin(user_id):
    profile = LinkedInProfile.query.filter_by(user_id=user_id).order_by(LinkedInProfile.id.desc()).first()
    if not profile:
        return jsonify({"error": "No LinkedIn data found for this user"}), 404
    return jsonify({
        "headline": profile.headline,
        "has_profile_photo": profile.has_profile_photo,
        "has_summary": profile.has_summary,
        "num_skills": profile.num_skills,
        "num_connections": profile.num_connections,
        "num_experiences": profile.num_experiences,
        "num_endorsements": profile.num_endorsements,
        "linkedin_score": profile.linkedin_score
    })

@app.route("/habits/<int:user_id>", methods=["POST"])
def create_habit_log(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    log_date_str = data.get("date")
    if log_date_str:
        log_date = datetime.strptime(log_date_str, "%Y-%m-%d").date()
    else:
        log_date = date_type.today()
    new_log = HabitLog(
        user_id=user_id,
        date=log_date,
        mood=data.get("mood"),
        study_hours=data.get("study_hours"),
        sleep_hours=data.get("sleep_hours"),
        topics_studied=data.get("topics_studied"),
        tasks_completed=data.get("tasks_completed")
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({"message": "Habit log created", "id": new_log.id, "date": str(new_log.date)}), 201

@app.route("/habits/bulk/<int:user_id>", methods=["POST"])
def create_habit_logs_bulk(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    entries = request.get_json()
    if not isinstance(entries, list):
        return jsonify({"error": "Expected a list of daily entries"}), 400
    created_ids = []
    for entry in entries:
        log_date_str = entry.get("date")
        if not log_date_str:
            continue
        log_date = datetime.strptime(log_date_str, "%Y-%m-%d").date()
        new_log = HabitLog(
            user_id=user_id,
            date=log_date,
            mood=entry.get("mood"),
            study_hours=entry.get("study_hours"),
            sleep_hours=entry.get("sleep_hours"),
            topics_studied=entry.get("topics_studied"),
            tasks_completed=entry.get("tasks_completed")
        )
        db.session.add(new_log)
        db.session.flush()
        created_ids.append(new_log.id)
    db.session.commit()
    return jsonify({"message": f"{len(created_ids)} habit logs created", "ids": created_ids}), 201

@app.route("/habits/<int:user_id>", methods=["GET"])
def get_habit_logs(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    logs = HabitLog.query.filter_by(user_id=user_id).order_by(HabitLog.date.desc()).all()
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "date": str(log.date),
            "mood": log.mood,
            "study_hours": log.study_hours,
            "sleep_hours": log.sleep_hours,
            "topics_studied": log.topics_studied,
            "tasks_completed": log.tasks_completed
        })
    return jsonify(result)

@app.route("/habits/<int:user_id>/<string:log_date>", methods=["GET"])
def get_habit_log_by_date(user_id, log_date):
    try:
        parsed_date = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    log = HabitLog.query.filter_by(user_id=user_id, date=parsed_date).first()
    if not log:
        return jsonify({"error": "No entry found for this date"}), 404
    return jsonify({
        "id": log.id,
        "date": str(log.date),
        "mood": log.mood,
        "study_hours": log.study_hours,
        "sleep_hours": log.sleep_hours,
        "topics_studied": log.topics_studied,
        "tasks_completed": log.tasks_completed
    })

@app.route("/habits/<int:user_id>/check-today", methods=["GET"])
def check_today_log(user_id):
    today = date_type.today()
    log = HabitLog.query.filter_by(user_id=user_id, date=today).first()
    return jsonify({"already_logged": log is not None})

@app.route("/habits/<int:user_id>/weekly-insight", methods=["GET"])
def weekly_insight(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    logs = HabitLog.query.filter_by(user_id=user_id).order_by(HabitLog.date.desc()).limit(7).all()
    if not logs:
        return jsonify({"error": "No habit logs found"}), 404
    total_sleep = sum(log.sleep_hours or 0 for log in logs)
    total_study = sum(log.study_hours or 0 for log in logs)
    count = len(logs)
    avg_sleep = round(total_sleep / count, 1)
    avg_study = round(total_study / count, 1)
    mood_counts = {}
    for log in logs:
        m = log.mood or "unknown"
        mood_counts[m] = mood_counts.get(m, 0) + 1
    topics = [log.topics_studied for log in logs if log.topics_studied]
    flags = []
    if avg_sleep < 6:
        flags.append("Low average sleep this week — consider prioritizing rest.")
    if avg_study < 2:
        flags.append("Study hours have been low this week.")
    stressed_or_tired_days = mood_counts.get("stressed", 0) + mood_counts.get("tired", 0) + mood_counts.get("slightly tired", 0)
    if stressed_or_tired_days >= 4:
        flags.append("Mood has leaned stressed/tired for several days — a break might help.")
    return jsonify({
        "days_analyzed": count,
        "average_sleep_hours": avg_sleep,
        "average_study_hours": avg_study,
        "mood_breakdown": mood_counts,
        "topics_this_week": topics,
        "wellness_flags": flags if flags else ["No major concerns this week — looking balanced."]
    })

@app.route("/habits/<int:log_id>", methods=["PUT"])
def update_habit_log(log_id):
    log = HabitLog.query.get(log_id)
    if not log:
        return jsonify({"error": "Habit log not found"}), 404
    data = request.get_json()
    if "mood" in data:
        log.mood = data["mood"]
    if "study_hours" in data:
        log.study_hours = data["study_hours"]
    if "sleep_hours" in data:
        log.sleep_hours = data["sleep_hours"]
    if "topics_studied" in data:
        log.topics_studied = data["topics_studied"]
    if "tasks_completed" in data:
        log.tasks_completed = data["tasks_completed"]
    db.session.commit()
    return jsonify({
        "message": "Habit log updated",
        "id": log.id,
        "mood": log.mood,
        "study_hours": log.study_hours,
        "sleep_hours": log.sleep_hours,
        "topics_studied": log.topics_studied,
        "tasks_completed": log.tasks_completed
    })

@app.route("/habits/<int:log_id>", methods=["DELETE"])
def delete_habit_log(log_id):
    log = HabitLog.query.get(log_id)
    if not log:
        return jsonify({"error": "Habit log not found"}), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": "Habit log deleted", "id": log_id})

@app.route("/chat/<int:user_id>", methods=["POST"])
def chat(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    context = build_user_context(user_id)

    system_prompt = f"""You are a supportive, encouraging student advisor chatbot. Your job is to help this specific student with confidence-building, study habits, GitHub/LinkedIn profile improvement, and general guidance.

Here is what you know about this student:
{context}

Be warm, personal, and reference their actual recent activity, GitHub score, LinkedIn score, and pattern analysis naturally when relevant. If asked how to improve their GitHub or LinkedIn presence, give specific, actionable suggestions based on their actual current numbers. Keep responses concise and conversational, not preachy."""

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)