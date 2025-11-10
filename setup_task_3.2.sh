#!/bin/bash

# Setup script for Task 3.2: Dynamic Scraping using Selenium
# This script installs Chrome/Chromium browser and ChromeDriver

echo "======================================================================"
echo "Task 3.2: Dynamic Scraping using Selenium - Setup"
echo "======================================================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  This script is designed for Linux systems."
    echo "   For other operating systems, please install Chrome and ChromeDriver manually."
    echo ""
    echo "   ChromeDriver download: https://chromedriver.chromium.org/downloads"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Step 1: Checking system requirements..."
echo "----------------------------------------------------------------------"

# Check if Chrome/Chromium is installed
if command_exists google-chrome; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✓ Google Chrome is installed: $CHROME_VERSION"
elif command_exists chromium-browser; then
    CHROME_VERSION=$(chromium-browser --version)
    echo "✓ Chromium is installed: $CHROME_VERSION"
elif command_exists chromium; then
    CHROME_VERSION=$(chromium --version)
    echo "✓ Chromium is installed: $CHROME_VERSION"
else
    echo "✗ Chrome/Chromium not found. Installing Chromium..."
    
    # Detect package manager
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y chromium-browser
    elif command_exists yum; then
        sudo yum install -y chromium
    elif command_exists dnf; then
        sudo dnf install -y chromium
    else
        echo "✗ Could not detect package manager. Please install Chrome/Chromium manually."
        exit 1
    fi
    
    if command_exists chromium-browser || command_exists chromium; then
        echo "✓ Chromium installed successfully"
    else
        echo "✗ Failed to install Chromium"
        exit 1
    fi
fi

echo ""
echo "Step 2: Installing ChromeDriver..."
echo "----------------------------------------------------------------------"

# Check if chromedriver is already installed
if command_exists chromedriver; then
    CHROMEDRIVER_VERSION=$(chromedriver --version)
    echo "✓ ChromeDriver is already installed: $CHROMEDRIVER_VERSION"
else
    echo "Installing ChromeDriver..."
    
    # Install chromedriver based on package manager
    if command_exists apt-get; then
        sudo apt-get install -y chromium-chromedriver
        
        # Create symlink if needed
        if [ ! -f /usr/bin/chromedriver ] && [ -f /usr/lib/chromium-browser/chromedriver ]; then
            sudo ln -s /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
        fi
    elif command_exists yum; then
        sudo yum install -y chromedriver
    elif command_exists dnf; then
        sudo dnf install -y chromedriver
    else
        echo "⚠️  Could not automatically install ChromeDriver."
        echo "   Please install it manually from: https://chromedriver.chromium.org/downloads"
        exit 1
    fi
    
    if command_exists chromedriver; then
        echo "✓ ChromeDriver installed successfully"
    else
        echo "✗ Failed to install ChromeDriver"
        echo "   Try manual installation: https://chromedriver.chromium.org/downloads"
        exit 1
    fi
fi

echo ""
echo "Step 3: Verifying Python dependencies..."
echo "----------------------------------------------------------------------"

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not activated"
    echo "   It's recommended to activate your virtual environment first:"
    echo "   source venv/bin/activate"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if selenium is installed
if python3 -c "import selenium" 2>/dev/null; then
    SELENIUM_VERSION=$(python3 -c "import selenium; print(selenium.__version__)")
    echo "✓ Selenium is installed (version $SELENIUM_VERSION)"
else
    echo "Installing Selenium..."
    pip install selenium==4.11.2
    
    if python3 -c "import selenium" 2>/dev/null; then
        echo "✓ Selenium installed successfully"
    else
        echo "✗ Failed to install Selenium"
        exit 1
    fi
fi

# Check if all required packages are installed
echo ""
echo "Checking other dependencies..."
REQUIRED_PACKAGES=("flask" "beautifulsoup4" "lxml" "requests")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "  ✓ $package"
    else
        echo "  ✗ $package (missing)"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo "Installing missing packages from requirements.txt..."
    pip install -r requirements.txt
fi

echo ""
echo "Step 4: Testing ChromeDriver setup..."
echo "----------------------------------------------------------------------"

# Create a simple test script
cat > /tmp/test_chromedriver.py << 'EOF'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com')
    print("✓ ChromeDriver test successful!")
    print(f"  Page title: {driver.title}")
    driver.quit()
    exit(0)
except Exception as e:
    print(f"✗ ChromeDriver test failed: {str(e)}")
    exit(1)
EOF

# Run the test
python3 /tmp/test_chromedriver.py
TEST_RESULT=$?

# Clean up test file
rm /tmp/test_chromedriver.py

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✓ Setup completed successfully!"
    echo "======================================================================"
    echo ""
    echo "What's next?"
    echo ""
    echo "1. Run the test suite:"
    echo "   python backend/test_selenium_scraper.py"
    echo ""
    echo "2. Start the Flask backend:"
    echo "   python backend/app.py"
    echo ""
    echo "3. Test the Selenium scraping endpoint:"
    echo "   curl -X POST http://localhost:5000/api/scrape-jobs-dynamic \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"job_titles\":[\"Software Engineer\"],\"location\":\"New York\",\"num_pages\":1}'"
    echo ""
    echo "4. Read the documentation:"
    echo "   - TASK_3.2_README.md - Complete documentation"
    echo "   - TASK_3.2_QUICKSTART.md - Quick start guide"
    echo "   - TASK_3.2_ARCHITECTURE.md - Architecture details"
    echo ""
    echo "======================================================================"
    exit 0
else
    echo ""
    echo "======================================================================"
    echo "✗ Setup completed with errors"
    echo "======================================================================"
    echo ""
    echo "ChromeDriver test failed. This could be due to:"
    echo "1. ChromeDriver version mismatch with Chrome/Chromium"
    echo "2. Missing system dependencies"
    echo "3. Permission issues"
    echo ""
    echo "Troubleshooting:"
    echo "- Check Chrome version: google-chrome --version"
    echo "- Check ChromeDriver version: chromedriver --version"
    echo "- Ensure versions are compatible"
    echo "- Try installing manually: https://chromedriver.chromium.org/downloads"
    echo ""
    exit 1
fi
