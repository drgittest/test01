#!/usr/bin/env python3
"""
Login Page Visual Regression Tests
Tests the visual appearance and functionality of the login page.
"""

import sys
from pathlib import Path
from base_visual_test import BaseVisualTester
from selenium.webdriver.common.by import By


class LoginVisualTester(BaseVisualTester):
    """Visual regression tests for login page."""
    
    def __init__(self, base_url="http://localhost:8000"):
        super().__init__(base_url, "Login Page")
        self.requires_login = False  # Login page doesn't require authentication
        
    def test_login_page_layout(self):
        """Test login page basic layout and styling."""
        return self.visual_regression_test("/login", "login_page", "form")
    
    def test_login_page_responsive(self):
        """Test login page responsiveness across devices."""
        return self.test_responsive_design("/login", "login_page", "form")
    
    def test_login_form_validation_states(self):
        """Test login form validation error states."""
        print("\n--- Testing Login Form Validation States ---")
        
        try:
            # Navigate to login page
            self.driver.get(f"{self.base_url}/login")
            self.wait_for_page_load("form")
            
            # Test data for different validation states
            test_data = {
                'empty_form': {
                    'fields': {},
                    'trigger': 'button[type="submit"]'
                },
                'invalid_credentials': {
                    'fields': {
                        'login_id': 'nonexistent_user',
                        'password': 'wrong_password'
                    },
                    'trigger': 'button[type="submit"]'
                },
                'valid_form': {
                    'fields': {
                        'login_id': 'asdf2',
                        'password': 'asdf'
                    }
                }
            }
            
            results = self.test_form_validation_states("form", test_data)
            
            # Test invalid credentials submission
            print("Testing invalid credentials submission...")
            self.driver.get(f"{self.base_url}/login")
            self.wait_for_page_load("form")
            
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.clear()
            username_field.send_keys("nonexistent_user")
            password_field.clear()
            password_field.send_keys("wrong_password")
            password_field.submit()
            
            # Wait for error message
            self.wait_for_page_load("form")
            
            # Take screenshot of error state
            error_screenshot = self.take_screenshot("login_error_state.png", "Login form with error message")
            
            # Check if error message is present
            page_source = self.driver.page_source
            if "IDまたはパスワードが違います" in page_source:
                print("✓ Error message displayed correctly")
                results.append(('error_message', True))
            else:
                print("✗ Error message not found")
                results.append(('error_message', False))
            
            return all(result for _, result in results)
            
        except Exception as e:
            print(f"✗ Login form validation test failed: {e}")
            return False
    
    def test_login_page_elements(self):
        """Test that all expected login page elements are present."""
        print("\n--- Testing Login Page Elements ---")
        
        try:
            self.driver.get(f"{self.base_url}/login")
            self.wait_for_page_load("form")
            
            # Expected elements
            expected_elements = [
                ('form', 'Login form'),
                ('input[name="login_id"]', 'Username field'),
                ('input[name="password"]', 'Password field'),
                ('button[type="submit"]', 'Submit button'),
            ]
            
            missing_elements = []
            for selector, description in expected_elements:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        print(f"✓ {description} found")
                    else:
                        print(f"✗ {description} not found")
                        missing_elements.append(description)
                except:
                    print(f"✗ {description} not found")
                    missing_elements.append(description)
            
            # Check for Japanese text
            page_source = self.driver.page_source
            if "ログイン" in page_source:
                print("✓ Japanese login text found")
            else:
                print("✗ Japanese login text not found")
                missing_elements.append("Japanese login text")
            
            # Take screenshot of complete page
            self.take_screenshot("login_elements_check.png", "Login page elements validation")
            
            return len(missing_elements) == 0
            
        except Exception as e:
            print(f"✗ Login page elements test failed: {e}")
            return False
    
    def run_page_specific_tests(self):
        """Run all login page specific tests."""
        tests = [
            ("Login Page Layout", self.test_login_page_layout),
            ("Login Page Responsive", self.test_login_page_responsive),
            ("Login Form Validation States", self.test_login_form_validation_states),
            ("Login Page Elements", self.test_login_page_elements),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"✗ {test_name} failed: {e}")
                results.append((test_name, False))
        
        # Print summary
        print(f"\n{'='*50}")
        print("📊 LOGIN PAGE TEST SUMMARY")
        print("="*50)
        
        passed = 0
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} login page tests passed")
        
        return passed == len(results)
    
    def create_baselines(self):
        """Create baseline screenshots for login page."""
        print("Creating baseline screenshots for login page...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Create baselines for all devices
            for device in self.viewports.keys():
                print(f"Creating {device} baseline...")
                self.set_viewport(device)
                self.driver.get(f"{self.base_url}/login")
                self.wait_for_page_load("form")
                
                baseline_filename = f"expected_login_page_{device}.png"
                baseline_path = self.baseline_dir / baseline_filename
                
                self.take_screenshot(baseline_filename, f"Login page baseline for {device}", self.baseline_dir)
            
            # Create validation state baselines
            print("Creating validation state baselines...")
            self.driver.get(f"{self.base_url}/login")
            self.wait_for_page_load("form")
            
            # Invalid credentials baseline
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys("invalid_user")
            password_field.send_keys("wrong_pass")
            password_field.submit()
            
            self.wait_for_page_load("form")
            self.take_screenshot("expected_login_error_state.png", "Login error state baseline", self.baseline_dir)
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create login baselines: {e}")
            return False
        finally:
            self.teardown_driver()


def main():
    """Main function to run login page visual tests."""
    tester = LoginVisualTester()
    
    if tester.run_all_tests():
        print("\n🎉 All login page visual tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some login page visual tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()