"""
typed_uuid
~~~~~~~~~~

A robust implementation of typed UUIDs for Python applications, providing type-safe UUID
management with prefix identification and full Pydantic/SQLAlchemy integration.

Basic usage:
#    >>> from typed_uuid import create_typed_uuid_class
#    >>> UserUUID = create_typed_uuid_class('User', 'user')
#    >>> user_id = UserUUID()
#    >>> str(user_id)
#    'user-550e8400-e29b-41d4-a716-446655440000'
"""

from typing import Any, Type, Optional, TypeVar, cast, ClassVar, Union, Dict, List, Set, Tuple
from uuid import UUID, uuid4
import re
import threading
from .exceptions import InvalidTypeIDError, InvalidUUIDError
from logging import getLogger

logger = getLogger(__name__)

T = TypeVar('T', bound='TypedUUID')

# Base62 alphabet for short encoding
_BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_BASE62_MAP = {c: i for i, c in enumerate(_BASE62_ALPHABET)}


def _encode_base62(num: int) -> str:
    """Encode an integer to base62 string."""
    if num == 0:
        return _BASE62_ALPHABET[0]

    result = []
    while num:
        num, remainder = divmod(num, 62)
        result.append(_BASE62_ALPHABET[remainder])
    return ''.join(reversed(result))


def _decode_base62(s: str) -> int:
    """Decode a base62 string to integer."""
    num = 0
    for char in s:
        if char not in _BASE62_MAP:
            raise ValueError(f"Invalid base62 character: {char}")
        num = num * 62 + _BASE62_MAP[char]
    return num


def _reconstruct_typed_uuid(type_id: str, uuid_str: str) -> 'TypedUUID':
    """
    Reconstruct a TypedUUID instance from pickle data.

    This function is used by __reduce__ to enable pickling of dynamically
    created TypedUUID subclasses.
    """
    # Get the class from registry, or create it if needed
    cls = TypedUUID.get_class_by_type_id(type_id)
    if cls is None:
        # Class not registered yet, create a generic one
        cls = create_typed_uuid_class(type_id.capitalize(), type_id)
    return cls(uuid_value=uuid_str)


class TypedUUID:
    """
    A UUID class that includes a type prefix for improved type safety and identification.

    This class maintains a registry of all created TypedUUID subclasses, ensuring that
    each type_id is unique and allowing retrieval of existing classes.

    Attributes:
        _type_id (ClassVar[str]): Class-level type identifier
        _class_registry (ClassVar[Dict[str, Type['TypedUUID']]]): Registry of TypedUUID classes

    Args:
        type_id (str): The type identifier prefix (alphanumeric only)
        uuid_value (Optional[Union[UUID, str, 'TypedUUID']]): Initial UUID value

    Raises:
        ValueError: If type_id is invalid or uuid_value cannot be parsed

    Example:
    #    >>> UserUUID = create_typed_uuid_class('User', 'user')
    #    >>> user_id = UserUUID()
    #    >>> str(user_id)
    #    'user-550e8400-e29b-41d4-a716-446655440000'
    #    >>> UserUUID.is_type_registered('user')
    #    True
    """

    __slots__ = ('_uuid', '_instance_type_id')

    _type_id: ClassVar[str] = None
    _uuid_pattern: ClassVar[re.Pattern] = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    _class_registry: ClassVar[Dict[str, Type['TypedUUID']]] = {}
    _registry_lock: ClassVar[threading.Lock] = threading.Lock()
    # Short format pattern: type_base62encoded
    _short_pattern: ClassVar[re.Pattern] = re.compile(
        r'^([a-zA-Z0-9]+)_([0-9A-Za-z]+)$'
    )

    @classmethod
    def get_registered_class(cls, type_id: str) -> Optional[Type['TypedUUID']]:
        """Get an existing TypedUUID class for a type_id if one exists."""
        with cls._registry_lock:
            return cls._class_registry.get(type_id)

    def __init__(
            self,
            type_id: str,
            uuid_value: Optional[Union[UUID, str, 'TypedUUID']] = None
    ) -> None:
        self._validate_type_id(type_id)
        self._instance_type_id: str = type_id
        self._uuid: UUID = self._process_uuid_value(uuid_value)

    # Core methods for base class
    @property
    def type_id(self) -> str:
        """Get the type identifier."""
        return self._instance_type_id

    @property
    def uuid(self) -> UUID:
        """Get the underlying UUID."""
        return self._uuid

    def __str__(self) -> str:
        """Return the string representation as 'type-uuid'."""
        return f"{self._instance_type_id}-{self._uuid}"

    # Yes, we have three methods for JSON serialization support.
    def __json__(self):
        """
        Support for JSON serialization.
        Used by:
            simplejson library when for_json=True is set
            Used by the FastAPI default JSON encoder
            MongoDB's BSON encoder
        """
        return str(self)

    def to_json(self):
        """
        Additional JSON serialization support.
        Used by:
            Some older Flask extensions
        """
        return str(self)

    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"TypedUUID(type_id='{self._instance_type_id}', uuid='{self._uuid}')"

    def __lt__(self, other: Any) -> bool:
        """Support sorting."""
        if isinstance(other, TypedUUID):
            return self.__key() < other.__key()
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        """Support sorting."""
        if isinstance(other, TypedUUID):
            return self.__key() <= other.__key()
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        """Support sorting."""
        if isinstance(other, TypedUUID):
            return self.__key() > other.__key()
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        """Support sorting."""
        if isinstance(other, TypedUUID):
            return self.__key() >= other.__key()
        return NotImplemented

    def __eq__(self, other: Any) -> bool:
        """Support equality comparison."""
        if isinstance(other, TypedUUID):
            return self.__key() == other.__key()
        if isinstance(other, str):
            try:
                # Use the instance's class to parse the string
                other_uuid = type(self).from_string(other)
                return self.__key() == other_uuid.__key()
            except (ValueError, AttributeError, InvalidUUIDError, InvalidTypeIDError, TypeError):
                return False
        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        """Support inequality comparison."""
        if isinstance(other, TypedUUID):
            return self.__key() != other.__key()
        if isinstance(other, str):
            try:
                # Use the instance's class to parse the string
                other_uuid = type(self).from_string(other)
                return self.__key() != other_uuid.__key()
            except (ValueError, AttributeError, InvalidUUIDError, InvalidTypeIDError, TypeError):
                return True
        return NotImplemented

    def __hash__(self) -> int:
        """Generate a hash based on type_id and uuid."""
        return hash((self._instance_type_id, self._uuid))

    def __format__(self, format_spec: str) -> str:
        """Support string formatting."""
        return format(str(self), format_spec)

    def __bytes__(self) -> bytes:
        """Convert to bytes."""
        return str(self).encode()

    def __key(self) -> tuple:
        """Get tuple for comparisons."""
        return self._instance_type_id, self._uuid

    @classmethod
    def from_string(cls, value: str) -> 'TypedUUID':
        """
        Enhanced from_string method that handles multiple string formats:
        - Full typed UUID: "type-uuid"
        - Plain UUID: "uuid"

        Args:
            value: String representation of UUID with optional type prefix

        Returns:
            TypedUUID: Instance of the specific TypedUUID subclass

        Raises:
            InvalidUUIDError: If the UUID format is invalid
            InvalidTypeIDError: If type_id doesn't match class type
        """
        if not value:
            raise InvalidUUIDError("UUID string cannot be empty")

        # First try to parse as a complete UUID
        try:
            UUID(value)
            return cls(uuid_value=value)
        except ValueError:
            # If that fails, try parsing as type-prefixed UUID
            if '-' in value:
                parts = value.split('-', 1)
                if len(parts) == 2 and parts[0].isalnum():
                    try:
                        # Verify the second part is a valid UUID
                        UUID(parts[1])
                        # If class has a type_id, validate it matches
                        if cls._type_id is not None and parts[0] != cls._type_id:
                            raise InvalidTypeIDError(
                                f"Type mismatch: expected {cls._type_id}, got {parts[0]}"
                            )
                        return cls(uuid_value=parts[1])
                    except ValueError:
                        raise InvalidUUIDError(f"Invalid UUID part: {parts[1]}")

            raise InvalidUUIDError(f"Invalid UUID format: {value}")

    # Protected helper methods
    @classmethod
    def _validate_type_id(cls, type_id: str) -> None:
        """Validate type_id format."""
        if type_id is None:
            raise InvalidTypeIDError("type_id cannot be None")
        if not isinstance(type_id, str):
            raise InvalidTypeIDError(f"type_id must be a string, not {type(type_id)}")
        if not type_id.strip():
            raise InvalidTypeIDError("type_id cannot be empty")
        if not type_id.isalnum():
            raise InvalidTypeIDError("type_id must be alphanumeric")

    def _process_uuid_value(self, uuid_value: Optional[Union[UUID, str, 'TypedUUID']]) -> UUID:
        """Process and validate uuid_value."""
        if uuid_value is None:
            return uuid4()

        if isinstance(uuid_value, UUID):
            return uuid_value

        if isinstance(uuid_value, TypedUUID):
            if uuid_value.type_id != self._instance_type_id:
                raise InvalidUUIDError(
                    f"Cannot create {self._instance_type_id} UUID from "
                    f"{uuid_value.type_id} UUID. Type mismatch."
                )
            return uuid_value.uuid

        if isinstance(uuid_value, str):
            return self._process_uuid_string(uuid_value)

        raise InvalidUUIDError(
            f"uuid_value must be UUID, str, TypedUUID, or None, not {type(uuid_value)}"
        )

    def get_uuid(self) -> str:
        """Get the UUID string without the type prefix."""
        return str(self._uuid)

    def _process_uuid_string(self, uuid_str: str) -> UUID:
        """
        Process and validate a UUID string.

        Args:
            uuid_str: String to process as UUID or TypedUUID

        Returns:
            UUID: Processed UUID instance

        Raises:
            InvalidUUIDError: If UUID format is invalid
            InvalidTypeIDError: If type_id doesn't match
        """
        if not uuid_str:
            logger.debug("_process_uuid_string: Empty UUID string")
            raise InvalidUUIDError("UUID string cannot be empty")

        # First try to parse as a complete UUID
        try:
            u = UUID(uuid_str)
            return u
        except ValueError:
            pass

        # If that fails, then check if it's a typed format
        if '-' in uuid_str:
            type_id, uuid_part = uuid_str.split('-', 1)
            if type_id.isalnum():
                # Verify it's a valid UUID part first
                try:
                    if self._uuid_pattern.match(uuid_part):
                        # Only then check type_id
                        if type_id != self._instance_type_id:
                            raise InvalidTypeIDError(
                                f"Type mismatch: expected {self._instance_type_id}, got {type_id}"
                            )
                        return UUID(uuid_part)
                except ValueError:
                    pass

        raise InvalidUUIDError(f"Invalid UUID format: {uuid_str}")

    @classmethod
    def format_pattern(cls) -> str:
        """Get the regex pattern for UUID format validation."""
        return (
            r"^[a-zA-Z0-9]+-"
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )

    # Type registry methods
    @classmethod
    def list_registered_types(cls) -> List[str]:
        """
        List all registered type IDs.

        Returns:
            List[str]: List of registered type IDs
        """
        with cls._registry_lock:
            return list(cls._class_registry.keys())

    @classmethod
    def get_class_by_type_id(cls, type_id: str) -> Optional[Type['TypedUUID']]:
        """
        Get the TypedUUID class for a given type_id.

        Args:
            type_id: The type identifier to look up

        Returns:
            Optional[Type['TypedUUID']]: The registered class or None if not found
        """
        with cls._registry_lock:
            return cls._class_registry.get(type_id)

    @classmethod
    def is_type_registered(cls, type_id: str) -> bool:
        """
        Check if a type_id is already registered.

        Args:
            type_id: The type identifier to check

        Returns:
            bool: True if type_id is registered, False otherwise
        """
        with cls._registry_lock:
            return type_id in cls._class_registry

    @classmethod
    def get_supported_adapters(cls) -> Set[str]:
        """Return set of supported adapter names for this class."""
        supported = set()
        if hasattr(cls, '__composite_values__'):
            supported.add('sqlalchemy')
        if hasattr(cls, '__get_pydantic_core_schema__'):
            supported.add('pydantic')
        return supported

    @staticmethod
    def json_default(obj):
        """Default JSON encoder for TypedUUID objects."""
        return str(obj)

    # Short encoding/decoding methods
    @property
    def short(self) -> str:
        """
        Get the short base62-encoded representation.

        Returns:
            str: Short format like 'user_7n42DGM5Tflk9n8mt7Fhc7'

        Example:
            >>> user_id = UserUUID()
            >>> user_id.short
            'user_7n42DGM5Tflk9n8mt7Fhc7'
        """
        # Convert UUID to integer and encode as base62
        uuid_int = self._uuid.int
        encoded = _encode_base62(uuid_int)
        return f"{self._instance_type_id}_{encoded}"

    @classmethod
    def from_short(cls, short_str: str) -> 'TypedUUID':
        """
        Create a TypedUUID from a short base62-encoded string.

        Args:
            short_str: Short format string like 'user_7n42DGM5Tflk9n8mt7Fhc7'

        Returns:
            TypedUUID: Instance of the TypedUUID subclass

        Raises:
            InvalidUUIDError: If format is invalid
            InvalidTypeIDError: If type doesn't match class type

        Example:
            >>> user_id = UserUUID.from_short('user_7n42DGM5Tflk9n8mt7Fhc7')
        """
        match = cls._short_pattern.match(short_str)
        if not match:
            raise InvalidUUIDError(f"Invalid short format: {short_str}")

        type_id, encoded = match.groups()

        # Validate type_id if class has one
        if cls._type_id is not None and type_id != cls._type_id:
            raise InvalidTypeIDError(
                f"Type mismatch: expected {cls._type_id}, got {type_id}"
            )

        try:
            uuid_int = _decode_base62(encoded)
            uuid_obj = UUID(int=uuid_int)
            return cls(uuid_value=uuid_obj)
        except (ValueError, OverflowError) as e:
            raise InvalidUUIDError(f"Invalid short encoding: {e}")

    # Pickle support
    def __reduce__(self) -> Tuple[Any, ...]:
        """
        Support for pickle serialization.

        Returns a tuple that allows pickle to reconstruct this object.
        Uses _reconstruct_typed_uuid helper for dynamically created classes.
        """
        return (
            _reconstruct_typed_uuid,
            (self._instance_type_id, str(self._uuid))
        )

    def __getstate__(self) -> Dict[str, Any]:
        """Get state for pickle serialization."""
        return {
            'type_id': self._instance_type_id,
            'uuid': str(self._uuid)
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Restore state from pickle deserialization."""
        self._instance_type_id = state['type_id']
        self._uuid = UUID(state['uuid'])

    # Auto-parsing from registry
    @classmethod
    def parse(cls, value: str) -> 'TypedUUID':
        """
        Parse a typed UUID string and return the appropriate TypedUUID subclass instance.

        This method automatically detects the type from the string and returns
        an instance of the correct registered TypedUUID subclass.

        Args:
            value: String in format 'type-uuid' or 'type_base62' (short format)

        Returns:
            TypedUUID: Instance of the appropriate TypedUUID subclass

        Raises:
            InvalidUUIDError: If format is invalid or type is not registered

        Example:
            >>> UserUUID = create_typed_uuid_class('User', 'user')
            >>> user_id = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
            >>> isinstance(user_id, UserUUID)
            True
        """
        if not value:
            raise InvalidUUIDError("Cannot parse empty string")

        # Try short format first (type_base62)
        short_match = cls._short_pattern.match(value)
        if short_match:
            type_id, _ = short_match.groups()
            target_cls = cls.get_class_by_type_id(type_id)
            if target_cls is None:
                raise InvalidUUIDError(f"Unknown type_id: {type_id}")
            return target_cls.from_short(value)

        # Try standard format (type-uuid)
        if '-' in value:
            parts = value.split('-', 1)
            if len(parts) == 2 and parts[0].isalnum():
                type_id = parts[0]
                # Check if it looks like a typed UUID (not a plain UUID)
                try:
                    # If the whole thing is a valid UUID, it's not typed
                    UUID(value)
                except ValueError:
                    # Not a plain UUID, so check for registered type
                    target_cls = cls.get_class_by_type_id(type_id)
                    if target_cls is not None:
                        return target_cls.from_string(value)
                    raise InvalidUUIDError(f"Unknown type_id: {type_id}")

        raise InvalidUUIDError(
            f"Invalid format: {value}. Expected 'type-uuid' or 'type_base62'"
        )

    # Helper for IDE class method resolution since path_param is added dynamically based on FastAPI availability
    @classmethod
    def path_param(cls, description: str = None) -> Any:
        """
        Create a FastAPI path parameter for this TypedUUID type.
        This is a stub that will be replaced by the FastAPI adapter if FastAPI is available.

        Args:
            description: Optional description for the parameter

        Returns:
            Annotated type for FastAPI path parameter

        Example:
            @router.get("/{user_id}")
            async def get_user(user_id: UserUUID.path_param()): ...

        Raises:
            NotImplementedError: If FastAPI is not installed
        """
        raise NotImplementedError(
            "FastAPI is not installed. Install it with: pip install fastapi"
        )

def create_typed_uuid_class(class_name: str, type_id: str) -> Type[T]:
    """
    Create or retrieve a TypedUUID subclass with the specified type_id.
    If a class with the given type_id already exists, returns the existing class.

    This function is thread-safe.

    Args:
        class_name: Name for the new class
        type_id: Type identifier for the UUID (alphanumeric characters only)

    Returns:
        Type[T]: New or existing TypedUUID subclass
    """
    # Use TypedUUID's validation method instead of duplicating the check
    TypedUUID._validate_type_id(type_id)  # This will raise InvalidTypeIDError if invalid

    with TypedUUID._registry_lock:
        # Check if we already have a class for this type_id (inside lock for thread safety)
        existing_class = TypedUUID._class_registry.get(type_id)
        if existing_class is not None:
            return cast(Type[T], existing_class)

        class_name_with_suffix = f"{class_name}UUID"

        def __init__(self, uuid_value: Optional[Union[UUID, str]] = None):
            """Initialize a new typed UUID instance."""
            super(self.__class__, self).__init__(type_id=type_id, uuid_value=uuid_value)

        @classmethod
        def validate(cls, v: Any) -> T:
            """Validate method specific to the created class"""
            try:
                if isinstance(v, str):
                    # For string input, try parsing it
                    if '-' in v:
                        parsed_type, uuid_str = v.split('-', 1)
                        if parsed_type == type_id:
                            return cls(uuid_value=uuid_str)
                    # If no type prefix or wrong prefix, try whole string as UUID
                    return cls(uuid_value=v)
                elif isinstance(v, UUID):
                    return cls(uuid_value=v)
                elif isinstance(v, cls):
                    return v
                elif isinstance(v, TypedUUID):
                    if v.type_id != type_id:
                        raise ValueError(f"Invalid type_id for {cls.__name__}")
                    return cls(v.uuid)
            except ValueError as e:
                raise ValueError(f"Invalid {cls.__name__} format: {str(e)}")
            raise ValueError(f"Invalid type for {cls.__name__}")

        @classmethod
        def generate(cls) -> T:
            """Generate a new instance with a random UUID."""
            return cls()

        # Create the new class with empty __slots__ to maintain memory efficiency
        new_class = type(
            class_name_with_suffix,
            (TypedUUID,),
            {
                '__slots__': (),  # Empty slots - parent has the actual slots
                '_type_id': type_id,
                '__init__': __init__,
                'validate': validate,
                'generate': generate,
                '__doc__': f"""A TypedUUID subclass for {class_name} identifiers with type_id '{type_id}'."""
            }
        )

        # Register the new class
        TypedUUID._class_registry[type_id] = new_class

    # Add adapter methods if available (outside lock - these don't modify registry)
    try:
        from .adapters.sqlalchemy import add_sqlalchemy_methods, SQLALCHEMY_AVAILABLE
        if SQLALCHEMY_AVAILABLE:
            add_sqlalchemy_methods(new_class)
    except ImportError:
        pass

    try:
        from .adapters.pydantic import add_pydantic_methods, PYDANTIC_AVAILABLE
        if PYDANTIC_AVAILABLE:
            add_pydantic_methods(new_class)
    except ImportError:
        pass

    try:
        from .adapters.fastapi import add_fastapi_methods, FASTAPI_AVAILABLE
        if FASTAPI_AVAILABLE:
            add_fastapi_methods(new_class)
    except ImportError:
        pass

    return cast(Type[T], new_class)
