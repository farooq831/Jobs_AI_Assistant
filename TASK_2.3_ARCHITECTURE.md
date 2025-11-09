# Task 2.3: Resume Upload Functionality - Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Frontend)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               React Application                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │          App.jsx (Main Container)               │  │  │
│  │  │  ┌─────────────────┐  ┌──────────────────────┐ │  │  │
│  │  │  │ UserDetailsForm │  │   ResumeUpload.jsx   │ │  │  │
│  │  │  │    Component    │  │     Component        │ │  │  │
│  │  │  └─────────────────┘  └──────────────────────┘ │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/CORS
                          │ (multipart/form-data)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Flask Backend (Python)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    app.py                              │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │           API Endpoints Layer                    │  │  │
│  │  │  • POST /api/resume-upload                       │  │  │
│  │  │  • GET  /api/resume/<id>                         │  │  │
│  │  │  • GET  /api/resume/<id>/full-text               │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         Business Logic Layer                     │  │  │
│  │  │  • allowed_file()                                │  │  │
│  │  │  • extract_text_from_pdf()                       │  │  │
│  │  │  • extract_text_from_docx()                      │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │           Data Storage Layer                     │  │  │
│  │  │  • resume_store {} (in-memory dict)              │  │  │
│  │  │  • uploads/ directory (file system)              │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ File I/O
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    File System                               │
│  • backend/uploads/sample_resume.pdf                         │
│  • backend/uploads/john_doe_resume.docx                      │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Components

#### ResumeUpload.jsx
```
ResumeUpload Component
├── State Management
│   ├── selectedFile (File | null)
│   ├── isDragging (boolean)
│   ├── isUploading (boolean)
│   ├── uploadSuccess (boolean)
│   ├── uploadError (string)
│   └── uploadedData (object | null)
│
├── Event Handlers
│   ├── handleFileSelect()
│   ├── handleFileInputChange()
│   ├── handleDragEnter()
│   ├── handleDragLeave()
│   ├── handleDragOver()
│   ├── handleDrop()
│   ├── handleUpload()
│   └── handleRemoveFile()
│
├── Validation Functions
│   ├── validateFile()
│   └── formatFileSize()
│
└── UI Elements
    ├── Drag-Drop Zone
    ├── File Input (hidden)
    ├── Upload Button
    ├── Success Alert
    ├── Error Alert
    ├── File Info Display
    └── Text Preview Section
```

### Backend Modules

#### app.py Structure
```
Flask Application
├── Configuration
│   ├── UPLOAD_FOLDER = 'uploads'
│   ├── ALLOWED_EXTENSIONS = {'pdf', 'docx'}
│   └── MAX_FILE_SIZE = 10MB
│
├── Data Stores
│   ├── user_details_store {}
│   └── resume_store {}
│
├── Utility Functions
│   ├── allowed_file()
│   ├── extract_text_from_pdf()
│   └── extract_text_from_docx()
│
└── API Routes
    ├── POST /api/resume-upload
    │   └── Upload, validate, and extract text
    ├── GET /api/resume/<id>
    │   └── Retrieve resume metadata
    └── GET /api/resume/<id>/full-text
        └── Retrieve full extracted text
```

## Data Flow

### Upload Flow
```
1. User Action
   └─> Drag & drop or click to select file

2. Frontend Validation
   ├─> Check file type (PDF/DOCX)
   ├─> Check file size (< 10MB)
   └─> Display error if invalid

3. File Upload
   ├─> Create FormData with file
   ├─> POST to /api/resume-upload
   └─> Show loading spinner

4. Backend Processing
   ├─> Receive multipart/form-data
   ├─> Validate file presence
   ├─> Validate file type
   ├─> Sanitize filename
   ├─> Read file stream
   ├─> Extract text (PDF or DOCX)
   ├─> Validate text length
   ├─> Save file to uploads/
   └─> Store metadata in resume_store

5. Response
   ├─> Return success with metadata
   ├─> Include text preview
   └─> Return resume_id

6. Frontend Update
   ├─> Display success message
   ├─> Show file details
   ├─> Show text preview
   └─> Clear file input
```

### Retrieval Flow
```
1. GET /api/resume/<id>
   ├─> Check if resume exists
   ├─> Return metadata + preview
   └─> Don't return full text

2. GET /api/resume/<id>/full-text
   ├─> Check if resume exists
   ├─> Return complete extracted text
   └─> Used for analysis
```

## Data Models

### Resume Store Structure
```python
resume_store = {
    1: {
        "filename": "john_doe_resume.pdf",
        "file_type": "pdf",
        "extracted_text": "Complete resume text here...",
        "text_length": 1234,
        "file_path": "uploads/john_doe_resume.pdf"
    },
    2: {
        "filename": "jane_smith_resume.docx",
        "file_type": "docx",
        "extracted_text": "Complete resume text here...",
        "text_length": 2345,
        "file_path": "uploads/jane_smith_resume.docx"
    }
}
```

### API Response Models

#### Upload Success Response
```json
{
  "success": true,
  "message": "Resume uploaded and processed successfully",
  "resume_id": 1,
  "filename": "john_doe_resume.pdf",
  "file_type": "pdf",
  "text_length": 1234,
  "text_preview": "First 200 characters..."
}
```

#### Error Response
```json
{
  "success": false,
  "message": "Invalid file type. Only PDF and DOCX files are allowed."
}
```

## Security Architecture

### File Upload Security
```
┌─────────────────────────────────────────┐
│        Security Layers                  │
├─────────────────────────────────────────┤
│ 1. File Type Validation                 │
│    ├─> Extension check (.pdf, .docx)    │
│    └─> MIME type validation             │
├─────────────────────────────────────────┤
│ 2. File Size Limitation                 │
│    └─> MAX_CONTENT_LENGTH = 10MB        │
├─────────────────────────────────────────┤
│ 3. Filename Sanitization                │
│    └─> secure_filename() from werkzeug  │
├─────────────────────────────────────────┤
│ 4. Content Validation                   │
│    └─> Minimum 50 characters            │
├─────────────────────────────────────────┤
│ 5. Error Handling                       │
│    └─> No system info in error messages │
└─────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React 18+**: Component framework
- **Bootstrap 5**: UI styling
- **Fetch API**: HTTP requests
- **HTML5 File API**: File handling
- **Drag and Drop API**: User interaction

### Backend
- **Flask 2.2.5**: Web framework
- **Flask-CORS 4.0.0**: Cross-origin support
- **PyPDF2 3.0.1**: PDF text extraction
- **python-docx 1.1.0**: DOCX text extraction
- **Werkzeug**: File handling utilities

### File Processing
- **PyPDF2**: Multi-page PDF reading
- **python-docx**: DOCX paragraph extraction
- **io.BytesIO**: Stream processing

## Performance Considerations

### Memory Management
```
File Upload (10MB max)
├─> Read as BytesIO stream
├─> Process in memory
├─> Extract text incrementally
└─> Store only extracted text (< 1MB typically)
```

### Scalability
```
Current: In-Memory Storage
├─> Suitable for development
├─> Limited to server memory
└─> Lost on server restart

Future: Database Storage
├─> Persistent storage
├─> Better for production
└─> Supports user sessions
```

## Error Handling Strategy

```
Error Types
├─> Client Errors (400)
│   ├─> No file provided
│   ├─> Invalid file type
│   ├─> File too large
│   └─> Insufficient text content
│
├─> Server Errors (500)
│   ├─> Extraction failures
│   ├─> File system errors
│   └─> Unexpected exceptions
│
└─> Not Found (404)
    └─> Resume ID not found
```

## Testing Architecture

```
Test Suite (test_resume_upload.py)
├─> Test 1: Health Check
│   └─> Verify backend is running
│
├─> Test 2: Valid PDF Upload
│   ├─> Generate test PDF
│   ├─> Upload via API
│   └─> Verify response
│
├─> Test 3: Missing File
│   └─> Verify 400 error
│
├─> Test 4: Invalid File Type
│   └─> Verify rejection
│
├─> Test 5: Resume Retrieval
│   └─> GET by ID
│
└─> Test 6: Full Text Retrieval
    └─> GET full content
```

## Integration Points

### Current Integrations
```
UserDetailsForm ─┐
                 ├─> App.jsx ─> Same Backend
ResumeUpload ────┘
```

### Future Integrations
```
Resume Upload
├─> Job Matching (Phase 5)
│   └─> Use extracted text for matching
│
├─> Resume Optimization (Phase 6)
│   ├─> Extract keywords
│   ├─> Compare with job requirements
│   └─> Generate recommendations
│
└─> Application Tracker (Phase 8)
    └─> Link resumes to applications
```

## Deployment Architecture

### Development
```
├─> Backend: localhost:5000
├─> Frontend: localhost:3000
└─> Storage: ./uploads/
```

### Production (Future)
```
├─> Backend: WSGI server (Gunicorn)
├─> Frontend: Static hosting (Nginx)
├─> Storage: AWS S3 or similar
└─> Database: PostgreSQL
```

## Monitoring & Logging

### Current Logging
- Flask debug mode
- Console errors
- HTTP status codes

### Future Enhancements
- Structured logging
- File upload metrics
- Error tracking (Sentry)
- Performance monitoring

---

**Architecture designed for scalability and maintainability.**
