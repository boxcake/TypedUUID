# TypedUUID Roadmap

This document outlines planned features for future releases.

## Planned Features

### UUID7 Support
**Status**: Planned
**Priority**: High

UUID7 provides time-ordered UUIDs that are better suited for database primary keys due to improved index locality. The timestamp is encoded in the first 48 bits.

```python
# Planned API
user_id = UserUUID.generate_v7()  # Time-ordered UUID

# Extract creation timestamp
created_at = user_id.timestamp  # datetime object
```

**Implementation Notes**:
- UUID7 is not in Python's standard library (proposed for Python 3.14)
- Will use `uuid7` or `uuid-utils` package as optional dependency
- Graceful degradation: clear error if package not installed

### Timestamp Extraction
**Status**: Planned (alongside UUID7)
**Priority**: High

Extract creation timestamp from UUID1 and UUID7 without database queries.

```python
# For UUID7
user_id = UserUUID.generate_v7()
print(user_id.timestamp)  # 2024-01-15 10:30:00+00:00

# For UUID1
user_id = UserUUID.generate_v1()
print(user_id.timestamp)  # 2024-01-15 10:30:00+00:00

# Returns None for UUID4 (no timestamp)
user_id = UserUUID()
print(user_id.timestamp)  # None
```

### Namespace UUIDs (UUID5)
**Status**: Planned
**Priority**: Medium

Generate deterministic UUIDs from names. Same input always produces the same UUID.

```python
# Planned API - each type has its own derived namespace
user_id = UserUUID.from_name("alice@example.com")
user_id2 = UserUUID.from_name("alice@example.com")
assert user_id == user_id2  # Always the same!

# Different types produce different UUIDs for same name
order_id = OrderUUID.from_name("alice@example.com")
assert user_id != order_id  # Different namespaces

# Explicit namespace override
user_id = UserUUID.from_name("alice@example.com", namespace=uuid.NAMESPACE_DNS)
```

**Use Cases**:
- Idempotent data imports (re-import produces same IDs)
- Distributed systems (generate matching IDs without coordination)
- URL-to-ID mapping
- Deduplication

## Completed Features

### v1.1.0
- [x] `__slots__` for memory efficiency
- [x] Short encoding/decoding (base62): `user_2n9cJxL4`
- [x] Pickle support
- [x] Auto-parsing: `TypedUUID.parse("user-...")` returns correct subclass

### v1.0.0
- [x] Core TypedUUID implementation
- [x] SQLAlchemy adapter
- [x] Pydantic v2 adapter
- [x] FastAPI adapter
- [x] Thread safety
- [x] Full comparison and hashing support
- [x] JSON serialization

## Future Considerations

These features may be added based on community interest:

- **GraphQL scalar type** - Custom scalar for GraphQL APIs
- **Marshmallow adapter** - Serialization library support
- **Click/Typer integration** - CLI argument parsing
- **ULID compatibility** - Interop with ULID format

## Contributing

Feature requests and pull requests are welcome! Please open an issue to discuss new features before implementing.
