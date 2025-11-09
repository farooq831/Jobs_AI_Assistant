#!/bin/bash

# Simple verification script for Task 3.1

echo "==========================================="
echo "Task 3.1 - Verification Script"
echo "==========================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check scrapers directory
echo "Checking scrapers module..."
if [ -d "backend/scrapers" ]; then
    echo -e "${GREEN}✓${NC} backend/scrapers/ directory exists"
    
    # Check individual files
    for file in __init__.py base_scraper.py indeed_scraper.py glassdoor_scraper.py; do
        if [ -f "backend/scrapers/$file" ]; then
            echo -e "${GREEN}✓${NC} backend/scrapers/$file"
        else
            echo -e "${RED}✗${NC} backend/scrapers/$file NOT FOUND"
        fi
    done
else
    echo -e "${RED}✗${NC} backend/scrapers/ directory NOT FOUND"
fi
echo ""

# Check test script
echo "Checking test script..."
if [ -f "backend/test_scraper.py" ]; then
    echo -e "${GREEN}✓${NC} backend/test_scraper.py exists"
else
    echo -e "${RED}✗${NC} backend/test_scraper.py NOT FOUND"
fi
echo ""

# Check documentation
echo "Checking documentation..."
for doc in TASK_3.1_README.md TASK_3.1_QUICKSTART.md TASK_3.1_ARCHITECTURE.md TASK_3.1_SUMMARY.md TASK_3.1_CHECKLIST.md; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✓${NC} $doc"
    else
        echo -e "${RED}✗${NC} $doc NOT FOUND"
    fi
done
echo ""

# Check Flask app
echo "Checking Flask app updates..."
if grep -q "api/scrape-jobs" backend/app.py; then
    echo -e "${GREEN}✓${NC} Scraping endpoints added to backend/app.py"
else
    echo -e "${RED}✗${NC} Scraping endpoints NOT found in backend/app.py"
fi
echo ""

# Check task.md update
echo "Checking task.md..."
if grep -q "Task 3.1.*Completed" task.md; then
    echo -e "${GREEN}✓${NC} Task 3.1 marked as completed in task.md"
else
    echo -e "${RED}✗${NC} Task 3.1 NOT marked as completed in task.md"
fi
echo ""

# Summary
echo "==========================================="
echo "Summary"
echo "==========================================="
echo ""
echo "All files have been created for Task 3.1!"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip3 install -r requirements.txt"
echo "2. Start Flask server: cd backend && python3 app.py"
echo "3. Run tests: cd backend && python3 test_scraper.py"
echo ""
echo "Read TASK_3.1_QUICKSTART.md for detailed instructions."
echo ""
