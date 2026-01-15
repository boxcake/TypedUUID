# Tutorial: Building a User System

In this tutorial, we'll build a complete user management system using TypedUUID with FastAPI and SQLAlchemy.

## What We'll Build

A REST API with:

- User registration and authentication
- Team management
- Role-based access control
- All with type-safe UUIDs

## Prerequisites

```bash
pip install typed-uuid[all] fastapi uvicorn sqlalchemy
```

## Step 1: Define Your ID Types

Create a central module for all your ID types:

```python
# app/ids.py
from typed_uuid import create_typed_uuid_class

# Core entities
UserUUID = create_typed_uuid_class('User', 'user')
TeamUUID = create_typed_uuid_class('Team', 'team')
RoleUUID = create_typed_uuid_class('Role', 'role')

# Sessions and tokens
SessionUUID = create_typed_uuid_class('Session', 'session')
TokenUUID = create_typed_uuid_class('Token', 'token')

# Audit
AuditUUID = create_typed_uuid_class('Audit', 'audit')
```

**Why do this?**

- Single source of truth for ID types
- Easy to import across your application
- Prevents duplicate type_id definitions

## Step 2: Create Database Models

```python
# app/models.py
from sqlalchemy import Column, String, ForeignKey, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session
from typed_uuid.adapters.sqlalchemy import TypedUUIDType

from app.ids import UserUUID, TeamUUID, RoleUUID

Base = declarative_base()

# Association table for many-to-many
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', TypedUUIDType('user'), ForeignKey('users.id')),
    Column('role_id', TypedUUIDType('role'), ForeignKey('roles.id'))
)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(TypedUUIDType('role'), primary_key=True, default=RoleUUID)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))

    users = relationship('User', secondary=user_roles, back_populates='roles')


class Team(Base):
    __tablename__ = 'teams'

    id = Column(TypedUUIDType('team'), primary_key=True, default=TeamUUID)
    name = Column(String(100), nullable=False)

    members = relationship('User', back_populates='team')


class User(Base):
    __tablename__ = 'users'

    id = Column(TypedUUIDType('user'), primary_key=True, default=UserUUID)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)

    team_id = Column(TypedUUIDType('team'), ForeignKey('teams.id'), nullable=True)
    team = relationship('Team', back_populates='members')

    roles = relationship('Role', secondary=user_roles, back_populates='users')
```

## Step 3: Create Pydantic Schemas

```python
# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.ids import UserUUID, TeamUUID, RoleUUID


# Role schemas
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: RoleUUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


# Team schemas
class TeamCreate(BaseModel):
    name: str


class TeamResponse(BaseModel):
    id: TeamUUID
    name: str

    class Config:
        from_attributes = True


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    team_id: Optional[TeamUUID] = None


class UserResponse(BaseModel):
    id: UserUUID
    email: str
    name: str
    team: Optional[TeamResponse] = None
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    team_id: Optional[TeamUUID] = None
```

## Step 4: Build the API

```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import hashlib

from app.ids import UserUUID, TeamUUID, RoleUUID
from app.models import Base, User, Team, Role
from app.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TeamCreate, TeamResponse,
    RoleCreate, RoleResponse
)
from app.database import engine, get_db

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management System")


# Helper function
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Team endpoints
@app.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    db_team = Team(id=TeamUUID(), name=team.name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@app.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: TeamUUID.path_param(), db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@app.get("/teams", response_model=List[TeamResponse])
def list_teams(db: Session = Depends(get_db)):
    return db.query(Team).all()


# Role endpoints
@app.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    db_role = Role(id=RoleUUID(), name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@app.get("/roles", response_model=List[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        id=UserUUID(),
        email=user.email,
        name=user.name,
        password_hash=hash_password(user.password),
        team_id=user.team_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: UserUUID.path_param(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UserUUID.path_param(),
    updates: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if updates.name:
        user.name = updates.name
    if updates.team_id is not None:
        user.team_id = updates.team_id

    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UserUUID.path_param(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()


@app.get("/users", response_model=List[UserResponse])
def list_users(
    team_id: Optional[TeamUUID] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if team_id:
        query = query.filter(User.team_id == team_id)
    return query.all()


# Role assignment
@app.post("/users/{user_id}/roles/{role_id}", response_model=UserResponse)
def assign_role(
    user_id: UserUUID.path_param(),
    role_id: RoleUUID.path_param(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)

    return user
```

## Step 5: Database Configuration

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./user_system.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Step 6: Run and Test

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for the interactive API documentation.

### Test the API

```bash
# Create a team
curl -X POST http://localhost:8000/teams \
  -H "Content-Type: application/json" \
  -d '{"name": "Engineering"}'

# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "name": "Alice", "password": "secret123"}'

# Get a user (use the ID from the response above)
curl http://localhost:8000/users/user-550e8400-e29b-41d4-a716-446655440000
```

## What You've Learned

1. **Centralized ID definitions** - All ID types in one module
2. **Type-safe database models** - SQLAlchemy with TypedUUIDType
3. **Validated API schemas** - Pydantic models with TypedUUID
4. **Type-safe endpoints** - FastAPI path parameters
5. **Relationships** - Foreign keys and many-to-many with TypedUUID

## Next Steps

- Add authentication with JWT tokens (use TokenUUID)
- Add audit logging (use AuditUUID)
- Add caching with TypedUUID keys
- Deploy to production

## Full Source Code

The complete source code for this tutorial is available at:
[github.com/boxcake/TypedUUID/examples/user-system](https://github.com/boxcake/TypedUUID)
