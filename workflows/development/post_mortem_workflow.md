# Post-Mortem Workflow

**Category:** Development  
**Complexity:** Intermediate  
**Estimated Time:** 2-4 hours  
**Prerequisites:** Incident resolved, team available  

---

## Overview

A post-mortem (or retrospective) is a structured process for learning from incidents, outages, or significant issues. This workflow guides you through conducting an effective post-mortem that focuses on improving systems and processes rather than assigning blame.

**When to Use:**
- After production incidents or outages
- Following significant bugs that reached production
- After near-misses that could have caused issues
- When you want to learn from a challenging deployment
- Post-project retrospectives for major features

---

## Quick Start

```bash
# 1. Schedule meeting within 24-48 hours of incident resolution
# 2. Gather relevant data (logs, metrics, timeline)
# 3. Follow 5-phase structure below
# 4. Document findings and action items
# 5. Follow up on improvements
```

---

## Step-by-Step Guide

### Phase 1: Preparation (30-60 minutes before meeting)

**Gather Data:**
```bash
# Collect incident timeline
cat incident_timeline.md

# Export relevant logs
kubectl logs deployment/api-server --since=24h > incident_logs.txt

# Export metrics/dashboards
# Save screenshots of relevant graphs showing:
# - Error rates
# - Response times  
# - Resource utilization
# - Traffic patterns

# Gather communication records
# Slack messages, PagerDuty alerts, status page updates
```

**Create Initial Timeline:**
```markdown
## Incident Timeline

**Detection:** 2024-01-15 14:23 UTC - Alert fired for high error rate
**Investigation Started:** 2024-01-15 14:25 UTC - On-call engineer began investigation
**Root Cause Identified:** 2024-01-15 14:45 UTC - Database connection pool exhausted
**Fix Applied:** 2024-01-15 15:10 UTC - Increased connection pool size
**Resolved:** 2024-01-15 15:15 UTC - Error rates returned to normal
**Duration:** 52 minutes
**Impact:** ~500 users affected, order processing delayed
```

---

### Phase 2: Facilitate the Meeting (60-90 minutes)

**Set the Tone:**
```markdown
# Opening Statement Template

"Thank you all for joining. This post-mortem is focused on learning and 
improving our systems - not on blame. We're here to understand what happened,
why it happened, and how we can prevent it in the future.

Everyone's perspective is valuable, especially if you were uncomfortable 
speaking up during the incident. Please share openly."
```

**Review Timeline Collaboratively:**
- Walk through the timeline chronologically
- Ask participants to fill in gaps or corrections
- Note what went well alongside what went wrong
- Document when people felt confused or uncertain

**Key Questions to Ask:**
1. **Detection:** How did we discover the issue?
2. **Communication:** How did information flow during the incident?
3. **Response:** What actions did we take and why?
4. **Contributing Factors:** What circumstances made this possible?
5. **Resilience:** What prevented this from being worse?

---

### Phase 3: Root Cause Analysis (30 minutes)

Use the **5 Whys** technique:

```markdown
## Example: Database Connection Pool Exhaustion

**Problem:** API requests failed with database connection errors

Why? → Connection pool was exhausted
Why? → Too many long-running queries  
Why? → New feature introduced N+1 query pattern
Why? → Code review didn't catch the performance issue
Why? → We don't have automated performance testing for database queries

**Root Causes Identified:**
1. Missing performance testing in CI/CD
2. Code review checklist doesn't include query performance
3. No monitoring for query execution time
```

**Avoid:**
- ❌ Stopping at "human error" - dig deeper
- ❌ Single root cause - there are usually multiple factors
- ❌ Blame or punishment - focus on systems
- ❌ Purely technical causes - include process issues

---

### Phase 4: Action Items (30 minutes)

**Generate Improvement Ideas:**
```markdown
## Brainstorming Categories

1. **Detection & Monitoring**
   - What would have helped us find this sooner?
   - What alerts were missing?

2. **Prevention**
   - What guardrails could prevent this?
   - What automated checks would help?

3. **Response & Tools**
   - What slowed us down during response?
   - What tools or runbooks would have helped?

4. **Communication**
   - How can we improve information flow?
   - Who should have been notified differently?

5. **Documentation**
   - What knowledge was missing?
   - What should we document for next time?
```

**Prioritize Action Items:**
```markdown
## Action Items Template

| Priority | Action | Owner | Due Date | Effort |
|----------|--------|-------|----------|--------|
| 🔴 High | Add connection pool monitoring alert | Sarah | Jan 20 | 2 hours |
| 🔴 High | Create database query performance test | Mike | Jan 25 | 1 day |
| 🟡 Medium | Update code review checklist | Team | Jan 22 | 1 hour |
| 🟢 Low | Document connection pool tuning guide | Alex | Feb 1 | 4 hours |

**Selection Criteria:**
- High: Prevents recurrence of this exact issue
- Medium: Improves detection or response
- Low: General improvements or nice-to-haves
```

---

### Phase 5: Documentation (30-60 minutes post-meeting)

**Create Post-Mortem Document:**

```markdown
# Post-Mortem: Database Connection Pool Exhaustion

**Date:** January 15, 2024  
**Incident Duration:** 52 minutes  
**Severity:** SEV-2 (Service Degradation)  
**Impact:** ~500 users, order processing delayed  
**Author:** [Name]  
**Reviewers:** [Team]  

---

## Executive Summary

Brief 2-3 sentence summary of what happened and key learnings.

---

## What Happened

Chronological narrative of the incident.

---

## Timeline

Detailed timeline with UTC timestamps.

---

## Root Cause Analysis

Technical explanation of why this occurred.

---

## What Went Well

- Fast detection (< 2 minutes)
- Clear communication in incident channel
- Effective collaboration between teams

---

## What Could Be Improved

- Query performance not caught in code review
- No automated performance tests
- Connection pool monitoring gaps

---

## Action Items

[Table from Phase 4]

---

## Lessons Learned

1. Performance impacts from new features need better testing
2. Database monitoring has gaps we need to address
3. Code review checklists should include performance considerations
```

**Share the Document:**
```bash
# Store in accessible location
cp postmortem.md /docs/postmortems/2024-01-15-db-connections.md

# Notify stakeholders
# Share summary in team channel
# Include in weekly engineering newsletter

# Archive for future reference
git add docs/postmortems/2024-01-15-db-connections.md
git commit -m "Add post-mortem for database connection incident"
git push
```

---

## Best Practices

### DO:
✅ **Conduct within 24-48 hours** - Memories are fresh  
✅ **Create blame-free environment** - Encourage honesty  
✅ **Focus on systems** - Not individual mistakes  
✅ **Document what went well** - Celebrate good responses  
✅ **Follow through on actions** - Track completion  
✅ **Share learnings** - Help other teams avoid same issue  

### DON'T:
❌ **Skip post-mortems** - Every incident is a learning opportunity  
❌ **Assign blame** - Focus on improving processes  
❌ **Stop at first answer** - Dig deeper with 5 Whys  
❌ **Create too many actions** - Better to complete 3 than start 10  
❌ **Forget to follow up** - Actions without completion waste time  
❌ **Hide incidents** - Transparency builds trust and learning  

---

## Common Patterns

### Blameless Post-Mortem Language

**Instead of:** "John deployed broken code"  
**Use:** "A deployment containing a bug reached production"

**Instead of:** "Sarah ignored the alert"  
**Use:** "The alert was not actioned within our SLA"

**Instead of:** "The team failed to test"  
**Use:** "Testing did not catch this edge case"

### Action Item Examples

```markdown
## Concrete, Measurable Actions

❌ BAD: "Improve monitoring"
✅ GOOD: "Add alert for connection pool utilization > 80% (Owner: Sarah, Due: Jan 20)"

❌ BAD: "Be more careful in code review"
✅ GOOD: "Add performance checklist item to PR template (Owner: Team, Due: Jan 22)"

❌ BAD: "Better documentation"  
✅ GOOD: "Create runbook for database connection issues (Owner: Mike, Due: Jan 30)"
```

### Long-Running Incident Pattern

```markdown
## Extended Incident Structure

For incidents lasting >4 hours, break timeline into phases:

1. **Detection Phase** (0-30 min)
   - How we found out
   - Initial triage

2. **Investigation Phase** (30 min - 2 hours)
   - Hypotheses explored
   - Dead ends encountered
   - Aha moments

3. **Resolution Phase** (2-4 hours)
   - Fix attempts
   - Rollbacks
   - Final solution

4. **Recovery Phase** (4+ hours)
   - System restoration
   - Verification
   - Communication
```

---

## Troubleshooting

### Issue: People Are Defensive During Meeting

**Symptoms:**
- Team members making excuses
- Reluctance to share what really happened
- Finger pointing or blame

**Solution:**
```markdown
# Restate Ground Rules

"I want to pause and remind everyone - this is a blameless post-mortem.
We're here to improve systems, not judge people. Every system we build
has failure modes, and it's our job to find and fix them.

Everyone here did their best with the information they had. Let's focus
on what we can learn together."

# If needed, take sidebar conversations offline
# Some discussions work better 1-on-1
```

---

### Issue: Too Many Action Items Generated

**Symptoms:**
- Action item list grows to 15+ items
- Items are vague or aspirational
- Team feeling overwhelmed

**Solution:**
```markdown
# Prioritization Exercise

1. Group similar items
2. Identify "must do" vs "nice to have"
3. Apply 80/20 rule - which 20% of actions prevent 80% of similar issues?

# Example Consolidation:
Before:
- Improve monitoring
- Add more alerts
- Better dashboards
- Update runbooks
- Monitoring training

After:
- Add 3 specific alerts for connection pool issues (Owner: Sarah)
- Create connection pool runbook (Owner: Mike)
```

---

### Issue: No Clear Root Cause Found

**Symptoms:**
- Multiple possible causes
- Uncertainty about what actually went wrong
- Hesitation to declare root cause

**Solution:**
```markdown
# Document Uncertainty

"Root Cause: Likely a combination of factors including X, Y, and Z.
We don't have complete certainty, but evidence points to..."

# Focus on Improvements Regardless

"Even without perfect clarity on the root cause, we identified several
improvements that will make us more resilient:
1. [Improvement that helps regardless]
2. [Another defensive improvement]"

# Consider Follow-up Investigation

"Action Item: Conduct deeper technical investigation into X
Owner: Mike, Due: Next week, Time: 4 hours"
```

---

## Related Workflows

**Prerequisites:**
- `devops-xxx_incident_response_workflow.md` - Handling the actual incident
- `devops-xxx_rollback_procedure.md` - How rollbacks work
- `dev-xxx_log_analysis.md` - Gathering diagnostic information

**Next Steps:**
- `dev-xxx_hotfix_procedure.md` - Implementing urgent fixes
- `qa-xxx_production_testing.md` - Testing in production
- `pm-xxx_progress_tracking.md` - Tracking action item completion

**Related:**
- `dev-xxx_technical_debt_mgmt.md` - Managing resulting technical debt
- `qa-xxx_quality_gate_execution.md` - Preventing future issues
- `pm-xxx_knowledge_transfer.md` - Sharing learnings

---

## Tags

`development` `incident-management` `post-mortem` `retrospective` `learning` `continuous-improvement` `blameless` `root-cause-analysis` `process`
