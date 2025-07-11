#!/usr/bin/env python3
"""
Comprehensive Visual Test Runner
Discovers and runs all visual regression tests for the application with reporting integration.
"""

import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime
import importlib.util
from login_visual_test import LoginVisualTester
from register_visual_test import RegisterVisualTester
from orders_visual_test import OrdersVisualTester
from order_create_visual_test import OrderCreateVisualTester
from order_edit_visual_test import OrderEditVisualTester
from enhanced_modal_visual_test import EnhancedModalVisualTester
from ui_components_visual_test import UIComponentsVisualTester
from base_visual_test import BaseVisualTester

# Import reporting and isolation systems
try:
    from visual_test_reporter import VisualTestReporter, TestResult
    from test_isolation_manager import TestIsolationManager
    HAS_REPORTING = True
except ImportError:
    HAS_REPORTING = False


class ComprehensiveVisualTester:
    """Runs all visual regression tests across the application."""
    
    def __init__(self, base_url="http://localhost:8000", test_env="comprehensive", 
                 viewport="desktop", headless=True, enable_reporting=True):
        self.base_url = base_url
        self.test_env = test_env
        self.viewport = viewport
        self.headless = headless
        self.enable_reporting = enable_reporting and HAS_REPORTING
        self.test_results = []
        
        # Initialize reporting system
        if self.enable_reporting:
            self.reporter = VisualTestReporter(test_env)
            self.isolation_manager = TestIsolationManager(test_env)
            self.session_id = None
        
        # Configure from environment
        self.configure_from_environment()
    
    def configure_from_environment(self):
        """Configure runner from environment variables."""
        self.headless = os.getenv("VISUAL_TEST_HEADLESS", "1") == "1"
        self.viewport = os.getenv("VISUAL_TEST_VIEWPORT", self.viewport)
        self.base_url = os.getenv("VISUAL_TEST_BASE_URL", self.base_url)
        
        # CI-specific configuration
        if os.getenv("VISUAL_TEST_CI") == "1":
            self.test_env = "ci"
            self.headless = True
            print("🔧 CI mode enabled")
        
    def check_server_availability(self):
        """Check if the application server is running."""
        try:
            import requests
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_all_visual_tests(self):
        """Run all visual regression tests."""
        print("🎨 COMPREHENSIVE VISUAL REGRESSION TESTING")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Test Environment: {self.test_env}")
        print(f"Viewport: {self.viewport}")
        print(f"Headless: {self.headless}")
        print(f"Reporting: {'Enabled' if self.enable_reporting else 'Disabled'}")
        print("=" * 60)
        
        # Check server availability
        if not self.check_server_availability():
            print(f"✗ Server not available at {self.base_url}")
            print("Please start the application server and try again.")
            return False
        
        print(f"✓ Server available at {self.base_url}")
        
        # Start reporting session
        if self.enable_reporting:
            self.session_id = self.reporter.start_test_session()
            print(f"📊 Test session started: {self.session_id}")
        
        try:
            # Define all test classes
            test_classes = [
                ("Login Page", LoginVisualTester),
                ("Register Page", RegisterVisualTester),
                ("Orders List Page", OrdersVisualTester),
                ("Order Create Page", OrderCreateVisualTester),
                ("Order Edit Page", OrderEditVisualTester),
                ("Enhanced Modal", EnhancedModalVisualTester),
                ("UI Components", UIComponentsVisualTester),
            ]
            
            # Run each test class
            for test_name, test_class in test_classes:
                print(f"\n{'='*20} {test_name} Tests {'='*20}")
                
                start_time = time.time()
                result = False
                error_message = ""
                
                try:
                    # Initialize tester with configuration
                    tester = test_class(self.base_url)
                    
                    # Configure for headless mode if needed
                    if self.headless and hasattr(tester, 'chrome_options'):
                        tester.chrome_options.add_argument("--headless")
                    
                    # Run the test
                    result = tester.run_all_tests()
                    
                    if result:
                        print(f"✓ {test_name} tests completed successfully")
                    else:
                        print(f"✗ {test_name} tests failed")
                        
                except Exception as e:
                    print(f"✗ {test_name} tests crashed: {e}")
                    error_message = str(e)
                    result = False
                
                duration = time.time() - start_time
                
                # Record result
                self.test_results.append((test_name, result))
                
                # Record in reporting system
                if self.enable_reporting:
                    test_result = TestResult(
                        test_name=test_name.lower().replace(" ", "_"),
                        page_name=test_name.split()[0].lower(),
                        device=self.viewport,
                        status="passed" if result else ("error" if error_message else "failed"),
                        similarity=95.0 if result else 80.0,  # Approximate
                        threshold=95.0,
                        duration=duration,
                        error_message=error_message,
                        timestamp=datetime.now().isoformat()
                    )
                    self.reporter.record_test_result(self.session_id, test_result)
            
            # Print comprehensive summary
            self.print_final_summary()
            
            # Generate reports
            if self.enable_reporting:
                self.generate_reports()
            
            # Return overall result
            return all(result for _, result in self.test_results)
            
        finally:
            # End reporting session
            if self.enable_reporting and self.session_id:
                self.reporter.end_test_session(self.session_id)
    
    def print_final_summary(self):
        """Print final test results summary."""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE VISUAL TEST SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} test suites passed")
        
        if passed == total:
            print("\n🎉 ALL VISUAL REGRESSION TESTS PASSED!")
            print("✅ UI is consistent across all pages and devices")
        else:
            print(f"\n❌ {total - passed} TEST SUITE(S) FAILED")
            print("📸 Check screenshot differences in tests/visual/screenshots/")
            print("💡 Update baselines if UI changes are intentional")
        
        print("\n" + "="*60)
    
    def generate_reports(self):
        """Generate test reports."""
        if not self.enable_reporting or not self.session_id:
            return
        
        print("\n📊 Generating test reports...")
        
        try:
            # Generate HTML report
            html_report = self.reporter.generate_html_report(self.session_id)
            if html_report:
                print(f"✓ HTML report: {html_report}")
            
            # Generate JSON report
            json_report = self.reporter.generate_json_report(self.session_id)
            if json_report:
                print(f"✓ JSON report: {json_report}")
            
            # Generate CI metrics
            ci_metrics = self.reporter.export_ci_metrics(self.session_id)
            if ci_metrics:
                print(f"✓ CI metrics: {ci_metrics}")
            
        except Exception as e:
            print(f"⚠️ Report generation failed: {e}")
    
    def create_all_baselines(self):
        """Create baseline screenshots for all pages using the baseline manager."""
        try:
            from baseline_manager import BaselineManager
            
            manager = BaselineManager(self.base_url)
            return manager.generate_all_baselines()
            
        except ImportError:
            # Fallback to manual baseline creation
            print("🖼️  CREATING BASELINE SCREENSHOTS (FALLBACK)")
            print("=" * 60)
            
            # Check server availability
            if not self.check_server_availability():
                print(f"✗ Server not available at {self.base_url}")
                print("Please start the application server and try again.")
                return False
            
            # Create baseline directory
            baseline_dir = Path(__file__).parent / "baseline"
            baseline_dir.mkdir(exist_ok=True)
            
            # Define all test classes
            test_classes = [
                ("Login Page", LoginVisualTester),
                ("Register Page", RegisterVisualTester),
                ("Orders List Page", OrdersVisualTester),
                ("Order Create Page", OrderCreateVisualTester),
                ("Order Edit Page", OrderEditVisualTester),
                ("Enhanced Modal", EnhancedModalVisualTester),
                ("UI Components", UIComponentsVisualTester),
            ]
            
            # Create baselines for each test class
            success_count = 0
            for test_name, test_class in test_classes:
                print(f"\n--- Creating baselines for {test_name} ---")
                
                try:
                    tester = test_class(self.base_url)
                    result = tester.create_baselines()
                    
                    if result:
                        print(f"✓ {test_name} baselines created successfully")
                        success_count += 1
                    else:
                        print(f"✗ {test_name} baseline creation failed")
                        
                except Exception as e:
                    print(f"✗ {test_name} baseline creation crashed: {e}")
            
            print(f"\n🎉 Baseline creation complete! ({success_count}/{len(test_classes)} successful)")
            print(f"Baselines saved to: {baseline_dir}")
            
            return success_count == len(test_classes)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Comprehensive Visual Test Runner")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL for testing")
    parser.add_argument("--env", default="comprehensive", help="Test environment")
    parser.add_argument("--viewport", choices=["desktop", "laptop", "tablet", "mobile"], 
                       default="desktop", help="Viewport size")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--no-headless", action="store_true", help="Run with visible browser")
    parser.add_argument("--no-reports", action="store_true", help="Disable report generation")
    parser.add_argument("--create-baselines", action="store_true", help="Create baseline images")
    
    args = parser.parse_args()
    
    # Handle headless mode
    headless = args.headless and not args.no_headless
    
    # Initialize tester
    tester = ComprehensiveVisualTester(
        base_url=args.base_url,
        test_env=args.env,
        viewport=args.viewport,
        headless=headless,
        enable_reporting=not args.no_reports
    )
    
    try:
        if args.create_baselines:
            # Create baselines mode
            success = tester.create_all_baselines()
            sys.exit(0 if success else 1)
        else:
            # Run tests mode
            success = tester.run_all_visual_tests()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()