# TypedUUID Class

The core class for type-safe UUID management.

## Overview

`TypedUUID` is the base class for all typed UUID instances. While you typically work with subclasses created via `create_typed_uuid_class()`, understanding the base class is important for advanced usage.

## Class Reference

::: typed_uuid.core.TypedUUID
    options:
      members:
        - __init__
        - type_id
        - uuid
        - from_string
        - validate
        - generate
        - parse
        - short
        - from_short
        - format_pattern
        - get_uuid
        - get_registered_class
        - get_class_by_type_id
        - is_type_registered
        - list_registered_types
        - json_default
        - __str__
        - __repr__
        - __eq__
        - __ne__
        - __lt__
        - __le__
        - __gt__
        - __ge__
        - __hash__
        - __bytes__
      show_root_heading: true
      show_source: false
      heading_level: 3

## Usage Examples

### Creating Instances

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

# Generate new UUID
user_id = UserUUID()

# From existing UUID string
user_id = UserUUID('550e8400-e29b-41d4-a716-446655440000')

# From typed string
user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')
```

### Properties

```python
user_id = UserUUID()

# Get the type identifier
print(user_id.type_id)  # 'user'

# Get the underlying UUID object
print(user_id.uuid)  # UUID('550e8400-...')

# Get short format
print(user_id.short)  # 'user_7n42DGM5Tflk9n8mt7Fhc7'
```

### Comparison Operations

```python
user1 = UserUUID('550e8400-e29b-41d4-a716-446655440000')
user2 = UserUUID('550e8400-e29b-41d4-a716-446655440000')
user3 = UserUUID()

# Equality
user1 == user2  # True
user1 == user3  # False

# String comparison
user1 == 'user-550e8400-e29b-41d4-a716-446655440000'  # True

# Ordering
sorted([user3, user1])  # Sorts by UUID value
```

### Registry Operations

```python
from typed_uuid import TypedUUID

# Check if type is registered
TypedUUID.is_type_registered('user')  # True

# List all registered types
TypedUUID.list_registered_types()  # ['user', 'order', ...]

# Get class by type_id
UserUUID = TypedUUID.get_class_by_type_id('user')
```

### Auto-Detection

```python
from typed_uuid import TypedUUID

# Parse any registered type
uuid = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
print(type(uuid).__name__)  # 'UserUUID'

# Works with short format too
uuid = TypedUUID.parse('user_7n42DGM5Tflk9n8mt7Fhc7')
```

## Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_type_id` | `ClassVar[str]` | The type identifier for this class |
| `_class_registry` | `ClassVar[Dict]` | Registry of all TypedUUID classes |
| `_registry_lock` | `ClassVar[Lock]` | Thread lock for registry access |

## Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_uuid` | `UUID` | The underlying UUID object |
| `_instance_type_id` | `str` | The type identifier for this instance |

## See Also

- [Creating TypedUUIDs](../guide/creating.md) - Detailed creation guide
- [Factory Functions](factory.md) - `create_typed_uuid_class()` documentation
- [Exceptions](exceptions.md) - Error handling
