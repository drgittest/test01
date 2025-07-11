#!/usr/bin/env python3
"""
Test Isolation Manager
Ensures test isolation, prevents interference between tests, and manages concurrent execution.
"""

import sys
import os
import time
import threading
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from contextlib import contextmanager
import json
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import signal


class TestIsolationManager:
    """Manages test isolation and prevents interference between concurrent tests."""
    
    def __init__(self, test_env: str = "visual_test"):
        self.test_env = test_env
        self.test_dir = Path(__file__).parent
        self.isolation_dir = self.test_dir / "isolation"
        self.locks_dir = self.isolation_dir / "locks"
        self.sessions_dir = self.isolation_dir / "sessions"
        self.cleanup_dir = self.isolation_dir / "cleanup"
        
        # Create directories
        self.isolation_dir.mkdir(exist_ok=True)
        self.locks_dir.mkdir(exist_ok=True)
        self.sessions_dir.mkdir(exist_ok=True)
        self.cleanup_dir.mkdir(exist_ok=True)
        
        # Test session management
        self.session_id = str(uuid.uuid4())
        self.session_file = self.sessions_dir / f"session_{self.session_id}.json"
        self.cleanup_registry = []
        
        # Resource locks
        self.active_locks = {}
        self.lock_timeout = 300  # 5 minutes
        
        # Test state tracking
        self.current_test = None
        self.test_results = {}
        self.resource_usage = {}
        
        # Initialize session
        self.initialize_session()
    
    def initialize_session(self):
        """Initialize test session with metadata."""
        session_data = {
            "session_id": self.session_id,
            "test_env": self.test_env,
            "started_at": datetime.now().isoformat(),
            "pid": os.getpid(),
            "status": "active",
            "tests_run": 0,
            "resources_used": [],
            "cleanup_actions": []
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Register cleanup handler
        signal.signal(signal.SIGTERM, self.cleanup_handler)
        signal.signal(signal.SIGINT, self.cleanup_handler)
    
    def cleanup_handler(self, signum, frame):
        """Handle cleanup on process termination."""
        print(f"\n🧹 Cleaning up test session {self.session_id}")
        self.cleanup_session()
        sys.exit(0)
    
    @contextmanager
    def test_isolation(self, test_name: str, resources: List[str] = None):
        """Context manager for test isolation."""
        resources = resources or []
        
        print(f"🔒 Starting isolated test: {test_name}")
        
        # Acquire resource locks
        acquired_locks = []
        try:
            for resource in resources:
                lock_acquired = self.acquire_resource_lock(resource, test_name)
                if lock_acquired:
                    acquired_locks.append(resource)
                else:
                    raise Exception(f"Could not acquire lock for resource: {resource}")
            
            # Set current test
            self.current_test = test_name
            self.update_session_data({"current_test": test_name, "status": "running"})
            
            # Create test-specific temporary directory
            test_temp_dir = self.create_test_temp_dir(test_name)
            
            # Yield control to test
            yield {
                "test_name": test_name,
                "session_id": self.session_id,
                "temp_dir": test_temp_dir,
                "resources": acquired_locks
            }
            
        except Exception as e:
            print(f"✗ Test isolation failed for {test_name}: {e}")
            raise
        
        finally:
            # Release resource locks
            for resource in acquired_locks:
                self.release_resource_lock(resource, test_name)
            
            # Cleanup test-specific resources
            if 'test_temp_dir' in locals():
                self.cleanup_test_temp_dir(test_temp_dir)
            
            # Update session
            self.current_test = None
            self.update_session_data({"current_test": None, "status": "idle"})
            
            print(f"🔓 Test isolation complete: {test_name}")
    
    def acquire_resource_lock(self, resource: str, test_name: str, timeout: int = None) -> bool:
        """Acquire a lock for a specific resource."""
        timeout = timeout or self.lock_timeout
        lock_file = self.locks_dir / f"{resource}.lock"
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Try to create lock file exclusively
                with open(lock_file, 'x') as f:
                    lock_data = {
                        "resource": resource,
                        "test_name": test_name,
                        "session_id": self.session_id,
                        "acquired_at": datetime.now().isoformat(),
                        "pid": os.getpid()
                    }
                    json.dump(lock_data, f)
                
                self.active_locks[resource] = lock_file
                print(f"✓ Acquired lock for resource: {resource}")
                return True
                
            except FileExistsError:
                # Lock file exists, check if it's stale
                if self.is_stale_lock(lock_file):
                    print(f"⚠️ Removing stale lock for resource: {resource}")
                    try:
                        lock_file.unlink()
                        continue
                    except:
                        pass
                
                # Wait and retry
                time.sleep(0.1)
        
        print(f"✗ Could not acquire lock for resource: {resource} (timeout)")
        return False
    
    def release_resource_lock(self, resource: str, test_name: str):
        """Release a resource lock."""
        lock_file = self.locks_dir / f"{resource}.lock"
        
        try:
            if lock_file.exists():
                # Verify we own the lock
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                if lock_data.get("session_id") == self.session_id:
                    lock_file.unlink()
                    if resource in self.active_locks:
                        del self.active_locks[resource]
                    print(f"✓ Released lock for resource: {resource}")
                else:
                    print(f"⚠️ Lock not owned by this session: {resource}")
            
        except Exception as e:
            print(f"⚠️ Error releasing lock for {resource}: {e}")
    
    def is_stale_lock(self, lock_file: Path) -> bool:
        """Check if a lock file is stale (process no longer exists)."""
        try:
            with open(lock_file, 'r') as f:
                lock_data = json.load(f)
            
            # Check if process still exists
            pid = lock_data.get("pid")
            if pid:
                try:
                    os.kill(pid, 0)  # Send signal 0 to check if process exists
                    return False  # Process exists, lock is valid
                except ProcessLookupError:
                    return True  # Process doesn't exist, lock is stale
                except PermissionError:
                    return False  # Process exists but we don't have permission
            
            # Check lock age
            acquired_at = lock_data.get("acquired_at")
            if acquired_at:
                lock_time = datetime.fromisoformat(acquired_at)
                age = (datetime.now() - lock_time).total_seconds()
                return age > self.lock_timeout
            
            return True  # No valid timestamp, assume stale
            
        except Exception:
            return True  # Error reading lock file, assume stale
    
    def create_test_temp_dir(self, test_name: str) -> Path:
        """Create a temporary directory for test-specific files."""
        temp_dir = self.isolation_dir / "temp" / f"{test_name}_{self.session_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Register for cleanup
        self.cleanup_registry.append(("temp_dir", temp_dir))
        
        return temp_dir
    
    def cleanup_test_temp_dir(self, temp_dir: Path):
        """Clean up test-specific temporary directory."""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                print(f"✓ Cleaned up temp directory: {temp_dir}")
            
            # Remove from cleanup registry
            self.cleanup_registry = [(t, p) for t, p in self.cleanup_registry if p != temp_dir]
            
        except Exception as e:
            print(f"⚠️ Error cleaning up temp directory {temp_dir}: {e}")
    
    def update_session_data(self, updates: Dict[str, Any]):
        """Update session data file."""
        try:
            # Read current data
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Apply updates
            session_data.update(updates)
            session_data["updated_at"] = datetime.now().isoformat()
            
            # Write back
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error updating session data: {e}")
    
    def register_cleanup_action(self, action_type: str, action_data: Dict[str, Any]):
        """Register a cleanup action to be performed at session end."""
        cleanup_action = {
            "type": action_type,
            "data": action_data,
            "registered_at": datetime.now().isoformat()
        }
        
        self.cleanup_registry.append(("action", cleanup_action))
        
        # Update session file
        self.update_session_data({"cleanup_actions": [a for t, a in self.cleanup_registry if t == "action"]})
    
    def execute_cleanup_actions(self):
        """Execute all registered cleanup actions."""
        print("🧹 Executing cleanup actions...")
        
        for cleanup_type, cleanup_data in self.cleanup_registry:
            try:
                if cleanup_type == "temp_dir":
                    self.cleanup_test_temp_dir(cleanup_data)
                elif cleanup_type == "action":
                    self.execute_cleanup_action(cleanup_data)
                    
            except Exception as e:
                print(f"⚠️ Error executing cleanup action: {e}")
    
    def execute_cleanup_action(self, action_data: Dict[str, Any]):
        """Execute a specific cleanup action."""
        action_type = action_data.get("type")
        
        if action_type == "database_cleanup":
            self.cleanup_database(action_data.get("data", {}))
        elif action_type == "file_cleanup":
            self.cleanup_files(action_data.get("data", {}))
        elif action_type == "process_cleanup":
            self.cleanup_processes(action_data.get("data", {}))
        else:
            print(f"⚠️ Unknown cleanup action type: {action_type}")
    
    def cleanup_database(self, data: Dict[str, Any]):
        """Clean up database resources."""
        print("🗄️ Cleaning up database resources...")
        
        # Import test data manager
        try:
            from test_data_manager import TestDataManager
            manager = TestDataManager()
            manager.cleanup_test_data()
            print("✓ Database cleanup completed")
        except Exception as e:
            print(f"⚠️ Database cleanup failed: {e}")
    
    def cleanup_files(self, data: Dict[str, Any]):
        """Clean up temporary files."""
        files_to_cleanup = data.get("files", [])
        
        for file_path in files_to_cleanup:
            try:
                path = Path(file_path)
                if path.exists():
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                    print(f"✓ Cleaned up file: {file_path}")
            except Exception as e:
                print(f"⚠️ Error cleaning up file {file_path}: {e}")
    
    def cleanup_processes(self, data: Dict[str, Any]):
        """Clean up child processes."""
        pids_to_cleanup = data.get("pids", [])
        
        for pid in pids_to_cleanup:
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✓ Terminated process: {pid}")
            except ProcessLookupError:
                print(f"ℹ️ Process {pid} already terminated")
            except Exception as e:
                print(f"⚠️ Error terminating process {pid}: {e}")
    
    def cleanup_session(self):
        """Clean up the entire test session."""
        print(f"🧹 Cleaning up session: {self.session_id}")
        
        # Release all active locks
        for resource in list(self.active_locks.keys()):
            self.release_resource_lock(resource, "session_cleanup")
        
        # Execute cleanup actions
        self.execute_cleanup_actions()
        
        # Update session status
        self.update_session_data({
            "status": "completed",
            "ended_at": datetime.now().isoformat()
        })
        
        print(f"✓ Session cleanup completed: {self.session_id}")
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all active test sessions."""
        active_sessions = []
        
        for session_file in self.sessions_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Check if session is still active
                if session_data.get("status") == "active":
                    pid = session_data.get("pid")
                    if pid:
                        try:
                            os.kill(pid, 0)
                            active_sessions.append(session_data)
                        except ProcessLookupError:
                            # Mark session as stale
                            session_data["status"] = "stale"
                            with open(session_file, 'w') as f:
                                json.dump(session_data, f, indent=2)
                            
            except Exception as e:
                print(f"⚠️ Error reading session file {session_file}: {e}")
        
        return active_sessions
    
    def cleanup_stale_sessions(self):
        """Clean up stale sessions and resources."""
        print("🧹 Cleaning up stale sessions...")
        
        cleaned_count = 0
        
        # Clean up stale session files
        for session_file in self.sessions_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                if session_data.get("status") in ["completed", "stale"]:
                    session_file.unlink()
                    cleaned_count += 1
                    
            except Exception as e:
                print(f"⚠️ Error cleaning session file {session_file}: {e}")
        
        # Clean up stale locks
        for lock_file in self.locks_dir.glob("*.lock"):
            if self.is_stale_lock(lock_file):
                try:
                    lock_file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    print(f"⚠️ Error removing stale lock {lock_file}: {e}")
        
        print(f"✓ Cleaned up {cleaned_count} stale resources")
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage information."""
        usage_info = {
            "session_id": self.session_id,
            "active_locks": list(self.active_locks.keys()),
            "temp_dirs": [str(p) for t, p in self.cleanup_registry if t == "temp_dir"],
            "cleanup_actions": len([a for t, a in self.cleanup_registry if t == "action"]),
            "current_test": self.current_test,
            "session_age": (datetime.now() - datetime.fromisoformat(self.get_session_data().get("started_at", ""))).total_seconds()
        }
        
        return usage_info
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get current session data."""
        try:
            with open(self.session_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def run_tests_with_isolation(self, test_functions: List[Dict[str, Any]], 
                                max_concurrent: int = 1) -> Dict[str, Any]:
        """Run multiple tests with proper isolation."""
        print(f"🚀 Running {len(test_functions)} tests with isolation (max concurrent: {max_concurrent})")
        
        results = {
            "total_tests": len(test_functions),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_results": {},
            "started_at": datetime.now().isoformat()
        }
        
        def run_isolated_test(test_info):
            """Run a single test with isolation."""
            test_name = test_info["name"]
            test_func = test_info["function"]
            resources = test_info.get("resources", [])
            
            try:
                with self.test_isolation(test_name, resources) as isolation_context:
                    result = test_func(isolation_context)
                    return test_name, {"status": "passed", "result": result}
                    
            except Exception as e:
                return test_name, {"status": "failed", "error": str(e)}
        
        # Run tests with thread pool
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_test = {executor.submit(run_isolated_test, test_info): test_info 
                            for test_info in test_functions}
            
            for future in as_completed(future_to_test):
                test_info = future_to_test[future]
                test_name = test_info["name"]
                
                try:
                    test_name, result = future.result()
                    results["test_results"][test_name] = result
                    
                    if result["status"] == "passed":
                        results["passed"] += 1
                        print(f"✓ {test_name}: PASSED")
                    else:
                        results["failed"] += 1
                        print(f"✗ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    results["errors"] += 1
                    results["test_results"][test_name] = {"status": "error", "error": str(e)}
                    print(f"✗ {test_name}: ERROR - {e}")
        
        results["ended_at"] = datetime.now().isoformat()
        
        # Print summary
        print(f"\n📊 TEST ISOLATION SUMMARY")
        print(f"Total: {results['total_tests']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Errors: {results['errors']}")
        
        return results


def main():
    """Main function for test isolation management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Isolation Manager")
    parser.add_argument("--env", default="visual_test", help="Test environment")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Show active sessions
    subparsers.add_parser("sessions", help="Show active test sessions")
    
    # Cleanup stale resources
    subparsers.add_parser("cleanup", help="Clean up stale sessions and resources")
    
    # Show resource usage
    subparsers.add_parser("usage", help="Show resource usage")
    
    # Test isolation
    test_parser = subparsers.add_parser("test", help="Run test with isolation")
    test_parser.add_argument("test_name", help="Test name")
    test_parser.add_argument("--resources", nargs="+", help="Resources to lock")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize isolation manager
    manager = TestIsolationManager(args.env)
    
    try:
        # Execute command
        if args.command == "sessions":
            sessions = manager.get_active_sessions()
            print(f"Active sessions: {len(sessions)}")
            for session in sessions:
                print(f"  Session: {session['session_id']}")
                print(f"    Started: {session.get('started_at', 'Unknown')}")
                print(f"    Current test: {session.get('current_test', 'None')}")
                print(f"    PID: {session.get('pid', 'Unknown')}")
            return 0
        
        elif args.command == "cleanup":
            manager.cleanup_stale_sessions()
            return 0
        
        elif args.command == "usage":
            usage = manager.get_resource_usage()
            print(json.dumps(usage, indent=2))
            return 0
        
        elif args.command == "test":
            def dummy_test(context):
                print(f"Running test: {context['test_name']}")
                time.sleep(1)
                return "success"
            
            with manager.test_isolation(args.test_name, args.resources or []) as context:
                result = dummy_test(context)
                print(f"Test result: {result}")
            
            return 0
        
        else:
            parser.print_help()
            return 1
    
    finally:
        manager.cleanup_session()


if __name__ == "__main__":
    sys.exit(main())