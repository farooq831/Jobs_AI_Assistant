#!/bin/bash

# Setup script for Task 2.1: User Detail Input Forms
# This script sets up both backend and frontend components

echo "=========================================="
echo "Task 2.1 Setup: User Detail Input Forms"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the Jobs_AI_Assistant directory"
    exit 1
fi

# Setup Backend
echo "Setting up Backend..."
echo "--------------------"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Backend setup complete!"
echo ""

# Setup Frontend
echo "Setting up Frontend..."
echo "--------------------"

cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Warning: Node.js is not installed"
    echo "Please install Node.js (version 16 or higher) from https://nodejs.org/"
    echo "After installing Node.js, run: cd frontend && npm install"
    cd ..
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Warning: npm is not installed"
    echo "npm should come with Node.js. Please reinstall Node.js"
    cd ..
    exit 1
fi

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo ""

# Install npm dependencies
if [ -f "package.json" ]; then
    echo "Installing npm dependencies..."
    npm install
    echo "✓ Frontend setup complete!"
else
    echo "Error: package.json not found in frontend directory"
    cd ..
    exit 1
fi

cd ..

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To run the application:"
echo ""
echo "1. Start the Backend (Terminal 1):"
echo "   cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant"
echo "   source venv/bin/activate"
echo "   cd backend"
echo "   python app.py"
echo ""
echo "2. Start the Frontend (Terminal 2):"
echo "   cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant/frontend"
echo "   npm start"
echo ""
echo "3. Test the API (Terminal 3):"
echo "   cd /home/farooq/AI_Cyber_Guard/Jobs_AI_Assistant"
echo "   source venv/bin/activate"
echo "   cd backend"
echo "   python test_api.py"
echo ""
echo "The application will be available at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:5000"
echo ""
