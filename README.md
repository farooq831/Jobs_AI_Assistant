AI Job Application Assistant — project scaffold

This repo contains scaffolding for the AI Job Application Assistant MVP.

Quick start (Windows PowerShell)

# 1. Create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. (Optional) Initialize frontend (React)
# npx create-react-app frontend

# 4. Run backend (development)
$env:FLASK_APP = "backend/app.py"
flask run --host=0.0.0.0 --port=5000

Project layout
- `backend/` — Flask app scaffold
- `frontend/` — frontend app (not created by default; see `frontend/README.md`)
- `docs/` — project docs (PRD, scope)

Next steps
- Implement scraper proof-of-concept and tests
- Build frontend forms and wire to backend APIs
- Add CI and unit tests
