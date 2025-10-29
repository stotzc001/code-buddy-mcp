# Token Management Handoff

**ID:** pro-004  
**Category:** Project Management  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 20-45 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Manage Claude conversation context limits and create effective handoffs when approaching token exhaustion

**Why:** Claude conversations have context windows that can fill up during long projects. Without proper token management, you lose valuable context and have to repeat yourself. Strategic handoffs preserve continuity and maintain productivity

**When to use:**
- Approaching Claude's context limit (feeling responses slow down)
- Completing a major phase and starting a new one
- Switching between different aspects of a project
- Before ending a long work session
- When conversation becomes cluttered with tangents
- After accumulating lots of code output that's no longer needed
- When you want a "fresh start" while preserving key context

---

## Prerequisites

**Required:**
- [ ] Active Claude conversation with work in progress
- [ ] Understanding of what context is essential vs disposable
- [ ] Access to project files and documentation
- [ ] Ability to create summary notes

**Check before starting:**
```bash
# Verify you have key files accessible
ls -la README.md PROGRESS.md
git status
git log -5 --oneline

# Check if important code is committed
git diff --stat
```

---

## Implementation Steps

### Step 1: Recognize Token Limit Signals

**What:** Identify when you're approaching context limits and need to plan a handoff

**How:**

**Warning Signs:**

| Signal | Meaning | Action Needed |
|--------|---------|---------------|
| Response time slowing | Context window filling | Consider handoff soon |
| Claude asks "what did we decide?" | Lost track in long context | Handoff needed |
| Repeated information | Claude re-explaining same things | Context is cluttered |
| "As I mentioned earlier" ambiguity | Too much history | Fresh start beneficial |
| Explicit token warning | Near limit | Immediate handoff required |
| Conversation feels scattered | Multiple topics mixed | Clean start would help |

**Proactive Monitoring:**

```markdown
## Signs You're Approaching Token Limits

### Response Quality
- [ ] Responses getting less specific
- [ ] Claude forgetting earlier decisions
- [ ] Having to re-explain context
- [ ] Answers becoming more generic

### Performance
- [ ] Response time increasing noticeably
- [ ] Longer pauses before responses
- [ ] Interface feeling sluggish

### Conversation State  
- [ ] 100+ messages in conversation
- [ ] Multiple complete features discussed
- [ ] Significant code output accumulated
- [ ] Mixed topics and tangents
- [ ] Working on project for 3+ hours straight

### Strategic Timing
- [ ] Completed a major milestone
- [ ] About to start a new feature
- [ ] Good stopping point reached
- [ ] End of work session approaching
```

**Optimal Handoff Timing:**

```
BEST TIMES FOR HANDOFF:
✅ After completing a feature/bug fix
✅ Before starting a new major task
✅ At natural project phase boundaries
✅ When switching from coding to documentation
✅ End of work day/session

AVOID HANDOFF:
❌ In middle of debugging complex issue
❌ During active code refactoring
❌ When holding critical temporary context
❌ In the middle of a multi-step process
```

**Verification:**
- [ ] Identified need for handoff
- [ ] Current task is at a good stopping point
- [ ] Have time to create proper handoff (15-30 min)
- [ ] Know what context is essential to preserve

**If This Fails:**
→ If task incomplete, finish current small step first
→ At minimum, commit code so state is saved
→ Create quick notes even if rushed

---

### Step 2: Capture Essential Context

**What:** Document all critical information needed to continue work seamlessly

**How:**

**Core Context Template:**

```markdown
# Project Handoff - [Project Name] - [Date]

## Current Status
**Working on:** [Brief description]
**Branch:** `feature/branch-name`
**Last commit:** `abc1234 - commit message`
**State:** [In progress / Paused / Blocked]

## What We Accomplished This Session
1. ✅ [Completed task 1]
2. ✅ [Completed task 2]
3. ⏸️  [Started but not finished]

## Current Task Details
**Goal:** [What we're trying to achieve]

**Approach Decided:**
- [Key decision 1 and why]
- [Key decision 2 and why]
- [Architecture/pattern we chose]

**Files Being Modified:**
- `src/module/file1.py` - [What changes]
- `tests/test_file.py` - [What tests added]
- `docs/api.md` - [What documented]

**Code Snippets (if critical):**
```python
# Important function we're working on
def critical_function():
    # Current state of implementation
    pass
```

## Next Steps (Priority Order)
1. **IMMEDIATE:** [Next concrete action]
   - Why: [Reason this is next]
   - Estimated: [Time]
   - Files: [Which files to edit]

2. **THEN:** [Following action]
   - Depends on: [Previous step]
   - Estimated: [Time]

3. **FUTURE:** [Later tasks]
   - Can be deferred because: [Reason]

## Key Decisions & Rationale
- **Decision:** [What we decided]
  - **Why:** [Reasoning]
  - **Alternatives considered:** [What we didn't choose and why]

- **Decision:** [Another important choice]
  - **Why:** [Reasoning]

## Important Context / Gotchas
- ⚠️  [Critical thing to remember]
- ⚠️  [Tricky edge case we discovered]
- ⚠️  [Known issue we're working around]
- 💡 [Insight that will be useful]

## Blockers / Questions
- [ ] [Blocker 1] - Waiting on: [Person/Event]
- [ ] [Question 1] - Need to: [Action to resolve]

## Dependencies & Environment
**Running:**
- Python 3.11 with venv
- PostgreSQL 14 (via Docker)
- Redis for caching

**Required:**
- API keys in `.env` file
- Database migrations applied
- Tests passing on main branch

## Resources & Links
- Design doc: [URL]
- Related PR: [URL]
- Issue tracker: [URL]
- Slack discussion: [URL]
- Previous Claude conversation: [URL]

## Search Keywords for Finding This
`project-name`, `feature-name`, `specific-technical-term`, `author-name`
```

**What to Include:**

**ALWAYS Include:**
- Current goal and what you're trying to achieve
- Key decisions made and their rationale  
- Concrete next steps
- Critical gotchas or tricky parts
- Files being modified

**CONSIDER Including:**
- Code snippets if they're essential
- Error messages you're debugging
- Architecture diagrams (links)
- Important discussions or decisions

**DON'T Include:**
- Full code dumps (link to files instead)
- Tangential discussions
- Obvious information
- Temporary debugging output
- Dead-end approaches you abandoned

**Verification:**
- [ ] Future you could continue work from these notes
- [ ] All key decisions documented with reasons
- [ ] Next steps are concrete and actionable
- [ ] Critical context preserved
- [ ] No essential information forgotten

**If This Fails:**
→ Minimum viable handoff: "Working on X, next step is Y"
→ Include commit hash and branch name
→ Link to more detailed notes elsewhere

---

### Step 3: Store Context for Retrieval

**What:** Save handoff information where it can be found later

**How:**

**Storage Location Options:**

**Option 1: Project Handoff Files**
```bash
# Create handoff directory
mkdir -p .handoffs
cd .handoffs

# Create dated handoff file
cat > 2025-10-26-session.md << 'EOF'
[Your handoff content]
EOF

# Add to git (or .gitignore if personal)
git add .handoffs/2025-10-26-session.md
git commit -m "Session handoff: API refactor progress"

# Or keep personal
echo ".handoffs/" >> .gitignore
```

**Option 2: Commit Message**
```bash
git add .
git commit -m "WIP: User authentication refactor

Current state:
- Refactored login endpoint
- Added password validation
- Tests passing

Next steps:
- Add email verification
- Update API docs  
- Create migration

Note: Redis must be running for tests
See .handoffs/2025-10-26.md for details"
```

**Option 3: Project Management Tool**
```markdown
# Update Jira/Linear/GitHub Issue

## Progress Update - Oct 26
**Status:** In Progress (60% complete)

**This Session:**
- ✅ Implemented core logic
- ✅ Added unit tests
- ⏸️  Started integration tests

**Next Session:**
- Complete integration tests
- Code review
- Documentation

**Notes:**
- Decided to use Redis instead of memcached (faster)
- Found edge case with null emails (TODO: fix)
- Performance looks good (< 50ms p95)
```

**Option 4: Local Documentation**
```bash
# Update project status doc
cat >> PROGRESS.md << 'EOF'

## Session: 2025-10-26

**Branch:** `feature/auth-refactor`
**Status:** 60% complete

**Completed:**
- Core authentication logic
- Password validation
- Unit test suite

**Next:**
- Integration tests
- API documentation
- Database migration

**Decisions:**
- Using Redis for session storage
- Bcrypt for password hashing
- JWT tokens with 1-hour expiry

**Gotchas:**
- Must run Redis locally for tests
- Email field can be null in legacy DB
EOF

git add PROGRESS.md
git commit -m "Update progress notes"
```

**Option 5: Claude's Memory**
```markdown
# For next Claude conversation, use memory tools

Tell Claude to remember:
"Current project: Refactoring user authentication
Current branch: feature/auth-refactor
Next steps: Complete integration tests, then update docs
Important: Redis must be running for tests to pass
Decision: Using JWT tokens with 1-hour expiry"
```

**Option 6: Personal Notes Tool**
```markdown
# In Notion, Obsidian, or similar

Title: [Project Name] - Auth Refactor Session

Date: 2025-10-26
Status: In Progress

[Handoff content copied here]

Tags: #project-name #authentication #work-in-progress
```

**Best Practice: Multiple Locations**

Use a hierarchy:
1. **Primary:** Commit message + git (always survives)
2. **Secondary:** `.handoffs/` directory (detailed notes)
3. **Tertiary:** Project management tool (team visibility)
4. **Optional:** Personal notes (for your workflow)
5. **Optional:** Claude memory (for AI assistance continuity)

**Verification:**
- [ ] Handoff notes stored in accessible location
- [ ] Can find notes via search or browsing
- [ ] Notes are backed up (committed to git)
- [ ] Team can see progress (if needed)
- [ ] Claude can reference in future (if using memory)

**If This Fails:**
→ At minimum: commit with descriptive message
→ Take screenshot of handoff notes
→ Email yourself the notes

---

### Step 4: Prepare for New Conversation

**What:** Set up the next Claude conversation for success

**How:**

**Creating Effective Conversation Starter:**

```markdown
# GOOD Conversation Starter

Hi Claude! I need to continue working on [Project Name].

## Context
I'm working on refactoring the user authentication system.

**Current branch:** `feature/auth-refactor`
**Last commit:** abc1234 - "Add password validation tests"

## What's Done
✅ Implemented core auth logic
✅ Added password validation  
✅ Unit tests passing

## What's Next
I need to complete the integration tests. Specifically:
1. Test login flow end-to-end
2. Test password reset workflow
3. Test edge cases (expired tokens, etc.)

## Key Context
- Using JWT tokens with 1-hour expiry
- Redis for session storage (must be running)
- Found edge case: email can be null for legacy users
- Tests are in `tests/integration/test_auth.py`

## Question
Can you help me write the integration test for the password reset flow?

[Paste current test file if needed]
```

**VS Bad Conversation Starter:**

```markdown
# BAD - Too Vague

Hey, can you help with my code?

[Pastes 1000 lines of code with no context]
```

**Conversation Starter Template:**

```markdown
# Claude Conversation Starter Template

Hi Claude! [Brief greeting + project name]

## Context
[1-2 sentences: What is the project/feature?]

**Current State:**
- Branch: [name]
- Last commit: [hash and message]
- Status: [what's done, what's in progress]

## Previous Session Summary
[2-4 bullet points of key accomplishments]

## Current Goal
[Specific thing you want to accomplish this session]

## Key Decisions/Context
[2-3 most important things to remember]
- Decision 1
- Gotcha/constraint to be aware of
- Any tricky edge cases

## What I Need Help With
[Specific, concrete question or task]

## Relevant Files
- `file1.py` - [what it does]
- `file2.py` - [what it does]

[Paste code only if essential]
```

**Attach Supporting Files:**

```markdown
# In your new Claude conversation

Upload key files:
- README.md (project overview)
- Your handoff notes (.handoffs/2025-10-26.md)
- Current file you're working on
- Related test files

This gives Claude immediate context without using tokens on repetition.
```

**Use Claude's Tools:**

```markdown
# If Claude has access to your project files

"Claude, can you read:
- README.md for project overview
- .handoffs/2025-10-26.md for my handoff notes
- src/auth/login.py for the current implementation

Then help me with [specific task]"
```

**Leverage Claude's Memory:**

```markdown
# If you previously told Claude to remember things

"Claude, what do you remember about this project?
Specifically about the authentication refactor?"

[Claude will recall stored memories]

"Great! Let's continue with [next task]"
```

**Use Past Chats Tools:**

```markdown
# If Claude has conversation_search or recent_chats

"Claude, can you search our past conversations about 
'authentication refactor' and tell me what we decided?"

[Claude retrieves previous context]

"Perfect! Now let's continue by [next step]"
```

**Verification:**
- [ ] New conversation has essential context
- [ ] Question or goal is specific
- [ ] Relevant files attached or referenced
- [ ] Previous decisions mentioned
- [ ] Claude can start helping immediately

**If This Fails:**
→ Start with minimal context, add more as needed
→ Ask Claude to help create summary from your notes
→ Reference the handoff document you created

---

### Step 5: Validate Handoff Completeness

**What:** Ensure the handoff has everything needed before ending current conversation

**How:**

**Handoff Completeness Checklist:**

```markdown
## Before Starting New Conversation, Verify:

### Essential Context Captured
- [ ] What we're building (goal)
- [ ] Why (business/technical reason)
- [ ] Current progress status
- [ ] Next concrete steps

### Decisions Documented  
- [ ] Key technical decisions made
- [ ] Rationale for those decisions
- [ ] Alternatives we considered and rejected
- [ ] Any assumptions or constraints

### Technical Details
- [ ] Branch name and last commit
- [ ] Files being modified
- [ ] Dependencies or prerequisites
- [ ] Environment requirements

### State Information
- [ ] What's working
- [ ] What's broken or in progress
- [ ] Any blockers
- [ ] Any temporary workarounds

### Retrieval Information
- [ ] Handoff saved to findable location
- [ ] Search keywords will work
- [ ] Date and project name clear
- [ ] Links to resources included

### Validation Test
- [ ] Could someone else (or future you) continue from this?
- [ ] Are next steps actionable and specific?
- [ ] Is context complete enough to avoid re-explaining?
```

**Test Your Handoff:**

```markdown
# The "Stranger Test"

Imagine showing your handoff notes to a competent developer who:
- Knows the tech stack
- Doesn't know this project
- Has 30 minutes to understand and continue

Ask yourself:
1. Would they understand what we're building?
2. Would they know what's already done?
3. Would they know what to do next?
4. Would they understand why we made key decisions?
5. Would they be able to run/test the code?

If any answer is "no" → add that missing context
```

**Common Missing Pieces:**

```markdown
# Often Forgotten Context:

1. **The "Why"**
   - Bad: "Refactoring auth code"
   - Good: "Refactoring auth code to support SSO integration 
           (needed for enterprise customers)"

2. **Key Decisions**
   - Bad: "Using Redis"
   - Good: "Using Redis instead of memcached because we need 
           persistence and better data structures"

3. **Gotchas**
   - Bad: [Not mentioned]
   - Good: "Email field can be null for legacy users - 
           handle this in validation"

4. **Next Steps**
   - Bad: "Finish the tests"
   - Good: "Write integration test for password reset flow - 
           see tests/integration/test_auth.py lines 45-60 for pattern"

5. **Current Blockers**
   - Bad: [Not mentioned]
   - Good: "Waiting for API key from ops team (Slack #ops) 
           before we can test email sending"
```

**Verification:**
- [ ] Handoff passes the "stranger test"
- [ ] All essential context included
- [ ] No critical information forgotten
- [ ] Notes are clear and actionable
- [ ] Could successfully start new conversation from this

**If This Fails:**
→ Add the missing pieces you identified
→ Better incomplete handoff than none
→ Can always start new conversation asking Claude to help fill gaps

---

### Step 6: Execute Clean Handoff

**What:** Smoothly transition to the new conversation with preserved context

**How:**

**Handoff Execution Steps:**

**1. Save All Work:**
```bash
# Commit current state
git add .
git commit -m "WIP: Auth refactor - integration tests in progress

Session handoff: See .handoffs/2025-10-26.md
Next: Complete password reset test"

# Push to remote (backup)
git push origin feature/auth-refactor

# Ensure handoff notes are saved
ls -la .handoffs/2025-10-26.md
```

**2. Create Handoff Summary:**
```markdown
# Quick copy-paste summary for new conversation

Project: User Auth Refactor
Branch: feature/auth-refactor  
Status: 60% - Integration tests in progress

Done:
✅ Core auth logic
✅ Password validation
✅ Unit tests

Next:
1. Complete password reset integration test
2. Test expired token handling
3. Update API docs

Key: Redis must be running, JWT tokens expire in 1hr

Handoff details: .handoffs/2025-10-26.md
```

**3. Store Context in Claude's Memory (if applicable):**
```markdown
# In current conversation, tell Claude:

"Claude, please remember for future conversations:

Project: User authentication refactor
Branch: feature/auth-refactor
Status: Integration tests in progress
Next task: Complete password reset flow test
Important: Redis required for tests, JWT tokens 1hr expiry
Key file: tests/integration/test_auth.py"
```

**4. Close Current Conversation Gracefully:**
```markdown
# In current conversation:

"Thanks Claude! We've made great progress.

Accomplished:
- Core auth logic implemented
- Password validation working
- Unit tests passing

I'm going to start a fresh conversation to work on the 
integration tests with a clean context window.

I've saved our progress in .handoffs/2025-10-26.md

See you in the next conversation!"
```

**5. Start New Conversation:**
```markdown
# First message in new conversation:

"Hi Claude! Continuing work on user authentication refactor.

[Paste handoff summary here]

I'd like to complete the password reset integration test.
Can you help me write a test that:
1. Requests password reset
2. Validates reset token
3. Updates password
4. Verifies login with new password

Current test file: tests/integration/test_auth.py
[Attach or paste relevant code if needed]"
```

**6. Verify Continuity:**
```markdown
# In new conversation, check:

"Claude, based on what I shared:
1. What are we working on?
2. What's our next step?
3. What's the key context you need to remember?"

[Claude should correctly summarize]

If Claude is missing context:
→ Provide additional details
→ Attach handoff document
→ Reference specific decisions made
```

**Verification:**
- [ ] All work committed and pushed
- [ ] Handoff notes saved
- [ ] Claude's memory updated (if applicable)
- [ ] New conversation started successfully
- [ ] Context successfully transferred
- [ ] Can immediately continue productive work

**If This Fails:**
→ Share handoff document in new conversation
→ Ask Claude to read project files for context
→ Use past_chats tools to reference previous conversation
→ Provide context iteratively as needed

---

## Verification Checklist

After completing this workflow:

- [ ] Recognized optimal handoff timing
- [ ] Captured all essential context
- [ ] Documented key decisions and rationale
- [ ] Stored handoff notes in accessible location
- [ ] Created effective new conversation starter
- [ ] Validated handoff completeness
- [ ] Successfully transferred to new conversation
- [ ] No productivity loss from token limits
- [ ] Can immediately continue work

---

## Common Issues & Solutions

### Issue: Lost critical context in handoff

**Symptoms:**
- New conversation lacks important decisions
- Have to re-explain background
- Claude doesn't understand next steps
- Missing key technical constraints

**Solution:**
```markdown
# Recovery strategy for lost context

1. **Immediate fix:**
   "Claude, I realized I didn't include important context.
   [Add the missing information]"

2. **Reference past conversation:**
   "Claude, can you search our past conversations for 
   'authentication refactor' and summarize what we decided?"

3. **Attach handoff document:**
   [Upload your .handoffs/2025-10-26.md file]
   "Claude, please read this handoff document for full context"

4. **Incremental rebuild:**
   Start working, add context as you realize it's needed
   Better to add gradually than block on perfect handoff
```

**Prevention:**
- Use the handoff completeness checklist
- Test with the "stranger test"
- Include "why" not just "what"
- Document key decisions and their rationale

---

### Issue: Handoff takes too long

**Symptoms:**
- Spending 30+ minutes on handoff notes
- Overthinking what to include
- Writing too much detail
- Handoff becomes a burden

**Solution:**
```markdown
# Quick Handoff Template (5-10 minutes)

## Status
Working on: [One sentence]
Branch: [name]
Progress: [X% or stage]

## Done This Session
- [Thing 1]
- [Thing 2]

## Next Steps
1. [Specific next action]
2. [Then this]

## Key Context
- [Most important thing to remember]
- [Critical gotcha]

## Files
- [File being modified]

That's it. This is enough for 90% of handoffs.
```

**Decision Tree:**

```
How critical is this context?

Will forget without notes → Include
Might forget → Include briefly
Can figure out from code → Skip
Tangential discussion → Skip
Dead-end approach → Skip
```

**Prevention:**
- Use templates (faster than freeform)
- Set 10-minute timer for handoff
- Perfect is enemy of good enough
- Can always add more context later if needed

---

### Issue: Can't find previous handoff notes

**Symptoms:**
- Stored notes somewhere, can't remember where
- Multiple handoff files, which is latest?
- Notes not showing up in search
- Lost or deleted notes

**Solution:**
```bash
# Search strategies

# 1. Search project for handoff files
find . -name "*handoff*" -o -name "*session*"
find . -name "*.md" -mtime -7  # Modified in last 7 days

# 2. Search git history
git log --all --grep="handoff\|session\|WIP" --since="1 week ago"

# 3. Search commit messages
git log --all --oneline | grep -i "handoff\|session"

# 4. Check common locations
ls -la .handoffs/
ls -la docs/sessions/
cat PROGRESS.md

# 5. Search file contents
grep -r "Next steps" . --include="*.md"
grep -r "Current status" . --include="*.md"

# 6. Check Claude's past conversations
# Use conversation_search or recent_chats
```

**Prevention:**
- Use consistent location: `.handoffs/` directory
- Use consistent naming: `YYYY-MM-DD-session.md`
- Add keywords for search: project name, feature name
- Commit handoffs to git (never lost)
- Use git tags for major handoffs

---

### Issue: Handoff notes become stale

**Symptoms:**
- Handoff says to do X, but you already did X
- Notes reference old file structure
- Decisions noted are now obsolete
- Confusing because outdated

**Solution:**
```markdown
# Mark outdated handoffs

In .handoffs/2025-10-23.md:

---
⚠️  **OUTDATED** - See .handoffs/2025-10-26.md for current status
---

# Or update in place

## Update [2025-10-26]
✅ Completed: Integration tests are done
🔄 Changed: Now using PostgreSQL instead of Redis
➡️  Next: See latest handoff in .handoffs/2025-10-26.md
```

**Prevention:**
- Date handoff files clearly
- Archive old handoffs to `.handoffs/archive/`
- Keep one "current status" doc that gets updated
- Delete obviously outdated handoffs

---

## Examples

### Example 1: Mid-Feature Handoff

**Context:** Implementing large feature, need break, want to continue later

**Execution:**
```markdown
# .handoffs/2025-10-26-payment-integration.md

# Payment Integration - Session Handoff

## Status
Branch: `feature/stripe-payment`
Commit: `abc1234 - Add payment endpoint structure`
Progress: 40% - API endpoint created, need to add processing logic

## Accomplished
✅ Created payment API endpoint (`/api/payments/charge`)
✅ Added Stripe SDK configuration
✅ Created payment model and migration
✅ Basic validation working

## Current Task
Adding payment processing logic to handle Stripe API calls.

**File:** `src/api/payments.py`
**Function:** `process_payment()` (lines 45-60)

**What's done:**
- Request validation
- Payment record creation
- Logging setup

**What's needed:**
- Call Stripe API to charge customer
- Handle success response
- Handle failure cases
- Update payment record with result

## Next Steps
1. **IMMEDIATE** (30 min): Complete `process_payment()` function
   - Use Stripe SDK: `stripe.Charge.create()`
   - Test with Stripe test keys
   - Handle CardError exception

2. **THEN** (20 min): Add tests
   - Mock Stripe API calls
   - Test success case
   - Test failure cases (declined card, network error)

3. **THEN** (15 min): Update docs
   - API documentation
   - Add examples

## Key Decisions
- **Using Stripe**: Chosen over PayPal for better API and webhooks
- **Idempotency**: Using `idempotency_key` to prevent double charges
- **Async**: Will add async processing later, synchronous for MVP

## Important Context
- Stripe test keys in `.env.example`
- Use test card: 4242 4242 4242 4242
- Webhook integration is Phase 2 (not needed yet)
- Currency is USD (hardcoded for now)

## Dependencies
- Stripe SDK installed: `pip install stripe`
- Environment variable: `STRIPE_SECRET_KEY`
- Database migration applied

## Code Snippet
```python
# Current state (incomplete)
def process_payment(amount: int, token: str) -> Payment:
    # Create payment record
    payment = Payment.objects.create(
        amount=amount,
        status='pending'
    )
    
    # TODO: Call Stripe API here
    # stripe.Charge.create(...)
    
    # TODO: Update payment record with result
    
    return payment
```

## Resources
- Stripe docs: https://stripe.com/docs/api/charges/create
- Our API spec: `docs/api/payments.md`

---

# New Conversation Starter

Hi Claude! Continuing work on Stripe payment integration.

I'm at 40% complete - created the API endpoint, now need to implement 
the payment processing logic.

Can you help me complete the `process_payment()` function in 
`src/api/payments.py`? Specifically:
1. Call Stripe API to charge customer
2. Handle success/failure cases
3. Update payment record with result

Key context:
- Using Stripe SDK (already installed)
- Test keys in .env
- Need idempotency for safety

[Would paste relevant code here]
```

**Result:** Seamless continuation in new conversation

---

### Example 2: Context Window Full During Debugging

**Context:** Long debugging session, conversation getting cluttered

**Execution:**
```markdown
# Current conversation is full of debug output, time to clean up

## In Current Conversation:
"Claude, we've figured out the issue! The bug was:
- Race condition in async code
- Fixed by adding proper locking

Solution implemented in commit abc1234.

I'm going to start a fresh conversation to continue with 
the next feature. Thanks for the help debugging!"

## Create Quick Handoff:
cat > .handoffs/2025-10-26-debug-complete.md << 'EOF'
# Debug Session Complete - User Auth

## Issue
Race condition causing intermittent test failures

## Root Cause
Multiple async tasks modifying user state simultaneously

## Solution
Added asyncio.Lock to user update operations
Files: src/models/user.py lines 234-256

## Commit
abc1234 - "fix: Add locking to prevent race condition"

## Tests
✅ All passing now (ran 100x to verify)

## Next Task
Continue with email verification feature
Branch: feature/email-verify
EOF

## New Conversation:
"Hi Claude! Just finished debugging a race condition (see commit abc1234).

Now I want to implement email verification. Can you help me plan
the approach? Requirements:
1. Send verification email on signup
2. Token expires in 24 hours  
3. User can't login until verified

What's the best way to structure this?"
```

**Result:** Clean start, focused on new task

---

### Example 3: End of Day Handoff

**Context:** Work day ending, want to resume tomorrow morning

**Execution:**
```markdown
# .handoffs/2025-10-26-eod.md

# End of Day Handoff - Oct 26

## Today's Accomplishments
✅ Implemented user search API endpoint
✅ Added pagination support
✅ Wrote unit tests (95% coverage)
✅ Updated API documentation

## Tomorrow's Plan
Start work on user filtering feature.

**Branch:** `feature/user-filters`
**Create new branch from:** `main`

**Tasks:**
1. Add query parameters for filtering (age, role, status)
2. Update search logic to apply filters
3. Add tests for each filter
4. Update API docs

**Estimated time:** 2-3 hours

## Notes for Tomorrow Me
- User search is working great, clean code
- Pattern for pagination can be reused for filters
- Remember to handle edge cases (null values, invalid ranges)
- Example similar code: `src/api/products.py` lines 45-80

## Environment
- All tests passing
- Database up to date
- No pending migrations
- Redis running (needed for tests)

## Resources
- API spec: docs/api/users.md (updated today)
- Design mockups: Figma link in Slack
- Discussion: Slack #backend thread from yesterday

---

Tomorrow morning starter:

"Hi Claude! Starting fresh today.

Yesterday I completed the user search API. Today I want to add 
filtering capabilities (filter by age, role, status).

Can you help me plan the implementation? I'm thinking:
- Add query params to existing search endpoint
- Extend database query with filters
- Add tests for each filter

What's the best approach?"
```

**Result:** Smooth start the next morning

---

## Best Practices

### DO:
✅ Create handoffs at natural breakpoints (feature complete, end of day)
✅ Document key decisions and their rationale
✅ Include "why" not just "what"
✅ Make next steps concrete and actionable
✅ Store handoffs in multiple places (git + notes)
✅ Test handoff with "stranger test"
✅ Keep handoffs concise but complete
✅ Use templates for speed
✅ Include search keywords
✅ Update Claude's memory when appropriate

### DON'T:
❌ Wait until context window is completely full
❌ Hand off in middle of complex debugging
❌ Skip documenting key decisions
❌ Write handoffs that are too vague ("finish the feature")
❌ Forget to commit code before handoff
❌ Include too much detail (full code dumps)
❌ Make handoffs a burden (keep them quick)
❌ Forget where you stored handoff notes
❌ Let handoff notes become outdated
❌ Skip handoffs because you're "in flow"

---

## Related Workflows

**Prerequisites:**
- `pro-003`: Startup Resume - For using handoffs to resume work
- `pro-001`: Knowledge Transfer - For documenting work for others
- `pro-002`: Progress Tracking - For maintaining project status

**Next Steps:**
- `pro-003`: Startup Resume - Using handoff to resume in next session
- `dev-001`: Feature Branch Development - Continuing feature work
- `qa-001`: PR Creation and Review - When feature ready for review

**Alternatives:**
- Continuous long conversation - Works for short tasks
- Frequent commits with good messages - Git as handoff notes
- Pair programming - Human provides continuity

---

## Tags
`project-management` `claude` `ai-assisted-development` `context-management` `token-limits` `handoff` `continuity` `documentation` `session-management` `productivity`
