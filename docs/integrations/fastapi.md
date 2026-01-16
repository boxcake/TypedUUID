# FastAPI Integration

TypedUUID integrates with FastAPI for building type-safe APIs.

## Installation

```bash
pip install typed-uuid[fastapi]
```

This also installs Pydantic support.

## Basic Usage

### Path Parameters

Use `path_param()` for type-safe path parameters:

```python
from fastapi import FastAPI
from typed_uuid import create_typed_uuid_class

app = FastAPI()

UserUUID = create_typed_uuid_class('User', 'user')

@app.get("/users/{user_id}")
async def get_user(user_id: UserUUID.path_param()):
    return {"user_id": str(user_id)}
```

### Request Bodies

Use TypedUUID in Pydantic models for request bodies:

```python
from pydantic import BaseModel

class CreateOrderRequest(BaseModel):
    user_id: UserUUID
    product_id: ProductUUID
    quantity: int

@app.post("/orders")
async def create_order(request: CreateOrderRequest):
    order_id = OrderUUID()
    return {
        "order_id": str(order_id),
        "user_id": str(request.user_id),
        "product_id": str(request.product_id)
    }
```

### Response Models

Use TypedUUID in response models:

```python
class UserResponse(BaseModel):
    id: UserUUID
    name: str
    email: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UserUUID.path_param()):
    return UserResponse(
        id=user_id,
        name="Alice",
        email="alice@example.com"
    )
```

## Path Parameter Options

### Custom Description

Add a description for OpenAPI documentation:

```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: UserUUID.path_param(description="The unique user identifier")
):
    return {"user_id": str(user_id)}
```

### Generated Documentation

The path parameter automatically includes:

- Example value: `user-550e8400-e29b-41d4-a716-446655440000`
- Pattern validation
- Type description

## Full API Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from typed_uuid import create_typed_uuid_class

app = FastAPI(title="User Management API")

# Create typed UUID classes
UserUUID = create_typed_uuid_class('User', 'user')
TeamUUID = create_typed_uuid_class('Team', 'team')

# In-memory storage (use a real database in production)
users_db = {}
teams_db = {}


# Models
class UserCreate(BaseModel):
    name: str
    email: str
    team_id: Optional[TeamUUID] = None


class UserResponse(BaseModel):
    id: UserUUID
    name: str
    email: str
    team_id: Optional[TeamUUID] = None


class TeamCreate(BaseModel):
    name: str


class TeamResponse(BaseModel):
    id: TeamUUID
    name: str
    member_ids: List[UserUUID]


# User endpoints
@app.post("/users", response_model=UserResponse)
async def create_user(request: UserCreate):
    user_id = UserUUID()
    user = UserResponse(
        id=user_id,
        name=request.name,
        email=request.email,
        team_id=request.team_id
    )
    users_db[str(user_id)] = user
    return user


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UserUUID.path_param(description="User ID")):
    user = users_db.get(str(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", response_model=List[UserResponse])
async def list_users():
    return list(users_db.values())


@app.delete("/users/{user_id}")
async def delete_user(user_id: UserUUID.path_param()):
    if str(user_id) not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[str(user_id)]
    return {"deleted": True}


# Team endpoints
@app.post("/teams", response_model=TeamResponse)
async def create_team(request: TeamCreate):
    team_id = TeamUUID()
    team = TeamResponse(
        id=team_id,
        name=request.name,
        member_ids=[]
    )
    teams_db[str(team_id)] = team
    return team


@app.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: TeamUUID.path_param()):
    team = teams_db.get(str(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
```

## Query Parameters

For query parameters, use standard Pydantic validation:

```python
from fastapi import Query
from typing import Optional

@app.get("/users")
async def list_users(
    team_id: Optional[str] = Query(None, description="Filter by team")
):
    if team_id:
        team_uuid = TeamUUID.from_string(team_id)
        # Filter users by team
    return list(users_db.values())
```

## Error Handling

FastAPI automatically returns validation errors:

```python
# Invalid UUID format returns 422 Unprocessable Entity
# GET /users/not-a-valid-uuid
# Response: {"detail": [{"loc": ["path", "user_id"], ...}]}
```

For custom error handling:

```python
from fastapi import HTTPException
from typed_uuid import InvalidUUIDError

@app.get("/users/{user_id}")
async def get_user(user_id: UserUUID.path_param()):
    try:
        user = users_db.get(str(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except InvalidUUIDError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
```

## Using Short IDs in URLs

Accept both standard and short format:

```python
from typed_uuid import TypedUUID

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Accept both standard and short UUID formats."""
    try:
        # Auto-detect format
        parsed_id = TypedUUID.parse(user_id)
        if not isinstance(parsed_id, UserUUID):
            raise HTTPException(status_code=400, detail="Expected user ID")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    return {"user_id": str(parsed_id)}
```

## OpenAPI Schema

TypedUUID generates proper OpenAPI schemas:

```yaml
paths:
  /users/{user_id}:
    get:
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
            pattern: "^[a-zA-Z0-9]+-[0-9a-f]{8}-..."
          example: "user-550e8400-e29b-41d4-a716-446655440000"
```

## Best Practices

### 1. Consistent ID Types

```python
# Define all ID types in one place
# app/ids.py
from typed_uuid import create_typed_uuid_class

UserUUID = create_typed_uuid_class('User', 'user')
OrderUUID = create_typed_uuid_class('Order', 'order')
ProductUUID = create_typed_uuid_class('Product', 'product')

# Import in your routes
from app.ids import UserUUID, OrderUUID, ProductUUID
```

### 2. Response Consistency

```python
# Always use response models
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UserUUID.path_param()):
    # ...

# Not this (loses type information)
@app.get("/users/{user_id}")
async def get_user(user_id: UserUUID.path_param()):
    return {"id": str(user_id), ...}  # ID becomes plain string
```

### 3. Document Your API

```python
@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
    description="Retrieve a user's details using their unique identifier."
)
async def get_user(
    user_id: UserUUID.path_param(description="The unique user identifier")
):
    """
    Get a user by their ID.

    - **user_id**: Must be a valid user UUID in format `user-{uuid}`
    """
    pass
```
