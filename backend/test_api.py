"""
Test script for User Details API endpoints
Run this after starting the Flask backend server
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_valid_submission():
    """Test valid user details submission"""
    print("\n=== Testing Valid Submission ===")
    data = {
        "name": "John Doe",
        "location": "New York, NY",
        "salary_min": 50000,
        "salary_max": 80000,
        "job_titles": ["Software Engineer", "Full Stack Developer", "Python Developer"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/user-details",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201

def test_invalid_submission_missing_fields():
    """Test submission with missing fields"""
    print("\n=== Testing Missing Fields ===")
    data = {
        "name": "Jane Smith"
        # Missing other required fields
    }
    
    response = requests.post(
        f"{BASE_URL}/api/user-details",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

def test_invalid_submission_salary_range():
    """Test submission with invalid salary range"""
    print("\n=== Testing Invalid Salary Range ===")
    data = {
        "name": "Bob Johnson",
        "location": "Chicago, IL",
        "salary_min": 100000,
        "salary_max": 50000,  # Max less than min
        "job_titles": ["Data Scientist"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/user-details",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

def test_invalid_submission_empty_name():
    """Test submission with empty name"""
    print("\n=== Testing Empty Name ===")
    data = {
        "name": "",
        "location": "Boston, MA",
        "salary_min": 60000,
        "salary_max": 90000,
        "job_titles": ["DevOps Engineer"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/user-details",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

def test_get_all_users():
    """Test retrieving all user details"""
    print("\n=== Testing Get All Users ===")
    response = requests.get(f"{BASE_URL}/api/user-details")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_user_by_id():
    """Test retrieving user by ID"""
    print("\n=== Testing Get User by ID (ID=1) ===")
    response = requests.get(f"{BASE_URL}/api/user-details/1")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 404]

def test_get_nonexistent_user():
    """Test retrieving non-existent user"""
    print("\n=== Testing Get Non-existent User (ID=9999) ===")
    response = requests.get(f"{BASE_URL}/api/user-details/9999")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 404

def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("User Details API Test Suite")
    print("=" * 60)
    print("\nMake sure the Flask backend is running on http://localhost:5000")
    print("\nStarting tests...")
    
    tests = [
        ("Health Check", test_health_check),
        ("Valid Submission", test_valid_submission),
        ("Missing Fields", test_invalid_submission_missing_fields),
        ("Invalid Salary Range", test_invalid_submission_salary_range),
        ("Empty Name", test_invalid_submission_empty_name),
        ("Get All Users", test_get_all_users),
        ("Get User by ID", test_get_user_by_id),
        ("Get Non-existent User", test_get_nonexistent_user),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append((test_name, "ERROR"))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, status in results:
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {status}")
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
