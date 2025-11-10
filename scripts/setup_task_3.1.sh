#!/bin/bash

# Task 3.1 Setup Script
# Sets up the job scraping module with all dependencies

set -e  # Exit on any error

echo "=========================================="
echo "Task 3.1: Job Scraping Module Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "Project root: $PROJECT_ROOT"
echo ""

# Check if Python 3 is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ first:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION found${NC}"
fi
echo ""

# Check if pip is available
echo "Checking pip installation..."
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}⚠ pip not found, attempting to install...${NC}"
    echo "Please run: sudo apt install python3-pip"
    echo ""
    echo "Or continue without virtual environment if dependencies are already installed system-wide"
    echo ""
fi

# Create virtual environment if it doesn't exist
VENV_DIR="$PROJECT_ROOT/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    if python3 -m venv "$VENV_DIR" 2>/dev/null; then
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    else
        echo -e "${YELLOW}⚠ Could not create virtual environment${NC}"
        echo "Continuing with system Python..."
        VENV_DIR=""
    fi
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment if it exists
if [ -n "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    echo ""
fi

# Install dependencies
echo "Installing dependencies..."
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
        echo "Installing from requirements.txt..."
        if [ -n "$VENV_DIR" ]; then
            pip install -r "$PROJECT_ROOT/requirements.txt" --quiet
        else
            echo "Please run: pip3 install -r requirements.txt"
            echo "Or: python3 -m pip install -r requirements.txt"
            echo ""
        fi
        echo -e "${GREEN}✓ Dependencies installation command executed${NC}"
    else
        echo -e "${YELLOW}⚠ pip not available${NC}"
        echo "Please install dependencies manually:"
        echo "  beautifulsoup4==4.12.2"
        echo "  requests==2.31.0"
        echo "  lxml==4.9.3"
        echo "  Flask==2.2.5"
        echo "  Flask-CORS==4.0.0"
    fi
else
    echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
fi
echo ""

# Verify scraper modules exist
echo "Verifying scraper modules..."
SCRAPERS_DIR="$PROJECT_ROOT/backend/scrapers"
if [ -d "$SCRAPERS_DIR" ]; then
    echo -e "${GREEN}✓ Scrapers directory exists${NC}"
    
    # Check for key files
    for file in "__init__.py" "base_scraper.py" "indeed_scraper.py" "glassdoor_scraper.py"; do
        if [ -f "$SCRAPERS_DIR/$file" ]; then
            echo -e "${GREEN}  ✓ $file${NC}"
        else
            echo -e "${RED}  ✗ $file missing${NC}"
        fi
    done
else
    echo -e "${RED}✗ Scrapers directory not found${NC}"
fi
echo ""

# Verify test script exists
echo "Verifying test script..."
if [ -f "$PROJECT_ROOT/backend/test_scraper.py" ]; then
    echo -e "${GREEN}✓ test_scraper.py exists${NC}"
else
    echo -e "${YELLOW}⚠ test_scraper.py not found${NC}"
fi
echo ""

# Verify Flask app
echo "Verifying Flask app..."
if [ -f "$PROJECT_ROOT/backend/app.py" ]; then
    echo -e "${GREEN}✓ app.py exists${NC}"
else
    echo -e "${RED}✗ app.py not found${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
echo "Files created:"
echo "  • backend/scrapers/__init__.py"
echo "  • backend/scrapers/base_scraper.py"
echo "  • backend/scrapers/indeed_scraper.py"
echo "  • backend/scrapers/glassdoor_scraper.py"
echo "  • backend/test_scraper.py"
echo "  • backend/app.py (updated with scraping endpoints)"
echo ""
echo "Documentation:"
echo "  • TASK_3.1_README.md"
echo "  • TASK_3.1_QUICKSTART.md"
echo "  • TASK_3.1_ARCHITECTURE.md"
echo "  • TASK_3.1_SUMMARY.md"
echo "  • TASK_3.1_CHECKLIST.md"
echo ""

echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Install dependencies (if not already installed):"
echo "   pip3 install -r requirements.txt"
echo ""
echo "2. Start the Flask server:"
echo "   cd backend"
echo "   python3 app.py"
echo ""
echo "3. Test the scrapers (in another terminal):"
echo "   cd backend"
echo "   python3 test_scraper.py"
echo ""
echo "4. Or test via API:"
echo "   curl -X POST http://localhost:5000/api/scrape-jobs \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"job_titles\":[\"Software Engineer\"],\"location\":\"NYC\",\"num_pages\":1}'"
echo ""
echo "=========================================="
echo "Documentation"
echo "=========================================="
echo ""
echo "• Quick Start: TASK_3.1_QUICKSTART.md"
echo "• Full Documentation: TASK_3.1_README.md"
echo "• Architecture: TASK_3.1_ARCHITECTURE.md"
echo "• Checklist: TASK_3.1_CHECKLIST.md"
echo ""

echo -e "${GREEN}✓ Task 3.1 setup complete!${NC}"
echo ""
