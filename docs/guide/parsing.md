# Parsing and Validation

This guide covers how to parse UUID strings and validate input.

## Parsing Typed UUID Strings

### Using from_string()

The `from_string()` class method parses a string into a TypedUUID:

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

# Parse a typed UUID string
user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')
print(user_id.uuid)  # 550e8400-e29b-41d4-a716-446655440000
```

### Accepted Formats

`from_string()` accepts multiple formats:

```python
# Full typed format
user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')

# Plain UUID (type prefix added automatically)
user_id = UserUUID.from_string('550e8400-e29b-41d4-a716-446655440000')

# Case-insensitive UUID part
user_id = UserUUID.from_string('user-550E8400-E29B-41D4-A716-446655440000')
```

### Type Validation

When parsing typed strings, the type must match:

```python
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# This works
user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')

# This raises InvalidTypeIDError - wrong type
user_id = UserUUID.from_string('order-550e8400-e29b-41d4-a716-446655440000')
# InvalidTypeIDError: Type mismatch: expected user, got order
```

## Auto-Detection with parse()

When you don't know the type ahead of time:

```python
from typed_uuid import TypedUUID, create_typed_uuid_class

# Register types first
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# Auto-detect type from string
uuid1 = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
uuid2 = TypedUUID.parse('order-550e8400-e29b-41d4-a716-446655440000')

print(isinstance(uuid1, UserUUID))   # True
print(isinstance(uuid2, OrderUUID))  # True
```

### parse() with Short Format

Auto-detection also works with short format:

```python
# Standard format
uuid1 = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')

# Short format
uuid2 = TypedUUID.parse('user_7n42DGM5Tflk9n8mt7Fhc7')

# Both return UserUUID instances
```

## Validation Methods

### Using validate()

The `validate()` method accepts multiple input types:

```python
from uuid import UUID

UserUUID = create_typed_uuid_class('User', 'user')

# Validate string input
user_id = UserUUID.validate('user-550e8400-e29b-41d4-a716-446655440000')

# Validate UUID object
user_id = UserUUID.validate(UUID('550e8400-e29b-41d4-a716-446655440000'))

# Validate existing TypedUUID
existing = UserUUID()
user_id = UserUUID.validate(existing)

# Returns the same instance if already correct type
print(user_id is existing)  # True
```

### Input Type Handling

| Input Type | Behavior |
|------------|----------|
| `str` | Parsed as UUID string |
| `UUID` | Wrapped in TypedUUID |
| Same TypedUUID type | Returned as-is |
| Different TypedUUID type | Raises ValueError if type_id differs |
| Other types | Raises ValueError |

## Error Handling

### InvalidUUIDError

Raised when the UUID format is invalid:

```python
from typed_uuid import InvalidUUIDError

try:
    user_id = UserUUID.from_string('not-a-valid-uuid')
except InvalidUUIDError as e:
    print(f"Invalid UUID: {e}")
```

### InvalidTypeIDError

Raised when the type_id is invalid or mismatched:

```python
from typed_uuid import InvalidTypeIDError

try:
    # Wrong type prefix
    user_id = UserUUID.from_string('order-550e8400-e29b-41d4-a716-446655440000')
except InvalidTypeIDError as e:
    print(f"Type mismatch: {e}")
```

### Catching All TypedUUID Errors

Both errors inherit from `TypedUUIDError`:

```python
from typed_uuid import TypedUUIDError

try:
    user_id = UserUUID.from_string(some_input)
except TypedUUIDError as e:
    print(f"Error: {e}")
```

## Validation Patterns

### API Input Validation

```python
from typed_uuid import InvalidUUIDError, InvalidTypeIDError

def get_user(user_id_str: str):
    """Get user by ID with validation."""
    try:
        user_id = UserUUID.from_string(user_id_str)
    except InvalidUUIDError:
        raise ValueError(f"Invalid user ID format: {user_id_str}")
    except InvalidTypeIDError:
        raise ValueError(f"Not a user ID: {user_id_str}")

    return fetch_user(user_id)
```

### Safe Parsing with Default

```python
def parse_user_id(value: str, default=None):
    """Parse user ID, returning default on failure."""
    try:
        return UserUUID.from_string(value)
    except (InvalidUUIDError, InvalidTypeIDError):
        return default

# Usage
user_id = parse_user_id(request.args.get('id'), default=None)
if user_id is None:
    return {"error": "Invalid user ID"}, 400
```

### Batch Validation

```python
def validate_user_ids(ids: list[str]) -> tuple[list[UserUUID], list[str]]:
    """Validate a list of user IDs, separating valid from invalid."""
    valid = []
    invalid = []

    for id_str in ids:
        try:
            valid.append(UserUUID.from_string(id_str))
        except (InvalidUUIDError, InvalidTypeIDError):
            invalid.append(id_str)

    return valid, invalid

# Usage
valid_ids, invalid_ids = validate_user_ids(request.json['user_ids'])
if invalid_ids:
    return {"error": "Invalid IDs", "invalid": invalid_ids}, 400
```

## Format Pattern

Get a regex pattern for validation:

```python
pattern = UserUUID.format_pattern()
print(pattern)  # ^[a-zA-Z0-9]+-[0-9a-f]{8}-[0-9a-f]{4}-...

import re
if re.match(pattern, some_string):
    print("Looks like a valid typed UUID")
```

This is useful for:

- Pre-validation before parsing
- Database constraints
- API schema validation
