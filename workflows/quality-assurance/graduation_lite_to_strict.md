# Graduation: Lite to Strict Type Checking

**ID:** qua-005  
**Category:** Quality Assurance  
**Priority:** MEDIUM  
**Complexity:** Intermediate  
**Estimated Time:** Multiple sprints (2-8 weeks)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic process for gradually transitioning a Python codebase from minimal or no type checking to strict mypy validation, ensuring quality improvements without disrupting development.

**Why:** Jumping directly to strict type checking in existing codebases creates hundreds of errors and blocks development. A gradual approach allows teams to improve type safety incrementally, fix errors in manageable batches, and build type-checking habits. Projects that graduate to strict typing have 30-40% fewer type-related bugs and better code maintainability.

**When to use:**
- Migrating legacy codebase to type checking
- New team members need type safety
- Preparing for major refactoring
- Improving code quality systematically
- Reducing production bugs
- Establishing quality standards

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ project
- [ ] Mypy installed and configured
- [ ] Team buy-in for gradual adoption
- [ ] CI/CD pipeline available
- [ ] Time for incremental improvements (2-8 weeks)

**Check before starting:**
```bash
# Verify mypy installed
mypy --version

# Check current type checking status
mypy src/ 2>&1 | tail -10

# Establish baseline
mypy src/ > baseline-errors.txt
wc -l baseline-errors.txt
```

---

## Implementation Steps

### Step 1: Assess Current State and Set Goals

**What:** Understand your starting point and define realistic targets for type checking maturity.

**How:**

**Measure current state:**
```bash
# Count total mypy errors
mypy src/ 2>&1 | grep "error:" | wc -l

# Categorize errors by type
mypy --show-error-codes src/ 2>&1 | grep -oP '\[\K[^\]]+' | sort | uniq -c | sort -rn

# Example output:
#  145 no-untyped-def      # Missing function annotations
#   89 var-annotated       # Missing variable annotations
#   45 arg-type            # Wrong argument types
#   23 return-value        # Wrong return types
#   12 attr-defined        # Attribute errors
```

**Check mypy configuration:**
```ini
# Current mypy.ini (example baseline)
[mypy]
python_version = 3.11
# Very lenient - likely your starting point
disallow_untyped_defs = False
check_untyped_defs = False
warn_return_any = False
```

**Define graduation levels:**
```markdown
# Type Checking Maturity Levels

## Level 0: No Type Checking ❌
- No mypy run
- No type hints
- **Current State for many legacy projects**

## Level 1: Basic Type Checking 🟡
- Mypy runs but allows untyped defs
- Type hints on new code only
- Basic error detection
- **Goal: 2-3 weeks**

## Level 2: Moderate Type Checking 🟢
- Most functions have type hints
- Checks untyped definitions
- Warns on unsafe patterns
- **Goal: 4-6 weeks**

## Level 3: Strict Type Checking ✅
- All functions typed
- No Any types
- Full type safety
- **Goal: 6-8 weeks**
```

**Set sprint goals:**
```markdown
# 8-Week Graduation Plan

## Sprint 1-2 (Weeks 1-2): Level 1
- Enable mypy in CI (lenient)
- Add type hints to new code
- Fix critical errors (50+)
- Baseline: 300 errors → 250 errors

## Sprint 3-4 (Weeks 3-4): Level 1.5
- Type hint public APIs
- Fix arg-type errors
- Enable check_untyped_defs
- Target: 250 errors → 150 errors

## Sprint 5-6 (Weeks 5-6): Level 2
- Type hint all functions
- Enable warn_return_any
- Fix return-value errors
- Target: 150 errors → 50 errors

## Sprint 7-8 (Weeks 7-8): Level 3
- Enable strict mode
- Fix remaining errors
- Full type coverage
- Target: 50 errors → 0 errors
```

**Verification:**
- [ ] Current state documented
- [ ] Error baseline captured
- [ ] Graduation levels defined
- [ ] Timeline established
- [ ] Team informed

**If This Fails:**
→ If too many errors (1000+), extend timeline
→ If team pushback, start with new code only
→ If urgent, focus on critical modules first

---

### Step 2: Level 1 - Enable Basic Type Checking

**What:** Turn on mypy with lenient settings and fix critical errors.

**How:**

**Configure Level 1 mypy:**
```ini
# mypy.ini - Level 1 Configuration

[mypy]
python_version = 3.11

# Very lenient - just catch obvious errors
disallow_untyped_defs = False
check_untyped_defs = False
warn_return_any = False
warn_unused_configs = True

# Exclude legacy code
exclude = [
    'legacy/',
    'old_code/',
]

# Ignore missing stubs
[mypy-external_library.*]
ignore_missing_imports = True
```

**Add to CI/CD:**
```yaml
# .github/workflows/type-check.yml

name: Type Check

on: [push, pull_request]

jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install mypy
      
      - name: Run mypy
        run: mypy src/
        continue-on-error: true  # Don't fail builds yet
```

**Add type hints to new code only:**
```python
# New code policy: All new functions must have type hints

# ✅ Good: New function with types
def create_user(name: str, email: str) -> User:
    return User(name=name, email=email)

# ❌ Bad: New function without types
def create_user(name, email):
    return User(name=name, email=email)
```

**Fix critical errors (arg-type, attr-defined):**
```python
# Fix errors that indicate actual bugs

# Error: Argument type mismatch
# Before:
def get_user(user_id: int) -> User:
    return User.query.get(user_id)

get_user("123")  # Error! Wrong type

# After:
get_user(int("123"))  # Fixed

# Error: Attribute doesn't exist
# Before:
user.full_name  # Error: User has no attribute full_name

# After:
user.name  # Use correct attribute
```

**Track progress:**
```bash
# Weekly check
mypy src/ 2>&1 | grep "error:" | wc -l

# Target: Reduce errors by 15-20% per sprint
# Week 0: 300 errors (baseline)
# Week 1: 280 errors (-7%)
# Week 2: 250 errors (-17%)
```

**Verification:**
- [ ] Mypy running in CI
- [ ] Configuration file created
- [ ] New code policy established
- [ ] Critical errors fixed (20-30)
- [ ] Error count reduced

**If This Fails:**
→ If CI fails too often, keep continue-on-error: true
→ If team resistance, make mypy optional initially
→ If too many errors, exclude more directories

---

### Step 3: Level 1.5 - Type Hint Public APIs

**What:** Add type hints to all public-facing functions and commonly used utilities.

**How:**

**Identify public API functions:**
```python
# Public API = functions/classes used by other modules

# Examples:
# - API endpoints
# - Database models
# - Service layer functions
# - Utility functions
# - Public class methods
```

**Type hint API functions:**
```python
# Before: Untyped API endpoint
def create_order(request):
    data = request.json
    order = Order(**data)
    db.session.add(order)
    db.session.commit()
    return order.to_dict()

# After: Typed API endpoint
from typing import Dict, Any
from flask import Request

def create_order(request: Request) -> Dict[str, Any]:
    data: Dict[str, Any] = request.json
    order = Order(**data)
    db.session.add(order)
    db.session.commit()
    return order.to_dict()
```

**Update configuration:**
```ini
# mypy.ini - Level 1.5

[mypy]
python_version = 3.11

# Start checking function bodies
check_untyped_defs = True  # NEW: Check untyped functions

disallow_untyped_defs = False  # Still allowing untyped
warn_return_any = False
warn_unused_configs = True
```

**Fix newly discovered errors:**
```bash
# New errors will appear with check_untyped_defs = True
mypy src/ --show-error-codes

# Common new errors:
# - Missing return statements
# - Type mismatches in function bodies
# - Incorrect type assumptions
```

**Add type hints systematically:**
```bash
# One module at a time
# 1. Type hint src/api/
# 2. Type hint src/models/
# 3. Type hint src/services/
# 4. Type hint src/utils/

# Track per module:
mypy src/api/ 2>&1 | grep "error:" | wc -l
```

**Verification:**
- [ ] Public API functions typed
- [ ] check_untyped_defs enabled
- [ ] New errors fixed
- [ ] Module coverage increasing
- [ ] Error count reduced 40-50%

**If This Fails:**
→ If too many new errors, do one module per sprint
→ If complex types needed, use Any temporarily
→ If blocking development, maintain per-module config

---

### Step 4: Level 2 - Enable Moderate Strictness

**What:** Require type hints on all functions and enable additional warnings.

**How:**

**Update configuration:**
```ini
# mypy.ini - Level 2

[mypy]
python_version = 3.11

# Require function annotations
disallow_untyped_defs = True  # NEW: Functions must have types

# Additional warnings
check_untyped_defs = True
warn_return_any = True  # NEW: Warn on returning Any
warn_unused_configs = True
warn_redundant_casts = True  # NEW: Warn on unnecessary casts
warn_unused_ignores = True  # NEW: Warn on unused # type: ignore

# Still lenient on some things
disallow_any_generics = False
disallow_untyped_calls = False
```

**Type hint all remaining functions:**
```python
# Before: Still some untyped functions
def process_data(items):
    results = []
    for item in items:
        result = transform(item)
        results.append(result)
    return results

# After: All functions typed
from typing import List, Any

def process_data(items: List[Any]) -> List[Any]:
    results: List[Any] = []
    for item in items:
        result = transform(item)
        results.append(result)
    return results

# Even better: Use specific types
from typing import List

def process_data(items: List[Item]) -> List[ProcessedItem]:
    results: List[ProcessedItem] = []
    for item in items:
        result = transform(item)
        results.append(result)
    return results
```

**Fix return-value errors:**
```python
# Common with disallow_untyped_defs

# Error: Missing return statement
def find_user(user_id: int) -> User:
    user = User.query.get(user_id)
    if not user:
        pass  # Error: No return!
    return user

# Fix:
def find_user(user_id: int) -> Optional[User]:
    user = User.query.get(user_id)
    if not user:
        return None
    return user
```

**Reduce Any usage:**
```python
# Before: Using Any
from typing import Any

def process(data: Any) -> Any:
    return transform(data)

# After: Specific types
from typing import Dict

def process(data: Dict[str, str]) -> Dict[str, int]:
    return {k: len(v) for k, v in data.items()}
```

**Enable in CI as blocker:**
```yaml
# .github/workflows/type-check.yml

- name: Run mypy
  run: mypy src/
  # Remove: continue-on-error: true
  # Now fails build if errors exist
```

**Verification:**
- [ ] All functions have type hints
- [ ] disallow_untyped_defs enabled
- [ ] Any usage reduced
- [ ] Return types correct
- [ ] Mypy blocks bad code in CI
- [ ] Error count < 50

**If This Fails:**
→ If too many errors, fix one module at a time
→ If blocking too much, keep some modules lenient
→ If team frustrated, add transition period

---

### Step 5: Level 3 - Enable Strict Mode

**What:** Enable full strict type checking with maximum safety.

**How:**

**Enable strict mode:**
```ini
# mypy.ini - Level 3 (Final)

[mypy]
python_version = 3.11

# Enable ALL strict checks
strict = True

# Equivalent to:
# disallow_any_generics = True
# disallow_untyped_calls = True
# disallow_untyped_defs = True
# disallow_incomplete_defs = True
# check_untyped_defs = True
# disallow_untyped_decorators = True
# warn_redundant_casts = True
# warn_unused_ignores = True
# warn_return_any = True
# warn_unreachable = True
# strict_equality = True
# strict_concatenate = True

warn_unused_configs = True
```

**Fix strict mode errors:**

**Error: disallow_any_generics**
```python
# Before: Generic without type parameter
def get_items() -> List:  # Error: Need List[X]
    return []

# After:
def get_items() -> List[Item]:
    return []
```

**Error: disallow_untyped_calls**
```python
# Before: Calling untyped function
def process():
    result = legacy_function()  # Error: legacy_function not typed
    return result

# After: Add type ignore or type the called function
def process() -> Any:
    result = legacy_function()  # type: ignore[no-untyped-call]
    return result

# Or better: Type the legacy function
def legacy_function() -> str:
    return "data"
```

**Error: disallow_untyped_decorators**
```python
# Before: Untyped decorator
@app.route("/users")
def get_users():
    return User.query.all()

# After: Type the decorator or ignore
from typing import Callable, Any

@app.route("/users")  # type: ignore[misc]
def get_users() -> List[Dict[str, Any]]:
    return [u.to_dict() for u in User.query.all()]
```

**Eliminate remaining type ignores:**
```python
# Review all # type: ignore comments
# Fix underlying issues where possible

# Before: Ignoring real issue
result = process(data)  # type: ignore

# After: Fix the actual issue
result: ProcessedData = process(data)
```

**Add type stubs for third-party libraries:**
```python
# Create stubs for untyped dependencies
# stubs/external_lib/__init__.pyi

from typing import Any, Optional

class Client:
    def __init__(self, api_key: str) -> None: ...
    def fetch(self, url: str) -> Optional[dict]: ...
```

**Verification:**
- [ ] Strict mode enabled
- [ ] Zero mypy errors
- [ ] Type ignores minimized
- [ ] Stubs for third-party libs
- [ ] CI enforces strict typing
- [ ] Team comfortable with types

**If This Fails:**
→ If too strict, selectively disable some strict flags
→ If third-party issues, use type: ignore with comments
→ If legacy code problems, exclude from strict checks

---

### Step 6: Maintain and Improve

**What:** Establish processes to maintain type safety and continue improving.

**How:**

**Pre-commit hooks:**
```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: 'v1.7.0'
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

**PR requirements:**
```markdown
# Pull Request Checklist

- [ ] All new code has type hints
- [ ] Mypy passes with strict mode
- [ ] No new type: ignore comments without justification
- [ ] Types added for modified functions
```

**Regular type coverage audits:**
```bash
# Check type coverage periodically
# (Requires mypy 1.0+)
mypy src/ --html-report mypy-report/
open mypy-report/index.html

# Track metrics:
# - Functions with type hints: 100%
# - Lines with type coverage: >95%
# - Type: ignore count: <10
```

**Type checking in code review:**
```markdown
## Type Review Checklist

✅ Functions have type hints
✅ Return types are specific (not Any)
✅ Optional[T] used for nullable
✅ Collections have type parameters
✅ Type ignores are justified
✅ No obvious type errors
```

**Team training:**
```markdown
# Monthly Type Checking Training

## Topics:
- Type hint best practices
- Common mypy errors
- Advanced typing features
- Performance considerations

## Resources:
- Python typing docs
- Mypy documentation
- Team wiki on typing patterns
```

**Verification:**
- [ ] Pre-commit hooks active
- [ ] PR requirements enforced
- [ ] Regular audits scheduled
- [ ] Code review includes types
- [ ] Team trained on types
- [ ] Type quality maintained

**If This Fails:**
→ If types regress, add stricter CI checks
→ If team needs help, pair programming sessions
→ If patterns emerge, document in team wiki

---

## Verification Checklist

- [ ] Current state assessed
- [ ] Graduation plan defined
- [ ] Level 1 achieved (basic checking)
- [ ] Level 1.5 achieved (public APIs typed)
- [ ] Level 2 achieved (all functions typed)
- [ ] Level 3 achieved (strict mode)
- [ ] Maintenance process established
- [ ] Team trained and comfortable

---

## Common Issues & Solutions

### Issue: Too Many Errors Appearing

**Symptoms:**
- Each strictness level reveals 100+ new errors
- Team overwhelmed
- Development slowed

**Solution:**
```markdown
1. **Slow down the graduation**
   - Extend sprints from 2 weeks to 4 weeks
   - Stay at current level longer
   - Fix errors in smaller batches

2. **Focus on critical paths first**
   - Type hint auth code
   - Type hint payment code
   - Leave utilities for later

3. **Per-module graduation**
   ```ini
   # mypy.ini
   [mypy-src.auth.*]
   strict = True  # Auth is strict

   [mypy-src.utils.*]
   disallow_untyped_defs = False  # Utils still lenient
   ```
```

---

### Issue: Team Resistance

**Symptoms:**
- Developers bypassing type checks
- Complaints about slowdown
- Excessive type: ignore usage

**Solution:**
```markdown
1. **Show value with examples**
   - Demonstrate bugs caught by types
   - Show IDE autocomplete improvements
   - Measure bug reduction

2. **Make it easy**
   - Provide type hint templates
   - Document common patterns
   - Offer pairing sessions

3. **Gradual enforcement**
   - Don't block PRs immediately
   - Start with warnings
   - Increase strictness slowly
```

---

### Issue: Third-Party Library Problems

**Symptoms:**
- Many ignore_missing_imports
- Untyped libraries block progress
- Can't enable strict mode

**Solution:**
```bash
# 1. Install type stubs if available
pip install types-requests
pip install types-redis

# 2. Create minimal stubs for critical functions
# stubs/library/__init__.pyi

# 3. Ignore less critical libraries
# mypy.ini
[mypy-less_critical_lib.*]
ignore_missing_imports = True
```

---

## Examples

### Example 1: 4-Week Fast Track

**Context:** Small project, 50 errors

**Execution:**
```markdown
Week 1: Level 1
- Enable mypy in CI (continue-on-error)
- Fix 20 critical errors
- Type hint new code only

Week 2: Level 1.5
- Type hint all API functions
- Enable check_untyped_defs
- Fix 15 more errors

Week 3: Level 2
- Type hint all functions
- Enable disallow_untyped_defs
- Fix 10 more errors

Week 4: Level 3
- Enable strict mode
- Fix final 5 errors
- Zero errors achieved! ✅
```

---

### Example 2: 8-Week Enterprise Project

**Context:** Large project, 500 errors

**Execution:**
```markdown
Weeks 1-2: Level 1
- Mypy CI with continue-on-error
- Fix 100 arg-type errors
- Type new code

Weeks 3-4: Level 1.5
- Type public APIs (100 functions)
- Enable check_untyped_defs
- Fix 150 errors

Weeks 5-6: Level 2
- Type all functions module by module
- Enable warn_return_any
- Fix 150 more errors

Weeks 7-8: Level 3
- Enable strict selectively
- Fix final 100 errors
- Document patterns
```

---

## Best Practices

### DO:
✅ **Start lenient** - Don't enable strict immediately
✅ **Graduate gradually** - 2-8 weeks depending on size
✅ **Fix in batches** - 20-50 errors per sprint
✅ **Type public APIs first** - Highest impact
✅ **Measure progress** - Track error count weekly
✅ **Celebrate milestones** - Each level is an achievement
✅ **Document patterns** - Help team learn
✅ **Make it easy** - Tools, templates, training

### DON'T:
❌ **Enable strict immediately** - Overwhelming
❌ **Fix everything at once** - Burnout
❌ **Ignore team concerns** - Get buy-in
❌ **Skip levels** - Each builds on previous
❌ **Forget to track** - Need to measure progress
❌ **Block development** - Balance safety with velocity
❌ **Give up halfway** - Stick to the plan
❌ **Leave maintenance to chance** - Need ongoing process

---

## Related Workflows

**Prerequisites:**
- [Mypy Type Fixing](./mypy_type_fixing.md)
- [Quality Gate Execution](./quality_gate_execution.md)

**Next Steps:**
- [Code Review Checklist](./code_review_checklist.md)
- [Complexity Reduction](./complexity_reduction.md)

**Related:**
- [Technical Debt Management](../development/technical_debt_mgmt.md)

---

## Tags
`quality-assurance` `type-checking` `mypy` `migration` `gradual-adoption` `best-practices` `process-improvement`
