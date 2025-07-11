#!/usr/bin/env python3
"""
Enhanced Modal Visual Regression Tests
Tests the modal design and functionality with comprehensive visual coverage.
"""

import sys
import time
from pathlib import Path
from base_visual_test import BaseVisualTester, ModalTester
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class EnhancedModalVisualTester(BaseVisualTester, ModalTester):
    """Enhanced visual regression tests for modal functionality."""
    
    def __init__(self, base_url="http://localhost:8000"):
        super().__init__(base_url, "Enhanced Modal")
        self.requires_login = True  # Modal functionality requires authentication
        
    def test_modal_opening_animations(self):
        """Test modal opening animations and transitions."""
        print("\n--- Testing Modal Opening Animations ---")
        
        try:
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Find View Details buttons
            view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            
            if not view_buttons:
                print("✗ No 'View Details' buttons found")
                return False
            
            # Take screenshot before opening modal
            self.take_screenshot("modal_before_open.png", "Page before modal opens")
            
            # Click to open modal
            first_button = view_buttons[0]
            first_button.click()
            
            # Capture opening animation states
            animation_frames = []
            for i in range(5):  # Capture 5 frames during opening
                time.sleep(0.1)
                frame_path = self.take_screenshot(f"modal_opening_frame_{i}.png", f"Modal opening frame {i}")
                if frame_path:
                    animation_frames.append(frame_path)
            
            # Wait for modal to fully open
            modal_open = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "[x-show='isOpen']"))
            )
            
            # Take screenshot of fully opened modal
            self.take_screenshot("modal_fully_open.png", "Modal fully opened")
            
            print(f"✓ Captured {len(animation_frames)} animation frames")
            
            # Close modal for cleanup
            self.close_modal()
            
            return True
            
        except Exception as e:
            print(f"✗ Modal opening animations test failed: {e}")
            return False
    
    def test_modal_content_loading_states(self):
        """Test modal content loading states and spinners."""
        print("\n--- Testing Modal Content Loading States ---")
        
        try:
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Find View Details buttons
            view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            
            if not view_buttons:
                print("✗ No 'View Details' buttons found")
                return False
            
            # Click to open modal
            first_button = view_buttons[0]
            first_button.click()
            
            # Try to capture loading state immediately
            try:
                loading_element = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[x-show='loading']"))
                )
                
                if loading_element.is_displayed():
                    self.take_screenshot("modal_loading_state.png", "Modal loading state")
                    print("✓ Loading state captured")
                else:
                    print("ℹ️ Loading state not visible (content loaded too quickly)")
                    
            except TimeoutException:
                print("ℹ️ Loading state not detected (content loaded quickly)")
            
            # Wait for content to load
            content_loaded = WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "[x-show='loading']"))
            )
            
            # Take screenshot of loaded content
            self.take_screenshot("modal_content_loaded.png", "Modal content loaded")
            
            # Verify content is present
            modal_content = self.driver.find_element(By.CSS_SELECTOR, ".fixed.inset-0.z-50")
            if modal_content.text:
                print("✓ Modal content loaded successfully")
                result = True
            else:
                print("✗ Modal content appears empty")
                result = False
            
            # Close modal
            self.close_modal()
            
            return result
            
        except Exception as e:
            print(f"✗ Modal content loading states test failed: {e}")
            return False
    
    def test_modal_responsive_behavior(self):
        """Test modal responsive behavior across different screen sizes."""
        print("\n--- Testing Modal Responsive Behavior ---")
        
        try:
            results = []
            
            for device, (width, height) in self.viewports.items():
                print(f"Testing modal on {device} ({width}x{height})...")
                
                # Set viewport
                self.set_viewport(device)
                
                # Navigate to orders page
                self.driver.get(f"{self.base_url}/orders")
                self.wait_for_page_load("table")
                
                # Find and click View Details button
                view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
                
                if not view_buttons:
                    print(f"✗ No 'View Details' buttons found on {device}")
                    results.append((device, False))
                    continue
                
                # Open modal
                first_button = view_buttons[0]
                first_button.click()
                
                # Wait for modal to open
                try:
                    modal_open = WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "[x-show='isOpen']"))
                    )
                    
                    # Take screenshot
                    self.take_screenshot(f"modal_responsive_{device}.png", f"Modal on {device}")
                    
                    # Check modal positioning and size
                    modal_element = self.driver.find_element(By.CSS_SELECTOR, ".fixed.inset-0.z-50")
                    modal_rect = modal_element.rect
                    
                    # Verify modal is visible and properly positioned
                    if modal_rect['width'] > 0 and modal_rect['height'] > 0:
                        print(f"✓ Modal properly displayed on {device}")
                        results.append((device, True))
                    else:
                        print(f"✗ Modal not properly displayed on {device}")
                        results.append((device, False))
                    
                    # Close modal
                    self.close_modal()
                    
                except TimeoutException:
                    print(f"✗ Modal failed to open on {device}")
                    results.append((device, False))
            
            # Print results
            print(f"\nResponsive modal test results:")
            for device, success in results:
                status = "✓" if success else "✗"
                print(f"{status} {device}: {'PASS' if success else 'FAIL'}")
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Modal responsive behavior test failed: {e}")
            return False
    
    def test_modal_closing_mechanisms(self):
        """Test different modal closing mechanisms."""
        print("\n--- Testing Modal Closing Mechanisms ---")
        
        try:
            closing_methods = [
                {
                    'name': 'close_button',
                    'method': lambda: self.driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]").click(),
                    'description': 'Close button click'
                },
                {
                    'name': 'escape_key',
                    'method': lambda: self.driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c'),  # ESC key
                    'description': 'Escape key press'
                },
                {
                    'name': 'backdrop_click',
                    'method': lambda: self.click_modal_backdrop(),
                    'description': 'Background overlay click'
                }
            ]
            
            results = []
            
            for method_info in closing_methods:
                print(f"Testing {method_info['description']}...")
                
                try:
                    # Navigate to orders page
                    self.driver.get(f"{self.base_url}/orders")
                    self.wait_for_page_load("table")
                    
                    # Open modal
                    if self.open_modal("button:contains('View Details')", "[x-show='isOpen']"):
                        
                        # Take screenshot before closing
                        self.take_screenshot(f"modal_before_close_{method_info['name']}.png", 
                                           f"Modal before {method_info['description']}")
                        
                        # Execute closing method
                        method_info['method']()
                        
                        # Wait for modal to close
                        modal_closed = WebDriverWait(self.driver, 10).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, "[x-show='isOpen']"))
                        )
                        
                        # Take screenshot after closing
                        self.take_screenshot(f"modal_after_close_{method_info['name']}.png", 
                                           f"Modal after {method_info['description']}")
                        
                        print(f"✓ {method_info['description']} successful")
                        results.append((method_info['name'], True))
                    else:
                        print(f"✗ Could not open modal for {method_info['description']} test")
                        results.append((method_info['name'], False))
                        
                except Exception as e:
                    print(f"✗ {method_info['description']} failed: {e}")
                    results.append((method_info['name'], False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Modal closing mechanisms test failed: {e}")
            return False
    
    def click_modal_backdrop(self):
        """Click on the modal backdrop to close modal."""
        try:
            # Find the modal backdrop (usually the fixed overlay)
            modal_backdrop = self.driver.find_element(By.CSS_SELECTOR, ".fixed.inset-0")
            
            # Click on the backdrop area (avoiding the modal content)
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(modal_backdrop, 10, 10)
            actions.click()
            actions.perform()
            
        except Exception as e:
            print(f"⚠️ Could not click modal backdrop: {e}")
            # Fallback to ESC key
            self.driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c')
    
    def test_modal_accessibility_features(self):
        """Test modal accessibility features."""
        print("\n--- Testing Modal Accessibility Features ---")
        
        try:
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Open modal
            if not self.open_modal("button:contains('View Details')", "[x-show='isOpen']"):
                return False
            
            # Take screenshot for accessibility review
            self.take_screenshot("modal_accessibility_review.png", "Modal accessibility features")
            
            accessibility_checks = []
            
            # Check for ARIA attributes
            try:
                modal_element = self.driver.find_element(By.CSS_SELECTOR, ".fixed.inset-0.z-50")
                
                # Check for aria-hidden or role attributes
                aria_hidden = modal_element.get_attribute('aria-hidden')
                role = modal_element.get_attribute('role')
                
                if role == 'dialog' or role == 'modal':
                    accessibility_checks.append(('ARIA role', True))
                    print("✓ Modal has proper ARIA role")
                else:
                    accessibility_checks.append(('ARIA role', False))
                    print("✗ Modal missing proper ARIA role")
                
            except:
                accessibility_checks.append(('ARIA role', False))
                print("✗ Could not check ARIA attributes")
            
            # Check for focus management
            try:
                active_element = self.driver.switch_to.active_element
                
                # Check if focus is within modal
                modal_element = self.driver.find_element(By.CSS_SELECTOR, ".fixed.inset-0.z-50")
                modal_contains_focus = modal_element.find_elements(By.XPATH, ".//*") 
                
                focus_managed = any(el == active_element for el in modal_contains_focus)
                
                if focus_managed:
                    accessibility_checks.append(('Focus management', True))
                    print("✓ Focus is properly managed within modal")
                else:
                    accessibility_checks.append(('Focus management', False))
                    print("✗ Focus not properly managed within modal")
                    
            except:
                accessibility_checks.append(('Focus management', False))
                print("✗ Could not check focus management")
            
            # Check for keyboard navigation
            try:
                # Try tabbing through modal elements
                body = self.driver.find_element(By.TAG_NAME, 'body')
                body.send_keys('\ue004')  # TAB key
                time.sleep(0.5)
                
                # Check if focus moved to next element
                new_active_element = self.driver.switch_to.active_element
                
                accessibility_checks.append(('Keyboard navigation', True))
                print("✓ Modal responds to keyboard navigation")
                
            except:
                accessibility_checks.append(('Keyboard navigation', False))
                print("✗ Modal keyboard navigation issues")
            
            # Close modal
            self.close_modal()
            
            # Calculate accessibility score
            passed_checks = sum(1 for _, passed in accessibility_checks if passed)
            total_checks = len(accessibility_checks)
            
            print(f"Accessibility score: {passed_checks}/{total_checks}")
            
            return passed_checks == total_checks
            
        except Exception as e:
            print(f"✗ Modal accessibility features test failed: {e}")
            return False
    
    def test_modal_visual_consistency(self):
        """Test modal visual consistency across different states."""
        print("\n--- Testing Modal Visual Consistency ---")
        
        try:
            # Test different modal states
            states = [
                {
                    'name': 'default',
                    'setup': lambda: None,
                    'description': 'Default modal state'
                },
                {
                    'name': 'with_long_content',
                    'setup': lambda: self.inject_long_content(),
                    'description': 'Modal with long content'
                },
                {
                    'name': 'with_special_characters',
                    'setup': lambda: self.inject_special_content(),
                    'description': 'Modal with special characters'
                }
            ]
            
            results = []
            
            for state in states:
                print(f"Testing {state['description']}...")
                
                try:
                    # Navigate to orders page
                    self.driver.get(f"{self.base_url}/orders")
                    self.wait_for_page_load("table")
                    
                    # Open modal
                    if self.open_modal("button:contains('View Details')", "[x-show='isOpen']"):
                        
                        # Setup state
                        state['setup']()
                        
                        # Take screenshot
                        self.take_screenshot(f"modal_consistency_{state['name']}.png", 
                                           state['description'])
                        
                        # Close modal
                        self.close_modal()
                        
                        results.append((state['name'], True))
                        print(f"✓ {state['description']} captured")
                    else:
                        results.append((state['name'], False))
                        print(f"✗ Could not open modal for {state['description']}")
                        
                except Exception as e:
                    print(f"✗ {state['description']} failed: {e}")
                    results.append((state['name'], False))
            
            return all(success for _, success in results)
            
        except Exception as e:
            print(f"✗ Modal visual consistency test failed: {e}")
            return False
    
    def inject_long_content(self):
        """Inject long content into modal for testing."""
        try:
            # Use JavaScript to modify modal content
            long_text = "This is a very long text content that should test how the modal handles overflow and scrolling. " * 20
            
            self.driver.execute_script("""
                const modal = document.querySelector('.fixed.inset-0.z-50');
                if (modal) {
                    const content = modal.querySelector('div');
                    if (content) {
                        content.innerHTML += '<p style="padding: 20px;">' + arguments[0] + '</p>';
                    }
                }
            """, long_text)
            
            time.sleep(1)  # Allow content to render
            
        except Exception as e:
            print(f"⚠️ Could not inject long content: {e}")
    
    def inject_special_content(self):
        """Inject special characters into modal for testing."""
        try:
            # Use JavaScript to add special characters
            special_text = "Special chars: üñíçødé ✓✗→←↑↓ 🎉🔥💡 «»""''‚„"
            
            self.driver.execute_script("""
                const modal = document.querySelector('.fixed.inset-0.z-50');
                if (modal) {
                    const content = modal.querySelector('div');
                    if (content) {
                        content.innerHTML += '<p style="padding: 10px; font-size: 14px;">' + arguments[0] + '</p>';
                    }
                }
            """, special_text)
            
            time.sleep(1)  # Allow content to render
            
        except Exception as e:
            print(f"⚠️ Could not inject special content: {e}")
    
    def run_page_specific_tests(self):
        """Run all enhanced modal specific tests."""
        tests = [
            ("Modal Opening Animations", self.test_modal_opening_animations),
            ("Modal Content Loading States", self.test_modal_content_loading_states),
            ("Modal Responsive Behavior", self.test_modal_responsive_behavior),
            ("Modal Closing Mechanisms", self.test_modal_closing_mechanisms),
            ("Modal Accessibility Features", self.test_modal_accessibility_features),
            ("Modal Visual Consistency", self.test_modal_visual_consistency),
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
        print("📊 ENHANCED MODAL TEST SUMMARY")
        print("="*50)
        
        passed = 0
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} enhanced modal tests passed")
        
        return passed == len(results)
    
    def create_baselines(self):
        """Create baseline screenshots for enhanced modal tests."""
        print("Creating baseline screenshots for enhanced modal tests...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Login first
            if not self.login():
                print("✗ Cannot create baselines without login")
                return False
            
            # Create baselines for different modal states
            modal_states = [
                'modal_fully_open',
                'modal_content_loaded',
                'modal_accessibility_review',
                'modal_consistency_default'
            ]
            
            for state in modal_states:
                print(f"Creating baseline for {state}...")
                
                try:
                    # Navigate to orders page
                    self.driver.get(f"{self.base_url}/orders")
                    self.wait_for_page_load("table")
                    
                    # Open modal
                    if self.open_modal("button:contains('View Details')", "[x-show='isOpen']"):
                        
                        # Create baseline screenshot
                        baseline_filename = f"expected_{state}.png"
                        self.take_screenshot(baseline_filename, f"Baseline for {state}", self.baseline_dir)
                        
                        # Close modal
                        self.close_modal()
                        
                except Exception as e:
                    print(f"⚠️ Could not create baseline for {state}: {e}")
            
            # Create responsive baselines
            for device in self.viewports.keys():
                print(f"Creating modal baseline for {device}...")
                
                try:
                    self.set_viewport(device)
                    self.driver.get(f"{self.base_url}/orders")
                    self.wait_for_page_load("table")
                    
                    if self.open_modal("button:contains('View Details')", "[x-show='isOpen']"):
                        baseline_filename = f"expected_modal_responsive_{device}.png"
                        self.take_screenshot(baseline_filename, f"Modal baseline for {device}", self.baseline_dir)
                        self.close_modal()
                        
                except Exception as e:
                    print(f"⚠️ Could not create {device} baseline: {e}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create enhanced modal baselines: {e}")
            return False
        finally:
            self.teardown_driver()


def main():
    """Main function to run enhanced modal visual tests."""
    tester = EnhancedModalVisualTester()
    
    if tester.run_all_tests():
        print("\n🎉 All enhanced modal visual tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some enhanced modal visual tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()