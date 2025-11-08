from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "AI Job Application Assistant backend"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Development server. For production use a WSGI server (gunicorn).
    app.run(host='0.0.0.0', port=5000, debug=True)
