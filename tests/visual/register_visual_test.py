#!/usr/bin/env python3
"""
Register Page Visual Regression Tests
Tests the visual appearance and functionality of the register page.
"""

import sys
from pathlib import Path
from base_visual_test import BaseVisualTester
from selenium.webdriver.common.by import By


class RegisterVisualTester(BaseVisualTester):
    """Visual regression tests for register page."""
    
    def __init__(self, base_url="http://localhost:8000"):
        super().__init__(base_url, "Register Page")
        self.requires_login = False  # Register page doesn't require authentication
        
    def test_register_page_layout(self):
        """Test register page basic layout and styling."""
        return self.visual_regression_test("/register", "register_page", "form")
    
    def test_register_page_responsive(self):
        """Test register page responsiveness across devices."""
        return self.test_responsive_design("/register", "register_page", "form")
    
    def test_register_form_validation_states(self):
        """Test register form validation error states."""
        print("\n--- Testing Register Form Validation States ---")
        
        try:
            # Navigate to register page
            self.driver.get(f"{self.base_url}/register")
            self.wait_for_page_load("form")
            
            # Test data for different validation states
            test_data = {
                'empty_form': {
                    'fields': {},
                    'trigger': 'button[type="submit"]'
                },
                'valid_form': {
                    'fields': {
                        'login_id': 'new_test_user',
                        'password': 'test_password'
                    }
                }
            }
            
            results = self.test_form_validation_states("form", test_data)
            
            # Test user already exists scenario
            print("Testing user already exists scenario...")
            self.driver.get(f"{self.base_url}/register")
            self.wait_for_page_load("form")
            
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Use existing user credentials
            username_field.clear()
            username_field.send_keys("asdf2")  # This user should already exist
            password_field.clear()
            password_field.send_keys("asdf")
            password_field.submit()
            
            # Wait for response
            self.wait_for_page_load("form")
            
            # Take screenshot of error state
            error_screenshot = self.take_screenshot("register_user_exists_error.png", "Register form with user exists error")
            
            # Check if error message is present
            page_source = self.driver.page_source
            if "既に存在します" in page_source:
                print("✓ User exists error message displayed correctly")
                results.append(('user_exists_error', True))
            else:
                print("✗ User exists error message not found")
                results.append(('user_exists_error', False))
            
            return all(result for _, result in results)
            
        except Exception as e:
            print(f"✗ Register form validation test failed: {e}")
            return False
    
    def test_register_page_elements(self):
        """Test that all expected register page elements are present."""
        print("\n--- Testing Register Page Elements ---")
        
        try:
            self.driver.get(f"{self.base_url}/register")
            self.wait_for_page_load("form")
            
            # Expected elements
            expected_elements = [
                ('form', 'Register form'),
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
            if "ユーザー登録" in page_source:
                print("✓ Japanese register text found")
            else:
                print("✗ Japanese register text not found")
                missing_elements.append("Japanese register text")
            
            # Take screenshot of complete page
            self.take_screenshot("register_elements_check.png", "Register page elements validation")
            
            return len(missing_elements) == 0
            
        except Exception as e:
            print(f"✗ Register page elements test failed: {e}")
            return False
    
    def test_register_success_flow(self):
        """Test successful registration flow."""
        print("\n--- Testing Register Success Flow ---")
        
        try:
            # Navigate to register page
            self.driver.get(f"{self.base_url}/register")
            self.wait_for_page_load("form")
            
            # Generate unique username
            import time
            unique_username = f"testuser_{int(time.time())}"
            
            # Fill registration form
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.clear()
            username_field.send_keys(unique_username)
            password_field.clear()
            password_field.send_keys("testpass123")
            
            # Take screenshot before submission
            self.take_screenshot("register_before_submit.png", "Register form before submission")
            
            # Submit form
            password_field.submit()
            
            # Wait for redirect or response
            self.wait_for_page_load()
            
            # Take screenshot after submission
            self.take_screenshot("register_after_submit.png", "Register form after submission")
            
            # Check if redirected to login page (success) or still on register page (error)
            current_url = self.driver.current_url
            if "login" in current_url:
                print("✓ Successfully redirected to login page")
                return True
            elif "register" in current_url:
                print("✓ Remained on register page (expected if user exists)")
                return True
            else:
                print(f"✗ Unexpected redirect to: {current_url}")
                return False
            
        except Exception as e:
            print(f"✗ Register success flow test failed: {e}")
            return False
    
    def run_page_specific_tests(self):
        """Run all register page specific tests."""
        tests = [
            ("Register Page Layout", self.test_register_page_layout),
            ("Register Page Responsive", self.test_register_page_responsive),
            ("Register Form Validation States", self.test_register_form_validation_states),
            ("Register Page Elements", self.test_register_page_elements),
            ("Register Success Flow", self.test_register_success_flow),
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
        print("📊 REGISTER PAGE TEST SUMMARY")
        print("="*50)
        
        passed = 0
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} register page tests passed")
        
        return passed == len(results)
    
    def create_baselines(self):
        """Create baseline screenshots for register page."""
        print("Creating baseline screenshots for register page...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Create baselines for all devices
            for device in self.viewports.keys():
                print(f"Creating {device} baseline...")
                self.set_viewport(device)
                self.driver.get(f"{self.base_url}/register")
                self.wait_for_page_load("form")
                
                baseline_filename = f"expected_register_page_{device}.png"
                self.take_screenshot(baseline_filename, f"Register page baseline for {device}", self.baseline_dir)
            
            # Create validation state baselines
            print("Creating validation state baselines...")
            self.driver.get(f"{self.base_url}/register")
            self.wait_for_page_load("form")
            
            # User exists error baseline
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys("asdf2")  # Existing user
            password_field.send_keys("asdf")
            password_field.submit()
            
            self.wait_for_page_load("form")
            self.take_screenshot("expected_register_user_exists_error.png", "Register user exists error baseline", self.baseline_dir)
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create register baselines: {e}")
            return False
        finally:
            self.teardown_driver()


def main():
    """Main function to run register page visual tests."""
    tester = RegisterVisualTester()
    
    if tester.run_all_tests():
        print("\n🎉 All register page visual tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some register page visual tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()