"""Test fixtures for auth verification tests."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variable for JWT_SECRET before importing app modules
os.environ["JWT_SECRET"] = "test-secret-key-for-unit-testing-purposes-only-12345"


@pytest.fixture(scope="function")
def client():
    """Create a test client with fresh temp database."""
    # Create a temporary database file for this test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    # Set the database path before importing any app modules that use it
    os.environ["DATABASE_PATH"] = tmp_db_path

    # Reset all singletons to ensure fresh state
    import app.services.database as db_module
    import app.services.auth_service as auth_module
    import app.services.rate_limiter as rate_module
    import app.services.token_blacklist as blacklist_module

    # Close existing connections if any
    if db_module._db_instance is not None:
        try:
            db_module._db_instance.close()
        except Exception:
            pass

    db_module._db_instance = None
    auth_module._auth_service = None
    rate_module._login_limiter = None
    rate_module._register_limiter = None
    rate_module._refresh_limiter = None
    blacklist_module._token_blacklist = None

    # Now import and create the app - this will initialize with fresh DB
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    # Cleanup
    db_module._db_instance = None
    auth_module._auth_service = None
    rate_module._login_limiter = None
    rate_module._register_limiter = None
    rate_module._refresh_limiter = None
    blacklist_module._token_blacklist = None

    # Remove temp database file
    try:
        os.unlink(tmp_db_path)
    except Exception:
        pass


@pytest.fixture
def valid_password():
    """Return a password that meets all requirements."""
    return "TestPassword123!"


@pytest.fixture
def test_user_data(valid_password):
    """Return valid user registration data."""
    return {
        "username": "testuser",
        "password": valid_password,
        "email": "test@example.com"
    }
