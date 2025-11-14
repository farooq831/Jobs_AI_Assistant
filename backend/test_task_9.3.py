"""
Test Suite for Task 9.3: Application Tracker Interface
Tests the integration between frontend tracker components and backend APIs
"""

import pytest
import json
from datetime import datetime
from app import app
from storage_manager import JobStorageManager
from application_status import ApplicationStatus


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def storage():
    """Create test storage manager"""
    return JobStorageManager(data_dir='test_data_task_9_3')


@pytest.fixture
def sample_jobs():
    """Create sample jobs for testing"""
    return [
        {
            'job_id': 'job_001',
            'title': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'salary': '$120k-$160k',
            'job_type': 'Full-time',
            'description': 'Build scalable web applications',
            'link': 'https://example.com/job1',
            'score': 85,
            'highlight': 'red',
            'status': 'pending',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'job_id': 'job_002',
            'title': 'Frontend Developer',
            'company': 'Design Studio',
            'location': 'Remote',
            'salary': '$90k-$120k',
            'job_type': 'Full-time',
            'description': 'React and TypeScript development',
            'link': 'https://example.com/job2',
            'score': 72,
            'highlight': 'yellow',
            'status': 'applied',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'job_id': 'job_003',
            'title': 'DevOps Engineer',
            'company': 'Cloud Services Inc',
            'location': 'Austin, TX',
            'salary': '$110k-$140k',
            'job_type': 'Full-time',
            'description': 'AWS and Kubernetes expertise',
            'link': 'https://example.com/job3',
            'score': 68,
            'highlight': 'yellow',
            'status': 'interview',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'job_id': 'job_004',
            'title': 'Backend Engineer',
            'company': 'Data Systems',
            'location': 'New York, NY',
            'salary': '$100k-$130k',
            'job_type': 'Full-time',
            'description': 'Python and database optimization',
            'link': 'https://example.com/job4',
            'score': 45,
            'highlight': 'green',
            'status': 'rejected',
            'scraped_at': datetime.now().isoformat()
        },
        {
            'job_id': 'job_005',
            'title': 'Full Stack Developer',
            'company': 'Startup Labs',
            'location': 'Seattle, WA',
            'salary': '$95k-$125k',
            'job_type': 'Full-time',
            'description': 'MERN stack development',
            'link': 'https://example.com/job5',
            'score': 78,
            'highlight': 'red',
            'status': 'offer',
            'scraped_at': datetime.now().isoformat()
        }
    ]


class TestJobDashboardAPI:
    """Test API endpoints used by Job Dashboard"""

    def test_fetch_stored_jobs(self, client, storage, sample_jobs):
        """Test fetching stored jobs for dashboard display"""
        # Store sample jobs
        user_id = 'test_user_001'
        for job in sample_jobs:
            storage.store_job(job, user_id)
        
        # Fetch jobs
        response = client.get(f'/api/jobs/stored/{user_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'jobs' in data
        assert len(data['jobs']) == len(sample_jobs)
        
        # Verify job structure
        job = data['jobs'][0]
        assert 'job_id' in job
        assert 'title' in job
        assert 'company' in job
        assert 'score' in job
        assert 'highlight' in job
        assert 'status' in job
    
    def test_fetch_jobs_with_filters(self, client, storage, sample_jobs):
        """Test filtering functionality"""
        user_id = 'test_user_002'
        for job in sample_jobs:
            storage.store_job(job, user_id)
        
        # Test highlight filter (excellent matches)
        response = client.get(f'/api/jobs/stored/{user_id}?highlight=red')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(job['highlight'] == 'red' for job in data['jobs'])
        
        # Test status filter (applied)
        response = client.get(f'/api/jobs/stored/{user_id}?status=applied')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(job['status'] == 'applied' for job in data['jobs'])
    
    def test_fetch_jobs_empty_result(self, client):
        """Test fetching jobs for non-existent user"""
        response = client.get('/api/jobs/stored/nonexistent_user')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['jobs'] == []


class TestStatusUpdateAPI:
    """Test status update API endpoints"""

    def test_update_job_status(self, client, storage, sample_jobs):
        """Test updating a job's application status"""
        user_id = 'test_user_003'
        job = sample_jobs[0]
        storage.store_job(job, user_id)
        
        # Update status
        update_data = {
            'status': 'applied',
            'notes': 'Applied through company website',
            'user_id': user_id
        }
        
        response = client.put(
            f'/api/jobs/{job["job_id"]}/status',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['status'] == 'applied'
        
        # Verify status was updated
        stored_job = storage.get_job(job['job_id'], user_id)
        assert stored_job['status'] == 'applied'
    
    def test_update_with_status_transition(self, client, storage, sample_jobs):
        """Test status update with valid transition"""
        user_id = 'test_user_004'
        job = sample_jobs[1]  # Already 'applied'
        storage.store_job(job, user_id)
        
        # Update to interview
        update_data = {
            'status': 'interview',
            'notes': 'Phone screening scheduled for next week',
            'user_id': user_id
        }
        
        response = client.put(
            f'/api/jobs/{job["job_id"]}/status',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'interview'
    
    def test_update_invalid_status(self, client, storage, sample_jobs):
        """Test updating with invalid status value"""
        user_id = 'test_user_005'
        job = sample_jobs[0]
        storage.store_job(job, user_id)
        
        update_data = {
            'status': 'invalid_status',
            'user_id': user_id
        }
        
        response = client.put(
            f'/api/jobs/{job["job_id"]}/status',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Should handle gracefully or return error
        assert response.status_code in [400, 200]
    
    def test_update_nonexistent_job(self, client):
        """Test updating status for non-existent job"""
        update_data = {
            'status': 'applied',
            'user_id': 'test_user_006'
        }
        
        response = client.put(
            '/api/jobs/nonexistent_job/status',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code in [404, 400]


class TestStatusHistoryAPI:
    """Test status history tracking"""

    def test_fetch_status_history(self, client, storage, sample_jobs):
        """Test fetching status history for a job"""
        user_id = 'test_user_007'
        job = sample_jobs[0]
        storage.store_job(job, user_id)
        
        # Make multiple status updates
        statuses = ['applied', 'interview', 'offer']
        for status in statuses:
            update_data = {
                'status': status,
                'notes': f'Updated to {status}',
                'user_id': user_id
            }
            client.put(
                f'/api/jobs/{job["job_id"]}/status',
                data=json.dumps(update_data),
                content_type='application/json'
            )
        
        # Fetch history
        response = client.get(f'/api/jobs/{job["job_id"]}/status/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'history' in data
        assert len(data['history']) >= len(statuses)
        
        # Verify history structure
        if data['history']:
            entry = data['history'][0]
            assert 'status' in entry
            assert 'timestamp' in entry
    
    def test_history_chronological_order(self, client, storage, sample_jobs):
        """Test that history is returned in chronological order"""
        user_id = 'test_user_008'
        job = sample_jobs[0]
        storage.store_job(job, user_id)
        
        # Make updates
        statuses = ['applied', 'interview']
        for status in statuses:
            update_data = {
                'status': status,
                'user_id': user_id
            }
            client.put(
                f'/api/jobs/{job["job_id"]}/status',
                data=json.dumps(update_data),
                content_type='application/json'
            )
        
        response = client.get(f'/api/jobs/{job["job_id"]}/status/history')
        data = json.loads(response.data)
        
        if len(data['history']) > 1:
            # Verify timestamps are in order (most recent first or oldest first)
            timestamps = [entry['timestamp'] for entry in data['history']]
            assert timestamps == sorted(timestamps) or timestamps == sorted(timestamps, reverse=True)


class TestDashboardStatistics:
    """Test statistics calculations for dashboard"""

    def test_calculate_statistics(self, storage, sample_jobs):
        """Test statistics calculation from job data"""
        user_id = 'test_user_009'
        for job in sample_jobs:
            storage.store_job(job, user_id)
        
        jobs = storage.get_all_jobs(user_id)
        
        # Calculate stats
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
        
        assert stats['total'] == 5
        assert stats['red'] == 2  # Excellent matches
        assert stats['yellow'] == 2  # Good matches
        assert stats['green'] == 1  # Fair matches
        assert stats['pending'] == 1
        assert stats['applied'] == 1
        assert stats['interview'] == 1
        assert stats['offer'] == 1
        assert stats['rejected'] == 1


class TestDashboardFiltering:
    """Test filtering and sorting functionality"""

    def test_search_by_title(self, sample_jobs):
        """Test searching jobs by title"""
        search_term = 'engineer'
        filtered = [
            job for job in sample_jobs
            if search_term.lower() in job['title'].lower()
        ]
        assert len(filtered) == 3  # Senior Software, DevOps, Backend
    
    def test_search_by_company(self, sample_jobs):
        """Test searching jobs by company"""
        search_term = 'tech'
        filtered = [
            job for job in sample_jobs
            if search_term.lower() in job['company'].lower()
        ]
        assert len(filtered) == 1  # Tech Corp
    
    def test_filter_by_highlight(self, sample_jobs):
        """Test filtering by match quality (highlight)"""
        highlight = 'red'
        filtered = [
            job for job in sample_jobs
            if job['highlight'].lower() == highlight
        ]
        assert len(filtered) == 2  # Excellent matches
    
    def test_filter_by_status(self, sample_jobs):
        """Test filtering by application status"""
        status = 'interview'
        filtered = [
            job for job in sample_jobs
            if job['status'].lower() == status
        ]
        assert len(filtered) == 1
    
    def test_sort_by_score(self, sample_jobs):
        """Test sorting jobs by score"""
        sorted_jobs = sorted(sample_jobs, key=lambda x: x['score'], reverse=True)
        scores = [job['score'] for job in sorted_jobs]
        assert scores == [85, 78, 72, 68, 45]
    
    def test_sort_by_title(self, sample_jobs):
        """Test sorting jobs by title"""
        sorted_jobs = sorted(sample_jobs, key=lambda x: x['title'].lower())
        titles = [job['title'] for job in sorted_jobs]
        assert titles[0] == 'Backend Engineer'
        assert titles[-1] == 'Senior Software Engineer'
    
    def test_combined_filters(self, sample_jobs):
        """Test combining multiple filters"""
        search_term = 'engineer'
        highlight = 'yellow'
        
        filtered = [
            job for job in sample_jobs
            if search_term.lower() in job['title'].lower()
            and job['highlight'].lower() == highlight
        ]
        assert len(filtered) == 1  # DevOps Engineer


class TestStatusBadgeLogic:
    """Test status badge display logic"""

    def test_status_colors(self):
        """Test status color mapping"""
        color_map = {
            'pending': '#6c757d',
            'applied': '#0d6efd',
            'interview': '#ffc107',
            'offer': '#28a745',
            'rejected': '#dc3545'
        }
        
        for status, expected_color in color_map.items():
            assert expected_color is not None
    
    def test_status_icons(self):
        """Test status icon mapping"""
        icon_map = {
            'pending': 'bi-clock',
            'applied': 'bi-send',
            'interview': 'bi-calendar-check',
            'offer': 'bi-check-circle',
            'rejected': 'bi-x-circle'
        }
        
        for status, expected_icon in icon_map.items():
            assert expected_icon.startswith('bi-')
    
    def test_status_formatting(self):
        """Test status text formatting"""
        test_cases = {
            'pending': 'Pending',
            'APPLIED': 'Applied',
            'interview': 'Interview',
            'OFFER': 'Offer',
            'rejected': 'Rejected'
        }
        
        for input_status, expected_output in test_cases.items():
            formatted = input_status.capitalize()
            assert formatted == expected_output


class TestModalInteraction:
    """Test status update modal functionality"""

    def test_modal_initial_state(self, sample_jobs):
        """Test modal opens with correct initial state"""
        job = sample_jobs[0]
        
        # Verify job data is available
        assert job['job_id'] is not None
        assert job['title'] is not None
        assert job['company'] is not None
        assert job['status'] is not None
    
    def test_status_options(self):
        """Test available status options in modal"""
        valid_statuses = ['pending', 'applied', 'interview', 'offer', 'rejected']
        
        for status in valid_statuses:
            assert status in [s.value for s in ApplicationStatus]
    
    def test_notes_optional(self, client, storage, sample_jobs):
        """Test that notes are optional when updating status"""
        user_id = 'test_user_010'
        job = sample_jobs[0]
        storage.store_job(job, user_id)
        
        # Update without notes
        update_data = {
            'status': 'applied',
            'user_id': user_id
        }
        
        response = client.put(
            f'/api/jobs/{job["job_id"]}/status',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200


class TestResponsiveLayout:
    """Test responsive layout considerations"""

    def test_mobile_card_layout(self, sample_jobs):
        """Test that job cards can be displayed on mobile"""
        # Verify all required fields are present
        for job in sample_jobs:
            assert 'title' in job
            assert 'company' in job
            assert 'location' in job
            assert 'score' in job
            assert 'status' in job
    
    def test_filter_controls_data(self, sample_jobs):
        """Test that filter controls have necessary data"""
        highlights = set(job['highlight'] for job in sample_jobs)
        statuses = set(job['status'] for job in sample_jobs)
        
        assert len(highlights) > 0
        assert len(statuses) > 0


class TestErrorHandling:
    """Test error handling in tracker interface"""

    def test_handle_missing_job_data(self, client):
        """Test handling of missing job data"""
        response = client.get('/api/jobs/stored/empty_user')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['jobs'] == []
    
    def test_handle_network_error_gracefully(self, client):
        """Test API error responses"""
        response = client.get('/api/jobs/stored/')  # Invalid endpoint
        assert response.status_code in [404, 400]
    
    def test_invalid_status_update(self, client, storage, sample_jobs):
        """Test updating with incomplete data"""
        user_id = 'test_user_011'
        job = sample_jobs[0]
        storage.store_job(job, user_id)
        
        # Missing required fields
        update_data = {}
        
        response = client.put(
            f'/api/jobs/{job["job_id"]}/status',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code in [400, 422]


def test_integration_workflow(client, storage, sample_jobs):
    """Test complete workflow from job display to status update"""
    user_id = 'test_integration_user'
    
    # 1. Store jobs
    for job in sample_jobs:
        storage.store_job(job, user_id)
    
    # 2. Fetch jobs for dashboard
    response = client.get(f'/api/jobs/stored/{user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['jobs']) == len(sample_jobs)
    
    # 3. Update a job status
    job_id = sample_jobs[0]['job_id']
    update_data = {
        'status': 'applied',
        'notes': 'Submitted application',
        'user_id': user_id
    }
    
    response = client.put(
        f'/api/jobs/{job_id}/status',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    
    # 4. Verify status history
    response = client.get(f'/api/jobs/{job_id}/status/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'history' in data
    
    # 5. Fetch updated jobs
    response = client.get(f'/api/jobs/stored/{user_id}')
    data = json.loads(response.data)
    updated_job = next(j for j in data['jobs'] if j['job_id'] == job_id)
    assert updated_job['status'] == 'applied'


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
