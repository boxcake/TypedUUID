# Core Concepts

This guide explains the fundamental concepts behind TypedUUID and how to use them effectively.

## What is a TypedUUID?

A TypedUUID combines a **type identifier** with a **standard UUID** to create a self-documenting identifier:

```
user-550e8400-e29b-41d4-a716-446655440000
│    └─────────────────────────────────────┘
│                    │
│              Standard UUID (v4)
│
└── Type identifier
```

This simple addition provides:

- **Self-documentation**: You can tell what an ID represents by looking at it
- **Type safety**: Different ID types can't be accidentally mixed up
- **Debugging**: Easier to trace IDs through logs and databases

## Class Registry

TypedUUID maintains a global registry of all created types:

```python
from typed_uuid import create_typed_uuid_class, TypedUUID

# Creating a class registers it
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# Check what's registered
print(TypedUUID.list_registered_types())  # ['user', 'order']

# Check if a type exists
print(TypedUUID.is_type_registered('user'))   # True
print(TypedUUID.is_type_registered('admin'))  # False

# Retrieve a class by type_id
cls = TypedUUID.get_class_by_type_id('user')
print(cls.__name__)  # UserUUID
```

### Registry Behavior

The registry ensures type_id uniqueness:

```python
# Creating with same type_id returns the same class
UserUUID1 = create_typed_uuid_class('User', 'user')
UserUUID2 = create_typed_uuid_class('User', 'user')

print(UserUUID1 is UserUUID2)  # True
```

!!! warning "Thread Safety"
    The registry is thread-safe. Multiple threads can safely create and access TypedUUID classes concurrently.

## Type ID Rules

Type identifiers must follow these rules:

| Rule | Description | Example |
|------|-------------|---------|
| Alphanumeric | Only letters and numbers | `user`, `Order123` |
| Case-sensitive | `user` ≠ `User` | Different types |
| Non-empty | Cannot be blank | ❌ `""` |
| No special characters | No hyphens, underscores in type_id | ❌ `user-id` |

```python
# Valid type IDs
create_typed_uuid_class('User', 'user')           # ✅
create_typed_uuid_class('Order', 'ORDER')         # ✅
create_typed_uuid_class('Product', 'prod123')     # ✅
create_typed_uuid_class('Org', 'organization')    # ✅ (any length)

# Invalid type IDs
create_typed_uuid_class('Invalid', 'user-id')     # ❌ InvalidTypeIDError
create_typed_uuid_class('Invalid', 'user_id')     # ❌ InvalidTypeIDError
create_typed_uuid_class('Invalid', '')            # ❌ InvalidTypeIDError
```

## Class Hierarchy

All TypedUUID classes inherit from the base `TypedUUID` class:

```python
from typed_uuid import TypedUUID, create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID()

# Inheritance check
print(isinstance(user_id, UserUUID))   # True
print(isinstance(user_id, TypedUUID))  # True

# Type checking in functions
def process(uuid: TypedUUID):
    """Accepts any TypedUUID subclass."""
    print(f"Processing {uuid.type_id}: {uuid}")

process(user_id)  # Works!
```

## Instance vs Class Attributes

Each TypedUUID has both instance and class-level attributes:

```python
UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID()

# Instance attributes
print(user_id.type_id)   # 'user' (from instance)
print(user_id.uuid)      # UUID object

# Class attributes
print(UserUUID._type_id) # 'user' (class-level)
```

## Memory Efficiency

TypedUUID uses `__slots__` for memory efficiency:

```python
user_id = UserUUID()

# Only stores essential data
# _uuid: The UUID object
# _instance_type_id: The type identifier string

# Cannot add arbitrary attributes
user_id.custom = "value"  # ❌ AttributeError
```

This makes TypedUUID instances lightweight, even when creating millions of them.

## Immutability

TypedUUID instances are effectively immutable:

```python
user_id = UserUUID()

# Cannot change the UUID
user_id._uuid = some_other_uuid  # Technically possible but don't do it!

# The string representation is always consistent
str1 = str(user_id)
str2 = str(user_id)
print(str1 == str2)  # Always True
```

## Hashing and Equality

TypedUUIDs are hashable and can be used in sets and as dictionary keys:

```python
user1 = UserUUID('550e8400-e29b-41d4-a716-446655440000')
user2 = UserUUID('550e8400-e29b-41d4-a716-446655440000')

# Same UUID = same hash
print(hash(user1) == hash(user2))  # True

# Works in sets
users = {user1, user2}
print(len(users))  # 1 (duplicates removed)

# Works as dict keys
data = {user1: "Alice"}
print(data[user2])  # "Alice" (same key)
```

## Next Steps

- [Creating TypedUUIDs](creating.md) - Detailed creation options
- [Parsing and Validation](parsing.md) - Parse and validate UUIDs
- [Short Encoding](short-encoding.md) - URL-friendly format
