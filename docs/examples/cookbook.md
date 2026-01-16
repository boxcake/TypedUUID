# Cookbook

Practical recipes for common TypedUUID use cases.

## Basic Recipes

### Creating a Set of Related ID Types

```python
from typed_uuid import create_typed_uuid_class

# E-commerce domain
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')
ProductUUID = create_typed_uuid_class('Product', 'product')
CartUUID = create_typed_uuid_class('Cart', 'cart')
PaymentUUID = create_typed_uuid_class('Payment', 'payment')

# Content management domain
ArticleUUID = create_typed_uuid_class('Article', 'article')
AuthorUUID = create_typed_uuid_class('Author', 'author')
CommentUUID = create_typed_uuid_class('Comment', 'comment')
TagUUID = create_typed_uuid_class('Tag', 'tag')
```

### ID Factory Function

```python
from typed_uuid import create_typed_uuid_class

def create_id_types(*names):
    """Create multiple ID types at once."""
    types = {}
    for name in names:
        type_id = name.lower()
        types[f'{name}UUID'] = create_typed_uuid_class(name, type_id)
    return types

# Usage
ids = create_id_types('User', 'Order', 'Product')
UserUUID = ids['UserUUID']
OrderUUID = ids['OrderUUID']
```

### Safe ID Parsing

```python
from typed_uuid import TypedUUID, InvalidUUIDError, InvalidTypeIDError
from typing import Optional

def safe_parse(value: str, expected_type=None) -> Optional[TypedUUID]:
    """Safely parse a UUID string, returning None on failure."""
    try:
        parsed = TypedUUID.parse(value)
        if expected_type and not isinstance(parsed, expected_type):
            return None
        return parsed
    except (InvalidUUIDError, InvalidTypeIDError):
        return None

# Usage
user_id = safe_parse('user-550e8400-e29b-41d4-a716-446655440000', UserUUID)
if user_id:
    print(f"Valid user ID: {user_id}")
else:
    print("Invalid or wrong type")
```

## Web Application Recipes

### Flask Route with TypedUUID

```python
from flask import Flask, jsonify, abort
from typed_uuid import create_typed_uuid_class, InvalidUUIDError

app = Flask(__name__)
UserUUID = create_typed_uuid_class('User', 'user')

@app.route('/users/<user_id>')
def get_user(user_id: str):
    try:
        parsed_id = UserUUID.from_string(user_id)
    except InvalidUUIDError:
        abort(400, description="Invalid user ID")

    # Fetch user from database
    user = db.get_user(parsed_id)
    if not user:
        abort(404, description="User not found")

    return jsonify({
        'id': str(user.id),
        'name': user.name
    })
```

### Django Model with TypedUUID

```python
from django.db import models
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

class User(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(UserUUID())
        super().save(*args, **kwargs)

    @property
    def typed_id(self):
        return UserUUID.from_string(self.id)
```

### GraphQL Resolver

```python
import strawberry
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

@strawberry.type
class User:
    id: str
    name: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: str) -> User:
        user_id = UserUUID.from_string(id)
        # Fetch and return user
        return User(id=str(user_id), name="Alice")
```

## Database Recipes

### Bulk Insert with TypedUUIDs

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

def bulk_create_users(names: list[str]):
    """Create multiple users with generated IDs."""
    users = [
        {'id': str(UserUUID()), 'name': name}
        for name in names
    ]

    cursor.executemany(
        "INSERT INTO users (id, name) VALUES (%(id)s, %(name)s)",
        users
    )
    return users
```

### Migration from Plain UUIDs

```python
from uuid import UUID
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

def migrate_user_ids():
    """Migrate existing plain UUIDs to TypedUUIDs."""
    cursor.execute("SELECT id FROM users_old")

    for row in cursor.fetchall():
        old_id = row[0]  # Plain UUID string
        new_id = UserUUID(old_id)  # Wrap in TypedUUID

        cursor.execute(
            "UPDATE users SET id = %s WHERE id = %s",
            (str(new_id), old_id)
        )
```

## Serialization Recipes

### Custom JSON Encoder

```python
import json
from typing import Any
from typed_uuid import TypedUUID

class AppJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles TypedUUIDs and other custom types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, TypedUUID):
            return obj.short  # Use short format for APIs
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return super().default(obj)

# Usage
data = {'user_id': UserUUID(), 'timestamp': '2024-01-15'}
json.dumps(data, cls=AppJSONEncoder)
```

### Dataclass with TypedUUID

```python
from dataclasses import dataclass, field
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

@dataclass
class User:
    name: str
    email: str
    id: UserUUID = field(default_factory=UserUUID)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email
        }

user = User(name='Alice', email='alice@example.com')
print(user.id)  # user-550e8400-...
```

## Testing Recipes

### Fixture for TypedUUIDs

```python
import pytest
from typed_uuid import create_typed_uuid_class

@pytest.fixture
def user_uuid_class():
    return create_typed_uuid_class('User', 'testuser')

@pytest.fixture
def sample_user_id(user_uuid_class):
    return user_uuid_class('550e8400-e29b-41d4-a716-446655440000')

def test_user_creation(sample_user_id):
    assert str(sample_user_id) == 'testuser-550e8400-e29b-41d4-a716-446655440000'
```

### Mocking TypedUUIDs

```python
from unittest.mock import patch
from uuid import UUID

def test_with_predictable_uuid():
    fixed_uuid = UUID('550e8400-e29b-41d4-a716-446655440000')

    with patch('uuid.uuid4', return_value=fixed_uuid):
        user_id = UserUUID()
        assert str(user_id) == 'user-550e8400-e29b-41d4-a716-446655440000'
```

### Parameterized Tests

```python
import pytest
from typed_uuid import create_typed_uuid_class, InvalidUUIDError

UserUUID = create_typed_uuid_class('User', 'user')

@pytest.mark.parametrize("input_str,should_succeed", [
    ('user-550e8400-e29b-41d4-a716-446655440000', True),
    ('550e8400-e29b-41d4-a716-446655440000', True),
    ('USER-550e8400-e29b-41d4-a716-446655440000', False),  # Case sensitive
    ('invalid', False),
    ('', False),
])
def test_parsing(input_str, should_succeed):
    if should_succeed:
        result = UserUUID.from_string(input_str)
        assert isinstance(result, UserUUID)
    else:
        with pytest.raises((InvalidUUIDError, Exception)):
            UserUUID.from_string(input_str)
```

## Logging Recipes

### Structured Logging

```python
import logging
import json
from typed_uuid import TypedUUID

class TypedUUIDLogFormatter(logging.Formatter):
    def format(self, record):
        # Convert any TypedUUIDs in the message to strings
        if hasattr(record, 'user_id') and isinstance(record.user_id, TypedUUID):
            record.user_id = str(record.user_id)
        return super().format(record)

# Usage
logger = logging.getLogger(__name__)
logger.info("User logged in", extra={'user_id': user_id})
```

### Request Context

```python
from contextvars import ContextVar
from typed_uuid import TypedUUID

request_id_var: ContextVar[TypedUUID] = ContextVar('request_id')

def set_request_id():
    RequestUUID = create_typed_uuid_class('Request', 'req')
    request_id_var.set(RequestUUID())

def get_request_id() -> str:
    return str(request_id_var.get())
```
