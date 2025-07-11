#!/usr/bin/env python3
"""
Base Visual Testing Framework
Provides reusable components for visual regression testing across all pages.
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
from abc import ABC, abstractmethod


class BaseVisualTester(ABC):
    """Base class for all visual testing implementations."""
    
    def __init__(self, base_url="http://localhost:8000", test_name="visual_test", use_test_data=True):
        self.base_url = base_url
        self.test_name = test_name
        self.use_test_data = use_test_data
        self.test_dir = Path(__file__).parent
        self.screenshots_dir = self.test_dir / "screenshots"
        self.baseline_dir = self.test_dir / "baseline"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Test data and isolation management
        self.test_data_manager = None
        self.isolation_manager = None
        self.test_credentials = None
        
        if use_test_data:
            self.initialize_test_data_systems()
        
        # Chrome options for consistent testing
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        
        self.driver = None
        
        # Configuration
        self.default_timeout = 10
        self.similarity_threshold = 95.0
        self.viewports = {
            'desktop': (1920, 1080),
            'laptop': (1366, 768),
            'tablet': (768, 1024),
            'mobile': (375, 667)
        }
    
    def initialize_test_data_systems(self):
        """Initialize test data and isolation management systems."""
        try:
            from test_data_manager import TestDataManager
            from test_isolation_manager import TestIsolationManager
            
            self.test_data_manager = TestDataManager()
            self.isolation_manager = TestIsolationManager()
            
            # Load test credentials
            self.test_data_manager.load_test_fixtures()
            self.test_credentials = self.test_data_manager.get_test_credentials()
            
            print(f"✓ Test data systems initialized for {self.test_name}")
            
        except ImportError as e:
            print(f"⚠️ Test data systems not available: {e}")
        except Exception as e:
            print(f"⚠️ Error initializing test data systems: {e}")
    
    def ensure_test_data_exists(self):
        """Ensure test data exists, create if necessary."""
        if not self.test_data_manager:
            return True
        
        try:
            # Check if test data exists
            if not self.test_data_manager.check_test_data_exists():
                print("📋 Creating test data for visual tests...")
                
                # Generate and seed test data
                success = self.test_data_manager.generate_and_seed_all(
                    user_count=3, 
                    order_count=10, 
                    force=False
                )
                
                if success:
                    print("✓ Test data created successfully")
                    # Update credentials
                    self.test_credentials = self.test_data_manager.get_test_credentials()
                else:
                    print("⚠️ Test data creation failed, using default credentials")
                    return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error ensuring test data exists: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data created by this test."""
        if self.test_data_manager:
            try:
                self.test_data_manager.cleanup_test_data()
                print("✓ Test data cleaned up")
            except Exception as e:
                print(f"⚠️ Test data cleanup failed: {e}")
    
    def get_test_credentials(self) -> Dict[str, str]:
        """Get test credentials for authentication."""
        if self.test_credentials:
            return self.test_credentials
        else:
            # Return default credentials
            return {
                "username": "asdf2",
                "password": "asdf"
            }
        
    def setup_driver(self):
        """Initialize the Chrome WebDriver."""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.implicitly_wait(self.default_timeout)
            print(f"✓ Chrome WebDriver initialized for {self.test_name}")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize Chrome WebDriver: {e}")
            return False
    
    def teardown_driver(self):
        """Clean up the WebDriver."""
        if self.driver:
            self.driver.quit()
            print(f"✓ WebDriver cleaned up for {self.test_name}")
    
    def set_viewport(self, device='desktop'):
        """Set browser viewport size."""
        if device in self.viewports:
            width, height = self.viewports[device]
            self.driver.set_window_size(width, height)
            time.sleep(1)  # Allow time for resize
            print(f"✓ Viewport set to {device} ({width}x{height})")
        else:
            print(f"✗ Unknown device: {device}")
    
    def login(self, username=None, password=None):
        """Login to the application using test credentials."""
        # Use test credentials if not provided
        if not username or not password:
            credentials = self.get_test_credentials()
            username = credentials["username"]
            password = credentials["password"]
        
        try:
            print(f"Logging in as {username}...")
            self.driver.get(f"{self.base_url}/login")
            
            username_field = WebDriverWait(self.driver, self.default_timeout).until(
                EC.presence_of_element_located((By.NAME, "login_id"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            password_field.submit()
            
            # Wait for redirect
            WebDriverWait(self.driver, self.default_timeout).until(
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
    
    def wait_for_page_load(self, selector=None, timeout=None):
        """Wait for page to fully load."""
        timeout = timeout or self.default_timeout
        try:
            if selector:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            else:
                # Wait for document ready state
                WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
            # Additional wait for dynamic content
            time.sleep(2)
            return True
        except TimeoutException:
            print(f"✗ Page load timeout after {timeout}s")
            return False
    
    def take_screenshot(self, filename, description="", directory=None):
        """Take a screenshot and save it."""
        try:
            save_dir = directory or self.screenshots_dir
            filepath = save_dir / filename
            
            # Ensure the element is fully loaded and visible
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            self.driver.save_screenshot(str(filepath))
            print(f"✓ Screenshot saved: {filename} - {description}")
            return filepath
        except Exception as e:
            print(f"✗ Failed to take screenshot {filename}: {e}")
            return None
    
    def compare_images(self, expected_path, actual_path, diff_path=None, threshold=None):
        """Compare two images and return similarity percentage."""
        threshold = threshold or self.similarity_threshold
        try:
            if not expected_path.exists():
                print(f"✗ Expected image not found: {expected_path}")
                return 0.0
            
            expected = Image.open(expected_path)
            actual = Image.open(actual_path)
            
            # Ensure both images have the same size
            if expected.size != actual.size:
                print(f"✗ Image sizes don't match: {expected.size} vs {actual.size}")
                # Resize actual to match expected
                actual = actual.resize(expected.size, Image.Resampling.LANCZOS)
            
            # Calculate difference
            diff = ImageChops.difference(expected, actual)
            
            # Calculate similarity percentage using a more robust method
            histogram = diff.histogram()
            total_pixels = expected.size[0] * expected.size[1]
            
            # Count non-zero pixels (differences)
            diff_pixels = sum(histogram[256:]) + sum(histogram[512:])  # R, G, B channels
            similarity = ((total_pixels * 3 - diff_pixels) / (total_pixels * 3)) * 100
            
            # Save diff image if requested and there are significant differences
            if diff_path and similarity < threshold:
                diff.save(diff_path)
                print(f"✓ Difference image saved: {diff_path}")
            
            return similarity
            
        except Exception as e:
            print(f"✗ Image comparison failed: {e}")
            return 0.0
    
    def visual_regression_test(self, page_url, page_name, selector=None, device='desktop'):
        """Perform a visual regression test for a page."""
        print(f"\n--- Testing {page_name} Visual Regression ({device}) ---")
        try:
            # Set viewport
            self.set_viewport(device)
            
            # Navigate to page
            self.driver.get(f"{self.base_url}{page_url}")
            
            # Wait for page load
            if not self.wait_for_page_load(selector):
                return False
            
            # Take screenshot
            filename = f"{page_name}_{device}_current.png"
            screenshot_path = self.take_screenshot(filename, f"{page_name} on {device}")
            if not screenshot_path:
                return False
            
            # Compare with baseline
            baseline_filename = f"expected_{page_name}_{device}.png"
            baseline_path = self.baseline_dir / baseline_filename
            diff_path = self.screenshots_dir / f"diff_{page_name}_{device}.png"
            
            similarity = self.compare_images(baseline_path, screenshot_path, diff_path)
            print(f"Visual similarity to baseline: {similarity:.2f}%")
            
            if similarity >= self.similarity_threshold:
                print(f"✓ {page_name} ({device}) matches baseline")
                return True
            else:
                print(f"✗ Visual regression detected! Similarity: {similarity:.2f}%")
                print(f"Check diff image: {diff_path}")
                return False
                
        except Exception as e:
            print(f"✗ {page_name} ({device}) visual regression test failed: {e}")
            return False
    
    def test_form_validation_states(self, form_selector, test_data):
        """Test form validation visual states."""
        results = []
        
        for state_name, data in test_data.items():
            try:
                print(f"Testing {state_name} state...")
                
                # Fill form with test data
                for field_name, value in data.get('fields', {}).items():
                    field = self.driver.find_element(By.NAME, field_name)
                    field.clear()
                    field.send_keys(value)
                
                # Trigger validation if needed
                if data.get('trigger'):
                    trigger_element = self.driver.find_element(By.CSS_SELECTOR, data['trigger'])
                    trigger_element.click()
                
                # Wait for validation to appear
                time.sleep(1)
                
                # Take screenshot
                filename = f"form_{state_name}.png"
                screenshot_path = self.take_screenshot(filename, f"Form {state_name} state")
                
                results.append((state_name, screenshot_path is not None))
                
            except Exception as e:
                print(f"✗ Form {state_name} test failed: {e}")
                results.append((state_name, False))
        
        return results
    
    def test_responsive_design(self, page_url, page_name, selector=None):
        """Test page responsiveness across different devices."""
        print(f"\n--- Testing {page_name} Responsive Design ---")
        results = []
        
        for device in self.viewports.keys():
            try:
                result = self.visual_regression_test(page_url, page_name, selector, device)
                results.append((device, result))
            except Exception as e:
                print(f"✗ {device} test failed: {e}")
                results.append((device, False))
        
        # Print results summary
        print(f"\nResponsive test results for {page_name}:")
        for device, success in results:
            status = "✓" if success else "✗"
            print(f"{status} {device}: {'PASS' if success else 'FAIL'}")
        
        return all(success for _, success in results)
    
    @abstractmethod
    def run_page_specific_tests(self):
        """Implement page-specific tests in subclasses."""
        pass
    
    def run_all_tests(self):
        """Run all visual tests for this page."""
        print(f"🎨 Starting {self.test_name} Visual Tests")
        print("=" * 50)
        
        # Ensure test data exists
        if self.use_test_data:
            self.ensure_test_data_exists()
        
        if not self.setup_driver():
            return False
        
        try:
            # Login if required
            if hasattr(self, 'requires_login') and self.requires_login:
                if not self.login():
                    print("✗ Cannot proceed without login")
                    return False
            
            # Run page-specific tests
            result = self.run_page_specific_tests()
            
            return result
            
        finally:
            self.teardown_driver()
            
            # Cleanup test data if configured
            if self.use_test_data and hasattr(self, 'cleanup_on_exit') and self.cleanup_on_exit:
                self.cleanup_test_data()


class ModalTester:
    """Mixin class for modal testing functionality."""
    
    def open_modal(self, trigger_selector, modal_selector="[x-show='isOpen']", timeout=10):
        """Open a modal by clicking a trigger element."""
        try:
            # Wait for Alpine.js to be ready
            time.sleep(2)
            
            trigger = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, trigger_selector))
            )
            trigger.click()
            
            # Wait for modal to appear
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, modal_selector))
            )
            
            # Wait for content to load
            time.sleep(2)
            
            print("✓ Modal opened successfully")
            return True
            
        except TimeoutException:
            print("✗ Modal did not appear within timeout")
            return False
        except Exception as e:
            print(f"✗ Failed to open modal: {e}")
            return False
    
    def close_modal(self, close_selector="button:contains('Close')", modal_selector="[x-show='isOpen']", timeout=10):
        """Close a modal by clicking the close button."""
        try:
            close_button = self.driver.find_element(By.XPATH, f"//button[contains(text(), 'Close')]")
            close_button.click()
            
            # Wait for modal to disappear
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, modal_selector))
            )
            
            print("✓ Modal closed successfully")
            return True
            
        except Exception as e:
            print(f"✗ Failed to close modal: {e}")
            return False
    
    def test_modal_content(self, expected_fields, modal_selector=".fixed.inset-0.z-50"):
        """Test that modal displays expected content."""
        try:
            # Wait for loading to finish
            WebDriverWait(self.driver, 10).until(
                lambda driver: not driver.find_elements(By.CSS_SELECTOR, "[x-show='loading']") or
                              not driver.find_element(By.CSS_SELECTOR, "[x-show='loading']").is_displayed()
            )
            
            # Get modal content
            modal_content = self.driver.find_element(By.CSS_SELECTOR, modal_selector)
            modal_text = modal_content.text
            
            # Verify expected fields are present
            missing_fields = []
            for field in expected_fields:
                if field not in modal_text:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"✗ Missing fields in modal: {missing_fields}")
                print(f"Modal text: {modal_text[:300]}...")
                return False
            
            print("✓ Modal content validation passed")
            return True
            
        except Exception as e:
            print(f"✗ Modal content test failed: {e}")
            return False


def create_baseline_script():
    """Generate a script to create baseline screenshots for all pages."""
    script_content = '''#!/usr/bin/env python3
"""
Baseline Screenshot Generator
Creates baseline screenshots for all visual regression tests.
"""

import sys
from pathlib import Path

# Import all page testers
from login_visual_test import LoginVisualTester
from register_visual_test import RegisterVisualTester
from orders_visual_test import OrdersVisualTester
from order_create_visual_test import OrderCreateVisualTester
from order_edit_visual_test import OrderEditVisualTester

def main():
    print("🖼️  Creating baseline screenshots for all pages")
    print("=" * 50)
    
    # Create baseline directory
    baseline_dir = Path(__file__).parent / "baseline"
    baseline_dir.mkdir(exist_ok=True)
    
    # List of all page testers
    testers = [
        LoginVisualTester(test_name="Login Baseline"),
        RegisterVisualTester(test_name="Register Baseline"),
        OrdersVisualTester(test_name="Orders Baseline"),
        OrderCreateVisualTester(test_name="Order Create Baseline"),
        OrderEditVisualTester(test_name="Order Edit Baseline"),
    ]
    
    for tester in testers:
        print(f"\\nCreating baselines for {tester.test_name}...")
        tester.create_baselines()
    
    print("\\n🎉 Baseline generation complete!")

if __name__ == "__main__":
    main()
'''
    
    baseline_script_path = Path(__file__).parent / "create_all_baselines.py"
    with open(baseline_script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✓ Baseline generation script created: {baseline_script_path}")