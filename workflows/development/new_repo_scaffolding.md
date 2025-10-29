# New Repo Scaffolding

**ID:** dev-023  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 45-60 minutes  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Create a complete, production-ready Python project structure from scratch with all necessary configuration files, directory structure, and tooling setup.

**Why:** A well-structured repository from the start prevents technical debt, ensures consistency across projects, includes best practices by default, and makes onboarding new developers easier.

**When to use:**
- Starting a new Python project
- Creating a microservice or library
- Standardizing project structure across team
- Migrating from unstructured code to proper project
- Creating proof-of-concept that might become production code

---

## Prerequisites

**Required Tools:**
- [ ] Python 3.10+ installed
- [ ] Git installed and configured
- [ ] GitHub/GitLab account with repo access
- [ ] Code editor with Python support
- [ ] pip and venv

**Required Knowledge:**
- [ ] Basic Git usage (clone, commit, push)
- [ ] Python project structure concepts
- [ ] Basic understanding of configuration files
- [ ] Command line proficiency

**Decisions to Make:**
- [ ] Project name and description
- [ ] License type (MIT, Apache, proprietary)
- [ ] Python version (recommend 3.11+)
- [ ] Framework (if any): Flask, Django, FastAPI, etc.
- [ ] Testing framework: pytest, unittest
- [ ] CI/CD platform: GitHub Actions, GitLab CI, Jenkins

**Check before starting:**
```bash
# Verify tools installed
python --version  # 3.10+
git --version
pip --version

# Verify git configuration
git config user.name
git config user.email

# Check GitHub CLI (optional but useful)
gh --version
```

---

## Implementation Steps

### Step 1: Create Repository and Clone

**What:** Initialize a new Git repository locally or on GitHub/GitLab.

**How:**

**Option A: Create on GitHub first (recommended)**
```bash
# Using GitHub CLI (fastest)
gh repo create my-project --public --clone

# Or via web interface:
# 1. Go to github.com/new
# 2. Fill in repository name
# 3. Choose public/private
# 4. Add README, .gitignore (Python), license
# 5. Clone to local:
git clone https://github.com/username/my-project.git
cd my-project
```

**Option B: Create locally first**
```bash
# Create project directory
mkdir my-project
cd my-project

# Initialize git
git init

# Create remote repository
gh repo create my-project --source=. --public

# Or manually on GitHub, then add remote:
git remote add origin https://github.com/username/my-project.git
```

**Verification:**
- [ ] Directory created and you're in it: `pwd`
- [ ] Git initialized: `ls -la .git`
- [ ] Remote configured: `git remote -v`
- [ ] Can access repository on GitHub/GitLab

**If This Fails:**
→ **No git:** Install git first
→ **Authentication error:** Set up SSH keys or use HTTPS with token
→ **Permission denied:** Check repository access rights

---

### Step 2: Create Directory Structure

**What:** Set up standard Python project directory structure.

**How:**
```bash
# Create standard Python project structure
mkdir -p src/my_project
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs
mkdir -p scripts
mkdir -p .github/workflows

# Create __init__.py files
touch src/my_project/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

# Create placeholder files
touch src/my_project/main.py
touch src/my_project/config.py
touch tests/unit/test_main.py
touch tests/conftest.py

# Verify structure
tree -L 3  # or ls -R on Windows
```

**Recommended structure:**
```
my-project/
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       ├── ci.yml
│       └── deploy.yml
├── src/
│   └── my_project/         # Main package (use underscores)
│       ├── __init__.py
│       ├── main.py         # Entry point
│       ├── config.py       # Configuration
│       ├── models/         # Data models
│       ├── services/       # Business logic
│       ├── api/            # API routes (if applicable)
│       └── utils/          # Utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # pytest fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── docs/                   # Documentation
│   ├── index.md
│   └── api.md
├── scripts/                # Utility scripts
│   ├── setup.sh
│   └── deploy.sh
├── .github/                # GitHub-specific files
├── .gitignore
├── README.md
├── LICENSE
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
├── requirements-dev.txt    # Dev dependencies
└── .env.example            # Environment template
```

**Verification:**
- [ ] All directories created
- [ ] __init__.py files in place
- [ ] Structure matches intended architecture

**If This Fails:**
→ **Permission error:** Check directory permissions
→ **Command not found:** Create manually or use Python script

---

### Step 3: Create Core Configuration Files

**What:** Set up essential configuration files for the project.

**How:**

**Create pyproject.toml:**
```bash
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "0.1.0"
description = "A brief description of your project"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

dependencies = [
    # Add your runtime dependencies here
    # "requests>=2.28.0",
    # "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.1",
    "black>=23.7.0",
    "ruff>=0.0.285",
    "mypy>=1.4.1",
    "pre-commit>=3.3.3",
]

test = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.1",
    "httpx>=0.24.1",  # For API testing
]

[project.scripts]
my-project = "my_project.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ['py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 88
target-version = "py310"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=src/my_project",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
]

[tool.coverage.run]
branch = true
source = ["src"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
EOF
```

**Create .gitignore:**
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.ruff_cache/

# Environment variables
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# CI/CD
*.pem
*.key

# Project specific
/data/
/output/
EOF
```

**Create .env.example:**
```bash
cat > .env.example << 'EOF'
# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://localhost:5432/myproject_dev

# API Keys (replace with your actual keys)
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here

# External Services
REDIS_URL=redis://localhost:6379
SENTRY_DSN=

# Feature Flags
ENABLE_FEATURE_X=False
EOF
```

**Create requirements files:**
```bash
# Main dependencies
cat > requirements.txt << 'EOF'
# Core dependencies
# Add your actual dependencies here based on project needs
# Example:
# fastapi==0.104.0
# uvicorn[standard]==0.24.0
# pydantic==2.4.2
# python-dotenv==1.0.0
EOF

# Development dependencies
cat > requirements-dev.txt << 'EOF'
-r requirements.txt

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-asyncio==0.21.1

# Code Quality
black==23.11.0
ruff==0.1.6
mypy==1.7.0

# Development
pre-commit==3.5.0
ipython==8.17.2
ipdb==0.13.13
EOF
```

**Verification:**
- [ ] pyproject.toml created with correct project name
- [ ] .gitignore includes Python patterns
- [ ] .env.example has template variables
- [ ] requirements files created
- [ ] All files have valid syntax

**If This Fails:**
→ **Syntax error:** Check TOML syntax with online validator
→ **File exists:** Use >> to append or remove existing file first

---

### Step 4: Create README and Documentation

**What:** Write comprehensive README with setup instructions.

**How:**

**Create README.md:**
```bash
cat > README.md << 'EOF'
# My Project

Brief one-line description of your project.

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- Python 3.10+
- PostgreSQL 14+ (if applicable)
- Redis (if applicable)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/username/my-project.git
cd my-project
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Initialize database (if applicable)

```bash
# Add your database setup commands
```

### 6. Run tests

```bash
pytest
```

## Usage

### Running locally

```bash
python -m my_project.main
# or
my-project
```

### Running tests

```bash
# All tests
pytest

# With coverage
pytest --cov

# Specific test file
pytest tests/unit/test_main.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Project Structure

```
src/my_project/     # Main application code
tests/              # Test suite
docs/               # Documentation
scripts/            # Utility scripts
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/username/my-project](https://github.com/username/my-project)
EOF
```

**Create LICENSE:**
```bash
# For MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

**Create CONTRIBUTING.md:**
```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to My Project

Thank you for considering contributing to this project!

## Development Setup

See [README.md](README.md) for installation instructions.

## Development Workflow

1. Create a branch for your work
2. Make your changes
3. Run tests and linters
4. Commit with clear messages
5. Push and create a Pull Request

## Code Standards

- Follow PEP 8 (enforced by Black and Ruff)
- Write tests for new features
- Add type hints to all functions
- Update documentation as needed

## Testing

Run all tests before submitting:

```bash
pytest
black --check src/ tests/
ruff check src/ tests/
mypy src/
```

## Pull Request Process

1. Update README.md with details of changes if applicable
2. Update documentation in `docs/`
3. Ensure all tests pass
4. Request review from maintainers
EOF
```

**Verification:**
- [ ] README.md has installation instructions
- [ ] LICENSE file present
- [ ] CONTRIBUTING.md explains workflow
- [ ] Documentation is clear and accurate

---

### Step 5: Set Up Pre-Commit Hooks

**What:** Configure automated code quality checks before commits.

**How:**

**Create .pre-commit-config.yaml:**
```bash
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
EOF
```

**Install pre-commit:**
```bash
# Install pre-commit package
pip install pre-commit

# Install the git hooks
pre-commit install

# Run on all files (optional, to test)
pre-commit run --all-files
```

**Verification:**
- [ ] .pre-commit-config.yaml created
- [ ] pre-commit installed: `pre-commit --version`
- [ ] Hooks installed in .git/hooks/
- [ ] Test run succeeds

**If This Fails:**
→ **Hook fails:** Fix the code issues it identifies
→ **Installation fails:** Ensure pre-commit is installed in venv

---

### Step 6: Create CI/CD Pipeline

**What:** Set up automated testing and deployment.

**How:**

**For GitHub Actions:**
```bash
mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Run linters
      run: |
        black --check src/ tests/
        ruff check src/ tests/
        mypy src/

    - name: Run tests
      run: |
        pytest --cov --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
EOF
```

**Verification:**
- [ ] .github/workflows/ci.yml created
- [ ] YAML syntax is valid
- [ ] Will run on push and PR

---

### Step 7: Create Initial Code

**What:** Add minimal working code to verify setup.

**How:**

**Create src/my_project/main.py:**
```python
"""Main entry point for the application."""
import sys
from typing import NoReturn


def main() -> int:
    """Main function.
    
    Returns:
        Exit code (0 for success)
    """
    print("Hello from my-project!")
    print(f"Python version: {sys.version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Create src/my_project/config.py:**
```python
"""Application configuration."""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    API_KEY: Optional[str] = os.getenv("API_KEY")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"


config = Config()
```

**Create tests/unit/test_main.py:**
```python
"""Tests for main module."""
import pytest
from my_project.main import main


def test_main_returns_zero():
    """Test that main returns 0 (success)."""
    result = main()
    assert result == 0


def test_main_runs_without_error(capsys):
    """Test that main runs and produces output."""
    result = main()
    captured = capsys.readouterr()
    
    assert result == 0
    assert "Hello from my-project!" in captured.out
    assert "Python version" in captured.out
```

**Create tests/conftest.py:**
```python
"""Pytest configuration and fixtures."""
import pytest


@pytest.fixture
def sample_fixture():
    """Example fixture for testing."""
    return {"key": "value"}
```

**Verification:**
- [ ] Code files created
- [ ] No syntax errors: `python -m py_compile src/my_project/*.py`
- [ ] Can import: `python -c "from my_project import main"`
- [ ] Tests exist and are valid

---

### Step 8: Initial Commit

**What:** Commit all scaffolding files to repository.

**How:**
```bash
# Stage all files
git add .

# Review what will be committed
git status

# Commit
git commit -m "Initial project scaffolding

- Set up project structure
- Configure tooling (black, ruff, mypy, pytest)
- Add CI/CD pipeline
- Create documentation (README, CONTRIBUTING)
- Add initial code and tests"

# Push to remote
git push -u origin main

# Verify on GitHub/GitLab
# Repository should now show all files
```

**Create develop branch:**
```bash
# Create and push develop branch
git checkout -b develop
git push -u origin develop

# Set develop as default branch (optional, via web interface)
```

**Verification:**
- [ ] All files committed
- [ ] Pushed to remote successfully
- [ ] Repository visible on GitHub/GitLab
- [ ] CI/CD pipeline triggered (check Actions tab)
- [ ] All checks passing

**If This Fails:**
→ **Push rejected:** Check authentication and permissions
→ **CI fails:** Review workflow logs and fix issues

---

## Verification Checklist

After completing this workflow, verify:

**Repository Structure:**
- [ ] Directory structure matches standard layout
- [ ] All __init__.py files in place
- [ ] src/ and tests/ directories exist

**Configuration Files:**
- [ ] pyproject.toml with correct metadata
- [ ] .gitignore with Python patterns
- [ ] .env.example for environment template
- [ ] requirements.txt and requirements-dev.txt

**Documentation:**
- [ ] README.md with clear instructions
- [ ] LICENSE file appropriate for project
- [ ] CONTRIBUTING.md with guidelines

**Code Quality:**
- [ ] Pre-commit hooks installed
- [ ] Black, Ruff, Mypy configured
- [ ] Pytest configured with coverage

**CI/CD:**
- [ ] GitHub Actions workflow created
- [ ] Pipeline runs on push/PR
- [ ] All checks passing

**Code:**
- [ ] Initial code compiles and runs
- [ ] Tests exist and pass
- [ ] Can install package: `pip install -e .`

**Git:**
- [ ] Repository initialized
- [ ] Remote configured
- [ ] Initial commit pushed
- [ ] Branches set up (main, develop)

---

## Common Issues & Solutions

### Issue: Permission denied when pushing to remote

**Symptoms:**
- `remote: Permission to user/repo denied`
- `fatal: unable to access`
- Authentication failures

**Solution:**
```bash
# Check remote URL
git remote -v

# For HTTPS, use token instead of password
git remote set-url origin https://TOKEN@github.com/user/repo.git

# Or switch to SSH
git remote set-url origin git@github.com:user/repo.git

# For SSH, ensure key is added
ssh-add ~/.ssh/id_rsa
ssh -T git@github.com  # Test connection

# Or use GitHub CLI
gh auth login
```

**Prevention:**
- Set up SSH keys before starting
- Or use GitHub CLI for authentication
- Store credentials in credential helper

---

### Issue: Pre-commit hooks fail on first run

**Symptoms:**
- `[INFO] Installing environment for hooks`
- Hooks fail with formatting/linting errors
- `Files were modified by this hook`

**Solution:**
```bash
# This is expected! Fix the issues:

# Let black format the code
black src/ tests/

# Fix ruff issues
ruff check --fix src/ tests/

# Fix mypy issues manually
mypy src/

# Run pre-commit again
pre-commit run --all-files

# If successful, commit
git add .
git commit -m "Fix code quality issues"
```

**Prevention:**
- Run pre-commit before first commit
- Format code as you write it
- Use IDE integration for linters

---

### Issue: Package installation fails

**Symptoms:**
- `pip install -e .` fails
- `ModuleNotFoundError` when running code
- Import errors

**Solution:**
```bash
# Check pyproject.toml syntax
python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))"

# Install in editable mode
pip install -e .

# Or install with dependencies
pip install -e ".[dev]"

# Verify installation
pip list | grep my-project

# Test import
python -c "from my_project import main"

# If still failing, check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

**Prevention:**
- Use editable install early
- Keep pyproject.toml syntax valid
- Test imports after setup

---

### Issue: CI/CD pipeline fails

**Symptoms:**
- GitHub Actions shows red X
- Tests pass locally but fail in CI
- "Command not found" errors

**Solution:**
```bash
# Common issues:

# 1. Missing dependencies
# Add to workflow:
pip install -e ".[dev,test]"

# 2. Environment differences
# Specify Python version explicitly
python-version: '3.11'

# 3. Path issues
# Use absolute imports, not relative

# 4. Missing environment variables
# Add to workflow secrets or hardcode test values

# Check workflow logs:
# GitHub: Actions tab → Failed workflow → Click on failed step

# Test locally with act (GitHub Actions locally)
act -j test
```

**Prevention:**
- Test with matrix of Python versions
- Pin dependencies
- Use consistent environments

---

### Issue: Import errors after installation

**Symptoms:**
- `ModuleNotFoundError: No module named 'my_project'`
- Wrong module imported
- Module found but empty

**Solution:**
```bash
# Check package is installed
pip list | grep my-project

# Verify __init__.py exists
ls src/my_project/__init__.py

# Check sys.path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall
pip uninstall my-project
pip install -e .

# Check from correct directory
cd /path/to/project
python -c "from my_project import main"

# Verify package structure
python -c "import my_project; print(my_project.__file__)"
```

**Prevention:**
- Always install in editable mode
- Use src/ layout to avoid import confusion
- Check __init__.py files exist

---

## Examples

### Example 1: FastAPI REST API Project

**Context:** Creating a new FastAPI microservice.

**Execution:**
```bash
# Step 1: Create repository
gh repo create my-api --public --clone
cd my-api

# Step 2: Create structure
mkdir -p src/my_api/{api,models,services}
mkdir -p tests/{unit,integration}
touch src/my_api/__init__.py
touch src/my_api/main.py
touch src/my_api/api/__init__.py
touch tests/__init__.py

# Step 3: Add FastAPI to pyproject.toml dependencies
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.4.0",
    "python-dotenv>=1.0.0",
]

# Step 4: Create main.py
cat > src/my_api/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(title="My API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

# Step 5: Configure CI for FastAPI
# Update .github/workflows/ci.yml to run uvicorn

# Step 6: Initial commit
git add .
git commit -m "Initial FastAPI project scaffolding"
git push
```

**Result:**
- FastAPI project structure
- Working API with health check
- CI/CD configured
- Ready for development

**Time:** ~30 minutes

---

### Example 2: Data Science Project

**Context:** Creating a project for ML experimentation.

**Execution:**
```bash
# Step 1: Create with different structure
mkdir -p notebooks
mkdir -p src/my_ds_project/{data,features,models}
mkdir -p data/{raw,processed,external}

# Step 2: Add DS dependencies to pyproject.toml
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "jupyter>=1.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
]

# Step 3: Create .gitignore additions for data
echo "data/raw/*.csv" >> .gitignore
echo "data/processed/*.csv" >> .gitignore
echo "*.ipynb_checkpoints" >> .gitignore
echo "models/*.pkl" >> .gitignore

# Step 4: Create notebook template
jupyter notebook  # Start server

# Step 5: Configure DVC for data versioning (optional)
pip install dvc
dvc init
dvc remote add -d storage s3://my-bucket/dvc

# Step 6: Commit
git add .
git commit -m "Initial data science project structure"
```

**Result:**
- Project optimized for data science
- Notebook support
- Data versioning ready
- Proper .gitignore for large files

---

### Example 3: CLI Tool Project

**Context:** Creating a command-line tool.

**Execution:**
```bash
# Step 1: Standard setup
gh repo create my-cli-tool --public --clone
cd my-cli-tool

# Step 2: Add CLI framework to pyproject.toml
dependencies = [
    "click>=8.1.0",  # or "typer>=0.9.0"
    "rich>=13.5.0",  # For beautiful output
]

# Add entry point in pyproject.toml
[project.scripts]
mytool = "my_cli_tool.cli:main"

# Step 3: Create CLI module
cat > src/my_cli_tool/cli.py << 'EOF'
import click

@click.group()
def main():
    """My CLI Tool - A helpful command-line utility."""
    pass

@main.command()
@click.option('--name', default='World', help='Name to greet')
def hello(name):
    """Say hello to someone."""
    click.echo(f'Hello {name}!')

if __name__ == '__main__':
    main()
EOF

# Step 4: Install and test
pip install -e .
mytool hello --name "User"

# Step 5: Add tests for CLI
cat > tests/unit/test_cli.py << 'EOF'
from click.testing import CliRunner
from my_cli_tool.cli import main

def test_hello_default():
    runner = CliRunner()
    result = runner.invoke(main, ['hello'])
    assert result.exit_code == 0
    assert 'Hello World!' in result.output
EOF
```

**Result:**
- Working CLI tool
- Installed as command
- Tests for CLI commands
- Rich output formatting

---

## Best Practices

### DO:
✅ **Use src/ layout** - Prevents import confusion and ensures proper installation
✅ **Include .gitignore from start** - Prevents accidental commits of sensitive data
✅ **Set up CI/CD immediately** - Catches issues early
✅ **Write README before code** - Forces you to think through the project
✅ **Use pyproject.toml** - Modern standard for Python projects
✅ **Include example .env file** - Documents required environment variables
✅ **Add pre-commit hooks** - Automatic code quality checks
✅ **Create CONTRIBUTING.md** - Helps onboard contributors
✅ **Use consistent naming** - Package names use underscores, repo names use hyphens
✅ **Document decisions early** - Add comments explaining non-obvious choices
✅ **Version from 0.1.0** - Semantic versioning from the start
✅ **Test the scaffold** - Run initial tests before development

### DON'T:
❌ **Put code in repo root** - Use src/ layout for proper structure
❌ **Skip .gitignore** - Will commit .env, __pycache__, etc.
❌ **Use setup.py** - It's legacy; use pyproject.toml
❌ **Mix underscores and hyphens** - Be consistent (underscores for packages)
❌ **Skip type hints** - Add them from the start
❌ **Commit .env files** - Use .env.example instead
❌ **Use vague project names** - Be descriptive but concise
❌ **Skip CI/CD setup** - Set it up early, fix it as you go
❌ **Over-engineer initially** - Start simple, add complexity as needed
❌ **Copy-paste old configs** - Outdated tools and practices

---

## Related Workflows

**Prerequisites:**
- None - this is typically the first workflow

**Next Steps:**
- [[dev-022]](environment_initialization.md) - Environment Initialization
- [[dev-024]](pre_commit_hooks.md) - Pre-Commit Hook Setup (if not included)
- [[sec-004]](../security/secret_management_solo.md) - Secret Management
- [[dev-025]](ci_cd_workflow.md) - CI/CD Workflow Setup (detailed)

**Alternatives:**
- Use cookiecutter templates for specific frameworks
- Use framework CLIs (django-admin startproject, fastapi-template)
- Clone and modify existing project template

**Complementary:**
- [[dvo-004]](../devops/cicd_pipeline_setup.md) - Full CI/CD Pipeline
- [[qua-008]](../quality-assurance/quality_gate_execution.md) - Quality Gates
- [[ver-001]](../version-control/branch_strategy.md) - Git Branch Strategy

---

## Tags
`development` `setup` `scaffolding` `project-structure` `python` `git` `ci-cd` `best-practices` `initialization` `automation`
