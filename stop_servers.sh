#!/bin/bash

# AI Job Application Assistant - Stop Script

echo "============================================"
echo "  Stopping AI Job Application Assistant"
echo "============================================"
echo ""

# Kill backend processes
echo "Stopping backend server..."
pkill -f "python3 backend/app.py" && echo "✓ Backend stopped" || echo "✗ No backend process found"

# Kill frontend processes
echo "Stopping frontend server..."
pkill -f "react-scripts start" && echo "✓ Frontend stopped" || echo "✗ No frontend process found"
pkill -f "node.*react-scripts" && echo "✓ Node processes stopped" || echo "✗ No node processes found"

# Kill any remaining Node processes related to the project
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "✓ Freed port 3000" || true
lsof -ti:5000 | xargs kill -9 2>/dev/null && echo "✓ Freed port 5000" || true

echo ""
echo "============================================"
echo "  All servers stopped"
echo "============================================"
