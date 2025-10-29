---
id: dev-016
category: Development
subcategory: AI Collaboration
title: Pair Programming with AI
description: Apply traditional pair programming methodology with AI assistants for enhanced learning, code quality, and productivity
priority: MEDIUM
complexity: Moderate
estimated_time: 60-120 minutes per session
tags: [development, ai, pair-programming, collaboration, knowledge-transfer, claude, copilot]
prerequisites:
  - AI coding assistant (Claude, GitHub Copilot, etc.)
  - Understanding of pair programming concepts
  - Active development task
  - Version control setup
related_workflows:
  - ai_assisted_session
  - code_review
  - knowledge_transfer
  - developer_onboarding
created: 2025-10-25
updated: 2025-10-25
---

# Pair Programming with AI

## Overview

**What:** Structured approach to pair programming with AI using driver-navigator methodology

**Why:**
- Combine human creativity with AI speed
- Maintain code quality through continuous review
- Accelerate learning and skill development
- Reduce bugs through real-time feedback
- Build better understanding through explanation

**When to use:**
- Learning new technologies or frameworks
- Tackling complex technical challenges
- Onboarding to unfamiliar codebases
- Developing critical features requiring high quality
- Knowledge transfer sessions
- Debugging difficult issues

**Traditional Pair Programming Roles:**
- **Driver:** Writes code, focuses on implementation details
- **Navigator:** Reviews code, thinks strategically, catches errors

**AI Pair Programming Variations:**
- **You as Driver, AI as Navigator:** You code, AI reviews and suggests
- **AI as Driver, You as Navigator:** AI codes, you guide and review
- **Ping-Pong:** Alternate between driver and navigator roles

---

## Prerequisites

**Required:**
- [ ] AI coding assistant with conversational capability
- [ ] Clear development task or learning goal
- [ ] Git repository for version control
- [ ] Testing framework available
- [ ] Development environment setup

**Check before starting:**
```bash
# Verify setup
git status
python --version  # or your language
pytest --version  # or test framework

# Ensure AI assistant is responsive
# Test with a simple query
```

**Recommended:**
- [ ] Screen sharing tool (if pairing with another human reviewing AI session)
- [ ] Note-taking tool for learning
- [ ] Timer for session management
- [ ] Quiet, focused workspace

---

## Implementation Steps

### Step 1: Session Setup and Role Selection

**What:** Define the session scope, goals, and decide who drives first

**How:**
1. **Define the session goal** - What will you accomplish?
2. **Choose the pairing style** - Driver-navigator, ping-pong, etc.
3. **Set time limit** - Typically 60-120 minutes
4. **Establish communication pattern** - How will you interact?

**Session Planning Template:**
```markdown
# Pairing Session Plan

**Date:** 2025-10-25
**Duration:** 90 minutes
**Goal:** Implement user authentication for FastAPI app

**Style:** AI as Navigator (I drive, AI reviews)
**Why:** I need to learn FastAPI patterns hands-on

**Success Criteria:**
- [ ] Auth routes implemented
- [ ] Tests passing
- [ ] I understand all the code
- [ ] Ready for code review

**Learning Goals:**
- Understand FastAPI dependencies
- Learn JWT implementation
- Practice security best practices
```

**Choosing the Right Style:**
```markdown
# AI as Navigator (You Drive)
Best for:
- Learning new concepts hands-on
- Building muscle memory
- When you need deep understanding
- Maintaining creative control

Example prompt:
"I'll write the code, you review and suggest improvements as I go"

# AI as Driver (You Navigate)
Best for:
- Exploring possibilities quickly
- When you're stuck on implementation
- Generating boilerplate
- Learning by reading code

Example prompt:
"You write code, I'll tell you what to implement next and review it"

# Ping-Pong
Best for:
- TDD (Test-Driven Development)
- Complex problems requiring multiple perspectives
- Maximizing learning

Example pattern:
"I'll write a test, you implement code to pass it, 
then you write next test, I implement. Let's alternate."
```

**Verification:**
- [ ] Clear session goal defined
- [ ] Role distribution decided
- [ ] Time box set
- [ ] AI assistant ready and responsive

**If This Fails:**
→ Start with simpler goal
→ Break into multiple shorter sessions
→ Try different pairing style

---

### Step 2: Context Sharing and Alignment

**What:** Ensure AI understands your codebase, standards, and goals

**How:**
1. **Share codebase structure** - Key files and architecture
2. **Explain coding standards** - Style, patterns, conventions
3. **Align on approach** - Discuss strategy before coding
4. **Set boundaries** - What AI should/shouldn't do

**Comprehensive Context Template:**
```markdown
# Context for AI Navigator

**Project Overview:**
- FastAPI REST API for task management
- PostgreSQL database with SQLAlchemy ORM
- Currently has basic CRUD for tasks
- Now adding user authentication

**Current Files:**
- main.py: FastAPI app initialization
- models.py: SQLAlchemy models
- database.py: DB connection
- routers/tasks.py: Task endpoints

**Coding Standards:**
- Type hints on all functions
- Google-style docstrings
- Black formatting (88 char line length)
- Pytest for testing
- Follow REST conventions

**Architecture Decisions:**
- Use JWT tokens (not sessions)
- OAuth2 password flow
- Bcrypt for password hashing
- Separate routers for different resources

**Your Role as Navigator:**
- Review my code as I write it
- Suggest improvements immediately
- Catch security issues
- Point out edge cases
- Help me understand FastAPI patterns
```

**Alignment Conversation:**
```markdown
You: "Before I start, let's discuss approach. For user auth, 
     I'm thinking: Pydantic models → password utils → auth routes. 
     Sound good?"

AI: "Good structure. I'd suggest also adding:
     1. User model in models.py first
     2. Then auth dependencies for protected routes
     3. Consider refresh tokens from the start
     
     Want to start with the User model?"

You: "Yes, but let's skip refresh tokens for v1. 
     I'll start with the User model now."
```

**Verification:**
- [ ] AI understands project structure
- [ ] Coding standards communicated
- [ ] Approach agreed upon
- [ ] Boundaries set

**If This Fails:**
→ Provide more context gradually
→ Reference specific files
→ Show examples from codebase

---

### Step 3: Driver-Navigator Interaction Pattern

**What:** Establish effective communication rhythm between you and AI

**How:**
1. **Driver announces intentions** - "I'm going to..."
2. **Navigator acknowledges and advises** - "Good, but consider..."
3. **Driver implements with commentary** - "Adding this..."
4. **Navigator provides real-time feedback** - "Watch out for..."

**Pattern A: You Drive, AI Navigates**

**Effective Communication:**
```python
# You (Driver):
"I'm going to create the User model now. 
Starting with basic fields: email, hashed_password, full_name."

# AI (Navigator):
"Good start. Consider adding:
- unique constraint on email
- created_at timestamp
- is_active boolean for account status
Also, use EmailStr from pydantic for email validation"

# You (Driver) - implementing:
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)  # Added unique
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)  # Added
    created_at = Column(DateTime, server_default=func.now())  # Added
    
# You: "Added your suggestions. Look good?"

# AI (Navigator):
"Looks good! One more suggestion: Add __repr__ for debugging.
Also, you might want username field or keep just email?"

# You: "Let's keep just email. Adding __repr__ now..."
```

**Pattern B: AI Drives, You Navigate**

**Effective Communication:**
```python
# You (Navigator):
"Create a Pydantic schema for user creation. 
Include email validation and password requirements."

# AI (Driver):
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

# You (Navigator): "Good, but let's relax password requirements for now.
# Just check minimum length. We can add complexity later."

# AI (Driver):
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=200)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepass123",
                "full_name": "John Doe"
            }
        }

# You: "Perfect. Now let's move to password hashing utilities."
```

**Pattern C: Ping-Pong (TDD Style)**

**Effective Communication:**
```python
# You write test:
def test_user_creation():
    """Test creating a new user"""
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    user = create_user(**user_data)
    
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.hashed_password != "password123"  # Should be hashed
    assert user.is_active is True

# AI implements to pass:
def create_user(email: str, password: str, full_name: str) -> User:
    """Create a new user with hashed password"""
    from auth import hash_password
    
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=True
    )
    return user

# AI writes next test:
def test_user_creation_duplicate_email():
    """Test that duplicate emails are rejected"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "User 1"
    }
    create_user(**user_data)
    
    # Should raise error on duplicate
    with pytest.raises(IntegrityError):
        create_user(**user_data)

# You implement to pass:
# ... (add duplicate check logic)
```

**Verification:**
- [ ] Clear communication rhythm established
- [ ] Both parties contributing effectively
- [ ] Questions and feedback flowing smoothly
- [ ] Code quality maintained

**If This Fails:**
→ Slow down, be more explicit
→ Ask AI to explain suggestions
→ Switch roles if stuck

---

### Step 4: Continuous Code Review

**What:** Maintain quality through ongoing review during development

**How:**
1. **Review as you go** - Don't wait until end
2. **Question everything** - Both parties challenge decisions
3. **Explain reasoning** - "I'm doing X because..."
4. **Catch issues early** - Security, bugs, design problems

**Real-Time Review Techniques:**

**Technique 1: Think Aloud Protocol**
```python
# You (Driver):
"I'm adding this function to hash passwords. 
Using bcrypt because it's the industry standard.
Setting cost factor to 12 for good security-performance balance."

def hash_password(password: str) -> str:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

# AI (Navigator):
"Good reasoning. Three points:
1. Consider making pwd_context global to avoid recreating
2. Add type hints and docstring
3. What about very long passwords? Might want max length"

# You: "Good catches. Refactoring now..."
```

**Technique 2: Challenge Assumptions**
```python
# AI (Driver):
def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

# You (Navigator):
"Wait, this has a timing attack vulnerability.
It takes longer to verify wrong password for existing user
than for non-existent user. Can you fix?"

# AI: "Excellent catch! Here's a constant-time version:"
def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    
    # Always verify, even if user doesn't exist
    if user is None:
        # Dummy verify to maintain constant time
        verify_password(password, "dummy_hash")
        return None
    
    if verify_password(password, user.hashed_password):
        return user
    return None
```

**Technique 3: Edge Case Exploration**
```python
# You: "What edge cases should we handle?"

# AI: "For user creation, consider:
# - Empty email
# - Invalid email format
# - Very long names
# - SQL injection attempts
# - Unicode characters in names
# - Null values
# - Duplicate registration attempts"

# You: "Let's add validation for these..."
```

**Review Checklist for Navigator:**
```markdown
During coding, check:
- [ ] Code matches intended functionality
- [ ] Security considerations addressed
- [ ] Error handling present
- [ ] Edge cases handled
- [ ] Code is readable and maintainable
- [ ] Performance implications considered
- [ ] Tests will pass (mental check)
- [ ] Follows project conventions
- [ ] No obvious bugs
- [ ] Could be simpler?
```

**Verification:**
- [ ] Code reviewed continuously
- [ ] Issues caught early
- [ ] Both parties engaged in review
- [ ] Quality standards maintained

**If This Fails:**
→ Pause and do formal review
→ Slow down implementation pace
→ Ask more questions

---

### Step 5: Knowledge Transfer and Learning

**What:** Maximize learning through active teaching and explanation

**How:**
1. **Explain your reasoning** - Make thinking visible
2. **Ask "why" questions** - Understand, don't just copy
3. **Request explanations** - "How does this work?"
4. **Document learnings** - Capture insights

**Learning Techniques:**

**Technique 1: Rubber Duck Explanation**
```python
# You (Driver): "Let me explain what I'm doing...
# I'm creating a dependency that validates JWT tokens.
# It will be used to protect routes that need authentication.
# FastAPI will call this for each protected endpoint request."

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT token and return current user"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

# AI (Navigator): "Good explanation. To deepen understanding:
# - Why use 'sub' claim for user ID?
# - What happens if token expires?
# - How does Depends() work in FastAPI?"

# You: "Good questions, let me research 'sub' claim..."
```

**Technique 2: Reverse Engineering**
```python
# AI provides code
def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# You: "Before I accept this, let me understand:
# 1. What's the structure of the JWT payload?
# 2. Why convert user_id to string?
# 3. What happens when token expires?
# 4. Can this token be refreshed?"

# AI explains each point...

# You: "Got it. So JWT has header, payload, signature.
# Payload has 'sub' (subject) and 'exp' (expiration).
# I need to add refresh token functionality separately."
```

**Technique 3: Teaching Back**
```python
# After implementing a feature, teach it back:

# You: "Let me explain the auth flow we just built:
# 1. User sends email/password to /token endpoint
# 2. We verify credentials using authenticate_user()
# 3. If valid, create JWT with create_access_token()
# 4. Return token to user
# 5. User includes token in Authorization header
# 6. Protected routes use get_current_user() dependency
# 7. Dependency validates token and returns user object
# 
# Did I get that right?"

# AI: "Perfect explanation! You understand the flow.
# One addition: The token includes expiration time,
# so old tokens automatically become invalid."
```

**Documentation of Learnings:**
```markdown
# Learning Log - FastAPI Authentication

## Key Concepts Learned
1. **FastAPI Dependencies:**
   - Depends() injects values into route functions
   - Used for auth, database sessions, config
   - Executed before route handler
   
2. **JWT Tokens:**
   - Stateless authentication
   - Contains claims (sub, exp, etc.)
   - Signed with secret key
   - Can't be modified without detection

3. **OAuth2 Password Flow:**
   - Standard auth pattern
   - POST to /token with credentials
   - Returns access_token and token_type
   - Include in header: "Bearer {token}"

## Patterns to Reuse
- Dependency injection for auth
- Pydantic for request validation
- Context managers for DB sessions

## Questions Resolved
Q: Why not use sessions?
A: JWT is stateless, scales better

Q: How to handle token refresh?
A: Need separate refresh token endpoint

## Next Steps
- Implement refresh tokens
- Add role-based access control
- Set up token blacklisting
```

**Verification:**
- [ ] Understanding deepened
- [ ] Can explain key concepts
- [ ] Patterns documented
- [ ] Questions answered

**If This Fails:**
→ Slow down, ask more questions
→ Research concepts independently
→ Request simpler explanations

---

### Step 6: Debugging Together

**What:** Collaborate on solving problems and bugs

**How:**
1. **Reproduce the issue** - Get clear error messages
2. **Form hypotheses** - What could be wrong?
3. **Test systematically** - Verify each hypothesis
4. **Learn from errors** - Understand root cause

**Collaborative Debugging:**

**Step 1: Share the Problem**
```python
# You: "I'm getting this error:"
"""
ValueError: Invalid JWT token
  File "auth.py", line 45, in get_current_user
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
"""

# AI: "Let's debug systematically:
# 1. Is the token being sent correctly?
# 2. Is the token format valid?
# 3. Is the SECRET_KEY correct?
# 4. Is the algorithm matching?
# 
# Can you print the token and SECRET_KEY? (Not in production!)"
```

**Step 2: Hypothesis Testing**
```python
# You add debugging:
async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"Received token: {token[:20]}...")  # First 20 chars
    print(f"SECRET_KEY set: {bool(SECRET_KEY)}")
    print(f"ALGORITHM: {ALGORITHM}")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # ...

# You: "Token is present, SECRET_KEY is set, algorithm is 'HS256'"

# AI: "Try printing the full token validation error:
except JWTError as e:
    print(f"JWT Error: {e}")
    print(f"Token: {token}")
    raise credentials_exception"

# You run it...
# Output: "JWT Error: Signature has expired"

# AI: "Ah! Token expired. Let's check TOKEN_EXPIRE_MINUTES setting."
```

**Step 3: Root Cause Analysis**
```python
# You: "ACCESS_TOKEN_EXPIRE_MINUTES = 1  # Found the issue!"

# AI: "That's very short. For development, use 30-60 minutes.
# For production, 15-30 minutes with refresh tokens.
# 
# Also, the error message could be clearer.
# Should we catch ExpiredSignatureError separately?"

# You: "Yes, let's improve error handling:"
from jwt import ExpiredSignatureError

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
except ExpiredSignatureError:
    raise HTTPException(
        status_code=401,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
except JWTError:
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

**Debugging Collaboration Patterns:**
```markdown
# When Stuck Pattern
1. State the problem clearly
2. Share all error messages
3. Show relevant code
4. Describe what you've tried
5. AI suggests approaches
6. Test each suggestion
7. Iterate

# Rubber Duck Debugging Pattern
You: "Walking through the code:
1. User logs in, gets token ✓
2. Token stored in frontend ✓
3. Token sent in header... wait, is the header format correct?"

AI: "Good catch! Show me the header format."

You: "Authorization: {token}"

AI: "Missing 'Bearer' prefix. Should be:
Authorization: Bearer {token}"
```

**Verification:**
- [ ] Bug identified and fixed
- [ ] Root cause understood
- [ ] Prevention strategy identified
- [ ] Learning documented

**If This Fails:**
→ Take a break, come back fresh
→ Search for similar issues online
→ Try minimal reproduction

---

### Step 7: Testing Together

**What:** Collaborate on test creation and validation

**How:**
1. **Define test cases together** - What should we test?
2. **Implement tests** - Follow TDD if possible
3. **Run and review** - Analyze failures together
4. **Improve coverage** - Identify gaps

**Collaborative Testing:**

**Test Planning:**
```python
# You: "What tests do we need for user authentication?"

# AI: "Let's cover these scenarios:

# Happy Path:
# - Valid credentials → successful auth
# - Valid token → access granted

# Error Cases:
# - Invalid email → 401
# - Wrong password → 401
# - Expired token → 401
# - Malformed token → 401
# - Missing token → 401
# - Nonexistent user → 401

# Edge Cases:
# - Very long password
# - Special characters in email
# - Case sensitivity of email

# Let's start with happy path. Want to drive or navigate?"
```

**You Drive Tests:**
```python
# You write test, AI reviews:

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_successful_login():
    """Test login with valid credentials"""
    # First, create a user
    response = client.post("/users/", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    
    # Now try to login
    response = client.post("/token", data={
        "username": "test@example.com",  # OAuth2 uses 'username'
        "password": "password123"
    })
    
    # AI: "Good structure. Add these assertions:"
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # AI: "Also test that the token works:"
    token = data["access_token"]
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

**AI Drives Tests:**
```python
# You: "Write tests for invalid credentials"

# AI provides:
def test_login_invalid_email():
    """Test login with non-existent email"""
    response = client.post("/token", data={
        "username": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 401
    assert "detail" in response.json()

def test_login_wrong_password():
    """Test login with wrong password"""
    # Create user first
    client.post("/users/", json={
        "email": "test2@example.com",
        "password": "correct_password",
        "full_name": "Test User 2"
    })
    
    # Try wrong password
    response = client.post("/token", data={
        "username": "test2@example.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401

# You: "Good! What about testing token expiration?"

# AI: "That's tricky. We'd need to mock time or set very short expiration.
# Here's an approach using freezegun..."
```

**Coverage Analysis Together:**
```bash
# Run coverage
pytest --cov=. --cov-report=html

# You: "We're at 85% coverage. What are we missing?"

# AI: "Looking at the report, we're not testing:
# 1. Password hashing edge cases (empty string, very long)
# 2. Token refresh functionality (not implemented yet)
# 3. Error handling in database operations
# 4. Concurrent login attempts
# 
# Which should we prioritize?"

# You: "Let's add password hashing tests first."
```

**Verification:**
- [ ] Comprehensive test suite created
- [ ] All tests passing
- [ ] Edge cases covered
- [ ] Coverage acceptable (>80%)

**If This Fails:**
→ Break down into smaller test units
→ Fix failing tests before continuing
→ Simplify test setup

---

### Step 8: Session Wrap-up and Retrospective

**What:** Review accomplishments, extract learnings, plan next steps

**How:**
1. **Review what was built** - Working code/features
2. **Capture learnings** - What did you learn?
3. **Identify patterns** - What worked well?
4. **Plan next session** - What's left to do?

**Session Review:**
```markdown
# Pairing Session Retrospective

**Session:** 2025-10-25 (90 minutes)
**Goal:** Implement user authentication
**Style:** Alternating driver-navigator

## Accomplished ✅
- [x] User model with SQLAlchemy
- [x] Pydantic schemas for request/response
- [x] Password hashing utilities
- [x] JWT token generation
- [x] Login endpoint
- [x] Protected route with auth dependency
- [x] Comprehensive test suite (87% coverage)

## Technical Learnings 📚
1. FastAPI dependency injection system
2. JWT token structure and validation
3. OAuth2 password flow implementation
4. Bcrypt password hashing
5. pytest fixtures for test setup

## Collaboration Learnings 🤝
**What Worked Well:**
- Alternating roles kept us both engaged
- AI caught security issues early
- Explaining code deepened understanding
- TDD approach maintained quality

**What Could Improve:**
- Spent too long debating token expiration
- Should have set up test database earlier
- Could use more code examples upfront

## Code Quality 🌟
**Strengths:**
- Clean, readable code
- Good test coverage
- Comprehensive error handling
- Security considerations addressed

**Technical Debt:**
- Need to add refresh tokens
- Should extract config to environment variables
- Database migrations not set up yet
- Missing rate limiting on login

## Best Practices Discovered 💡
1. **Always validate tokens explicitly**
   ```python
   # Don't trust tokens blindly
   user = get_current_user(token)
   if not user or not user.is_active:
       raise auth_error
   ```

2. **Use constant-time comparison for auth**
   ```python
   # Prevents timing attacks
   verify_password(provided, stored)
   # Better than: provided == stored
   ```

3. **Test auth flows end-to-end**
   ```python
   # Test full flow: register → login → access protected route
   ```

## Prompts That Worked Well 📝
1. "Explain this pattern before implementing"
2. "What security issues should I consider?"
3. "Review my code as I write it"
4. "What edge cases am I missing?"
5. "Can you simplify this?"

## Next Session Plan 📅
**Goal:** Add refresh tokens and rate limiting
**Estimated Time:** 60 minutes
**Style:** You drive, AI navigates (for learning)

**Tasks:**
1. Implement refresh token endpoint
2. Add token blacklisting
3. Add rate limiting with slowapi
4. Update tests
5. Add API documentation

**Preparation:**
- Read about refresh token patterns
- Review rate limiting strategies
- Set up Redis for token blacklisting
```

**Knowledge Transfer Document:**
```markdown
# FastAPI Authentication Implementation Guide

## Overview
Implemented JWT-based authentication following OAuth2 password flow.

## Architecture
```
User → POST /token → Validate credentials → Generate JWT → Return token
↓
User → GET /protected → Validate JWT → Execute route → Return response
```

## Key Components

### 1. User Model
- SQLAlchemy ORM model
- Fields: id, email, hashed_password, full_name, is_active, created_at
- Email is unique and indexed

### 2. Authentication Flow
```python
1. User provides email + password
2. authenticate_user() verifies credentials
3. create_access_token() generates JWT
4. Token returned to user
5. User includes token in Authorization header
6. get_current_user() dependency validates token
7. Protected routes execute
```

### 3. Security Measures
- Bcrypt password hashing (cost factor 12)
- JWT tokens with expiration
- Timing attack prevention
- Input validation with Pydantic
- HTTP-only cookies (optional)

## Code Locations
- `models.py`: User model
- `schemas.py`: Pydantic models
- `auth.py`: Auth utilities
- `routers/auth.py`: Auth endpoints
- `dependencies.py`: get_current_user
- `tests/test_auth.py`: Test suite

## Testing
```bash
pytest tests/test_auth.py -v --cov=auth
```

## Future Enhancements
1. Refresh tokens
2. Rate limiting
3. Two-factor authentication
4. Social auth (OAuth)
5. Role-based access control
```

**Verification:**
- [ ] Session accomplishments documented
- [ ] Learnings captured
- [ ] Code committed
- [ ] Next session planned
- [ ] Knowledge transferred

**If This Fails:**
→ At minimum, commit code and write summary

---

## Verification Checklist

After completing this workflow:

- [ ] Session goal achieved or progress made
- [ ] Code is working and tested
- [ ] Both parties learned something
- [ ] Quality maintained throughout
- [ ] Collaboration was effective
- [ ] Learnings documented
- [ ] Code reviewed and understood
- [ ] Tests passing
- [ ] Ready for next session or merge
- [ ] Retrospective completed

---

## Common Issues & Solutions

### Issue: AI Too Passive as Navigator

**Symptoms:**
- AI just says "looks good"
- Not catching issues
- Not providing valuable feedback

**Solution:**
```markdown
# Explicitly request active review:
"I want you to be a strict code reviewer.
Challenge my decisions.
Point out potential issues.
Suggest improvements even if code works.
Ask hard questions."
```

**Prevention:**
- Set expectations upfront
- Ask specific questions
- Request critique, not just approval

---

### Issue: AI Too Aggressive with Suggestions

**Symptoms:**
- Too many suggestions
- Interrupting flow
- Over-engineering solutions

**Solution:**
```markdown
# Set boundaries:
"Focus on critical issues only.
Let me make minor decisions.
Suggest improvements at natural stopping points.
Keep solutions simple unless I ask for advanced."
```

**Prevention:**
- Communicate your experience level
- Set review frequency preferences

---

### Issue: Losing Focus During Session

**Symptoms:**
- Scope creep
- Getting distracted by tangents
- Original goal forgotten

**Solution:**
```markdown
# Refocus prompt:
"Let's get back to our original goal: [goal].
We can explore [tangent] in a future session.
What's the next step toward our goal?"
```

**Prevention:**
- Write down goal and keep visible
- Set time boxes for exploration
- Review progress regularly

---

### Issue: One Person Dominating

**Symptoms:**
- AI doing all the work
- You not understanding the code
- Feeling like a spectator

**Solution:**
```markdown
# Switch roles:
"Stop. Let me drive for a while.
I'll implement the next feature.
You review and guide me."

# Or slow down:
"Explain this before moving forward.
I need to understand each step."
```

**Prevention:**
- Set role switching intervals
- Require understanding before continuing
- Ask "why" questions frequently

---

### Issue: Getting Stuck on Problems

**Symptoms:**
- Same issue for >15 minutes
- Multiple failed approaches
- Frustration building

**Solution:**
```markdown
# Reset approach:
"This approach isn't working.
Let's try a completely different strategy.
Or: Let's implement the simplest version first."

# Or seek external help:
"Can you suggest resources to learn this concept?
Let's research before implementing."
```

**Prevention:**
- Time box difficult problems
- Try simplest solution first
- Take breaks when stuck

---

## Examples

### Example 1: Learning New Framework (You Drive, AI Navigates)

**Scenario:** Learning React hooks for the first time

```javascript
// You: "I'm going to create a component with useState"
import React, { useState } from 'react';

function Counter() {
    // You: "Creating state for count..."
    const [count, setCount] = useState(0);
    
    // AI: "Good! useState returns [value, setter].
    // Now add a button to increment."
    
    // You: "Adding button..."
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                Increment
            </button>
        </div>
    );
}

// AI: "Works! But consider:
// 1. What if you need to increment by variable amount?
// 2. Should count have a max value?
// 3. Try using functional update: setCount(prev => prev + 1)
// Want to explore any of these?"

// You: "What's functional update and why?"
```

**Outcome:** Built working component while learning React patterns

---

### Example 2: Debugging Complex Issue (Collaborative)

**Scenario:** WebSocket connection keeps dropping

```python
# You: "WebSocket disconnects after 30 seconds every time"

# AI: "Let's debug systematically:
# 1. Check timeout settings
# 2. Look for connection keep-alive
# 3. Review error logs
# 4. Check network config
# 
# Start with server-side timeout?"

# You examine code:
app = FastAPI()
websocket_manager = WebSocketManager()  # default timeout?

# AI: "Check WebSocketManager implementation"

# You find:
class WebSocketManager:
    def __init__(self, timeout=30):  # Found it!
        self.timeout = timeout

# AI: "That's the issue! 30 second timeout.
# Increase it or implement ping/pong keep-alive."

# Together you implement:
class WebSocketManager:
    def __init__(self, timeout=300):  # 5 minutes
        self.timeout = timeout
        
    async def keep_alive(self, websocket):
        while True:
            await asyncio.sleep(20)
            await websocket.send_json({"type": "ping"})
```

**Outcome:** Found and fixed issue in 10 minutes through systematic collaboration

---

### Example 3: Building Feature (Ping-Pong TDD)

**Scenario:** Implementing shopping cart functionality

```python
# You write test:
def test_add_item_to_cart():
    cart = ShoppingCart()
    cart.add_item("apple", quantity=2, price=1.50)
    assert cart.total == 3.00
    assert len(cart.items) == 1

# AI implements:
class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, name, quantity, price):
        self.items.append({
            'name': name,
            'quantity': quantity,
            'price': price
        })
    
    @property
    def total(self):
        return sum(item['quantity'] * item['price'] 
                   for item in self.items)

# Tests pass! AI writes next test:
def test_add_duplicate_items():
    cart = ShoppingCart()
    cart.add_item("apple", quantity=2, price=1.50)
    cart.add_item("apple", quantity=1, price=1.50)
    # Should combine: 3 apples total
    assert cart.items[0]['quantity'] == 3
    assert len(cart.items) == 1

# You implement:
def add_item(self, name, quantity, price):
    # Check if item exists
    for item in self.items:
        if item['name'] == name and item['price'] == price:
            item['quantity'] += quantity
            return
    # New item
    self.items.append({...})

# Continue alternating...
```

**Outcome:** Well-tested feature built incrementally with clear design

---

## Best Practices

### DO:
✅ **Set clear goals and time limits**
✅ **Communicate intentions before acting**
✅ **Question and challenge suggestions**
✅ **Switch roles regularly**
✅ **Focus on understanding, not just completion**
✅ **Review code continuously**
✅ **Test as you go**
✅ **Take breaks when stuck**
✅ **Document learnings**
✅ **Celebrate progress**

### DON'T:
❌ **Blindly accept AI suggestions**
❌ **Let AI do all the work**
❌ **Skip explanation for speed**
❌ **Continue without understanding**
❌ **Ignore quality for quantity**
❌ **Work on multiple goals at once**
❌ **Keep same role entire session**
❌ **Skip retrospective**
❌ **Forget to commit code**
❌ **Ignore your instincts**

---

## Common Patterns

### Pattern 1: Structured Session Template

```markdown
**Pre-Session (5 min):**
- Set goal and success criteria
- Choose pairing style
- Gather context and resources
- Set timer

**Coding Session (60-90 min):**
- 25 min: Code with role A
- 5 min: Break
- 25 min: Code with role B (switched)
- 5 min: Break
- 25 min: Code with role A
- 5 min: Final review

**Retrospective (10 min):**
- Review accomplishments
- Capture learnings
- Plan next session
- Commit code
```

### Pattern 2: Learning-Focused Session

```markdown
1. AI explains concept
2. You implement while explaining your thinking
3. AI corrects misconceptions
4. You refactor to best practices
5. You teach concept back to AI
6. Document key learnings
```

### Pattern 3: Problem-Solving Session

```markdown
1. Define problem clearly
2. Brainstorm approaches together
3. Pick simplest approach
4. Implement incrementally
5. Test each increment
6. Debug together if issues
7. Refine solution
8. Document decision rationale
```

---

## Related Workflows

**Prerequisites:**
- [Environment Initialization](./environment_initialization.md) - Setup dev environment
- [Git Workflow](../version-control/branch_strategy.md) - Version control basics
- [Test Writing](./test_writing.md) - Testing fundamentals

**Next Steps:**
- [Code Review](../quality_assurance/code_review_checklist.md) - Review completed work
- [Refactoring Strategy](./refactoring_strategy.md) - Improve pair-programmed code
- [Knowledge Transfer](../project-management/knowledge_transfer.md) - Share learnings with team

**Alternatives:**
- [AI-Assisted Session](./ai_assisted_session.md) - Less structured AI collaboration
- Solo development with periodic AI consultation
- Traditional pair programming with human partner

---

## Tags
`development` `pair-programming` `ai` `collaboration` `learning` `knowledge-transfer` `code-quality` `tdd` `mentoring` `best-practices`

---

## Metadata
- **Workflow Type:** Collaborative Development Process
- **Skill Level:** Beginner to Advanced (adapts to experience)
- **Team Size:** 1 developer + AI
- **Frequency:** As needed for learning or complex tasks
- **Success Rate:** High with proper communication
