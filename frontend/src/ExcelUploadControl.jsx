import React, { useState, useRef } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const ExcelUploadControl = ({ userId, onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [validationResults, setValidationResults] = useState(null);
  const [uploadResults, setUploadResults] = useState(null);
  const fileInputRef = useRef(null);

  // Allowed file types
  const ALLOWED_TYPES = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel'
  ];
  const ALLOWED_EXTENSIONS = ['xlsx', 'xls'];
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

  // Validate file
  const validateFile = (file) => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: 'File size exceeds 10MB limit' };
    }

    // Check file extension
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(fileExtension)) {
      return { valid: false, error: 'Only Excel files (.xlsx, .xls) are allowed' };
    }

    // Check MIME type if available
    if (file.type && !ALLOWED_TYPES.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Please upload an Excel file' };
    }

    return { valid: true };
  };

  // Handle file selection
  const handleFileSelect = (file) => {
    setUploadError('');
    setUploadSuccess('');
    setValidationResults(null);
    setUploadResults(null);

    const validation = validateFile(file);
    if (!validation.valid) {
      setUploadError(validation.error);
      return;
    }

    setSelectedFile(file);
  };

  // Handle file input change
  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // Handle drag events
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  // Handle validate file
  const handleValidate = async () => {
    if (!selectedFile) {
      setUploadError('Please select a file first');
      return;
    }

    setIsValidating(true);
    setUploadError('');
    setValidationResults(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (userId) {
        formData.append('user_id', userId);
      }

      const response = await fetch('http://localhost:5000/api/upload/excel/validate', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setValidationResults(data);
        if (data.valid) {
          setUploadSuccess('File validated successfully! Ready to upload.');
        } else {
          setUploadError('File validation found issues. Please review below.');
        }
      } else {
        setUploadError(data.message || 'Failed to validate file');
      }
    } catch (error) {
      console.error('Validation error:', error);
      setUploadError('Failed to connect to server. Please try again.');
    } finally {
      setIsValidating(false);
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setUploadError('');
    setUploadSuccess('');
    setUploadResults(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (userId) {
        formData.append('user_id', userId);
      }

      const response = await fetch('http://localhost:5000/api/upload/excel', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setUploadSuccess('Excel file processed successfully!');
        setUploadResults(data);
        setSelectedFile(null);
        setValidationResults(null);
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        // Callback to parent component
        if (onUploadSuccess) {
          onUploadSuccess(data);
        }
      } else {
        setUploadError(data.message || 'Failed to upload file');
        if (data.validation_errors) {
          setValidationResults({ errors: data.validation_errors });
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError('Failed to connect to server. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle apply updates (after upload)
  const handleApplyUpdates = async () => {
    if (!uploadResults || !uploadResults.parsed_data) {
      setUploadError('No data to apply. Please upload a file first.');
      return;
    }

    setIsUploading(true);
    setUploadError('');
    setUploadSuccess('');

    try {
      const response = await fetch('http://localhost:5000/api/upload/excel/apply-updates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          updates: uploadResults.parsed_data
        })
      });

      const data = await response.json();

      if (response.ok) {
        setUploadSuccess(`Successfully applied ${data.applied_count || 0} status updates!`);
        setUploadResults(data);
        // Callback to parent component
        if (onUploadSuccess) {
          onUploadSuccess(data);
        }
      } else {
        setUploadError(data.message || 'Failed to apply updates');
      }
    } catch (error) {
      console.error('Apply updates error:', error);
      setUploadError('Failed to connect to server. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle remove selected file
  const handleRemoveFile = () => {
    setSelectedFile(null);
    setUploadError('');
    setValidationResults(null);
    setUploadResults(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="excel-upload-control">
      {uploadSuccess && (
        <div className="alert alert-success alert-dismissible fade show mb-3" role="alert">
          <i className="bi bi-check-circle me-2"></i>
          <strong>Success!</strong> {uploadSuccess}
          <button
            type="button"
            className="btn-close"
            onClick={() => setUploadSuccess('')}
            aria-label="Close"
          ></button>
        </div>
      )}

      {uploadError && (
        <div className="alert alert-danger alert-dismissible fade show mb-3" role="alert">
          <i className="bi bi-exclamation-triangle me-2"></i>
          <strong>Error!</strong> {uploadError}
          <button
            type="button"
            className="btn-close"
            onClick={() => setUploadError('')}
            aria-label="Close"
          ></button>
        </div>
      )}

      <div className="card">
        <div className="card-header bg-warning text-dark">
          <h5 className="mb-0">
            <i className="bi bi-upload me-2"></i>
            Upload Excel for Status Updates
          </h5>
        </div>
        <div className="card-body">
          {/* Drag and Drop Zone */}
          <div
            className={`border rounded p-4 text-center mb-3 ${
              isDragging ? 'border-primary bg-light' : 'border-secondary'
            } ${selectedFile ? 'border-success' : ''}`}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              minHeight: '180px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center'
            }}
            onClick={() => !selectedFile && fileInputRef.current?.click()}
          >
            {selectedFile ? (
              <div>
                <i className="bi bi-file-earmark-excel-fill text-success" style={{ fontSize: '3rem' }}></i>
                <h6 className="mt-3 text-success">Excel File Selected</h6>
                <p className="mb-2"><strong>{selectedFile.name}</strong></p>
                <p className="text-muted small mb-3">{formatFileSize(selectedFile.size)}</p>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-danger"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveFile();
                  }}
                >
                  <i className="bi bi-trash me-1"></i>
                  Remove File
                </button>
              </div>
            ) : (
              <div>
                <i className="bi bi-cloud-arrow-up" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                <h6 className="mt-3">Drag & Drop Excel file here</h6>
                <p className="text-muted">or click to browse</p>
                <p className="text-muted small">Supported formats: .xlsx, .xls (Max 10MB)</p>
              </div>
            )}
          </div>

          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            className="d-none"
            accept=".xlsx,.xls"
            onChange={handleFileInputChange}
          />

          {/* Action Buttons */}
          <div className="d-grid gap-2 mb-3">
            {!validationResults && selectedFile && (
              <button
                type="button"
                className="btn btn-outline-info"
                onClick={handleValidate}
                disabled={!selectedFile || isValidating}
              >
                {isValidating ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Validating...
                  </>
                ) : (
                  <>
                    <i className="bi bi-check-square me-2"></i>
                    Validate File
                  </>
                )}
              </button>
            )}

            {selectedFile && (
              <button
                type="button"
                className="btn btn-warning btn-lg"
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
              >
                {isUploading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Processing...
                  </>
                ) : (
                  <>
                    <i className="bi bi-upload me-2"></i>
                    Upload & Process Excel
                  </>
                )}
              </button>
            )}

            {uploadResults && uploadResults.parsed_data && (
              <button
                type="button"
                className="btn btn-success btn-lg"
                onClick={handleApplyUpdates}
                disabled={isUploading}
              >
                <i className="bi bi-check-all me-2"></i>
                Apply Status Updates
              </button>
            )}
          </div>

          {/* Validation Results */}
          {validationResults && (
            <div className="mt-3">
              <h6 className="text-muted mb-2">
                <i className="bi bi-info-circle me-2"></i>
                Validation Results:
              </h6>
              <div className={`alert ${validationResults.valid ? 'alert-success' : 'alert-warning'}`}>
                <strong>Status: {validationResults.valid ? 'Valid' : 'Issues Found'}</strong>
                {validationResults.rows_found && (
                  <p className="mb-1">
                    <i className="bi bi-table me-1"></i>
                    Rows found: {validationResults.rows_found}
                  </p>
                )}
                {validationResults.warnings && validationResults.warnings.length > 0 && (
                  <div className="mt-2">
                    <strong>Warnings:</strong>
                    <ul className="mb-0 mt-1">
                      {validationResults.warnings.map((warning, idx) => (
                        <li key={idx}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {validationResults.errors && validationResults.errors.length > 0 && (
                  <div className="mt-2">
                    <strong>Errors:</strong>
                    <ul className="mb-0 mt-1">
                      {validationResults.errors.map((error, idx) => (
                        <li key={idx} className="text-danger">{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Upload Results */}
          {uploadResults && (
            <div className="mt-3">
              <h6 className="text-muted mb-2">
                <i className="bi bi-list-check me-2"></i>
                Upload Results:
              </h6>
              <div className="alert alert-info">
                {uploadResults.total_rows && (
                  <p className="mb-1">
                    <strong>Total Rows:</strong> {uploadResults.total_rows}
                  </p>
                )}
                {uploadResults.valid_rows && (
                  <p className="mb-1">
                    <strong>Valid Rows:</strong> {uploadResults.valid_rows}
                  </p>
                )}
                {uploadResults.invalid_rows && uploadResults.invalid_rows > 0 && (
                  <p className="mb-1 text-warning">
                    <strong>Invalid Rows:</strong> {uploadResults.invalid_rows}
                  </p>
                )}
                {uploadResults.applied_count !== undefined && (
                  <p className="mb-1 text-success">
                    <strong>Applied Updates:</strong> {uploadResults.applied_count}
                  </p>
                )}
                {uploadResults.summary && (
                  <div className="mt-2">
                    <strong>Summary:</strong>
                    <pre className="mb-0 mt-1 small" style={{ whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(uploadResults.summary, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Info Section */}
          <div className="mt-3">
            <h6 className="text-muted mb-2">
              <i className="bi bi-question-circle me-2"></i>
              How to use:
            </h6>
            <ol className="text-muted small mb-0">
              <li>Export your jobs data to Excel first</li>
              <li>Update the "Status" column with: Applied, Interview, Offer, Rejected, or Pending</li>
              <li>Optionally add notes in the "Notes" column</li>
              <li>Upload the modified Excel file here</li>
              <li>Review validation results and apply updates</li>
            </ol>
            <div className="alert alert-light mt-2 mb-0">
              <small>
                <i className="bi bi-lightbulb me-1"></i>
                <strong>Tip:</strong> The Excel file should have columns like Job ID, Job Title, Company, Status, and optionally Notes.
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExcelUploadControl;
