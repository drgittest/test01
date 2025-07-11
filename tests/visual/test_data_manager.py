#!/usr/bin/env python3
"""
Test Data Management System
Manages test data fixtures, database seeding, and test isolation for visual regression tests.
"""

import sys
import os
import json
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from faker import Faker
import sqlite3

# Import application models (adjust imports based on actual structure)
try:
    from models import User, Order, Base, engine, SessionLocal
    from sqlalchemy.orm import Session
except ImportError:
    print("⚠️ Could not import application models. Some features may be limited.")
    User = None
    Order = None
    Base = None
    engine = None
    SessionLocal = None


@dataclass
class TestUser:
    """Test user data structure."""
    login_id: str
    password: str
    display_name: str = ""
    created_for_test: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestOrder:
    """Test order data structure."""
    order_number: str
    customer_name: str
    item: str
    quantity: int
    price: int
    status: str = "pending"
    created_at: str = ""
    updated_at: str = ""
    created_for_test: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TestDataManager:
    """Manages test data fixtures and database seeding for visual tests."""
    
    def __init__(self, test_env: str = "visual_test"):
        self.test_env = test_env
        self.faker = Faker(['en_US', 'ja_JP'])  # Support both English and Japanese
        self.test_dir = Path(__file__).parent
        self.fixtures_dir = self.test_dir / "fixtures"
        self.fixtures_dir.mkdir(exist_ok=True)
        
        # Test data configuration
        self.test_users_file = self.fixtures_dir / "test_users.json"
        self.test_orders_file = self.fixtures_dir / "test_orders.json"
        self.test_session_file = self.fixtures_dir / "test_session.json"
        
        # Database connection
        self.db_session = None
        
        # Test data registry
        self.created_users = []
        self.created_orders = []
        self.test_session_data = {}
        
    def initialize_database_connection(self) -> bool:
        """Initialize database connection for test data operations."""
        try:
            if SessionLocal:
                self.db_session = SessionLocal()
                print("✓ Database connection initialized")
                return True
            else:
                print("⚠️ Database models not available")
                return False
        except Exception as e:
            print(f"✗ Failed to initialize database connection: {e}")
            return False
    
    def cleanup_database_connection(self):
        """Clean up database connection."""
        if self.db_session:
            self.db_session.close()
            print("✓ Database connection closed")
    
    def generate_test_users(self, count: int = 5) -> List[TestUser]:
        """Generate test users with realistic data."""
        test_users = []
        
        # Always include known test users for consistent testing
        known_users = [
            TestUser(
                login_id="visual_test_user",
                password="visual_test_pass",
                display_name="Visual Test User"
            ),
            TestUser(
                login_id="asdf2",
                password="asdf", 
                display_name="Default Test User"
            ),
            TestUser(
                login_id="test_admin",
                password="admin123",
                display_name="Test Administrator"
            )
        ]
        
        test_users.extend(known_users)
        
        # Generate additional random users
        for i in range(count - len(known_users)):
            user_id = f"test_user_{i}_{int(time.time())}"
            test_users.append(TestUser(
                login_id=user_id,
                password="testpass123",
                display_name=self.faker.name()
            ))
        
        self.created_users = test_users
        return test_users
    
    def generate_test_orders(self, count: int = 20) -> List[TestOrder]:
        """Generate test orders with realistic data."""
        test_orders = []
        
        # Define realistic order data patterns
        items = [
            "Laptop Computer", "Wireless Mouse", "Keyboard",
            "Monitor", "USB Cable", "Headphones", "Smartphone",
            "Tablet", "Printer", "Scanner", "Webcam", "Speakers",
            "Hard Drive", "Memory Card", "Power Bank", "Charger"
        ]
        
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        
        # Generate orders with realistic patterns
        for i in range(count):
            order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{i:04d}"
            
            # Create realistic order data
            item = random.choice(items)
            quantity = random.randint(1, 10)
            base_price = random.randint(50, 2000)
            total_price = base_price * quantity
            
            # Create order with timestamp variations
            created_time = datetime.now() - timedelta(days=random.randint(0, 30))
            updated_time = created_time + timedelta(hours=random.randint(1, 48))
            
            test_order = TestOrder(
                order_number=order_number,
                customer_name=self.faker.name(),
                item=item,
                quantity=quantity,
                price=total_price,
                status=random.choice(statuses),
                created_at=created_time.isoformat(),
                updated_at=updated_time.isoformat()
            )
            
            test_orders.append(test_order)
        
        # Add some specific orders for consistent testing
        specific_orders = [
            TestOrder(
                order_number="VISUAL_TEST_001",
                customer_name="Visual Test Customer",
                item="Test Product",
                quantity=1,
                price=100,
                status="pending"
            ),
            TestOrder(
                order_number="VISUAL_TEST_002",
                customer_name="Another Test Customer",
                item="Another Test Product",
                quantity=2,
                price=200,
                status="processing"
            )
        ]
        
        test_orders.extend(specific_orders)
        self.created_orders = test_orders
        return test_orders
    
    def save_test_fixtures(self):
        """Save test data fixtures to JSON files."""
        try:
            # Save users
            users_data = [user.to_dict() for user in self.created_users]
            with open(self.test_users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            # Save orders
            orders_data = [order.to_dict() for order in self.created_orders]
            with open(self.test_orders_file, 'w') as f:
                json.dump(orders_data, f, indent=2)
            
            # Save session data
            self.test_session_data = {
                "created_at": datetime.now().isoformat(),
                "test_env": self.test_env,
                "users_count": len(self.created_users),
                "orders_count": len(self.created_orders)
            }
            
            with open(self.test_session_file, 'w') as f:
                json.dump(self.test_session_data, f, indent=2)
            
            print(f"✓ Test fixtures saved:")
            print(f"  Users: {len(self.created_users)}")
            print(f"  Orders: {len(self.created_orders)}")
            
        except Exception as e:
            print(f"✗ Failed to save test fixtures: {e}")
    
    def load_test_fixtures(self) -> bool:
        """Load test data fixtures from JSON files."""
        try:
            # Load users
            if self.test_users_file.exists():
                with open(self.test_users_file, 'r') as f:
                    users_data = json.load(f)
                    self.created_users = [TestUser(**user) for user in users_data]
            
            # Load orders
            if self.test_orders_file.exists():
                with open(self.test_orders_file, 'r') as f:
                    orders_data = json.load(f)
                    self.created_orders = [TestOrder(**order) for order in orders_data]
            
            # Load session data
            if self.test_session_file.exists():
                with open(self.test_session_file, 'r') as f:
                    self.test_session_data = json.load(f)
            
            print(f"✓ Test fixtures loaded:")
            print(f"  Users: {len(self.created_users)}")
            print(f"  Orders: {len(self.created_orders)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to load test fixtures: {e}")
            return False
    
    def seed_database(self, force: bool = False) -> bool:
        """Seed database with test data."""
        if not self.initialize_database_connection():
            print("⚠️ Cannot seed database - connection failed")
            return False
        
        try:
            # Check if test data already exists
            if not force and self.check_test_data_exists():
                print("ℹ️ Test data already exists. Use --force to recreate.")
                return True
            
            # Clear existing test data
            self.cleanup_test_data()
            
            # Seed users
            if User and self.created_users:
                for test_user in self.created_users:
                    # Check if user already exists
                    existing_user = self.db_session.query(User).filter_by(login_id=test_user.login_id).first()
                    if not existing_user:
                        db_user = User(
                            login_id=test_user.login_id,
                            password=test_user.password  # In real app, this would be hashed
                        )
                        self.db_session.add(db_user)
                
                print(f"✓ Seeded {len(self.created_users)} users")
            
            # Seed orders
            if Order and self.created_orders:
                for test_order in self.created_orders:
                    # Check if order already exists
                    existing_order = self.db_session.query(Order).filter_by(order_number=test_order.order_number).first()
                    if not existing_order:
                        db_order = Order(
                            order_number=test_order.order_number,
                            customer_name=test_order.customer_name,
                            item=test_order.item,
                            quantity=test_order.quantity,
                            price=test_order.price,
                            status=test_order.status,
                            created_at=test_order.created_at or datetime.now().isoformat(),
                            updated_at=test_order.updated_at or datetime.now().isoformat()
                        )
                        self.db_session.add(db_order)
                
                print(f"✓ Seeded {len(self.created_orders)} orders")
            
            # Commit changes
            self.db_session.commit()
            print("✓ Database seeding completed")
            
            return True
            
        except Exception as e:
            print(f"✗ Database seeding failed: {e}")
            if self.db_session:
                self.db_session.rollback()
            return False
        
        finally:
            self.cleanup_database_connection()
    
    def check_test_data_exists(self) -> bool:
        """Check if test data already exists in database."""
        try:
            if User and self.db_session:
                # Check for known test users
                test_user = self.db_session.query(User).filter_by(login_id="visual_test_user").first()
                if test_user:
                    return True
            
            if Order and self.db_session:
                # Check for known test orders
                test_order = self.db_session.query(Order).filter_by(order_number="VISUAL_TEST_001").first()
                if test_order:
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking test data: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data from database."""
        try:
            if not self.db_session:
                return
            
            # Remove test users
            if User:
                test_user_ids = [user.login_id for user in self.created_users]
                self.db_session.query(User).filter(User.login_id.in_(test_user_ids)).delete(synchronize_session=False)
            
            # Remove test orders
            if Order:
                test_order_numbers = [order.order_number for order in self.created_orders]
                self.db_session.query(Order).filter(Order.order_number.in_(test_order_numbers)).delete(synchronize_session=False)
            
            self.db_session.commit()
            print("✓ Test data cleaned up")
            
        except Exception as e:
            print(f"⚠️ Error cleaning up test data: {e}")
            if self.db_session:
                self.db_session.rollback()
    
    def create_test_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Create a specific test scenario with predetermined data."""
        scenarios = {
            "empty_database": {
                "description": "Empty database for testing empty states",
                "users": [],
                "orders": [],
                "setup": lambda: self.cleanup_test_data()
            },
            "single_user": {
                "description": "Single user with no orders",
                "users": [TestUser("single_user", "password", "Single User")],
                "orders": [],
                "setup": lambda: self.seed_single_user_scenario()
            },
            "user_with_orders": {
                "description": "User with multiple orders",
                "users": [TestUser("user_with_orders", "password", "User With Orders")],
                "orders": self.generate_test_orders(5),
                "setup": lambda: self.seed_user_with_orders_scenario()
            },
            "full_data": {
                "description": "Full test dataset",
                "users": self.generate_test_users(5),
                "orders": self.generate_test_orders(20),
                "setup": lambda: self.seed_database(force=True)
            }
        }
        
        if scenario_name not in scenarios:
            print(f"✗ Unknown scenario: {scenario_name}")
            return {}
        
        scenario = scenarios[scenario_name]
        print(f"📋 Creating test scenario: {scenario['description']}")
        
        # Set up data
        self.created_users = scenario["users"]
        self.created_orders = scenario["orders"]
        
        # Execute setup
        try:
            scenario["setup"]()
            print(f"✓ Test scenario '{scenario_name}' created successfully")
            return {
                "scenario_name": scenario_name,
                "description": scenario["description"],
                "users_count": len(scenario["users"]),
                "orders_count": len(scenario["orders"]),
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Failed to create test scenario '{scenario_name}': {e}")
            return {}
    
    def seed_single_user_scenario(self):
        """Seed database with single user scenario."""
        if not self.initialize_database_connection():
            return
        
        try:
            self.cleanup_test_data()
            
            if User and self.created_users:
                user = self.created_users[0]
                db_user = User(login_id=user.login_id, password=user.password)
                self.db_session.add(db_user)
                self.db_session.commit()
                
            print("✓ Single user scenario seeded")
            
        except Exception as e:
            print(f"✗ Single user scenario seeding failed: {e}")
            if self.db_session:
                self.db_session.rollback()
        finally:
            self.cleanup_database_connection()
    
    def seed_user_with_orders_scenario(self):
        """Seed database with user and orders scenario."""
        if not self.initialize_database_connection():
            return
        
        try:
            self.cleanup_test_data()
            
            # Add user
            if User and self.created_users:
                user = self.created_users[0]
                db_user = User(login_id=user.login_id, password=user.password)
                self.db_session.add(db_user)
            
            # Add orders
            if Order and self.created_orders:
                for order in self.created_orders:
                    db_order = Order(
                        order_number=order.order_number,
                        customer_name=order.customer_name,
                        item=order.item,
                        quantity=order.quantity,
                        price=order.price,
                        status=order.status,
                        created_at=order.created_at or datetime.now().isoformat(),
                        updated_at=order.updated_at or datetime.now().isoformat()
                    )
                    self.db_session.add(db_order)
            
            self.db_session.commit()
            print("✓ User with orders scenario seeded")
            
        except Exception as e:
            print(f"✗ User with orders scenario seeding failed: {e}")
            if self.db_session:
                self.db_session.rollback()
        finally:
            self.cleanup_database_connection()
    
    def get_test_credentials(self) -> Dict[str, str]:
        """Get test credentials for authentication."""
        if self.created_users:
            primary_user = self.created_users[0]
            return {
                "username": primary_user.login_id,
                "password": primary_user.password
            }
        else:
            # Return default credentials
            return {
                "username": "asdf2",
                "password": "asdf"
            }
    
    def export_test_data(self, output_path: Path = None) -> Path:
        """Export test data to a comprehensive JSON file."""
        if not output_path:
            output_path = self.fixtures_dir / f"test_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_info": {
                "created_at": datetime.now().isoformat(),
                "test_env": self.test_env,
                "version": "1.0"
            },
            "users": [user.to_dict() for user in self.created_users],
            "orders": [order.to_dict() for order in self.created_orders],
            "session_data": self.test_session_data,
            "statistics": {
                "users_count": len(self.created_users),
                "orders_count": len(self.created_orders),
                "order_statuses": self.get_order_status_distribution(),
                "date_range": self.get_order_date_range()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✓ Test data exported to: {output_path}")
        return output_path
    
    def get_order_status_distribution(self) -> Dict[str, int]:
        """Get distribution of order statuses."""
        status_counts = {}
        for order in self.created_orders:
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def get_order_date_range(self) -> Dict[str, str]:
        """Get date range of test orders."""
        if not self.created_orders:
            return {"start": "", "end": ""}
        
        dates = []
        for order in self.created_orders:
            if order.created_at:
                try:
                    date = datetime.fromisoformat(order.created_at.replace('Z', '+00:00'))
                    dates.append(date)
                except:
                    pass
        
        if dates:
            return {
                "start": min(dates).isoformat(),
                "end": max(dates).isoformat()
            }
        else:
            return {"start": "", "end": ""}
    
    def generate_and_seed_all(self, user_count: int = 5, order_count: int = 20, force: bool = False) -> bool:
        """Generate and seed all test data."""
        print("🔄 GENERATING AND SEEDING TEST DATA")
        print("=" * 50)
        
        # Generate test data
        print("📝 Generating test data...")
        self.generate_test_users(user_count)
        self.generate_test_orders(order_count)
        
        # Save fixtures
        print("💾 Saving test fixtures...")
        self.save_test_fixtures()
        
        # Seed database
        print("🌱 Seeding database...")
        success = self.seed_database(force)
        
        if success:
            print("\n✅ Test data generation and seeding completed successfully!")
            print(f"  👥 Users: {len(self.created_users)}")
            print(f"  📦 Orders: {len(self.created_orders)}")
            print(f"  🎯 Test credentials: {self.get_test_credentials()}")
        else:
            print("\n❌ Test data generation and seeding failed!")
        
        return success


def main():
    """Main function for test data management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual Test Data Management")
    parser.add_argument("--env", default="visual_test", help="Test environment name")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate test data
    gen_parser = subparsers.add_parser("generate", help="Generate test data")
    gen_parser.add_argument("--users", type=int, default=5, help="Number of users to generate")
    gen_parser.add_argument("--orders", type=int, default=20, help="Number of orders to generate")
    gen_parser.add_argument("--force", action="store_true", help="Force regeneration")
    
    # Seed database
    seed_parser = subparsers.add_parser("seed", help="Seed database with test data")
    seed_parser.add_argument("--force", action="store_true", help="Force reseeding")
    
    # Create scenario
    scenario_parser = subparsers.add_parser("scenario", help="Create test scenario")
    scenario_parser.add_argument("name", help="Scenario name (empty_database, single_user, user_with_orders, full_data)")
    
    # Clean up
    subparsers.add_parser("cleanup", help="Clean up test data")
    
    # Export data
    export_parser = subparsers.add_parser("export", help="Export test data")
    export_parser.add_argument("--output", type=Path, help="Output file path")
    
    # Get credentials
    subparsers.add_parser("credentials", help="Get test credentials")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize test data manager
    manager = TestDataManager(args.env)
    
    # Execute command
    if args.command == "generate":
        manager.generate_test_users(args.users)
        manager.generate_test_orders(args.orders)
        manager.save_test_fixtures()
        return 0
    
    elif args.command == "seed":
        manager.load_test_fixtures()
        success = manager.seed_database(args.force)
        return 0 if success else 1
    
    elif args.command == "scenario":
        result = manager.create_test_scenario(args.name)
        return 0 if result else 1
    
    elif args.command == "cleanup":
        manager.load_test_fixtures()
        manager.cleanup_test_data()
        return 0
    
    elif args.command == "export":
        manager.load_test_fixtures()
        manager.export_test_data(args.output)
        return 0
    
    elif args.command == "credentials":
        manager.load_test_fixtures()
        creds = manager.get_test_credentials()
        print(f"Username: {creds['username']}")
        print(f"Password: {creds['password']}")
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())