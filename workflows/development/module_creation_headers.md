# Module Creation with Headers

**ID:** dev-014  
**Category:** Development  
**Priority:** MEDIUM  
**Complexity:** Simple  
**Estimated Time:** 10-15 minutes  
**Frequency:** Per Module  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Create Python modules with proper headers, docstrings, type annotations, and standard imports following best practices for maintainability and documentation.

**Why:** Well-structured module headers improve code discoverability, maintainability, and enable better IDE support. They serve as the first line of documentation and set expectations for module usage.

**When to use:**
- Creating a new Python module (.py file)
- Refactoring existing code into separate modules
- Establishing code standards for a project
- When starting any new Python file in a codebase

---

## Prerequisites

**Required Knowledge:**
- [ ] Python basics (modules, imports, functions)
- [ ] Understanding of docstrings and PEP 257
- [ ] Basic knowledge of type hints (PEP 484)

**Required Tools:**
- [ ] Python 3.8+ installed
- [ ] Text editor or IDE with Python support
- [ ] (Optional) `mypy` for type checking
- [ ] (Optional) `ruff` or `pylint` for linting

**Check before starting:**
```bash
python --version  # Should show 3.8+
# Optional tools
pip list | grep mypy
pip list | grep ruff
```

---

## Implementation Steps

### Step 1: Create Module with Basic Header

**What:** Set up the file with module-level docstring and metadata

**How:**
1. Create a new .py file with a descriptive name (use snake_case)
2. Add module-level docstring at the very top
3. Include basic metadata if applicable

**Example:**
```python
"""
Module for handling user authentication and authorization.

This module provides functions and classes for:
- User login/logout
- Token generation and validation
- Permission checking
- Session management

Typical usage example:
    from myapp.auth import authenticate_user, generate_token
    
    user = authenticate_user(username, password)
    if user:
        token = generate_token(user)
```

**Verification:**
- [ ] Docstring is the first thing in the file
- [ ] Docstring describes module purpose clearly
- [ ] Usage example provided (if applicable)

---

### Step 2: Add Module-Level Metadata (Optional)

**What:** Include authorship, versioning, and license information if required by your project

**How:**
```python
"""
Module for handling user authentication.

[docstring content here]
"""

__author__ = "Your Name"
__version__ = "1.0.0"
__maintainer__ = "Your Name"
__email__ = "your.email@example.com"
__status__ = "Production"  # or "Development", "Prototype"
__license__ = "MIT"  # or your project's license

# Alternative minimal approach:
__all__ = ["authenticate_user", "generate_token", "User"]
```

**Verification:**
- [ ] Metadata is after docstring but before imports
- [ ] `__all__` explicitly defines public API (recommended)

**If This Fails:**
→ Metadata is optional; skip if not required by project standards

---

### Step 3: Organize Imports with Standard Grouping

**What:** Add imports in the standard order with proper grouping

**How:**
Import order per PEP 8:
1. Standard library imports
2. Related third-party imports
3. Local application/library specific imports

```python
"""Module docstring here."""

__all__ = ["UserAuth", "authenticate", "generate_token"]

# Standard library imports
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

# Third-party imports
import jwt
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

# Local application imports
from myapp.config import settings
from myapp.database import get_db
from myapp.models import User
from myapp.schemas import UserCreate, UserResponse
```

**Verification:**
- [ ] Imports grouped into three sections
- [ ] Blank lines separate groups
- [ ] Imports sorted alphabetically within each group
- [ ] No wildcard imports (avoid `from module import *`)

---

### Step 4: Add Type Annotations and Constants

**What:** Define module-level constants and type aliases

**How:**
```python
"""Module docstring."""

__all__ = ["UserAuth", "authenticate"]

# Standard library imports
from typing import Optional, Dict, Any, TypeAlias
from datetime import timedelta

# Third-party imports
import jwt
from pydantic import BaseModel

# Local imports
from myapp.config import settings

# Module-level constants
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Type aliases for clarity
TokenPayload: TypeAlias = Dict[str, Any]
UserID: TypeAlias = int

# Configuration
TOKEN_EXPIRE_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
```

**Verification:**
- [ ] Constants in UPPER_CASE
- [ ] Type annotations on constants
- [ ] Constants grouped logically
- [ ] Type aliases defined for complex types

---

### Step 5: Add Main Function/Class Definitions with Docstrings

**What:** Implement the core functionality with comprehensive docstrings

**How:**
```python
def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username to authenticate
        password: The plaintext password to verify
        db: Database session for querying
        
    Returns:
        User object if authentication succeeds, None otherwise
        
    Raises:
        ValueError: If username or password is empty
        DatabaseError: If database connection fails
        
    Example:
        >>> db = get_db()
        >>> user = authenticate_user("john_doe", "secret123", db)
        >>> if user:
        ...     print(f"Welcome {user.username}")
    """
    if not username or not password:
        raise ValueError("Username and password cannot be empty")
    
    user = db.query(User).filter(User.username == username).first()
    if user and user.verify_password(password):
        return user
    return None


class UserAuth:
    """
    Handle user authentication and token management.
    
    This class provides methods for authenticating users and managing
    JWT tokens for API authentication.
    
    Attributes:
        secret_key: Secret key for JWT encoding/decoding
        algorithm: Algorithm used for JWT encoding
        
    Example:
        >>> auth = UserAuth(SECRET_KEY)
        >>> token = auth.create_token(user_id=123)
        >>> payload = auth.decode_token(token)
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        """
        Initialize UserAuth with secret key and algorithm.
        
        Args:
            secret_key: Secret key for JWT operations
            algorithm: JWT algorithm to use (default: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT token for a user.
        
        Args:
            user_id: ID of the user to create token for
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
            
        Raises:
            JWTError: If token creation fails
        """
        # Implementation here
        pass
```

**Verification:**
- [ ] All functions have docstrings
- [ ] Docstrings include Args, Returns, Raises sections
- [ ] Type annotations on all parameters and returns
- [ ] Examples provided for complex functions

---

### Step 6: Add Module-Level Guard Clause (if applicable)

**What:** Add code to run when module is executed directly

**How:**
```python
# ... rest of module code ...

def main() -> None:
    """
    Main function for CLI or testing purposes.
    
    This function is called when the module is run directly.
    """
    # Example usage or testing code
    print("Testing authentication module...")
    # Add your test code here


if __name__ == "__main__":
    main()
```

**Verification:**
- [ ] Main function has docstring
- [ ] Guard clause is at the end of file
- [ ] Main function is for testing/CLI only

**If This Fails:**
→ Skip this step if module is library code only (not meant to be executed)

---

## Verification Checklist

After creating the module, verify:

- [ ] Module docstring is first thing in file
- [ ] `__all__` defines public API (if applicable)
- [ ] Imports organized in 3 groups (stdlib, third-party, local)
- [ ] No wildcard imports (`from x import *`)
- [ ] Constants defined in UPPER_CASE with type annotations
- [ ] All functions/classes have comprehensive docstrings
- [ ] Type annotations on all function signatures
- [ ] Examples included in complex function docstrings
- [ ] Code passes `ruff check` or `pylint` (if used)
- [ ] Code passes `mypy` type checking (if used)

---

## Common Issues & Solutions

### Issue 1: Import Order Confusion

**Symptoms:**
- Linter warnings about import order
- Inconsistent import organization

**Solution:**
Use `isort` to automatically organize imports:
```bash
pip install isort
isort mymodule.py

# Or configure in pyproject.toml:
[tool.isort]
profile = "black"
line_length = 100
```

---

### Issue 2: Docstring Format Inconsistency

**Symptoms:**
- Different docstring styles across codebase
- IDE not recognizing docstring format

**Solution:**
Choose and stick to one style (Google, NumPy, or reStructuredText):

**Google Style (Recommended):**
```python
def func(arg1: str, arg2: int) -> bool:
    """
    Summary line.
    
    Extended description.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When input is invalid
    """
```

**NumPy Style:**
```python
def func(arg1: str, arg2: int) -> bool:
    """
    Summary line.
    
    Parameters
    ----------
    arg1 : str
        Description of arg1
    arg2 : int
        Description of arg2
        
    Returns
    -------
    bool
        Description of return value
    """
```

---

### Issue 3: Type Annotation Errors

**Symptoms:**
- `mypy` errors on type hints
- IDE showing type warnings

**Solution:**
```python
# Use Optional for nullable values
from typing import Optional
def get_user(user_id: int) -> Optional[User]:
    # ...

# Use Union for multiple possible types
from typing import Union
def process(data: Union[str, int, None]) -> str:
    # ...

# Use List, Dict, etc. for containers
from typing import List, Dict
def get_items() -> List[Dict[str, Any]]:
    # ...

# For Python 3.10+, use built-in types
def get_items() -> list[dict[str, Any]]:
    # ...
```

---

## Best Practices

### DO:
✅ Always include module-level docstring  
✅ Use `__all__` to define public API explicitly  
✅ Group imports in standard order (stdlib, third-party, local)  
✅ Add type annotations to all function signatures  
✅ Include usage examples in docstrings for complex functions  
✅ Use descriptive names that indicate module purpose  
✅ Keep module focused on single responsibility  
✅ Add constants at module level (not scattered in functions)

### DON'T:
❌ Use wildcard imports (`from module import *`)  
❌ Mix different docstring styles in same project  
❌ Leave functions without docstrings  
❌ Forget type annotations on parameters and returns  
❌ Create modules with too many unrelated functions  
❌ Use overly generic names like `utils.py` or `helpers.py`  
❌ Skip the module docstring  
❌ Put executable code at module level (use `if __name__ == "__main__"`)

---

## Examples

### Example 1: Simple Utility Module

```python
"""
Utility functions for string manipulation.

Provides common string operations like slugification,
truncation, and sanitization.
"""

__all__ = ["slugify", "truncate", "sanitize"]

import re
from typing import Optional

# Constants
MAX_SLUG_LENGTH: int = 50
DEFAULT_TRUNCATE_LENGTH: int = 100

def slugify(text: str, max_length: int = MAX_SLUG_LENGTH) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to convert to slug
        max_length: Maximum length of slug
        
    Returns:
        Slugified string (lowercase, hyphenated)
        
    Example:
        >>> slugify("Hello World!")
        'hello-world'
    """
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug[:max_length]

def truncate(text: str, length: int = DEFAULT_TRUNCATE_LENGTH, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length (including suffix)
        suffix: String to append when truncated
        
    Returns:
        Truncated string with suffix if needed
        
    Example:
        >>> truncate("This is a long text", 10)
        'This is...'
    """
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix
```

---

### Example 2: Complex Service Module

```python
"""
User authentication service with JWT token management.

This module provides complete authentication functionality including
user verification, token generation, and session management.
"""

__all__ = ["AuthService", "authenticate", "create_access_token"]

# Standard library
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Third-party
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Local imports
from myapp.config import settings
from myapp.models.user import User
from myapp.schemas.auth import TokenData

# Constants
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Service for handling user authentication.
    
    Provides methods for password verification, token generation,
    and user authentication workflows.
    
    Example:
        >>> service = AuthService()
        >>> user = service.authenticate("username", "password")
        >>> token = service.create_token(user.id)
    """
    
    def __init__(self) -> None:
        """Initialize authentication service."""
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in token (typically user_id)
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
            
        Raises:
            JWTError: If token encoding fails
            
        Example:
            >>> token = service.create_access_token({"sub": "123"})
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Convenience function for direct import
def authenticate(username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password.
    
    Args:
        username: Username to authenticate
        password: Plain text password
        
    Returns:
        User object if authentication succeeds, None otherwise
    """
    service = AuthService()
    # Implementation...
    return None
```

---

## Related Workflows

**Before This Workflow:**
- [[dev-022]](environment_initialization.md) - Set up development environment first
- [[dev-023]](new_repo_scaffolding.md) - Create project structure

**After This Workflow:**
- [[dev-004]](type_annotation_addition.md) - Add comprehensive type hints
- [[dev-002]](test_writing.md) - Write tests for the module
- [[qua-009]](../quality-assurance/ruff_error_resolution.md) - Fix linting issues

**Complementary Workflows:**
- [[qua-006]](../quality-assurance/mypy_type_fixing.md) - Fix type checking errors
- [[qua-001]](../quality-assurance/code_review_checklist.md) - Review code quality

---

## Tags

`python` `module-creation` `docstrings` `type-hints` `code-standards` `pep8` `development` `best-practices`
