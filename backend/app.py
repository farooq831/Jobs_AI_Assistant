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
from data_processor import DataProcessor, clean_job_data, filter_jobs
from keyword_extractor import get_keyword_extractor
from job_scorer import get_job_scorer
from resume_analyzer import get_resume_analyzer
import requests

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
        }, 200)
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


@app.route('/api/filter-jobs', methods=['POST'])
def filter_jobs_endpoint():
    """
    Filter jobs based on user preferences
    
    Expected JSON payload:
    {
        "jobs": [...],  // Optional - if not provided, uses stored jobs
        "user_location": "New York, NY",  // Optional
        "salary_min": 50000,  // Optional
        "salary_max": 150000,  // Optional
        "job_types": ["Remote", "Hybrid"]  // Optional - Remote, Onsite, Hybrid
    }
    
    Returns filtered jobs and filtering statistics
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        # Get jobs to filter (either from request or storage)
        jobs = data.get('jobs')
        if not jobs:
            # If no jobs provided, get from storage
            jobs = storage_manager.get_all_jobs()
            
            if not jobs:
                return jsonify({
                    "success": False,
                    "message": "No jobs available to filter. Please scrape jobs first."
                }), 404
        
        # Extract filter criteria
        user_location = data.get('user_location')
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        job_types = data.get('job_types')
        
        # Validate salary range if both provided
        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                return jsonify({
                    "success": False,
                    "message": "salary_min cannot be greater than salary_max"
                }), 400
        
        # Apply filters
        filtered_jobs, stats = filter_jobs(
            jobs,
            user_location=user_location,
            salary_min=salary_min,
            salary_max=salary_max,
            job_types=job_types
        )
        
        return jsonify({
            "success": True,
            "message": "Jobs filtered successfully",
            "statistics": stats,
            "filtered_jobs_count": len(filtered_jobs),
            "jobs": filtered_jobs
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error filtering jobs: {str(e)}"
        }), 500


@app.route('/api/filter-jobs/user/<int:user_id>', methods=['POST'])
def filter_jobs_by_user_preferences(user_id):
    """
    Filter stored jobs based on a specific user's preferences
    
    Uses the user details stored from /api/user-details endpoint
    
    Optional JSON payload:
    {
        "job_types": ["Remote", "Hybrid"]  // Override job type preferences
    }
    
    Returns filtered jobs matching user's location and salary preferences
    """
    try:
        # Get user details
        if user_id not in user_details_store:
            return jsonify({
                "success": False,
                "message": f"User with ID {user_id} not found"
            }), 404
        
        user_details = user_details_store[user_id]
        
        # Get jobs from storage
        jobs = storage_manager.get_all_jobs()
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "No jobs available to filter. Please scrape jobs first."
            }), 404
        
        # Get optional job types from request
        data = request.get_json() if request.get_json() else {}
        job_types = data.get('job_types')
        
        # Apply filters using user's preferences
        filtered_jobs, stats = filter_jobs(
            jobs,
            user_location=user_details.get('location'),
            salary_min=user_details.get('salary_min'),
            salary_max=user_details.get('salary_max'),
            job_types=job_types
        )
        
        return jsonify({
            "success": True,
            "message": f"Jobs filtered for user {user_details.get('name')}",
            "user_details": {
                "name": user_details.get('name'),
                "location": user_details.get('location'),
                "salary_min": user_details.get('salary_min'),
                "salary_max": user_details.get('salary_max'),
                "job_types": job_types
            },
            "statistics": stats,
            "filtered_jobs_count": len(filtered_jobs),
            "jobs": filtered_jobs
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error filtering jobs: {str(e)}"
        }), 500


# ============================================================================
# KEYWORD EXTRACTION ENDPOINTS (Task 5.1)
# ============================================================================

@app.route('/api/extract-keywords/job', methods=['POST'])
def extract_job_keywords():
    """
    Extract keywords from job posting data.
    
    Expected JSON:
    {
        "title": "Software Engineer",
        "description": "Job description text...",
        "job_id": "optional-job-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        title = data.get('title', '')
        description = data.get('description', '')
        
        if not title and not description:
            return jsonify({
                "success": False,
                "message": "Either title or description must be provided"
            }), 400
        
        # Get keyword extractor
        extractor = get_keyword_extractor()
        
        # Extract keywords
        job_data = {
            'title': title,
            'description': description
        }
        
        keywords = extractor.extract_job_keywords(job_data)
        
        return jsonify({
            "success": True,
            "job_id": data.get('job_id'),
            "keywords": keywords,
            "message": "Keywords extracted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error extracting keywords: {str(e)}"
        }), 500


@app.route('/api/extract-keywords/resume', methods=['POST'])
def extract_resume_keywords():
    """
    Extract keywords from resume text.
    
    Expected JSON:
    {
        "resume_text": "Resume content...",
        "resume_id": "optional-resume-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        resume_text = data.get('resume_text', '')
        
        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({
                "success": False,
                "message": "Resume text must be at least 50 characters"
            }), 400
        
        # Get keyword extractor
        extractor = get_keyword_extractor()
        
        # Extract keywords
        keywords = extractor.extract_resume_keywords(resume_text)
        
        return jsonify({
            "success": True,
            "resume_id": data.get('resume_id'),
            "keywords": keywords,
            "message": "Keywords extracted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error extracting keywords: {str(e)}"
        }), 500


@app.route('/api/extract-keywords/resume/<resume_id>', methods=['GET'])
def extract_keywords_from_stored_resume(resume_id):
    """
    Extract keywords from a previously uploaded resume.
    """
    try:
        # Get resume from storage
        resume_data = uploaded_resumes.get(resume_id)
        
        if not resume_data:
            return jsonify({
                "success": False,
                "message": "Resume not found"
            }), 404
        
        resume_text = resume_data.get('extracted_text', '')
        
        if not resume_text:
            return jsonify({
                "success": False,
                "message": "No text available for this resume"
            }), 400
        
        # Get keyword extractor
        extractor = get_keyword_extractor()
        
        # Extract keywords
        keywords = extractor.extract_resume_keywords(resume_text)
        
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "resume_filename": resume_data.get('filename'),
            "keywords": keywords,
            "message": "Keywords extracted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error extracting keywords: {str(e)}"
        }), 500


@app.route('/api/match-keywords', methods=['POST'])
def match_keywords():
    """
    Calculate keyword match between job and resume.
    
    Expected JSON:
    {
        "job_keywords": {...},  // Output from extract_job_keywords
        "resume_keywords": {...}  // Output from extract_resume_keywords
    }
    
    OR
    
    {
        "job_id": "job-123",
        "resume_id": "resume-456"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        # Get keyword extractor
        extractor = get_keyword_extractor()
        
        # Option 1: Direct keyword objects provided
        if 'job_keywords' in data and 'resume_keywords' in data:
            job_keywords = data['job_keywords']
            resume_keywords = data['resume_keywords']
        
        # Option 2: Extract from stored job and resume
        elif 'job_id' in data and 'resume_id' in data:
            job_id = data['job_id']
            resume_id = data['resume_id']
            
            # Get job from storage
            storage = JobStorageManager()
            all_jobs = storage.get_all_jobs()
            job = next((j for j in all_jobs if j.get('id') == job_id), None)
            
            if not job:
                return jsonify({
                    "success": False,
                    "message": f"Job {job_id} not found"
                }), 404
            
            # Get resume from storage
            resume_data = uploaded_resumes.get(resume_id)
            
            if not resume_data:
                return jsonify({
                    "success": False,
                    "message": f"Resume {resume_id} not found"
                }), 404
            
            # Extract keywords
            job_keywords = extractor.extract_job_keywords(job)
            resume_keywords = extractor.extract_resume_keywords(resume_data.get('extracted_text', ''))
        
        else:
            return jsonify({
                "success": False,
                "message": "Either provide job_keywords and resume_keywords, or job_id and resume_id"
            }), 400
        
        # Calculate match
        match_result = extractor.calculate_keyword_match(job_keywords, resume_keywords)
        
        return jsonify({
            "success": True,
            "match_result": match_result,
            "message": "Keyword match calculated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error calculating keyword match: {str(e)}"
        }), 500


@app.route('/api/batch-extract-keywords/jobs', methods=['POST'])
def batch_extract_job_keywords():
    """
    Extract keywords from multiple jobs at once.
    
    Expected JSON:
    {
        "job_ids": ["job1", "job2", ...]  // Optional: specific job IDs
        "limit": 10  // Optional: limit number of jobs
    }
    
    If no job_ids provided, processes all jobs in storage.
    """
    try:
        data = request.get_json() or {}
        
        # Get jobs from storage
        storage = JobStorageManager()
        all_jobs = storage.get_all_jobs()
        
        # Filter by job_ids if provided
        job_ids = data.get('job_ids', [])
        if job_ids:
            jobs_to_process = [j for j in all_jobs if j.get('id') in job_ids]
        else:
            jobs_to_process = all_jobs
        
        # Apply limit if provided
        limit = data.get('limit')
        if limit:
            jobs_to_process = jobs_to_process[:limit]
        
        if not jobs_to_process:
            return jsonify({
                "success": False,
                "message": "No jobs found to process"
            }), 404
        
        # Get keyword extractor
        extractor = get_keyword_extractor()
        
        # Extract keywords for each job
        results = []
        for job in jobs_to_process:
            try:
                keywords = extractor.extract_job_keywords(job)
                results.append({
                    "job_id": job.get('id'),
                    "job_title": job.get('title'),
                    "keywords": keywords,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "job_id": job.get('id'),
                    "job_title": job.get('title'),
                    "error": str(e),
                    "success": False
                })
        
        successful = sum(1 for r in results if r['success'])
        
        return jsonify({
            "success": True,
            "total_jobs": len(jobs_to_process),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results,
            "message": f"Processed {len(results)} jobs"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error batch extracting keywords: {str(e)}"
        }), 500


@app.route('/api/score-job', methods=['POST'])
def score_single_job():
    """
    Score a single job against user preferences.
    
    Expected JSON:
    {
        "job": {...},  // Job data
        "user_preferences": {...},  // User preferences (location, salary_min/max, job_titles, job_types)
        "resume_keywords": {...}  // Optional: pre-extracted resume keywords
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        job = data.get('job')
        user_preferences = data.get('user_preferences')
        resume_keywords = data.get('resume_keywords')
        
        if not job:
            return jsonify({
                "success": False,
                "message": "Job data is required"
            }), 400
        
        if not user_preferences:
            return jsonify({
                "success": False,
                "message": "User preferences are required"
            }), 400
        
        # Get job scorer
        scorer = get_job_scorer()
        
        # Score the job
        score_result = scorer.score_job(job, user_preferences, resume_keywords)
        
        return jsonify({
            "success": True,
            "score": score_result,
            "message": "Job scored successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error scoring job: {str(e)}"
        }), 500


@app.route('/api/score-jobs', methods=['POST'])
def score_multiple_jobs():
    """
    Score multiple jobs against user preferences.
    
    Expected JSON:
    {
        "jobs": [...],  // Array of job data
        "user_preferences": {...},  // User preferences
        "resume_keywords": {...},  // Optional: pre-extracted resume keywords
        "save_to_storage": true  // Optional: save scores to storage (default: false)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        jobs = data.get('jobs', [])
        user_preferences = data.get('user_preferences')
        resume_keywords = data.get('resume_keywords')
        save_to_storage = data.get('save_to_storage', False)
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "Jobs array is required"
            }), 400
        
        if not user_preferences:
            return jsonify({
                "success": False,
                "message": "User preferences are required"
            }), 400
        
        # Get job scorer
        scorer = get_job_scorer()
        
        # Score all jobs
        scored_jobs = scorer.score_jobs(jobs, user_preferences, resume_keywords)
        
        # Optionally save scores to storage
        if save_to_storage:
            storage = JobStorageManager()
            job_scores = {job['id']: job['score'] for job in scored_jobs if 'id' in job and 'score' in job}
            update_result = storage.update_jobs_scores(job_scores)
            
            return jsonify({
                "success": True,
                "scored_jobs": scored_jobs,
                "storage_update": update_result,
                "message": f"Scored {len(scored_jobs)} jobs and updated storage"
            }), 200
        
        return jsonify({
            "success": True,
            "scored_jobs": scored_jobs,
            "message": f"Scored {len(scored_jobs)} jobs successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error scoring jobs: {str(e)}"
        }), 500


@app.route('/api/score-stored-jobs/<user_id>', methods=['POST'])
def score_stored_jobs(user_id):
    """
    Score all stored jobs for a specific user.
    
    Expected JSON:
    {
        "filters": {...},  // Optional: filters to apply before scoring
        "resume_id": "resume-123"  // Optional: resume ID for keyword extraction
    }
    
    Retrieves user preferences from storage and scores all matching jobs.
    """
    try:
        data = request.get_json() or {}
        
        # Get user preferences
        if user_id not in user_details_store:
            return jsonify({
                "success": False,
                "message": f"User {user_id} not found"
            }), 404
        
        user_preferences = user_details_store[user_id]
        
        # Get resume keywords if resume_id provided
        resume_keywords = None
        resume_id = data.get('resume_id')
        if resume_id and resume_id in resume_store:
            extractor = get_keyword_extractor()
            resume_text = resume_store[resume_id].get('extracted_text', '')
            if resume_text:
                resume_keywords = extractor.extract_resume_keywords(resume_text)
        
        # Get jobs from storage
        storage = JobStorageManager()
        filters = data.get('filters')
        jobs = storage.get_all_jobs(filters)
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "No jobs found in storage"
            }), 404
        
        # Get job scorer
        scorer = get_job_scorer()
        
        # Score all jobs
        scored_jobs = scorer.score_jobs(jobs, user_preferences, resume_keywords)
        
        # Save scores to storage
        job_scores = {job['id']: job['score'] for job in scored_jobs if 'id' in job and 'score' in job}
        update_result = storage.update_jobs_scores(job_scores)
        
        # Calculate statistics
        stats = scorer.calculate_statistics(scored_jobs)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "total_jobs": len(scored_jobs),
            "scored_jobs": scored_jobs,
            "storage_update": update_result,
            "statistics": stats,
            "message": f"Scored {len(scored_jobs)} jobs for user {user_id}"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error scoring stored jobs: {str(e)}"
        }), 500


@app.route('/api/score-thresholds', methods=['GET'])
def get_score_thresholds():
    """
    Get the current scoring thresholds for color highlighting.
    """
    try:
        scorer = get_job_scorer()
        
        return jsonify({
            "success": True,
            "thresholds": {
                "red": scorer.THRESHOLD_RED,
                "yellow": scorer.THRESHOLD_YELLOW,
                "white": 100  # Above yellow threshold
            },
            "description": {
                "red": f"Score < {scorer.THRESHOLD_RED}% - Poor match",
                "yellow": f"{scorer.THRESHOLD_RED}% <= Score < {scorer.THRESHOLD_YELLOW}% - Fair match",
                "white": f"Score >= {scorer.THRESHOLD_YELLOW}% - Good match"
            },
            "message": "Score thresholds retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting score thresholds: {str(e)}"
        }), 500


@app.route('/api/update-weights', methods=['POST'])
def update_scoring_weights():
    """
    Update the scoring weights for the job scorer.
    
    Expected JSON:
    {
        "weights": {
            "keyword_match": 0.5,
            "salary_match": 0.25,
            "location_match": 0.15,
            "job_type_match": 0.1
        }
    }
    
    Weights must sum to 1.0.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        weights = data.get('weights')
        
        if not weights:
            return jsonify({
                "success": False,
                "message": "Weights are required"
            }), 400
        
        # Validate weights sum to 1.0
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            return jsonify({
                "success": False,
                "message": f"Weights must sum to 1.0, got {total}"
            }), 400
        
        # Create new scorer with updated weights
        scorer = get_job_scorer(weights=weights)
        
        return jsonify({
            "success": True,
            "weights": scorer.weights,
            "message": "Scoring weights updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error updating weights: {str(e)}"
        }), 500


@app.route('/api/jobs-by-highlight/<highlight>', methods=['GET'])
def get_jobs_by_highlight(highlight):
    """
    Get all jobs with a specific highlight color.
    
    Parameters:
        highlight: 'red', 'yellow', or 'white'
    """
    try:
        if highlight not in ['red', 'yellow', 'white']:
            return jsonify({
                "success": False,
                "message": "Invalid highlight. Must be 'red', 'yellow', or 'white'"
            }), 400
        
        storage = JobStorageManager()
        jobs = storage.get_jobs_by_highlight(highlight)
        
        return jsonify({
            "success": True,
            "highlight": highlight,
            "total_jobs": len(jobs),
            "jobs": jobs,
            "message": f"Found {len(jobs)} jobs with {highlight} highlight"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting jobs by highlight: {str(e)}"
        }), 500


@app.route('/api/jobs-by-score', methods=['GET'])
def get_jobs_by_score():
    """
    Get jobs filtered by score range.
    
    Query parameters:
        min_score: Minimum score (optional)
        max_score: Maximum score (optional)
    """
    try:
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        
        storage = JobStorageManager()
        jobs = storage.get_scored_jobs(min_score, max_score)
        
        return jsonify({
            "success": True,
            "min_score": min_score,
            "max_score": max_score,
            "total_jobs": len(jobs),
            "jobs": jobs,
            "message": f"Found {len(jobs)} jobs in score range"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting jobs by score: {str(e)}"
        }), 500


# ============================================================================
# RESUME ANALYSIS ENDPOINTS (Task 6.1)
# ============================================================================

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    """
    Analyze resume text and extract comprehensive information.
    
    Expected JSON:
    {
        "resume_text": "Resume content...",
        "resume_id": "optional-resume-id",
        "top_n": 50  // Optional: number of keywords to extract
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        resume_text = data.get('resume_text', '')
        top_n = data.get('top_n', 50)
        
        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({
                "success": False,
                "message": "Resume text must be at least 50 characters"
            }), 400
        
        # Get resume analyzer
        analyzer = get_resume_analyzer()
        
        # Analyze resume
        analysis = analyzer.extract_resume_keywords(resume_text, top_n=top_n)
        
        return jsonify({
            "success": True,
            "resume_id": data.get('resume_id'),
            "analysis": analysis,
            "message": "Resume analyzed successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error analyzing resume: {str(e)}"
        }), 500


@app.route('/api/analyze-resume/<int:resume_id>', methods=['GET'])
def analyze_stored_resume(resume_id):
    """
    Analyze a previously uploaded resume from storage.
    
    Query parameters:
        top_n: Number of keywords to extract (default: 50)
    """
    try:
        # Get resume from storage
        if resume_id not in resume_store:
            return jsonify({
                "success": False,
                "message": "Resume not found"
            }), 404
        
        resume_data = resume_store[resume_id]
        resume_text = resume_data.get('extracted_text', '')
        
        if not resume_text:
            return jsonify({
                "success": False,
                "message": "No text available for this resume"
            }), 400
        
        top_n = request.args.get('top_n', type=int, default=50)
        
        # Get resume analyzer
        analyzer = get_resume_analyzer()
        
        # Analyze resume
        analysis = analyzer.extract_resume_keywords(resume_text, top_n=top_n)
        
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "filename": resume_data.get('filename'),
            "analysis": analysis,
            "message": "Resume analyzed successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error analyzing resume: {str(e)}"
        }), 500


@app.route('/api/extract-skills-from-list', methods=['POST'])
def extract_skills_from_list():
    """
    Extract and categorize skills from a direct list input.
    
    Expected JSON:
    {
        "skills": ["Python", "JavaScript", "Leadership", "Machine Learning", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        skills_list = data.get('skills', [])
        
        if not skills_list or not isinstance(skills_list, list):
            return jsonify({
                "success": False,
                "message": "Skills must be provided as a non-empty list"
            }), 400
        
        # Get resume analyzer
        analyzer = get_resume_analyzer()
        
        # Extract and categorize skills
        categorized = analyzer.extract_skills_from_list(skills_list)
        
        return jsonify({
            "success": True,
            "categorized_skills": categorized,
            "message": "Skills extracted and categorized successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error extracting skills: {str(e)}"
        }), 500


@app.route('/api/compare-resume-with-job', methods=['POST'])
def compare_resume_with_job():
    """
    Compare resume with job posting and get recommendations.
    
    Expected JSON:
    {
        "resume_keywords": {...},  // From analyze-resume endpoint
        "job_keywords": {...},  // From extract-keywords/job endpoint
        "resume_id": "optional-resume-id",
        "job_id": "optional-job-id"
    }
    
    OR
    
    {
        "resume_id": 123,  // ID from resume storage
        "job_id": "job-uuid"  // ID from job storage
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        analyzer = get_resume_analyzer()
        extractor = get_keyword_extractor()
        
        # Option 1: Direct keyword objects provided
        if 'resume_keywords' in data and 'job_keywords' in data:
            resume_keywords = data['resume_keywords']
            job_keywords = data['job_keywords']
        
        # Option 2: Extract from stored resume and job
        elif 'resume_id' in data and 'job_id' in data:
            resume_id = data['resume_id']
            job_id = data['job_id']
            
            # Get resume from storage
            if resume_id not in resume_store:
                return jsonify({
                    "success": False,
                    "message": f"Resume {resume_id} not found"
                }), 404
            
            resume_text = resume_store[resume_id].get('extracted_text', '')
            
            # Get job from storage
            storage = JobStorageManager()
            job = storage.get_job_by_id(job_id)
            
            if not job:
                return jsonify({
                    "success": False,
                    "message": f"Job {job_id} not found"
                }), 404
            
            # Extract keywords
            resume_keywords = analyzer.extract_resume_keywords(resume_text)
            job_keywords = extractor.extract_job_keywords(job)
        
        else:
            return jsonify({
                "success": False,
                "message": "Either provide resume_keywords and job_keywords, or resume_id and job_id"
            }), 400
        
        # Compare resume with job
        comparison = analyzer.compare_resume_with_job(resume_keywords, job_keywords)
        
        return jsonify({
            "success": True,
            "comparison": comparison,
            "message": "Resume and job compared successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error comparing resume with job: {str(e)}"
        }), 500


@app.route('/api/get-skill-categories', methods=['GET'])
def get_skill_categories():
    """
    Get available skill categories for reference.
    
    Returns examples of technical and soft skills.
    """
    try:
        analyzer = get_resume_analyzer()
        categories = analyzer.get_skill_categories()
        
        return jsonify({
            "success": True,
            "skill_categories": categories,
            "message": "Skill categories retrieved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting skill categories: {str(e)}"
        }), 500


@app.route('/api/batch-analyze-resumes', methods=['POST'])
def batch_analyze_resumes():
    """
    Analyze multiple resumes at once.
    
    Expected JSON:
    {
        "resume_ids": [1, 2, 3, ...]  // List of resume IDs from storage
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        resume_ids = data.get('resume_ids', [])
        
        if not resume_ids or not isinstance(resume_ids, list):
            return jsonify({
                "success": False,
                "message": "resume_ids must be provided as a non-empty list"
            }), 400
        
        analyzer = get_resume_analyzer()
        results = []
        
        for resume_id in resume_ids:
            try:
                if resume_id not in resume_store:
                    results.append({
                        "resume_id": resume_id,
                        "success": False,
                        "error": "Resume not found"
                    })
                    continue
                
                resume_data = resume_store[resume_id]
                resume_text = resume_data.get('extracted_text', '')
                
                analysis = analyzer.extract_resume_keywords(resume_text)
                
                results.append({
                    "resume_id": resume_id,
                    "filename": resume_data.get('filename'),
                    "analysis": analysis,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "resume_id": resume_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r.get('success', False))
        
        return jsonify({
            "success": True,
            "total_resumes": len(resume_ids),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results,
            "message": f"Analyzed {successful} out of {len(resume_ids)} resumes"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error batch analyzing resumes: {str(e)}"
        }), 500


@app.route('/api/resume-job-match-report', methods=['POST'])
def generate_resume_job_match_report():
    """
    Generate a comprehensive match report between a resume and multiple jobs.
    
    Expected JSON:
    {
        "resume_id": 123,
        "job_ids": ["job-1", "job-2", ...],  // Optional: specific jobs, or all jobs if not provided
        "min_score": 40  // Optional: minimum match score to include
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        resume_id = data.get('resume_id')
        job_ids = data.get('job_ids', [])
        min_score = data.get('min_score', 0)
        
        if not resume_id:
            return jsonify({
                "success": False,
                "message": "resume_id is required"
            }), 400
        
        # Get resume from storage
        if resume_id not in resume_store:
            return jsonify({
                "success": False,
                "message": f"Resume {resume_id} not found"
            }), 404
        
        resume_text = resume_store[resume_id].get('extracted_text', '')
        
        # Get jobs from storage
        storage = JobStorageManager()
        
        if job_ids:
            jobs = [storage.get_job_by_id(job_id) for job_id in job_ids]
            jobs = [j for j in jobs if j is not None]
        else:
            jobs = storage.get_all_jobs()
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "No jobs found"
            }), 404
        
        # Analyze resume
        analyzer = get_resume_analyzer()
        extractor = get_keyword_extractor()
        
        resume_keywords = analyzer.extract_resume_keywords(resume_text)
        
        # Compare with each job
        match_reports = []
        
        for job in jobs:
            try:
                job_keywords = extractor.extract_job_keywords(job)
                comparison = analyzer.compare_resume_with_job(resume_keywords, job_keywords)
                
                match_score = comparison['weighted_match_score']
                
                if match_score >= min_score:
                    match_reports.append({
                        "job_id": job.get('id'),
                        "job_title": job.get('title'),
                        "company": job.get('company'),
                        "location": job.get('location'),
                        "match_score": match_score,
                        "match_level": comparison['match_level'],
                        "technical_match": comparison['match_result']['technical_match']['match_percentage'],
                        "soft_skills_match": comparison['match_result']['soft_skills_match']['match_percentage'],
                        "recommendations": comparison['recommendations']
                    })
            except Exception as e:
                logger.error(f"Error comparing with job {job.get('id')}: {str(e)}")
        
        # Sort by match score (highest first)
        match_reports.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "resume_filename": resume_store[resume_id].get('filename'),
            "total_jobs_analyzed": len(jobs),
            "matching_jobs": len(match_reports),
            "match_reports": match_reports,
            "message": f"Generated match report for {len(match_reports)} jobs"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error generating match report: {str(e)}"
        }), 500


# ===================================================================
# Task 6.2: Analyze Job Keywords - Missing Keyword Analysis
# ===================================================================

@app.route('/api/analyze-job-keywords', methods=['POST'])
def analyze_job_keywords():
    """
    Task 6.2: Analyze high-frequency keywords across multiple job postings
    and identify which ones are missing from the resume.
    
    Request body:
    {
        "job_descriptions": ["job desc 1", "job desc 2", ...],  // Required
        "resume_text": "resume text...",  // Optional if resume_id provided
        "resume_id": 123,  // Optional if resume_text provided
        "top_n": 30  // Optional, default 30
    }
    
    Returns:
    {
        "success": true,
        "analysis": {
            "analysis_summary": {...},
            "high_frequency_keywords": {...},
            "missing_keywords": {...},
            "recommendations": [...]
        }
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        job_descriptions = data.get('job_descriptions', [])
        resume_text = data.get('resume_text')
        resume_id = data.get('resume_id')
        top_n = data.get('top_n', 30)
        
        # Validate inputs
        if not job_descriptions:
            return jsonify({
                "success": False,
                "message": "At least one job description is required"
            }), 400
        
        if not isinstance(job_descriptions, list):
            return jsonify({
                "success": False,
                "message": "job_descriptions must be an array of strings"
            }), 400
        
        if not resume_text and not resume_id:
            return jsonify({
                "success": False,
                "message": "Either resume_text or resume_id must be provided"
            }), 400
        
        # Get resume text if resume_id provided
        if resume_id and not resume_text:
            resume_id = int(resume_id)
            if resume_id not in resume_store:
                return jsonify({
                    "success": False,
                    "message": f"Resume with ID {resume_id} not found"
                }), 404
            resume_text = resume_store[resume_id].get('full_text')
        
        # Analyze job keywords
        analyzer = get_resume_analyzer()
        analysis = analyzer.analyze_job_keywords(
            job_descriptions=job_descriptions,
            resume_text=resume_text,
            top_n=top_n
        )
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "message": f"Analyzed {len(job_descriptions)} job postings successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Validation error: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(f"Error analyzing job keywords: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error analyzing job keywords: {str(e)}"
        }), 500


@app.route('/api/analyze-job-keywords/stored-jobs', methods=['POST'])
def analyze_keywords_from_stored_jobs():
    """
    Analyze job keywords from stored jobs for a specific resume.
    
    Request body:
    {
        "resume_id": 123,  // Required
        "job_ids": ["job-1", "job-2", ...],  // Optional, analyzes all stored jobs if not provided
        "top_n": 30  // Optional, default 30
    }
    
    Returns: Same as /api/analyze-job-keywords
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        resume_id = data.get('resume_id')
        job_ids = data.get('job_ids')
        top_n = data.get('top_n', 30)
        
        # Validate resume_id
        if not resume_id:
            return jsonify({
                "success": False,
                "message": "resume_id is required"
            }), 400
        
        resume_id = int(resume_id)
        if resume_id not in resume_store:
            return jsonify({
                "success": False,
                "message": f"Resume with ID {resume_id} not found"
            }), 404
        
        resume_text = resume_store[resume_id].get('full_text')
        
        # Get jobs
        if job_ids:
            jobs = []
            for job_id in job_ids:
                job = storage_manager.get_job(job_id)
                if job:
                    jobs.append(job)
        else:
            # Get all stored jobs
            jobs = storage_manager.get_all_jobs()
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "No jobs found to analyze"
            }), 404
        
        # Extract job descriptions
        job_descriptions = [job.get('description', '') for job in jobs if job.get('description')]
        
        if not job_descriptions:
            return jsonify({
                "success": False,
                "message": "No job descriptions found in stored jobs"
            }), 400
        
        # Analyze job keywords
        analyzer = get_resume_analyzer()
        analysis = analyzer.analyze_job_keywords(
            job_descriptions=job_descriptions,
            resume_text=resume_text,
            top_n=top_n
        )
        
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "jobs_analyzed": len(job_descriptions),
            "analysis": analysis,
            "message": f"Analyzed {len(job_descriptions)} stored job postings successfully"
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Validation error: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(f"Error analyzing stored jobs keywords: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error analyzing stored jobs keywords: {str(e)}"
        }), 500


@app.route('/api/missing-keywords-summary/<int:resume_id>', methods=['GET'])
def get_missing_keywords_summary(resume_id):
    """
    Get a quick summary of missing keywords for a resume against all stored jobs.
    
    Returns: Simplified view focused on critical missing keywords
    """
    try:
        # Validate resume
        if resume_id not in resume_store:
            return jsonify({
                "success": False,
                "message": f"Resume with ID {resume_id} not found"
            }), 404
        
        resume_text = resume_store[resume_id].get('full_text')
        
        # Get all stored jobs
        jobs = storage_manager.get_all_jobs()
        
        if not jobs:
            return jsonify({
                "success": False,
                "message": "No jobs found to analyze"
            }), 404
        
        # Extract job descriptions
        job_descriptions = [job.get('description', '') for job in jobs if job.get('description')]
        
        # Analyze job keywords
        analyzer = get_resume_analyzer()
        analysis = analyzer.analyze_job_keywords(
            job_descriptions=job_descriptions,
            resume_text=resume_text,
            top_n=20
        )
        
        # Create simplified summary
        missing = analysis['missing_keywords']
        summary = {
            "critical_technical_skills": [k['keyword'] for k in missing['critical_technical']],
            "important_technical_skills": [k['keyword'] for k in missing['important_technical']],
            "critical_soft_skills": [k['keyword'] for k in missing['critical_soft_skills']],
            "important_soft_skills": [k['keyword'] for k in missing['important_soft_skills']],
            "technical_coverage": analysis['analysis_summary']['technical_coverage_percentage'],
            "soft_skills_coverage": analysis['analysis_summary']['soft_skills_coverage_percentage'],
            "top_recommendations": analysis['recommendations'][:5]
        }
        
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "jobs_analyzed": len(job_descriptions),
            "summary": summary,
            "message": "Missing keywords summary generated successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating missing keywords summary: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error generating summary: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Development server. For production use a WSGI server (gunicorn).
    app.run(host='0.0.0.0', port=5000, debug=True)

# Upload and analyze resume
with open('resume.pdf', 'rb') as f:
    r = requests.post('http://localhost:5000/api/resume-upload', files={'resume': f})
    resume_id = r.json()['resume_id']

# Get analysis
analysis = requests.get(f'http://localhost:5000/api/analyze-resume/{resume_id}')
print(analysis.json()['analysis'])

# Compare with job
comparison = requests.post('http://localhost:5000/api/compare-resume-with-job',
    json={'resume_id': resume_id, 'job_id': 'job-123'})
print(f"Match: {comparison.json()['comparison']['weighted_match_score']}%")

