# Serialization

This guide covers how to serialize TypedUUIDs for storage, transmission, and interchange.

## String Serialization

### Standard String Format

The most common serialization is the string format:

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID()

# Serialize to string
serialized = str(user_id)
print(serialized)  # user-550e8400-e29b-41d4-a716-446655440000

# Deserialize from string
restored = UserUUID.from_string(serialized)
```

### Short String Format

For more compact serialization:

```python
# Serialize to short format
serialized = user_id.short
print(serialized)  # user_7n42DGM5Tflk9n8mt7Fhc7

# Deserialize from short format
restored = UserUUID.from_short(serialized)
```

## JSON Serialization

### Using json.dumps()

TypedUUID provides a `json_default` helper:

```python
import json
from typed_uuid import TypedUUID

user_id = UserUUID()
data = {
    "user_id": user_id,
    "name": "Alice"
}

# Serialize with json_default
json_str = json.dumps(data, default=TypedUUID.json_default)
print(json_str)  # {"user_id": "user-550e8400-...", "name": "Alice"}
```

### Custom JSON Encoder

Create a reusable encoder:

```python
import json
from typed_uuid import TypedUUID

class TypedUUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TypedUUID):
            return str(obj)
        return super().default(obj)

# Usage
json_str = json.dumps(data, cls=TypedUUIDEncoder)
```

### Using __json__ Method

TypedUUID instances have a `__json__` method:

```python
user_id = UserUUID()
print(user_id.__json__())  # user-550e8400-e29b-41d4-a716-446655440000
```

This is used automatically by some frameworks.

## Pickle Serialization

TypedUUID fully supports pickle:

```python
import pickle

user_id = UserUUID()

# Serialize
pickled = pickle.dumps(user_id)

# Deserialize
restored = pickle.loads(pickled)

print(user_id == restored)  # True
print(type(restored).__name__)  # UserUUID
```

### Pickle Protocol Support

All pickle protocols are supported:

```python
import pickle

user_id = UserUUID()

# Test different protocols
for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
    pickled = pickle.dumps(user_id, protocol=protocol)
    restored = pickle.loads(pickled)
    assert user_id == restored
```

### Pickling with Dynamically Created Classes

TypedUUID handles pickle correctly even for dynamically created classes:

```python
# This works correctly
UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID()

pickled = pickle.dumps(user_id)
restored = pickle.loads(pickled)

# The restored object is the correct type
assert isinstance(restored, UserUUID)
```

## Bytes Serialization

Get the raw bytes of the UUID:

```python
user_id = UserUUID()

# Get 16-byte representation
uuid_bytes = bytes(user_id)
print(len(uuid_bytes))  # 16
print(uuid_bytes)  # b'\x55\x0e\x84\x00...'

# Reconstruct from bytes
from uuid import UUID
restored_uuid = UUID(bytes=uuid_bytes)
restored = UserUUID(restored_uuid)
```

## Database Serialization

### For String Columns

Store as string:

```python
# Save
cursor.execute(
    "INSERT INTO users (id) VALUES (?)",
    (str(user_id),)
)

# Load
cursor.execute("SELECT id FROM users WHERE ...")
row = cursor.fetchone()
user_id = UserUUID.from_string(row[0])
```

### For Binary Columns

Store as bytes:

```python
# Save
cursor.execute(
    "INSERT INTO users (id) VALUES (?)",
    (bytes(user_id),)
)

# Load
cursor.execute("SELECT id FROM users WHERE ...")
row = cursor.fetchone()
uuid_obj = UUID(bytes=row[0])
user_id = UserUUID(uuid_obj)
```

### With SQLAlchemy

See [SQLAlchemy Integration](../integrations/sqlalchemy.md) for the recommended approach.

## API Response Serialization

### Flask/Django Pattern

```python
def serialize_user(user) -> dict:
    """Serialize user for API response."""
    return {
        "id": str(user.id),  # or user.id.short for compact
        "name": user.name,
        "email": user.email
    }
```

### FastAPI/Pydantic Pattern

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: UserUUID
    name: str

# Automatic serialization handled by Pydantic
```

See [Pydantic Integration](../integrations/pydantic.md) for details.

## State Serialization

### __getstate__ and __setstate__

TypedUUID implements these for custom serialization:

```python
user_id = UserUUID()

# Get state
state = user_id.__getstate__()
print(state)  # {'type_id': 'user', 'uuid': '550e8400-...'}

# Restore state
new_instance = UserUUID.__new__(UserUUID)
new_instance.__setstate__(state)
print(new_instance == user_id)  # True
```

This is primarily used internally by pickle but can be useful for custom serialization.

## Serialization Comparison

| Method | Output | Size | Use Case |
|--------|--------|------|----------|
| `str()` | `user-550e8400-...` | ~45 chars | General purpose |
| `.short` | `user_7n42DGM...` | ~25 chars | URLs, APIs |
| `bytes()` | Binary | 16 bytes | Binary storage |
| `pickle` | Binary | ~100 bytes | Python-to-Python |
| JSON | String in JSON | ~50 chars | Web APIs |

## Best Practices

### 1. Choose Format Based on Context

```python
# For databases and logs: standard format
db_value = str(user_id)

# For URLs and user-facing: short format
url_value = user_id.short

# For binary protocols: bytes
binary_value = bytes(user_id)
```

### 2. Document Your Serialization Choice

```python
class UserAPI:
    """
    User ID Formats:
    - Database: Standard format (user-550e8400-...)
    - API responses: Short format (user_7n42DGM...)
    - Internal: TypedUUID objects
    """
    pass
```

### 3. Be Consistent Within a System

```python
# Pick one format for your API and stick with it
class Config:
    USE_SHORT_IDS = True

def serialize_id(typed_uuid):
    if Config.USE_SHORT_IDS:
        return typed_uuid.short
    return str(typed_uuid)
```
