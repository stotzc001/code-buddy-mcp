---
id: dev-006
title: Dependency Upgrade
category: Development
subcategory: Maintenance
tags:
  - dependencies
  - maintenance
  - security
  - updates
  - pip
  - requirements
prerequisites:
  - dev-003  # Environment Initialization
related_workflows:
  - dev-007  # Dependency Update Strategy
  - qa-002   # Test Failure Investigation
  - dev-002  # Test Writing
complexity: intermediate
estimated_time: 30-60 minutes
last_updated: 2025-10-25
---

# Dependency Upgrade

## Overview

**What:** Systematic process for safely upgrading Python dependencies, testing for compatibility issues, and updating documentation to keep projects secure and current.

**Why:** Regular dependency upgrades are critical for security patches, bug fixes, performance improvements, and access to new features. Outdated dependencies increase technical debt and security vulnerabilities.

**When to use:**
- Monthly/quarterly scheduled maintenance
- After security vulnerability announcements
- When needing new features from updated packages
- Before major releases
- When encountering bugs fixed in newer versions
- As part of technical debt reduction

---

## Prerequisites

**Required:**
- [ ] Virtual environment set up and activated
- [ ] Working test suite (at least basic tests)
- [ ] Git repository with clean working tree
- [ ] requirements.txt or pyproject.toml
- [ ] Access to CI/CD pipeline (recommended)

**Required Tools:**
- [ ] pip or poetry installed
- [ ] pip-tools (recommended): `pip install pip-tools`
- [ ] pytest for testing

**Check before starting:**
```bash
# Ensure virtual environment is active
which python  # Should point to venv

# Check current dependency versions
pip list

# Verify clean git state
git status  # Should show no uncommitted changes

# Backup current requirements
cp requirements.txt requirements.txt.backup

# Ensure tests pass before upgrade
pytest
```

---

## Implementation Steps

### Step 1: Audit Current Dependencies

**What:** Review current dependency versions, identify outdated packages, and check for security vulnerabilities.

**How:** Use pip and security tools to assess the current state.

**Check outdated packages:**
```bash
# List outdated packages
pip list --outdated

# More detailed output
pip list --outdated --format=columns

# Save to file for reference
pip list --outdated > outdated_packages.txt

# Check for specific package version
pip show package-name
```

**Check for security vulnerabilities:**
```bash
# Install safety (security checker)
pip install safety

# Check for known vulnerabilities
safety check

# Generate detailed report
safety check --json > security_report.json

# Check specific requirements file
safety check -r requirements.txt
```

**Analyze dependency tree:**
```bash
# Install pipdeptree
pip install pipdeptree

# View dependency tree
pipdeptree

# Show only top-level dependencies
pipdeptree --packages $(pip freeze | grep -v "^\-e" | cut -d= -f1 | tr '\n' ',')

# Find what depends on a specific package
pipdeptree --reverse --packages requests

# Check for conflicts
pipdeptree --warn conflict
```

**Example output analysis:**
```bash
# Sample outdated packages
Package    Version  Latest   Type
---------- -------- -------- -----
requests   2.28.0   2.31.0   wheel
flask      2.2.0    3.0.0    wheel  # Major version - be careful!
pytest     7.2.0    7.4.3    wheel

# Sample safety check
╒══════════════════════════════════════════════════════════╕
│                                                          │
│                       /$$$$$$            /$$             │
│                      /$$__  $$          | $$             │
│           /$$$$$$$ /$$$$$$| $$  /$$$$$$ /$$$$$$   /$$   │
│          /$$_____/|____  $| $$ /$$__  $|_  $$_/  | $$   │
│         |  $$$$$$  /$$$$$$| $$| $$  \__/ | $$    | $$   │
│          \____  $$/$$__  $| $$| $$       | $$ /$|  $$   │
│          /$$$$$$$/$$$$$$| $$| $$       |  $$$$/ \  $$   │
│         |_______/|_______/|__/|__/        \___/   \__/   │
│                                                          │
╘══════════════════════════════════════════════════════════╛

 VULNERABILITIES FOUND: 2

╒═══════════╤═════════════════════════════════════════════════╕
│ Package   │ requests                                        │
├───────────┼─────────────────────────────────────────────────┤
│ Installed │ 2.28.0                                          │
├───────────┼─────────────────────────────────────────────────┤
│ Affected  │ <2.31.0                                         │
├───────────┼─────────────────────────────────────────────────┤
│ ID        │ 51668                                           │
╘═══════════╧═════════════════════════════════════════════════╛
```

**Categorize updates:**
```bash
# Create upgrade plan document
cat > UPGRADE_PLAN.md << 'EOF'
# Dependency Upgrade Plan

## Critical Security Updates (Do First)
- requests: 2.28.0 → 2.31.0 (CVE fix)
- cryptography: 38.0.0 → 41.0.5 (security patch)

## Major Version Updates (Test Carefully)
- flask: 2.2.0 → 3.0.0 (breaking changes expected)
- sqlalchemy: 1.4.40 → 2.0.0 (major API changes)

## Minor/Patch Updates (Lower Risk)
- pytest: 7.2.0 → 7.4.3
- black: 23.7.0 → 23.11.0
- pydantic: 2.4.0 → 2.5.0

## Dependencies to Keep (Pinned)
- numpy: 1.24.0 (required by other packages)
EOF
```

**Verification:**
- [ ] Outdated packages identified
- [ ] Security vulnerabilities documented
- [ ] Dependency tree analyzed
- [ ] Upgrade plan created with priorities
- [ ] Major version changes flagged for careful testing

**If This Fails:**
→ **pip list --outdated hangs**: May be network issue, try with `--timeout=15`
→ **safety check fails**: Install with `pip install safety --break-system-packages`
→ **pipdeptree errors**: Ensure virtual environment is activated

---

### Step 2: Upgrade Dependencies Incrementally

**What:** Upgrade packages one at a time or in small groups, starting with critical security updates.

**How:** Use systematic approach to upgrade, test, and commit changes.

**Upgrade strategy: One at a time (safest)**
```bash
# Start with critical security fixes
pip install --upgrade requests==2.31.0

# Run tests immediately
pytest

# If tests pass, update requirements
pip freeze | grep requests >> requirements.txt.new

# If tests fail, investigate before moving on
```

**Upgrade strategy: By category (faster)**
```bash
# Create separate requirements files by priority
cat > requirements-security.txt << 'EOF'
requests>=2.31.0
cryptography>=41.0.5
EOF

cat > requirements-minor.txt << 'EOF'
pytest>=7.4.0
black>=23.11.0
EOF

# Upgrade security packages first
pip install -r requirements-security.txt --upgrade

# Test
pytest

# Then minor updates
pip install -r requirements-minor.txt --upgrade

# Test again
pytest
```

**Using pip-compile (recommended for complex projects):**
```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in with loose constraints
cat > requirements.in << 'EOF'
# Core dependencies with minimum versions
flask>=2.2.0,<4.0.0
requests>=2.28.0
sqlalchemy>=1.4.0,<3.0.0
pydantic>=2.0.0

# Let pip-compile find latest compatible versions
EOF

# Compile to requirements.txt
pip-compile requirements.in

# Install compiled requirements
pip-sync requirements.txt

# Upgrade all to latest compatible versions
pip-compile --upgrade requirements.in

# Or upgrade specific package
pip-compile --upgrade-package requests requirements.in
```

**Handle major version upgrades separately:**
```bash
# For major version changes (e.g., Flask 2→3)
# 1. Read changelog
curl -s https://flask.palletsprojects.com/en/3.0.x/changes/ | grep "Version 3.0"

# 2. Check migration guide
# Visit documentation for migration guides

# 3. Create feature branch
git checkout -b upgrade/flask-3.0

# 4. Upgrade
pip install flask==3.0.0

# 5. Run tests and fix breaking changes
pytest -v

# 6. Update code for breaking changes
# (See migration guide)

# 7. Commit with detailed message
git add requirements.txt
git commit -m "chore: upgrade Flask 2.2→3.0

Breaking changes:
- Updated import paths for blueprints
- Changed session interface API
- Updated error handler registration

Fixes #123"
```

**Testing each upgrade:**
```bash
# After each upgrade, run full test suite
pytest -v

# Check for deprecation warnings
pytest -W default

# Run specific integration tests
pytest tests/integration/

# Check import errors
python -c "from myapp import create_app; create_app()"

# Run application smoke test
./scripts/smoke_test.sh
```

**Verification:**
- [ ] Security updates applied and tested
- [ ] Minor/patch updates applied and tested
- [ ] Major version updates handled separately
- [ ] All tests pass after each upgrade
- [ ] No new deprecation warnings (or documented)

**If This Fails:**
→ **Tests fail**: Rollback (`pip install package==old_version`), investigate, fix code
→ **Import errors**: Check for breaking API changes in changelog
→ **Dependency conflicts**: Use `pip-compile` to resolve or pin conflicting packages

---

### Step 3: Update Requirements Files

**What:** Update all dependency specification files to reflect new versions.

**How:** Update requirements.txt, requirements-dev.txt, and pyproject.toml with new versions.

**Update requirements.txt:**
```bash
# Freeze current environment
pip freeze > requirements.txt

# Or use pip-compile
pip-compile requirements.in

# Clean up unnecessary packages
# Remove packages that are sub-dependencies
# Keep only direct dependencies

# Better: Use separate files for clarity
pip freeze | grep -E "^(flask|requests|sqlalchemy)" > requirements.txt

# Or manually update with specific versions
cat > requirements.txt << 'EOF'
# Core web framework
flask==3.0.0
werkzeug==3.0.0

# HTTP client
requests==2.31.0

# Database
sqlalchemy==2.0.23
psycopg[binary]==3.1.18

# Configuration
python-dotenv==1.0.0
pydantic==2.5.0
EOF
```

**Update requirements-dev.txt:**
```bash
cat > requirements-dev.txt << 'EOF'
-r requirements.txt

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-asyncio==0.21.1

# Code quality
black==23.11.0
ruff==0.1.6
mypy==1.7.0

# Development
pre-commit==3.5.0
ipython==8.17.2
EOF
```

**Update pyproject.toml:**
```toml
# Update [project] dependencies
[project]
dependencies = [
    "flask>=3.0.0,<4.0.0",
    "requests>=2.31.0",
    "sqlalchemy>=2.0.0,<3.0.0",
    "pydantic>=2.5.0,<3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "black>=23.11.0",
    "ruff>=0.1.6",
    "mypy>=1.7.0",
]
```

**Document changes:**
```bash
# Create CHANGELOG entry
cat >> CHANGELOG.md << 'EOF'
## [Unreleased]

### Changed
- Updated Flask from 2.2.0 to 3.0.0
- Updated requests from 2.28.0 to 2.31.0 (security fix)
- Updated pytest from 7.2.0 to 7.4.3
- Updated black from 23.7.0 to 23.11.0

### Fixed
- Security vulnerability in requests (CVE-2023-XXXXX)

### Breaking Changes
- Flask 3.0 changes session interface - see migration guide
EOF

# Update README if needed
# Add notes about minimum versions
cat >> README.md << 'EOF'

## Requirements

- Python 3.10+
- Flask 3.0+
- PostgreSQL 14+
EOF
```

**Verification:**
- [ ] requirements.txt updated with exact versions
- [ ] requirements-dev.txt includes all dev tools
- [ ] pyproject.toml updated (if applicable)
- [ ] CHANGELOG.md documents changes
- [ ] README.md updated if requirements changed
- [ ] Can install from updated requirements: `pip install -r requirements.txt`

**If This Fails:**
→ **pip install fails**: Check for typos in package names or version numbers
→ **Dependency conflicts**: Adjust version constraints to compatible ranges

---

### Step 4: Test Thoroughly

**What:** Run comprehensive tests to ensure upgrades don't break functionality.

**How:** Execute full test suite, integration tests, and manual testing.

**Run test suite:**
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run tests multiple times to catch flaky tests
pytest --count=5

# Run with different Python versions (if using tox)
tox

# Check for deprecation warnings
pytest -W default::DeprecationWarning

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
pytest tests/unit/  # Only unit tests
```

**Test with different configurations:**
```bash
# Test with different environment variables
DEBUG=True pytest
DEBUG=False pytest

# Test database migrations
flask db downgrade base
flask db upgrade
pytest tests/integration/test_database.py

# Test API endpoints
python tests/smoke_test_api.py
```

**Manual testing checklist:**
```bash
# Create manual testing checklist
cat > MANUAL_TEST_CHECKLIST.md << 'EOF'
# Manual Testing After Dependency Upgrade

## Core Functionality
- [ ] Application starts without errors
- [ ] Homepage loads
- [ ] User authentication works
- [ ] Database queries execute
- [ ] API endpoints respond correctly

## Critical Features
- [ ] Payment processing (if applicable)
- [ ] File uploads
- [ ] Email sending
- [ ] Background jobs

## Edge Cases
- [ ] Error handling works
- [ ] Rate limiting functions
- [ ] Session management

## Performance
- [ ] Response times acceptable
- [ ] Database query performance
- [ ] Memory usage normal
EOF
```

**Check for issues:**
```bash
# Look for common problems after upgrades

# 1. Import errors
python -c "from myapp import create_app; app = create_app()"

# 2. Deprecation warnings
python -W default -m pytest

# 3. Type errors (if using mypy)
mypy src/

# 4. Linting errors
ruff check src/

# 5. Startup errors
python -m myapp.main &
PID=$!
sleep 5
kill $PID

# 6. Memory leaks (basic check)
python -c "
import tracemalloc
tracemalloc.start()
from myapp import create_app
app = create_app()
# Do some operations
current, peak = tracemalloc.get_traced_memory()
print(f'Current: {current / 1024 / 1024:.1f} MB; Peak: {peak / 1024 / 1024:.1f} MB')
tracemalloc.stop()
"
```

**Performance testing:**
```bash
# Benchmark critical operations
python -m pytest tests/performance/ --benchmark-only

# Or use timeit for specific functions
python -m timeit -s "from myapp import slow_function" "slow_function()"

# Load testing (if applicable)
locust -f tests/load_test.py --headless -u 100 -r 10 --run-time 1m
```

**Verification:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] No new deprecation warnings
- [ ] Manual testing completed
- [ ] Performance is acceptable
- [ ] No memory leaks detected
- [ ] Application starts and runs correctly

**If This Fails:**
→ **Tests fail**: Review test output, check if due to breaking changes in upgraded packages
→ **Performance regression**: Profile code to identify bottlenecks, consider rolling back specific packages
→ **Memory leaks**: Check for unclosed connections, improper caching

---

### Step 5: Update Documentation

**What:** Update all documentation to reflect dependency changes and any code modifications.

**How:** Update README, CHANGELOG, migration guides, and inline comments.

**Update CHANGELOG.md:**
```markdown
# Changelog

## [1.2.0] - 2025-10-25

### Changed
- **BREAKING**: Upgraded Flask from 2.2.0 to 3.0.0
  - Updated session interface usage
  - Changed blueprint registration
  - See [Flask 3.0 migration guide](https://flask.palletsprojects.com/en/3.0.x/changes/)
- Upgraded requests from 2.28.0 to 2.31.0
  - Fixes security vulnerability CVE-2023-32681
- Upgraded SQLAlchemy from 1.4.40 to 2.0.23
  - Updated query API usage
  - See [SQLAlchemy 2.0 migration](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- Upgraded pytest from 7.2.0 to 7.4.3
- Upgraded black from 23.7.0 to 23.11.0
- Upgraded mypy from 1.4.1 to 1.7.0

### Added
- Added UPGRADE_PLAN.md for tracking future upgrades
- Added deprecation warnings for old API usage

### Fixed
- Fixed security vulnerability in requests library
- Resolved deprecation warnings from Flask 2.x

### Migration Guide
For developers updating their local environment:
```bash
pip install -r requirements.txt --upgrade
pytest  # Ensure tests pass
```

Breaking changes in Flask 3.0:
- `flask.json` moved to `flask.json.provider`
- Blueprint registration signature changed
- See MIGRATION.md for details
```

**Create migration guide (if needed):**
```markdown
# Migration Guide: Flask 2.x to 3.0

## Breaking Changes

### 1. JSON Provider API
**Before:**
```python
from flask import json
response = json.jsonify(data)
```

**After:**
```python
from flask.json import jsonify
response = jsonify(data)
```

### 2. Blueprint Registration
**Before:**
```python
app.register_blueprint(bp, url_prefix='/api')
```

**After:**
```python
app.register_blueprint(bp, url_prefix='/api', cli_group='api')
```

### 3. Session Interface
**Before:**
```python
session_interface = MySessionInterface()
app.session_interface = session_interface
```

**After:**
```python
from flask.sessions import SessionInterface
class MySessionInterface(SessionInterface):
    # Must implement all required methods
    pass
```

## Deprecations
- `flask.json.JSONEncoder` - Use `flask.json.provider.JSONProvider`
- `app.before_first_request` - Use `app.before_first_request_funcs` or init in factory

## Testing
Run full test suite:
```bash
pytest -v
```

Check for remaining deprecation warnings:
```bash
pytest -W default::DeprecationWarning
```
```

**Update README.md:**
```markdown
# Update requirements section
## Requirements

- Python 3.10+
- Flask 3.0+
- SQLAlchemy 2.0+
- PostgreSQL 14+

## Installation

```bash
pip install -r requirements.txt
```

### Upgrading from Previous Version

If upgrading from Flask 2.x or SQLAlchemy 1.x, see [MIGRATION.md](MIGRATION.md) for breaking changes.
```

**Update inline documentation:**
```python
# Update code comments for changed APIs

# Before
def get_users():
    """Fetch all users using SQLAlchemy 1.x API."""
    return User.query.all()

# After
def get_users():
    """Fetch all users using SQLAlchemy 2.0 API.
    
    Note: Updated for SQLAlchemy 2.0. Uses select() instead of Query API.
    See: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
    """
    from sqlalchemy import select
    return db.session.execute(select(User)).scalars().all()
```

**Verification:**
- [ ] CHANGELOG.md updated with all changes
- [ ] MIGRATION.md created if breaking changes exist
- [ ] README.md requirements section updated
- [ ] Inline documentation updated
- [ ] API documentation regenerated (if applicable)

**If This Fails:**
→ **Missing changes**: Review git diff to ensure all changes are documented

---

### Step 6: Run CI/CD Pipeline

**What:** Verify changes work in CI/CD environment before merging.

**How:** Push to feature branch and let CI run all checks.

**Create feature branch:**
```bash
# Create branch for upgrade
git checkout -b chore/dependency-upgrade-2025-10

# Stage changes
git add requirements.txt requirements-dev.txt pyproject.toml
git add CHANGELOG.md MIGRATION.md
git add src/  # If code changes
git add tests/  # If test changes

# Check what's being committed
git status
git diff --staged

# Commit with detailed message
git commit -m "chore: upgrade dependencies (Oct 2025)

Security updates:
- requests 2.28.0 → 2.31.0 (CVE-2023-32681)
- cryptography 38.0.0 → 41.0.5

Major updates:
- Flask 2.2.0 → 3.0.0 (breaking changes - see MIGRATION.md)
- SQLAlchemy 1.4.40 → 2.0.23 (breaking changes - see MIGRATION.md)

Minor updates:
- pytest 7.2.0 → 7.4.3
- black 23.7.0 → 23.11.0
- mypy 1.4.1 → 1.7.0
- ruff 0.0.285 → 0.1.6

Breaking changes:
- Updated Flask session interface usage
- Updated SQLAlchemy query API
- See MIGRATION.md for migration guide

Testing:
- All unit tests pass
- All integration tests pass
- Manual testing completed
- Performance benchmarks acceptable

Closes #234"

# Push to remote
git push -u origin chore/dependency-upgrade-2025-10
```

**Monitor CI pipeline:**
```bash
# If using GitHub CLI
gh pr create --title "chore: Dependency upgrade (Oct 2025)" \
  --body "See commit message for details" \
  --label "dependencies,maintenance"

# Watch CI status
gh pr checks --watch

# Or check on web interface
# GitHub: Go to Pull Requests → Your PR → Checks tab
```

**CI should verify:**
- [ ] All tests pass on all Python versions
- [ ] Linting passes (black, ruff, mypy)
- [ ] Coverage hasn't decreased significantly
- [ ] Build succeeds
- [ ] Documentation builds

**If CI fails:**
```bash
# Pull latest CI logs
gh run view --log-failed

# Common CI-specific issues:

# 1. Environment differences
# Fix: Update CI config with correct Python/OS versions

# 2. Missing system dependencies
# Fix: Update CI workflow to install required packages

# 3. Timeout issues
# Fix: Increase timeout or optimize slow tests

# 4. Flaky tests
# Fix: Identify and fix flaky tests or mark as flaky

# Make fixes locally
# Commit and push
git add .
git commit -m "fix: CI issues after dependency upgrade"
git push
```

**Verification:**
- [ ] CI pipeline completes successfully
- [ ] All checks pass (tests, linting, coverage)
- [ ] No new warnings or errors
- [ ] Build artifacts generated correctly

**If This Fails:**
→ **CI fails but local passes**: Check for environment differences (Python version, OS, dependencies)
→ **Flaky tests**: Mark as flaky or fix race conditions

---

### Step 7: Deploy to Staging and Test

**What:** Deploy upgraded dependencies to staging environment for integration testing.

**How:** Deploy to staging, run smoke tests, monitor for issues.

**Deploy to staging:**
```bash
# Merge to develop branch (if using gitflow)
git checkout develop
git merge chore/dependency-upgrade-2025-10

# Push to trigger staging deployment
git push origin develop

# Or deploy manually
./scripts/deploy_staging.sh

# Or use deployment tool
kubectl apply -f k8s/staging/
```

**Smoke test in staging:**
```bash
# Run automated smoke tests
./tests/smoke_tests.sh https://staging.example.com

# Or manual checks
curl https://staging.example.com/health
# Should return: {"status": "healthy"}

curl https://staging.example.com/api/version
# Should return updated version info
```

**Monitor staging:**
```bash
# Check application logs
kubectl logs -f deployment/app -n staging

# Or with logging service
# View logs in Datadog/CloudWatch/etc.

# Check error rates
# Should be similar to before upgrade

# Check performance metrics
# Response times should be comparable

# Monitor for 24-48 hours
# Watch for:
# - Memory leaks
# - Increased error rates
# - Performance degradation
# - Database connection issues
```

**Integration testing in staging:**
```markdown
# Staging Integration Test Checklist

## Core Flows
- [ ] User registration and login
- [ ] Create/Read/Update/Delete operations
- [ ] Payment processing
- [ ] Email notifications

## Third-party Integrations
- [ ] External API calls work
- [ ] Webhooks received correctly
- [ ] OAuth flows functional

## Performance
- [ ] Page load times acceptable
- [ ] API response times normal
- [ ] Database queries performant

## Edge Cases
- [ ] Error handling works
- [ ] Rate limiting functions
- [ ] Concurrent requests handled
```

**Rollback plan:**
```bash
# If issues found in staging, rollback:

# Revert the merge commit
git revert -m 1 <merge-commit-hash>
git push origin develop

# Or rollback deployment
kubectl rollout undo deployment/app -n staging

# Or redeploy previous version
./scripts/deploy_staging.sh --version v1.1.0
```

**Verification:**
- [ ] Deployed to staging successfully
- [ ] Smoke tests pass
- [ ] No errors in staging logs
- [ ] Performance metrics normal
- [ ] Integration tests pass
- [ ] Monitored for 24+ hours with no issues

**If This Fails:**
→ **Deployment fails**: Check deployment logs, verify configuration
→ **Staging issues**: Rollback, investigate, fix, redeploy
→ **Performance regression**: Profile in staging, optimize or rollback

---

### Step 8: Deploy to Production

**What:** Deploy upgraded dependencies to production with monitoring and rollback plan.

**How:** Gradual rollout with careful monitoring and quick rollback if needed.

**Pre-production checklist:**
```markdown
# Production Deployment Checklist

## Pre-Deployment
- [ ] All tests pass in CI
- [ ] Staging tests successful for 24+ hours
- [ ] No known issues in staging
- [ ] Rollback plan documented
- [ ] Team notified of deployment
- [ ] Deployment window scheduled
- [ ] On-call engineer available

## Deployment Preparation
- [ ] Database backup taken
- [ ] Previous version Docker image tagged
- [ ] Rollback script tested
- [ ] Monitoring dashboards ready
- [ ] Alert thresholds reviewed

## Post-Deployment
- [ ] Smoke tests pass
- [ ] Error rates normal
- [ ] Performance metrics acceptable
- [ ] Monitor for 2+ hours
- [ ] Team notified of success
```

**Deploy with gradual rollout:**
```bash
# Blue-green deployment
kubectl set image deployment/app app=myapp:v1.2.0 -n production
kubectl rollout status deployment/app -n production

# Or canary deployment (10% → 50% → 100%)
# Deploy to 10% of instances
kubectl set image deployment/app-canary app=myapp:v1.2.0
# Monitor for 30 minutes
# If good, deploy to 50%
# Monitor for 1 hour
# If good, deploy to 100%

# Or manual deployment
./scripts/deploy_production.sh --gradual
```

**Monitor production closely:**
```bash
# Watch logs
kubectl logs -f deployment/app -n production

# Monitor error rates
# Should remain < 1%

# Monitor response times
# Should remain < 200ms p95

# Check key metrics:
# - Request rate (should be normal)
# - Error rate (should not spike)
# - Response time (should be stable)
# - Memory usage (should not grow)
# - CPU usage (should be stable)

# Set up alerts for:
# - Error rate > 2%
# - Response time > 500ms
# - Memory usage > 80%
```

**Quick rollback if needed:**
```bash
# If issues detected, rollback immediately

# Kubernetes rollback
kubectl rollout undo deployment/app -n production

# Verify rollback
kubectl rollout status deployment/app -n production

# Or manual rollback
./scripts/rollback_production.sh --to-version v1.1.0

# Notify team
echo "Rolled back production due to [issue]" | slack-cli --channel deployments
```

**Post-deployment validation:**
```bash
# Run production smoke tests
./tests/production_smoke_test.sh

# Check critical functionality:
curl https://api.example.com/health
curl https://api.example.com/api/v1/users/me -H "Authorization: Bearer $TOKEN"

# Verify third-party integrations
./tests/integration_test.sh --env production

# Monitor for 2-4 hours after deployment
# Watch dashboards for anomalies
```

**Document deployment:**
```bash
# Update deployment log
cat >> DEPLOYMENTS.md << 'EOF'
## Deployment: v1.2.0 - Dependency Upgrade
**Date:** 2025-10-25
**Deployed by:** [Your Name]
**Duration:** 15 minutes
**Rollback Plan:** Tested and ready

### Changes
- Upgraded Flask 2.2→3.0
- Upgraded SQLAlchemy 1.4→2.0
- Security updates for requests

### Result
- ✅ Successful deployment
- ✅ All smoke tests passed
- ✅ Metrics normal after 4 hours
- No rollback needed

### Issues
None

### Next Steps
- Monitor for 48 hours
- Update team documentation
- Schedule next dependency upgrade
EOF
```

**Verification:**
- [ ] Deployed to production successfully
- [ ] No deployment errors
- [ ] Smoke tests pass in production
- [ ] Error rates remain normal (<1%)
- [ ] Performance metrics stable
- [ ] Monitored for 2+ hours with no issues
- [ ] Deployment documented

**If This Fails:**
→ **Deployment fails**: Investigate logs, rollback if critical
→ **Error rate spikes**: Rollback immediately, investigate offline
→ **Performance issues**: Profile, optimize, or rollback if severe

---

## Verification Checklist

After completing this workflow:

**Audit Complete:**
- [ ] Outdated packages identified
- [ ] Security vulnerabilities checked
- [ ] Dependency tree analyzed
- [ ] Upgrade plan created

**Upgrades Applied:**
- [ ] Security updates installed
- [ ] Minor/patch updates applied
- [ ] Major version updates handled carefully
- [ ] Tests pass after each upgrade

**Documentation Updated:**
- [ ] requirements.txt updated
- [ ] CHANGELOG.md has entry
- [ ] MIGRATION.md created (if needed)
- [ ] README.md updated

**Testing Complete:**
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done
- [ ] Performance acceptable

**Deployed:**
- [ ] CI pipeline passes
- [ ] Deployed to staging
- [ ] Deployed to production
- [ ] Monitored for issues

---

## Best Practices

### DO:
✅ Upgrade regularly (monthly/quarterly schedule)
✅ Test each upgrade immediately
✅ Commit after each successful upgrade
✅ Read changelogs for major versions
✅ Check for breaking changes before upgrading
✅ Use pip-compile for consistent environments
✅ Run security scans (safety check)
✅ Monitor after production deployment
✅ Keep rollback plan ready
✅ Document breaking changes
✅ Upgrade dependencies before major releases
✅ Test in staging before production

### DON'T:
❌ Upgrade everything at once
❌ Skip reading changelogs for major versions
❌ Ignore deprecation warnings
❌ Deploy upgrades on Friday afternoon
❌ Skip testing after upgrades
❌ Forget to update documentation
❌ Ignore security vulnerabilities
❌ Upgrade in production without staging test
❌ Make unrelated code changes during upgrade
❌ Skip CI/CD pipeline
❌ Forget to back up before upgrading

---

## Common Patterns

### Pattern 1: Monthly Dependency Maintenance
```bash
# Add to calendar: First Monday of each month
# 1-2 hour maintenance window

#!/bin/bash
# monthly_dependency_update.sh

echo "Starting monthly dependency update..."

# Check for outdated packages
pip list --outdated > outdated_$(date +%Y-%m).txt

# Check security
safety check --json > security_$(date +%Y-%m).json

# If vulnerabilities found, prioritize those
if [ $(cat security_*.json | jq '.vulnerabilities | length') -gt 0 ]; then
    echo "Security vulnerabilities found! Upgrade immediately."
fi

# Create upgrade PR
gh pr create --title "chore: Monthly dependency update $(date +%Y-%m)" \
  --body "Automated monthly dependency check"
```

### Pattern 2: Security-Only Updates
```bash
# For security updates, upgrade immediately

# Check for vulnerabilities
safety check --json | jq '.vulnerabilities'

# If found, create emergency PR
pip install package==safe_version
pytest
git add requirements.txt
git commit -m "security: upgrade package (CVE-XXXX)"
git push

# Fast-track through CI
# Deploy to production after minimal staging time
```

### Pattern 3: Pre-Release Testing
```bash
# Before major releases, update all dependencies

# 1. Create upgrade branch
git checkout -b chore/pre-release-upgrades

# 2. Upgrade all (except pinned)
pip list --outdated | awk 'NR>2 {print $1}' | xargs pip install --upgrade

# 3. Run comprehensive tests
pytest
mypy src/
black --check src/

# 4. Fix any issues
# 5. Merge before release
```

---

## Troubleshooting

### Issue: Dependency conflict after upgrade

**Symptoms:**
- `pip install` fails with "conflicting dependencies"
- Multiple packages require different versions of same dependency

**Solution:**
```bash
# View dependency tree to find conflict
pipdeptree

# Example output might show:
# package-a==1.0.0
#   - requests==2.28.0
# package-b==2.0.0
#   - requests>=2.31.0

# Option 1: Update package-a if possible
pip install --upgrade package-a

# Option 2: Use compatible versions
pip install package-a package-b --upgrade

# Option 3: Use pip-compile to resolve
cat > requirements.in << 'EOF'
package-a
package-b
EOF
pip-compile requirements.in

# Option 4: Pin one package to compatible version
echo "package-a>=1.1.0" >> requirements.in
```

**Prevention:**
- Use pip-compile for automatic conflict resolution
- Keep dependencies up to date (less conflicts)
- Check compatibility before upgrading

---

### Issue: Tests pass locally but fail in CI after upgrade

**Symptoms:**
- All tests pass on local machine
- CI fails with test errors or import errors

**Solution:**
```bash
# Common causes:

# 1. Different Python versions
# Check .github/workflows/ci.yml
python-version: ['3.10', '3.11']  # Make sure these match your local

# 2. System dependencies missing in CI
# Add to CI workflow:
- name: Install system dependencies
  run: |
    apt-get update
    apt-get install -y libpq-dev  # Example for PostgreSQL

# 3. Environment variables
# Add to CI:
env:
  DATABASE_URL: postgresql://localhost/test_db
  DEBUG: true

# 4. Cache issues
# Clear CI cache or add:
- name: Clear pip cache
  run: pip cache purge

# Test locally with act (GitHub Actions locally)
act -j test
```

**Prevention:**
- Use same Python version locally and in CI
- Document system dependencies
- Test with act before pushing

---

### Issue: Application slower after upgrade

**Symptoms:**
- Response times increased
- Higher CPU usage
- More database queries

**Solution:**
```bash
# Profile the application
python -m cProfile -o profile.stats app.py

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)
"

# Compare performance before/after
pytest --benchmark-compare=before.json tests/performance/

# Common issues:

# 1. N+1 queries (SQLAlchemy 2.0)
# Use eager loading:
from sqlalchemy import select
from sqlalchemy.orm import selectinload
stmt = select(User).options(selectinload(User.posts))

# 2. New default behaviors
# Check changelog for performance-related changes

# 3. Debug mode enabled
# Ensure DEBUG=False in production

# If regression is severe, rollback
pip install package==old_version
```

**Prevention:**
- Run performance benchmarks before/after upgrade
- Test with production-like data volume
- Profile critical paths

---

### Issue: Breaking changes not documented

**Symptoms:**
- Code breaks after upgrade
- No migration guide available
- Unclear how to update code

**Solution:**
```bash
# 1. Check package changelog
pip show package | grep Home-page
# Visit homepage → changelog

# 2. Search GitHub issues
# github.com/package/repo/issues

# 3. Compare API docs
# Compare old vs new documentation

# 4. Git blame the changes
# github.com/package/repo/compare/v1.0...v2.0

# 5. Community resources
# Stack Overflow, Reddit, package forums

# Document your findings
cat > MIGRATION.md << 'EOF'
# Migration Guide: package v1 → v2

## Breaking Changes I Found
1. Function renamed: old_func() → new_func()
2. Import path changed: from package import X → from package.new import X
3. Parameter removed: func(a, b) → func(a)

## Code Updates Needed
[Document your changes]
EOF
```

**Prevention:**
- Always read changelogs before upgrading
- Test major upgrades in isolated branch
- Document findings for team

---

## Related Workflows

**Prerequisites:**
- [[dev-003]] Environment Initialization - Need working environment
- [[dev-002]] Test Writing - Need tests to verify upgrades

**Next Steps:**
- [[dev-007]] Dependency Update Strategy - Long-term maintenance plan
- [[qa-002]] Test Failure Investigation - If tests fail after upgrade
- [[dvo-013]] Rollback Procedure - If upgrade causes production issues

**Related:**
- [[sec-002]] Security Vulnerability Management - Addressing CVEs
- [[qa-008]] Quality Gate Execution - CI/CD checks
- [[dvo-014]] Performance Tuning - Optimizing after upgrades

---

## Tags
`development` `dependencies` `maintenance` `security` `updates` `pip` `requirements` `testing` `deployment` `best-practices`
