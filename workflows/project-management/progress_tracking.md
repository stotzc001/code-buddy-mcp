# Progress Tracking

**ID:** pro-002  
**Category:** Project Management  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematically track and communicate project progress to maintain visibility and accountability

**Why:** Without clear progress tracking, projects drift, stakeholders lose confidence, and teams waste time on status meetings. Good tracking enables autonomous work, early risk detection, and data-driven decisions

**When to use:**
- Starting a new project or sprint
- Daily/weekly status updates
- Before stakeholder meetings
- When project feels off track
- During sprint reviews or retrospectives
- When context gets lost between sessions
- For personal accountability and motivation
- When working with distributed teams

---

## Prerequisites

**Required:**
- [ ] Project with defined goals or milestones
- [ ] Understanding of what "done" looks like
- [ ] Method for recording progress (tool or document)
- [ ] Regular cadence for updates

**Check before starting:**
```bash
# Verify project structure exists
ls -la README.md ROADMAP.md
cat PROGRESS.md || echo "Need to create PROGRESS.md"

# Check for project management tool access
# Jira, Linear, GitHub Projects, etc.

# Review current git activity
git log --since="1 week ago" --oneline
git branch --list
```

---

## Implementation Steps

### Step 1: Define Success Metrics

**What:** Establish clear, measurable criteria for tracking progress

**How:**

**SMART Goals Framework:**

| Component | Description | Example |
|-----------|-------------|---------|
| **Specific** | Clear and unambiguous | "Implement user authentication" not "Work on auth" |
| **Measurable** | Quantifiable progress | "Complete 5 API endpoints" |
| **Achievable** | Realistic given resources | Based on team capacity |
| **Relevant** | Aligned with project goals | Supports product roadmap |
| **Time-bound** | Has a deadline | "By end of sprint" |

**Project Success Metrics:**

```markdown
# Project: User Authentication System

## Success Criteria

### Functional Requirements (Must Have)
- [ ] Users can register with email/password
- [ ] Users can login and receive JWT token
- [ ] Users can reset forgotten passwords
- [ ] API endpoints protected by authentication
- [ ] Session management implemented

### Quality Requirements
- [ ] 90%+ test coverage for auth module
- [ ] < 200ms p95 response time for auth endpoints
- [ ] Zero security vulnerabilities (Snyk scan)
- [ ] All code reviewed and approved

### Delivery Requirements
- [ ] Deployed to production
- [ ] Documentation complete
- [ ] Runbook created for operations
- [ ] Stakeholder sign-off received

## Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Endpoints | 6 | 4 | 🟡 66% |
| Test Coverage | 90% | 85% | 🟡 Close |
| Response Time | <200ms | 180ms | 🟢 Good |
| Documentation | 100% | 75% | 🟡 In Progress |
| Sprint Progress | 100% | 60% | 🟡 On Track |

## Definition of Done

**Feature is done when:**
1. Code complete and committed
2. Unit tests passing (>90% coverage)
3. Integration tests passing
4. Code reviewed and approved
5. Documentation updated
6. Deployed to staging
7. QA approved
8. Deployed to production
9. Monitoring configured
10. Stakeholder notified

```

**Breaking Down Large Projects:**

```markdown
# Epic: User Authentication System

## Phase 1: Basic Authentication (Week 1-2)
- [ ] Register endpoint
- [ ] Login endpoint
- [ ] JWT token generation
- [ ] Token validation middleware

## Phase 2: Security Features (Week 3-4)
- [ ] Password reset flow
- [ ] Email verification
- [ ] Rate limiting
- [ ] Security audit

## Phase 3: Polish (Week 5)
- [ ] Error messages and UX
- [ ] Documentation
- [ ] Performance optimization
- [ ] Deployment

## Milestones
- ✅ M1: Basic auth working locally (Week 2)
- ⏸️  M2: Security features complete (Week 4)
- ⬜ M3: Production deployment (Week 5)
```

**Verification:**
- [ ] Goals are SMART (specific, measurable, achievable, relevant, time-bound)
- [ ] Success criteria clearly defined
- [ ] Metrics identified and measurable
- [ ] Large projects broken into phases
- [ ] Definition of "done" established

**If This Fails:**
→ Start with MVP: What's the smallest valuable outcome?
→ Ask: "How will we know we're done?"
→ Break down until tasks are < 2 days each

---

### Step 2: Choose Tracking Method

**What:** Select appropriate tools and formats for tracking progress

**How:**

**Tracking Tool Options:**

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **Markdown File** | Solo dev, simple projects | Version controlled, simple, portable | Manual updates, no automation |
| **GitHub Issues/Projects** | Code-centric teams | Integrated with code, free | Limited PM features |
| **Jira** | Large teams, complex projects | Powerful, reporting, integrations | Complex, expensive |
| **Linear** | Fast-moving tech teams | Beautiful UX, fast, modern | Newer, less integrations |
| **Notion** | Knowledge-heavy projects | Flexible, collaborative | Can get messy |
| **Spreadsheet** | Data-driven tracking | Flexible, formulas, charts | Manual, not collaborative |
| **Trello** | Visual/kanban workflow | Simple, intuitive | Limited for complex projects |
| **Asana** | Task-oriented teams | Great for tasks, timeline view | Can be overwhelming |

**Decision Matrix:**

```
Team Size:
├─ Solo → Markdown file or GitHub Issues
├─ 2-5 people → GitHub Projects or Trello
├─ 5-20 people → Linear or Jira
└─ 20+ people → Jira or Asana

Project Complexity:
├─ Simple → Markdown or Trello
├─ Medium → GitHub Projects or Linear
└─ Complex → Jira

Budget:
├─ Free → Markdown, GitHub, Trello
├─ <$10/user → Linear, Asana
└─ >$10/user → Jira

Integration Needs:
├─ Code-centric → GitHub Projects
├─ Multi-tool → Jira (best integrations)
└─ Minimal → Markdown or Trello
```

**Lightweight PROGRESS.md Template:**

```markdown
# Project Progress - [Project Name]

**Last Updated:** 2025-10-26
**Status:** 🟢 On Track / 🟡 At Risk / 🔴 Blocked
**Overall Progress:** 60% complete

---

## Current Sprint (Week of Oct 21-25)

### Completed ✅
- [x] Implemented user registration endpoint
- [x] Added password validation
- [x] Created user model and migration
- [x] Unit tests for registration (95% coverage)

### In Progress 🔄
- [ ] Login endpoint (80% complete)
  - ✅ JWT token generation working
  - ✅ Token validation middleware
  - ⏸️  Refresh token logic (in progress)
- [ ] Password reset flow (40% complete)
  - ✅ Reset request endpoint
  - ⏸️  Email template (waiting on design)
  - ⬜ Reset confirmation endpoint

### Planned Next ⏭️
- [ ] Email verification
- [ ] Rate limiting
- [ ] Security audit

### Blockers 🚧
- **Blocker 1:** Waiting for email template from design team
  - Impact: Can't complete password reset
  - Workaround: Using temporary template for testing
  - ETA: Monday Oct 28

---

## Metrics

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Features Complete | 6 | 4 | ↗️ |
| Test Coverage | 90% | 87% | ↗️ |
| API Response Time | <200ms | 175ms | → |
| Open Bugs | 0 | 2 | ↘️ |

---

## Milestones

- ✅ **M1:** Basic auth (Oct 15) - COMPLETE
- 🔄 **M2:** Security features (Oct 29) - IN PROGRESS (70%)
- ⬜ **M3:** Production launch (Nov 5) - PLANNED

---

## Risks & Issues

### 🔴 High Priority
- Performance concerns with bcrypt (may need to optimize)
  - Mitigation: Testing with production-like data

### 🟡 Medium Priority  
- Email service integration unclear
  - Mitigation: Researching SendGrid vs AWS SES

### 🟢 Low Priority
- Documentation needs polish
  - Mitigation: Will do in polish phase

---

## Team Velocity

**This Week:**
- Completed: 8 story points
- Committed: 10 story points
- Velocity: 80%

**Sprint Burndown:**
```
10 │     
 8 │  ╲  
 6 │   ╲___
 4 │       ╲___
 2 │           ╲___
 0 │_______________╲
   Mon Tue Wed Thu Fri
```

---

## Notes

- Team was blocked on email templates Mon-Tue
- Added extra time for security review
- May need to push M3 by 2 days (waiting confirmation)

---

## Next Update: Friday, Nov 1
```

**Jira/Linear Workflow:**

```markdown
# Issue Tracking Best Practices

## Issue States:
- **Backlog:** Idea, not yet prioritized
- **Ready:** Prioritized, ready to start
- **In Progress:** Actively working
- **In Review:** PR open, awaiting approval
- **Testing:** In QA or staging
- **Done:** Deployed and verified

## Issue Structure:
**Title:** [Component] Short description
Example: "[API] Add user login endpoint"

**Description:**
- **Goal:** What we're trying to achieve
- **Acceptance Criteria:** How we know it's done
- **Technical Notes:** Implementation details
- **Dependencies:** What needs to happen first
- **Estimate:** Story points or hours

**Labels:**
- Type: feature, bug, tech-debt, docs
- Priority: p0, p1, p2, p3
- Component: api, frontend, database, infra
- Sprint: sprint-24, sprint-25

**Example Issue:**
```
Title: [API] Implement password reset endpoint

Description:
Goal: Allow users to reset forgotten passwords

Acceptance Criteria:
- [ ] POST /api/auth/reset-request accepts email
- [ ] Sends email with reset token
- [ ] POST /api/auth/reset-confirm validates token and updates password
- [ ] Rate limited to prevent abuse
- [ ] Integration tests cover happy path and errors

Technical Notes:
- Use same token generation as email verification
- Tokens expire after 1 hour
- Store in Redis with TTL

Dependencies:
- Blocked by: Email service integration (#123)

Estimate: 5 story points (1-2 days)

Labels: feature, p1, api, sprint-25
```
```

**Verification:**
- [ ] Tracking tool selected and configured
- [ ] Team has access and understands tool
- [ ] Template or structure defined
- [ ] Initial items/tasks created
- [ ] Tool fits team's workflow

**If This Fails:**
→ Start simple: Markdown file in repo
→ Can always migrate to more sophisticated tool later
→ Tool should serve the team, not vice versa

---

### Step 3: Establish Update Cadence

**What:** Create a regular rhythm for updating and reviewing progress

**How:**

**Update Frequency Guide:**

```markdown
## Daily Updates (Solo or Small Team)

**When:** End of day (5-10 min)
**Format:** Quick status in PROGRESS.md or team chat

**Template:**
```
📅 Daily Update - Oct 26

✅ Today:
- Completed login endpoint
- Added tests for authentication

🔄 Tomorrow:
- Start password reset flow
- Review Alice's PR

🚧 Blockers:
- None
```

**Where:** Slack, Discord, or commit message

---

## Weekly Updates (Team or Stakeholders)

**When:** Friday afternoon or Monday morning
**Format:** Structured report

**Template:**
```
# Weekly Progress Report - Week of Oct 21

## Highlights 🌟
- Completed user registration (M1 achieved!)
- Security audit passed with no critical issues
- Performance improvements: 250ms → 175ms

## This Week's Completed Work
- [x] User registration endpoint (#101)
- [x] Password validation (#102)
- [x] JWT token generation (#103)
- [x] Unit test suite (#104)

## Next Week's Plan
- [ ] Password reset flow (#105)
- [ ] Email verification (#106)
- [ ] Rate limiting (#107)

## Metrics
- Progress: 60% → 75% (+15%)
- Velocity: 8 / 10 story points (80%)
- Test coverage: 85% → 87% (+2%)

## Blockers & Risks
- 🟡 Email templates delayed (low impact)
- 🟢 All other work on track

## Budget & Timeline
- On schedule for Nov 5 launch
- 15 dev days consumed of 25 budgeted
```

**Where:** Email, Slack, project management tool

---

## Sprint Reviews (2-4 weeks)

**When:** End of sprint
**Format:** Demo + retrospective

**Agenda:**
1. Demo completed work (15 min)
2. Review metrics and velocity (10 min)
3. Discuss what went well (10 min)
4. Discuss what could improve (10 min)
5. Action items for next sprint (5 min)

**Documentation:**
```markdown
# Sprint 24 Review - Oct 25

## What We Built
- User authentication system (demo: [video link])
- 6/6 features completed
- 0 bugs in production

## Metrics
- Velocity: 8 points (target: 10)
- Quality: 0 bugs, 90% test coverage
- Performance: All endpoints < 200ms

## Retrospective

### 👍 What Went Well
- Great collaboration on security review
- Caught performance issue early
- Test coverage automation saved time

### 👎 What Could Improve
- Email template dependency blocked us
- Need better estimation (underestimated by 20%)
- Should have automated deployment earlier

### 🎯 Actions for Next Sprint
- [ ] Add dependency tracking to planning
- [ ] Use planning poker for estimation
- [ ] Set up CD pipeline (priority)

## Next Sprint Goals
- Password reset and email verification
- Deploy to production
- Complete documentation
```

**Where:** Confluence, Notion, team wiki
```

**Automation Tips:**

```bash
# Automate metrics collection

# Git activity
git log --since="1 week ago" --oneline --author="$(git config user.name)" | wc -l
# Commits this week

# Test coverage (Python)
pytest --cov=src --cov-report=term-missing | grep TOTAL
# Coverage percentage

# Pull requests
gh pr list --author "@me" --state merged --search "merged:>2025-10-20"
# PRs merged this week

# Script to generate weekly report
#!/bin/bash
# weekly-report.sh

echo "# Weekly Report - $(date +%Y-%m-%d)"
echo
echo "## Git Activity"
echo "Commits: $(git log --since='1 week ago' --oneline | wc -l)"
echo
echo "## PRs"
gh pr list --author "@me" --state merged --search "merged:>$(date -d '1 week ago' +%Y-%m-%d)"
echo
echo "## Test Coverage"
pytest --cov=src --cov-report=term-missing | grep TOTAL
```

**Verification:**
- [ ] Update frequency established
- [ ] Templates created
- [ ] Team knows when to update
- [ ] Automation in place (optional)
- [ ] Updates actually happening

**If This Fails:**
→ Start with weekly, add daily if needed
→ Make updates part of routine (end of day, start of standup)
→ Use reminders/calendar invites

---

### Step 4: Track Blockers and Risks

**What:** Proactively identify and manage issues that could impact progress

**How:**

**Blocker vs Risk vs Issue:**

| Type | Definition | Example | When to Track |
|------|------------|---------|---------------|
| **Blocker** | Prevents work right now | Waiting for API key | Immediately |
| **Risk** | Might cause problems | Library might be deprecated | When identified |
| **Issue** | Problem to solve | Bug in production | When discovered |

**Blocker Tracking Template:**

```markdown
## Blockers 🚧

### Active Blockers

**Blocker #1: Email Service Integration**
- **Impact:** Can't test password reset flow
- **Owner:** @alice (waiting on DevOps)
- **Workaround:** Using console logging for testing
- **ETA:** Oct 28 (2 days)
- **Risk Level:** 🟡 Medium (will delay M2 by 2 days)
- **Status:** Escalated to tech lead

**Blocker #2: Performance Issue in Production**
- **Impact:** API response time 2x slower
- **Owner:** @bob (investigating)
- **Workaround:** None
- **ETA:** Unknown
- **Risk Level:** 🔴 High (affects users now)
- **Status:** P0 incident, all hands on deck

### Resolved Blockers
- ✅ Database migration issue (Oct 24) - Fixed by DevOps team
- ✅ Missing test data (Oct 23) - Created seed script

---

## Risks 🎲

### High Priority (Could Seriously Impact Delivery)

**Risk #1: Third-Party Library Stability**
- **Description:** Using beta version of auth library
- **Probability:** 30% (some reported bugs)
- **Impact:** Could require rewrite (2 week delay)
- **Mitigation:** 
  - Monitor issue tracker daily
  - Have fallback plan to use stable version
  - Tested critical flows in isolation
- **Owner:** @charlie
- **Status:** Monitoring

### Medium Priority (Could Cause Minor Delays)

**Risk #2: Email Deliverability**
- **Description:** Password reset emails might go to spam
- **Probability:** 50% (common issue)
- **Impact:** Poor user experience, support load
- **Mitigation:**
  - Using reputable email service (SendGrid)
  - Implementing SPF/DKIM/DMARC
  - Testing with multiple email providers
- **Owner:** @alice
- **Status:** Testing in progress

### Low Priority (Minor Impact if Happens)

**Risk #3: Documentation Delay**
- **Description:** Might not finish docs by launch
- **Probability:** 20%
- **Impact:** Internal only, not user-facing
- **Mitigation:**
  - Can deploy without complete docs
  - Will finish docs post-launch
- **Owner:** @bob
- **Status:** Scheduled for polish phase

---

## Issue Log

| ID | Title | Severity | Status | Owner | ETA |
|----|-------|----------|--------|-------|-----|
| #1 | Login returns 500 on invalid token | 🔴 P0 | Fixed | @bob | ✅ Oct 24 |
| #2 | Password reset email template broken | 🟡 P1 | In Progress | @alice | Oct 28 |
| #3 | Documentation typos | 🟢 P3 | Backlog | @charlie | Nov 5 |
```

**Escalation Criteria:**

```markdown
# When to Escalate

## Escalate Immediately (P0):
- System is down or broken
- Security vulnerability discovered
- Data loss or corruption
- Blocking multiple people for >4 hours

## Escalate Same Day (P1):
- Blocker will cause sprint goal miss
- Risk probability increased significantly
- Critical bug affecting users
- Blocking team for >1 day

## Escalate This Week (P2):
- Blocker will cause minor delay
- Risk needs stakeholder decision
- Bug affects small user segment
- Blocking work for >3 days

## Track But Don't Escalate (P3):
- Minor issues with workarounds
- Low-impact risks
- Nice-to-have features blocked
```

**Risk Assessment Matrix:**

```
         Low Impact    Medium Impact   High Impact
High     🟡 Monitor    🟠 Mitigate    🔴 Escalate
Prob     
Medium   🟢 Track      🟡 Monitor     🟠 Mitigate
Prob     
Low      ⬜ Ignore     🟢 Track       🟡 Monitor
Prob
```

**Verification:**
- [ ] Blockers tracked and visible
- [ ] Risks identified and assessed
- [ ] Owners assigned
- [ ] Escalation criteria clear
- [ ] Mitigation plans documented

**If This Fails:**
→ At minimum: Track active blockers only
→ Add risk tracking as project matures
→ Escalate when in doubt

---

### Step 5: Measure and Visualize Progress

**What:** Use data and visuals to understand trends and communicate status

**How:**

**Key Metrics to Track:**

**1. Completion Metrics:**
```markdown
## Feature Completion
- Features Planned: 10
- Features Complete: 7
- Features In Progress: 2
- Features Remaining: 1
- **Completion Rate:** 70%

## Task Completion (Sprint)
- Tasks Planned: 25
- Tasks Complete: 20
- Tasks In Progress: 3
- Tasks Remaining: 2
- **Sprint Velocity:** 80% (20/25)

## Story Points (if using)
- Points Committed: 20
- Points Completed: 16
- Points In Progress: 3
- Points Remaining: 1
- **Velocity:** 16 points (last sprint: 14)
```

**2. Quality Metrics:**
```markdown
## Code Quality
- Test Coverage: 87% (target: 90%)
- Linting Violations: 3 (down from 12)
- Security Vulnerabilities: 0 (target: 0)
- Code Review Approval: 100%

## Bug Metrics
- Open Bugs: 2
- Bugs Fixed This Week: 5
- New Bugs This Week: 1
- Bug Fix Rate: +4 net

## Technical Debt
- TODO/FIXME Comments: 8 (down from 15)
- Deprecated API Usage: 0
- Outdated Dependencies: 2 (non-critical)
```

**3. Performance Metrics:**
```markdown
## System Performance
- API Response Time (p95): 175ms (target: <200ms)
- Database Query Time: 25ms avg
- Error Rate: 0.05% (target: <0.1%)
- Uptime: 99.95% (target: 99.9%)

## Team Performance
- Deployment Frequency: 5/week (target: daily)
- Lead Time: 2 days (commit to deploy)
- MTTR: 15 minutes (mean time to recovery)
- Change Failure Rate: 5% (target: <10%)
```

**Progress Visualization:**

**1. Burn Down Chart:**
```markdown
# Sprint Burn Down (Story Points)

20 │╲                          
18 │ ╲                         
16 │  ╲___                     
14 │      ╲___                 
12 │          ╲___             
10 │              ╲___         
 8 │                  ╲___     
 6 │                      ╲___ 
 4 │                          ╲
 2 │                           ╲
 0 │────────────────────────────╲
   M  T  W  T  F  M  T  W  T  F
```

**2. Velocity Chart:**
```markdown
# Sprint Velocity (Story Points Completed)

  20│        ███
  18│        ███
  16│  ███   ███
  14│  ███   ███   ███
  12│  ███   ███   ███
  10│  ███   ███   ███
   8│  ███   ███   ███   ███
   6│  ███   ███   ███   ███
   4│  ███   ███   ███   ███
   2│  ███   ███   ███   ███
   0└──────────────────────────
      S22  S23  S24  S25

Average Velocity: 15.5 points
Trend: ↗️ Improving
```

**3. Cumulative Flow Diagram:**
```markdown
# Work Item States Over Time

  50│                    ▓▓▓▓▓ Done
  45│              ▓▓▓▓▓▓░░░░░ In Review
  40│        ▓▓▓▓▓▓░░░░░▒▒▒▒▒ In Progress
  35│  ▓▓▓▓▓▓░░░░░▒▒▒▒▒▓▓▓▓▓ To Do
  30└─────────────────────────
     W1   W2   W3   W4   W5

Legend:
▓ = Done
░ = In Review
▒ = In Progress
▒ = To Do
```

**4. Health Dashboard:**
```markdown
# Project Health Dashboard

┌─────────────────────────────────┐
│ Overall Status: 🟢 ON TRACK     │
├─────────────────────────────────┤
│ Progress:    75% ████████████▌  │
│ Quality:     90% █████████████▎ │
│ Schedule:    On Time ✓          │
│ Budget:      85% used ▼         │
├─────────────────────────────────┤
│ Active Risks:        2 🟡       │
│ Open Blockers:       0 🟢       │
│ Critical Bugs:       0 🟢       │
│ Team Velocity:      ↗️ +12%     │
└─────────────────────────────────┘
```

**Simple Markdown Progress Bars:**

```markdown
## Feature Progress

**User Authentication:** [████████░░] 80%
**Password Reset:**     [██████░░░░] 60%
**Email Verification:** [████░░░░░░] 40%
**Rate Limiting:**      [░░░░░░░░░░]  0%

## Sprint Progress

Day 1: [██░░░░░░░░] 20%
Day 2: [████░░░░░░] 40%
Day 3: [██████░░░░] 60%
Day 4: [████████░░] 80%
Day 5: [██████████] 100% ✓
```

**Generating Charts:**

```python
# generate_burndown.py
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Sprint data
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
planned = [20, 16, 12, 8, 4, 0]
actual = [20, 17, 12, 10, 5, 2]

plt.figure(figsize=(10, 6))
plt.plot(planned, 'b--', label='Planned', linewidth=2)
plt.plot(actual, 'r-', label='Actual', linewidth=2)
plt.xlabel('Day')
plt.ylabel('Story Points Remaining')
plt.title('Sprint Burn Down Chart')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('burndown.png')
```

```bash
# Generate chart and add to report
python generate_burndown.py
cp burndown.png docs/sprint-24-burndown.png
git add docs/sprint-24-burndown.png
git commit -m "Add sprint 24 burndown chart"
```

**Verification:**
- [ ] Key metrics identified and tracked
- [ ] Progress visualized clearly
- [ ] Trends visible (improving/degrading)
- [ ] Stakeholders can understand charts
- [ ] Data is up-to-date

**If This Fails:**
→ Start with simple percentages
→ Use text-based progress bars
→ Add visualizations as needed
→ Tools like Jira/Linear have built-in charts

---

### Step 6: Communicate Progress Effectively

**What:** Share progress with stakeholders in appropriate format and frequency

**How:**

**Stakeholder Matrix:**

| Stakeholder | Interest | Detail Level | Frequency | Format |
|-------------|----------|--------------|-----------|--------|
| **Product Manager** | Features, timeline | High | Daily | Slack update |
| **Engineering Team** | Technical details | Very High | Daily | Standup |
| **Tech Lead** | Architecture, risks | High | Weekly | 1:1 meeting |
| **Executive/CEO** | Business impact | Low | Monthly | Executive summary |
| **Customer Support** | User-facing changes | Medium | Per release | Release notes |
| **Marketing** | Launch readiness | Low | Bi-weekly | Email update |

**Communication Templates:**

**1. Daily Standup Update:**
```markdown
**Yesterday:**
- Completed login endpoint with JWT tokens
- Fixed bug in password validation
- Reviewed Alice's PR for user model

**Today:**
- Start password reset flow
- Add integration tests
- Pair with Bob on email service

**Blockers:**
- None

**Help Needed:**
- Need design feedback on error messages
```

**2. Weekly Stakeholder Update:**
```markdown
Subject: Weekly Update - User Auth Project

Hi [Product Manager],

Quick update on the authentication project:

✅ **What's Done:**
- User registration and login complete
- JWT token system working
- Security audit passed

🔄 **In Progress:**
- Password reset flow (60% complete)
- Email verification (starting next week)

📅 **Timeline:**
- On track for Nov 5 launch
- 75% complete overall

🚧 **Blockers:**
- Email template from design (minor delay, workaround in place)

📊 **Metrics:**
- Test coverage: 87% (target: 90%)
- Performance: 175ms p95 (target: <200ms)
- 0 critical bugs

**Next Week:**
- Complete password reset
- Start email verification
- Begin documentation

Let me know if you have questions!

[Your Name]
```

**3. Monthly Executive Summary:**
```markdown
# Executive Summary - User Authentication Project
**Date:** October 2025

## Status: 🟢 ON TRACK

**Progress:** 75% complete
**Launch Date:** November 5, 2025 (on schedule)
**Budget:** 85% utilized

## Key Accomplishments
- Core authentication system complete and tested
- Security audit passed with no critical findings
- Performance exceeds requirements (175ms vs 200ms target)

## What's Next
- Password reset and email verification (2 weeks)
- Production deployment and monitoring setup (1 week)

## Risks
- 🟡 Minor: Email service integration delayed 2 days (low impact)
- 🟢 All other work on track

## Business Impact
- Will enable 100% of new users to self-serve account creation
- Reduces support tickets by estimated 40% (based on competitor data)
- Unblocks enterprise SSO integration (Q1 2026 roadmap)

## Ask
- None at this time. Will notify if timeline changes.

---
Questions? Reach out to [Your Name] ([email])
```

**4. Sprint Review Summary:**
```markdown
# Sprint 24 Review - User Authentication

**Demo:** [Link to video or slides]

## What We Built
- User registration with validation ✅
- Login with JWT tokens ✅
- Session management ✅
- Security audit complete ✅

## Metrics
- Features: 4/4 complete (100%)
- Tests: 87% coverage (target: 90%, close)
- Performance: 175ms p95 (target: <200ms, ✓)
- Bugs: 0 critical, 2 minor

## Retrospective Highlights

**What Went Well:**
- Great cross-team collaboration on security
- Caught performance issue early in staging
- Test automation saved 4 hours/week

**What to Improve:**
- Better estimation (off by 20%)
- Dependency tracking (blocked for 2 days)
- Earlier deployment setup

**Actions:**
- Add dependency tracking to planning ✓
- Use planning poker for estimation ✓
- Automate deployment pipeline (priority next sprint)

## Next Sprint Goals
- Password reset and email verification
- Documentation and runbooks
- Production deployment

**Questions?** [Your Name] ([email])
```

**Communication Best Practices:**

```markdown
## DO:
✅ Tailor format to audience (exec vs engineer)
✅ Lead with status (green/yellow/red)
✅ Be honest about problems
✅ Provide context for decisions
✅ Include next steps
✅ Use data to support claims
✅ Make it scannable (bullets, bold, emojis)
✅ Include a "so what?" (business impact)

## DON'T:
❌ Over-communicate (respect people's time)
❌ Hide problems (surface issues early)
❌ Use jargon with non-technical stakeholders
❌ Send update without reading it first
❌ Forget to include timeline
❌ Make it too long (respect 2-minute rule)
❌ Be vague ("making progress")
❌ Send only when things go wrong
```

**Automation:**

```bash
# Auto-generate weekly report
#!/bin/bash
# weekly-report.sh

cat << EOF
# Weekly Update - $(date +%Y-%m-%d)

## Git Activity
Commits: $(git log --since='1 week ago' --oneline | wc -l)

## Pull Requests
$(gh pr list --author "@me" --state merged --search "merged:>$(date -d '1 week ago' +%Y-%m-%d)" --json title --jq '.[] | "- " + .title')

## Test Coverage
$(pytest --cov=src --cov-report=term-missing | grep TOTAL)

## Active Branches
$(git branch | grep -v "main\|master" | wc -l) feature branches

---
Generated automatically. For details, see PROGRESS.md
EOF
```

**Verification:**
- [ ] Stakeholders know project status
- [ ] Communication appropriate for audience
- [ ] Updates sent on schedule
- [ ] Feedback received and acted on
- [ ] No surprises at milestones

**If This Fails:**
→ Over-communicate rather than under-communicate
→ Ask stakeholders: "What do you need to know?"
→ Use templates to make it easier

---

## Verification Checklist

After completing this workflow:

- [ ] Success metrics defined (SMART goals)
- [ ] Tracking method chosen and working
- [ ] Update cadence established
- [ ] Blockers and risks tracked
- [ ] Progress measured and visualized
- [ ] Stakeholders informed regularly
- [ ] Team has visibility into status
- [ ] Can answer "How's it going?" with data

---

## Common Issues & Solutions

### Issue: Progress tracking feels like busywork

**Symptoms:**
- Team resents status updates
- Tracking takes more time than work
- Data never gets used
- Updates feel pointless

**Solution:**
```markdown
# Make Tracking Valuable

## 1. Minimize Overhead
- Update as you work, not separate task
- Use commit messages as updates
- Automate metric collection
- Keep updates < 5 minutes

## 2. Show the Value
- Use data to make decisions
- Reference metrics in retrospectives
- Show how tracking prevented issues
- Demonstrate trend improvements

## 3. Right-Size It
# Too much tracking:
- Every task in 15-minute increments
- Daily reports to everyone
- Complex spreadsheets

# Just enough:
- Weekly progress summary
- Clear blocker visibility
- Simple metrics
- Milestone tracking

## 4. Make It Actionable
# Bad metric (not actionable):
"We completed 16 story points"

# Good metric (actionable):
"Velocity dropped 20%. Root cause: underestimated API integration. 
 Action: Add buffer for external dependencies."
```

**Prevention:**
- Start minimal, add as needed
- Make updates part of natural workflow
- Use data for decisions, not just reporting
- Get team input on what to track

---

### Issue: Can't estimate progress accurately

**Symptoms:**
- "90% done" for weeks
- Constantly behind schedule
- Surprises at deadline
- Poor velocity predictions

**Solution:**
```markdown
# Improve Estimation

## 1. Break Down Work
# Instead of:
"Build authentication system" (3 weeks?)

# Do this:
- Set up JWT library (2 hours)
- Create user model (3 hours)
- Implement registration endpoint (4 hours)
- Add password validation (2 hours)
- Write unit tests (6 hours)
- Integration tests (4 hours)
- Documentation (3 hours)
---
Total: 24 hours = 3 days

## 2. Use Historical Data
# Track actual vs estimated time:
- Estimated: 3 days
- Actual: 4 days
- Factor: 1.33x

# Apply factor to future estimates:
- New estimate: 5 days
- Adjusted: 5 × 1.33 = 6.65 days
- Buffer: 7 days

## 3. Plan for Unknowns
# Add buffer based on confidence:
- 90% confident: +10% buffer
- 70% confident: +25% buffer
- 50% confident: +50% buffer
- Unknown: +100% buffer

# Example:
- Core work: 5 days (90% confident)
- External dependency: 2 days (50% confident)
- Estimate: 5×1.1 + 2×1.5 = 8.5 days
- Round up: 9 days

## 4. Track Unknowns Explicitly
- Known knowns: What we know we know
- Known unknowns: What we know we don't know ← TRACK THESE
- Unknown unknowns: What we don't know we don't know

# Example tracker:
## Known Unknowns:
- [ ] How to integrate with email service?
  - Research needed: 4 hours
  - Decision needed: Which provider?
- [ ] Database migration strategy?
  - Spike needed: 2 hours
  - May need DBA consultation
```

**Prevention:**
- Break tasks into < 2 day chunks
- Track actual vs estimated time
- Review estimates in retrospectives
- Build in buffer for unknowns

---

### Issue: Too many metrics, information overload

**Symptoms:**
- Tracking 20+ metrics
- Nobody looks at dashboards
- Don't know which metrics matter
- Analysis paralysis

**Solution:**
```markdown
# Focus on Critical Few

## The One Metric That Matters (OMTM)
For each phase, pick ONE key metric:

**Phase 1: Build MVP**
→ OMTM: Features complete / Features planned

**Phase 2: Launch**
→ OMTM: Production errors per day

**Phase 3: Grow**
→ OMTM: User adoption rate

## The "Must Track" Metrics (3-5 max)
- **Progress:** % complete or velocity
- **Quality:** Test coverage or bug count
- **Performance:** Response time or uptime
- **Team:** Blockers or happiness score

## Track More, Report Less
- Collect many metrics
- Automate the collection
- Only report the critical few
- Others available on request

## Good Dashboard:
┌─────────────────────────────┐
│ Status: 🟢 ON TRACK         │
│ Progress: 75%               │
│ Velocity: ↗️ +12%           │
│ Blockers: 0                 │
└─────────────────────────────┘

## Bad Dashboard:
┌─────────────────────────────┐
│ Features: 7/10              │
│ Tasks: 20/25                │
│ Points: 16/20               │
│ Coverage: 87%               │
│ Response: 175ms             │
│ Errors: 0.05%               │
│ LOC: 3,427                  │
│ Commits: 42                 │
│ PRs: 8                      │
│ ... (15 more metrics)       │
└─────────────────────────────┘
← Too much!
```

**Prevention:**
- Start with 3-5 key metrics
- Add metrics only when needed for decisions
- Remove metrics nobody uses
- Simple dashboards > complex ones

---

## Examples

### Example 1: Solo Developer Project

**Context:** Building a side project alone, want to track progress

**Execution:**
```markdown
# PROGRESS.md

# My SaaS Project - Progress Tracker

**Goal:** Launch MVP by December 1
**Current Status:** 🟡 Slightly Behind (2 days)
**Last Updated:** October 26

---

## This Week (Oct 21-25)

### Completed ✅
- [x] User authentication (4 hrs)
- [x] Basic dashboard UI (6 hrs)
- [x] Database schema (2 hrs)

### In Progress 🔄
- [ ] Stripe integration (60% done, 4 hrs left)
- [ ] Email notifications (not started, 3 hrs)

### Next Week ⏭️
- [ ] User onboarding flow
- [ ] Settings page
- [ ] Deploy to staging

### Blockers 🚧
- Stripe test mode not working (workaround: using Stripe CLI)

---

## Metrics

**Weekly Velocity:**
- Week 1: 12 hours productive
- Week 2: 15 hours productive
- Week 3: 16 hours productive ← Improving!
- Week 4: 18 hours productive (goal)

**Launch Readiness:**
- Core features: 70% [███████░░░]
- Nice-to-haves: 30% [███░░░░░░░]
- Overall: 60% [██████░░░░]

**Timeline:**
- Days until launch: 36
- Days remaining: 34
- Status: 2 days behind (not critical)

---

## Weekly Reflection

**What went well:**
- Finished auth faster than expected
- Found good UI library (saves time)

**What slowed me down:**
- Stripe integration trickier than expected
- Spent 2 hrs debugging CORS issue

**Learnings:**
- Start integration testing earlier
- Stripe has better Node SDK than Python

**Next week focus:**
- Complete Stripe integration
- Don't start new features until current ones done
```

**Result:** Clear progress visibility, stay motivated, hit deadlines

---

### Example 2: Team Sprint Tracking

**Context:** 5-person team, 2-week sprint, using Jira

**Execution:**

**Sprint Planning (Day 1):**
```markdown
# Sprint 25 - Oct 21 - Nov 1

## Sprint Goal
Complete password reset and email verification features

## Committed Work (25 story points)
- Password reset flow (8 points) - @alice
- Email verification (8 points) - @bob
- Rate limiting (5 points) - @charlie
- Documentation (4 points) - @david

## Stretch Goals (if time permits)
- Security audit (5 points)
- Performance optimization (3 points)

## Sprint Risks
- 🟡 Email service integration might be tricky
- 🟡 Alice unavailable Thu-Fri (PTO)

## Daily Standup Time: 9:30 AM
```

**Daily Standup (Day 5):**
```markdown
**Alice:**
- Yesterday: Completed reset request endpoint
- Today: Working on reset confirmation
- Blockers: None

**Bob:**
- Yesterday: Email template integration
- Today: Finish email verification logic
- Blockers: Waiting on design review for email template

**Charlie:**
- Yesterday: Research rate limiting strategies
- Today: Implement rate limiting middleware
- Blockers: None

**David:**
- Yesterday: Started API documentation
- Today: Continue documentation
- Blockers: Need code freeze to finalize docs
```

**Mid-Sprint Check (Day 7):**
```markdown
# Sprint 25 - Mid-Sprint Review

**Burn Down:**
```
25 │╲              ← Ideal
20 │ ╲___          
15 │     ╲___      
10 │         ╲___  ← Actual (slightly behind)
 5 │             ╲
 0 └──────────────
   1 2 3 4 5 6 7 8 9 10
```

**Status:**
- Completed: 12 points (48%)
- In Progress: 8 points (32%)
- Not Started: 5 points (20%)

**Concern:** Slightly behind due to email template delay
**Action:** Bob switching to other tasks while waiting on design

**Forecast:** Will complete committed work, unlikely to hit stretch goals
```

**Sprint Review (Day 10):**
```markdown
# Sprint 25 - Review

## Completed (23/25 points = 92%)
✅ Password reset flow (8 points)
✅ Email verification (8 points)
✅ Rate limiting (5 points)
✅ Documentation (2/4 points - in progress)

## Not Completed
❌ Complete documentation (2 points - 50% done)

## Stretch Goals: Not attempted (as expected)

## Metrics
- Velocity: 23 points (vs 25 committed = 92%)
- Quality: 0 bugs, 90% test coverage ✓
- Team happiness: 4/5 (good)

## Retrospective

**👍 What Went Well:**
- Team collaboration excellent
- Early risk identification (email delay)
- Pivoting around blocker worked well

**👎 What Could Improve:**
- Documentation should start earlier
- Need better estimation for external dependencies
- Alice's PTO should have been accounted for

**🎯 Actions:**
- Start docs on day 1, not day 7
- Add 20% buffer for external dependencies
- Check PTO calendar during planning

## Next Sprint: Sprint 26
- Complete remaining docs (2 points carried over)
- Security audit (5 points)
- Begin production deployment prep (8 points)
```

**Result:** Team stayed on track, learned and improved, transparent to stakeholders

---

## Best Practices

### DO:
✅ Define success criteria upfront (what is "done"?)
✅ Track what matters, not everything
✅ Update regularly (daily or weekly)
✅ Visualize progress (charts, bars, emojis)
✅ Surface blockers immediately
✅ Communicate proactively
✅ Use data to make decisions
✅ Keep it simple and sustainable
✅ Celebrate milestones
✅ Learn from retrospectives

### DON'T:
❌ Track metrics nobody uses
❌ Make tracking feel like busywork
❌ Hide problems or risks
❌ Ignore warning signs (trends)
❌ Over-complicate the system
❌ Forget to update stakeholders
❌ Measure without acting
❌ Compare velocity across teams
❌ Punish honest estimates
❌ Track time in 15-min increments (overkill)

---

## Related Workflows

**Prerequisites:**
- `pro-003`: Startup Resume - For maintaining progress across sessions
- `pro-004`: Token Management Handoff - For preserving context
- `pro-001`: Knowledge Transfer - For documenting decisions

**Next Steps:**
- `qa-001`: PR Creation and Review - Marking work as complete
- `devops-013`: Release Management - Coordinating releases
- `qa-010`: Sprint Planning - Planning next iteration

**Alternatives:**
- Agile/Scrum ceremonies - Formal progress tracking framework
- Daily standups - Verbal progress updates
- Kanban board - Visual progress tracking
- Management software - Automated tracking (Jira, Linear)

---

## Tags
`project-management` `progress-tracking` `metrics` `reporting` `agile` `sprint` `velocity` `burndown` `stakeholder-communication` `transparency` `team-coordination` `productivity`
