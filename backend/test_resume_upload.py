#!/usr/bin/env python3
"""
Test script for resume upload API endpoint
Tests the /api/resume-upload endpoint with sample files
"""

import requests
import os
import sys
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Backend URL
BASE_URL = "http://localhost:5000"

def create_sample_pdf():
    """Create a sample PDF file for testing"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Add some sample text
    c.drawString(100, 750, "Sample Resume")
    c.drawString(100, 730, "Name: John Doe")
    c.drawString(100, 710, "Email: john.doe@example.com")
    c.drawString(100, 690, "Phone: (555) 123-4567")
    c.drawString(100, 670, "")
    c.drawString(100, 650, "PROFESSIONAL SUMMARY")
    c.drawString(100, 630, "Experienced software engineer with 5+ years of experience in Python,")
    c.drawString(100, 610, "JavaScript, and React. Strong background in building scalable web")
    c.drawString(100, 590, "applications and RESTful APIs.")
    c.drawString(100, 570, "")
    c.drawString(100, 550, "SKILLS")
    c.drawString(100, 530, "- Python, Flask, Django")
    c.drawString(100, 510, "- JavaScript, React, Node.js")
    c.drawString(100, 490, "- SQL, PostgreSQL, MongoDB")
    c.drawString(100, 470, "- Git, Docker, AWS")
    
    c.save()
    buffer.seek(0)
    return buffer

def test_health_check():
    """Test if the backend is running"""
    print("\n" + "="*60)
    print("Test 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend is running")
            print(f"Response: {response.json()}")
            return True
        else:
            print("✗ Backend returned unexpected status code")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend. Is it running?")
        print("Please start the backend with: python backend/app.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_upload_pdf():
    """Test uploading a PDF file"""
    print("\n" + "="*60)
    print("Test 2: Upload PDF Resume")
    print("="*60)
    
    try:
        # Create a sample PDF
        pdf_buffer = create_sample_pdf()
        
        # Prepare the file for upload
        files = {
            'resume': ('sample_resume.pdf', pdf_buffer, 'application/pdf')
        }
        
        response = requests.post(f"{BASE_URL}/api/resume-upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print("✓ PDF upload successful")
                print(f"  - Filename: {data.get('filename')}")
                print(f"  - File Type: {data.get('file_type')}")
                print(f"  - Text Length: {data.get('text_length')}")
                print(f"  - Resume ID: {data.get('resume_id')}")
                return data.get('resume_id')
            else:
                print("✗ Upload failed:", data.get('message'))
                return None
        else:
            print("✗ Upload failed with status code:", response.status_code)
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_no_file_upload():
    """Test uploading without a file"""
    print("\n" + "="*60)
    print("Test 3: Upload Without File (Should Fail)")
    print("="*60)
    
    try:
        response = requests.post(f"{BASE_URL}/api/resume-upload")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("✓ Correctly rejected request without file")
            return True
        else:
            print("✗ Should have returned 400 status code")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_invalid_file_type():
    """Test uploading an invalid file type"""
    print("\n" + "="*60)
    print("Test 4: Upload Invalid File Type (Should Fail)")
    print("="*60)
    
    try:
        # Create a fake text file
        files = {
            'resume': ('resume.txt', BytesIO(b'This is a text file'), 'text/plain')
        }
        
        response = requests.post(f"{BASE_URL}/api/resume-upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("✓ Correctly rejected invalid file type")
            return True
        else:
            print("✗ Should have returned 400 status code")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_resume(resume_id):
    """Test retrieving a resume by ID"""
    print("\n" + "="*60)
    print(f"Test 5: Get Resume by ID ({resume_id})")
    print("="*60)
    
    if not resume_id:
        print("⊘ Skipped (no resume ID available)")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/resume/{resume_id}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ Successfully retrieved resume")
                return True
            else:
                print("✗ Failed to retrieve resume")
                return False
        else:
            print("✗ Request failed with status code:", response.status_code)
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_resume_full_text(resume_id):
    """Test retrieving full text from a resume"""
    print("\n" + "="*60)
    print(f"Test 6: Get Full Resume Text ({resume_id})")
    print("="*60)
    
    if not resume_id:
        print("⊘ Skipped (no resume ID available)")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/resume/{resume_id}/full-text")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ Successfully retrieved full text")
                print(f"  - Text Length: {len(data.get('extracted_text', ''))}")
                print(f"  - Text Preview: {data.get('extracted_text', '')[:100]}...")
                return True
            else:
                print("✗ Failed to retrieve full text")
                return False
        else:
            print("✗ Request failed with status code:", response.status_code)
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Resume Upload API Test Suite")
    print("="*60)
    
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("\n⚠ Warning: reportlab not found. Installing...")
        os.system(f"{sys.executable} -m pip install reportlab")
    
    # Run tests
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    if not results[0][1]:
        print("\n" + "="*60)
        print("Tests aborted: Backend is not running")
        print("="*60)
        return
    
    # Test 2: Upload PDF
    resume_id = test_upload_pdf()
    results.append(("Upload PDF", resume_id is not None))
    
    # Test 3: No file upload
    results.append(("No File Upload", test_no_file_upload()))
    
    # Test 4: Invalid file type
    results.append(("Invalid File Type", test_invalid_file_type()))
    
    # Test 5: Get resume
    results.append(("Get Resume", test_get_resume(resume_id)))
    
    # Test 6: Get full text
    results.append(("Get Full Text", test_get_resume_full_text(resume_id)))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:25} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
