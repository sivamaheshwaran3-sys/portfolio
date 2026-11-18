# Personal Portfolio Website

Full-stack portfolio: HTML/CSS/JavaScript frontend, Flask backend, SQLite database.
Project cards are read from the database; the contact form saves messages to it.

## Run locally

```bash
pip install -r requirements.txt
python app.py          # http://localhost:5000
```

The database (`portfolio.db`) is created and seeded with your two projects on first run.

## Before you publish

- In `app.py`, set the `github` and `linkedin` URLs in `PROFILE`.
- Add `github_url` / `live_url` for each project (edit `SEED_PROJECTS` before first run, or use the API below).
- Edit the profile text, skills and achievements in `PROFILE` as needed.

## API

| Method | Route            | Purpose                                         |
|--------|------------------|-------------------------------------------------|
| GET    | `/api/projects`  | List projects (JSON)                            |
| POST   | `/api/projects`  | Add a project; needs `X-Admin-Token` header     |
| POST   | `/api/contact`   | Save a contact message                          |
| GET    | `/health`        | Health check                                    |

Add a project (set `ADMIN_TOKEN` in the environment first):

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" -H "X-Admin-Token: $ADMIN_TOKEN" \
  -d '{"title":"My App","description":"What it does","tech":"Django, MySQL","github_url":"https://github.com/you/app"}'
```

Read saved contact messages:

```bash
sqlite3 portfolio.db "SELECT created_at, name, email, body FROM messages;"
```

## Deploy
https://portfolio-7rjy.onrender.com
**Heroku / Render** (a Python server is needed, so these fit best):
1. Push this folder to a GitHub repo.
2. Create the app and connect the repo. The `Procfile` runs `gunicorn app:app`.
3. Set `ADMIN_TOKEN`. Note: these platforms reset the local filesystem on redeploy, so SQLite data
   is lost. For a durable live site, move to the platform's PostgreSQL add-on or set `DATABASE_PATH`
   to a persistent disk (Render offers one).

**Netlify / Vercel** are built for static sites and serverless functions, so this Flask app would need
adapting there. Use Heroku or Render to deploy it as-is.

## Structure

```
app.py              Flask app, routes, schema, seed data
templates/index.html  Page template
static/style.css      Styling
static/script.js      Contact form logic
requirements.txt, Procfile
```
