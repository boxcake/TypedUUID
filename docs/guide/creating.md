# Creating TypedUUIDs

This guide covers all the ways to create TypedUUID classes and instances.

## Creating TypedUUID Classes

### Basic Creation

Use `create_typed_uuid_class()` to create a new TypedUUID type:

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
```

Parameters:

- `class_name`: Name for the class (used to generate `{name}UUID`)
- `type_id`: The prefix that will appear in UUID strings

### Naming Conventions

The class name and type_id serve different purposes:

```python
# class_name: Used for the Python class name
# type_id: Used in the string representation

UserUUID = create_typed_uuid_class('User', 'usr')
print(UserUUID.__name__)  # 'UserUUID'
print(UserUUID())         # 'usr-550e8400-...'
```

Common patterns:

```python
# Matching names (recommended for clarity)
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# Abbreviated type_ids (for shorter strings)
UserUUID = create_typed_uuid_class('User', 'usr')
OrganizationUUID = create_typed_uuid_class('Organization', 'org')

# Domain-specific prefixes
AccountUUID = create_typed_uuid_class('Account', 'acct')
TransactionUUID = create_typed_uuid_class('Transaction', 'txn')
```

## Creating Instances

### Generate New UUID

Create an instance with a new random UUID:

```python
UserUUID = create_typed_uuid_class('User', 'user')

# No arguments = generate new UUID v4
user_id = UserUUID()
print(user_id)  # user-550e8400-e29b-41d4-a716-446655440000
```

### From Existing UUID

Create from an existing UUID:

```python
from uuid import UUID

# From UUID object
existing_uuid = UUID('550e8400-e29b-41d4-a716-446655440000')
user_id = UserUUID(existing_uuid)

# From UUID string (plain)
user_id = UserUUID('550e8400-e29b-41d4-a716-446655440000')

# From typed UUID string
user_id = UserUUID('user-550e8400-e29b-41d4-a716-446655440000')
```

### Using from_string()

Parse from a string representation:

```python
# Parse typed format
user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')

# Parse plain UUID
user_id = UserUUID.from_string('550e8400-e29b-41d4-a716-446655440000')
```

### Using generate()

Explicitly generate a new UUID:

```python
user_id = UserUUID.generate()
```

This is equivalent to `UserUUID()` but more explicit about intent.

### Using validate()

Validate and convert various input types:

```python
from uuid import UUID

# From string
user_id = UserUUID.validate('user-550e8400-e29b-41d4-a716-446655440000')

# From UUID object
user_id = UserUUID.validate(UUID('550e8400-e29b-41d4-a716-446655440000'))

# From existing TypedUUID instance
user_id = UserUUID.validate(existing_user_id)
```

## Auto-Detection with parse()

When you have a UUID string but don't know its type:

```python
from typed_uuid import TypedUUID

# Create some types first
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# Parse with auto-detection
uuid1 = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
uuid2 = TypedUUID.parse('order-550e8400-e29b-41d4-a716-446655440000')

print(type(uuid1).__name__)  # UserUUID
print(type(uuid2).__name__)  # OrderUUID

# Also works with short format
uuid3 = TypedUUID.parse('user_7n42DGM5Tflk9n8mt7Fhc7')
print(type(uuid3).__name__)  # UserUUID
```

!!! warning "Registration Required"
    `TypedUUID.parse()` only works for registered types. Unregistered types raise `InvalidUUIDError`.

## Batch Creation with create_typed_uuid_classes()

For SQLAlchemy integration, use the utility function:

```python
from typed_uuid import create_typed_uuid_classes

# Returns tuple if SQLAlchemy is available
result = create_typed_uuid_classes('User', 'user')

# With SQLAlchemy installed:
UserUUID, UserUUIDType = result

# Without SQLAlchemy:
UserUUID = result
```

## Error Handling

Handle creation errors appropriately:

```python
from typed_uuid import create_typed_uuid_class, InvalidTypeIDError, InvalidUUIDError

# Invalid type_id
try:
    BadUUID = create_typed_uuid_class('Bad', 'user-id')  # Hyphen not allowed
except InvalidTypeIDError as e:
    print(f"Invalid type_id: {e}")

# Invalid UUID
try:
    UserUUID = create_typed_uuid_class('User', 'user')
    user_id = UserUUID('not-a-valid-uuid')
except InvalidUUIDError as e:
    print(f"Invalid UUID: {e}")
```

## Best Practices

### 1. Create Classes at Module Level

```python
# myapp/ids.py
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')
ProductUUID = create_typed_uuid_class('Product', 'product')

# Then import elsewhere
# from myapp.ids import UserUUID, OrderUUID
```

### 2. Use Descriptive Type IDs

```python
# Good: Clear what the ID represents
create_typed_uuid_class('User', 'user')
create_typed_uuid_class('Organization', 'organization')

# Less good: Cryptic abbreviations
create_typed_uuid_class('User', 'u')
create_typed_uuid_class('Organization', 'o')
```

### 3. Be Consistent with Casing

```python
# Pick a convention and stick with it
# Option 1: lowercase (recommended)
create_typed_uuid_class('User', 'user')
create_typed_uuid_class('Order', 'order')

# Option 2: UPPERCASE
create_typed_uuid_class('User', 'USER')
create_typed_uuid_class('Order', 'ORDER')
```

### 4. Document Your Types

```python
# Create a central registry of your types
"""
ID Type Registry
================
user     - User accounts
order    - Customer orders
product  - Product catalog items
org      - Organizations/tenants
"""

UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')
ProductUUID = create_typed_uuid_class('Product', 'product')
OrgUUID = create_typed_uuid_class('Organization', 'org')
```
