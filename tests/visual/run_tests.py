#!/usr/bin/env python3
"""
Simple test runner for visual tests.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from test_modal_design import ModalVisualTester

def main():
    """Run the visual tests."""
    print("🎨 Modal Visual Testing Suite")
    print("=" * 40)
    
    # Check if server is running
    import requests
    try:
        response = requests.get("http://127.0.0.1:8086/orders", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running on port 8086")
        else:
            print("⚠️  Server responded with status code:", response.status_code)
    except requests.exceptions.RequestException:
        print("⚠️  Warning: Server might not be running on port 8086")
        print("   Please start the server with: uvicorn main:app --reload --port 8086")
    
    print("\nStarting visual tests...")
    
    # Run tests
    tester = ModalVisualTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All visual tests passed!")
        print("📸 Screenshots saved in: tests/visual/screenshots/")
        sys.exit(0)
    else:
        print("\n❌ Some visual tests failed!")
        print("📸 Check screenshots in: tests/visual/screenshots/")
        sys.exit(1)

if __name__ == "__main__":
    main() 