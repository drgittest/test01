#!/bin/bash

# Test Runner Script for Order Management System
# This script runs all tests in the correct order

echo "🚀 Starting Test Suite for Order Management System"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the project root."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected."
    echo "   Make sure you have activated your virtual environment."
fi

# Function to check if server is running
check_server() {
    curl -s http://localhost:8000 > /dev/null 2>&1
    return $?
}

# Function to run tests with status
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo ""
    echo "📋 Running: $test_name"
    echo "Command: $command"
    echo "----------------------------------------"
    
    if eval "$command"; then
        echo "✅ $test_name - PASSED"
        return 0
    else
        echo "❌ $test_name - FAILED"
        return 1
    fi
}

# Track results
pytest_passed=false
integration_passed=false
visual_passed=false

# 1. Run pytest tests (test_main.py)
echo ""
echo "Step 1: Running pytest tests..."
if run_test "Pytest Tests" "python -m pytest test_main.py -v"; then
    pytest_passed=true
fi

# 2. Check server status
echo ""
echo "Step 2: Checking server status..."
if check_server; then
    echo "✅ Server is running on port 8000"
    
    # 3. Run integration tests
    echo ""
    echo "Step 3: Running integration tests..."
    if run_test "Integration Tests" "python tests/integration_test.py"; then
        integration_passed=true
    fi
    
    # 4. Run visual regression tests
    echo ""
    echo "Step 4: Running visual regression tests..."
    if run_test "Visual Tests" "cd tests/visual && python simple_visual_test.py"; then
        visual_passed=true
    fi
else
    echo "⚠️  Server not running on port 8000"
    echo "   Please start the server with: uvicorn main:app --reload --port 8000"
    echo "   Then run this script again."
fi

# Summary
echo ""
echo "=================================================="
echo "📊 TEST SUMMARY"
echo "=================================================="

echo "Pytest Tests:        $([ "$pytest_passed" = true ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "Integration Tests:   $([ "$integration_passed" = true ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "Visual Tests:        $([ "$visual_passed" = true ] && echo "✅ PASSED" || echo "❌ FAILED")"

# Count passed tests
passed=0
[ "$pytest_passed" = true ] && ((passed++))
[ "$integration_passed" = true ] && ((passed++))
[ "$visual_passed" = true ] && ((passed++))

echo ""
echo "Overall: $passed/3 test suites passed"

if [ $passed -eq 3 ]; then
    echo "🎉 All tests passed! Your application is ready for production."
    exit 0
else
    echo "⚠️  Some tests failed. Please review the output above."
    exit 1
fi 