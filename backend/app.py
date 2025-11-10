from flask import Flask, jsonify, request
from flask_cors import CORS
import re
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import io
from scrapers.indeed_scraper import IndeedScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from scrapers.indeed_selenium_scraper import IndeedSeleniumScraper
from scrapers.glassdoor_selenium_scraper import GlassdoorSeleniumScraper

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Store user details in memory (for now - can be replaced with database later)
user_details_store = {}
# Store resume data in memory
resume_store = {}
# Store scraped jobs in memory
scraped_jobs_store = {}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_stream):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")

def extract_text_from_docx(file_stream):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_stream)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting DOCX text: {str(e)}")

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

@app.route('/api/resume-upload', methods=['POST'])
def upload_resume():
    """
    Endpoint to handle resume file upload and extract text
    Expected: multipart/form-data with 'resume' file field
    """
    try:
        # Check if file is in the request
        if 'resume' not in request.files:
            return jsonify({
                "success": False,
                "message": "No file provided"
            }), 400
        
        file = request.files['resume']
        
        # Check if file has a name
        if file.filename == '':
            return jsonify({
                "success": False,
                "message": "No file selected"
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "message": "Invalid file type. Only PDF and DOCX files are allowed."
            }), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Read file content
        file_stream = io.BytesIO(file.read())
        
        # Extract text based on file type
        try:
            if file_extension == 'pdf':
                extracted_text = extract_text_from_pdf(file_stream)
            elif file_extension == 'docx':
                extracted_text = extract_text_from_docx(file_stream)
            else:
                return jsonify({
                    "success": False,
                    "message": "Unsupported file type"
                }), 400
            
            # Validate that text was extracted
            if not extracted_text or len(extracted_text.strip()) < 50:
                return jsonify({
                    "success": False,
                    "message": "Could not extract sufficient text from the resume. Please ensure the file is readable and contains text."
                }), 400
            
            # Save the file (optional - for future reference)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_stream.seek(0)  # Reset stream position
            with open(file_path, 'wb') as f:
                f.write(file_stream.read())
            
            # Store resume data in memory
            resume_id = len(resume_store) + 1
            resume_store[resume_id] = {
                "filename": filename,
                "file_type": file_extension,
                "extracted_text": extracted_text,
                "text_length": len(extracted_text),
                "file_path": file_path
            }
            
            return jsonify({
                "success": True,
                "message": "Resume uploaded and processed successfully",
                "resume_id": resume_id,
                "filename": filename,
                "file_type": file_extension,
                "text_length": len(extracted_text),
                "text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
            }), 201
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error processing file: {str(e)}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/resume/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    """
    Endpoint to retrieve resume data by ID
    """
    if resume_id in resume_store:
        resume = resume_store[resume_id].copy()
        # Don't send the full text by default, just metadata
        resume_data = {
            "resume_id": resume_id,
            "filename": resume["filename"],
            "file_type": resume["file_type"],
            "text_length": resume["text_length"],
            "text_preview": resume["extracted_text"][:200] + "..." if len(resume["extracted_text"]) > 200 else resume["extracted_text"]
        }
        return jsonify({
            "success": True,
            "data": resume_data
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Resume not found"
        }), 404

@app.route('/api/resume/<int:resume_id>/full-text', methods=['GET'])
def get_resume_full_text(resume_id):
    """
    Endpoint to retrieve full extracted text from resume
    """
    if resume_id in resume_store:
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "extracted_text": resume_store[resume_id]["extracted_text"]
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Resume not found"
        }), 404

@app.route('/api/scrape-jobs', methods=['POST'])
def scrape_jobs():
    """
    Endpoint to scrape jobs from Indeed and Glassdoor
    Expected JSON payload:
    {
        "job_titles": ["Software Engineer", "Data Scientist"],
        "location": "New York, NY",
        "num_pages": 2,
        "sources": ["indeed", "glassdoor"]  // Optional, defaults to both
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        # Validate required fields
        if 'job_titles' not in data or not isinstance(data['job_titles'], list):
            return jsonify({
                "success": False,
                "message": "job_titles must be a list"
            }), 400
        
        if 'location' not in data or not data['location']:
            return jsonify({
                "success": False,
                "message": "location is required"
            }), 400
        
        job_titles = data['job_titles']
        location = data['location']
        num_pages = data.get('num_pages', 1)
        sources = data.get('sources', ['indeed', 'glassdoor'])
        
        # Validate num_pages
        if not isinstance(num_pages, int) or num_pages < 1 or num_pages > 5:
            return jsonify({
                "success": False,
                "message": "num_pages must be an integer between 1 and 5"
            }), 400
        
        all_jobs = []
        scraping_results = {
            "indeed": {"success": False, "count": 0, "error": None},
            "glassdoor": {"success": False, "count": 0, "error": None}
        }
        
        # Scrape from Indeed
        if 'indeed' in sources:
            try:
                indeed_scraper = IndeedScraper()
                for job_title in job_titles:
                    jobs = indeed_scraper.scrape_jobs(job_title, location, num_pages)
                    all_jobs.extend(jobs)
                    scraping_results["indeed"]["count"] += len(jobs)
                scraping_results["indeed"]["success"] = True
            except Exception as e:
                scraping_results["indeed"]["error"] = str(e)
                print(f"Error scraping Indeed: {str(e)}")
        
        # Scrape from Glassdoor
        if 'glassdoor' in sources:
            try:
                glassdoor_scraper = GlassdoorScraper()
                for job_title in job_titles:
                    jobs = glassdoor_scraper.scrape_jobs(job_title, location, num_pages)
                    all_jobs.extend(jobs)
                    scraping_results["glassdoor"]["count"] += len(jobs)
                scraping_results["glassdoor"]["success"] = True
            except Exception as e:
                scraping_results["glassdoor"]["error"] = str(e)
                print(f"Error scraping Glassdoor: {str(e)}")
        
        # Store scraped jobs
        scrape_id = len(scraped_jobs_store) + 1
        scraped_jobs_store[scrape_id] = {
            "job_titles": job_titles,
            "location": location,
            "num_pages": num_pages,
            "sources": sources,
            "jobs": all_jobs,
            "total_jobs": len(all_jobs),
            "scraping_results": scraping_results
        }
        
        return jsonify({
            "success": True,
            "message": f"Scraped {len(all_jobs)} jobs successfully",
            "scrape_id": scrape_id,
            "total_jobs": len(all_jobs),
            "scraping_results": scraping_results,
            "jobs": all_jobs
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/scrape-jobs/<int:scrape_id>', methods=['GET'])
def get_scraped_jobs(scrape_id):
    """
    Endpoint to retrieve scraped jobs by ID
    """
    if scrape_id in scraped_jobs_store:
        return jsonify({
            "success": True,
            "data": scraped_jobs_store[scrape_id]
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Scrape result not found"
        }), 404

@app.route('/api/scrape-jobs', methods=['GET'])
def get_all_scraped_jobs():
    """
    Endpoint to retrieve all scraped jobs
    """
    return jsonify({
        "success": True,
        "count": len(scraped_jobs_store),
        "data": scraped_jobs_store
    }), 200

@app.route('/api/scrape-jobs-dynamic', methods=['POST'])
def scrape_jobs_dynamic():
    """
    Endpoint to scrape jobs using Selenium for dynamic content
    Handles JavaScript-loaded content and pagination
    Expected JSON payload:
    {
        "job_titles": ["Software Engineer", "Data Scientist"],
        "location": "New York, NY",
        "num_pages": 2,
        "sources": ["indeed", "glassdoor"],  // Optional, defaults to both
        "headless": true  // Optional, defaults to true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        # Validate required fields
        if 'job_titles' not in data or not isinstance(data['job_titles'], list):
            return jsonify({
                "success": False,
                "message": "job_titles must be a list"
            }), 400
        
        if 'location' not in data or not data['location']:
            return jsonify({
                "success": False,
                "message": "location is required"
            }), 400
        
        job_titles = data['job_titles']
        location = data['location']
        num_pages = data.get('num_pages', 1)
        sources = data.get('sources', ['indeed', 'glassdoor'])
        headless = data.get('headless', True)
        
        # Validate num_pages
        if not isinstance(num_pages, int) or num_pages < 1 or num_pages > 5:
            return jsonify({
                "success": False,
                "message": "num_pages must be an integer between 1 and 5"
            }), 400
        
        all_jobs = []
        scraping_results = {
            "indeed": {"success": False, "count": 0, "error": None},
            "glassdoor": {"success": False, "count": 0, "error": None}
        }
        
        # Scrape from Indeed using Selenium
        if 'indeed' in sources:
            try:
                indeed_scraper = IndeedSeleniumScraper(headless=headless)
                for job_title in job_titles:
                    jobs = indeed_scraper.scrape_jobs(job_title, location, num_pages)
                    all_jobs.extend(jobs)
                    scraping_results["indeed"]["count"] += len(jobs)
                scraping_results["indeed"]["success"] = True
            except Exception as e:
                scraping_results["indeed"]["error"] = str(e)
                print(f"Error scraping Indeed with Selenium: {str(e)}")
        
        # Scrape from Glassdoor using Selenium
        if 'glassdoor' in sources:
            try:
                glassdoor_scraper = GlassdoorSeleniumScraper(headless=headless)
                for job_title in job_titles:
                    jobs = glassdoor_scraper.scrape_jobs(job_title, location, num_pages)
                    all_jobs.extend(jobs)
                    scraping_results["glassdoor"]["count"] += len(jobs)
                scraping_results["glassdoor"]["success"] = True
            except Exception as e:
                scraping_results["glassdoor"]["error"] = str(e)
                print(f"Error scraping Glassdoor with Selenium: {str(e)}")
        
        # Store scraped jobs
        scrape_id = len(scraped_jobs_store) + 1
        scraped_jobs_store[scrape_id] = {
            "job_titles": job_titles,
            "location": location,
            "num_pages": num_pages,
            "sources": sources,
            "method": "selenium",
            "jobs": all_jobs,
            "total_jobs": len(all_jobs),
            "scraping_results": scraping_results
        }
        
        return jsonify({
            "success": True,
            "message": f"Scraped {len(all_jobs)} jobs successfully using Selenium",
            "scrape_id": scrape_id,
            "total_jobs": len(all_jobs),
            "scraping_results": scraping_results,
            "jobs": all_jobs
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Development server. For production use a WSGI server (gunicorn).
    app.run(host='0.0.0.0', port=5000, debug=True)
