# Quick Start

This guide will get you up and running with TypedUUID in 5 minutes.

## Creating Your First TypedUUID

```python
from typed_uuid import create_typed_uuid_class

# Create a typed UUID class for users
UserUUID = create_typed_uuid_class('User', 'user')

# Generate a new user ID
user_id = UserUUID()
print(user_id)  # user-550e8400-e29b-41d4-a716-446655440000
```

That's it! You now have a type-safe UUID that clearly identifies what it represents.

## Understanding the Output

A TypedUUID consists of two parts:

```
user-550e8400-e29b-41d4-a716-446655440000
^^^^                                       <- Type prefix
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ <- Standard UUID
```

## Creating Multiple Types

Create different UUID types for different entities:

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')
ProductUUID = create_typed_uuid_class('Product', 'product')

# Each type is distinct
user_id = UserUUID()
order_id = OrderUUID()
product_id = ProductUUID()

print(user_id)     # user-...
print(order_id)    # order-...
print(product_id)  # product-...
```

## Parsing Existing UUIDs

Parse UUIDs from strings:

```python
# Parse a typed UUID string
user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')

# Or parse a plain UUID (type prefix will be added)
user_id = UserUUID('550e8400-e29b-41d4-a716-446655440000')
```

## Auto-Detecting Types

Let TypedUUID figure out the type automatically:

```python
from typed_uuid import TypedUUID

# TypedUUID.parse() detects the type from the string
user_id = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
order_id = TypedUUID.parse('order-550e8400-e29b-41d4-a716-446655440000')

print(type(user_id).__name__)   # UserUUID
print(type(order_id).__name__)  # OrderUUID
```

## Short Format for URLs

Get a compact, URL-friendly representation:

```python
user_id = UserUUID()

# Standard format
print(str(user_id))      # user-550e8400-e29b-41d4-a716-446655440000

# Short format (base62 encoded)
print(user_id.short)     # user_7n42DGM5Tflk9n8mt7Fhc7

# Parse back from short format
parsed = UserUUID.from_short('user_7n42DGM5Tflk9n8mt7Fhc7')
```

## Using with Functions

TypedUUIDs provide type safety in function signatures:

```python
def get_user(user_id: UserUUID) -> dict:
    """Fetch a user by their ID."""
    return {"id": str(user_id), "name": "Alice"}

def create_order(user_id: UserUUID, product_id: ProductUUID) -> OrderUUID:
    """Create an order for a user."""
    order_id = OrderUUID()
    # ... create order logic ...
    return order_id

# Clear what each function expects
user = get_user(user_id)
order = create_order(user_id, product_id)
```

## Comparing UUIDs

TypedUUIDs support equality and comparison:

```python
user1 = UserUUID('550e8400-e29b-41d4-a716-446655440000')
user2 = UserUUID('550e8400-e29b-41d4-a716-446655440000')
user3 = UserUUID()

# Equality
print(user1 == user2)  # True
print(user1 == user3)  # False

# Compare with strings
print(user1 == 'user-550e8400-e29b-41d4-a716-446655440000')  # True

# Use in sets and as dict keys
users = {user1, user2, user3}  # Set of 2 (user1 and user2 are equal)
user_data = {user1: "Alice"}   # Dict with UUID key
```

## JSON Serialization

TypedUUIDs serialize to JSON automatically:

```python
import json
from typed_uuid import TypedUUID

user_id = UserUUID()

# Use the json_default helper
data = {"user_id": user_id}
json_str = json.dumps(data, default=TypedUUID.json_default)
print(json_str)  # {"user_id": "user-550e8400-..."}
```

## Next Steps

Now that you understand the basics:

- [Core Concepts](../guide/concepts.md) - Deeper understanding of TypedUUID
- [Framework Integration](../integrations/sqlalchemy.md) - Use with SQLAlchemy, Pydantic, FastAPI
- [API Reference](../api/typeduuid.md) - Complete API documentation
