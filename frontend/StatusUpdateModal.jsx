import React, { useState, useEffect } from 'react';
import './StatusUpdateModal.css';

const StatusUpdateModal = ({ job, onClose, onUpdate }) => {
  const [status, setStatus] = useState(job.status || 'pending');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    // Fetch status history when modal opens
    fetchStatusHistory();
  }, [job.job_id]);

  const fetchStatusHistory = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/jobs/${job.job_id}/status/history`);
      if (response.ok) {
        const data = await response.json();
        setHistory(data.history || []);
      }
    } catch (err) {
      console.error('Error fetching status history:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onUpdate(job.job_id, status, notes);
    } catch (err) {
      console.error('Error updating status:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (statusValue) => {
    const colors = {
      pending: '#6c757d',
      applied: '#0d6efd',
      interview: '#ffc107',
      offer: '#28a745',
      rejected: '#dc3545'
    };
    return colors[statusValue?.toLowerCase()] || colors.pending;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h5 className="modal-title">
            <i className="bi bi-pencil-square me-2"></i>
            Update Application Status
          </h5>
          <button className="btn-close" onClick={onClose}>
            <i className="bi bi-x-lg"></i>
          </button>
        </div>

        <div className="modal-body">
          {/* Job Info */}
          <div className="job-info mb-4">
            <h6 className="job-info-title">{job.title}</h6>
            <div className="job-info-company">{job.company}</div>
            <div className="job-info-location">
              <i className="bi bi-geo-alt me-1"></i>
              {job.location}
            </div>
          </div>

          {/* Status Update Form */}
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="status" className="form-label">
                Application Status
              </label>
              <select
                id="status"
                className="form-select"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                required
              >
                <option value="pending">Pending</option>
                <option value="applied">Applied</option>
                <option value="interview">Interview Scheduled</option>
                <option value="offer">Offer Received</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            <div className="mb-3">
              <label htmlFor="notes" className="form-label">
                Notes (Optional)
              </label>
              <textarea
                id="notes"
                className="form-control"
                rows="3"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes about this status update..."
              />
            </div>

            <div className="d-flex gap-2">
              <button
                type="submit"
                className="btn btn-primary flex-grow-1"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2"></span>
                    Updating...
                  </>
                ) : (
                  <>
                    <i className="bi bi-check-lg me-2"></i>
                    Update Status
                  </>
                )}
              </button>
              <button
                type="button"
                className="btn btn-outline-secondary"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </form>

          {/* History Toggle */}
          {history.length > 0 && (
            <div className="mt-4">
              <button
                className="btn btn-link p-0"
                onClick={() => setShowHistory(!showHistory)}
              >
                <i className={`bi bi-chevron-${showHistory ? 'up' : 'down'} me-1`}></i>
                {showHistory ? 'Hide' : 'Show'} Status History ({history.length})
              </button>

              {showHistory && (
                <div className="status-history mt-3">
                  <div className="timeline">
                    {history.map((entry, index) => (
                      <div key={index} className="timeline-item">
                        <div
                          className="timeline-marker"
                          style={{ backgroundColor: getStatusColor(entry.status) }}
                        ></div>
                        <div className="timeline-content">
                          <div className="timeline-header">
                            <span className="timeline-status">
                              {entry.status ? entry.status.charAt(0).toUpperCase() + entry.status.slice(1) : 'Unknown'}
                            </span>
                            <span className="timeline-date">
                              {formatDate(entry.timestamp)}
                            </span>
                          </div>
                          {entry.notes && (
                            <div className="timeline-notes">{entry.notes}</div>
                          )}
                          {entry.user_id && (
                            <div className="timeline-user">
                              <i className="bi bi-person me-1"></i>
                              {entry.user_id}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatusUpdateModal;
