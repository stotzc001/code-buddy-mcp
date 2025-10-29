---
title: FastAPI REST Endpoint Creation
description: Comprehensive workflow for creating production-ready REST API endpoints with FastAPI, including validation, error handling, testing, and documentation
category: Development
subcategory: Backend
tags: [api, rest, fastapi, backend, python]
technologies: [Python, FastAPI, Pydantic, pytest]
complexity: intermediate
estimated_time_minutes: 45
use_cases: [Creating new API endpoints, Adding features to existing APIs, Building microservices]
problem_statement: Creating REST API endpoints requires following best practices for validation, error handling, testing, and documentation to ensure reliability and maintainability
author: Code Buddy Team
---

# FastAPI REST Endpoint Creation Workflow

## Overview

This workflow guides you through creating production-ready REST API endpoints using FastAPI. You'll learn how to implement proper request/response validation, error handling, authentication, testing, and API documentation.

## Prerequisites

Before starting, ensure you have:
- Python 3.8+ installed
- FastAPI and dependencies: `pip install fastapi uvicorn pydantic pytest httpx`
- Basic understanding of HTTP methods (GET, POST, PUT, DELETE)
- Familiarity with Python type hints

## Step 1: Define Pydantic Models

Create request/response models with validation:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    """Request model for creating a user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric'
        return v

class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy models
```

## Step 2: Create the Endpoint

Define the route handler with proper typing:

```python
from fastapi import FastAPI, HTTPException, status, Depends
from typing import List

app = FastAPI(title="User API", version="1.0.0")

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the provided information",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "User already exists"}
    },
    tags=["users"]
)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)  # Database dependency
) -> UserResponse:
    """
    Create a new user with the following information:
    
    - **username**: Unique username (3-50 chars, alphanumeric)
    - **email**: Valid email address
    - **full_name**: Optional full name
    - **age**: Optional age (0-150)
    """
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | 
        (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists"
        )
    
    # Create user
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
```

## Step 3: Implement Error Handling

Add custom exception handlers:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## Step 4: Add Authentication (Optional)

Implement JWT authentication:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Verify JWT token and return current user."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Protected endpoint
@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

## Step 5: Write Tests

Create comprehensive tests:

```python
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

def test_create_user_success():
    """Test successful user creation."""
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "age": 25
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data

def test_create_user_duplicate():
    """Test duplicate user prevention."""
    user_data = {
        "username": "duplicate",
        "email": "dup@example.com"
    }
    
    # Create first user
    response1 = client.post("/users", json=user_data)
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = client.post("/users", json=user_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]

def test_create_user_invalid_email():
    """Test email validation."""
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "invalid-email"
        }
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("email" in str(error).lower() for error in errors)

@pytest.mark.parametrize("age,expected_status", [
    (-1, 422),   # Negative age
    (0, 201),    # Minimum valid age
    (150, 201),  # Maximum valid age
    (151, 422),  # Over maximum age
])
def test_create_user_age_validation(age, expected_status):
    """Test age validation boundaries."""
    response = client.post(
        "/users",
        json={
            "username": f"user_{age}",
            "email": f"user{age}@example.com",
            "age": age
        }
    )
    assert response.status_code == expected_status
```

## Step 6: Add Rate Limiting (Optional)

Implement rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/users", response_model=UserResponse)
@limiter.limit("5/minute")  # 5 requests per minute
async def create_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # ... endpoint implementation
    pass
```

## Step 7: Document with OpenAPI

FastAPI auto-generates OpenAPI docs. Enhance with metadata:

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="User Management API",
        version="1.0.0",
        description="REST API for user management with authentication",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

Access docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Step 8: Run and Test

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

Test the endpoint:

```bash
# Create user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "age": 30
  }'

# Run tests
pytest tests/ -v
```

## Best Practices

### 1. Use Type Hints
- Always use type hints for better IDE support and validation
- Leverage Pydantic for automatic validation

### 2. Proper HTTP Status Codes
- 200: OK (successful GET/PUT/PATCH)
- 201: Created (successful POST)
- 204: No Content (successful DELETE)
- 400: Bad Request (validation error)
- 401: Unauthorized (missing/invalid auth)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 409: Conflict (duplicate resource)
- 500: Internal Server Error

### 3. Error Handling
- Use HTTPException for expected errors
- Log unexpected errors for debugging
- Return consistent error format

### 4. Security
- Validate all inputs
- Use HTTPS in production
- Implement rate limiting
- Add CORS if needed
- Never expose internal errors to clients

### 5. Testing
- Test success cases
- Test error cases
- Test boundary conditions
- Use parametrized tests for multiple scenarios
- Aim for 80%+ code coverage

## Common Patterns

### Pagination
```python
from fastapi import Query

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
```

### Filtering
```python
@app.get("/users", response_model=List[UserResponse])
async def list_users(
    username: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None, ge=0)
):
    query = db.query(User)
    if username:
        query = query.filter(User.username.contains(username))
    if min_age:
        query = query.filter(User.age >= min_age)
    return query.all()
```

### Background Tasks
```python
from fastapi import BackgroundTasks

async def send_welcome_email(email: str):
    # Send email asynchronously
    pass

@app.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    
    # Send email in background
    background_tasks.add_task(send_welcome_email, new_user.email)
    
    return new_user
```

## Troubleshooting

### Issue: Validation errors not showing
**Solution**: Check Pydantic model field definitions and validators

### Issue: 422 Unprocessable Entity
**Solution**: Review request body matches Pydantic model exactly

### Issue: Database connection errors
**Solution**: Verify database dependency and connection pool settings

### Issue: CORS errors in browser
**Solution**: Add CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

After mastering this workflow:
1. Explore advanced FastAPI features (WebSockets, GraphQL)
2. Implement caching with Redis
3. Add monitoring and logging
4. Deploy to production (Docker, Kubernetes)
5. Implement API versioning

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [HTTP Status Codes](https://httpstatuses.com)
- [REST API Best Practices](https://restfulapi.net)

## Estimated Time

- Setup: 5 minutes
- Implementation: 25 minutes
- Testing: 10 minutes
- Documentation: 5 minutes

**Total**: ~45 minutes for complete implementation
