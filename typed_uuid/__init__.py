# typed_uuid/__init__.py
from .core import TypedUUID, create_typed_uuid_class
from .exceptions import TypedUUIDError, InvalidTypeIDError, InvalidUUIDError
from .utils import create_typed_uuid_classes

try:
    from .adapters.sqlalchemy import TypedUUIDType, SQLALCHEMY_AVAILABLE, create_typed_uuid_type
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    TypedUUIDType = None
    create_typed_uuid_type = None

try:
    from .adapters.pydantic import add_pydantic_methods, PYDANTIC_AVAILABLE
except ImportError:
    PYDANTIC_AVAILABLE = False
    add_pydantic_methods = None

__all__ = [
    'TypedUUID',
    'create_typed_uuid_class',
    'TypedUUIDError',
    'InvalidTypeIDError',
    'InvalidUUIDError',
    'create_typed_uuid_classes'
]

if SQLALCHEMY_AVAILABLE:
    __all__.extend(['TypedUUIDType', 'create_typed_uuid_type'])

if PYDANTIC_AVAILABLE:
    __all__.append('add_pydantic_methods')
