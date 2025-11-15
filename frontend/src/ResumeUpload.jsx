import React, { useState, useRef } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const ResumeUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadedData, setUploadedData] = useState(null);
  const fileInputRef = useRef(null);

  // Allowed file types
  const ALLOWED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  const ALLOWED_EXTENSIONS = ['pdf', 'docx'];
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

  // Validate file
  const validateFile = (file) => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: 'File size exceeds 10MB limit' };
    }

    // Check file type
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(fileExtension)) {
      return { valid: false, error: 'Only PDF and DOCX files are allowed' };
    }

    if (!ALLOWED_TYPES.includes(file.type) && file.type !== '') {
      return { valid: false, error: 'Invalid file type. Please upload a PDF or DOCX file' };
    }

    return { valid: true };
  };

  // Handle file selection
  const handleFileSelect = (file) => {
    setUploadError('');
    setUploadSuccess(false);
    setUploadedData(null);

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

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setUploadError('');
    setUploadSuccess(false);

    try {
      const formData = new FormData();
      formData.append('resume', selectedFile);

      const response = await fetch('http://localhost:5000/api/resume-upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setUploadSuccess(true);
        setUploadedData(data);
        setSelectedFile(null);
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        setUploadError(data.message || 'Failed to upload resume');
      }
    } catch (error) {
      console.error('Error uploading resume:', error);
      setUploadError('Failed to connect to server. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle remove selected file
  const handleRemoveFile = () => {
    setSelectedFile(null);
    setUploadError('');
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
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow">
            <div className="card-header bg-success text-white">
              <h3 className="mb-0">Upload Resume</h3>
              <p className="mb-0 small">Upload your resume for job matching analysis</p>
            </div>
            <div className="card-body">
              {uploadSuccess && uploadedData && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                  <strong>Success!</strong> Resume uploaded successfully.
                  <ul className="mb-0 mt-2">
                    <li>Filename: {uploadedData.filename}</li>
                    <li>File type: {uploadedData.file_type.toUpperCase()}</li>
                    <li>Text extracted: {uploadedData.text_length} characters</li>
                  </ul>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setUploadSuccess(false)}
                    aria-label="Close"
                  ></button>
                </div>
              )}

              {uploadError && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                  <strong>Error!</strong> {uploadError}
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setUploadError('')}
                    aria-label="Close"
                  ></button>
                </div>
              )}

              {/* Drag and Drop Zone */}
              <div
                className={`border rounded p-5 text-center mb-3 ${
                  isDragging ? 'border-primary bg-light' : 'border-secondary'
                } ${selectedFile ? 'border-success' : ''}`}
                onDragEnter={handleDragEnter}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  minHeight: '200px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center'
                }}
                onClick={() => !selectedFile && fileInputRef.current?.click()}
              >
                {selectedFile ? (
                  <div>
                    <i className="bi bi-file-earmark-check text-success" style={{ fontSize: '3rem' }}></i>
                    <h5 className="mt-3 text-success">File Selected</h5>
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
                      Remove File
                    </button>
                  </div>
                ) : (
                  <div>
                    <i className="bi bi-cloud-upload" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
                    <h5 className="mt-3">Drag & Drop your resume here</h5>
                    <p className="text-muted">or click to browse</p>
                    <p className="text-muted small">Supported formats: PDF, DOCX (Max 10MB)</p>
                  </div>
                )}
              </div>

              {/* Hidden File Input */}
              <input
                ref={fileInputRef}
                type="file"
                className="d-none"
                accept=".pdf,.docx"
                onChange={handleFileInputChange}
              />

              {/* Upload Button */}
              <div className="d-grid gap-2">
                <button
                  type="button"
                  className="btn btn-success btn-lg"
                  onClick={handleUpload}
                  disabled={!selectedFile || isUploading}
                >
                  {isUploading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-upload me-2"></i>
                      Upload Resume
                    </>
                  )}
                </button>
              </div>

              {/* Info Section */}
              <div className="mt-4">
                <h6 className="text-muted">Why upload your resume?</h6>
                <ul className="text-muted small">
                  <li>Extract keywords from your resume to match against job descriptions</li>
                  <li>Identify missing skills and get optimization recommendations</li>
                  <li>Improve your job matching score based on your actual experience</li>
                  <li>Your resume data is processed securely and stored temporarily</li>
                </ul>
              </div>

              {/* Preview extracted text if available */}
              {uploadedData && uploadedData.text_preview && (
                <div className="mt-4">
                  <h6>Text Preview:</h6>
                  <div className="border rounded p-3 bg-light" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    <pre className="mb-0 small" style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                      {uploadedData.text_preview}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeUpload;
