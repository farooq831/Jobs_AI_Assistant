"""
Interactive Demo for Application Status Model

This demo showcases all features of the application status tracking system:
- Creating and managing status histories
- Valid and invalid transitions
- Status history tracking
- Bulk operations
- Statistics and reporting
- Import/Export functionality

Author: AI Job Application Assistant
Date: November 2025
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from application_status import (
    ApplicationStatus,
    StatusTransition,
    StatusHistory,
    ApplicationStatusManager,
    validate_status,
    get_valid_next_statuses,
    create_status_summary
)


def print_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_subheader(title):
    """Print a formatted subsection header"""
    print(f"\n{title}")
    print("-" * 70)


def demo_basic_usage():
    """Demonstrate basic status model usage"""
    print_header("DEMO 1: Basic Usage - Application Status Enum")
    
    print("1.1 Available Statuses:")
    statuses = ApplicationStatus.get_all_statuses()
    print(f"    {', '.join(statuses)}")
    
    print("\n1.2 Creating Status from String:")
    test_strings = ["Applied", "interview", "OFFER"]
    for status_str in test_strings:
        status = ApplicationStatus.from_string(status_str)
        print(f"    '{status_str}' → {status}")
    
    print("\n1.3 Status Validation:")
    test_cases = ["Applied", "Invalid", "Pending", "Submitted"]
    for test in test_cases:
        is_valid, error = validate_status(test)
        if is_valid:
            print(f"    ✓ '{test}' is valid")
        else:
            print(f"    ✗ '{test}' is invalid: {error}")
    
    print("\n1.4 Valid Next Statuses:")
    for status_str in ["Pending", "Applied", "Interview"]:
        valid_next = get_valid_next_statuses(status_str)
        print(f"    From '{status_str}': {', '.join(valid_next)}")


def demo_status_transitions():
    """Demonstrate status transitions"""
    print_header("DEMO 2: Status Transitions")
    
    print("2.1 Creating Transitions:")
    
    print("\n    Valid Transitions:")
    valid_cases = [
        (ApplicationStatus.PENDING, ApplicationStatus.APPLIED, "Submitted application"),
        (ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW, "Scheduled phone screen"),
        (ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER, "Received offer letter")
    ]
    
    for from_status, to_status, notes in valid_cases:
        transition = StatusTransition(from_status=from_status, to_status=to_status, notes=notes)
        is_valid = "✓" if transition.is_valid_transition() else "✗"
        print(f"    {is_valid} {from_status.value} → {to_status.value}: {notes}")
    
    print("\n    Invalid Transitions:")
    invalid_cases = [
        (ApplicationStatus.APPLIED, ApplicationStatus.PENDING),
        (ApplicationStatus.INTERVIEW, ApplicationStatus.APPLIED),
        (ApplicationStatus.OFFER, ApplicationStatus.PENDING)
    ]
    
    for from_status, to_status in invalid_cases:
        transition = StatusTransition(from_status=from_status, to_status=to_status)
        is_valid = "✓" if transition.is_valid_transition() else "✗"
        print(f"    {is_valid} {from_status.value} → {to_status.value} (blocked)")


def demo_status_history():
    """Demonstrate status history management"""
    print_header("DEMO 3: Status History Management")
    
    print("3.1 Creating Status History:")
    history = StatusHistory(job_id="demo_job_123")
    print(f"    Job ID: {history.job_id}")
    print(f"    Initial Status: {history.current_status.value}")
    print(f"    Created: {history.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n3.2 Adding Status Transitions:")
    transitions_to_add = [
        (ApplicationStatus.APPLIED, "Submitted application online", "user_123"),
        (ApplicationStatus.INTERVIEW, "Completed phone screen", "user_123"),
        (ApplicationStatus.OFFER, "Received offer letter", "user_123")
    ]
    
    for status, notes, user_id in transitions_to_add:
        success = history.add_transition(status, notes=notes, user_id=user_id)
        if success:
            print(f"    ✓ Transitioned to {status.value}: {notes}")
        else:
            print(f"    ✗ Failed to transition to {status.value}")
    
    print("\n3.3 Status History Summary:")
    print(f"    Current Status: {history.current_status.value}")
    print(f"    Total Transitions: {history.get_transition_count()}")
    print(f"    Days in Current Status: {history.get_days_in_current_status()}")
    
    print("\n3.4 Timeline:")
    for i, transition in enumerate(history.transitions, 1):
        from_status = transition.from_status.value if transition.from_status else "None"
        print(f"    {i}. {from_status} → {transition.to_status.value}")
        print(f"       Time: {transition.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"       Notes: {transition.notes}")


def demo_status_manager():
    """Demonstrate ApplicationStatusManager"""
    print_header("DEMO 4: Application Status Manager")
    
    manager = ApplicationStatusManager()
    
    print("4.1 Creating Multiple Job Histories:")
    jobs = [
        ("job_001", "Software Engineer at TechCorp"),
        ("job_002", "Data Scientist at DataInc"),
        ("job_003", "Product Manager at StartupXYZ"),
        ("job_004", "DevOps Engineer at CloudCo"),
        ("job_005", "Full Stack Developer at WebDev")
    ]
    
    for job_id, description in jobs:
        manager.create_history(job_id)
        print(f"    ✓ Created history for {job_id}: {description}")
    
    print("\n4.2 Updating Job Statuses:")
    updates = [
        ("job_001", ApplicationStatus.APPLIED, "Application submitted"),
        ("job_001", ApplicationStatus.INTERVIEW, "Phone screen completed"),
        ("job_002", ApplicationStatus.APPLIED, "Applied via referral"),
        ("job_003", ApplicationStatus.APPLIED, "Submitted application"),
        ("job_003", ApplicationStatus.INTERVIEW, "Technical interview scheduled"),
        ("job_003", ApplicationStatus.OFFER, "Offer received!"),
        ("job_004", ApplicationStatus.APPLIED, "Application submitted"),
        ("job_004", ApplicationStatus.REJECTED, "Application rejected"),
        ("job_005", ApplicationStatus.APPLIED, "Application in progress")
    ]
    
    for job_id, status, notes in updates:
        manager.update_status(job_id, status, notes=notes)
        print(f"    → {job_id}: {status.value} - {notes}")
    
    print("\n4.3 Jobs by Status:")
    for status in ApplicationStatus:
        jobs_with_status = manager.get_jobs_by_status(status)
        if jobs_with_status:
            print(f"    {status.value}: {', '.join(jobs_with_status)}")
    
    print("\n4.4 Overall Statistics:")
    stats = manager.get_statistics()
    print(f"    Total Jobs: {stats['total_jobs']}")
    print(f"    Status Distribution:")
    for status, count in stats['status_counts'].items():
        print(f"      - {status}: {count}")
    print(f"    Average Transitions: {stats['average_transitions']}")
    print(f"    Avg Days in Current Status: {stats['average_days_in_current_status']}")
    
    return manager


def demo_bulk_operations(manager):
    """Demonstrate bulk operations"""
    print_header("DEMO 5: Bulk Operations")
    
    print("5.1 Bulk Status Updates:")
    bulk_updates = [
        {"job_id": "job_006", "status": "Applied", "notes": "New application"},
        {"job_id": "job_007", "status": "Applied", "notes": "Another application"},
        {"job_id": "job_001", "status": "Offer", "notes": "Received offer!"},
        {"job_id": "job_002", "status": "Interview", "notes": "Interview scheduled"}
    ]
    
    print(f"    Performing {len(bulk_updates)} updates...")
    results = manager.bulk_update(bulk_updates)
    
    print(f"\n    Results:")
    print(f"      Total: {results['total']}")
    print(f"      ✓ Successful: {results['successful']}")
    print(f"      ✗ Failed: {results['failed']}")
    
    if results['errors']:
        print(f"\n    Errors:")
        for error in results['errors']:
            print(f"      - Job {error['job_id']}: {error['error']}")


def demo_export_import(manager):
    """Demonstrate export and import functionality"""
    print_header("DEMO 6: Export and Import")
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    export_file = os.path.join(temp_dir, "status_histories_demo.json")
    
    print(f"6.1 Exporting to JSON:")
    print(f"    File: {export_file}")
    
    success = manager.export_to_json(export_file)
    if success:
        print(f"    ✓ Successfully exported {len(manager.histories)} histories")
        
        # Show file size
        file_size = os.path.getsize(export_file)
        print(f"    File size: {file_size} bytes")
    
    print("\n6.2 JSON Structure Preview:")
    with open(export_file, 'r') as f:
        data = json.load(f)
    
    print(f"    Exported at: {data['exported_at']}")
    print(f"    Total jobs: {data['total_jobs']}")
    print(f"    Sample history (first job):")
    
    if data['histories']:
        sample = data['histories'][0]
        print(f"      Job ID: {sample['job_id']}")
        print(f"      Current Status: {sample['current_status']}")
        print(f"      Transitions: {len(sample['transitions'])}")
    
    print("\n6.3 Importing to New Manager:")
    new_manager = ApplicationStatusManager()
    success = new_manager.import_from_json(export_file)
    
    if success:
        print(f"    ✓ Successfully imported {len(new_manager.histories)} histories")
        print(f"    Verification: {len(manager.histories)} == {len(new_manager.histories)}")
    
    # Cleanup
    if os.path.exists(export_file):
        os.remove(export_file)
        print(f"\n    Cleaned up temporary file")


def demo_advanced_features():
    """Demonstrate advanced features"""
    print_header("DEMO 7: Advanced Features")
    
    print("7.1 Status Summary:")
    history = StatusHistory(job_id="advanced_demo_job")
    history.add_transition(ApplicationStatus.APPLIED, notes="Applied on career site")
    history.add_transition(ApplicationStatus.INTERVIEW, notes="Technical interview")
    history.add_transition(ApplicationStatus.OFFER, notes="Offer received")
    
    summary = create_status_summary(history)
    print(f"    Job ID: {summary['job_id']}")
    print(f"    Current Status: {summary['current_status']}")
    print(f"    Total Transitions: {summary['total_transitions']}")
    print(f"    Days in Current Status: {summary['days_in_current_status']}")
    
    print("\n    Timeline:")
    for event in summary['timeline']:
        from_status = event['from'] if event['from'] else "Initial"
        print(f"      {from_status} → {event['to']} ({event['date']})")
        if event['notes']:
            print(f"        Note: {event['notes']}")
    
    print("\n7.2 Invalid Transition Handling:")
    test_history = StatusHistory(job_id="test_job")
    test_history.add_transition(ApplicationStatus.APPLIED)
    
    print(f"    Current Status: {test_history.current_status.value}")
    print(f"    Attempting invalid transition: Applied → Pending")
    
    success = test_history.add_transition(ApplicationStatus.PENDING)
    if not success:
        print(f"    ✗ Transition blocked (as expected)")
        print(f"    Current Status remains: {test_history.current_status.value}")
    
    print("\n7.3 Forced Transition (without validation):")
    print(f"    Forcing: Applied → Pending")
    success = test_history.add_transition(ApplicationStatus.PENDING, validate=False)
    if success:
        print(f"    ✓ Transition forced")
        print(f"    New Status: {test_history.current_status.value}")


def demo_real_world_scenario():
    """Demonstrate real-world job application tracking scenario"""
    print_header("DEMO 8: Real-World Scenario")
    
    print("Scenario: Tracking Multiple Job Applications Over Time\n")
    
    manager = ApplicationStatusManager()
    
    # Week 1: Submit applications
    print("Week 1 - Submitting Applications:")
    week1_jobs = [
        ("google_swe", "Google - Software Engineer"),
        ("meta_ml", "Meta - Machine Learning Engineer"),
        ("amazon_dev", "Amazon - Backend Developer"),
    ]
    
    for job_id, title in week1_jobs:
        manager.create_history(job_id)
        manager.update_status(job_id, ApplicationStatus.APPLIED, notes="Application submitted")
        print(f"  ✓ Applied to {title}")
    
    # Week 2: Some interviews
    print("\nWeek 2 - Interview Invitations:")
    manager.update_status("google_swe", ApplicationStatus.INTERVIEW, notes="Phone screen scheduled")
    manager.update_status("meta_ml", ApplicationStatus.INTERVIEW, notes="Technical interview")
    print("  ✓ Google - Phone screen scheduled")
    print("  ✓ Meta - Technical interview scheduled")
    
    # Week 3: More progress
    print("\nWeek 3 - Progress:")
    manager.update_status("google_swe", ApplicationStatus.OFFER, notes="Offer received!")
    manager.update_status("amazon_dev", ApplicationStatus.REJECTED, notes="Position filled")
    print("  ✓ Google - Offer received!")
    print("  ✗ Amazon - Application rejected")
    
    # Add new applications
    print("\nWeek 3 - New Applications:")
    manager.create_history("netflix_eng", ApplicationStatus.PENDING)
    manager.update_status("netflix_eng", ApplicationStatus.APPLIED, notes="Applied via referral")
    print("  ✓ Applied to Netflix - Software Engineer (via referral)")
    
    # Final status
    print("\n" + "-" * 70)
    print("Current Application Status Summary:")
    print("-" * 70)
    
    stats = manager.get_statistics()
    print(f"\nTotal Applications: {stats['total_jobs']}")
    print("\nStatus Breakdown:")
    for status, count in stats['status_counts'].items():
        print(f"  {status}: {count}")
    
    print("\nDetailed Status by Job:")
    for job_id, history in manager.histories.items():
        summary = create_status_summary(history)
        print(f"\n  {job_id}:")
        print(f"    Current: {summary['current_status']}")
        print(f"    Days in status: {summary['days_in_current_status']}")
        print(f"    Transitions: {summary['total_transitions']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  APPLICATION STATUS MODEL - INTERACTIVE DEMO")
    print("  AI Job Application Assistant")
    print("  November 2025")
    print("=" * 70)
    
    try:
        # Run demos
        demo_basic_usage()
        demo_status_transitions()
        demo_status_history()
        manager = demo_status_manager()
        demo_bulk_operations(manager)
        demo_export_import(manager)
        demo_advanced_features()
        demo_real_world_scenario()
        
        # Completion message
        print("\n" + "=" * 70)
        print("  DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nKey Features Demonstrated:")
        print("  ✓ Application status enum and validation")
        print("  ✓ Status transition rules and validation")
        print("  ✓ Status history tracking and management")
        print("  ✓ Multi-job status management")
        print("  ✓ Bulk operations")
        print("  ✓ Export/Import functionality")
        print("  ✓ Statistics and reporting")
        print("  ✓ Real-world usage scenarios")
        print("\nFor more information, see:")
        print("  - backend/application_status.py (module)")
        print("  - backend/test_application_status.py (tests)")
        print("  - TASK_8.1_README.md (documentation)")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
