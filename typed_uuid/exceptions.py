# typed_uuid/exceptions.py

class TypedUUIDError(Exception):
    """Base exception for TypedUUID errors"""
    pass


class InvalidTypeIDError(TypedUUIDError):
    """Raised when type_id is invalid"""
    pass


class InvalidUUIDError(TypedUUIDError):
    """Raised when UUID value is invalid"""
    pass
