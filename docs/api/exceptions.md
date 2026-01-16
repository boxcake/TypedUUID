# Exceptions

TypedUUID exception classes for error handling.

## Exception Hierarchy

```
Exception
└── TypedUUIDError
    ├── InvalidTypeIDError
    └── InvalidUUIDError
```

---

## TypedUUIDError

Base exception for all TypedUUID errors.

::: typed_uuid.exceptions.TypedUUIDError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Usage

Catch all TypedUUID-related errors:

```python
from typed_uuid import TypedUUIDError

try:
    user_id = UserUUID.from_string(some_input)
except TypedUUIDError as e:
    print(f"TypedUUID error: {e}")
```

---

## InvalidTypeIDError

Raised when a type_id is invalid or mismatched.

::: typed_uuid.exceptions.InvalidTypeIDError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### When Raised

- Creating a class with an invalid type_id
- Parsing a UUID with wrong type prefix
- Type mismatch during validation

### Examples

```python
from typed_uuid import create_typed_uuid_class, InvalidTypeIDError

# Invalid type_id format
try:
    BadUUID = create_typed_uuid_class('Bad', 'user-id')  # Hyphen not allowed
except InvalidTypeIDError as e:
    print(f"Invalid type_id: {e}")

# Type mismatch
try:
    UserUUID = create_typed_uuid_class('User', 'user')
    user_id = UserUUID.from_string('order-550e8400-e29b-41d4-a716-446655440000')
except InvalidTypeIDError as e:
    print(f"Type mismatch: {e}")
    # Output: "Type mismatch: expected user, got order"
```

### Common Causes

| Error | Cause | Solution |
|-------|-------|----------|
| `type_id must be alphanumeric` | Special characters in type_id | Use only a-z, A-Z, 0-9 |
| `type_id cannot be empty` | Empty string | Provide a valid type_id |
| `Type mismatch: expected X, got Y` | Wrong type prefix | Use correct TypedUUID class |

---

## InvalidUUIDError

Raised when a UUID value is invalid.

::: typed_uuid.exceptions.InvalidUUIDError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### When Raised

- Parsing an invalid UUID string
- Creating instance with malformed UUID
- Unknown type_id when using `TypedUUID.parse()`

### Examples

```python
from typed_uuid import InvalidUUIDError

# Invalid UUID format
try:
    user_id = UserUUID.from_string('not-a-valid-uuid')
except InvalidUUIDError as e:
    print(f"Invalid UUID: {e}")

# Unknown type in parse()
try:
    uuid = TypedUUID.parse('unknown-550e8400-e29b-41d4-a716-446655440000')
except InvalidUUIDError as e:
    print(f"Unknown type: {e}")
    # Output: "Unknown type_id: unknown"
```

### Common Causes

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid UUID format` | Malformed UUID string | Check UUID format |
| `UUID string cannot be empty` | Empty input | Validate input before parsing |
| `Unknown type_id` | Type not registered | Register type first |

---

## Error Handling Patterns

### Basic Error Handling

```python
from typed_uuid import (
    TypedUUIDError,
    InvalidTypeIDError,
    InvalidUUIDError
)

def parse_user_id(value: str):
    try:
        return UserUUID.from_string(value)
    except InvalidTypeIDError:
        raise ValueError(f"Not a user ID: {value}")
    except InvalidUUIDError:
        raise ValueError(f"Invalid UUID format: {value}")
```

### Specific Error Handling

```python
def validate_and_parse(value: str, expected_type: type):
    try:
        result = expected_type.from_string(value)
        return result
    except InvalidTypeIDError as e:
        # Wrong type prefix
        return None, f"Type error: {e}"
    except InvalidUUIDError as e:
        # Invalid format
        return None, f"Format error: {e}"
```

### API Error Response

```python
from fastapi import HTTPException

def get_user(user_id_str: str):
    try:
        user_id = UserUUID.from_string(user_id_str)
    except InvalidTypeIDError:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID type"
        )
    except InvalidUUIDError:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID format"
        )

    return fetch_user(user_id)
```

### Safe Parsing Helper

```python
from typing import Optional, TypeVar, Type

T = TypeVar('T', bound=TypedUUID)

def safe_parse(
    value: str,
    uuid_type: Type[T]
) -> Optional[T]:
    """Parse UUID safely, returning None on error."""
    try:
        return uuid_type.from_string(value)
    except (InvalidTypeIDError, InvalidUUIDError):
        return None

# Usage
user_id = safe_parse(request.args['id'], UserUUID)
if user_id is None:
    return {"error": "Invalid ID"}, 400
```
