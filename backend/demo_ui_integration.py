#!/usr/bin/env python3
"""
Demo script for Task 8.3: UI Integration
Demonstrates the integration of job dashboard with application status tracking.
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def demo_1_fetch_jobs():
    """Demo 1: Fetch all stored jobs"""
    print_section("Demo 1: Fetch All Jobs")
    
    try:
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            print(f"✓ Successfully fetched {len(jobs)} jobs")
            
            if jobs:
                print("\nSample job:")
                job = jobs[0]
                print(f"  ID: {job.get('id')}")
                print(f"  Title: {job.get('title')}")
                print(f"  Company: {job.get('company')}")
                print(f"  Score: {job.get('score', 'N/A')}")
                print(f"  Highlight: {job.get('highlight', 'N/A')}")
                print(f"  Status: {job.get('status', 'pending')}")
        else:
            print(f"✗ Failed to fetch jobs: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_2_get_status_summary():
    """Demo 2: Get application status summary"""
    print_section("Demo 2: Get Status Summary")
    
    try:
        response = requests.get(f"{BASE_URL}/api/jobs/status/summary")
        if response.status_code == 200:
            summary = response.json()
            print("✓ Status Summary:")
            print(f"  Total Jobs: {summary.get('total_jobs', 0)}")
            print(f"  Applied: {summary.get('applied', 0)}")
            print(f"  Interview: {summary.get('interview', 0)}")
            print(f"  Offer: {summary.get('offer', 0)}")
            print(f"  Rejected: {summary.get('rejected', 0)}")
            print(f"  Pending: {summary.get('pending', 0)}")
        else:
            print(f"✗ Failed to get summary: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_3_update_job_status():
    """Demo 3: Update job status"""
    print_section("Demo 3: Update Job Status")
    
    # First, get a job to update
    try:
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        if response.status_code != 200:
            print("✗ Cannot fetch jobs for demo")
            return
        
        jobs = response.json().get('jobs', [])
        if not jobs:
            print("✗ No jobs available for demo")
            return
        
        job = jobs[0]
        job_id = job.get('id')
        print(f"Updating job: {job.get('title')} at {job.get('company')}")
        
        # Update status
        update_data = {
            "status": "applied",
            "notes": "Application submitted via company website",
            "user_id": "demo_user"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/status/{job_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Status updated successfully")
            print(f"  Old Status: {result.get('old_status', 'N/A')}")
            print(f"  New Status: {result.get('new_status')}")
            print(f"  Timestamp: {result.get('timestamp')}")
        else:
            print(f"✗ Failed to update status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_4_get_status_history():
    """Demo 4: Get status history for a job"""
    print_section("Demo 4: Get Status History")
    
    try:
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        if response.status_code != 200:
            print("✗ Cannot fetch jobs for demo")
            return
        
        jobs = response.json().get('jobs', [])
        if not jobs:
            print("✗ No jobs available for demo")
            return
        
        job = jobs[0]
        job_id = job.get('id')
        print(f"Fetching history for: {job.get('title')} at {job.get('company')}")
        
        response = requests.get(f"{BASE_URL}/api/jobs/status-history/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            print(f"✓ Found {len(history)} status changes")
            
            for i, entry in enumerate(history[:3], 1):  # Show first 3
                print(f"\n  Entry {i}:")
                print(f"    Status: {entry.get('old_status', 'N/A')} → {entry.get('new_status')}")
                print(f"    Timestamp: {entry.get('timestamp')}")
                if entry.get('notes'):
                    print(f"    Notes: {entry.get('notes')}")
        else:
            print(f"✗ Failed to get history: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_5_filter_jobs_by_status():
    """Demo 5: Filter jobs by status"""
    print_section("Demo 5: Filter Jobs by Status")
    
    statuses = ['pending', 'applied', 'interview']
    
    for status in statuses:
        try:
            response = requests.get(f"{BASE_URL}/api/jobs/status?status={status}")
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                print(f"✓ {status.upper()}: {len(jobs)} jobs")
            else:
                print(f"✗ Failed to filter by {status}: {response.status_code}")
        except Exception as e:
            print(f"✗ Error filtering {status}: {e}")

def demo_6_filter_jobs_by_highlight():
    """Demo 6: Filter jobs by highlight"""
    print_section("Demo 6: Filter Jobs by Highlight")
    
    highlights = ['red', 'yellow', 'green']
    
    for highlight in highlights:
        try:
            response = requests.get(f"{BASE_URL}/api/jobs-by-highlight/{highlight}")
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                print(f"✓ {highlight.upper()}: {len(jobs)} jobs")
                
                if jobs:
                    print(f"   Sample: {jobs[0].get('title')} - Score: {jobs[0].get('score', 'N/A')}")
            else:
                print(f"✗ Failed to filter by {highlight}: {response.status_code}")
        except Exception as e:
            print(f"✗ Error filtering {highlight}: {e}")

def demo_7_batch_status_update():
    """Demo 7: Batch status update"""
    print_section("Demo 7: Batch Status Update")
    
    try:
        response = requests.get(f"{BASE_URL}/api/storage/jobs")
        if response.status_code != 200:
            print("✗ Cannot fetch jobs for demo")
            return
        
        jobs = response.json().get('jobs', [])
        if len(jobs) < 2:
            print("✗ Need at least 2 jobs for batch demo")
            return
        
        # Update first 2 jobs
        updates = [
            {
                "job_id": jobs[0].get('id'),
                "status": "interview",
                "notes": "Phone screening scheduled"
            },
            {
                "job_id": jobs[1].get('id'),
                "status": "applied",
                "notes": "Applied via LinkedIn"
            }
        ]
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/batch-status",
            json={"updates": updates, "user_id": "demo_user"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Batch update successful")
            print(f"  Updated: {result.get('updated', 0)} jobs")
            print(f"  Failed: {result.get('failed', 0)} jobs")
        else:
            print(f"✗ Failed batch update: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_8_enhanced_status_summary():
    """Demo 8: Get enhanced status summary with details"""
    print_section("Demo 8: Enhanced Status Summary")
    
    try:
        response = requests.get(f"{BASE_URL}/api/jobs/status-summary/enhanced")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Enhanced Status Summary:")
            print(f"\n  Overview:")
            print(f"    Total Jobs: {data.get('total_jobs', 0)}")
            print(f"    Total Applications: {data.get('total_with_status', 0)}")
            
            print(f"\n  By Status:")
            for status, count in data.get('by_status', {}).items():
                print(f"    {status.capitalize()}: {count}")
            
            if 'recent_updates' in data:
                print(f"\n  Recent Updates: {len(data['recent_updates'])}")
        else:
            print(f"✗ Failed to get enhanced summary: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_9_ui_workflow_simulation():
    """Demo 9: Simulate complete UI workflow"""
    print_section("Demo 9: Complete UI Workflow Simulation")
    
    print("Simulating user journey through UI...")
    
    # Step 1: User opens dashboard
    print("\n1. User opens dashboard - fetching jobs...")
    time.sleep(0.5)
    response = requests.get(f"{BASE_URL}/api/storage/jobs")
    if response.status_code == 200:
        jobs_count = len(response.json().get('jobs', []))
        print(f"   ✓ Loaded {jobs_count} jobs")
    
    # Step 2: User views status summary
    print("\n2. User views status summary...")
    time.sleep(0.5)
    response = requests.get(f"{BASE_URL}/api/jobs/status/summary")
    if response.status_code == 200:
        summary = response.json()
        print(f"   ✓ Summary displayed: {summary.get('total_jobs', 0)} total jobs")
    
    # Step 3: User filters by highlight
    print("\n3. User filters by 'red' highlight...")
    time.sleep(0.5)
    response = requests.get(f"{BASE_URL}/api/jobs-by-highlight/red")
    if response.status_code == 200:
        red_jobs = len(response.json().get('jobs', []))
        print(f"   ✓ Filtered: {red_jobs} red-highlighted jobs")
    
    # Step 4: User clicks to update status
    print("\n4. User clicks 'Update Status' on a job...")
    time.sleep(0.5)
    response = requests.get(f"{BASE_URL}/api/storage/jobs")
    if response.status_code == 200:
        jobs = response.json().get('jobs', [])
        if jobs:
            job = jobs[0]
            print(f"   ✓ Modal opened for: {job.get('title')}")
            
            # Step 5: User views status history
            print("\n5. User views status history...")
            time.sleep(0.5)
            response = requests.get(f"{BASE_URL}/api/jobs/status-history/{job.get('id')}")
            if response.status_code == 200:
                history_count = len(response.json().get('history', []))
                print(f"   ✓ History loaded: {history_count} entries")
            
            # Step 6: User updates status
            print("\n6. User updates status to 'applied'...")
            time.sleep(0.5)
            response = requests.put(
                f"{BASE_URL}/api/jobs/status/{job.get('id')}",
                json={"status": "applied", "notes": "Applied via company portal"}
            )
            if response.status_code == 200:
                print(f"   ✓ Status updated successfully")
    
    print("\n✓ Workflow simulation complete!")

def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  TASK 8.3: UI INTEGRATION - DEMO SUITE")
    print("  Testing job dashboard and status tracking integration")
    print("="*60)
    
    demos = [
        ("Fetch All Jobs", demo_1_fetch_jobs),
        ("Get Status Summary", demo_2_get_status_summary),
        ("Update Job Status", demo_3_update_job_status),
        ("Get Status History", demo_4_get_status_history),
        ("Filter by Status", demo_5_filter_jobs_by_status),
        ("Filter by Highlight", demo_6_filter_jobs_by_highlight),
        ("Batch Status Update", demo_7_batch_status_update),
        ("Enhanced Summary", demo_8_enhanced_status_summary),
        ("UI Workflow Simulation", demo_9_ui_workflow_simulation),
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  0. Run all demos")
    
    choice = input("\nSelect demo to run (0-9): ").strip()
    
    if choice == '0':
        for name, demo_func in demos:
            demo_func()
            time.sleep(1)
    elif choice.isdigit() and 1 <= int(choice) <= len(demos):
        demos[int(choice) - 1][1]()
    else:
        print("Invalid choice")
    
    print("\n" + "="*60)
    print("  Demo Complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
