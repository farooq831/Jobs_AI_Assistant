#!/bin/bash
# Setup script for Task 2.3: Resume Upload Functionality
# This script installs dependencies and verifies the setup

echo "=========================================="
echo "Task 2.3: Resume Upload Functionality Setup"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python3 is installed
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python3 found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python3 not found. Please install Python3."
    exit 1
fi

# Check if pip is available
echo ""
echo "Checking pip installation..."
if python3 -m pip --version &> /dev/null; then
    PIP_VERSION=$(python3 -m pip --version)
    echo -e "${GREEN}✓${NC} pip found: $PIP_VERSION"
else
    echo -e "${RED}✗${NC} pip not found. Please install pip:"
    echo "    Ubuntu/Debian: sudo apt install python3-pip"
    echo "    Fedora/RHEL: sudo dnf install python3-pip"
    echo "    macOS: python3 -m ensurepip --upgrade"
    exit 1
fi

# Check if Node.js is installed (for frontend)
echo ""
echo "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Node.js not found. You'll need it for the frontend."
    echo "    Please install from: https://nodejs.org/"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
echo "---------------------------------------"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment found"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠${NC} No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Install requirements
echo "Installing packages from requirements.txt..."
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python dependencies installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install Python dependencies"
    exit 1
fi

# Verify new dependencies
echo ""
echo "Verifying Task 2.3 dependencies..."
echo "---------------------------------------"

# Check PyPDF2
python3 -c "import PyPDF2" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} PyPDF2 installed"
else
    echo -e "${RED}✗${NC} PyPDF2 not found"
fi

# Check python-docx
python3 -c "import docx" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} python-docx installed"
else
    echo -e "${RED}✗${NC} python-docx not found"
fi

# Check Flask
python3 -c "import flask" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Flask installed"
else
    echo -e "${RED}✗${NC} Flask not found"
fi

# Check Flask-CORS
python3 -c "import flask_cors" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Flask-CORS installed"
else
    echo -e "${RED}✗${NC} Flask-CORS not found"
fi

# Create uploads directory
echo ""
echo "Creating uploads directory..."
mkdir -p backend/uploads
if [ -d "backend/uploads" ]; then
    echo -e "${GREEN}✓${NC} Uploads directory created"
else
    echo -e "${RED}✗${NC} Failed to create uploads directory"
fi

# Check if frontend dependencies are installed
echo ""
echo "Checking frontend dependencies..."
echo "---------------------------------------"

if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies already installed"
else
    echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed"
    echo "To install, run:"
    echo "    cd frontend && npm install"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
echo "Task 2.3 Components:"
echo "  • Backend endpoint: /api/resume-upload"
echo "  • Backend endpoint: /api/resume/<id>"
echo "  • Backend endpoint: /api/resume/<id>/full-text"
echo "  • Frontend component: ResumeUpload.jsx"
echo "  • Test suite: backend/test_resume_upload.py"
echo ""
echo "Next Steps:"
echo "  1. Start backend server:"
echo "     cd backend && python app.py"
echo ""
echo "  2. Start frontend (in another terminal):"
echo "     cd frontend && npm start"
echo ""
echo "  3. Run tests:"
echo "     python backend/test_resume_upload.py"
echo ""
echo "  4. Access the application:"
echo "     Frontend: http://localhost:3000"
echo "     Backend API: http://localhost:5000"
echo ""
echo -e "${GREEN}✓${NC} Setup complete! Read TASK_2.3_README.md for detailed documentation."
echo ""
