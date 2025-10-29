---
id: dev-014
title: Developer Onboarding
category: Development
subcategory: Team Management
tags:
  - onboarding
  - documentation
  - setup
  - team
  - workflow
  - standards
prerequisites:
  - dev-003  # Environment Initialization
  - dev-005  # New Repo Scaffolding
related_workflows:
  - dev-004  # Pre-commit Hooks
  - qa-001   # Code Review Checklist
  - pm-003   # Knowledge Transfer
complexity: intermediate
estimated_time: 2-4 hours
last_updated: 2025-10-25
---

# Developer Onboarding

## Overview

**What:** Comprehensive workflow for onboarding new developers to your team, project, or codebase, ensuring they're productive quickly while understanding team standards and workflows.

**Why:** Effective onboarding reduces time-to-productivity, improves code quality, strengthens team culture, and increases developer retention. A systematic onboarding process ensures consistency and prevents knowledge gaps.

**When to use:**
- Onboarding new hires to the team
- Transitioning contractors or consultants
- Bringing in developers from other teams
- Onboarding open-source contributors
- Refreshing existing team members on standards
- Documenting processes for future hires

---

## Prerequisites

**Required:**
- [ ] Access to version control system (GitHub, GitLab, etc.)
- [ ] Project repository access (read/write permissions)
- [ ] Communication tools access (Slack, Teams, email)
- [ ] Documentation repository or wiki access
- [ ] Development machine (laptop, cloud workspace)

**Organizational:**
- [ ] Onboarding checklist template
- [ ] Team contact list
- [ ] Project documentation (README, architecture docs)
- [ ] Development standards document
- [ ] CI/CD pipeline documentation

**Check before starting:**
```bash
# Verify team member has necessary access
git clone https://github.com/yourorg/project.git

# Check communication tools
# - Can send message in team channel
# - Can access shared documents
# - Has calendar access for meetings

# Verify development environment
python --version
node --version
docker --version
```

---

## Implementation Steps

### Step 1: Prepare Onboarding Materials

**What:** Create comprehensive documentation and checklists before the new developer starts.

**How:** Develop or update onboarding documentation that covers technical setup, team processes, and cultural norms.

**Create onboarding checklist** (`docs/ONBOARDING.md`):
```markdown
# Developer Onboarding Checklist

## Pre-Start (HR/IT)
- [ ] Email account created
- [ ] GitHub/GitLab account invited to organization
- [ ] Slack/Teams account created and added to channels
- [ ] Development machine ordered/configured
- [ ] VPN access provisioned
- [ ] Calendar invites sent for team meetings

## Day 1: Welcome & Setup
- [ ] Meet with manager/team lead
- [ ] Receive onboarding buddy assignment
- [ ] Tour of office/introduction to remote team norms
- [ ] Access to documentation wiki
- [ ] Setup development environment
- [ ] Clone repositories
- [ ] Review team communication guidelines
- [ ] Join team standups and meetings

## Week 1: Environment & Context
- [ ] Complete environment setup
- [ ] Run project locally
- [ ] Execute test suite successfully
- [ ] Make first small commit (fix typo, update docs)
- [ ] Attend architecture overview session
- [ ] Shadow code review process
- [ ] Read through project documentation
- [ ] Setup IDE with team conventions

## Week 2-4: First Tasks & Integration
- [ ] Complete first "good first issue"
- [ ] Participate in code review (reviewer role)
- [ ] Attend sprint planning/retrospective
- [ ] Pair program with team member
- [ ] Present work in team demo
- [ ] Contribute to team documentation
- [ ] Learn deployment process

## Month 2-3: Independence & Growth
- [ ] Take on medium-complexity features
- [ ] Lead feature development
- [ ] Mentor another new team member
- [ ] Contribute to architectural decisions
- [ ] Improve team processes/tooling
```

**Create developer guide** (`docs/DEVELOPER_GUIDE.md`):
```markdown
# Developer Guide

## Team Structure
- **Team Lead:** Alice Johnson (@alice)
- **Tech Lead:** Bob Smith (@bob)
- **Frontend:** Carol Davis (@carol), Dan Wilson (@dan)
- **Backend:** Eve Martinez (@eve), Frank Lee (@frank)
- **DevOps:** Grace Kim (@grace)

## Communication
- **Daily Standup:** 9:30 AM PST (Zoom link in calendar)
- **Slack Channels:**
  - #team-engineering (main channel)
  - #team-frontend, #team-backend (focus areas)
  - #deploys (deployment notifications)
  - #incidents (production issues)
- **Code Reviews:** Tag reviewers, respond within 24 hours
- **Office Hours:** Wednesdays 2-4 PM (ask any questions)

## Development Workflow
1. Pick ticket from sprint board (Jira/Linear)
2. Create feature branch: `feature/TICKET-123-description`
3. Develop with TDD (write tests first)
4. Run linters and tests locally
5. Push and create pull request
6. Request reviews from 2+ team members
7. Address feedback and merge
8. Verify in staging environment
9. Deploy to production (with approval)

## Code Standards
- **Language:** Python 3.11+, TypeScript 5.0+
- **Style Guide:** PEP 8 (Python), Airbnb (TypeScript)
- **Linters:** ruff, mypy, eslint, prettier
- **Test Coverage:** >80% for new code
- **Documentation:** Docstrings for all public functions

## Key Repositories
- `main-api` - Core REST API (FastAPI)
- `web-app` - Frontend application (React)
- `infrastructure` - Terraform configs
- `docs` - Confluence/documentation

## Getting Help
1. Check documentation wiki
2. Ask in #team-engineering
3. Reach out to onboarding buddy
4. Schedule 1:1 with team lead
5. Use office hours
```

**Create quick reference** (`docs/QUICK_REFERENCE.md`):
```markdown
# Quick Reference

## Common Commands
```bash
# Setup
make install              # Install dependencies
make setup-dev            # Setup dev environment

# Development
make run                  # Start local server
make test                 # Run test suite
make lint                 # Run linters
make format               # Format code

# Database
make db-migrate           # Run migrations
make db-reset             # Reset local DB

# Deployment
make deploy-staging       # Deploy to staging
make deploy-production    # Deploy to production
```

## Important Links
- [Sprint Board](https://jira.company.com/board/123)
- [CI/CD Dashboard](https://ci.company.com/pipelines)
- [API Documentation](https://api-docs.company.com)
- [Monitoring](https://datadog.company.com/dashboard)
- [On-Call Schedule](https://pagerduty.company.com)

## Emergency Contacts
- On-Call Engineer: Check PagerDuty
- Security Issues: security@company.com
- IT Support: it-help@company.com
```

**Verification:**
- [ ] Onboarding checklist covers all necessary steps
- [ ] Developer guide includes all team information
- [ ] Documentation is up-to-date with current processes
- [ ] Links work and point to correct resources
- [ ] Quick reference has accurate commands

**If This Fails:**
→ Review with existing team members for completeness
→ Test documentation by following it yourself
→ Update outdated information
→ Add missing sections based on team feedback

---

### Step 2: Setup Development Environment

**What:** Guide the new developer through setting up their local development environment with all necessary tools and configurations.

**How:** Provide step-by-step instructions for installing dependencies, configuring tools, and verifying the setup works correctly.

**Create environment setup script** (`scripts/setup_dev_environment.sh`):
```bash
#!/bin/bash
# Development Environment Setup Script
# For macOS/Linux (adjust for Windows if needed)

set -e  # Exit on error

echo "🚀 Setting up development environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v git >/dev/null 2>&1 || { echo "❌ git not found. Please install git."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found. Please install Python 3.11+"; exit 1; }

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher required. Found: $PYTHON_VERSION"
    exit 1
fi

# Install system dependencies (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected. Checking Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "📦 Installing system dependencies..."
    brew install postgresql@15 redis node
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Setup environment variables
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your local configuration"
fi

# Install Node dependencies (if applicable)
if [ -f "package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Setup database
echo "🗄️  Setting up database..."
createdb your_project_dev 2>/dev/null || echo "Database already exists"
python manage.py migrate

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
pytest tests/

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Update .env with your local configuration"
echo "3. Start development server: make run"
echo "4. Visit http://localhost:8000"
```

**Create IDE configuration guide** (`docs/IDE_SETUP.md`):
```markdown
# IDE Setup Guide

## VS Code (Recommended)

### Install Extensions
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "eamodio.gitlens",
    "github.copilot"
  ]
}
```

### Workspace Settings
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.rulers": [88]
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### Launch Configuration
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Python: Current Test File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"]
    }
  ]
}
```

## PyCharm

1. Open project directory
2. Configure Python interpreter:
   - Settings → Project → Python Interpreter
   - Select `venv/bin/python`
3. Enable pytest:
   - Settings → Tools → Python Integrated Tools
   - Default test runner: pytest
4. Configure ruff:
   - Settings → Tools → External Tools
   - Add ruff as external tool
5. Configure Black:
   - Settings → Tools → Black
   - Enable "On code reformat"

## Common Issues

### Issue: Python interpreter not found
**Solution:** 
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Import errors in IDE
**Solution:** Mark `src/` as sources root
- VS Code: Add to `python.analysis.extraPaths`
- PyCharm: Right-click `src/` → Mark Directory as → Sources Root
```

**Run setup script:**
```bash
# Make script executable
chmod +x scripts/setup_dev_environment.sh

# Run setup
./scripts/setup_dev_environment.sh

# Verify setup
source venv/bin/activate
python -c "import sys; print(f'Python: {sys.version}')"
pytest --version
ruff --version
```

**Verification:**
- [ ] Virtual environment created successfully
- [ ] All dependencies installed without errors
- [ ] Pre-commit hooks installed
- [ ] Database created and migrations run
- [ ] Tests pass successfully
- [ ] IDE configured correctly

**If This Fails:**
→ Check system requirements (Python version, OS compatibility)
→ Install missing system dependencies manually
→ Review error messages for specific issues
→ Check internet connection for package downloads
→ Consult team for environment-specific issues

---

### Step 3: Complete First Task ("Good First Issue")

**What:** Assign and guide the new developer through their first contribution to build confidence and familiarity with the workflow.

**How:** Select a well-scoped, low-risk task that touches key parts of the system and provides clear success criteria.

**Identify good first issues:**
```markdown
# Characteristics of Good First Issues:
- Clear, well-defined requirements
- Limited scope (4-8 hours of work)
- Touches multiple parts of system (exposure)
- Has example code to reference
- Clear verification criteria
- Low risk if mistakes made
- Provides opportunity for code review

# Examples:
1. Add input validation to existing endpoint
2. Add tests for uncovered code
3. Improve error messages
4. Add logging to a service
5. Update documentation
6. Refactor small utility function
7. Fix typo or formatting issue
```

**Example first issue** (GitHub issue template):
```markdown
# Good First Issue: Add Validation to User Email

## Description
Add validation to the user registration endpoint to ensure email addresses are valid format and not from disposable email domains.

## Context
- Endpoint: `POST /api/users/register`
- Current code: `src/api/routes/users.py:45-67`
- Related tests: `tests/unit/api/test_users.py`

## Requirements
1. Add email format validation (regex for valid email)
2. Add check against disposable email domain list
3. Return clear error message if validation fails
4. Add unit tests for validation logic
5. Update API documentation

## Implementation Hints
```python
# Example validation function structure
def validate_email(email: str) -> tuple[bool, str]:
    """Validate email address.
    
    Returns:
        (is_valid, error_message)
    """
    # 1. Check format with regex
    # 2. Check against disposable domains
    # 3. Return appropriate result
    pass

# Disposable domains list (for reference):
DISPOSABLE_DOMAINS = [
    "tempmail.com",
    "throwaway.email",
    "guerrillamail.com"
]
```

## Success Criteria
- [ ] Email format validation works
- [ ] Disposable domains are blocked
- [ ] Error messages are user-friendly
- [ ] Unit tests have >90% coverage
- [ ] All existing tests still pass
- [ ] API docs updated

## Resources
- Email regex pattern: [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322)
- Similar validation: `src/utils/validators.py:12-34`
- Test patterns: `tests/unit/api/test_auth.py`

## Time Estimate
4-6 hours

## Questions?
Ask in #team-engineering or reach out to @alice (onboarding buddy)
```

**Guide through the workflow:**
```bash
# 1. Create feature branch
git checkout main
git pull origin main
git checkout -b feature/USER-123-email-validation

# 2. Implement changes
# - Write tests first (TDD approach)
# - Implement validation function
# - Update endpoint to use validation
# - Update documentation

# 3. Run tests and linters locally
make test
make lint

# 4. Commit changes
git add .
git commit -m "feat: add email validation to user registration

- Add email format validation with regex
- Block disposable email domains
- Add comprehensive unit tests
- Update API documentation

Closes #USER-123"

# 5. Push and create pull request
git push origin feature/USER-123-email-validation

# 6. Create PR on GitHub
# - Use PR template
# - Add description and screenshots
# - Request reviews from team members

# 7. Address review feedback
# - Make requested changes
# - Push updates to same branch
# - Respond to comments

# 8. Merge after approval
# - Verify CI passes
# - Merge to main
# - Delete feature branch
```

**Pair programming session:**
```markdown
# Pair Programming Tips for First Task

## As Navigator (Experienced Developer):
- Explain architectural decisions
- Share keyboard shortcuts
- Point out common patterns
- Explain why code is structured a certain way
- Share debugging techniques
- Be patient with questions

## As Driver (New Developer):
- Ask questions about anything unclear
- Share your thought process out loud
- Don't hesitate to try things
- Take notes on patterns to remember
- Ask about alternatives

## Session Structure:
1. Review the issue together (5 min)
2. Plan approach (10 min)
3. Write tests first (20 min)
4. Implement feature (30 min)
5. Refactor and clean up (15 min)
6. Create PR together (10 min)
```

**Verification:**
- [ ] First task completed successfully
- [ ] Code merged to main branch
- [ ] PR process understood
- [ ] Developer comfortable with git workflow
- [ ] Developer can run tests locally
- [ ] Developer understands code review process

**If This Fails:**
→ Break task into smaller subtasks
→ Provide more detailed implementation guidance
→ Schedule additional pair programming sessions
→ Choose an even simpler first task
→ Address specific knowledge gaps (git, testing, etc.)

---

### Step 4: Shadow Code Review Process

**What:** Have the new developer observe and participate in code reviews to learn team standards and review practices.

**How:** Start by observing reviews, then reviewing simple PRs, and gradually increase complexity.

**Code review guidelines** (`docs/CODE_REVIEW.md`):
```markdown
# Code Review Guidelines

## Review Timeline
- **Response Time:** Within 24 hours of PR creation
- **Review Depth:** 15-30 minutes per PR
- **Approval Threshold:** 2 approvals required

## What to Review

### Functionality
- [ ] Code does what PR description says
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No obvious bugs

### Testing
- [ ] New code has tests
- [ ] Tests are meaningful (not just for coverage)
- [ ] Tests follow existing patterns
- [ ] All tests pass in CI

### Code Quality
- [ ] Code is readable and maintainable
- [ ] Naming is clear and consistent
- [ ] Functions are focused (single responsibility)
- [ ] No unnecessary complexity
- [ ] Follows project conventions

### Documentation
- [ ] Public APIs have docstrings
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] Breaking changes documented

### Security
- [ ] No sensitive data exposed
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] XSS vulnerabilities addressed

## How to Give Feedback

### Good Feedback
✅ **Be specific:**
"The error message on line 45 could be more descriptive. Consider mentioning which field failed validation."

✅ **Explain why:**
"We should use a constant here instead of a magic number because it's used in multiple places and easier to maintain."

✅ **Offer alternatives:**
"Instead of a nested if here, consider using early returns for better readability."

✅ **Ask questions:**
"What happens if the user_id is None here? Should we add a check?"

✅ **Appreciate good work:**
"Great test coverage! I especially like how you tested the edge cases."

### Bad Feedback
❌ **Too vague:**
"This code is bad."

❌ **Personal attacks:**
"Did you even test this?"

❌ **Nitpicky without reason:**
"Use single quotes instead of double quotes." (when no style guide specifies)

❌ **No explanation:**
"Don't do it this way."

## Review Levels

### 🟢 Minor (Quick approve)
- Documentation updates
- Test additions
- Typo fixes
- Code formatting

### 🟡 Normal (Standard review)
- Feature additions
- Bug fixes
- Refactoring
- Most PRs

### 🔴 Major (Detailed review)
- Architecture changes
- Security-related changes
- Database migrations
- API contract changes
- Performance-critical code

## Review Checklist Template
```markdown
## Review Checklist
- [ ] Code accomplishes stated goal
- [ ] Tests are comprehensive
- [ ] No obvious bugs or issues
- [ ] Code is maintainable
- [ ] Follows team conventions
- [ ] Documentation is adequate
- [ ] No security concerns

## Comments
[Your feedback here]

## Verdict
- ✅ Approved
- 💬 Approved with comments
- 🔄 Request changes
```

**Shadow review process:**

Week 1: **Observe**
```markdown
# New developer shadows 5+ code reviews

## Activity:
1. Watch senior developer review PR
2. Take notes on what they look for
3. Ask questions about decisions
4. Learn review tool features

## Questions to Consider:
- What did reviewer check first?
- How did they phrase feedback?
- What made them approve/reject?
- What was the back-and-forth process?
```

Week 2: **Practice**
```markdown
# New developer reviews simple PRs with oversight

## Activity:
1. Review documentation/test PRs
2. Leave comments (don't approve yet)
3. Senior developer reviews your review
4. Discuss feedback quality

## Focus Areas:
- Clarity of feedback
- Catching real issues
- Balancing thoroughness with speed
```

Week 3+: **Independent**
```markdown
# New developer conducts full reviews

## Activity:
1. Review all types of PRs
2. Provide approval/request changes
3. Self-reflect on review quality
4. Ask for feedback on reviews

## Goal:
- Become trusted reviewer
- Maintain team standards
- Help others improve
```

**Example review workflow:**
```bash
# 1. Check out PR branch locally
git fetch origin
git checkout pr-branch-name

# 2. Review the changes
git diff main...HEAD

# 3. Run tests and linters
make test
make lint

# 4. Test the feature manually
# - Start application
# - Test happy path
# - Test edge cases
# - Check error messages

# 5. Leave review comments
# - Use GitHub/GitLab review interface
# - Be specific and constructive
# - Use review template

# 6. Approve or request changes
# - ✅ Approve if all looks good
# - 💬 Comment for discussion
# - 🔄 Request changes if issues found
```

**Verification:**
- [ ] Developer has observed 5+ code reviews
- [ ] Developer has reviewed 3+ simple PRs
- [ ] Developer understands review criteria
- [ ] Developer can give constructive feedback
- [ ] Developer is added to CODEOWNERS file

**If This Fails:**
→ Provide review checklist to follow
→ Pair on reviews with experienced developer
→ Start with even simpler PRs (docs only)
→ Provide feedback on the feedback given
→ Review CODE_REVIEW.md guidelines together

---

### Step 5: Learn Deployment Process

**What:** Teach the new developer how to deploy code to staging and production environments safely.

**How:** Walk through deployment process, explain safeguards, and practice with staging deployments.

**Deployment documentation** (`docs/DEPLOYMENT.md`):
```markdown
# Deployment Guide

## Environments

### Development (Local)
- **Purpose:** Local development and testing
- **URL:** http://localhost:8000
- **Database:** Local PostgreSQL
- **Deploys:** Automatic on code change (hot reload)

### Staging
- **Purpose:** Pre-production testing and QA
- **URL:** https://staging.example.com
- **Database:** Staging PostgreSQL (anonymized prod data)
- **Deploys:** Automatic on merge to `develop` branch
- **Access:** Team members + QA team

### Production
- **Purpose:** Live customer-facing application
- **URL:** https://api.example.com
- **Database:** Production PostgreSQL
- **Deploys:** Manual approval required
- **Access:** All authenticated users

## Deployment Process

### Automatic: Merge to Develop → Staging
```bash
# 1. Merge PR to develop branch
git checkout develop
git pull origin develop
git merge feature/my-feature

# 2. CI/CD automatically:
# - Runs all tests
# - Builds Docker image
# - Deploys to staging
# - Runs smoke tests

# 3. Verify in staging
curl https://staging.example.com/health
# Visit staging URL and test manually
```

### Manual: Staging → Production
```bash
# 1. Create release PR
git checkout main
git checkout -b release/v1.2.3
git merge develop

# 2. Update version
# Update VERSION file or package.json

# 3. Create PR to main
# Requires approval from 2+ senior engineers

# 4. Deploy to production
# After PR merged, trigger production deploy in CI/CD
# Or run: make deploy-production

# 5. Monitor deployment
# Watch metrics, logs, error rates
# Be ready to rollback if needed
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing in CI
- [ ] Code reviewed and approved
- [ ] Database migrations reviewed
- [ ] Feature flags configured
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Team notified in #deploys channel

### During Deployment
- [ ] Post in #deploys: "Deploying v1.2.3 to production"
- [ ] Monitor deployment progress
- [ ] Check health endpoint
- [ ] Verify key metrics (error rate, latency)
- [ ] Run smoke tests
- [ ] Check logs for errors

### Post-Deployment
- [ ] Verify features work in production
- [ ] Check error rates (should be normal)
- [ ] Monitor for 15 minutes
- [ ] Post in #deploys: "v1.2.3 deployed successfully ✅"
- [ ] Update deployment log
- [ ] Close deployment incident

## Rollback Procedure

### When to Rollback
- Error rate increases >2x baseline
- Critical feature broken
- Database corruption
- Security vulnerability discovered
- Customer-facing issue

### How to Rollback
```bash
# Option 1: Revert commit (small change)
git revert <commit-hash>
git push origin main

# Option 2: Rollback to previous version (large change)
# In CI/CD dashboard:
# 1. Select previous successful deployment
# 2. Click "Rollback to this version"
# 3. Confirm

# Option 3: Manual (emergency)
# SSH to server
ssh production-server
cd /app
git checkout <previous-version>
sudo systemctl restart app

# Post-rollback:
# 1. Notify team in #deploys
# 2. Create incident ticket
# 3. Schedule post-mortem
```

## Database Migrations

### Running Migrations

**Staging:**
```bash
# Migrations run automatically on deploy
# Check logs to verify:
kubectl logs -f deployment/api -n staging | grep migrate
```

**Production:**
```bash
# Migrations require manual trigger
# 1. Review migration SQL
# 2. Test in staging first
# 3. Take database backup
# 4. Run migration
make db-migrate-production

# 5. Verify migration
make db-check-production
```

### Migration Safeguards
- [ ] Backward compatible (can rollback code)
- [ ] Tested in staging with prod-size data
- [ ] Non-blocking (doesn't lock tables)
- [ ] Can be run multiple times (idempotent)
- [ ] Has rollback script

## Monitoring During Deployment

### Key Metrics to Watch
```bash
# Error Rate (should stay < 1%)
# Latency (p95 should stay < 200ms)
# Request Rate (should be stable)
# Database Connections (should not spike)
```

### Dashboards to Check
- [Main Dashboard](https://datadog.com/dashboard/main)
- [Error Tracking](https://sentry.io/project)
- [Logs](https://logs.example.com)

## Common Deployment Issues

### Issue: Health check failing
```bash
# Check logs
kubectl logs -f deployment/api

# Common causes:
# - Database connection failed
# - Environment variable missing
# - Service dependency down

# Fix and redeploy
```

### Issue: Tests passing but deployment failing
```bash
# Check deployment logs
# Common causes:
# - Missing secret/config in production
# - Infrastructure issue
# - Resource limits exceeded

# Contact DevOps team
```
```

**Practice deployment:**
```bash
# Week 1: Shadow deployments
# Watch experienced developer deploy
# Take notes on process
# Learn monitoring tools

# Week 2: Deploy to staging
# Make small change
# Deploy to staging yourself
# Monitor metrics
# Verify deployment successful

# Week 3+: Production deploys
# With supervision initially
# Can deploy independently after 5+ successful deploys
```

**Verification:**
- [ ] Developer understands deployment environments
- [ ] Developer can deploy to staging independently
- [ ] Developer knows how to monitor deployments
- [ ] Developer understands rollback process
- [ ] Developer has practiced emergency rollback in staging

**If This Fails:**
→ Create step-by-step deployment script
→ Provide more supervised deployment practice
→ Set up test deployments to learn environment
→ Review deployment documentation together
→ Schedule deployment training session

---

### Step 6: Integrate with Team Culture

**What:** Help the new developer understand and adopt team norms, communication patterns, and collaborative practices.

**How:** Facilitate relationship building, explain unwritten rules, and encourage active participation in team activities.

**Team culture guide** (`docs/TEAM_CULTURE.md`):
```markdown
# Team Culture & Norms

## Communication Principles

### Async First
- Default to written communication (Slack, GitHub)
- Reduces meeting overhead
- Respects different time zones
- Creates searchable record

### Meeting Etiquette
- Cameras optional but encouraged
- Mute when not speaking
- Use reactions to avoid talking over
- Share screen when presenting
- Take notes in shared doc

### Response Time Expectations
- **Slack DM:** 4 hours during work hours
- **PR Review:** 24 hours
- **Email:** 48 hours
- **Urgent (tagged @here):** 30 minutes
- **Emergency (PagerDuty):** Immediate

## Team Rituals

### Daily Standup (9:30 AM PST)
**Format:** 15 minutes, everyone shares:
- What you did yesterday
- What you're doing today
- Any blockers

**Tips:**
- Keep it brief (1-2 minutes)
- Be specific about work
- Ask for help if blocked
- Skip if nothing to report

### Sprint Planning (Every 2 weeks)
- Review upcoming work
- Break down stories
- Commit to sprint goals
- Ask questions about requirements

### Retrospective (Every 2 weeks)
- What went well
- What could improve
- Action items for next sprint
- Safe space for feedback

### Demo Day (Fridays)
- Show what you built
- 5-10 minute demos
- Get feedback
- Celebrate wins

### Office Hours (Wednesdays 2-4 PM)
- Open forum for questions
- No question too small
- Learn from others' questions
- Build relationships

## Collaboration Norms

### Asking for Help
✅ **Do:**
- Share what you've tried
- Provide context and error messages
- Ask in public channels when possible
- Follow up when resolved

❌ **Don't:**
- Suffer in silence
- Wait days before asking
- Ask without trying first
- Forget to say thank you

### Giving Feedback
✅ **Do:**
- Focus on behavior, not person
- Be specific and constructive
- Assume positive intent
- Praise in public, criticize in private

❌ **Don't:**
- Attack personally
- Be vague
- Save feedback for retrospective
- Forget to follow up

### Decisions
- **Type 1 (Reversible):** Decide yourself, inform team
- **Type 2 (Hard to reverse):** Discuss with team first
- Document significant decisions in ADRs
- Explain reasoning in PR descriptions

## Social Norms

### Remote Work
- Core hours: 10 AM - 3 PM PST (overlap time)
- Set Slack status when away
- Update calendar with OOO/Focus time
- Respond within working hours

### Work-Life Balance
- Don't expect responses outside work hours
- Use scheduled send for after-hours messages
- Take breaks and vacation
- No hero culture - ask for help
- Sustainable pace over crunch

### Team Building
- Monthly team lunch (remote friendly)
- Quarterly off-site
- Slack channels: #random, #pets, #gaming
- Optional social events

## Unwritten Rules

### Code Ownership
- No "my code" vs "your code"
- Everyone can modify anything
- Original author not always best reviewer
- Shared responsibility for quality

### Documentation
- If you learn something, document it
- Update docs as you go
- Don't hoard knowledge
- Write for future you (6 months later)

### Quality Bar
- Working > perfect
- Ship incrementally
- Refactor continuously
- Tests are not optional
- Leave code better than you found it

### Debugging
- Reproduce before fixing
- Share findings in Slack
- Document unknowns
- Add tests for bugs
```

**Relationship building activities:**
```markdown
## Week 1: Meet the Team

### 1:1 Coffee Chats (30 min each)
- Team Lead
- Tech Lead
- Onboarding Buddy
- 2-3 team members in different roles
- 1 person from another team you'll work with

### Questions to Ask:
- How did you join the company?
- What's your favorite project you've worked on?
- What's something you wish you knew earlier?
- What do you like about working here?
- What are your interests outside work?

## Week 2: Team Activities

### Attend Social Events
- Team lunch
- Coffee breaks
- After-work hangouts
- Show and tell sessions

### Participate in Channels
- Share wins in #wins channel
- Post in #random
- React to messages
- Share helpful resources

## Month 1: Build Relationships

### Pair Programming
- Schedule sessions with different team members
- Learn their working style
- Share your perspective
- Build rapport

### Lunch Roulette
- Random lunch pairings
- Learn about different roles
- Expand network
- Build informal connections
```

**Verification:**
- [ ] Developer has met all team members
- [ ] Developer actively participates in standups
- [ ] Developer asks questions in team channels
- [ ] Developer has paired with 3+ team members
- [ ] Developer understands team communication norms

**If This Fails:**
→ Assign more structured 1:1 meetings
→ Encourage participation in team channels
→ Provide conversation starters
→ Check in weekly about integration
→ Address any team dynamics issues

---

### Step 7: First Month Review & Feedback

**What:** Conduct structured feedback sessions to assess progress, address concerns, and set goals for continued growth.

**How:** Schedule regular check-ins, gather feedback, and create development plan based on strengths and areas for improvement.

**30-day review template:**
```markdown
# 30-Day Onboarding Review

**Developer:** [Name]
**Manager:** [Name]
**Date:** [Date]
**Onboarding Buddy:** [Name]

## Technical Skills Assessment

### Environment Setup
- [ ] Can run project locally
- [ ] Understands project architecture
- [ ] Comfortable with development tools
- [ ] Can navigate codebase

**Rating:** ⭐⭐⭐⭐⭐ (1-5)
**Comments:**

### Code Quality
- [ ] Writes clean, maintainable code
- [ ] Follows team conventions
- [ ] Writes comprehensive tests
- [ ] Uses appropriate patterns

**Rating:** ⭐⭐⭐⭐⭐
**Comments:**

### Code Review
- [ ] Provides thoughtful feedback
- [ ] Catches meaningful issues
- [ ] Communicates constructively
- [ ] Understands approval criteria

**Rating:** ⭐⭐⭐⭐⭐
**Comments:**

### Workflow Mastery
- [ ] Understands git workflow
- [ ] Can create good PRs
- [ ] Knows deployment process
- [ ] Uses CI/CD effectively

**Rating:** ⭐⭐⭐⭐⭐
**Comments:**

## Team Integration

### Communication
- [ ] Participates in standups
- [ ] Asks questions appropriately
- [ ] Shares progress and blockers
- [ ] Collaborates effectively

**Rating:** ⭐⭐⭐⭐⭐
**Comments:**

### Culture Fit
- [ ] Understands team norms
- [ ] Collaborates well
- [ ] Embraces feedback
- [ ] Contributes to culture

**Rating:** ⭐⭐⭐⭐⭐
**Comments:**

## Completed Work

### Tasks Completed
1. [Task 1 - Brief description]
2. [Task 2 - Brief description]
3. [Task 3 - Brief description]

### Quality of Work
**Rating:** ⭐⭐⭐⭐⭐
**Comments:**

### Impact
**Rating:** ⭐⭐⭐⭐⭐
**Comments:**

## Feedback from Team

### Onboarding Buddy Feedback
> [Quote from onboarding buddy]

### Peer Feedback
> [Quote from peer review or collaboration]

### Code Review Feedback
> [Summary of code review comments/trends]

## Strengths

1. **[Strength 1]**
   - Examples: [Specific instances]

2. **[Strength 2]**
   - Examples: [Specific instances]

3. **[Strength 3]**
   - Examples: [Specific instances]

## Areas for Growth

1. **[Area 1]**
   - Current state: [Description]
   - Goal: [What success looks like]
   - Action plan: [Steps to improve]

2. **[Area 2]**
   - Current state: [Description]
   - Goal: [What success looks like]
   - Action plan: [Steps to improve]

## Goals for Next 30 Days

### Technical Goals
1. [Specific, measurable goal]
2. [Specific, measurable goal]
3. [Specific, measurable goal]

### Process Goals
1. [Specific, measurable goal]
2. [Specific, measurable goal]

### Team Goals
1. [Specific, measurable goal]
2. [Specific, measurable goal]

## Support Needed

**From Manager:**
- [Specific support needed]

**From Team:**
- [Specific support needed]

**Resources/Training:**
- [Specific resources needed]

## Overall Assessment

**Onboarding Progress:** 
- [ ] Ahead of expectations
- [ ] Meeting expectations
- [ ] Needs additional support

**Ready for Independent Work:**
- [ ] Yes, ready for normal sprint work
- [ ] Mostly, still needs guidance in [areas]
- [ ] No, continue focused onboarding

**Comments:**
[Overall assessment and next steps]

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action 1] | [Person] | [Date] | 🔲 |
| [Action 2] | [Person] | [Date] | 🔲 |
| [Action 3] | [Person] | [Date] | 🔲 |

## Next Review
**Date:** [60-day review date]
**Focus Areas:** [Specific areas to assess]

---

**Signatures:**

Manager: _________________ Date: _______
Developer: _________________ Date: _______
```

**Continuous feedback process:**
```markdown
## Weekly Check-ins (Weeks 1-4)

### Format: 30 minutes
- How's onboarding going?
- Any blockers or confusion?
- What's going well?
- What support do you need?

### Template
1. **Wins this week:**
   - [What went well]

2. **Challenges:**
   - [What was difficult]
   - [Help needed]

3. **Learning:**
   - [New things learned]
   - [Areas still unclear]

4. **Action items:**
   - [ ] [To do for next week]

## Monthly Check-ins (Months 2-6)

### Format: 60 minutes
- Review progress on goals
- Discuss career development
- Address any concerns
- Set new goals
- Provide feedback

### Topics
- Technical skill development
- Project assignments
- Team dynamics
- Career aspirations
- Work-life balance
```

**Verification:**
- [ ] 30-day review completed
- [ ] Feedback documented
- [ ] Goals set for next period
- [ ] Developer feels supported
- [ ] Action items identified

**If This Fails:**
→ Schedule more frequent check-ins
→ Provide more specific feedback
→ Adjust goals to be more achievable
→ Increase mentorship support
→ Address concerns promptly

---

### Step 8: Long-term Development Planning

**What:** Create personalized growth plan aligned with developer's career goals and team needs.

**How:** Identify skill gaps, set development goals, and provide opportunities for growth through projects, mentorship, and training.

**Development plan template** (`docs/DEVELOPMENT_PLAN.md`):
```markdown
# Individual Development Plan

**Developer:** [Name]
**Manager:** [Name]
**Period:** [Date Range]
**Review Date:** [Next Review]

## Career Goals

### Short-term (6 months)
- [Goal 1]
- [Goal 2]
- [Goal 3]

### Long-term (1-2 years)
- [Goal 1]
- [Goal 2]
- [Goal 3]

### Aspirations
- [Career direction]
- [Desired role]
- [Skills to develop]

## Current Skills Assessment

### Technical Skills
| Skill | Current Level | Target Level | Priority |
|-------|--------------|--------------|----------|
| Python | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | High |
| TypeScript | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium |
| PostgreSQL | ⭐⭐ | ⭐⭐⭐⭐ | High |
| Docker/K8s | ⭐⭐ | ⭐⭐⭐ | Low |

### Soft Skills
| Skill | Current Level | Target Level | Priority |
|-------|--------------|--------------|----------|
| Communication | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | High |
| Leadership | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium |
| Mentoring | ⭐⭐ | ⭐⭐⭐⭐ | Medium |

## Development Activities

### Projects
1. **Lead [Project Name]**
   - Goal: Gain experience leading feature development
   - Timeline: Q2 2025
   - Success metrics: Feature shipped on time, team satisfaction

2. **Contribute to [Infrastructure Project]**
   - Goal: Learn DevOps and infrastructure
   - Timeline: Ongoing
   - Success metrics: Deploy infrastructure change independently

### Learning Resources
- [ ] Complete [Online Course Name]
- [ ] Read [Book Name]
- [ ] Attend [Conference Name]
- [ ] Complete [Certification]

### Mentorship
- **Mentor:** [Senior Developer Name]
- **Focus:** [Specific skill/area]
- **Cadence:** Weekly 1:1s
- **Goals:** [Learning objectives]

### Stretch Assignments
- Lead technical design for [Feature]
- Present at team tech talk
- Mentor junior developer
- Contribute to open source

## Quarterly Goals

### Q1 2025
1. **Technical:**
   - [ ] Improve test coverage to 85%
   - [ ] Learn and implement caching strategy
   - [ ] Optimize API response times by 30%

2. **Process:**
   - [ ] Conduct 20+ code reviews
   - [ ] Document 3 team processes
   - [ ] Lead 2 knowledge sharing sessions

3. **Leadership:**
   - [ ] Mentor 1 junior developer
   - [ ] Lead sprint planning
   - [ ] Present at engineering all-hands

## Progress Tracking

### Monthly Milestones
- **Month 1:** [Milestone]
- **Month 2:** [Milestone]
- **Month 3:** [Milestone]

### Review Schedule
- Weekly: Progress check-ins
- Monthly: Review goals and adjust
- Quarterly: Formal review and new goals

## Support and Resources

### Training Budget
- Amount: $2,000/year
- Approved courses: [List]
- Conference budget: $1,500/year

### Time Allocation
- Learning time: 10% (4 hours/week)
- Mentorship: 2 hours/week
- Side projects: As available

### Tools and Access
- [ ] Premium learning platform subscription
- [ ] Conference tickets
- [ ] Books and resources
- [ ] Certification exam fees
```

**Growth opportunities:**
```markdown
## Ways to Grow

### Technical Depth
- Own complex technical problems
- Design architectural solutions
- Optimize performance
- Improve system reliability
- Learn new technologies

### Technical Breadth
- Work across tech stack
- Learn adjacent technologies
- Understand infrastructure
- Explore different domains
- Contribute to various projects

### Leadership
- Mentor junior developers
- Lead technical initiatives
- Facilitate technical discussions
- Make architectural decisions
- Represent team in meetings

### Specialization
- Become domain expert
- Deep dive into technology
- Contribute to ecosystem
- Write technical content
- Speak at conferences
```

**Verification:**
- [ ] Development plan created and documented
- [ ] Goals aligned with career aspirations
- [ ] Clear path for skill development
- [ ] Regular progress reviews scheduled
- [ ] Support and resources identified

**If This Fails:**
→ Break goals into smaller, achievable milestones
→ Provide more specific learning resources
→ Adjust timeline to be more realistic
→ Increase frequency of check-ins
→ Align goals with team priorities

---

## Verification Checklist

After completing this workflow:

- [ ] Onboarding materials created and documented
- [ ] Development environment setup successfully
- [ ] First task completed and merged
- [ ] Code review process understood
- [ ] Deployment process learned
- [ ] Integrated with team culture
- [ ] 30-day review completed
- [ ] Development plan created
- [ ] Developer is productive and confident
- [ ] Team welcomes and supports new member

---

## Best Practices

### DO:
✅ Create comprehensive onboarding documentation
✅ Assign an onboarding buddy for guidance
✅ Start with simple, well-defined tasks
✅ Provide regular feedback and check-ins
✅ Encourage questions and learning
✅ Build relationships and team connections
✅ Set clear expectations and goals
✅ Celebrate early wins and progress
✅ Be patient with learning curve
✅ Adjust onboarding based on individual needs
✅ Document tribal knowledge
✅ Create safe environment for questions

### DON'T:
❌ Throw new developer into complex tasks immediately
❌ Assume they know unwritten rules
❌ Forget to follow up and check progress
❌ Neglect social/cultural integration
❌ Overwhelm with too much information at once
❌ Skip formal feedback sessions
❌ Leave them to figure everything out alone
❌ Expect immediate productivity
❌ Use outdated or incomplete documentation
❌ Ignore signs of struggle or confusion

---

## Common Patterns

### Pattern 1: Onboarding Buddy System
```markdown
## Buddy Responsibilities

### Week 1:
- Daily check-ins (15 min)
- Answer questions
- Tour of codebase
- Introduce to team members

### Weeks 2-4:
- 3x weekly check-ins
- Pair programming sessions
- Code review guidance
- Process questions

### Months 2-3:
- Weekly check-ins
- Available for questions
- Career advice
- Team integration
```

### Pattern 2: Progressive Complexity
```markdown
## Task Difficulty Progression

### Week 1: Trivial
- Fix typos
- Update documentation
- Format code

### Week 2: Simple
- Add tests
- Add input validation
- Simple bug fixes

### Week 3-4: Moderate
- Small features
- Refactoring
- Integration work

### Month 2+: Complex
- Full features
- Architecture decisions
- Cross-team collaboration
```

### Pattern 3: Learning Tracks
```markdown
## Specialized Learning Paths

### Backend Track
1. API design and implementation
2. Database optimization
3. Caching strategies
4. Background job processing
5. Microservices architecture

### Frontend Track
1. Component design
2. State management
3. Performance optimization
4. Accessibility
5. Testing strategies

### Full-Stack Track
- Combination of both
- Focus on integration
- End-to-end features
```

---

## Troubleshooting

### Issue: New developer seems overwhelmed

**Symptoms:**
- Not asking questions
- Missing deadlines
- Disengaged in meetings
- Struggling with tasks

**Solutions:**
- Reduce scope of assignments
- Increase check-in frequency
- Pair more often with experienced developers
- Break tasks into smaller pieces
- Address any specific concerns directly

**Prevention:**
- Monitor early warning signs
- Create psychologically safe environment
- Normalize asking for help
- Set realistic expectations
- Provide clear support channels

---

### Issue: Onboarding documentation is outdated

**Symptoms:**
- Setup instructions don't work
- Links are broken
- Process has changed
- New tools not documented

**Solutions:**
```bash
# 1. Audit all onboarding docs
find docs/ -name "*onboarding*" -o -name "*setup*"

# 2. Test setup process yourself
# Follow docs exactly as written
# Note any issues

# 3. Update docs
# Fix broken links
# Update outdated information
# Add missing sections

# 4. Create maintenance schedule
# Review quarterly
# Update after major changes
# Assign doc ownership
```

**Prevention:**
- Review docs with each new hire
- Assign doc ownership
- Update docs immediately when processes change
- Include in code review checklist

---

### Issue: New developer not integrating with team

**Symptoms:**
- Doesn't participate in discussions
- Works in isolation
- Misses team events
- Doesn't build relationships

**Solutions:**
- Schedule more 1:1s with team members
- Assign buddy to facilitate introductions
- Encourage participation in social channels
- Include in team decision-making
- Address any team dynamics issues

**Prevention:**
- Proactive team introductions
- Structured social activities
- Inclusive team culture
- Regular relationship-building opportunities

---

## Related Workflows

**Prerequisites:**
- [[environment_initialization]] - Setup before onboarding
- [[new_repo_scaffolding]] - Project structure understanding

**Next Steps:**
- [[knowledge_transfer]] - Document knowledge for future onboarding
- [[pair_programming_ai]] - Ongoing collaboration practices
- [[code_review_checklist]] - Detailed review practices

**Related:**
- [[pre_commit_hooks]] - Setup development tooling
- [[ci_cd_workflow]] - Understanding automation
- [[developer_documentation]] - Creating documentation

---

## Tags
`development` `onboarding` `documentation` `team` `workflow` `standards` `mentoring` `culture` `training` `management`
