# Project Formatter Setup

**ID:** config-003  
**Category:** Configuration Management  
**Priority:** MEDIUM  
**Complexity:** Simple  
**Estimated Time:** 15-20 minutes  
**Frequency:** Once per project  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Set up automated code formatting with Black, isort, and configuration for consistent code style across the project.

**Why:**
- Ensures consistent code style across team
- Eliminates style debates and bikeshedding
- Automates formatting in CI/CD
- Improves code readability
- Reduces code review friction

**When to use:**
- Starting a new Python project
- Standardizing existing project formatting
- Setting up team development standards
- Configuring CI/CD pipelines
- Improving code quality processes

---

## Prerequisites

**Required Knowledge:**
- [ ] Basic Python project structure
- [ ] Command line usage
- [ ] Git basics

**Required Tools:**
- [ ] Python 3.8+ installed
- [ ] pip or poetry for package management
- [ ] Git (optional, for pre-commit hooks)

**Check before starting:**
```bash
python --version  # Should show 3.8+
pip --version     # Should be available
```

---

## Implementation Steps

### Step 1: Install Formatting Tools

**What:** Install Black, isort, and supporting tools.

**How:**

```bash
# Install formatters
pip install black isort

# Optional: Install flake8 for linting
pip install flake8 flake8-bugbear

# Optional: Install pre-commit for git hooks
pip install pre-commit

# Add to requirements-dev.txt
cat > requirements-dev.txt << EOF
black>=24.0.0
isort>=5.13.0
flake8>=7.0.0
flake8-bugbear>=24.0.0
pre-commit>=3.6.0
EOF

# Or with poetry
poetry add --group dev black isort flake8 flake8-bugbear pre-commit
```

**Verification:**
```bash
black --version
isort --version
flake8 --version
```

**If This Fails:**
→ Update pip: `pip install --upgrade pip`

---

### Step 2: Configure Black

**What:** Create Black configuration file.

**How:**

**File: pyproject.toml** (recommended approach)
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''
```

**Or File: .black** (alternative)
```
[black]
line-length = 100
target-version = py38
```

**Test Black:**
```bash
# Format single file
black myfile.py

# Format entire project
black .

# Check without modifying (for CI)
black --check .

# Show what would be changed
black --diff .
```

**Verification:**
- [ ] Black configuration created
- [ ] `black .` runs successfully
- [ ] Files formatted consistently

---

### Step 3: Configure isort

**What:** Configure import sorting to work with Black.

**How:**

**Add to pyproject.toml:**
```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "*/venv/*", "*/.venv/*"]

# Optional: Group imports
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
known_first_party = ["your_package_name"]
```

**Test isort:**
```bash
# Sort imports in file
isort myfile.py

# Sort all files
isort .

# Check without modifying
isort --check-only .

# Show what would be changed
isort --diff .
```

**Verification:**
- [ ] isort configuration created
- [ ] isort compatible with Black
- [ ] `isort .` runs successfully

---

### Step 4: Configure Flake8 (Optional)

**What:** Set up linting to catch style issues.

**How:**

**File: .flake8** or **setup.cfg:**
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, E266, E501, W503
exclude =
    .git,
    __pycache__,
    .venv,
    venv,
    build,
    dist,
    migrations,
    .eggs,
    *.egg
max-complexity = 10
```

**Or in pyproject.toml** (requires flake8-pyproject):
```toml
[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "E266", "E501", "W503"]
exclude = [".git", "__pycache__", ".venv", "venv", "build", "dist"]
max-complexity = 10
```

**Test Flake8:**
```bash
flake8 .
```

**Verification:**
- [ ] Flake8 runs without conflicting with Black
- [ ] Appropriate rules ignored

---

### Step 5: Create Format Scripts

**What:** Create convenient scripts for formatting.

**How:**

**File: scripts/format.sh** (Unix/Mac)
```bash
#!/bin/bash
# Format code with Black and isort

set -e

echo "🎨 Formatting code..."

echo "📦 Sorting imports with isort..."
isort .

echo "⚫ Formatting with Black..."
black .

echo "✅ Code formatted successfully!"
```

**File: scripts/format.bat** (Windows)
```batch
@echo off
echo Formatting code...

echo Sorting imports with isort...
isort .

echo Formatting with Black...
black .

echo Code formatted successfully!
```

**File: scripts/check-format.sh** (CI/CD)
```bash
#!/bin/bash
# Check code formatting without making changes

set -e

echo "🔍 Checking code formatting..."

echo "📦 Checking import order..."
isort --check-only . || {
    echo "❌ Imports not sorted. Run: isort ."
    exit 1
}

echo "⚫ Checking Black formatting..."
black --check . || {
    echo "❌ Code not formatted. Run: black ."
    exit 1
}

echo "🔍 Running Flake8..."
flake8 . || {
    echo "❌ Linting errors found."
    exit 1
}

echo "✅ All formatting checks passed!"
```

**Make executable:**
```bash
chmod +x scripts/format.sh
chmod +x scripts/check-format.sh
```

**Verification:**
- [ ] Format script created
- [ ] Check script created
- [ ] Scripts are executable

---

### Step 6: Set Up Pre-commit Hooks

**What:** Automatically format code before commits.

**How:**

**File: .pre-commit-config.yaml**
```yaml
# Pre-commit hooks configuration
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-bugbear]
```

**Install pre-commit:**
```bash
# Install hooks
pre-commit install

# Test on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

**Verification:**
- [ ] Pre-commit hooks installed
- [ ] Hooks run on git commit
- [ ] All checks pass

**If This Fails:**
→ Ensure pre-commit package is installed
→ Run `pre-commit install` in project root

---

### Step 7: Add Format Commands to Package

**What:** Add convenient format commands to project.

**How:**

**If using Makefile:**
```makefile
.PHONY: format check-format

format:
	@echo "🎨 Formatting code..."
	isort .
	black .
	@echo "✅ Done!"

check-format:
	@echo "🔍 Checking format..."
	isort --check-only .
	black --check .
	flake8 .
	@echo "✅ Format check passed!"
```

**If using pyproject.toml with Poe the Poet:**
```toml
[tool.poe.tasks]
format = {cmd = "black . && isort .", help = "Format code with black and isort"}
format-check = {cmd = "black --check . && isort --check-only . && flake8 .", help = "Check code formatting"}
```

**Usage:**
```bash
# With Makefile
make format
make check-format

# With Poe
poe format
poe format-check

# Or directly with scripts
./scripts/format.sh
./scripts/check-format.sh
```

**Verification:**
- [ ] Format commands work
- [ ] Check commands work
- [ ] Team members can run easily

---

## Verification Checklist

- [ ] Black installed and configured
- [ ] isort installed and configured (compatible with Black)
- [ ] Flake8 configured (optional)
- [ ] pyproject.toml has formatter configurations
- [ ] Format scripts created and executable
- [ ] Pre-commit hooks installed (optional)
- [ ] `black .` runs without errors
- [ ] `isort .` runs without errors
- [ ] All files formatted consistently
- [ ] Team members can format code easily
- [ ] CI/CD can check formatting

---

## Common Issues & Solutions

### Issue: Black and isort Conflict

**Solution:**
Ensure isort profile is set to "black":
```toml
[tool.isort]
profile = "black"
```

---

### Issue: Pre-commit Hooks Fail

**Solution:**
```bash
# Update hooks
pre-commit autoupdate

# Run on all files
pre-commit run --all-files

# Skip hooks if needed (emergency only)
git commit --no-verify
```

---

## Best Practices

### DO:
✅ Use Black's defaults when possible
✅ Configure isort to work with Black
✅ Set up pre-commit hooks for automation
✅ Include formatting in CI/CD checks
✅ Document formatting commands in README

### DON'T:
❌ Override too many Black settings
❌ Mix formatters (choose Black or alternatives)
❌ Skip formatting checks in CI
❌ Commit unformatted code

---

## Examples

### Example: Complete pyproject.toml

```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]
```

---

## Related Workflows

**Before This Workflow:**
- [[dev-001]](../development/environment_initialization.md) - Environment setup

**After This Workflow:**
- [[qa-001]](../quality-assurance/code_review_checklist.md) - Code review
- [[dev-009]](../development/pre_commit_hooks.md) - Pre-commit hooks

---

## Tags
`formatting` `black` `isort` `code-style` `automation` `python` `quality`
