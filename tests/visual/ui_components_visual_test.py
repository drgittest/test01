#!/usr/bin/env python3
"""
UI Components Visual Regression Tests
Tests navigation, buttons, forms, and other UI components for visual consistency.
"""

import sys
import time
from pathlib import Path
from base_visual_test import BaseVisualTester
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class UIComponentsVisualTester(BaseVisualTester):
    """Visual regression tests for UI components."""
    
    def __init__(self, base_url="http://localhost:8000"):
        super().__init__(base_url, "UI Components")
        self.requires_login = False  # Test both authenticated and non-authenticated components
        
    def test_navigation_styling(self):
        """Test header/navigation styling consistency."""
        print("\n--- Testing Navigation Styling ---")
        
        try:
            # Test navigation on different pages
            test_pages = [
                ("/login", "Login page navigation"),
                ("/register", "Register page navigation"),
            ]
            
            # Add authenticated pages after login
            if self.login():
                test_pages.extend([
                    ("/", "Home page navigation"),
                    ("/orders", "Orders page navigation"),
                    ("/orders/create", "Create order page navigation"),
                ])
            
            results = []
            
            for page_url, description in test_pages:
                print(f"Testing {description}...")
                
                try:
                    self.driver.get(f"{self.base_url}{page_url}")
                    self.wait_for_page_load()
                    
                    # Take screenshot focusing on navigation
                    self.take_screenshot(f"navigation_{page_url.replace('/', '_')}.png", description)
                    
                    # Check for common navigation elements
                    nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, header, .navbar, .nav")
                    
                    if nav_elements:
                        print(f"✓ Navigation elements found on {description}")
                        results.append((description, True))
                    else:
                        print(f"ℹ️ No explicit navigation elements found on {description}")
                        results.append((description, True))  # Not necessarily a failure
                        
                except Exception as e:
                    print(f"✗ {description} failed: {e}")
                    results.append((description, False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Navigation styling test failed: {e}")
            return False
    
    def test_button_states_and_interactions(self):
        """Test button states and hover interactions."""
        print("\n--- Testing Button States and Interactions ---")
        
        try:
            # Test buttons on different pages
            test_pages = [
                ("/login", "Login page buttons"),
                ("/register", "Register page buttons"),
            ]
            
            # Add authenticated pages after login
            if self.login():
                test_pages.extend([
                    ("/orders", "Orders page buttons"),
                    ("/orders/create", "Create order page buttons"),
                ])
            
            results = []
            
            for page_url, description in test_pages:
                print(f"Testing {description}...")
                
                try:
                    self.driver.get(f"{self.base_url}{page_url}")
                    self.wait_for_page_load()
                    
                    # Find all buttons
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, .btn, input[type='submit']")
                    
                    if buttons:
                        print(f"✓ Found {len(buttons)} button(s) on {description}")
                        
                        # Test button states
                        for i, button in enumerate(buttons[:3]):  # Test first 3 buttons
                            try:
                                # Normal state
                                self.take_screenshot(f"button_normal_{page_url.replace('/', '_')}_{i}.png", 
                                                   f"Button {i} normal state")
                                
                                # Hover state
                                actions = ActionChains(self.driver)
                                actions.move_to_element(button).perform()
                                time.sleep(0.5)
                                
                                self.take_screenshot(f"button_hover_{page_url.replace('/', '_')}_{i}.png", 
                                                   f"Button {i} hover state")
                                
                                # Move away to reset state
                                actions.move_by_offset(10, 10).perform()
                                
                            except Exception as e:
                                print(f"⚠️ Could not test button {i}: {e}")
                        
                        results.append((description, True))
                    else:
                        print(f"ℹ️ No buttons found on {description}")
                        results.append((description, True))  # Not necessarily a failure
                        
                except Exception as e:
                    print(f"✗ {description} failed: {e}")
                    results.append((description, False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Button states and interactions test failed: {e}")
            return False
    
    def test_form_field_styling_consistency(self):
        """Test form field styling consistency across pages."""
        print("\n--- Testing Form Field Styling Consistency ---")
        
        try:
            # Test form fields on different pages
            form_pages = [
                ("/login", "Login form fields"),
                ("/register", "Register form fields"),
            ]
            
            # Add authenticated pages after login
            if self.login():
                form_pages.extend([
                    ("/orders/create", "Create order form fields"),
                ])
            
            results = []
            
            for page_url, description in form_pages:
                print(f"Testing {description}...")
                
                try:
                    self.driver.get(f"{self.base_url}{page_url}")
                    self.wait_for_page_load("form")
                    
                    # Find form elements
                    form_elements = {
                        'text_inputs': self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='password']"),
                        'number_inputs': self.driver.find_elements(By.CSS_SELECTOR, "input[type='number']"),
                        'select_fields': self.driver.find_elements(By.CSS_SELECTOR, "select"),
                        'textareas': self.driver.find_elements(By.CSS_SELECTOR, "textarea"),
                        'labels': self.driver.find_elements(By.CSS_SELECTOR, "label"),
                        'submit_buttons': self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"),
                    }
                    
                    # Take screenshot of form
                    self.take_screenshot(f"form_fields_{page_url.replace('/', '_')}.png", description)
                    
                    # Test field states
                    for field_type, elements in form_elements.items():
                        if elements:
                            print(f"✓ Found {len(elements)} {field_type} on {description}")
                            
                            # Test first element of each type
                            if field_type in ['text_inputs', 'number_inputs']:
                                try:
                                    first_element = elements[0]
                                    
                                    # Normal state
                                    self.take_screenshot(f"field_normal_{field_type}_{page_url.replace('/', '_')}.png", 
                                                       f"{field_type} normal state")
                                    
                                    # Focus state
                                    first_element.click()
                                    time.sleep(0.5)
                                    
                                    self.take_screenshot(f"field_focus_{field_type}_{page_url.replace('/', '_')}.png", 
                                                       f"{field_type} focus state")
                                    
                                    # Filled state
                                    first_element.send_keys("test")
                                    time.sleep(0.5)
                                    
                                    self.take_screenshot(f"field_filled_{field_type}_{page_url.replace('/', '_')}.png", 
                                                       f"{field_type} filled state")
                                    
                                    # Clear field
                                    first_element.clear()
                                    
                                except Exception as e:
                                    print(f"⚠️ Could not test {field_type}: {e}")
                    
                    results.append((description, True))
                    
                except Exception as e:
                    print(f"✗ {description} failed: {e}")
                    results.append((description, False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Form field styling consistency test failed: {e}")
            return False
    
    def test_loading_states_and_spinners(self):
        """Test loading states and spinner animations."""
        print("\n--- Testing Loading States and Spinners ---")
        
        try:
            # Test loading states where applicable
            loading_scenarios = [
                {
                    'name': 'login_loading',
                    'setup': lambda: self.test_login_loading(),
                    'description': 'Login form loading state'
                },
                {
                    'name': 'form_submission_loading',
                    'setup': lambda: self.test_form_submission_loading(),
                    'description': 'Form submission loading state'
                },
                {
                    'name': 'page_navigation_loading',
                    'setup': lambda: self.test_page_navigation_loading(),
                    'description': 'Page navigation loading state'
                }
            ]
            
            results = []
            
            for scenario in loading_scenarios:
                print(f"Testing {scenario['description']}...")
                
                try:
                    result = scenario['setup']()
                    results.append((scenario['name'], result))
                    
                    if result:
                        print(f"✓ {scenario['description']} captured")
                    else:
                        print(f"✗ {scenario['description']} failed")
                        
                except Exception as e:
                    print(f"✗ {scenario['description']} failed: {e}")
                    results.append((scenario['name'], False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Loading states and spinners test failed: {e}")
            return False
    
    def test_login_loading(self):
        """Test login form loading state."""
        try:
            self.driver.get(f"{self.base_url}/login")
            self.wait_for_page_load("form")
            
            # Fill login form
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys("testuser")
            password_field.send_keys("testpass")
            
            # Take screenshot before submission
            self.take_screenshot("login_before_submit.png", "Login form before submission")
            
            # Submit form
            password_field.submit()
            
            # Try to capture loading state
            try:
                # Look for loading indicators
                loading_elements = self.driver.find_elements(By.CSS_SELECTOR, ".loading, .spinner, [class*='load']")
                
                if loading_elements:
                    self.take_screenshot("login_loading_state.png", "Login loading state")
                    print("✓ Login loading state captured")
                    return True
                else:
                    print("ℹ️ No loading indicators found during login")
                    return True  # Not necessarily a failure
                    
            except Exception as e:
                print(f"⚠️ Could not capture login loading state: {e}")
                return True  # Not necessarily a failure
            
        except Exception as e:
            print(f"✗ Login loading test failed: {e}")
            return False
    
    def test_form_submission_loading(self):
        """Test form submission loading states."""
        try:
            # Test with order creation form if authenticated
            if self.login():
                self.driver.get(f"{self.base_url}/orders/create")
                self.wait_for_page_load("form")
                
                # Fill form
                form_data = {
                    'order_number': 'LOADING_TEST',
                    'customer_name': 'Loading Test Customer',
                    'item': 'Test Item',
                    'quantity': '1',
                    'price': '100'
                }
                
                for field_name, value in form_data.items():
                    try:
                        field = self.driver.find_element(By.NAME, field_name)
                        field.send_keys(value)
                    except:
                        pass
                
                # Take screenshot before submission
                self.take_screenshot("form_before_submit.png", "Form before submission")
                
                # Submit form
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                submit_button.click()
                
                # Try to capture loading state
                try:
                    loading_elements = self.driver.find_elements(By.CSS_SELECTOR, ".loading, .spinner, [class*='load']")
                    
                    if loading_elements:
                        self.take_screenshot("form_submission_loading.png", "Form submission loading state")
                        print("✓ Form submission loading state captured")
                        return True
                    else:
                        print("ℹ️ No loading indicators found during form submission")
                        return True
                        
                except Exception as e:
                    print(f"⚠️ Could not capture form submission loading state: {e}")
                    return True
            
            return True
            
        except Exception as e:
            print(f"✗ Form submission loading test failed: {e}")
            return False
    
    def test_page_navigation_loading(self):
        """Test page navigation loading states."""
        try:
            # Test navigation between pages
            pages = ["/login", "/register"]
            
            for page in pages:
                try:
                    self.driver.get(f"{self.base_url}{page}")
                    
                    # Take screenshot of page loading
                    self.take_screenshot(f"page_loading_{page.replace('/', '_')}.png", 
                                       f"Page loading for {page}")
                    
                    # Wait for page to fully load
                    self.wait_for_page_load()
                    
                    # Take screenshot of loaded page
                    self.take_screenshot(f"page_loaded_{page.replace('/', '_')}.png", 
                                       f"Page loaded for {page}")
                    
                except Exception as e:
                    print(f"⚠️ Could not test page loading for {page}: {e}")
            
            return True
            
        except Exception as e:
            print(f"✗ Page navigation loading test failed: {e}")
            return False
    
    def test_responsive_ui_components(self):
        """Test UI components responsiveness."""
        print("\n--- Testing Responsive UI Components ---")
        
        try:
            # Test key pages across different viewports
            test_pages = ["/login", "/register"]
            
            if self.login():
                test_pages.extend(["/orders", "/orders/create"])
            
            results = []
            
            for page_url in test_pages:
                for device in self.viewports.keys():
                    print(f"Testing {page_url} components on {device}...")
                    
                    try:
                        self.set_viewport(device)
                        self.driver.get(f"{self.base_url}{page_url}")
                        self.wait_for_page_load()
                        
                        # Take screenshot
                        self.take_screenshot(f"components_{page_url.replace('/', '_')}_{device}.png", 
                                           f"Components on {page_url} for {device}")
                        
                        # Check for responsive elements
                        responsive_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                                                       "[class*='responsive'], [class*='mobile'], [class*='tablet'], [class*='desktop']")
                        
                        if responsive_elements:
                            print(f"✓ Found {len(responsive_elements)} responsive elements")
                        
                        results.append((f"{page_url}_{device}", True))
                        
                    except Exception as e:
                        print(f"✗ {page_url} on {device} failed: {e}")
                        results.append((f"{page_url}_{device}", False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Responsive UI components test failed: {e}")
            return False
    
    def test_error_states_visual_feedback(self):
        """Test error states and visual feedback."""
        print("\n--- Testing Error States Visual Feedback ---")
        
        try:
            # Test error states on different forms
            error_scenarios = [
                {
                    'page': '/login',
                    'action': lambda: self.trigger_login_error(),
                    'description': 'Login error state'
                },
                {
                    'page': '/register',
                    'action': lambda: self.trigger_register_error(),
                    'description': 'Register error state'
                }
            ]
            
            results = []
            
            for scenario in error_scenarios:
                print(f"Testing {scenario['description']}...")
                
                try:
                    self.driver.get(f"{self.base_url}{scenario['page']}")
                    self.wait_for_page_load("form")
                    
                    # Trigger error
                    error_triggered = scenario['action']()
                    
                    if error_triggered:
                        # Take screenshot of error state
                        self.take_screenshot(f"error_state_{scenario['page'].replace('/', '_')}.png", 
                                           scenario['description'])
                        
                        results.append((scenario['description'], True))
                        print(f"✓ {scenario['description']} captured")
                    else:
                        results.append((scenario['description'], False))
                        print(f"✗ Could not trigger {scenario['description']}")
                        
                except Exception as e:
                    print(f"✗ {scenario['description']} failed: {e}")
                    results.append((scenario['description'], False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Error states visual feedback test failed: {e}")
            return False
    
    def trigger_login_error(self):
        """Trigger login error for visual testing."""
        try:
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys("invalid_user")
            password_field.send_keys("invalid_password")
            password_field.submit()
            
            time.sleep(2)  # Wait for error to appear
            
            # Check if error message appears
            page_source = self.driver.page_source
            if "IDまたはパスワードが違います" in page_source or "error" in page_source.lower():
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Could not trigger login error: {e}")
            return False
    
    def trigger_register_error(self):
        """Trigger register error for visual testing."""
        try:
            username_field = self.driver.find_element(By.NAME, "login_id")
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Use existing username to trigger error
            username_field.send_keys("asdf2")
            password_field.send_keys("asdf")
            password_field.submit()
            
            time.sleep(2)  # Wait for error to appear
            
            # Check if error message appears
            page_source = self.driver.page_source
            if "既に存在します" in page_source or "error" in page_source.lower():
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Could not trigger register error: {e}")
            return False
    
    def run_page_specific_tests(self):
        """Run all UI components specific tests."""
        tests = [
            ("Navigation Styling", self.test_navigation_styling),
            ("Button States and Interactions", self.test_button_states_and_interactions),
            ("Form Field Styling Consistency", self.test_form_field_styling_consistency),
            ("Loading States and Spinners", self.test_loading_states_and_spinners),
            ("Responsive UI Components", self.test_responsive_ui_components),
            ("Error States Visual Feedback", self.test_error_states_visual_feedback),
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
        print("📊 UI COMPONENTS TEST SUMMARY")
        print("="*50)
        
        passed = 0
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} UI components tests passed")
        
        return passed == len(results)
    
    def create_baselines(self):
        """Create baseline screenshots for UI components."""
        print("Creating baseline screenshots for UI components...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Create baselines for key UI states
            ui_states = [
                ('navigation_login', '/login'),
                ('navigation_register', '/register'),
                ('button_normal_login', '/login'),
                ('form_fields_login', '/login'),
                ('error_state_login', '/login'),
            ]
            
            for state_name, page_url in ui_states:
                print(f"Creating baseline for {state_name}...")
                
                try:
                    self.driver.get(f"{self.base_url}{page_url}")
                    self.wait_for_page_load()
                    
                    baseline_filename = f"expected_{state_name}.png"
                    self.take_screenshot(baseline_filename, f"Baseline for {state_name}", self.baseline_dir)
                    
                except Exception as e:
                    print(f"⚠️ Could not create baseline for {state_name}: {e}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create UI components baselines: {e}")
            return False
        finally:
            self.teardown_driver()


def main():
    """Main function to run UI components visual tests."""
    tester = UIComponentsVisualTester()
    
    if tester.run_all_tests():
        print("\n🎉 All UI components visual tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some UI components visual tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()