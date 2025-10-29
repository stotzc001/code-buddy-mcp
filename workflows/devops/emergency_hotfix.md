---
title: Emergency Hotfix
description: Rapid response workflow for critical production bugs requiring immediate fixes outside normal deployment cycles
category: DevOps
subcategory: Incident Management
tags: [devops, incident, emergency, deployment, hotfix, production]
technologies: [Git, CI/CD, Monitoring, Rollback]
complexity: complex
estimated_time_minutes: 30
use_cases: [Critical bug in production, Security vulnerability, Data corruption, Service outage, Revenue-impacting issues]
problem_statement: Production systems occasionally require immediate fixes that cannot wait for normal release cycles. Emergency hotfixes must be deployed quickly while maintaining safety and traceability.
author: Code Buddy Team
---

# Emergency Hotfix

**ID:** dvo-013  
**Category:** DevOps  
**Priority:** CRITICAL  
**Complexity:** Complex  
**Estimated Time:** 30-120 minutes (varies by severity)  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Execute rapid deployment of critical bug fixes to production with minimal risk and maximum traceability.

**Why:** 
- Production issues can cause revenue loss, data corruption, or security breaches
- Normal deployment cycles (hours/days) are too slow for critical issues
- Quick action required while maintaining safety and quality

**When to use:**
- **Critical severity issues:**
  - Complete service outage
  - Data corruption or loss
  - Security vulnerabilities being exploited
  - Payment processing failures
  - Legal/compliance violations
  
- **NOT for:**
  - Feature requests (use normal deployment)
  - Minor bugs that can wait
  - Performance optimizations
  - Cosmetic issues

---

## Prerequisites

**Required:**
- [ ] Production access credentials
- [ ] Incident commander authority/approval
- [ ] Monitoring access (logs, metrics, alerts)
- [ ] Deployment pipeline access
- [ ] Rollback capability verified
- [ ] Communication channel set up (Slack, PagerDuty, etc.)

**Check before starting:**
```bash
# Verify you have production access
kubectl get nodes  # For k8s
aws sts get-caller-identity  # For AWS
heroku auth:whoami  # For Heroku

# Verify git status
git status  # Clean working directory
git remote -v  # Confirm repository

# Check current production version
curl https://api.yourservice.com/health | jq .version

# Verify rollback capability
git tag --list | grep prod- | tail -5
```

**Emergency contacts ready:**
- [ ] On-call engineer
- [ ] Engineering manager
- [ ] Platform/SRE team
- [ ] Customer support lead

---

## Implementation Steps

### Step 1: Assess and Triage (5-10 minutes)

**What:** Quickly determine severity, impact, and whether hotfix is justified.

**How:**

1. **Gather information:**
```bash
# Check error rates
datadog query "service:api status:error" --last 1h

# Check recent deployments
git log --oneline -10 origin/production

# Check monitoring dashboards
open https://dashboard.datadog.com/production

# Review incident reports
gh issue list --label "incident" --state open
```

2. **Assess severity:**

| Severity | Criteria | Response Time | Examples |
|----------|----------|---------------|----------|
| **P0 - Critical** | Complete outage, data loss | Immediate | Service down, payments failing, data corruption |
| **P1 - High** | Major functionality broken | < 2 hours | Key feature broken, significant user impact |
| **P2 - Medium** | Limited impact | < 24 hours | Minor feature broken, workaround available |
| **P3 - Low** | Minimal impact | Normal cycle | Cosmetic issues, edge cases |

3. **Decision matrix:**
```
Is it P0/P1? YES → Continue with hotfix
             NO  → Schedule for normal deployment

Can it wait 4 hours? YES → Use normal deployment
                     NO  → Continue with hotfix

Is root cause understood? YES → Continue with hotfix
                          NO  → Stabilize first, fix later
```

**Verification:**
- [ ] Severity determined (P0 or P1 only)
- [ ] Impact quantified (users affected, revenue impact)
- [ ] Root cause identified
- [ ] Hotfix justified (cannot wait for normal cycle)
- [ ] Incident commander notified

**If This Fails:**
→ If unsure about root cause, focus on mitigation first (rollback, feature flag)
→ If impact unclear, check with customer support for user reports

---

### Step 2: Create Hotfix Branch (5 minutes)

**What:** Create an isolated branch from production for the emergency fix.

**How:**

```bash
# 1. Start from latest production
git fetch origin
git checkout production  # or main, master depending on workflow
git pull origin production

# 2. Create hotfix branch with descriptive name
git checkout -b hotfix/payment-processing-fix-$(date +%Y%m%d)

# Alternative naming patterns:
# hotfix/issue-1234-payment-fix
# hotfix/CRITICAL-service-down
# hotfix/P0-data-corruption

# 3. Verify starting point
git log --oneline -1
# Should match production deployment

# 4. Create tracking issue
gh issue create \
  --title "HOTFIX: Payment processing failure" \
  --label "hotfix,P0,incident" \
  --body "Production issue requiring immediate fix.
  
Root cause: [description]
Impact: [affected users/revenue]
Fix: [brief description]
Incident: [link to incident doc]"
```

**Branch naming convention:**
```
hotfix/[severity]-[brief-description]-[date]

Examples:
✅ hotfix/P0-payment-gateway-20250125
✅ hotfix/CRITICAL-auth-bypass-20250125
✅ hotfix/data-corruption-fix-20250125

❌ hotfix/fix-bug
❌ fix-payment
❌ emergency
```

**Verification:**
- [ ] Hotfix branch created
- [ ] Branch starts from production HEAD
- [ ] Branch follows naming convention
- [ ] Tracking issue created
- [ ] Team notified in Slack

---

### Step 3: Implement Minimal Fix (15-30 minutes)

**What:** Write the smallest possible fix that resolves the critical issue.

**How:**

**Principles:**
1. **Minimal scope** - Fix ONLY the critical issue
2. **Low risk** - Avoid refactoring or cleanup
3. **Tested** - Include tests that would catch this bug
4. **Reversible** - Easy to rollback if needed

**Example Fix:**
```python
# Bad: Large refactoring in hotfix
def process_payment(amount, currency, user_id):
    # Refactored entire payment system...  ❌ TOO MUCH
    
# Good: Minimal targeted fix
def process_payment(amount, currency, user_id):
    # Added missing validation that caused the bug
    if amount <= 0:  # ✅ MINIMAL FIX
        raise ValueError("Amount must be positive")
    
    # Rest of code unchanged
    return payment_gateway.charge(amount, currency, user_id)
```

**Testing the fix:**
```bash
# Run relevant tests
pytest tests/test_payments.py -v

# Add regression test
# tests/test_payments.py
def test_payment_rejects_negative_amount():
    """Regression test for hotfix/P0-payment-gateway-20250125"""
    with pytest.raises(ValueError, match="Amount must be positive"):
        process_payment(amount=-10, currency="USD", user_id=123)

# Run full test suite if time permits
pytest tests/ --maxfail=1

# Test locally with production-like data
docker-compose up -d
python scripts/test_payment_flow.py
```

**Code review checklist:**
```markdown
Hotfix Review Checklist:
- [ ] Fixes only the critical issue
- [ ] No scope creep (refactoring, cleanup)
- [ ] Includes test that catches the bug
- [ ] No breaking changes
- [ ] Safe to rollback
- [ ] Documented with comments
- [ ] Error handling added if missing
```

**Verification:**
- [ ] Fix implements minimal change
- [ ] Tests pass locally
- [ ] Regression test added
- [ ] Code reviewed (even if brief)
- [ ] Fix confirmed to resolve root cause

**If This Fails:**
→ If tests fail, fix the tests or the code (don't skip tests)
→ If fix is too large, consider feature flag to disable broken feature instead

---

### Step 4: Fast-Track Review & Merge (10-15 minutes)

**What:** Get emergency approval and merge to production.

**How:**

```bash
# 1. Commit with clear message
git add -A
git commit -m "HOTFIX: Fix payment processing negative amount bug

Problem: Payments were processed with negative amounts causing refunds
Root Cause: Missing validation in process_payment()
Solution: Add amount > 0 validation
Impact: Prevents revenue loss from accidental refunds

Fixes #1234
Incident: https://company.pagerduty.com/incidents/123"

# 2. Push and create PR
git push origin hotfix/P0-payment-gateway-20250125

gh pr create \
  --title "🚨 HOTFIX: Fix payment processing negative amounts" \
  --body "## Emergency Hotfix

**Severity:** P0 - Critical
**Impact:** Payment processing failures
**Root Cause:** Missing validation
**Fix:** Added amount validation

## Testing
- [x] Unit tests pass
- [x] Manual testing in staging
- [x] Regression test added

## Rollback Plan
Revert commit: \`git revert <commit>\`

cc: @oncall @engineering-manager" \
  --label "hotfix,P0,urgent" \
  --assignee @oncall

# 3. Request emergency review
slack-notify "#engineering-oncall" \
  "🚨 HOTFIX PR ready for emergency review: [PR link]
  
  Issue: Payment processing bug
  Impact: $X revenue at risk
  Need approval in next 10 minutes"

# 4. Merge after approval (skip normal review process)
gh pr merge --squash --delete-branch
```

**Fast-track approval criteria:**
```
✅ Can fast-track if:
- P0/P1 severity confirmed
- Fix is minimal and targeted
- Tests pass
- At least 1 senior engineer reviewed
- Rollback plan documented

❌ Cannot fast-track if:
- Large code changes
- Tests failing
- No reviewer available
- Rollback unclear
```

**Verification:**
- [ ] PR created with full context
- [ ] Emergency reviewer assigned
- [ ] Tests passing in CI
- [ ] PR approved
- [ ] Branch merged to production

---

### Step 5: Deploy to Production (5-15 minutes)

**What:** Deploy the hotfix to production with monitoring.

**How:**

```bash
# 1. Trigger production deployment
# (Method depends on your CI/CD setup)

# GitHub Actions
gh workflow run deploy-production.yml \
  --ref hotfix/P0-payment-gateway-20250125

# Jenkins
jenkins-cli build "production-deploy" \
  -p BRANCH="production" \
  -p VERSION="hotfix-20250125"

# Manual deployment (if needed)
./scripts/deploy.sh production

# Kubernetes
kubectl set image deployment/api \
  api=myapp:hotfix-20250125 \
  -n production

kubectl rollout status deployment/api -n production

# 2. Monitor deployment
watch kubectl get pods -n production

# 3. Tag the hotfix
git tag -a "hotfix-20250125-payment-fix" -m "Emergency hotfix for payment processing"
git push origin hotfix-20250125-payment-fix
```

**Deployment checklist:**
```markdown
Pre-deployment:
- [ ] Stakeholders notified
- [ ] Monitoring dashboard open
- [ ] Rollback plan ready
- [ ] Error tracking prepared

During deployment:
- [ ] Deployment triggered
- [ ] Health checks passing
- [ ] No new errors in logs
- [ ] Metrics stable

Post-deployment:
- [ ] Fix verified in production
- [ ] Monitoring shows improvement
- [ ] Stakeholders updated
- [ ] Documentation updated
```

**Verification:**
- [ ] Deployment completed successfully
- [ ] Health checks passing
- [ ] No new errors in logs
- [ ] Original issue resolved
- [ ] Metrics returning to normal

**If This Fails:**
→ **ROLLBACK IMMEDIATELY** - See Step 6

---

### Step 6: Monitor and Verify Fix (15-30 minutes)

**What:** Confirm the hotfix resolved the issue without introducing new problems.

**How:**

```bash
# 1. Check error rates
datadog query "service:api status:error" --last 10m

# 2. Check key metrics
curl https://api.yourservice.com/metrics | jq .
# Look for:
# - Error rate decreased
# - Response time normal
# - Success rate improved

# 3. Test the fixed functionality
curl -X POST https://api.yourservice.com/payments \
  -H "Content-Type: application/json" \
  -d '{"amount": -10, "currency": "USD"}' \
  # Should now return 400 error

curl -X POST https://api.yourservice.com/payments \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "currency": "USD"}' \
  # Should work correctly

# 4. Check logs for the fix
kubectl logs -l app=api --tail=100 -n production | grep "Amount must be positive"

# 5. Monitor dashboards for 15-30 minutes
# - Error rates
# - API response times
# - Database connections
# - Queue depths
# - User-reported issues
```

**Success criteria:**
```
✅ Fix is successful if:
- Original issue no longer occurring
- Error rate returned to normal
- No new errors introduced
- Key metrics stable
- Customer reports decreasing

⚠️ Partial success if:
- Issue reduced but not eliminated
- May need additional fix

❌ Failed if:
- Issue still occurring
- New errors introduced
- Metrics worse than before
→ ROLLBACK IMMEDIATELY
```

**Verification:**
- [ ] Original issue resolved
- [ ] No new issues introduced
- [ ] Error rates normal
- [ ] Metrics stable for 15+ minutes
- [ ] Customer support confirms fix

---

## Verification Checklist

After completing this workflow:

- [ ] Critical issue resolved
- [ ] Hotfix deployed to production
- [ ] Monitoring shows improvement
- [ ] No new issues introduced
- [ ] Hotfix documented and tagged
- [ ] Post-mortem scheduled
- [ ] Customer support notified
- [ ] Backport to development branch completed
- [ ] Technical debt ticket created (if needed)

---

## Common Issues & Solutions

### Issue: Hotfix Makes Things Worse

**Symptoms:**
- New errors appearing
- Metrics degrading
- Different functionality broken

**Solution:**
```bash
# IMMEDIATE ROLLBACK
# Kubernetes
kubectl rollout undo deployment/api -n production

# Git revert
git revert HEAD
git push origin production

# Feature flag disable
curl -X POST https://api.yourservice.com/admin/features \
  -d '{"payment_validation": false}'

# Verify rollback successful
curl https://api.yourservice.com/health
```

**Prevention:**
- Smaller, more targeted fixes
- Better testing before deployment
- Feature flags for risky changes
- Canary deployments

---

### Issue: Can't Reproduce Issue in Staging

**Symptoms:**
- Bug occurs in production only
- Cannot test fix locally
- Staging behaves differently

**Solution:**
```bash
# Use production data (safely)
# 1. Copy anonymized production data
pg_dump production_db | \
  python scripts/anonymize.py | \
  psql staging_db

# 2. Use production traffic sampling
kubectl port-forward svc/api 8080:80 -n production
# Test against production (read-only)

# 3. Deploy to canary first
./scripts/deploy.sh canary
# 1% of traffic goes to canary

# Monitor canary
watch 'kubectl logs -l version=canary --tail=50'
```

**Prevention:**
- Production-like staging environment
- Regular data synchronization
- Synthetic production monitoring

---

### Issue: Fix Takes Too Long to Deploy

**Symptoms:**
- CI/CD pipeline taking 30+ minutes
- Too many manual approval gates
- Deployment process too complex

**Solution:**
```bash
# Use emergency fast-track deployment
# Skip non-critical gates
./scripts/deploy-emergency.sh production \
  --skip-integration-tests \
  --skip-approval \
  --fast

# Or deploy directly (last resort)
git push production hotfix/emergency:master
heroku releases:rollback v1234

# Document what you skipped
echo "Skipped full test suite due to P0 emergency" >> incident.log
```

**Prevention:**
- Streamline deployment pipeline
- Separate critical vs non-critical checks
- Pre-approved emergency deployment process
- Feature flags to avoid full deployments

---

## Examples

### Example 1: Payment Gateway Timeout

**Context:** Payment API timing out, causing revenue loss.

**Execution:**
```bash
# 1. Identify issue
grep "payment_timeout" logs/production.log
# Found: timeout set to 5s, gateway needs 10s

# 2. Create hotfix
git checkout -b hotfix/payment-timeout-20250125

# 3. Fix (minimal change)
# Before: PAYMENT_TIMEOUT = 5
# After:  PAYMENT_TIMEOUT = 15

# 4. Test locally
curl -X POST localhost:8000/payment -d '...' -w '%{time_total}'
# Confirmed: completes in 8-12 seconds

# 5. Deploy
git commit -m "HOTFIX: Increase payment timeout to 15s"
./scripts/deploy.sh production --hotfix

# 6. Monitor
datadog query "payment.success_rate" --last 30m
# Success rate: 95% → 99.5% ✅
```

**Result:** Payment success rate restored within 20 minutes.

---

### Example 2: Memory Leak Causing Crashes

**Context:** Application crashing every 2 hours due to memory leak.

**Execution:**
```bash
# 1. Quick mitigation: increase restart frequency
kubectl scale deployment/api --replicas=6
kubectl set probe deployment/api \
  --liveness --period-seconds=300

# 2. Root cause: memory leak in cache
# Review heap dump
jmap -dump:live,file=heap.bin $(pgrep java)
jhat heap.bin

# 3. Hotfix: add cache eviction
git checkout -b hotfix/cache-eviction-20250125

# Code change:
# Before: cache = {}
# After:  cache = TTLCache(maxsize=1000, ttl=3600)

# 4. Test memory growth
python scripts/memory_test.py
# Confirmed: memory stable over 6 hours

# 5. Deploy with gradual rollout
kubectl set image deployment/api api=myapp:hotfix-v2 \
  && kubectl rollout pause deployment/api
# Monitor 10% of pods for 30 minutes
kubectl rollout resume deployment/api

# 6. Monitor for 4 hours
while true; do
  kubectl top pods | grep api
  sleep 300
done
# Memory stable ✅
```

**Result:** Service stabilized, memory usage controlled.

---

## Best Practices

### DO:
✅ Document everything (commands, decisions, timestamps)
✅ Communicate constantly (Slack, PagerDuty, email)
✅ Make minimal changes (fix only the critical issue)
✅ Test the fix (even if quick smoke tests)
✅ Monitor after deployment (watch for 30+ minutes)
✅ Schedule post-mortem within 24 hours
✅ Tag and document the hotfix
✅ Backport fix to development branch

### DON'T:
❌ Skip testing "because it's urgent"
❌ Add features or refactoring
❌ Deploy without rollback plan
❌ Work alone (always have a second person)
❌ Skip documentation "will do later"
❌ Ignore monitoring after deployment
❌ Forget to notify stakeholders
❌ Skip post-mortem

---

## Related Workflows

**Prerequisites:**
- [[dvo-008]](./incident_response_workflow.md) - Incident Response Workflow (for assessment)
- [[ver-001]](../version-control/branch_strategy.md) - Git Branch Strategy

**Next Steps:**
- [[dvo-015]](./rollback_procedure.md) - Rollback Procedure (if hotfix fails)
- [[dvo-001]](./application_monitoring_setup.md) - Application Monitoring Setup
- Post-mortem documentation

**Complementary:**
- [[sec-003]](../security/secret_incident_solo.md) - Secret Incident Response (for security hotfixes)
- [[dvo-014]](./incident_response.md) - Production Incident Response
- [[ver-003]](../version-control/merge_conflict_resolution.md) - Merge Conflict Resolution

**Alternatives:**
- Feature flag toggle (disable broken feature)
- Traffic routing (route around broken service)
- Manual workaround (temporary process change)

---

## Tags
`devops` `incident` `emergency` `deployment` `hotfix` `production` `critical` `rollback` `monitoring`
