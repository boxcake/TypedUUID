# typed_uuid/adapters/sqlalchemy.py
import logging
from typing import Type, Optional

try:
    from sqlalchemy import TypeDecorator, String
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

from ..core import TypedUUID

logger = logging.getLogger(__name__)


def add_sqlalchemy_methods(cls: Type[TypedUUID]) -> None:
    """Add SQLAlchemy-specific methods to a TypedUUID class."""

    def replace(self, old: str, new: str, count: int = -1) -> str:
        """Implement string replace for SQLAlchemy compatibility."""
        return str(self).replace(old, new, count)

    def __composite_values__(self):
        """Support for SQLAlchemy composite columns."""
        return self._instance_type_id, str(self._uuid)

    @classmethod
    def __from_db_value__(cls, value: str) -> 'TypedUUID':
        """Reconstruct TypedUUID from database string value."""
        return cls.from_string(value)

    # Add methods to class
    cls.replace = replace
    cls.__composite_values__ = __composite_values__
    cls.__from_db_value__ = __from_db_value__


if SQLALCHEMY_AVAILABLE:
    class TypedUUIDType(TypeDecorator):
        impl = String
        cache_ok = True

        def __init__(self, type_id: str):
            # Column size: type_id length + hyphen + UUID (36 chars)
            super().__init__(len(type_id) + 37)
            self.type_id = type_id

        @property
        def python_type(self):
            """Return the Python type for this column type."""
            # Get the specific TypedUUID class for this type_id
            uuid_class = TypedUUID.get_class_by_type_id(self.type_id)
            if uuid_class is None:
                raise NotImplementedError(f"No TypedUUID class registered for type_id: {self.type_id}")
            return uuid_class

        def process_bind_param(self, value: Optional[TypedUUID], dialect) -> Optional[str]:
            if value is None:
                return None
            if not isinstance(value, TypedUUID):
                raise ValueError(f"Value must be TypedUUID, not {type(value)}")
            if value.type_id != self.type_id:
                raise ValueError(f"Expected type_id {self.type_id}, got {value.type_id}")
            return str(value)

        def process_result_value(self, value: Optional[str], dialect) -> Optional[TypedUUID]:
            if value is None:
                return None
            return self.python_type.from_string(value)


    def create_typed_uuid_type(type_id: str) -> Type[TypedUUIDType]:
        """
        Create a specific SQLAlchemy type class for a TypedUUID type.

        Args:
            type_id: The type identifier for the UUID

        Returns:
            Type[TypedUUIDType]: A new TypedUUIDType subclass specific to the type_id
        """

        class GeneratedTypedUUIDType(TypedUUIDType):
            cache_ok = True  # Enable caching since the type is immutable

            def __init__(self):
                super().__init__(type_id)

            @property
            def python_type(self):
                return TypedUUID.get_class_by_type_id(type_id)

        GeneratedTypedUUIDType.__name__ = f"{type_id.capitalize()}UUIDType"
        return GeneratedTypedUUIDType
else:
    # Provide placeholder when SQLAlchemy is not available
    TypedUUIDType = None
    create_typed_uuid_type = None
