"""Tests for TypedUUID framework adapters."""
import pytest

from typed_uuid import TypedUUID, create_typed_uuid_class
from typed_uuid.utils import create_typed_uuid_classes


# Check for optional dependencies
try:
    import sqlalchemy
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import pydantic
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    import fastapi
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class TestCreateTypedUUIDClasses:
    """Tests for create_typed_uuid_classes utility function."""

    def test_returns_single_class_without_sqlalchemy(self):
        """Test returns single class when SQLAlchemy not available."""
        if SQLALCHEMY_AVAILABLE:
            pytest.skip("SQLAlchemy is available")

        result = create_typed_uuid_classes('Test', 'tst1')
        assert not isinstance(result, tuple)
        assert result._type_id == 'tst1'

    def test_returns_tuple_with_sqlalchemy(self):
        """Test returns tuple when SQLAlchemy is available."""
        if not SQLALCHEMY_AVAILABLE:
            pytest.skip("SQLAlchemy not installed")

        result = create_typed_uuid_classes('Test', 'tst2')
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0]._type_id == 'tst2'


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
class TestSQLAlchemyAdapter:
    """Tests for SQLAlchemy adapter."""

    def test_sqlalchemy_methods_added(self):
        """Test SQLAlchemy methods are added to TypedUUID class."""
        UserUUID = create_typed_uuid_class('User', 'sqla1')
        assert hasattr(UserUUID, '__composite_values__')
        assert hasattr(UserUUID, '__from_db_value__')
        assert hasattr(UserUUID, 'replace')

    def test_composite_values(self):
        """Test __composite_values__ returns tuple."""
        UserUUID = create_typed_uuid_class('User', 'sqla2')
        user_id = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')
        values = user_id.__composite_values__()
        assert isinstance(values, tuple)
        assert len(values) == 2
        assert values[0] == 'sqla2'
        assert values[1] == '550e8400-e29b-41d4-a716-446655440000'

    def test_replace_method(self):
        """Test replace method works correctly."""
        UserUUID = create_typed_uuid_class('User', 'sqla3')
        user_id = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')
        result = user_id.replace('-', '_')
        assert '-' not in result
        assert '_' in result

    def test_from_db_value(self):
        """Test __from_db_value__ reconstructs TypedUUID."""
        UserUUID = create_typed_uuid_class('User', 'sqla4')
        user_id = UserUUID.__from_db_value__('sqla4-550e8400-e29b-41d4-a716-446655440000')
        assert user_id.type_id == 'sqla4'
        assert str(user_id.uuid) == '550e8400-e29b-41d4-a716-446655440000'

    def test_typed_uuid_type_creation(self):
        """Test TypedUUIDType can be created."""
        from typed_uuid.adapters.sqlalchemy import create_typed_uuid_type, TypedUUIDType

        UserUUIDType = create_typed_uuid_type('sqla5')
        assert UserUUIDType is not None
        assert UserUUIDType.__name__ == 'Sqla5UUIDType'

    def test_typed_uuid_type_bind_param(self):
        """Test TypedUUIDType process_bind_param."""
        from typed_uuid.adapters.sqlalchemy import create_typed_uuid_type

        UserUUID = create_typed_uuid_class('User', 'sqla6')
        UserUUIDType = create_typed_uuid_type('sqla6')

        type_instance = UserUUIDType()
        user_id = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')

        result = type_instance.process_bind_param(user_id, None)
        assert result == 'sqla6-550e8400-e29b-41d4-a716-446655440000'

    def test_typed_uuid_type_bind_param_none(self):
        """Test TypedUUIDType process_bind_param with None."""
        from typed_uuid.adapters.sqlalchemy import create_typed_uuid_type

        create_typed_uuid_class('User', 'sqla7')
        UserUUIDType = create_typed_uuid_type('sqla7')

        type_instance = UserUUIDType()
        result = type_instance.process_bind_param(None, None)
        assert result is None

    def test_typed_uuid_type_result_value(self):
        """Test TypedUUIDType process_result_value."""
        from typed_uuid.adapters.sqlalchemy import create_typed_uuid_type

        UserUUID = create_typed_uuid_class('User', 'sqla8')
        UserUUIDType = create_typed_uuid_type('sqla8')

        type_instance = UserUUIDType()
        result = type_instance.process_result_value(
            'sqla8-550e8400-e29b-41d4-a716-446655440000', None
        )
        assert isinstance(result, UserUUID)
        assert result.type_id == 'sqla8'

    def test_typed_uuid_type_result_value_none(self):
        """Test TypedUUIDType process_result_value with None."""
        from typed_uuid.adapters.sqlalchemy import create_typed_uuid_type

        create_typed_uuid_class('User', 'sqla9')
        UserUUIDType = create_typed_uuid_type('sqla9')

        type_instance = UserUUIDType()
        result = type_instance.process_result_value(None, None)
        assert result is None


@pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not installed")
class TestPydanticAdapter:
    """Tests for Pydantic adapter."""

    def test_pydantic_methods_added(self):
        """Test Pydantic methods are added to TypedUUID class."""
        UserUUID = create_typed_uuid_class('User', 'pyd1')
        assert hasattr(UserUUID, '__get_pydantic_core_schema__')
        assert hasattr(UserUUID, '__get_pydantic_json_schema__')
        assert hasattr(UserUUID, 'validate_json')
        assert hasattr(UserUUID, 'model_dump')

    def test_pydantic_model_validation(self):
        """Test TypedUUID works in Pydantic models."""
        from pydantic import BaseModel

        UserUUID = create_typed_uuid_class('User', 'pyd2')

        class UserModel(BaseModel):
            id: UserUUID
            name: str

        user = UserModel(
            id='pyd2-550e8400-e29b-41d4-a716-446655440000',
            name='Alice'
        )
        assert user.id.type_id == 'pyd2'
        assert user.name == 'Alice'

    def test_pydantic_model_validation_from_instance(self):
        """Test TypedUUID instance validation in Pydantic models."""
        from pydantic import BaseModel

        UserUUID = create_typed_uuid_class('User', 'pyd3')

        class UserModel(BaseModel):
            id: UserUUID
            name: str

        user_id = UserUUID()
        user = UserModel(id=user_id, name='Bob')
        assert user.id is user_id

    def test_pydantic_model_serialization(self):
        """Test TypedUUID serialization in Pydantic models."""
        from pydantic import BaseModel

        UserUUID = create_typed_uuid_class('User', 'pyd4')

        class UserModel(BaseModel):
            id: UserUUID
            name: str

        user = UserModel(
            id='pyd4-550e8400-e29b-41d4-a716-446655440000',
            name='Charlie'
        )
        data = user.model_dump()
        assert data['id'] == 'pyd4-550e8400-e29b-41d4-a716-446655440000'

    def test_pydantic_json_serialization(self):
        """Test TypedUUID JSON serialization in Pydantic models."""
        from pydantic import BaseModel
        import json

        UserUUID = create_typed_uuid_class('User', 'pyd5')

        class UserModel(BaseModel):
            id: UserUUID
            name: str

        user = UserModel(
            id='pyd5-550e8400-e29b-41d4-a716-446655440000',
            name='Diana'
        )
        json_str = user.model_dump_json()
        data = json.loads(json_str)
        assert data['id'] == 'pyd5-550e8400-e29b-41d4-a716-446655440000'

    def test_validate_json_method(self):
        """Test validate_json class method."""
        UserUUID = create_typed_uuid_class('User', 'pyd6')
        result = UserUUID.validate_json('pyd6-550e8400-e29b-41d4-a716-446655440000')
        assert result.type_id == 'pyd6'

    def test_model_dump_method(self):
        """Test model_dump instance method."""
        UserUUID = create_typed_uuid_class('User', 'pyd7')
        user_id = UserUUID(uuid_value='550e8400-e29b-41d4-a716-446655440000')
        result = user_id.model_dump()
        assert result == 'pyd7-550e8400-e29b-41d4-a716-446655440000'


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
class TestFastAPIAdapter:
    """Tests for FastAPI adapter."""

    def test_path_param_method_added(self):
        """Test path_param method is added to TypedUUID class."""
        UserUUID = create_typed_uuid_class('User', 'fapi1')
        # When FastAPI is available, path_param should not raise NotImplementedError
        try:
            result = UserUUID.path_param()
            assert result is not None
        except NotImplementedError:
            pytest.fail("path_param should be available when FastAPI is installed")

    def test_path_param_with_description(self):
        """Test path_param with custom description."""
        UserUUID = create_typed_uuid_class('User', 'fapi2')
        result = UserUUID.path_param(description="User identifier")
        assert result is not None

    def test_path_param_returns_annotated_type(self):
        """Test path_param returns an Annotated type."""
        from typing import get_origin, get_args
        try:
            from typing import Annotated
        except ImportError:
            from typing_extensions import Annotated

        UserUUID = create_typed_uuid_class('User', 'fapi3')
        result = UserUUID.path_param()

        # Check it's an Annotated type
        assert get_origin(result) is Annotated
        args = get_args(result)
        assert len(args) >= 2
        assert args[0] is UserUUID
