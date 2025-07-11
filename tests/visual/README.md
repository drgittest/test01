# Visual Regression Testing Suite

## Overview

This comprehensive visual regression testing suite ensures UI consistency across all application pages and devices. The system provides automated screenshot comparison, baseline management, performance reporting, and CI/CD integration.

## Features

- **Comprehensive Page Coverage**: Tests all application pages (login, register, orders, modals, UI components)
- **Multi-Device Support**: Desktop, laptop, tablet, and mobile viewport testing
- **Advanced Baseline Management**: Versioned baselines with backup/restore capabilities
- **Performance Reporting**: Detailed HTML and JSON reports with metrics
- **CI/CD Integration**: Docker containerization and GitHub Actions workflow
- **Test Data Management**: Automated test data generation and isolation
- **Similarity Analysis**: Multiple comparison algorithms with configurable thresholds

## Architecture
- **Selenium WebDriver**: Browser automation for interaction testing
- **Pillow (PIL)**: Advanced image processing and comparison
- **ChromeDriver**: Chrome browser driver for Selenium
- **SQLite Database**: Test results and performance metrics storage
- **Jinja2 Templates**: HTML report generation
- **Docker**: Containerization for CI/CD
- **GitHub Actions**: Automated testing workflow

## Quick Start

### Prerequisites

1. **Python 3.9+** with required packages:
   ```bash
   pip install -r requirements.txt
   pip install selenium pillow jinja2 faker
   ```

2. **Chrome and ChromeDriver**:
   ```bash
   # macOS
   brew install chrome chromedriver
   
   # Linux
   sudo apt-get install chromium-browser chromium-chromedriver
   ```

3. **Application Server**: Ensure your FastAPI server is running on `http://localhost:8000`

### Running Tests

1. **Basic Test Run**:
   ```bash
   python comprehensive_visual_test.py
   ```

2. **Create Baseline Images** (first time setup):
   ```bash
   python comprehensive_visual_test.py --create-baselines
   ```

3. **Run with Specific Viewport**:
   ```bash
   python comprehensive_visual_test.py --viewport mobile
   ```

4. **Run in Visible Browser** (for debugging):
   ```bash
   python comprehensive_visual_test.py --no-headless
   ```

## Directory Structure

```
tests/visual/
├── README.md                      # This documentation
├── BASELINE_SYSTEM.md             # Baseline management documentation
├── 
├── # Core Test Framework
├── base_visual_test.py            # Base classes and utilities
├── comprehensive_visual_test.py   # Main test runner
├── 
├── # Page-Specific Tests
├── login_visual_test.py           # Login page tests
├── register_visual_test.py        # Registration page tests
├── orders_visual_test.py          # Orders list page tests
├── order_create_visual_test.py    # Order creation page tests
├── order_edit_visual_test.py      # Order editing page tests
├── enhanced_modal_visual_test.py  # Modal functionality tests
├── ui_components_visual_test.py   # UI components tests
├── 
├── # Infrastructure
├── baseline_manager.py            # Baseline creation and management
├── baseline_comparator.py         # Image comparison and analysis
├── visual_test_reporter.py        # Test reporting system
├── test_data_manager.py           # Test data generation
├── test_isolation_manager.py      # Test isolation and cleanup
├── 
├── # CI/CD Integration
├── Dockerfile.visual-tests        # Docker container for CI/CD
├── docker-entrypoint.sh           # Docker entrypoint script
├── 
├── # Test Assets
├── baseline/                      # Baseline images
├── screenshots/                   # Current test screenshots
├── diff/                         # Difference images
├── reports/                      # Generated reports
├── fixtures/                     # Test data fixtures
└── isolation/                    # Test isolation data
```

## Usage

### Running Visual Tests

#### 1. Simple Visual Regression Test
```bash
# Run the simplified test (recommended for CI/CD)
python simple_visual_test.py
```

This test:
- Takes a screenshot of the orders list page
- Compares it with the baseline
- Reports similarity percentage
- Saves difference image if significant differences found

#### 2. Comprehensive Modal Testing
```bash
# Run full modal interaction testing
python test_modal_design.py
```

This test:
- Tests modal opening/closing
- Validates modal content display
- Tests responsive behavior
- Generates detailed reports

#### 3. Test Runner
```bash
# Run all tests with the test runner
python run_tests.py
```

### Creating Baseline Screenshots

#### Manual Baseline Creation
```bash
# Create baseline screenshots manually
python create_manual_baseline.py
```

#### Automated Baseline Creation
```bash
# Create baseline screenshots automatically
python create_baseline_screenshots.py
```

## API Documentation

### SimpleVisualTest Class
```python
class SimpleVisualTest:
    """
    Simplified visual regression testing for orders list page
    """
    
    def __init__(self, base_url="http://localhost:8000"):
        """
        Initialize test with base URL
        
        Args:
            base_url (str): Base URL of the application
        """
    
    def take_screenshot(self, filename="orders_list.png"):
        """
        Take screenshot of orders list page
        
        Args:
            filename (str): Output filename for screenshot
        """
    
    def compare_with_baseline(self, actual_file, baseline_file="baseline/orders_list.png"):
        """
        Compare actual screenshot with baseline
        
        Args:
            actual_file (str): Path to actual screenshot
            baseline_file (str): Path to baseline screenshot
            
        Returns:
            float: Similarity percentage (0-100)
        """
```

### ModalDesignTest Class
```python
class ModalDesignTest:
    """
    Comprehensive modal interaction and visual testing
    """
    
    def test_modal_open_close(self):
        """Test modal opening and closing functionality"""
    
    def test_modal_content(self):
        """Test modal content display and formatting"""
    
    def test_modal_responsive(self):
        """Test modal responsive behavior"""
    
    def test_modal_accessibility(self):
        """Test modal accessibility features"""
```

## Configuration

### Test Configuration
```python
# Test configuration options
TEST_CONFIG = {
    'base_url': 'http://localhost:8000',
    'timeout': 10,
    'window_size': (1920, 1080),
    'screenshot_dir': 'screenshots',
    'baseline_dir': 'baseline',
    'similarity_threshold': 95.0  # Minimum similarity percentage
}
```

### Browser Configuration
```python
# Chrome options for consistent testing
CHROME_OPTIONS = [
    '--headless',           # Run in headless mode
    '--no-sandbox',         # Disable sandbox
    '--disable-dev-shm-usage',  # Disable shared memory
    '--window-size=1920,1080'   # Set window size
]
```

## Troubleshooting

### Common Issues

#### 1. ChromeDriver Not Found
```bash
# Error: chromedriver executable needs to be in PATH
# Solution: Install ChromeDriver
brew install chromedriver  # macOS
# or download from https://chromedriver.chromium.org/
```

#### 2. Connection Refused
```bash
# Error: Connection refused to localhost:8000
# Solution: Ensure FastAPI server is running
uvicorn main:app --reload --port 8000
```

#### 3. Authentication Required
```bash
# Error: Redirected to login page
# Solution: Update test credentials in test files
# or ensure user is logged in before running tests
```

#### 4. Screenshot Differences
```bash
# High difference percentage in visual tests
# Possible causes:
# - UI changes made to the application
# - Different screen resolutions
# - Browser updates affecting rendering
# - Dynamic content (timestamps, IDs)

# Solution: Update baseline screenshots
python create_baseline_screenshots.py
```

### Debug Mode
```python
# Enable debug mode for detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Disable headless mode to see browser actions
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--window-size=1920,1080'
    # Remove '--headless' to see browser window
]
```

## Best Practices

### 1. Baseline Management
- Update baselines when intentional UI changes are made
- Use consistent browser versions and screen resolutions
- Document baseline creation process

### 2. Test Reliability
- Use fixed window sizes for consistent results
- Implement proper waits for dynamic content
- Handle authentication consistently

### 3. Performance
- Run tests in headless mode for CI/CD
- Use appropriate timeouts
- Clean up temporary files

### 4. Maintenance
- Regular updates of ChromeDriver
- Monitor test stability
- Review and update test cases as needed

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Visual Tests
on: [push, pull_request]

jobs:
  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install selenium pillow fastapi uvicorn
      - name: Install ChromeDriver
        run: |
          sudo apt-get update
          sudo apt-get install -y chromium-chromedriver
      - name: Run visual tests
        run: |
          cd tests/visual
          python simple_visual_test.py
```

## Contributing

When adding new visual tests:
1. Follow the existing code structure
2. Add proper documentation
3. Include error handling
4. Update this README if needed
5. Test on different environments

## Support

For issues with visual testing:
1. Check the troubleshooting section
2. Review test logs and error messages
3. Verify environment setup
4. Test manually to reproduce issues 