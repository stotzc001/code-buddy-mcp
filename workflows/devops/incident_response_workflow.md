---
title: Incident Response Workflow
description: Comprehensive workflow for managing production incidents from detection through resolution and post-mortem
category: DevOps
subcategory: Incident Management
tags: [devops, incident-management, on-call, troubleshooting, monitoring, sre]
technologies: [PagerDuty, Datadog, Slack, Git, Kubernetes]
complexity: complex
estimated_time_minutes: 60
use_cases: [Production outages, Service degradation, Security incidents, Data issues, Performance problems]
problem_statement: Production incidents require coordinated response to minimize impact, restore service quickly, and learn from failures
author: Code Buddy Team
---

# Incident Response Workflow

**ID:** dvo-008  
**Category:** DevOps  
**Priority:** CRITICAL  
**Complexity:** Complex  
**Estimated Time:** Variable (30 minutes to several hours)  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Structured process for detecting, responding to, and resolving production incidents while minimizing user impact and ensuring proper communication.

**Why:**
- Reduces mean time to resolution (MTTR)
- Prevents chaotic, uncoordinated responses
- Ensures proper documentation and learning
- Maintains customer trust through transparency
- Creates audit trail for compliance

**When to use:**
- Service outages or degradation
- Security breaches or suspicious activity
- Data integrity issues
- Performance problems affecting users
- Alert threshold breaches
- Customer-reported critical issues

---

## Prerequisites

**Required:**
- [ ] On-call schedule established
- [ ] Incident management tool access (PagerDuty, Opsgenie)
- [ ] Monitoring dashboard access (Datadog, Grafana, CloudWatch)
- [ ] Communication channel access (Slack, Teams)
- [ ] Production system access
- [ ] Incident response runbook
- [ ] Contact list for escalations

**Tools setup:**
```bash
# Verify access to critical systems
kubectl get nodes  # Kubernetes access
aws sts get-caller-identity  # AWS access
datadog --version  # Monitoring CLI

# Check communication tools
slack-cli auth test
pagerduty-cli incident list

# Verify you're on-call
pagerduty-cli oncall show
```

**Check before responding:**
- [ ] Incident severity classification defined
- [ ] Escalation paths documented
- [ ] Status page credentials available
- [ ] Rollback procedures tested
- [ ] Emergency contacts list current

---

## Implementation Steps

### Step 1: Detect and Acknowledge (2-5 minutes)

**What:** Receive alert, acknowledge incident, and prevent alert fatigue for team.

**How:**

1. **Alert received via:**
```bash
# PagerDuty notification
# SMS, email, phone call, mobile push

# Monitoring system
# Datadog, New Relic, Prometheus alerts

# Customer reports
# Support tickets, social media, direct contact
```

2. **Acknowledge immediately:**
```bash
# Via PagerDuty
pagerduty-cli incident ack --id P1234567

# Or mobile app
# Click "Acknowledge" in PagerDuty app

# Via Slack
# Click "Acknowledge" button in alert message
```

3. **Initial assessment (30 seconds):**
```
Quick check:
- What service is affected?
- How many users impacted?
- Since when did this start?
- Is it getting worse?
```

**Severity classification:**

| Level | Impact | Response Time | Examples |
|-------|--------|---------------|----------|
| **SEV-1 (Critical)** | Complete outage or data loss | Immediate | API down, DB corrupted, security breach |
| **SEV-2 (High)** | Major feature broken | < 30 min | Payment processing down, login issues |
| **SEV-3 (Medium)** | Degraded performance | < 2 hours | Slow API response, partial feature failure |
| **SEV-4 (Low)** | Minor issues | < 24 hours | Edge case bug, cosmetic issues |

**Verification:**
- [ ] Alert acknowledged within 5 minutes
- [ ] Severity level determined
- [ ] Team aware you're responding
- [ ] Incident timer started

**If This Fails:**
→ If you can't acknowledge, escalate immediately to backup on-call
→ If unsure of severity, assume higher severity and de-escalate later

---

### Step 2: Assemble Incident Response Team (5 minutes)

**What:** Gather the right people based on incident severity and scope.

**How:**

**For SEV-1 (Critical):**
```bash
# Page entire incident response team
slack-notify "#incident-response" \
  "@here SEV-1 INCIDENT: API completely down
  
  Incident Commander: @oncall-engineer
  Symptoms: All health checks failing
  Impact: 100% of users affected
  
  Join war room: /zoom/incident-room
  Incident doc: https://docs.company.com/incidents/20250125"

# Page specific roles
pagerduty-cli incident trigger \
  --service "engineering-manager" \
  --title "SEV-1: API Down" \
  --urgency "high"
```

**Role assignments:**
```
SEV-1 Incident Roles:

✅ Incident Commander (IC)
   - Coordinates response
   - Makes key decisions
   - Manages communication
   
✅ Technical Lead
   - Drives technical investigation
   - Implements fixes
   - Coordinates with engineers

✅ Communications Lead
   - Updates status page
   - Communicates with customers
   - Coordinates with support

✅ Scribe
   - Documents timeline
   - Records decisions
   - Tracks action items

Optional:
- Subject Matter Experts (SMEs)
- Customer Success rep
- Legal (for security/data incidents)
- PR (for high-visibility incidents)
```

**For SEV-2/3:**
```bash
# Smaller team, async coordination
slack-notify "#engineering-oncall" \
  "SEV-2: Payment processing slow
  
  Lead: @oncall
  Monitoring: https://dashboard.datadog.com/payments
  
  Working on it, will update in 15 min"
```

**Create incident workspace:**
```bash
# Zoom/Google Meet for SEV-1
zoom create-room --instant --name "incident-20250125"

# Slack channel
slack-cli channel create "incident-20250125-api-down"
slack-cli channel invite @engineering-team

# Incident document
notion create "Incident 2025-01-25: API Outage" \
  --template incident-response
```

**Verification:**
- [ ] Incident Commander assigned
- [ ] Key roles filled based on severity
- [ ] Communication channel established
- [ ] Incident document created
- [ ] War room started (for SEV-1)

---

### Step 3: Assess and Communicate (10 minutes)

**What:** Understand the scope and communicate status to stakeholders.

**How:**

**Quick assessment:**
```bash
# 1. Check monitoring dashboards
open "https://dashboard.datadog.com/overview"

# 2. Review recent deployments
git log --oneline origin/production -10

# 3. Check error logs
kubectl logs -l app=api --tail=100 -n production | grep ERROR

# 4. Query metrics
datadog query "avg:system.cpu.user{service:api}" --last 1h

# 5. Check external status
curl -I https://api.yourservice.com/health
curl https://status.aws.amazon.com

# 6. Review alerts
pagerduty-cli incident list --status triggered
```

**Initial status update (within 10 minutes):**
```markdown
# Status Page Update Template

**What we know:**
We are investigating issues with [service] that began at [time].

**Impact:**
[X%] of users are experiencing [symptoms].

**What we're doing:**
Our team is actively investigating the root cause.

**Updates:**
We will provide updates every 30 minutes or as significant 
developments occur.

Last updated: [timestamp]
```

**Post to status page:**
```bash
# Statuspage.io
curl -X POST https://api.statuspage.io/v1/incidents \
  -H "Authorization: OAuth $STATUSPAGE_TOKEN" \
  -d '{
    "incident": {
      "name": "API Service Disruption",
      "status": "investigating",
      "impact": "major",
      "body": "We are investigating...",
      "component_ids": ["api-service"]
    }
  }'

# Or manually update
open "https://manage.statuspage.io"
```

**Internal communication:**
```bash
# Slack stakeholder update
slack-notify "#exec-team" \
  "🚨 SEV-1 Incident Update
  
  Status: Investigating
  Service: API
  Impact: 85% of API requests failing
  Started: 14:23 UTC
  Team: 5 engineers responding
  
  IC: @alice
  Next update: 15:00 UTC
  
  Live updates: #incident-20250125-api-down"

# Email executives
mail-send executives@company.com \
  --subject "SEV-1: API Service Disruption" \
  --body-file incident-update.txt
```

**Verification:**
- [ ] Impact scope determined
- [ ] Status page updated
- [ ] Stakeholders notified
- [ ] Customer support briefed
- [ ] Update schedule established (every 30 min)

---

### Step 4: Investigate and Diagnose (15-45 minutes)

**What:** Find the root cause of the incident.

**How:**

**Investigation checklist:**
```markdown
1. Recent Changes
   - [ ] Deployments in last 4 hours?
   - [ ] Configuration changes?
   - [ ] Infrastructure modifications?
   - [ ] Traffic pattern changes?

2. System Health
   - [ ] CPU/Memory/Disk usage normal?
   - [ ] Network connectivity OK?
   - [ ] Database connections available?
   - [ ] Queue depths normal?

3. Dependencies
   - [ ] Third-party services up?
   - [ ] Internal services responding?
   - [ ] DNS resolving correctly?
   - [ ] SSL certificates valid?

4. Data Integrity
   - [ ] Database consistent?
   - [ ] Cache coherent?
   - [ ] File systems not full?
```

**Systematic investigation:**
```bash
# 1. Check recent deployments
git log --since="4 hours ago" origin/production
kubectl rollout history deployment/api -n production

# 2. Review metrics
datadog dashboard "api-overview"
# Look for anomalies:
# - CPU spikes
# - Memory leaks
# - Error rate increases
# - Response time degradation

# 3. Analyze logs
kubectl logs -l app=api --since=1h -n production \
  | grep -E "ERROR|FATAL|Exception" \
  | sort | uniq -c | sort -rn

# 4. Check dependencies
curl https://status.aws.amazon.com
curl https://status.stripe.com
dig api.yourservice.com

# 5. Database investigation
psql -h prod-db -c "
  SELECT pid, state, query, state_change
  FROM pg_stat_activity
  WHERE state != 'idle'
  ORDER BY state_change;
"

# 6. Network tracing
kubectl exec -it api-pod -n production -- \
  tcpdump -i any -n port 443

# 7. Check resource limits
kubectl top pods -n production
kubectl describe pod api-xyz -n production | grep -A5 "Limits"
```

**Common patterns to look for:**
```
🔍 Deployment Issues
   - New version deployed recently
   - Rollout incomplete/stuck
   - Configuration mismatch

🔍 Resource Exhaustion
   - Memory leak (growing RSS)
   - File descriptor leak
   - Database connection pool full

🔍 Cascade Failures
   - One service down → others fail
   - Retry storms
   - Circuit breakers not working

🔍 External Dependencies
   - AWS outage
   - Payment provider down
   - DNS issues

🔍 Traffic Anomalies
   - DDoS or bot traffic
   - Viral feature causing load
   - Scheduled job overload
```

**Document findings:**
```markdown
## Investigation Timeline

14:23 - Incident detected, API health checks failing
14:25 - Checked recent deployments: v2.34 deployed at 14:15
14:28 - Reviewed logs: database connection errors
14:30 - Database checks: connection pool exhausted
14:32 - Root cause identified: connection leak in v2.34

## Root Cause
New deployment (v2.34) introduced connection leak in 
payment processing module. Each request opens DB connection
but fails to close it on error path.

## Evidence
- git diff v2.33..v2.34 src/payments.py
- Line 234: missing conn.close() in except block
- Confirmed: connection pool grew from 10 → 100 in 15 minutes
```

**Verification:**
- [ ] Root cause identified with confidence
- [ ] Evidence documented
- [ ] Timeline maintained
- [ ] Hypothesis tested
- [ ] Team agrees on diagnosis

**If This Fails:**
→ If root cause unclear, implement mitigation (rollback, increase resources)
→ Continue investigation after service restored

---

### Step 5: Implement Fix (10-30 minutes)

**What:** Restore service using the fastest safe method.

**How:**

**Mitigation options (fastest to slowest):**

**Option 1: Rollback (5-10 min)**
```bash
# Fastest recovery for deployment issues
kubectl rollout undo deployment/api -n production
kubectl rollout status deployment/api -n production

# Verify health
curl https://api.yourservice.com/health
# Should return 200 OK

# Update status
slack-notify "#incident-response" \
  "✅ Rolled back to v2.33, monitoring for recovery"
```

**Option 2: Configuration change (5-15 min)**
```bash
# Fix via config without code change
kubectl edit configmap api-config -n production

# Update database connection pool
max_connections: 200  # Was 100

# Restart to pick up config
kubectl rollout restart deployment/api -n production
```

**Option 3: Hotfix deployment (15-30 min)**
```bash
# See emergency_hotfix.md workflow
git checkout -b hotfix/connection-leak-20250125
# Make minimal fix
git commit -m "HOTFIX: Close DB connections in error path"
# Deploy (follow hotfix workflow)
./scripts/deploy.sh production --hotfix
```

**Option 4: Scale resources (2-5 min)**
```bash
# Temporary mitigation while fixing
kubectl scale deployment/api --replicas=20 -n production
kubectl autoscale deployment/api --min=10 --max=50

# Or increase resource limits
kubectl set resources deployment/api \
  --limits=memory=4Gi,cpu=2000m \
  -n production
```

**Option 5: Feature flag toggle (1-2 min)**
```bash
# Disable broken feature immediately
curl -X POST https://api.yourservice.com/admin/features \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"payment_v2": false}'

# Verify disabled
curl https://api.yourservice.com/admin/features | jq .payment_v2
```

**Implementing fix:**
```bash
# 1. Announce action
slack-notify "#incident-response" \
  "🔧 Implementing fix: Rolling back to v2.33
  Expected downtime: 2 minutes
  Status updates every 60 seconds"

# 2. Execute fix
kubectl rollout undo deployment/api -n production

# 3. Monitor closely
watch 'kubectl get pods -n production && \
       curl -s https://api.yourservice.com/health | jq .'

# 4. Verify recovery
# - Health checks green
# - Error rate dropped
# - Response times normal
# - Customer reports stopping
```

**Verification:**
- [ ] Fix implemented
- [ ] Service responding normally
- [ ] Error rate acceptable
- [ ] Metrics returned to baseline
- [ ] Customer impact reduced

---

### Step 6: Monitor and Verify Resolution (15-30 minutes)

**What:** Confirm incident is fully resolved and won't recur.

**How:**

```bash
# Monitor key metrics for 15-30 minutes
datadog dashboard "incident-recovery" --watch

# Check specific indicators:
# ✅ API success rate > 99.5%
# ✅ Response time < p95 threshold
# ✅ Error rate < 0.1%
# ✅ No new alerts firing

# Customer verification
# - Support ticket rate decreased
# - Social media complaints stopped
# - No new customer reports

# System health
kubectl get pods -n production  # All Running
kubectl top pods -n production  # Resources normal
psql -h prod-db -c "SELECT count(*) FROM pg_stat_activity;"  # Connections normal
```

**Declare resolution:**
```markdown
**When to declare resolved:**
✅ Service fully operational for 15+ minutes
✅ Error rates at normal levels
✅ No ongoing customer impact
✅ Monitoring stable
✅ Root cause understood
✅ Fix verified effective

**Status page update:**
"RESOLVED: The issue affecting [service] has been resolved.
All services are operating normally. 

Root cause: [brief explanation]
Resolution: [what we did]
Duration: [total time]

We will conduct a post-mortem and share learnings.

Resolved at: [timestamp]"
```

**Close incident:**
```bash
# Update status page
curl -X PATCH https://api.statuspage.io/v1/incidents/abc123 \
  -d '{"incident": {"status": "resolved"}}'

# Close PagerDuty incident
pagerduty-cli incident resolve --id P1234567

# Archive Slack channel (after post-mortem)
slack-cli channel archive incident-20250125-api-down

# Final stakeholder update
slack-notify "#exec-team" \
  "✅ RESOLVED: API incident
  
  Duration: 47 minutes
  Root cause: Database connection leak in v2.34
  Resolution: Rollback to v2.33
  Impact: ~10,000 failed requests
  
  Post-mortem scheduled for tomorrow 2pm
  
  Thanks to response team: @alice @bob @charlie"
```

**Verification:**
- [ ] Service stable for 30+ minutes
- [ ] No customer complaints
- [ ] All metrics normal
- [ ] Status page updated to "Resolved"
- [ ] PagerDuty incident closed
- [ ] Stakeholders notified

---

### Step 7: Conduct Post-Mortem (Within 48 hours)

**What:** Learn from the incident to prevent future occurrences.

**How:**

**Schedule post-mortem meeting:**
```markdown
Attendees:
- Incident Commander
- Technical responders
- Engineering Manager
- Product Manager (if customer-facing)
- Anyone who wants to learn

Agenda (1 hour):
1. Timeline review (15 min)
2. Root cause analysis (15 min)
3. What went well (10 min)
4. What could improve (15 min)
5. Action items (5 min)
```

**Post-mortem document template:**
```markdown
# Incident Post-Mortem: API Outage - 2025-01-25

## Summary
On January 25, 2025 at 14:23 UTC, our API experienced a 
47-minute outage affecting 85% of requests due to a database 
connection leak introduced in deployment v2.34.

## Impact
- Duration: 47 minutes
- Users affected: ~10,000
- Requests failed: ~50,000
- Revenue impact: ~$5,000

## Timeline
| Time | Event |
|------|-------|
| 14:15 | v2.34 deployed to production |
| 14:23 | First alerts: API health checks failing |
| 14:25 | Incident Commander paged, SEV-1 declared |
| 14:28 | Investigation started, logs reviewed |
| 14:32 | Root cause identified: connection leak |
| 14:35 | Decision: rollback to v2.33 |
| 14:38 | Rollback completed |
| 14:45 | Service recovery confirmed |
| 15:10 | Incident declared resolved |

## Root Cause
Deployment v2.34 introduced code that failed to close database
connections on error paths in payment processing. Under load,
this exhausted the connection pool (max 100 connections) within
15 minutes.

Code change:
```python
# Missing connection cleanup
try:
    result = db.execute(query)
except Exception as e:
    logger.error(e)
    return None  # ❌ Connection leaked here
```

## What Went Well
✅ Detection was quick (8 minutes from deploy to alert)
✅ Team responded within 5 minutes
✅ Root cause found in 14 minutes
✅ Rollback executed smoothly
✅ Communication was clear and frequent
✅ No data loss occurred

## What Could Have Gone Better
❌ Code review missed the connection leak
❌ Load testing didn't catch the issue
❌ No circuit breaker to prevent cascade
❌ Initial rollback took 15 minutes (should be faster)
❌ Status page update was delayed by 10 minutes

## Action Items

| Action | Owner | Deadline | Priority |
|--------|-------|----------|----------|
| Add connection lifecycle tests | @alice | 2025-02-01 | P0 |
| Implement connection pool monitoring | @bob | 2025-02-01 | P0 |
| Improve code review checklist for resource leaks | @charlie | 2025-02-05 | P1 |
| Add circuit breaker to database layer | @diana | 2025-02-15 | P1 |
| Automate rollback for common failure patterns | @erik | 2025-03-01 | P2 |
| Load test database connection handling | @alice | 2025-02-01 | P1 |

## Lessons Learned
1. Resource lifecycle bugs are hard to catch in unit tests
2. Load testing should include error injection
3. Fast rollback is critical for rapid recovery
4. Connection pool monitoring should alert earlier
5. Code review needs specific checklists for common issues
```

**Follow-up:**
```bash
# Create GitHub issues for action items
gh issue create \
  --title "[Post-mortem] Add connection lifecycle tests" \
  --label "incident-followup,P0" \
  --assignee @alice \
  --body "From incident 2025-01-25 post-mortem..."

# Schedule follow-up review (2 weeks)
gcal create-event \
  --title "Incident Action Items Review" \
  --date "2025-02-08" \
  --attendees "@incident-team"

# Update runbooks
git checkout -b update-runbook-connection-leaks
# Edit docs/runbooks/database-issues.md
git commit -m "Add connection leak detection to runbook"
```

**Verification:**
- [ ] Post-mortem completed within 48 hours
- [ ] All action items assigned with deadlines
- [ ] Document shared with engineering team
- [ ] Lessons incorporated into training
- [ ] Follow-up review scheduled

---

## Verification Checklist

After completing this workflow:

- [ ] Incident detected and acknowledged within 5 minutes
- [ ] Appropriate team assembled
- [ ] Status communicated to stakeholders
- [ ] Root cause identified
- [ ] Service restored
- [ ] Incident documented thoroughly
- [ ] Post-mortem conducted
- [ ] Action items created and tracked
- [ ] Lessons shared with team

---

## Common Issues & Solutions

### Issue: Cannot Find Root Cause Quickly

**Symptoms:**
- Investigation taking too long
- Multiple competing theories
- No clear evidence

**Solution:**
```bash
# Prioritize restoration over investigation
# 1. Implement mitigation immediately
kubectl rollout undo deployment/api

# 2. Continue investigation after service restored
# 3. Focus on "what changed recently"
git log --since="6 hours ago" --all
```

**Prevention:**
- Better observability (distributed tracing)
- Automated change tracking
- Pre-incident load testing

---

### Issue: Fix Makes Things Worse

**Symptoms:**
- Attempted fix causes new problems
- Metrics deteriorating
- More services affected

**Solution:**
```bash
# STOP - Revert immediately
kubectl rollout undo deployment/api

# Reassess
# - Was diagnosis correct?
# - Did we test the fix?
# - What did we miss?

# Get help
slack-notify "#engineering-all" \
  "Need senior engineer help on SEV-1 incident"
```

**Prevention:**
- Test fixes in staging first
- Use canary deployments
- Have rollback plan before fixing

---

### Issue: Multiple Simultaneous Incidents

**Symptoms:**
- Several alerts firing
- Multiple services affected
- Team overwhelmed

**Solution:**
```markdown
Triage Priority:
1. P0: Complete outages, data loss
2. P1: Major feature broken
3. P2: Degraded performance
4. P3: Minor issues

Strategy:
- Assign separate IC for each P0/P1
- Defer P2/P3 until critical resolved
- Escalate for more engineers
- Check for common cause (e.g., AWS outage)
```

**Prevention:**
- Better fault isolation
- Circuit breakers between services
- Chaos engineering testing

---

## Best Practices

### DO:
✅ Acknowledge alerts within 5 minutes
✅ Communicate early and often
✅ Document everything in real-time
✅ Focus on restoration first, investigation second
✅ Update status page proactively
✅ Assign clear roles and responsibilities
✅ Conduct blameless post-mortems
✅ Track and complete action items

### DON'T:
❌ Blame individuals during incidents
❌ Skip documentation "until later"
❌ Make changes without announcing
❌ Forget to update stakeholders
❌ Rush fixes without testing
❌ Skip post-mortem
❌ Ignore action items from previous incidents
❌ Panic or work in isolation

---

## Related Workflows

**Prerequisites:**
- [[dvo-001]](./application_monitoring_setup.md) - Application Monitoring Setup
- On-call rotation established

**Next Steps:**
- [[dvo-013]](./emergency_hotfix.md) - Emergency Hotfix (if code fix needed)
- [[dvo-015]](./rollback_procedure.md) - Rollback Procedure
- Post-mortem documentation

**Complementary:**
- [[sec-003]](../security/secret_incident_solo.md) - Secret Incident Response (for security incidents)
- [[dvo-012]](./performance_tuning.md) - Performance Tuning (for performance incidents)

**Alternatives:**
- Automated remediation (for known issues)
- Runbook automation
- Self-healing systems

---

## Tags
`devops` `incident-management` `on-call` `troubleshooting` `monitoring` `sre` `post-mortem` `communication`
