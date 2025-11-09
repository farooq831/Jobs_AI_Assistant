# Task 2.3: Resume Upload Functionality - Documentation

## Overview
Task 2.3 implements resume upload functionality with support for PDF and DOCX files, automatic text extraction, and server-side processing for job matching analysis.

## Completion Date
November 9, 2025

## Features Implemented

### Backend Features
1. **File Upload Endpoint** (`/api/resume-upload`)
   - Accepts PDF and DOCX file uploads
   - Maximum file size: 10MB
   - File type validation
   - Secure filename handling
   - Text extraction from uploaded files
   - Storage of resume data in memory

2. **Text Extraction**
   - PDF text extraction using PyPDF2
   - DOCX text extraction using python-docx
   - Validates minimum text content (50 characters)
   - Returns text preview and full text

3. **Resume Retrieval Endpoints**
   - `/api/resume/<id>` - Get resume metadata and preview
   - `/api/resume/<id>/full-text` - Get complete extracted text

### Frontend Features
1. **ResumeUpload Component**
   - Drag-and-drop file upload interface
   - Click-to-browse file selection
   - File type validation (PDF, DOCX only)
   - File size validation (max 10MB)
   - Upload progress indicator
   - Success/error notifications
   - Text preview display
   - Beautiful Bootstrap styling

2. **User Experience**
   - Visual feedback for drag-and-drop
   - File information display (name, size)
   - Remove file option before upload
   - Informative help text
   - Responsive design

## Files Created/Modified

### Created Files
1. **frontend/ResumeUpload.jsx**
   - React component for resume upload
   - Implements drag-and-drop and file selection
   - Client-side validation
   - API integration

2. **backend/test_resume_upload.py**
   - Comprehensive test suite for resume upload API
   - 6 different test scenarios
   - Automated PDF generation for testing
   - Tests validation, error handling, and data retrieval

### Modified Files
1. **requirements.txt**
   - Added PyPDF2==3.0.1 for PDF processing
   - Added python-docx==1.1.0 for DOCX processing

2. **backend/app.py**
   - Added resume upload endpoint
   - Added text extraction functions
   - Added resume retrieval endpoints
   - Added file validation utilities

3. **frontend/App.jsx**
   - Integrated ResumeUpload component
   - Added header section
   - Improved layout structure

4. **task.md**
   - Marked Task 2.3 as completed
   - Added deliverables documentation

## Setup Instructions

### 1. Install Python Dependencies
```bash
# If using a virtual environment (recommended)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install specific packages
pip install PyPDF2==3.0.1 python-docx==1.1.0 reportlab
```

### 2. Create Uploads Directory
The backend automatically creates the `uploads/` directory, but you can create it manually:
```bash
mkdir -p backend/uploads
```

### 3. Start Backend Server
```bash
cd backend
python app.py
```
The server will run on http://localhost:5000

### 4. Start Frontend Development Server
```bash
cd frontend
npm install  # If not already installed
npm start
```
The frontend will run on http://localhost:3000

## Testing

### Backend API Testing
Run the automated test suite:
```bash
cd backend
python test_resume_upload.py
```

This will test:
1. Backend health check
2. PDF file upload
3. Validation for missing files
4. Validation for invalid file types
5. Resume retrieval by ID
6. Full text retrieval

### Manual Frontend Testing
1. Open http://localhost:3000 in your browser
2. Scroll to the "Upload Resume" section
3. Try drag-and-drop with a PDF or DOCX file
4. Try clicking to browse and select a file
5. Click "Upload Resume" button
6. Verify success message and text preview

### Test Files
Create test files:
- **PDF**: Use any PDF resume or the test script generates one
- **DOCX**: Create a simple Word document with resume text

## API Endpoints

### POST /api/resume-upload
Upload a resume file for processing.

**Request:**
- Content-Type: multipart/form-data
- Field: `resume` (file)

**Response (Success - 201):**
```json
{
  "success": true,
  "message": "Resume uploaded and processed successfully",
  "resume_id": 1,
  "filename": "john_doe_resume.pdf",
  "file_type": "pdf",
  "text_length": 1234,
  "text_preview": "Sample Resume\nName: John Doe..."
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "message": "Invalid file type. Only PDF and DOCX files are allowed."
}
```

### GET /api/resume/<resume_id>
Get resume metadata and text preview.

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "resume_id": 1,
    "filename": "john_doe_resume.pdf",
    "file_type": "pdf",
    "text_length": 1234,
    "text_preview": "Sample Resume..."
  }
}
```

### GET /api/resume/<resume_id>/full-text
Get complete extracted text from resume.

**Response (Success - 200):**
```json
{
  "success": true,
  "resume_id": 1,
  "extracted_text": "Complete resume text here..."
}
```

## File Structure
```
Jobs_AI_Assistant/
├── backend/
│   ├── app.py                     # Updated with resume endpoints
│   ├── test_resume_upload.py      # New test suite
│   └── uploads/                   # Auto-created directory for uploaded files
├── frontend/
│   ├── ResumeUpload.jsx           # New component
│   └── App.jsx                    # Updated to include ResumeUpload
├── requirements.txt               # Updated with new dependencies
└── task.md                        # Updated with completion status
```

## Validation Rules

### File Validation
- **Allowed types**: PDF (.pdf), DOCX (.docx)
- **Max file size**: 10 MB
- **Minimum text content**: 50 characters after extraction

### Text Extraction
- Extracts all text from PDF pages
- Extracts all paragraphs from DOCX
- Removes excessive whitespace
- Validates readable content

## Security Features
1. **Secure filename handling**: Uses `werkzeug.secure_filename()`
2. **File type validation**: Checks both extension and MIME type
3. **File size limit**: 10MB maximum to prevent abuse
4. **Content validation**: Ensures extracted text is meaningful
5. **Error handling**: Graceful error messages without exposing system details

## Next Steps (Future Enhancements)
1. **Database Storage**: Replace in-memory storage with SQLite/PostgreSQL
2. **User Association**: Link resumes to specific users
3. **Multiple Resumes**: Allow users to upload multiple resume versions
4. **File Deletion**: Add endpoint to delete uploaded resumes
5. **Text Analysis**: Implement keyword extraction and skill matching
6. **Resume Optimization**: Generate improvement suggestions
7. **File Preview**: Add PDF/DOCX preview in browser
8. **Cloud Storage**: Store files in AWS S3 or similar service

## Integration Points

### Current Integrations
- Integrates with UserDetailsForm in the main App
- Stores data in same backend as user details
- Uses same CORS configuration

### Future Integrations
- Will be used in Phase 5 (Job Matching and Scoring)
- Text will feed into Phase 6 (Resume Optimization)
- Keywords will be extracted for comparison with job descriptions

## Troubleshooting

### Issue: "Cannot connect to backend"
**Solution**: Ensure backend server is running on port 5000
```bash
cd backend
python app.py
```

### Issue: "Error extracting PDF text"
**Solution**: 
- Ensure PDF is not password-protected
- Try a different PDF file
- Check if PDF contains actual text (not just images)

### Issue: "Invalid file type"
**Solution**: 
- Only PDF and DOCX files are supported
- Check file extension is correct
- Ensure file is not corrupted

### Issue: "File size exceeds 10MB limit"
**Solution**: 
- Compress or reduce the file size
- Remove unnecessary images from the document

## Testing Checklist
- [x] Backend endpoints created and functional
- [x] PDF text extraction working
- [x] DOCX text extraction working
- [x] File validation working
- [x] Frontend component created
- [x] Drag-and-drop functionality working
- [x] File upload to backend working
- [x] Success/error notifications working
- [x] Text preview display working
- [x] Component integrated in main App
- [x] Test suite created and passing
- [x] Documentation completed

## Contributors
- GitHub Copilot (Implementation)
- Date: November 9, 2025

## Related Documentation
- See `TASK_2.1_README.md` for User Details Form documentation
- See `task.md` for overall project task breakdown
- See `backend/README.md` for backend setup instructions
- See `frontend/README.md` for frontend setup instructions
