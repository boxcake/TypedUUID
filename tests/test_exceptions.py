"""Tests for TypedUUID exceptions."""
import pytest

from typed_uuid.exceptions import TypedUUIDError, InvalidTypeIDError, InvalidUUIDError


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_invalid_type_id_inherits_from_base(self):
        """Test InvalidTypeIDError inherits from TypedUUIDError."""
        assert issubclass(InvalidTypeIDError, TypedUUIDError)

    def test_invalid_uuid_inherits_from_base(self):
        """Test InvalidUUIDError inherits from TypedUUIDError."""
        assert issubclass(InvalidUUIDError, TypedUUIDError)

    def test_base_inherits_from_exception(self):
        """Test TypedUUIDError inherits from Exception."""
        assert issubclass(TypedUUIDError, Exception)


class TestExceptionMessages:
    """Tests for exception messages."""

    def test_invalid_type_id_message(self):
        """Test InvalidTypeIDError can be raised with message."""
        with pytest.raises(InvalidTypeIDError) as exc_info:
            raise InvalidTypeIDError("test message")
        assert "test message" in str(exc_info.value)

    def test_invalid_uuid_message(self):
        """Test InvalidUUIDError can be raised with message."""
        with pytest.raises(InvalidUUIDError) as exc_info:
            raise InvalidUUIDError("test message")
        assert "test message" in str(exc_info.value)

    def test_base_error_message(self):
        """Test TypedUUIDError can be raised with message."""
        with pytest.raises(TypedUUIDError) as exc_info:
            raise TypedUUIDError("test message")
        assert "test message" in str(exc_info.value)


class TestExceptionCatching:
    """Tests for catching exceptions at different levels."""

    def test_catch_invalid_type_id_as_base(self):
        """Test catching InvalidTypeIDError as TypedUUIDError."""
        try:
            raise InvalidTypeIDError("test")
        except TypedUUIDError:
            pass  # Should be caught
        else:
            pytest.fail("InvalidTypeIDError should be caught as TypedUUIDError")

    def test_catch_invalid_uuid_as_base(self):
        """Test catching InvalidUUIDError as TypedUUIDError."""
        try:
            raise InvalidUUIDError("test")
        except TypedUUIDError:
            pass  # Should be caught
        else:
            pytest.fail("InvalidUUIDError should be caught as TypedUUIDError")

    def test_catch_all_as_exception(self):
        """Test catching TypedUUIDError as Exception."""
        try:
            raise TypedUUIDError("test")
        except Exception:
            pass  # Should be caught
        else:
            pytest.fail("TypedUUIDError should be caught as Exception")
