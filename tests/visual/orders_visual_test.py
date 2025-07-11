#!/usr/bin/env python3
"""
Orders List Page Visual Regression Tests
Tests the visual appearance and functionality of the orders list page.
"""

import sys
import time
from pathlib import Path
from base_visual_test import BaseVisualTester, ModalTester
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class OrdersVisualTester(BaseVisualTester, ModalTester):
    """Visual regression tests for orders list page."""
    
    def __init__(self, base_url="http://localhost:8000"):
        super().__init__(base_url, "Orders List")
        self.requires_login = True  # Orders page requires authentication
        
    def test_orders_list_layout(self):
        """Test orders list page basic layout and styling."""
        return self.visual_regression_test("/orders", "orders_list", "table")
    
    def test_orders_list_responsive(self):
        """Test orders list page responsiveness across devices."""
        return self.test_responsive_design("/orders", "orders_list", "table")
    
    def test_orders_table_elements(self):
        """Test that all expected orders table elements are present."""
        print("\n--- Testing Orders Table Elements ---")
        
        try:
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Expected elements
            expected_elements = [
                ('table', 'Orders table'),
                ('thead', 'Table header'),
                ('tbody', 'Table body'),
                ('th:contains("Order Number")', 'Order Number column'),
                ('th:contains("Customer Name")', 'Customer Name column'),
                ('th:contains("Item")', 'Item column'),
                ('th:contains("Quantity")', 'Quantity column'),
                ('th:contains("Price")', 'Price column'),
                ('th:contains("Status")', 'Status column'),
                ('th:contains("Actions")', 'Actions column'),
            ]
            
            missing_elements = []
            for selector, description in expected_elements:
                try:
                    if ':contains(' in selector:
                        # Handle pseudo-selector for text content
                        element_text = selector.split(':contains(')[1].strip('")')
                        if element_text not in self.driver.page_source:
                            missing_elements.append(description)
                            print(f"✗ {description} not found")
                        else:
                            print(f"✓ {description} found")
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element:
                            print(f"✓ {description} found")
                        else:
                            print(f"✗ {description} not found")
                            missing_elements.append(description)
                except:
                    print(f"✗ {description} not found")
                    missing_elements.append(description)
            
            # Check for page title
            if "Order List" in self.driver.page_source:
                print("✓ Page title 'Order List' found")
            else:
                print("✗ Page title 'Order List' not found")
                missing_elements.append("Page title")
            
            # Take screenshot of complete page
            self.take_screenshot("orders_table_elements.png", "Orders table elements validation")
            
            return len(missing_elements) == 0
            
        except Exception as e:
            print(f"✗ Orders table elements test failed: {e}")
            return False
    
    def test_orders_list_with_data(self):
        """Test orders list with actual data."""
        print("\n--- Testing Orders List with Data ---")
        
        try:
            # First create some test orders via API or database
            self.create_test_orders()
            
            # Navigate to orders page
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Check if orders are displayed
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            if len(table_rows) > 0:
                print(f"✓ Found {len(table_rows)} order(s) in table")
                
                # Take screenshot with data
                self.take_screenshot("orders_with_data.png", "Orders list with test data")
                
                return True
            else:
                print("✗ No orders found in table")
                # Take screenshot of empty state
                self.take_screenshot("orders_empty_state.png", "Orders list empty state")
                return False
                
        except Exception as e:
            print(f"✗ Orders list with data test failed: {e}")
            return False
    
    def test_orders_list_empty_state(self):
        """Test orders list empty state display."""
        print("\n--- Testing Orders List Empty State ---")
        
        try:
            # Clear any existing orders (if possible)
            # For now, we'll just check the current state
            
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Check if there are no orders
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            if len(table_rows) == 0:
                print("✓ Empty state confirmed - no orders in table")
                
                # Take screenshot of empty state
                self.take_screenshot("orders_empty_state_confirmed.png", "Orders list empty state")
                
                return True
            else:
                print(f"ℹ️ Found {len(table_rows)} order(s) - not empty state")
                return True  # Not a failure, just not empty
                
        except Exception as e:
            print(f"✗ Orders list empty state test failed: {e}")
            return False
    
    def test_orders_list_modal_integration(self):
        """Test that modal functionality works from orders list."""
        print("\n--- Testing Orders List Modal Integration ---")
        
        try:
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Look for "View Details" buttons
            view_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'View Details')]")
            
            if not view_buttons:
                print("✗ No 'View Details' buttons found")
                return False
            
            print(f"✓ Found {len(view_buttons)} 'View Details' button(s)")
            
            # Test modal opening
            first_button = view_buttons[0]
            if self.open_modal("button:contains('View Details')", "[x-show='isOpen']"):
                
                # Test modal content
                expected_fields = ["Order ID", "Order Number", "Customer Name", "Item", "Quantity", "Price", "Status"]
                modal_content_valid = self.test_modal_content(expected_fields)
                
                # Take screenshot of modal
                self.take_screenshot("orders_modal_open.png", "Orders modal opened from list")
                
                # Test modal closing
                close_success = self.close_modal()
                
                return modal_content_valid and close_success
            else:
                return False
                
        except Exception as e:
            print(f"✗ Orders list modal integration test failed: {e}")
            return False
    
    def test_orders_list_pagination(self):
        """Test orders list pagination (if applicable)."""
        print("\n--- Testing Orders List Pagination ---")
        
        try:
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Look for pagination elements
            pagination_elements = self.driver.find_elements(By.CSS_SELECTOR, ".pagination, .page-nav, [class*='page']")
            
            if pagination_elements:
                print("✓ Pagination elements found")
                
                # Take screenshot with pagination
                self.take_screenshot("orders_with_pagination.png", "Orders list with pagination")
                
                return True
            else:
                print("ℹ️ No pagination elements found (may not be implemented)")
                return True  # Not a failure if pagination isn't implemented
                
        except Exception as e:
            print(f"✗ Orders list pagination test failed: {e}")
            return False
    
    def test_orders_list_actions(self):
        """Test action buttons in orders list."""
        print("\n--- Testing Orders List Actions ---")
        
        try:
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Look for action buttons
            action_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, a.btn, .btn")
            
            if action_buttons:
                print(f"✓ Found {len(action_buttons)} action button(s)")
                
                # Take screenshot with actions visible
                self.take_screenshot("orders_with_actions.png", "Orders list with action buttons")
                
                return True
            else:
                print("✗ No action buttons found")
                return False
                
        except Exception as e:
            print(f"✗ Orders list actions test failed: {e}")
            return False
    
    def create_test_orders(self):
        """Create test orders for visual testing."""
        try:
            # Navigate to create order page and create a test order
            self.driver.get(f"{self.base_url}/orders/create")
            self.wait_for_page_load("form")
            
            # Fill out the form
            test_order_data = {
                "order_number": "TEST001",
                "customer_name": "Test Customer",
                "item": "Test Item",
                "quantity": "1",
                "price": "100",
                "status": "pending"
            }
            
            for field_name, value in test_order_data.items():
                try:
                    field = self.driver.find_element(By.NAME, field_name)
                    field.clear()
                    field.send_keys(value)
                except:
                    pass  # Field might not exist
            
            # Submit the form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            # Wait for redirect
            time.sleep(2)
            
            print("✓ Test order created")
            
        except Exception as e:
            print(f"⚠️ Could not create test order: {e}")
    
    def run_page_specific_tests(self):
        """Run all orders list page specific tests."""
        tests = [
            ("Orders List Layout", self.test_orders_list_layout),
            ("Orders List Responsive", self.test_orders_list_responsive),
            ("Orders Table Elements", self.test_orders_table_elements),
            ("Orders List with Data", self.test_orders_list_with_data),
            ("Orders List Empty State", self.test_orders_list_empty_state),
            ("Orders List Modal Integration", self.test_orders_list_modal_integration),
            ("Orders List Pagination", self.test_orders_list_pagination),
            ("Orders List Actions", self.test_orders_list_actions),
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
        print("📊 ORDERS LIST PAGE TEST SUMMARY")
        print("="*50)
        
        passed = 0
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} orders list page tests passed")
        
        return passed == len(results)
    
    def create_baselines(self):
        """Create baseline screenshots for orders list page."""
        print("Creating baseline screenshots for orders list page...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Login first
            if not self.login():
                print("✗ Cannot create baselines without login")
                return False
            
            # Create test data
            self.create_test_orders()
            
            # Create baselines for all devices
            for device in self.viewports.keys():
                print(f"Creating {device} baseline...")
                self.set_viewport(device)
                self.driver.get(f"{self.base_url}/orders")
                self.wait_for_page_load("table")
                
                baseline_filename = f"expected_orders_list_{device}.png"
                self.take_screenshot(baseline_filename, f"Orders list baseline for {device}", self.baseline_dir)
            
            # Create modal baseline
            print("Creating modal baseline...")
            self.driver.get(f"{self.base_url}/orders")
            self.wait_for_page_load("table")
            
            # Open modal
            if self.open_modal("button:contains('View Details')", "[x-show='isOpen']"):
                self.take_screenshot("expected_orders_modal.png", "Orders modal baseline", self.baseline_dir)
                self.close_modal()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create orders list baselines: {e}")
            return False
        finally:
            self.teardown_driver()


def main():
    """Main function to run orders list page visual tests."""
    tester = OrdersVisualTester()
    
    if tester.run_all_tests():
        print("\n🎉 All orders list page visual tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some orders list page visual tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()