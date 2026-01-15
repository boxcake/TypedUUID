# typed_uuid/adapters/fastapi.py
from typing import Type, Any

try:
    from fastapi import Path
    from typing import Annotated
    from ..core import TypedUUID

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TypedUUID = None


def add_fastapi_methods(cls: Type['TypedUUID']) -> None:
    """Add FastAPI-specific methods to a TypedUUID class."""
    if not FASTAPI_AVAILABLE:
        return

    @classmethod
    def path_param(cls, description: str = None) -> Any:
        """
        Create a FastAPI path parameter for this TypedUUID type.

        Args:
            description: Optional description for the parameter

        Returns:
            Annotated type for FastAPI path parameter

        Example:
            @router.get("/{user_id}")
            async def get_user(user_id: UserUUID.path_param()): ...
        """
        return Annotated[
            cls,
            Path(
                description=description or f"{cls.__name__} identifier",
                examples=[f"{cls._type_id}-550e8400-e29b-41d4-a716-446655440000"]
            )
        ]

    # Add method to class
    cls.path_param = path_param
