---
id: dev-017
title: CI/CD Pipeline Implementation
category: Development
subcategory: Automation
tags:
  - ci-cd
  - automation
  - testing
  - deployment
  - github-actions
  - pipeline
prerequisites:
  - dev-006  # Test Writing
  - dev-003  # Environment Initialization
related_workflows:
  - dev-018  # Docker Container Creation
  - qa-002   # Code Review Checklist
  - sec-001  # Secret Management
complexity: intermediate
estimated_time: 45-60 minutes
last_updated: 2025-10-25
---

# CI/CD Pipeline Implementation

## Overview

**What:** Set up automated continuous integration and deployment pipelines that run tests, checks, and deployments on every code change.

**Why:** CI/CD automates quality checks, catches bugs early, ensures consistent deployments, and accelerates development velocity by reducing manual processes.

**When to use:**
- Starting a new project that needs automated testing
- Adding automated checks to existing projects
- Improving deployment reliability
- Enforcing code quality standards automatically
- Reducing manual deployment effort

---

## Prerequisites

**Required:**
- [ ] Git repository (GitHub, GitLab, or similar)
- [ ] Basic knowledge of YAML syntax
- [ ] Existing test suite (or write tests first)
- [ ] Access to CI/CD platform (GitHub Actions, GitLab CI, CircleCI)

**Optional:**
- [ ] Docker knowledge (for containerized deployments)
- [ ] Cloud platform account (for deployment targets)

**Check before starting:**
```bash
# Verify you have a test suite
pytest --collect-only

# Check git remote is configured
git remote -v

# Verify branch protection isn't blocking CI setup
git branch -r
```

---

## Implementation Steps

### Step 1: Choose CI/CD Platform

**What:** Select and configure your CI/CD platform based on your repository host and requirements.

**How:** Most teams use their repository's native CI platform for simplicity. GitHub Actions for GitHub, GitLab CI for GitLab, etc.

**Decision Matrix:**
```yaml
GitHub → GitHub Actions (free for public repos)
GitLab → GitLab CI (built-in)
Any Git → CircleCI, Travis CI, Jenkins
```

**For this guide:** We'll use GitHub Actions (most common)

**Setup:**
```bash
# Create GitHub Actions directory
mkdir -p .github/workflows

# This is where CI configuration files will live
ls .github/workflows/
```

**Verification:**
- [ ] `.github/workflows/` directory exists
- [ ] You have push access to the repository
- [ ] GitHub Actions is enabled in repo settings

**If This Fails:**
→ Check repository permissions
→ Verify GitHub Actions isn't disabled by organization policy
→ Try creating directory through GitHub web interface

---

### Step 2: Create Basic CI Pipeline

**What:** Set up a workflow that runs on every push and pull request to verify code quality.

**How:** Create a YAML file that defines when to run, what environment to use, and which commands to execute.

**Code:**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        pip install ruff
        ruff check .
    
    - name: Run type checking
      run: |
        pip install mypy
        mypy .
    
    - name: Run tests with coverage
      run: |
        pip install pytest pytest-cov
        pytest --cov=src --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

**Commit and push:**
```bash
git add .github/workflows/ci.yml
git commit -m "Add CI pipeline"
git push
```

**Verification:**
- [ ] Workflow file committed successfully
- [ ] GitHub Actions tab shows new workflow
- [ ] Workflow runs automatically on push
- [ ] All jobs complete successfully (green checkmark)

**If This Fails:**
→ Check YAML syntax (use https://www.yamllint.com/)
→ Review GitHub Actions logs for specific errors
→ Ensure all commands work locally first
→ Verify matrix versions match your project requirements

---

### Step 3: Add Code Quality Gates

**What:** Integrate automated code quality tools that enforce standards and catch issues.

**How:** Add jobs for linting, formatting, security scanning, and complexity analysis.

**Code:**

Add to `.github/workflows/ci.yml` (new job):

```yaml
  quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install quality tools
      run: |
        pip install ruff black isort bandit radon
    
    - name: Check code formatting
      run: |
        black --check .
        isort --check-only .
    
    - name: Security scan
      run: |
        bandit -r src/ -f json -o bandit-report.json
        # Don't fail on security warnings, just report
        bandit -r src/ || true
    
    - name: Complexity analysis
      run: |
        radon cc src/ -a -nb
        radon mi src/ -nb
    
    - name: Upload security report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-report
        path: bandit-report.json
```

**Configuration files:**

Create `.ruff.toml`:
```toml
line-length = 100
target-version = "py311"

[lint]
select = ["E", "F", "I", "N", "W", "B", "Q"]
ignore = ["E501"]  # Line too long (handled by formatter)
```

Create `pyproject.toml` (or add to existing):
```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100
```

**Verification:**
- [ ] Quality checks run on every push
- [ ] Code formatting is enforced
- [ ] Security scan completes
- [ ] Reports are uploaded as artifacts

**If This Fails:**
→ Run each tool locally to fix issues: `black .`, `isort .`
→ Adjust rules in config files if too strict
→ Use `|| true` for non-blocking checks initially
→ Gradually increase strictness as code improves

---

### Step 4: Set Up Continuous Deployment

**What:** Automatically deploy your application when code is merged to main branch.

**How:** Add deployment jobs that trigger only on successful merges to production branches.

**Code:**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Allow manual triggers

jobs:
  deploy:
    runs-on: ubuntu-latest
    # Only deploy if tests pass
    needs: [test, quality]  # Reference jobs from ci.yml if combined
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Build application
      run: |
        # Your build steps here
        python -m build
    
    # Example: Deploy to Railway
    - name: Deploy to Railway
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
      run: |
        npm install -g @railway/cli
        railway up --service ${{ secrets.RAILWAY_SERVICE_ID }}
    
    # Example: Deploy to Heroku
    # - name: Deploy to Heroku
    #   uses: akhileshns/heroku-deploy@v3.12.14
    #   with:
    #     heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
    #     heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
    #     heroku_email: ${{ secrets.HEROKU_EMAIL }}
    
    # Example: Deploy to AWS
    # - name: Configure AWS credentials
    #   uses: aws-actions/configure-aws-credentials@v4
    #   with:
    #     aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    #     aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    #     aws-region: us-east-1
    
    # - name: Deploy to ECS
    #   run: |
    #     aws ecs update-service --cluster prod --service myapp --force-new-deployment
    
    - name: Create deployment notification
      if: success()
      run: |
        echo "Deployment successful! 🚀"
        # Add Slack/Discord webhook notification here
```

**Add secrets in GitHub:**
```bash
# Go to: Settings → Secrets and variables → Actions → New repository secret

# Add your deployment credentials:
RAILWAY_TOKEN=<your-token>
RAILWAY_SERVICE_ID=<your-service-id>

# Or for other platforms:
HEROKU_API_KEY=<your-key>
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

**Verification:**
- [ ] Deploy workflow only triggers on main branch
- [ ] Secrets are configured in repository settings
- [ ] Deployment succeeds to target platform
- [ ] Application is accessible after deployment
- [ ] Rollback plan is documented

**If This Fails:**
→ Test deployment commands locally first
→ Verify secrets are correctly set in GitHub
→ Check deployment platform status/logs
→ Use `workflow_dispatch` to manually trigger and debug
→ Add verbose logging: `set -x` in bash scripts

---

### Step 5: Add Docker Build Pipeline

**What:** Build and push Docker images as part of CI/CD for consistent deployments.

**How:** Add Docker build job that creates images on successful tests and pushes to registry.

**Code:**

Add to `.github/workflows/ci.yml`:

```yaml
  docker:
    runs-on: ubuntu-latest
    needs: [test, quality]
    # Only build Docker images for main branch and tags
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    # Or login to GitHub Container Registry
    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: |
          myusername/myapp
          ghcr.io/${{ github.repository }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha,prefix={{branch}}-
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=registry,ref=myusername/myapp:buildcache
        cache-to: type=registry,ref=myusername/myapp:buildcache,mode=max
```

**Create Dockerfile** (if needed):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Verification:**
- [ ] Docker image builds successfully
- [ ] Image is pushed to registry
- [ ] Image can be pulled and run locally
- [ ] Image is tagged correctly (branch, SHA, version)
- [ ] Build cache reduces build time

**If This Fails:**
→ Test Docker build locally: `docker build -t test .`
→ Verify Docker Hub credentials are correct
→ Check Dockerfile syntax and base image availability
→ Ensure .dockerignore excludes unnecessary files
→ Review build logs for specific errors

---

### Step 6: Implement Branch Protection Rules

**What:** Enforce CI checks before allowing code to be merged to protected branches.

**How:** Configure branch protection rules in GitHub repository settings.

**Steps:**

1. Go to **Settings → Branches → Add branch protection rule**

2. Configure protection for `main`:
```yaml
Branch name pattern: main

Settings to enable:
☑ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Dismiss stale reviews when new commits are pushed
  
☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
  Status checks: (select all CI jobs)
    - test
    - quality
    - docker (if applicable)
    
☑ Require conversation resolution before merging

☑ Require linear history (optional but recommended)

☑ Include administrators (enforces rules on admins too)
```

3. Add protection for `develop` (if using git-flow):
```yaml
Same as main, but:
- Require approvals: 0 (for faster iteration)
- Allow force pushes (for rebasing)
```

**Verification:**
- [ ] Cannot push directly to main
- [ ] Must create PR to merge code
- [ ] PR blocked until CI passes
- [ ] Cannot merge with failing checks
- [ ] Merge button shows status checks

**If This Fails:**
→ Ensure you have admin access to repository
→ Wait for CI jobs to complete at least once
→ Check that job names match protection rules exactly
→ Verify status checks appear in PR interface

---

### Step 7: Add Deployment Environments

**What:** Set up environment-specific configurations and approvals for production deployments.

**How:** Use GitHub Environments to manage deployment targets with protection rules.

**Setup:**

1. Go to **Settings → Environments → New environment**

2. Create `production` environment:
```yaml
Environment name: production

Protection rules:
☑ Required reviewers: [select reviewers]
  - Wait time: 0 minutes (or add delay)

☑ Deployment branches:
  - Selected branches: main

Environment secrets:
- PRODUCTION_API_KEY
- PRODUCTION_DATABASE_URL
- PRODUCTION_ALLOWED_HOSTS
```

3. Create `staging` environment:
```yaml
Environment name: staging

Protection rules:
☐ Required reviewers (optional for staging)

☑ Deployment branches:
  - Selected branches: main, develop

Environment secrets:
- STAGING_API_KEY
- STAGING_DATABASE_URL
```

**Update deploy workflow:**
```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        env:
          API_KEY: ${{ secrets.STAGING_API_KEY }}
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          # Deploy to staging
          echo "Deploying to staging environment"
  
  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        env:
          API_KEY: ${{ secrets.PRODUCTION_API_KEY }}
          DATABASE_URL: ${{ secrets.PRODUCTION_DATABASE_URL }}
        run: |
          # Deploy to production
          echo "Deploying to production environment"
```

**Verification:**
- [ ] Environments appear in repository settings
- [ ] Production requires manual approval
- [ ] Environment-specific secrets are isolated
- [ ] Deployments show in environment history
- [ ] Can view deployment status per environment

**If This Fails:**
→ Check environment names match exactly in workflow
→ Verify branch restrictions are configured correctly
→ Ensure reviewers have proper permissions
→ Test with staging environment first

---

### Step 8: Monitor and Optimize

**What:** Set up monitoring, notifications, and continuous improvement of CI/CD pipeline.

**How:** Add status badges, notifications, and performance tracking.

**Status badges in README:**
```markdown
# My Project

![CI](https://github.com/username/repo/workflows/CI/badge.svg)
![Deploy](https://github.com/username/repo/workflows/Deploy/badge.svg)
[![codecov](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
```

**Slack notifications:**
```yaml
    - name: Notify on failure
      if: failure()
      uses: slackapi/slack-github-action@v1.25.0
      with:
        payload: |
          {
            "text": "❌ CI Failed: ${{ github.repository }}",
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*CI Failed*\nRepo: ${{ github.repository }}\nBranch: ${{ github.ref }}\nCommit: ${{ github.sha }}"
                }
              }
            ]
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**Performance optimization:**
```yaml
# Add job concurrency limits
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Use dependency caching
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

# Parallelize tests
strategy:
  matrix:
    test-group: [unit, integration, e2e]
```

**Track metrics:**
- Time to run CI (aim for < 10 minutes)
- Test success rate (aim for > 95%)
- Deployment frequency (daily → multiple times per day)
- Lead time for changes (< 1 day)
- Mean time to recovery (< 1 hour)

**Verification:**
- [ ] Status badges show current build status
- [ ] Team receives notifications for failures
- [ ] CI completes in reasonable time (< 15 min)
- [ ] Deployment history is tracked
- [ ] Metrics show improvement over time

**If This Fails:**
→ Profile slow tests and parallelize
→ Reduce matrix combinations if too slow
→ Use workflow caching effectively
→ Consider splitting into multiple workflows
→ Review notification frequency to avoid spam

---

## Verification Checklist

After completing this workflow:

- [ ] CI pipeline runs on every push and PR
- [ ] All tests run automatically
- [ ] Code quality checks enforce standards
- [ ] Docker images build successfully (if applicable)
- [ ] Deployments work to target environments
- [ ] Branch protection prevents bad code from merging
- [ ] Production deployments require approval
- [ ] Team is notified of failures
- [ ] Pipeline completes in < 15 minutes
- [ ] Documentation is updated with CI/CD process

---

## Best Practices

### DO:
✅ Run CI on every branch and PR
✅ Keep CI fast (< 10 min) by parallelizing and caching
✅ Fail fast - run quick checks first (linting before tests)
✅ Use matrix testing for multiple Python/OS versions
✅ Separate CI (test) from CD (deploy) workflows
✅ Require PR reviews and CI passage before merging
✅ Use semantic versioning for releases
✅ Cache dependencies to speed up builds
✅ Monitor CI performance and optimize bottlenecks
✅ Document deployment process in README
✅ Use environment-specific secrets
✅ Test rollback procedures

### DON'T:
❌ Store secrets in workflow files (use GitHub Secrets)
❌ Deploy directly from local machine
❌ Skip CI checks with force pushes
❌ Run expensive integration tests on every commit
❌ Deploy without running tests first
❌ Ignore flaky tests (fix or remove them)
❌ Over-complicate with too many jobs/steps
❌ Deploy to production without staging first
❌ Forget to version Docker images
❌ Leave notifications too noisy (filter to failures only)

---

## Common Patterns

### Pattern 1: Fast Feedback Loop
```yaml
# Run fast checks first, slow tests later
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ruff check .  # 10 seconds
  
  test-unit:
    needs: [lint]  # Only if lint passes
    steps:
      - run: pytest tests/unit  # 2 minutes
  
  test-integration:
    needs: [test-unit]  # Only if unit tests pass
    steps:
      - run: pytest tests/integration  # 5 minutes
```

### Pattern 2: Conditional Deployments
```yaml
jobs:
  deploy:
    if: |
      github.event_name == 'push' &&
      github.ref == 'refs/heads/main' &&
      !contains(github.event.head_commit.message, '[skip ci]')
    steps:
      - run: ./deploy.sh
```

### Pattern 3: Reusable Workflows
```yaml
# .github/workflows/reusable-test.yml
name: Reusable Tests

on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pytest

# Use in main workflow:
# .github/workflows/ci.yml
jobs:
  test-py310:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.10'
```

### Pattern 4: Manual Approval Gates
```yaml
jobs:
  approve:
    runs-on: ubuntu-latest
    environment: production-approval
    steps:
      - run: echo "Approved by ${{ github.actor }}"
  
  deploy:
    needs: [approve]
    steps:
      - run: ./deploy-to-prod.sh
```

---

## Troubleshooting

### Issue: Workflow not triggering

**Symptoms:**
- Pushed code but no workflow run appears
- PR opened but checks don't start

**Solutions:**
```bash
# 1. Check workflow syntax
yamllint .github/workflows/*.yml

# 2. Verify GitHub Actions is enabled
# Settings → Actions → Allow all actions

# 3. Check branch filters match
git branch  # Compare with workflow 'on.push.branches'

# 4. Look for workflow errors in Actions tab
# May have syntax errors preventing run
```

**Prevention:**
- Validate YAML before committing
- Test workflows with `workflow_dispatch` first
- Check Actions tab for workflow status

---

### Issue: Tests pass locally but fail in CI

**Symptoms:**
- `pytest` succeeds on local machine
- Same tests fail in GitHub Actions

**Solutions:**
```yaml
# 1. Check Python version matches
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Match your local version

# 2. Install all dependencies
- run: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt  # Don't forget dev deps!

# 3. Check for environment-specific tests
- run: pytest -v  # Verbose output shows which test fails

# 4. Debug by SSH into runner
- uses: lhotari/action-upterm@v1  # Temporarily add for debugging
```

**Prevention:**
- Use exact versions in requirements.txt
- Run tests in Docker locally (matches CI environment)
- Don't rely on local environment variables

---

### Issue: Secrets not working

**Symptoms:**
- Deployment fails with authentication errors
- Environment variables are empty in workflow

**Solutions:**
```yaml
# 1. Check secret name matches exactly (case-sensitive)
env:
  API_KEY: ${{ secrets.API_KEY }}  # Must match Settings → Secrets

# 2. Verify secret is set in correct location
# - Repository secrets: Available to all workflows
# - Environment secrets: Only for specific environment

# 3. Check secret isn't masked in logs
# Secrets are automatically hidden, won't appear in output

# 4. Use secret in step that needs it
- name: Deploy
  env:
    TOKEN: ${{ secrets.DEPLOY_TOKEN }}  # Set at step level
  run: |
    echo "Token length: ${#TOKEN}"  # Check it exists (don't print value!)
    ./deploy.sh
```

**Prevention:**
- Document which secrets are required
- Use environment secrets for env-specific values
- Never commit secrets to code (use .env.example templates)

---

### Issue: CI takes too long

**Symptoms:**
- Workflow runs for 20+ minutes
- Tests timeout
- Team waits too long for feedback

**Solutions:**
```yaml
# 1. Profile test execution
- run: pytest --durations=10  # Show 10 slowest tests

# 2. Parallelize tests
strategy:
  matrix:
    test-suite: [unit, integration, e2e]
steps:
  - run: pytest tests/${{ matrix.test-suite }}

# 3. Use caching aggressively
- uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      .pytest_cache
      .mypy_cache
    key: ${{ runner.os }}-${{ hashFiles('**/*.py') }}

# 4. Split into multiple jobs
jobs:
  lint:  # Fast feedback (30 sec)
  test:  # Parallel tests (3 min)
    needs: [lint]
  integration:  # Slow tests (5 min)
    needs: [test]

# 5. Use faster runners (if available)
runs-on: ubuntu-latest-4-cores  # GitHub Enterprise
```

**Prevention:**
- Keep unit tests fast (< 5 min total)
- Move slow integration tests to nightly builds
- Mock external services in tests
- Use test markers to run subsets: `pytest -m "not slow"`

---

## Related Workflows

**Prerequisites:**
- [[test_writing]] - Need tests before CI is useful
- [[environment_initialization]] - Proper env setup for consistency

**Next Steps:**
- [[docker_container_creation]] - Containerize for deployment
- [[kubernetes_deployment]] - Orchestrate containers
- [[application_monitoring_setup]] - Monitor after deployment

**Alternatives:**
- [[cicd_pipeline_setup]] - More detailed DevOps perspective
- GitLab CI (.gitlab-ci.yml) - Similar concepts, different syntax
- Jenkins - Traditional on-premise CI/CD
- CircleCI - Alternative cloud CI platform

---

## Tags
`development` `ci-cd` `automation` `testing` `deployment` `github-actions` `pipeline` `quality-assurance` `devops`
