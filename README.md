# Advisor - AI-Powered Student Self-Growth Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-lightblue.svg)
![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)

**Advisor** is a comprehensive web application designed to help BCA students optimize their academic performance, build professional digital presence, and receive personalized AI-powered mentorship through habit tracking and intelligent guidance.

## 🎯 Overview

Advisor combines three core modules into an integrated platform:

- **📊 Habit Tracker**: Log daily mood, study hours, sleep, topics studied, and tasks completed
- **💼 Digital Presence Analyzer**: Score and improve GitHub and LinkedIn profiles with data-driven metrics
- **🤖 AI Student Advisor**: Conversational AI chatbot providing context-aware personalized guidance

## ✨ Key Features

### Authentication & User Management
- Secure user registration with email-style username
- Bcrypt password hashing for security
- Session-based authentication
- User profile management

### Habit Tracking & Analytics
- Daily habit logging (mood, study hours, sleep, topics, tasks)
- Bulk upload for historical data
- Pattern analysis engine:
  - Identify best/worst days of the week
  - Correlate study hours with mood
  - Weekly wellness insights with actionable flags
  - Average calculations for sleep and study hours

### GitHub Integration
- Fetch GitHub profile data (REST API)
- Track yearly contributions (GraphQL)
- Digital presence scoring (0-100):
  - Public repositories
  - Follower count
  - Bio presence
  - Account age
  - Average contributions/year
- Avatar retrieval and contribution breakdown

### LinkedIn Profile Management
- Submit LinkedIn profile metrics manually
- Digital presence scoring (0-100):
  - Profile photo & headline
  - Skills count
  - Connections & experiences
  - Endorsements
  - Profile completeness
- Score history tracking

### AI Chatbot (Groq-Powered)
- Context-aware responses using student's actual data
- Personalized advice based on:
  - Recent habit logs
  - GitHub/LinkedIn scores
  - Pattern analysis
  - Mood and wellness trends
- Supportive, encouraging tone
- Actionable improvement suggestions

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | Flask | 3.0.0 |
| **Database ORM** | Flask-SQLAlchemy | 3.1.1 |
| **Database** | SQLite | Built-in |
| **Authentication** | Flask-Bcrypt | 1.0.1 |
| **CORS Handling** | Flask-CORS | 4.0.0 |
| **HTTP Requests** | Requests | 2.31.0 |
| **Data Analysis** | Pandas | 2.1.4 |
| **AI/LLM** | Groq SDK | 0.4.2 |
| **Env Config** | python-dotenv | 1.0.0 |
| **Frontend** | HTML5, CSS3, Vanilla JS | - |
| **External APIs** | GitHub (REST + GraphQL) | Public |

## 📋 Requirements

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
Flask-Bcrypt==1.0.1
python-dotenv==1.0.0
groq==0.4.2
requests==2.31.0
pandas==2.1.4
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git (optional, for cloning)
- Groq API key (free tier available)
- GitHub personal access token (for API queries)

### Step-by-Step Installation

**1. Clone or Extract Project**
```bash
cd advisor
```

**2. Create Virtual Environment**
```bash
python3 -m venv venv
```

**3. Activate Virtual Environment**

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**5. Create .env File**

Create a file named `.env` in the project root with your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_personal_token_here
SECRET_KEY=your_secure_random_secret_key
FLASK_ENV=development
```

**Getting API Keys:**

- **Groq API Key**: Visit [console.groq.com](https://console.groq.com) and sign up for free
- **GitHub Token**: Go to GitHub Settings → Developer settings → Personal access tokens → Generate new token (Select `public_repo` and `user` scopes)
- **SECRET_KEY**: Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`

**6. Initialize Database**

The database will be created automatically on first run. To pre-initialize:

```bash
python3
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

**7. Run Application**
```bash
python app.py
```

Application will be available at **http://localhost:5000**

## 📖 Usage Guide

### User Registration
1. Open http://localhost:5000
2. Click "Sign Up"
3. Enter username, password, full name, and optional GitHub username
4. Click "Register"

### Login
1. On homepage, enter credentials
2. Click "Login"

### Daily Habit Logging
1. Navigate to "Dashboard" or "Habit Tracker"
2. Fill in today's information:
   - **Mood**: Select from dropdown (motivated, happy, slightly tired, tired, stressed)
   - **Study Hours**: Enter float (e.g., 5.5)
   - **Sleep Hours**: Enter hours slept
   - **Topics Studied**: List of subjects/topics
   - **Tasks Completed**: What you accomplished
3. Click "Log Habit"

### View Weekly Insights
1. Go to "Dashboard"
2. See weekly wellness analysis:
   - Average sleep and study hours
   - Mood breakdown by day
   - Wellness flags and recommendations
   - Topics covered this week

### GitHub Digital Presence
1. Go to "GitHub Digital Presence"
2. Enter your GitHub username
3. View:
   - Profile stats (repos, followers, bio)
   - Yearly contributions breakdown
   - Digital presence score (0-100)
   - Score calculation breakdown

### LinkedIn Profile Setup
1. Go to "LinkedIn Profile"
2. Enter your LinkedIn information:
   - Headline
   - Number of skills, connections, experiences, endorsements
   - Check if you have profile photo and summary
3. Click "Submit"
4. View your LinkedIn score and history

### Chat with AI Advisor
1. Open "Chat" or "Advisor" tab
2. Type your question (e.g., "How can I improve my GitHub score?" or "I'm feeling stressed, any advice?")
3. Receive personalized response based on your actual data
4. Continue conversation for follow-up questions

## 🔌 API Endpoints

### Authentication
```
POST   /signup                          Register new user
POST   /login                           Authenticate user
POST   /logout                          End session
GET    /me                              Get current user info
```

### Habit Logging
```
POST   /habits/<user_id>                Create habit log
GET    /habits/<user_id>                Get all logs for user
GET    /habits/<user_id>/<date>         Get specific day's log (YYYY-MM-DD)
GET    /habits/<user_id>/check-today    Check if today already logged
GET    /habits/<user_id>/weekly-insight Get weekly analysis & wellness flags
POST   /habits/bulk/<user_id>           Bulk upload multiple days
PUT    /habits/<log_id>                 Update specific log
DELETE /habits/<log_id>                 Delete specific log
```

### GitHub
```
GET    /github/<username>               Fetch GitHub profile data
GET    /digital-presence/<username>     Get GitHub score and breakdown
GET    /test-contributions/<username>   Get yearly contribution data
```

### LinkedIn
```
POST   /linkedin/<user_id>              Submit LinkedIn profile data
GET    /linkedin/<user_id>              Retrieve latest LinkedIn data
```

### Chat
```
POST   /chat/<user_id>                  Send message to AI advisor
```

### Utility
```
GET    /api/health                      API health check
```

## 📊 Database Schema

### User Table
```sql
- id (Integer, Primary Key)
- username (String, Unique)
- password_hash (String)
- name (String)
- github_username (String, Optional)
- linkedin_headline (String, Optional)
- created_at (DateTime)
```

### HabitLog Table
```sql
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key → User)
- date (Date)
- mood (String)
- study_hours (Float)
- sleep_hours (Float)
- topics_studied (String)
- tasks_completed (String)
```

### LinkedInProfile Table
```sql
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key → User)
- headline (String)
- has_profile_photo (Boolean)
- has_summary (Boolean)
- num_skills (Integer)
- num_connections (Integer)
- num_experiences (Integer)
- num_endorsements (Integer)
- linkedin_score (Float)
```

## 🧮 Scoring Algorithms

### GitHub Digital Presence Score (0-100)
- Public repos: min(count, 20) × 1.5
- Followers: min(count, 50) × 0.3
- Bio presence: +10 points
- Account age: min(years, 10) × 2
- Avg contributions/year: min(avg, 100) × 0.25

**Example**: 15 repos + 30 followers + bio + 5 years + 50 avg contributions = 15×1.5 + 30×0.3 + 10 + 5×2 + 50×0.25 = 22.5 + 9 + 10 + 10 + 12.5 = 64/100

### LinkedIn Digital Presence Score (0-100)
- Headline: +10 points
- Profile photo: +15 points
- Summary: +15 points
- Skills: min(count, 20) × 1
- Connections: min(count, 500) × 0.04
- Experiences: min(count, 5) × 3
- Endorsements: min(count, 25) × 0.2

**Example**: All features + 15 skills + 300 connections + 4 experiences + 20 endorsements = 10+15+15+15+12+12+4 = 83/100

## 🔍 Pattern Analysis Features

The app analyzes your 7+ days of habit logs to provide insights:

1. **Best/Worst Days**: Which days of the week you're most/least productive
2. **Study-Mood Correlation**: Does more study correlate with better mood? (-1 to +1 scale)
3. **Mood Breakdown by Day**: Histogram of mood distribution across weekdays
4. **Wellness Flags**: Automatic alerts for:
   - Low average sleep (< 6 hours)
   - Low study hours (< 2 hours)
   - High stress/tired days (≥ 4 days per week)

## 🛡️ Security Features

- **Password Security**: Bcrypt hashing (salted, strong)
- **Session Management**: Flask sessions with secure cookies
- **CORS Protection**: Configurable cross-origin requests
- **Environment Variables**: API keys never hardcoded
- **Database**: SQLite with SQLAlchemy ORM (prevents SQL injection)
- **Input Validation**: Type checking and parsing

## 🚧 Configuration

### Flask Configuration
```python
DEBUG=True                          # Set to False in production
SQLALCHEMY_DATABASE_URI            # Currently SQLite
SECRET_KEY                         # From .env
CORS_ORIGINS                       # Frontend domain
```

### Environment Variables (.env)
```
GROQ_API_KEY                       # Groq API key
GITHUB_TOKEN                       # GitHub personal token
SECRET_KEY                         # Flask session secret
FLASK_ENV                          # development or production
```

## 📝 Example Requests

### Create Habit Log
```bash
curl -X POST http://localhost:5000/habits/1 \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-09-24",
    "mood": "happy",
    "study_hours": 5,
    "sleep_hours": 7,
    "topics_studied": "Database Design, APIs",
    "tasks_completed": "Completed 2 assignments"
  }'
```

### Get Weekly Insights
```bash
curl http://localhost:5000/habits/1/weekly-insight
```

### Chat with AI
```bash
curl -X POST http://localhost:5000/chat/1 \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I improve my GitHub score?"}'
```

### Check GitHub Score
```bash
curl http://localhost:5000/digital-presence/torvalds
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
**Solution**: Activate virtual environment and run `pip install -r requirements.txt`

### "Cannot find working tool" (RAR extraction error)
**Solution**: Not related to Advisor. Occurs during unarchiving.

### GitHub API rate limit exceeded
**Solution**: GitHub has rate limits. Use a GitHub token to increase limit from 60 to 5000 requests/hour

### Groq API errors
**Solution**: 
- Verify API key is valid in console.groq.com
- Check .env file is in root directory
- Ensure GROQ_API_KEY variable is set

### Database locked error
**Solution**: SQLite doesn't handle concurrent writes. For production, migrate to PostgreSQL.

### Chatbot responses are generic
**Solution**: Ensure you have at least 3 days of habit logs for meaningful pattern analysis. Chat uses this context.

## 📈 Performance Tips

1. **Cache GitHub Data**: Don't query GitHub API on every request. Cache for 1 hour.
2. **Pagination**: For users with 100+ habit logs, implement pagination.
3. **Database Indexes**: Add indexes on `(user_id, date)` in HabitLog table.
4. **Static Files**: Serve frontend CSS/JS through CDN or caching headers.
5. **API Rate Limiting**: Implement rate limiting on /chat endpoint.

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (using Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t advisor .
docker run -p 8000:8000 -e GROQ_API_KEY=xxx -e GITHUB_TOKEN=xxx advisor
```

### Cloud Deployment Options
- **Heroku**: `git push heroku main`
- **AWS EC2**: Deploy with Gunicorn + Nginx
- **Google Cloud Run**: Containerized deployment
- **PythonAnywhere**: Simple Python hosting

## 🔮 Future Enhancements

- [ ] Email notifications for wellness reminders
- [ ] Leaderboards and peer comparison
- [ ] Data visualization dashboards (charts, graphs)
- [ ] Predictive analytics (forecast performance)
- [ ] Mobile app (React Native)
- [ ] Progressive Web App (PWA)
- [ ] Social features (friend connections, challenges)
- [ ] LinkedIn auto-sync via web scraping
- [ ] Spaced repetition recommendations
- [ ] Calendar integration
- [ ] Slack integration

## 📚 Learning Resources

### Built With This Project
- Flask Quickstart: https://flask.palletsprojects.com/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- Groq API Docs: https://console.groq.com/docs
- GitHub API: https://docs.github.com/en/rest
- Pandas User Guide: https://pandas.pydata.org/docs/

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

**Priyanshu** - BCA Student at IITM Janakpuri, GGSIPU
- GitHub: [@priyanshu02590](https://github.com/priyanshu02590)
- Email: priyanshu@example.com

## 🙏 Acknowledgments

- Groq team for fast, accessible LLM inference
- GitHub for comprehensive API documentation
- Flask and SQLAlchemy communities for excellent libraries
- IITM Janakpuri for academic guidance

## 📞 Support

For questions, issues, or feature requests:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Contact via email

---

**Happy Learning! 🚀 Let Advisor help you grow.**
