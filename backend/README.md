Backend (Flask) setup

Windows PowerShell (from project root):

# Create a virtual environment
python -m venv .venv

# Activate the venv in PowerShell
.\.venv\Scripts\Activate.ps1

# Install backend (project-level) dependencies
pip install -r requirements.txt

# Run the Flask app (development)
$env:FLASK_APP = "backend/app.py"
flask run --host=0.0.0.0 --port=5000

Notes
- The `requirements.txt` is in the project root and includes scraping and NLP libs used in the MVP.
- For production, use a WSGI server (e.g., gunicorn) and configure environment variables securely.
- If you need to install spaCy language models, run: `python -m spacy download en_core_web_sm` after activating the venv.
