# Adapters

Framework integration adapters for TypedUUID.

## SQLAlchemy Adapter

### TypedUUIDType

SQLAlchemy column type for storing TypedUUIDs.

```python
from typed_uuid.adapters.sqlalchemy import TypedUUIDType
```

#### Usage

```python
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from typed_uuid import create_typed_uuid_class
from typed_uuid.adapters.sqlalchemy import TypedUUIDType

Base = declarative_base()
UserUUID = create_typed_uuid_class('User', 'user')

class User(Base):
    __tablename__ = 'users'

    id = Column(TypedUUIDType('user'), primary_key=True, default=UserUUID)
    name = Column(String(100))
```

#### Constructor

```python
TypedUUIDType(type_id: str)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `type_id` | `str` | The type identifier to use |

#### Methods

| Method | Description |
|--------|-------------|
| `process_bind_param(value, dialect)` | Convert TypedUUID to string for database |
| `process_result_value(value, dialect)` | Convert string from database to TypedUUID |

### create_typed_uuid_type

Create a pre-configured SQLAlchemy type for a specific type_id.

```python
from typed_uuid.adapters.sqlalchemy import create_typed_uuid_type

UserUUIDType = create_typed_uuid_type('user')
```

---

## Pydantic Adapter

### add_pydantic_methods

Adds Pydantic v2 support methods to a TypedUUID class.

```python
from typed_uuid.adapters.pydantic import add_pydantic_methods
```

!!! note "Automatic Application"
    This is called automatically by `create_typed_uuid_class()` when Pydantic is installed.

#### Added Methods

| Method | Description |
|--------|-------------|
| `__get_pydantic_core_schema__` | Returns Pydantic core schema |
| `__get_pydantic_json_schema__` | Returns JSON schema for OpenAPI |
| `validate_json` | Validates JSON string input |
| `model_dump` | Serializes to string |
| `__json__` | JSON serialization support |

#### Usage in Models

```python
from pydantic import BaseModel
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

class User(BaseModel):
    id: UserUUID
    name: str

# Automatic validation
user = User(id='user-550e8400-e29b-41d4-a716-446655440000', name='Alice')

# Automatic serialization
print(user.model_dump_json())
# {"id": "user-550e8400-...", "name": "Alice"}
```

### PYDANTIC_AVAILABLE

Boolean flag indicating if Pydantic is installed.

```python
from typed_uuid.adapters.pydantic import PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    # Use Pydantic features
    pass
```

---

## FastAPI Adapter

### add_fastapi_methods

Adds FastAPI support methods to a TypedUUID class.

```python
from typed_uuid.adapters.fastapi import add_fastapi_methods
```

!!! note "Automatic Application"
    This is called automatically by `create_typed_uuid_class()` when FastAPI is installed.

#### Added Methods

| Method | Description |
|--------|-------------|
| `path_param(description=None)` | Creates FastAPI path parameter type |

### path_param()

Creates an annotated type for FastAPI path parameters.

```python
UserUUID.path_param(description: str = None) -> Annotated[UserUUID, Path]
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | `str` | Optional description for OpenAPI docs |

#### Returns

An `Annotated` type suitable for FastAPI path parameter declaration.

#### Usage

```python
from fastapi import FastAPI
from typed_uuid import create_typed_uuid_class

app = FastAPI()
UserUUID = create_typed_uuid_class('User', 'user')

@app.get("/users/{user_id}")
async def get_user(user_id: UserUUID.path_param(description="The user ID")):
    return {"user_id": str(user_id)}
```

### FASTAPI_AVAILABLE

Boolean flag indicating if FastAPI is installed.

```python
from typed_uuid.adapters.fastapi import FASTAPI_AVAILABLE

if FASTAPI_AVAILABLE:
    # Use FastAPI features
    pass
```

---

## Checking Adapter Availability

### At Import Time

```python
from typed_uuid.adapters.sqlalchemy import SQLALCHEMY_AVAILABLE
from typed_uuid.adapters.pydantic import PYDANTIC_AVAILABLE
from typed_uuid.adapters.fastapi import FASTAPI_AVAILABLE

print(f"SQLAlchemy: {SQLALCHEMY_AVAILABLE}")
print(f"Pydantic: {PYDANTIC_AVAILABLE}")
print(f"FastAPI: {FASTAPI_AVAILABLE}")
```

### From TypedUUID Class

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

# Check what methods are available
has_pydantic = hasattr(UserUUID, '__get_pydantic_core_schema__')
has_fastapi = callable(getattr(UserUUID, 'path_param', None))
```

---

## Manual Adapter Application

If you need to manually apply adapters:

```python
from typed_uuid import create_typed_uuid_class

# Create without automatic adapters
UserUUID = create_typed_uuid_class('User', 'user')

# Manually add specific adapter
from typed_uuid.adapters.pydantic import add_pydantic_methods, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    add_pydantic_methods(UserUUID)
```

!!! warning "Automatic Application"
    Adapters are automatically applied when you use `create_typed_uuid_class()`.
    Manual application is only needed in special cases.
