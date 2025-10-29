# Application Settings Management

**ID:** config-001  
**Category:** Configuration Management  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 30-45 minutes  
**Frequency:** Once per project + updates as needed  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Centralized configuration management for application settings using environment-specific configurations, environment variables, and structured settings classes.

**Why:** 
- Separates configuration from code for better security and flexibility
- Enables different configurations for dev, staging, and production
- Provides type safety and validation for configuration values
- Simplifies deployment and environment management
- Reduces configuration errors through structured approach

**When to use:**
- Setting up a new project's configuration system
- Migrating from hardcoded values to environment-based config
- Implementing multi-environment deployments
- Adding new configuration parameters to existing projects
- Standardizing configuration across microservices

---

## Prerequisites

**Required Knowledge:**
- [ ] Understanding of environment variables
- [ ] Python configuration patterns
- [ ] Basic security principles for secrets
- [ ] Environment-specific deployment concepts

**Required Tools:**
- [ ] Python 3.8+ installed
- [ ] Access to environment variable management (shell, Docker, K8s)
- [ ] Text editor or IDE
- [ ] Git for version control

**Required Files:**
- [ ] Project root directory
- [ ] `.env.example` template (will be created)

**Check before starting:**
```bash
python --version  # Should show 3.8+
pip --version     # Should be available
```

---

## Dependencies

**Auto-Load These Workflows:**
- None (foundational workflow)

**Called By These Workflows:**
- [[dev-002]](../development/environment_initialization.md) - Environment setup
- [[devops-001]](../devops/cicd_pipeline_setup.md) - CI/CD configuration
- [[sec-001]](../security/secret_management_solo.md) - Secret management

**Related Workflows:**
- [[config-002]](./pydantic_settings_configuration.md) - Advanced Pydantic-based settings
- [[devops-005]](../devops/docker_container_creation.md) - Docker environment variables

---

## Implementation Steps

### Step 1: Choose Configuration Strategy

**What:** Select the appropriate configuration approach based on project complexity.

**Why:** Different projects need different levels of configuration sophistication.

**How:**

**Simple Projects (< 10 settings):**
```python
# config.py - Simple dictionary-based
import os

config = {
    'DEBUG': os.getenv('DEBUG', 'False') == 'True',
    'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///./app.db'),
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
}
```

**Medium Projects (10-30 settings):**
```python
# config.py - Class-based with validation
import os
from typing import Literal

class Config:
    """Application configuration"""
    
    # App Settings
    DEBUG: bool = os.getenv('DEBUG', 'False') == 'True'
    ENV: Literal['development', 'staging', 'production'] = os.getenv('ENV', 'development')
    APP_NAME: str = os.getenv('APP_NAME', 'MyApp')
    VERSION: str = os.getenv('VERSION', '1.0.0')
    
    # Database Settings
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
    DB_POOL_SIZE: int = int(os.getenv('DB_POOL_SIZE', '10'))
    DB_MAX_OVERFLOW: int = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    # Redis Settings
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security Settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key')
    CORS_ORIGINS: list[str] = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> None:
        """Validate critical settings"""
        if cls.ENV == 'production':
            assert cls.SECRET_KEY != 'dev-secret-key', "Production must have custom SECRET_KEY"
            assert cls.DEBUG is False, "Production must have DEBUG=False"

# Initialize and validate
config = Config()
config.validate()
```

**Large Projects (30+ settings) - Use Pydantic:**
See [[config-002]](./pydantic_settings_configuration.md) for Pydantic-based approach.

**Verification:**
- [ ] Configuration strategy selected based on project size
- [ ] Implementation approach documented

**If This Fails:**
→ Start with simple approach, migrate to complex as needed

---

### Step 2: Create Configuration File Structure

**What:** Set up the file structure for managing configurations.

**How:**

```bash
# Create configuration directory structure
mkdir -p config
touch config/__init__.py
touch config/settings.py
touch config/development.py
touch config/staging.py
touch config/production.py
```

**File: config/settings.py** (Base configuration)
```python
"""
Base configuration settings
"""
import os
from pathlib import Path
from typing import Any

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

class BaseConfig:
    """Base configuration shared across all environments"""
    
    # Application
    APP_NAME: str = "MyApplication"
    VERSION: str = "1.0.0"
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    LOG_DIR: Path = BASE_DIR / "logs"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    DB_ECHO: bool = False  # SQL query logging
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Feature Flags
    ENABLE_SWAGGER: bool = True
    ENABLE_METRICS: bool = True
    
    # External Services
    REDIS_URL: str | None = os.getenv("REDIS_URL")
    ELASTICSEARCH_URL: str | None = os.getenv("ELASTICSEARCH_URL")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_db_url(cls) -> str:
        """Get database URL with fallback"""
        return cls.DATABASE_URL
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return os.getenv("ENV", "development") == "production"
```

**File: config/development.py**
```python
"""
Development environment configuration
"""
from .settings import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Development-specific settings"""
    
    DEBUG: bool = True
    TESTING: bool = False
    
    # Development database
    DATABASE_URL: str = "sqlite:///./dev.db"
    DB_ECHO: bool = True  # Log all SQL queries
    
    # Relaxed security for development
    SECRET_KEY: str = "dev-secret-key-not-for-production"
    
    # Development CORS - allow all
    CORS_ORIGINS: list[str] = ["*"]
    
    # Verbose logging
    LOG_LEVEL: str = "DEBUG"
    
    # Enable all dev tools
    ENABLE_SWAGGER: bool = True
    ENABLE_DEBUG_TOOLBAR: bool = True
    ENABLE_PROFILER: bool = True
```

**File: config/production.py**
```python
"""
Production environment configuration
"""
import os
from .settings import BaseConfig

class ProductionConfig(BaseConfig):
    """Production-specific settings"""
    
    DEBUG: bool = False
    TESTING: bool = False
    
    # Production database (must be set via environment)
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_RECYCLE: int = 3600
    
    # Strict security
    SECRET_KEY: str = os.getenv("SECRET_KEY")  # Must be set
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "").split(",")
    
    # Production logging
    LOG_LEVEL: str = "WARNING"
    
    # Disable development tools
    ENABLE_SWAGGER: bool = False
    ENABLE_DEBUG_TOOLBAR: bool = False
    ENABLE_PROFILER: bool = False
    
    # Production services
    REDIS_URL: str = os.getenv("REDIS_URL")
    SENTRY_DSN: str | None = os.getenv("SENTRY_DSN")
    
    @classmethod
    def validate(cls) -> None:
        """Validate production configuration"""
        assert cls.DATABASE_URL, "DATABASE_URL must be set in production"
        assert cls.SECRET_KEY, "SECRET_KEY must be set in production"
        assert cls.SECRET_KEY != "dev-secret-key-not-for-production", \
            "Must use secure SECRET_KEY in production"
        assert cls.DEBUG is False, "DEBUG must be False in production"
```

**File: config/__init__.py**
```python
"""
Configuration management
"""
import os
from typing import Type

from .settings import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig

# Staging config (optional)
class StagingConfig(BaseConfig):
    """Staging environment configuration"""
    DEBUG: bool = False
    TESTING: bool = True
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://staging")
    LOG_LEVEL: str = "INFO"

# Configuration registry
config_by_name = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env: str | None = None) -> Type[BaseConfig]:
    """
    Get configuration based on environment
    
    Args:
        env: Environment name. If None, reads from ENV environment variable
        
    Returns:
        Configuration class for the specified environment
        
    Example:
        >>> config = get_config('production')
        >>> print(config.DATABASE_URL)
    """
    if env is None:
        env = os.getenv('ENV', 'development')
    
    config_class = config_by_name.get(env, config_by_name['default'])
    
    # Validate production config
    if env == 'production' and hasattr(config_class, 'validate'):
        config_class.validate()
    
    return config_class

# Export active configuration
settings = get_config()
```

**Verification:**
- [ ] Configuration file structure created
- [ ] Base settings defined
- [ ] Environment-specific configs created
- [ ] Configuration loader implemented

**If This Fails:**
→ Ensure directory structure is correct
→ Check Python import paths

---

### Step 3: Create Environment Templates

**What:** Create `.env` templates for different environments.

**How:**

**File: .env.example** (Template for developers)
```bash
# Environment Configuration
# Copy this file to .env and fill in your values

# Environment Selection
ENV=development  # Options: development, staging, production

# Application
APP_NAME=MyApplication
VERSION=1.0.0
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp_dev
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# External APIs (optional)
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Monitoring (production)
SENTRY_DSN=https://xxx@sentry.io/xxx

# Logging
LOG_LEVEL=INFO
```

**File: .env.development** (Local development)
```bash
ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=dev-secret-key
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
```

**File: .env.production** (Production template - never commit actual production values)
```bash
ENV=production
DEBUG=false

# Set these via environment/secrets management
DATABASE_URL=postgresql://user:pass@prod-db:5432/myapp
SECRET_KEY=MUST_BE_SET_VIA_SECRETS
REDIS_URL=redis://prod-redis:6379/0
SENTRY_DSN=MUST_BE_SET_VIA_SECRETS

LOG_LEVEL=WARNING
CORS_ORIGINS=https://myapp.com,https://www.myapp.com
```

**Update .gitignore:**
```bash
# Add to .gitignore
.env
.env.local
.env.*.local
*.env

# Keep templates
!.env.example
!.env.*.example
```

**Verification:**
- [ ] .env.example created with all settings documented
- [ ] Environment-specific templates created
- [ ] .gitignore updated to exclude actual .env files
- [ ] Templates do not contain real secrets

**If This Fails:**
→ Ensure file permissions are correct
→ Verify .gitignore is working: `git status` should not show .env files

---

### Step 4: Implement Configuration Loading

**What:** Create utility to load and use configuration in your application.

**How:**

**File: app/config_loader.py**
```python
"""
Configuration loader with environment variable support
"""
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Load environment variables from .env file
def load_env_file(env: str | None = None) -> None:
    """
    Load environment variables from .env file
    
    Args:
        env: Specific environment to load (e.g., 'development', 'staging')
    """
    base_dir = Path(__file__).resolve().parent.parent
    
    # Load environment-specific .env file
    if env:
        env_file = base_dir / f".env.{env}"
        if env_file.exists():
            load_dotenv(env_file)
            print(f"Loaded {env_file}")
    
    # Load default .env file
    default_env = base_dir / ".env"
    if default_env.exists():
        load_dotenv(default_env)
        print(f"Loaded {default_env}")

# Initialize configuration
def init_config() -> Any:
    """
    Initialize configuration with environment variables
    
    Returns:
        Active configuration object
    """
    # Load .env files
    env = os.getenv('ENV', 'development')
    load_env_file(env)
    
    # Import and return config
    from config import settings
    
    print(f"Configuration loaded: {env}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Debug: {settings.DEBUG}")
    
    return settings
```

**Usage in your application:**

**File: app/main.py** (FastAPI example)
```python
"""
Main application entry point
"""
from fastapi import FastAPI
from app.config_loader import init_config

# Load configuration
config = init_config()

# Create FastAPI app with configuration
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    debug=config.DEBUG,
    docs_url="/docs" if config.ENABLE_SWAGGER else None,
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": config.ENV if hasattr(config, 'ENV') else "unknown",
        "version": config.VERSION,
    }

@app.get("/config-info")
async def config_info():
    """Get non-sensitive configuration information"""
    return {
        "app_name": config.APP_NAME,
        "version": config.VERSION,
        "debug": config.DEBUG,
        "environment": getattr(config, 'ENV', 'development'),
        "features": {
            "swagger": config.ENABLE_SWAGGER,
            "metrics": getattr(config, 'ENABLE_METRICS', False),
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
    )
```

**Verification:**
- [ ] Configuration loads from environment variables
- [ ] .env files are read correctly
- [ ] Environment-specific settings work
- [ ] Application starts with correct configuration

**If This Fails:**
→ Check .env file location and format
→ Verify python-dotenv is installed: `pip install python-dotenv`
→ Ensure ENV variable is set correctly

---

### Step 5: Add Configuration Validation

**What:** Implement validation to catch configuration errors early.

**How:**

```python
# config/validation.py
"""
Configuration validation
"""
import os
import sys
from typing import Any, Callable

class ConfigValidator:
    """Validate configuration settings"""
    
    @staticmethod
    def validate_required(value: Any, name: str) -> Any:
        """Ensure required value is set"""
        if value is None or value == "":
            raise ValueError(f"Required configuration '{name}' is not set")
        return value
    
    @staticmethod
    def validate_url(value: str, name: str) -> str:
        """Validate URL format"""
        if not value:
            raise ValueError(f"URL '{name}' cannot be empty")
        if not (value.startswith('http://') or 
                value.startswith('https://') or
                value.startswith('postgresql://') or
                value.startswith('redis://') or
                value.startswith('sqlite://')):
            raise ValueError(f"Invalid URL format for '{name}': {value}")
        return value
    
    @staticmethod
    def validate_in_choices(value: Any, choices: list, name: str) -> Any:
        """Validate value is in allowed choices"""
        if value not in choices:
            raise ValueError(
                f"Invalid value for '{name}': {value}. "
                f"Must be one of: {', '.join(map(str, choices))}"
            )
        return value
    
    @staticmethod
    def validate_positive_int(value: int, name: str) -> int:
        """Validate positive integer"""
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"'{name}' must be a positive integer, got: {value}")
        return value
    
    @staticmethod
    def validate_production_secrets(config: Any) -> None:
        """Validate production has proper secrets"""
        if not hasattr(config, 'ENV') or config.ENV != 'production':
            return
        
        # Check SECRET_KEY
        if not hasattr(config, 'SECRET_KEY') or \
           config.SECRET_KEY in ['dev-secret-key', 'change-me-in-production', '']:
            raise ValueError(
                "Production environment must have a secure SECRET_KEY set"
            )
        
        # Check DATABASE_URL
        if not hasattr(config, 'DATABASE_URL') or not config.DATABASE_URL:
            raise ValueError(
                "Production environment must have DATABASE_URL set"
            )
        
        # Check DEBUG is False
        if hasattr(config, 'DEBUG') and config.DEBUG:
            raise ValueError(
                "Production environment must have DEBUG=False"
            )
        
        print("✅ Production configuration validation passed")

def validate_config(config: Any) -> None:
    """
    Run all configuration validations
    
    Args:
        config: Configuration object to validate
        
    Raises:
        ValueError: If validation fails
    """
    validator = ConfigValidator()
    
    try:
        # Validate critical settings
        if hasattr(config, 'DATABASE_URL'):
            validator.validate_url(config.DATABASE_URL, 'DATABASE_URL')
        
        if hasattr(config, 'ENV'):
            validator.validate_in_choices(
                config.ENV,
                ['development', 'staging', 'production'],
                'ENV'
            )
        
        if hasattr(config, 'LOG_LEVEL'):
            validator.validate_in_choices(
                config.LOG_LEVEL.upper(),
                ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                'LOG_LEVEL'
            )
        
        # Validate production-specific requirements
        validator.validate_production_secrets(config)
        
        print("✅ Configuration validation successful")
        
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}", file=sys.stderr)
        sys.exit(1)
```

**Add validation to config/__init__.py:**
```python
from .validation import validate_config

# ... existing code ...

def get_config(env: str | None = None) -> Type[BaseConfig]:
    """Get and validate configuration"""
    if env is None:
        env = os.getenv('ENV', 'development')
    
    config_class = config_by_name.get(env, config_by_name['default'])
    
    # Validate configuration
    validate_config(config_class)
    
    return config_class
```

**Verification:**
- [ ] Configuration validation runs on startup
- [ ] Production environment requires secure secrets
- [ ] Invalid configurations are caught early
- [ ] Helpful error messages displayed

**If This Fails:**
→ Check validation logic for your specific requirements
→ Add custom validators as needed

---

### Step 6: Implement Hot Reload (Optional)

**What:** Enable configuration reload without restarting the application.

**How:**

```python
# config/hot_reload.py
"""
Hot reload configuration for development
"""
import time
import threading
from pathlib import Path
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    """Handle configuration file changes"""
    
    def __init__(self, reload_callback: Callable):
        self.reload_callback = reload_callback
        self.last_reload = 0
        self.debounce_seconds = 1
    
    def on_modified(self, event):
        """Called when .env file is modified"""
        if event.src_path.endswith('.env'):
            current_time = time.time()
            if current_time - self.last_reload > self.debounce_seconds:
                print(f"Configuration file changed: {event.src_path}")
                self.reload_callback()
                self.last_reload = current_time

def watch_config_files(reload_callback: Callable, watch_path: Path | None = None):
    """
    Watch configuration files for changes
    
    Args:
        reload_callback: Function to call when config changes
        watch_path: Directory to watch (default: current directory)
    """
    if watch_path is None:
        watch_path = Path.cwd()
    
    event_handler = ConfigFileHandler(reload_callback)
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False)
    observer.start()
    
    print(f"👀 Watching for configuration changes in: {watch_path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Usage example
if __name__ == "__main__":
    def reload_config():
        """Reload configuration"""
        print("♻️  Reloading configuration...")
        from config import get_config
        config = get_config()
        print(f"✅ Configuration reloaded: ENV={getattr(config, 'ENV', 'unknown')}")
    
    watch_config_files(reload_config)
```

**Install dependency:**
```bash
pip install watchdog
```

**Verification:**
- [ ] Configuration file watcher installed
- [ ] Changes to .env trigger reload
- [ ] Application picks up new configuration

**If This Fails:**
→ Hot reload is optional for production
→ Restart application instead for production deployments

---

### Step 7: Document Configuration

**What:** Create comprehensive configuration documentation.

**How:**

**File: docs/CONFIGURATION.md**
```markdown
# Configuration Guide

## Overview

This application uses environment-based configuration management with support for:
- Multiple environments (development, staging, production)
- Environment variables and .env files
- Type-safe configuration classes
- Validation and error checking

## Quick Start

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```bash
   nano .env
   ```

3. Run the application:
   ```bash
   python -m app.main
   ```

## Configuration Settings

### Core Settings

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| `ENV` | No | `development` | Environment: development, staging, production |
| `DEBUG` | No | `false` | Enable debug mode |
| `APP_NAME` | No | `MyApplication` | Application name |
| `VERSION` | No | `1.0.0` | Application version |

### Database Settings

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| `DATABASE_URL` | Yes* | `sqlite:///./app.db` | Database connection URL |
| `DB_POOL_SIZE` | No | `10` | Connection pool size |
| `DB_MAX_OVERFLOW` | No | `20` | Max connections beyond pool size |

*Required in production

### Security Settings

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| `SECRET_KEY` | Yes* | N/A | Secret key for encryption/signing |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins (comma-separated) |

*Required in production

### Logging Settings

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| `LOG_LEVEL` | No | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |

## Environment-Specific Configuration

### Development
- Uses SQLite by default
- DEBUG enabled
- Verbose logging
- All development tools enabled

### Production
- Requires PostgreSQL
- DEBUG disabled
- Production logging level
- Strict validation

## Security Notes

1. **Never commit .env files** - they may contain secrets
2. **Use strong SECRET_KEY** - generate with: `openssl rand -hex 32`
3. **Restrict CORS origins** - don't use `*` in production
4. **Validate production config** - application will check on startup

## Troubleshooting

### "Required configuration 'X' is not set"
→ Set the required environment variable in your .env file

### "Invalid URL format"
→ Check your DATABASE_URL or other URL formats

### Configuration not loading
→ Ensure .env file is in the project root
→ Check file permissions
→ Install python-dotenv: `pip install python-dotenv`
```

**Verification:**
- [ ] Configuration documentation created
- [ ] All settings documented with descriptions
- [ ] Environment-specific notes included
- [ ] Security guidance provided

**If This Fails:**
→ Update documentation as configuration evolves

---

## Verification Checklist

After completing this workflow:

- [ ] Configuration file structure created
- [ ] Base and environment-specific configs defined
- [ ] .env templates created and .gitignore updated
- [ ] Configuration loading implemented
- [ ] Validation added for critical settings
- [ ] Application starts with correct configuration
- [ ] Environment switching works (dev/staging/prod)
- [ ] Secrets are not committed to version control
- [ ] Documentation created for all settings
- [ ] Team members can set up configuration using .env.example

---

## Common Issues & Solutions

### Issue 1: Configuration Not Loading

**Symptoms:**
- Environment variables not being read
- Default values always used
- AttributeError when accessing config

**Cause:**
- .env file not in correct location
- python-dotenv not installed
- File permissions issues

**Solution:**
```bash
# Install python-dotenv
pip install python-dotenv

# Check .env file location
ls -la .env

# Verify file is readable
cat .env

# Test configuration loading
python -c "from config import settings; print(settings.DATABASE_URL)"
```

**Prevention:**
- Include python-dotenv in requirements.txt
- Document .env file location in README
- Add configuration validation on startup

---

### Issue 2: Production Secrets in Version Control

**Symptoms:**
- .env file visible in `git status`
- Secrets committed to repository
- Security vulnerability

**Cause:**
- .gitignore not properly configured
- .env file added before .gitignore

**Solution:**
```bash
# Remove from git history (CAREFUL - rewrites history)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Or use git-filter-repo (recommended)
git filter-repo --path .env --invert-paths

# Update .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore

# Commit .gitignore
git add .gitignore
git commit -m "Add .env to .gitignore"

# Rotate all secrets that were exposed
```

**Prevention:**
- Add .gitignore early in project
- Use pre-commit hooks to check for secrets
- Regularly audit version control for sensitive files

---

### Issue 3: Different Behavior Across Environments

**Symptoms:**
- Works in development, fails in production
- Unexpected configuration values
- Feature flags not working

**Cause:**
- ENV variable not set correctly
- Environment-specific config not loading
- Hardcoded values override environment

**Solution:**
```python
# Add debug logging to config loading
def get_config(env: str | None = None) -> Type[BaseConfig]:
    if env is None:
        env = os.getenv('ENV', 'development')
    
    print(f"🔧 Loading config for environment: {env}")
    print(f"🔧 Available configs: {list(config_by_name.keys())}")
    
    config_class = config_by_name.get(env, config_by_name['default'])
    print(f"🔧 Selected config class: {config_class.__name__}")
    
    return config_class

# Test environment detection
python -c "import os; print(f\"ENV={os.getenv('ENV', 'NOT SET')}\")"
```

**Prevention:**
- Always set ENV explicitly in deployment
- Validate environment on startup
- Log configuration source on startup

---

### Issue 4: Type Conversion Errors

**Symptoms:**
- TypeError when accessing config values
- Boolean settings not working
- Integer settings as strings

**Cause:**
- Environment variables are always strings
- Missing type conversion

**Solution:**
```python
# Proper type conversion
class Config:
    # Boolean
    DEBUG: bool = os.getenv('DEBUG', 'False') == 'True'
    # or
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
    
    # Integer
    PORT: int = int(os.getenv('PORT', '8000'))
    
    # List
    ALLOWED_HOSTS: list[str] = os.getenv('ALLOWED_HOSTS', '').split(',')
    
    # Float
    TIMEOUT: float = float(os.getenv('TIMEOUT', '30.0'))
    
    # Optional with None
    API_KEY: str | None = os.getenv('API_KEY') or None
```

**Prevention:**
- Always specify type conversions
- Use Pydantic for automatic validation
- Test with different environment variable formats

---

## Best Practices

### DO:
✅ **Use environment-specific configuration files**
   - Clear separation between dev/staging/prod

✅ **Validate configuration on startup**
   - Fail fast with clear error messages

✅ **Document all configuration options**
   - Include defaults, types, and descriptions

✅ **Use .env.example as template**
   - Helps new developers set up quickly

✅ **Keep secrets out of version control**
   - Use .gitignore and environment variables

✅ **Use type annotations**
   - Provides IDE support and validation

✅ **Provide sensible defaults**
   - Application should run with minimal configuration

✅ **Use configuration classes**
   - Better than raw dictionaries for complex configs

### DON'T:
❌ **Don't hardcode secrets in configuration files**
   - Always use environment variables

❌ **Don't commit .env files**
   - Commit .env.example only

❌ **Don't use global variables**
   - Pass configuration explicitly or use dependency injection

❌ **Don't access os.getenv() throughout codebase**
   - Centralize in configuration module

❌ **Don't ignore production validation**
   - Always validate critical settings

❌ **Don't use same secrets across environments**
   - Each environment needs unique secrets

❌ **Don't assume environment variables are set**
   - Provide defaults or fail with clear error

❌ **Don't mix configuration concerns**
   - Keep application config separate from infrastructure

---

## Examples

### Example 1: Basic Flask Application

```python
# config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

# app.py
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/health')
def health():
    return {'status': 'healthy'}
```

---

### Example 2: FastAPI with Pydantic Settings

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()

# main.py
from fastapi import FastAPI
from config import settings

app = FastAPI(title=settings.app_name)
```

---

### Example 3: Django-Style Configuration

```python
# settings/base.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    'django.contrib.admin',
    # ...
]

# settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost']
DATABASE = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}

# settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DB_NAME'),
    # ...
}
```

---

### Example 4: Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    environment:
      - ENV=development
      - DEBUG=true
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - .env
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD=password
```

---

## Related Workflows

**Before This Workflow:**
- [[dev-001]](../development/environment_initialization.md) - Set up development environment

**After This Workflow:**
- [[config-002]](./pydantic_settings_configuration.md) - Advanced Pydantic settings
- [[sec-001]](../security/secret_management_solo.md) - Manage secrets securely
- [[devops-001]](../devops/cicd_pipeline_setup.md) - Configure CI/CD with environment variables

**Alternative Workflows:**
- [[config-002]](./pydantic_settings_configuration.md) - Use Pydantic for type-safe configuration

**Complementary Workflows:**
- [[config-004]](./system_logs_configuration.md) - Configure logging
- [[devops-005]](../devops/docker_container_creation.md) - Docker environment management

---

## Notes

### For Code Buddy (AI Assistant)
- Always check for .env file before running application
- Verify environment-specific configuration is loaded correctly
- Validate production configuration has secure secrets
- Help user choose appropriate configuration complexity
- Remind about .gitignore for .env files

### For Humans
- Start simple, add complexity as needed
- Document all configuration options
- Use .env.example as template for new developers
- Consider using Pydantic for large projects (30+ settings)
- Rotate secrets if accidentally committed
- Different environments need different SECRET_KEY values

### Deviation Protocol
- Can skip validation for very simple projects
- Can use simple dictionary config for < 10 settings
- Can skip hot reload for production-only projects
- Consider cloud provider secret managers for production

---

## Tags
`configuration` `settings` `environment` `deployment` `security` `python` `best-practices` `devops`

## Additional Metadata
**Automation Potential:** Partial (can generate templates)
**Risk Level:** Medium (misconfiguration can cause outages)
**Team Size:** Solo to Large (scalable approach)
**Environment:** All (dev, staging, production)
**Last Reviewed:** 2025-10-27
**Next Review Due:** 2026-04-27
