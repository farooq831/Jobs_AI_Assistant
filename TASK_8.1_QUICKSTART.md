# Task 8.1: Application Status Model - Quickstart Guide

**Get started with the Application Status Model in 5 minutes!**

---

## Quick Installation

```bash
# Navigate to backend directory
cd backend/

# The module is already available - no additional dependencies needed!
```

---

## 5-Minute Tutorial

### Step 1: Import the Module (30 seconds)

```python
from application_status import (
    ApplicationStatus,
    ApplicationStatusManager
)
```

### Step 2: Create Status Manager (30 seconds)

```python
# Initialize the manager
manager = ApplicationStatusManager()
```

### Step 3: Track Your First Job (1 minute)

```python
# Create a new job tracking
job_id = "google-software-engineer"
manager.create_history(job_id, ApplicationStatus.PENDING)

# Update to Applied
manager.update_status(
    job_id,
    ApplicationStatus.APPLIED,
    notes="Submitted application via referral"
)

# Get current status
history = manager.get_history(job_id)
print(f"Current status: {history.current_status.value}")
# Output: Current status: Applied
```

### Step 4: Progress Through Stages (2 minutes)

```python
# Move to interview
manager.update_status(
    job_id,
    ApplicationStatus.INTERVIEW,
    notes="Phone screen scheduled for next Monday"
)

# Got the offer!
manager.update_status(
    job_id,
    ApplicationStatus.OFFER,
    notes="Received offer: $180k base + equity"
)

# View complete history
from application_status import create_status_summary

summary = create_status_summary(history)
print(f"\n{summary['job_id']}")
print(f"Current: {summary['current_status']}")
print(f"Transitions: {summary['total_transitions']}")
print("\nTimeline:")
for event in summary['timeline']:
    print(f"  {event['date']}: {event['from'] or 'Initial'} → {event['to']}")
```

### Step 5: Track Multiple Jobs (1 minute)

```python
# Track multiple applications
jobs = [
    ("meta-frontend", ApplicationStatus.APPLIED),
    ("amazon-backend", ApplicationStatus.INTERVIEW),
    ("netflix-fullstack", ApplicationStatus.PENDING),
]

for job_id, status in jobs:
    manager.create_history(job_id, status)

# Get statistics
stats = manager.get_statistics()
print(f"\nTotal jobs tracked: {stats['total_jobs']}")
print("Status distribution:")
for status, count in stats['status_counts'].items():
    print(f"  {status}: {count}")
```

---

## Common Operations

### Check Valid Next Statuses

```python
from application_status import get_valid_next_statuses

# What can I do from "Applied"?
next_statuses = get_valid_next_statuses("Applied")
print(f"From Applied, you can move to: {', '.join(next_statuses)}")
# Output: From Applied, you can move to: Interview, Offer, Rejected
```

### Bulk Updates

```python
# Update multiple jobs at once
updates = [
    {"job_id": "job-1", "status": "Interview", "notes": "Tech screen"},
    {"job_id": "job-2", "status": "Offer", "notes": "Offer received!"},
    {"job_id": "job-3", "status": "Rejected", "notes": "Not moving forward"},
]

results = manager.bulk_update(updates)
print(f"Updated {results['successful']} out of {results['total']} jobs")
```

### Filter by Status

```python
# Get all jobs in interview stage
interview_jobs = manager.get_jobs_by_status(ApplicationStatus.INTERVIEW)
print(f"Jobs in interview: {', '.join(interview_jobs)}")

# Get all offers
offers = manager.get_jobs_by_status(ApplicationStatus.OFFER)
print(f"Current offers: {', '.join(offers)}")
```

### Save and Load

```python
# Export to file
manager.export_to_json("my_job_applications.json")

# Load later
new_manager = ApplicationStatusManager()
new_manager.import_from_json("my_job_applications.json")
```

---

## Try the Interactive Demo

```bash
# Run the full interactive demo
python3 demo_application_status.py

# Follow the prompts to explore all features!
```

---

## Run Tests

```bash
# Verify everything works
python3 test_application_status.py

# You should see: 38 tests passed ✓
```

---

## The 5 Statuses

```
┌─────────┐  Submit     ┌─────────┐  Schedule   ┌──────────┐
│ Pending │ ────────→   │ Applied │ ─────────→  │Interview │
└─────────┘             └─────────┘             └──────────┘
                             │                        │
                             │                        │
                             ↓                        ↓
                        ┌─────────┐              ┌────────┐
                        │Rejected │              │ Offer  │
                        └─────────┘              └────────┘
```

**Status Meanings:**
- **Pending** - Haven't applied yet
- **Applied** - Application submitted
- **Interview** - In interview process
- **Offer** - Received job offer
- **Rejected** - Application rejected

---

## Quick Reference

### Valid Transitions

| From      | Can Go To                    |
|-----------|------------------------------|
| Pending   | Applied, Interview, Offer, Rejected |
| Applied   | Interview, Offer, Rejected   |
| Interview | Offer, Rejected              |
| Offer     | Applied (if reapplying)      |
| Rejected  | Applied (if reapplying)      |

### Key Methods

```python
# Manager
manager.create_history(job_id, initial_status)
manager.update_status(job_id, new_status, notes=None)
manager.get_history(job_id)
manager.bulk_update(updates)
manager.get_statistics()
manager.get_jobs_by_status(status)
manager.export_to_json(filepath)
manager.import_from_json(filepath)

# History
history.add_transition(new_status, notes=None)
history.get_transition_count()
history.get_days_in_current_status()
history.to_dict() / from_dict(data)

# Status
ApplicationStatus.from_string(status_str)
ApplicationStatus.get_all_statuses()
ApplicationStatus.is_valid_status(status_str)

# Utilities
validate_status(status_str)
get_valid_next_statuses(current_status)
create_status_summary(history)
```

---

## Real-World Example

```python
#!/usr/bin/env python3
"""Track my job applications"""

from application_status import ApplicationStatus, ApplicationStatusManager

# Setup
manager = ApplicationStatusManager()

# Add my applications
applications = {
    "google-swe": "Googleplex Software Engineer",
    "meta-react": "Meta Frontend Developer",
    "amazon-aws": "Amazon Cloud Engineer",
}

for job_id, title in applications.items():
    manager.create_history(job_id)
    print(f"Tracking: {title}")

# Update statuses as I progress
manager.update_status("google-swe", ApplicationStatus.APPLIED,
                     notes="Applied via referral")
manager.update_status("meta-react", ApplicationStatus.APPLIED,
                     notes="Applied on career site")
manager.update_status("amazon-aws", ApplicationStatus.INTERVIEW,
                     notes="Phone screen scheduled")

# Check my progress
stats = manager.get_statistics()
print(f"\nTracking {stats['total_jobs']} applications")
print(f"Status breakdown: {stats['status_counts']}")

# See who's in interview stage
in_interview = manager.get_jobs_by_status(ApplicationStatus.INTERVIEW)
print(f"\nActive interviews: {len(in_interview)}")

# Save progress
manager.export_to_json("my_applications.json")
print("\n✓ Progress saved!")
```

---

## Need More Help?

- 📖 **Full Documentation:** See `TASK_8.1_README.md`
- 🏗️ **Architecture Details:** See `TASK_8.1_ARCHITECTURE.md`
- ✅ **Completion Report:** See `TASK_8.1_COMPLETION_REPORT.md`
- 🎮 **Try the Demo:** Run `python3 demo_application_status.py`
- 🧪 **Run Tests:** Run `python3 test_application_status.py`

---

## Congratulations! 🎉

You're now ready to track your job applications with the Application Status Model!

**Next Steps:**
1. Start tracking your real applications
2. Explore the demo for advanced features
3. Check out the full documentation for API details

---

*Quickstart Guide - Task 8.1*  
*AI Job Application Assistant - November 2025*
