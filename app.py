"""Personal portfolio backend (Flask + SQLite).

Routes
  GET  /                 Portfolio page, projects rendered from the database
  GET  /api/projects     All projects as JSON
  POST /api/projects     Add a project (requires X-Admin-Token header)
  POST /api/contact      Store a message from the contact form
  GET  /health           Simple health check
"""
import os
import re
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "portfolio.db"))
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")  # empty = adding projects via API disabled

app = Flask(__name__)

PROFILE = {
    "name": "Maheshwaran S",
    "role": "Full Stack Developer",
    "tagline": "AI & Data Science undergraduate building responsive, database-driven web apps.",
    "summary": (
        "Driven AI & Data Science undergraduate seeking a Full Stack Developer internship. "
        "I build responsive web applications, RESTful APIs and database-driven solutions with "
        "Django and SQL/NoSQL databases, and I care about software architecture, problem-solving "
        "and scalable, AI-integrated user experiences."
    ),
    "email": "sivamaheshwaran@gmail.com",
    "github": "https://github.com/",      # TODO: replace with your GitHub profile URL
    "linkedin": "https://www.linkedin.com/",  # TODO: replace with your LinkedIn profile URL
    "education": {
        "degree": "B.Tech in Artificial Intelligence & Data Science",
        "school": "Rajalakshmi Institute of Technology, Chennai",
        "years": "2024 – 2028",
        "score": "CGPA 7.7 / 10",
    },
    "skills": {
        "Languages": ["Python", "JavaScript", "SQL"],
        "Frontend": ["HTML", "CSS", "JavaScript", "Tailwind CSS", "Bootstrap"],
        "Backend": ["Django"],
        "Databases": ["MySQL", "MongoDB", "Firebase Firestore"],
        "Tools": ["Git", "GitHub", "VS Code"],
        "Core concepts": ["DSA", "OOPs", "DBMS"],
    },
    "achievements": [
        ("250+", "coding problems solved across competitive programming platforms"),
        ("3+", "end-to-end full-stack applications built and deployed"),
        ("Active", "participant in college-level hackathons and coding events"),
    ],
}

SEED_PROJECTS = [
    {
        "title": "ShopWise – Smart E-Commerce Platform",
        "description": (
            "Responsive e-commerce web app with user authentication, product search and "
            "filtering, a shopping cart and order management. Django backend with MySQL "
            "storing products, users and orders."
        ),
        "tech": "HTML, CSS, Tailwind CSS, Django, MySQL",
        "github_url": "",
        "live_url": "",
    },
    {
        "title": "Student Management System",
        "description": (
            "Responsive web app for managing student details, academic records and attendance, "
            "with full add / update / delete / view workflows backed by MySQL."
        ),
        "tech": "HTML, CSS, Bootstrap, MySQL",
        "github_url": "",
        "live_url": "",
    },
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    tech        TEXT NOT NULL,
    github_url  TEXT DEFAULT '',
    live_url    TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO projects (title, description, tech, github_url, live_url, created_at) "
            "VALUES (:title, :description, :tech, :github_url, :live_url, :created_at)",
            [dict(p, created_at=now()) for p in SEED_PROJECTS],
        )
    db.commit()
    db.close()


def fetch_projects():
    rows = get_db().execute("SELECT * FROM projects ORDER BY id").fetchall()
    projects = []
    for r in rows:
        p = dict(r)
        p["tech_list"] = [t.strip() for t in p["tech"].split(",") if t.strip()]
        projects.append(p)
    return projects


@app.route("/")
def index():
    return render_template("index.html", profile=PROFILE, projects=fetch_projects())


@app.route("/api/projects", methods=["GET"])
def api_projects():
    return jsonify([{k: v for k, v in p.items() if k != "tech_list"} for p in fetch_projects()])


@app.route("/api/projects", methods=["POST"])
def api_add_project():
    if not ADMIN_TOKEN or request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        return jsonify(error="Unauthorized"), 401
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    tech = (data.get("tech") or "").strip()
    if not (title and description and tech):
        return jsonify(error="title, description and tech are required"), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO projects (title, description, tech, github_url, live_url, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (title, description, tech, data.get("github_url", ""), data.get("live_url", ""), now()),
    )
    db.commit()
    return jsonify(id=cur.lastrowid), 201


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    body = (data.get("message") or "").strip()
    if not name or not body or not EMAIL_RE.match(email):
        return jsonify(error="Please provide a name, a valid email and a message."), 400
    if len(name) > 100 or len(email) > 200 or len(body) > 2000:
        return jsonify(error="One of the fields is too long."), 400
    db = get_db()
    db.execute(
        "INSERT INTO messages (name, email, body, created_at) VALUES (?, ?, ?, ?)",
        (name, email, body, now()),
    )
    db.commit()
    return jsonify(ok=True), 201


@app.route("/health")
def health():
    return jsonify(status="ok")


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", 5000)))
