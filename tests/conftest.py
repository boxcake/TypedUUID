"""Pytest configuration and fixtures for TypedUUID tests."""
import sys
from pathlib import Path
import pytest

# Add parent directory to path to enable package imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from typed_uuid import TypedUUID, create_typed_uuid_class


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the TypedUUID registry before each test to ensure isolation."""
    # Store original registry
    original_registry = TypedUUID._class_registry.copy()

    # Clear registry for test
    with TypedUUID._registry_lock:
        TypedUUID._class_registry.clear()

    yield

    # Restore original registry after test
    with TypedUUID._registry_lock:
        TypedUUID._class_registry.clear()
        TypedUUID._class_registry.update(original_registry)


@pytest.fixture
def user_uuid_class():
    """Create a UserUUID class for testing."""
    return create_typed_uuid_class('User', 'user')


@pytest.fixture
def order_uuid_class():
    """Create an OrderUUID class for testing."""
    return create_typed_uuid_class('Order', 'order')


@pytest.fixture
def sample_uuid_string():
    """Return a sample UUID string for testing."""
    return '550e8400-e29b-41d4-a716-446655440000'


@pytest.fixture
def sample_typed_uuid_string():
    """Return a sample typed UUID string for testing."""
    return 'user-550e8400-e29b-41d4-a716-446655440000'
