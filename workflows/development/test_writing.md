---
id: dev-002
title: Test Writing Best Practices
category: Development
subcategory: Quality Assurance
tags:
  - testing
  - pytest
  - unit-tests
  - integration-tests
  - tdd
  - quality
prerequisites:
  - dev-003  # Environment Initialization
related_workflows:
  - qa-003   # Test Failure Investigation
  - qa-004   # Coverage Gap Analysis
  - test-002 # Mocking Strategy
  - dev-017  # CI/CD Pipeline
complexity: beginner
estimated_time: 30-45 minutes
last_updated: 2025-10-25
---

# Test Writing Best Practices

## Overview

**What:** Comprehensive guide to writing effective unit, integration, and end-to-end tests using pytest and modern testing practices.

**Why:** Well-written tests catch bugs early, enable confident refactoring, serve as documentation, and ensure code reliability. Good tests save time and money by preventing production issues.

**When to use:**
- Writing tests for new features (TDD approach)
- Adding tests to legacy code (retrofitting)
- Fixing bugs (write test first, then fix)
- Improving test coverage
- Setting up test infrastructure for new projects

---

## Prerequisites

**Required:**
- [ ] Python 3.10+ installed
- [ ] pytest installed (`pip install pytest`)
- [ ] Basic understanding of your codebase
- [ ] Code to test (or using TDD, intention of what to build)

**Optional but recommended:**
- [ ] pytest-cov (coverage reporting)
- [ ] pytest-mock (mocking utilities)
- [ ] pytest-xdist (parallel test execution)

**Check before starting:**
```bash
# Verify pytest is installed
pytest --version

# Check if you have a tests directory
ls tests/ 2>/dev/null || echo "Need to create tests directory"

# Verify you have a source directory
ls src/ 2>/dev/null || ls *.py

# Check current test coverage (if tests exist)
pytest --cov=src --cov-report=term-missing 2>/dev/null || echo "No tests yet"
```

---

## Implementation Steps

### Step 1: Set Up Test Infrastructure

**What:** Create the basic directory structure and configuration files for organized testing.

**How:** Establish a clear separation between test types and configure pytest for your project.

**Directory structure:**
```bash
my_project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── unit/                 # Fast, isolated tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/          # Tests with external dependencies
│   │   ├── __init__.py
│   │   ├── test_database.py
│   │   └── test_api.py
│   └── e2e/                  # End-to-end tests
│       ├── __init__.py
│       └── test_workflows.py
├── pytest.ini               # Pytest configuration
└── requirements-dev.txt     # Test dependencies
```

**Create structure:**
```bash
# Create test directories
mkdir -p tests/{unit,integration,e2e}
touch tests/__init__.py
touch tests/{unit,integration,e2e}/__init__.py

# Create pytest configuration
cat > pytest.ini << 'EOF'
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output options
addopts = 
    -ra
    --strict-markers
    --strict-config
    --showlocals
    --tb=short

# Markers for test organization
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may use database, external APIs)
    e2e: End-to-end tests (full system tests)
    slow: Tests that take > 1 second
    smoke: Critical smoke tests that must always pass

# Minimum coverage
[coverage:run]
source = src
omit = 
    */tests/*
    */test_*.py

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
EOF

# Create conftest.py for shared fixtures
cat > tests/conftest.py << 'EOF'
"""Shared pytest fixtures and configuration."""
import pytest
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "id": 1,
        "name": "Test Item",
        "value": 100
    }


# Add your shared fixtures here
EOF

# Add test dependencies
cat > requirements-dev.txt << 'EOF'
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-asyncio>=0.21.0
pytest-xdist>=3.3.0
pytest-timeout>=2.1.0
hypothesis>=6.82.0
EOF

pip install -r requirements-dev.txt
```

**Verification:**
- [ ] `tests/` directory structure created
- [ ] `pytest.ini` configuration file exists
- [ ] Can run `pytest` without errors (even if no tests yet)
- [ ] Test dependencies installed

**If This Fails:**
→ Ensure you're in the project root directory
→ Check file permissions (use `chmod +x` if needed)
→ Verify pytest installed: `python -m pytest --version`

---

### Step 2: Write Your First Unit Test

**What:** Create a simple unit test following the Arrange-Act-Assert pattern.

**How:** Start with testing a pure function - something with no dependencies, just input → output.

**Example function to test** (in `src/utils.py`):
```python
# src/utils.py
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price.
    
    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)
    
    Returns:
        Discounted price
    
    Raises:
        ValueError: If discount_percent not in valid range
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount
```

**Write the test** (in `tests/unit/test_utils.py`):
```python
# tests/unit/test_utils.py
import pytest
from src.utils import calculate_discount


class TestCalculateDiscount:
    """Tests for the calculate_discount function."""
    
    def test_no_discount(self):
        """Test with 0% discount returns original price."""
        # Arrange
        price = 100.0
        discount = 0.0
        
        # Act
        result = calculate_discount(price, discount)
        
        # Assert
        assert result == 100.0
    
    def test_fifty_percent_discount(self):
        """Test 50% discount halves the price."""
        result = calculate_discount(100.0, 50.0)
        assert result == 50.0
    
    def test_full_discount(self):
        """Test 100% discount gives zero price."""
        result = calculate_discount(100.0, 100.0)
        assert result == 0.0
    
    def test_decimal_discount(self):
        """Test discount with decimal percentage."""
        result = calculate_discount(100.0, 15.5)
        assert result == 84.5
    
    def test_invalid_discount_negative(self):
        """Test that negative discount raises ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            calculate_discount(100.0, -10.0)
    
    def test_invalid_discount_over_hundred(self):
        """Test that discount > 100 raises ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            calculate_discount(100.0, 150.0)
    
    @pytest.mark.parametrize("price,discount,expected", [
        (100.0, 10.0, 90.0),
        (50.0, 20.0, 40.0),
        (200.0, 25.0, 150.0),
        (75.0, 33.33, 50.0025),
    ])
    def test_various_discounts(self, price, discount, expected):
        """Test multiple discount scenarios."""
        result = calculate_discount(price, discount)
        assert result == pytest.approx(expected, rel=1e-2)
```

**Run the tests:**
```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_utils.py

# Run specific test
pytest tests/unit/test_utils.py::TestCalculateDiscount::test_fifty_percent_discount
```

**Verification:**
- [ ] All tests pass
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Test names clearly describe what they test
- [ ] Edge cases are covered (0%, 100%, invalid values)
- [ ] Parametrized tests reduce code duplication

**If This Fails:**
→ Check import paths match your project structure
→ Ensure `__init__.py` files exist in all directories
→ Run with `-v` flag for detailed error messages
→ Use `--tb=long` for full tracebacks

---

### Step 3: Use Fixtures for Test Setup

**What:** Create reusable test fixtures to avoid duplication and make tests cleaner.

**How:** Define fixtures in `conftest.py` for shared setup, or in test files for local fixtures.

**Example: Testing a User model**

Create the model (`src/models.py`):
```python
# src/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model."""
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
    
    def update_email(self, new_email: str) -> None:
        """Update user email with validation."""
        if "@" not in new_email:
            raise ValueError("Invalid email format")
        self.email = new_email
```

**Create fixtures** (in `tests/conftest.py`):
```python
# tests/conftest.py
import pytest
from datetime import datetime
from src.models import User


@pytest.fixture
def sample_user():
    """Provide a standard test user."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        created_at=datetime(2024, 1, 1, 12, 0, 0)
    )


@pytest.fixture
def inactive_user(sample_user):
    """Provide an inactive user (builds on sample_user)."""
    sample_user.deactivate()
    return sample_user


@pytest.fixture
def multiple_users():
    """Provide a list of test users."""
    return [
        User(1, "alice", "alice@example.com", datetime.now()),
        User(2, "bob", "bob@example.com", datetime.now()),
        User(3, "charlie", "charlie@example.com", datetime.now()),
    ]
```

**Write tests using fixtures** (`tests/unit/test_models.py`):
```python
# tests/unit/test_models.py
import pytest
from src.models import User


class TestUser:
    """Tests for User model."""
    
    def test_user_creation(self, sample_user):
        """Test user is created with correct attributes."""
        assert sample_user.id == 1
        assert sample_user.username == "testuser"
        assert sample_user.email == "test@example.com"
        assert sample_user.is_active is True
    
    def test_deactivate_user(self, sample_user):
        """Test user deactivation."""
        sample_user.deactivate()
        assert sample_user.is_active is False
    
    def test_inactive_user_fixture(self, inactive_user):
        """Test inactive user fixture is already deactivated."""
        assert inactive_user.is_active is False
    
    def test_update_email_valid(self, sample_user):
        """Test updating email with valid format."""
        sample_user.update_email("newemail@example.com")
        assert sample_user.email == "newemail@example.com"
    
    def test_update_email_invalid(self, sample_user):
        """Test updating email with invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid email"):
            sample_user.update_email("notanemail")
    
    def test_multiple_users(self, multiple_users):
        """Test working with multiple users."""
        assert len(multiple_users) == 3
        assert all(user.is_active for user in multiple_users)
```

**Run with fixture debugging:**
```bash
# Show fixture setup/teardown
pytest --setup-show tests/unit/test_models.py

# List available fixtures
pytest --fixtures
```

**Verification:**
- [ ] Fixtures defined in conftest.py are accessible to all tests
- [ ] Fixtures reduce code duplication
- [ ] Tests remain independent (each gets fresh fixture)
- [ ] Fixture dependencies work (inactive_user uses sample_user)

**If This Fails:**
→ Check fixture names match function parameters
→ Ensure conftest.py is in tests/ directory
→ Verify imports in conftest.py are correct
→ Use `--setup-show` to debug fixture execution order

---

### Step 4: Test Async Code

**What:** Write tests for asynchronous functions using pytest-asyncio.

**How:** Mark async tests with `@pytest.mark.asyncio` and use `await` in test functions.

**Example async service** (`src/services.py`):
```python
# src/services.py
import asyncio
import aiohttp
from typing import Dict, Any


class DataService:
    """Service for fetching data from APIs."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def fetch_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch user data from API.
        
        Args:
            user_id: User ID to fetch
            
        Returns:
            User data dictionary
        """
        url = f"{self.base_url}/users/{user_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    
    async def process_batch(self, items: list) -> list:
        """Process multiple items concurrently."""
        tasks = [self._process_item(item) for item in items]
        return await asyncio.gather(*tasks)
    
    async def _process_item(self, item: Any) -> Any:
        """Process single item (simulated delay)."""
        await asyncio.sleep(0.1)  # Simulate processing
        return item * 2
```

**Write async tests** (`tests/unit/test_services.py`):
```python
# tests/unit/test_services.py
import pytest
from unittest.mock import AsyncMock, patch
from src.services import DataService


@pytest.fixture
def data_service():
    """Provide a DataService instance."""
    return DataService(base_url="https://api.example.com")


class TestDataService:
    """Tests for DataService."""
    
    @pytest.mark.asyncio
    async def test_fetch_user_success(self, data_service):
        """Test successful user fetch."""
        # Mock the HTTP call
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "id": 1,
            "name": "Test User"
        }
        mock_response.raise_for_status = AsyncMock()
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await data_service.fetch_user(1)
            
            assert result["id"] == 1
            assert result["name"] == "Test User"
    
    @pytest.mark.asyncio
    async def test_process_batch(self, data_service):
        """Test batch processing."""
        items = [1, 2, 3, 4, 5]
        results = await data_service.process_batch(items)
        
        assert results == [2, 4, 6, 8, 10]
    
    @pytest.mark.asyncio
    async def test_process_batch_empty(self, data_service):
        """Test batch processing with empty list."""
        results = await data_service.process_batch([])
        assert results == []
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(5)  # Fail if test takes > 5 seconds
    async def test_concurrent_processing(self, data_service):
        """Test that batch processing runs concurrently."""
        import time
        
        items = [1] * 10  # 10 items
        start = time.time()
        await data_service.process_batch(items)
        duration = time.time() - start
        
        # If sequential: 10 * 0.1s = 1.0s
        # If concurrent: ~0.1s
        assert duration < 0.5, "Processing should be concurrent"
```

**Run async tests:**
```bash
# Run all async tests
pytest -m asyncio

# Run with asyncio debug mode
pytest --asyncio-mode=auto
```

**Verification:**
- [ ] Async tests run successfully
- [ ] Tests use `await` properly
- [ ] Async operations are mocked correctly
- [ ] Concurrent behavior is verified
- [ ] Tests have timeout protection

**If This Fails:**
→ Ensure pytest-asyncio is installed
→ Mark all async tests with `@pytest.mark.asyncio`
→ Don't mix sync and async in same test
→ Use `AsyncMock` for mocking async functions

---

### Step 5: Write Integration Tests

**What:** Test components working together with real dependencies (database, external APIs, etc.).

**How:** Use pytest fixtures to set up real resources, then clean up after tests.

**Example: Testing database operations**

Create database service (`src/database.py`):
```python
# src/database.py
import psycopg
from typing import List, Optional


class DatabaseService:
    """PostgreSQL database service."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def create_user(self, username: str, email: str) -> int:
        """Create a new user and return ID."""
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
                    (username, email)
                )
                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Fetch user by ID."""
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, username, email FROM users WHERE id = %s",
                    (user_id,)
                )
                row = cur.fetchone()
                if row:
                    return {"id": row[0], "username": row[1], "email": row[2]}
                return None
```

**Integration test fixtures** (`tests/integration/conftest.py`):
```python
# tests/integration/conftest.py
import pytest
import psycopg
import os
from src.database import DatabaseService


@pytest.fixture(scope="session")
def test_db_connection_string():
    """Provide test database connection string."""
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://localhost/test_db"
    )


@pytest.fixture(scope="function")
def db_service(test_db_connection_string):
    """Provide DatabaseService with fresh test database."""
    # Set up: Create tables
    with psycopg.connect(test_db_connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    email VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
    
    service = DatabaseService(test_db_connection_string)
    
    yield service
    
    # Tear down: Clean up test data
    with psycopg.connect(test_db_connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
            conn.commit()
```

**Integration tests** (`tests/integration/test_database.py`):
```python
# tests/integration/test_database.py
import pytest


@pytest.mark.integration
class TestDatabaseService:
    """Integration tests for DatabaseService."""
    
    def test_create_and_get_user(self, db_service):
        """Test creating and retrieving a user."""
        # Create user
        user_id = db_service.create_user("alice", "alice@example.com")
        assert user_id > 0
        
        # Retrieve user
        user = db_service.get_user(user_id)
        assert user is not None
        assert user["username"] == "alice"
        assert user["email"] == "alice@example.com"
    
    def test_get_nonexistent_user(self, db_service):
        """Test retrieving non-existent user returns None."""
        user = db_service.get_user(99999)
        assert user is None
    
    def test_multiple_users(self, db_service):
        """Test creating multiple users."""
        user1_id = db_service.create_user("alice", "alice@example.com")
        user2_id = db_service.create_user("bob", "bob@example.com")
        
        assert user1_id != user2_id
        
        user1 = db_service.get_user(user1_id)
        user2 = db_service.get_user(user2_id)
        
        assert user1["username"] == "alice"
        assert user2["username"] == "bob"
```

**Run integration tests:**
```bash
# Run only integration tests
pytest -m integration

# Run integration tests with database URL
TEST_DATABASE_URL=postgresql://localhost/test_db pytest -m integration

# Skip integration tests (for quick testing)
pytest -m "not integration"
```

**Verification:**
- [ ] Integration tests use real database
- [ ] Test database is cleaned between tests
- [ ] Tests can run independently
- [ ] Connection string can be configured via environment
- [ ] Teardown properly cleans test data

**If This Fails:**
→ Ensure test database exists and is accessible
→ Check database permissions
→ Verify connection string format
→ Use Docker for consistent test database
→ Check that teardown runs even on test failure

---

### Step 6: Use Mocking Effectively

**What:** Replace external dependencies with mocks to keep tests fast and isolated.

**How:** Use pytest-mock or unittest.mock to replace functions, methods, or entire objects.

**Example: Mocking external API calls**

Service that calls external API (`src/api_client.py`):
```python
# src/api_client.py
import requests
from typing import Dict, Any


class WeatherService:
    """Service for fetching weather data."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weather.com"
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Weather data dictionary
            
        Raises:
            requests.HTTPError: If API request fails
        """
        response = requests.get(
            f"{self.base_url}/current",
            params={"city": city, "api_key": self.api_key}
        )
        response.raise_for_status()
        return response.json()
    
    def is_raining(self, city: str) -> bool:
        """Check if it's currently raining in city."""
        weather = self.get_current_weather(city)
        return weather.get("conditions") == "rain"
```

**Tests with mocking** (`tests/unit/test_api_client.py`):
```python
# tests/unit/test_api_client.py
import pytest
from unittest.mock import Mock, patch
from requests.exceptions import HTTPError
from src.api_client import WeatherService


@pytest.fixture
def weather_service():
    """Provide WeatherService with fake API key."""
    return WeatherService(api_key="test_key_12345")


class TestWeatherService:
    """Tests for WeatherService."""
    
    @patch("requests.get")
    def test_get_current_weather_success(self, mock_get, weather_service):
        """Test successful weather fetch."""
        # Configure mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "city": "London",
            "temperature": 15,
            "conditions": "cloudy"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Call the method
        result = weather_service.get_current_weather("London")
        
        # Verify the result
        assert result["city"] == "London"
        assert result["temperature"] == 15
        
        # Verify the API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "api_key" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["city"] == "London"
    
    @patch("requests.get")
    def test_get_current_weather_http_error(self, mock_get, weather_service):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPError):
            weather_service.get_current_weather("InvalidCity")
    
    @patch.object(WeatherService, "get_current_weather")
    def test_is_raining_true(self, mock_get_weather, weather_service):
        """Test is_raining when it's raining."""
        mock_get_weather.return_value = {
            "city": "London",
            "conditions": "rain"
        }
        
        assert weather_service.is_raining("London") is True
        mock_get_weather.assert_called_once_with("London")
    
    @patch.object(WeatherService, "get_current_weather")
    def test_is_raining_false(self, mock_get_weather, weather_service):
        """Test is_raining when it's not raining."""
        mock_get_weather.return_value = {
            "city": "London",
            "conditions": "sunny"
        }
        
        assert weather_service.is_raining("London") is False


# Alternative: Using pytest-mock (mocker fixture)
class TestWeatherServiceWithMocker:
    """Tests using pytest-mock plugin."""
    
    def test_get_weather_with_mocker(self, mocker, weather_service):
        """Test using mocker fixture (pytest-mock)."""
        # Mock requests.get
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"temperature": 20}
        mock_get = mocker.patch("requests.get", return_value=mock_response)
        
        result = weather_service.get_current_weather("Paris")
        
        assert result["temperature"] == 20
        assert mock_get.called
```

**Verification:**
- [ ] External dependencies are mocked
- [ ] Tests run without network access
- [ ] Mock behavior is verified
- [ ] Tests remain fast (< 0.1s per test)
- [ ] Both unittest.mock and pytest-mock patterns work

**If This Fails:**
→ Check mock patch path matches import path in code
→ Verify mock return values match expected data structure
→ Use `mocker.spy()` to verify calls without replacing function
→ Remember: patch where it's used, not where it's defined

---

### Step 7: Measure and Improve Coverage

**What:** Track which parts of your code are tested and systematically add tests for uncovered areas.

**How:** Use pytest-cov to generate coverage reports and identify gaps.

**Commands:**
```bash
# Run tests with coverage
pytest --cov=src tests/

# Generate detailed coverage report
pytest --cov=src --cov-report=html tests/

# Show missing line numbers
pytest --cov=src --cov-report=term-missing tests/

# Fail if coverage is below threshold
pytest --cov=src --cov-fail-under=80 tests/

# Generate multiple report formats
pytest --cov=src --cov-report=html --cov-report=term --cov-report=xml tests/
```

**Example coverage output:**
```
---------- coverage: platform linux, python 3.11.4-final-0 -----------
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src/__init__.py          0      0   100%
src/main.py             45      3    93%   78-80
src/models.py           32      0   100%
src/services.py         28      8    71%   45-52, 67
src/utils.py            15      1    93%   23
--------------------------------------------------
TOTAL                  120     12    90%
```

**Analyzing coverage:**
```python
# Look at HTML report
# Open htmlcov/index.html in browser
# Click on files to see which lines aren't tested

# Focus on:
# 1. Main business logic (highest priority)
# 2. Error handling paths
# 3. Edge cases
# 4. Public API functions
```

**Add tests for uncovered code:**
```python
# If coverage shows src/services.py lines 45-52 untested:

# View the code
cat src/services.py | sed -n '45,52p'

# Write test for that code path
def test_previously_uncovered_path():
    """Test the error handling in process_data."""
    service = DataService()
    
    # This triggers lines 45-52
    with pytest.raises(ValueError):
        service.process_data(invalid_input=True)
```

**Coverage configuration** (`.coveragerc` or `pyproject.toml`):
```ini
# .coveragerc
[run]
source = src
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */site-packages/*

[report]
precision = 2
show_missing = True
skip_covered = False

# Fail build if coverage drops below 80%
fail_under = 80

[html]
directory = htmlcov
```

**Verification:**
- [ ] Coverage reports generate successfully
- [ ] Can identify untested code
- [ ] Coverage is >= 80% (adjust based on project needs)
- [ ] Coverage doesn't include test files themselves
- [ ] HTML report is readable and helpful

**If This Fails:**
→ Install pytest-cov: `pip install pytest-cov`
→ Check source paths match your project structure
→ Exclude test files from coverage calculation
→ Don't aim for 100% coverage (diminishing returns)

---

### Step 8: Organize and Maintain Tests

**What:** Implement patterns and practices for long-term test maintainability.

**How:** Use test markers, organize tests logically, and follow naming conventions.

**Test organization strategies:**

```python
# 1. Use descriptive test names
def test_user_cannot_delete_other_users_posts():  # Clear!
    pass

def test_delete():  # Too vague!
    pass


# 2. Group related tests in classes
class TestUserAuthentication:
    """All authentication-related tests."""
    
    def test_login_success(self):
        pass
    
    def test_login_wrong_password(self):
        pass
    
    def test_login_nonexistent_user(self):
        pass


# 3. Use markers to categorize tests
@pytest.mark.smoke
def test_app_starts():
    """Critical test that app can start."""
    pass

@pytest.mark.slow
def test_large_dataset_processing():
    """Test that takes > 5 seconds."""
    pass

@pytest.mark.skip(reason="Waiting for API v2")
def test_new_api_feature():
    pass

@pytest.mark.xfail(reason="Known bug #123")
def test_buggy_feature():
    pass


# 4. Parametrize to reduce duplication
@pytest.mark.parametrize("username,password,expected", [
    ("alice", "pass123", "success"),
    ("bob", "wrong", "failure"),
    ("", "pass123", "failure"),
    ("alice", "", "failure"),
])
def test_login_various_inputs(username, password, expected):
    result = login(username, password)
    assert result.status == expected
```

**Running specific test subsets:**
```bash
# Run only smoke tests (critical tests)
pytest -m smoke

# Run all except slow tests
pytest -m "not slow"

# Run smoke and integration tests
pytest -m "smoke or integration"

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run tests that failed last time
pytest --lf  # --last-failed

# Run failed tests first, then others
pytest --ff  # --failed-first

# Stop after first failure (fail fast)
pytest -x

# Stop after N failures
pytest --maxfail=3
```

**Maintaining test quality:**

```python
# Good test practices:

# 1. One assertion per test (when possible)
def test_user_creation():
    user = create_user("alice")
    assert user.username == "alice"

def test_user_starts_active():
    user = create_user("alice")
    assert user.is_active is True


# 2. Clear Arrange-Act-Assert structure
def test_discount_calculation():
    # Arrange
    price = 100
    discount_percent = 20
    
    # Act
    final_price = calculate_discount(price, discount_percent)
    
    # Assert
    assert final_price == 80


# 3. Use helper functions for complex setup
def create_test_user_with_posts(num_posts=5):
    """Helper to create user with posts."""
    user = User(username="test")
    for i in range(num_posts):
        user.posts.append(Post(title=f"Post {i}"))
    return user

def test_user_post_count():
    user = create_test_user_with_posts(num_posts=3)
    assert len(user.posts) == 3


# 4. Test one thing at a time
def test_user_activation():  # Good: focused
    user = create_inactive_user()
    user.activate()
    assert user.is_active

def test_user_lifecycle():  # Bad: tests too much
    user = create_user()
    user.deactivate()
    assert not user.is_active
    user.activate()
    assert user.is_active
    user.delete()
    assert user.deleted
    # This should be 4 separate tests!
```

**Verification:**
- [ ] Tests are well-organized by feature/module
- [ ] Test names are descriptive
- [ ] Markers are used for categorization
- [ ] Can run test subsets easily
- [ ] Tests are independent and can run in any order

**If This Fails:**
→ Review pytest documentation on markers
→ Refactor large test files into smaller, focused files
→ Add docstrings to test classes explaining their purpose
→ Use `pytest --collect-only` to see test organization

---

## Verification Checklist

After completing this workflow:

- [ ] Test infrastructure is set up (directories, pytest.ini, conftest.py)
- [ ] Can run pytest successfully
- [ ] Have unit tests covering core business logic
- [ ] Have integration tests for external dependencies
- [ ] Async code is tested properly
- [ ] Mocks are used to isolate unit tests
- [ ] Coverage is measured and >= 80%
- [ ] Tests are well-organized with clear naming
- [ ] CI/CD runs tests automatically
- [ ] Team follows testing standards

---

## Best Practices

### DO:
✅ Write tests first (TDD) when possible
✅ Keep tests fast - unit tests should be < 0.1s each
✅ Use fixtures to reduce duplication
✅ Test edge cases and error conditions
✅ Use descriptive test names that explain what they test
✅ Follow Arrange-Act-Assert pattern
✅ Keep tests independent - each can run in isolation
✅ Mock external dependencies in unit tests
✅ Use integration tests sparingly (they're slow)
✅ Measure coverage but don't obsess over 100%
✅ Run tests before committing code
✅ Keep test code clean and maintainable

### DON'T:
❌ Skip testing "because it's obvious"
❌ Test implementation details (test behavior instead)
❌ Have tests depend on each other (test order shouldn't matter)
❌ Use sleep() to wait for async operations (use proper async testing)
❌ Test third-party library code (trust it works)
❌ Commit code with failing tests
❌ Ignore flaky tests (fix or remove them)
❌ Make tests too complex (tests should be simple)
❌ Test everything in integration tests (too slow)
❌ Leave TODOs in test code (either implement or remove)

---

## Common Patterns

### Pattern 1: Factory Functions for Test Data
```python
# conftest.py
def create_user(**overrides):
    """Factory for creating test users with custom attributes."""
    defaults = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True
    }
    defaults.update(overrides)
    return User(**defaults)

# In tests:
def test_admin_user():
    admin = create_user(username="admin", is_admin=True)
    assert admin.is_admin
```

### Pattern 2: Context Managers for Setup/Teardown
```python
from contextlib import contextmanager

@contextmanager
def temporary_database():
    """Provide a temporary database that's cleaned up."""
    db = create_test_database()
    try:
        yield db
    finally:
        db.drop_all_tables()
        db.close()

# In tests:
def test_database_operations():
    with temporary_database() as db:
        # Database exists here
        db.insert_user("alice")
        assert db.count_users() == 1
    # Database is cleaned up here
```

### Pattern 3: Parametrize for Multiple Test Cases
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("HELLO", "HELLO"),
    ("HeLLo", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase_conversion(input, expected):
    assert uppercase(input) == expected
```

### Pattern 4: Hypothesis for Property-Based Testing
```python
from hypothesis import given
import hypothesis.strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Addition is commutative: a + b == b + a"""
    assert a + b == b + a

@given(st.lists(st.integers()))
def test_sort_idempotent(items):
    """Sorting twice gives same result as sorting once."""
    once = sorted(items)
    twice = sorted(sorted(items))
    assert once == twice
```

---

## Troubleshooting

### Issue: Tests run slow

**Symptoms:**
- Full test suite takes > 2 minutes
- Unit tests take > 0.1s each
- Developers avoid running tests

**Solutions:**
```bash
# 1. Identify slow tests
pytest --durations=10

# 2. Run tests in parallel
pip install pytest-xdist
pytest -n auto  # Use all CPU cores

# 3. Mark slow tests
@pytest.mark.slow
def test_large_dataset():
    pass

# Run fast tests by default
pytest -m "not slow"

# 4. Use mocks instead of real resources
# Before (slow):
def test_api_call():
    response = requests.get("https://api.example.com")
    
# After (fast):
@patch("requests.get")
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
```

**Prevention:**
- Keep unit tests < 0.1s by mocking everything
- Move slow tests to integration category
- Run slow tests only in CI, not locally

---

### Issue: Flaky tests (pass sometimes, fail sometimes)

**Symptoms:**
- Tests fail randomly
- Re-running tests gives different results
- CI fails while local tests pass

**Solutions:**
```python
# Common causes:

# 1. Race conditions in async code
# BAD:
async def test_concurrent_updates():
    await update_user(1)
    user = await get_user(1)
    assert user.updated  # Might not be updated yet!

# GOOD:
async def test_concurrent_updates():
    await update_user(1)
    await asyncio.sleep(0.1)  # Or use proper synchronization
    user = await get_user(1)
    assert user.updated


# 2. Test order dependencies
# BAD:
def test_create_user():
    create_user("alice")

def test_count_users():
    assert count_users() == 1  # Depends on test above!

# GOOD:
@pytest.fixture(autouse=True)
def clean_database():
    clear_all_users()


# 3. Time-based assertions
# BAD:
def test_timestamp():
    user = create_user()
    assert user.created_at == datetime.now()  # Timing issue!

# GOOD:
def test_timestamp():
    before = datetime.now()
    user = create_user()
    after = datetime.now()
    assert before <= user.created_at <= after
```

**Prevention:**
- Ensure tests are independent
- Use fixed timestamps in tests (mock datetime.now)
- Don't rely on external services
- Use proper async synchronization

---

### Issue: Import errors in tests

**Symptoms:**
- `ModuleNotFoundError` when running tests
- Tests can't import application code
- Imports work in application but not in tests

**Solutions:**
```bash
# 1. Check __init__.py files exist
find . -type d -name tests -o -name src | xargs -I {} ls {}/__init__.py

# 2. Verify PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest

# 3. Install package in editable mode
pip install -e .

# 4. Check imports match directory structure
# Directory: src/myapp/utils.py
# Import: from src.myapp.utils import ...

# 5. Use absolute imports in tests
# DON'T: from ..utils import function
# DO: from src.myapp.utils import function
```

**Prevention:**
- Always use absolute imports in tests
- Install your package with `pip install -e .`
- Keep `__init__.py` in all directories

---

### Issue: Fixtures not being used

**Symptoms:**
- Fixture defined but test doesn't see it
- "fixture 'X' not found" error
- Fixture in conftest.py isn't accessible

**Solutions:**
```python
# 1. Check fixture name matches parameter name
@pytest.fixture
def database():  # Fixture name
    return Database()

def test_query(database):  # Parameter name must match!
    pass


# 2. Verify conftest.py location
tests/
  conftest.py          # Available to all tests
  unit/
    conftest.py        # Available only to unit/ tests
    test_models.py


# 3. Check fixture scope isn't too narrow
@pytest.fixture(scope="function")  # New instance per test
@pytest.fixture(scope="class")     # Shared within test class
@pytest.fixture(scope="module")    # Shared within test file
@pytest.fixture(scope="session")   # Shared across all tests


# 4. List available fixtures
pytest --fixtures
```

**Prevention:**
- Put shared fixtures in tests/conftest.py
- Use `pytest --fixtures` to verify fixtures are visible
- Document fixture purpose with docstrings

---

## Related Workflows

**Prerequisites:**
- [[environment_initialization]] - Need environment before testing
- [[type_annotation_addition]] - Type hints help catch errors

**Next Steps:**
- [[ci_cd_workflow]] - Automate test execution
- [[code_review_checklist]] - Review tests along with code
- [[test_failure_investigation]] - Debug failing tests
- [[coverage_gap_analysis]] - Improve test coverage

**Related:**
- [[mocking_strategy]] - Deep dive into mocking
- [[property_based_testing]] - Advanced testing with Hypothesis
- [[test_data_generation]] - Generate realistic test data

---

## Tags
`development` `testing` `pytest` `unit-tests` `integration-tests` `tdd` `quality` `best-practices` `fixtures` `mocking`
