# Pydantic Integration

TypedUUID integrates with Pydantic v2 for data validation and serialization.

## Installation

```bash
pip install typed-uuid[pydantic]
```

## Basic Usage

### In Pydantic Models

Use TypedUUID directly as a field type:

```python
from pydantic import BaseModel
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

class User(BaseModel):
    id: UserUUID
    name: str
    email: str
```

### Creating Model Instances

```python
# From TypedUUID instance
user_id = UserUUID()
user = User(id=user_id, name='Alice', email='alice@example.com')

# From string (auto-validated)
user = User(
    id='user-550e8400-e29b-41d4-a716-446655440000',
    name='Alice',
    email='alice@example.com'
)

# From plain UUID string
user = User(
    id='550e8400-e29b-41d4-a716-446655440000',
    name='Alice',
    email='alice@example.com'
)
```

### Validation

Pydantic automatically validates TypedUUID fields:

```python
from pydantic import ValidationError

try:
    user = User(
        id='not-a-valid-uuid',
        name='Alice',
        email='alice@example.com'
    )
except ValidationError as e:
    print(e)
    # validation error for id
```

Type mismatches are caught:

```python
OrderUUID = create_typed_uuid_class('Order', 'order')

class Order(BaseModel):
    id: OrderUUID
    user_id: UserUUID

try:
    # Wrong type for user_id
    order = Order(
        id='order-123e4567-e89b-12d3-a456-426614174000',
        user_id='order-123e4567-e89b-12d3-a456-426614174000'  # Should be 'user-...'
    )
except ValidationError as e:
    print(e)  # Type mismatch error
```

## Serialization

### JSON Output

TypedUUIDs serialize to strings in JSON:

```python
user = User(id=UserUUID(), name='Alice', email='alice@example.com')

# model_dump() returns dict with string ID
data = user.model_dump()
print(data)
# {'id': 'user-550e8400-...', 'name': 'Alice', 'email': 'alice@example.com'}

# model_dump_json() returns JSON string
json_str = user.model_dump_json()
print(json_str)
# {"id": "user-550e8400-...", "name": "Alice", "email": "alice@example.com"}
```

### Instance Serialization

TypedUUID instances have a `model_dump()` method:

```python
user_id = UserUUID()
print(user_id.model_dump())  # 'user-550e8400-...'
```

## JSON Schema

TypedUUID generates proper JSON schemas:

```python
schema = User.model_json_schema()
print(schema['properties']['id'])
# {
#     'type': 'string',
#     'format': 'typed-uuid',
#     'pattern': '^[a-zA-Z0-9]+-[0-9a-f]{8}-...'
# }
```

This is useful for:

- OpenAPI documentation
- Client SDK generation
- Form validation

## Optional Fields

Use `Optional` for nullable fields:

```python
from typing import Optional

class User(BaseModel):
    id: UserUUID
    manager_id: Optional[UserUUID] = None
    name: str

# manager_id can be None or a valid UserUUID
user = User(id=UserUUID(), name='Alice')  # manager_id defaults to None
user = User(id=UserUUID(), manager_id=UserUUID(), name='Alice')
```

## Lists and Collections

TypedUUIDs work in collections:

```python
from typing import List

class Team(BaseModel):
    id: TeamUUID
    name: str
    member_ids: List[UserUUID]

team = Team(
    id=TeamUUID(),
    name='Engineering',
    member_ids=[UserUUID(), UserUUID(), UserUUID()]
)
```

## Nested Models

Use TypedUUIDs in nested models:

```python
class Address(BaseModel):
    id: AddressUUID
    street: str
    city: str

class User(BaseModel):
    id: UserUUID
    name: str
    addresses: List[Address]

user = User(
    id=UserUUID(),
    name='Alice',
    addresses=[
        Address(id=AddressUUID(), street='123 Main St', city='Boston'),
        Address(id=AddressUUID(), street='456 Oak Ave', city='Cambridge')
    ]
)
```

## Custom Validation

Add additional validation with Pydantic validators:

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    id: UserUUID
    name: str

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        # Custom validation logic
        if isinstance(v, str) and v.startswith('admin-'):
            raise ValueError('Admin IDs not allowed in User model')
        return v
```

## Using validate_json()

TypedUUID classes have a `validate_json()` method:

```python
# Validate a JSON string directly
user_id = UserUUID.validate_json('user-550e8400-e29b-41d4-a716-446655440000')
print(type(user_id))  # UserUUID
```

## Best Practices

### 1. Type All ID Fields

```python
# Good: All IDs are typed
class Order(BaseModel):
    id: OrderUUID
    user_id: UserUUID
    product_ids: List[ProductUUID]

# Avoid: Using plain strings for IDs
class Order(BaseModel):
    id: str  # No type safety
    user_id: str
    product_ids: List[str]
```

### 2. Use Strict Mode When Needed

```python
from pydantic import ConfigDict

class StrictUser(BaseModel):
    model_config = ConfigDict(strict=True)

    id: UserUUID
    name: str

# Strict mode requires exact types
```

### 3. Document Expected Formats

```python
from pydantic import Field

class User(BaseModel):
    id: UserUUID = Field(
        description="User identifier in format 'user-{uuid}'",
        examples=['user-550e8400-e29b-41d4-a716-446655440000']
    )
    name: str
```

## Compatibility Notes

- Requires Pydantic v2.0 or higher
- Pydantic v1 is not supported
- Works with pydantic-settings for configuration management
