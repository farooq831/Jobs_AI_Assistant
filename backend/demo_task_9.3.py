"""
Interactive Demo for Task 9.3: Application Tracker Interface
Demonstrates all features of the job application tracker UI
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init()

BASE_URL = 'http://localhost:5000'

# Demo configuration
DEMO_USER_ID = 'demo_user_task_9_3'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{Style.RESET_ALL}\n")


def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_info(text):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {text}{Style.RESET_ALL}")


def create_sample_jobs():
    """Create sample jobs for demo"""
    return [
        {
            'job_id': 'demo_job_001',
            'title': 'Senior Full Stack Developer',
            'company': 'Tech Innovators Inc',
            'location': 'San Francisco, CA (Hybrid)',
            'salary': '$140k-$180k',
            'job_type': 'Full-time',
            'description': 'Build scalable web applications using React, Node.js, and AWS. Lead technical initiatives and mentor junior developers.',
            'link': 'https://example.com/jobs/001',
            'score': 92,
            'highlight': 'red',
            'status': 'pending',
            'scraped_at': datetime.now().isoformat(),
            'resume_tips': [
                'Emphasize your React and Node.js experience',
                'Highlight leadership and mentoring skills',
                'Add specific AWS services you have worked with'
            ]
        },
        {
            'job_id': 'demo_job_002',
            'title': 'Frontend Engineer',
            'company': 'Design Labs',
            'location': 'Remote',
            'salary': '$100k-$130k',
            'job_type': 'Full-time',
            'description': 'Create beautiful user interfaces with React and TypeScript. Work closely with design team.',
            'link': 'https://example.com/jobs/002',
            'score': 78,
            'highlight': 'yellow',
            'status': 'applied',
            'scraped_at': datetime.now().isoformat(),
            'resume_tips': [
                'Showcase your React projects',
                'Include TypeScript proficiency',
                'Mention collaboration with designers'
            ]
        },
        {
            'job_id': 'demo_job_003',
            'title': 'DevOps Engineer',
            'company': 'Cloud Systems Corp',
            'location': 'Austin, TX',
            'salary': '$120k-$150k',
            'job_type': 'Full-time',
            'description': 'Manage CI/CD pipelines, Kubernetes clusters, and cloud infrastructure.',
            'link': 'https://example.com/jobs/003',
            'score': 71,
            'highlight': 'yellow',
            'status': 'interview',
            'scraped_at': datetime.now().isoformat(),
            'resume_tips': [
                'Detail your Kubernetes experience',
                'List CI/CD tools you have used',
                'Mention cloud certifications'
            ]
        },
        {
            'job_id': 'demo_job_004',
            'title': 'Backend Developer',
            'company': 'Data Solutions Ltd',
            'location': 'New York, NY',
            'salary': '$110k-$140k',
            'job_type': 'Full-time',
            'description': 'Build RESTful APIs and optimize database performance using Python and PostgreSQL.',
            'link': 'https://example.com/jobs/004',
            'score': 65,
            'highlight': 'green',
            'status': 'rejected',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'job_id': 'demo_job_005',
            'title': 'Software Engineer',
            'company': 'Startup Ventures',
            'location': 'Seattle, WA',
            'salary': '$95k-$125k',
            'job_type': 'Full-time',
            'description': 'Work on exciting projects in a fast-paced startup environment.',
            'link': 'https://example.com/jobs/005',
            'score': 88,
            'highlight': 'red',
            'status': 'offer',
            'scraped_at': datetime.now().isoformat(),
            'resume_tips': [
                'Emphasize startup experience',
                'Show ability to wear multiple hats',
                'Highlight fast-paced project delivery'
            ]
        },
        {
            'job_id': 'demo_job_006',
            'title': 'Mobile Developer',
            'company': 'App Studio',
            'location': 'Remote',
            'salary': '$105k-$135k',
            'job_type': 'Full-time',
            'description': 'Develop cross-platform mobile applications using React Native.',
            'link': 'https://example.com/jobs/006',
            'score': 55,
            'highlight': 'green',
            'status': 'pending',
            'scraped_at': datetime.now().isoformat()
        }
    ]


def demo_01_store_sample_jobs():
    """Demo 1: Store sample jobs in the system"""
    print_header("Demo 1: Store Sample Jobs")
    
    jobs = create_sample_jobs()
    
    for i, job in enumerate(jobs, 1):
        try:
            response = requests.post(
                f'{BASE_URL}/api/jobs/store',
                json={'job': job, 'user_id': DEMO_USER_ID}
            )
            
            if response.status_code == 200:
                print_success(f"{i}. Stored: {job['title']} at {job['company']}")
                print(f"   Score: {job['score']} | Status: {job['status'].upper()}")
            else:
                print_error(f"Failed to store job: {job['title']}")
        except Exception as e:
            print_error(f"Error: {str(e)}")
    
    print_info(f"\nTotal jobs stored: {len(jobs)}")
    input("\nPress Enter to continue...")


def demo_02_fetch_dashboard_data():
    """Demo 2: Fetch jobs for dashboard display"""
    print_header("Demo 2: Fetch Dashboard Data")
    
    try:
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            
            print_success(f"Fetched {len(jobs)} jobs from backend")
            print("\n" + "─" * 70)
            
            for i, job in enumerate(jobs, 1):
                highlight_color = {
                    'red': Fore.RED,
                    'yellow': Fore.YELLOW,
                    'green': Fore.GREEN,
                    'white': Fore.WHITE
                }.get(job.get('highlight', 'white').lower(), Fore.WHITE)
                
                print(f"\n{highlight_color}[{i}] {job.get('title', 'N/A')}{Style.RESET_ALL}")
                print(f"    Company: {job.get('company', 'N/A')}")
                print(f"    Location: {job.get('location', 'N/A')}")
                print(f"    Score: {job.get('score', 0)} | Status: {job.get('status', 'pending').upper()}")
                print(f"    Salary: {job.get('salary', 'Not disclosed')}")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_03_calculate_statistics():
    """Demo 3: Calculate dashboard statistics"""
    print_header("Demo 3: Dashboard Statistics")
    
    try:
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            jobs = response.json().get('jobs', [])
            
            stats = {
                'total': len(jobs),
                'red': sum(1 for j in jobs if j.get('highlight', '').lower() == 'red'),
                'yellow': sum(1 for j in jobs if j.get('highlight', '').lower() == 'yellow'),
                'green': sum(1 for j in jobs if j.get('highlight', '').lower() == 'green'),
                'white': sum(1 for j in jobs if j.get('highlight', '').lower() == 'white'),
                'pending': sum(1 for j in jobs if j.get('status', '').lower() == 'pending'),
                'applied': sum(1 for j in jobs if j.get('status', '').lower() == 'applied'),
                'interview': sum(1 for j in jobs if j.get('status', '').lower() == 'interview'),
                'offer': sum(1 for j in jobs if j.get('status', '').lower() == 'offer'),
                'rejected': sum(1 for j in jobs if j.get('status', '').lower() == 'rejected')
            }
            
            print_success("Statistics calculated:")
            print(f"\n{Fore.CYAN}Match Quality:{Style.RESET_ALL}")
            print(f"  {Fore.RED}● Excellent (Red):{Style.RESET_ALL}    {stats['red']:3d}")
            print(f"  {Fore.YELLOW}● Good (Yellow):{Style.RESET_ALL}      {stats['yellow']:3d}")
            print(f"  {Fore.GREEN}● Fair (Green):{Style.RESET_ALL}       {stats['green']:3d}")
            print(f"  {Fore.WHITE}● Poor (White):{Style.RESET_ALL}       {stats['white']:3d}")
            
            print(f"\n{Fore.CYAN}Application Status:{Style.RESET_ALL}")
            print(f"  ⏳ Pending:    {stats['pending']:3d}")
            print(f"  ✉️  Applied:    {stats['applied']:3d}")
            print(f"  📅 Interview:  {stats['interview']:3d}")
            print(f"  🎉 Offer:      {stats['offer']:3d}")
            print(f"  ❌ Rejected:   {stats['rejected']:3d}")
            
            print(f"\n{Fore.CYAN}Total Jobs:{Style.RESET_ALL} {stats['total']}")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_04_filter_by_highlight():
    """Demo 4: Filter jobs by match quality (highlight)"""
    print_header("Demo 4: Filter by Match Quality")
    
    highlights = ['red', 'yellow', 'green']
    
    try:
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            all_jobs = response.json().get('jobs', [])
            
            for highlight in highlights:
                filtered = [j for j in all_jobs if j.get('highlight', '').lower() == highlight]
                
                color = {
                    'red': Fore.RED,
                    'yellow': Fore.YELLOW,
                    'green': Fore.GREEN
                }.get(highlight, Fore.WHITE)
                
                label = {
                    'red': 'Excellent Matches',
                    'yellow': 'Good Matches',
                    'green': 'Fair Matches'
                }.get(highlight, 'Matches')
                
                print(f"\n{color}{'─'*50}")
                print(f"{label} ({len(filtered)} jobs)")
                print(f"{'─'*50}{Style.RESET_ALL}")
                
                if filtered:
                    for job in filtered:
                        print(f"  • {job.get('title', 'N/A')} - {job.get('company', 'N/A')}")
                        print(f"    Score: {job.get('score', 0)} | Status: {job.get('status', 'pending').upper()}")
                else:
                    print("  No jobs found")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_05_filter_by_status():
    """Demo 5: Filter jobs by application status"""
    print_header("Demo 5: Filter by Application Status")
    
    statuses = ['pending', 'applied', 'interview', 'offer', 'rejected']
    
    try:
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            all_jobs = response.json().get('jobs', [])
            
            for status in statuses:
                filtered = [j for j in all_jobs if j.get('status', '').lower() == status]
                
                icon = {
                    'pending': '⏳',
                    'applied': '✉️',
                    'interview': '📅',
                    'offer': '🎉',
                    'rejected': '❌'
                }.get(status, '•')
                
                print(f"\n{Fore.CYAN}{icon} {status.upper()} ({len(filtered)} jobs){Style.RESET_ALL}")
                print("─" * 50)
                
                if filtered:
                    for job in filtered:
                        print(f"  • {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                        print(f"    Score: {job.get('score', 0)} | {job.get('location', 'N/A')}")
                else:
                    print("  No jobs found")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_06_sort_jobs():
    """Demo 6: Sort jobs by different criteria"""
    print_header("Demo 6: Sort Jobs")
    
    try:
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            jobs = response.json().get('jobs', [])
            
            # Sort by score (descending)
            print(f"\n{Fore.CYAN}Sorted by Score (Highest First):{Style.RESET_ALL}")
            print("─" * 70)
            sorted_by_score = sorted(jobs, key=lambda x: x.get('score', 0), reverse=True)
            for i, job in enumerate(sorted_by_score[:5], 1):
                print(f"{i}. {job.get('title', 'N/A')} - Score: {job.get('score', 0)}")
            
            # Sort by title (ascending)
            print(f"\n{Fore.CYAN}Sorted by Title (A-Z):{Style.RESET_ALL}")
            print("─" * 70)
            sorted_by_title = sorted(jobs, key=lambda x: x.get('title', '').lower())
            for i, job in enumerate(sorted_by_title[:5], 1):
                print(f"{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            
            # Sort by company (ascending)
            print(f"\n{Fore.CYAN}Sorted by Company (A-Z):{Style.RESET_ALL}")
            print("─" * 70)
            sorted_by_company = sorted(jobs, key=lambda x: x.get('company', '').lower())
            for i, job in enumerate(sorted_by_company[:5], 1):
                print(f"{i}. {job.get('company', 'N/A')} - {job.get('title', 'N/A')}")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_07_search_jobs():
    """Demo 7: Search jobs by keyword"""
    print_header("Demo 7: Search Jobs")
    
    search_terms = ['engineer', 'developer', 'remote', 'tech']
    
    try:
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            all_jobs = response.json().get('jobs', [])
            
            for term in search_terms:
                results = [
                    job for job in all_jobs
                    if term.lower() in job.get('title', '').lower()
                    or term.lower() in job.get('company', '').lower()
                    or term.lower() in job.get('location', '').lower()
                ]
                
                print(f"\n{Fore.YELLOW}Search: '{term}' ({len(results)} results){Style.RESET_ALL}")
                print("─" * 70)
                
                if results:
                    for job in results[:3]:
                        print(f"  • {job.get('title', 'N/A')}")
                        print(f"    {job.get('company', 'N/A')} - {job.get('location', 'N/A')}")
                else:
                    print("  No matches found")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_08_update_status():
    """Demo 8: Update job application status"""
    print_header("Demo 8: Update Application Status")
    
    try:
        # Get a job to update
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            jobs = response.json().get('jobs', [])
            
            if jobs:
                # Find a pending job
                pending_job = next((j for j in jobs if j.get('status', '').lower() == 'pending'), jobs[0])
                
                print_info(f"Updating status for: {pending_job.get('title', 'N/A')}")
                print(f"Current status: {pending_job.get('status', 'pending').upper()}")
                
                # Update to 'applied'
                update_data = {
                    'status': 'applied',
                    'notes': 'Applied through company website on ' + datetime.now().strftime('%Y-%m-%d'),
                    'user_id': DEMO_USER_ID
                }
                
                update_response = requests.put(
                    f"{BASE_URL}/api/jobs/{pending_job['job_id']}/status",
                    json=update_data
                )
                
                if update_response.status_code == 200:
                    result = update_response.json()
                    print_success(f"Status updated to: {result.get('status', 'applied').upper()}")
                    print(f"Notes: {update_data['notes']}")
                else:
                    print_error("Failed to update status")
            else:
                print_error("No jobs available")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_09_view_status_history():
    """Demo 9: View status history for a job"""
    print_header("Demo 9: View Status History")
    
    try:
        # Get jobs
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            jobs = response.json().get('jobs', [])
            
            if jobs:
                # Select a job (prefer one with 'interview' status)
                job = next((j for j in jobs if j.get('status', '').lower() == 'interview'), jobs[0])
                
                print_info(f"Viewing history for: {job.get('title', 'N/A')}")
                print(f"Company: {job.get('company', 'N/A')}")
                
                # Fetch history
                history_response = requests.get(f"{BASE_URL}/api/jobs/{job['job_id']}/status/history")
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    history = history_data.get('history', [])
                    
                    if history:
                        print(f"\n{Fore.CYAN}Status History ({len(history)} entries):{Style.RESET_ALL}")
                        print("─" * 70)
                        
                        for i, entry in enumerate(history, 1):
                            status = entry.get('status', 'unknown')
                            timestamp = entry.get('timestamp', 'N/A')
                            notes = entry.get('notes', '')
                            
                            icon = {
                                'pending': '⏳',
                                'applied': '✉️',
                                'interview': '📅',
                                'offer': '🎉',
                                'rejected': '❌'
                            }.get(status.lower(), '•')
                            
                            print(f"\n{icon} {i}. {status.upper()}")
                            print(f"   {timestamp}")
                            if notes:
                                print(f"   Notes: {notes}")
                    else:
                        print_info("No status history available")
                else:
                    print_error("Failed to fetch status history")
            else:
                print_error("No jobs available")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def demo_10_complete_workflow():
    """Demo 10: Complete application tracking workflow"""
    print_header("Demo 10: Complete Workflow")
    
    try:
        # 1. Fetch jobs
        print(f"{Fore.CYAN}Step 1: Fetching jobs...{Style.RESET_ALL}")
        response = requests.get(f'{BASE_URL}/api/jobs/stored/{DEMO_USER_ID}')
        
        if response.status_code == 200:
            jobs = response.json().get('jobs', [])
            print_success(f"Found {len(jobs)} jobs")
            
            # 2. Filter excellent matches
            print(f"\n{Fore.CYAN}Step 2: Filtering excellent matches (red)...{Style.RESET_ALL}")
            excellent = [j for j in jobs if j.get('highlight', '').lower() == 'red']
            print_success(f"Found {len(excellent)} excellent matches")
            
            if excellent:
                job = excellent[0]
                print(f"  → {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                
                # 3. Update status to 'applied'
                print(f"\n{Fore.CYAN}Step 3: Applying to job...{Style.RESET_ALL}")
                update_data = {
                    'status': 'applied',
                    'notes': 'Great match! Submitted application with tailored resume.',
                    'user_id': DEMO_USER_ID
                }
                
                update_response = requests.put(
                    f"{BASE_URL}/api/jobs/{job['job_id']}/status",
                    json=update_data
                )
                
                if update_response.status_code == 200:
                    print_success("Application status updated to APPLIED")
                
                time.sleep(1)
                
                # 4. Update to interview
                print(f"\n{Fore.CYAN}Step 4: Interview scheduled...{Style.RESET_ALL}")
                update_data['status'] = 'interview'
                update_data['notes'] = 'Phone screening scheduled for next Monday at 2 PM.'
                
                update_response = requests.put(
                    f"{BASE_URL}/api/jobs/{job['job_id']}/status",
                    json=update_data
                )
                
                if update_response.status_code == 200:
                    print_success("Status updated to INTERVIEW")
                
                time.sleep(1)
                
                # 5. View history
                print(f"\n{Fore.CYAN}Step 5: Viewing application history...{Style.RESET_ALL}")
                history_response = requests.get(f"{BASE_URL}/api/jobs/{job['job_id']}/status/history")
                
                if history_response.status_code == 200:
                    history = history_response.json().get('history', [])
                    print_success(f"History contains {len(history)} status updates")
                    
                    for entry in history[-3:]:
                        status = entry.get('status', 'unknown')
                        print(f"  • {status.upper()} - {entry.get('notes', 'No notes')[:50]}")
                
                # 6. Summary
                print(f"\n{Fore.GREEN}{'─'*70}")
                print("Workflow Complete!")
                print(f"{'─'*70}{Style.RESET_ALL}")
                print(f"Job: {job.get('title', 'N/A')}")
                print(f"Company: {job.get('company', 'N/A')}")
                print(f"Match Score: {job.get('score', 0)}")
                print(f"Current Status: INTERVIEW")
                print(f"Total Status Updates: {len(history)}")
        else:
            print_error("Failed to fetch jobs")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")


def main_menu():
    """Display main menu and handle demo selection"""
    demos = [
        ("Store Sample Jobs", demo_01_store_sample_jobs),
        ("Fetch Dashboard Data", demo_02_fetch_dashboard_data),
        ("Calculate Statistics", demo_03_calculate_statistics),
        ("Filter by Match Quality", demo_04_filter_by_highlight),
        ("Filter by Status", demo_05_filter_by_status),
        ("Sort Jobs", demo_06_sort_jobs),
        ("Search Jobs", demo_07_search_jobs),
        ("Update Status", demo_08_update_status),
        ("View Status History", demo_09_view_status_history),
        ("Complete Workflow", demo_10_complete_workflow)
    ]
    
    while True:
        print_header("Task 9.3: Application Tracker Interface Demo")
        
        print(f"{Fore.CYAN}Available Demos:{Style.RESET_ALL}\n")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  {i:2d}. {name}")
        print(f"   0. Run All Demos")
        print(f"  99. Exit")
        
        choice = input(f"\n{Fore.YELLOW}Select demo (0-{len(demos)} or 99): {Style.RESET_ALL}")
        
        if choice == '99':
            print(f"\n{Fore.GREEN}Thank you for using the demo!{Style.RESET_ALL}\n")
            break
        elif choice == '0':
            for name, demo_func in demos:
                demo_func()
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            demos[int(choice) - 1][1]()
        else:
            print_error("Invalid choice. Please try again.")
            time.sleep(1)


if __name__ == '__main__':
    print(f"{Fore.CYAN}")
    print("=" * 70)
    print("Task 9.3: Application Tracker Interface - Interactive Demo")
    print("=" * 70)
    print(f"{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Prerequisites:{Style.RESET_ALL}")
    print("  • Backend server running on http://localhost:5000")
    print("  • Frontend can be tested separately")
    print("\nThis demo showcases:")
    print("  • Job listing dashboard")
    print("  • Filtering and sorting")
    print("  • Status updates")
    print("  • Status history tracking")
    print("  • Complete application workflow")
    
    input(f"\n{Fore.GREEN}Press Enter to start...{Style.RESET_ALL}")
    
    main_menu()
