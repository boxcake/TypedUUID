# TypedUUID

[![CI](https://github.com/boxcake/TypedUUID/actions/workflows/ci.yml/badge.svg)](https://github.com/boxcake/TypedUUID/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/typed-uuid.svg)](https://badge.fury.io/py/typed-uuid)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust Python library for type-safe UUID management with prefix identification. TypedUUID enhances standard UUIDs by adding a type prefix, making it easy to identify what kind of entity a UUID represents at a glance.

## Features

- **Type-safe UUIDs**: Prefix UUIDs with a type identifier (e.g., `user-550e8400-e29b-41d4-a716-446655440000`)
- **Human-readable**: Instantly identify what type of entity a UUID belongs to
- **Thread-safe**: Safe for use in multi-threaded applications
- **Framework integrations**: Built-in support for SQLAlchemy, Pydantic, and FastAPI
- **Zero hard dependencies**: Core library works standalone; adapters activate when frameworks are installed
- **Full validation**: Comprehensive validation of type IDs and UUID formats
- **Comparison support**: Full support for equality, ordering, and hashing

## Installation

```bash
pip install typed-uuid
```

### Optional dependencies

```bash
# For SQLAlchemy support
pip install typed-uuid[sqlalchemy]

# For Pydantic support
pip install typed-uuid[pydantic]

# For FastAPI support (includes Pydantic)
pip install typed-uuid[fastapi]

# For all integrations
pip install typed-uuid[all]
```

## Quick Start

```python
from typed_uuid import create_typed_uuid_class

# Create a typed UUID class for users
UserUUID = create_typed_uuid_class('User', 'user')

# Generate a new UUID
user_id = UserUUID()
print(user_id)  # user-550e8400-e29b-41d4-a716-446655440000

# Parse from string
user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')

# Create from existing UUID
from uuid import UUID
user_id = UserUUID(uuid_value=UUID('550e8400-e29b-41d4-a716-446655440000'))

# Get the raw UUID without prefix
raw_uuid = user_id.get_uuid()  # '550e8400-e29b-41d4-a716-446655440000'
```

## Type ID Rules

- Must be alphanumeric only (a-z, A-Z, 0-9)
- Case-sensitive (`user` and `User` are different types)
- Cannot be empty

```python
# Valid type IDs
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')
ProductUUID = create_typed_uuid_class('Product', 'prod')
OrgUUID = create_typed_uuid_class('Organization', 'organization')  # Long type IDs are fine

# Invalid type IDs (will raise InvalidTypeIDError)
create_typed_uuid_class('Invalid', 'user-id')      # Contains hyphen
create_typed_uuid_class('Invalid', 'user@id')      # Contains special character
create_typed_uuid_class('Invalid', '')             # Empty
```

## API Reference

### TypedUUID Class

#### Class Methods

| Method | Description |
|--------|-------------|
| `from_string(value)` | Parse a TypedUUID from a string |
| `generate()` | Generate a new instance with a random UUID |
| `validate(value)` | Validate and convert a value to this TypedUUID type |
| `is_type_registered(type_id)` | Check if a type_id is registered |
| `list_registered_types()` | List all registered type IDs |
| `get_class_by_type_id(type_id)` | Get the class for a type_id |
| `format_pattern()` | Get the regex pattern for validation |

#### Instance Properties

| Property | Description |
|----------|-------------|
| `type_id` | The type identifier prefix |
| `uuid` | The underlying UUID object |

#### Instance Methods

| Method | Description |
|--------|-------------|
| `get_uuid()` | Get the UUID string without the type prefix |
| `__str__()` | Returns the full typed UUID string |
| `__hash__()` | Enables use in sets and dict keys |

### Factory Functions

#### `create_typed_uuid_class(class_name, type_id)`

Creates a new TypedUUID subclass with the specified type identifier.

```python
UserUUID = create_typed_uuid_class('User', 'user')
```

#### `create_typed_uuid_classes(name, type_id)`

Creates both a TypedUUID class and its corresponding SQLAlchemy type (if SQLAlchemy is available).

```python
# With SQLAlchemy installed
UserUUID, UserUUIDType = create_typed_uuid_classes('User', 'user')

# Without SQLAlchemy
UserUUID = create_typed_uuid_classes('User', 'user')
```

## Framework Integrations

### SQLAlchemy

TypedUUID integrates seamlessly with SQLAlchemy for database storage.

```python
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from typed_uuid import create_typed_uuid_classes

Base = declarative_base()

# Create both UUID class and SQLAlchemy type
UserUUID, UserUUIDType = create_typed_uuid_classes('User', 'user')

class User(Base):
    __tablename__ = 'users'

    id = Column(UserUUIDType(), primary_key=True, default=UserUUID)
    name = Column(String(100))

# Usage
user = User(id=UserUUID(), name="Alice")
session.add(user)
session.commit()

# The ID is stored as 'user-550e8400-e29b-41d4-a716-446655440000' in the database
```

### Pydantic

TypedUUID works with Pydantic v2 for validation and serialization.

```python
from pydantic import BaseModel
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

class UserModel(BaseModel):
    id: UserUUID
    name: str

# Validation from string
user = UserModel(id='user-550e8400-e29b-41d4-a716-446655440000', name='Alice')

# Validation from UUID instance
user = UserModel(id=UserUUID(), name='Bob')

# Serialization
print(user.model_dump_json())
# {"id": "user-550e8400-e29b-41d4-a716-446655440000", "name": "Bob"}
```

### FastAPI

TypedUUID provides FastAPI path parameter support with automatic OpenAPI documentation.

```python
from fastapi import FastAPI
from typed_uuid import create_typed_uuid_class

app = FastAPI()

UserUUID = create_typed_uuid_class('User', 'user')

@app.get("/users/{user_id}")
async def get_user(user_id: UserUUID.path_param(description="The user's ID")):
    return {"user_id": str(user_id)}

# OpenAPI docs will show the parameter with:
# - Example: user-550e8400-e29b-41d4-a716-446655440000
# - Pattern validation
# - Description
```

## Comparison and Hashing

TypedUUID instances support full comparison operations:

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

id1 = UserUUID()
id2 = UserUUID()

# Equality
id1 == id2  # False (different UUIDs)
id1 == id1  # True

# String comparison
id1 == 'user-550e8400-e29b-41d4-a716-446655440000'  # True if UUIDs match

# Ordering (for sorting)
sorted([id2, id1])  # Sorts by (type_id, uuid)

# Hashing (for sets and dicts)
user_set = {id1, id2}
user_dict = {id1: "Alice", id2: "Bob"}
```

## JSON Serialization

TypedUUID supports multiple JSON serialization methods:

```python
import json
from typed_uuid import create_typed_uuid_class, TypedUUID

UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID()

# Using default encoder
json.dumps({'id': user_id}, default=TypedUUID.json_default)

# Using __json__ method (supported by simplejson, FastAPI)
user_id.__json__()  # 'user-550e8400-e29b-41d4-a716-446655440000'

# Direct string conversion
str(user_id)  # 'user-550e8400-e29b-41d4-a716-446655440000'
```

## Short Encoding

TypedUUID supports compact base62 encoding for URL-friendly identifiers:

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID()

# Get short representation
print(user_id.short)  # user_7n42DGM5Tflk9n8mt7Fhc7

# Decode from short format
decoded = UserUUID.from_short('user_7n42DGM5Tflk9n8mt7Fhc7')
assert decoded.uuid == user_id.uuid
```

The short format uses underscore (`_`) as separator to distinguish from the standard hyphen-separated format.

## Auto-Parsing

Parse typed UUIDs without knowing the type in advance:

```python
from typed_uuid import TypedUUID, create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# Auto-detect type from string (standard format)
entity = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
assert isinstance(entity, UserUUID)

# Also works with short format
entity = TypedUUID.parse('order_7n42DGM5Tflk9n8mt7Fhc7')
assert isinstance(entity, OrderUUID)
```

## Pickle Support

TypedUUID instances can be pickled and unpickled:

```python
import pickle
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID()

# Pickle and restore
data = pickle.dumps(user_id)
restored = pickle.loads(data)

assert restored.uuid == user_id.uuid
assert isinstance(restored, UserUUID)
```

## Exceptions

| Exception | Description |
|-----------|-------------|
| `TypedUUIDError` | Base exception for all TypedUUID errors |
| `InvalidTypeIDError` | Raised when a type_id is invalid |
| `InvalidUUIDError` | Raised when a UUID value is invalid |

```python
from typed_uuid import create_typed_uuid_class, InvalidTypeIDError, InvalidUUIDError

try:
    create_typed_uuid_class('Invalid', 'too-long-type-id')
except InvalidTypeIDError as e:
    print(f"Invalid type ID: {e}")

UserUUID = create_typed_uuid_class('User', 'user')

try:
    UserUUID.from_string('not-a-valid-uuid')
except InvalidUUIDError as e:
    print(f"Invalid UUID: {e}")
```

## Thread Safety

TypedUUID is thread-safe. The class registry uses a lock to prevent race conditions when creating new TypedUUID classes from multiple threads.

```python
from concurrent.futures import ThreadPoolExecutor
from typed_uuid import create_typed_uuid_class

def create_user_uuid():
    # Safe to call from multiple threads
    UserUUID = create_typed_uuid_class('User', 'user')
    return UserUUID()

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(create_user_uuid) for _ in range(100)]
    results = [f.result() for f in futures]
```

## Registry

TypedUUID maintains a registry of all created classes, preventing duplicate type IDs:

```python
from typed_uuid import create_typed_uuid_class, TypedUUID

# Create a class
UserUUID = create_typed_uuid_class('User', 'user')

# Calling again with the same type_id returns the existing class
UserUUID2 = create_typed_uuid_class('User', 'user')
assert UserUUID is UserUUID2  # Same class

# Check registered types
TypedUUID.list_registered_types()  # ['user']
TypedUUID.is_type_registered('user')  # True
TypedUUID.get_class_by_type_id('user')  # UserUUID class
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
