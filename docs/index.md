# TypedUUID

**Type-safe UUID management with prefix identification for Python**

[![CI](https://github.com/boxcake/TypedUUID/actions/workflows/ci.yml/badge.svg)](https://github.com/boxcake/TypedUUID/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/typed-uuid.svg)](https://badge.fury.io/py/typed-uuid)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

TypedUUID enhances standard UUIDs by adding a type prefix, making it easy to identify what kind of entity a UUID represents at a glance.

```python
from typed_uuid import create_typed_uuid_class

# Create typed UUID classes
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# Generate new IDs
user_id = UserUUID()
print(user_id)  # user-550e8400-e29b-41d4-a716-446655440000

# Parse existing IDs
parsed = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')
```

## Why TypedUUID?

Working with multiple UUIDs in a codebase can be confusing:

```python
# Without TypedUUID - which ID is which?
def process_order(user_id, order_id, product_id):
    # Easy to mix these up!
    pass

# With TypedUUID - self-documenting and type-safe
def process_order(user_id: UserUUID, order_id: OrderUUID, product_id: ProductUUID):
    # Clear what each parameter expects
    pass
```

## Features

- **Type-safe UUIDs** - Prefix UUIDs with a type identifier
- **Human-readable** - Instantly identify what type of entity a UUID belongs to
- **Thread-safe** - Safe for use in multi-threaded applications
- **Framework integrations** - Built-in support for SQLAlchemy, Pydantic, and FastAPI
- **Short encoding** - Compact base62 format for URLs
- **Zero hard dependencies** - Core library works standalone

## Quick Example

```python
from typed_uuid import create_typed_uuid_class, TypedUUID

# Create typed UUID classes for your domain
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

# Generate new UUIDs
user_id = UserUUID()
order_id = OrderUUID()

print(f"User: {user_id}")   # user-a1b2c3d4-...
print(f"Order: {order_id}") # order-e5f6g7h8-...

# Short format for URLs
print(user_id.short)  # user_7n42DGM5Tflk9n8mt7Fhc7

# Auto-detect type when parsing
parsed = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
print(type(parsed).__name__)  # UserUUID
```

## Installation

```bash
pip install typed-uuid
```

With framework support:

```bash
pip install typed-uuid[sqlalchemy]
pip install typed-uuid[pydantic]
pip install typed-uuid[fastapi]
pip install typed-uuid[all]
```

## Next Steps

- [Installation](getting-started/installation.md) - Detailed installation options
- [Quick Start](getting-started/quickstart.md) - Get up and running in 5 minutes
- [User Guide](guide/concepts.md) - Learn the core concepts
- [API Reference](api/typeduuid.md) - Complete API documentation
