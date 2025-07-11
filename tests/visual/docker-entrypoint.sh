#!/bin/bash
# Docker entrypoint script for visual regression tests

set -e

# Function to check if server is running
check_server() {
    local url="$1"
    local max_attempts=30
    local attempt=1
    
    echo "Checking if server is available at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✓ Server is available at $url"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: Server not ready, waiting..."
        sleep 2
        ((attempt++))
    done
    
    echo "✗ Server is not available after $max_attempts attempts"
    return 1
}

# Function to start the application server
start_server() {
    echo "Starting application server..."
    
    # Check if we need to run database migrations
    if [ -f "alembic.ini" ]; then
        echo "Running database migrations..."
        alembic upgrade head
    fi
    
    # Start the FastAPI server in background
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Check if server is running
    if ! check_server "http://localhost:8000"; then
        echo "✗ Failed to start application server"
        exit 1
    fi
    
    return 0
}

# Function to run visual tests
run_visual_tests() {
    echo "Running visual regression tests..."
    
    cd /app/tests/visual
    
    # Set test environment variables
    export VISUAL_TEST_ENV="ci"
    export VISUAL_TEST_BASE_URL="http://localhost:8000"
    export VISUAL_TEST_HEADLESS="1"
    export VISUAL_TEST_CI="1"
    
    # Create test data if needed
    if [ -f "test_data_manager.py" ]; then
        echo "Creating test data..."
        python test_data_manager.py generate --users 3 --orders 10 --force
        python test_data_manager.py seed --force
    fi
    
    # Generate baselines if they don't exist
    if [ ! -d "baseline" ] || [ -z "$(ls -A baseline)" ]; then
        echo "Creating baseline images..."
        python baseline_manager.py generate
    fi
    
    # Run comprehensive visual tests
    echo "Running comprehensive visual tests..."
    python comprehensive_visual_test.py
    
    # Generate test reports
    echo "Generating test reports..."
    if [ -f "visual_test_reporter.py" ]; then
        # Get the latest session ID
        SESSION_ID=$(python -c "import sqlite3; conn = sqlite3.connect('reports/test_results.db'); cursor = conn.cursor(); cursor.execute('SELECT id FROM test_sessions ORDER BY started_at DESC LIMIT 1'); result = cursor.fetchone(); print(result[0] if result else 'unknown'); conn.close()")
        
        if [ "$SESSION_ID" != "unknown" ]; then
            python visual_test_reporter.py report "$SESSION_ID" --format both
            python visual_test_reporter.py ci-metrics "$SESSION_ID" --output reports/ci_metrics.json
        fi
    fi
    
    # Run baseline comparison
    if [ -f "baseline_comparator.py" ]; then
        echo "Running baseline comparison..."
        python baseline_comparator.py compare --report
    fi
    
    echo "Visual tests completed"
}

# Function to cleanup
cleanup() {
    echo "Cleaning up..."
    
    # Kill server if it's running
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    
    # Clean up test data
    if [ -f "test_data_manager.py" ]; then
        python test_data_manager.py cleanup 2>/dev/null || true
    fi
    
    # Clean up test isolation
    if [ -f "test_isolation_manager.py" ]; then
        python test_isolation_manager.py cleanup 2>/dev/null || true
    fi
}

# Set up trap for cleanup
trap cleanup EXIT

# Main execution
echo "🎨 Visual Test Docker Container Starting"
echo "====================================="

# Parse command line arguments
COMMAND="${1:-test}"

case "$COMMAND" in
    "test")
        echo "Running full visual test suite..."
        start_server
        run_visual_tests
        ;;
    "server")
        echo "Starting server only..."
        start_server
        # Keep container running
        wait $SERVER_PID
        ;;
    "baseline")
        echo "Generating baseline images..."
        start_server
        cd /app/tests/visual
        python baseline_manager.py generate
        ;;
    "report")
        echo "Generating reports only..."
        cd /app/tests/visual
        if [ -f "visual_test_reporter.py" ]; then
            SESSION_ID="${2:-latest}"
            if [ "$SESSION_ID" = "latest" ]; then
                SESSION_ID=$(python -c "import sqlite3; conn = sqlite3.connect('reports/test_results.db'); cursor = conn.cursor(); cursor.execute('SELECT id FROM test_sessions ORDER BY started_at DESC LIMIT 1'); result = cursor.fetchone(); print(result[0] if result else 'unknown'); conn.close()")
            fi
            python visual_test_reporter.py report "$SESSION_ID" --format both
        fi
        ;;
    "bash")
        echo "Starting bash shell..."
        exec /bin/bash
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Available commands: test, server, baseline, report, bash"
        exit 1
        ;;
esac

echo "🎉 Visual test container execution completed"
