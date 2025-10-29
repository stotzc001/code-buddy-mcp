# Hotfix Procedure

**Category:** Development  
**Complexity:** Intermediate  
**Estimated Time:** 30 minutes - 2 hours  
**Prerequisites:** Production access, deployment permissions  

---

## Overview

A hotfix is an emergency fix deployed directly to production to address critical issues. This workflow ensures hotfixes are deployed safely while maintaining code quality and proper documentation, even under time pressure.

**When to Use:**
- Critical security vulnerability discovered
- Production-breaking bug affecting all users
- Data integrity issue requiring immediate fix
- Compliance violation that must be resolved urgently
- Revenue-impacting defect

**When NOT to Use:**
- Minor bugs that can wait for normal release cycle
- Feature requests, even if urgent
- Performance optimizations (unless causing downtime)
- Cosmetic issues

---

## Quick Start

```bash
# 1. Assess severity and get approval
# 2. Create hotfix branch from production tag
git checkout -b hotfix/critical-auth-bypass v1.2.3
# 3. Make minimal fix
# 4. Test thoroughly
# 5. Deploy to production
# 6. Merge back to main and develop branches
```

---

## Step-by-Step Guide

### Phase 1: Assessment & Approval (5-15 minutes)

**Determine Severity:**

```markdown
## Severity Matrix

**CRITICAL (Hotfix Required):**
- Complete service outage
- Security breach or vulnerability
- Data loss or corruption
- Financial impact (payments broken, billing issues)
- Legal/compliance violations

**HIGH (Consider Hotfix):**
- Partial service degradation affecting >50% of users
- Significant feature completely broken
- Performance degradation causing timeouts

**MEDIUM (Normal Release):**
- Feature partially working
- Affects <50% of users
- Workaround available
- Can wait 24-48 hours

**LOW (Normal Release):**
- Cosmetic issues
- Minor bugs
- Edge cases
- Can wait for next sprint
```

**Get Approval:**
```bash
# Document the issue
cat << EOF > hotfix-assessment.md
## Hotfix Request

**Issue:** Authentication bypass allowing unauthorized access
**Severity:** CRITICAL
**Impact:** All users affected, security vulnerability
**Discovered:** 2024-01-15 14:30 UTC
**Reporter:** Security team
**Estimated Fix Time:** 45 minutes
**Risk if Delayed:** Active exploitation possible

**Approvers:**
- [ ] Engineering Manager: ___________
- [ ] On-call Lead: ___________
- [ ] CTO (for critical issues): ___________
EOF

# Get verbal or Slack approval for critical issues
# Document approval in ticket/Slack thread
```

---

### Phase 2: Create Hotfix Branch (5 minutes)

**Branch from Production Tag:**

```bash
# Find current production version
git fetch --tags
git tag -l | grep -E "^v[0-9]" | sort -V | tail -1
# Output: v1.2.3

# Create hotfix branch from production tag
git checkout -b hotfix/auth-bypass-fix v1.2.3

# For git-flow users
git flow hotfix start auth-bypass-fix v1.2.3

# Verify you're on the right base
git log --oneline -1
# Should show: v1.2.3 tag commit
```

**Branch Naming Conventions:**
```bash
# Format: hotfix/<issue-id>-<brief-description>
hotfix/SEC-123-auth-bypass
hotfix/PROD-456-payment-failure
hotfix/critical-memory-leak

# Or with version number
hotfix/1.2.4-auth-bypass
```

---

### Phase 3: Implement the Fix (15-60 minutes)

**Keep Changes Minimal:**

```python
# ❌ BAD: Using hotfix as opportunity to refactor
def authenticate_user(token):
    # Let's rewrite the whole auth system while we're here
    new_auth_system = CompleteRewrite()
    return new_auth_system.validate(token)

# ✅ GOOD: Minimal, targeted fix
def authenticate_user(token):
    # Fix: Add null check to prevent bypass
    if not token:
        return False
    
    # Existing validation logic
    return validate_token(token)
```

**Testing Checklist:**
```bash
# Run relevant unit tests
pytest tests/test_auth.py -v

# Run integration tests
pytest tests/integration/test_auth_flow.py -v

# Manual testing in staging/local
# 1. Verify fix resolves the issue
# 2. Verify no regression in happy path
# 3. Test edge cases related to the fix

# Performance check (if applicable)
# Ensure fix doesn't introduce performance regression
```

**Document the Change:**
```bash
git commit -m "hotfix: Fix authentication bypass vulnerability

- Add null check before token validation
- Prevents unauthenticated access via empty token
- Addresses SEC-123

SECURITY: This fixes a critical security vulnerability
discovered on 2024-01-15. All token validation now properly
checks for null/empty tokens before proceeding.

Tested:
- Unit tests pass
- Integration tests pass  
- Manual verification in staging
- No performance impact measured"
```

---

### Phase 4: Expedited Code Review (15-30 minutes)

**Request Immediate Review:**

```markdown
# Slack Message Template

🚨 HOTFIX PR Ready for Review - URGENT

**Issue:** Critical authentication bypass vulnerability
**PR:** https://github.com/org/repo/pull/1234
**Branch:** hotfix/auth-bypass-fix
**Reviewers:** @tech-lead @security-team
**ETA to deploy:** 30 minutes

**Change Summary:**
- Added null check in authentication flow
- 5 lines changed, 15 lines of tests added
- All tests passing

**Testing Done:**
- ✅ Unit tests
- ✅ Integration tests
- ✅ Manual verification in staging
- ✅ Security team validated fix

**Urgency:** Production security vulnerability, needs immediate deployment

Please review ASAP - ping me with any questions!
```

**Review Checklist (for reviewer):**
```markdown
## Hotfix Review Checklist

- [ ] Fix addresses the stated problem
- [ ] Changes are minimal and focused
- [ ] No unrelated changes included
- [ ] Tests added/updated appropriately
- [ ] No obvious regressions
- [ ] Deployment plan is clear
- [ ] Rollback plan is documented
- [ ] Changes will merge cleanly to main branch

**For Critical Security Fixes:**
- [ ] Security team has reviewed
- [ ] Fix doesn't introduce new vulnerabilities
- [ ] No sensitive data exposed in logs/errors
```

---

### Phase 5: Deploy to Production (15-30 minutes)

**Pre-Deployment Checklist:**

```bash
# 1. Tag the hotfix
git tag -a v1.2.4 -m "Hotfix: Authentication bypass fix (SEC-123)"
git push origin v1.2.4

# 2. Verify CI/CD pipeline
# Check that all tests pass
# Check that build succeeds

# 3. Prepare monitoring
# Open relevant dashboards
# Set up alerts for error rates
# Have logs ready to check

# 4. Communicate deployment
# Post in incident channel
# Update status page if needed
# Notify stakeholders
```

**Deploy:**

```bash
# Option 1: Automated deployment
./deploy.sh production v1.2.4

# Option 2: Manual deployment (Kubernetes example)
kubectl set image deployment/api-server \
  api-server=myorg/api-server:v1.2.4 \
  -n production

# Watch the rollout
kubectl rollout status deployment/api-server -n production

# Option 3: Blue-green deployment
# Deploy to blue environment
# Run smoke tests
# Switch traffic to blue
# Keep green as instant rollback option
```

**Post-Deployment Verification:**

```bash
# 1. Check health endpoint
curl https://api.example.com/health
# Expected: 200 OK

# 2. Verify the fix
# Test the scenario that was broken

# 3. Check error rates
# Error rate should return to normal
# No new errors introduced

# 4. Monitor for 15-30 minutes
# Watch metrics, logs, alerts
# Look for any unexpected behavior

# 5. Confirm with stakeholders
# Security team: vulnerability resolved
# Users: functionality restored
# Monitoring: all green
```

---

### Phase 6: Merge Back to Main Branches (30 minutes)

**Merge to Main/Master:**

```bash
# Merge hotfix to main branch
git checkout main
git merge --no-ff hotfix/auth-bypass-fix
git push origin main

# Or via PR (preferred for audit trail)
gh pr create \
  --base main \
  --head hotfix/auth-bypass-fix \
  --title "Merge hotfix: Authentication bypass fix" \
  --body "Merging v1.2.4 hotfix back to main branch"
```

**Merge to Develop:**

```bash
# Merge hotfix to develop branch
git checkout develop
git merge --no-ff hotfix/auth-bypass-fix

# Resolve any conflicts
# Test that develop still works after merge

git push origin develop
```

**Clean Up:**

```bash
# Delete hotfix branch (locally and remote)
git branch -d hotfix/auth-bypass-fix
git push origin --delete hotfix/auth-bypass-fix

# For git-flow users
git flow hotfix finish auth-bypass-fix
```

---

## Best Practices

### DO:
✅ **Keep changes minimal** - Only fix the specific issue  
✅ **Test thoroughly** - Even under time pressure  
✅ **Document everything** - Future you will thank present you  
✅ **Communicate clearly** - Keep stakeholders informed  
✅ **Merge back to all branches** - Prevent regression in next release  
✅ **Create post-mortem** - Learn from why hotfix was needed  

### DON'T:
❌ **Skip testing** - Never deploy untested code to production  
❌ **Add unrelated changes** - Resist the urge to "fix other stuff too"  
❌ **Work alone** - Get at least one other pair of eyes  
❌ **Skip documentation** - Document the what, why, and how  
❌ **Forget to merge back** - Hotfix must make it to main branch  
❌ **Deploy and disappear** - Monitor for at least 30 minutes  

---

## Common Patterns

### Security Hotfix Pattern

```bash
# Security fixes need extra care

# 1. Coordinate with security team
# 2. Consider notification timeline
#    - Internal first
#    - Customers after fix is deployed
#    - Public disclosure (if applicable) after mitigation

# 3. Don't mention vulnerability in public commit messages
# BAD commit message:
git commit -m "Fix SQL injection in user search"

# GOOD commit message:
git commit -m "Improve input validation in search functionality"

# 4. After deployment, update security advisory
# 5. Document in security changelog
```

### Database Migration Hotfix Pattern

```bash
# When hotfix requires database change

# 1. Make migration reversible
# Example: Adding a column with default value
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;

# 2. Deploy in two phases
# Phase 1: Deploy code that works with OR without new column
# Phase 2: Run migration
# Phase 3: Deploy code that relies on new column

# 3. Test rollback thoroughly
# Ensure rollback doesn't break database state
```

### Multiple Hotfix Pattern

```bash
# When multiple hotfixes are needed simultaneously

# Create separate branches for each
git checkout -b hotfix/issue-1 v1.2.3
git checkout -b hotfix/issue-2 v1.2.3

# Deploy independently
# Tag as v1.2.4, v1.2.5, etc.

# Or combine if related
git checkout -b hotfix/combined-critical-fixes v1.2.3
# Apply all fixes
# Tag as v1.2.4
```

---

## Troubleshooting

### Issue: Hotfix Causes New Problems

**Symptoms:**
- New errors appear after hotfix deployment
- Different functionality breaks
- Performance degrades

**Solution:**
```bash
# Immediate: Rollback
kubectl rollout undo deployment/api-server -n production

# Or revert to previous version
./deploy.sh production v1.2.3

# Investigate what went wrong
# Review logs
kubectl logs deployment/api-server -n production --tail=1000

# Fix the fix
git checkout hotfix/auth-bypass-fix
# Make corrections
git commit -m "Fix issue introduced in hotfix"

# Re-test more thoroughly
# Deploy again when confident
```

---

### Issue: Merge Conflicts When Merging Back

**Symptoms:**
- Git reports conflicts merging hotfix to main/develop
- Files have diverged significantly

**Solution:**
```bash
# Understand the conflicts
git checkout main
git merge hotfix/auth-bypass-fix
# CONFLICT appears

# Review conflicts carefully
git status
git diff

# Resolve conflicts
# Keep hotfix changes, they're critical
# But don't lose new work from main

# Test after merge
npm test

# Commit the merge
git commit -m "Merge hotfix: resolve conflicts with main branch"
```

---

### Issue: Hotfix Needed But No Access

**Symptoms:**
- Critical issue discovered
- Person who can fix it lacks deployment access
- Outside business hours

**Solution:**
```markdown
# Escalation Path

1. **On-call Engineer**: Check PagerDuty/on-call schedule
2. **Engineering Manager**: Escalate if on-call unavailable
3. **CTO/VP Engineering**: Emergency contact for critical issues

# While waiting:
- Document the issue thoroughly
- Prepare the fix locally
- Create PR for review
- Test in staging
- Have everything ready for immediate deployment

# Request temporary access if appropriate
# Document decision in incident notes
```

---

## Related Workflows

**Prerequisites:**
- `devops-xxx_incident_response_workflow.md` - Responding to the incident
- `dev-xxx_version_release_tagging.md` - Understanding version scheme
- `version-control-xxx_branch_strategy.md` - Branching model

**Next Steps:**
- `dev-xxx_post_mortem_workflow.md` - Learning from the incident
- `devops-xxx_rollback_procedure.md` - If hotfix goes wrong
- `qa-xxx_production_testing.md` - Verification after deployment

**Alternatives:**
- `dev-xxx_feature_flag_management.md` - Disable feature instead of hotfix
- `devops-xxx_rollback_procedure.md` - Revert to previous version

---

## Tags

`development` `hotfix` `emergency` `production` `deployment` `incident-response` `critical` `security` `branching`
