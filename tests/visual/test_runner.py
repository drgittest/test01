#!/usr/bin/env python3
"""
Advanced Visual Test Runner
Automatically discovers and runs all visual test modules.
"""

import sys
import os
import importlib
from pathlib import Path
from comprehensive_visual_test import ComprehensiveVisualTester


class VisualTestRunner:
    """Advanced test runner that discovers and executes all visual tests."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent
        self.test_results = []
        
    def discover_test_modules(self):
        """Discover all visual test modules."""
        test_modules = []
        
        # Look for all files ending with 'visual_test.py'
        for test_file in self.test_dir.glob("*_visual_test.py"):
            if test_file.name != "base_visual_test.py":  # Skip base class
                module_name = test_file.stem
                test_modules.append(module_name)
        
        return test_modules
    
    def run_individual_test_module(self, module_name):
        """Run a specific visual test module."""
        print(f"\n{'='*20} Running {module_name} {'='*20}")
        
        try:
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location(module_name, self.test_dir / f"{module_name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the tester class (should end with 'VisualTester')
            tester_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    attr_name.endswith('VisualTester') and 
                    attr_name != 'BaseVisualTester'):
                    tester_class = attr
                    break
            
            if not tester_class:
                print(f"✗ No tester class found in {module_name}")
                return False
            
            # Run the tests
            tester = tester_class(self.base_url)
            result = tester.run_all_tests()
            
            return result
            
        except Exception as e:
            print(f"✗ Failed to run {module_name}: {e}")
            return False
    
    def run_all_discovered_tests(self):
        """Run all discovered visual test modules."""
        print("🔍 DISCOVERING AND RUNNING ALL VISUAL TESTS")
        print("=" * 60)
        
        # Discover test modules
        test_modules = self.discover_test_modules()
        
        if not test_modules:
            print("✗ No visual test modules found")
            return False
        
        print(f"📋 Found {len(test_modules)} visual test modules:")
        for module in test_modules:
            print(f"  - {module}")
        
        # Run each test module
        for module_name in test_modules:
            result = self.run_individual_test_module(module_name)
            self.test_results.append((module_name, result))
        
        # Print summary
        self.print_summary()
        
        return all(result for _, result in self.test_results)
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("📊 VISUAL TEST DISCOVERY SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for module_name, result in self.test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {module_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} visual test modules passed")
        
        if passed == total:
            print("\n🎉 ALL VISUAL TEST MODULES PASSED!")
        else:
            print(f"\n❌ {total - passed} VISUAL TEST MODULE(S) FAILED")
    
    def create_all_baselines(self):
        """Create baselines for all discovered test modules."""
        print("🖼️  CREATING BASELINES FOR ALL VISUAL TESTS")
        print("=" * 60)
        
        test_modules = self.discover_test_modules()
        
        for module_name in test_modules:
            print(f"\n--- Creating baselines for {module_name} ---")
            
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(module_name, self.test_dir / f"{module_name}.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find the tester class
                tester_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name.endswith('VisualTester') and 
                        attr_name != 'BaseVisualTester'):
                        tester_class = attr
                        break
                
                if tester_class:
                    tester = tester_class(self.base_url)
                    if hasattr(tester, 'create_baselines'):
                        tester.create_baselines()
                        print(f"✓ Baselines created for {module_name}")
                    else:
                        print(f"⚠️  {module_name} doesn't support baseline creation")
                else:
                    print(f"✗ No tester class found in {module_name}")
                    
            except Exception as e:
                print(f"✗ Failed to create baselines for {module_name}: {e}")
        
        print("\n🎉 Baseline creation process complete!")


def main():
    """Main function."""
    runner = VisualTestRunner()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create-baselines":
            runner.create_all_baselines()
            return 0
        elif sys.argv[1] == "--comprehensive":
            # Run the comprehensive tester instead
            comprehensive_tester = ComprehensiveVisualTester()
            if comprehensive_tester.run_all_visual_tests():
                return 0
            else:
                return 1
    
    # Default: run all discovered tests
    if runner.run_all_discovered_tests():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())