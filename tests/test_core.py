"""Tests for core TypedUUID functionality."""
import json
from uuid import UUID
import pytest

from typed_uuid import TypedUUID, create_typed_uuid_class
from typed_uuid.exceptions import InvalidTypeIDError, InvalidUUIDError


class TestCreateTypedUUIDClass:
    """Tests for create_typed_uuid_class factory function."""

    def test_create_basic_class(self):
        """Test creating a basic TypedUUID class."""
        UserUUID = create_typed_uuid_class('User', 'user')
        assert UserUUID is not None
        assert UserUUID._type_id == 'user'
        assert UserUUID.__name__ == 'UserUUID'

    def test_create_class_with_short_type_id(self):
        """Test creating a class with a single character type_id."""
        XUUID = create_typed_uuid_class('X', 'x')
        assert XUUID._type_id == 'x'

    def test_create_class_with_max_length_type_id(self):
        """Test creating a class with maximum length type_id (8 chars)."""
        LongUUID = create_typed_uuid_class('Long', 'abcd1234')
        assert LongUUID._type_id == 'abcd1234'

    def test_duplicate_type_id_returns_same_class(self):
        """Test that creating a class with existing type_id returns the same class."""
        UserUUID1 = create_typed_uuid_class('User', 'user')
        UserUUID2 = create_typed_uuid_class('User', 'user')
        assert UserUUID1 is UserUUID2

    def test_invalid_type_id_too_long(self):
        """Test that type_id longer than 8 characters raises error."""
        with pytest.raises(InvalidTypeIDError):
            create_typed_uuid_class('Invalid', 'toolongid')

    def test_invalid_type_id_empty(self):
        """Test that empty type_id raises error."""
        with pytest.raises(InvalidTypeIDError):
            create_typed_uuid_class('Invalid', '')

    def test_invalid_type_id_with_hyphen(self):
        """Test that type_id with hyphen raises error."""
        with pytest.raises(InvalidTypeIDError):
            create_typed_uuid_class('Invalid', 'user-id')

    def test_invalid_type_id_with_special_chars(self):
        """Test that type_id with special characters raises error."""
        with pytest.raises(InvalidTypeIDError):
            create_typed_uuid_class('Invalid', 'user@id')

    def test_invalid_type_id_none(self):
        """Test that None type_id raises error."""
        with pytest.raises(InvalidTypeIDError):
            create_typed_uuid_class('Invalid', None)

    def test_invalid_type_id_whitespace_only(self):
        """Test that whitespace-only type_id raises error."""
        with pytest.raises(InvalidTypeIDError):
            create_typed_uuid_class('Invalid', '   ')


class TestTypedUUIDInstantiation:
    """Tests for TypedUUID instance creation."""

    def test_create_with_no_args(self, user_uuid_class):
        """Test creating a TypedUUID with no arguments generates a UUID."""
        user_id = user_uuid_class()
        assert user_id is not None
        assert user_id.type_id == 'user'
        assert isinstance(user_id.uuid, UUID)

    def test_create_with_uuid_object(self, user_uuid_class, sample_uuid_string):
        """Test creating a TypedUUID with a UUID object."""
        uuid_obj = UUID(sample_uuid_string)
        user_id = user_uuid_class(uuid_value=uuid_obj)
        assert str(user_id.uuid) == sample_uuid_string

    def test_create_with_uuid_string(self, user_uuid_class, sample_uuid_string):
        """Test creating a TypedUUID with a UUID string."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        assert str(user_id.uuid) == sample_uuid_string

    def test_create_with_typed_uuid_string(self, user_uuid_class, sample_typed_uuid_string):
        """Test creating a TypedUUID with a typed UUID string."""
        user_id = user_uuid_class(uuid_value=sample_typed_uuid_string)
        assert str(user_id) == sample_typed_uuid_string

    def test_create_with_uppercase_uuid(self, user_uuid_class):
        """Test creating a TypedUUID with uppercase UUID string."""
        uuid_str = '550E8400-E29B-41D4-A716-446655440000'
        user_id = user_uuid_class(uuid_value=uuid_str)
        assert user_id is not None

    def test_create_with_wrong_type_prefix(self, user_uuid_class):
        """Test creating a TypedUUID with wrong type prefix raises error."""
        with pytest.raises(InvalidTypeIDError):
            user_uuid_class(uuid_value='order-550e8400-e29b-41d4-a716-446655440000')

    def test_create_with_invalid_uuid(self, user_uuid_class):
        """Test creating a TypedUUID with invalid UUID raises error."""
        with pytest.raises(InvalidUUIDError):
            user_uuid_class(uuid_value='not-a-valid-uuid')


class TestTypedUUIDFromString:
    """Tests for TypedUUID.from_string method."""

    def test_from_string_typed(self, user_uuid_class, sample_typed_uuid_string):
        """Test parsing a typed UUID string."""
        user_id = user_uuid_class.from_string(sample_typed_uuid_string)
        assert str(user_id) == sample_typed_uuid_string

    def test_from_string_plain_uuid(self, user_uuid_class, sample_uuid_string):
        """Test parsing a plain UUID string."""
        user_id = user_uuid_class.from_string(sample_uuid_string)
        assert str(user_id.uuid) == sample_uuid_string
        assert user_id.type_id == 'user'

    def test_from_string_empty(self, user_uuid_class):
        """Test parsing empty string raises error."""
        with pytest.raises(InvalidUUIDError):
            user_uuid_class.from_string('')

    def test_from_string_invalid(self, user_uuid_class):
        """Test parsing invalid string raises error."""
        with pytest.raises(InvalidUUIDError):
            user_uuid_class.from_string('invalid')

    def test_from_string_wrong_type(self, user_uuid_class):
        """Test parsing string with wrong type raises error."""
        with pytest.raises(InvalidTypeIDError):
            user_uuid_class.from_string('order-550e8400-e29b-41d4-a716-446655440000')


class TestTypedUUIDStringRepresentation:
    """Tests for TypedUUID string representations."""

    def test_str(self, user_uuid_class, sample_uuid_string):
        """Test __str__ returns type-uuid format."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        assert str(user_id) == f'user-{sample_uuid_string}'

    def test_repr(self, user_uuid_class, sample_uuid_string):
        """Test __repr__ returns detailed representation."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        repr_str = repr(user_id)
        assert 'TypedUUID' in repr_str
        assert 'user' in repr_str
        assert sample_uuid_string in repr_str

    def test_format(self, user_uuid_class, sample_uuid_string):
        """Test __format__ works correctly."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        assert f'{user_id}' == str(user_id)
        assert f'{user_id:>50}' == str(user_id).rjust(50)

    def test_bytes(self, user_uuid_class, sample_uuid_string):
        """Test __bytes__ returns encoded string."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        assert bytes(user_id) == str(user_id).encode()


class TestTypedUUIDComparison:
    """Tests for TypedUUID comparison operations."""

    def test_equality_same_uuid(self, user_uuid_class, sample_uuid_string):
        """Test equality of two TypedUUIDs with same UUID."""
        user_id1 = user_uuid_class(uuid_value=sample_uuid_string)
        user_id2 = user_uuid_class(uuid_value=sample_uuid_string)
        assert user_id1 == user_id2

    def test_equality_different_uuid(self, user_uuid_class):
        """Test inequality of two TypedUUIDs with different UUIDs."""
        user_id1 = user_uuid_class()
        user_id2 = user_uuid_class()
        assert user_id1 != user_id2

    def test_equality_with_string(self, user_uuid_class, sample_typed_uuid_string):
        """Test equality comparison with string."""
        user_id = user_uuid_class.from_string(sample_typed_uuid_string)
        assert user_id == sample_typed_uuid_string

    def test_inequality_with_string(self, user_uuid_class):
        """Test inequality comparison with different string."""
        user_id = user_uuid_class()
        assert user_id != 'user-different-uuid'

    def test_less_than(self, user_uuid_class):
        """Test less than comparison."""
        user_id1 = user_uuid_class(uuid_value='00000000-0000-0000-0000-000000000001')
        user_id2 = user_uuid_class(uuid_value='00000000-0000-0000-0000-000000000002')
        assert user_id1 < user_id2

    def test_less_than_or_equal(self, user_uuid_class, sample_uuid_string):
        """Test less than or equal comparison."""
        user_id1 = user_uuid_class(uuid_value=sample_uuid_string)
        user_id2 = user_uuid_class(uuid_value=sample_uuid_string)
        assert user_id1 <= user_id2

    def test_greater_than(self, user_uuid_class):
        """Test greater than comparison."""
        user_id1 = user_uuid_class(uuid_value='00000000-0000-0000-0000-000000000002')
        user_id2 = user_uuid_class(uuid_value='00000000-0000-0000-0000-000000000001')
        assert user_id1 > user_id2

    def test_greater_than_or_equal(self, user_uuid_class, sample_uuid_string):
        """Test greater than or equal comparison."""
        user_id1 = user_uuid_class(uuid_value=sample_uuid_string)
        user_id2 = user_uuid_class(uuid_value=sample_uuid_string)
        assert user_id1 >= user_id2

    def test_sorting(self, user_uuid_class):
        """Test that TypedUUIDs can be sorted."""
        ids = [
            user_uuid_class(uuid_value='00000000-0000-0000-0000-000000000003'),
            user_uuid_class(uuid_value='00000000-0000-0000-0000-000000000001'),
            user_uuid_class(uuid_value='00000000-0000-0000-0000-000000000002'),
        ]
        sorted_ids = sorted(ids)
        assert sorted_ids[0].uuid < sorted_ids[1].uuid < sorted_ids[2].uuid


class TestTypedUUIDHashing:
    """Tests for TypedUUID hashing."""

    def test_hash_consistent(self, user_uuid_class, sample_uuid_string):
        """Test that hash is consistent for same UUID."""
        user_id1 = user_uuid_class(uuid_value=sample_uuid_string)
        user_id2 = user_uuid_class(uuid_value=sample_uuid_string)
        assert hash(user_id1) == hash(user_id2)

    def test_hash_in_set(self, user_uuid_class, sample_uuid_string):
        """Test that TypedUUIDs work in sets."""
        user_id1 = user_uuid_class(uuid_value=sample_uuid_string)
        user_id2 = user_uuid_class(uuid_value=sample_uuid_string)
        user_id3 = user_uuid_class()

        user_set = {user_id1, user_id2, user_id3}
        assert len(user_set) == 2  # user_id1 and user_id2 are equal

    def test_hash_in_dict(self, user_uuid_class, sample_uuid_string):
        """Test that TypedUUIDs work as dict keys."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        user_dict = {user_id: 'Alice'}
        assert user_dict[user_id] == 'Alice'


class TestTypedUUIDRegistry:
    """Tests for TypedUUID registry functionality."""

    def test_is_type_registered(self, user_uuid_class):
        """Test is_type_registered returns True for registered types."""
        assert TypedUUID.is_type_registered('user')

    def test_is_type_not_registered(self):
        """Test is_type_registered returns False for unregistered types."""
        assert not TypedUUID.is_type_registered('nonexistent')

    def test_list_registered_types(self, user_uuid_class, order_uuid_class):
        """Test list_registered_types returns all registered types."""
        types = TypedUUID.list_registered_types()
        assert 'user' in types
        assert 'order' in types

    def test_get_class_by_type_id(self, user_uuid_class):
        """Test get_class_by_type_id returns correct class."""
        cls = TypedUUID.get_class_by_type_id('user')
        assert cls is user_uuid_class

    def test_get_class_by_type_id_not_found(self):
        """Test get_class_by_type_id returns None for unknown type."""
        cls = TypedUUID.get_class_by_type_id('nonexistent')
        assert cls is None

    def test_get_registered_class(self, user_uuid_class):
        """Test get_registered_class returns correct class."""
        cls = TypedUUID.get_registered_class('user')
        assert cls is user_uuid_class


class TestTypedUUIDProperties:
    """Tests for TypedUUID properties."""

    def test_type_id_property(self, user_uuid_class):
        """Test type_id property returns correct value."""
        user_id = user_uuid_class()
        assert user_id.type_id == 'user'

    def test_uuid_property(self, user_uuid_class, sample_uuid_string):
        """Test uuid property returns UUID object."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        assert isinstance(user_id.uuid, UUID)
        assert str(user_id.uuid) == sample_uuid_string

    def test_get_uuid(self, user_uuid_class, sample_uuid_string):
        """Test get_uuid returns string without prefix."""
        user_id = user_uuid_class(uuid_value=sample_uuid_string)
        assert user_id.get_uuid() == sample_uuid_string


class TestTypedUUIDValidate:
    """Tests for TypedUUID validate class method."""

    def test_validate_string(self, user_uuid_class, sample_typed_uuid_string):
        """Test validate with typed string."""
        user_id = user_uuid_class.validate(sample_typed_uuid_string)
        assert str(user_id) == sample_typed_uuid_string

    def test_validate_uuid_object(self, user_uuid_class, sample_uuid_string):
        """Test validate with UUID object."""
        uuid_obj = UUID(sample_uuid_string)
        user_id = user_uuid_class.validate(uuid_obj)
        assert str(user_id.uuid) == sample_uuid_string

    def test_validate_typed_uuid(self, user_uuid_class, sample_uuid_string):
        """Test validate with TypedUUID instance."""
        user_id1 = user_uuid_class(uuid_value=sample_uuid_string)
        user_id2 = user_uuid_class.validate(user_id1)
        assert user_id1 is user_id2

    def test_validate_invalid_type(self, user_uuid_class):
        """Test validate with invalid type raises error."""
        with pytest.raises(ValueError):
            user_uuid_class.validate(12345)


class TestTypedUUIDGenerate:
    """Tests for TypedUUID generate class method."""

    def test_generate(self, user_uuid_class):
        """Test generate creates new instance."""
        user_id = user_uuid_class.generate()
        assert user_id is not None
        assert user_id.type_id == 'user'

    def test_generate_unique(self, user_uuid_class):
        """Test generate creates unique UUIDs."""
        ids = [user_uuid_class.generate() for _ in range(100)]
        unique_ids = set(str(id) for id in ids)
        assert len(unique_ids) == 100


class TestTypedUUIDJSON:
    """Tests for TypedUUID JSON serialization."""

    def test_json_method(self, user_uuid_class, sample_typed_uuid_string):
        """Test __json__ method returns string."""
        user_id = user_uuid_class.from_string(sample_typed_uuid_string)
        assert user_id.__json__() == sample_typed_uuid_string

    def test_to_json(self, user_uuid_class, sample_typed_uuid_string):
        """Test to_json method returns string."""
        user_id = user_uuid_class.from_string(sample_typed_uuid_string)
        assert user_id.to_json() == sample_typed_uuid_string

    def test_json_default(self, user_uuid_class, sample_typed_uuid_string):
        """Test json_default static method."""
        user_id = user_uuid_class.from_string(sample_typed_uuid_string)
        result = TypedUUID.json_default(user_id)
        assert result == sample_typed_uuid_string

    def test_json_dumps(self, user_uuid_class, sample_typed_uuid_string):
        """Test serialization with json.dumps."""
        user_id = user_uuid_class.from_string(sample_typed_uuid_string)
        json_str = json.dumps({'id': user_id}, default=TypedUUID.json_default)
        data = json.loads(json_str)
        assert data['id'] == sample_typed_uuid_string


class TestTypedUUIDFormatPattern:
    """Tests for TypedUUID format_pattern method."""

    def test_format_pattern(self, user_uuid_class):
        """Test format_pattern returns valid regex pattern."""
        import re
        pattern = user_uuid_class.format_pattern()
        assert pattern is not None

        # Test pattern matches valid typed UUIDs
        regex = re.compile(pattern, re.IGNORECASE)
        assert regex.match('user-550e8400-e29b-41d4-a716-446655440000')

    def test_format_pattern_no_match_invalid(self, user_uuid_class):
        """Test format_pattern doesn't match invalid strings."""
        import re
        pattern = user_uuid_class.format_pattern()
        regex = re.compile(pattern, re.IGNORECASE)
        assert not regex.match('invalid-string')


class TestTypedUUIDPathParam:
    """Tests for TypedUUID path_param stub method."""

    def test_path_param_raises_not_implemented(self, user_uuid_class):
        """Test path_param raises NotImplementedError when FastAPI not installed."""
        # Note: This test assumes FastAPI is not installed or the stub hasn't been replaced
        # In actual use, this would be replaced by the FastAPI adapter
        with pytest.raises(NotImplementedError):
            TypedUUID.path_param()


class TestTypedUUIDSupportedAdapters:
    """Tests for TypedUUID get_supported_adapters method."""

    def test_get_supported_adapters_base(self):
        """Test get_supported_adapters on base class."""
        adapters = TypedUUID.get_supported_adapters()
        assert isinstance(adapters, set)
