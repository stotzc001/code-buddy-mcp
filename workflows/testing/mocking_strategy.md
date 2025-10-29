# Test Mocking Strategy

**ID:** tes-003  
**Category:** Testing  
**Priority:** MEDIUM  
**Complexity:** Intermediate  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Create effective mock objects and stubs to isolate unit tests from external dependencies

**Why:** Mocking enables fast, reliable tests by replacing slow/unreliable dependencies (databases, APIs, file systems) with controlled test doubles, reducing test time from minutes to milliseconds

**When to use:**
- Testing code that depends on external services
- Isolating units for true unit testing
- Testing error conditions that are hard to reproduce
- Avoiding slow operations in test suites
- Testing code that uses third-party libraries
- Creating deterministic tests for time-dependent code

---

## Prerequisites

**Required:**
- [ ] Testing framework installed (pytest, Jest, JUnit, etc.)
- [ ] Mocking library (unittest.mock, Jest, Mockito, etc.)
- [ ] Understanding of dependency injection
- [ ] Code under test with identifiable dependencies

**Check before starting:**
```bash
# Python
python -c "from unittest.mock import Mock; print('unittest.mock available')"

# JavaScript
npm list jest  # Jest has built-in mocking

# Java
# Check Maven/Gradle for Mockito dependency
```

---

## Implementation Steps

### Step 1: Identify Dependencies to Mock

**What:** Analyze code to find external dependencies that should be mocked

**How:**
Look for these common mock candidates:
- **External services:** HTTP APIs, databases, message queues
- **File system:** File reads/writes, directory operations
- **Time/randomness:** `datetime.now()`, `random()`, `UUID.generate()`
- **Third-party libraries:** Payment processors, email services
- **Slow operations:** Image processing, ML inference
- **Stateful objects:** Connections, sessions, caches

**Analysis questions:**
- Does this dependency slow down tests?
- Is this dependency unreliable (network, external service)?
- Can this dependency cause side effects?
- Do I need to control this dependency's behavior for testing?

**Code/Commands:**
```python
# Example: Identify dependencies
class UserService:
    def __init__(self, database, email_client, payment_api):
        self.db = database          # ✅ Mock - slow, stateful
        self.email = email_client   # ✅ Mock - external service
        self.payment = payment_api  # ✅ Mock - third-party API
    
    def create_user(self, user_data):
        # This method has 3 dependencies to mock
        user = self.db.save(user_data)
        self.email.send_welcome(user.email)
        self.payment.create_customer(user.id)
        return user
```

**Verification:**
- [ ] Listed all external dependencies
- [ ] Identified which dependencies need mocking
- [ ] Dependencies are injectable (not hardcoded)
- [ ] Clear boundaries between unit and external systems

**If This Fails:**
→ Refactor to use dependency injection
→ Start with most obvious external dependencies (DB, HTTP)
→ Use integration tests if mocking is too complex

---

### Step 2: Choose Mocking Strategy

**What:** Select the appropriate mocking technique for each dependency

**How:**

**Mocking Strategies:**

1. **Mock Objects** - Full object replacement with programmable behavior
2. **Stubs** - Simple objects with hardcoded responses
3. **Spies** - Real objects that track how they're called
4. **Fakes** - Working implementations with shortcuts (in-memory DB)
5. **Monkey Patching** - Runtime replacement of functions/classes

**Decision Matrix:**

| Need | Strategy | Example |
|------|----------|---------|
| Control return values | Stub | Return "success" from API |
| Verify method calls | Mock/Spy | Check email.send() was called |
| Replace system calls | Monkey Patch | Mock datetime.now() |
| Simulate real behavior | Fake | Use in-memory SQLite for tests |
| Test error conditions | Mock | Raise network timeout error |

**Code Examples:**

```python
# STUB - Simple return values
class StubDatabase:
    def get_user(self, user_id):
        return {"id": user_id, "name": "Test User"}

# MOCK - Programmable with verification
from unittest.mock import Mock

mock_db = Mock()
mock_db.get_user.return_value = {"id": 1, "name": "Test"}
# Later: verify it was called
mock_db.get_user.assert_called_once_with(1)

# SPY - Track calls on real object
class SpyDatabase:
    def __init__(self, real_db):
        self.real_db = real_db
        self.calls = []
    
    def get_user(self, user_id):
        self.calls.append(('get_user', user_id))
        return self.real_db.get_user(user_id)

# FAKE - Simplified working implementation
class FakeDatabase:
    def __init__(self):
        self.users = {}
    
    def get_user(self, user_id):
        return self.users.get(user_id)
    
    def save_user(self, user):
        self.users[user['id']] = user
```

**Verification:**
- [ ] Strategy matches testing needs
- [ ] Won't over-mock (leaving nothing to test)
- [ ] Mocks are simpler than real implementation
- [ ] Tests remain readable and maintainable

**If This Fails:**
→ Start with simple stubs, add complexity as needed
→ Use library mocks (unittest.mock) before custom implementations
→ Consider if integration test might be better

---

### Step 3: Implement Mocks with Framework

**What:** Create mocks using your testing framework's tools

**How:**

**Python (unittest.mock):**

```python
from unittest.mock import Mock, MagicMock, patch, call
import pytest

# Basic mock
def test_with_basic_mock():
    mock_db = Mock()
    mock_db.get_user.return_value = {"id": 1, "name": "Alice"}
    
    service = UserService(mock_db)
    user = service.get_user(1)
    
    assert user["name"] == "Alice"
    mock_db.get_user.assert_called_once_with(1)

# Mock with side effects
def test_with_side_effect():
    mock_api = Mock()
    mock_api.call.side_effect = [
        {"status": "pending"},  # First call
        {"status": "complete"}  # Second call
    ]
    
    service = PollingService(mock_api)
    result = service.wait_for_completion()
    
    assert result["status"] == "complete"
    assert mock_api.call.call_count == 2

# Patch built-in functions
@patch('datetime.datetime')
def test_with_time_mock(mock_datetime):
    mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0)
    
    service = TimeService()
    result = service.get_current_time()
    
    assert result.hour == 12

# Context manager patching
def test_with_context_patch():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}
        
        result = fetch_api_data()
        
        assert result["data"] == "test"
        mock_get.assert_called_once()

# Mock multiple methods
def test_with_multiple_methods():
    mock_db = Mock()
    mock_db.get_user.return_value = {"id": 1}
    mock_db.save_user.return_value = True
    
    service = UserService(mock_db)
    service.update_user(1, {"name": "Updated"})
    
    # Verify call order and arguments
    expected_calls = [
        call.get_user(1),
        call.save_user({"id": 1, "name": "Updated"})
    ]
    assert mock_db.method_calls == expected_calls
```

**JavaScript (Jest):**

```javascript
// Basic mock
test('with basic mock', () => {
  const mockDb = {
    getUser: jest.fn().mockReturnValue({ id: 1, name: 'Alice' })
  };
  
  const service = new UserService(mockDb);
  const user = service.getUser(1);
  
  expect(user.name).toBe('Alice');
  expect(mockDb.getUser).toHaveBeenCalledWith(1);
  expect(mockDb.getUser).toHaveBeenCalledTimes(1);
});

// Mock with different return values
test('with multiple return values', () => {
  const mockApi = {
    call: jest.fn()
      .mockReturnValueOnce({ status: 'pending' })
      .mockReturnValueOnce({ status: 'complete' })
  };
  
  const service = new PollingService(mockApi);
  const result = service.waitForCompletion();
  
  expect(result.status).toBe('complete');
  expect(mockApi.call).toHaveBeenCalledTimes(2);
});

// Mock module
jest.mock('axios');
test('with mocked module', async () => {
  const axios = require('axios');
  axios.get.mockResolvedValue({ data: { user: 'test' } });
  
  const result = await fetchUser(1);
  
  expect(result.user).toBe('test');
  expect(axios.get).toHaveBeenCalledWith('/users/1');
});

// Spy on real method
test('with spy', () => {
  const user = new User();
  const spy = jest.spyOn(user, 'save');
  
  user.update({ name: 'New Name' });
  
  expect(spy).toHaveBeenCalledTimes(1);
  spy.mockRestore();
});

// Mock timer
test('with timer mock', () => {
  jest.useFakeTimers();
  const callback = jest.fn();
  
  setTimeout(callback, 1000);
  jest.advanceTimersByTime(1000);
  
  expect(callback).toHaveBeenCalled();
  jest.useRealTimers();
});
```

**Java (Mockito):**

```java
import static org.mockito.Mockito.*;
import org.junit.jupiter.api.Test;

@Test
void testWithBasicMock() {
    // Create mock
    UserRepository mockRepo = mock(UserRepository.class);
    when(mockRepo.findById(1L)).thenReturn(new User(1L, "Alice"));
    
    UserService service = new UserService(mockRepo);
    User user = service.getUser(1L);
    
    assertEquals("Alice", user.getName());
    verify(mockRepo, times(1)).findById(1L);
}

@Test
void testWithMultipleReturns() {
    ApiClient mockApi = mock(ApiClient.class);
    when(mockApi.call())
        .thenReturn(new Status("pending"))
        .thenReturn(new Status("complete"));
    
    PollingService service = new PollingService(mockApi);
    Status result = service.waitForCompletion();
    
    assertEquals("complete", result.getValue());
    verify(mockApi, times(2)).call();
}

@Test
void testWithException() {
    Database mockDb = mock(Database.class);
    when(mockDb.connect()).thenThrow(new ConnectionException());
    
    assertThrows(ServiceException.class, () -> {
        new Service(mockDb).initialize();
    });
}

// Argument captor
@Test
void testWithArgumentCaptor() {
    EmailService mockEmail = mock(EmailService.class);
    UserService service = new UserService(mockEmail);
    
    service.createUser(new User("test@example.com"));
    
    ArgumentCaptor<Email> captor = ArgumentCaptor.forClass(Email.class);
    verify(mockEmail).send(captor.capture());
    
    Email sentEmail = captor.getValue();
    assertEquals("test@example.com", sentEmail.getTo());
}
```

**Verification:**
- [ ] Mocks created successfully
- [ ] Return values configured correctly
- [ ] Method calls are verified
- [ ] Tests pass with mocks

**If This Fails:**
→ Check mock setup before assertions
→ Use `print(mock.method_calls)` to see what was called
→ Ensure mock is passed to code under test

---

### Step 4: Configure Mock Behavior

**What:** Set up complex mock behaviors for realistic testing

**How:**

**Return Values:**
```python
# Simple return
mock.method.return_value = "result"

# Different values on each call
mock.method.side_effect = ["first", "second", "third"]

# Computed return value
mock.method.side_effect = lambda x: x * 2

# Return different values based on arguments
def custom_return(arg):
    return {"small": 1, "large": 100}[arg]
mock.method.side_effect = custom_return
```

**Exceptions:**
```python
# Raise exception
mock.method.side_effect = ValueError("Invalid input")

# Raise on specific call
mock.method.side_effect = [
    "success",
    RuntimeError("Network error"),
    "success"
]
```

**Async operations:**
```python
# Python async mock
import asyncio
from unittest.mock import AsyncMock

mock_api = AsyncMock()
mock_api.fetch.return_value = {"data": "test"}

async def test_async():
    result = await mock_api.fetch()
    assert result["data"] == "test"

# JavaScript async mock
test('async operation', async () => {
  const mockApi = {
    fetch: jest.fn().mockResolvedValue({ data: 'test' })
  };
  
  const result = await mockApi.fetch();
  expect(result.data).toBe('test');
});
```

**Context managers:**
```python
# Mock file operations
from unittest.mock import mock_open, patch

m = mock_open(read_data='file contents')
with patch('builtins.open', m):
    with open('file.txt') as f:
        data = f.read()
    
assert data == 'file contents'
m.assert_called_once_with('file.txt')
```

**Verification:**
- [ ] Mock behavior matches real dependency
- [ ] Error conditions can be simulated
- [ ] Async operations handled correctly
- [ ] Edge cases covered

**If This Fails:**
→ Start simple, add complexity incrementally
→ Test mock behavior separately first
→ Check mock configuration syntax

---

### Step 5: Verify Mock Interactions

**What:** Assert that code interacts with mocks correctly

**How:**

**Call verification patterns:**

```python
# Python
mock.method.assert_called()              # Called at least once
mock.method.assert_called_once()         # Called exactly once
mock.method.assert_called_with(arg)      # Called with specific args
mock.method.assert_called_once_with(arg) # Once with specific args
mock.method.assert_not_called()          # Never called

# Check call count
assert mock.method.call_count == 3

# Check call arguments
assert mock.method.call_args == call(1, foo='bar')

# Check all calls
assert mock.method.call_args_list == [
    call(1),
    call(2),
    call(3)
]

# Any call with arguments
mock.method.assert_any_call(arg)
```

```javascript
// JavaScript (Jest)
expect(mock.method).toHaveBeenCalled()
expect(mock.method).toHaveBeenCalledTimes(3)
expect(mock.method).toHaveBeenCalledWith(arg1, arg2)
expect(mock.method).toHaveBeenLastCalledWith(arg)
expect(mock.method).toHaveBeenNthCalledWith(2, arg)
expect(mock.method).not.toHaveBeenCalled()
```

```java
// Java (Mockito)
verify(mock).method()
verify(mock, times(3)).method()
verify(mock, never()).method()
verify(mock, atLeastOnce()).method()
verify(mock, atMost(3)).method()
verify(mock).method(eq(arg))
verifyNoMoreInteractions(mock)
```

**Order verification:**
```python
# Python - verify call order
from unittest.mock import call

manager = Mock()
manager.attach_mock(mock1, 'mock1')
manager.attach_mock(mock2, 'mock2')

# Use mocks
mock1.method()
mock2.method()

# Verify order
expected_calls = [
    call.mock1.method(),
    call.mock2.method()
]
assert manager.mock_calls == expected_calls
```

**Verification:**
- [ ] All expected calls verified
- [ ] Call arguments checked
- [ ] Call count assertions pass
- [ ] Call order validated when important

**If This Fails:**
→ Print `mock.method_calls` to see what happened
→ Use `.assert_called()` first, then add argument checks
→ Reset mock between test sections if needed

---

### Step 6: Avoid Common Mocking Pitfalls

**What:** Follow best practices to keep mocks maintainable

**How:**

**Pitfall 1: Over-mocking**
```python
# BAD - Mocking too much, nothing left to test
def test_over_mocked():
    mock_validator = Mock(return_value=True)
    mock_formatter = Mock(return_value="formatted")
    mock_saver = Mock(return_value=True)
    
    # The actual code being tested is trivial
    result = process(mock_validator, mock_formatter, mock_saver)
    assert result is True  # What did we actually test?

# GOOD - Mock external dependencies only
def test_appropriate_mocking():
    mock_db = Mock()  # External dependency
    
    # Test real logic with real validator and formatter
    service = UserService(database=mock_db)
    user = service.create_user({"email": "test@example.com"})
    
    # Verify interaction with external system
    mock_db.save.assert_called_once()
```

**Pitfall 2: Brittle tests**
```python
# BAD - Tests internal implementation details
def test_brittle():
    mock_cache = Mock()
    service = Service(mock_cache)
    
    service.get_data("key")
    
    # This breaks if implementation changes, even if behavior doesn't
    mock_cache._internal_method.assert_called()

# GOOD - Test public interface only
def test_robust():
    mock_cache = Mock()
    service = Service(mock_cache)
    
    result = service.get_data("key")
    
    # Only verify public contract
    assert result is not None
    mock_cache.get.assert_called_with("key")
```

**Pitfall 3: Mock leaking between tests**
```python
# BAD - Mock state persists
mock_db = Mock()  # Module-level, shared

def test_one():
    mock_db.get.return_value = "test1"
    assert service.fetch() == "test1"

def test_two():
    # Still has return_value from test_one!
    assert service.fetch() is None  # FAILS

# GOOD - Fresh mock per test
@pytest.fixture
def mock_db():
    return Mock()

def test_one(mock_db):
    mock_db.get.return_value = "test1"
    assert Service(mock_db).fetch() == "test1"

def test_two(mock_db):
    # Fresh mock, no state leak
    assert Service(mock_db).fetch() is None
```

**Pitfall 4: Not testing error paths**
```python
# GOOD - Test both success and failure
def test_success_path():
    mock_api = Mock(return_value={"status": "ok"})
    result = service.call_api(mock_api)
    assert result["status"] == "ok"

def test_error_path():
    mock_api = Mock(side_effect=NetworkError())
    with pytest.raises(ServiceError):
        service.call_api(mock_api)
```

**Verification:**
- [ ] Mocks replace only external dependencies
- [ ] Tests verify behavior, not implementation
- [ ] Mocks are isolated between tests
- [ ] Both success and error paths tested

**If This Fails:**
→ Ask: "What behavior am I testing?"
→ Use fixtures/setUp to get fresh mocks
→ Review if integration test might be better

---

## Verification Checklist

After completing this workflow:

- [ ] All external dependencies identified and mocked
- [ ] Appropriate mocking strategy chosen for each dependency
- [ ] Mocks configured with realistic behavior
- [ ] Mock interactions verified in tests
- [ ] Tests are fast and reliable
- [ ] Error conditions tested
- [ ] No mock leakage between tests
- [ ] Code remains testable and loosely coupled

---

## Common Issues & Solutions

### Issue: Mocks don't match real behavior

**Symptoms:**
- Tests pass but production fails
- Mocks return impossible values
- Tests don't catch real bugs

**Solution:**
```python
# Use contract tests or integration tests
def test_mock_matches_reality():
    """Verify mock behavior matches real API"""
    mock_api = create_mock_api()
    real_api = RealAPI(test_mode=True)
    
    # Same input should give compatible output
    result_mock = call_with_api(mock_api)
    result_real = call_with_api(real_api)
    
    assert type(result_mock) == type(result_real)
    assert result_mock.keys() == result_real.keys()

# Or use VCR/recorded responses
@vcr.use_cassette('fixtures/api_response.yaml')
def test_with_real_response():
    # Uses recorded real API response
    result = call_api()
    assert result["status"] == "success"
```

**Prevention:**
- Run integration tests regularly
- Keep mocks updated with API changes
- Use contract testing
- Record real responses for mocks

---

### Issue: Tests become unreadable

**Symptoms:**
- Setup code is longer than test code
- Mocks nested 5+ levels deep
- Hard to understand what's being tested

**Solution:**
```python
# BAD
def test_complex():
    mock1 = Mock()
    mock1.method.return_value.attribute.method.return_value = "value"
    # ... 20 more lines of mock setup
    result = function(mock1)
    assert result == "expected"

# GOOD - Extract to fixture/helper
@pytest.fixture
def configured_mocks():
    """Ready-to-use mocks for common scenario"""
    mocks = {
        'db': create_mock_db(),
        'api': create_mock_api(),
        'cache': create_mock_cache()
    }
    # All configuration in one place
    return mocks

def test_readable(configured_mocks):
    result = function(configured_mocks['db'])
    assert result == "expected"
```

**Prevention:**
- Extract mock setup to fixtures or factory functions
- Use builder pattern for complex mocks
- Consider if integration test would be clearer

---

### Issue: Mocking framework fights language features

**Symptoms:**
- Can't mock __init__, __new__, built-ins
- Property mocks don't work
- Struggling with metaclasses or descriptors

**Solution:**
```python
# For difficult-to-mock code
# Option 1: Refactor to use dependency injection
class Service:
    def __init__(self, time_provider=None):
        self.time_provider = time_provider or datetime
    
    def get_timestamp(self):
        return self.time_provider.now()

# Option 2: Use wrapper/adapter
class TimeProvider:
    @staticmethod
    def now():
        return datetime.now()

# Option 3: Accept it's an integration test
def test_with_real_datetime():
    """Can't easily mock datetime, so test real behavior"""
    service = Service()
    start = datetime.now()
    timestamp = service.get_timestamp()
    end = datetime.now()
    assert start <= timestamp <= end
```

**Prevention:**
- Design for testability with DI
- Wrap hard-to-mock built-ins
- Sometimes integration tests are the answer

---

## Examples

### Example 1: Testing Email Service

**Context:** Test user registration without sending real emails

**Implementation:**
```python
from unittest.mock import Mock
import pytest

class UserRegistration:
    def __init__(self, database, email_service):
        self.db = database
        self.email = email_service
    
    def register(self, email, password):
        if self.db.user_exists(email):
            return {"error": "User already exists"}
        
        user_id = self.db.create_user(email, password)
        self.email.send_welcome(email, user_id)
        return {"success": True, "user_id": user_id}

def test_successful_registration():
    # Setup mocks
    mock_db = Mock()
    mock_db.user_exists.return_value = False
    mock_db.create_user.return_value = 123
    
    mock_email = Mock()
    
    # Test
    service = UserRegistration(mock_db, mock_email)
    result = service.register("test@example.com", "password")
    
    # Verify
    assert result["success"] is True
    assert result["user_id"] == 123
    mock_db.user_exists.assert_called_once_with("test@example.com")
    mock_db.create_user.assert_called_once_with("test@example.com", "password")
    mock_email.send_welcome.assert_called_once_with("test@example.com", 123)

def test_duplicate_user():
    # Setup mocks
    mock_db = Mock()
    mock_db.user_exists.return_value = True
    
    mock_email = Mock()
    
    # Test
    service = UserRegistration(mock_db, mock_email)
    result = service.register("existing@example.com", "password")
    
    # Verify
    assert "error" in result
    mock_email.send_welcome.assert_not_called()  # No email sent
```

**Result:** Tests run in 0.01s instead of 2s with real email service

---

### Example 2: Testing API Client with Network Errors

**Context:** Test retry logic when network is unreliable

**Implementation:**
```python
import requests
from unittest.mock import patch, Mock

class APIClient:
    def __init__(self, base_url, max_retries=3):
        self.base_url = base_url
        self.max_retries = max_retries
    
    def fetch_data(self, endpoint):
        for attempt in range(self.max_retries):
            try:
                response = requests.get(f"{self.base_url}/{endpoint}")
                response.raise_for_status()
                return response.json()
            except requests.RequestException:
                if attempt == self.max_retries - 1:
                    raise
        
@patch('requests.get')
def test_retry_on_network_error(mock_get):
    # First two calls fail, third succeeds
    mock_get.side_effect = [
        requests.RequestException("Network error"),
        requests.RequestException("Network error"),
        Mock(json=lambda: {"data": "success"}, status_code=200)
    ]
    
    client = APIClient("https://api.example.com", max_retries=3)
    result = client.fetch_data("users")
    
    assert result["data"] == "success"
    assert mock_get.call_count == 3

@patch('requests.get')
def test_max_retries_exceeded(mock_get):
    # All calls fail
    mock_get.side_effect = requests.RequestException("Network error")
    
    client = APIClient("https://api.example.com", max_retries=3)
    
    with pytest.raises(requests.RequestException):
        client.fetch_data("users")
    
    assert mock_get.call_count == 3
```

**Result:** Can test retry logic without actual network calls or waits

---

### Example 3: Testing Time-Dependent Code

**Context:** Test caching expiration without waiting

**Implementation:**
```python
from datetime import datetime, timedelta
from unittest.mock import patch

class Cache:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self.data = {}
    
    def set(self, key, value):
        self.data[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def get(self, key):
        if key not in self.data:
            return None
        
        if datetime.now() > self.data[key]['expires']:
            del self.data[key]
            return None
        
        return self.data[key]['value']

def test_cache_expiration():
    cache = Cache(ttl_seconds=60)
    
    # Mock time at 12:00
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0)
        cache.set('key', 'value')
        
        # Value should exist
        assert cache.get('key') == 'value'
    
    # Mock time at 12:02 (after expiration)
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 2)
        
        # Value should be expired
        assert cache.get('key') is None
```

**Result:** Test time-dependent behavior instantly

---

## Best Practices

### DO:
✅ Mock external dependencies only (APIs, databases, file systems)
✅ Use dependency injection to make code testable
✅ Verify behavior, not implementation details
✅ Test both success and error paths
✅ Keep mocks simple and realistic
✅ Use fresh mocks for each test (fixtures)
✅ Document what mocks represent
✅ Name mocks clearly (mock_db, mock_api_client)
✅ Use appropriate assertion methods
✅ Combine mocks with integration tests

### DON'T:
❌ Mock everything - test real logic when possible
❌ Test internal implementation details
❌ Create complex mock hierarchies
❌ Let mocks leak between tests
❌ Mock something you don't own without testing the real thing
❌ Write mocks that don't match reality
❌ Over-specify mock interactions (don't assert call count if you don't care)
❌ Use mocks as an excuse for bad design
❌ Forget to test error conditions
❌ Mock the code under test

---

## Related Workflows

**Prerequisites:**
- `dev-008`: Unit Testing Setup - Basic testing infrastructure
- `dev-002`: Function Refactoring - Making code testable with DI

**Next Steps:**
- `tes-002`: Property Based Testing - Testing with generated inputs
- `tes-004`: Test Data Generation - Creating realistic test data
- `qa-008`: Integration Testing - Testing without mocks

**Alternatives:**
- `tes-004`: Test Data Generation - Using real data with test doubles
- In-memory fakes - Using fast real implementations (SQLite, in-memory queue)
- Contract testing - Ensuring mocks match real APIs

---

## Tags
`testing` `mocking` `unit-testing` `test-doubles` `stubs` `spies` `fakes` `unittest-mock` `jest` `mockito` `dependency-injection`
