# Coverage Gap Analysis

**ID:** qua-003  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic process for identifying untested code, analyzing test coverage gaps, and prioritizing areas that need additional testing to improve overall code quality.

**Why:** Code coverage analysis helps identify risky, untested code paths before they cause production issues. Research shows that code with >80% test coverage has 40% fewer bugs than code with <50% coverage.

**When to use:**
- Before major releases or deployments
- When onboarding to legacy codebases
- After adding significant new features
- When test suite feels insufficient
- During code review process
- When improving code quality metrics

---

## Prerequisites

**Required:**
- [ ] Python project with test suite
- [ ] Coverage tool installed (coverage.py, pytest-cov)
- [ ] Access to codebase and test files
- [ ] Test runner configured

**Check before starting:**
```bash
# Verify coverage tool
pip show coverage pytest-cov

# Or install
pip install coverage pytest-cov

# Check tests run
pytest

# Verify coverage works
pytest --cov=src --cov-report=term
```

---

## Implementation Steps

### Step 1: Generate Baseline Coverage Report

**What:** Run the test suite with coverage enabled to establish current coverage baseline.

**How:**

```bash
# Basic coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Example output:
# Name                      Stmts   Miss  Cover   Missing
# -------------------------------------------------------
# src/app.py                   45      8    82%   23-25, 67-70
# src/auth.py                  67     34    49%   12-45, 89-102
# src/database.py              23      0   100%
# TOTAL                       224     87    61%
```

**Configure coverage:**
```ini
# .coveragerc
[run]
source = src
omit =
    */tests/*
    */migrations/*

[report]
precision = 2
show_missing = True
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    if TYPE_CHECKING:
```

**Verification:**
- [ ] Coverage report generated
- [ ] Overall coverage percentage identified
- [ ] Low-coverage modules identified

**If This Fails:**
→ Install coverage: `pip install pytest-cov`
→ Fix failing tests before coverage analysis

---

### Step 2: Identify Critical Uncovered Code

**What:** Prioritize coverage gaps by identifying which untested code is most critical.

**How:**

```markdown
## Criticality Levels:

🔴 **Critical:**
- Authentication/authorization
- Payment processing
- Data validation
- Security operations
- Core business logic

🟡 **High Priority:**
- Complex algorithms
- Data transformations
- Integration points
- Background jobs

🟢 **Medium Priority:**
- Utility functions
- Formatting logic
- Helper functions

⚪ **Low Priority:**
- Debug code
- Simple constants
```

**Analyze specific gaps:**
```bash
# View specific file coverage
coverage report src/auth.py

# View detailed missing lines
coverage annotate src/auth.py
cat src/auth.py,cover
```

**Verification:**
- [ ] Critical uncovered code identified
- [ ] Coverage gaps categorized by priority
- [ ] High-risk areas documented

**If This Fails:**
→ Consult with domain experts about criticality
→ Focus on top 10 most critical areas

---

### Step 3: Analyze Why Code Is Uncovered

**What:** Understand reasons behind coverage gaps.

**How:**

**Common reasons:**

1. **Genuinely untested:**
```python
def new_feature(data):
    # New code, no tests yet
    return process(data)
```

2. **Dead code:**
```bash
# Check if code is used
grep -r "function_name" src/
```

3. **External dependencies not mocked:**
```python
@patch('external.api')
def test_with_mock(mock_api):
    # Now testable
    pass
```

4. **Complex test setup:**
```python
# Use factories/fixtures
@pytest.fixture
def test_user():
    return UserFactory.create()
```

**Verification:**
- [ ] Reasons for gaps documented
- [ ] Dead code identified
- [ ] Mock requirements noted

---

### Step 4: Create Action Plan

**What:** Develop concrete plan for addressing gaps.

**How:**

```markdown
# Coverage Improvement Plan

## Sprint 1 - Critical

### 🔴 Authentication (49% → 90%)
**Effort:** 4 hours
**Tests Needed:**
- [ ] test_verify_password
- [ ] test_create_session
- [ ] test_session_expiration
**Owner:** @alice
**Due:** Friday

### 🔴 Payments (35% → 95%)
**Effort:** 6 hours
**Tests Needed:**
- [ ] test_process_refund
- [ ] test_payment_failure
**Owner:** @bob
**Due:** Friday

## Backlog - Medium/Low
- Utility functions (4 hours)
- Dead code removal (2 hours)
```

**Verification:**
- [ ] Action plan created with priorities
- [ ] Owners assigned
- [ ] Effort estimated

---

### Step 5: Implement Tests

**What:** Write tests to cover identified gaps.

**How:**

```python
# tests/test_auth.py

def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "SecurePassword123!"
    hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    assert verify_password(password, hash.decode())

def test_verify_password_incorrect():
    """Test password verification with wrong password."""
    password = "SecurePassword123!"
    wrong = "WrongPassword!"
    hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    assert not verify_password(wrong, hash.decode())

def test_session_expiration():
    """Test session expires after timeout."""
    user = create_test_user()
    token = create_session(user.id, expires_in=1)
    
    assert get_session(token) is not None
    time.sleep(2)
    assert get_session(token) is None
```

**Verify improvement:**
```bash
pytest --cov=src/auth --cov-report=term
# Before: 49%
# After: 93% ✅
```

**Verification:**
- [ ] Tests written for critical gaps
- [ ] Tests pass
- [ ] Coverage improved

---

### Step 6: Monitor Coverage

**What:** Establish ongoing coverage monitoring.

**How:**

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest --cov=src \
           --cov-report=xml \
           --cov-fail-under=80

- name: Upload to Codecov
  uses: codecov/codecov-action@v3
```

**Set requirements:**
```ini
# pytest.ini
[pytest]
addopts = --cov=src --cov-fail-under=80
```

**Verification:**
- [ ] CI/CD coverage checks configured
- [ ] Coverage requirements enforced
- [ ] Team aware of standards

---

## Verification Checklist

- [ ] Baseline coverage report generated
- [ ] Critical gaps identified
- [ ] Root causes analyzed  
- [ ] Action plan created
- [ ] Tests written
- [ ] Coverage improved
- [ ] Monitoring configured

---

## Common Issues & Solutions

### Issue: High Coverage But Still Bugs

**Symptoms:**
- 80%+ coverage but bugs occur
- Coverage feels meaningless

**Solution:**
```python
# Focus on test quality, not just coverage

# ❌ Bad: Tests execution, not behavior
def test_divide():
    result = divide(10, 2)
    assert result  # Just checks it returns something

# ✅ Good: Tests actual behavior
def test_divide_positive():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

**Prevention:**
- Review tests for quality
- Use mutation testing
- Require meaningful assertions

---

### Issue: Can't Reach Target Coverage

**Solution:**
```markdown
1. Analyze what's not covered
2. Adjust targets realistically
3. Use `# pragma: no cover` for defensive code
4. Focus on branch coverage
```

---

## Examples

### Example 1: Auth Module Improvement

**Context:** Auth at 49%, needs 90% before audit

**Execution:**
```bash
# Generate report
pytest --cov=src/auth --cov-report=html

# Write missing tests
# test_verify_password_*
# test_create_session_*

# Verify
pytest --cov=src/auth
# Result: 93% ✅
```

---

## Best Practices

### DO:
✅ **Focus on critical code first**
✅ **Write meaningful tests**
✅ **Delete dead code**
✅ **Automate coverage checks**
✅ **Track trends over time**

### DON'T:
❌ **Chase 100% coverage**
❌ **Write tests just for coverage**
❌ **Ignore test quality**
❌ **Skip edge cases**

---

## Related Workflows

**Prerequisites:**
- [Test Writing](../development/test_writing.md)
- [CI/CD Workflow](../development/ci_cd_workflow.md)

**Next Steps:**
- [Quality Gate Execution](./quality_gate_execution.md)
- [Code Review Checklist](./code_review_checklist.md)

---

## Tags
`quality-assurance` `testing` `code-coverage` `metrics` `best-practices`
