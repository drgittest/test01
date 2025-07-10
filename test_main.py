from starlette.testclient import TestClient
from main import app
import pytest
from models import Base, User, settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
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