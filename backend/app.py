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
from storage_manager import JobStorageManager
from data_processor import DataProcessor, clean_job_data

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

# Initialize storage manager for persistent job storage
storage_manager = JobStorageManager(storage_dir='data')

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
        
        # Save to persistent storage
        storage_result = storage_manager.save_jobs(
            all_jobs, 
            source=",".join(sources),
            skip_duplicates=True
        )
        
        # Save to persistent storage
        storage_result = storage_manager.save_jobs(
            all_jobs, 
            source=",".join(sources),
            skip_duplicates=True
        )
        
        return jsonify({
            "success": True,
            "message": f"Scraped {len(all_jobs)} jobs successfully",
            "scrape_id": scrape_id,
            "total_jobs": len(all_jobs),
            "scraping_results": scraping_results,
            "storage_result": storage_result,
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
        
        # Save to persistent storage
        storage_result = storage_manager.save_jobs(
            all_jobs, 
            source=",".join(sources) + "_selenium",
            skip_duplicates=True
        )
        
        # Save to persistent storage
        storage_result = storage_manager.save_jobs(
            all_jobs, 
            source=",".join(sources) + "_selenium",
            skip_duplicates=True
        )
        
        return jsonify({
            "success": True,
            "message": f"Scraped {len(all_jobs)} jobs successfully using Selenium",
            "scrape_id": scrape_id,
            "total_jobs": len(all_jobs),
            "scraping_results": scraping_results,
            "storage_result": storage_result,
            "jobs": all_jobs
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

# ==================== Storage Management Endpoints ====================

@app.route('/api/storage/jobs', methods=['GET'])
def get_stored_jobs():
    """
    Endpoint to retrieve all stored jobs with optional filtering
    Query parameters:
    - source: Filter by source (e.g., 'indeed', 'glassdoor')
    - location: Filter by location
    - limit: Maximum number of jobs to return
    - offset: Number of jobs to skip
    """
    try:
        # Get query parameters
        source = request.args.get('source')
        location = request.args.get('location')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int, default=0)
        
        # Build filters
        filters = {}
        if source:
            filters['source'] = source
        if location:
            filters['location'] = location
        
        # Get jobs
        jobs = storage_manager.get_all_jobs(filters if filters else None)
        
        # Apply pagination
        total = len(jobs)
        if limit:
            jobs = jobs[offset:offset + limit]
        else:
            jobs = jobs[offset:]
        
        return jsonify({
            "success": True,
            "total": total,
            "count": len(jobs),
            "offset": offset,
            "jobs": jobs
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving jobs: {str(e)}"
        }), 500

@app.route('/api/storage/jobs/<job_id>', methods=['GET'])
def get_stored_job(job_id):
    """
    Endpoint to retrieve a specific job by ID
    """
    try:
        job = storage_manager.get_job_by_id(job_id)
        
        if job:
            return jsonify({
                "success": True,
                "job": job
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Job not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving job: {str(e)}"
        }), 500

@app.route('/api/storage/jobs/<job_id>', methods=['DELETE'])
def delete_stored_job(job_id):
    """
    Endpoint to delete a specific job by ID
    """
    try:
        success = storage_manager.delete_job(job_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Job deleted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Job not found or deletion failed"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error deleting job: {str(e)}"
        }), 500

@app.route('/api/storage/jobs', methods=['DELETE'])
def clear_stored_jobs():
    """
    Endpoint to clear all stored jobs
    """
    try:
        success = storage_manager.clear_all_jobs()
        
        if success:
            return jsonify({
                "success": True,
                "message": "All jobs cleared successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to clear jobs"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error clearing jobs: {str(e)}"
        }), 500

@app.route('/api/storage/statistics', methods=['GET'])
def get_storage_statistics():
    """
    Endpoint to get storage statistics
    """
    try:
        stats = storage_manager.get_statistics()
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving statistics: {str(e)}"
        }), 500

@app.route('/api/storage/errors', methods=['GET'])
def get_storage_errors():
    """
    Endpoint to get recent scraping errors
    Query parameters:
    - limit: Maximum number of errors to return (default: 10)
    """
    try:
        limit = request.args.get('limit', type=int, default=10)
        errors = storage_manager.get_recent_errors(limit)
        
        return jsonify({
            "success": True,
            "count": len(errors),
            "errors": errors
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error retrieving errors: {str(e)}"
        }), 500

@app.route('/api/storage/export', methods=['POST'])
def export_stored_jobs():
    """
    Endpoint to export jobs to a JSON file
    Expected JSON payload:
    {
        "output_file": "exported_jobs.json",
        "filters": {
            "source": "indeed",
            "location": "New York"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'output_file' not in data:
            return jsonify({
                "success": False,
                "message": "output_file is required"
            }), 400
        
        output_file = data['output_file']
        filters = data.get('filters')
        
        # Ensure output file is in data directory for security
        output_path = os.path.join('data', os.path.basename(output_file))
        
        success = storage_manager.export_to_json(output_path, filters)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Jobs exported to {output_path}",
                "file": output_path
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Export failed"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error exporting jobs: {str(e)}"
        }), 500


@app.route('/api/clean-data', methods=['POST'])
def clean_data():
    """
    Clean and normalize job data
    Removes duplicates, incomplete entries, and normalizes locations and salaries
    
    Request body:
    {
        "jobs": [...],  # Optional: provide jobs to clean, or clean stored jobs
        "save": true    # Optional: save cleaned data back to storage (default: false)
    }
    
    Returns cleaned jobs and statistics
    """
    try:
        data = request.get_json()
        save_to_storage = data.get('save', False) if data else False
        
        # Get jobs to clean
        if data and 'jobs' in data:
            jobs = data['jobs']
        else:
            # Load jobs from storage
            jobs = storage_manager.get_all_jobs()
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "No jobs to clean. Please provide jobs or scrape data first."
            }), 400
        
        # Clean the data
        cleaned_jobs, stats = clean_job_data(jobs)
        
        # Optionally save back to storage
        if save_to_storage:
            storage_manager.clear_jobs()
            for job in cleaned_jobs:
                storage_manager.add_job(job)
            
        return jsonify({
            "success": True,
            "message": "Data cleaning completed successfully",
            "statistics": stats,
            "cleaned_jobs_count": len(cleaned_jobs),
            "jobs": cleaned_jobs
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error cleaning data: {str(e)}"
        }), 500


@app.route('/api/clean-data/stats', methods=['GET'])
def get_cleaning_stats():
    """
    Get statistics about stored jobs and potential cleaning improvements
    
    Returns job statistics and cleaning recommendations
    """
    try:
        jobs = storage_manager.get_all_jobs()
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "No jobs found in storage"
            }), 404
        
        # Analyze data for potential issues
        processor = DataProcessor()
        
        # Count potential duplicates
        seen_hashes = set()
        duplicates = 0
        for job in jobs:
            job_hash = processor._generate_job_hash(job)
            if job_hash in seen_hashes:
                duplicates += 1
            seen_hashes.add(job_hash)
        
        # Count incomplete entries
        incomplete = sum(1 for job in jobs if not all(
            job.get(field) and str(job.get(field)).strip()
            for field in processor.REQUIRED_FIELDS
        ))
        
        # Count entries with unnormalized data
        unnormalized_locations = sum(1 for job in jobs 
            if 'location' in job and job['location'] and 
            processor._normalize_single_location(job['location']) != job['location'])
        
        unnormalized_salaries = sum(1 for job in jobs 
            if 'salary' in job and job['salary'] and 
            not job.get('salary_min'))
        
        return jsonify({
            "success": True,
            "total_jobs": len(jobs),
            "potential_duplicates": duplicates,
            "incomplete_entries": incomplete,
            "unnormalized_locations": unnormalized_locations,
            "unnormalized_salaries": unnormalized_salaries,
            "recommendation": "Run /api/clean-data with save=true to clean the data" if (duplicates > 0 or incomplete > 0) else "Data appears clean"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error analyzing data: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Development server. For production use a WSGI server (gunicorn).
    app.run(host='0.0.0.0', port=5000, debug=True)
