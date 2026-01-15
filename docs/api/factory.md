# Factory Functions

Functions for creating TypedUUID classes.

## create_typed_uuid_class

The primary factory function for creating TypedUUID subclasses.

::: typed_uuid.core.create_typed_uuid_class
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Usage

```python
from typed_uuid import create_typed_uuid_class

# Create a new TypedUUID class
UserUUID = create_typed_uuid_class('User', 'user')

# The class name includes 'UUID' suffix
print(UserUUID.__name__)  # 'UserUUID'

# Create instances
user_id = UserUUID()
print(user_id)  # 'user-550e8400-e29b-41d4-a716-446655440000'
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `class_name` | `str` | Base name for the class (becomes `{name}UUID`) |
| `type_id` | `str` | Type identifier prefix for UUID strings |

### Returns

A new TypedUUID subclass with the specified type_id.

### Thread Safety

This function is thread-safe. Multiple threads can safely create classes concurrently.

### Registry Behavior

If a class with the same `type_id` already exists, the existing class is returned:

```python
UserUUID1 = create_typed_uuid_class('User', 'user')
UserUUID2 = create_typed_uuid_class('User', 'user')

print(UserUUID1 is UserUUID2)  # True
```

---

## create_typed_uuid_classes

Utility function that creates both a TypedUUID class and its SQLAlchemy type.

::: typed_uuid.utils.create_typed_uuid_classes
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Usage

```python
from typed_uuid import create_typed_uuid_classes

# Returns tuple when SQLAlchemy is available
UserUUID, UserUUIDType = create_typed_uuid_classes('User', 'user')

# Use in SQLAlchemy models
class User(Base):
    id = Column(UserUUIDType(), primary_key=True, default=UserUUID)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Base name for the classes |
| `type_id` | `str` | Type identifier prefix |

### Returns

- **With SQLAlchemy**: `Tuple[Type[TypedUUID], Type[TypedUUIDType]]`
- **Without SQLAlchemy**: `Type[TypedUUID]`

### Behavior

This function:

1. Creates a TypedUUID class using `create_typed_uuid_class()`
2. Adds FastAPI methods if FastAPI is available
3. Creates a SQLAlchemy TypedUUIDType if SQLAlchemy is available
4. Returns a tuple or single class depending on available dependencies

---

## _reconstruct_typed_uuid

Internal helper for pickle support.

::: typed_uuid.core._reconstruct_typed_uuid
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

!!! note "Internal Function"
    This function is used internally for pickle serialization and should not be called directly.

---

## Best Practices

### Define Classes at Module Level

```python
# ids.py - Define all your ID types here
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')
ProductUUID = create_typed_uuid_class('Product', 'product')
```

### Use Consistent Naming

```python
# Good: Consistent lowercase type_ids
create_typed_uuid_class('User', 'user')
create_typed_uuid_class('Order', 'order')

# Good: Consistent abbreviated type_ids
create_typed_uuid_class('User', 'usr')
create_typed_uuid_class('Order', 'ord')

# Avoid: Mixed conventions
create_typed_uuid_class('User', 'user')
create_typed_uuid_class('Order', 'ORD')  # Inconsistent
```

### Handle Optional Dependencies

```python
from typed_uuid import create_typed_uuid_classes

result = create_typed_uuid_classes('User', 'user')

# Check if SQLAlchemy type was created
if isinstance(result, tuple):
    UserUUID, UserUUIDType = result
else:
    UserUUID = result
    UserUUIDType = None  # SQLAlchemy not available
```
