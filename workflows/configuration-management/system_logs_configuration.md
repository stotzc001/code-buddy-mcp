# System Logs Configuration

**ID:** config-004  
**Category:** Configuration Management  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 30 minutes  
**Frequency:** Once per project + updates  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Configure structured logging with Python's logging module, including formatters, handlers, log levels, and log aggregation for production systems.

**Why:**
- Essential for debugging and troubleshooting
- Enables monitoring and alerting
- Provides audit trails
- Supports compliance requirements
- Facilitates root cause analysis

**When to use:**
- Setting up a new project's logging
- Improving existing logging infrastructure
- Implementing structured logging
- Adding log aggregation (ELK, CloudWatch, etc.)
- Troubleshooting production issues

---

## Prerequisites

**Required Knowledge:**
- [ ] Python logging module basics
- [ ] Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [ ] Understanding of log handlers and formatters

**Required Tools:**
- [ ] Python 3.8+ installed
- [ ] Application configuration system

**Check before starting:**
```bash
python -c "import logging; print('✅ Logging module available')"
```

---

## Implementation Steps

### Step 1: Create Basic Logging Configuration

**What:** Set up structured logging configuration.

**How:**

**File: config/logging_config.py**
```python
"""
Logging configuration
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Any

def get_log_config(
    log_level: str = "INFO",
    log_dir: Path | None = None,
    enable_file_logging: bool = True,
    json_format: bool = False,
) -> dict[str, Any]:
    """
    Get logging configuration dictionary
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_file_logging: Whether to log to files
        json_format: Use JSON format for structured logging
        
    Returns:
        Logging configuration dictionary
    """
    if log_dir is None:
        log_dir = Path("logs")
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Formatter configurations
    formatters = {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    
    if json_format:
        formatters["json"] = {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        }
    
    # Handler configurations
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    }
    
    if enable_file_logging:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_dir / "app.log"),
            "maxBytes": 10_485_760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        }
        
        handlers["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(log_dir / "errors.log"),
            "maxBytes": 10_485_760,
            "backupCount": 5,
            "encoding": "utf8",
        }
    
    # Root logger configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "root": {
            "level": log_level,
            "handlers": list(handlers.keys()),
        },
        "loggers": {
            # Set specific log levels for third-party libraries
            "urllib3": {"level": "WARNING"},
            "requests": {"level": "WARNING"},
            "sqlalchemy.engine": {"level": "WARNING"},
            "boto3": {"level": "WARNING"},
            "botocore": {"level": "WARNING"},
        },
    }
    
    return config

def setup_logging(
    log_level: str = "INFO",
    log_dir: Path | None = None,
    enable_file_logging: bool = True,
    json_format: bool = False,
) -> None:
    """
    Configure application logging
    
    Args:
        log_level: Logging level
        log_dir: Directory for log files
        enable_file_logging: Whether to log to files
        json_format: Use JSON format
        
    Example:
        >>> setup_logging(log_level="DEBUG", log_dir=Path("logs"))
    """
    config = get_log_config(
        log_level=log_level,
        log_dir=log_dir,
        enable_file_logging=enable_file_logging,
        json_format=json_format,
    )
    
    logging.config.dictConfig(config)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={log_level}, dir={log_dir}")

# Usage
if __name__ == "__main__":
    setup_logging(log_level="DEBUG")
    
    logger = logging.getLogger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
```

**Verification:**
```bash
python config/logging_config.py
# Should see logs in console and logs/ directory
```

---

### Step 2: Create Structured JSON Logging

**What:** Implement JSON structured logging for better log parsing.

**How:**

```bash
# Install JSON logger
pip install python-json-logger
```

**File: config/json_logging.py**
```python
"""
JSON structured logging
"""
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter with additional fields
    """
    
    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Add application name
        log_record['app'] = 'MyApplication'
        
        # Add environment
        import os
        log_record['environment'] = os.getenv('ENV', 'development')

def get_json_handler(log_file: str = "logs/app.json") -> logging.Handler:
    """
    Create JSON log handler
    
    Args:
        log_file: Path to JSON log file
        
    Returns:
        Configured JSON log handler
    """
    from pathlib import Path
    
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    handler = logging.FileHandler(log_file)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    return handler

# Example usage
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Add JSON handler
    json_handler = get_json_handler()
    logger.addHandler(json_handler)
    
    # Log some messages
    logger.info("Application started", extra={'user_id': 123})
    logger.error("Database connection failed", extra={'db': 'postgres', 'host': 'localhost'})
    
    # Read and parse JSON log
    with open('logs/app.json', 'r') as f:
        for line in f:
            log_entry = json.loads(line)
            print(json.dumps(log_entry, indent=2))
```

**Verification:**
- [ ] JSON logs created in logs/app.json
- [ ] Logs are valid JSON
- [ ] Additional fields present

---

### Step 3: Integrate with Application Configuration

**What:** Connect logging configuration to application settings.

**How:**

**Update config/settings.py:**
```python
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # ... other settings ...
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    log_dir: Path = Field(
        default=Path("logs"),
        description="Log directory"
    )
    
    enable_file_logging: bool = Field(
        default=True,
        description="Enable logging to files"
    )
    
    enable_json_logging: bool = Field(
        default=False,
        description="Use JSON format for logs"
    )
    
    # Optional: Sentry for error tracking
    sentry_dsn: str | None = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )

settings = Settings()
```

**File: app/logging.py**
```python
"""
Application logging setup
"""
import logging
from config.settings import settings
from config.logging_config import setup_logging

def init_logging() -> None:
    """Initialize application logging"""
    setup_logging(
        log_level=settings.log_level,
        log_dir=settings.log_dir,
        enable_file_logging=settings.enable_file_logging,
        json_format=settings.enable_json_logging,
    )
    
    # Optional: Setup Sentry
    if settings.sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
        )
        logging.info("Sentry error tracking initialized")
    
    logging.info("Application logging initialized")

# Call during application startup
# init_logging()
```

**Verification:**
- [ ] Logging configuration reads from settings
- [ ] Log level can be changed via environment variable
- [ ] File logging can be toggled

---

### Step 4: Add Request Logging Middleware

**What:** Log HTTP requests and responses (for web applications).

**How:**

**File: app/middleware/logging_middleware.py** (FastAPI example)
```python
"""
Request logging middleware
"""
import logging
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Log request
        logger.info(
            "Request started",
            extra={
                'request_id': request_id,
                'method': request.method,
                'url': str(request.url),
                'client_host': request.client.host if request.client else None,
                'user_agent': request.headers.get('user-agent'),
            }
        )
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'url': str(request.url),
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                }
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                "Request failed",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'url': str(request.url),
                    'duration_ms': round(duration * 1000, 2),
                    'error': str(e),
                },
                exc_info=True,
            )
            
            raise

# Add to FastAPI app
# app.add_middleware(LoggingMiddleware)
```

**Verification:**
- [ ] All requests are logged
- [ ] Response time tracked
- [ ] Request IDs generated
- [ ] Errors logged with context

---

### Step 5: Create Logger Helper

**What:** Create utility for consistent logging across application.

**How:**

**File: app/utils/logger.py**
```python
"""
Logging utilities
"""
import logging
import functools
import time
from typing import Any, Callable

def get_logger(name: str) -> logging.Logger:
    """
    Get logger with application name prefix
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello world")
    """
    return logging.getLogger(f"app.{name}")

def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time
    
    Example:
        @log_execution_time
        def slow_function():
            time.sleep(1)
    """
    logger = get_logger(func.__module__)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        logger.debug(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                f"{func.__name__} completed",
                extra={'duration_ms': round(duration * 1000, 2)}
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"{func.__name__} failed",
                extra={
                    'duration_ms': round(duration * 1000, 2),
                    'error': str(e),
                },
                exc_info=True
            )
            
            raise
    
    return wrapper

def log_function_call(func: Callable) -> Callable:
    """
    Decorator to log function calls with arguments
    
    Example:
        @log_function_call
        def add(a, b):
            return a + b
    """
    logger = get_logger(func.__module__)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(
            f"Calling {func.__name__}",
            extra={'args': args, 'kwargs': kwargs}
        )
        
        return func(*args, **kwargs)
    
    return wrapper

# Usage examples
if __name__ == "__main__":
    from app.logging import init_logging
    init_logging()
    
    logger = get_logger(__name__)
    logger.info("This is a test message")
    
    @log_execution_time
    def slow_function():
        time.sleep(0.1)
        return "done"
    
    result = slow_function()
```

**Verification:**
- [ ] Logger helper works
- [ ] Execution time decorator works
- [ ] Function call decorator works

---

### Step 6: Add Log Rotation and Cleanup

**What:** Implement log rotation and automatic cleanup of old logs.

**How:**

**File: scripts/cleanup_logs.py**
```python
"""
Log cleanup script
"""
import logging
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_logs(
    log_dir: Path,
    days_to_keep: int = 30,
    dry_run: bool = False
) -> None:
    """
    Remove log files older than specified days
    
    Args:
        log_dir: Directory containing log files
        days_to_keep: Keep logs from last N days
        dry_run: If True, only print what would be deleted
    """
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    log_files = log_dir.glob("*.log*")
    
    for log_file in log_files:
        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        
        if file_time < cutoff_date:
            if dry_run:
                print(f"Would delete: {log_file}")
            else:
                print(f"Deleting: {log_file}")
                log_file.unlink()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup old log files")
    parser.add_argument("--log-dir", type=Path, default=Path("logs"))
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    
    args = parser.parse_args()
    
    cleanup_old_logs(args.log_dir, args.days, args.dry_run)
```

**Add to crontab (Linux/Mac):**
```bash
# Cleanup logs older than 30 days every day at 2am
0 2 * * * /path/to/python /path/to/scripts/cleanup_logs.py
```

**Verification:**
- [ ] Log rotation configured
- [ ] Old logs cleaned up automatically
- [ ] Cleanup script works

---

## Verification Checklist

- [ ] Logging configuration created
- [ ] Log levels configurable via environment
- [ ] Console logging works
- [ ] File logging works (if enabled)
- [ ] Log rotation configured
- [ ] JSON logging implemented (if needed)
- [ ] Request logging added (for web apps)
- [ ] Logger utility created
- [ ] Sentry integrated (if using)
- [ ] Old logs cleanup configured
- [ ] Logs directory created
- [ ] No sensitive data in logs

---

## Common Issues & Solutions

### Issue: Logs Not Appearing

**Solution:**
```python
import logging

# Check log level
logger = logging.getLogger()
print(f"Root logger level: {logging.getLevelName(logger.level)}")

# Ensure handler is attached
print(f"Handlers: {logger.handlers}")

# Test logging
logging.debug("Debug message")
logging.info("Info message")
```

---

### Issue: Duplicate Log Messages

**Solution:**
```python
# Avoid creating multiple handlers
logger = logging.getLogger(__name__)

# Remove existing handlers before adding new ones
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Or set propagate to False
logger.propagate = False
```

---

## Best Practices

### DO:
✅ Use structured logging (JSON) for production
✅ Include request IDs for tracing
✅ Log at appropriate levels
✅ Rotate logs automatically
✅ Aggregate logs centrally (ELK, CloudWatch, etc.)
✅ Monitor error logs

### DON'T:
❌ Log sensitive data (passwords, tokens, PII)
❌ Over-log in production (use INFO/WARNING)
❌ Ignore log file size limits
❌ Use print() instead of logging
❌ Log entire request/response bodies by default

---

## Tags
`logging` `monitoring` `observability` `debugging` `configuration` `python`
