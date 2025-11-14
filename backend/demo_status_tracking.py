"""
Interactive Demo for Task 8.2: Backend Status Tracking Logic
Demonstrates the complete job application status tracking functionality

Author: AI Job Application Assistant
Date: November 2025
Version: 1.0.0
"""

import os
import shutil
from datetime import datetime, timedelta
from storage_manager import JobStorageManager
from application_status import ApplicationStatus

# Setup demo environment
DEMO_DIR = "demo_status_data"


def setup_demo():
    """Setup demo environment with sample data"""
    print("="*70)
    print("TASK 8.2: BACKEND STATUS TRACKING LOGIC - DEMONSTRATION")
    print("="*70)
    print()
    
    # Clean up any existing demo data
    if os.path.exists(DEMO_DIR):
        shutil.rmtree(DEMO_DIR)
    
    # Create storage manager
    storage = JobStorageManager(storage_dir=DEMO_DIR)
    
    # Add sample jobs
    sample_jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Giants Inc",
            "location": "San Francisco, CA",
            "salary": "$150,000 - $180,000",
            "job_type": "Hybrid",
            "description": "Build scalable cloud applications",
            "link": "https://example.com/job1"
        },
        {
            "title": "Data Scientist",
            "company": "AI Innovations",
            "location": "New York, NY",
            "salary": "$140,000 - $170,000",
            "job_type": "Remote",
            "description": "ML model development",
            "link": "https://example.com/job2"
        },
        {
            "title": "Product Manager",
            "company": "StartupXYZ",
            "location": "Austin, TX",
            "salary": "$130,000 - $160,000",
            "job_type": "Onsite",
            "description": "Lead product strategy",
            "link": "https://example.com/job3"
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Services Co",
            "location": "Seattle, WA",
            "salary": "$135,000 - $165,000",
            "job_type": "Remote",
            "description": "Infrastructure automation",
            "link": "https://example.com/job4"
        },
        {
            "title": "Full Stack Developer",
            "company": "Web Solutions Ltd",
            "location": "Boston, MA",
            "salary": "$120,000 - $150,000",
            "job_type": "Hybrid",
            "description": "Modern web development",
            "link": "https://example.com/job5"
        }
    ]
    
    print("📦 Adding sample jobs to storage...")
    result = storage.save_jobs(sample_jobs, source="demo")
    print(f"✅ Added {result['added']} jobs")
    print()
    
    # Get stored jobs with their IDs
    stored_jobs = storage.get_all_jobs()
    job_ids = [job['id'] for job in stored_jobs]
    
    return storage, job_ids


def demo_1_create_status_histories(storage, job_ids):
    """Demo 1: Create status histories for jobs"""
    print("="*70)
    print("DEMO 1: Creating Status Histories")
    print("="*70)
    print()
    
    print("📝 Creating status histories for all jobs...")
    for i, job_id in enumerate(job_ids, 1):
        success = storage.create_status_history(job_id, "Pending")
        status = "✅" if success else "❌"
        print(f"  {status} Job {i}: {job_id[:20]}...")
    
    print()
    print("📊 Status Summary:")
    histories = storage.get_all_status_histories()
    print(f"  Total histories created: {len(histories)}")
    print()


def demo_2_update_statuses(storage, job_ids):
    """Demo 2: Update job statuses with notes"""
    print("="*70)
    print("DEMO 2: Updating Job Statuses")
    print("="*70)
    print()
    
    updates = [
        (job_ids[0], "Applied", "Submitted application via LinkedIn", "user_demo"),
        (job_ids[1], "Applied", "Applied through company website", "user_demo"),
        (job_ids[2], "Interview", "Phone screen completed, on-site scheduled", "user_demo"),
        (job_ids[3], "Applied", "Submitted with referral", "user_demo"),
        (job_ids[4], "Pending", "Preparing application materials", "user_demo"),
    ]
    
    print("🔄 Updating job statuses...")
    for job_id, status, notes, user_id in updates:
        result = storage.update_job_status_with_history(
            job_id=job_id,
            new_status=status,
            notes=notes,
            user_id=user_id
        )
        
        if result["success"]:
            print(f"  ✅ {result['new_status']:12} | Days in status: {result['days_in_status']}")
            print(f"     Note: {notes}")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        print()


def demo_3_status_progression(storage, job_ids):
    """Demo 3: Progress a job through multiple statuses"""
    print("="*70)
    print("DEMO 3: Job Application Progression")
    print("="*70)
    print()
    
    job_id = job_ids[1]  # Data Scientist position
    
    print(f"📈 Progressing application through lifecycle...")
    print(f"   Job ID: {job_id[:20]}...")
    print()
    
    progression = [
        ("Interview", "Technical phone screen passed"),
        ("Interview", "On-site interview completed"),
        ("Offer", "Offer received! Negotiating terms"),
    ]
    
    for status, notes in progression:
        result = storage.update_job_status_with_history(
            job_id=job_id,
            new_status=status,
            notes=notes
        )
        
        if result["success"]:
            print(f"  ✅ {result['new_status']:12} | Transitions: {result['transition_count']}")
            print(f"     {notes}")
        print()
    
    # Show complete timeline
    print("📅 Complete Status Timeline:")
    timeline = storage.get_status_timeline(job_id)
    for i, transition in enumerate(timeline, 1):
        from_status = transition['from_status'] or 'Initial'
        to_status = transition['to_status']
        date = transition['date']
        notes = transition['notes']
        print(f"  {i}. {from_status} → {to_status}")
        print(f"     {date}")
        if notes:
            print(f"     {notes}")
        print()


def demo_4_bulk_updates(storage, job_ids):
    """Demo 4: Bulk status updates"""
    print("="*70)
    print("DEMO 4: Bulk Status Updates")
    print("="*70)
    print()
    
    bulk_updates = [
        {
            "job_id": job_ids[3],
            "status": "Interview",
            "notes": "Moving to interview stage",
            "user_id": "user_demo"
        },
        {
            "job_id": job_ids[4],
            "status": "Applied",
            "notes": "Application submitted",
            "user_id": "user_demo"
        }
    ]
    
    print("🔄 Performing bulk status update...")
    results = storage.bulk_update_statuses(bulk_updates)
    
    print(f"  Total: {results['total']}")
    print(f"  ✅ Successful: {results['successful']}")
    print(f"  ❌ Failed: {results['failed']}")
    
    if results.get('errors'):
        print("\n  Errors:")
        for error in results['errors']:
            print(f"    • Job {error.get('job_id')}: {error.get('error')}")
    print()


def demo_5_query_by_status(storage):
    """Demo 5: Query jobs by status"""
    print("="*70)
    print("DEMO 5: Querying Jobs by Status")
    print("="*70)
    print()
    
    for status in ["Pending", "Applied", "Interview", "Offer"]:
        jobs = storage.get_jobs_by_status_with_history(status)
        print(f"📋 {status} ({len(jobs)} jobs):")
        
        for job in jobs:
            job_data = job.get('status_history', {})
            print(f"  • {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"    Days in status: {job_data.get('days_in_current_status', 0)}")
        
        if not jobs:
            print(f"  No jobs in {status} status")
        print()


def demo_6_enhanced_summary(storage):
    """Demo 6: Get enhanced status summary"""
    print("="*70)
    print("DEMO 6: Enhanced Status Summary")
    print("="*70)
    print()
    
    summary = storage.get_enhanced_status_summary()
    
    print("📊 Overall Statistics:")
    print(f"  Total jobs tracked: {summary.get('total_jobs', 0)}")
    print(f"  Jobs with status: {summary.get('jobs_with_status', 0)}")
    print(f"  Jobs without status: {summary.get('jobs_without_status', 0)}")
    print()
    
    print("📈 Status Distribution:")
    status_counts = summary.get('status_counts', {})
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {status:12} | {bar} ({count})")
    print()
    
    history_stats = summary.get('history_stats', {})
    if history_stats:
        print("📉 History Statistics:")
        print(f"  Avg transitions per job: {history_stats.get('average_transitions', 0):.1f}")
        print(f"  Avg days in current status: {history_stats.get('average_days_in_current_status', 0):.1f}")
        print()


def demo_7_pending_actions(storage):
    """Demo 7: Get jobs pending action"""
    print("="*70)
    print("DEMO 7: Jobs Pending Action")
    print("="*70)
    print()
    
    print("🔍 Jobs that have been in current status for 0+ days:")
    pending = storage.get_jobs_pending_action(days_threshold=0)
    
    if pending:
        for job in pending:
            print(f"  ⚠️  {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"     Status: {job.get('current_status')} ({job.get('days_in_status')} days)")
            print(f"     Last updated: {job.get('last_updated', 'Unknown')[:19]}")
            print()
    else:
        print("  ✅ No jobs pending action")
    print()


def demo_8_invalid_transitions(storage, job_ids):
    """Demo 8: Demonstrate invalid status transitions"""
    print("="*70)
    print("DEMO 8: Invalid Status Transitions")
    print("="*70)
    print()
    
    job_id = job_ids[2]  # Job currently in Interview status
    
    print("❌ Attempting invalid transition (Interview → Pending)...")
    result = storage.update_job_status_with_history(
        job_id=job_id,
        new_status="Pending"
    )
    
    if not result["success"]:
        print(f"  ✅ Correctly rejected: {result.get('error')}")
    else:
        print(f"  ❌ Should have been rejected!")
    print()
    
    print("✅ Valid transitions from Interview:")
    from application_status import get_valid_next_statuses
    valid_next = get_valid_next_statuses("Interview")
    for status in valid_next:
        print(f"  • Interview → {status}")
    print()


def demo_9_export_report(storage):
    """Demo 9: Export comprehensive status report"""
    print("="*70)
    print("DEMO 9: Export Status Report")
    print("="*70)
    print()
    
    report_path = os.path.join(DEMO_DIR, "status_report.json")
    
    print(f"💾 Exporting status report to: {report_path}")
    success = storage.export_status_report(report_path)
    
    if success:
        print("  ✅ Report exported successfully!")
        file_size = os.path.getsize(report_path)
        print(f"  File size: {file_size:,} bytes")
        print()
        
        # Show report structure
        import json
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        print("📄 Report Structure:")
        for key in report.keys():
            if isinstance(report[key], dict):
                print(f"  • {key}: {len(report[key])} items")
            elif isinstance(report[key], list):
                print(f"  • {key}: {len(report[key])} items")
            else:
                print(f"  • {key}: {report[key]}")
    else:
        print("  ❌ Export failed!")
    print()


def demo_10_api_usage():
    """Demo 10: Show API endpoint usage"""
    print("="*70)
    print("DEMO 10: API Endpoints Reference")
    print("="*70)
    print()
    
    endpoints = [
        ("POST", "/api/jobs/status-history/<job_id>", "Create status history"),
        ("PUT", "/api/jobs/status-history/<job_id>", "Update job status with history"),
        ("GET", "/api/jobs/status-history/<job_id>", "Get status history"),
        ("GET", "/api/jobs/status-histories", "Get all status histories"),
        ("POST", "/api/jobs/status-history/bulk", "Bulk status updates"),
        ("GET", "/api/jobs/status-by-status/<status>", "Get jobs by status"),
        ("GET", "/api/jobs/status-summary/enhanced", "Get enhanced summary"),
        ("GET", "/api/jobs/status-timeline/<job_id>", "Get status timeline"),
        ("GET", "/api/jobs/pending-action", "Get jobs pending action"),
        ("POST", "/api/jobs/status-report/export", "Export status report"),
        ("GET", "/api/jobs/status-report/download", "Download status report"),
    ]
    
    print("🌐 Available API Endpoints:")
    print()
    for method, endpoint, description in endpoints:
        print(f"  {method:6} {endpoint:45} - {description}")
    print()
    
    print("💡 Example Usage:")
    print("""
  # Update job status
  curl -X PUT http://localhost:5000/api/jobs/status-history/job_123 \\
    -H "Content-Type: application/json" \\
    -d '{
      "status": "Applied",
      "notes": "Submitted via LinkedIn",
      "user_id": "user123"
    }'
  
  # Get jobs by status
  curl http://localhost:5000/api/jobs/status-by-status/Applied
  
  # Get enhanced summary
  curl http://localhost:5000/api/jobs/status-summary/enhanced
    """)


def run_interactive_demo():
    """Run interactive demo with user prompts"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  TASK 8.2: BACKEND STATUS TRACKING LOGIC - INTERACTIVE DEMO  ".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    input("Press Enter to start the demonstration...")
    print("\n")
    
    # Setup
    storage, job_ids = setup_demo()
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 1
    demo_1_create_status_histories(storage, job_ids)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 2
    demo_2_update_statuses(storage, job_ids)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 3
    demo_3_status_progression(storage, job_ids)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 4
    demo_4_bulk_updates(storage, job_ids)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 5
    demo_5_query_by_status(storage)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 6
    demo_6_enhanced_summary(storage)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 7
    demo_7_pending_actions(storage)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 8
    demo_8_invalid_transitions(storage, job_ids)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 9
    demo_9_export_report(storage)
    input("Press Enter to continue...")
    print("\n")
    
    # Demo 10
    demo_10_api_usage()
    
    # Cleanup prompt
    print("\n")
    print("="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print()
    print(f"Demo data stored in: {DEMO_DIR}/")
    print("You can inspect the following files:")
    print(f"  • {os.path.join(DEMO_DIR, 'jobs.json')} - Job records")
    print(f"  • {os.path.join(DEMO_DIR, 'status_history.json')} - Status histories")
    print(f"  • {os.path.join(DEMO_DIR, 'status_report.json')} - Exported report")
    print()
    
    cleanup = input("Would you like to clean up demo data? (y/n): ")
    if cleanup.lower() == 'y':
        shutil.rmtree(DEMO_DIR)
        print("✅ Demo data cleaned up!")
    else:
        print(f"📁 Demo data preserved in: {DEMO_DIR}/")
    
    print("\n")
    print("Thank you for exploring Task 8.2!")
    print()


if __name__ == "__main__":
    run_interactive_demo()
