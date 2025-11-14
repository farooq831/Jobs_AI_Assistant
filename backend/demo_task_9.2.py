#!/usr/bin/env python3
"""
Demo Script for Task 9.2: Forms and File Upload Controls
Comprehensive demonstration of all form validation and file upload functionality
"""

import requests
import json
import os
import sys
from io import BytesIO
from pathlib import Path

# API Base URL
BASE_URL = "http://localhost:5000"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{CYAN}{BOLD}{'='*80}{RESET}")
    print(f"{CYAN}{BOLD}{text.center(80)}{RESET}")
    print(f"{CYAN}{BOLD}{'='*80}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ {text}{RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")


def demo_1_user_details_form_valid():
    """Demo 1: Submit valid user details form"""
    print_header("Demo 1: Valid User Details Form Submission")
    
    user_data = {
        "name": "John Doe",
        "location": "New York, NY",
        "salary_min": 80000,
        "salary_max": 120000,
        "job_titles": ["Software Engineer", "Full Stack Developer"],
        "job_types": ["Remote", "Hybrid"]
    }
    
    print_info(f"Submitting user details:")
    print(json.dumps(user_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_success("User details submitted successfully!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print_error(f"Failed with status {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def demo_2_user_details_form_invalid():
    """Demo 2: Test form validation with invalid data"""
    print_header("Demo 2: Form Validation with Invalid Data")
    
    # Test case 1: Missing required fields
    print_info("Test Case 1: Missing required fields")
    invalid_data_1 = {
        "name": "",
        "location": "",
        "salary_min": -1000,
        "salary_max": 50000
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=invalid_data_1,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print_success("Validation correctly rejected invalid data")
            errors = response.json().get('errors', {})
            print(f"Validation errors: {json.dumps(errors, indent=2)}")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
    
    # Test case 2: Invalid salary range
    print_info("\nTest Case 2: Invalid salary range (min > max)")
    invalid_data_2 = {
        "name": "Test User",
        "location": "Boston, MA",
        "salary_min": 150000,
        "salary_max": 80000,
        "job_titles": ["Developer"],
        "job_types": ["Remote"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/user-details",
            json=invalid_data_2,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print_success("Validation correctly rejected invalid salary range")
            errors = response.json().get('errors', {})
            print(f"Validation errors: {json.dumps(errors, indent=2)}")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def demo_3_resume_upload_pdf():
    """Demo 3: Upload a PDF resume"""
    print_header("Demo 3: Resume Upload (PDF)")
    
    # Create a sample PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Sample Resume) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000214 00000 n\n0000000304 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n397\n%%EOF"
    
    files = {
        'resume': ('sample_resume.pdf', BytesIO(pdf_content), 'application/pdf')
    }
    
    print_info("Uploading sample PDF resume...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/resume-upload",
            files=files
        )
        
        if response.status_code == 200:
            print_success("Resume uploaded successfully!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result.get('resume_id')
        else:
            print_error(f"Upload failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return None


def demo_4_resume_upload_invalid():
    """Demo 4: Test resume upload validation"""
    print_header("Demo 4: Resume Upload Validation")
    
    # Test case 1: Invalid file type
    print_info("Test Case 1: Invalid file type (.txt)")
    invalid_file = {
        'resume': ('invalid.txt', BytesIO(b"This is a text file"), 'text/plain')
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/resume-upload",
            files=invalid_file
        )
        
        if response.status_code == 400:
            print_success("Validation correctly rejected invalid file type")
            print(f"Error message: {response.json().get('message')}")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
    
    # Test case 2: File too large (simulated)
    print_info("\nTest Case 2: File size validation")
    print_info("(Actual test would require 10MB+ file, skipping for demo)")


def demo_5_export_excel():
    """Demo 5: Export jobs to Excel"""
    print_header("Demo 5: Export Jobs to Excel")
    
    export_data = {
        "jobs": [
            {
                "id": "job_001",
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "New York, NY",
                "salary": "$80,000 - $120,000",
                "job_type": "Remote",
                "match_score": 85,
                "highlight": "green"
            },
            {
                "id": "job_002",
                "title": "Full Stack Developer",
                "company": "Startup Inc",
                "location": "San Francisco, CA",
                "salary": "$90,000 - $130,000",
                "job_type": "Hybrid",
                "match_score": 75,
                "highlight": "yellow"
            }
        ],
        "user_id": "user_001",
        "include_tips": True
    }
    
    print_info("Exporting jobs to Excel...")
    print(f"Jobs to export: {len(export_data['jobs'])}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/export/excel",
            json=export_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_success("Excel export successful!")
            
            # Save the file
            filename = "demo_jobs_export.xlsx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print_success(f"File saved as: {filename}")
            print_info(f"File size: {len(response.content)} bytes")
        else:
            print_error(f"Export failed with status {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def demo_6_export_csv():
    """Demo 6: Export jobs to CSV"""
    print_header("Demo 6: Export Jobs to CSV")
    
    export_data = {
        "jobs": [
            {
                "id": "job_001",
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "New York, NY",
                "salary": "$80,000 - $120,000",
                "job_type": "Remote",
                "match_score": 85
            }
        ],
        "user_id": "user_001"
    }
    
    print_info("Exporting jobs to CSV...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/export/csv",
            json=export_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_success("CSV export successful!")
            
            # Save the file
            filename = "demo_jobs_export.csv"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print_success(f"File saved as: {filename}")
            
            # Display content preview
            content = response.content.decode('utf-8')
            lines = content.split('\n')[:5]
            print_info("File preview (first 5 lines):")
            for line in lines:
                print(f"  {line}")
        else:
            print_error(f"Export failed with status {response.status_code}")
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def demo_7_export_pdf():
    """Demo 7: Export jobs to PDF"""
    print_header("Demo 7: Export Jobs to PDF")
    
    export_data = {
        "jobs": [
            {
                "id": "job_001",
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "New York, NY",
                "salary": "$80,000 - $120,000",
                "job_type": "Remote",
                "match_score": 85,
                "highlight": "green",
                "description": "Great opportunity for experienced software engineer."
            }
        ],
        "user_id": "user_001",
        "include_tips": True
    }
    
    print_info("Exporting jobs to PDF...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/export/pdf",
            json=export_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_success("PDF export successful!")
            
            # Save the file
            filename = "demo_jobs_export.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print_success(f"File saved as: {filename}")
            print_info(f"File size: {len(response.content)} bytes")
        else:
            print_error(f"Export failed with status {response.status_code}")
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")


def demo_8_excel_upload_validation():
    """Demo 8: Excel upload validation"""
    print_header("Demo 8: Excel Upload Validation")
    
    print_info("Testing Excel upload validation endpoint...")
    print_warning("Note: This requires a pre-formatted Excel file")
    print_info("Skipping actual upload for demo (would use real Excel file)")


def demo_9_form_field_validation():
    """Demo 9: Test individual field validation"""
    print_header("Demo 9: Individual Field Validation")
    
    test_cases = [
        {
            "name": "Name too short",
            "data": {"name": "A", "location": "NYC", "salary_min": 50000, "salary_max": 80000, "job_titles": ["Dev"], "job_types": ["Remote"]},
            "expected": "validation error"
        },
        {
            "name": "Name too long",
            "data": {"name": "A" * 150, "location": "NYC", "salary_min": 50000, "salary_max": 80000, "job_titles": ["Dev"], "job_types": ["Remote"]},
            "expected": "validation error"
        },
        {
            "name": "Negative salary",
            "data": {"name": "John Doe", "location": "NYC", "salary_min": -5000, "salary_max": 80000, "job_titles": ["Dev"], "job_types": ["Remote"]},
            "expected": "validation error"
        },
        {
            "name": "Empty job titles",
            "data": {"name": "John Doe", "location": "NYC", "salary_min": 50000, "salary_max": 80000, "job_titles": [], "job_types": ["Remote"]},
            "expected": "validation error"
        },
        {
            "name": "No job types selected",
            "data": {"name": "John Doe", "location": "NYC", "salary_min": 50000, "salary_max": 80000, "job_titles": ["Dev"], "job_types": []},
            "expected": "validation error"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print_info(f"\nTest Case {i}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/user-details",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print_success("Validation correctly rejected invalid data")
                errors = response.json().get('errors', {})
                print(f"  Errors: {list(errors.keys())}")
            else:
                print_warning(f"Unexpected status: {response.status_code}")
        except Exception as e:
            print_error(f"Exception occurred: {str(e)}")


def demo_10_job_type_selection():
    """Demo 10: Job type selection validation"""
    print_header("Demo 10: Job Type Selection (Remote/Onsite/Hybrid)")
    
    test_cases = [
        {
            "name": "Remote only",
            "job_types": ["Remote"]
        },
        {
            "name": "Onsite only",
            "job_types": ["Onsite"]
        },
        {
            "name": "Hybrid only",
            "job_types": ["Hybrid"]
        },
        {
            "name": "All types",
            "job_types": ["Remote", "Onsite", "Hybrid"]
        },
        {
            "name": "Remote and Hybrid",
            "job_types": ["Remote", "Hybrid"]
        }
    ]
    
    for test_case in test_cases:
        print_info(f"\nTesting: {test_case['name']}")
        
        data = {
            "name": "Test User",
            "location": "New York, NY",
            "salary_min": 70000,
            "salary_max": 100000,
            "job_titles": ["Software Engineer"],
            "job_types": test_case['job_types']
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/user-details",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print_success(f"Successfully submitted with job types: {', '.join(test_case['job_types'])}")
            else:
                print_error(f"Failed with status {response.status_code}")
        except Exception as e:
            print_error(f"Exception occurred: {str(e)}")


def run_all_demos():
    """Run all demonstration scenarios"""
    print_header("TASK 9.2: FORMS AND FILE UPLOAD CONTROLS - COMPREHENSIVE DEMO")
    
    print_info("This demo showcases all form validation and file upload functionality")
    print_info("Make sure the Flask backend is running on http://localhost:5000\n")
    
    demos = [
        ("User Details Form - Valid Submission", demo_1_user_details_form_valid),
        ("User Details Form - Validation Testing", demo_2_user_details_form_invalid),
        ("Resume Upload - PDF", demo_3_resume_upload_pdf),
        ("Resume Upload - Validation", demo_4_resume_upload_invalid),
        ("Export to Excel", demo_5_export_excel),
        ("Export to CSV", demo_6_export_csv),
        ("Export to PDF", demo_7_export_pdf),
        ("Excel Upload Validation", demo_8_excel_upload_validation),
        ("Field-by-Field Validation", demo_9_form_field_validation),
        ("Job Type Selection", demo_10_job_type_selection)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
            input(f"\n{YELLOW}Press Enter to continue to next demo...{RESET}")
        except KeyboardInterrupt:
            print_warning("\n\nDemo interrupted by user")
            sys.exit(0)
        except Exception as e:
            print_error(f"Demo failed with error: {str(e)}")
            input(f"\n{YELLOW}Press Enter to continue...{RESET}")
    
    print_header("ALL DEMOS COMPLETED")
    print_success("Task 9.2 demonstration finished successfully!")


def interactive_menu():
    """Interactive menu for selecting demos"""
    while True:
        print_header("TASK 9.2 DEMO - INTERACTIVE MENU")
        print("Select a demo to run:")
        print(f"{CYAN}1.{RESET}  User Details Form - Valid Submission")
        print(f"{CYAN}2.{RESET}  User Details Form - Validation Testing")
        print(f"{CYAN}3.{RESET}  Resume Upload - PDF")
        print(f"{CYAN}4.{RESET}  Resume Upload - Validation")
        print(f"{CYAN}5.{RESET}  Export to Excel")
        print(f"{CYAN}6.{RESET}  Export to CSV")
        print(f"{CYAN}7.{RESET}  Export to PDF")
        print(f"{CYAN}8.{RESET}  Excel Upload Validation")
        print(f"{CYAN}9.{RESET}  Field-by-Field Validation")
        print(f"{CYAN}10.{RESET} Job Type Selection")
        print(f"{CYAN}11.{RESET} Run All Demos")
        print(f"{CYAN}0.{RESET}  Exit")
        
        choice = input(f"\n{YELLOW}Enter your choice (0-11): {RESET}").strip()
        
        demos = {
            '1': demo_1_user_details_form_valid,
            '2': demo_2_user_details_form_invalid,
            '3': demo_3_resume_upload_pdf,
            '4': demo_4_resume_upload_invalid,
            '5': demo_5_export_excel,
            '6': demo_6_export_csv,
            '7': demo_7_export_pdf,
            '8': demo_8_excel_upload_validation,
            '9': demo_9_form_field_validation,
            '10': demo_10_job_type_selection,
            '11': run_all_demos
        }
        
        if choice == '0':
            print_info("Exiting demo...")
            break
        elif choice in demos:
            try:
                demos[choice]()
                input(f"\n{YELLOW}Press Enter to return to menu...{RESET}")
            except KeyboardInterrupt:
                print_warning("\n\nDemo interrupted")
            except Exception as e:
                print_error(f"Error: {str(e)}")
                input(f"\n{YELLOW}Press Enter to continue...{RESET}")
        else:
            print_error("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--all':
            run_all_demos()
        else:
            interactive_menu()
    except KeyboardInterrupt:
        print_warning("\n\nExiting...")
        sys.exit(0)
