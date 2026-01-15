"""Tests for new TypedUUID features: slots, short encoding, pickle, auto-parse."""
import pickle
import sys
import pytest

from typed_uuid import TypedUUID, create_typed_uuid_class
from typed_uuid.exceptions import InvalidUUIDError, InvalidTypeIDError


class TestSlots:
    """Tests for __slots__ implementation."""

    def test_slots_defined(self):
        """Test that __slots__ is defined on TypedUUID."""
        assert hasattr(TypedUUID, '__slots__')
        assert '_uuid' in TypedUUID.__slots__
        assert '_instance_type_id' in TypedUUID.__slots__

    def test_no_dict_on_instance(self):
        """Test that instances don't have __dict__ (slots optimization)."""
        UserUUID = create_typed_uuid_class('User', 'user')
        user_id = UserUUID()
        # With __slots__, instances shouldn't have __dict__
        assert not hasattr(user_id, '__dict__')

    def test_cannot_add_arbitrary_attributes(self):
        """Test that arbitrary attributes cannot be added (slots restriction)."""
        UserUUID = create_typed_uuid_class('User', 'user')
        user_id = UserUUID()
        with pytest.raises(AttributeError):
            user_id.arbitrary_attr = "value"

    def test_memory_efficiency(self):
        """Test that slotted instances use less memory."""
        UserUUID = create_typed_uuid_class('User', 'memtest')
        user_id = UserUUID()
        # Slotted objects should have smaller size
        size = sys.getsizeof(user_id)
        # Just verify it's reasonable (not a huge dict-based object)
        assert size < 200  # Reasonable size for a slotted object


class TestShortEncoding:
    """Tests for short base62 encoding/decoding."""

    def test_short_property(self):
        """Test short property returns underscore-separated format."""
        UserUUID = create_typed_uuid_class('User', 'user')
        user_id = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')
        short = user_id.short
        assert short.startswith('user_')
        assert '_' in short
        # Should be shorter than full UUID
        assert len(short) < len(str(user_id))

    def test_short_is_alphanumeric(self):
        """Test short encoding only uses alphanumeric characters."""
        UserUUID = create_typed_uuid_class('User', 'user')
        user_id = UserUUID()
        short = user_id.short
        type_id, encoded = short.split('_', 1)
        assert encoded.isalnum()

    def test_from_short_roundtrip(self):
        """Test encoding then decoding returns same UUID."""
        UserUUID = create_typed_uuid_class('User', 'user')
        original = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')
        short = original.short

        decoded = UserUUID.from_short(short)
        assert decoded.uuid == original.uuid
        assert decoded.type_id == original.type_id

    def test_from_short_multiple_roundtrips(self):
        """Test multiple UUIDs roundtrip correctly."""
        UserUUID = create_typed_uuid_class('User', 'srt')
        for _ in range(100):
            original = UserUUID()
            decoded = UserUUID.from_short(original.short)
            assert decoded.uuid == original.uuid

    def test_from_short_invalid_format(self):
        """Test from_short raises error for invalid format."""
        UserUUID = create_typed_uuid_class('User', 'user')
        with pytest.raises(InvalidUUIDError):
            UserUUID.from_short('invalid-format')

    def test_from_short_wrong_type(self):
        """Test from_short raises error for wrong type."""
        UserUUID = create_typed_uuid_class('User', 'user')
        OrderUUID = create_typed_uuid_class('Order', 'order')
        order_id = OrderUUID()

        with pytest.raises(InvalidTypeIDError):
            UserUUID.from_short(order_id.short)

    def test_from_short_invalid_base62(self):
        """Test from_short raises error for invalid base62 characters."""
        UserUUID = create_typed_uuid_class('User', 'user')
        with pytest.raises(InvalidUUIDError):
            UserUUID.from_short('user_!!invalid!!')

    def test_short_zero_uuid(self):
        """Test short encoding handles zero UUID."""
        UserUUID = create_typed_uuid_class('User', 'zero')
        user_id = UserUUID(uuid_value='00000000-0000-0000-0000-000000000000')
        short = user_id.short
        decoded = UserUUID.from_short(short)
        assert decoded.uuid == user_id.uuid

    def test_short_max_uuid(self):
        """Test short encoding handles max UUID."""
        UserUUID = create_typed_uuid_class('User', 'max')
        user_id = UserUUID(uuid_value='ffffffff-ffff-ffff-ffff-ffffffffffff')
        short = user_id.short
        decoded = UserUUID.from_short(short)
        assert decoded.uuid == user_id.uuid


class TestPickleSupport:
    """Tests for pickle serialization."""

    def test_pickle_roundtrip(self):
        """Test pickling and unpickling preserves data."""
        UserUUID = create_typed_uuid_class('User', 'pkl1')
        original = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')

        pickled = pickle.dumps(original)
        restored = pickle.loads(pickled)

        assert restored.uuid == original.uuid
        assert restored.type_id == original.type_id
        assert str(restored) == str(original)

    def test_pickle_preserves_class(self):
        """Test pickled object is instance of correct class."""
        UserUUID = create_typed_uuid_class('User', 'pkl2')
        original = UserUUID()

        pickled = pickle.dumps(original)
        restored = pickle.loads(pickled)

        assert isinstance(restored, UserUUID)
        assert type(restored).__name__ == 'UserUUID'

    def test_pickle_multiple_instances(self):
        """Test pickling multiple instances."""
        UserUUID = create_typed_uuid_class('User', 'pkl3')
        instances = [UserUUID() for _ in range(10)]

        pickled = pickle.dumps(instances)
        restored = pickle.loads(pickled)

        assert len(restored) == len(instances)
        for orig, rest in zip(instances, restored):
            assert orig.uuid == rest.uuid

    def test_pickle_protocols(self):
        """Test pickling works with all protocols."""
        UserUUID = create_typed_uuid_class('User', 'pkl4')
        original = UserUUID()

        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            pickled = pickle.dumps(original, protocol=protocol)
            restored = pickle.loads(pickled)
            assert restored.uuid == original.uuid

    def test_getstate_setstate(self):
        """Test __getstate__ and __setstate__ directly."""
        UserUUID = create_typed_uuid_class('User', 'pkl5')
        original = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')

        state = original.__getstate__()
        assert 'type_id' in state
        assert 'uuid' in state
        assert state['type_id'] == 'pkl5'

        new_instance = UserUUID.__new__(UserUUID)
        new_instance.__setstate__(state)
        assert new_instance.uuid == original.uuid


class TestAutoParse:
    """Tests for TypedUUID.parse() auto-detection."""

    def test_parse_standard_format(self):
        """Test parsing standard type-uuid format."""
        UserUUID = create_typed_uuid_class('User', 'user')
        user_id = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')

        assert isinstance(user_id, UserUUID)
        assert user_id.type_id == 'user'
        assert str(user_id.uuid) == '550e8400-e29b-41d4-a716-446655440000'

    def test_parse_short_format(self):
        """Test parsing short base62 format."""
        UserUUID = create_typed_uuid_class('User', 'user')
        original = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')
        short = original.short

        parsed = TypedUUID.parse(short)
        assert isinstance(parsed, UserUUID)
        assert parsed.uuid == original.uuid

    def test_parse_returns_correct_subclass(self):
        """Test parse returns the correct TypedUUID subclass."""
        UserUUID = create_typed_uuid_class('User', 'usr')
        OrderUUID = create_typed_uuid_class('Order', 'ord')

        user_id = TypedUUID.parse('usr-550e8400-e29b-41d4-a716-446655440000')
        order_id = TypedUUID.parse('ord-550e8400-e29b-41d4-a716-446655440000')

        assert type(user_id).__name__ == 'UserUUID'
        assert type(order_id).__name__ == 'OrderUUID'

    def test_parse_unknown_type_raises_error(self):
        """Test parsing unknown type raises error."""
        with pytest.raises(InvalidUUIDError) as exc_info:
            TypedUUID.parse('unknown-550e8400-e29b-41d4-a716-446655440000')
        assert 'Unknown type_id' in str(exc_info.value)

    def test_parse_empty_string_raises_error(self):
        """Test parsing empty string raises error."""
        with pytest.raises(InvalidUUIDError):
            TypedUUID.parse('')

    def test_parse_invalid_format_raises_error(self):
        """Test parsing invalid format raises error."""
        with pytest.raises(InvalidUUIDError):
            TypedUUID.parse('not-a-valid-format-at-all')

    def test_parse_roundtrip_standard(self):
        """Test parse roundtrip with standard format."""
        UserUUID = create_typed_uuid_class('User', 'prs1')
        original = UserUUID()
        parsed = TypedUUID.parse(str(original))
        assert parsed.uuid == original.uuid
        assert isinstance(parsed, UserUUID)

    def test_parse_roundtrip_short(self):
        """Test parse roundtrip with short format."""
        UserUUID = create_typed_uuid_class('User', 'prs2')
        original = UserUUID()
        parsed = TypedUUID.parse(original.short)
        assert parsed.uuid == original.uuid
        assert isinstance(parsed, UserUUID)


class TestBase62Functions:
    """Tests for base62 encoding/decoding functions."""

    def test_encode_zero(self):
        """Test encoding zero."""
        from typed_uuid.core import _encode_base62
        assert _encode_base62(0) == '0'

    def test_encode_decode_roundtrip(self):
        """Test encoding then decoding returns original."""
        from typed_uuid.core import _encode_base62, _decode_base62
        for num in [0, 1, 62, 100, 1000, 10000, 2**128 - 1]:
            encoded = _encode_base62(num)
            decoded = _decode_base62(encoded)
            assert decoded == num

    def test_decode_invalid_char(self):
        """Test decoding invalid character raises error."""
        from typed_uuid.core import _decode_base62
        with pytest.raises(ValueError):
            _decode_base62('invalid!')
