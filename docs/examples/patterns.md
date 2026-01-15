# Real-World Patterns

Design patterns and architectural approaches using TypedUUID.

## Domain-Driven Design

### Entity Base Class

```python
from abc import ABC
from typing import TypeVar, Generic
from typed_uuid import TypedUUID

T = TypeVar('T', bound=TypedUUID)

class Entity(ABC, Generic[T]):
    """Base class for domain entities with typed IDs."""

    def __init__(self, id: T):
        self._id = id

    @property
    def id(self) -> T:
        return self._id

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


# Usage
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')

class User(Entity[UserUUID]):
    def __init__(self, id: UserUUID, name: str, email: str):
        super().__init__(id)
        self.name = name
        self.email = email

    @classmethod
    def create(cls, name: str, email: str) -> 'User':
        return cls(UserUUID(), name, email)
```

### Aggregate Root Pattern

```python
from typed_uuid import create_typed_uuid_class
from typing import List
from datetime import datetime

OrderUUID = create_typed_uuid_class('Order', 'order')
OrderItemUUID = create_typed_uuid_class('OrderItem', 'item')
UserUUID = create_typed_uuid_class('User', 'user')
ProductUUID = create_typed_uuid_class('Product', 'product')


class OrderItem:
    def __init__(self, product_id: ProductUUID, quantity: int, price: float):
        self.id = OrderItemUUID()
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    @property
    def total(self) -> float:
        return self.quantity * self.price


class Order:
    """Aggregate root for orders."""

    def __init__(self, user_id: UserUUID):
        self.id = OrderUUID()
        self.user_id = user_id
        self.items: List[OrderItem] = []
        self.created_at = datetime.utcnow()
        self._status = 'pending'

    def add_item(self, product_id: ProductUUID, quantity: int, price: float):
        if self._status != 'pending':
            raise ValueError("Cannot modify non-pending order")
        item = OrderItem(product_id, quantity, price)
        self.items.append(item)
        return item.id

    def remove_item(self, item_id: OrderItemUUID):
        self.items = [i for i in self.items if i.id != item_id]

    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)

    def submit(self):
        if not self.items:
            raise ValueError("Cannot submit empty order")
        self._status = 'submitted'
```

### Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class UserRepository(ABC):
    """Abstract repository for User entities."""

    @abstractmethod
    def get(self, id: UserUUID) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def delete(self, id: UserUUID) -> None:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass


class SQLUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session):
        self.session = session

    def get(self, id: UserUUID) -> Optional[User]:
        return self.session.query(UserModel).filter(
            UserModel.id == str(id)
        ).first()

    def save(self, user: User) -> None:
        model = UserModel(
            id=str(user.id),
            name=user.name,
            email=user.email
        )
        self.session.merge(model)
        self.session.commit()
```

## API Design Patterns

### Resource Identifiers

```python
from dataclasses import dataclass
from typed_uuid import create_typed_uuid_class, TypedUUID

# Create IDs for each resource type
UserUUID = create_typed_uuid_class('User', 'user')
PostUUID = create_typed_uuid_class('Post', 'post')
CommentUUID = create_typed_uuid_class('Comment', 'comment')

@dataclass
class ResourceRef:
    """A reference to a resource by its typed ID."""
    resource_type: str
    id: TypedUUID

    @classmethod
    def from_string(cls, value: str) -> 'ResourceRef':
        parsed = TypedUUID.parse(value)
        return cls(
            resource_type=parsed.type_id,
            id=parsed
        )

    def __str__(self):
        return str(self.id)

# Usage in APIs
def get_resource(ref: ResourceRef):
    if ref.resource_type == 'user':
        return get_user(ref.id)
    elif ref.resource_type == 'post':
        return get_post(ref.id)
    # ...
```

### HATEOAS Links

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class Link:
    href: str
    rel: str
    method: str = 'GET'

def user_links(user_id: UserUUID) -> Dict[str, Link]:
    base = f"/api/users/{user_id.short}"
    return {
        'self': Link(href=base, rel='self'),
        'update': Link(href=base, rel='update', method='PUT'),
        'delete': Link(href=base, rel='delete', method='DELETE'),
        'orders': Link(href=f"{base}/orders", rel='orders'),
    }

def user_response(user, include_links=True):
    response = {
        'id': user.id.short,
        'name': user.name,
        'email': user.email,
    }
    if include_links:
        response['_links'] = {
            k: {'href': v.href, 'method': v.method}
            for k, v in user_links(user.id).items()
        }
    return response
```

## Event-Driven Patterns

### Domain Events

```python
from dataclasses import dataclass, field
from datetime import datetime
from typed_uuid import create_typed_uuid_class

EventUUID = create_typed_uuid_class('Event', 'evt')

@dataclass
class DomainEvent:
    """Base class for domain events."""
    id: EventUUID = field(default_factory=EventUUID)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class UserCreated(DomainEvent):
    user_id: UserUUID = None
    email: str = ""

@dataclass
class OrderPlaced(DomainEvent):
    order_id: OrderUUID = None
    user_id: UserUUID = None
    total: float = 0.0

# Event store
class EventStore:
    def __init__(self):
        self.events = []

    def append(self, event: DomainEvent):
        self.events.append(event)
        print(f"Event {event.id}: {type(event).__name__}")

    def get_events_for(self, aggregate_id: TypedUUID):
        return [e for e in self.events if self._matches(e, aggregate_id)]
```

### Command Pattern

```python
from dataclasses import dataclass
from typed_uuid import create_typed_uuid_class

CommandUUID = create_typed_uuid_class('Command', 'cmd')

@dataclass
class Command:
    """Base class for commands."""
    id: CommandUUID = field(default_factory=CommandUUID)

@dataclass
class CreateUser(Command):
    name: str = ""
    email: str = ""

@dataclass
class PlaceOrder(Command):
    user_id: UserUUID = None
    product_ids: list = field(default_factory=list)

class CommandHandler:
    def handle(self, command: Command):
        handler_name = f"handle_{type(command).__name__}"
        handler = getattr(self, handler_name, None)
        if handler:
            return handler(command)
        raise ValueError(f"No handler for {type(command).__name__}")

    def handle_CreateUser(self, cmd: CreateUser):
        user_id = UserUUID()
        # Create user logic
        return user_id
```

## Multi-Tenancy Patterns

### Tenant-Scoped IDs

```python
from typed_uuid import create_typed_uuid_class

TenantUUID = create_typed_uuid_class('Tenant', 'tenant')

class TenantContext:
    """Context manager for tenant-scoped operations."""

    _current_tenant = None

    def __init__(self, tenant_id: TenantUUID):
        self.tenant_id = tenant_id

    def __enter__(self):
        TenantContext._current_tenant = self.tenant_id
        return self

    def __exit__(self, *args):
        TenantContext._current_tenant = None

    @classmethod
    def current(cls) -> TenantUUID:
        if cls._current_tenant is None:
            raise RuntimeError("No tenant context")
        return cls._current_tenant

# Usage
tenant_id = TenantUUID()
with TenantContext(tenant_id):
    # All operations here are scoped to this tenant
    current = TenantContext.current()
    print(f"Operating in tenant: {current}")
```

### Composite Keys

```python
@dataclass
class TenantScopedID:
    """An ID that's scoped to a tenant."""
    tenant_id: TenantUUID
    resource_id: TypedUUID

    def __str__(self):
        return f"{self.tenant_id.short}:{self.resource_id.short}"

    @classmethod
    def parse(cls, value: str) -> 'TenantScopedID':
        tenant_part, resource_part = value.split(':')
        return cls(
            tenant_id=TenantUUID.from_short(tenant_part),
            resource_id=TypedUUID.parse(resource_part)
        )
```

## Caching Patterns

### Cache Key Generation

```python
from typed_uuid import TypedUUID

def cache_key(*args) -> str:
    """Generate a cache key from TypedUUIDs and strings."""
    parts = []
    for arg in args:
        if isinstance(arg, TypedUUID):
            parts.append(arg.short)  # Use short format for compact keys
        else:
            parts.append(str(arg))
    return ':'.join(parts)

# Usage
key = cache_key('user', user_id, 'profile')
# Result: 'user:user_7n42DGM5...:profile'

cached_data = cache.get(key)
```

### Entity Cache

```python
from typing import TypeVar, Generic, Optional
from functools import lru_cache

T = TypeVar('T')

class EntityCache(Generic[T]):
    def __init__(self, loader, ttl=300):
        self.loader = loader
        self.cache = {}

    def get(self, id: TypedUUID) -> Optional[T]:
        key = str(id)
        if key not in self.cache:
            self.cache[key] = self.loader(id)
        return self.cache[key]

    def invalidate(self, id: TypedUUID):
        self.cache.pop(str(id), None)

# Usage
user_cache = EntityCache[User](lambda id: db.get_user(id))
user = user_cache.get(user_id)
```
