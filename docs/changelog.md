# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2024-01-15

### Added

- **`__slots__` optimization**: TypedUUID instances now use `__slots__` for reduced memory footprint and faster attribute access
- **Short encoding**: New `.short` property returns a compact base62-encoded format (`user_7n42DGM5Tflk9n8mt7Fhc7`)
- **Short decoding**: New `from_short()` class method to parse short-format strings back to TypedUUID instances
- **Pickle support**: Full pickle serialization/deserialization support via `__reduce__`, `__getstate__`, and `__setstate__`
- **Auto-parsing**: New `TypedUUID.parse()` method automatically detects format and returns the correct registered subclass
- **ROADMAP.md**: Documentation for planned features (UUID7, timestamp extraction, namespace UUIDs)

### Changed

- Dynamically created TypedUUID subclasses now include `__slots__ = ()` to maintain memory efficiency
- Improved thread safety with `threading.Lock` for class registry operations
- Removed arbitrary 8-character limit on type_id length

### Fixed

- Import error in `__init__.py` (`add_pydantic_support` renamed to `add_pydantic_methods`)
- UUID regex pattern now case-insensitive for proper UUID validation
- `__eq__` and `__ne__` methods now use `type(self).from_string()` instead of base class method
- FastAPI adapter `Type` import moved outside try block to prevent `NameError`
- Removed stray logger reference from another project in SQLAlchemy adapter
- Python 3.13 compatibility fix for Pydantic adapter classmethod handling

---

## [1.0.0] - 2024-01-10

### Added

**Core Features**

- Core `TypedUUID` class with type prefix support
- `create_typed_uuid_class()` factory function for creating typed UUID classes
- Class registry for tracking all created TypedUUID subclasses
- Full comparison operators (`__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`)
- Hashing support for use in sets and as dictionary keys
- JSON serialization via `json_default()` static method
- String parsing via `from_string()` class method

**Adapters**

- **SQLAlchemy adapter**: `TypedUUIDType` for database column types
- **Pydantic v2 adapter**: Validation and serialization support
- **FastAPI adapter**: Path parameter support with `path_param()` method

**Utilities**

- `create_typed_uuid_classes()` for batch creation of multiple UUID types
- Thread-safe class registry with `get_registered_class()` and `is_type_registered()`
- Custom exceptions: `TypedUUIDError`, `InvalidTypeIDError`, `InvalidUUIDError`

---

[View full changelog on GitHub](https://github.com/boxcake/TypedUUID/blob/main/CHANGELOG.md)
