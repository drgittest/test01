from starlette.testclient import TestClient
from main import app
import pytest
from models import Base, User, settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use a shared in-memory SQLite database for all test connections
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the SessionLocal dependency in main.py
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables before running tests
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Patch main.SessionLocal to use the test database
import main as main_app
main_app.SessionLocal = TestingSessionLocal

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Clean up tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_get():
    response = client.get("/register")
    assert response.status_code == 200
    # Check for Japanese text in the template
    assert "ユーザー登録" in response.text


def test_register_post():
    response = client.post("/register", data={"login_id": "testuser", "password": "testpass"}, follow_redirects=False)
    # Should redirect to /login if successful, or return 200 with error if user exists
    if response.status_code == 302:
        assert response.headers["location"] == "/login"
    elif response.status_code == 200:
        # Should contain the error message for existing user
        assert "既に存在します" in response.text
    else:
        print("Unexpected response:", response.text)
        assert False, f"Unexpected status code: {response.status_code}"


def test_login_get():
    response = client.get("/login")
    assert response.status_code == 200
    # Check for Japanese text in the template
    assert "ログイン" in response.text


def test_login_post_success():
    # First, register a user
    client.post("/register", data={"login_id": "testuser", "password": "testpass"}, follow_redirects=False)
    # Then, try to log in
    response = client.post("/login", data={"login_id": "testuser", "password": "testpass"}, follow_redirects=False)
    # Should redirect to /
    assert response.status_code == 302
    assert response.headers["location"] == "/"


def test_login_post_failure():
    response = client.post("/login", data={"login_id": "wronguser", "password": "wrongpass"})
    assert response.status_code == 200
    assert "IDまたはパスワードが違います" in response.text 


def test_logout():
    # Register and log in a user
    client.post("/register", data={"login_id": "testuser", "password": "testpass"}, follow_redirects=False)
    client.post("/login", data={"login_id": "testuser", "password": "testpass"}, follow_redirects=False)
    # Call logout
    response = client.get("/logout", follow_redirects=False)
    # Should redirect to /login
    assert response.status_code == 307 or response.status_code == 302
    assert "/login" in response.headers["location"] 


def test_index_authenticated():
    # Register and log in a user
    client.post("/register", data={"login_id": "testuser2", "password": "testpass"}, follow_redirects=False)
    client.post("/login", data={"login_id": "testuser2", "password": "testpass"}, follow_redirects=False)
    # Access the index page
    response = client.get("/")
    assert response.status_code == 200
    assert "こんにちは" in response.text
    assert "testuser2" in response.text 


def test_orders_list():
    # The /orders page should be accessible without authentication (middleware allows it)
    response = client.get("/orders")
    assert response.status_code == 200
    # Check for table headers in the response
    assert "Order List" in response.text
    assert "Order Number" in response.text
    assert "Customer Name" in response.text
    assert "Item" in response.text
    assert "Quantity" in response.text
    assert "Price" in response.text
    assert "Status" in response.text 


def test_orders_create_get():
    # The /orders/create page should be accessible without authentication (middleware allows it)
    response = client.get("/orders/create")
    assert response.status_code == 200
    # Check for form fields in the response
    assert "Create Order" in response.text
    assert "Order Number" in response.text
    assert "Customer Name" in response.text
    assert "Item" in response.text
    assert "Quantity" in response.text
    assert "Price" in response.text
    assert "Status" in response.text
    assert "Back to Order List" in response.text 


def test_orders_create_post():
    # Register and log in a user
    client.post("/register", data={"login_id": "createuser", "password": "createpass"}, follow_redirects=False)
    client.post("/login", data={"login_id": "createuser", "password": "createpass"}, follow_redirects=False)

    # Submit the order creation form
    order_data = {
        "order_number": "ORD003",
        "customer_name": "Charlie",
        "item": "Thingamajig",
        "quantity": 7,
        "price": 3000,
        "status": "pending"
    }
    response = client.post("/orders/create", data=order_data, follow_redirects=True)
    assert response.status_code == 200
    # Check that the new order appears in the order list
    assert "ORD003" in response.text
    assert "Charlie" in response.text
    assert "Thingamajig" in response.text
    assert "7" in response.text
    assert "3000" in response.text
    assert "pending" in response.text


def test_order_detail():
    # Register and log in a user
    client.post("/register", data={"login_id": "testuser", "password": "testpass"}, follow_redirects=False)
    client.post("/login", data={"login_id": "testuser", "password": "testpass"}, follow_redirects=False)

    # Create an order in the test database
    from models import Order
    import datetime
    with TestingSessionLocal() as db:
        order = Order(
            order_number="ORD001",
            customer_name="Alice",
            item="Widget",
            quantity=5,
            price=1000,
            status="pending",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat()
        )
        db.add(order)
        db.commit()
        order_id = order.id
    # Access the order detail page as an authenticated user
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert "Order Detail" in response.text
    assert "ORD001" in response.text
    assert "Alice" in response.text
    assert "Widget" in response.text
    assert "5" in response.text
    assert "1000" in response.text
    assert "pending" in response.text
    assert "Back to Order List" in response.text 


def test_order_edit_get():
    # Register and log in a user
    client.post("/register", data={"login_id": "edituser", "password": "editpass"}, follow_redirects=False)
    client.post("/login", data={"login_id": "edituser", "password": "editpass"}, follow_redirects=False)

    # Create an order in the test database
    from models import Order
    import datetime
    with TestingSessionLocal() as db:
        order = Order(
            order_number="ORD002",
            customer_name="Bob",
            item="Gadget",
            quantity=3,
            price=1500,
            status="pending",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat()
        )
        db.add(order)
        db.commit()
        order_id = order.id
    # Access the order edit page
    response = client.get(f"/orders/{order_id}/edit")
    assert response.status_code == 200
    assert "Edit Order" in response.text
    assert "Order Number" in response.text
    assert "Customer Name" in response.text
    assert "Item" in response.text
    assert "Quantity" in response.text
    assert "Price" in response.text
    assert "Status" in response.text
    assert "Back to Order Detail" in response.text 


def test_order_edit_post():
    # Register and log in a user
    client.post("/register", data={"login_id": "editpostuser", "password": "editpostpass"}, follow_redirects=False)
    client.post("/login", data={"login_id": "editpostuser", "password": "editpostpass"}, follow_redirects=False)

    # Create an order in the test database
    from models import Order
    import datetime
    with TestingSessionLocal() as db:
        order = Order(
            order_number="ORD004",
            customer_name="Daisy",
            item="Widget",
            quantity=2,
            price=500,
            status="pending",
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat()
        )
        db.add(order)
        db.commit()
        order_id = order.id
    # Update the order via the edit form
    updated_data = {
        "order_number": "ORD004-EDITED",
        "customer_name": "Daisy Updated",
        "item": "Widget Pro",
        "quantity": 5,
        "price": 1200,
        "status": "shipped"
    }
    response = client.post(f"/orders/{order_id}/edit", data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    # Check that the updated order details appear in the detail page
    assert "ORD004-EDITED" in response.text
    assert "Daisy Updated" in response.text
    assert "Widget Pro" in response.text
    assert "5" in response.text
    assert "1200" in response.text
    assert "shipped" in response.text 