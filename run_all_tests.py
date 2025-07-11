#!/usr/bin/env python3
"""
Comprehensive Test Runner for Order Management System
Runs all tests: pytest, integration, and visual tests
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_server_running():
    """Check if the FastAPI server is running on port 8000"""
    try:
        import requests
        response = requests.get("http://localhost:8000", timeout=2)
        return response.status_code == 200
    except:
        return False

def create_visual_baselines():
    """Create baseline screenshots for visual regression tests."""
    print("🖼️  Creating Visual Test Baselines")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_running():
        print("⚠️  FastAPI server not running on port 8000")
        print("   Please run 'uvicorn main:app --reload --port 8000' in another terminal")
        print("   Then run this script again with --create-baselines")
        return False
    
    print("✅ Server is running on port 8000")
    
    # Create baselines using comprehensive visual test
    print("\n📋 Creating comprehensive visual baselines...")
    baseline_result = run_command("cd tests/visual && python comprehensive_visual_test.py --create-baselines", "Create Visual Baselines")
    
    if baseline_result:
        print("🎉 Visual baselines created successfully!")
        print("📸 Baseline screenshots saved to tests/visual/baseline/")
        return True
    else:
        print("❌ Failed to create visual baselines")
        return False

def main():
    print("🚀 Starting Comprehensive Test Suite")
    print("=" * 60)
    
    # Check for baseline creation mode
    if len(sys.argv) > 1 and sys.argv[1] == "--create-baselines":
        return 0 if create_visual_baselines() else 1
    
    # Track test results
    results = []
    
    # 1. Run pytest tests (test_main.py)
    print("\n📋 Step 1: Running pytest tests...")
    pytest_result = run_command("python -m pytest test_main.py -v", "Pytest Tests (test_main.py)")
    results.append(("Pytest Tests", pytest_result))
    
    # 2. Check if server is running for integration/visual tests
    print("\n📋 Step 2: Checking server status...")
    if not check_server_running():
        print("⚠️  FastAPI server not running on port 8000")
        print("   Starting server for integration tests...")
        print("   Please run 'uvicorn main:app --reload --port 8000' in another terminal")
        print("   Then run this script again.")
        return
    
    print("✅ Server is running on port 8000")
    
    # 3. Run integration tests
    print("\n📋 Step 3: Running integration tests...")
    integration_result = run_command("python tests/integration_test.py", "Integration Tests")
    results.append(("Integration Tests", integration_result))
    
    # 4. Run comprehensive visual regression tests
    print("\n📋 Step 4: Running comprehensive visual regression tests...")
    visual_command = "cd tests/visual && python comprehensive_visual_test.py --headless"
    if "--create-baselines" in sys.argv:
        visual_command += " --create-baselines"
    visual_result = run_command(visual_command, "Comprehensive Visual Tests")
    results.append(("Visual Tests", visual_result))
    
    # 5. Run legacy visual tests (for backward compatibility)
    print("\n📋 Step 5: Running legacy visual tests...")
    legacy_visual_result = run_command("cd tests/visual && python simple_visual_test.py", "Legacy Visual Tests")
    results.append(("Legacy Visual Tests", legacy_visual_result))
    
    # 6. Run modal design tests
    print("\n📋 Step 6: Running modal design tests...")
    modal_result = run_command("cd tests/visual && python test_modal_design.py", "Modal Design Tests")
    results.append(("Modal Tests", modal_result))
    
    # 7. Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Your application is ready for production.")
        print("\n💡 Tips:")
        print("  - Run with '--create-baselines' to update visual baselines")
        print("  - Visual tests require the server to be running on port 8000")
        print("  - Check tests/visual/screenshots/ for visual test outputs")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        print("\n🔍 Troubleshooting:")
        print("  - For visual test failures, check tests/visual/screenshots/")
        print("  - Update baselines if UI changes are intentional")
        print("  - Ensure server is running for integration/visual tests")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 