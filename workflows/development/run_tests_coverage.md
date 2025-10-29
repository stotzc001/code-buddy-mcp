# Run Tests with Coverage

**ID:** dev-019  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 5-15 minutes  
**Frequency:** Every code change  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Execute project test suite with code coverage tracking to identify which parts of the codebase are tested and which need additional test coverage.

**Why:** Code coverage metrics help ensure thorough testing, identify untested code paths, and maintain confidence in code changes. Coverage reports highlight gaps in test suites and track testing progress over time.

**When to use:**
- Before committing code changes
- During code review process
- In CI/CD pipelines
- When identifying areas needing more tests
- To track testing progress on new features
- Before production releases

---

## Prerequisites

**Required Knowledge:**
- [ ] Basic understanding of testing frameworks
- [ ] Familiarity with command line
- [ ] Understanding of code coverage concepts

**Required Tools:**
- [ ] Test framework installed (pytest, jest, unittest, etc.)
- [ ] Coverage tool installed (pytest-cov, coverage.py, istanbul, etc.)

**For Python:**
```bash
pip install pytest pytest-cov
```

**For JavaScript/TypeScript:**
```bash
npm install --save-dev jest @testing-library/react
# or
npm install --save-dev vitest @vitest/coverage-v8
```

**Check before starting:**
```bash
# Python
python -m pytest --version
python -m pytest --cov --version

# JavaScript/Node
npx jest --version
# or
npx vitest --version
```

---

## Implementation Steps

### Step 1: Run Tests with Basic Coverage

**What:** Execute tests with coverage tracking enabled

**How:**

**For Python with pytest:**
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term

# Run specific test file with coverage
pytest tests/test_auth.py --cov=src.auth --cov-report=term

# Run with verbose output
pytest --cov=src --cov-report=term -v

# Include missing lines in report
pytest --cov=src --cov-report=term-missing
```

**For JavaScript with Jest:**
```bash
# Run all tests with coverage
npm test -- --coverage

# Or if configured in package.json
npm run test:coverage

# Run specific test file
npm test -- auth.test.js --coverage
```

**For JavaScript with Vitest:**
```bash
# Run with coverage
npx vitest --coverage

# Or with npm script
npm run test:coverage
```

**Expected Output:**
```
---------- coverage: platform linux, python 3.11.0 -----------
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
src/__init__.py              0      0   100%
src/auth.py                 45      3    93%   23, 67-68
src/database.py             32      8    75%   12, 45-51
src/utils.py                15      0   100%
------------------------------------------------------
TOTAL                       92     11    88%
```

**Verification:**
- [ ] Tests execute successfully
- [ ] Coverage report displays
- [ ] Coverage percentage shown for each file

---

### Step 2: Generate HTML Coverage Report

**What:** Create an interactive HTML report for detailed coverage analysis

**How:**

**For Python:**
```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# View in browser (Linux/Mac)
open htmlcov/index.html
# Or (Windows)
start htmlcov/index.html
```

**For JavaScript (Jest):**
```bash
# Generate HTML report
npm test -- --coverage --coverageReporters=html

# View report
open coverage/index.html
```

**For JavaScript (Vitest):**
```bash
# Generate HTML report (default)
npx vitest --coverage

# View report
open coverage/index.html
```

**What to Look For in HTML Report:**
- **Green lines:** Covered by tests
- **Red lines:** Not covered by tests
- **Yellow lines:** Partially covered (e.g., branch not taken)
- File-by-file breakdown
- Line-by-line coverage visualization

**Verification:**
- [ ] HTML report generated in coverage directory
- [ ] Can view report in browser
- [ ] Can click through files to see coverage

---

### Step 3: Set Coverage Thresholds

**What:** Configure minimum coverage requirements to maintain code quality

**How:**

**For Python (pytest.ini or pyproject.toml):**

```ini
# pytest.ini
[tool:pytest]
addopts = 
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80"
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__init__.py"
]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = false
```

**For JavaScript (package.json):**

```json
{
  "jest": {
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    },
    "collectCoverageFrom": [
      "src/**/*.{js,jsx,ts,tsx}",
      "!src/**/*.test.{js,jsx,ts,tsx}",
      "!src/**/*.spec.{js,jsx,ts,tsx}",
      "!src/index.{js,ts}"
    ]
  }
}
```

**For Vitest (vitest.config.ts):**

```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      },
      exclude: [
        'node_modules/',
        'src/**/*.test.ts',
        'src/**/*.spec.ts'
      ]
    }
  }
})
```

**Verification:**
- [ ] Coverage thresholds configured
- [ ] Tests fail if coverage drops below threshold
- [ ] Threshold appropriate for project (typically 70-90%)

---

### Step 4: Exclude Files from Coverage

**What:** Exclude test files, generated code, and non-critical files from coverage metrics

**How:**

**For Python (.coveragerc or pyproject.toml):**

```ini
# .coveragerc
[run]
source = src
omit =
    */tests/*
    */test_*.py
    */__init__.py
    */migrations/*
    */settings/*
    **/config.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

**For JavaScript (Jest in package.json):**

```json
{
  "jest": {
    "coveragePathIgnorePatterns": [
      "/node_modules/",
      "/dist/",
      "/build/",
      "\\.test\\.(js|ts|tsx)$",
      "\\.spec\\.(js|ts|tsx)$",
      "/migrations/",
      "/fixtures/"
    ]
  }
}
```

**Verification:**
- [ ] Excluded files don't appear in coverage reports
- [ ] Coverage percentage reflects actual application code
- [ ] Test files are not counted in coverage

---

### Step 5: Integrate Coverage with CI/CD

**What:** Add coverage checks to automated pipeline

**How:**

**GitHub Actions (Python):**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -r requirements.txt
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=term --cov-report=xml --cov-fail-under=80
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

**GitHub Actions (JavaScript):**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests with coverage
        run: npm run test:coverage
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
```

**Verification:**
- [ ] CI runs tests with coverage
- [ ] Coverage reports uploaded (optional)
- [ ] Build fails if coverage below threshold

---

### Step 6: Review and Improve Coverage

**What:** Analyze coverage report and add tests for uncovered code

**How:**

1. **Open HTML coverage report:**
   ```bash
   open htmlcov/index.html
   # or
   open coverage/index.html
   ```

2. **Identify low coverage files:**
   - Look for files with <80% coverage
   - Focus on critical business logic first
   - Deprioritize configuration/boilerplate

3. **Click through to see uncovered lines:**
   - Red lines = not executed
   - Yellow = partial branch coverage
   - Review logic to understand why not covered

4. **Add tests for uncovered code:**
   ```python
   # If auth.py line 23 is uncovered (error path):
   def test_authentication_with_invalid_credentials():
       """Test that invalid credentials raise error."""
       with pytest.raises(AuthenticationError):
           authenticate_user("invalid", "wrong")
   ```

5. **Re-run coverage:**
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

6. **Verify improvement:**
   - Coverage should increase
   - Previously red lines now green

**Verification:**
- [ ] Critical paths have >90% coverage
- [ ] Error handling paths are tested
- [ ] Edge cases are covered
- [ ] Coverage trending upward over time

---

## Verification Checklist

After running tests with coverage:

- [ ] All tests pass
- [ ] Coverage report generated successfully
- [ ] Coverage percentage meets threshold (e.g., ≥80%)
- [ ] HTML report viewable and detailed
- [ ] Critical code paths have high coverage
- [ ] Uncovered lines identified and understood
- [ ] Configuration excludes irrelevant files
- [ ] CI/CD runs coverage checks (if applicable)

---

## Common Issues & Solutions

### Issue 1: Coverage Lower Than Expected

**Symptoms:**
```
Coverage: 45% (expected 80%+)
```

**Cause:**
- Missing tests for error paths
- Untested utility functions
- Dead code not removed

**Solution:**
```bash
# Identify specific uncovered lines
pytest --cov=src --cov-report=term-missing

# Focus on missing lines shown in report
# Example output:
# src/auth.py    67%    15-20, 45-50

# Add tests for those specific lines
# Then verify improvement
```

---

### Issue 2: Tests Pass but Coverage Fails

**Symptoms:**
```
FAILED: coverage threshold not met
Required: 80%, Actual: 75%
```

**Solution:**
```bash
# Option 1: Add more tests to increase coverage
pytest --cov=src --cov-report=html
# Review HTML report for gaps

# Option 2: Adjust threshold if unrealistic
# pyproject.toml
[tool.coverage.report]
fail_under = 75  # Reduced from 80

# Option 3: Exclude files that shouldn't count
[tool.coverage.run]
omit = [
    "*/migrations/*",
    "*/settings/*"
]
```

---

### Issue 3: Coverage Includes Test Files

**Symptoms:**
- Test files appear in coverage report
- Coverage artificially inflated

**Solution:**
```toml
# pyproject.toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/*_test.py"
]
```

```json
// package.json
{
  "jest": {
    "coveragePathIgnorePatterns": [
      "\\.test\\.(js|ts|tsx)$",
      "\\.spec\\.(js|ts|tsx)$"
    ]
  }
}
```

---

### Issue 4: Slow Test Execution with Coverage

**Symptoms:**
- Tests take much longer with coverage enabled

**Solution:**
```bash
# Run coverage only when needed (not every time)
# Normal development: fast tests without coverage
pytest

# Before commit: full coverage
pytest --cov=src --cov-report=term-missing

# Or use markers to skip slow tests
pytest -m "not slow" --cov=src
```

---

## Best Practices

### DO:
✅ Run coverage regularly (before commits, in CI)  
✅ Set realistic coverage thresholds (70-90%)  
✅ Focus on testing critical business logic  
✅ Review HTML reports to identify gaps  
✅ Exclude test files and generated code  
✅ Track coverage trends over time  
✅ Use coverage to guide testing efforts  
✅ Combine with other quality metrics

### DON'T:
❌ Aim for 100% coverage at all costs  
❌ Write tests just to increase percentage  
❌ Include test files in coverage metrics  
❌ Ignore consistently uncovered code  
❌ Set threshold too low (below 70%)  
❌ Skip coverage in CI/CD  
❌ Forget to test error/edge cases  
❌ Let coverage drop without investigation

---

## Examples

### Example 1: Python Project Basic Coverage

```bash
# Install coverage tools
$ pip install pytest pytest-cov

# Run tests with coverage
$ pytest --cov=src --cov-report=term-missing

---------- coverage: platform linux, python 3.11 -----------
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
src/__init__.py              0      0   100%
src/auth.py                 45      5    89%   23, 67-70
src/database.py             32      8    75%   12, 45-51
src/utils.py                15      0   100%
------------------------------------------------------
TOTAL                       92     13    86%

# Generate HTML report for details
$ pytest --cov=src --cov-report=html

# View report
$ open htmlcov/index.html
```

---

### Example 2: JavaScript Project with Jest

```bash
# Install Jest with coverage
$ npm install --save-dev jest @testing-library/react

# Add script to package.json
$ npm pkg set scripts.test:coverage="jest --coverage"

# Run tests with coverage
$ npm run test:coverage

PASS  src/auth.test.js
PASS  src/utils.test.js

--------------------|---------|----------|---------|---------|
File                | % Stmts | % Branch | % Funcs | % Lines |
--------------------|---------|----------|---------|---------|
All files           |   85.71 |    75.00 |   88.88 |   85.71 |
 auth.js            |   90.00 |    80.00 |  100.00 |   90.00 |
 utils.js           |   80.00 |    66.66 |   75.00 |   80.00 |
--------------------|---------|----------|---------|---------|

# Open HTML report
$ open coverage/index.html
```

---

### Example 3: Setting Up Coverage Threshold

```bash
# Add configuration to pyproject.toml
$ cat >> pyproject.toml << 'EOF'

[tool.pytest.ini_options]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80"
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py"
]

[tool.coverage.report]
fail_under = 80
show_missing = true
EOF

# Now pytest will fail if coverage drops below 80%
$ pytest
...
FAILED: coverage threshold not met (78% < 80%)
```

---

## Related Workflows

**Before This Workflow:**
- [[dev-002]](test_writing.md) - Write comprehensive tests first
- [[tes-004]](../testing/test_data_generation.md) - Generate test data

**After This Workflow:**
- [[qua-003]](../quality-assurance/coverage_gap_analysis.md) - Analyze coverage gaps
- [[qua-010]](../quality-assurance/test_failure_investigation.md) - Fix failing tests

**Complementary Workflows:**
- [[tes-001]](../testing/performance_regression_investigation.md) - Performance testing
- [[qua-001]](../quality-assurance/code_review_checklist.md) - Code review

---

## Tags

`testing` `coverage` `pytest` `jest` `quality-assurance` `ci-cd` `automation` `development`
