#!/usr/bin/env python3
"""
Visual testing script for modal functionality using Selenium and PIL.
Tests the modal design and functionality across different scenarios.
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
from PIL import Image, ImageChops
import json

class ModalVisualTester:
    def __init__(self, base_url="http://127.0.0.1:8086"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent
        self.screenshots_dir = self.test_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-gpu")
        
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
        """Take a screenshot and save it."""
        try:
            filepath = self.screenshots_dir / filename
            self.driver.save_screenshot(str(filepath))
            print(f"✓ Screenshot saved: {filename} - {description}")
            return filepath
        except Exception as e:
            print(f"✗ Failed to take screenshot {filename}: {e}")
            return None
    
    def compare_images(self, expected_path, actual_path, diff_path=None):
        """Compare two images and return similarity percentage."""
        try:
            if not expected_path.exists():
                print(f"✗ Expected image not found: {expected_path}")
                return 0.0
            
            expected = Image.open(expected_path)
            actual = Image.open(actual_path)
            
            # Ensure both images have the same size
            if expected.size != actual.size:
                print(f"✗ Image sizes don't match: {expected.size} vs {actual.size}")
                return 0.0
            
            # Calculate difference
            diff = ImageChops.difference(expected, actual)
            
            # Calculate similarity percentage
            total_pixels = expected.size[0] * expected.size[1]
            diff_pixels = len(diff.getcolors()) if diff.getcolors() else 0
            similarity = ((total_pixels - diff_pixels) / total_pixels) * 100
            
            # Save diff image if requested
            if diff_path and diff.getbbox():
                diff.save(diff_path)
                print(f"✓ Difference image saved: {diff_path}")
            
            return similarity
            
        except Exception as e:
            print(f"✗ Image comparison failed: {e}")
            return 0.0
    
    def test_orders_page_load(self):
        """Test that the orders page loads correctly and matches baseline."""
        print("\n--- Testing Orders Page Load ---")
        try:
            self.driver.get(f"{self.base_url}/orders")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            assert "Order List" in self.driver.page_source
            assert "Alpine.js" in self.driver.page_source
            assert "Tailwind" in self.driver.page_source
            screenshot_path = self.take_screenshot("orders_page.png", "Orders page loaded")
            # Visual regression check
            baseline_path = self.screenshots_dir.parent / "baseline" / "expected_orders_list.png"
            diff_path = self.screenshots_dir / "diff_orders_page.png"
            similarity = self.compare_images(baseline_path, screenshot_path, diff_path)
            print(f"Visual similarity to baseline: {similarity:.2f}%")
            if similarity < 99.0:
                print(f"✗ Visual regression detected for orders list page! See diff: {diff_path}")
                return False
            print("✓ Orders page loaded and matches baseline")
            return True
        except Exception as e:
            print(f"✗ Orders page load failed: {e}")
            return False

    def test_modal_trigger(self):
        """Test that clicking on order rows triggers the modal and matches baseline."""
        print("\n--- Testing Modal Trigger ---")
        try:
            # Wait for Alpine.js to be ready
            time.sleep(3)
            
            # Find and click "View Details" button instead of table row
            view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            if not view_buttons:
                print("✗ No 'View Details' buttons found")
                return False
            first_button = view_buttons[0]
            first_button.click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "[x-show='isOpen'], [x-show='true']"))
            )
            screenshot_path = self.take_screenshot("modal_open.png", "Modal opened")
            # Visual regression check
            baseline_path = self.screenshots_dir.parent / "baseline" / "expected_modal_open.png"
            diff_path = self.screenshots_dir / "diff_modal_open.png"
            similarity = self.compare_images(baseline_path, screenshot_path, diff_path)
            print(f"Visual similarity to baseline: {similarity:.2f}%")
            if similarity < 99.0:
                print(f"✗ Visual regression detected for modal open! See diff: {diff_path}")
                return False
            print("✓ Modal triggered and matches baseline")
            return True
        except TimeoutException:
            print("✗ Modal did not appear within timeout")
            return False
        except Exception as e:
            print(f"✗ Modal trigger failed: {e}")
            return False

    def test_modal_content(self):
        """Test that modal displays order content correctly."""
        print("\n--- Testing Modal Content ---")
        try:
            # Wait for modal content to load (wait for loading to finish)
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "[x-show='loading']"))
            )
            
            # Wait a bit more for content to be fully loaded
            time.sleep(2)
            
            # Get modal content
            modal_content = self.driver.find_element(By.CSS_SELECTOR, ".fixed.inset-0.z-50")
            
            # Verify order fields are present
            expected_fields = ["Order ID", "Order Number", "Customer Name", "Item", "Quantity", "Price", "Status"]
            modal_text = modal_content.text
            for field in expected_fields:
                if field not in modal_text:
                    print(f"✗ Field '{field}' not found in modal")
                    print(f"Modal text: {modal_text[:200]}...")
                    return False
            
            # Take screenshot of modal with content
            self.take_screenshot("modal_with_content.png", "Modal with order content")
            
            print("✓ Modal content displayed correctly")
            return True
            
        except Exception as e:
            print(f"✗ Modal content test failed: {e}")
            return False
    
    def test_modal_close(self):
        """Test that modal can be closed properly."""
        print("\n--- Testing Modal Close ---")
        try:
            # Find and click close button (using Alpine.js @click)
            close_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]")
            close_button.click()
            
            # Wait for modal to disappear
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "[x-show='isOpen']"))
            )
            
            # Take screenshot after modal closed
            self.take_screenshot("modal_closed.png", "Modal closed")
            
            print("✓ Modal closed successfully")
            return True
            
        except Exception as e:
            print(f"✗ Modal close failed: {e}")
            return False
    
    def test_responsive_design(self):
        """Test modal responsiveness on different screen sizes."""
        print("\n--- Testing Responsive Design ---")
        screen_sizes = [
            (1920, 1080, "desktop"),
            (1366, 768, "laptop"),
            (768, 1024, "tablet"),
            (375, 667, "mobile")
        ]
        
        results = []
        
        for width, height, device in screen_sizes:
            try:
                print(f"Testing {device} viewport ({width}x{height})...")
                
                # Set viewport size
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Navigate to orders page
                self.driver.get(f"{self.base_url}/orders")
                
                # Wait for Alpine.js to be ready
                time.sleep(3)
                
                # Open modal using View Details button
                view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
                if view_buttons:
                    view_buttons[0].click()
                    
                    # Wait for modal
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "[x-show='isOpen'], [x-show='true']"))
                    )
                    
                    # Take screenshot
                    filename = f"modal_{device}.png"
                    self.take_screenshot(filename, f"Modal on {device}")
                    
                    # Close modal
                    close_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]")
                    close_button.click()
                    
                    results.append((device, True))
                else:
                    results.append((device, False))
                    
            except Exception as e:
                print(f"✗ {device} test failed: {e}")
                results.append((device, False))
        
        # Print results
        for device, success in results:
            status = "✓" if success else "✗"
            print(f"{status} {device}: {'PASS' if success else 'FAIL'}")
        
        return all(success for _, success in results)
    
    def test_mobile_modal(self):
        """Test modal on mobile viewport and compare to baseline."""
        print("\n--- Testing Mobile Modal Visual Regression ---")
        try:
            self.driver.set_window_size(375, 667)
            self.driver.get(f"{self.base_url}/orders")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            # Wait for Alpine.js to be ready
            time.sleep(3)
            
            # Find and click "View Details" button
            view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            if not view_buttons:
                print("✗ No 'View Details' buttons found")
                return False
            first_button = view_buttons[0]
            first_button.click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "[x-show='isOpen'], [x-show='true']"))
            )
            screenshot_path = self.take_screenshot("modal_mobile.png", "Modal open on mobile")
            baseline_path = self.screenshots_dir.parent / "baseline" / "expected_modal_open_mobile.png"
            diff_path = self.screenshots_dir / "diff_modal_mobile.png"
            similarity = self.compare_images(baseline_path, screenshot_path, diff_path)
            print(f"Visual similarity to baseline: {similarity:.2f}%")
            if similarity < 99.0:
                print(f"✗ Visual regression detected for mobile modal! See diff: {diff_path}")
                return False
            print("✓ Mobile modal matches baseline")
            return True
        except Exception as e:
            print(f"✗ Mobile modal visual regression failed: {e}")
            return False

    def run_all_tests(self):
        """Run all visual tests."""
        print("🚀 Starting Modal Visual Tests")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login first
            if not self.login():
                print("✗ Cannot proceed without login")
                return False
            
            # Run tests
            tests = [
                ("Orders Page Load", self.test_orders_page_load),
                ("Modal Trigger", self.test_modal_trigger),
                ("Modal Content", self.test_modal_content),
                ("Modal Close", self.test_modal_close),
                ("Responsive Design", self.test_responsive_design),
                ("Mobile Modal Visual Regression", self.test_mobile_modal),
            ]
            
            results = []
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, result))
            
            # Print summary
            print("\n" + "="*50)
            print("📊 TEST SUMMARY")
            print("="*50)
            
            passed = 0
            for test_name, result in results:
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"{status}: {test_name}")
                if result:
                    passed += 1
            
            print(f"\nOverall: {passed}/{len(results)} tests passed")
            
            return passed == len(results)
            
        finally:
            self.teardown_driver()

def main():
    """Main function to run the visual tests."""
    tester = ModalVisualTester()
    
    if tester.run_all_tests():
        print("\n🎉 All visual tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some visual tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 