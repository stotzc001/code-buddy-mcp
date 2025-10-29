# Pydantic Settings Configuration

**ID:** config-002  
**Category:** Configuration Management  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 30-45 minutes  
**Frequency:** Once per project  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Type-safe configuration management using Pydantic's BaseSettings for automatic validation, type checking, and environment variable parsing.

**Why:**
- Automatic type conversion and validation
- IDE autocomplete and type checking support
- Built-in environment variable parsing
- Clear error messages for misconfiguration
- Supports complex nested configurations
- JSON Schema generation for documentation

**When to use:**
- Projects with 20+ configuration settings
- Need strong type safety and validation
- Complex configuration with nested structures
- Want automatic environment variable parsing
- Need configuration documentation generation
- Building production-grade applications

---

## Prerequisites

**Required Knowledge:**
- [ ] Python type hints and annotations
- [ ] Pydantic models basics
- [ ] Environment variables
- [ ] Configuration management concepts

**Required Tools:**
- [ ] Python 3.8+ installed
- [ ] pip or poetry for package management
- [ ] Pydantic v2 (pydantic-settings)

**Check before starting:**
```bash
python --version  # Should show 3.8+
pip show pydantic  # Check if installed
```

---

## Dependencies

**Auto-Load These Workflows:**
- [[config-001]](./application_settings.md) - Basic configuration concepts

**Called By These Workflows:**
- [[dev-002]](../development/environment_initialization.md) - Environment setup
- [[devops-001]](../devops/cicd_pipeline_setup.md) - CI/CD configuration

**Related Workflows:**
- [[config-001]](./application_settings.md) - Simpler configuration approach
- [[sec-001]](../security/secret_management_solo.md) - Secret management

---

## Implementation Steps

### Step 1: Install Pydantic Settings

**What:** Install pydantic and pydantic-settings packages.

**Why:** Pydantic v2 moved settings to separate package for better modularity.

**How:**

```bash
# Install pydantic and pydantic-settings
pip install pydantic pydantic-settings

# Or add to requirements.txt
echo "pydantic>=2.0.0" >> requirements.txt
echo "pydantic-settings>=2.0.0" >> requirements.txt
pip install -r requirements.txt

# Or with poetry
poetry add pydantic pydantic-settings

# Optional: Install dotenv support
pip install python-dotenv
```

**Verification:**
```bash
python -c "from pydantic_settings import BaseSettings; print('✅ Pydantic settings installed')"
```

**If This Fails:**
→ Ensure pip is up to date: `pip install --upgrade pip`
→ Check Python version: `python --version`

---

### Step 2: Create Base Settings Model

**What:** Create a Pydantic settings model with automatic environment variable loading.

**How:**

**File: config/settings.py**
```python
"""
Pydantic-based configuration management
"""
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings using Pydantic
    
    Automatically loads from environment variables and .env file
    """
    
    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,  # Allow case-insensitive env vars
        extra='ignore',  # Ignore extra env vars
    )
    
    # Application Settings
    app_name: str = Field(
        default="MyApplication",
        description="Application name"
    )
    
    version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        alias="ENV",  # Can use ENV in environment variables
        description="Deployment environment"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # Database Settings
    database_url: str = Field(
        ...,  # Required field
        description="Database connection URL",
        examples=["postgresql://user:pass@localhost:5432/mydb"]
    )
    
    db_pool_size: int = Field(
        default=10,
        ge=1,  # Greater than or equal to 1
        le=100,  # Less than or equal to 100
        description="Database connection pool size"
    )
    
    db_max_overflow: int = Field(
        default=20,
        ge=0,
        description="Maximum overflow connections"
    )
    
    db_echo: bool = Field(
        default=False,
        description="Echo SQL queries to logs"
    )
    
    # Redis Settings
    redis_url: str | None = Field(
        default=None,
        description="Redis connection URL"
    )
    
    redis_ttl: int = Field(
        default=3600,
        ge=0,
        description="Default Redis TTL in seconds"
    )
    
    # Security Settings
    secret_key: str = Field(
        ...,  # Required
        min_length=32,
        description="Secret key for signing/encryption"
    )
    
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="Access token expiration time"
    )
    
    # API Settings
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API version 1 prefix"
    )
    
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Feature Flags
    enable_swagger: bool = Field(
        default=True,
        description="Enable Swagger/OpenAPI docs"
    )
    
    enable_metrics: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    # External Services
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key"
    )
    
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key"
    )
    
    # Paths
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent,
        description="Base directory path"
    )
    
    # Computed properties
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    # Validators
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format"""
        if not v:
            raise ValueError("Database URL cannot be empty")
        
        allowed_schemes = ['postgresql://', 'mysql://', 'sqlite:///', 'mongodb://']
        if not any(v.startswith(scheme) for scheme in allowed_schemes):
            raise ValueError(
                f"Database URL must start with one of: {', '.join(allowed_schemes)}"
            )
        
        return v
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v) -> list[str]:
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Support comma-separated string
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @model_validator(mode='after')
    def validate_production_settings(self) -> 'Settings':
        """Validate production-specific requirements"""
        if self.environment == 'production':
            # Ensure debug is off
            if self.debug:
                raise ValueError("DEBUG must be False in production")
            
            # Ensure secure secret key
            if self.secret_key in ['dev', 'development', 'change-me']:
                raise ValueError("Production requires secure SECRET_KEY")
            
            # Ensure Swagger is disabled
            if self.enable_swagger:
                raise ValueError("Swagger should be disabled in production")
        
        return self


# Create global settings instance
settings = Settings()

# Export for easy import
__all__ = ['settings', 'Settings']
```

**Verification:**
- [ ] Settings class created with type hints
- [ ] Required fields marked with `...`
- [ ] Validators defined for critical fields
- [ ] Settings instance created

**If This Fails:**
→ Check Pydantic version: `pip show pydantic`
→ Ensure pydantic-settings is installed

---

### Step 3: Create Environment-Specific Settings

**What:** Create environment-specific configuration classes inheriting from base settings.

**How:**

**File: config/environments.py**
```python
"""
Environment-specific settings
"""
from typing import Literal
from pydantic import Field
from .settings import Settings

class DevelopmentSettings(Settings):
    """Development environment settings"""
    
    environment: Literal["development"] = "development"
    debug: bool = True
    
    # Development database
    database_url: str = Field(
        default="sqlite:///./dev.db",
        description="Development database"
    )
    
    db_echo: bool = True  # Log all SQL queries
    
    # Relaxed CORS for development
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allow all origins in dev"
    )
    
    # Enable all dev tools
    enable_swagger: bool = True
    enable_debug_toolbar: bool = True
    
    # Verbose logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    
    # Development secret (not for production!)
    secret_key: str = Field(
        default="dev-secret-key-not-for-production" * 2,  # Make it long enough
        min_length=32
    )

class StagingSettings(Settings):
    """Staging environment settings"""
    
    environment: Literal["staging"] = "staging"
    debug: bool = False
    
    # Staging uses production-like database
    database_url: str  # Required, no default
    
    # Staging has same restrictions as production
    enable_swagger: bool = True  # Can keep docs in staging
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

class ProductionSettings(Settings):
    """Production environment settings"""
    
    environment: Literal["production"] = "production"
    debug: bool = False
    
    # Production requires these to be set via environment
    database_url: str  # Required
    secret_key: str  # Required
    
    # Stricter production settings
    db_pool_size: int = 20
    db_max_overflow: int = 40
    db_echo: bool = False
    
    # Restricted CORS
    cors_origins: list[str]  # Required, must be explicit
    
    # Disable dev tools
    enable_swagger: bool = False
    
    # Production logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    
    # Monitoring
    sentry_dsn: str | None = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )

# Configuration factory
def get_settings(env: str | None = None) -> Settings:
    """
    Get settings for specified environment
    
    Args:
        env: Environment name (development, staging, production)
        
    Returns:
        Settings instance for the environment
        
    Example:
        >>> settings = get_settings('production')
        >>> print(settings.database_url)
    """
    import os
    
    if env is None:
        env = os.getenv('ENV', 'development')
    
    env_map = {
        'development': DevelopmentSettings,
        'staging': StagingSettings,
        'production': ProductionSettings,
    }
    
    settings_class = env_map.get(env, DevelopmentSettings)
    
    try:
        return settings_class()
    except Exception as e:
        print(f"❌ Failed to load {env} settings: {e}")
        raise
```

**Verification:**
- [ ] Environment-specific classes created
- [ ] Each environment has appropriate defaults
- [ ] Production has stricter requirements
- [ ] Settings factory function works

**If This Fails:**
→ Check environment variable ENV is set
→ Verify .env file exists and is readable

---

### Step 4: Add Advanced Validation

**What:** Implement custom validators for complex business logic.

**How:**

**File: config/validators.py**
```python
"""
Custom validators for settings
"""
from pydantic import field_validator, model_validator
from typing import Any
import re

class AdvancedValidatorsMixin:
    """Mixin with advanced validation methods"""
    
    @field_validator('database_url')
    @classmethod
    def validate_production_database(cls, v: str, info) -> str:
        """Ensure production doesn't use SQLite"""
        environment = info.data.get('environment', 'development')
        
        if environment == 'production' and v.startswith('sqlite:'):
            raise ValueError(
                "Production environment cannot use SQLite database. "
                "Use PostgreSQL, MySQL, or other production database."
            )
        
        return v
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key_strength(cls, v: str, info) -> str:
        """Ensure secret key is strong enough"""
        environment = info.data.get('environment', 'development')
        
        if environment == 'production':
            # Check length
            if len(v) < 32:
                raise ValueError("Production SECRET_KEY must be at least 32 characters")
            
            # Check complexity (has uppercase, lowercase, numbers, special chars)
            if not (re.search(r'[A-Z]', v) and 
                    re.search(r'[a-z]', v) and 
                    re.search(r'[0-9]', v)):
                raise ValueError(
                    "Production SECRET_KEY should contain uppercase, "
                    "lowercase, and numbers"
                )
        
        return v
    
    @field_validator('cors_origins')
    @classmethod
    def validate_cors_origins(cls, v: list[str], info) -> list[str]:
        """Validate CORS origins for production"""
        environment = info.data.get('environment', 'development')
        
        if environment == 'production' and '*' in v:
            raise ValueError(
                "Production cannot use wildcard (*) in CORS origins. "
                "Specify explicit origins."
            )
        
        # Validate URL format
        for origin in v:
            if origin != '*' and not origin.startswith(('http://', 'https://')):
                raise ValueError(
                    f"Invalid CORS origin format: {origin}. "
                    "Must start with http:// or https://"
                )
        
        return v
    
    @model_validator(mode='after')
    def validate_redis_cache_settings(self) -> 'AdvancedValidatorsMixin':
        """Validate Redis is configured if caching is enabled"""
        if hasattr(self, 'enable_caching') and self.enable_caching:
            if not self.redis_url:
                raise ValueError(
                    "Caching is enabled but REDIS_URL is not configured"
                )
        
        return self
    
    @model_validator(mode='after')
    def validate_monitoring_in_production(self) -> 'AdvancedValidatorsMixin':
        """Ensure monitoring is configured in production"""
        if self.environment == 'production':
            if hasattr(self, 'sentry_dsn') and not self.sentry_dsn:
                import warnings
                warnings.warn(
                    "Production environment should have Sentry configured "
                    "for error tracking"
                )
        
        return self


# Enhanced settings with advanced validation
class ValidatedSettings(Settings, AdvancedValidatorsMixin):
    """Settings with advanced validation"""
    pass
```

**Usage:**
```python
# config/__init__.py
from .validators import ValidatedSettings

# Use validated settings instead of base
settings = ValidatedSettings()
```

**Verification:**
- [ ] Custom validators implemented
- [ ] Production-specific validations work
- [ ] Security validations enforced
- [ ] Warnings shown for recommended settings

**If This Fails:**
→ Review validation logic for your requirements
→ Test with different environment configurations

---

### Step 5: Implement Nested Settings

**What:** Support complex nested configuration structures.

**How:**

**File: config/nested_settings.py**
```python
"""
Nested configuration structures
"""
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseModel):
    """Database configuration"""
    
    url: str = Field(..., description="Database URL")
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0)
    echo: bool = Field(default=False)
    pool_recycle: int = Field(default=3600, ge=-1)
    
    model_config = SettingsConfigDict(
        env_prefix='DB_'  # DB_URL, DB_POOL_SIZE, etc.
    )

class RedisConfig(BaseModel):
    """Redis configuration"""
    
    url: str | None = Field(default=None)
    ttl: int = Field(default=3600, ge=0)
    max_connections: int = Field(default=50, ge=1)
    
    model_config = SettingsConfigDict(
        env_prefix='REDIS_'
    )

class SecurityConfig(BaseModel):
    """Security configuration"""
    
    secret_key: str = Field(..., min_length=32)
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    
    model_config = SettingsConfigDict(
        env_prefix='SECURITY_'
    )

class APIConfig(BaseModel):
    """API configuration"""
    
    prefix: str = Field(default="/api/v1")
    rate_limit_per_minute: int = Field(default=60, ge=1)
    max_request_size: int = Field(default=10_000_000, ge=0)  # 10MB
    
    model_config = SettingsConfigDict(
        env_prefix='API_'
    )

class NestedSettings(BaseSettings):
    """
    Settings with nested configuration
    
    Example .env:
        DB_URL=postgresql://localhost/mydb
        DB_POOL_SIZE=20
        REDIS_URL=redis://localhost:6379
        SECURITY_SECRET_KEY=xxx
    """
    
    app_name: str = "MyApp"
    environment: str = "development"
    debug: bool = False
    
    # Nested configurations
    database: DatabaseConfig
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig
    api: APIConfig = Field(default_factory=APIConfig)
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter='__'  # Support DB__URL format
    )

# Usage
settings = NestedSettings()

# Access nested config
print(settings.database.url)
print(settings.redis.ttl)
print(settings.security.secret_key)
```

**Environment variables:**
```bash
# Flat format with prefix
DB_URL=postgresql://localhost/mydb
DB_POOL_SIZE=20

# Or nested format with delimiter
DATABASE__URL=postgresql://localhost/mydb
DATABASE__POOL_SIZE=20
```

**Verification:**
- [ ] Nested models created
- [ ] Environment prefixes work
- [ ] Nested settings accessible
- [ ] Both flat and nested env vars work

**If This Fails:**
→ Check env_prefix is correct
→ Verify env_nested_delimiter setting

---

### Step 6: Add Configuration Export and Documentation

**What:** Generate configuration documentation and export schemas.

**How:**

**File: config/export.py**
```python
"""
Configuration export and documentation
"""
import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel

def export_json_schema(settings_class: type[BaseModel], output_path: str | Path) -> None:
    """
    Export JSON schema for settings
    
    Args:
        settings_class: Settings class to export
        output_path: Path to save JSON schema
        
    Example:
        >>> export_json_schema(Settings, 'config_schema.json')
    """
    schema = settings_class.model_json_schema()
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ JSON schema exported to: {output_path}")

def generate_env_example(settings_class: type[BaseModel], output_path: str | Path) -> None:
    """
    Generate .env.example from settings class
    
    Args:
        settings_class: Settings class to document
        output_path: Path to save .env.example
    """
    schema = settings_class.model_json_schema()
    properties = schema.get('properties', {})
    required = set(schema.get('required', []))
    
    lines = [
        "# Environment Configuration",
        "# Generated from Pydantic settings",
        "",
    ]
    
    for field_name, field_info in properties.items():
        # Convert to uppercase env var format
        env_var = field_name.upper()
        
        # Add description as comment
        description = field_info.get('description', '')
        if description:
            lines.append(f"# {description}")
        
        # Add type information
        field_type = field_info.get('type', 'string')
        lines.append(f"# Type: {field_type}")
        
        # Mark if required
        if field_name in required:
            lines.append(f"# REQUIRED")
        
        # Add default value or placeholder
        default = field_info.get('default')
        if default is not None:
            lines.append(f"{env_var}={default}")
        else:
            lines.append(f"{env_var}=  # TODO: Set this value")
        
        lines.append("")  # Empty line between fields
    
    output_path = Path(output_path)
    output_path.write_text('\n'.join(lines))
    
    print(f"✅ .env.example generated: {output_path}")

def print_current_config(settings: BaseModel) -> None:
    """
    Print current configuration (hiding secrets)
    
    Args:
        settings: Settings instance to print
    """
    print("\n📋 Current Configuration:")
    print("=" * 50)
    
    config_dict = settings.model_dump()
    
    secret_fields = {'secret_key', 'api_key', 'password', 'token'}
    
    for key, value in config_dict.items():
        # Hide secrets
        if any(secret in key.lower() for secret in secret_fields):
            display_value = "***hidden***"
        else:
            display_value = value
        
        print(f"{key}: {display_value}")
    
    print("=" * 50 + "\n")

# CLI tool for config management
if __name__ == "__main__":
    import sys
    from config import settings, Settings
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m config.export schema <output.json>")
        print("  python -m config.export env-example <output.env>")
        print("  python -m config.export show")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "schema":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "config_schema.json"
        export_json_schema(Settings, output_file)
    
    elif command == "env-example":
        output_file = sys.argv[2] if len(sys.argv) > 2 else ".env.example"
        generate_env_example(Settings, output_file)
    
    elif command == "show":
        print_current_config(settings)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
```

**Usage:**
```bash
# Generate JSON schema
python -m config.export schema config_schema.json

# Generate .env.example
python -m config.export env-example .env.example

# Show current configuration
python -m config.export show
```

**Verification:**
- [ ] JSON schema generation works
- [ ] .env.example generation works
- [ ] Current config display works (with secrets hidden)
- [ ] Documentation is accurate

**If This Fails:**
→ Ensure settings class is importable
→ Check file write permissions

---

### Step 7: Implement Dynamic Reloading (Development)

**What:** Add ability to reload configuration without restarting application.

**How:**

**File: config/reload.py**
```python
"""
Configuration hot reload for development
"""
import importlib
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

class ConfigReloadHandler(FileSystemEventHandler):
    """Handle configuration file changes"""
    
    def __init__(self, reload_callback: Callable):
        self.reload_callback = reload_callback
        self.last_reload = 0
    
    def on_modified(self, event):
        """Called when .env file changes"""
        if event.src_path.endswith('.env'):
            print(f"♻️  Configuration file changed: {event.src_path}")
            self.reload_callback()

def watch_config(reload_callback: Callable, watch_dir: Path | None = None):
    """
    Watch for configuration changes
    
    Args:
        reload_callback: Function to call on config change
        watch_dir: Directory to watch (default: current dir)
    """
    if watch_dir is None:
        watch_dir = Path.cwd()
    
    handler = ConfigReloadHandler(reload_callback)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    
    print(f"👀 Watching for config changes in: {watch_dir}")
    
    try:
        while True:
            observer.join(timeout=1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Example reload callback
def reload_config():
    """Reload configuration module"""
    import config
    importlib.reload(config)
    print("✅ Configuration reloaded")
```

**Verification:**
- [ ] File watcher installed
- [ ] Configuration reloads on .env changes
- [ ] Application picks up new values

**If This Fails:**
→ Install watchdog: `pip install watchdog`
→ Hot reload is optional for production

---

## Verification Checklist

After completing this workflow:

- [ ] Pydantic and pydantic-settings installed
- [ ] Base settings model with type hints created
- [ ] Environment-specific settings configured
- [ ] Validators working correctly
- [ ] Nested configurations supported (if needed)
- [ ] Configuration loads from environment variables
- [ ] Configuration loads from .env file
- [ ] Production settings validated on startup
- [ ] JSON schema can be exported
- [ ] .env.example can be generated
- [ ] No secrets in version control
- [ ] IDE autocomplete works for settings
- [ ] Type errors caught by mypy/pylance

---

## Common Issues & Solutions

### Issue 1: ValidationError on Startup

**Symptoms:**
- `pydantic.ValidationError` when starting application
- Missing required fields error
- Type conversion errors

**Cause:**
- Required fields not set in environment
- Wrong type in environment variable
- Missing .env file

**Solution:**
```bash
# Check what's missing
python -c "from config import settings" 2>&1 | grep "Field required"

# Set missing environment variables
export DATABASE_URL="postgresql://localhost/mydb"
export SECRET_KEY="your-secret-key-here"

# Or create .env file
cat > .env << EOF
DATABASE_URL=postgresql://localhost/mydb
SECRET_KEY=$(openssl rand -hex 32)
EOF

# Test again
python -c "from config import settings; print('✅ Config loaded')"
```

**Prevention:**
- Provide .env.example template
- Document all required fields
- Use validation error messages to guide users

---

### Issue 2: Type Conversion Not Working

**Symptoms:**
- Boolean values always True
- Numbers treated as strings
- List fields not parsing correctly

**Cause:**
- Pydantic needs correct type hints
- Environment variables are always strings

**Solution:**
```python
# Correct type hints
class Settings(BaseSettings):
    # Boolean - Pydantic converts "true", "1", "yes", "on" to True
    debug: bool = False
    
    # Integer
    port: int = 8000
    
    # List - use Field with split
    from pydantic import Field
    
    allowed_hosts: list[str] = Field(
        default_factory=list,
        json_schema_extra={'env_parse': lambda x: x.split(',')}
    )
    
    # Or use validator
    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def parse_list(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',')]
        return v
```

**Prevention:**
- Always use proper type hints
- Test with string environment variables
- Use validators for complex types

---

### Issue 3: Nested Settings Not Loading

**Symptoms:**
- Nested configuration fields not populated
- Environment variables ignored
- ValidationError for nested models

**Cause:**
- Missing env_prefix configuration
- Wrong environment variable naming
- Nested delimiter not set

**Solution:**
```python
# Correct nested configuration
class DatabaseConfig(BaseModel):
    url: str
    pool_size: int = 10
    
    model_config = SettingsConfigDict(
        env_prefix='DB_'  # ← Important!
    )

class Settings(BaseSettings):
    database: DatabaseConfig
    
    model_config = SettingsConfigDict(
        env_nested_delimiter='__'  # Support DB__URL or DATABASE__URL
    )

# Environment variables
# Option 1: With prefix
DB_URL=postgresql://localhost/mydb
DB_POOL_SIZE=20

# Option 2: With nested delimiter
DATABASE__URL=postgresql://localhost/mydb
DATABASE__POOL_SIZE=20
```

**Prevention:**
- Document environment variable naming
- Provide examples for nested configs
- Test with both formats

---

## Best Practices

### DO:
✅ **Use type hints everywhere**
   - Enables IDE autocomplete and validation

✅ **Mark required fields with `...`**
   - Clear which settings must be provided

✅ **Use Field() for documentation**
   - Helps generate docs and schemas

✅ **Implement validators for business logic**
   - Catch misconfiguration early

✅ **Use Literal types for enums**
   - Restricts to valid values

✅ **Provide sensible defaults**
   - Development should "just work"

✅ **Validate production settings strictly**
   - Use model_validator for complex checks

✅ **Generate .env.example automatically**
   - Keeps documentation in sync

### DON'T:
❌ **Don't use Optional without default**
   - Use `| None = None` or `= Field(default=None)`

❌ **Don't skip type hints**
   - Defeats the purpose of Pydantic

❌ **Don't hardcode secrets**
   - Always use environment variables

❌ **Don't ignore validation errors**
   - They indicate misconfiguration

❌ **Don't use mutable defaults**
   - Use `Field(default_factory=list)` instead

❌ **Don't access os.getenv() directly**
   - Let Pydantic handle environment variables

❌ **Don't skip production validation**
   - Use model_validator to check production config

---

## Examples

### Example 1: FastAPI with Pydantic Settings

```python
# config/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    database_url: str = Field(..., alias="DATABASE_URL")
    secret_key: str = Field(..., min_length=32)
    
    model_config = {'env_file': '.env'}

settings = Settings()

# main.py
from fastapi import FastAPI
from config.settings import settings

app = FastAPI(title=settings.app_name)

@app.get("/")
async def root():
    return {"app": settings.app_name}
```

---

### Example 2: Complex Nested Configuration

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "mydb"
    user: str
    password: str
    
    model_config = SettingsConfigDict(env_prefix='DB_')
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class Settings(BaseSettings):
    database: DatabaseSettings
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter='__'
    )

# .env file
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=admin
DB_PASSWORD=secret

# Or using nested format
DATABASE__HOST=localhost
DATABASE__PORT=5432
```

---

### Example 3: Multiple Environment Files

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    app_name: str = "MyApp"
    database_url: str
    
    model_config = SettingsConfigDict(
        # Load from multiple files
        env_file=('.env', f'.env.{os.getenv("ENV", "development")}'),
        env_file_encoding='utf-8',
    )

# Files:
# .env - common settings
# .env.development - dev-specific
# .env.production - prod-specific
```

---

## Related Workflows

**Before This Workflow:**
- [[config-001]](./application_settings.md) - Basic configuration concepts

**After This Workflow:**
- [[dev-002]](../development/environment_initialization.md) - Use settings in project
- [[devops-001]](../devops/cicd_pipeline_setup.md) - CI/CD configuration
- [[sec-001]](../security/secret_management_solo.md) - Manage secrets

**Alternative Workflows:**
- [[config-001]](./application_settings.md) - Simpler approach for small projects

**Complementary Workflows:**
- [[config-004]](./system_logs_configuration.md) - Configure logging
- [[dev-004]](../development/type_annotation_addition.md) - Add type hints

---

## Tags
`pydantic` `configuration` `settings` `type-safety` `validation` `environment` `python` `best-practices`

## Additional Metadata
**Automation Potential:** High (can generate schemas and docs)
**Risk Level:** Low (validation catches errors)
**Team Size:** Solo to Large (scalable approach)
**Environment:** All (dev, staging, production)
**Last Reviewed:** 2025-10-27
**Next Review Due:** 2026-04-27
