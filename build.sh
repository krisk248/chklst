#!/bin/bash
# build.sh - Build frontend for production deployment

set -e  # Exit on any error

echo "Building chklst frontend..."

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "Error: frontend directory not found"
    exit 1
fi

# Check if npm/package.json exists
if [ ! -f "frontend/package.json" ]; then
    echo "Error: frontend/package.json not found"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
else
    echo "Frontend dependencies already installed"
fi

# Build frontend
echo "Building frontend with Vite..."
cd frontend
npm run build
cd ..

# Check if build was successful
if [ ! -d "frontend/dist" ]; then
    echo "Error: Frontend build failed - dist directory not created"
    exit 1
fi

echo "Build complete!"
echo "Frontend built successfully to frontend/dist/"
echo ""
echo "To run the application:"
echo "  Production mode: pipenv run python app.py"
echo "  Development mode: pipenv run python app.py --dev"
