# Test Failure Investigation

**ID:** qua-010  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 30-90 minutes (per failure)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic approach to investigating, diagnosing, and fixing failing tests efficiently, whether they're unit tests, integration tests, or end-to-end tests.

**Why:** Failing tests can block development, delay releases, and indicate real bugs or test quality issues. A structured investigation process helps identify root causes quickly, fix issues effectively, and prevent similar failures. Studies show that proper test failure investigation can reduce debug time by 50% and catch production bugs 80% earlier in the development cycle.

**When to use:**
- CI/CD pipeline shows failing tests
- Tests fail locally but pass in CI (or vice versa)
- Intermittent/flaky test failures
- Tests break after code changes
- Tests fail after dependency updates
- New tests written that immediately fail
- Production bug revealed by adding new test

---

## Prerequisites

**Required:**
- [ ] Access to codebase and test suite
- [ ] Development environment set up
- [ ] Test runner configured (pytest, jest, etc.)
- [ ] Access to CI/CD logs
- [ ] Understanding of testing frameworks used

**Check before starting:**
```bash
# Verify test environment
python --version  # or node --version
pytest --version  # or appropriate test runner

# Check test configuration
cat pytest.ini  # or jest.config.js

# Verify dependencies installed
pip list  # or npm list
pip check  # Check for dependency conflicts

# Ensure database is accessible (if needed)
psql -U user -d testdb -c "SELECT 1"  # or equivalent

# Check for running test services
docker ps  # If using containers for tests

# Verify test data fixtures available
ls tests/fixtures/
```

---

## Implementation Steps

### Step 1: Gather Information About the Failure

**What:** Collect all available information about the failing test before jumping into code.

**How:**

**Identify the failing test:**
```bash
# Run the test suite to identify failures
pytest -v

# Example output:
# tests/test_user.py::test_create_user FAILED
# tests/test_user.py::test_update_user PASSED
# tests/test_user.py::test_delete_user FAILED

# Run specific failing test with verbose output
pytest tests/test_user.py::test_create_user -v -s

# Or with even more detail
pytest tests/test_user.py::test_create_user -vv --tb=long

# For JavaScript/Jest:
npm test -- --verbose test_user.test.js
```

**Capture the error message:**
```bash
# Run test and save output
pytest tests/test_user.py::test_create_user -v > test_output.txt 2>&1

# Or use pytest's built-in reporting
pytest tests/test_user.py::test_create_user --tb=long --capture=no

# Example error output to analyze:
# FAILED tests/test_user.py::test_create_user - AssertionError: assert 201 == 200
#   where 201 = response.status_code
#   Expected status code 200, got 201
```

**Check CI/CD logs:**
```bash
# Get CI logs (GitHub Actions)
gh run view <run-id> --log

# Download full logs
gh run download <run-id>

# Key information to extract from CI logs:
# - Exact error message
# - Stack trace
# - Environment details (Python/Node version, OS)
# - Timing information
# - Whether it passed in previous runs
```

**Determine failure pattern:**
```markdown
## Questions to answer:

1. **When did it start failing?**
   - After specific commit?
   - After dependency update?
   - Always failed?
   - Random/intermittent?

2. **Where does it fail?**
   - Local environment only?
   - CI/CD only?
   - Specific OS/platform?
   - Specific test runner version?

3. **How often does it fail?**
   - Every time (deterministic)?
   - Sometimes (flaky)?
   - Only under certain conditions?

4. **What changed?**
   - Recent code changes
   - Dependency updates
   - Configuration changes
   - Infrastructure changes
```

**Check test history:**
```bash
# Find when test was introduced
git log --follow --oneline tests/test_user.py

# Check recent changes to test
git log -p tests/test_user.py | head -100

# Find who last modified it
git blame tests/test_user.py

# Check if test ever passed in CI
gh run list --workflow=tests.yml --limit=20

# View specific test results over time
# (varies by CI platform - GitHub, GitLab, Jenkins, etc.)
```

**Verification:**
- [ ] Exact error message captured
- [ ] Stack trace obtained
- [ ] Failure pattern identified (deterministic vs. flaky)
- [ ] Environment details noted
- [ ] Recent changes identified
- [ ] Test history reviewed
- [ ] CI logs examined

**If This Fails:**
→ If can't reproduce locally, debug in CI environment
→ If error message unclear, add more logging to test
→ If no stack trace, ensure test runner configured for verbose output

---

### Step 2: Reproduce the Failure Consistently

**What:** Get the test to fail reliably in your local environment so you can debug effectively.

**How:**

**Run test in isolation:**
```bash
# Run single failing test
pytest tests/test_user.py::test_create_user -v

# If it passes in isolation, might be a test ordering issue
# Run all tests in that file
pytest tests/test_user.py -v

# If still passes, might be affected by other test files
# Run entire test suite
pytest -v
```

**Check for test dependencies:**
```python
# ❌ Bad: Test depends on another test running first
def test_create_user():
    # Assumes test_setup_database already ran
    user = User.query.first()  # Might be None if run in isolation
    assert user is not None

# ✅ Good: Test is independent
def test_create_user():
    # Set up everything test needs
    setup_test_database()
    user = create_test_user()
    assert user is not None
```

**Reproduce environment conditions:**
```bash
# Match CI environment
# 1. Check CI Python version
python --version  # Ensure matches CI

# 2. Install exact dependency versions
pip install -r requirements-dev.txt

# 3. Match environment variables
export DATABASE_URL="postgresql://localhost/testdb"
export DEBUG=False
export TESTING=True

# 4. Use same database state
dropdb testdb && createdb testdb
python manage.py migrate

# 5. Match working directory
cd /path/to/project/root
pytest tests/test_user.py::test_create_user
```

**Test different scenarios:**
```bash
# Run test multiple times (check for flakiness)
for i in {1..10}; do
    echo "Run $i:"
    pytest tests/test_user.py::test_create_user -v
done

# Run in parallel (expose race conditions)
pytest tests/test_user.py -n 4

# Run with different random seeds
pytest tests/test_user.py --randomly-seed=1
pytest tests/test_user.py --randomly-seed=2

# Run in different orders
pytest tests/test_user.py --random-order
```

**Debug with pytest options:**
```bash
# Drop into debugger on failure
pytest tests/test_user.py::test_create_user --pdb

# Show local variables in traceback
pytest tests/test_user.py::test_create_user -l

# Don't capture output (see print statements)
pytest tests/test_user.py::test_create_user -s

# Show full diff for assertion failures
pytest tests/test_user.py::test_create_user -vv

# Increase verbosity
pytest tests/test_user.py::test_create_user -vvv
```

**Add debugging output:**
```python
# Add temporary logging to test
import logging
logging.basicConfig(level=logging.DEBUG)

def test_create_user():
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Creating user with email: {email}")
    response = client.post("/users", json={"email": email})
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response body: {response.json()}")
    
    assert response.status_code == 200
```

**Verification:**
- [ ] Test fails consistently locally
- [ ] Failure matches CI failure
- [ ] Can reproduce on demand
- [ ] Environment matches CI
- [ ] Debugging output available
- [ ] Test dependencies identified

**If This Fails:**
→ If can't reproduce locally, add more logging in CI
→ If only fails in CI, request SSH access or use CI debugging tools
→ If test is flaky, run 100+ times to find pattern
→ Document conditions under which it fails

---

### Step 3: Analyze the Root Cause

**What:** Determine why the test is failing by examining the code, test, and their interactions.

**How:**

**Understand what the test is testing:**
```python
# Read the test carefully
def test_create_user():
    """
    Test user creation endpoint.
    
    Verifies that:
    1. User can be created with valid data
    2. Response returns 200 status
    3. User is saved to database
    4. Email verification sent
    """
    response = client.post("/users", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    
    assert response.status_code == 200  # ← Failing here, getting 201
    assert "id" in response.json()
    
    # Verify user in database
    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None
    assert user.name == "Test User"
```

**Common failure categories:**

**1. Assertion Failures:**
```python
# Example: assert response.status_code == 200
# Got: 201

# Investigate why code returns different value
# Check the actual endpoint:
@app.route("/users", methods=["POST"])
def create_user():
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201  # ← Ah! Returns 201, not 200

# Options:
# 1. Fix test (if 201 is correct for creation):
assert response.status_code == 201

# 2. Fix code (if 200 is required):
return jsonify(user.to_dict()), 200
```

**2. Missing/Incorrect Test Data:**
```python
# Test assumes data exists that doesn't
def test_update_user():
    user = User.query.get(1)  # ← Might be None!
    assert user is not None, "User not found"
    
    # Fix: Create user in test
    user = create_test_user(id=1)
    # Now proceed with test
```

**3. Incorrect Mocking:**
```python
# ❌ Mock not working as expected
from unittest.mock import patch

def test_send_email():
    with patch('app.email.send') as mock_send:
        send_welcome_email("test@example.com")
        mock_send.assert_called_once()  # ← Fails: mock not called

# Issue: Wrong import path
# If code does: from app.email import send
# And test mocks: 'app.email.send'
# The mock won't work!

# ✅ Fix: Mock where it's used, not where it's defined
with patch('app.services.user.send') as mock_send:
    # Now works
```

**4. Race Conditions:**
```python
# Test fails intermittently due to timing
def test_async_processing():
    submit_job()
    result = get_job_result()  # ← Sometimes None, sometimes has value
    assert result is not None

# Fix: Add proper waiting
def test_async_processing():
    submit_job()
    
    # Wait for job completion with timeout
    for _ in range(50):  # 5 seconds max
        result = get_job_result()
        if result is not None:
            break
        time.sleep(0.1)
    
    assert result is not None
```

**5. Environment-Specific Issues:**
```python
# Test fails in CI but passes locally
def test_file_path():
    data_file = "data/test.json"  # ← Relative path
    with open(data_file) as f:
        data = json.load(f)

# Issue: Working directory differs in CI

# Fix: Use absolute paths
import os
data_file = os.path.join(os.path.dirname(__file__), "fixtures/test.json")
```

**Use debugging tools:**
```bash
# Run with debugger
pytest tests/test_user.py::test_create_user --pdb

# When breakpoint hits:
# (Pdb) p response.status_code  # Print variable
# 201
# (Pdb) p response.json()  # Print response body
# {'id': 1, 'email': 'test@example.com'}
# (Pdb) c  # Continue
# (Pdb) n  # Next line
# (Pdb) s  # Step into function

# Add breakpoints in code
import pdb; pdb.set_trace()  # Will break here
```

**Check code changes:**
```bash
# What changed in the code under test?
git diff main -- src/app/routes/users.py

# Example diff shows:
# - return jsonify(user.to_dict()), 200
# + return jsonify(user.to_dict()), 201  # Changed to follow REST standards

# Ah! Someone changed status code, need to update test
```

**Check dependency changes:**
```bash
# Compare dependency versions
git diff main -- requirements.txt

# If library updated:
# - Check changelog for breaking changes
# - Check if behavior changed
# - Update test to match new behavior

# Example:
# - requests 2.28.0 → 2.31.0
# Check: https://github.com/psf/requests/blob/main/HISTORY.md
```

**Verification:**
- [ ] Root cause identified
- [ ] Understand why test fails
- [ ] Know what needs to change (code or test)
- [ ] Impact of change understood
- [ ] Breaking change identified (if any)

**If This Fails:**
→ Add more logging to understand flow
→ Use debugger to step through code
→ Compare working vs broken versions
→ Ask teammate familiar with code
→ Check git history and blame for context

---

### Step 4: Implement the Fix

**What:** Fix either the code or the test, depending on what the investigation revealed.

**How:**

**Scenario 1: Test is wrong, code is correct**
```python
# Example: Test expects wrong status code
# Fix the test:

# ❌ Before:
def test_create_user():
    response = client.post("/users", json=data)
    assert response.status_code == 200  # Wrong expectation

# ✅ After:
def test_create_user():
    response = client.post("/users", json=data)
    assert response.status_code == 201  # Correct: 201 for creation
    assert "id" in response.json()
```

**Scenario 2: Code is wrong, test is correct**
```python
# Example: Code has a bug
# Fix the code:

# ❌ Before (buggy code):
def create_user(email, name):
    if User.query.filter_by(email=email).first():
        return None  # Returns None instead of raising error
    
    user = User(email=email, name=name)
    db.session.add(user)
    db.session.commit()
    return user

# ✅ After (fixed):
def create_user(email, name):
    if User.query.filter_by(email=email).first():
        raise ValueError(f"User with email {email} already exists")
    
    user = User(email=email, name=name)
    db.session.add(user)
    db.session.commit()
    return user
```

**Scenario 3: Test has incorrect setup**
```python
# ❌ Before: Test doesn't set up data correctly
def test_update_user():
    response = client.put("/users/1", json={"name": "Updated"})
    assert response.status_code == 200  # Fails: user doesn't exist

# ✅ After: Set up test data
def test_update_user():
    # Create user first
    user = create_test_user(id=1, name="Original")
    
    response = client.put(f"/users/{user.id}", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
```

**Scenario 4: Flaky test needs better synchronization**
```python
# ❌ Before: Race condition
def test_async_job():
    job_id = submit_async_job()
    time.sleep(1)  # Hope it's done!
    result = get_job_result(job_id)
    assert result.status == "completed"  # Sometimes fails

# ✅ After: Proper waiting with timeout
def test_async_job():
    job_id = submit_async_job()
    
    # Poll with timeout
    timeout = time.time() + 10  # 10 seconds
    while time.time() < timeout:
        result = get_job_result(job_id)
        if result.status == "completed":
            break
        time.sleep(0.1)
    
    assert result.status == "completed", f"Job timed out: {result.status}"
```

**Scenario 5: Mock needs fixing**
```python
# ❌ Before: Mock not working
from unittest.mock import patch

def test_send_notification():
    with patch('app.notifications.send_email') as mock_email:
        notify_user(user_id=1, message="Hello")
        mock_email.assert_called()  # Fails: not called

# Issue: Wrong patch location
# Code does: from app.notifications import send_email
# Need to patch where it's imported

# ✅ After: Patch correct location
def test_send_notification():
    with patch('app.services.notifications.send_email') as mock_email:
        notify_user(user_id=1, message="Hello")
        mock_email.assert_called_once_with(
            to="user1@example.com",
            subject="Notification",
            body="Hello"
        )
```

**Scenario 6: Environment-specific issue**
```python
# ❌ Before: Hardcoded path fails in CI
def test_load_config():
    with open('/app/config/test.json') as f:  # Fails: different path in CI
        config = json.load(f)

# ✅ After: Use relative path
import os

def test_load_config():
    config_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "test_config.json"
    )
    with open(config_path) as f:
        config = json.load(f)
```

**Make minimal changes:**
```python
# Principle: Fix the specific issue, don't refactor everything

# ❌ Don't do this:
# - Fix test
# - Refactor entire test file
# - Update unrelated tests
# - Change code style
# All in one commit

# ✅ Do this:
# 1. Fix the specific failing test
# 2. Verify it passes
# 3. Commit
# 4. Refactor in separate PR if needed
```

**Verification:**
- [ ] Fix is minimal and targeted
- [ ] Fix addresses root cause
- [ ] No unrelated changes
- [ ] Fix is clear and understandable
- [ ] Comments added if fix is non-obvious

**If This Fails:**
→ If fix doesn't work, re-analyze root cause
→ If fix is too complex, consider refactoring
→ If unsure about fix, discuss with team
→ If multiple issues, fix one at a time

---

### Step 5: Verify the Fix

**What:** Ensure the fix works and doesn't break anything else.

**How:**

**Run the fixed test:**
```bash
# Run fixed test once
pytest tests/test_user.py::test_create_user -v

# Run multiple times to check for flakiness
for i in {1..20}; do
    pytest tests/test_user.py::test_create_user -v || echo "Failed on run $i"
done

# Should pass consistently
```

**Run related tests:**
```bash
# Run all tests in same file
pytest tests/test_user.py -v

# Run all tests in same module/directory
pytest tests/user/ -v

# Run tests tagged with related markers
pytest -m user_management -v
```

**Run full test suite:**
```bash
# Run entire test suite
pytest

# Or with coverage
pytest --cov=src --cov-report=term --cov-report=html

# Check that:
# - All tests pass
# - No new failures introduced
# - Coverage maintained or improved
```

**Test in different environments:**
```bash
# Test with different Python versions (using tox)
tox

# Or manually:
python3.9 -m pytest tests/test_user.py
python3.10 -m pytest tests/test_user.py
python3.11 -m pytest tests/test_user.py

# Test on different OS (if applicable)
# - Run in Docker container
# - Run in CI environment
```

**Check CI/CD:**
```bash
# Commit and push
git add tests/test_user.py
git commit -m "fix: Update test to expect 201 status code for user creation"
git push origin fix/test-user-creation

# Create PR and verify CI passes
gh pr create --title "fix: Update test to expect 201 status code" --body "..."

# Monitor CI
gh pr checks <pr-number>

# All checks should pass ✅
```

**Verify no regressions:**
```bash
# Check test metrics
pytest --durations=10  # Slowest tests
# Ensure fix didn't make tests significantly slower

# Check coverage
pytest --cov=src --cov-report=term
# Ensure coverage didn't decrease

# Run performance tests (if applicable)
pytest tests/performance/ -v
```

**Verification:**
- [ ] Fixed test passes consistently
- [ ] Related tests pass
- [ ] Full test suite passes
- [ ] CI/CD passes
- [ ] No new failures introduced
- [ ] Performance not degraded
- [ ] Coverage maintained

**If This Fails:**
→ If test still fails, root cause misidentified - go back to Step 3
→ If other tests fail, fix introduced regression - review changes
→ If CI fails but local passes, environment issue - investigate
→ If flaky, run more times to verify

---

### Step 6: Document and Prevent Future Failures

**What:** Document the fix and take steps to prevent similar issues in the future.

**How:**

**Update test documentation:**
```python
# Add clear docstring explaining what test does
def test_create_user():
    """
    Test user creation endpoint returns 201 Created.
    
    Verifies that:
    - POST /users creates new user
    - Response status is 201 (Created) per REST standards
    - Response includes user ID
    - User is saved to database
    - Welcome email is sent
    
    Note: Changed from expecting 200 to 201 in PR #456
    to align with REST standards.
    """
    response = client.post("/users", json=data)
    assert response.status_code == 201  # 201 Created
```

**Add comments for non-obvious fixes:**
```python
# If fix requires explanation:
def test_async_processing():
    submit_job()
    
    # Wait for job completion with 10s timeout
    # Note: Job processing can take 5-8 seconds under load
    # See issue #789 for details on timing requirements
    timeout = time.time() + 10
    while time.time() < timeout:
        result = get_job_result()
        if result is not None:
            break
        time.sleep(0.1)
    
    assert result is not None, "Job did not complete within timeout"
```

**Create issue for underlying problems:**
```bash
# If fix is a workaround, create issue for proper fix
gh issue create --title "Refactor async job polling to use callbacks" --body "
Current test uses polling with timeout (test_async_processing).
This is brittle and slow.

Better approach:
- Use callbacks or webhooks
- Add job completion event
- Remove polling from tests

See PR #456 for current workaround.
"
```

**Add regression test:**
```python
# If bug was missed by tests, add test for it
def test_create_user_duplicate_email():
    """
    Test that creating user with duplicate email fails.
    
    Regression test for bug #789 where duplicate emails
    were silently ignored instead of raising error.
    """
    # Create first user
    create_user("test@example.com", "User 1")
    
    # Attempt to create duplicate should fail
    with pytest.raises(ValueError, match="already exists"):
        create_user("test@example.com", "User 2")
```

**Update test fixtures/helpers:**
```python
# If test setup was problematic, improve fixtures
@pytest.fixture
def test_user():
    """Create test user with default attributes."""
    user = User(
        email=f"test-{uuid.uuid4()}@example.com",  # Unique email
        name="Test User",
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    yield user
    
    # Cleanup
    db.session.delete(user)
    db.session.commit()

def test_update_user(test_user):
    # Now test has clean user automatically
    response = client.put(f"/users/{test_user.id}", json={"name": "Updated"})
    assert response.status_code == 200
```

**Document in commit message:**
```bash
git commit -m "fix: Update user creation test to expect 201 status

The test was expecting 200 OK but the endpoint correctly returns
201 Created per REST conventions. This was changed in PR #123
but test wasn't updated.

Root cause: API change merged without updating test
Fix: Update test assertion from 200 to 201

Closes #789"
```

**Share learnings with team:**
```markdown
# Post in team chat or wiki:

## Test Failure Investigation - Learnings

**Issue:** test_create_user was failing with status code mismatch

**Root Cause:** API changed to return 201 but test still expected 200

**Fix:** Updated test assertion

**Lessons:**
1. Always update tests when changing API contracts
2. Use constants for status codes to avoid this:
   ```python
   assert response.status_code == status.HTTP_201_CREATED
   ```
3. Add API contract tests to catch breaking changes

**Prevention:**
- Added linting rule to detect hardcoded status codes
- Updated PR template to remind about test updates
- Scheduled refactor to use status code constants (issue #790)
```

**Improve test infrastructure:**
```python
# Add helpers to prevent common issues

# Helper for status codes
from http import HTTPStatus

def test_create_user():
    response = client.post("/users", json=data)
    # Use enum instead of magic number
    assert response.status_code == HTTPStatus.CREATED

# Helper for waiting
def wait_for_condition(condition_func, timeout=10, interval=0.1):
    """Wait for condition to be true with timeout."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        if condition_func():
            return True
        time.sleep(interval)
    return False

def test_async_job():
    job_id = submit_job()
    
    # Now much cleaner
    assert wait_for_condition(
        lambda: get_job(job_id).status == "completed",
        timeout=10
    ), "Job did not complete"
```

**Verification:**
- [ ] Test documentation updated
- [ ] Non-obvious fixes commented
- [ ] Regression test added if needed
- [ ] Related issues created
- [ ] Commit message is descriptive
- [ ] Team informed of learnings
- [ ] Prevention measures identified

**If This Fails:**
→ If documentation unclear, get feedback from teammate
→ If prevention measures not obvious, discuss in team meeting
→ If similar issues keep occurring, deeper root cause needed

---

## Verification Checklist

After completing test failure investigation:

- [ ] Failure information gathered completely
- [ ] Failure reproduced consistently
- [ ] Root cause identified
- [ ] Fix implemented and tested
- [ ] Full test suite passes
- [ ] CI/CD passes
- [ ] Fix documented
- [ ] Prevention measures implemented
- [ ] Team informed if significant
- [ ] Related issues created

---

## Common Issues & Solutions

### Issue: Can't Reproduce Failure Locally

**Symptoms:**
- Test passes locally
- Fails in CI
- Can't debug effectively

**Solution:**
```bash
# 1. Match CI environment exactly
# Check CI config (e.g., .github/workflows/test.yml)
# Note: Python version, dependencies, environment variables

# 2. Use Docker to match CI
docker run -it python:3.11 bash
# Install dependencies and run test

# 3. Add debug logging in CI
# Modify test temporarily:
import logging
logging.basicConfig(level=logging.DEBUG)

# 4. Use CI debugging features
# GitHub Actions: Enable debug logging
# Add workflow variable: ACTIONS_STEP_DEBUG=true

# 5. Request SSH access to CI (if supported)
# Fly.io, Heroku, some CI providers allow SSH

# 6. Compare environments
pip freeze  # Local
# vs. CI requirements
```

**Prevention:**
- Use same dependencies in local and CI (requirements.txt)
- Use containers for consistency
- Add more comprehensive logging
- Test with multiple environments locally

---

### Issue: Flaky Test (Passes Sometimes)

**Symptoms:**
- Test passes 80-90% of time
- Fails randomly
- Hard to debug

**Solution:**
```python
# 1. Run test many times to understand frequency
for i in range(100):
    result = pytest.main(['-x', 'tests/test_flaky.py'])
    if result != 0:
        print(f"Failed on iteration {i}")

# 2. Common causes of flakiness:

# A. Race conditions
# Fix: Add proper synchronization
from tenacity import retry, stop_after_delay, wait_fixed

@retry(stop=stop_after_delay(10), wait=wait_fixed(0.1))
def wait_for_job():
    job = get_job()
    if job.status != "completed":
        raise Exception("Not ready")
    return job

# B. Test ordering dependencies
# Fix: Make tests independent
@pytest.fixture(autouse=True)
def reset_state():
    # Reset database, cache, etc.
    db.session.rollback()
    cache.clear()

# C. Time-dependent logic
# Fix: Mock time
from freezegun import freeze_time

@freeze_time("2024-01-01 12:00:00")
def test_time_dependent():
    # Now time is fixed
    pass

# D. Random data
# Fix: Use fixed seed
import random
random.seed(42)

# Or use faker with seed
from faker import Faker
fake = Faker()
Faker.seed(42)

# 3. Mark as flaky if can't fix immediately
@pytest.mark.flaky(reruns=3)
def test_flaky():
    # Will retry up to 3 times
    pass
```

**Prevention:**
- Avoid time.sleep() in tests
- Use proper synchronization primitives
- Make tests independent
- Use fixed seeds for randomness
- Mock time-dependent code

---

### Issue: Test Fails After Dependency Update

**Symptoms:**
- Test worked before
- Updated dependency
- Now test fails
- Not sure which dependency caused it

**Solution:**
```bash
# 1. Identify which dependency changed
git diff HEAD~1 requirements.txt

# 2. Check changelogs
# For each updated dependency:
# - requests: https://github.com/psf/requests/blob/main/HISTORY.md
# - pytest: https://docs.pytest.org/en/stable/changelog.html

# 3. Bisect to find problematic dependency
# Revert dependencies one by one:
pip install 'requests==2.28.0'  # Old version
pytest tests/test_api.py  # Does it pass now?

# 4. Check for breaking changes
# Example: pytest 7.0 changed fixture behavior
# https://docs.pytest.org/en/stable/deprecations.html

# 5. Update code to work with new version
# Or pin dependency to old version temporarily:
requirements.txt:
requests==2.28.0  # TODO: Update to 2.31.0 (see issue #789)

# 6. Create issue for proper fix
gh issue create --title "Update code for requests 2.31.0"
```

**Prevention:**
- Update dependencies regularly (not all at once)
- Read changelogs before updating
- Have good test coverage
- Use renovate/dependabot for incremental updates

---

### Issue: Mock Not Working

**Symptoms:**
- Mock appears correct
- Code still calls real function
- Test fails or has side effects

**Solution:**
```python
# Common issue: Mocking wrong location

# ❌ Wrong: Mock where function is defined
# Code: from app.email import send_email
with patch('app.email.send_email'):  # Won't work!
    ...

# ✅ Right: Mock where function is used
# If code imports: from app.email import send_email
with patch('app.services.user.send_email'):  # Works!
    ...

# Or mock the module:
with patch('app.email.send_email'):
    from app.services import user  # Import after patching
    ...

# How to find correct patch location:
# 1. Find where function is imported in code under test
# 2. Mock at that location

# Example:
# File: app/services/user.py
# from app.email import send_email

# Mock location should be:
with patch('app.services.user.send_email'):
    # Now works

# Pro tip: Use patch.object for clarity
from app.services import user
with patch.object(user, 'send_email'):
    # Clear what's being mocked
```

**Prevention:**
- Always mock where function is used, not defined
- Use patch.object for clarity
- Add test to verify mock is called
- Document mock locations in test docstrings

---

## Examples

### Example 1: Simple Assertion Failure

**Context:** Test expects 200 status, gets 201

**Investigation:**
```bash
# Step 1: Run test
$ pytest tests/test_user.py::test_create_user -v
FAILED - assert 201 == 200

# Step 2: Check code
@app.route("/users", methods=["POST"])
def create_user():
    ...
    return jsonify(user), 201  # Returns 201

# Step 3: Check if this is correct
# REST standards: POST creating resource → 201 Created ✓

# Step 4: Fix test
def test_create_user():
    response = client.post("/users", json=data)
    assert response.status_code == 201  # Changed from 200

# Step 5: Verify
$ pytest tests/test_user.py::test_create_user -v
PASSED
```

**Result:** Test updated to match correct API behavior, all tests pass

---

### Example 2: Flaky Test Investigation

**Context:** Test sometimes fails with "User not found"

**Investigation:**
```python
# Step 1: Run multiple times
for i in range(50):
    result = pytest.main(['-x', 'tests/test_user_update.py'])
    if result != 0:
        print(f"Failed on iteration {i}")
# Output: Failed on iterations: 3, 7, 12, 23, 41

# Step 2: Examine test
def test_update_user():
    user_id = create_user()  # Async operation
    update_user(user_id, name="New Name")  # Might run before create completes
    user = get_user(user_id)
    assert user.name == "New Name"

# Step 3: Root cause = race condition

# Step 4: Fix with proper waiting
def test_update_user():
    user_id = create_user()
    
    # Wait for user to be created
    timeout = time.time() + 5
    while time.time() < timeout:
        if get_user(user_id):
            break
        time.sleep(0.1)
    
    update_user(user_id, name="New Name")
    user = get_user(user_id)
    assert user.name == "New Name"

# Step 5: Verify
for i in range(100):
    pytest.main(['-x', 'tests/test_user_update.py'])
# All pass!
```

**Result:** Race condition fixed, test now reliable

---

### Example 3: CI-Only Failure

**Context:** Test passes locally, fails in CI

**Investigation:**
```bash
# Step 1: Check CI logs
$ gh run view 12345 --log
ERROR: FileNotFoundError: [Errno 2] No such file or directory: 'data/test.json'

# Step 2: Check test
def test_load_data():
    with open('data/test.json') as f:  # Relative path
        data = json.load(f)

# Step 3: Root cause = working directory differs in CI

# Step 4: Fix with absolute path
import os

def test_load_data():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(test_dir, 'fixtures', 'test.json')
    with open(data_file) as f:
        data = json.load(f)

# Step 5: Push and verify CI
$ git push
$ gh pr checks
✓ All checks passed
```

**Result:** Path issue fixed, works in both local and CI

---

## Best Practices

### DO:
✅ **Gather information first** - Don't jump straight to coding  
✅ **Reproduce consistently** - Can't fix what you can't reproduce  
✅ **Make minimal changes** - Fix only what's broken  
✅ **Run full test suite** - Ensure no regressions  
✅ **Document the fix** - Help others understand  
✅ **Add regression tests** - Prevent same failure  
✅ **Share learnings** - Help team improve  
✅ **Fix flaky tests immediately** - Don't let them accumulate

### DON'T:
❌ **Guess at solutions** - Understand root cause first  
❌ **Skip reproduction** - "Works on my machine" isn't enough  
❌ **Make large changes** - Scope creep complicates debugging  
❌ **Only fix one test** - Related tests may have same issue  
❌ **Ignore flaky tests** - They indicate real problems  
❌ **Rush the fix** - Take time to understand fully  
❌ **Skip documentation** - Future you will thank current you  
❌ **Disable failing tests** - Fix them instead

---

## Related Workflows

**Prerequisites:**
- [Test Writing](../development/test_writing.md) - How to write good tests
- [CI/CD Workflow](../development/ci_cd_workflow.md) - Understanding CI pipeline
- [Debugging Techniques](../development/debugging_workflow.md) - General debugging skills

**Next Steps:**
- [Coverage Gap Analysis](./coverage_gap_analysis.md) - Improving test coverage
- [Ruff Error Resolution](./ruff_error_resolution.md) - Fixing linting errors
- [Code Review Checklist](./code_review_checklist.md) - Catching issues in review

**Related:**
- [Performance Regression Investigation](../testing/performance_regression_investigation.md) - Performance test failures
- [Rollback Procedure](../devops/rollback_procedure.md) - If fix needs reverting

---

## Tags
`quality-assurance` `testing` `debugging` `troubleshooting` `ci-cd` `test-automation` `best-practices`
