#!/usr/bin/env python3
"""
Simplified script to create baseline screenshots for visual testing.
This script will take screenshots of the expected visual state
for comparison during automated visual testing.
"""

import os
import time
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SimpleBaselineScreenshotCreator:
    def __init__(self, base_url="http://127.0.0.1:8086"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent
        self.baseline_dir = self.test_dir / "baseline"
        self.baseline_dir.mkdir(exist_ok=True)
        
        # Setup Chrome options for consistent screenshots
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")  # Fixed window size
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-plugins")
        # Don't disable JavaScript - we need it for the modal
        
        self.driver = None
        
    def setup_driver(self):
        """Initialize the Chrome WebDriver."""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.implicitly_wait(10)
            print("✓ Chrome WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize Chrome WebDriver: {e}")
            return False
    
    def teardown_driver(self):
        """Clean up the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("✓ WebDriver cleaned up")
    
    def login(self, username="asdf2", password="asdf"):
        """Login to the application."""
        try:
            print(f"Logging in as {username}...")
            
            self.driver.get(f"{self.base_url}/login")
            
            # Fill login form
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            password_field.submit()
            
            # Wait for redirect to home page
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.current_url.endswith("/") or 
                             driver.current_url.endswith("/login")
            )
            
            # Check if login was successful
            if "login" not in self.driver.current_url:
                print("✓ Login successful")
                return True
            else:
                print("✗ Login failed - still on login page")
                return False
                
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    def take_screenshot(self, filename, description=""):
        """Take a screenshot and save it to baseline directory."""
        try:
            filepath = self.baseline_dir / filename
            self.driver.save_screenshot(str(filepath))
            print(f"✓ Baseline screenshot saved: {filename} - {description}")
            return filepath
        except Exception as e:
            print(f"✗ Failed to take screenshot {filename}: {e}")
            return None
    
    def create_orders_list_baseline(self):
        """Create baseline screenshot of the orders list page."""
        print("\n--- Creating Orders List Baseline Screenshot ---")
        try:
            # Navigate to orders page
            self.driver.get(f"{self.base_url}/orders")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Wait a bit more for any dynamic content
            time.sleep(3)
            
            # Take screenshot
            self.take_screenshot("expected_orders_list.png", "Orders list page baseline")
            
            print("✓ Orders list baseline screenshot created")
            return True
            
        except Exception as e:
            print(f"✗ Failed to create orders list baseline: {e}")
            return False
    
    def create_modal_baseline(self):
        """Create baseline screenshot of the modal in open state."""
        print("\n--- Creating Modal Baseline Screenshot ---")
        try:
            # Navigate to orders page
            self.driver.get(f"{self.base_url}/orders")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Wait for Alpine.js to load
            time.sleep(3)
            
            # Find and click on "View Details" button for first order
            view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            
            if not view_buttons:
                print("✗ No 'View Details' buttons found")
                return False
            
            # Click on first "View Details" button
            first_button = view_buttons[0]
            first_button.click()
            
            # Wait for modal to appear - look for the modal container
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".fixed.inset-0.z-50"))
            )
            
            # Wait a bit more for modal content to load
            time.sleep(3)
            
            # Take screenshot of modal
            self.take_screenshot("expected_modal_open.png", "Modal in open state baseline")
            
            print("✓ Modal baseline screenshot created")
            return True
            
        except TimeoutException:
            print("✗ Modal did not appear within timeout")
            return False
        except Exception as e:
            print(f"✗ Failed to create modal baseline: {e}")
            return False
    
    def create_mobile_baseline(self):
        """Create baseline screenshots for mobile viewport."""
        print("\n--- Creating Mobile Baseline Screenshots ---")
        try:
            # Set mobile viewport
            self.driver.set_window_size(375, 667)  # iPhone SE size
            
            # Orders list mobile
            self.driver.get(f"{self.base_url}/orders")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            time.sleep(3)
            self.take_screenshot("expected_orders_list_mobile.png", "Orders list mobile baseline")
            
            # Modal mobile
            view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            if view_buttons:
                first_button = view_buttons[0]
                first_button.click()
                
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".fixed.inset-0.z-50"))
                )
                time.sleep(3)
                self.take_screenshot("expected_modal_open_mobile.png", "Modal mobile baseline")
            
            print("✓ Mobile baseline screenshots created")
            return True
            
        except Exception as e:
            print(f"✗ Failed to create mobile baseline: {e}")
            return False
    
    def create_documentation(self):
        """Create documentation for the baseline screenshots."""
        print("\n--- Creating Baseline Documentation ---")
        
        doc_content = """# Baseline Screenshots for Visual Testing

This directory contains baseline screenshots used for automated visual testing of the order modal functionality.

## Screenshots

### Desktop (1920x1080)
- `expected_orders_list.png` - Orders list page in normal state
- `expected_modal_open.png` - Modal window in open state with order details

### Mobile (375x667 - iPhone SE)
- `expected_orders_list_mobile.png` - Orders list page on mobile viewport
- `expected_modal_open_mobile.png` - Modal window on mobile viewport

## Expected Visual State

### Orders List Page
- Clean table layout with order data
- Responsive design that adapts to screen size
- Proper spacing and typography
- No modal visible initially

### Modal Window
- Centered modal with backdrop
- Order details displayed in structured format
- Close button (X) in top-right corner
- Edit button for navigation to edit page
- Proper focus management and keyboard navigation

## Usage

These baseline screenshots are used by the automated visual testing suite to:
1. Compare current visual state against expected state
2. Detect visual regressions
3. Ensure consistent appearance across different environments
4. Validate responsive design behavior

## Regenerating Baselines

To regenerate these baseline screenshots:

```bash
cd tests/visual
python create_baseline_screenshots_simple.py
```

## Notes

- Screenshots are taken in headless Chrome with consistent settings
- Window size is fixed at 1920x1080 for desktop and 375x667 for mobile
- JavaScript is enabled for proper modal functionality
- Screenshots include the full page content for comprehensive comparison
"""
        
        doc_path = self.baseline_dir / "README.md"
        with open(doc_path, 'w') as f:
            f.write(doc_content)
        
        print("✓ Baseline documentation created")
        return True
    
    def run_all(self):
        """Run all baseline screenshot creation tasks."""
        print("🎨 Creating Baseline Screenshots for Visual Testing")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login first
            if not self.login():
                print("⚠️  Login failed, but continuing with public pages...")
            
            # Create all baseline screenshots
            success = True
            success &= self.create_orders_list_baseline()
            success &= self.create_modal_baseline()
            success &= self.create_mobile_baseline()
            success &= self.create_documentation()
            
            if success:
                print("\n🎉 All baseline screenshots created successfully!")
                print(f"📁 Baseline files saved in: {self.baseline_dir}")
                print("\n📋 Next steps:")
                print("1. Review the baseline screenshots")
                print("2. Run automated visual tests: python run_tests.py")
                print("3. Update baselines if needed after design changes")
            else:
                print("\n❌ Some baseline screenshots failed to create!")
                print("Check the error messages above.")
            
            return success
            
        finally:
            self.teardown_driver()

def main():
    """Main function to run baseline screenshot creation."""
    creator = SimpleBaselineScreenshotCreator()
    success = creator.run_all()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 