# typed_uuid/utils.py
from typing import Any, Tuple, Type, Union
from .core import TypedUUID, create_typed_uuid_class


def create_typed_uuid_classes(
        name: str,
        type_id: str
) -> Union[Tuple[Type[TypedUUID], Any], Type[TypedUUID]]:
    """
    Create a TypedUUID class and optionally its corresponding SQLAlchemy type if available.

    Args:
        name: The base name for the classes
        type_id: The type identifier for the UUID

    Returns:
        If SQLAlchemy is available:
            Tuple[Type[TypedUUID], Type[TypedUUIDType]]: The generated TypedUUID and TypedUUIDType classes
        If SQLAlchemy is not available:
            Type[TypedUUID]: Just the generated TypedUUID class

    Example:
        >>> # With SQLAlchemy
        >>> UserUUID, UserUUIDType = create_typed_uuid_classes('User', 'user')
        >>>
        >>> # Without SQLAlchemy
        >>> UserUUID = create_typed_uuid_classes('User', 'user')
    """
    uuid_class = create_typed_uuid_class(name, type_id)

    try:
        from .adapters.fastapi import add_fastapi_methods, FASTAPI_AVAILABLE
        if FASTAPI_AVAILABLE:
            add_fastapi_methods(uuid_class)
    except ImportError:
        pass

    try:
        from .adapters.sqlalchemy import create_typed_uuid_type, SQLALCHEMY_AVAILABLE
    except ImportError:
        SQLALCHEMY_AVAILABLE = False

    if SQLALCHEMY_AVAILABLE:
        type_class = create_typed_uuid_type(type_id)
        return uuid_class, type_class

    return uuid_class
