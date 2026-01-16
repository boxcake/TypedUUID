# Installation

## Requirements

- Python 3.10 or higher

## Basic Installation

Install TypedUUID using pip:

```bash
pip install typed-uuid
```

This installs the core library with no additional dependencies.

## Optional Dependencies

TypedUUID provides optional integrations with popular frameworks. Install them as needed:

### SQLAlchemy Support

For database integration with SQLAlchemy:

```bash
pip install typed-uuid[sqlalchemy]
```

This adds:

- `TypedUUIDType` - SQLAlchemy column type
- Automatic serialization/deserialization

### Pydantic Support

For data validation with Pydantic v2:

```bash
pip install typed-uuid[pydantic]
```

This adds:

- Pydantic model field support
- JSON schema generation
- Automatic validation

### FastAPI Support

For API development with FastAPI:

```bash
pip install typed-uuid[fastapi]
```

This adds:

- Path parameter support
- OpenAPI schema integration
- Automatic validation and documentation

### All Dependencies

Install all optional dependencies at once:

```bash
pip install typed-uuid[all]
```

## Development Installation

For contributing to TypedUUID:

```bash
git clone https://github.com/boxcake/TypedUUID.git
cd TypedUUID
pip install -e ".[all,dev]"
```

This installs:

- All optional dependencies
- pytest and pytest-cov for testing
- Development tools

## Verifying Installation

Verify the installation:

```python
>>> from typed_uuid import create_typed_uuid_class, TypedUUID
>>> UserUUID = create_typed_uuid_class('User', 'user')
>>> user_id = UserUUID()
>>> print(user_id)
user-550e8400-e29b-41d4-a716-446655440000
```

Check installed version:

```python
>>> import typed_uuid
>>> # Version is available in package metadata
```

## Upgrading

Upgrade to the latest version:

```bash
pip install --upgrade typed-uuid
```

## Compatibility

| Python Version | Support |
|----------------|---------|
| 3.10           | ✅      |
| 3.11           | ✅      |
| 3.12           | ✅      |
| 3.13           | ✅      |
| 3.9 and below  | ❌      |

!!! note "Python 3.9 Support"
    Python 3.9 and earlier are not supported due to Pydantic v2 compatibility requirements.
