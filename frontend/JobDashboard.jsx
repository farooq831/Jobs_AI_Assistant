import React, { useState, useEffect } from 'react';
import StatusBadge from './StatusBadge';
import StatusUpdateModal from './StatusUpdateModal';
import './JobDashboard.css';

const JobDashboard = ({ userId = 'user1' }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [statusSummary, setStatusSummary] = useState(null);
  
  // Filter states
  const [filterHighlight, setFilterHighlight] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch jobs on component mount
  useEffect(() => {
    fetchJobs();
    fetchStatusSummary();
  }, [userId]);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/storage/jobs');
      if (!response.ok) {
        throw new Error('Failed to fetch jobs');
      }
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatusSummary = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/jobs/status/summary');
      if (response.ok) {
        const data = await response.json();
        setStatusSummary(data);
      }
    } catch (err) {
      console.error('Error fetching status summary:', err);
    }
  };

  const handleStatusUpdate = (job) => {
    setSelectedJob(job);
    setShowStatusModal(true);
  };

  const handleStatusUpdateSuccess = async (jobId, newStatus, notes) => {
    try {
      // Update job status via API
      const response = await fetch(`http://localhost:5000/api/jobs/status/${jobId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus,
          notes: notes,
          user_id: userId
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      // Refresh jobs and summary
      await fetchJobs();
      await fetchStatusSummary();
      setShowStatusModal(false);
      setSelectedJob(null);
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Failed to update status: ' + err.message);
    }
  };

  // Filter and sort jobs
  const getFilteredAndSortedJobs = () => {
    let filtered = [...jobs];

    // Apply highlight filter
    if (filterHighlight !== 'all') {
      filtered = filtered.filter(job => 
        job.highlight?.toLowerCase() === filterHighlight.toLowerCase()
      );
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(job => 
        job.status?.toLowerCase() === filterStatus.toLowerCase()
      );
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(job => 
        job.title?.toLowerCase().includes(query) ||
        job.company?.toLowerCase().includes(query) ||
        job.location?.toLowerCase().includes(query)
      );
    }

    // Sort jobs
    filtered.sort((a, b) => {
      let aVal, bVal;
      
      switch (sortBy) {
        case 'score':
          aVal = a.score || 0;
          bVal = b.score || 0;
          break;
        case 'title':
          aVal = a.title || '';
          bVal = b.title || '';
          break;
        case 'company':
          aVal = a.company || '';
          bVal = b.company || '';
          break;
        case 'date':
          aVal = new Date(a.scraped_at || 0);
          bVal = new Date(b.scraped_at || 0);
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    return filtered;
  };

  const getHighlightColor = (highlight) => {
    switch (highlight?.toLowerCase()) {
      case 'red':
        return 'danger';
      case 'yellow':
        return 'warning';
      case 'white':
        return 'light';
      case 'green':
        return 'success';
      default:
        return 'secondary';
    }
  };

  const filteredJobs = getFilteredAndSortedJobs();

  return (
    <div className="job-dashboard">
      <div className="container-fluid">
        <div className="row mb-4">
          <div className="col-12">
            <h2 className="mb-3">Job Listings Dashboard</h2>
            
            {/* Status Summary */}
            {statusSummary && (
              <div className="row mb-3">
                <div className="col">
                  <div className="card">
                    <div className="card-body">
                      <h5 className="card-title">Application Status Summary</h5>
                      <div className="row text-center">
                        <div className="col">
                          <h3>{statusSummary.total_jobs || 0}</h3>
                          <small>Total Jobs</small>
                        </div>
                        <div className="col">
                          <h3 className="text-primary">{statusSummary.applied || 0}</h3>
                          <small>Applied</small>
                        </div>
                        <div className="col">
                          <h3 className="text-info">{statusSummary.interview || 0}</h3>
                          <small>Interview</small>
                        </div>
                        <div className="col">
                          <h3 className="text-success">{statusSummary.offer || 0}</h3>
                          <small>Offers</small>
                        </div>
                        <div className="col">
                          <h3 className="text-danger">{statusSummary.rejected || 0}</h3>
                          <small>Rejected</small>
                        </div>
                        <div className="col">
                          <h3 className="text-secondary">{statusSummary.pending || 0}</h3>
                          <small>Pending</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Filters and Search */}
            <div className="card mb-3">
              <div className="card-body">
                <div className="row g-3">
                  <div className="col-md-3">
                    <label className="form-label">Search</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search jobs..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Highlight</label>
                    <select
                      className="form-select"
                      value={filterHighlight}
                      onChange={(e) => setFilterHighlight(e.target.value)}
                    >
                      <option value="all">All</option>
                      <option value="red">Red</option>
                      <option value="yellow">Yellow</option>
                      <option value="white">White</option>
                      <option value="green">Green</option>
                    </select>
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Status</label>
                    <select
                      className="form-select"
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                    >
                      <option value="all">All</option>
                      <option value="pending">Pending</option>
                      <option value="applied">Applied</option>
                      <option value="interview">Interview</option>
                      <option value="offer">Offer</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Sort By</label>
                    <select
                      className="form-select"
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                    >
                      <option value="score">Score</option>
                      <option value="title">Title</option>
                      <option value="company">Company</option>
                      <option value="date">Date</option>
                    </select>
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">Order</label>
                    <select
                      className="form-select"
                      value={sortOrder}
                      onChange={(e) => setSortOrder(e.target.value)}
                    >
                      <option value="desc">Descending</option>
                      <option value="asc">Ascending</option>
                    </select>
                  </div>
                  <div className="col-md-1 d-flex align-items-end">
                    <button
                      className="btn btn-primary w-100"
                      onClick={fetchJobs}
                      disabled={loading}
                    >
                      <i className="bi bi-arrow-clockwise"></i> Refresh
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-3">Loading jobs...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="alert alert-danger" role="alert">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Jobs List */}
        {!loading && !error && (
          <div className="row">
            <div className="col-12">
              <p className="text-muted mb-3">
                Showing {filteredJobs.length} of {jobs.length} jobs
              </p>
              
              {filteredJobs.length === 0 ? (
                <div className="alert alert-info">
                  No jobs found. Try adjusting your filters or scrape some jobs first.
                </div>
              ) : (
                <div className="jobs-grid">
                  {filteredJobs.map((job) => (
                    <div
                      key={job.id}
                      className={`card mb-3 job-card border-${getHighlightColor(job.highlight)}`}
                    >
                      <div className="card-body">
                        <div className="d-flex justify-content-between align-items-start mb-2">
                          <h5 className="card-title mb-0">{job.title}</h5>
                          <div className="d-flex gap-2">
                            {job.highlight && (
                              <span className={`badge bg-${getHighlightColor(job.highlight)}`}>
                                {job.highlight}
                              </span>
                            )}
                            <StatusBadge status={job.status || 'pending'} />
                          </div>
                        </div>
                        
                        <h6 className="card-subtitle mb-2 text-muted">{job.company}</h6>
                        
                        <div className="job-details mb-3">
                          <p className="mb-1">
                            <i className="bi bi-geo-alt"></i> {job.location || 'N/A'}
                          </p>
                          <p className="mb-1">
                            <i className="bi bi-currency-dollar"></i> {job.salary || 'Not specified'}
                          </p>
                          <p className="mb-1">
                            <i className="bi bi-briefcase"></i> {job.job_type || 'N/A'}
                          </p>
                          {job.score !== undefined && (
                            <p className="mb-1">
                              <i className="bi bi-star-fill"></i> Match Score: <strong>{job.score.toFixed(1)}%</strong>
                            </p>
                          )}
                        </div>

                        {job.description && (
                          <p className="card-text text-truncate-3">
                            {job.description}
                          </p>
                        )}

                        <div className="d-flex gap-2 mt-3">
                          {job.url && (
                            <a
                              href={job.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="btn btn-sm btn-outline-primary"
                            >
                              <i className="bi bi-box-arrow-up-right"></i> View Job
                            </a>
                          )}
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() => handleStatusUpdate(job)}
                          >
                            <i className="bi bi-pencil"></i> Update Status
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Status Update Modal */}
      {showStatusModal && selectedJob && (
        <StatusUpdateModal
          job={selectedJob}
          onClose={() => {
            setShowStatusModal(false);
            setSelectedJob(null);
          }}
          onUpdate={handleStatusUpdateSuccess}
        />
      )}
    </div>
  );
};

export default JobDashboard;
