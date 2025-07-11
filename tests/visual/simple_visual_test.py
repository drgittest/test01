#!/usr/bin/env python3
"""
Simplified visual testing script that focuses on core visual regression functionality.
This script tests the orders list page and compares it to baseline screenshots.
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

class SimpleVisualTester:
    def __init__(self, base_url="http://127.0.0.1:8086"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent
        self.screenshots_dir = self.test_dir / "screenshots"
        self.baseline_dir = self.test_dir / "baseline"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
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
            
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            password_field.submit()
            
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.current_url.endswith("/") or 
                             driver.current_url.endswith("/login")
            )
            
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
    
    def compare_images(self, expected_path, actual_path, diff_path=None, threshold=95.0):
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
            
            # Save diff image if requested and there are differences
            if diff_path and diff.getbbox():
                diff.save(diff_path)
                print(f"✓ Difference image saved: {diff_path}")
            
            return similarity
            
        except Exception as e:
            print(f"✗ Image comparison failed: {e}")
            return 0.0
    
    def test_orders_list_visual_regression(self):
        """Test that the orders list page matches the baseline screenshot."""
        print("\n--- Testing Orders List Visual Regression ---")
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
            screenshot_path = self.take_screenshot("orders_list_current.png", "Current orders list page")
            if not screenshot_path:
                return False
            
            # Compare with baseline
            baseline_path = self.baseline_dir / "expected_orders_list.png"
            diff_path = self.screenshots_dir / "diff_orders_list.png"
            
            similarity = self.compare_images(baseline_path, screenshot_path, diff_path)
            print(f"Visual similarity to baseline: {similarity:.2f}%")
            
            if similarity >= 95.0:
                print("✓ Orders list page matches baseline")
                return True
            else:
                print(f"✗ Visual regression detected! Similarity: {similarity:.2f}%")
                print(f"Check diff image: {diff_path}")
                return False
                
        except Exception as e:
            print(f"✗ Orders list visual regression test failed: {e}")
            return False
    
    def test_mobile_orders_list_visual_regression(self):
        """Test that the mobile orders list page matches the baseline screenshot."""
        print("\n--- Testing Mobile Orders List Visual Regression ---")
        try:
            # Set mobile viewport
            self.driver.set_window_size(375, 667)
            
            # Navigate to orders page
            self.driver.get(f"{self.base_url}/orders")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Wait a bit more for any dynamic content
            time.sleep(3)
            
            # Take screenshot
            screenshot_path = self.take_screenshot("orders_list_mobile_current.png", "Current mobile orders list page")
            if not screenshot_path:
                return False
            
            # Compare with baseline
            baseline_path = self.baseline_dir / "expected_orders_list_mobile.png"
            diff_path = self.screenshots_dir / "diff_orders_list_mobile.png"
            
            similarity = self.compare_images(baseline_path, screenshot_path, diff_path)
            print(f"Visual similarity to baseline: {similarity:.2f}%")
            
            if similarity >= 95.0:
                print("✓ Mobile orders list page matches baseline")
                return True
            else:
                print(f"✗ Mobile visual regression detected! Similarity: {similarity:.2f}%")
                print(f"Check diff image: {diff_path}")
                return False
                
        except Exception as e:
            print(f"✗ Mobile orders list visual regression test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all visual regression tests."""
        print("🎨 Simple Visual Regression Testing")
        print("=" * 40)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login first
            if not self.login():
                print("✗ Cannot proceed without login")
                return False
            
            # Run tests
            tests = [
                ("Orders List Visual Regression", self.test_orders_list_visual_regression),
                ("Mobile Orders List Visual Regression", self.test_mobile_orders_list_visual_regression),
            ]
            
            results = []
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, result))
            
            # Print summary
            print("\n" + "="*50)
            print("📊 VISUAL REGRESSION TEST SUMMARY")
            print("="*50)
            
            passed = 0
            for test_name, result in results:
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"{status}: {test_name}")
                if result:
                    passed += 1
            
            print(f"\nOverall: {passed}/{len(results)} visual regression tests passed")
            
            if passed == len(results):
                print("\n🎉 All visual regression tests passed!")
                print("✅ The UI matches the expected baseline screenshots")
            else:
                print("\n❌ Some visual regression tests failed!")
                print("📸 Check the diff images in: tests/visual/screenshots/")
                print("💡 Update baselines if changes are intentional")
            
            return passed == len(results)
            
        finally:
            self.teardown_driver()

def main():
    """Main function to run the visual regression tests."""
    tester = SimpleVisualTester()
    
    if tester.run_all_tests():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 