from flask import Flask, jsonify, request
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Store user details in memory (for now - can be replaced with database later)
user_details_store = {}

def validate_user_details(data):
    """
    Server-side validation for user details
    Returns (is_valid, errors_dict)
    """
    errors = {}
    
    # Validate name
    if 'name' not in data or not data['name']:
        errors['name'] = 'Name is required'
    elif not isinstance(data['name'], str):
        errors['name'] = 'Name must be a string'
    elif len(data['name'].strip()) < 2:
        errors['name'] = 'Name must be at least 2 characters'
    elif len(data['name'].strip()) > 100:
        errors['name'] = 'Name must not exceed 100 characters'
    elif not re.match(r'^[a-zA-Z\s\'-]+$', data['name'].strip()):
        errors['name'] = 'Name contains invalid characters'
    
    # Validate location
    if 'location' not in data or not data['location']:
        errors['location'] = 'Location is required'
    elif not isinstance(data['location'], str):
        errors['location'] = 'Location must be a string'
    elif len(data['location'].strip()) < 2:
        errors['location'] = 'Location must be at least 2 characters'
    elif len(data['location'].strip()) > 100:
        errors['location'] = 'Location must not exceed 100 characters'
    
    # Validate salary_min
    if 'salary_min' not in data:
        errors['salary_min'] = 'Minimum salary is required'
    elif not isinstance(data['salary_min'], (int, float)):
        errors['salary_min'] = 'Minimum salary must be a number'
    elif data['salary_min'] < 0:
        errors['salary_min'] = 'Minimum salary cannot be negative'
    elif data['salary_min'] > 10000000:
        errors['salary_min'] = 'Minimum salary seems unrealistic'
    
    # Validate salary_max
    if 'salary_max' not in data:
        errors['salary_max'] = 'Maximum salary is required'
    elif not isinstance(data['salary_max'], (int, float)):
        errors['salary_max'] = 'Maximum salary must be a number'
    elif data['salary_max'] < 0:
        errors['salary_max'] = 'Maximum salary cannot be negative'
    elif data['salary_max'] > 10000000:
        errors['salary_max'] = 'Maximum salary seems unrealistic'
    
    # Validate salary range
    if 'salary_min' not in errors and 'salary_max' not in errors:
        if data['salary_min'] > data['salary_max']:
            errors['salary_min'] = 'Minimum salary cannot exceed maximum salary'
            errors['salary_max'] = 'Maximum salary must be greater than minimum salary'
    
    # Validate job_titles
    if 'job_titles' not in data:
        errors['job_titles'] = 'Job titles are required'
    elif not isinstance(data['job_titles'], list):
        errors['job_titles'] = 'Job titles must be a list'
    elif len(data['job_titles']) == 0:
        errors['job_titles'] = 'At least one job title is required'
    elif len(data['job_titles']) > 20:
        errors['job_titles'] = 'Maximum 20 job titles allowed'
    else:
        # Validate each job title
        for i, title in enumerate(data['job_titles']):
            if not isinstance(title, str):
                errors['job_titles'] = f'Job title at position {i+1} must be a string'
                break
            elif len(title.strip()) < 2:
                errors['job_titles'] = f'Job title at position {i+1} is too short'
                break
            elif len(title.strip()) > 100:
                errors['job_titles'] = f'Job title at position {i+1} is too long'
                break
    
    return len(errors) == 0, errors

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "AI Job Application Assistant backend"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/user-details', methods=['POST'])
def submit_user_details():
    """
    Endpoint to receive and validate user details
    Expected JSON payload:
    {
        "name": "John Doe",
        "location": "New York, NY",
        "salary_min": 50000,
        "salary_max": 80000,
        "job_titles": ["Software Engineer", "Full Stack Developer"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        # Validate the data
        is_valid, errors = validate_user_details(data)
        
        if not is_valid:
            return jsonify({
                "success": False,
                "message": "Validation failed",
                "errors": errors
            }), 400
        
        # Store the user details (in memory for now)
        user_id = len(user_details_store) + 1
        user_details_store[user_id] = {
            "name": data['name'].strip(),
            "location": data['location'].strip(),
            "salary_min": data['salary_min'],
            "salary_max": data['salary_max'],
            "job_titles": [title.strip() for title in data['job_titles']]
        }
        
        return jsonify({
            "success": True,
            "message": "User details saved successfully",
            "user_id": user_id,
            "data": user_details_store[user_id]
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/user-details', methods=['GET'])
def get_user_details():
    """
    Endpoint to retrieve all stored user details
    """
    return jsonify({
        "success": True,
        "count": len(user_details_store),
        "data": user_details_store
    }), 200

@app.route('/api/user-details/<int:user_id>', methods=['GET'])
def get_user_detail_by_id(user_id):
    """
    Endpoint to retrieve specific user details by ID
    """
    if user_id in user_details_store:
        return jsonify({
            "success": True,
            "data": user_details_store[user_id]
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

if __name__ == '__main__':
    # Development server. For production use a WSGI server (gunicorn).
    app.run(host='0.0.0.0', port=5000, debug=True)
