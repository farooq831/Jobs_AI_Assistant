import React, { useState, useEffect } from 'react';
import StatusBadge from './StatusBadge';
import StatusUpdateModal from './StatusUpdateModal';
import './JobDashboard.css';

const JobDashboard = ({ userId = 'default_user' }) => {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filter and sort states
  const [searchTerm, setSearchTerm] = useState('');
  const [highlightFilter, setHighlightFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('score');
  const [sortOrder, setSortOrder] = useState('desc');
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  
  // Statistics
  const [stats, setStats] = useState({
    total: 0,
    red: 0,
    yellow: 0,
    white: 0,
    green: 0,
    applied: 0,
    interview: 0,
    offer: 0,
    rejected: 0,
    pending: 0
  });

  // Fetch jobs on component mount
  useEffect(() => {
    fetchJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  // Apply filters and sorting when jobs or filters change
  useEffect(() => {
    applyFiltersAndSort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobs, searchTerm, highlightFilter, statusFilter, sortBy, sortOrder]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch jobs from backend
      const response = await fetch(`http://localhost:5000/api/jobs/stored/${userId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.statusText}`);
      }
      
      const data = await response.json();
      setJobs(data.jobs || []);
      calculateStats(data.jobs || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (jobList) => {
    const newStats = {
      total: jobList.length,
      red: 0,
      yellow: 0,
      white: 0,
      green: 0,
      applied: 0,
      interview: 0,
      offer: 0,
      rejected: 0,
      pending: 0
    };

    jobList.forEach(job => {
      // Count by highlight
      const highlight = job.highlight ? job.highlight.toLowerCase() : 'white';
      if (highlight in newStats) {
        newStats[highlight]++;
      }

      // Count by status
      const status = job.status ? job.status.toLowerCase() : 'pending';
      if (status in newStats) {
        newStats[status]++;
      }
    });

    setStats(newStats);
  };

  const applyFiltersAndSort = () => {
    let filtered = [...jobs];

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(job =>
        (job.title && job.title.toLowerCase().includes(term)) ||
        (job.company && job.company.toLowerCase().includes(term)) ||
        (job.location && job.location.toLowerCase().includes(term))
      );
    }

    // Apply highlight filter
    if (highlightFilter !== 'all') {
      filtered = filtered.filter(job => {
        const highlight = job.highlight ? job.highlight.toLowerCase() : 'white';
        return highlight === highlightFilter.toLowerCase();
      });
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(job => {
        const status = job.status ? job.status.toLowerCase() : 'pending';
        return status === statusFilter.toLowerCase();
      });
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aVal, bVal;

      switch (sortBy) {
        case 'score':
          aVal = a.score || 0;
          bVal = b.score || 0;
          break;
        case 'title':
          aVal = (a.title || '').toLowerCase();
          bVal = (b.title || '').toLowerCase();
          break;
        case 'company':
          aVal = (a.company || '').toLowerCase();
          bVal = (b.company || '').toLowerCase();
          break;
        case 'date':
          aVal = new Date(a.scraped_at || 0);
          bVal = new Date(b.scraped_at || 0);
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
      } else {
        return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
      }
    });

    setFilteredJobs(filtered);
  };

  const handleStatusUpdate = async (jobId, newStatus, notes) => {
    try {
      const response = await fetch(`http://localhost:5000/api/jobs/${jobId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus,
          notes: notes,
          user_id: userId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      // Refresh jobs after update
      await fetchJobs();
      setShowModal(false);
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Failed to update status: ' + err.message);
    }
  };

  const openStatusModal = (job) => {
    setSelectedJob(job);
    setShowModal(true);
  };

  const closeStatusModal = () => {
    setShowModal(false);
    setSelectedJob(null);
  };

  const getHighlightColor = (highlight) => {
    const colors = {
      red: '#dc3545',
      yellow: '#ffc107',
      white: '#6c757d',
      green: '#28a745'
    };
    return colors[highlight?.toLowerCase()] || colors.white;
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Poor Match';
  };

  if (loading) {
    return (
      <div className="job-dashboard">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3">Loading jobs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="job-dashboard">
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Error!</h4>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchJobs}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="job-dashboard">
      {/* Statistics Summary */}
      <div className="stats-summary mb-4">
        <div className="row g-3">
          <div className="col-md-2">
            <div className="stat-card">
              <div className="stat-label">Total Jobs</div>
              <div className="stat-value">{stats.total}</div>
            </div>
          </div>
          <div className="col-md-2">
            <div className="stat-card highlight-red">
              <div className="stat-label">Excellent</div>
              <div className="stat-value">{stats.red}</div>
            </div>
          </div>
          <div className="col-md-2">
            <div className="stat-card highlight-yellow">
              <div className="stat-label">Good</div>
              <div className="stat-value">{stats.yellow}</div>
            </div>
          </div>
          <div className="col-md-2">
            <div className="stat-card highlight-green">
              <div className="stat-label">Fair</div>
              <div className="stat-value">{stats.green}</div>
            </div>
          </div>
          <div className="col-md-2">
            <div className="stat-card">
              <div className="stat-label">Applied</div>
              <div className="stat-value">{stats.applied}</div>
            </div>
          </div>
          <div className="col-md-2">
            <div className="stat-card">
              <div className="stat-label">Interview</div>
              <div className="stat-value">{stats.interview}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="filters-section mb-4">
        <div className="row g-3">
          <div className="col-md-4">
            <input
              type="text"
              className="form-control"
              placeholder="Search by title, company, or location..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="col-md-2">
            <select
              className="form-select"
              value={highlightFilter}
              onChange={(e) => setHighlightFilter(e.target.value)}
            >
              <option value="all">All Matches</option>
              <option value="red">Excellent</option>
              <option value="yellow">Good</option>
              <option value="green">Fair</option>
              <option value="white">Poor</option>
            </select>
          </div>
          <div className="col-md-2">
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="applied">Applied</option>
              <option value="interview">Interview</option>
              <option value="offer">Offer</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div className="col-md-2">
            <select
              className="form-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="score">Sort by Score</option>
              <option value="title">Sort by Title</option>
              <option value="company">Sort by Company</option>
              <option value="date">Sort by Date</option>
            </select>
          </div>
          <div className="col-md-2">
            <button
              className="btn btn-outline-secondary w-100"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
            </button>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="jobs-list">
        {filteredJobs.length === 0 ? (
          <div className="alert alert-info">
            <i className="bi bi-info-circle me-2"></i>
            No jobs found matching your filters.
          </div>
        ) : (
          <div className="row g-3">
            {filteredJobs.map((job) => (
              <div key={job.job_id} className="col-12">
                <div
                  className="job-card"
                  style={{
                    borderLeft: `5px solid ${getHighlightColor(job.highlight)}`
                  }}
                >
                  <div className="job-card-header">
                    <div className="job-title-section">
                      <h5 className="job-title">{job.title}</h5>
                      <div className="job-company">{job.company}</div>
                    </div>
                    <div className="job-score-section">
                      <div className="score-badge" style={{
                        backgroundColor: getHighlightColor(job.highlight),
                        color: 'white'
                      }}>
                        {job.score || 0}
                      </div>
                      <div className="score-label">{getScoreLabel(job.score)}</div>
                    </div>
                  </div>

                  <div className="job-card-body">
                    <div className="job-details">
                      <div className="job-detail-item">
                        <i className="bi bi-geo-alt"></i>
                        <span>{job.location || 'Not specified'}</span>
                      </div>
                      <div className="job-detail-item">
                        <i className="bi bi-cash"></i>
                        <span>{job.salary || 'Not disclosed'}</span>
                      </div>
                      <div className="job-detail-item">
                        <i className="bi bi-briefcase"></i>
                        <span>{job.job_type || 'Full-time'}</span>
                      </div>
                      <div className="job-detail-item">
                        <StatusBadge status={job.status || 'pending'} />
                      </div>
                      {(job.url || job.link) && (
                        <div className="job-detail-item">
                          <i className="bi bi-link-45deg"></i>
                          <a 
                            href={job.url || job.link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="job-link"
                          >
                            View Job Posting
                          </a>
                        </div>
                      )}
                    </div>

                    {job.description && (
                      <div className="job-description">
                        <p>{job.description.substring(0, 200)}...</p>
                      </div>
                    )}

                    {job.resume_tips && job.resume_tips.length > 0 && (
                      <div className="resume-tips">
                        <h6><i className="bi bi-lightbulb"></i> Resume Tips</h6>
                        <ul>
                          {job.resume_tips.slice(0, 3).map((tip, index) => (
                            <li key={index}>{tip}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  <div className="job-card-footer">
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => openStatusModal(job)}
                    >
                      <i className="bi bi-pencil me-1"></i>
                      Update Status
                    </button>
                    {job.link && (
                      <a
                        href={job.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-sm btn-outline-primary"
                      >
                        <i className="bi bi-box-arrow-up-right me-1"></i>
                        View Job
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Status Update Modal */}
      {showModal && selectedJob && (
        <StatusUpdateModal
          job={selectedJob}
          onClose={closeStatusModal}
          onUpdate={handleStatusUpdate}
        />
      )}
    </div>
  );
};

export default JobDashboard;
