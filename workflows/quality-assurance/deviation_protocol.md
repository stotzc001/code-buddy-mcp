# Deviation Protocol

**ID:** qua-004  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 15-30 minutes (per deviation request)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Formal process for requesting, approving, and tracking deviations from established quality standards when necessary, ensuring deviations are justified, documented, and temporary.

**Why:** Quality standards exist for good reasons, but reality sometimes requires pragmatic exceptions. A deviation protocol balances maintaining standards with business needs. Without a formal process, deviations become technical debt that never gets fixed. With proper protocol, deviations are tracked, time-boxed, and eventually resolved. Teams with deviation protocols have 60% less permanent technical debt than those without.

**When to use:**
- Emergency hotfix needs immediate deployment
- Third-party library incompatibility
- Legacy code maintenance
- Temporary workaround needed
- Standards impossible to meet (rare)
- Deadline pressure (carefully)
- Performance optimization requires trade-offs
- Experimentation or proof-of-concept

---

## Prerequisites

**Required:**
- [ ] Established quality standards
- [ ] Team agreement on deviation process
- [ ] Issue tracking system
- [ ] Tech lead or approval authority

**Check before starting:**
```bash
# Review current quality standards
cat docs/QUALITY_STANDARDS.md

# Check existing deviations
gh issue list --label "deviation"

# Verify approval process documented
cat docs/DEVIATION_PROCESS.md
```

---

## Implementation Steps

### Step 1: Identify Need for Deviation

**What:** Recognize when a deviation from standards is necessary and document the specific standard being violated.

**How:**

**Common deviation scenarios:**

**1. Emergency hotfix:**
```markdown
## Scenario
Production is down. Fix needs immediate deployment.
Standard violated: Code review required before merge.

## Business Impact
- Every minute costs $10,000
- Affects 50,000 users
- Reputation damage

## Justification
Cannot wait 2 hours for code review.
Will get review retroactively.
```

**2. Third-party incompatibility:**
```markdown
## Scenario
New version of critical library has no type stubs.
Standard violated: 100% type coverage required.

## Business Impact
- Security fix in new version is critical
- Current version has vulnerability
- No type stubs available from maintainer

## Justification
Cannot wait for community to create stubs.
Will create stubs ourselves later.
```

**3. Performance optimization:**
```markdown
## Scenario
Optimization requires bypassing ORM.
Standard violated: Must use ORM for database access.

## Business Impact
- Current query takes 30s
- Times out under load
- Raw SQL reduces to 0.5s

## Justification
ORM generates inefficient query.
Performance critical for user experience.
```

**4. Legacy code maintenance:**
```markdown
## Scenario
Fixing bug in legacy module without tests.
Standard violated: 80% test coverage required.

## Business Impact
- Security vulnerability needs fix
- Adding tests would take 2 weeks
- Risk of breaking other functionality

## Justification
Urgent security fix.
Will add tests in dedicated cleanup sprint.
```

**Evaluate if deviation is necessary:**
```markdown
## Questions to Ask:

1. **Is there really no alternative?**
   - Can we meet the standard with more effort?
   - Is there a creative solution?

2. **What's the real cost of compliance?**
   - Time: hours vs days vs weeks
   - Resources: who's available
   - Risk: what could go wrong

3. **What's the cost of non-compliance?**
   - Technical debt
   - Future maintenance
   - Team morale

4. **Is this truly temporary?**
   - Will we fix it later? (honestly)
   - Is there a plan to comply?
```

**Verification:**
- [ ] Specific standard identified
- [ ] Business impact documented
- [ ] Justification clear
- [ ] Alternatives considered

**If This Fails:**
→ If standard is unclear, document it first
→ If justification weak, try to comply with standard
→ If alternatives exist, use them instead

---

### Step 2: Document the Deviation Request

**What:** Create formal documentation of the deviation request with all necessary details.

**How:**

**Deviation request template:**
```markdown
# Deviation Request: [Short Title]

## Metadata
- **Requester:** @username
- **Date:** 2025-10-26
- **Severity:** Critical | High | Medium | Low
- **Type:** Emergency | Technical | Legacy | Performance

## Standard Being Violated
- **Standard:** [Specific quality standard]
- **Normal Requirement:** [What's normally required]
- **Deviation:** [What you're doing instead]

Example:
- **Standard:** All code must have 80% test coverage
- **Normal Requirement:** Add tests before merging
- **Deviation:** Merging with 0% coverage

## Business Justification
[Why this deviation is necessary]

- **Impact if we wait:** [Cost/risk of complying]
- **Impact if we deviate:** [Cost/risk of deviating]
- **Business value:** [What this enables]

## Technical Details
[What's being changed and why]

```python
# Code example
def emergency_fix():
    # This bypasses validation for speed
    pass
```

## Alternatives Considered
1. [Alternative 1] - Rejected because [reason]
2. [Alternative 2] - Rejected because [reason]
3. [Alternative 3] - Rejected because [reason]

## Remediation Plan
[How and when will this be fixed]

- **Target Date:** [When will this be resolved]
- **Steps to Resolve:**
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]

## Risks and Mitigation
- **Risk 1:** [What could go wrong]
  - **Mitigation:** [How we'll handle it]
- **Risk 2:** [What could go wrong]
  - **Mitigation:** [How we'll handle it]

## Approval Checklist
- [ ] Tech lead approval
- [ ] Product owner informed
- [ ] Remediation plan documented
- [ ] Timeline agreed upon
- [ ] Risks acknowledged
```

**Example deviation request:**
```markdown
# Deviation Request: Emergency Hotfix - Skip Code Review

## Metadata
- **Requester:** @alice
- **Date:** 2025-10-26 14:30
- **Severity:** Critical
- **Type:** Emergency

## Standard Being Violated
- **Standard:** All code changes require peer review before merge
- **Normal Requirement:** At least 1 approval from team member
- **Deviation:** Merging immediately without review

## Business Justification
Production database connection pool exhausted. All users unable to access service.

- **Impact if we wait:** $10,000/minute revenue loss, 50,000 affected users
- **Impact if we deviate:** Potential for incomplete fix or regression
- **Business value:** Restore service immediately

## Technical Details
Increase connection pool size from 10 to 50.

```python
# config/database.py
SQLALCHEMY_POOL_SIZE = 50  # Was 10
```

## Alternatives Considered
1. Wait for code review (2 hours) - Rejected: Too costly
2. Restart servers - Rejected: Temporary, doesn't fix root cause
3. Scale horizontally - Rejected: Takes 30 minutes to provision

## Remediation Plan
- **Target Date:** Today, 2025-10-26 18:00
- **Steps to Resolve:**
  1. Deploy fix immediately
  2. Monitor for 1 hour
  3. Get retroactive code review by EOD
  4. Add pool size monitoring
  5. Document in postmortem

## Risks and Mitigation
- **Risk:** Pool size too high, consumes DB resources
  - **Mitigation:** Monitor DB connections, ready to adjust
- **Risk:** Fix doesn't solve issue
  - **Mitigation:** Keep investigating, ready to rollback

## Approval Checklist
- [x] Tech lead approval (@bob)
- [x] Product owner informed
- [x] Remediation plan documented
- [x] Timeline agreed upon
- [x] Risks acknowledged
```

**Verification:**
- [ ] Template completed
- [ ] All fields filled
- [ ] Justification strong
- [ ] Remediation plan clear
- [ ] Risks identified

**If This Fails:**
→ If template incomplete, fill in all sections
→ If justification unclear, work with requester
→ If remediation vague, define specific steps

---

### Step 3: Get Appropriate Approval

**What:** Route deviation request to appropriate authority for approval.

**How:**

**Approval authority by severity:**
```markdown
## Critical (Production down, security breach)
- **Approver:** Any senior engineer on-call
- **Required:** 1 approval
- **Response Time:** < 15 minutes
- **Process:** Slack/phone approval, document after

## High (Blocking release, significant impact)
- **Approver:** Tech lead
- **Required:** 1 approval
- **Response Time:** < 4 hours
- **Process:** GitHub issue with immediate review

## Medium (Technical convenience, minor impact)
- **Approver:** Tech lead + 1 senior engineer
- **Required:** 2 approvals
- **Response Time:** < 1 day
- **Process:** GitHub issue with team discussion

## Low (Nice-to-have, no immediate impact)
- **Approver:** Tech lead + team consensus
- **Required:** 3 approvals
- **Response Time:** < 1 week
- **Process:** Team meeting discussion
```

**Approval workflow:**
```bash
# 1. Create GitHub issue
gh issue create \
  --title "Deviation: Emergency Hotfix - Skip Review" \
  --body-file deviation-request.md \
  --label "deviation,critical" \
  --assignee @tech-lead

# 2. Request approval (for critical)
# Post in Slack: #emergencies channel
"🚨 Deviation request: [link]
Need approval to skip code review for prod hotfix.
@tech-lead please review immediately."

# 3. Document approval
# On GitHub issue:
"✅ Approved by @tech-lead at 14:35
Proceeding with deployment."

# 4. Link to PR/commit
# Add deviation issue link to PR/commit:
git commit -m "fix: Increase DB pool size

Emergency fix for connection exhaustion.
Deviation approved: #123"
```

**Approval decision criteria:**
```markdown
## Tech Lead Should Approve If:
✅ Justification is strong
✅ Business impact is real
✅ Alternatives truly exhausted
✅ Remediation plan is solid
✅ Risks are acceptable
✅ Team will learn from this

## Tech Lead Should Reject If:
❌ Justification is weak ("faster this way")
❌ Standard can be met with effort
❌ Better alternatives exist
❌ No remediation plan
❌ Risks are too high
❌ Pattern of seeking deviations
```

**Fast-track for emergencies:**
```markdown
## Emergency Approval Process

### If production is down:
1. Act first (deploy fix)
2. Document during (in Slack)
3. Get approval after (within 1 hour)
4. Full documentation by EOD

### Template:
"Emergency deviation enacted at 14:30.

What: Deployed without code review
Why: Production down, losing $10k/min
Fix: Increased DB pool size
Approval: Retroactive approval from @tech-lead at 14:45
Ticket: #123"
```

**Verification:**
- [ ] Appropriate approver identified
- [ ] Approval requested
- [ ] Decision documented
- [ ] Timeline met

**If This Fails:**
→ If no approver available, escalate to next level
→ If rejected, comply with standard or improve justification
→ If emergency, get retroactive approval

---

### Step 4: Implement with Documentation

**What:** Execute the deviation with clear documentation in code and commits.

**How:**

**Document in code:**
```python
# DEVIATION: #123 - Emergency fix, no code review
# Approved by: @tech-lead
# Date: 2025-10-26
# TODO: Add proper pool size configuration (#124)

SQLALCHEMY_POOL_SIZE = 50  # Emergency increase from 10
```

```python
# Example: Type checking deviation
from typing import Any

def process_legacy_data(data: Any) -> Any:  # type: ignore[misc]
    """
    Process legacy data from external system.
    
    DEVIATION #125: Using Any type for legacy data.
    - Reason: External system has no type information
    - Approved by: @tech-lead
    - TODO: Create TypedDict for data structure (#126)
    """
    return transform(data)
```

**Document in commit:**
```bash
git commit -m "fix: Emergency DB pool size increase

Increased pool from 10 to 50 to resolve connection exhaustion.

DEVIATION: #123
- Standard: Code review required before merge
- Approved by: @tech-lead
- Reason: Production down, $10k/min revenue loss
- Remediation: Retroactive review by EOD

Related: #124 (proper configuration)
"
```

**Document in PR:**
```markdown
## Pull Request: Emergency Hotfix

### Deviation Notice
⚠️ This PR violates code review standard

**Deviation Issue:** #123
**Approval:** @tech-lead
**Reason:** Critical production outage
**Retroactive Review:** Required by 2025-10-26 18:00

### Changes
- Increased database connection pool size
- Temporary fix until proper configuration implemented

### Remediation
- [ ] Add pool size monitoring (#124)
- [ ] Implement dynamic pool configuration (#125)
- [ ] Document in runbook (#126)
```

**Add monitoring/tracking:**
```python
# Add TODO comments with issue numbers
# TODO(#124): Replace hardcoded pool size with config
# TODO(#125): Add pool size monitoring
# FIXME(#126): Remove deviation once proper fix deployed

# Use linting tools to track
# ruff: noqa: E501 - Deviation #123, long line acceptable here

# Add to tech debt tracking
# docs/tech-debt.md
## Active Deviations
1. #123 - Hardcoded DB pool size (due: 2025-11-01)
```

**Verification:**
- [ ] Deviation documented in code
- [ ] Commit message explains deviation
- [ ] PR links to deviation issue
- [ ] TODOs created for remediation

**If This Fails:**
→ If documentation missing, add before merging
→ If unclear, review with tech lead
→ If too complex, break into smaller changes

---

### Step 5: Track and Remediate

**What:** Ensure deviations are temporary by tracking and resolving them within agreed timeline.

**How:**

**Create remediation issues:**
```bash
# Create follow-up issues immediately

# Issue 1: Retroactive code review
gh issue create \
  --title "Retroactive Review: Emergency DB Hotfix" \
  --body "Review emergency fix from #123" \
  --label "code-review,deviation" \
  --milestone "Sprint 23"

# Issue 2: Proper fix
gh issue create \
  --title "Replace Hardcoded DB Pool Size with Config" \
  --body "Remove deviation from #123. \
Move pool size to configuration file." \
  --label "tech-debt,deviation" \
  --milestone "Sprint 24"

# Issue 3: Monitoring
gh issue create \
  --title "Add DB Connection Pool Monitoring" \
  --body "Add alerts for pool exhaustion. \
Prevents future incidents." \
  --label "monitoring,deviation" \
  --milestone "Sprint 24"
```

**Track deviations in dashboard:**
```python
# scripts/deviation_tracker.py

import json
from datetime import datetime, timedelta

def get_active_deviations():
    """Get all open deviation issues."""
    issues = gh_api.get_issues(label="deviation", state="open")
    return issues

def check_overdue():
    """Check for overdue deviations."""
    issues = get_active_deviations()
    overdue = []
    
    for issue in issues:
        due_date = issue.milestone.due_date
        if due_date and datetime.now() > due_date:
            overdue.append(issue)
    
    return overdue

def generate_report():
    """Generate deviation status report."""
    active = get_active_deviations()
    overdue = check_overdue()
    
    print(f"Active Deviations: {len(active)}")
    print(f"Overdue: {len(overdue)}")
    
    if overdue:
        print("\n⚠️ Overdue Deviations:")
        for issue in overdue:
            print(f"  - #{issue.number}: {issue.title}")
            print(f"    Due: {issue.milestone.due_date}")
```

**Regular deviation reviews:**
```markdown
# Weekly Deviation Review (15 min standup)

## Agenda:
1. New deviations this week
2. Overdue deviations (action items)
3. Recently resolved deviations (celebrate)

## Metrics:
- Total active: 5
- Added this week: 2
- Resolved this week: 1
- Overdue: 1 (escalate)

## Actions:
- #123: Review scheduled for today
- #124: Assigned to @alice
- #125: Blocked on dependency (follow up)
```

**Remediation deadline enforcement:**
```yaml
# .github/workflows/deviation-check.yml

name: Check Overdue Deviations

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday 9am

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check overdue deviations
        run: |
          python scripts/deviation_tracker.py
          
          # Post to Slack if overdue
          if [ $OVERDUE_COUNT -gt 0 ]; then
            curl -X POST $SLACK_WEBHOOK \
              -d "⚠️ $OVERDUE_COUNT overdue deviations!"
          fi
```

**Close deviation when resolved:**
```bash
# When remediation complete
gh issue close 123 --comment "
Deviation resolved ✅

Remediation completed:
- ✅ Retroactive code review (#127)
- ✅ Moved to config file (#128)
- ✅ Added monitoring (#129)

Total time in deviation: 5 days
Standard now met: Code reviewed, properly configured
"
```

**Verification:**
- [ ] Remediation issues created
- [ ] Deadlines set
- [ ] Tracking dashboard updated
- [ ] Regular reviews scheduled
- [ ] Deviation resolved on time

**If This Fails:**
→ If deadline missed, escalate immediately
→ If forgotten, improve tracking system
→ If blocked, unblock or extend deadline with new approval

---

### Step 6: Learn and Improve Standards

**What:** Use deviation patterns to improve standards and processes.

**How:**

**Analyze deviation patterns:**
```python
# scripts/analyze_deviations.py

def analyze_patterns():
    """Analyze closed deviations for patterns."""
    
    deviations = get_closed_deviations()
    
    # Group by reason
    reasons = {}
    for dev in deviations:
        reason = dev.metadata['type']
        reasons[reason] = reasons.get(reason, 0) + 1
    
    # Most common reasons:
    # Emergency: 15 (50%)
    # Legacy: 8 (27%)
    # Performance: 5 (17%)
    # Technical: 2 (7%)
    
    return reasons

# Insights:
# - Too many emergencies (improve monitoring)
# - Legacy code needs cleanup sprint
# - Performance issues need architecture review
```

**Quarterly deviation retrospective:**
```markdown
# Q4 Deviation Retrospective

## Statistics:
- Total deviations: 30
- Average duration: 8 days
- Longest: 45 days (#123)
- Most common: Emergency hotfixes (50%)

## What Went Well:
✅ Fast approval process
✅ Clear documentation
✅ 90% resolved on time

## What Needs Improvement:
❌ Too many emergency hotfixes
❌ Some deviations extended multiple times
❌ Legacy code cleanup delayed

## Actions:
1. Improve monitoring to catch issues earlier
2. Schedule legacy code cleanup sprint
3. Add pre-production environment
4. Update standards for performance cases

## Standard Updates:
- Performance deviations: Add fast-track process
- Legacy code: Temporarily lower coverage req
- Emergency process: Formalize retroactive reviews
```

**Update standards based on learnings:**
```markdown
# Standards Update (2025-10)

## New: Performance Exception Process
If optimization requires deviation from ORM standard:
1. Document performance requirements
2. Show ORM solution attempted
3. Measure before/after
4. Tech lead approval required
5. Add performance tests

## Updated: Emergency Hotfix Process
Formalized retroactive review process:
- Deploy immediately if production down
- Document in emergency-fixes.md
- Retroactive review within 4 hours
- Full postmortem within 24 hours
- Share learnings in team meeting

## Removed: 100% Type Coverage Requirement
Updated to: 90% type coverage required
- Third-party libs without stubs exempt
- Document exemptions in pyproject.toml
- Create stubs as time allows
```

**Share learnings:**
```markdown
# Team Wiki: Deviation Learnings

## Case Study: DB Pool Exhaustion (#123)

### What Happened:
- Production down due to connection pool exhaustion
- Required immediate fix without code review
- Deployed in 15 minutes

### What We Learned:
- Need better connection monitoring
- Pool size should be configurable
- Emergency process worked well

### Process Improvements:
- Added connection pool monitoring
- Created DB configuration guide
- Updated on-call runbook

### Similar Situations:
If you face connection issues:
1. Check connection pool metrics first
2. Review configuration options
3. Consider horizontal scaling
4. Document in runbook
```

**Verification:**
- [ ] Patterns analyzed
- [ ] Retrospective conducted
- [ ] Standards updated
- [ ] Learnings shared
- [ ] Process improved

**If This Fails:**
→ If no patterns found, collect more data
→ If standards not updated, schedule review
→ If learnings not shared, improve communication

---

## Verification Checklist

- [ ] Deviation need identified
- [ ] Request documented thoroughly
- [ ] Approval obtained
- [ ] Implementation documented
- [ ] Remediation tracked
- [ ] Standards improved
- [ ] Team learned from experience

---

## Common Issues & Solutions

### Issue: Too Many Deviation Requests

**Symptoms:**
- Constant deviation requests
- Standards rarely met
- Team sees standards as optional

**Solution:**
```markdown
1. **Review standards**
   - Are they realistic?
   - Too strict for team maturity?
   - Need updating?

2. **Investigate root causes**
   - Why can't we meet standards?
   - Training needed?
   - Process issues?

3. **Strengthen approval**
   - Make approval harder to get
   - Require stronger justification
   - Track patterns

4. **Improve standards**
   - Update unrealistic standards
   - Add exceptions for common cases
   - Make standards achievable
```

---

### Issue: Deviations Never Get Resolved

**Symptoms:**
- Open deviations pile up
- No one fixes them
- Technical debt increases

**Solution:**
```markdown
1. **Strengthen tracking**
   ```yaml
   # Auto-escalate overdue
   - name: Escalate Overdue
     if: days_overdue > 7
     notify: @tech-lead, @product
   ```

2. **Reserve capacity**
   - 10% of sprint for tech debt
   - Mandatory deviation cleanup time
   - No new features until fixed

3. **Make it visible**
   - Dashboard on team screen
   - Daily standup item
   - Sprint retrospective topic

4. **Tie to performance**
   - Track resolution as metric
   - Include in reviews
   - Celebrate quick resolution
```

---

## Examples

### Example 1: Emergency Hotfix

**Context:** Production database connection pool exhausted

**Execution:**
```markdown
1. Act immediately (14:30)
   - Deploy fix
   - Post in Slack

2. Document during (14:35)
   - Create issue #123
   - Document in code
   - Commit with deviation note

3. Get approval (14:45)
   - Tech lead approves retroactively
   - Confirms in issue

4. Remediate (same day)
   - Code review at 16:00
   - Create follow-up issues
   - Schedule proper fix

Result: Service restored in 15 minutes,
deviation resolved in 4 hours ✅
```

---

### Example 2: Legacy Code Maintenance

**Context:** Security fix in untested legacy code

**Execution:**
```markdown
1. Request deviation (Day 1)
   - Document: Adding tests = 2 weeks
   - Justify: Security fix urgent
   - Plan: Add tests in cleanup sprint

2. Get approval (Day 1)
   - Tech lead + senior engineer approve
   - Condition: Add to cleanup backlog

3. Implement (Day 2)
   - Fix vulnerability
   - Document deviation
   - Create cleanup issues

4. Remediate (Week 3)
   - Cleanup sprint scheduled
   - Tests added
   - Deviation closed

Result: Security fixed quickly,
tests added within month ✅
```

---

## Best Practices

### DO:
✅ **Document thoroughly** - Clear justification
✅ **Get proper approval** - Follow the process
✅ **Time-box deviations** - Set deadlines
✅ **Track religiously** - Never forget
✅ **Remediate promptly** - Fix as promised
✅ **Learn from patterns** - Improve standards
✅ **Make exceptions** - When truly needed
✅ **Communicate openly** - Team awareness

### DON'T:
❌ **Abuse the process** - Only when needed
❌ **Skip documentation** - Always document
❌ **Forget remediation** - Always fix
❌ **Hide deviations** - Be transparent
❌ **Extend indefinitely** - Time-box strictly
❌ **Lower standards** - Maintain quality
❌ **Normalize deviations** - Keep them rare
❌ **Blame requesters** - Process is for them

---

## Related Workflows

**Prerequisites:**
- [Quality Gate Execution](./quality_gate_execution.md)
- [Code Review Checklist](./code_review_checklist.md)

**Next Steps:**
- [Technical Debt Management](../development/technical_debt_mgmt.md)
- [Rollback Procedure](../devops/rollback_procedure.md)

**Related:**
- [Emergency Hotfix](../devops/emergency_hotfix.md)

---

## Tags
`quality-assurance` `process` `standards` `deviation` `technical-debt` `governance` `best-practices`
