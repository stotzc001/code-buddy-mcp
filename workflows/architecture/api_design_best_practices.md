# API Design Best Practices

**ID:** arc-001  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design robust, scalable, developer-friendly APIs following industry best practices and conventions

**Why:** Well-designed APIs reduce integration complexity by 60%, improve developer experience, enable system evolution, and prevent costly redesigns that can take months to fix

**When to use:**
- Designing new public or internal APIs
- Reviewing and improving existing API designs
- Creating API standards and guidelines for teams
- Planning API versioning or major migrations
- Building microservices architecture
- Exposing system functionality to partners or third parties

---

## Prerequisites

**Required:**
- [ ] Understanding of REST principles and/or GraphQL
- [ ] Familiarity with HTTP methods, status codes, and headers
- [ ] Knowledge of authentication mechanisms (OAuth2, JWT, API keys)
- [ ] Basic understanding of API documentation tools (OpenAPI/Swagger)

**Check before starting:**
```bash
# Check for API design/documentation tools
which swagger  # or openapi-generator
npm list -g @stoplight/spectral-cli  # API linting
pip show apispec  # Python OpenAPI tools

# If using GraphQL
npm list graphql
```

---

## Implementation Steps

### Step 1: Define Resources and Naming Conventions

**What:** Identify domain resources and establish consistent naming patterns

**How:**

**Resource Identification:**

Start with domain entities and their relationships:
- **Entities:** Users, Products, Orders, Invoices
- **Collections:** Groups of entities
- **Actions:** Operations on resources (when REST verbs aren't enough)

**REST Naming Conventions:**

```
GOOD Examples:
GET    /api/v1/users                    # Get list of users
GET    /api/v1/users/{id}              # Get specific user
POST   /api/v1/users                    # Create new user
PUT    /api/v1/users/{id}              # Update entire user
PATCH  /api/v1/users/{id}              # Partial user update
DELETE /api/v1/users/{id}              # Delete user

# Nested resources
GET    /api/v1/users/{id}/orders       # Get user's orders
GET    /api/v1/orders/{id}/items       # Get order items

# Complex operations (use POST with action endpoints)
POST   /api/v1/orders/{id}/cancel      # Cancel order
POST   /api/v1/users/{id}/reset-password

BAD Examples:
GET    /api/getUsers                    # ❌ Verb in URL
POST   /api/user/create                 # ❌ Redundant action
GET    /api/users/get/{id}             # ❌ Verb in path
PUT    /api/v1/updateUser              # ❌ Not RESTful
GET    /api/v1/users-list              # ❌ Inconsistent
```

**Naming Rules:**

1. **Use nouns, not verbs:** `/users` not `/getUsers`
2. **Use plural for collections:** `/users` not `/user`
3. **Use kebab-case:** `/order-items` not `/orderItems` or `/order_items`
4. **Keep URLs lowercase:** `/api/users` not `/API/Users`
5. **Use hierarchy:** `/users/{id}/orders` for relationships
6. **Limit nesting:** Max 2-3 levels deep

**GraphQL Naming:**

```graphql
# Good GraphQL naming
type User {
  id: ID!
  firstName: String!      # camelCase for fields
  lastName: String!
  orders: [Order!]!       # Related resources
  createdAt: DateTime!
}

type Query {
  user(id: ID!): User
  users(
    first: Int
    after: String
    filter: UserFilter
  ): UserConnection!      # Pagination built-in
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
}

# Naming conventions:
# - Types: PascalCase
# - Fields: camelCase
# - Queries: descriptive, plural for lists
# - Mutations: verb + noun (createUser, not userCreate)
```

**Verification:**
- [ ] All resources identified and documented
- [ ] Naming follows consistent convention
- [ ] URL hierarchy reflects resource relationships
- [ ] No verbs in resource names (REST)
- [ ] Field names use camelCase (GraphQL)

**If This Fails:**
→ Review domain model with team
→ Look at successful APIs in your industry for patterns
→ Start with core resources, add edge cases later

---

### Step 2: Choose HTTP Methods and Status Codes Correctly

**What:** Map operations to appropriate HTTP methods and return meaningful status codes

**How:**

**HTTP Methods (REST):**

```
GET     - Retrieve resource(s), idempotent, safe
POST    - Create new resource, send actions
PUT     - Replace entire resource, idempotent
PATCH   - Partial update, idempotent
DELETE  - Remove resource, idempotent
HEAD    - Like GET but only headers
OPTIONS - Get allowed methods (CORS)
```

**Common Patterns:**

```python
# GET - Retrieve (Safe & Idempotent)
GET /api/v1/users
Response: 200 OK
{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 20
  }
}

GET /api/v1/users/{id}
Response: 200 OK (found) or 404 Not Found

# POST - Create (Not Idempotent)
POST /api/v1/users
Body: {
  "email": "user@example.com",
  "name": "John Doe"
}
Response: 201 Created
Location: /api/v1/users/123
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-10-26T10:00:00Z"
}

# PUT - Replace (Idempotent)
PUT /api/v1/users/{id}
Body: {
  "email": "newemail@example.com",
  "name": "Jane Doe",
  "role": "admin"
}
Response: 200 OK (updated) or 204 No Content

# PATCH - Partial Update (Idempotent)
PATCH /api/v1/users/{id}
Body: {
  "name": "Jane Smith"  # Only update name
}
Response: 200 OK

# DELETE - Remove (Idempotent)
DELETE /api/v1/users/{id}
Response: 204 No Content or 200 OK with details
```

**HTTP Status Codes:**

```
Success:
200 OK              - Request succeeded
201 Created         - Resource created (POST)
202 Accepted        - Async processing started
204 No Content      - Success, no body (DELETE, some PUT/PATCH)

Client Errors:
400 Bad Request     - Invalid request body/parameters
401 Unauthorized    - Authentication required/failed
403 Forbidden       - Authenticated but not authorized
404 Not Found       - Resource doesn't exist
405 Method Not Allowed - HTTP method not supported
409 Conflict        - Resource state conflict (duplicate email)
422 Unprocessable   - Validation failed
429 Too Many Requests - Rate limit exceeded

Server Errors:
500 Internal Error  - Server error (log details, hide from client)
502 Bad Gateway     - Upstream service error
503 Service Unavailable - Temporary outage
504 Gateway Timeout - Upstream timeout
```

**Status Code Decision Tree:**

```python
def choose_status_code(result):
    if result.is_success:
        if result.created:
            return 201  # POST created resource
        elif result.has_body:
            return 200  # GET, most PUT/PATCH
        else:
            return 204  # DELETE, some PUT/PATCH
    
    elif result.is_client_error:
        if not result.authenticated:
            return 401  # No/invalid auth
        elif not result.authorized:
            return 403  # Not allowed
        elif not result.exists:
            return 404  # Not found
        elif result.validation_failed:
            return 422  # Invalid data
        elif result.rate_limited:
            return 429  # Too many requests
        else:
            return 400  # Generic client error
    
    else:  # Server error
        return 500  # Log details internally
```

**Verification:**
- [ ] GET never modifies data
- [ ] POST used for creation
- [ ] PUT replaces entire resource
- [ ] PATCH for partial updates
- [ ] DELETE returns 204 or 200
- [ ] Appropriate status codes used
- [ ] 2xx for success, 4xx for client errors, 5xx for server errors

**If This Fails:**
→ Review HTTP specification (RFC 7231)
→ Check if operation is truly idempotent
→ Consider if you need custom status codes (usually don't)

---

### Step 3: Design Request and Response Formats

**What:** Standardize JSON structures for consistency and predictability

**How:**

**Request Body Standards:**

```json
// POST /api/v1/users - Create user
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "member",
  "preferences": {
    "notifications": true,
    "theme": "dark"
  }
}

// PATCH /api/v1/users/{id} - Partial update
{
  "name": "Jane Doe"  // Only fields being updated
}

// Guidelines:
// - Use camelCase for JSON keys
// - Nest related data logically
// - Validate all inputs
// - Don't require null for optional fields
```

**Response Body Standards:**

```json
// Single resource
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "member",
  "createdAt": "2025-10-26T10:00:00Z",
  "updatedAt": "2025-10-26T10:00:00Z"
}

// Collection with metadata
{
  "data": [
    { "id": 1, "name": "User 1" },
    { "id": 2, "name": "User 2" }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "perPage": 20,
    "totalPages": 8
  },
  "links": {
    "first": "/api/v1/users?page=1",
    "prev": null,
    "next": "/api/v1/users?page=2",
    "last": "/api/v1/users?page=8"
  }
}

// Consistent timestamps
{
  "createdAt": "2025-10-26T10:00:00Z",  // ISO 8601, UTC
  "updatedAt": "2025-10-26T11:30:00Z"
}
```

**Error Response Format:**

```json
// Standard error format
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid",
    "details": [
      {
        "field": "email",
        "message": "Email address is invalid",
        "code": "INVALID_EMAIL"
      },
      {
        "field": "name",
        "message": "Name is required",
        "code": "REQUIRED_FIELD"
      }
    ],
    "requestId": "req_abc123",
    "timestamp": "2025-10-26T10:00:00Z"
  }
}

// Server errors (hide details from clients)
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "requestId": "req_xyz789",
    "timestamp": "2025-10-26T10:00:00Z"
  }
}
// Log full stack trace server-side only
```

**Field Naming:**

```python
# Consistent field names
{
  "id": 123,                    # Always 'id', not 'userId' or 'user_id'
  "createdAt": "...",          # Timestamps: createdAt, updatedAt, deletedAt
  "isActive": true,            # Booleans: is/has prefix (isActive, hasAccess)
  "totalCount": 150,           # Counts: use 'count' or 'total'
  "items": [],                 # Arrays: plural nouns
  "metadata": {},              # Objects: descriptive nouns
}

# Avoid:
{
  "user_id": 123,              # ❌ snake_case
  "UserId": 123,               # ❌ PascalCase  
  "created": "...",            # ❌ Ambiguous
  "active": true,              # ❌ Not clear it's boolean
}
```

**Verification:**
- [ ] Consistent JSON key naming (camelCase)
- [ ] Timestamps in ISO 8601 format (UTC)
- [ ] Collections have pagination metadata
- [ ] Error format is standardized
- [ ] Null vs missing fields handled consistently
- [ ] Response envelopes used consistently

**If This Fails:**
→ Create JSON schema definitions first
→ Use API linting tools (Spectral, API Blueprint)
→ Review existing successful APIs for patterns

---

### Step 4: Implement Versioning Strategy

**What:** Plan for API evolution without breaking existing clients

**How:**

**Versioning Approaches:**

```
1. URL Path Versioning (Recommended for REST)
   GET /api/v1/users
   GET /api/v2/users
   
   ✅ Clear, visible, easy to route
   ❌ Requires new endpoints for changes

2. Header Versioning
   GET /api/users
   Accept: application/vnd.myapi.v1+json
   
   ✅ Clean URLs
   ❌ Less discoverable, harder to test

3. Query Parameter
   GET /api/users?version=1
   
   ✅ Simple
   ❌ Easy to forget, pollutes query params

4. Content Negotiation
   GET /api/users
   Accept: application/json; version=1
   
   ✅ Standards-compliant
   ❌ Complex, often overkill
```

**Recommended: URL Path Versioning:**

```python
# Version in URL path
/api/v1/users      # Version 1
/api/v2/users      # Version 2 (breaking changes)
/api/v1/products   # v1 still available

# When to increment version:
# - Breaking changes (field removal, rename)
# - Changed behavior that breaks clients
# - New required parameters

# Non-breaking changes (don't version):
# - Adding optional fields
# - Adding new endpoints
# - Adding optional query parameters
# - Fixing bugs
```

**Version Management:**

```python
# FastAPI version routing
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/users")
async def get_users_v1():
    return {"version": 1, "users": [...]}

# Version 2 with breaking changes
v2_router = APIRouter(prefix="/api/v2")

@v2_router.get("/users")
async def get_users_v2():
    # New response format
    return {
        "version": 2,
        "data": {"users": [...]},
        "meta": {...}
    }

app.include_router(v1_router)
app.include_router(v2_router)

# Deprecation headers
from fastapi import Response

@v1_router.get("/users")
async def get_users_deprecated(response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2026-01-01T00:00:00Z"
    response.headers["Link"] = '</api/v2/users>; rel="successor-version"'
    return {"users": [...]}
```

**GraphQL Versioning (Different Approach):**

```graphql
# GraphQL doesn't version the entire API
# Instead, deprecate fields and add new ones

type User {
  id: ID!
  name: String!
  # Old field (deprecated)
  email: String! @deprecated(reason: "Use `emailAddress` instead")
  # New field
  emailAddress: String!
}

# Clients gradually migrate, no breaking changes
```

**Version Lifecycle:**

```
v1: Active (2023-01-01 → 2025-01-01)
  ↓ Announce deprecation 6 months before sunset
v1: Deprecated (2024-07-01)
  ↓ Add sunset header, update docs
v2: Active (2024-01-01 → ongoing)
  ↓
v1: Sunset (2025-01-01)
  ↓ Return 410 Gone
v1: Removed from documentation
```

**Verification:**
- [ ] Versioning strategy documented
- [ ] Major versions in URLs (/v1, /v2)
- [ ] Deprecation policy defined
- [ ] Sunset headers added to old versions
- [ ] All versions fully documented

**If This Fails:**
→ Start with v1, even if it's your first API
→ Plan for v2 before you need it
→ Give clients 6-12 months to migrate

---

### Step 5: Design Authentication and Authorization

**What:** Secure API access with proper authentication and authorization

**How:**

**Authentication Methods:**

```
1. API Keys (Simple, good for server-to-server)
   Authorization: Bearer sk_live_abc123...
   
2. JWT Tokens (Stateless, scalable)
   Authorization: Bearer eyJhbGci...
   
3. OAuth 2.0 (Industry standard)
   Authorization: Bearer <access_token>
   
4. Basic Auth (Simple, less secure)
   Authorization: Basic base64(username:password)
```

**Recommended: JWT with OAuth 2.0:**

```python
# FastAPI with JWT authentication
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        return {"id": user_id, "role": payload.get("role")}
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/api/v1/users/me")
async def get_current_user_profile(current_user = Depends(get_current_user)):
    return {"user": current_user}
```

**Authorization Patterns:**

```python
# Role-Based Access Control (RBAC)
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

def require_role(required_role: Role):
    def role_checker(user = Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

@app.delete("/api/v1/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user = Depends(require_role(Role.ADMIN))
):
    # Only admins can delete users
    return {"deleted": user_id}

# Resource-Based Authorization
@app.patch("/api/v1/users/{user_id}")
async def update_user(
    user_id: int,
    current_user = Depends(get_current_user)
):
    # Users can only update their own profile (or admins)
    if current_user["id"] != user_id and current_user["role"] != Role.ADMIN:
        raise HTTPException(status_code=403)
    
    return {"updated": user_id}
```

**Security Headers:**

```python
# Add security headers to all responses
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

**Rate Limiting:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/search")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def search(request: Request):
    return {"results": [...]}

# Return rate limit info in headers
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 87
# X-RateLimit-Reset: 1614556800
```

**Verification:**
- [ ] Authentication method chosen and implemented
- [ ] Authorization checks on protected endpoints
- [ ] Security headers configured
- [ ] Rate limiting implemented
- [ ] HTTPS enforced in production
- [ ] Sensitive data not logged

**If This Fails:**
→ Start with API keys for simplicity, add OAuth later
→ Use existing auth libraries (don't roll your own)
→ Test auth failures explicitly

---

### Step 6: Add Filtering, Sorting, and Pagination

**What:** Enable clients to efficiently query large datasets

**How:**

**Pagination Patterns:**

```python
# Offset-based pagination (simple, but less efficient)
GET /api/v1/users?page=2&per_page=20
GET /api/v1/users?offset=20&limit=20

{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 2,
    "per_page": 20,
    "total_pages": 8
  },
  "links": {
    "first": "/api/v1/users?page=1",
    "prev": "/api/v1/users?page=1",
    "next": "/api/v1/users?page=3",
    "last": "/api/v1/users?page=8"
  }
}

# Cursor-based pagination (efficient, real-time safe)
GET /api/v1/users?cursor=abc123&limit=20

{
  "data": [...],
  "pagination": {
    "next_cursor": "xyz789",
    "has_more": true
  }
}

# FastAPI implementation
from fastapi import Query

@app.get("/api/v1/users")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * per_page
    users = db.query(User).offset(offset).limit(per_page).all()
    total = db.query(User).count()
    
    return {
        "data": users,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    }
```

**Filtering:**

```python
# Query parameters for filtering
GET /api/v1/users?role=admin&status=active
GET /api/v1/orders?created_after=2025-01-01&min_amount=100

@app.get("/api/v1/users")
async def list_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    email_contains: Optional[str] = None
):
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    if email_contains:
        query = query.filter(User.email.contains(email_contains))
    
    return {"data": query.all()}

# Advanced filtering with operators
GET /api/v1/products?price[gte]=100&price[lte]=500
# price >= 100 AND price <= 500

GET /api/v1/users?created_at[gt]=2025-01-01&role[in]=admin,moderator
# created_at > 2025-01-01 AND role IN (admin, moderator)
```

**Sorting:**

```python
# Query parameter sorting
GET /api/v1/users?sort=created_at          # Ascending
GET /api/v1/users?sort=-created_at         # Descending (minus prefix)
GET /api/v1/users?sort=last_name,first_name # Multiple fields

@app.get("/api/v1/users")
async def list_users(sort: str = "created_at"):
    query = db.query(User)
    
    # Parse sort parameter
    for field in sort.split(","):
        if field.startswith("-"):
            # Descending
            query = query.order_by(desc(getattr(User, field[1:])))
        else:
            # Ascending
            query = query.order_by(asc(getattr(User, field)))
    
    return {"data": query.all()}
```

**Field Selection (Sparse Fieldsets):**

```python
# Request only needed fields
GET /api/v1/users?fields=id,name,email

@app.get("/api/v1/users")
async def list_users(fields: Optional[str] = None):
    if fields:
        # Return only requested fields
        field_list = fields.split(",")
        users = db.query(*[getattr(User, f) for f in field_list]).all()
    else:
        # Return all fields
        users = db.query(User).all()
    
    return {"data": users}
```

**Search:**

```python
# Full-text search
GET /api/v1/users?q=john+doe

@app.get("/api/v1/users")
async def search_users(q: Optional[str] = None):
    query = db.query(User)
    
    if q:
        # Search across multiple fields
        search = f"%{q}%"
        query = query.filter(
            or_(
                User.name.ilike(search),
                User.email.ilike(search)
            )
        )
    
    return {"data": query.all()}
```

**Verification:**
- [ ] Pagination implemented (offset or cursor)
- [ ] Filtering works for common queries
- [ ] Sorting supports multiple fields
- [ ] Default limits prevent huge responses
- [ ] Query parameters validated
- [ ] Efficient database queries (no N+1)

**If This Fails:**
→ Start with simple offset pagination
→ Add filtering for most-requested fields first
→ Use database indexes for filtered/sorted fields

---

### Step 7: Document with OpenAPI/Swagger

**What:** Create comprehensive, interactive API documentation

**How:**

**FastAPI Auto-Documentation:**

```python
from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(
    title="My API",
    description="Comprehensive API for user management",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI at /docs
    redoc_url="/redoc"       # ReDoc at /redoc
)

# Pydantic models for automatic schema
class User(BaseModel):
    id: int = Field(..., description="Unique user identifier", example=123)
    email: str = Field(..., description="User email address", example="user@example.com")
    name: str = Field(..., description="User full name", example="John Doe")
    role: str = Field(..., description="User role", example="member")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "name": "John Doe",
                "role": "member"
            }
        }

class UserCreate(BaseModel):
    email: str = Field(..., example="user@example.com")
    name: str = Field(..., min_length=1, max_length=100, example="John Doe")
    role: str = Field(default="member", example="member")

# Documented endpoints
@app.get(
    "/api/v1/users",
    response_model=List[User],
    summary="List all users",
    description="Retrieve a paginated list of all users in the system",
    tags=["Users"]
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, description="Filter by role")
):
    """
    Retrieve users with pagination and optional filtering.
    
    - **page**: Page number (starts at 1)
    - **per_page**: Number of items per page (max 100)
    - **role**: Optional role filter (admin, member, guest)
    
    Returns a list of users matching the criteria.
    """
    return [...]

@app.post(
    "/api/v1/users",
    response_model=User,
    status_code=201,
    summary="Create new user",
    tags=["Users"]
)
async def create_user(user: UserCreate = Body(...)):
    """
    Create a new user account.
    
    Required fields:
    - email: Valid email address
    - name: User's full name (1-100 characters)
    
    Optional fields:
    - role: User role (defaults to 'member')
    """
    return {...}
```

**OpenAPI Extensions:**

```python
# Custom OpenAPI schema
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="Comprehensive API documentation",
        routes=app.routes,
    )
    
    # Add authentication scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Add global security
    openapi_schema["security"] = [{"Bearer": []}]
    
    # Add examples
    openapi_schema["components"]["examples"] = {
        "UserExample": {
            "value": {
                "id": 123,
                "email": "user@example.com",
                "name": "John Doe"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Additional Documentation:**

```markdown
# API Overview

## Base URL
https://api.example.com/v1

## Authentication
All requests require Bearer token in Authorization header:
```
Authorization: Bearer YOUR_TOKEN_HERE
```

## Rate Limits
- 100 requests per minute per IP
- 1000 requests per hour per API key

## Pagination
All list endpoints support pagination:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

## Error Handling
All errors follow this format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": []
  }
}
```

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error
```

**Verification:**
- [ ] OpenAPI/Swagger docs auto-generated
- [ ] All endpoints documented
- [ ] Request/response examples provided
- [ ] Authentication documented
- [ ] Error responses documented
- [ ] Rate limits explained

**If This Fails:**
→ Use FastAPI/Flask-RESTX for auto-docs
→ Start with basic endpoint descriptions
→ Add examples gradually

---

## Verification Checklist

After completing this workflow:

- [ ] Resources and endpoints follow naming conventions
- [ ] HTTP methods and status codes used correctly
- [ ] Request/response formats standardized
- [ ] Versioning strategy implemented
- [ ] Authentication and authorization working
- [ ] Pagination, filtering, sorting implemented
- [ ] API fully documented (OpenAPI/Swagger)
- [ ] Rate limiting configured
- [ ] Error handling standardized
- [ ] Security headers configured
- [ ] CORS configured appropriately
- [ ] API tested with real clients

---

## Common Issues & Solutions

### Issue: Inconsistent naming across endpoints

**Symptoms:**
- Some endpoints use camelCase, others snake_case
- Verbs in URLs (`/getUsers`)
- Inconsistent pluralization

**Solution:**
```python
# Create style guide and lint rules
# tools/api_linter.py
import re

def check_endpoint(path):
    errors = []
    
    # Check for verbs
    verbs = ['get', 'create', 'update', 'delete', 'post', 'put']
    if any(verb in path.lower() for verb in verbs):
        errors.append(f"Verb found in path: {path}")
    
    # Check for snake_case (should be kebab-case)
    if '_' in path:
        errors.append(f"Use kebab-case, not snake_case: {path}")
    
    # Check pluralization
    parts = path.split('/')
    for part in parts:
        if part and not part.startswith('{'):
            if not part.endswith('s') and part not in ['api', 'v1', 'v2']:
                errors.append(f"Resource should be plural: {part}")
    
    return errors

# Run in CI/CD
for endpoint in get_all_endpoints():
    errors = check_endpoint(endpoint)
    if errors:
        print(f"Errors in {endpoint}: {errors}")
        sys.exit(1)
```

**Prevention:**
- Document naming conventions in README
- Use API linting tools (Spectral)
- Code review checklist includes API design
- Auto-generate endpoints from schema

---

### Issue: Breaking changes without versioning

**Symptoms:**
- Clients break when API updated
- Can't maintain backward compatibility
- No deprecation warnings

**Solution:**
```python
# Implement version management
from enum import Enum

class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"

# Support multiple versions simultaneously
@app.get("/api/v1/users")
async def get_users_v1():
    return {"users": [...]}  # Old format

@app.get("/api/v2/users")
async def get_users_v2():
    return {
        "data": {"users": [...]},  # New format
        "meta": {...}
    }

# Add deprecation warnings
@app.get("/api/v1/users")
async def get_users_deprecated(response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2026-06-01T00:00:00Z"
    response.headers["Link"] = '</api/v2/users>; rel="successor-version"'
    return {"users": [...]}

# After sunset date, return 410 Gone
@app.get("/api/v1/users")
async def get_users_gone():
    raise HTTPException(
        status_code=410,
        detail="API v1 has been sunset. Use /api/v2/users"
    )
```

**Prevention:**
- Always version APIs from the start (/v1)
- Announce deprecations 6-12 months in advance
- Maintain old versions for compatibility period
- Document migration path clearly

---

### Issue: N+1 query problem in API responses

**Symptoms:**
- Slow response times for nested resources
- Database connection pool exhausted
- Hundreds of queries for single endpoint

**Solution:**
```python
# BAD - N+1 queries
@app.get("/api/v1/users")
async def get_users_bad():
    users = db.query(User).all()  # 1 query
    result = []
    for user in users:
        posts = db.query(Post).filter(Post.user_id == user.id).all()  # N queries
        result.append({"user": user, "posts": posts})
    return result

# GOOD - Eager loading
from sqlalchemy.orm import joinedload

@app.get("/api/v1/users")
async def get_users_good():
    users = db.query(User).options(
        joinedload(User.posts)  # Load posts in same query
    ).all()  # 1-2 queries total
    
    return [{
        "user": user,
        "posts": user.posts  # Already loaded
    } for user in users]

# BETTER - Use DataLoader pattern (GraphQL)
from aiodataloader import DataLoader

class PostLoader(DataLoader):
    async def batch_load_fn(self, user_ids):
        # Load all posts for multiple users at once
        posts = await db.query(Post).filter(
            Post.user_id.in_(user_ids)
        ).all()
        
        # Group by user_id
        posts_by_user = defaultdict(list)
        for post in posts:
            posts_by_user[post.user_id].append(post)
        
        return [posts_by_user[user_id] for user_id in user_ids]
```

**Prevention:**
- Use ORM eager loading (joinedload, selectinload)
- Implement DataLoader pattern
- Monitor query counts in development
- Add query count assertions in tests

---

## Examples

### Example 1: RESTful User Management API

**Context:** Building user management for SaaS application

**Implementation:**
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI(title="User Management API", version="1.0.0")

# Models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "member"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

# Endpoints
@app.get("/api/v1/users", response_model=List[User], tags=["Users"])
async def list_users(
    page: int = 1,
    per_page: int = 20,
    role: Optional[str] = None,
    search: Optional[str] = None
):
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(User.name.contains(search))
    
    total = query.count()
    users = query.offset((page-1)*per_page).limit(per_page).all()
    
    return users

@app.get("/api/v1/users/{user_id}", response_model=User, tags=["Users"])
async def get_user(user_id: int):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/v1/users", response_model=User, status_code=201, tags=["Users"])
async def create_user(user: UserCreate):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user

@app.patch("/api/v1/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(user_id: int, updates: dict):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404)
    
    for key, value in updates.items():
        setattr(user, key, value)
    
    db.commit()
    return user

@app.delete("/api/v1/users/{user_id}", status_code=204, tags=["Users"])
async def delete_user(user_id: int):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404)
    
    db.delete(user)
    db.commit()
    return
```

**Result:** 
- Full CRUD operations
- Pagination and filtering
- Proper status codes
- Auto-generated OpenAPI docs
- Type-safe requests/responses

---

### Example 2: GraphQL API Design

**Context:** Building flexible API for mobile and web clients

**Implementation:**
```python
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

# GraphQL Types
class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User

class Query(graphene.ObjectType):
    users = graphene.List(
        UserType,
        first=graphene.Int(),
        after=graphene.String(),
        role=graphene.String()
    )
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    
    def resolve_users(self, info, first=20, after=None, role=None):
        query = User.query
        
        if role:
            query = query.filter(User.role == role)
        if after:
            query = query.filter(User.id > after)
        
        return query.limit(first).all()
    
    def resolve_user(self, info, id):
        return User.query.get(id)

class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        name = graphene.String(required=True)
        role = graphene.String()
    
    user = graphene.Field(UserType)
    
    def mutate(self, info, email, name, role="member"):
        user = User(email=email, name=name, role=role)
        db.session.add(user)
        db.session.commit()
        return CreateUser(user=user)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# Usage
"""
query {
  users(first: 10, role: "admin") {
    id
    name
    email
    posts {
      title
    }
  }
}

mutation {
  createUser(email: "user@example.com", name: "John Doe") {
    user {
      id
      name
    }
  }
}
"""
```

**Result:**
- Flexible field selection
- No over-fetching
- Single endpoint
- Strong typing
- Built-in introspection

---

## Best Practices

### DO:
✅ Use nouns for resources, HTTP verbs for actions
✅ Version APIs from the start (/api/v1)
✅ Return appropriate HTTP status codes
✅ Implement pagination for all list endpoints
✅ Use JWT or OAuth2 for authentication
✅ Document all endpoints with OpenAPI/Swagger
✅ Validate all inputs server-side
✅ Use HTTPS in production (always)
✅ Implement rate limiting
✅ Add proper error messages with request IDs
✅ Use consistent naming conventions (camelCase JSON)
✅ Support filtering, sorting, field selection
✅ Add deprecation warnings before breaking changes

### DON'T:
❌ Put verbs in REST URLs (`/getUsers`)
❌ Expose database schema directly
❌ Use GET for operations that change data
❌ Return 200 OK for all responses
❌ Skip authentication on "internal" APIs
❌ Hard-code API keys or secrets
❌ Ignore CORS in browser clients
❌ Return stack traces to clients
❌ Skip validation on trusted inputs
❌ Use sequential IDs (use UUIDs for public APIs)
❌ Mix snake_case and camelCase
❌ Build your own auth system (use proven libraries)

---

## Related Workflows

**Prerequisites:**
- `arc-009`: Architecture Decision Records - Document API design decisions
- `dev-004`: Third Party API Integration - Understanding API consumption

**Next Steps:**
- `arc-003`: Caching Strategy Implementation - Add caching to APIs
- `devops-008`: Application Performance Monitoring - Monitor API performance
- `qa-008`: Integration Testing - Test API endpoints

**Alternatives:**
- GraphQL instead of REST for flexible queries
- gRPC for high-performance service-to-service
- WebSockets for real-time bidirectional communication

---

## Tags
`architecture` `api-design` `rest` `graphql` `best-practices` `openapi` `swagger` `authentication` `versioning` `http`
