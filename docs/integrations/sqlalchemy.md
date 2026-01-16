# SQLAlchemy Integration

TypedUUID integrates seamlessly with SQLAlchemy for database storage and retrieval.

## Installation

```bash
pip install typed-uuid[sqlalchemy]
```

## Basic Usage

### Column Type

Use `TypedUUIDType` for column definitions:

```python
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import declarative_base, Session
from typed_uuid import create_typed_uuid_class
from typed_uuid.adapters.sqlalchemy import TypedUUIDType

Base = declarative_base()

# Create your typed UUID class
UserUUID = create_typed_uuid_class('User', 'user')

class User(Base):
    __tablename__ = 'users'

    id = Column(TypedUUIDType('user'), primary_key=True, default=UserUUID)
    name = Column(String(100))
```

### Creating Records

```python
engine = create_engine('sqlite:///example.db')
Base.metadata.create_all(engine)

with Session(engine) as session:
    # Create with auto-generated ID
    user = User(id=UserUUID(), name='Alice')
    session.add(user)

    # Or let the default generate it
    user2 = User(name='Bob')  # id auto-generated
    session.add(user2)

    session.commit()
```

### Querying

```python
with Session(engine) as session:
    # Query by TypedUUID
    user_id = UserUUID.from_string('user-550e8400-e29b-41d4-a716-446655440000')
    user = session.query(User).filter(User.id == user_id).first()

    # Query returns TypedUUID instances
    all_users = session.query(User).all()
    for user in all_users:
        print(type(user.id))  # <class 'UserUUID'>
        print(user.id)        # user-550e8400-...
```

## Using create_typed_uuid_classes()

The utility function creates both UUID and SQLAlchemy types:

```python
from typed_uuid import create_typed_uuid_classes

# Returns tuple when SQLAlchemy is available
UserUUID, UserUUIDType = create_typed_uuid_classes('User', 'user')

class User(Base):
    __tablename__ = 'users'

    id = Column(UserUUIDType(), primary_key=True, default=UserUUID)
    name = Column(String(100))
```

## Type Safety

The SQLAlchemy type enforces type_id matching:

```python
UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

class User(Base):
    __tablename__ = 'users'
    id = Column(TypedUUIDType('user'), primary_key=True)

# This works
user = User(id=UserUUID())

# This raises ValueError - wrong type
user = User(id=OrderUUID())  # ValueError: Expected type_id user, got order
```

## Relationships

Use TypedUUIDs in foreign key relationships:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')

class User(Base):
    __tablename__ = 'users'

    id = Column(TypedUUIDType('user'), primary_key=True, default=UserUUID)
    name = Column(String(100))
    orders = relationship('Order', back_populates='user')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(TypedUUIDType('order'), primary_key=True, default=OrderUUID)
    user_id = Column(TypedUUIDType('user'), ForeignKey('users.id'))
    total = Column(String(20))
    user = relationship('User', back_populates='orders')
```

## Composite Values

TypedUUID works with SQLAlchemy composite values:

```python
user = User(id=UserUUID())

# Access composite values
values = user.id.__composite_values__()
print(values)  # ('user', UUID('550e8400-...'))
```

## Migration Considerations

### Column Size

The column stores the full typed UUID string:

```
user-550e8400-e29b-41d4-a716-446655440000
```

Column size is calculated as: `len(type_id) + 37` (hyphen + 36-char UUID).

### Alembic Migrations

```python
# In your Alembic migration
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(41), primary_key=True),  # user + hyphen + UUID
        sa.Column('name', sa.String(100))
    )
```

## Advanced Usage

### Custom Base Class

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Use with modern SQLAlchemy patterns
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = 'users'

    id: Mapped[UserUUID] = mapped_column(
        TypedUUIDType('user'),
        primary_key=True,
        default=UserUUID
    )
    name: Mapped[str] = mapped_column(String(100))
```

### Async SQLAlchemy

TypedUUID works with async SQLAlchemy:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine('postgresql+asyncpg://...')

async with AsyncSession(engine) as session:
    user = User(id=UserUUID(), name='Alice')
    session.add(user)
    await session.commit()
```

## Best Practices

### 1. Define IDs in a Central Module

```python
# app/ids.py
from typed_uuid import create_typed_uuid_classes

UserUUID, UserUUIDType = create_typed_uuid_classes('User', 'user')
OrderUUID, OrderUUIDType = create_typed_uuid_classes('Order', 'order')
ProductUUID, ProductUUIDType = create_typed_uuid_classes('Product', 'product')
```

### 2. Use Type Annotations

```python
from typing import Optional

class User(Base):
    __tablename__ = 'users'

    id: Mapped[UserUUID] = mapped_column(...)
    manager_id: Mapped[Optional[UserUUID]] = mapped_column(
        TypedUUIDType('user'),
        ForeignKey('users.id'),
        nullable=True
    )
```

### 3. Index Considerations

UUID columns can be indexed effectively:

```python
from sqlalchemy import Index

class Order(Base):
    __tablename__ = 'orders'

    id = Column(TypedUUIDType('order'), primary_key=True)
    user_id = Column(TypedUUIDType('user'), ForeignKey('users.id'), index=True)
```
