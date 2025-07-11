#!/usr/bin/env python3
"""
Baseline Management System
Comprehensive baseline generation, versioning, and comparison management.
"""

import sys
import os
import shutil
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import importlib.util

# Import all test modules
from login_visual_test import LoginVisualTester
from register_visual_test import RegisterVisualTester
from orders_visual_test import OrdersVisualTester
from order_create_visual_test import OrderCreateVisualTester
from order_edit_visual_test import OrderEditVisualTester
from enhanced_modal_visual_test import EnhancedModalVisualTester
from ui_components_visual_test import UIComponentsVisualTester


class BaselineManager:
    """Manages visual test baselines with versioning and comparison capabilities."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent
        self.baseline_dir = self.test_dir / "baseline"
        self.baseline_versions_dir = self.test_dir / "baseline_versions"
        self.baseline_metadata_file = self.baseline_dir / "baseline_metadata.json"
        
        # Create directories
        self.baseline_dir.mkdir(exist_ok=True)
        self.baseline_versions_dir.mkdir(exist_ok=True)
        
        # Test modules configuration
        self.test_modules = {
            "login": {"class": LoginVisualTester, "name": "Login Page"},
            "register": {"class": RegisterVisualTester, "name": "Register Page"},
            "orders": {"class": OrdersVisualTester, "name": "Orders List"},
            "order_create": {"class": OrderCreateVisualTester, "name": "Order Create"},
            "order_edit": {"class": OrderEditVisualTester, "name": "Order Edit"},
            "enhanced_modal": {"class": EnhancedModalVisualTester, "name": "Enhanced Modal"},
            "ui_components": {"class": UIComponentsVisualTester, "name": "UI Components"},
        }
        
        # Viewport configurations
        self.viewports = {
            'desktop': (1920, 1080),
            'laptop': (1366, 768),
            'tablet': (768, 1024),
            'mobile': (375, 667)
        }
        
    def check_server_availability(self):
        """Check if the application server is running."""
        try:
            import requests
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def load_baseline_metadata(self) -> Dict:
        """Load baseline metadata from JSON file."""
        if self.baseline_metadata_file.exists():
            try:
                with open(self.baseline_metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_baseline_metadata(self, metadata: Dict):
        """Save baseline metadata to JSON file."""
        try:
            with open(self.baseline_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save baseline metadata: {e}")
    
    def create_baseline_version(self, version_name: str) -> Path:
        """Create a new baseline version directory."""
        version_dir = self.baseline_versions_dir / version_name
        version_dir.mkdir(exist_ok=True)
        return version_dir
    
    def backup_current_baselines(self, version_name: str = None) -> str:
        """Backup current baselines to versioned directory."""
        if not version_name:
            version_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        version_dir = self.create_baseline_version(version_name)
        
        # Copy all baseline files
        baseline_files = list(self.baseline_dir.glob("expected_*.png"))
        
        if baseline_files:
            for baseline_file in baseline_files:
                shutil.copy2(baseline_file, version_dir / baseline_file.name)
            
            # Copy metadata
            if self.baseline_metadata_file.exists():
                shutil.copy2(self.baseline_metadata_file, version_dir / "baseline_metadata.json")
            
            print(f"✓ Backed up {len(baseline_files)} baseline files to {version_dir}")
            return version_name
        else:
            print("⚠️ No baseline files found to backup")
            return ""
    
    def restore_baseline_version(self, version_name: str) -> bool:
        """Restore baselines from a specific version."""
        version_dir = self.baseline_versions_dir / version_name
        
        if not version_dir.exists():
            print(f"✗ Version '{version_name}' does not exist")
            return False
        
        baseline_files = list(version_dir.glob("expected_*.png"))
        
        if not baseline_files:
            print(f"✗ No baseline files found in version '{version_name}'")
            return False
        
        # Clear current baselines
        for existing_file in self.baseline_dir.glob("expected_*.png"):
            existing_file.unlink()
        
        # Copy version files to baseline directory
        for baseline_file in baseline_files:
            shutil.copy2(baseline_file, self.baseline_dir / baseline_file.name)
        
        # Restore metadata
        metadata_file = version_dir / "baseline_metadata.json"
        if metadata_file.exists():
            shutil.copy2(metadata_file, self.baseline_metadata_file)
        
        print(f"✓ Restored {len(baseline_files)} baseline files from version '{version_name}'")
        return True
    
    def list_baseline_versions(self) -> List[str]:
        """List all available baseline versions."""
        versions = []
        for version_dir in self.baseline_versions_dir.iterdir():
            if version_dir.is_dir():
                versions.append(version_dir.name)
        return sorted(versions)
    
    def generate_all_baselines(self, include_modules: List[str] = None) -> bool:
        """Generate baselines for all or specified test modules."""
        print("🖼️ COMPREHENSIVE BASELINE GENERATION")
        print("=" * 60)
        
        # Check server availability
        if not self.check_server_availability():
            print(f"✗ Server not available at {self.base_url}")
            print("Please start the application server and try again.")
            return False
        
        print(f"✓ Server available at {self.base_url}")
        
        # Backup existing baselines
        backup_version = self.backup_current_baselines()
        if backup_version:
            print(f"✓ Current baselines backed up as version: {backup_version}")
        
        # Determine which modules to process
        modules_to_process = include_modules if include_modules else list(self.test_modules.keys())
        
        # Generate baselines for each module
        baseline_metadata = {
            "created_at": datetime.now().isoformat(),
            "server_url": self.base_url,
            "modules": {},
            "viewports": self.viewports,
            "total_baselines": 0
        }
        
        total_success = 0
        total_modules = len(modules_to_process)
        
        for module_name in modules_to_process:
            if module_name not in self.test_modules:
                print(f"⚠️ Unknown module: {module_name}")
                continue
            
            module_config = self.test_modules[module_name]
            print(f"\n--- Creating baselines for {module_config['name']} ---")
            
            try:
                # Initialize tester
                tester = module_config['class'](self.base_url)
                
                # Create baselines
                if hasattr(tester, 'create_baselines'):
                    baseline_count_before = len(list(self.baseline_dir.glob("expected_*.png")))
                    
                    success = tester.create_baselines()
                    
                    baseline_count_after = len(list(self.baseline_dir.glob("expected_*.png")))
                    new_baselines = baseline_count_after - baseline_count_before
                    
                    if success:
                        print(f"✓ {module_config['name']} baselines created successfully")
                        print(f"  Generated {new_baselines} new baseline(s)")
                        
                        baseline_metadata["modules"][module_name] = {
                            "name": module_config['name'],
                            "success": True,
                            "baselines_created": new_baselines,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        total_success += 1
                    else:
                        print(f"✗ {module_config['name']} baseline creation failed")
                        baseline_metadata["modules"][module_name] = {
                            "name": module_config['name'],
                            "success": False,
                            "error": "Baseline creation failed",
                            "created_at": datetime.now().isoformat()
                        }
                else:
                    print(f"⚠️ {module_config['name']} doesn't support baseline creation")
                    baseline_metadata["modules"][module_name] = {
                        "name": module_config['name'],
                        "success": False,
                        "error": "Baseline creation not supported",
                        "created_at": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                print(f"✗ {module_config['name']} baseline creation crashed: {e}")
                baseline_metadata["modules"][module_name] = {
                    "name": module_config['name'],
                    "success": False,
                    "error": str(e),
                    "created_at": datetime.now().isoformat()
                }
        
        # Update metadata
        baseline_metadata["total_baselines"] = len(list(self.baseline_dir.glob("expected_*.png")))
        baseline_metadata["successful_modules"] = total_success
        baseline_metadata["total_modules"] = total_modules
        
        self.save_baseline_metadata(baseline_metadata)
        
        # Print summary
        print(f"\n{'='*60}")
        print("📊 BASELINE GENERATION SUMMARY")
        print("="*60)
        
        print(f"Successful modules: {total_success}/{total_modules}")
        print(f"Total baselines created: {baseline_metadata['total_baselines']}")
        
        if backup_version:
            print(f"Previous baselines backed up as: {backup_version}")
        
        print(f"Baseline metadata saved to: {self.baseline_metadata_file}")
        
        if total_success == total_modules:
            print("\n🎉 All baseline generation completed successfully!")
            return True
        else:
            print(f"\n⚠️ {total_modules - total_success} module(s) failed")
            return False
    
    def generate_module_baselines(self, module_name: str) -> bool:
        """Generate baselines for a specific module."""
        return self.generate_all_baselines([module_name])
    
    def generate_viewport_baselines(self, viewport: str) -> bool:
        """Generate baselines for a specific viewport size."""
        print(f"🖼️ GENERATING BASELINES FOR {viewport.upper()} VIEWPORT")
        print("=" * 60)
        
        if viewport not in self.viewports:
            print(f"✗ Unknown viewport: {viewport}")
            print(f"Available viewports: {', '.join(self.viewports.keys())}")
            return False
        
        # Check server availability
        if not self.check_server_availability():
            print(f"✗ Server not available at {self.base_url}")
            return False
        
        success_count = 0
        total_modules = len(self.test_modules)
        
        for module_name, module_config in self.test_modules.items():
            print(f"\n--- Creating {viewport} baselines for {module_config['name']} ---")
            
            try:
                tester = module_config['class'](self.base_url)
                
                if hasattr(tester, 'create_baselines'):
                    # Override viewport creation for specific viewport
                    original_viewports = tester.viewports
                    tester.viewports = {viewport: self.viewports[viewport]}
                    
                    success = tester.create_baselines()
                    
                    # Restore original viewports
                    tester.viewports = original_viewports
                    
                    if success:
                        print(f"✓ {module_config['name']} {viewport} baselines created")
                        success_count += 1
                    else:
                        print(f"✗ {module_config['name']} {viewport} baseline creation failed")
                        
            except Exception as e:
                print(f"✗ {module_config['name']} {viewport} baseline creation crashed: {e}")
        
        print(f"\n{viewport.upper()} baseline generation: {success_count}/{total_modules} successful")
        return success_count == total_modules
    
    def compare_baselines(self, version1: str, version2: str = "current") -> Dict:
        """Compare baselines between two versions."""
        print(f"📊 COMPARING BASELINES: {version1} vs {version2}")
        print("=" * 60)
        
        if version2 == "current":
            version2_dir = self.baseline_dir
        else:
            version2_dir = self.baseline_versions_dir / version2
            if not version2_dir.exists():
                print(f"✗ Version '{version2}' does not exist")
                return {}
        
        version1_dir = self.baseline_versions_dir / version1
        if not version1_dir.exists():
            print(f"✗ Version '{version1}' does not exist")
            return {}
        
        # Get baseline files from both versions
        v1_files = {f.name: f for f in version1_dir.glob("expected_*.png")}
        v2_files = {f.name: f for f in version2_dir.glob("expected_*.png")}
        
        comparison_result = {
            "version1": version1,
            "version2": version2,
            "compared_at": datetime.now().isoformat(),
            "files": {},
            "summary": {
                "total_files": 0,
                "identical": 0,
                "different": 0,
                "missing_in_v1": 0,
                "missing_in_v2": 0
            }
        }
        
        # Files in both versions
        common_files = set(v1_files.keys()) & set(v2_files.keys())
        
        for filename in common_files:
            # Simple file size comparison (can be enhanced with image comparison)
            v1_size = v1_files[filename].stat().st_size
            v2_size = v2_files[filename].stat().st_size
            
            if v1_size == v2_size:
                comparison_result["files"][filename] = {"status": "identical", "size_diff": 0}
                comparison_result["summary"]["identical"] += 1
            else:
                comparison_result["files"][filename] = {"status": "different", "size_diff": v2_size - v1_size}
                comparison_result["summary"]["different"] += 1
        
        # Files only in version 1
        v1_only = set(v1_files.keys()) - set(v2_files.keys())
        for filename in v1_only:
            comparison_result["files"][filename] = {"status": "missing_in_v2"}
            comparison_result["summary"]["missing_in_v2"] += 1
        
        # Files only in version 2
        v2_only = set(v2_files.keys()) - set(v1_files.keys())
        for filename in v2_only:
            comparison_result["files"][filename] = {"status": "missing_in_v1"}
            comparison_result["summary"]["missing_in_v1"] += 1
        
        comparison_result["summary"]["total_files"] = len(comparison_result["files"])
        
        # Print summary
        print(f"Total files compared: {comparison_result['summary']['total_files']}")
        print(f"Identical: {comparison_result['summary']['identical']}")
        print(f"Different: {comparison_result['summary']['different']}")
        print(f"Missing in {version1}: {comparison_result['summary']['missing_in_v1']}")
        print(f"Missing in {version2}: {comparison_result['summary']['missing_in_v2']}")
        
        return comparison_result
    
    def clean_old_versions(self, keep_count: int = 5) -> int:
        """Clean old baseline versions, keeping only the most recent ones."""
        versions = self.list_baseline_versions()
        
        if len(versions) <= keep_count:
            print(f"✓ Only {len(versions)} versions exist, no cleanup needed")
            return 0
        
        # Sort by creation time (assuming timestamp in name)
        versions.sort(reverse=True)
        
        versions_to_delete = versions[keep_count:]
        deleted_count = 0
        
        for version in versions_to_delete:
            try:
                version_dir = self.baseline_versions_dir / version
                shutil.rmtree(version_dir)
                deleted_count += 1
                print(f"✓ Deleted old baseline version: {version}")
            except Exception as e:
                print(f"✗ Could not delete version {version}: {e}")
        
        print(f"✓ Cleaned {deleted_count} old baseline versions")
        return deleted_count
    
    def get_baseline_info(self) -> Dict:
        """Get information about current baselines."""
        info = {
            "baseline_directory": str(self.baseline_dir),
            "baseline_files": [],
            "total_baselines": 0,
            "versions_directory": str(self.baseline_versions_dir),
            "available_versions": self.list_baseline_versions(),
            "metadata": self.load_baseline_metadata()
        }
        
        # Get baseline files
        baseline_files = list(self.baseline_dir.glob("expected_*.png"))
        info["total_baselines"] = len(baseline_files)
        
        for baseline_file in baseline_files:
            stat = baseline_file.stat()
            info["baseline_files"].append({
                "filename": baseline_file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return info


def main():
    """Main function for baseline management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual Test Baseline Management")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for the application")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate all baselines
    gen_parser = subparsers.add_parser("generate", help="Generate all baselines")
    gen_parser.add_argument("--modules", nargs="+", help="Specific modules to generate baselines for")
    
    # Generate module baselines
    mod_parser = subparsers.add_parser("generate-module", help="Generate baselines for a specific module")
    mod_parser.add_argument("module", help="Module name")
    
    # Generate viewport baselines
    view_parser = subparsers.add_parser("generate-viewport", help="Generate baselines for a specific viewport")
    view_parser.add_argument("viewport", help="Viewport name (desktop, laptop, tablet, mobile)")
    
    # Backup baselines
    backup_parser = subparsers.add_parser("backup", help="Backup current baselines")
    backup_parser.add_argument("--name", help="Backup version name")
    
    # Restore baselines
    restore_parser = subparsers.add_parser("restore", help="Restore baselines from a version")
    restore_parser.add_argument("version", help="Version name to restore")
    
    # List versions
    subparsers.add_parser("list", help="List all baseline versions")
    
    # Compare versions
    compare_parser = subparsers.add_parser("compare", help="Compare baseline versions")
    compare_parser.add_argument("version1", help="First version to compare")
    compare_parser.add_argument("version2", nargs="?", default="current", help="Second version to compare (default: current)")
    
    # Clean old versions
    clean_parser = subparsers.add_parser("clean", help="Clean old baseline versions")
    clean_parser.add_argument("--keep", type=int, default=5, help="Number of versions to keep (default: 5)")
    
    # Get info
    subparsers.add_parser("info", help="Get baseline information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize baseline manager
    manager = BaselineManager(args.url)
    
    # Execute command
    if args.command == "generate":
        success = manager.generate_all_baselines(args.modules)
        return 0 if success else 1
    
    elif args.command == "generate-module":
        success = manager.generate_module_baselines(args.module)
        return 0 if success else 1
    
    elif args.command == "generate-viewport":
        success = manager.generate_viewport_baselines(args.viewport)
        return 0 if success else 1
    
    elif args.command == "backup":
        version = manager.backup_current_baselines(args.name)
        return 0 if version else 1
    
    elif args.command == "restore":
        success = manager.restore_baseline_version(args.version)
        return 0 if success else 1
    
    elif args.command == "list":
        versions = manager.list_baseline_versions()
        if versions:
            print("Available baseline versions:")
            for version in versions:
                print(f"  - {version}")
        else:
            print("No baseline versions found")
        return 0
    
    elif args.command == "compare":
        result = manager.compare_baselines(args.version1, args.version2)
        return 0 if result else 1
    
    elif args.command == "clean":
        deleted = manager.clean_old_versions(args.keep)
        return 0
    
    elif args.command == "info":
        info = manager.get_baseline_info()
        print(json.dumps(info, indent=2))
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())