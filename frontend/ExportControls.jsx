import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const ExportControls = ({ userId, resumeId, jobs = [], showCustomExport = true }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState('excel');
  const [exportType, setExportType] = useState('stored'); // stored, custom, quick
  const [exportError, setExportError] = useState('');
  const [exportSuccess, setExportSuccess] = useState('');
  const [includeResumeTips, setIncludeResumeTips] = useState(true);

  // Export configurations
  const exportFormats = [
    { value: 'excel', label: 'Excel (.xlsx)', icon: 'bi-file-earmark-excel' },
    { value: 'csv', label: 'CSV (.csv)', icon: 'bi-file-earmark-text' },
    { value: 'pdf', label: 'PDF (.pdf)', icon: 'bi-file-earmark-pdf' }
  ];

  const exportTypes = [
    { value: 'stored', label: 'All Stored Jobs', description: 'Export all jobs from database' },
    { value: 'custom', label: 'Custom Selection', description: 'Export selected jobs only' },
    { value: 'quick', label: 'Quick Export', description: 'Fast export without tips' }
  ];

  // Handle export
  const handleExport = async () => {
    setExportError('');
    setExportSuccess('');

    // Validation
    if (exportType === 'stored' && !userId) {
      setExportError('User ID is required for stored jobs export');
      return;
    }

    if (exportType === 'custom' && (!jobs || jobs.length === 0)) {
      setExportError('No jobs selected for export');
      return;
    }

    setIsExporting(true);

    try {
      let endpoint = '';
      let method = 'GET';
      let body = null;

      // Build endpoint based on format and type
      if (exportFormat === 'excel') {
        if (exportType === 'stored') {
          endpoint = `/api/export/excel/stored-jobs/${userId}`;
          method = 'GET';
        } else if (exportType === 'custom') {
          endpoint = '/api/export/excel';
          method = 'POST';
          body = JSON.stringify({
            jobs: jobs,
            user_id: userId,
            include_tips: includeResumeTips,
            resume_id: resumeId
          });
        } else if (exportType === 'quick') {
          endpoint = `/api/export/excel/quick/${userId}`;
          method = 'GET';
        }
      } else if (exportFormat === 'csv') {
        if (exportType === 'stored') {
          endpoint = `/api/export/csv/stored-jobs/${userId}`;
          method = 'GET';
        } else if (exportType === 'custom') {
          endpoint = '/api/export/csv';
          method = 'POST';
          body = JSON.stringify({ jobs: jobs, user_id: userId });
        } else if (exportType === 'quick') {
          endpoint = `/api/export/csv/quick/${userId}`;
          method = 'GET';
        }
      } else if (exportFormat === 'pdf') {
        if (exportType === 'stored') {
          endpoint = `/api/export/pdf/stored-jobs/${userId}`;
          method = 'GET';
        } else if (exportType === 'custom') {
          endpoint = '/api/export/pdf';
          method = 'POST';
          body = JSON.stringify({
            jobs: jobs,
            user_id: userId,
            include_tips: includeResumeTips
          });
        } else if (exportType === 'quick') {
          endpoint = `/api/export/pdf/quick/${userId}`;
          method = 'GET';
        }
      }

      const options = {
        method: method,
        headers: method === 'POST' ? { 'Content-Type': 'application/json' } : {}
      };

      if (body) {
        options.body = body;
      }

      const response = await fetch(`http://localhost:5000${endpoint}`, options);

      if (response.ok) {
        // Get filename from Content-Disposition header or create default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `jobs_export.${exportFormat}`;
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }

        // Download the file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        setExportSuccess(`Successfully exported to ${filename}`);
      } else {
        const errorData = await response.json();
        setExportError(errorData.message || `Failed to export ${exportFormat.toUpperCase()}`);
      }
    } catch (error) {
      console.error('Export error:', error);
      setExportError('Failed to connect to server. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  // Quick export buttons for common formats
  const handleQuickExport = async (format) => {
    setExportFormat(format);
    setExportType('quick');
    // Trigger export after state update
    setTimeout(() => handleExport(), 100);
  };

  return (
    <div className="export-controls">
      {exportSuccess && (
        <div className="alert alert-success alert-dismissible fade show mb-3" role="alert">
          <i className="bi bi-check-circle me-2"></i>
          <strong>Success!</strong> {exportSuccess}
          <button
            type="button"
            className="btn-close"
            onClick={() => setExportSuccess('')}
            aria-label="Close"
          ></button>
        </div>
      )}

      {exportError && (
        <div className="alert alert-danger alert-dismissible fade show mb-3" role="alert">
          <i className="bi bi-exclamation-triangle me-2"></i>
          <strong>Error!</strong> {exportError}
          <button
            type="button"
            className="btn-close"
            onClick={() => setExportError('')}
            aria-label="Close"
          ></button>
        </div>
      )}

      <div className="card">
        <div className="card-header bg-info text-white">
          <h5 className="mb-0">
            <i className="bi bi-download me-2"></i>
            Export Jobs Data
          </h5>
        </div>
        <div className="card-body">
          {/* Quick Export Buttons */}
          <div className="mb-4">
            <h6 className="text-muted mb-2">Quick Export:</h6>
            <div className="btn-group" role="group">
              <button
                type="button"
                className="btn btn-outline-success"
                onClick={() => handleQuickExport('excel')}
                disabled={isExporting || !userId}
                title="Quick Excel export without tips"
              >
                <i className="bi bi-file-earmark-excel me-2"></i>
                Excel
              </button>
              <button
                type="button"
                className="btn btn-outline-primary"
                onClick={() => handleQuickExport('csv')}
                disabled={isExporting || !userId}
                title="Quick CSV export"
              >
                <i className="bi bi-file-earmark-text me-2"></i>
                CSV
              </button>
              <button
                type="button"
                className="btn btn-outline-danger"
                onClick={() => handleQuickExport('pdf')}
                disabled={isExporting || !userId}
                title="Quick PDF export without tips"
              >
                <i className="bi bi-file-earmark-pdf me-2"></i>
                PDF
              </button>
            </div>
          </div>

          <hr />

          {/* Advanced Export Options */}
          {showCustomExport && (
            <>
              <h6 className="text-muted mb-3">Advanced Export Options:</h6>

              {/* Export Format Selection */}
              <div className="mb-3">
                <label className="form-label fw-bold">Export Format:</label>
                <div className="btn-group w-100" role="group">
                  {exportFormats.map((format) => (
                    <React.Fragment key={format.value}>
                      <input
                        type="radio"
                        className="btn-check"
                        name="exportFormat"
                        id={`format-${format.value}`}
                        value={format.value}
                        checked={exportFormat === format.value}
                        onChange={(e) => setExportFormat(e.target.value)}
                      />
                      <label
                        className={`btn btn-outline-secondary ${exportFormat === format.value ? 'active' : ''}`}
                        htmlFor={`format-${format.value}`}
                      >
                        <i className={`${format.icon} me-2`}></i>
                        {format.label}
                      </label>
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* Export Type Selection */}
              <div className="mb-3">
                <label className="form-label fw-bold">Export Type:</label>
                {exportTypes.map((type) => (
                  <div key={type.value} className="form-check">
                    <input
                      className="form-check-input"
                      type="radio"
                      name="exportType"
                      id={`type-${type.value}`}
                      value={type.value}
                      checked={exportType === type.value}
                      onChange={(e) => setExportType(e.target.value)}
                    />
                    <label className="form-check-label" htmlFor={`type-${type.value}`}>
                      <strong>{type.label}</strong>
                      <br />
                      <small className="text-muted">{type.description}</small>
                    </label>
                  </div>
                ))}
              </div>

              {/* Additional Options */}
              {(exportFormat === 'excel' || exportFormat === 'pdf') && exportType !== 'quick' && (
                <div className="mb-3">
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="includeResumeTips"
                      checked={includeResumeTips}
                      onChange={(e) => setIncludeResumeTips(e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor="includeResumeTips">
                      Include resume optimization tips
                      <br />
                      <small className="text-muted">
                        Add personalized tips as comments (Excel) or section (PDF)
                      </small>
                    </label>
                  </div>
                </div>
              )}

              {/* Export Button */}
              <div className="d-grid">
                <button
                  type="button"
                  className="btn btn-primary btn-lg"
                  onClick={handleExport}
                  disabled={isExporting || (exportType === 'stored' && !userId)}
                >
                  {isExporting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Exporting...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-download me-2"></i>
                      Export {exportFormat.toUpperCase()}
                    </>
                  )}
                </button>
              </div>

              {/* Info */}
              <div className="mt-3">
                <small className="text-muted">
                  <i className="bi bi-info-circle me-1"></i>
                  {exportType === 'custom' && jobs.length > 0 && `${jobs.length} job(s) will be exported. `}
                  {exportType === 'stored' && !userId && 'Please provide a user ID to export stored jobs. '}
                  Export files will be downloaded automatically.
                </small>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExportControls;
