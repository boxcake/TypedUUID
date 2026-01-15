# typed_uuid/adapters/pydantic.py
from typing import Type, Any
from ..core import TypedUUID
try:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler

    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import CoreSchema, core_schema

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


def add_pydantic_methods(cls: Type[TypedUUID]) -> None:
    """Add Pydantic-specific methods to a TypedUUID class."""

    def __get_pydantic_core_schema__(
            cls_inner, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """Define the Pydantic core schema for validation"""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls_inner.validate),
            ]),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls_inner),
                core_schema.no_info_plain_validator_function(cls_inner.validate),
            ]),
            serialization=core_schema.to_string_ser_schema(),
        )

    def __get_pydantic_json_schema__(
            cls_inner, core_schema_arg: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema_arg)
        json_schema.update(
            type="string",
            pattern=cls_inner.format_pattern(),
            format="typed-uuid"
        )
        return json_schema

    def __json__(self) -> str:
        """Support for JSON serialization."""
        return str(self)

    def validate_json(cls_inner, value: str) -> 'TypedUUID':
        """Validate and create instance from JSON string"""
        try:
            if isinstance(value, str):
                return cls_inner.from_string(value)
            raise ValueError(f"Invalid JSON value for {cls_inner.__name__}")
        except ValueError as e:
            raise ValueError(f"Invalid {cls_inner.__name__} format: {str(e)}")

    def model_dump(self, **kwargs):
        """Support for Pydantic model serialization"""
        return str(self)

    # Add methods to class
    cls.model_dump = model_dump
    cls.__json__ = __json__
    cls.validate_json = classmethod(validate_json)
    cls.__get_pydantic_core_schema__ = classmethod(__get_pydantic_core_schema__)
    cls.__get_pydantic_json_schema__ = classmethod(__get_pydantic_json_schema__)