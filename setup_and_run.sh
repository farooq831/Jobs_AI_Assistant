#!/bin/bash

echo "=========================================="
echo "AI Job Assistant - Setup and Run Script"
echo "=========================================="
echo ""

# Check Python installation
echo "1. Checking Python installation..."
python3 --version

# Check if pip is available
echo ""
echo "2. Checking pip installation..."
if command -v pip3 &> /dev/null; then
    pip3 --version
elif python3 -m pip --version &> /dev/null; then
    echo "pip is available via python3 -m pip"
    alias pip3="python3 -m pip"
else
    echo "ERROR: pip is not installed!"
    echo "Please install pip first: sudo apt install python3-pip"
    exit 1
fi

# Install Python dependencies
echo ""
echo "3. Installing Python dependencies..."
pip3 install -r requirements.txt --user

# Check Node.js installation
echo ""
echo "4. Checking Node.js installation..."
if command -v node &> /dev/null; then
    node --version
    npm --version
else
    echo "WARNING: Node.js is not installed!"
    echo "Frontend will not be available without Node.js"
fi

# Install frontend dependencies if Node is available
if command -v npm &> /dev/null; then
    echo ""
    echo "5. Installing frontend dependencies..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    else
        echo "Frontend dependencies already installed"
    fi
    cd ..
fi

echo ""
echo "=========================================="
echo "Setup complete! Ready to run."
echo "=========================================="
echo ""
echo "To start the application:"
echo "1. Backend: python3 backend/app.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
