import React, { useState, useEffect } from 'react';
import './StatusUpdateModal.css';

const StatusUpdateModal = ({ job, onClose, onUpdate }) => {
  const [status, setStatus] = useState(job.status || 'pending');
  const [notes, setNotes] = useState('');
  const [statusHistory, setStatusHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const statusOptions = [
    { value: 'pending', label: 'Pending', color: 'secondary' },
    { value: 'applied', label: 'Applied', color: 'primary' },
    { value: 'interview', label: 'Interview', color: 'info' },
    { value: 'offer', label: 'Offer', color: 'success' },
    { value: 'rejected', label: 'Rejected', color: 'danger' }
  ];

  useEffect(() => {
    if (job.id) {
      fetchStatusHistory();
    }
  }, [job.id]);

  const fetchStatusHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await fetch(`http://localhost:5000/api/jobs/status-history/${job.id}`);
      if (response.ok) {
        const data = await response.json();
        setStatusHistory(data.history || []);
      }
    } catch (err) {
      console.error('Error fetching status history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      await onUpdate(job.id, status, notes);
    } catch (err) {
      console.error('Error updating status:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (statusValue) => {
    const option = statusOptions.find(opt => opt.value === statusValue);
    return option ? option.color : 'secondary';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog modal-lg" onClick={(e) => e.stopPropagation()}>
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Update Application Status</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          
          <div className="modal-body">
            {/* Job Information */}
            <div className="job-info mb-4">
              <h6 className="fw-bold">{job.title}</h6>
              <p className="text-muted mb-1">{job.company}</p>
              <p className="text-muted mb-0">
                <i className="bi bi-geo-alt"></i> {job.location || 'N/A'}
              </p>
            </div>

            {/* Status Update Form */}
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="status" className="form-label fw-bold">
                  Application Status
                </label>
                <select
                  id="status"
                  className="form-select"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  required
                >
                  {statusOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-3">
                <label htmlFor="notes" className="form-label fw-bold">
                  Notes (Optional)
                </label>
                <textarea
                  id="notes"
                  className="form-control"
                  rows="3"
                  placeholder="Add any notes about this status update..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                ></textarea>
              </div>

              <div className="d-flex gap-2">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Updating...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-circle me-2"></i>
                      Update Status
                    </>
                  )}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={onClose}
                  disabled={submitting}
                >
                  Cancel
                </button>
              </div>
            </form>

            {/* Status History */}
            <div className="mt-4">
              <h6 className="fw-bold mb-3">Status History</h6>
              
              {loadingHistory ? (
                <div className="text-center py-3">
                  <div className="spinner-border spinner-border-sm text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              ) : statusHistory.length > 0 ? (
                <div className="status-history-timeline">
                  {statusHistory.map((entry, index) => (
                    <div key={index} className="timeline-item">
                      <div className="timeline-marker">
                        <span className={`badge bg-${getStatusColor(entry.new_status)}`}>
                          {entry.new_status}
                        </span>
                      </div>
                      <div className="timeline-content">
                        <div className="d-flex justify-content-between align-items-start">
                          <div>
                            <strong>
                              {entry.old_status ? 
                                `${entry.old_status} → ${entry.new_status}` : 
                                entry.new_status
                              }
                            </strong>
                            {entry.notes && (
                              <p className="mb-0 mt-1 text-muted small">{entry.notes}</p>
                            )}
                          </div>
                          <small className="text-muted">
                            {formatDate(entry.timestamp)}
                          </small>
                        </div>
                        {entry.user_id && (
                          <small className="text-muted">By: {entry.user_id}</small>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">No status history available.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusUpdateModal;
