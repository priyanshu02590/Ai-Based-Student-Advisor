from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import requests
import os

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///advisor.db"
db = SQLAlchemy(app)

# ---- MODELS ----

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

# ---- HELPER FUNCTIONS ----

def calculate_github_score(data):
    score = 0

    # Repos: up to 40 points, capped at 20 repos
    repos = data.get("public_repos", 0)
    score += min(repos, 20) * 2

    # Followers: up to 20 points, capped at 50 followers
    followers = data.get("followers", 0)
    score += min(followers, 50) * 0.4

    # Bio filled: 10 points
    if data.get("bio"):
        score += 10

    # Account age: up to 30 points, 3 points per year, capped at 10 years
    created_at = data.get("created_at")
    if created_at:
        created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        years = (datetime.now() - created_date).days / 365
        score += min(years, 10) * 3

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

# ---- ROUTES ----

@app.route("/")
def home():
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
        "created_at": data.get("created_at"),
        "digital_presence_score": calculate_github_score(data)
    }

    return jsonify(result)

@app.route("/test-contributions/<username>")
def test_contributions(username):
    result = get_github_contributions(username)
    return jsonify(result)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    new_user = User(
        name=data.get("name"),
        github_username=data.get("github_username"),
        linkedin_headline=data.get("linkedin_headline")
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created", "id": new_user.id}), 201

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "github_username": user.github_username,
            "linkedin_headline": user.linkedin_headline
        })

    return jsonify(result)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
