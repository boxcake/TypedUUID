# Short Encoding

TypedUUID provides a compact, URL-friendly encoding using base62.

## Overview

The short format encodes the UUID portion using base62 (alphanumeric only):

```python
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
user_id = UserUUID('550e8400-e29b-41d4-a716-446655440000')

# Standard format (47 characters)
print(str(user_id))      # user-550e8400-e29b-41d4-a716-446655440000

# Short format (typically 26-28 characters)
print(user_id.short)     # user_7n42DGM5Tflk9n8mt7Fhc7
```

## Format Comparison

| Format | Example | Length | Use Case |
|--------|---------|--------|----------|
| Standard | `user-550e8400-e29b-41d4-a716-446655440000` | 41-52 chars | Databases, logs |
| Short | `user_7n42DGM5Tflk9n8mt7Fhc7` | 22-30 chars | URLs, APIs |

## Getting the Short Format

Use the `.short` property:

```python
user_id = UserUUID()

# Get short format
short = user_id.short
print(short)  # user_7n42DGM5Tflk9n8mt7Fhc7
```

### Short Format Structure

```
user_7n42DGM5Tflk9n8mt7Fhc7
│    └────────────────────┘
│             │
│        Base62-encoded UUID
│
└── Type identifier (same as standard format)
```

Note: Short format uses underscore (`_`) as separator, while standard uses hyphen (`-`).

## Parsing Short Format

### Using from_short()

Parse a short-format string back to a TypedUUID:

```python
# From short format
user_id = UserUUID.from_short('user_7n42DGM5Tflk9n8mt7Fhc7')

print(user_id)  # user-550e8400-e29b-41d4-a716-446655440000
```

### Roundtrip Example

```python
# Create original
original = UserUUID()
print(f"Original: {original}")

# Get short format
short = original.short
print(f"Short: {short}")

# Parse back
restored = UserUUID.from_short(short)
print(f"Restored: {restored}")

# Verify equality
print(f"Equal: {original == restored}")  # True
```

## Auto-Detection

`TypedUUID.parse()` automatically detects the format:

```python
from typed_uuid import TypedUUID

# Both work with parse()
uuid1 = TypedUUID.parse('user-550e8400-e29b-41d4-a716-446655440000')
uuid2 = TypedUUID.parse('user_7n42DGM5Tflk9n8mt7Fhc7')

print(uuid1 == uuid2)  # True (if same underlying UUID)
```

## Base62 Encoding

### Character Set

Base62 uses these 62 characters:

```
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

This makes short UUIDs:

- URL-safe (no special characters)
- Case-sensitive
- Alphanumeric only

### Length Variation

The encoded length varies slightly based on the UUID value:

```python
# Minimum value UUID
min_uuid = UserUUID('00000000-0000-0000-0000-000000000000')
print(min_uuid.short)  # user_0

# Maximum value UUID
max_uuid = UserUUID('ffffffff-ffff-ffff-ffff-ffffffffffff')
print(max_uuid.short)  # user_7n42DGM5Tflk9n8mt7Fhc7 (22 chars)

# Typical UUID
typical = UserUUID()
print(len(typical.short))  # Usually 22-27 characters total
```

## Use Cases

### URL-Friendly IDs

```python
# API endpoints
user_id = UserUUID()
url = f"/api/users/{user_id.short}"
# /api/users/user_7n42DGM5Tflk9n8mt7Fhc7

# Query parameters
url = f"/search?user={user_id.short}"
```

### Short Links

```python
# Generate short link
document_id = DocumentUUID()
short_link = f"https://example.com/d/{document_id.short}"
# https://example.com/d/doc_3K5mNpQrStUvWxYz
```

### QR Codes

Shorter strings make smaller QR codes:

```python
# More efficient for QR encoding
order_id = OrderUUID()
qr_data = order_id.short  # Fewer characters = smaller QR
```

## Error Handling

```python
from typed_uuid import InvalidUUIDError

try:
    # Invalid base62 characters
    user_id = UserUUID.from_short('user_invalid!@#')
except InvalidUUIDError as e:
    print(f"Invalid short format: {e}")

try:
    # Wrong type prefix
    user_id = UserUUID.from_short('order_7n42DGM5Tflk9n8mt7Fhc7')
except InvalidUUIDError as e:
    print(f"Type mismatch: {e}")
```

## Best Practices

### 1. Use Short Format for External-Facing IDs

```python
# In your API response
return {
    "id": user_id.short,  # Cleaner for clients
    "name": user.name
}
```

### 2. Store Standard Format in Database

```python
# Database stores full format for compatibility
db.execute(
    "INSERT INTO users (id, name) VALUES (?, ?)",
    (str(user_id), name)  # Standard format
)
```

### 3. Accept Both Formats in API

```python
def get_user(id_param: str):
    """Accept both short and standard format."""
    try:
        # Try short format first
        if '_' in id_param:
            return UserUUID.from_short(id_param)
        else:
            return UserUUID.from_string(id_param)
    except InvalidUUIDError:
        raise ValueError(f"Invalid user ID: {id_param}")
```

Or use auto-detection:

```python
def get_user(id_param: str):
    """Use parse() for automatic format detection."""
    return TypedUUID.parse(id_param)
```
