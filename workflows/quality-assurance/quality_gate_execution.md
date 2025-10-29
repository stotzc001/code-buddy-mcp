# Quality Gate Execution

**ID:** qua-008  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 20-40 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Automated quality checks that must pass before code can be merged or deployed, acting as gatekeepers to prevent low-quality code from reaching production.

**Why:** Quality gates catch issues early when they're cheapest to fix. They enforce standards consistently across teams, reducing technical debt and production bugs by up to 60%. Without quality gates, teams spend 30-40% of time fixing preventable issues that slip into production.

**When to use:**
- Before merging pull requests
- Before deploying to staging/production
- During CI/CD pipeline
- After dependency updates
- For release candidates
- During code review process

---

## Prerequisites

**Required:**
- [ ] CI/CD pipeline configured
- [ ] Quality tools installed (ruff, mypy, pytest, etc.)
- [ ] Project quality standards defined
- [ ] Access to repository settings

**Check before starting:**
```bash
# Verify tools installed
pip show ruff mypy pytest pytest-cov bandit safety

# Or install
pip install ruff mypy pytest pytest-cov bandit safety

# Check CI/CD configuration
cat .github/workflows/test.yml

# Verify quality config files
ls -la .ruff.toml mypy.ini pytest.ini
```

---

## Implementation Steps

### Step 1: Define Quality Gate Criteria

**What:** Establish clear, measurable quality standards that code must meet.

**How:**

**Define quality metrics:**
```markdown
# quality-standards.md

## Mandatory Quality Gates (Must Pass)

### 🔴 Build & Tests
- ✅ Build succeeds
- ✅ All tests pass
- ✅ No test failures

### 🔴 Code Coverage
- ✅ Overall coverage ≥ 80%
- ✅ New code coverage ≥ 90%
- ✅ No coverage decrease

### 🔴 Linting
- ✅ Ruff checks pass (0 errors)
- ✅ No critical issues

### 🔴 Type Checking
- ✅ Mypy passes in strict mode
- ✅ No type errors

### 🔴 Security
- ✅ No high/critical vulnerabilities (bandit)
- ✅ No vulnerable dependencies (safety)
- ✅ No secrets in code

## Optional Quality Gates (Warnings)

### 🟡 Code Quality
- ⚠️ Cyclomatic complexity < 10
- ⚠️ Function length < 50 lines
- ⚠️ No code smells (pylint)

### 🟡 Documentation
- ⚠️ Public functions have docstrings
- ⚠️ README updated for features
```

**Configuration files:**
```toml
# pyproject.toml

[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "--cov-fail-under=80",
    "--strict-markers",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = false

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "UP"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Verification:**
- [ ] Quality standards documented
- [ ] Thresholds defined
- [ ] Configuration files created
- [ ] Team agreed on standards

**If This Fails:**
→ Start with industry standards (80% coverage, 0 linting errors)
→ Adjust based on team maturity
→ Gradually increase strictness

---

### Step 2: Implement Automated Checks

**What:** Set up automated tools to run quality checks consistently.

**How:**

**Create quality check script:**
```bash
#!/bin/bash
# scripts/quality-gate.sh

set -e  # Exit on any error

echo "🚀 Running Quality Gates..."

# Build check
echo "📦 Checking build..."
python -m compileall src/

# Tests
echo "🧪 Running tests..."
pytest --cov=src \
       --cov-report=term-missing \
       --cov-report=xml \
       --cov-fail-under=80 \
       --junit-xml=test-results.xml

# Linting
echo "🔍 Running linter..."
ruff check src/ tests/

# Type checking
echo "📝 Type checking..."
mypy src/

# Security checks
echo "🔐 Security scan..."
bandit -r src/ -f json -o bandit-report.json
safety check --json

echo "✅ All quality gates passed!"
```

**Make script executable:**
```bash
chmod +x scripts/quality-gate.sh

# Test locally
./scripts/quality-gate.sh
```

**CI/CD integration:**
```yaml
# .github/workflows/quality-gates.yml

name: Quality Gates

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run Quality Gates
        run: |
          ./scripts/quality-gate.sh
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results.xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
      
      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const coverage = fs.readFileSync('coverage.xml', 'utf8');
            // Parse and comment on PR
```

**Pre-commit hooks:**
```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: Ruff Linter
        entry: ruff check
        language: system
        types: [python]
        pass_filenames: false
      
      - id: mypy
        name: Type Check (mypy)
        entry: mypy
        language: system
        types: [python]
        pass_filenames: false
      
      - id: tests
        name: Run Tests
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

**Verification:**
- [ ] Quality check script created
- [ ] CI/CD pipeline configured
- [ ] Pre-commit hooks installed
- [ ] All checks passing locally

**If This Fails:**
→ Test each check individually
→ Fix issues before combining
→ Start with subset of checks, add more gradually

---

### Step 3: Configure Quality Gate Enforcement

**What:** Enforce quality gates so that code cannot be merged/deployed without passing.

**How:**

**GitHub branch protection:**
```bash
# Via GitHub UI:
# Settings → Branches → Add rule

# Or via API/CLI:
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=quality-gates \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field enforce_admins=true

# Branch protection rules:
# ✅ Require status checks before merging
#    - quality-gates (CI check)
#    - coverage/codecov
# ✅ Require pull request reviews
# ✅ Require branches to be up to date
# ✅ Include administrators
```

**GitLab merge request rules:**
```yaml
# .gitlab-ci.yml

quality_gate:
  stage: test
  script:
    - ./scripts/quality-gate.sh
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  only:
    - merge_requests

# In GitLab UI:
# Settings → Merge Requests → Merge checks
# ✅ Pipelines must succeed
# ✅ All threads must be resolved
```

**SonarQube integration:**
```yaml
# .github/workflows/sonarqube.yml

- name: SonarQube Scan
  uses: sonarsource/sonarqube-scan-action@master
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

- name: SonarQube Quality Gate
  uses: sonarsource/sonarqube-quality-gate-action@master
  timeout-minutes: 5
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**Deployment gates:**
```yaml
# .github/workflows/deploy.yml

deploy-production:
  needs: [quality-gates, integration-tests]
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  
  environment:
    name: production
    url: https://app.example.com
  
  steps:
    - name: Verify Quality Gates
      run: |
        # Check all gates passed
        if [[ "${{ needs.quality-gates.result }}" != "success" ]]; then
          echo "Quality gates failed!"
          exit 1
        fi
    
    - name: Deploy
      run: |
        ./scripts/deploy.sh production
```

**Verification:**
- [ ] Branch protection enabled
- [ ] Status checks required
- [ ] Cannot merge without passing
- [ ] Deployment gates configured

**If This Fails:**
→ Test by attempting to merge failing PR
→ Verify administrators also blocked
→ Check CI/CD status integration

---

### Step 4: Monitor Quality Metrics

**What:** Track quality metrics over time to identify trends.

**How:**

**Set up dashboards:**
```python
# scripts/quality-metrics.py

import json
from datetime import datetime
from typing import Dict

def collect_metrics() -> Dict:
    """Collect quality metrics."""
    
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'build': {
            'status': 'passing',
            'duration': 45  # seconds
        },
        'tests': {
            'total': 234,
            'passed': 234,
            'failed': 0,
            'skipped': 0,
            'duration': 12  # seconds
        },
        'coverage': {
            'total': 85.2,
            'files': {
                'src/auth.py': 93.0,
                'src/api.py': 78.5,
                # ...
            }
        },
        'linting': {
            'errors': 0,
            'warnings': 3
        },
        'type_coverage': 95.0,
        'security': {
            'vulnerabilities': {
                'critical': 0,
                'high': 0,
                'medium': 2,
                'low': 5
            }
        }
    }
    
    return metrics

def save_metrics(metrics: Dict):
    """Save metrics to history."""
    
    try:
        with open('metrics-history.json', 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    
    history.append(metrics)
    
    with open('metrics-history.json', 'w') as f:
        json.dump(history, f, indent=2)

# Run after quality gates
metrics = collect_metrics()
save_metrics(metrics)
```

**Generate reports:**
```python
# scripts/quality-report.py

import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_trend_report():
    """Generate quality trend report."""
    
    with open('metrics-history.json') as f:
        history = json.load(f)
    
    # Last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    recent = [
        m for m in history
        if datetime.fromisoformat(m['timestamp']) > cutoff
    ]
    
    # Extract metrics
    dates = [datetime.fromisoformat(m['timestamp']) for m in recent]
    coverage = [m['coverage']['total'] for m in recent]
    test_count = [m['tests']['total'] for m in recent]
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.plot(dates, coverage, marker='o')
    ax1.axhline(y=80, color='r', linestyle='--', label='Target')
    ax1.set_ylabel('Coverage %')
    ax1.set_title('Test Coverage Trend')
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(dates, test_count, marker='o', color='green')
    ax2.set_ylabel('Test Count')
    ax2.set_title('Test Suite Growth')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('quality-trend.png')
    print("Report saved to quality-trend.png")

generate_trend_report()
```

**Set up alerts:**
```yaml
# .github/workflows/quality-alerts.yml

- name: Check Quality Degradation
  run: |
    python scripts/check-quality-degradation.py
    
# scripts/check-quality-degradation.py:
# - Compare current metrics to last run
# - Alert if coverage drops > 5%
# - Alert if test failures increase
# - Alert if new security vulnerabilities
```

**Verification:**
- [ ] Metrics collection automated
- [ ] Dashboards available
- [ ] Trend reports generated
- [ ] Alerts configured

---

### Step 5: Handle Quality Gate Failures

**What:** Establish clear process for when quality gates fail.

**How:**

**Failure response workflow:**
```markdown
# When Quality Gate Fails:

## 1. Identify the failure
```bash
# Check CI logs
gh run view <run-id> --log

# Local reproduction
./scripts/quality-gate.sh
```

## 2. Categorize the issue
- 🔴 Test failures → Fix immediately
- 🔴 Coverage drop → Add tests
- 🔴 Linting errors → Run ruff --fix
- 🔴 Type errors → Add type hints
- 🔴 Security issues → Fix immediately

## 3. Fix the issue
- Don't disable checks
- Don't lower thresholds
- Fix the root cause

## 4. Verify fix
```bash
# Run checks locally
./scripts/quality-gate.sh

# Push and verify CI
git push
gh pr checks
```

## 5. Document if needed
- Complex fixes → Add comments
- New patterns → Update guide
```

**Common fixes:**
```bash
# Test failures
pytest -vv --lf  # Run last failed tests
pytest --pdb  # Debug failures

# Coverage drops
pytest --cov=src --cov-report=html
# Identify gaps, add tests

# Linting errors
ruff check --fix src/

# Type errors
mypy src/
# Add type hints or use # type: ignore with justification

# Security issues
safety check  # Update dependencies
bandit -r src/  # Fix security issues
```

**Exemption process:**
```markdown
# When exemption is genuinely needed:

1. Document why quality gate cannot be met
2. Get approval from tech lead
3. Create issue for follow-up
4. Set reminder to fix
5. Merge with explicit override

Example:
```yaml
# .github/workflows/override.yml
if: contains(github.event.pull_request.labels.*.name, 'quality-gate-override')
  continue-on-error: true
```

Verification:
- [ ] Failure workflow documented
- [ ] Team trained on fixes
- [ ] Exemption process defined

---

### Step 6: Continuous Improvement

**What:** Regularly review and improve quality gates.

**How:**

**Monthly review:**
```markdown
## Quality Gate Review Meeting

### Metrics Review
- Overall pass rate
- Common failure reasons
- Time to fix failures
- False positive rate

### Adjustments Needed?
- Thresholds too strict/lenient?
- Missing checks?
- Unnecessary checks?
- Tool configuration issues?

### Action Items
- Update configurations
- Add new checks
- Remove problematic checks
- Train team on gaps
```

**Gradual strictness increase:**
```python
# Example: Increasing coverage requirement

# Month 1: 70% (current baseline)
# Month 2: 75% (achievable)
# Month 3: 80% (target)

# Update pyproject.toml monthly:
[tool.coverage.report]
fail_under = 75  # Increment monthly
```

**Verification:**
- [ ] Regular reviews scheduled
- [ ] Improvement process defined
- [ ] Team feedback collected

---

## Verification Checklist

- [ ] Quality criteria defined
- [ ] Automated checks implemented
- [ ] CI/CD enforcement configured
- [ ] Metrics monitored
- [ ] Failure process documented
- [ ] Continuous improvement plan

---

## Common Issues & Solutions

### Issue: Quality Gates Too Slow

**Symptoms:**
- CI takes > 10 minutes
- Developers bypass locally

**Solution:**
```bash
# Parallelize checks
pytest -n auto  # Parallel tests
ruff check & mypy src/ & wait  # Parallel linting

# Cache dependencies
# In CI, cache pip packages
```

---

### Issue: False Positives

**Symptoms:**
- Valid code flagged
- Team frustrated

**Solution:**
```python
# Configure tools to reduce noise
# Use # type: ignore, # noqa with justification
# Adjust tool configuration
```

---

## Examples

### Example 1: Adding Quality Gates

**Context:** New project needs quality gates

**Execution:**
```bash
# 1. Define standards
echo "Coverage: 80%, Linting: 0 errors" > quality-standards.md

# 2. Create script
./scripts/quality-gate.sh

# 3. Add to CI
# .github/workflows/quality-gates.yml

# 4. Enable branch protection
gh api repos/:owner/:repo/branches/main/protection

# 5. Test
git push
gh pr checks
```

---

## Best Practices

### DO:
✅ **Start with basics** - Build, tests, linting
✅ **Enforce consistently** - No exceptions
✅ **Fail fast** - Run quick checks first
✅ **Provide clear feedback** - Show what failed

### DON'T:
❌ **Make gates too slow** - Keep under 5 minutes
❌ **Allow bypasses** - Enforce for all
❌ **Ignore failures** - Fix immediately
❌ **Set unrealistic standards** - Be pragmatic

---

## Related Workflows

**Prerequisites:**
- [CI/CD Workflow](../development/ci_cd_workflow.md)
- [Test Writing](../development/test_writing.md)

**Next Steps:**
- [Code Review Checklist](./code_review_checklist.md)
- [Coverage Gap Analysis](./coverage_gap_analysis.md)

---

## Tags
`quality-assurance` `ci-cd` `automation` `quality-gates` `testing` `best-practices`
