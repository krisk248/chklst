#!/bin/bash

# Deployment Verification Script for chklst
# Checks all required components are in place

set -e  # Exit on error

echo "=========================================="
echo "chklst Deployment Verification"
echo "=========================================="
echo ""

# Check Python
echo "1. Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "   ERROR: Python 3 not found"
    exit 1
fi
python3 --version
echo "   OK"
echo ""

# Check Pipenv
echo "2. Checking Pipenv..."
if ! command -v pipenv &> /dev/null; then
    echo "   ERROR: Pipenv not found"
    exit 1
fi
pipenv --version
echo "   OK"
echo ""

# Check Node
echo "3. Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "   ERROR: Node.js not found"
    exit 1
fi
node --version
echo "   OK"
echo ""

# Check npm
echo "4. Checking npm..."
if ! command -v npm &> /dev/null; then
    echo "   ERROR: npm not found"
    exit 1
fi
npm --version
echo "   OK"
echo ""

# Check required files
echo "5. Checking required files..."
files=(
    "app.py"
    "Pipfile"
    "README.md"
    "run_tests.py"
    "backend/main.py"
    "backend/database.py"
    "backend/config.py"
    "frontend/package.json"
    "frontend/src/App.vue"
    "tests/conftest.py"
    "PHASE_8_SUMMARY.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ MISSING: $file"
        exit 1
    fi
done
echo ""

# Check About page
echo "6. Checking About page (Kannan attribution)..."
if grep -q "Kannan" frontend/src/views/AboutView.vue; then
    echo "   ✓ Developer name 'Kannan' found in About page"
else
    echo "   ✗ ERROR: 'Kannan' not found in About page"
    exit 1
fi
echo ""

# Check Pipfile dependencies
echo "7. Checking Pipfile dependencies..."
required_packages=("fastapi" "uvicorn" "sqlalchemy" "pydantic" "pytest")
for package in "${required_packages[@]}"; do
    if grep -q "$package" Pipfile; then
        echo "   ✓ $package"
    else
        echo "   ✗ MISSING: $package"
        exit 1
    fi
done
echo ""

# Check Python environment
echo "8. Checking Python environment..."
if pipenv --venv &> /dev/null; then
    echo "   ✓ Virtual environment exists"
else
    echo "   ⚠ Warning: Virtual environment not initialized"
    echo "     Run: pipenv install"
fi
echo ""

# Check frontend dependencies
echo "9. Checking frontend dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo "   ✓ Node modules installed"
else
    echo "   ⚠ Warning: Node modules not installed"
    echo "     Run: cd frontend && npm install && cd .."
fi
echo ""

# Check frontend build
echo "10. Checking frontend build..."
if [ -d "frontend/dist" ]; then
    echo "   ✓ Frontend built (dist directory exists)"
else
    echo "   ⚠ Info: Frontend not built yet"
    echo "     Run: cd frontend && npm run build && cd .."
fi
echo ""

# Summary
echo "=========================================="
echo "Deployment Verification Summary"
echo "=========================================="
echo ""
echo "✓ All required files present"
echo "✓ About page contains 'Kannan' attribution"
echo "✓ Project structure verified"
echo "✓ Dependencies documented"
echo ""
echo "To start the application:"
echo "  Development:  pipenv run python app.py --dev"
echo "  Production:   pipenv run python app.py"
echo ""
echo "To run tests:"
echo "  pipenv run python run_tests.py"
echo ""
echo "=========================================="
