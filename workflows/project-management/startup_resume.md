# Startup Resume

**ID:** pro-003  
**Category:** Project Management  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 15-30 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematically resume work on a project after a break, ensuring full context and continuity

**Why:** Jumping back into code without proper context leads to wasted time, repeated work, and mistakes. A structured resume process ensures you understand current state, priorities, and next steps before writing any code

**When to use:**
- Starting work after a weekend or vacation
- Returning to a project after working on something else
- Beginning a new session with Claude after previous conversations
- Taking over work from another developer
- After a context/token limit reset in a long conversation
- When you've forgotten where you left off

---

## Prerequisites

**Required:**
- [ ] Access to version control (git)
- [ ] Access to project documentation
- [ ] Development environment set up
- [ ] Previous work history (git log, notes, or memory)

**Check before starting:**
```bash
# Verify you're in the right project
pwd
git status

# Check if environment works
git log -5 --oneline
ls -la

# For Python projects
python --version
which python

# For Node projects
node --version
npm --version
```

---

## Implementation Steps

### Step 1: Assess Time Since Last Session

**What:** Determine how long it's been and how much context you've lost

**How:**

**Check Last Activity:**

```bash
# When was last commit?
git log -1 --format="%ar - %s"

# When did you last work on files?
git log --all --pretty=format:"%h %ad | %s%d [%an]" --date=short | head -10

# Show your recent activity
git log --author="$(git config user.name)" --since="1 week ago" --oneline

# What branches exist?
git branch -a

# Are there uncommitted changes?
git status
git stash list
```

**Context Loss Assessment:**

| Time Gap | Context Level | Resume Strategy |
|----------|---------------|-----------------|
| < 1 day | High - Remember most | Quick review, dive in |
| 1-3 days | Medium - Remember outline | Review notes, recent commits |
| 4-7 days | Low - Fuzzy memories | Full context rebuild |
| > 1 week | Minimal - Treat as new | Complete orientation |
| > 1 month | None - Fresh start | Act like new developer |

**Verification:**
- [ ] Know how long it's been
- [ ] Identified last working state
- [ ] Found uncommitted work (if any)
- [ ] Know which branch to work on

**If This Fails:**
→ Check `.git/logs/HEAD` for detailed git activity
→ Look in IDE recent files list
→ Check project management tools (Jira, Linear, etc.)

---

### Step 2: Gather Context from Multiple Sources

**What:** Rebuild understanding of project state from all available sources

**How:**

**Source 1: Git History**

```bash
# Review recent commits with details
git log --oneline --decorate --graph -20

# See what changed recently
git log --since="1 week ago" --name-status --oneline

# Review specific files that changed
git log --follow --oneline -- path/to/important/file.py

# Check for merge conflicts or issues
git log --grep="fix\|bug\|TODO" --since="2 weeks ago"

# Review current branch
git log main..$(git branch --show-current) --oneline
```

**Source 2: Documentation**

```bash
# Check for project notes
cat README.md
cat CONTRIBUTING.md
cat docs/CHANGELOG.md

# Look for TODO or FIXME in code
grep -r "TODO\|FIXME" src/ --include="*.py" | head -20

# Check for project status files
cat STATUS.md
cat ROADMAP.md
ls docs/
```

**Source 3: Issue Tracker/Project Management**

```bash
# If using GitHub
gh issue list --assignee "@me" --state open

# Check project board
gh project list

# Or manually visit:
# - GitHub Issues
# - Jira board
# - Linear
# - Asana
```

**Source 4: Communication Channels**

- Check Slack/Discord for recent project discussions
- Review email threads about the project
- Check meeting notes or calendar for context
- Look at PR comments or code reviews

**Source 5: Previous Claude Conversation (if applicable)**

If resuming work with Claude after a break:

```
Ask Claude:
"Can you help me resume? What were we working on in our last conversation?"

Or use Claude's memory:
"What do you remember about this project? What was our last task?"

Or check past chats:
Use recent_chats or conversation_search tools to find previous discussion
```

**Create Context Summary:**

```markdown
# Project Resume Context - [Date]

## Last Session
- Date: [when]
- Working on: [feature/bug]
- Branch: [branch-name]
- Last commit: [message]

## Current State
- [ ] Tests passing: Yes/No
- [ ] Build working: Yes/No  
- [ ] Blockers: [list any]
- [ ] Pending PRs: [links]

## Uncommitted Work
- Files changed: [list]
- Stashed changes: [describe]
- WIP commits: [any]

## Next Actions
1. [Immediate task]
2. [Follow-up task]
3. [Future task]

## Open Questions
- [Question 1]
- [Question 2]
```

**Verification:**
- [ ] Understand what you were working on
- [ ] Know current project state (passing/failing)
- [ ] Identified any blockers or issues
- [ ] Have list of next actions
- [ ] Found relevant documentation

**If This Fails:**
→ Start with smallest unit: last commit message
→ Read recent PR descriptions
→ Ask team members for context

---

### Step 3: Verify Environment and Dependencies

**What:** Ensure development environment is ready and up-to-date

**How:**

**Check Environment Status:**

```bash
# Git status
git status
git fetch origin
git status  # Check if behind origin

# Check if dependencies need updating
# Python
pip list --outdated
git log requirements.txt

# Node.js
npm outdated
git log package.json

# Check if .env needs updates
git log .env.example
diff .env.example .env
```

**Update if Needed:**

```bash
# Update dependencies
# Python
pip install -r requirements.txt --upgrade

# Node.js
npm install
npm update

# Database migrations (if applicable)
# Django
python manage.py showmigrations
python manage.py migrate

# Rails
rails db:migrate:status
rails db:migrate

# Alembic
alembic current
alembic upgrade head
```

**Run Health Checks:**

```bash
# Run tests to verify everything works
pytest tests/
npm test
cargo test

# Check code quality
ruff check .
mypy src/
npm run lint

# Start development server as smoke test
# Python
python manage.py runserver
flask run

# Node.js
npm run dev

# Check if it starts without errors
curl http://localhost:8000/health
```

**Verification:**
- [ ] Git repository is clean or changes are understood
- [ ] Dependencies are up to date
- [ ] Database is migrated
- [ ] Tests pass
- [ ] Development server starts
- [ ] No obvious broken state

**If This Fails:**
→ Create a fresh virtual environment / node_modules
→ Check if `.env` secrets are configured
→ Look for breaking changes in dependencies
→ Check if database needs reset

---

### Step 4: Prioritize and Create Action Plan

**What:** Decide what to work on based on priority and context

**How:**

**Eisenhower Matrix for Task Prioritization:**

```
            URGENT          NOT URGENT
IMPORTANT  ┌─────────────┐ ┌─────────────┐
           │ DO FIRST    │ │ SCHEDULE    │
           │ - Blockers  │ │ - Planning  │
           │ - Bugs      │ │ - Refactor  │
           │ - Hotfixes  │ │ - Tech debt │
           └─────────────┘ └─────────────┘
           
NOT        ┌─────────────┐ ┌─────────────┐
IMPORTANT  │ DELEGATE    │ │ ELIMINATE   │
           │ - Nice-to   │ │ - Bike-     │
           │   haves     │ │   shedding  │
           └─────────────┘ └─────────────┘
```

**Priority Assessment:**

```python
# priority_assessment.py
def assess_task_priority(task):
    score = 0
    
    # Business impact
    if task.blocks_others:
        score += 10
    if task.affects_production:
        score += 10
    if task.customer_facing:
        score += 5
    
    # Technical impact  
    if task.fixes_security_issue:
        score += 10
    if task.fixes_bug:
        score += 5
    if task.reduces_tech_debt:
        score += 3
    
    # Effort vs value
    if task.effort == "small" and task.value == "high":
        score += 5  # Quick win!
    
    # Time sensitivity
    if task.has_deadline:
        score += 5
    
    return score
```

**Create Action Plan:**

**For Short Session (< 2 hours):**
```markdown
## Today's Focus

### Quick Win (30 min)
- [ ] Fix small bug in [module]
- [ ] Add test for [feature]
- [ ] Update documentation

### Main Task (60-90 min)
- [ ] Complete [feature name]
  - [ ] Implement core logic
  - [ ] Add tests
  - [ ] Update docs

### Wrap-up (15 min)
- [ ] Commit work
- [ ] Update status notes
- [ ] Plan next session
```

**For Long Session (> 4 hours):**
```markdown
## Today's Sprint

### Morning: Foundation
- [ ] Complete context rebuild
- [ ] Fix failing tests
- [ ] Review open PRs

### Midday: Core Work
- [ ] Implement [major feature]
  - [ ] Design approach
  - [ ] Write implementation
  - [ ] Add comprehensive tests

### Afternoon: Polish
- [ ] Code review and refactor
- [ ] Documentation
- [ ] Create PR

### Wrap-up
- [ ] Status update
- [ ] Plan tomorrow
```

**Decision Framework:**

```
START HERE:
1. Are tests failing?
   YES → Fix tests first (broken builds block everything)
   NO → Continue

2. Is there a production bug?
   YES → Hotfix immediately
   NO → Continue

3. Is someone blocked on your work?
   YES → Unblock them first
   NO → Continue

4. Do you have incomplete work from last session?
   YES → Finish it first (minimize WIP)
   NO → Start new highest-priority task

5. Pick highest-priority task that:
   - Fits time available
   - You have context for
   - Isn't blocked by dependencies
```

**Verification:**
- [ ] Have clear list of tasks
- [ ] Tasks prioritized by importance
- [ ] Estimated time for each task
- [ ] Know what to do first
- [ ] Plan fits time available

**If This Fails:**
→ Default to: Fix tests → Fix bugs → Complete WIP → New feature
→ When unsure, pick smallest valuable task
→ Ask team lead for priority guidance

---

### Step 5: Start with Low-Risk Warm-up

**What:** Ease back into coding with a small, low-risk task to rebuild momentum

**How:**

**Warm-up Task Ideas:**

**1. Documentation Updates (5-15 min)**
```bash
# Update README if anything changed
# Add comments to confusing code
# Update CHANGELOG
# Fix typos or outdated docs
```

**2. Code Cleanup (10-20 min)**
```python
# Remove unused imports
# Fix linting warnings
# Rename confusing variables
# Extract magic numbers to constants

# Example
# BEFORE
def process(x):
    if x > 100:  # What is 100?
        return x * 2
        
# AFTER
MAX_THRESHOLD = 100

def process_value(value):
    """Process value with threshold check."""
    if value > MAX_THRESHOLD:
        return value * 2
```

**3. Test Addition (15-30 min)**
```python
# Add a missing test case
# Improve test coverage for module you'll work on
# Add edge case tests

def test_user_validation_edge_cases():
    """Test edge cases found in production."""
    assert validate_user({"age": 0}) == False
    assert validate_user({"age": 150}) == False
    assert validate_user({"name": ""}) == False
```

**4. Small Bug Fix (20-30 min)**
```python
# Pick easiest bug from issue tracker
# Fix a TODO you left previously
# Resolve a minor inconsistency

# Look for easy wins
git grep "FIXME\|TODO" | head -5
```

**Benefits of Warm-up:**
- ✅ Rebuilds muscle memory
- ✅ Verifies environment works
- ✅ Provides quick success/momentum
- ✅ Refreshes code familiarity
- ✅ Low risk if you make mistakes
- ✅ Still provides value

**Example Warm-up Sequence:**

```bash
# 1. Run tests to see current state (2 min)
pytest tests/

# 2. Fix obvious linting issues (5 min)
ruff check . --fix

# 3. Add one test case (10 min)
# tests/test_user.py - add edge case

# 4. Update documentation (8 min)
# README.md - add new feature notes

# Total: 25 minutes of productive warm-up
# Now ready for main work with confidence!
```

**Verification:**
- [ ] Completed at least one small task
- [ ] Environment confirmed working
- [ ] Rebuilding confidence/momentum
- [ ] Ready for larger tasks

**If This Fails:**
→ Even smaller: fix a typo, add a comment
→ If environment broken, that's your real task
→ Don't skip this - cold starts lead to mistakes

---

### Step 6: Document Handoff for Next Session

**What:** Create notes for future you (or next developer) to resume efficiently

**How:**

**Create Handoff Document:**

```markdown
# Session Handoff - [Date] - [Your Name]

## What I Did Today
- ✅ Fixed bug in user authentication
- ✅ Added tests for edge cases
- ✅ Updated API documentation
- ⏸️  Started refactoring database queries (in progress)

## Current State
Branch: `feature/user-auth-fix`
Last commit: `abc1234 - Add validation tests`

### Passing
- ✅ All tests passing
- ✅ Linting clean
- ✅ CI/CD green

### In Progress
- 🔄 Database query refactor (src/db/queries.py)
- 🔄 Need to update migration

### Blocked/Issues
- ⚠️  Waiting for API key from ops team (Slack #ops)
- ⚠️  Performance test failing intermittently (issue #456)

## Next Steps
1. **IMMEDIATE** (next session): Finish query refactor
   - Files: src/db/queries.py, src/models/user.py
   - Tests needed for new query methods
   - Estimated: 1-2 hours

2. **THEN**: Create migration for schema change
   - Django migration
   - Test on dev database
   - Estimated: 30 min

3. **FUTURE**: Update API documentation
   - After refactor lands
   - Coordinate with tech writer
   - Estimated: 1 hour

## Key Decisions Made
- Chose to use Redis for caching (faster than memcached)
- Decided NOT to refactor auth module yet (too risky)
- Agreed with team to postpone feature X to next sprint

## Context for Next Developer
- Database schema change is necessary because [reason]
- The weird hack in line 234 is temporary until [PR link]
- Don't forget to run migrations before testing
- The Redis dependency requires Docker running locally

## Open Questions
- Should we add rate limiting to this endpoint?
- How to handle legacy users without email?
- Need product decision on error message wording

## Resources
- Design doc: [link]
- Slack thread: [link]
- Related PR: [link]
- Jira ticket: [link]

## Time Log
- Context rebuild: 20 min
- Bug fix: 45 min
- Testing: 30 min
- Refactor start: 60 min
- Documentation: 15 min
- **Total: 2h 50min**
```

**Alternative Quick Format:**

```markdown
# Quick Handoff - [Date]

## Did
- Fixed auth bug
- Added tests

## Doing
- Query refactor (50% done)

## Next
1. Finish refactor (1h)
2. Create migration (30m)
3. Update docs (1h)

## Blockers
- Need API key (waiting on ops)

## Notes
- Don't forget: migrations required
- Redis must be running
```

**Where to Store Handoff Notes:**

1. **In Project:**
```bash
# Create handoff file
echo "[notes]" > .handoff/2025-10-26.md

# Add to .gitignore (personal notes)
echo ".handoff/" >> .gitignore

# Or commit if team handoffs
git add .handoff/2025-10-26.md
git commit -m "Handoff notes for session"
```

2. **In Commit Message:**
```bash
git commit -m "WIP: User auth refactor

In progress:
- Refactoring database queries
- 50% complete
- Tests passing for completed parts

Next session:
- Complete src/db/queries.py
- Add migration
- Update docs

Blockers:
- Need API key from ops
"
```

3. **In Project Management Tool:**
- Update Jira ticket with progress
- Add comment to GitHub issue
- Update Linear status

4. **In Claude's Memory (if using Claude):**
```
Tell Claude: "Remember for next session:
- We're refactoring database queries
- Current file: src/db/queries.py
- Need to create migration after
- Tests are passing"
```

**Verification:**
- [ ] Future you will understand where you left off
- [ ] All context captured
- [ ] Next steps clear
- [ ] Blockers documented
- [ ] Resources linked

**If This Fails:**
→ Minimum: commit with descriptive message
→ At least update issue/ticket status
→ Even brief notes better than none

---

## Verification Checklist

After completing this workflow:

- [ ] Full context of project state understood
- [ ] Development environment verified working
- [ ] Know what was being worked on previously
- [ ] Clear priority list for current session
- [ ] Completed at least one warm-up task
- [ ] Ready to start main development work
- [ ] Handoff notes created for next session
- [ ] No time wasted on confusion or false starts

---

## Common Issues & Solutions

### Issue: Can't remember what I was working on

**Symptoms:**
- Staring at code with no context
- Multiple WIP branches
- Unclear what's important
- No idea what's broken vs working

**Solution:**
```bash
# Reconstruct from git history
git log --all --author="$(git config user.name)" \
    --since="2 weeks ago" --format="%h %ad %s" \
    --date=short | head -20

# Check commit messages for clues
git log --oneline -10

# Look at branch names
git branch -a | grep -v "main\|master"

# Check what changed in last session
git diff HEAD~5..HEAD --stat

# If all else fails, ask team
# "Hey team, where did we leave off on [project]?"
```

**Prevention:**
- Always create handoff notes before stopping
- Write descriptive commit messages
- Update issue tracker regularly
- Use branch names that explain the work

---

### Issue: Environment is broken after time away

**Symptoms:**
- Tests failing that should pass
- Dependencies missing or outdated
- Database migrations not applied
- Environment variables not set

**Solution:**
```bash
# Nuclear option: fresh start
# Python
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node
rm -rf node_modules/
npm install

# Database reset (CAUTION: loses data)
python manage.py reset_db
python manage.py migrate

# Check .env exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edit .env with real values!"
fi

# Run setup script if exists
./scripts/setup.sh
make setup
```

**Prevention:**
- Document setup steps in README
- Create setup scripts (setup.sh, Makefile)
- Use Docker for consistency
- Version pin dependencies

---

### Issue: Too many things to do, don't know where to start

**Symptoms:**
- Overwhelmed by task list
- Everything seems equally important
- Jumping between tasks without finishing
- Analysis paralysis

**Solution:**
```python
# Apply the "One Thing" rule
# From book: "The ONE Thing" by Gary Keller

# Ask: "What's the ONE thing I can do right now such that
#       by doing it, everything else becomes easier or unnecessary?"

# Example decision tree:
if tests_failing:
    do("Fix tests")  # Everything else depends on this
elif blocking_others:
    do("Unblock them")  # Multiplies team productivity  
elif have_incomplete_wip:
    do("Finish WIP")  # Reduce cognitive load
else:
    do("Highest value task that fits time available")
```

**Start-Small Strategy:**
```markdown
When overwhelmed, do this 15-minute MVP:

1. (5 min) Pick ONE small task
2. (8 min) Complete it fully
3. (2 min) Commit and feel accomplished

Now momentum is building. Pick next small task.

"Success breeds success. Start with wins."
```

**Prevention:**
- Maintain prioritized backlog
- Limit WIP (work in progress)
- Use time-boxing
- Break big tasks into small ones

---

### Issue: Lost motivation / can't focus

**Symptoms:**
- Distracted easily
- Code feels overwhelming
- Avoiding difficult parts
- Procrastinating on task

**Solution:**

**1. Pomodoro Technique:**
```markdown
25 min: Work (no distractions)
5 min: Break
Repeat 4x
15-30 min: Long break
```

**2. Reduce Scope:**
```markdown
# Instead of:
"Implement entire authentication system"

# Do:
"Write one test for login validation"
"Add one error message"
"Extract one function"

Small wins → momentum → larger tasks
```

**3. Change Task Type:**
```markdown
If stuck on:
- Hard problem → Switch to easy task (docs, cleanup)
- Creative work → Switch to mechanical work (tests)
- Solo coding → Pair with someone / ask Claude
- Screen time → Take walk, sketch design on paper
```

**4. Remember Why:**
```markdown
This feature will:
- Help users accomplish [goal]
- Solve problem of [pain point]
- Make [person's] job easier
- Improve [metric]

Code isn't just code - it helps people.
```

**Prevention:**
- Take regular breaks
- Work on things you find interesting
- Celebrate small wins
- Maintain work-life balance

---

## Examples

### Example 1: Returning After Weekend

**Context:** Monday morning, resuming Friday's work

**Execution:**
```bash
# 1. Quick context check (5 min)
git log --since="Friday" --oneline --author="me"
cat .handoff/2025-10-23.md  # Friday's notes

# Output shows:
# - Was working on API endpoint refactor
# - Tests were passing
# - PR was 80% ready

# 2. Verify environment (3 min)
git status
pytest tests/  # All passing ✓
python manage.py runserver  # Starts fine ✓

# 3. Quick warm-up (10 min)
# Add one missing test case
# Update API doc with new endpoint
git add . && git commit -m "docs: Update API endpoint docs"

# 4. Resume main work (rest of morning)
# Finish the remaining 20% of PR
# Address code review comments
# Ready to merge!
```

**Result:** Productive start, no wasted time, work flows smoothly

---

### Example 2: Returning After Vacation (2 weeks)

**Context:** Back from 2-week vacation, many changes happened

**Execution:**
```bash
# 1. Extensive context rebuild (30 min)
# Read recent commits
git log --since="2 weeks ago" --oneline | head -50

# Check what changed in codebase
git diff --stat HEAD~100..HEAD

# Pull latest
git pull origin main

# Check team communications
# - Read Slack channels (10 min skim)
# - Check emails about project
# - Review merged PRs

# 2. Environment update (15 min)
pip install -r requirements.txt --upgrade
python manage.py migrate
pytest tests/  # 2 tests failing (expected - new changes)

# 3. Sync with team (30 min)
# Send message: "Back from vacation! What's the priority?"
# Team responds: Focus on Feature X, Y got delayed
# Quick sync call with lead

# 4. Study new code (45 min)
# Read the 2 major PRs that merged
# Understand new patterns being used
# Fix the 2 failing tests (understand new code)

# 5. Start with easy task (60 min)
# Pick up small issue from backlog
# Get comfortable with codebase again
# Build confidence before tackling bigger tasks

# Day 1 complete: Context rebuilt, environment ready
# Day 2: Start on Feature X with full context
```

**Result:** Smooth reintegration, no major confusion, ready for real work by Day 2

---

### Example 3: Taking Over from Another Developer

**Context:** Coworker left, you're taking over their project mid-flight

**Execution:**
```bash
# 1. Find their work (15 min)
# Check their branches
git branch -a | grep "coworker-name"

# Review their recent commits
git log --author="coworker@email.com" --since="1 month ago"

# Find their tickets
gh issue list --assignee "coworker-name"

# 2. Scheduled handoff meeting (60 min)
# Meet with coworker before they leave (if possible)
# Or with their manager/team lead
# Questions:
# - What's the current status?
# - What's most important?
# - What's blocking?
# - What are the gotchas?
# - Where's the documentation?

# 3. Document understanding (30 min)
# Create .handoff/takeover-notes.md
# Summarize what you learned
# List what's unclear
# Identify knowledge gaps

# 4. Explore codebase (90 min)
# Read through their main files
# Run their code
# Read their tests
# Understand the architecture

# 5. Make small change (60 min)
# Fix a small bug or add small feature
# This forces understanding
# Reveals gaps in knowledge

# 6. Ask questions (ongoing)
# Slack the team with specific questions
# Don't assume - ask for clarification
```

**Result:** Successful handoff, minimal knowledge loss

---

## Best Practices

### DO:
✅ Always create handoff notes before ending session
✅ Start with small warm-up tasks to rebuild context
✅ Verify environment works before diving into code
✅ Use git history as your memory
✅ Update issue tracker / project management tools
✅ Communicate with team about status and blockers
✅ Time-box context rebuilding (don't spend hours on it)
✅ Commit WIP with clear messages if leaving mid-task
✅ Prioritize ruthlessly - not everything is urgent
✅ Take breaks to maintain focus and avoid burnout

### DON'T:
❌ Jump straight into coding without context
❌ Assume you remember everything from last time
❌ Skip environment verification
❌ Leave cryptic commit messages
❌ Have multiple WIP branches without notes
❌ Forget to communicate with team
❌ Try to tackle everything at once
❌ Skip the warm-up (cold starts lead to bugs)
❌ Work on old branches without pulling latest
❌ Forget to document decisions and gotchas

---

## Related Workflows

**Prerequisites:**
- `pro-002`: Progress Tracking - For understanding project status
- `pro-001`: Knowledge Transfer - For documenting work for others
- `vc-002`: Branch Management - For organizing work in branches

**Next Steps:**
- `pro-004`: Token Management Handoff - For long Claude conversations
- `dev-001`: Feature Branch Development - Once you know what to build
- `qa-001`: PR Creation and Review - When ready to submit work

**Alternatives:**
- Pair programming - Have someone walk you through current state
- Mob programming - Team codes together, always in sync
- Continuous deployment - Small changes, less context needed

---

## Tags
`project-management` `productivity` `context` `resume-work` `handoff` `knowledge-continuity` `git` `documentation` `planning` `prioritization`
