---
id: dev-003
title: Environment Initialization
category: Development
subcategory: Setup
tags:
  - setup
  - environment
  - python
  - virtual-environment
  - dependencies
  - configuration
prerequisites: []
related_workflows:
  - dev-005  # New Repo Scaffolding
  - dev-014  # Developer Onboarding
  - dev-004  # Pre-commit Hooks
  - sec-001  # Secret Management
complexity: beginner
estimated_time: 30-45 minutes
last_updated: 2025-10-25
---

# Environment Initialization

## Overview

**What:** Complete setup workflow for initializing a Python development environment with proper isolation, dependencies, configuration, and tooling for any project.

**Why:** A properly initialized environment ensures consistency across developers, eliminates "works on my machine" problems, prevents dependency conflicts, and accelerates onboarding. Isolated environments protect your system Python and enable working on multiple projects with different requirements.

**When to use:**
- Starting work on a new project (first time setup)
- Onboarding new team members to existing projects
- Setting up a new development machine
- Switching between projects with different dependencies
- After cloning a repository
- When you need to verify setup reproducibility
- Setting up CI/CD environments

---

## Prerequisites

**Required Software:**
- [ ] Python 3.10+ installed (`python --version`)
- [ ] pip (Python package manager) installed
- [ ] Git installed and configured
- [ ] Code editor or IDE installed
- [ ] Terminal/Command prompt access

**Required Knowledge:**
- [ ] Basic command line navigation (cd, ls, pwd)
- [ ] Understanding of virtual environments concept
- [ ] Basic git operations (clone, pull)
- [ ] How to edit text files

**Optional but Recommended:**
- [ ] Docker Desktop (for databases/services)
- [ ] PostgreSQL or MySQL client
- [ ] Postman or curl (for API testing)

**Check before starting:**
```bash
# Verify Python version (must be 3.10+)
python --version
python3 --version  # Try this if python doesn't work

# Verify pip
pip --version
pip3 --version  # Try this if pip doesn't work

# Verify git
git --version
git config --list  # Check git is configured

# Verify you're in project root
pwd  # Should show project directory
ls -la  # Should see files like README.md, requirements.txt
```

---

## Implementation Steps

### Step 1: Create and Activate Virtual Environment

**What:** Create an isolated Python environment to prevent dependency conflicts and system pollution.

**How:** Use Python's built-in `venv` module to create a directory containing its own Python interpreter and package space.

**Why this matters:**
- Isolates project dependencies from system Python
- Allows different projects to use different package versions
- Makes dependency management reproducible
- Prevents breaking system tools that depend on system Python

**Create virtual environment:**
```bash
# Using venv (built-in, recommended for Python 3.3+)
python -m venv venv

# Alternative names (all common conventions)
python -m venv .venv     # Hidden directory
python -m venv env       # Shorter name
python -m venv myproject-env  # Descriptive name

# Using specific Python version
python3.11 -m venv venv

# With system site packages (rarely needed)
python -m venv venv --system-site-packages
```

**Activate virtual environment:**

**On Windows (Command Prompt):**
```cmd
# Activate
venv\Scripts\activate.bat

# Verify activation
where python  # Should point to venv\Scripts\python.exe
```

**On Windows (PowerShell):**
```powershell
# May need to allow script execution first (one time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate
venv\Scripts\Activate.ps1

# Verify activation
Get-Command python  # Should point to venv
```

**On macOS/Linux (bash/zsh):**
```bash
# Activate
source venv/bin/activate

# Verify activation
which python  # Should point to venv/bin/python
echo $VIRTUAL_ENV  # Should show venv path
```

**Alternative: Using pyenv for Python version management:**
```bash
# Install pyenv (macOS with Homebrew)
brew install pyenv

# Install specific Python version
pyenv install 3.11.5

# Set Python version for this directory
pyenv local 3.11.5

# Create venv with that Python
python -m venv venv
source venv/bin/activate
```

**Alternative: Using conda:**
```bash
# Create conda environment
conda create -n myproject python=3.11

# Activate
conda activate myproject

# Deactivate
conda deactivate
```

**Verification:**
- [ ] Virtual environment directory created (should see `venv/` or `.venv/`)
- [ ] Environment is activated (prompt should show `(venv)` or environment name)
- [ ] `which python` points to virtual environment, not system Python
- [ ] `python --version` shows expected Python version
- [ ] `pip list` shows minimal packages (only pip, setuptools, wheel)

**If This Fails:**
→ **"No module named venv"** (Debian/Ubuntu): Install with `sudo apt-get install python3-venv`
→ **Permission denied**: Check directory permissions or run without sudo
→ **PowerShell script execution blocked**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
→ **Command not found**: Ensure Python is in PATH environment variable

---

### Step 2: Upgrade Core Package Management Tools

**What:** Update pip, setuptools, and wheel to latest versions before installing project dependencies.

**How:** Use pip to upgrade itself and related packaging tools.

**Why this matters:**
- Older pip versions have bugs and security issues
- Modern pip handles dependencies better
- Newer versions support modern package formats (wheels, PEP 517)
- Prevents installation failures with new packages

**Upgrade commands:**
```bash
# Method 1: Upgrade pip using itself (most common)
python -m pip install --upgrade pip

# Method 2: Upgrade all core tools at once (recommended)
python -m pip install --upgrade pip setuptools wheel

# Method 3: If pip is severely broken, use get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py

# Verify versions
pip --version  # Should show 23.0+
python -m pip --version  # More reliable way to call pip
```

**What each tool does:**
- **pip**: Package installer (like npm for Python)
- **setuptools**: Build system for Python packages
- **wheel**: Binary distribution format (faster installs)

**Additional useful tools:**
```bash
# Install pip-tools for dependency management
pip install pip-tools

# Install pipx for installing CLI tools globally
pip install pipx

# Ensure pipx PATH is configured
pipx ensurepath
```

**Verification:**
- [ ] pip upgraded to version 23.0+ (`pip --version`)
- [ ] setuptools and wheel installed (`pip show setuptools wheel`)
- [ ] No error messages during upgrade
- [ ] Can run `pip list` without warnings

**If This Fails:**
→ **SSL Certificate Error**: Use `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip`
→ **Permission error**: Ensure virtual environment is activated (never use sudo with pip)
→ **Network timeout**: Check internet connection or configure corporate proxy
→ **"Failed building wheel"**: This is usually okay, packages will be installed from source instead

---

### Step 3: Install Project Dependencies

**What:** Install all required Python packages for the project according to dependency specification files.

**How:** Use pip to install packages from requirements files or pyproject.toml.

**Dependency file types:**

**1. requirements.txt (most common):**
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install test dependencies
pip install -r requirements-test.txt

# Install all at once
pip install -r requirements.txt -r requirements-dev.txt
```

**2. pyproject.toml with pip:**
```bash
# Install package in editable mode
pip install -e .

# Install with optional dependency groups
pip install -e ".[dev]"
pip install -e ".[dev,test,docs]"
```

**3. Poetry (if project uses it):**
```bash
# Install poetry first
pip install poetry

# Install dependencies
poetry install

# Install without development dependencies
poetry install --no-dev

# Activate poetry's virtual environment
poetry shell
```

**4. Pipenv (if project uses it):**
```bash
# Install pipenv first
pip install pipenv

# Install from Pipfile
pipenv install

# Install development dependencies too
pipenv install --dev

# Activate pipenv shell
pipenv shell
```

**Multi-file requirements structure:**
```bash
# Common pattern:
requirements/
├── base.txt          # Core dependencies (always needed)
├── development.txt   # Dev tools (includes base.txt)
├── testing.txt       # Test tools (includes base.txt)
└── production.txt    # Production-specific (includes base.txt)

# Install for development
pip install -r requirements/base.txt
pip install -r requirements/development.txt
pip install -r requirements/testing.txt

# Or if development.txt includes base.txt
pip install -r requirements/development.txt
```

**Example requirements.txt formats:**
```txt
# Basic format
flask==2.3.0
requests==2.31.0
sqlalchemy==2.0.0

# With comments
flask==2.3.0      # Web framework
requests==2.31.0  # HTTP client
sqlalchemy==2.0.0 # Database ORM

# Version constraints
flask>=2.0.0,<3.0.0  # Compatible with Flask 2.x
requests~=2.31.0     # Compatible release (2.31.x)
pandas>=1.5.0        # Minimum version

# From GitHub (development versions)
git+https://github.com/user/repo.git@main#egg=package

# From local path (for development)
-e /path/to/local/package

# Including other requirement files
-r base.txt
```

**Dealing with problematic packages:**
```bash
# Install specific packages first if they have special requirements
pip install numpy  # Must be installed before some scientific packages
pip install -r requirements.txt

# Install with no dependencies (if dependency resolution fails)
pip install --no-deps package_name

# Install from wheel only (skip source builds)
pip install --only-binary :all: package_name

# Install with specific index URL
pip install --index-url https://pypi.org/simple package_name
```

**Verification:**
- [ ] All packages installed without errors
- [ ] Can import key packages: `python -c "import flask; print(flask.__version__)"`
- [ ] No dependency conflicts: `pip check`
- [ ] Expected package count: `pip list | wc -l`
- [ ] Verify specific packages: `pip show flask requests`

**If This Fails:**
→ **Compilation errors (C extensions):**
  - **Windows**: Install Visual Studio Build Tools from Microsoft
  - **macOS**: Install Xcode Command Line Tools: `xcode-select --install`
  - **Linux**: Install build tools: `sudo apt-get install build-essential python3-dev`

→ **Version conflict**: Check requirements.txt for conflicting version specifications
  ```bash
  # Find conflicts
  pip check
  
  # See dependency tree
  pip install pipdeptree
  pipdeptree
  ```

→ **Package not found**: Check package name spelling, may have been renamed or removed from PyPI

→ **Slow installation**: Use `--use-pep517` flag or consider using a local package mirror

---

### Step 4: Configure Environment Variables

**What:** Set up environment-specific configuration and secrets using a `.env` file.

**How:** Create and populate a `.env` file from template, ensuring secrets are not committed to version control.

**Why this matters:**
- Separates configuration from code (12-factor app principle)
- Keeps secrets out of version control
- Allows different settings per environment (dev/staging/prod)
- Makes configuration changes easy without code changes

**Create .env file:**
```bash
# Copy template file
cp .env.example .env

# Or create from scratch
cat > .env << 'EOF'
# Application
DEBUG=True
LOG_LEVEL=DEBUG
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://localhost:5432/myapp_dev

# External APIs
API_KEY=your-api-key-here
THIRD_PARTY_URL=https://api.example.com

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@example.com
EMAIL_PASSWORD=your-password
EOF

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

**Common .env patterns:**

**Development environment:**
```bash
# .env (development)
ENV=development
DEBUG=True
LOG_LEVEL=DEBUG

# Use local database
DATABASE_URL=postgresql://postgres:password@localhost:5432/myapp_dev

# Disable external services or use mocks
SEND_EMAILS=False
USE_CACHE=False

# Relaxed security for development
SECRET_KEY=dev-secret-key-not-for-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional: Enable debug toolbar
ENABLE_DEBUG_TOOLBAR=True
```

**Loading environment variables in Python:**

**Using python-dotenv (recommended):**
```python
# Install python-dotenv
pip install python-dotenv

# In your config.py or settings.py
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
DEBUG = os.getenv("DEBUG", "False") == "True"
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# With defaults
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
```

**Using pydantic-settings (type-safe):**
```python
# Install pydantic-settings
pip install pydantic-settings

# In your config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
    database_url: str
    secret_key: str
    api_key: str = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Use settings
settings = Settings()
print(settings.database_url)
```

**.env file security best practices:**
```bash
# ✅ DO:
# 1. Add .env to .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore  # Keep template

# 2. Provide .env.example with dummy values
# .env.example
DATABASE_URL=postgresql://localhost:5432/myapp_dev
SECRET_KEY=change-me-in-production
API_KEY=get-from-team-lead

# 3. Document required variables
# docs/CONFIGURATION.md
cat > docs/CONFIGURATION.md << 'EOF'
# Required Environment Variables

## DATABASE_URL
PostgreSQL connection string
Example: postgresql://user:pass@localhost:5432/dbname

## SECRET_KEY
Secret key for session encryption (min 32 chars)
Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

## API_KEY
Third-party API key
Obtain from: https://api.example.com/settings
EOF

# ❌ DON'T:
# - Commit .env files to git
# - Store production secrets in .env
# - Use weak default secrets
# - Share .env files via email/Slack
```

**Generate secure secrets:**
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate UUID
python -c "import uuid; print(uuid.uuid4())"

# Generate password
python -c "import secrets, string; chars = string.ascii_letters + string.digits; print(''.join(secrets.choice(chars) for _ in range(32)))"
```

**Verification:**
- [ ] .env file created and populated
- [ ] .env is in .gitignore (check with `git status`)
- [ ] Can load variables: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DEBUG'))"`
- [ ] All required variables defined
- [ ] No plain text secrets in version control

**If This Fails:**
→ **Variables not loading**: Ensure python-dotenv is installed and load_dotenv() is called before accessing
→ **Wrong values**: Check for typos, extra spaces, or quotes in .env file
→ **File not found**: Verify .env is in project root or specify path: `load_dotenv('.env')`

---

### Step 5: Initialize Database (if applicable)

**What:** Set up local database, create schema, and optionally load seed data.

**How:** Use project-specific database initialization commands or scripts.

**Database options for local development:**

**Option 1: Docker Compose (recommended):**
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
# Start database
docker-compose up -d db

# Check if running
docker-compose ps

# View logs
docker-compose logs db

# Stop database
docker-compose down

# Reset database (delete data)
docker-compose down -v
```

**Option 2: Local PostgreSQL:**
```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb myapp_dev

# Or using psql
psql postgres
CREATE DATABASE myapp_dev;
\q

# Test connection
psql -d myapp_dev -c "SELECT version();"
```

**Option 3: SQLite (for simple projects):**
```bash
# No installation needed, database is just a file
# Configured in .env
DATABASE_URL=sqlite:///./myapp.db

# SQLite browser for GUI
brew install --cask db-browser-for-sqlite
```

**Run database migrations:**

**Django:**
```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load fixture data (if available)
python manage.py loaddata fixtures/initial_data.json

# Show migration status
python manage.py showmigrations
```

**Flask with Alembic:**
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head

# Or using Flask-Migrate
flask db upgrade

# Show current revision
alembic current
```

**SQLAlchemy without framework:**
```python
# In scripts/init_db.py
from app.database import engine, Base
from app.models import User, Post  # Import all models

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database initialized successfully")
```

```bash
# Run script
python scripts/init_db.py
```

**Database seeding:**
```python
# scripts/seed_db.py
from app.database import SessionLocal
from app.models import User, Post

def seed_database():
    """Populate database with test data."""
    db = SessionLocal()
    
    try:
        # Create test users
        users = [
            User(username="alice", email="alice@example.com"),
            User(username="bob", email="bob@example.com"),
        ]
        db.add_all(users)
        db.commit()
        
        # Create test posts
        posts = [
            Post(title="First Post", content="Hello World", author_id=1),
            Post(title="Second Post", content="Test content", author_id=2),
        ]
        db.add_all(posts)
        db.commit()
        
        print(f"Created {len(users)} users and {len(posts)} posts")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
```

```bash
# Run seed script
python scripts/seed_db.py
```

**Verification:**
- [ ] Database service is running
- [ ] Can connect to database: `python -c "from app.database import engine; print(engine.connect())"`
- [ ] Tables created: Check with database client or SQL query
- [ ] Migrations applied: Check migration status
- [ ] Can insert and query data: `python -c "from app.database import SessionLocal; from app.models import User; db = SessionLocal(); print(db.query(User).count())"`

**If This Fails:**
→ **Connection refused**: Ensure database is running (`docker-compose ps` or `brew services list`)
→ **Authentication failed**: Check DATABASE_URL credentials match database configuration
→ **Database doesn't exist**: Create it manually: `createdb myapp_dev` (PostgreSQL) or it will be created automatically (SQLite)
→ **Migration error**: Check migration files for syntax errors or incompatible changes

---

### Step 6: Install and Configure Development Tools

**What:** Set up code formatters, linters, type checkers, and other development tools.

**How:** Install tools via pip and configure them for the project.

**Essential development tools:**

**1. Code Formatting:**
```bash
# Black - Python code formatter
pip install black

# Configure in pyproject.toml
cat >> pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
EOF

# Format code
black .
black src/  # Format specific directory
black --check .  # Check without modifying

# isort - Import sorting
pip install isort

# Configure in pyproject.toml
cat >> pyproject.toml << 'EOF'
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
EOF

# Sort imports
isort .
isort --check-only .
```

**2. Linting:**
```bash
# Ruff - Fast Python linter (recommended)
pip install ruff

# Configure in pyproject.toml
cat >> pyproject.toml << 'EOF'
[tool.ruff]
line-length = 88
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__
"tests/*" = ["S101"]      # Allow assert in tests
EOF

# Run linter
ruff check .
ruff check --fix .  # Auto-fix issues

# Alternative: flake8
pip install flake8 flake8-bugbear flake8-comprehensions

# Configure in .flake8
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, E501
exclude = .git,__pycache__,venv,build,dist
max-complexity = 10
EOF

# Run flake8
flake8 src/
```

**3. Type Checking:**
```bash
# mypy - Static type checker
pip install mypy

# Configure in pyproject.toml
cat >> pyproject.toml << 'EOF'
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start permissive
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
EOF

# Run type checker
mypy src/
mypy --strict src/  # Strict mode
```

**4. Testing Tools:**
```bash
# pytest - Testing framework
pip install pytest pytest-cov pytest-mock pytest-asyncio

# Configure in pyproject.toml
cat >> pyproject.toml << 'EOF'
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
EOF

# Run tests
pytest
pytest -v  # Verbose
pytest --cov  # With coverage
pytest -k test_user  # Run specific tests
pytest -m "not slow"  # Skip slow tests
```

**5. Pre-commit Hooks:**
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

# Install hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Run hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

**6. IDE Configuration (VS Code):**
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.rulers": [88]
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true
  }
}
```

```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "tamasfe.even-better-toml",
    "eamodio.gitlens"
  ]
}
```

**Verification:**
- [ ] All tools installed: `black --version`, `ruff --version`, `mypy --version`, `pytest --version`
- [ ] Tools run without errors: `black --check .`, `ruff check .`, `mypy src/`
- [ ] Pre-commit hooks installed: `pre-commit run --all-files`
- [ ] IDE configured (extensions recommended, settings applied)
- [ ] Tests run successfully: `pytest`

**If This Fails:**
→ **Tool conflicts**: Check for conflicting configurations in pyproject.toml vs separate config files
→ **Pre-commit fails**: Run `pre-commit run` to see which hook fails, fix that specific issue
→ **mypy errors**: Start with permissive settings, gradually increase strictness
→ **Tests fail**: This might be expected initially - verify tests are properly written

---

### Step 7: Verify Setup with Tests and Application

**What:** Run the test suite and start the application to verify everything is working.

**How:** Execute tests, check coverage, and start the development server.

**Run comprehensive tests:**
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test categories
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests

# Run tests in parallel (faster)
pytest -n auto  # Requires pytest-xdist

# Run tests with detailed output on failure
pytest -vv --tb=short

# Run only failed tests from last run
pytest --lf  # Last failed
pytest --ff  # Failed first, then others

# Generate coverage HTML report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

**Run linters and formatters:**
```bash
# Check code formatting
black --check .
isort --check-only .

# Check linting
ruff check .
flake8 src/

# Run type checker
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files

# Create script for quick checks
cat > scripts/check.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Running code checks..."

echo "📏 Checking code formatting..."
black --check .
isort --check-only .

echo "🔎 Running linter..."
ruff check .

echo "📘 Running type checker..."
mypy src/

echo "🧪 Running tests..."
pytest

echo "✅ All checks passed!"
EOF

chmod +x scripts/check.sh
./scripts/check.sh
```

**Start the application:**

**Flask:**
```bash
# Development server
flask run

# With specific host/port
flask run --host=0.0.0.0 --port=8000

# With debug mode
FLASK_ENV=development flask run

# With auto-reload
flask run --reload
```

**Django:**
```bash
# Development server
python manage.py runserver

# Specific port
python manage.py runserver 8001

# All interfaces
python manage.py runserver 0.0.0.0:8000
```

**FastAPI:**
```bash
# Development server with auto-reload
uvicorn main:app --reload

# Specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# With workers (production-like)
uvicorn main:app --workers 4
```

**Verify application is running:**
```bash
# Check health endpoint
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health

# Or use httpie (more readable)
http http://localhost:8000/health

# Check API documentation
# FastAPI: http://localhost:8000/docs
# Browse to see interactive API docs

# Check application logs
# Should show successful startup, database connection, etc.
```

**Create comprehensive verification script:**
```bash
# scripts/verify_setup.sh
cat > scripts/verify_setup.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying development environment setup..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${RED}❌ Virtual environment not activated${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Virtual environment active: $VIRTUAL_ENV${NC}"
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python version: $PYTHON_VERSION${NC}"

# Check required packages
echo "📦 Checking required packages..."
python -c "import flask" 2>/dev/null && echo -e "${GREEN}✅ Flask installed${NC}" || echo -e "${RED}❌ Flask not installed${NC}"
python -c "import pytest" 2>/dev/null && echo -e "${GREEN}✅ Pytest installed${NC}" || echo -e "${RED}❌ Pytest not installed${NC}"
python -c "import black" 2>/dev/null && echo -e "${GREEN}✅ Black installed${NC}" || echo -e "${RED}❌ Black not installed${NC}"

# Check environment variables
if [ -f .env ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
else
    echo -e "${RED}❌ .env file missing${NC}"
fi

# Check database connection
python -c "from app.database import engine; engine.connect()" 2>/dev/null && echo -e "${GREEN}✅ Database connection works${NC}" || echo -e "${RED}❌ Database connection failed${NC}"

# Run tests
echo "🧪 Running tests..."
pytest --tb=short -q && echo -e "${GREEN}✅ Tests passed${NC}" || echo -e "${RED}❌ Tests failed${NC}"

echo ""
echo -e "${GREEN}🎉 Setup verification complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Start the application: flask run"
echo "2. Visit: http://localhost:5000"
echo "3. Start developing!"
EOF

chmod +x scripts/verify_setup.sh
./scripts/verify_setup.sh
```

**Verification:**
- [ ] All tests pass (or expected failures documented)
- [ ] No linting errors (or acceptable warnings documented)
- [ ] Type checking passes (or known issues documented)
- [ ] Application starts without errors
- [ ] Can access application at localhost (health check returns 200)
- [ ] Database connection works
- [ ] Can make API requests successfully
- [ ] Development tools (debugger, hot reload) work

**If This Fails:**
→ **Tests fail**: Review test output, may be environmental differences or expected failures
→ **Linting errors**: Run `black .` and `ruff check --fix .` to auto-fix many issues
→ **App won't start**: Check logs for specific error, verify DATABASE_URL, check port conflicts
→ **Database connection fails**: Ensure database is running, check connection string

---

### Step 8: Document Setup and Create Runbook

**What:** Document your specific setup, any deviations from standard process, and create operational runbook.

**How:** Create documentation files for future reference and team members.

**Create local setup notes:**
```bash
# Create personal setup notes (not committed)
cat > SETUP_NOTES.local.md << 'EOF'
# Local Development Setup Notes

**Setup Date:** $(date)
**Setup By:** $(whoami)

## Environment Details
- **OS:** $(uname -s) $(uname -r)
- **Python Version:** $(python --version)
- **Pip Version:** $(pip --version)
- **Virtual Environment:** $(echo $VIRTUAL_ENV)

## Deviations from Standard Setup
- Using port 8001 instead of 8000 (port conflict with other project)
- PostgreSQL installed via Homebrew instead of Docker
- Added custom .env variables for local testing

## Setup Time
- Total setup time: 45 minutes
- Main blockers: Had to install Xcode Command Line Tools

## Tips for Next Time
- Run `brew install postgresql@15` before starting
- Remember to activate virtual environment!
- Use `./scripts/verify_setup.sh` to check everything

## Local Configuration
- Database: postgresql://localhost:5432/myapp_dev
- API runs on: http://localhost:8001
- Logs location: ./logs/development.log

## Useful Commands
```bash
# Start everything
./scripts/start_dev.sh

# Run tests quickly
pytest -x  # Stop on first failure

# Database shell
psql myapp_dev
```

## Team Contacts
- Setup help: @tech-lead
- Database access: @devops
- API keys: @product-manager
EOF

# Add to .gitignore
echo "SETUP_NOTES.local.md" >> .gitignore
```

**Create developer runbook:**
```bash
# docs/RUNBOOK.md
cat > docs/RUNBOOK.md << 'EOF'
# Developer Runbook

## Daily Development Workflow

### Starting Work
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Update dependencies (if needed)
git pull
pip install -r requirements.txt

# 3. Run database migrations
flask db upgrade

# 4. Start services
docker-compose up -d  # Database, Redis, etc.

# 5. Start application
flask run
```

### Before Committing
```bash
# 1. Run tests
pytest

# 2. Check code quality
./scripts/check.sh

# 3. Commit with pre-commit hooks
git add .
git commit -m "feat: your message"
```

### Ending Work
```bash
# 1. Stop application (Ctrl+C)

# 2. Stop services (optional, can leave running)
docker-compose down

# 3. Deactivate virtual environment (optional)
deactivate
```

## Common Tasks

### Adding New Dependency
```bash
# 1. Install package
pip install new-package

# 2. Update requirements
pip freeze > requirements.txt

# Or better: use pip-tools
echo "new-package>=1.0.0" >> requirements.in
pip-compile requirements.in
pip install -r requirements.txt

# 3. Commit the change
git add requirements.txt
git commit -m "chore: add new-package dependency"
```

### Database Operations
```bash
# Create migration
flask db migrate -m "add user table"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade

# Reset database (careful!)
flask db downgrade base
flask db upgrade
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_users.py

# Specific test
pytest tests/test_users.py::test_create_user

# With coverage
pytest --cov=src --cov-report=html

# Watch mode (requires pytest-watch)
ptw
```

### Debugging
```bash
# Use built-in debugger
import pdb; pdb.set_trace()

# Or use iPython debugger (better)
import ipdb; ipdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# Run with debugger attached
python -m pdb manage.py runserver
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Database Connection Refused
```bash
# Check if PostgreSQL is running
pg_isready
# Or
docker-compose ps

# Restart if needed
brew services restart postgresql@15
# Or
docker-compose restart db
```

### Tests Failing
```bash
# Reset test database
flask db downgrade base
flask db upgrade

# Clear pytest cache
rm -rf .pytest_cache

# Run with verbose output
pytest -vv --tb=long
```

### Import Errors
```bash
# Verify virtual environment is active
which python

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

## Performance Tips
- Use `pytest -n auto` for parallel testing
- Use `--lf` to run only failed tests
- Use `docker-compose up -d` to run services in background
- Add `__pycache__` to .gitignore

## Security Reminders
- Never commit .env files
- Rotate API keys regularly
- Use strong SECRET_KEY in production
- Keep dependencies updated
EOF
```

**Create quick start script:**
```bash
# scripts/start_dev.sh
cat > scripts/start_dev.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting development environment..."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Copy from .env.example"
    exit 1
fi

# Start services
echo "📦 Starting services (database, redis)..."
docker-compose up -d

# Wait for database
echo "⏳ Waiting for database..."
sleep 3

# Run migrations
echo "🗄️  Running database migrations..."
flask db upgrade

# Start application
echo "🎉 Starting application..."
echo "Visit: http://localhost:5000"
flask run
EOF

chmod +x scripts/start_dev.sh
```

**Update project README:**
```bash
# Add quick start section to README.md
cat >> README.md << 'EOF'

## Quick Start for Developers

### First Time Setup
```bash
# 1. Clone repository
git clone https://github.com/company/project.git
cd project

# 2. Run setup
./scripts/setup_dev_environment.sh

# 3. Start developing
./scripts/start_dev.sh
```

### Development Workflow
See [docs/RUNBOOK.md](docs/RUNBOOK.md) for detailed development instructions.

### Getting Help
- Technical questions: #engineering-help
- Setup issues: @tech-lead
- Bug reports: GitHub Issues
EOF
```

**Verification:**
- [ ] SETUP_NOTES.local.md created with environment details
- [ ] RUNBOOK.md created with common tasks
- [ ] Start script created and tested
- [ ] README updated with quick start
- [ ] Documentation is accurate and helpful

---

## Verification Checklist

After completing this workflow, verify:

**Environment:**
- [ ] Virtual environment created at `venv/` or `.venv/`
- [ ] Python version is 3.10+ (`python --version`)
- [ ] pip upgraded to 23.0+ (`pip --version`)
- [ ] Virtual environment is activated (prompt shows `(venv)`)

**Dependencies:**
- [ ] All packages from requirements.txt installed
- [ ] `pip check` shows no conflicts
- [ ] Can import main dependencies without errors
- [ ] Development tools installed (black, ruff, mypy, pytest)

**Configuration:**
- [ ] .env file exists and populated
- [ ] .env is in .gitignore
- [ ] Environment variables load correctly
- [ ] No secrets in version control

**Database:**
- [ ] Database service running
- [ ] Database created
- [ ] Migrations applied
- [ ] Can connect from application

**Development Tools:**
- [ ] Pre-commit hooks installed (`pre-commit run --all-files`)
- [ ] IDE configured with virtual environment
- [ ] Code formatters work (black, isort)
- [ ] Linters work (ruff, flake8)
- [ ] Type checker works (mypy)

**Application:**
- [ ] Tests run and pass (`pytest`)
- [ ] Application starts (`flask run` or equivalent)
- [ ] Can access at localhost
- [ ] Health endpoint returns 200
- [ ] Can make successful API requests

**Documentation:**
- [ ] Setup notes created
- [ ] Runbook documented
- [ ] README updated
- [ ] Known issues documented

---

## Best Practices

### DO:
✅ Use virtual environments for every project
✅ Upgrade pip before installing dependencies
✅ Keep .env out of version control
✅ Document your setup process
✅ Run tests before committing
✅ Use pre-commit hooks
✅ Keep dependencies up to date
✅ Verify setup with automated script
✅ Use consistent Python version across team
✅ Create project-specific scripts for common tasks
✅ Test setup on fresh machine periodically
✅ Provide .env.example with documentation

### DON'T:
❌ Install packages globally (always use virtual environment)
❌ Use `sudo pip install` (breaks environment isolation)
❌ Commit .env files or secrets
❌ Skip dependency version pinning
❌ Mix pip and conda without careful management
❌ Ignore failed tests after setup
❌ Use incompatible Python versions
❌ Skip database initialization
❌ Forget to activate virtual environment
❌ Install unnecessary dependencies
❌ Use different database engines in dev vs prod

---

## Common Patterns

### Pattern 1: Makefile for Common Commands
```makefile
# Makefile
.PHONY: install test lint format clean run

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest --cov=src --cov-report=html

lint:
	black --check .
	ruff check .
	mypy src/

format:
	black .
	isort .
	ruff check --fix .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov

run:
	flask run

db-reset:
	flask db downgrade base
	flask db upgrade
```

Usage:
```bash
make install  # Setup environment
make test     # Run tests
make lint     # Check code quality
make format   # Auto-format code
make run      # Start app
```

### Pattern 2: Docker Compose for All Services
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME:-myapp_dev}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  mailhog:  # Email testing
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI

volumes:
  postgres_data:
  redis_data:
```

### Pattern 3: Environment-Specific Requirements
```bash
# requirements/base.txt - Core dependencies
flask==2.3.0
sqlalchemy==2.0.0
pydantic==2.0.0

# requirements/development.txt
-r base.txt
black==23.12.0
pytest==7.4.0
ipython==8.18.0
pytest-cov==4.1.0

# requirements/production.txt
-r base.txt
gunicorn==21.2.0
psycopg[binary]==3.1.0
```

---

## Troubleshooting

### Issue: Virtual environment activation fails on Windows PowerShell

**Symptoms:**
- `Activate.ps1 cannot be loaded because running scripts is disabled`
- Permission denied error

**Solution:**
```powershell
# Check execution policy
Get-ExecutionPolicy

# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\Activate.ps1
```

**Prevention:**
- Set execution policy before creating virtual environment
- Use Windows Terminal instead of PowerShell ISE
- Document this step in setup instructions

---

### Issue: pip install fails with SSL certificate errors

**Symptoms:**
- `SSL: CERTIFICATE_VERIFY_FAILED`
- `Could not fetch URL`
- Connection timeout

**Solution:**
```bash
# Temporary: Trust PyPI hosts
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org package_name

# Permanent: Update certificates
pip install --upgrade certifi

# Corporate proxy: Configure pip
pip config set global.proxy http://proxy.company.com:8080
pip config set global.trusted-host pypi.org files.pythonhosted.org

# Or use environment variables
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=https://proxy:8080
pip install -r requirements.txt
```

**Prevention:**
- Update system certificates regularly
- Configure proxy before starting setup
- Use company PyPI mirror if available

---

### Issue: Package compilation fails (C extensions)

**Symptoms:**
- `error: Microsoft Visual C++ 14.0 is required`
- `gcc: command not found`
- Build failure for psycopg2, lxml, Pillow

**Solution:**

**Windows:**
```powershell
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Or install pre-built wheels
pip install --only-binary :all: psycopg2

# Use psycopg3 instead (has binary wheels)
pip install "psycopg[binary]"
```

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# For specific packages, install dependencies
brew install postgresql  # For psycopg2
brew install libxml2      # For lxml
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential python3-dev
sudo apt-get install libpq-dev  # PostgreSQL
sudo apt-get install libxml2-dev libxslt1-dev  # lxml

# Fedora/RHEL
sudo dnf install gcc python3-devel
sudo dnf install postgresql-devel
```

**Prevention:**
- Install build tools before starting
- Use packages with binary wheels when available
- Document required system packages in README

---

### Issue: Import errors despite packages being installed

**Symptoms:**
- `ModuleNotFoundError: No module named 'package'`
- Package shows in `pip list` but won't import
- Different behavior in IDE vs terminal

**Solution:**
```bash
# Verify you're in correct virtual environment
which python  # Should point to venv/bin/python
echo $VIRTUAL_ENV  # Should show venv path

# Verify package is installed in this environment
pip show package_name

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall package
pip uninstall package_name
pip install package_name

# Install in editable mode if working on package itself
pip install -e .

# For IDE (VS Code): Select correct Python interpreter
# Cmd/Ctrl+Shift+P → "Python: Select Interpreter" → Choose venv
```

**Prevention:**
- Always activate virtual environment before work
- Configure IDE to use virtual environment Python
- Use absolute imports: `from myproject.module import func`
- Add virtual environment to .gitignore

---

### Issue: Database connection fails

**Symptoms:**
- `could not connect to server: Connection refused`
- `FATAL: password authentication failed`
- `database "myapp" does not exist`

**Solution:**
```bash
# Check if database is running
# PostgreSQL
pg_isready -h localhost -p 5432
# Or check service status
brew services list | grep postgresql
docker-compose ps

# Start database if not running
brew services start postgresql@15
# Or
docker-compose up -d db

# Create database if it doesn't exist
createdb myapp_dev
# Or
psql postgres -c "CREATE DATABASE myapp_dev;"

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL
# Should be: postgresql://user:password@localhost:5432/myapp_dev

# Test connection
psql -d myapp_dev -c "SELECT version();"

# Check user permissions
psql postgres
\du  # List users
GRANT ALL PRIVILEGES ON DATABASE myapp_dev TO your_user;
```

**Prevention:**
- Start database before application
- Use Docker Compose for consistent database setup
- Document database setup in README
- Use health checks in docker-compose.yml

---

## Related Workflows

**Prerequisites:**
- None (this is typically the first workflow)

**Next Steps:**
- [[dev-004]] Pre-commit Hook Setup - Add automated code quality checks
- [[dev-014]] Developer Onboarding - Complete team onboarding process
- [[dev-002]] Test Writing - Begin writing tests
- [[sec-001]] Secret Management - Secure sensitive data

**Related:**
- [[dev-005]] New Repo Scaffolding - Creating new project structure
- [[dep-002]] Docker Container Creation - Containerizing your application
- [[cfg-001]] Configuration Management - Advanced configuration patterns

---

## Tags
`development` `setup` `environment` `python` `virtual-environment` `dependencies` `configuration` `initialization` `onboarding` `prerequisites`
