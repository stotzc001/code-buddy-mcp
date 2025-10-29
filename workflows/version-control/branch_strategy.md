# Branch Strategy

**ID:** ver-001  
**Category:** Version Control  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 30-60 minutes (initial setup)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Establish and implement a consistent git branching strategy that supports team collaboration, release management, and deployment workflows.

**Why:** A well-defined branching strategy prevents conflicts, enables parallel development, supports multiple release versions, and provides clear paths for hotfixes. Without a strategy, teams face merge chaos, deployment confusion, and difficulty tracking features.

**When to use:**
- Starting a new project or repository
- Team experiencing frequent merge conflicts
- Need to support multiple environments (dev, staging, prod)
- Transitioning from ad-hoc branching to structured workflow
- Scaling team size (>3 developers)
- Need to support multiple release versions simultaneously

---

## Prerequisites

**Required:**
- [ ] Git installed (2.x+)
- [ ] Understanding of git basics (clone, commit, push, pull)
- [ ] Repository access for all team members
- [ ] CI/CD pipeline in place (or planned)
- [ ] Team alignment on chosen strategy

**Check before starting:**
```bash
# Verify git version
git --version

# Check current branches
git branch -a

# Verify remote configuration
git remote -v

# Check if repository is clean
git status

# View current branch protection rules (GitHub)
gh repo view --json branchProtectionRules
```

---

## Implementation Steps

### Step 1: Choose Branching Strategy

**What:** Select the branching model that best fits your team size, release cadence, and deployment needs.

**How:**
Evaluate your requirements and select from proven strategies.

**Strategy Comparison:**

| Strategy | Best For | Team Size | Release Frequency | Complexity |
|----------|----------|-----------|-------------------|------------|
| **Trunk-Based** | Continuous deployment, fast iteration | Small-Medium (1-10) | Multiple per day | ⭐ Simple |
| **GitHub Flow** | Web apps, SaaS products | Medium (5-20) | Daily/Weekly | ⭐⭐ Moderate |
| **GitFlow** | Scheduled releases, multiple versions | Medium-Large (10-50+) | Monthly/Quarterly | ⭐⭐⭐ Complex |
| **GitLab Flow** | Environment-based deployment | Medium (5-30) | Weekly/Bi-weekly | ⭐⭐ Moderate |

**Trunk-Based Development:**
```
main (always deployable)
  ↓
feature branches (short-lived, <2 days)
  ↓
Merge to main daily
  ↓
Deploy from main continuously
```

**GitHub Flow:**
```
main (production)
  ↓
feature/branch-name
  ↓
Pull Request → Review → Merge
  ↓
Deploy from main
```

**GitFlow:**
```
main (production releases only)
  ↓
develop (integration branch)
  ↓
feature/*, release/*, hotfix/*
  ↓
Complex merge patterns
```

**GitLab Flow:**
```
main → pre-production → production
  ↓
feature branches merge to main
  ↓
Promote through environments
```

**Decision Framework:**
```markdown
## Questions to Ask

1. **How often do you deploy to production?**
   - Multiple times per day → Trunk-Based
   - Daily/Weekly → GitHub Flow or GitLab Flow
   - Monthly/Quarterly → GitFlow

2. **Do you need to support multiple production versions?**
   - No → Trunk-Based or GitHub Flow
   - Yes → GitFlow

3. **Team experience with git?**
   - Junior → GitHub Flow (simpler)
   - Senior → Any strategy
   - Mixed → Start simple (GitHub Flow)

4. **Release rollback strategy?**
   - Fast-forward only → Trunk-Based
   - Tag-based → GitHub Flow
   - Need release branches → GitFlow

5. **CI/CD maturity?**
   - Fully automated → Trunk-Based
   - Partial automation → GitHub Flow
   - Manual releases → GitFlow
```

**Example Decision:**
```bash
# For a SaaS web application:
# - Team: 8 developers
# - Deploy: Multiple times per day
# - Environment: Staging + Production
# - CI/CD: Fully automated
# 
# CHOICE: GitHub Flow (simple, supports CD, good for teams)
```

**Verification:**
- [ ] Strategy selected and documented
- [ ] Team agrees on chosen strategy
- [ ] Strategy matches deployment needs
- [ ] Team trained on strategy basics

**If This Fails:**
→ If team can't agree, start with simplest (GitHub Flow) and iterate  
→ If needs unclear, document requirements first  
→ If existing workflows complex, plan migration path  

---

### Step 2: Define Branch Naming Conventions

**What:** Establish clear, consistent branch naming patterns that convey purpose and context.

**How:**
Create naming rules that everyone follows without thinking.

**Naming Patterns:**

```bash
# Feature Development
feature/short-description
feature/user-authentication
feature/payment-integration
feature/JIRA-123-user-profile

# Bug Fixes
bugfix/issue-description
bugfix/login-error
bugfix/GH-456-memory-leak
fix/critical-security-patch

# Hotfixes (production)
hotfix/critical-issue
hotfix/payment-gateway-down
hotfix/PROD-789

# Release Branches (GitFlow)
release/1.2.0
release/2024-Q1

# Experimental/Research
experiment/new-architecture
spike/graphql-investigation
poc/ai-integration

# Documentation
docs/api-guide
docs/setup-instructions
```

**Branch Naming Rules:**

```yaml
# .github/branch-naming-rules.yml
rules:
  format: "type/description"
  
  types:
    - feature  # New functionality
    - bugfix   # Bug fixes
    - hotfix   # Critical production fixes
    - release  # Release preparation
    - docs     # Documentation only
    - refactor # Code refactoring
    - test     # Adding tests
    - chore    # Build/tool changes
  
  description:
    - Lowercase only
    - Hyphen-separated (kebab-case)
    - Max 50 characters
    - No special characters except: - / #
    - Include ticket number when applicable
  
  examples:
    valid:
      - feature/user-authentication
      - bugfix/GH-123-login-error
      - hotfix/payment-critical
      - release/v1.2.0
    
    invalid:
      - Feature/UserAuth  # Wrong case
      - fix_login_bug     # Underscores not allowed
      - my-awesome-feature-that-does-many-things  # Too long
```

**Enforcement:**

```bash
# Pre-push hook to validate branch names
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Enforce branch naming convention

BRANCH=$(git rev-parse --abbrev-ref HEAD)
VALID_PATTERN="^(feature|bugfix|hotfix|release|docs|refactor|test|chore)/[a-z0-9-]{1,50}$"

if [[ ! $BRANCH =~ $VALID_PATTERN ]] && [ "$BRANCH" != "main" ] && [ "$BRANCH" != "develop" ]; then
  echo "❌ Invalid branch name: $BRANCH"
  echo ""
  echo "Branch names must follow: type/description"
  echo "Valid types: feature, bugfix, hotfix, release, docs, refactor, test, chore"
  echo "Description: lowercase, hyphen-separated, max 50 chars"
  echo ""
  echo "Examples:"
  echo "  ✅ feature/user-authentication"
  echo "  ✅ bugfix/GH-123-login-error"
  echo "  ❌ Feature/UserAuth"
  echo "  ❌ fix_something"
  exit 1
fi
EOF

chmod +x .git/hooks/pre-push

# GitHub Action to validate branch names on PR
cat > .github/workflows/branch-name-check.yml << 'EOF'
name: Branch Name Check

on:
  pull_request:
    types: [opened, reopened]

jobs:
  check-branch-name:
    runs-on: ubuntu-latest
    steps:
      - name: Validate branch name
        run: |
          BRANCH="${{ github.head_ref }}"
          PATTERN="^(feature|bugfix|hotfix|release|docs|refactor|test|chore)/[a-z0-9-]{1,50}$"
          
          if [[ ! $BRANCH =~ $PATTERN ]]; then
            echo "❌ Invalid branch name: $BRANCH"
            echo "See: docs/branch-naming.md"
            exit 1
          fi
          
          echo "✅ Branch name valid: $BRANCH"
EOF
```

**Documentation:**

```markdown
# Branch Naming Guide

## Quick Reference

| Type | When to Use | Example |
|------|-------------|---------|
| `feature/` | New features | `feature/user-dashboard` |
| `bugfix/` | Non-critical bugs | `bugfix/typo-fix` |
| `hotfix/` | Production emergencies | `hotfix/payment-down` |
| `release/` | Release preparation | `release/v2.0.0` |
| `docs/` | Documentation changes | `docs/api-guide` |

## Creating Branches

```bash
# Good
git checkout -b feature/user-authentication
git checkout -b bugfix/GH-789-cache-issue

# Bad
git checkout -b Feature/UserAuth
git checkout -b fix_something
git checkout -b johns-awesome-branch
```

## Why This Matters

- **Clarity**: Anyone can understand purpose at a glance
- **Automation**: CI/CD can apply different rules per type
- **Organization**: Easy to find related branches
- **History**: Clear git log and branch listing
```

**Verification:**
- [ ] Naming convention documented
- [ ] Team trained on conventions
- [ ] Pre-push hook installed (optional)
- [ ] CI check configured
- [ ] Examples provided in documentation

**If This Fails:**
→ If team forgets conventions, add enforcement hooks  
→ If naming too strict, relax rules slightly  
→ If existing branches violate rules, create migration plan  

---

### Step 3: Establish Branch Hierarchy and Protection

**What:** Define branch relationships and protection rules to prevent accidental changes to critical branches.

**How:**
Configure main branches with appropriate protection rules.

**Branch Hierarchy (GitHub Flow Example):**

```
main (protected)
├── feature/user-auth ─┐
├── feature/payment    │─→ Pull Requests → main
├── bugfix/login      ─┘
└── hotfix/critical (direct to main when approved)
```

**Branch Hierarchy (GitFlow Example):**

```
main (protected)
├── develop (protected)
│   ├── feature/x ─┐
│   ├── feature/y  │─→ Pull Requests → develop
│   └── feature/z ─┘
├── release/1.2.0 (from develop → main)
└── hotfix/critical (from main → main + develop)
```

**Main Branch Protection (GitHub):**

```bash
# Via GitHub CLI
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -F required_status_checks='{
    "strict": true,
    "contexts": ["ci/tests", "ci/lint", "ci/security-scan"]
  }' \
  -F enforce_admins=true \
  -F required_pull_request_reviews='{
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  }' \
  -F restrictions=null

# Via GitHub UI
# Settings → Branches → Branch protection rules → Add rule

# Protection settings:
# ✅ Require pull request before merging
#    ✅ Require approvals (1+)
#    ✅ Dismiss stale reviews
# ✅ Require status checks to pass
#    ✅ Require branches to be up to date
#    - ci/tests
#    - ci/lint
#    - ci/security-scan
# ✅ Require conversation resolution before merging
# ✅ Require signed commits (optional)
# ✅ Include administrators
# ✅ Restrict who can push (optional)
```

**Development Branch Protection:**

```bash
# For GitFlow's develop branch
gh api repos/:owner/:repo/branches/develop/protection \
  -X PUT \
  -F required_status_checks='{
    "strict": true,
    "contexts": ["ci/tests", "ci/lint"]
  }' \
  -F required_pull_request_reviews='{
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": false
  }'

# Slightly less strict than main:
# - 1 approval (vs 2 for main)
# - Don't dismiss stale reviews (faster iteration)
# - Status checks still required
```

**GitLab Protection:**

```ruby
# Via GitLab API
require 'gitlab'

client = Gitlab.client(
  endpoint: 'https://gitlab.com/api/v4',
  private_token: ENV['GITLAB_TOKEN']
)

client.protect_branch(
  'project-id',
  'main',
  {
    push_access_level: 0,  # No one can push
    merge_access_level: 30, # Developers can merge
    allow_force_push: false,
    code_owner_approval_required: true
  }
)

# Via GitLab UI
# Settings → Repository → Protected Branches
```

**CODEOWNERS File:**

```bash
# .github/CODEOWNERS or .gitlab/CODEOWNERS
# Code owners must review specific paths

# Global owners
* @org/core-team

# Backend
/src/api/ @backend-team @alice
/src/database/ @backend-team @database-admin

# Frontend
/src/frontend/ @frontend-team
/src/components/ @frontend-team @design-lead

# Infrastructure
/infrastructure/ @devops-team
/.github/workflows/ @devops-team
/Dockerfile @devops-team

# Security
/src/auth/ @security-team
/src/encryption/ @security-team

# Documentation
/docs/ @tech-writer @docs-team

# Configuration (sensitive)
/.env.example @security-team
/config/production.yml @ops-lead
```

**Verification:**
- [ ] Main branch protected
- [ ] Status checks configured
- [ ] Required reviewers set
- [ ] CODEOWNERS file created
- [ ] Team permissions configured
- [ ] Protection tested (try direct push)

**If This Fails:**
→ If protection too strict, relax for non-main branches  
→ If team blocked, ensure proper permissions  
→ If status checks fail, verify CI configuration  

---

### Step 4: Document Workflow

**What:** Create clear documentation explaining the entire branching workflow from start to finish.

**How:**
Write step-by-step guide that covers all common scenarios.

**Workflow Documentation Template:**

```markdown
# Git Workflow Guide

## Overview

We use **GitHub Flow** for simple, continuous deployment:
- One main branch (`main`) that's always deployable
- Feature branches for all changes
- Pull requests for code review
- Automated CI/CD deployment

## Quick Start

### Starting New Work

1. **Update main branch**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit frequently**
   ```bash
   git add .
   git commit -m "feat: Add user authentication"
   git push origin feature/your-feature-name
   ```

4. **Create pull request**
   ```bash
   gh pr create --title "Add user authentication" --body "Description"
   # Or use GitHub UI
   ```

5. **Address review feedback**
   ```bash
   git add .
   git commit -m "fix: Address review comments"
   git push
   ```

6. **Merge when approved**
   - Use "Squash and merge" for clean history
   - Delete branch after merge

## Detailed Workflows

### Feature Development

```
main
  ↓ Create branch
feature/my-feature
  ↓ Commits
  ↓ Push
  ↓ Pull Request
  ↓ Review
  ↓ CI passes
  ↓ Approval
  ↓ Merge
main (updated)
```

**Commands:**
```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create and switch to feature branch
git checkout -b feature/user-profile

# 3. Work and commit
git add src/profile.py
git commit -m "feat: Add user profile page"

git add tests/test_profile.py
git commit -m "test: Add profile tests"

# 4. Push to remote
git push -u origin feature/user-profile

# 5. Create PR (GitHub CLI)
gh pr create \
  --title "Add user profile page" \
  --body "Implements user profile with avatar upload"

# 6. Keep branch updated while PR is open
git checkout main
git pull
git checkout feature/user-profile
git merge main

# 7. Merge PR (via GitHub UI or CLI)
gh pr merge --squash --delete-branch

# 8. Update local main
git checkout main
git pull origin main
```

### Bug Fixes

```bash
# Same as feature development, but use bugfix/ prefix
git checkout -b bugfix/GH-123-login-error
# ... fix the bug ...
git add src/auth.py
git commit -m "fix: Resolve login timeout issue (fixes #123)"
git push origin bugfix/GH-123-login-error
gh pr create --title "Fix login timeout (closes #123)"
```

### Hotfixes (Production Emergencies)

```bash
# For critical production bugs requiring immediate fix

# 1. Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/payment-gateway-down

# 2. Make minimal fix
git add src/payment.py
git commit -m "hotfix: Fix payment gateway timeout"

# 3. Push and create PR with "hotfix" label
git push origin hotfix/payment-gateway-down
gh pr create \
  --title "[HOTFIX] Fix payment gateway timeout" \
  --label hotfix \
  --reviewer @tech-lead

# 4. Fast-track review and merge
# Reviewer approves immediately
# CI runs expedited checks
# Deploy to production ASAP

# 5. Monitor in production
# Watch error rates, metrics
```

### Keeping Branch Updated

```bash
# Regularly sync with main to avoid conflicts

# Method 1: Merge (preserves all commits)
git checkout feature/my-branch
git fetch origin
git merge origin/main

# Method 2: Rebase (cleaner history)
git checkout feature/my-branch
git fetch origin
git rebase origin/main

# If rebase conflicts:
# 1. Resolve conflicts
# 2. git add <resolved-files>
# 3. git rebase --continue
# 4. git push --force-with-lease
```

## Best Practices

### Branch Lifecycle

- **Create**: From up-to-date main
- **Lifespan**: Keep short (<3 days preferred)
- **Updates**: Merge main regularly (daily if possible)
- **Review**: Request review when feature complete
- **Merge**: Squash commits for clean history
- **Delete**: Immediately after merge

### Commit Messages

```bash
# Good
git commit -m "feat: Add user authentication API"
git commit -m "fix: Resolve memory leak in cache layer"
git commit -m "docs: Update API documentation"

# Bad
git commit -m "updates"
git commit -m "fixed stuff"
git commit -m "WIP"
```

See: [Commit Message Guide](./commit_message_correction.md)

### Code Review

- Request review when feature is complete and tested
- Respond to feedback promptly
- Don't take feedback personally
- Explain your reasoning when disagreeing
- Mark conversations as resolved

### Merge Strategy

**Use "Squash and Merge" for:**
- Feature branches with many commits
- Work-in-progress commits
- Cleaner main branch history

**Use "Merge Commit" for:**
- Large features needing preserved history
- Multiple developers on same branch
- Explicit merge points

**Use "Rebase and Merge" for:**
- Small, atomic changes
- Single-commit branches
- Linear history preference

## Common Scenarios

### Scenario 1: Feature Not Ready but Main Changed

```bash
# You're working on feature/A
# Main has new commits you need

git checkout main
git pull origin main
git checkout feature/A
git merge main
# Resolve conflicts if any
git push
```

### Scenario 2: Need to Switch Features Mid-Work

```bash
# Stash unfinished work
git stash push -m "WIP: User profile work"

# Switch to other feature
git checkout feature/other-work
# ... do urgent work ...
git commit -m "feat: Urgent feature"

# Return to original work
git checkout feature/A
git stash pop
# Continue working
```

### Scenario 3: Accidentally Committed to Main

```bash
# BEFORE pushing
git log  # Note commit SHA
git checkout -b feature/my-work
git checkout main
git reset --hard origin/main

# AFTER pushing (if you have admin access)
git checkout main
git reset --hard <commit-before-accident>
git push --force

# Safer alternative: revert
git revert <accidental-commit-sha>
git push
```

### Scenario 4: Need to Delete Remote Branch

```bash
# Delete local branch
git branch -d feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature

# Or use GitHub CLI
gh pr close <pr-number> --delete-branch
```

## Troubleshooting

### "Your branch is behind origin/main"

```bash
git pull origin main
# Or
git fetch origin
git rebase origin/main
```

### "Merge conflict"

```bash
# See conflicted files
git status

# Resolve each file manually
# Edit files, remove conflict markers (<<<<< ===== >>>>>)

# Mark as resolved
git add <resolved-file>

# Complete merge
git commit
```

See: [Merge Conflict Resolution](./merge_conflict_resolution.md)

### "Cannot delete branch - not fully merged"

```bash
# Branch has commits not in main
git branch -D feature/branch  # Force delete (lose commits)

# Or merge the branch first
git checkout main
git merge feature/branch
```

## FAQ

**Q: How long should branches live?**
A: Ideally <3 days. Long-lived branches cause merge conflicts.

**Q: Should I rebase or merge?**
A: Merge for safety. Rebase for clean history (but never rebase pushed commits).

**Q: Can I push directly to main?**
A: No, main is protected. Always use PRs.

**Q: What if CI fails?**
A: Fix the issue, commit, and push. PR will update automatically.

**Q: How many approvals needed?**
A: 1 approval for most PRs. 2 for infrastructure changes.

---

Last updated: 2025-10-26
Maintained by: @engineering-team
```

**Verification:**
- [ ] Documentation complete
- [ ] Examples cover common scenarios
- [ ] Troubleshooting section included
- [ ] Links to related workflows
- [ ] Accessible to entire team (wiki/README)

**If This Fails:**
→ If documentation too long, create quick-reference card  
→ If team doesn't read docs, conduct training session  
→ If unclear, add more examples and diagrams  

---

### Step 5: Configure CI/CD Integration

**What:** Set up continuous integration to validate branches automatically before merging.

**How:**
Configure automated checks that run on every push and pull request.

**GitHub Actions Workflow:**

```yaml
# .github/workflows/branch-ci.yml
name: Branch CI

on:
  push:
    branches:
      - main
      - develop
      - 'feature/**'
      - 'bugfix/**'
      - 'hotfix/**'
  pull_request:
    branches:
      - main
      - develop

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff mypy
          pip install -r requirements.txt
      
      - name: Run linting
        run: |
          ruff check src/
          mypy src/

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/ -ll
      
      - name: Run safety check
        run: |
          pip install safety
          safety check

  build:
    runs-on: ubuntu-latest
    needs: [lint, test, security]
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Test image
        run: |
          docker run myapp:${{ github.sha }} python -c "import src; print('OK')"

  deploy-preview:
    runs-on: ubuntu-latest
    needs: build
    if: |
      github.event_name == 'pull_request' &&
      startsWith(github.head_ref, 'feature/')
    steps:
      - name: Deploy to preview environment
        run: |
          echo "Deploying PR #${{ github.event.number }} to preview"
          # Deploy to preview environment
```

**Branch-Specific CI Rules:**

```yaml
# .github/workflows/main-only.yml
# Stricter checks for main branch
name: Main Branch CI

on:
  push:
    branches:
      - main

jobs:
  all-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # All checks from branch-ci.yml
      
      # Additional checks for main:
      - name: Integration tests
        run: pytest tests/integration/ -v
      
      - name: Performance tests
        run: pytest tests/performance/ --benchmark-only
      
      - name: Smoke tests in staging
        run: |
          # Deploy to staging
          # Run smoke tests
          
  deploy-production:
    needs: all-checks
    if: success()
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # Production deployment logic
```

**GitLab CI Configuration:**

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.11"

# Run on all branches
.base_job:
  image: python:${PYTHON_VERSION}
  before_script:
    - pip install -r requirements.txt

lint:
  extends: .base_job
  stage: validate
  script:
    - ruff check src/
    - mypy src/

test:
  extends: .base_job
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.10", "3.11", "3.12"]
  script:
    - pytest tests/ -v --cov=src
  coverage: '/TOTAL.*\s+(\d+%)$/'

security:
  extends: .base_job
  stage: validate
  script:
    - bandit -r src/ -ll
    - safety check

build:
  stage: build
  script:
    - docker build -t myapp:$CI_COMMIT_SHA .
  only:
    - main
    - develop
    - /^feature\/.*$/

deploy_staging:
  stage: deploy
  script:
    - echo "Deploying to staging"
  only:
    - develop
  environment:
    name: staging
    url: https://staging.example.com

deploy_production:
  stage: deploy
  script:
    - echo "Deploying to production"
  only:
    - main
  environment:
    name: production
    url: https://example.com
  when: manual
```

**Status Check Configuration:**

```bash
# Require specific checks before merge
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -F required_status_checks='{
    "strict": true,
    "contexts": [
      "lint",
      "test (3.10)",
      "test (3.11)",
      "test (3.12)",
      "security",
      "build"
    ]
  }'
```

**Verification:**
- [ ] CI workflow files created
- [ ] Workflows run on push/PR
- [ ] Status checks appear on PRs
- [ ] Required checks configured
- [ ] Team notified of CI requirements

**If This Fails:**
→ If workflows fail, check YAML syntax  
→ If checks don't run, verify branch patterns  
→ If too many checks, prioritize essential ones  

---

### Step 6: Train Team on Workflow

**What:** Ensure all team members understand and can execute the branching strategy.

**How:**
Conduct training sessions and provide hands-on practice.

**Training Session Outline:**

```markdown
# Branching Strategy Training
Duration: 60 minutes

## Agenda

### Part 1: Theory (15 min)
- Why we need a branching strategy
- Our chosen strategy (GitHub Flow)
- Branch hierarchy and protection
- Benefits and trade-offs

### Part 2: Hands-On (30 min)
- Create feature branch
- Make commits
- Push to remote
- Create pull request
- Review process
- Merge and cleanup

### Part 3: Q&A (15 min)
- Common scenarios
- Troubleshooting
- Questions and discussion
```

**Hands-On Exercise:**

```bash
# Exercise: Complete Feature Branch Workflow

# Step 1: Clone training repository
git clone git@github.com:org/training-repo.git
cd training-repo

# Step 2: Create feature branch
git checkout main
git pull origin main
git checkout -b feature/YOUR-NAME-hello-world

# Step 3: Make a change
echo "Hello from YOUR-NAME!" >> greetings.txt
git add greetings.txt
git commit -m "feat: Add greeting from YOUR-NAME"

# Step 4: Push to remote
git push -u origin feature/YOUR-NAME-hello-world

# Step 5: Create pull request
gh pr create --title "Add greeting from YOUR-NAME"

# Step 6: Request review from trainer
gh pr review --request @trainer

# Step 7: Make requested changes (trainer will comment)
echo "Additional greeting!" >> greetings.txt
git add greetings.txt
git commit -m "feat: Add additional greeting"
git push

# Step 8: Merge when approved
# Trainer will approve, then you merge via UI

# Step 9: Update main and clean up
git checkout main
git pull origin main
git branch -d feature/YOUR-NAME-hello-world
```

**Training Materials:**

```markdown
# Quick Reference Card

## Common Commands

```bash
# Start new feature
git checkout main && git pull
git checkout -b feature/my-feature

# Commit work
git add <files>
git commit -m "type: description"
git push

# Create PR
gh pr create

# Update branch
git fetch origin
git merge origin/main

# After merge
git checkout main && git pull
git branch -d feature/my-feature
```

## Commit Types
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests only
- `refactor:` Code restructure

## Branch Prefixes
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Production fixes

## Need Help?
- Docs: wiki/git-workflow
- Slack: #git-help
- Lead: @tech-lead
```

**Verification:**
- [ ] Training session conducted
- [ ] All team members completed exercise
- [ ] Quick reference distributed
- [ ] Questions addressed
- [ ] Follow-up scheduled (if needed)

**If This Fails:**
→ If team confused, schedule additional 1-on-1 sessions  
→ If exercise too complex, simplify first iteration  
→ If resistance to change, address concerns individually  

---

### Step 7: Monitor and Enforce

**What:** Track branch usage and enforce strategy compliance through automation and code review.

**How:**
Set up monitoring, alerts, and gentle enforcement mechanisms.

**Monitoring Dashboard:**

```python
# scripts/branch_monitoring.py
"""
Monitor branch health and compliance.
"""
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

def get_branch_metrics():
    """Analyze repository branch health."""
    
    # Get all branches
    result = subprocess.run(
        ['git', 'branch', '-r', '--format=%(refname:short)\t%(committerdate:iso)'],
        capture_output=True,
        text=True
    )
    
    branches = []
    for line in result.stdout.split('\n'):
        if line.strip():
            name, date = line.split('\t')
            branches.append({
                'name': name.replace('origin/', ''),
                'date': datetime.fromisoformat(date.strip())
            })
    
    # Analyze
    now = datetime.now()
    stale_branches = []
    invalid_names = []
    
    valid_prefixes = ['feature/', 'bugfix/', 'hotfix/', 'release/', 'docs/']
    
    for branch in branches:
        # Skip main/develop
        if branch['name'] in ['main', 'develop']:
            continue
        
        # Check age
        age = now - branch['date']
        if age > timedelta(days=30):
            stale_branches.append({
                'name': branch['name'],
                'age_days': age.days
            })
        
        # Check naming
        if not any(branch['name'].startswith(p) for p in valid_prefixes):
            invalid_names.append(branch['name'])
    
    return {
        'total_branches': len(branches),
        'stale_branches': stale_branches,
        'invalid_names': invalid_names
    }

def generate_report():
    """Generate branch health report."""
    metrics = get_branch_metrics()
    
    report = f"""
# Branch Health Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total branches: {metrics['total_branches']}
- Stale branches (>30 days): {len(metrics['stale_branches'])}
- Invalid naming: {len(metrics['invalid_names'])}

## Stale Branches (>30 days)
"""
    
    for branch in sorted(metrics['stale_branches'], key=lambda x: x['age_days'], reverse=True):
        report += f"- {branch['name']} ({branch['age_days']} days old)\n"
    
    if metrics['invalid_names']:
        report += "\n## Invalid Branch Names\n"
        for name in metrics['invalid_names']:
            report += f"- {name}\n"
    
    report += """
## Recommendations
- Review stale branches for deletion
- Fix invalid branch names
- Encourage short-lived branches (<7 days)
"""
    
    return report

if __name__ == '__main__':
    print(generate_report())
```

**Automated Cleanup:**

```yaml
# .github/workflows/branch-cleanup.yml
name: Branch Cleanup

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Find stale branches
        id: stale
        run: |
          # Find branches older than 30 days
          git for-each-ref --format='%(refname:short) %(committerdate:iso)' refs/remotes/origin/ | \
          while read branch date; do
            branch=${branch#origin/}
            [ "$branch" = "main" ] && continue
            [ "$branch" = "develop" ] && continue
            
            days_old=$(( ($(date +%s) - $(date -d "$date" +%s)) / 86400 ))
            if [ $days_old -gt 30 ]; then
              echo "$branch ($days_old days old)"
              echo "::warning::Branch $branch is $days_old days old"
            fi
          done
      
      - name: Create issue for stale branches
        uses: actions/github-script@v7
        with:
          script: |
            const stale = `${{ steps.stale.outputs }}`;
            if (stale) {
              github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: '🧹 Stale branches detected',
                body: `The following branches are older than 30 days:\n\n${stale}\n\nConsider deleting if no longer needed.`,
                labels: ['housekeeping']
              });
            }
```

**Enforcement Hooks:**

```bash
# .github/workflows/enforce-strategy.yml
name: Enforce Branch Strategy

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-compliance:
    runs-on: ubuntu-latest
    steps:
      - name: Check branch name
        run: |
          BRANCH="${{ github.head_ref }}"
          
          if [[ ! $BRANCH =~ ^(feature|bugfix|hotfix|release|docs)/ ]]; then
            echo "::error::Invalid branch name: $BRANCH"
            echo "Must start with: feature/, bugfix/, hotfix/, release/, or docs/"
            exit 1
          fi
      
      - name: Check branch age
        run: |
          # Check if branch is too old (>14 days)
          # Encourage merging or rebasing
          
      - name: Check commit count
        run: |
          # Warn if too many commits (suggest squashing)
```

**Metrics and Reporting:**

```bash
# Weekly report script
cat > scripts/weekly_branch_report.sh << 'EOF'
#!/bin/bash
# Generate weekly branch metrics

echo "# Weekly Branch Report - $(date +'%Y-%m-%d')"
echo ""

echo "## Active Branches"
git branch -r | grep -v "HEAD\|main\|develop" | wc -l

echo ""
echo "## Merged This Week"
git log --since='1 week ago' --oneline --merges | wc -l

echo ""
echo "## Average Branch Lifespan"
# Complex calculation here

echo ""
echo "## Top Contributors"
git shortlog -sn --since='1 week ago' | head -5

echo ""
echo "## Compliance"
echo "- Branches following naming convention: X%"
echo "- PRs with required reviews: Y%"
echo "- Average review time: Z hours"
EOF

chmod +x scripts/weekly_branch_report.sh
```

**Verification:**
- [ ] Monitoring script implemented
- [ ] Stale branch detection configured
- [ ] Enforcement workflows active
- [ ] Weekly reports scheduled
- [ ] Team receives metrics

**If This Fails:**
→ If too many alerts, adjust thresholds  
→ If enforcement too strict, add exceptions  
→ If team ignores reports, schedule review meetings  

---

### Step 8: Review and Iterate

**What:** Regularly review the branching strategy's effectiveness and adjust based on team feedback.

**How:**
Schedule retrospectives and gather metrics to improve the process.

**Retrospective Questions:**

```markdown
# Branching Strategy Retrospective

## What's Working Well?
- What aspects of the branch strategy are helpful?
- What makes your workflow smoother?
- What would you not want to change?

## What's Not Working?
- What friction points do you experience?
- What takes too long?
- What's confusing or unclear?

## Metrics Review
- Average branch lifespan: X days (target: <7)
- Merge conflicts per week: Y (target: <5)
- PR review time: Z hours (target: <24)
- Stale branches: N (target: <10)
- Naming compliance: M% (target: >95%)

## Proposed Changes
- [Team-suggested improvements]
- [Process adjustments]
- [Tool changes]

## Action Items
- [ ] Update documentation
- [ ] Adjust branch protection rules
- [ ] Additional training needed
- [ ] Tool improvements
```

**Feedback Collection:**

```bash
# Create feedback form
cat > docs/branch-strategy-feedback.md << 'EOF'
# Branch Strategy Feedback

## Quick Feedback

Rate your agreement (1-5):
- [ ] Branch naming is clear and intuitive
- [ ] PR process is efficient
- [ ] CI checks are valuable
- [ ] Documentation is helpful
- [ ] Training was adequate

## Open Feedback

**What frustrates you most about our git workflow?**


**What would make your workflow easier?**


**Any suggestions for improvement?**


Submit via: [Form URL] or email to @tech-lead
EOF
```

**Continuous Improvement:**

```python
# scripts/strategy_metrics.py
"""
Track branching strategy effectiveness over time.
"""
import subprocess
from datetime import datetime, timedelta
from statistics import mean

def calculate_metrics(days=30):
    """Calculate key metrics for last N days."""
    
    since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Average branch lifespan
    result = subprocess.run(
        ['git', 'log', '--since', since, '--merges', '--format=%H %P'],
        capture_output=True, text=True
    )
    
    lifespans = []
    for line in result.stdout.split('\n'):
        if not line:
            continue
        # Calculate time from branch creation to merge
        # ... implementation ...
    
    # Merge conflict rate
    conflicts = subprocess.run(
        ['git', 'log', '--since', since, '--grep', 'Merge conflict'],
        capture_output=True, text=True
    ).stdout.count('\n')
    
    # Review turnaround time (requires PR data from GitHub)
    # ... implementation ...
    
    return {
        'avg_branch_lifespan_days': mean(lifespans) if lifespans else 0,
        'merge_conflicts': conflicts,
        'total_merges': len(lifespans)
    }

# Track monthly and visualize trends
```

**Strategy Adjustments:**

```markdown
# Common Adjustments

## When to Simplify
**Symptoms:**
- Team confused by complex rules
- Low compliance
- Frequent mistakes

**Actions:**
- Remove release branches if not needed
- Simplify naming conventions
- Reduce protection rules

## When to Add Structure
**Symptoms:**
- Frequent merge conflicts
- Production incidents
- Lost work

**Actions:**
- Add more branch protection
- Require more reviews
- Implement stricter naming

## When to Change Strategy
**Symptoms:**
- Doesn't match deployment cadence
- Team size changed significantly
- Product needs evolved

**Actions:**
- Re-evaluate strategy choice
- Pilot new strategy with subset
- Plan migration carefully
```

**Verification:**
- [ ] Retrospective scheduled (monthly/quarterly)
- [ ] Feedback mechanism in place
- [ ] Metrics tracked over time
- [ ] Improvements documented
- [ ] Changes communicated to team

**If This Fails:**
→ If no feedback collected, make it easier (form vs email)  
→ If metrics show no improvement, investigate root causes  
→ If team resistant to changes, involve them in solutions  

---

## Verification Checklist

After completing this workflow:

- [ ] Branching strategy selected and documented
- [ ] Branch naming conventions established
- [ ] Branch protection rules configured
- [ ] Workflow documentation complete and accessible
- [ ] CI/CD integration configured
- [ ] Team trained on strategy
- [ ] Monitoring and enforcement set up
- [ ] Retrospective scheduled
- [ ] All team members can execute workflow
- [ ] First successful cycle completed

---

## Common Issues & Solutions

### Issue: "Too many long-lived branches"

**Symptoms:**
- 20+ active branches
- Branches older than 30 days
- Frequent merge conflicts

**Solution:**
```bash
# 1. Identify stale branches
git for-each-ref --sort=committerdate --format='%(refname:short) %(committerdate:relative)' refs/remotes/

# 2. Contact owners
for branch in $(git branch -r --format='%(refname:short)'); do
  echo "Branch: $branch"
  git log -1 --format='Last commit by: %an <%ae>' $branch
done

# 3. Delete after confirmation
git push origin --delete feature/old-branch

# 4. Implement policies
# - Weekly branch review meeting
# - Auto-notify on 7-day old branches
# - Encourage small, frequent PRs
```

**Prevention:**
- Set expectations: branches < 7 days
- Regular cleanup (weekly)
- Break large features into smaller PRs
- Use feature flags for long-running work

---

### Issue: "Frequent merge conflicts"

**Symptoms:**
- Conflicts on every merge
- Hours spent resolving conflicts
- Lost or duplicated work

**Solution:**
```bash
# 1. Increase merge frequency
# Merge main into feature branch daily
git checkout feature/my-branch
git fetch origin
git merge origin/main

# 2. Communicate large changes
# Before big refactors, announce in Slack
# Coordinate with team on timing

# 3. Use smaller PRs
# Break work into logical chunks
# Merge frequently

# 4. Pair programming
# For complex areas, work together
```

**Prevention:**
- Merge main into feature branches daily
- Communicate before large refactors
- Use linters to maintain consistent style
- Establish coding standards

---

### Issue: "CI takes too long"

**Symptoms:**
- 30+ minute CI runs
- Team waiting for checks
- Bypass CI to move faster

**Solution:**
```yaml
# 1. Parallelize tests
jobs:
  test:
    strategy:
      matrix:
        module: [api, frontend, backend, worker]
    steps:
      - run: pytest tests/${{ matrix.module }}

# 2. Run only affected tests on branches
- name: Run tests
  run: |
    if [ "${{ github.ref }}" != "refs/heads/main" ]; then
      pytest tests/unit/  # Fast tests only
    else
      pytest tests/  # All tests
    fi

# 3. Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

# 4. Optimize slowest tests
pytest --durations=10
```

**Prevention:**
- Review CI performance monthly
- Move slow tests to nightly builds
- Invest in faster CI infrastructure
- Use test impact analysis

---

### Issue: "Team bypasses branch protection"

**Symptoms:**
- Direct commits to main
- Merged without review
- CI checks skipped

**Solution:**
```bash
# 1. Verify protection rules
gh api repos/:owner/:repo/branches/main/protection

# 2. Include administrators in protection
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -F enforce_admins=true

# 3. Audit recent violations
git log --oneline main --since='1 week ago' --format='%H %an %s' | \
  grep -v "Merge pull request"

# 4. Discuss with team
# Understand why rules were bypassed
# Address legitimate concerns
# Reinforce importance of process
```

**Prevention:**
- Make exceptions rare (true emergencies only)
- Document bypass procedure
- Require approval from 2+ leads
- Post-mortem on bypasses

---

## Examples

### Example 1: Startup Using GitHub Flow

**Context:**
- 5-person team
- Deploy multiple times daily
- Fast iteration needed

**Strategy:**
```
main (production)
  ├── feature/user-profiles
  ├── feature/payment-integration
  └── bugfix/signup-error
```

**Configuration:**
```yaml
# Branch protection: main
- Require PR reviews: 1
- Require status checks: CI, Tests
- Enforce for admins: No
- Allow force push: No

# CI: Run on all branches
# Deploy: From main automatically

# Result:
# - Simple workflow, easy to learn
# - Fast merges (<1 hour)
# - Continuous deployment
```

---

### Example 2: Enterprise Using GitFlow

**Context:**
- 50-person team
- Monthly releases
- Support multiple versions

**Strategy:**
```
main (v1.5.0, v1.4.2)
├── develop
│   ├── feature/new-api
│   ├── feature/dashboard
│   └── bugfix/cache-issue
├── release/1.6.0
└── hotfix/critical-security
```

**Configuration:**
```yaml
# Branch protection: main, develop
main:
  - Require PR reviews: 2
  - Require status checks: Full CI Suite
  - Enforce for admins: Yes
  - Allow force push: No

develop:
  - Require PR reviews: 1
  - Require status checks: CI, Tests
  - Enforce for admins: Yes

# CI: Different checks per branch type
# Deploy: Manual from release branches

# Result:
# - Supports parallel releases
# - Clear version history
# - Stable production
```

---

### Example 3: Open Source Using Forking Workflow

**Context:**
- Community project
- External contributors
- Maintainer approval required

**Strategy:**
```
upstream/main
  ↓ fork
contributor/main
  ↓ branch
contributor/feature/new-docs
  ↓ PR to upstream
upstream/main (merged)
```

**Configuration:**
```yaml
# Branch protection: main
- Require PR reviews: 2 (maintainers)
- Require status checks: All CI
- Enforce for admins: Yes
- Require signed commits: Yes

# CI: Run on forks
# Deploy: Automatic from main

# Result:
# - Secure against untrusted code
# - Maintainer control
# - Contributor friendly
```

---

## Best Practices

### DO:
✅ Keep branches short-lived (<7 days)  
✅ Merge main frequently (daily)  
✅ Use descriptive branch names  
✅ Protect production branches  
✅ Require code reviews  
✅ Run CI on all branches  
✅ Delete branches after merge  
✅ Document the strategy  
✅ Train the team  
✅ Iterate based on feedback  

### DON'T:
❌ Let branches live for months  
❌ Allow direct commits to main  
❌ Skip code reviews  
❌ Use ambiguous branch names  
❌ Bypass CI checks  
❌ Keep stale branches  
❌ Over-complicate the strategy  
❌ Ignore team feedback  
❌ Change strategy without communication  
❌ Force new strategy without training  

---

## Related Workflows

**Prerequisites:**
- **development/developer_onboarding.md** - Git basics for new team members
- **version-control/commit_message_correction.md** - Commit message standards

**Next Steps:**
- **version-control/merge_conflict_resolution.md** - Handling conflicts
- **development/ci_cd_workflow.md** - Continuous integration setup
- **development/code_review_checklist.md** - Review process

**Related:**
- **development/pre_commit_hooks.md** - Enforce standards locally
- **project-management/knowledge_transfer.md** - Onboarding new developers

---

## Tags
`version-control` `git` `branching` `workflow` `github-flow` `gitflow` `collaboration`
