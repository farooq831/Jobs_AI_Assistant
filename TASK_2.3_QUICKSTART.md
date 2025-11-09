# Task 2.3: Resume Upload - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.7+
- Node.js 14+
- pip (Python package manager)
- npm (Node package manager)

### Step 1: Install Dependencies (2 min)

```bash
# Run the automated setup script
cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant
./setup_task_2.3.sh
```

**OR manually:**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Start Backend (1 min)

```bash
# Terminal 1
cd backend
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 3: Start Frontend (1 min)

```bash
# Terminal 2 (new terminal)
cd frontend
npm start
```

Browser will automatically open to `http://localhost:3000`

### Step 4: Test the Feature (1 min)

1. **Scroll down** to "Upload Resume" section
2. **Drag & drop** a PDF or DOCX file, OR **click** to browse
3. **Click "Upload Resume"** button
4. **See success message** with extracted text preview

### Step 5: Run Tests (Optional)

```bash
# Terminal 3
python backend/test_resume_upload.py
```

Expected output: `🎉 All tests passed!`

---

## 📁 Test Files

### Create a Test PDF
1. Open any word processor
2. Type some resume content:
   ```
   John Doe
   Software Engineer
   Skills: Python, JavaScript, React
   Experience: 5 years
   ```
3. Save as PDF

### Create a Test DOCX
1. Open Microsoft Word or Google Docs
2. Type the same content
3. Save as .docx

---

## 🎯 What to Expect

### Frontend Features
- ✅ Drag and drop zone with visual feedback
- ✅ File information (name, size)
- ✅ Upload progress spinner
- ✅ Success message with details
- ✅ Text preview from uploaded file
- ✅ Error messages for invalid files

### Supported Files
- ✅ PDF files (.pdf)
- ✅ DOCX files (.docx)
- ❌ Max size: 10MB
- ❌ Other formats not supported

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill the process if needed
kill -9 <PID>

# Or use a different port
python app.py  # Edit to change port
```

### Frontend won't start?
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Can't upload files?
1. Check backend is running on port 5000
2. Check browser console for errors (F12)
3. Verify file is PDF or DOCX
4. Ensure file is under 10MB

### "Module not found" error?
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📊 API Endpoints

Test with curl:

```bash
# Upload a file
curl -X POST \
  http://localhost:5000/api/resume-upload \
  -F "resume=@path/to/your/resume.pdf"

# Get resume by ID
curl http://localhost:5000/api/resume/1

# Get full text
curl http://localhost:5000/api/resume/1/full-text
```

---

## 📖 Need More Help?

- **Full Documentation:** See `TASK_2.3_README.md`
- **API Details:** See `TASK_2.3_README.md` (API Endpoints section)
- **Checklist:** See `TASK_2.3_CHECKLIST.md`
- **Summary:** See `TASK_2.3_SUMMARY.md`

---

## ✅ Success Checklist

After completing the quick start, you should have:

- [ ] Backend running on http://localhost:5000
- [ ] Frontend running on http://localhost:3000
- [ ] Able to drag and drop files
- [ ] Able to upload PDF files
- [ ] Able to upload DOCX files
- [ ] See success messages after upload
- [ ] See text preview from uploaded files
- [ ] All tests passing (if you ran them)

---

**🎉 You're all set! Task 2.3 is complete and ready to use.**

**Next:** Move on to Task 3.1 - Static Scraping with BeautifulSoup
