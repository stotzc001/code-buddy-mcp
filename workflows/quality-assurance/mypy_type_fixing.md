# Mypy Type Fixing

**ID:** qua-006  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 30-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic approach to adding type hints and resolving mypy type checking errors in Python codebases to improve code quality, catch bugs early, and enhance IDE support.

**Why:** Type hints catch 15% of bugs before runtime through static analysis, improve IDE autocomplete and refactoring, serve as documentation, and make code more maintainable. Mypy ensures type consistency across the codebase, preventing common errors like passing wrong argument types or accessing non-existent attributes.

**When to use:**
- Adding type hints to new or existing code
- Fixing mypy errors in CI/CD pipeline
- Migrating to strict type checking
- Before major refactoring
- During code review
- Improving code documentation
- Onboarding to typed codebase

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ project
- [ ] Mypy installed
- [ ] Basic understanding of Python type hints
- [ ] Access to codebase

**Check before starting:**
```bash
# Verify mypy installed
mypy --version

# Or install
pip install mypy

# Check mypy configuration
cat mypy.ini  # or check pyproject.toml

# Run mypy to see current state
mypy src/

# Check Python version (type hint syntax varies)
python --version
```

---

## Implementation Steps

### Step 1: Run Mypy and Understand Errors

**What:** Execute mypy to identify all type-related issues in your codebase.

**How:**

**Basic mypy commands:**
```bash
# Check entire project
mypy .

# Check specific directory
mypy src/

# Check specific file
mypy src/app.py

# Verbose output
mypy --show-error-codes src/

# Example output:
# src/app.py:23: error: Argument 1 to "process" has incompatible type "str"; expected "int"  [arg-type]
# src/utils.py:45: error: Function is missing a return type annotation  [no-untyped-def]
# src/api.py:67: error: Need type annotation for "data"  [var-annotated]
```

**Understand error format:**
```bash
# Error format:
# file:line: error: message [error-code]
#
# Common error codes:
# - arg-type: Wrong argument type
# - return-value: Wrong return type
# - assignment: Type mismatch in assignment
# - no-untyped-def: Missing function type hints
# - var-annotated: Missing variable type hint
# - attr-defined: Attribute doesn't exist
# - union-attr: Accessing attribute on union type
# - call-arg: Wrong number/type of arguments
```

**Configure mypy:**
```ini
# mypy.ini (or add to pyproject.toml)

[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Start lenient
check_untyped_defs = True

# Exclude paths
exclude = [
    'tests/',
    'migrations/',
    'build/',
]

# Per-module options
[mypy-external_lib.*]
ignore_missing_imports = True
```

**Count errors by type:**
```bash
# Total errors
mypy src/ | grep error | wc -l

# Errors by type
mypy --show-error-codes src/ | grep -oP '\[\K[^\]]+' | sort | uniq -c | sort -rn

# Example output:
#  45 no-untyped-def
#  23 arg-type
#  12 var-annotated
#   8 return-value
#   5 attr-defined
```

**Verification:**
- [ ] Mypy runs successfully
- [ ] All errors listed
- [ ] Error codes identified
- [ ] Configuration reviewed

**If This Fails:**
→ If mypy not installed: `pip install mypy`
→ If syntax errors: Fix Python syntax first
→ If import errors: Install dependencies or ignore imports

---

### Step 2: Prioritize Errors by Impact

**What:** Not all type errors are equal - focus on errors that indicate real bugs or affect critical code.

**How:**

**Categorize by severity:**
```markdown
## 🔴 Critical (Fix Immediately)
- arg-type: Wrong argument types (likely bugs!)
- return-value: Wrong return types
- attr-defined: Accessing non-existent attributes
- call-arg: Wrong function calls

## 🟡 High Priority (Fix Soon)
- union-attr: Unsafe attribute access on unions
- assignment: Type mismatches
- no-any-return: Functions returning Any

## 🟢 Medium Priority (Fix During Refactoring)
- no-untyped-def: Missing function annotations
- var-annotated: Missing variable annotations

## ⚪ Low Priority (Optional)
- import: Missing stub files for libraries
- Cosmetic type issues
```

**Focus on critical paths:**
```python
# Prioritize type errors in:
# 1. Authentication/authorization
# 2. Payment processing
# 3. Data validation
# 4. API endpoints
# 5. Database operations

# Lower priority:
# - Utility functions
# - Internal helpers
# - Debug code
```

**Create error inventory:**
```bash
# Generate report by file
mypy src/ --show-error-codes | awk -F: '{print $1}' | sort | uniq -c | sort -rn

# Example output:
#  23 src/api.py
#  15 src/models.py
#  12 src/utils.py

# Focus on files with most errors
```

**Verification:**
- [ ] Errors categorized by severity
- [ ] Critical files identified
- [ ] Fix order determined

**If This Fails:**
→ If unsure about priority, fix arg-type errors first
→ If too many errors, start with one module

---

### Step 3: Add Basic Type Hints

**What:** Add type annotations to function signatures and important variables.

**How:**

**Function annotations:**
```python
# Before: No type hints
def process_user(data):
    user_id = data.get('id')
    return fetch_user(user_id)

# After: With type hints
from typing import Dict, Any, Optional

def process_user(data: Dict[str, Any]) -> Optional[User]:
    user_id: int = data.get('id')
    return fetch_user(user_id)

# Common patterns:

# Simple types
def add(a: int, b: int) -> int:
    return a + b

# Optional (can be None)
def find_user(user_id: int) -> Optional[User]:
    return User.get(user_id)  # May return None

# Union types (multiple possibilities)
from typing import Union

def process(value: Union[int, str]) -> str:
    return str(value)

# Lists and dictionaries
from typing import List, Dict

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

# Any (when type is truly unknown - avoid when possible)
from typing import Any

def process_dynamic(data: Any) -> Any:
    return transform(data)
```

**Class annotations:**
```python
# Before: No annotations
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.age = None

# After: With annotations
from typing import Optional

class User:
    def __init__(self, name: str, email: str) -> None:
        self.name: str = name
        self.email: str = email
        self.age: Optional[int] = None
    
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'email': self.email,
            'age': self.age
        }
```

**Variable annotations:**
```python
# Before: Implicit types
users = []
total = 0
config = {}

# After: Explicit types
from typing import List, Dict, Any

users: List[User] = []
total: int = 0
config: Dict[str, Any] = {}

# When mypy can infer, annotations are optional
count = 0  # Mypy knows this is int
name = "Alice"  # Mypy knows this is str

# But when starting with empty collections, annotate:
items: List[int] = []  # Good
items = []  # Bad - mypy infers List[Any]
```

**Verification:**
- [ ] Function signatures annotated
- [ ] Return types specified
- [ ] Critical variables annotated
- [ ] Mypy errors reduced

**If This Fails:**
→ If unsure about type, use Any temporarily
→ If complex type, break into simpler types
→ If third-party library, ignore with # type: ignore

---

### Step 4: Fix Common Type Errors

**What:** Address the most common mypy errors with standard patterns.

**How:**

**Error: arg-type (Wrong argument type)**
```python
# Error: Argument 1 has incompatible type "str"; expected "int"

# Before:
def get_user(user_id: int) -> User:
    return User.objects.get(id=user_id)

get_user("123")  # Error: passing str instead of int

# Fix 1: Convert the argument
get_user(int("123"))

# Fix 2: Update function to accept both
from typing import Union

def get_user(user_id: Union[int, str]) -> User:
    if isinstance(user_id, str):
        user_id = int(user_id)
    return User.objects.get(id=user_id)
```

**Error: return-value (Wrong return type)**
```python
# Error: Incompatible return value type (got "None", expected "User")

# Before:
def find_user(email: str) -> User:
    user = User.objects.filter(email=email).first()
    return user  # May return None!

# Fix: Use Optional
from typing import Optional

def find_user(email: str) -> Optional[User]:
    user = User.objects.filter(email=email).first()
    return user  # None is now allowed
```

**Error: attr-defined (Attribute doesn't exist)**
```python
# Error: "User" has no attribute "full_name"

# Before:
user = get_user(123)
print(user.full_name)  # Attribute doesn't exist!

# Fix 1: Use correct attribute
print(user.name)

# Fix 2: Add attribute to class
class User:
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**Error: union-attr (Union type attribute access)**
```python
# Error: Item "None" of "Optional[User]" has no attribute "name"

# Before:
user = find_user("alice@example.com")  # Returns Optional[User]
print(user.name)  # Error: user might be None!

# Fix 1: Check for None
user = find_user("alice@example.com")
if user is not None:
    print(user.name)  # Safe now

# Fix 2: Use assert (if you're certain it exists)
user = find_user("alice@example.com")
assert user is not None
print(user.name)

# Fix 3: Provide default
user = find_user("alice@example.com")
name = user.name if user else "Unknown"
```

**Error: no-untyped-def (Missing annotations)**
```python
# Error: Function is missing a type annotation

# Before:
def calculate_total(items):
    return sum(item.price for item in items)

# Fix: Add annotations
from typing import List
from decimal import Decimal

def calculate_total(items: List[Item]) -> Decimal:
    return sum(item.price for item in items)
```

**Error: var-annotated (Missing variable annotation)**
```python
# Error: Need type annotation for "data"

# Before:
data = {}  # Mypy doesn't know the type

# Fix: Add annotation
from typing import Dict, Any

data: Dict[str, Any] = {}
```

**Verification:**
- [ ] Common errors fixed
- [ ] Code still works correctly
- [ ] Tests pass
- [ ] Mypy errors reduced

**If This Fails:**
→ If fix breaks code, revert and investigate
→ If type is complex, use Any temporarily
→ If uncertain, add # type: ignore with comment

---

### Step 5: Handle Complex Types

**What:** Deal with advanced typing scenarios like generics, protocols, and complex unions.

**How:**

**Generic types:**
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

# Usage with type safety
int_stack: Stack[int] = Stack()
int_stack.push(1)  # OK
int_stack.push("hello")  # Error: Expected int
```

**Protocols (structural subtyping):**
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

# Both work - structural typing
render(Circle())
render(Square())
```

**TypedDict (structured dictionaries):**
```python
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: int

def process_user(user: UserDict) -> str:
    return f"{user['name']} <{user['email']}>"

# Type-safe dictionary access
user: UserDict = {
    'id': 1,
    'name': 'Alice',
    'email': 'alice@example.com',
    'age': 30
}
process_user(user)
```

**Callable types:**
```python
from typing import Callable

# Function that takes a callback
def apply_operation(
    value: int,
    operation: Callable[[int], int]
) -> int:
    return operation(value)

def double(x: int) -> int:
    return x * 2

result = apply_operation(5, double)  # 10
```

**Literal types:**
```python
from typing import Literal

def set_status(status: Literal['pending', 'active', 'deleted']) -> None:
    print(f"Status set to: {status}")

set_status('active')  # OK
set_status('invalid')  # Error: Not in literal values
```

**Verification:**
- [ ] Generic types used where appropriate
- [ ] Protocols for structural typing
- [ ] TypedDict for structured dicts
- [ ] Complex types working correctly

**If This Fails:**
→ If too complex, simplify or use Any
→ If mypy doesn't understand, use # type: ignore
→ If affecting performance, profile code

---

### Step 6: Configure Strictness and Ignore Patterns

**What:** Adjust mypy configuration for appropriate strictness level and handle unavoidable type issues.

**How:**

**Gradual strictness configuration:**
```ini
# mypy.ini

# Level 1: Lenient (starting point)
[mypy]
python_version = 3.11
warn_return_any = False
warn_unused_configs = True
disallow_untyped_defs = False
check_untyped_defs = False

# Level 2: Moderate (after basic fixes)
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
check_untyped_defs = True
warn_redundant_casts = True

# Level 3: Strict (production quality)
[mypy]
python_version = 3.11
strict = True  # Enables all strict flags
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_generics = True
warn_redundant_casts = True
warn_unused_ignores = True
```

**Ignoring specific errors:**
```python
# Inline ignore (use sparingly)
result = complex_function()  # type: ignore[return-value]

# Ignore entire line
import untyped_library  # type: ignore

# Ignore specific error code
data = get_data()  # type: ignore[attr-defined]

# With justification (recommended)
result = legacy_api()  # type: ignore[no-untyped-call] - Legacy API, no stubs available
```

**Per-file configuration:**
```ini
# mypy.ini

# Strict for new code
[mypy-src.new_module.*]
disallow_untyped_defs = True

# Lenient for legacy code
[mypy-src.legacy.*]
ignore_errors = True

# Ignore missing imports for third-party libs
[mypy-external_lib.*]
ignore_missing_imports = True
```

**Create type stubs for third-party libraries:**
```python
# stubs/external_lib.pyi

from typing import Any, Optional

class SomeClass:
    def method(self, arg: str) -> int: ...

def some_function(x: Any) -> Optional[str]: ...
```

**Verification:**
- [ ] Mypy configuration appropriate for project maturity
- [ ] Type ignores used judiciously
- [ ] Ignores have justifications
- [ ] Per-file configs set where needed

**If This Fails:**
→ Start with lenient config, increase strictness gradually
→ Document reasons for ignores
→ Create issues for ignored errors to fix later

---

## Verification Checklist

- [ ] All mypy errors identified
- [ ] Errors prioritized
- [ ] Basic type hints added
- [ ] Common errors fixed
- [ ] Complex types handled
- [ ] Configuration appropriate
- [ ] Tests pass
- [ ] CI/CD updated

---

## Common Issues & Solutions

### Issue: Too Many Errors to Fix

**Symptoms:**
- 500+ mypy errors
- Overwhelming
- Don't know where to start

**Solution:**
```bash
# Strategy 1: One module at a time
mypy src/auth.py --show-error-codes
# Fix all errors in one file
# Commit, move to next file

# Strategy 2: One error type at a time
mypy src/ --show-error-codes | grep "\[no-untyped-def\]"
# Fix all missing function annotations
# Commit

# Strategy 3: Start lenient, increase strictness
# mypy.ini
[mypy]
disallow_untyped_defs = False  # Start here
check_untyped_defs = True

# After fixing basics:
disallow_untyped_defs = True  # Increase strictness
```

**Prevention:**
- Enable mypy early
- Fix errors as you write code
- Use pre-commit hooks

---

### Issue: Third-Party Library Missing Types

**Symptoms:**
- Error: Cannot find implementation or library stub
- Library has no type information

**Solution:**
```bash
# 1. Check if stub package exists
pip install types-requests  # For requests library
pip install types-redis     # For redis library

# 2. If no stubs, ignore missing imports
# mypy.ini
[mypy-problematic_library.*]
ignore_missing_imports = True

# 3. Or create your own stubs
# stubs/library_name.pyi
```

---

### Issue: Type Hints Break at Runtime

**Symptoms:**
- Code works fine
- Mypy passes
- Runtime error about types

**Solution:**
```python
# Problem: Using future annotations
from __future__ import annotations

def process(user: User) -> Result:
    # If User isn't imported, this fails at runtime!
    pass

# Fix: Import for runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import User, Result

def process(user: 'User') -> 'Result':
    # String annotations work at runtime
    pass
```

---

## Examples

### Example 1: Adding Types to Untyped Function

**Context:** Function with no type hints causing errors

**Execution:**
```python
# Before (no types):
def calculate_discount(price, discount_percent, user):
    if user.is_premium:
        discount_percent += 10
    return price * (1 - discount_percent / 100)

# After (with types):
from decimal import Decimal
from typing import Union

def calculate_discount(
    price: Decimal,
    discount_percent: Union[int, float],
    user: User
) -> Decimal:
    if user.is_premium:
        discount_percent += 10
    return price * (Decimal('1') - Decimal(discount_percent) / Decimal('100'))
```

---

### Example 2: Fixing Optional Type Error

**Context:** Function returns Optional but code doesn't check

**Execution:**
```python
# Before (error):
def get_user(id: int) -> Optional[User]:
    return User.query.get(id)

user = get_user(123)
print(user.name)  # Error: user might be None

# After (fixed):
user = get_user(123)
if user is not None:
    print(user.name)
else:
    print("User not found")

# Or with default:
user = get_user(123)
name = user.name if user else "Unknown"
```

---

## Best Practices

### DO:
✅ **Start with function signatures** - Most important
✅ **Use Optional for nullable values** - Explicit None handling
✅ **Fix real bugs first** - arg-type, return-value errors
✅ **Increase strictness gradually** - Lenient → Moderate → Strict
✅ **Document type ignores** - Explain why ignoring
✅ **Use TypedDict for structured dicts** - Better than Dict[str, Any]
✅ **Run mypy in CI/CD** - Catch errors early
✅ **Check for None before accessing** - Avoid union-attr errors

### DON'T:
❌ **Overuse Any** - Defeats purpose of type checking
❌ **Ignore errors without reason** - Document why
❌ **Make everything strict immediately** - Gradual adoption
❌ **Forget runtime checks** - Types don't validate at runtime
❌ **Skip tests** - Type hints can break code
❌ **Use assert for None checks in production** - Asserts can be disabled
❌ **Type hint everything** - Focus on important code
❌ **Fight the type system** - If it's hard, there's probably a better way

---

## Related Workflows

**Prerequisites:**
- [Ruff Error Resolution](./ruff_error_resolution.md)
- [Code Review Checklist](./code_review_checklist.md)

**Next Steps:**
- [Graduation Lite to Strict](./graduation_lite_to_strict.md)
- [Quality Gate Execution](./quality_gate_execution.md)

**Related:**
- [Refactoring Strategy](../development/refactoring_strategy.md)

---

## Tags
`quality-assurance` `type-checking` `mypy` `python` `static-analysis` `best-practices`
