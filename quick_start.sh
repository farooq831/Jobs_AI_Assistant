#!/bin/bash

# AI Job Application Assistant - Quick Start Script
# This script starts both backend and frontend servers

echo "============================================"
echo "  AI Job Application Assistant"
echo "  Starting Application..."
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed!${NC}"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}WARNING: Flask is not installed!${NC}"
    echo "Please run: pip3 install -r requirements.txt"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}WARNING: Node.js is not installed!${NC}"
    echo "Frontend will not be available."
    echo "Backend will start on port 5000 only."
    FRONTEND_AVAILABLE=false
else
    FRONTEND_AVAILABLE=true
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data uploads

# Start backend server in background
echo ""
echo -e "${GREEN}Starting Backend Server...${NC}"
python3 backend/app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
echo "Backend logs: backend.log"

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Backend server started successfully on http://localhost:5000${NC}"
else
    echo -e "${RED}✗ Backend server failed to start. Check backend.log for errors.${NC}"
    exit 1
fi

# Start frontend if Node.js is available
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo ""
    echo -e "${GREEN}Starting Frontend Server...${NC}"
    
    # Check if node_modules exists in frontend
    if [ ! -d "frontend/node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        cd frontend
        npm install > ../frontend_install.log 2>&1
        cd ..
    fi
    
    cd frontend
    npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    echo "Frontend PID: $FRONTEND_PID"
    echo "Frontend logs: frontend.log"
    
    sleep 3
    
    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${GREEN}✓ Frontend server started successfully on http://localhost:3000${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend server may have issues. Check frontend.log for details.${NC}"
    fi
fi

# Display access information
echo ""
echo "============================================"
echo -e "${GREEN}  Application Started Successfully!${NC}"
echo "============================================"
echo ""
echo "Access Points:"
echo "  • Backend API:  http://localhost:5000"
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "  • Frontend UI:  http://localhost:3000"
fi
echo ""
echo "Process IDs:"
echo "  • Backend:  $BACKEND_PID"
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "  • Frontend: $FRONTEND_PID"
fi
echo ""
echo "Log Files:"
echo "  • Backend:  backend.log"
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "  • Frontend: frontend.log"
fi
echo ""
echo "To stop the application:"
echo "  kill $BACKEND_PID"
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "  kill $FRONTEND_PID"
fi
echo ""
echo "Or press Ctrl+C and then run:"
echo "  pkill -f 'python3 backend/app.py'"
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "  pkill -f 'react-scripts start'"
fi
echo ""
echo "============================================"
echo "Opening application in browser..."
echo "============================================"

# Try to open browser
if [ "$FRONTEND_AVAILABLE" = true ]; then
    sleep 5
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    elif command -v open &> /dev/null; then
        open http://localhost:3000
    else
        echo "Please manually open: http://localhost:3000"
    fi
else
    echo "Please manually open: http://localhost:5000"
fi

# Keep script running
echo ""
echo "Press Ctrl+C to stop all servers..."
wait
