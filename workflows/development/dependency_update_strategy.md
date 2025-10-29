# Dependency Update Strategy

**ID:** dev-019  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 2-3 hours (initial setup), ongoing maintenance  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Establish a comprehensive strategy and policy for managing dependency updates, balancing security, stability, and keeping dependencies current.

**Why:** Without a clear strategy, dependencies either go stale (security risks, compatibility issues) or updates cause frequent breakages. A good strategy minimizes both risks while maintaining a healthy dependency ecosystem.

**When to use:**
- Setting up a new project's dependency management approach
- Onboarding team to dependency update practices
- After experiencing update-related incidents
- Quarterly review of dependency health
- Establishing CI/CD dependency automation

---

## Prerequisites

**Required:**
- [ ] Project uses a dependency management tool (pip, npm, poetry, etc.)
- [ ] Access to repository and CI/CD configuration
- [ ] Understanding of project's dependencies
- [ ] Permission to configure automated tools (Dependabot, Renovate)

**Recommended:**
- [ ] Test suite with good coverage (80%+)
- [ ] Staging environment for testing updates
- [ ] Security scanning tools (pip-audit, npm audit)

**Check before starting:**
```bash
# List current dependencies
pip list  # or npm list, or poetry show

# Check for known vulnerabilities
pip-audit  # or npm audit

# Check for outdated packages
pip list --outdated  # or npm outdated

# Verify test suite runs
pytest  # or npm test

# Check current Python/Node version
python --version  # or node --version
```

---

## Implementation Steps

### Step 1: Define Dependency Classification and Policies

**What:** Categorize dependencies by type and establish update policies for each category.

**How:** Create a dependency matrix that defines how aggressively to update different types of dependencies.

**Code/Commands:**
```markdown
# Create DEPENDENCY_POLICY.md in repository

# Dependency Update Policy

## Dependency Categories

### 1. Security Dependencies (Critical)
**Examples:** cryptography, jwt libraries, authentication packages  
**Policy:** Update within 24-48 hours of security advisory  
**Auto-merge:** Yes, after tests pass  
**Testing:** Full integration test suite + manual security verification  
**Notification:** Immediate alert to team

### 2. Core Framework Dependencies (High Priority)
**Examples:** FastAPI, React, Django, Express  
**Policy:** Update within 1 week of stable release  
**Auto-merge:** No, requires review  
**Testing:** Full test suite + smoke tests in staging  
**Notification:** Slack channel notification  
**Cadence:** Check weekly

### 3. Development Dependencies (Medium Priority)
**Examples:** pytest, eslint, ruff, black, type checkers  
**Policy:** Update monthly or as needed  
**Auto-merge:** Yes, if tests pass  
**Testing:** Unit tests + linting  
**Notification:** Weekly digest  
**Cadence:** Monthly review

### 4. Indirect Dependencies (Low Priority)
**Examples:** Transitive dependencies from packages  
**Policy:** Update when parent updates or security issue found  
**Auto-merge:** Yes, with parent  
**Testing:** Full test suite  
**Notification:** None unless issues  
**Cadence:** Quarterly review

### 5. Pinned Dependencies (Special Handling)
**Examples:** Dependencies pinned due to compatibility issues  
**Policy:** Track upstream, plan migration path  
**Auto-merge:** Never  
**Testing:** Dedicated testing sprint  
**Notification:** Monthly reminder to review  
**Cadence:** Quarterly evaluation for unblocking

---

## Update Approval Matrix

| Severity | Type | Timeline | Approval Required | Auto-merge Allowed |
|----------|------|----------|-------------------|-------------------|
| Critical Security | Any | 24-48h | Security Lead + One Dev | Yes (after tests) |
| Major Version | Framework | 1 week | Tech Lead + Two Devs | No |
| Minor Version | Framework | 3-5 days | One Senior Dev | If tests pass |
| Patch Version | Framework | 1-2 days | Any Dev | Yes |
| Major Version | Library | 1 week | One Dev | No |
| Minor/Patch | Library | 2-3 days | Any Dev | If tests pass |
| Dev Tools | Any | 1 week | Any Dev | Yes |

---

## Risk Assessment Framework

Before updating, assess risk using this matrix:

**Low Risk** (proceed with standard testing):
- Patch version updates (1.2.3 → 1.2.4)
- Updates with good changelogs showing only bug fixes
- Dev dependencies that don't affect runtime

**Medium Risk** (require thorough testing):
- Minor version updates (1.2.0 → 1.3.0)
- Updates to critical path dependencies
- Dependencies with breaking changes in changelog

**High Risk** (require spike investigation):
- Major version updates (1.x → 2.x)
- Core framework updates
- Dependencies with minimal changelog/documentation
- Updates affecting security or authentication

**Action by Risk Level:**
- Low: Run tests, auto-merge if green
- Medium: Manual testing in staging + review
- High: Spike (time-boxed investigation) → plan → execute

---

## Blocked Updates Register

| Dependency | Current | Latest | Why Blocked | Unblock Strategy | Review Date |
|------------|---------|--------|-------------|------------------|-------------|
| pydantic | 1.10.2 | 2.5.0 | Breaking API changes | Migration sprint planned Q4 | 2025-12-01 |
| | | | affects 15 files | | |
```

**Create dependency configuration file:**
```toml
# pyproject.toml or similar
[tool.dependency-policy]
# Auto-update categories
security-updates = "always"
framework-updates = "weekly"
dev-updates = "monthly"

# Pinned for compatibility
pinned = [
    "pydantic==1.10.2",  # Waiting for migration (TD-042)
]

# Ignored (vendor code, deprecated but functional)
ignored = [
    "old-internal-lib",  # Vendor code, no updates available
]

# Pre-release tolerance
allow-pre-releases = false
```

**Verification:**
- [ ] Policy document created and reviewed by team
- [ ] Dependency categories clearly defined
- [ ] Update timelines realistic for team capacity
- [ ] Risk assessment framework understood
- [ ] Blocked updates tracked with unblock plans

**If This Fails:**
→ If policies too complex: Start with 3 categories (security/framework/other)
→ If timelines too aggressive: Add buffer, iterate based on actual performance
→ If team disagrees: Run workshop to build consensus on priorities

---

### Step 2: Set Up Automated Dependency Scanning

**What:** Configure automated tools to detect outdated and vulnerable dependencies.

**How:** Implement Dependabot, Renovate, or similar tools with appropriate configuration for your update policy.

**Code/Commands:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
      time: "03:00"  # Run at 3 AM UTC
    open-pull-requests-limit: 5
    
    # Group updates by type
    groups:
      security-updates:
        applies-to: security-updates
        update-types:
          - "patch"
          - "minor"
          - "major"
      
      framework-updates:
        patterns:
          - "fastapi*"
          - "django*"
          - "sqlalchemy*"
        update-types:
          - "patch"
          - "minor"
      
      dev-dependencies:
        dependency-type: "development"
        update-types:
          - "patch"
          - "minor"
    
    # Labels for categorization
    labels:
      - "dependencies"
      - "automated"
    
    # Reviewers
    reviewers:
      - "backend-team"
    
    # Commit message format
    commit-message:
      prefix: "deps"
      include: "scope"
    
    # Ignore specific dependencies
    ignore:
      - dependency-name: "pydantic"
        # Pinned pending migration
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]
        # Major updates need manual review

  # Dev dependencies can be more aggressive
  - package-ecosystem: "pip"
    directory: "/tests"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "dev-tools"
    reviewers:
      - "any-dev"
```

**Alternative: Renovate (more flexible)**
```json
// renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:base"
  ],
  "dependencyDashboard": true,
  "dependencyDashboardTitle": "Dependency Updates Dashboard",
  
  "packageRules": [
    {
      "description": "Security updates - auto-merge after tests",
      "matchUpdateTypes": ["patch"],
      "matchPackagePatterns": ["*"],
      "vulnerabilityAlerts": {
        "enabled": true
      },
      "automerge": true,
      "automergeType": "pr",
      "automergeStrategy": "squash",
      "labels": ["security", "automerge"]
    },
    {
      "description": "Framework updates - require review",
      "matchPackagePatterns": ["^fastapi", "^django", "^sqlalchemy"],
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "framework updates",
      "schedule": ["before 10am on Monday"],
      "automerge": false,
      "reviewers": ["tech-lead"],
      "labels": ["framework", "needs-review"]
    },
    {
      "description": "Major updates - manual only",
      "matchUpdateTypes": ["major"],
      "enabled": false,
      "labels": ["major-version", "manual-review-required"]
    },
    {
      "description": "Dev dependencies - weekly batch",
      "matchDepTypes": ["devDependencies"],
      "groupName": "dev dependencies",
      "schedule": ["before 10am on Monday"],
      "automerge": true,
      "labels": ["dev-dependencies"]
    }
  ],
  
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"],
    "assignees": ["@security-team"]
  },
  
  "prConcurrentLimit": 10,
  "prHourlyLimit": 0,
  
  "timezone": "America/New_York"
}
```

**Set up security scanning:**
```bash
# Install security scanner
pip install pip-audit

# Create security check script
cat > scripts/security_check.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Checking for security vulnerabilities..."

# Check Python dependencies
pip-audit --format json --output security-report.json

# Parse results
VULNS=$(jq '.dependencies | length' security-report.json)

if [ "$VULNS" -gt 0 ]; then
    echo "⚠️  Found $VULNS vulnerabilities!"
    pip-audit --format markdown
    exit 1
else
    echo "✅ No security vulnerabilities found"
fi
EOF

chmod +x scripts/security_check.sh

# Add to CI
cat >> .github/workflows/security.yml << 'EOF'
name: Security Scan

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  push:
    branches: [main]
  pull_request:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt pip-audit
      
      - name: Run security scan
        run: ./scripts/security_check.sh
      
      - name: Upload results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.json
      
      - name: Create issue on vulnerability
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Security vulnerabilities detected',
              labels: ['security', 'dependencies'],
              body: 'Security scan failed. Check the workflow logs.'
            });
EOF
```

**Verification:**
- [ ] Dependabot or Renovate configured and active
- [ ] Security scanning running daily
- [ ] PRs automatically created for updates
- [ ] Labels and reviewers correctly assigned
- [ ] Grouped updates working as configured

**If This Fails:**
→ If too many PRs: Reduce frequency or increase grouping
→ If auto-merge too aggressive: Start with manual review, enable gradually
→ If security alerts noisy: Tune severity thresholds

---

### Step 3: Establish Update Cadence and Schedule

**What:** Define regular schedule for reviewing and applying dependency updates.

**How:** Create calendar events and automation for different update types.

**Code/Commands:**
```markdown
# Team Calendar - Dependency Update Schedule

## Daily (Automated)
- **Time:** 3:00 AM UTC
- **What:** Security vulnerability scans run
- **Action:** Auto-create PRs for critical security patches
- **Owner:** Automated (Dependabot)
- **Notification:** Slack #security channel if issues found

## Weekly (Monday Morning)
- **Time:** 10:00 AM local
- **What:** Review and merge pending patch updates
- **Action:** 
  1. Review Dependabot PRs from last week
  2. Merge passing patch updates
  3. Investigate any failing tests
- **Owner:** On-call developer
- **Duration:** 30 minutes
- **Notification:** Calendar invite, Slack reminder

## Bi-weekly (Every other Friday)
- **Time:** 2:00 PM local
- **What:** Framework and minor version review
- **Action:**
  1. Review changelog for framework updates
  2. Test in staging if needed
  3. Schedule or merge approved updates
- **Owner:** Rotating (entire team)
- **Duration:** 1 hour
- **Notification:** Calendar invite

## Monthly (First Monday)
- **Time:** 3:00 PM local
- **What:** Dev dependencies and comprehensive review
- **Action:**
  1. Batch update all dev dependencies
  2. Review blocked dependencies register
  3. Plan major version migrations if needed
- **Owner:** Tech lead + interested devs
- **Duration:** 1-2 hours
- **Notification:** Calendar invite + agenda in advance

## Quarterly (First Monday of Quarter)
- **Time:** Half-day session
- **What:** Strategic dependency review
- **Action:**
  1. Review all pinned dependencies
  2. Plan migrations for blocked updates
  3. Evaluate new alternatives
  4. Update dependency policy if needed
- **Owner:** Tech lead + senior devs
- **Duration:** 4 hours
- **Notification:** Calendar invite 2 weeks in advance
```

**Automation scripts:**
```python
# scripts/weekly_update_check.py
"""Weekly dependency update review script."""

import subprocess
import json
from datetime import datetime

def get_pending_prs():
    """Get open Dependabot PRs."""
    result = subprocess.run(
        ['gh', 'pr', 'list', '--label', 'dependencies', '--json', 'number,title,createdAt,labels'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def categorize_prs(prs):
    """Categorize PRs by type."""
    categories = {
        'security': [],
        'patch': [],
        'minor': [],
        'major': []
    }
    
    for pr in prs:
        labels = [l['name'] for l in pr['labels']]
        if 'security' in labels:
            categories['security'].append(pr)
        elif 'patch' in labels or any('patch' in l.lower() for l in labels):
            categories['patch'].append(pr)
        elif 'major' in labels:
            categories['major'].append(pr)
        else:
            categories['minor'].append(pr)
    
    return categories

def generate_report(categories):
    """Generate weekly update report."""
    print("# Weekly Dependency Update Report")
    print(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
    
    for category, prs in categories.items():
        if prs:
            print(f"## {category.title()} Updates ({len(prs)})\n")
            for pr in prs:
                age_days = (datetime.now() - datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00'))).days
                print(f"- PR #{pr['number']}: {pr['title']}")
                print(f"  Age: {age_days} days")
                
                # Get CI status
                ci_result = subprocess.run(
                    ['gh', 'pr', 'checks', str(pr['number'])],
                    capture_output=True,
                    text=True
                )
                print(f"  CI: {'✅ Passing' if 'success' in ci_result.stdout.lower() else '❌ Failing'}")
                print()
    
    # Recommendations
    print("## Recommended Actions\n")
    if categories['security']:
        print("⚠️  **URGENT:** Review and merge security updates immediately")
    if categories['patch']:
        print("✅ Consider auto-merging patch updates with passing tests")
    if categories['minor']:
        print("👀 Review minor updates and test in staging if needed")
    if categories['major']:
        print("🚧 Major updates require dedicated time - schedule for next sprint")

if __name__ == "__main__":
    prs = get_pending_prs()
    categories = categorize_prs(prs)
    generate_report(categories)
```

**Slack notification automation:**
```bash
# Add to CI to post weekly summary
cat > .github/workflows/weekly-dep-report.yml << 'EOF'
name: Weekly Dependency Report

on:
  schedule:
    - cron: '0 14 * * 1'  # Mondays at 2 PM UTC
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Generate report
        id: report
        run: |
          REPORT=$(python scripts/weekly_update_check.py)
          echo "report<<EOF" >> $GITHUB_OUTPUT
          echo "$REPORT" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      
      - name: Post to Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Weekly Dependency Update Report",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "${{ steps.report.outputs.report }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
EOF
```

**Verification:**
- [ ] Calendar events created for all cadences
- [ ] Team members assigned to rotation
- [ ] Automation scripts tested and working
- [ ] Slack notifications configured
- [ ] First weekly review completed successfully

**If This Fails:**
→ If schedule too frequent: Start with monthly, gradually increase
→ If team ignores schedule: Make it shorter, more focused
→ If automation too noisy: Tune thresholds, reduce notifications

---

### Step 4: Define Testing Requirements for Updates

**What:** Establish what testing is required before merging dependency updates.

**How:** Create tiered testing strategy based on risk level and update type.

**Code/Commands:**
```yaml
# .github/workflows/dependency-update-tests.yml
name: Dependency Update Tests

on:
  pull_request:
    paths:
      - 'requirements.txt'
      - 'pyproject.toml'
      - 'poetry.lock'
      - 'package.json'
      - 'package-lock.json'

jobs:
  determine-risk:
    runs-on: ubuntu-latest
    outputs:
      risk-level: ${{ steps.assess.outputs.risk }}
    steps:
      - uses: actions/checkout@v3
      
      - name: Assess risk level
        id: assess
        run: |
          # Check if this is a major version update
          if git diff origin/main -- requirements.txt | grep -E '==.*→.*==.*' | grep -v '+1\|+0\.'; then
            echo "risk=high" >> $GITHUB_OUTPUT
          # Check if it's a security update
          elif [[ "${{ github.event.pull_request.labels }}" == *"security"* ]]; then
            echo "risk=critical" >> $GITHUB_OUTPUT
          # Check if it's a framework update
          elif git diff origin/main -- requirements.txt | grep -E 'fastapi|django|flask'; then
            echo "risk=medium" >> $GITHUB_OUTPUT
          else
            echo "risk=low" >> $GITHUB_OUTPUT
          fi
  
  basic-tests:
    runs-on: ubuntu-latest
    needs: determine-risk
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run unit tests
        run: pytest tests/unit -v
      
      - name: Linting
        run: ruff check src/
      
      - name: Type checking
        run: mypy src/ --strict
  
  integration-tests:
    runs-on: ubuntu-latest
    needs: [determine-risk, basic-tests]
    if: needs.determine-risk.outputs.risk-level != 'low'
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run integration tests
        run: pytest tests/integration -v
      
      - name: API contract tests
        run: pytest tests/api -v
  
  performance-tests:
    runs-on: ubuntu-latest
    needs: [determine-risk, integration-tests]
    if: needs.determine-risk.outputs.risk-level == 'high' || needs.determine-risk.outputs.risk-level == 'critical'
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Benchmark tests
        run: pytest tests/performance --benchmark-only
      
      - name: Load testing
        run: |
          docker-compose up -d
          locust -f tests/load/locustfile.py --headless -u 100 -r 10 --run-time 2m
  
  security-validation:
    runs-on: ubuntu-latest
    needs: determine-risk
    if: needs.determine-risk.outputs.risk-level == 'critical'
    steps:
      - uses: actions/checkout@v3
      
      - name: Security audit
        run: pip-audit --strict
      
      - name: Vulnerability scan
        run: |
          pip install safety
          safety check --json
      
      - name: SAST scan
        uses: github/codeql-action/analyze@v2
```

**Testing matrix by risk level:**
```markdown
# Testing Requirements for Dependency Updates

## Low Risk (Patch updates, dev dependencies)
**Required:**
- [x] Unit tests pass
- [x] Linting passes
- [x] Type checking passes

**Optional:**
- [ ] Integration tests
- [ ] Manual smoke test

**Auto-merge:** Yes, if all required tests pass

---

## Medium Risk (Minor updates, library updates)
**Required:**
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Linting passes
- [x] Type checking passes
- [x] API contract tests pass

**Optional:**
- [ ] Performance benchmarks
- [ ] Staging deployment test

**Auto-merge:** If tests pass AND reviewed by one developer

---

## High Risk (Major updates, framework updates)
**Required:**
- [x] All unit tests pass
- [x] All integration tests pass
- [x] API contract tests pass
- [x] Performance benchmarks (no regression >5%)
- [x] Manual testing in staging
- [x] Security audit passes
- [x] Code review by tech lead

**Recommended:**
- [x] Canary deployment to 5% of users
- [x] Monitor error rates for 24 hours

**Auto-merge:** Never - requires manual approval

---

## Critical Risk (Security updates)
**Required:**
- [x] All tests (unit, integration, security)
- [x] Vulnerability scan confirms fix
- [x] Security team review
- [x] Staging deployment verification
- [x] Rollback plan documented

**Fast-track if:**
- [ ] CVE is actively exploited
- [ ] Public exploit available
- [ ] Affects customer data

**Timeline:** 24-48 hours maximum
```

**Verification:**
- [ ] Testing matrix defined and documented
- [ ] CI/CD pipelines enforce testing requirements
- [ ] Risk assessment automatic based on update type
- [ ] Team understands which tests are mandatory
- [ ] Fast-track process for critical security updates

**If This Fails:**
→ If tests take too long: Parallelize, optimize, or reduce for low-risk updates
→ If tests too expensive: Cache dependencies, use smaller test datasets
→ If false negatives: Improve test coverage before enabling auto-merge

---

### Step 5: Create Communication and Escalation Protocol

**What:** Establish clear communication channels for dependency issues and escalation paths.

**How:** Define who needs to be notified for different types of updates and issues.

**Code/Commands:**
```markdown
# Dependency Update Communication Protocol

## Notification Channels

### Slack Channels
- **#dependencies** - All automated dependency PRs and updates
- **#security-alerts** - Critical security vulnerabilities (P0/P1)
- **#engineering-alerts** - Failed updates, broken builds
- **#releases** - Successful dependency update deployments

### Email Lists
- **security-team@company.com** - Critical security updates
- **eng-leads@company.com** - Major version updates, policy changes
- **dev-team@company.com** - Weekly dependency digest

### GitHub
- **@backend-team** - All backend dependency PRs
- **@frontend-team** - All frontend dependency PRs
- **@security-team** - Security-labeled PRs
- **@tech-leads** - Major version updates

---

## Escalation Matrix

### Level 1: Standard Update (No escalation)
**Triggers:**
- Patch version updates with passing tests
- Dev dependency updates
- Successfully auto-merged PRs

**Action:**
- Auto-merge or routine review
- Post to #dependencies channel

**Timeline:** 1-3 days

---

### Level 2: Requires Review
**Triggers:**
- Minor version updates
- Framework updates
- Tests failing on update
- Updates requiring code changes

**Action:**
1. Post to #dependencies with @backend-team mention
2. Assign to on-call developer
3. Reviewer investigates and approves/rejects

**Timeline:** 2-5 days

**Escalate to Level 3 if:**
- Not addressed in 5 days
- Blocks other work
- Multiple test failures

---

### Level 3: Engineering Lead Attention
**Triggers:**
- Major version updates
- Breaking changes requiring significant refactoring
- Multiple dependencies failing together
- Level 2 not resolved in 5 days

**Action:**
1. Post to #engineering-alerts
2. Tag @tech-lead
3. Schedule 30-minute sync to discuss
4. Create action plan with timeline

**Timeline:** 1 week

**Escalate to Level 4 if:**
- Affects production stability
- Security vulnerability involved
- Timeline at risk

---

### Level 4: Security/Critical Incident
**Triggers:**
- CVE with CVSS score ≥7.0
- Active exploitation in the wild
- Production outage related to dependency
- Zero-day vulnerability

**Action:**
1. Immediate Slack alert to #security-alerts
2. Email to security-team@ and eng-leads@
3. Create incident in PagerDuty
4. Convene emergency sync within 1 hour
5. Activate incident response protocol

**Timeline:** 24-48 hours maximum

**Response Team:**
- Security Lead (Incident Commander)
- Tech Lead
- On-call Engineer
- Product Manager (for customer communication)

---

## Communication Templates

### Routine Update (Level 1)
```
✅ Dependencies updated automatically
- Package: fastapi-utils
- Version: 0.2.1 → 0.2.2  
- Type: Patch
- Tests: All passing
- PR: #1234
```

### Review Needed (Level 2)
```
👀 Dependency update needs review
- Package: fastapi
- Version: 0.104.0 → 0.105.0
- Type: Minor
- Tests: 2 failing (see details)
- Impact: Medium
- PR: #1235
- Assigned: @jane-doe
```

### Major Update (Level 3)
```
🚧 Major dependency update requires planning
- Package: SQLAlchemy  
- Version: 1.4.x → 2.0.x
- Breaking changes: Yes (see migration guide)
- Affected files: ~30
- Estimated effort: 3-5 days
- Proposed timeline: Sprint 23
- Tech lead review: @tech-lead
- Planning doc: [link]
```

### Critical Security (Level 4)
```
🚨 CRITICAL SECURITY UPDATE REQUIRED
- Package: cryptography
- CVE: CVE-2024-12345 (CVSS 9.8)
- Vulnerability: Remote code execution
- Status: Actively exploited
- Required version: 41.0.7+
- Timeline: 24 hours
- Incident: INC-4567
- IC: @security-lead
- War room: #incident-4567
```
```

**Automated notifications:**
```python
# scripts/send_dependency_alert.py
"""Send dependency update notifications to appropriate channels."""

import os
import requests
import json
from typing import Dict

SLACK_WEBHOOKS = {
    'dependencies': os.getenv('SLACK_WEBHOOK_DEPS'),
    'security': os.getenv('SLACK_WEBHOOK_SECURITY'),
    'engineering': os.getenv('SLACK_WEBHOOK_ENG')
}

def send_slack_alert(channel: str, message: Dict):
    """Send formatted message to Slack."""
    webhook_url = SLACK_WEBHOOKS.get(channel)
    if not webhook_url:
        print(f"Warning: No webhook configured for channel {channel}")
        return
    
    response = requests.post(webhook_url, json=message)
    response.raise_for_status()

def alert_security_update(package: str, current_version: str, new_version: str, cve: str, severity: str):
    """Alert for security update."""
    message = {
        "text": f"🚨 Security update required: {package}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Security Update: {package}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Current:*\n{current_version}"},
                    {"type": "mrkdwn", "text": f"*Required:*\n{new_version}"},
                    {"type": "mrkdwn", "text": f"*CVE:*\n{cve}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity}"}
                ]
            }
        ]
    }
    
    send_slack_alert('security', message)

# Example usage
if __name__ == "__main__":
    alert_security_update(
        package="cryptography",
        current_version="41.0.6",
        new_version="41.0.7",
        cve="CVE-2024-12345",
        severity="CRITICAL (9.8)"
    )
```

**Verification:**
- [ ] Notification channels created and tested
- [ ] Escalation levels defined and documented
- [ ] Team knows who to contact for each level
- [ ] Automated alerts configured
- [ ] Response times realistic and achievable

**If This Fails:**
→ If notifications too noisy: Increase thresholds, batch low-priority
→ If escalations ignored: Make accountabilities clearer, add to on-call rotation
→ If response times missed: Reassess capacity, adjust timelines

---

### Step 6: Plan for Major Version Migrations

**What:** Develop structured approach for handling major version updates that require significant effort.

**How:** Create migration planning template and process for high-risk updates.

**Code/Commands:**
```markdown
# Major Version Migration Template

## Example: SQLAlchemy 1.4 → 2.0 Migration

### Overview
**Package:** SQLAlchemy  
**Current Version:** 1.4.51  
**Target Version:** 2.0.25  
**Migration Type:** Major (Breaking Changes)  
**Estimated Effort:** 5-8 days  
**Priority:** MEDIUM (migrate by end of Q4 2025)

---

### Why Migrate?
- SQLAlchemy 1.4 reaching end of support
- 2.0 has performance improvements (20-30% faster)
- Better type hinting support
- Required for upcoming Python 3.12 compatibility

---

### Breaking Changes Assessment

#### HIGH Impact (Must Fix)
1. **Query API removed** - All `session.query()` must migrate to `select()`
   - Affected files: 15
   - Estimated effort: 3 days

2. **Eager loading changes** - `joinedload` behavior different
   - Affected files: 8
   - Estimated effort: 1 day

3. **Session.get() signature changed**
   - Affected files: 12
   - Estimated effort: 0.5 days

#### MEDIUM Impact (Should Fix)
1. **Deprecation warnings** - Several methods deprecated
   - Can be addressed incrementally
   - Use compatibility layer initially

2. **Type stub changes**
   - Update type hints in 3 files
   - Estimated effort: 0.5 days

#### LOW Impact (Nice to Fix)
1. **New features available** - Async support, better joins
   - Can adopt later
   - Not blocking migration

---

### Migration Strategy

#### Phase 1: Preparation (Sprint 22)
- [ ] Set up isolated branch: `feat/sqlalchemy-2.0-migration`
- [ ] Install SQLAlchemy 2.0 in dev environment
- [ ] Run tests to identify all breaking changes
- [ ] Document all required changes
- [ ] Create task breakdown in Jira

**Exit Criteria:**
- Complete list of affected files
- Detailed task breakdown
- Spike completed successfully

---

#### Phase 2: Incremental Migration (Sprint 23-24)
- [ ] Migrate models and table definitions
- [ ] Update query patterns (session.query → select)
- [ ] Fix eager loading patterns
- [ ] Update tests
- [ ] Address deprecation warnings

**Approach:** File-by-file migration
**Testing:** Run tests after each file

**Exit Criteria:**
- All tests passing with SQLAlchemy 2.0
- No deprecation warnings
- Code review completed

---

#### Phase 3: Validation (Sprint 24)
- [ ] Deploy to staging environment
- [ ] Run full integration test suite
- [ ] Performance testing (verify 20%+ improvement)
- [ ] Load testing
- [ ] Manual QA testing

**Exit Criteria:**
- No regressions in staging
- Performance improved
- Load tests pass

---

#### Phase 4: Production Rollout (Sprint 25)
- [ ] Canary deployment (5% of traffic)
- [ ] Monitor for 24 hours
- [ ] Gradual rollout (25% → 50% → 100%)
- [ ] Full monitoring for 1 week

**Rollback Plan:**
- Keep SQLAlchemy 1.4 in requirements as fallback
- Feature flag to switch between versions if needed
- Database changes backward compatible

**Exit Criteria:**
- 100% traffic on new version
- No increase in error rates
- Performance metrics improved

---

### Risk Mitigation

**Risk:** Migration breaks production queries  
**Mitigation:** Comprehensive testing in staging, canary deployment, feature flag  
**Probability:** LOW  
**Impact:** HIGH

**Risk:** Performance regression despite promises  
**Mitigation:** Benchmark tests, load testing before rollout  
**Probability:** MEDIUM  
**Impact:** MEDIUM

**Risk:** Team unfamiliar with new API  
**Mitigation:** Training session, pair programming on first few files  
**Probability:** MEDIUM  
**Impact:** LOW

---

### Success Metrics

- [ ] All tests passing (100%)
- [ ] Test coverage maintained or improved (>85%)
- [ ] Query performance improved by ≥15%
- [ ] No increase in error rates
- [ ] Team velocity not significantly impacted
- [ ] Documentation updated

---

### Resources

**Documentation:**
- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [Internal migration examples](./docs/sqlalchemy-migration-examples.md)

**Team:**
- Lead: @jane-doe (SQLAlchemy expert)
- Support: @john-smith @alice-wong
- Reviewer: @tech-lead

**Timeline:**
- Start: Sprint 22 (Week of Dec 1)
- Complete: Sprint 25 (Week of Jan 15)
- Buffer: 1 sprint for unexpected issues

---

### Sign-off

- [ ] Eng Lead Approval: __________
- [ ] Security Review: __________
- [ ] Product Approval: __________

Date: __________
```

**Create migration tracking:**
```python
# scripts/track_migration.py
"""Track progress of major version migration."""

import ast
from pathlib import Path
from typing import List, Dict

def find_legacy_patterns(file_path: Path) -> List[str]:
    """Find SQLAlchemy 1.4 patterns in file."""
    with open(file_path) as f:
        content = f.read()
    
    legacy_patterns = []
    
    # Pattern 1: session.query()
    if 'session.query(' in content:
        legacy_patterns.append('Uses session.query() (deprecated)')
    
    # Pattern 2: Old-style joinedload
    if 'joinedload(' in content and 'selectinload' not in content:
        legacy_patterns.append('Uses old joinedload pattern')
    
    # Pattern 3: Legacy Session.get() signature
    if '.get(' in content:
        # Parse AST to check signature
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == 'get':
                        if len(node.args) == 1:  # Old signature
                            legacy_patterns.append('Uses legacy Session.get() signature')
        except:
            pass
    
    return legacy_patterns

def generate_migration_report(src_dir='src') -> Dict:
    """Generate report of migration progress."""
    report = {
        'total_files': 0,
        'migrated': 0,
        'remaining': 0,
        'files_by_status': {
            'complete': [],
            'in_progress': [],
            'not_started': []
        }
    }
    
    for py_file in Path(src_dir).rglob('*.py'):
        report['total_files'] += 1
        legacy = find_legacy_patterns(py_file)
        
        if not legacy:
            report['migrated'] += 1
            report['files_by_status']['complete'].append(str(py_file))
        else:
            report['remaining'] += 1
            # Check git history to see if file was recently modified
            # (indicating in-progress migration)
            report['files_by_status']['not_started'].append({
                'file': str(py_file),
                'issues': legacy
            })
    
    return report

def print_report(report: Dict):
    """Print formatted migration progress report."""
    print("# SQLAlchemy 2.0 Migration Progress\n")
    
    pct_complete = (report['migrated'] / max(report['total_files'], 1)) * 100
    print(f"**Progress:** {report['migrated']}/{report['total_files']} files ({pct_complete:.1f}%)\n")
    
    print(f"✅ Migrated: {report['migrated']}")
    print(f"⏳ Remaining: {report['remaining']}\n")
    
    if report['files_by_status']['not_started']:
        print("## Files Requiring Migration\n")
        for item in report['files_by_status']['not_started'][:10]:
            print(f"### {item['file']}")
            for issue in item['issues']:
                print(f"- {issue}")
            print()

if __name__ == "__main__":
    report = generate_migration_report()
    print_report(report)
```

**Verification:**
- [ ] Migration plan created for each major update
- [ ] Phased approach defined
- [ ] Risk assessment completed
- [ ] Rollback plan documented
- [ ] Team capacity allocated

**If This Fails:**
→ If migration too large: Break into smaller phases, migrate subsystem by subsystem
→ If risks too high: Consider staying on current version longer, plan more thoroughly
→ If team lacks expertise: Hire consultant, extensive pair programming

---

### Step 7: Monitor and Measure Success

**What:** Track metrics to ensure dependency update strategy is effective.

**How:** Monitor key indicators of dependency health and team efficiency.

**Code/Commands:**
```python
# scripts/dependency_health_metrics.py
"""Track dependency health metrics over time."""

import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List
import matplotlib.pyplot as plt

class DependencyMetrics:
    def __init__(self):
        self.metrics_file = 'dependency_metrics.json'
        self.load_history()
    
    def load_history(self):
        """Load historical metrics."""
        try:
            with open(self.metrics_file) as f:
                self.history = json.load(f)
        except FileNotFoundError:
            self.history = []
    
    def collect_current_metrics(self) -> Dict:
        """Collect current dependency metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_dependencies': self._count_dependencies(),
            'outdated_dependencies': self._count_outdated(),
            'security_vulnerabilities': self._count_vulnerabilities(),
            'avg_dependency_age_days': self._calculate_avg_age(),
            'update_frequency_per_month': self._calculate_update_frequency(),
            'time_to_update_security_hours': self._calculate_security_response_time(),
            'blocked_dependencies': self._count_blocked()
        }
        return metrics
    
    def _count_dependencies(self) -> int:
        """Count total dependencies."""
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        return len(result.stdout.strip().split('\n')) - 2  # Exclude header
    
    def _count_outdated(self) -> int:
        """Count outdated dependencies."""
        result = subprocess.run(['pip', 'list', '--outdated'], capture_output=True, text=True)
        return len(result.stdout.strip().split('\n')) - 2
    
    def _count_vulnerabilities(self) -> int:
        """Count known vulnerabilities."""
        result = subprocess.run(['pip-audit', '--format', 'json'], capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
            return len(data.get('dependencies', []))
        except:
            return 0
    
    def record_snapshot(self):
        """Record current metrics."""
        current = self.collect_current_metrics()
        self.history.append(current)
        
        with open(self.metrics_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        return current
    
    def generate_dashboard(self):
        """Generate metrics dashboard."""
        if len(self.history) < 2:
            print("Not enough data for trends")
            return
        
        # Extract time series
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in self.history]
        outdated = [m['outdated_dependencies'] for m in self.history]
        vulnerabilities = [m['security_vulnerabilities'] for m in self.history]
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot outdated dependencies
        ax1.plot(timestamps, outdated, marker='o', label='Outdated')
        ax1.set_ylabel('Count')
        ax1.set_title('Outdated Dependencies Over Time')
        ax1.legend()
        ax1.grid(True)
        
        # Plot vulnerabilities
        ax2.plot(timestamps, vulnerabilities, marker='o', color='red', label='Vulnerabilities')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Count')
        ax2.set_title('Security Vulnerabilities Over Time')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('dependency_health_dashboard.png')
        print("Dashboard saved to dependency_health_dashboard.png")
    
    def generate_report(self) -> str:
        """Generate text report of metrics."""
        current = self.history[-1]
        previous = self.history[-30] if len(self.history) >= 30 else self.history[0]
        
        report = f"""# Dependency Health Report

**Date:** {datetime.now().strftime('%Y-%m-%d')}

## Current Status

- **Total Dependencies:** {current['total_dependencies']}
- **Outdated:** {current['outdated_dependencies']} ({current['outdated_dependencies']/max(current['total_dependencies'],1)*100:.1f}%)
- **Security Vulnerabilities:** {current['security_vulnerabilities']}
- **Avg Dependency Age:** {current['avg_dependency_age_days']} days
- **Updates This Month:** {current['update_frequency_per_month']}

## Trends (Last 30 Days)

"""
        # Calculate deltas
        outdated_delta = current['outdated_dependencies'] - previous['outdated_dependencies']
        vuln_delta = current['security_vulnerabilities'] - previous['security_vulnerabilities']
        
        report += f"- Outdated dependencies: {outdated_delta:+d} ({'📈' if outdated_delta > 0 else '📉'})\n"
        report += f"- Vulnerabilities: {vuln_delta:+d} ({'📈' if vuln_delta > 0 else '📉'})\n"
        
        ## Target Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Security Vulns | 0 | {current['security_vulnerabilities']} | {'✅' if current['security_vulnerabilities'] == 0 else '❌'} |
| Outdated % | <10% | {current['outdated_dependencies']/max(current['total_dependencies'],1)*100:.1f}% | {'✅' if current['outdated_dependencies']/current['total_dependencies'] < 0.1 else '❌'} |
| Avg Age | <90 days | {current['avg_dependency_age_days']} days | {'✅' if current['avg_dependency_age_days'] < 90 else '❌'} |
| Update Frequency | >10/month | {current['update_frequency_per_month']} | {'✅' if current['update_frequency_per_month'] > 10 else '❌'} |
"""
        
        return report

# Usage
metrics = DependencyMetrics()
metrics.record_snapshot()
print(metrics.generate_report())
metrics.generate_dashboard()
```

**Dashboard goals:**
```markdown
# Dependency Health Goals

## Target Metrics (Quarterly)

### Security
- **Zero known vulnerabilities** with CVSS >7.0
- Security updates applied within 48 hours
- All dependencies scanned daily

### Freshness
- <10% of dependencies outdated
- Average dependency age <90 days
- No dependencies >1 year behind latest

### Velocity
- >10 dependency updates per month
- Update frequency proportional to release cadence
- Major version migrations every 6-12 months

### Team Impact
- <5 hours/week spent on dependency issues
- Zero production incidents from dependency bugs
- Developer satisfaction score >4/5 for dependency management

---

## Red Flags (Require Immediate Action)

🚨 **Critical:**
- Any vulnerability with CVSS >9.0
- >3 high-severity vulnerabilities
- Core framework >2 major versions behind

⚠️ **Warning:**
- >20% of dependencies outdated
- >5 blocked dependencies without migration plan
- Security updates taking >1 week

---

## Monthly Review Questions

1. Are we meeting target metrics?
2. What's blocking dependency updates?
3. Do we need to adjust our strategy?
4. Are there patterns in failures?
5. Is the team satisfied with the process?
```

**Verification:**
- [ ] Metrics collection automated (daily or weekly)
- [ ] Dashboard accessible to team
- [ ] Target metrics defined and agreed upon
- [ ] Monthly reviews scheduled
- [ ] Trends visible and actionable

**If This Fails:**
→ If metrics not actionable: Simplify to 3-5 key indicators
→ If no one looks at dashboard: Present in standups/retros
→ If targets unrealistic: Adjust based on actual capabilities

---

### Step 8: Document and Share Knowledge

**What:** Create comprehensive documentation of dependency update strategy and share with team.

**How:** Write clear documentation, conduct training, and establish feedback loop.

**Code/Commands:**
```markdown
# Create comprehensive documentation

# docs/DEPENDENCY_STRATEGY.md

# Dependency Update Strategy

> **TL;DR:** We update dependencies regularly using automated tools, with different 
> policies for security vs. feature updates. See [Quick Reference](#quick-reference) 
> for common tasks.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Philosophy](#philosophy)
3. [Categories & Policies](#categories--policies)
4. [How to Handle Updates](#how-to-handle-updates)
5. [Troubleshooting](#troubleshooting)
6. [FAQs](#faqs)

---

## Quick Reference

### I see a Dependabot PR. What do I do?

1. **Check the labels:**
   - `security` → Review immediately, merge within 48h
   - `patch` → Auto-merges if tests pass
   - `minor` → Review within 3 days
   - `major` → Needs tech lead approval

2. **Verify tests are passing:**
   - Green checkmark → Good to merge (if appropriate per above)
   - Red X → Investigate failures, may need code changes

3. **Review the changelog:**
   - Look for breaking changes
   - Check if our usage patterns are affected

4. **Merge or request changes:**
   - Approve if safe
   - Request changes if concerns
   - Add comments for context

### Common Commands

```bash
# Check for outdated dependencies
pip list --outdated

# Check for security vulnerabilities
pip-audit

# Update a specific package
pip install --upgrade package-name

# Test after updating
pytest

# Rollback if needed
pip install package-name==old.version
```

---

## Philosophy

Our dependency update strategy balances three priorities:

1. **Security First** - Vulnerabilities are addressed immediately
2. **Stability Second** - We prefer proven stable versions
3. **Currency Third** - We stay reasonably up-to-date but don't chase bleeding edge

We believe:
- Regular small updates are safer than rare large updates
- Automated tools catch most issues early
- Good tests enable confident updates
- Some technical debt (old dependencies) is acceptable short-term

---

## Categories & Policies

[Insert the policy matrix from Step 1]

---

## How to Handle Updates

### Security Updates
[Detailed walkthrough with examples]

### Framework Updates  
[Detailed walkthrough with examples]

### Major Version Migrations
[Link to migration template and examples]

---

## Troubleshooting

### Tests failing after update?
1. Check changelog for breaking changes
2. Update our code to match new API
3. If too complex, create migration plan
4. Document as technical debt if deferring

### Can't update due to conflicts?
1. Check if multiple dependencies need updating together
2. Try updating in order of dependency graph
3. Consider using dependency resolver tools
4. Document as blocked dependency

[... more troubleshooting scenarios ...]

---

## FAQs

**Q: Why can't we just always use the latest versions?**
A: Latest isn't always stable. We wait for versions to be proven in production
by the community before adopting.

**Q: How do I know if a dependency is safe to update?**
A: Check: (1) Does it pass our tests? (2) Is the changelog clear? (3) Is the
new version widely adopted? If yes to all three, likely safe.

**Q: What if I disagree with an auto-merged update?**
A: Revert it, create an issue explaining why, and adjust our policy if needed.

**Q: Who is responsible for dependency updates?**
A: Everyone! It's part of normal development work, not a separate job.

[... more FAQs ...]
```

**Training materials:**
```markdown
# Dependency Update Training - 30 Minute Workshop

## Agenda

### Part 1: Why This Matters (5 min)
- Story: Real incident caused by outdated dependency
- Cost of debt vs. cost of maintenance
- Our philosophy and approach

### Part 2: Hands-On Walkthrough (15 min)
**Activity:** Everyone handles a real Dependabot PR together
1. Find PR in GitHub
2. Review changelog
3. Check test results  
4. Make merge decision
5. Monitor after merge

### Part 3: Tools and Resources (5 min)
- Where to find documentation
- Slack channels for help
- How to escalate issues

### Part 4: Q&A (5 min)
- Open floor for questions
- Address specific scenarios

---

## Post-Training

- [ ] Add everyone to #dependencies Slack channel
- [ ] Share documentation links
- [ ] Assign "dependency buddy" for first week
- [ ] Schedule follow-up in 2 weeks
```

**Feedback loop:**
```markdown
# Dependency Strategy Feedback Form

Please help us improve our dependency update strategy by sharing your experience.

## Overall Experience (1-5 stars)
How would you rate our dependency update process?
[ ] ⭐ [ ] ⭐⭐ [ ] ⭐⭐⭐ [ ] ⭐⭐⭐⭐ [ ] ⭐⭐⭐⭐⭐

## What's Working Well?
[Free text]

## What's Frustrating?
[Free text]

## Specific Issues
- [ ] Too many PRs to review
- [ ] Not clear what to do with PRs
- [ ] Tests take too long
- [ ] Don't understand the policies
- [ ] Security updates too slow
- [ ] Other: ___________

## Suggestions for Improvement
[Free text]

## Would you like to discuss this in person?
[ ] Yes, please contact me
[ ] No, feedback is sufficient

---

Submitted anonymously. Results shared in monthly dependency review.
```

**Verification:**
- [ ] Documentation comprehensive and accessible
- [ ] Team training completed
- [ ] Feedback mechanism established
- [ ] Knowledge shared via wiki/docs site
- [ ] Onboarding includes dependency training

**If This Fails:**
→ If documentation not used: Make it more scannable, add more examples
→ If team still confused: Run more frequent training sessions
→ If no feedback: Actively solicit in retros and 1-on-1s

---

## Verification Checklist

After implementing dependency update strategy:

- [ ] Dependency policies defined and documented
- [ ] Automated tools (Dependabot/Renovate) configured
- [ ] Update cadence established with calendar events
- [ ] Testing requirements defined by risk level
- [ ] Communication channels and escalation paths clear
- [ ] Major version migration process documented
- [ ] Metrics dashboard tracking dependency health
- [ ] Team trained on strategy and tools
- [ ] Documentation comprehensive and accessible
- [ ] Feedback loop for continuous improvement

---

## Best Practices

### DO:
✅ **Update regularly in small increments** - Easier than big-bang updates
✅ **Prioritize security updates** - Address within 24-48 hours
✅ **Trust but verify** - Tests catch most issues, but review changelogs
✅ **Document blocked dependencies** - Track with unblock plans
✅ **Communicate clearly** - Right people notified at right time
✅ **Balance automation with human judgment** - Auto-merge low-risk, review high-risk
✅ **Learn from incidents** - Update strategy based on what breaks
✅ **Celebrate wins** - Recognize team for keeping dependencies healthy

### DON'T:
❌ **Don't ignore automated PRs** - They pile up quickly
❌ **Don't skip testing** - "It's just a patch" famous last words
❌ **Don't defer security updates** - They compound risk
❌ **Don't update everything at once** - Hard to debug if something breaks
❌ **Don't blindly auto-merge everything** - Some updates need review
❌ **Don't let dependencies go stale** - Harder to update later
❌ **Don't update without reading changelog** - Know what's changing
❌ **Don't forget rollback plan** - Always have a way back

---

## Common Issues & Solutions

### Issue: Too Many Dependency PRs Overwhelming Team

**Symptoms:**
- 20+ open Dependabot PRs
- Team ignoring updates
- PRs sit for weeks

**Solution:**
1. Group related updates (framework, dev tools, etc.)
2. Batch low-priority updates weekly
3. Reduce PR frequency in config
4. Enable auto-merge for patch updates

**Prevention:**
Start with aggressive grouping and auto-merge policies, adjust as needed.

---

### Issue: Updates Frequently Break Tests

**Symptoms:**
- Most PRs have failing tests
- Team afraid to merge updates
- Lots of manual fixes required

**Solution:**
1. Improve test stability (flaky tests are the real problem)
2. Increase test coverage before updating
3. Update dependencies more frequently (smaller changes)
4. Review and fix tests before dependency updates

**Prevention:**
Invest in test quality first. Dependencies aren't the problem, tests are.

---

### Issue: Security Updates Taking Too Long

**Symptoms:**
- Security PRs sit for >3 days
- Multiple high-severity vulnerabilities open
- No clear ownership

**Solution:**
1. Assign on-call role for security updates
2. Add security updates to daily standup
3. Enable auto-merge for security patches (with tests)
4. Create escalation path to eng leadership

**Prevention:**
Make security updates non-negotiable priority with clear ownership.

---

### Issue: Team Doesn't Follow Strategy

**Symptoms:**
- Policies ignored
- Random ad-hoc updates
- No consistency

**Solution:**
1. Understand why (too complex? unclear? disagree?)
2. Simplify policies to bare essentials
3. Make it easier to follow than to bypass
4. Enforce in code review and CI

**Prevention:**
Keep strategy simple and make compliance path of least resistance.

---

## Related Workflows

**Prerequisites:**
- [Environment Initialization](./environment_initialization.md) - Set up dependency management
- [Test Writing](./test_writing.md) - Tests enable safe updates

**Next Steps:**
- [Dependency Upgrade](./dependency_upgrade.md) - Execute specific updates
- [CI/CD Pipeline](./ci_cd_workflow.md) - Automate testing of updates
- [Rollback Procedure](./rollback_procedure.md) - Handle failed updates

**Related:**
- [Security Best Practices](../security/code_buddy_secret_rules.md) - Secure dependency handling
- [Technical Debt Management](./technical_debt_mgmt.md) - Track blocked dependencies
- [Version Release Tagging](./version_release_tagging.md) - Version your own code

---

## Tags
`development` `dependencies` `security` `automation` `strategy` `policy` `maintenance`
