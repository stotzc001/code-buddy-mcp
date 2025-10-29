# Ruff Error Resolution

**ID:** qua-009  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 15-45 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic approach to identifying, understanding, and resolving Python linting errors reported by Ruff - a fast Python linter that replaces Flake8, isort, pyupgrade, and more.

**Why:** Ruff catches common bugs, style issues, and code smells before they reach production. It's 10-100x faster than traditional linters and consolidates multiple tools into one. Clean linting helps maintain code quality, improves readability, and prevents bugs - studies show linting catches 15-25% of bugs before runtime.

**When to use:**
- Before committing code
- When CI/CD pipeline reports linting errors
- During code review
- After updating Ruff or adding new rules
- When onboarding to project with strict linting
- Setting up new project standards

---

## Prerequisites

**Required:**
- [ ] Python project with Ruff installed
- [ ] Access to codebase
- [ ] Understanding of Python basics
- [ ] Editor/IDE configured

**Check before starting:**
```bash
# Verify Ruff installed
ruff --version

# Or install
pip install ruff

# Check current configuration
cat ruff.toml  # or pyproject.toml

# Run quick check
ruff check .

# Check for specific file
ruff check src/myfile.py
```

---

## Implementation Steps

### Step 1: Run Ruff and Identify Errors

**What:** Run Ruff to get complete list of linting errors in your codebase.

**How:**

**Basic Ruff commands:**
```bash
# Check all Python files
ruff check .

# Check specific directory
ruff check src/

# Check specific file
ruff check src/app.py

# Show errors with full context
ruff check --show-files --show-fixes

# Output to file for review
ruff check . > ruff-errors.txt

# Example output:
# src/app.py:23:5: F401 [*] `os.path` imported but unused
# src/app.py:45:80: E501 Line too long (95 > 88)
# src/utils.py:12:1: I001 [*] Import block is un-sorted or un-formatted
# src/api.py:67:5: B006 Do not use mutable data structures for argument defaults
```

**Understand error format:**
```bash
# Error format:
# file:line:column: CODE [*] message
#
# Parts:
# - file:line:column: Location
# - CODE: Error code (F401, E501, etc.)
# - [*]: Auto-fixable
# - message: Description

# Error code categories:
# E: pycodestyle errors
# F: Pyflakes (undefined names, unused imports)
# I: isort (import sorting)
# N: pep8-naming
# B: flake8-bugbear (likely bugs)
# UP: pyupgrade (upgrade syntax)
# And many more...
```

**Count errors by type:**
```bash
# Count total errors
ruff check . | wc -l

# Count by error type
ruff check . | cut -d: -f4 | cut -d' ' -f1 | sort | uniq -c | sort -rn

# Example output:
#  45 F401  # Unused imports
#  23 E501  # Line too long
#  12 I001  # Import sorting
#   8 B006  # Mutable defaults
#   5 F841  # Unused variables
```

**Verification:**
- [ ] Ruff runs successfully
- [ ] All errors listed
- [ ] Error types identified
- [ ] Auto-fixable errors noted

**If This Fails:**
→ If Ruff not installed: `pip install ruff`
→ If syntax errors block Ruff: Fix syntax first
→ If too many errors: Start with one directory/file

---

### Step 2: Prioritize and Categorize Errors

**What:** Not all errors are equal - prioritize by severity and fix the most important ones first.

**How:**

**Categorize errors by priority:**
```markdown
## 🔴 Critical (Fix Immediately)
- F401: Unused imports (can hide real issues)
- F841: Unused variables (potential bugs)
- B006: Mutable default arguments (causes bugs)
- B008: Function call in default argument
- E722: Bare except (hides errors)

## 🟡 High Priority (Fix Soon)
- I001: Import sorting (maintainability)
- N: Naming convention violations
- UP: Upgrade to modern Python syntax
- W: Warnings

## 🟢 Medium Priority (Fix When Refactoring)
- E501: Line too long (readability)
- Style issues

## ⚪ Low Priority (Optional)
- Comment formatting
- Docstring style (if not enforced)
```

**Focus on auto-fixable first:**
```bash
# See what can be auto-fixed
ruff check --fix --diff

# Preview fixes without applying
ruff check --fix --dry-run

# Apply auto-fixes
ruff check --fix .

# Many errors with [*] can be fixed automatically!
```

**Identify error patterns:**
```bash
# Find most common errors
ruff check . | grep "F401" | wc -l  # Unused imports

# Find files with most errors
ruff check . | cut -d: -f1 | sort | uniq -c | sort -rn | head -10

# Example:
#  45 src/utils.py
#  23 src/api.py
#  12 src/models.py
```

**Verification:**
- [ ] Errors categorized by priority
- [ ] Auto-fixable errors identified
- [ ] Problematic files identified
- [ ] Fix order determined

**If This Fails:**
→ If unsure about priority, start with auto-fixes
→ If too many errors, focus on one directory at a time

---

### Step 3: Auto-Fix Simple Errors

**What:** Let Ruff automatically fix errors that have safe, deterministic fixes.

**How:**

**Apply auto-fixes safely:**
```bash
# Dry run first (see what would change)
ruff check --fix --dry-run .

# Review the diff
ruff check --fix --diff . | less

# Apply fixes
ruff check --fix .

# Common auto-fixes:
# - Remove unused imports (F401)
# - Sort imports (I001)
# - Remove unused variables (F841)
# - Upgrade syntax (UP)
# - Format strings (UP032)
```

**Fix specific error types:**
```bash
# Fix only import sorting
ruff check --select I --fix .

# Fix only unused imports
ruff check --select F401 --fix .

# Fix multiple types
ruff check --select F401,I001 --fix .

# Fix everything except line length
ruff check --ignore E501 --fix .
```

**Review auto-fixes:**
```bash
# See what changed
git diff

# If fixes look good
git add -p  # Review each change
git commit -m "fix: Apply Ruff auto-fixes"

# If fixes broke something
git checkout .  # Revert
```

**Common auto-fixable errors:**
```python
# F401: Unused imports
# Before:
import os
import sys  # Unused
from typing import Dict, List  # Dict unused

def main():
    print(os.path.exists('.'))

# After (ruff --fix):
import os
from typing import List

def main():
    print(os.path.exists('.'))

# I001: Import sorting
# Before:
from app import models
import sys
from typing import Dict

# After (ruff --fix):
import sys
from typing import Dict

from app import models

# UP032: f-string formatting
# Before:
name = "Alice"
msg = "Hello {}".format(name)

# After (ruff --fix):
name = "Alice"
msg = f"Hello {name}"
```

**Verification:**
- [ ] Auto-fixes applied
- [ ] Changes reviewed in git diff
- [ ] Tests still pass
- [ ] No functionality broken

**If This Fails:**
→ If auto-fix breaks code, revert and fix manually
→ If unsure about fix, review diff carefully
→ If tests fail, investigate and fix

---

### Step 4: Fix Manual Errors

**What:** Fix errors that require understanding and manual code changes.

**How:**

**Common manual fixes:**

**F401: Remove unused imports**
```python
# Error: F401 `datetime.timedelta` imported but unused

# Before:
from datetime import datetime, timedelta
import requests

def get_current_time():
    return datetime.now()
# timedelta never used!

# After:
from datetime import datetime
import requests

def get_current_time():
    return datetime.now()
```

**F841: Remove unused variables**
```python
# Error: F841 Local variable `result` is assigned to but never used

# Before:
def process_data(items):
    result = []  # Never used
    for item in items:
        print(item)
    return items

# After:
def process_data(items):
    for item in items:
        print(item)
    return items

# Or if you meant to use it:
def process_data(items):
    result = []
    for item in items:
        result.append(process(item))
    return result
```

**B006: Mutable default arguments**
```python
# Error: B006 Do not use mutable data structures for argument defaults

# Before (BUG!):
def add_item(item, items=[]):  # Same list reused!
    items.append(item)
    return items

# Calling:
add_item(1)  # [1]
add_item(2)  # [1, 2] - Unexpected!

# After (Fixed):
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

# Now works correctly:
add_item(1)  # [1]
add_item(2)  # [2]
```

**E722: Bare except clauses**
```python
# Error: E722 Do not use bare `except`

# Before:
def load_config():
    try:
        with open('config.json') as f:
            return json.load(f)
    except:  # Catches everything, including KeyboardInterrupt!
        return {}

# After:
def load_config():
    try:
        with open('config.json') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to load config: {e}")
        return {}
```

**E501: Line too long**
```python
# Error: E501 Line too long (95 > 88)

# Before:
result = very_long_function_name(argument1, argument2, argument3, argument4, argument5)

# After (multiple approaches):

# 1. Break into multiple lines
result = very_long_function_name(
    argument1,
    argument2,
    argument3,
    argument4,
    argument5
)

# 2. Use intermediate variables
args = (argument1, argument2, argument3, argument4, argument5)
result = very_long_function_name(*args)

# 3. Simplify
result = shorter_name(arg1, arg2, arg3, arg4, arg5)
```

**N8XX: Naming conventions**
```python
# Error: N802 Function name should be lowercase

# Before:
def ProcessData(items):  # PascalCase for function
    pass

# After:
def process_data(items):  # snake_case
    pass

# Error: N806 Variable should be lowercase

# Before:
UserCount = 10  # PascalCase for variable

# After:
user_count = 10  # snake_case

# Constants should be UPPER_CASE
MAX_USERS = 100
```

**Verification:**
- [ ] Manual errors fixed
- [ ] Code still works correctly
- [ ] Tests pass
- [ ] No functionality changed

**If This Fails:**
→ If unclear how to fix, search for error code online
→ If fix breaks code, add # noqa with justification
→ If unsure, ask for code review

---

### Step 5: Configure Ruff Appropriately

**What:** Adjust Ruff configuration to match team standards and project needs.

**How:**

**Basic configuration:**
```toml
# pyproject.toml

[tool.ruff]
# Increase line length if team prefers
line-length = 100

# Python version
target-version = "py311"

# Exclude directories
exclude = [
    ".git",
    ".venv",
    "migrations",
    "build",
    "dist",
]

[tool.ruff.lint]
# Select error codes to check
select = [
    "E",   # pycodestyle errors
    "F",   # Pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
    "C4",  # flake8-comprehensions
]

# Ignore specific rules
ignore = [
    "E501",  # Line too long (formatter handles this)
    "B008",  # Function call in defaults (we use this intentionally)
]

# Allow auto-fixes for specific rules
fixable = ["ALL"]
unfixable = []

[tool.ruff.lint.per-file-ignores]
# Ignore specific rules in specific files
"tests/**/*.py" = ["F401", "F841"]  # Unused imports/vars OK in tests
"__init__.py" = ["F401"]  # Unused imports OK in __init__
```

**Rule selection strategies:**
```toml
# Conservative (recommended for existing projects):
select = ["E", "F"]  # Just errors and undefined names

# Moderate (good balance):
select = ["E", "F", "I", "B", "UP"]

# Strict (for new projects or high quality bar):
select = ["ALL"]
ignore = [
    "D",    # pydocstyle (unless enforcing docstrings)
    "ANN",  # Type annotations (unless using mypy)
]
```

**Ignore errors with justification:**
```python
# Ignore specific line
result = function(arg1, arg2, arg3, arg4, arg5, arg6)  # noqa: E501

# Ignore with explanation
try:
    dangerous_operation()
except Exception:  # noqa: E722 - Catch-all intentional here
    logger.error("Operation failed")

# Ignore specific rule
from typing import *  # noqa: F403 - Star import intentional

# Ignore file
# ruff: noqa
```

**Per-file configuration:**
```toml
[tool.ruff.lint.per-file-ignores]
# Tests can have longer lines and unused imports
"tests/**/*.py" = ["E501", "F401", "F841"]

# __init__.py files can have unused imports (re-exports)
"**/__init__.py" = ["F401"]

# Scripts can print to stdout
"scripts/**/*.py" = ["T201"]  # Allow print statements

# Generated code
"generated/**/*.py" = ["ALL"]
```

**Verification:**
- [ ] Configuration file created
- [ ] Rules aligned with team standards
- [ ] Exclusions documented
- [ ] Per-file ignores set appropriately

**If This Fails:**
→ Start with defaults, adjust as needed
→ Discuss configuration with team
→ Document reasons for ignores

---

### Step 6: Integrate with Development Workflow

**What:** Make Ruff part of everyday development to catch errors early.

**How:**

**Pre-commit hooks:**
```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      # Run linter
      - id: ruff
        args: [--fix]
      # Run formatter
      - id: ruff-format

# Install hooks:
pip install pre-commit
pre-commit install
```

**CI/CD integration:**
```yaml
# .github/workflows/lint.yml

name: Lint

on: [push, pull_request]

jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: chartboost/ruff-action@v1
        with:
          args: 'check --output-format=github'
```

**Editor integration:**

**VS Code:**
```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": true,
    "source.organizeImports.ruff": true
  }
}
```

**PyCharm/IntelliJ:**
```bash
# Settings → Tools → External Tools → Add
# Program: ruff
# Arguments: check --fix $FilePath$
# Working directory: $ProjectFileDir$
```

**Git hooks:**
```bash
# .git/hooks/pre-commit
#!/bin/bash
ruff check .
if [ $? -ne 0 ]; then
    echo "Ruff check failed. Fix errors before committing."
    exit 1
fi
```

**Makefile integration:**
```makefile
# Makefile

.PHONY: lint
lint:
	ruff check .

.PHONY: lint-fix
lint-fix:
	ruff check --fix .

.PHONY: format
format:
	ruff format .

.PHONY: check
check: lint
	pytest
```

**Verification:**
- [ ] Pre-commit hooks installed
- [ ] CI/CD checks Ruff
- [ ] Editor shows Ruff errors
- [ ] Team uses Ruff regularly

**If This Fails:**
→ Start with CI/CD first
→ Add pre-commit hooks gradually
→ Provide editor setup documentation

---

## Verification Checklist

- [ ] All Ruff errors identified
- [ ] Errors categorized and prioritized
- [ ] Auto-fixes applied
- [ ] Manual errors fixed
- [ ] Configuration adjusted
- [ ] Integration with workflow complete
- [ ] Team trained on Ruff usage

---

## Common Issues & Solutions

### Issue: Too Many Errors to Fix

**Symptoms:**
- 1000+ errors
- Overwhelming
- Don't know where to start

**Solution:**
```bash
# Strategy 1: One directory at a time
ruff check src/auth/ --fix
# Fix, test, commit
# Repeat for each directory

# Strategy 2: One rule at a time
ruff check --select F401 --fix .  # Unused imports
git commit -m "fix: Remove unused imports"

ruff check --select I001 --fix .  # Import sorting  
git commit -m "fix: Sort imports"

# Strategy 3: New code only
# Add to pyproject.toml:
[tool.ruff.lint.per-file-ignores]
"old_code/**/*.py" = ["ALL"]  # Ignore legacy code

# Fix new files as you touch them
```

**Prevention:**
- Enable Ruff early in project
- Fix errors immediately
- Use pre-commit hooks

---

### Issue: Ruff and Formatter Conflict

**Symptoms:**
- Ruff wants one format
- Black/other formatter wants different format
- Endless reformatting loop

**Solution:**
```toml
# Use Ruff's built-in formatter (replaces Black)
[tool.ruff]
line-length = 100

# Or configure Ruff to match Black
[tool.ruff.lint]
ignore = ["E501"]  # Let formatter handle line length

# Format with Ruff:
ruff format .
```

---

### Issue: False Positives

**Symptoms:**
- Ruff flags valid code
- Pattern is intentional

**Solution:**
```python
# Use inline ignores with justification
dangerous_operation()  # noqa: S501 - Validated input

# Or adjust configuration
[tool.ruff.lint]
ignore = ["B008"]  # We intentionally use function calls in defaults
```

---

## Examples

### Example 1: Cleaning Up Unused Imports

**Context:** 45 F401 errors (unused imports)

**Execution:**
```bash
# Check how many
ruff check --select F401 . | wc -l
# Output: 45

# Auto-fix
ruff check --select F401 --fix .

# Verify
git diff
pytest  # Ensure nothing broken

# Commit
git commit -m "fix: Remove 45 unused imports"
```

**Result:** All unused imports removed, tests pass

---

### Example 2: Fixing Mutable Defaults

**Context:** 8 B006 errors (mutable default arguments)

**Execution:**
```python
# Before:
def add_to_cache(key, value, cache={}):  # B006
    cache[key] = value
    return cache

# After:
def add_to_cache(key, value, cache=None):
    if cache is None:
        cache = {}
    cache[key] = value
    return cache

# Test to ensure fix works
def test_add_to_cache():
    result1 = add_to_cache("a", 1)
    result2 = add_to_cache("b", 2)
    assert result1 != result2  # Now works!
```

---

## Best Practices

### DO:
✅ **Fix errors immediately** - Don't let them accumulate
✅ **Use auto-fix liberally** - Ruff's fixes are safe
✅ **Configure appropriately** - Match team standards
✅ **Integrate with workflow** - Pre-commit, CI/CD
✅ **Fix one type at a time** - Easier to review
✅ **Run before committing** - Catch errors early
✅ **Use meaningful ignores** - Explain why ignoring

### DON'T:
❌ **Ignore all errors** - Fix them instead
❌ **Disable rules without reason** - Understand why first
❌ **Skip configuration** - Defaults may not fit
❌ **Forget to test** - Auto-fixes can break code
❌ **Let errors accumulate** - Fix continuously
❌ **Argue about style** - Let Ruff decide

---

## Related Workflows

**Prerequisites:**
- [Code Review Checklist](./code_review_checklist.md)
- [CI/CD Workflow](../development/ci_cd_workflow.md)

**Next Steps:**
- [Mypy Type Fixing](./mypy_type_fixing.md)
- [Quality Gate Execution](./quality_gate_execution.md)

**Related:**
- [Refactoring Strategy](../development/refactoring_strategy.md)

---

## Tags
`quality-assurance` `linting` `python` `ruff` `code-quality` `automation` `best-practices`
