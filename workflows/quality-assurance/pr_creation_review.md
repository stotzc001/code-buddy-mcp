# PR Creation and Review

**ID:** qua-007  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 20-40 minutes (per PR)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive guide for creating high-quality pull requests that get reviewed and merged quickly while maintaining code quality standards.

**Why:** Well-structured PRs with clear descriptions, proper scope, and thorough testing reduce review time, minimize back-and-forth, and prevent bugs. Research shows PRs under 400 lines get reviewed 40% faster and have 15% fewer bugs than larger PRs. Good PR practices also facilitate knowledge sharing, improve code quality, and establish a positive team culture.

**When to use:**
- Creating any pull request for code changes
- Preparing features for review
- Submitting bug fixes
- Proposing refactorings
- Contributing to open source projects
- Establishing PR standards for teams

---

## Prerequisites

**Required:**
- [ ] Git installed and configured
- [ ] Access to repository and PR platform (GitHub/GitLab/Bitbucket)
- [ ] Feature branch with committed changes
- [ ] Understanding of project contribution guidelines
- [ ] CI/CD pipeline configured

**Check before starting:**
```bash
# Verify Git configuration
git config --get user.name
git config --get user.email

# Check current branch
git branch --show-current

# Verify remote connection
git remote -v

# Check commit history
git log --oneline -10

# Verify all changes committed
git status

# Ensure branch is up to date
git fetch origin
git status
```

---

## Implementation Steps

### Step 1: Prepare Your Branch

**What:** Ensure your branch is clean, up-to-date, and ready for review before creating the PR.

**How:**

**Update from main branch:**
```bash
# Fetch latest changes
git fetch origin

# Switch to main branch
git checkout main
git pull origin main

# Switch back to feature branch
git checkout feature/your-feature

# Rebase onto latest main (or merge if team prefers)
git rebase main

# If conflicts occur:
# 1. Resolve conflicts in each file
# 2. git add <resolved-files>
# 3. git rebase --continue

# Force push (if rebased)
git push --force-with-lease origin feature/your-feature

# Or merge if team uses merge workflow
# git merge main
# git push origin feature/your-feature
```

**Clean up commits:**
```bash
# View commit history
git log --oneline origin/main..HEAD

# If too many small commits, squash them
# Interactive rebase (e.g., last 5 commits)
git rebase -i HEAD~5

# In the editor:
# - Keep 'pick' for first commit
# - Change 'pick' to 'squash' for commits to combine
# - Save and close

# Update commit message
# Edit to create single, clear commit message

# Force push (with safety check)
git push --force-with-lease origin feature/your-feature

# Example: Squashing commits
# Before:
# pick abc123 WIP: Start feature
# pick def456 Fix typo
# pick ghi789 Add tests
# pick jkl012 Fix lint errors
#
# After:
# pick abc123 Add user authentication feature
# squash def456 Fix typo
# squash ghi789 Add tests
# squash jkl012 Fix lint errors
```

**Verify changes:**
```bash
# Check diff against main
git diff main...HEAD

# Count changes
git diff --stat main...HEAD

# Verify tests pass
pytest

# Run linting
ruff check .
mypy .

# Check for secrets or sensitive data
git diff main...HEAD | grep -i 'password\|secret\|key\|token'
```

**Verification:**
- [ ] Branch is up to date with main
- [ ] All tests pass locally
- [ ] Linting passes
- [ ] No merge conflicts
- [ ] Commits are clean and logical
- [ ] No secrets or sensitive data in changes
- [ ] Changes are focused on single concern

**If This Fails:**
→ If rebase conflicts are complex, consider merge strategy instead
→ If tests fail, fix before creating PR
→ If too many changes, consider splitting into multiple PRs
→ If secrets detected, remove and rotate them immediately

---

### Step 2: Write Clear PR Title and Description

**What:** Create informative PR title and comprehensive description that helps reviewers understand the changes quickly.

**How:**

**PR Title conventions:**
```markdown
# Good PR titles (use conventional commits format):

feat: Add user authentication with OAuth
fix: Resolve memory leak in background task
refactor: Extract payment processing logic
docs: Update API documentation for v2 endpoints
test: Add integration tests for checkout flow
perf: Optimize database queries in user service
chore: Update dependencies to latest versions

# Components:
# [type]: [concise description under 72 characters]
#
# Types:
# - feat: New feature
# - fix: Bug fix
# - refactor: Code change that neither fixes bug nor adds feature
# - docs: Documentation only
# - test: Adding or updating tests
# - perf: Performance improvement
# - chore: Maintenance tasks
# - style: Formatting, missing semicolons, etc.
# - ci: CI/CD changes
#
# Bad PR titles:
# ❌ "Updates"
# ❌ "Fix stuff"
# ❌ "WIP - Don't merge"
# ❌ "John's changes"
```

**PR Description template:**
```markdown
## Summary
Brief overview of what this PR does (2-3 sentences).

## Motivation
Why is this change needed? What problem does it solve?
Link to related issue: Closes #123

## Changes
Detailed list of changes made:
- Added OAuth authentication flow
- Refactored user service to use new auth
- Updated API endpoints to require authentication
- Added migration for user_auth_tokens table

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [x] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Dependency update

## Testing
How was this tested? What scenarios were covered?
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Tested on staging environment

**Test scenarios:**
1. User can log in with OAuth
2. Invalid credentials are rejected
3. Tokens expire correctly
4. Logout invalidates tokens

## Screenshots (if applicable)
[Add screenshots or videos for UI changes]

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review performed
- [x] Comments added for complex code
- [x] Documentation updated
- [x] No new warnings generated
- [x] Tests added and passing
- [x] Dependent changes merged
- [x] Migration scripts tested
- [x] No secrets in code

## Performance Impact
- Database queries: +2 queries (cached)
- API response time: No significant change
- Memory usage: +5MB (acceptable)

## Security Considerations
- OAuth tokens stored securely (encrypted)
- HTTPS required for auth endpoints
- Rate limiting applied
- Input validation for all endpoints

## Rollback Plan
If issues occur:
1. Revert PR using git revert
2. Run rollback migration
3. Clear authentication cache

## Additional Notes
- Depends on PR #456 being merged first
- Requires environment variable: OAUTH_CLIENT_ID
- Documentation: See docs/authentication.md

## Review Focus Areas
Please pay special attention to:
1. Token expiration logic (line 145-160)
2. Database migration (migration_005.sql)
3. Error handling in OAuth callback
```

**For smaller PRs (bug fixes):**
```markdown
## Summary
Fix memory leak in background task processor

## Problem
Background tasks were not releasing database connections after completion,
causing connection pool exhaustion under high load.

## Solution
- Added explicit connection.close() in finally block
- Implemented connection pooling with max_overflow=10
- Added monitoring for connection pool metrics

## Testing
- Ran load test with 1000 concurrent tasks
- Monitored connection pool for 24 hours
- No connection leaks detected

Closes #789
```

**Verification:**
- [ ] Title follows convention
- [ ] Description is clear and complete
- [ ] Linked to related issues
- [ ] Changes are explained
- [ ] Testing approach documented
- [ ] Checklist completed
- [ ] Breaking changes highlighted
- [ ] Dependencies noted

**If This Fails:**
→ If unsure about description, ask teammate for feedback
→ If changes are complex, add diagrams or flowcharts
→ If performance impact unknown, run benchmarks

---

### Step 3: Ensure PR Size is Manageable

**What:** Keep PR small and focused to enable faster, more thorough reviews.

**How:**

**Check PR size:**
```bash
# Count lines changed
git diff --stat main...HEAD

# Target sizes:
# Ideal: < 200 lines changed
# Good: 200-400 lines changed
# Large: 400-800 lines changed (try to split)
# Too large: > 800 lines (must split)

# Check file count
git diff --name-only main...HEAD | wc -l

# Ideal: < 10 files
# Good: 10-20 files
# Too many: > 20 files (consider splitting)
```

**If PR is too large, split it:**
```bash
# Create separate branches for logical chunks

# Example: Large feature → Multiple PRs
# 1. PR #1: Database schema changes
git checkout -b feature/auth-db-schema
git cherry-pick <commits-for-db>
git push origin feature/auth-db-schema

# 2. PR #2: Backend API (depends on #1)
git checkout -b feature/auth-api
git cherry-pick <commits-for-api>
git push origin feature/auth-api

# 3. PR #3: Frontend integration (depends on #2)
git checkout -b feature/auth-frontend
git cherry-pick <commits-for-frontend>
git push origin feature/auth-frontend

# Note dependencies in PR descriptions
```

**When to split PRs:**
```markdown
Split if PR contains:
✓ Database migrations + feature code → Separate PRs
✓ Multiple unrelated bug fixes → One PR per bug
✓ Refactoring + new feature → Refactor PR first, then feature
✓ Frontend + backend changes → Can split or keep together (team preference)
✓ Documentation + code → Can be together if related

Keep together if:
✓ Changes are tightly coupled
✓ Tests would fail without both parts
✓ Splitting would create temporary broken state
✓ Small enough to review (< 400 lines)
```

**Verification:**
- [ ] PR is focused on single concern
- [ ] Changes are < 400 lines (or justified if larger)
- [ ] Files changed are < 20 (or justified if more)
- [ ] No unrelated changes included
- [ ] Can be reviewed in < 30 minutes
- [ ] Can be understood without extensive context

**If This Fails:**
→ Split into multiple PRs with clear dependencies
→ Use stacked PRs (PR #2 builds on PR #1)
→ Document relationship between PRs
→ Merge in sequence

---

### Step 4: Add Tests and Verify CI Passes

**What:** Ensure comprehensive test coverage and all automated checks pass before requesting review.

**How:**

**Add tests for new code:**
```python
# Example: Testing new authentication feature

# Unit tests
def test_oauth_token_generation():
    """Test OAuth token is generated correctly."""
    user = create_test_user()
    token = generate_oauth_token(user)
    
    assert token is not None
    assert len(token) == 32
    assert validate_token(token, user.id)

def test_oauth_token_expiration():
    """Test token expires after configured time."""
    user = create_test_user()
    token = generate_oauth_token(user, expires_in=1)
    
    assert validate_token(token, user.id)
    time.sleep(2)
    assert not validate_token(token, user.id)

# Integration tests
def test_oauth_login_flow():
    """Test complete OAuth login flow."""
    client = TestClient(app)
    
    # 1. Initiate OAuth
    response = client.get("/auth/oauth/login")
    assert response.status_code == 302
    assert "oauth.provider.com" in response.headers["location"]
    
    # 2. Handle callback
    response = client.get("/auth/oauth/callback", params={
        "code": "test_code",
        "state": "test_state"
    })
    assert response.status_code == 200
    assert "token" in response.json()

# Edge case tests
def test_invalid_oauth_token():
    """Test invalid token is rejected."""
    with pytest.raises(AuthenticationError):
        validate_token("invalid_token", user_id=123)

def test_expired_token_cleanup():
    """Test expired tokens are cleaned up."""
    # Create expired tokens
    create_expired_tokens(count=10)
    
    # Run cleanup
    cleanup_expired_tokens()
    
    # Verify cleanup
    expired_count = count_expired_tokens()
    assert expired_count == 0
```

**Run all tests locally:**
```bash
# Run full test suite
pytest -v

# Run with coverage
pytest --cov=. --cov-report=term --cov-report=html

# Check coverage report
open htmlcov/index.html

# Coverage requirements:
# - Overall: >= 80%
# - New code: >= 90%
# - Critical paths: 100%

# Run specific test types
pytest tests/unit/ -v          # Unit tests
pytest tests/integration/ -v   # Integration tests
pytest -m "not slow" -v        # Skip slow tests
pytest --runslow -v            # Include slow tests
```

**Verify CI/CD pipeline:**
```bash
# Push changes to trigger CI
git push origin feature/your-feature

# Check CI status (GitHub)
gh pr checks <pr-number>

# Or check on web interface
# GitHub: https://github.com/user/repo/pull/123/checks
# GitLab: https://gitlab.com/user/repo/-/merge_requests/123/pipelines

# Expected checks:
# ✅ Build successful
# ✅ Unit tests passed (100%)
# ✅ Integration tests passed
# ✅ Linting passed (ruff, pylint)
# ✅ Type checking passed (mypy)
# ✅ Security scan passed (bandit, safety)
# ✅ Code coverage >= 80%
# ✅ Documentation builds
```

**If CI fails:**
```bash
# View CI logs
gh run view <run-id>

# Download logs for local debugging
gh run download <run-id>

# Common CI failures:

# 1. Test failures
# → Run tests locally: pytest -v
# → Fix failing tests
# → Commit and push

# 2. Linting errors
# → Run locally: ruff check . --fix
# → Commit fixes: git commit -am "fix: Resolve linting errors"

# 3. Type errors
# → Run locally: mypy .
# → Add type hints or # type: ignore with justification

# 4. Coverage drop
# → Add tests for uncovered code
# → Aim for 90%+ coverage on new code

# 5. Security issues
# → Run: bandit -r src/
# → Fix vulnerabilities or document false positives
```

**Verification:**
- [ ] All tests pass locally
- [ ] New functionality has unit tests
- [ ] Integration tests cover happy path
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Test coverage >= 90% for new code
- [ ] All CI checks passing
- [ ] No flaky tests

**If This Fails:**
→ Don't create PR until tests pass
→ If tests are flaky, fix or mark as such
→ If coverage too low, add more tests
→ If CI keeps failing, debug locally first

---

### Step 5: Self-Review Your Changes

**What:** Review your own code as if you were the reviewer to catch issues before others see them.

**How:**

**Use GitHub/GitLab PR preview:**
```bash
# Create draft PR to see diff
gh pr create --draft --title "Draft: Your feature" --body "Self-review in progress"

# Or view diff on command line
git diff main...HEAD

# Review on web interface:
# - Easier to see overall structure
# - Can add comments to your own code
# - See changes as reviewers will
```

**Self-review checklist:**
```markdown
## Code Quality
- [ ] No commented-out code
- [ ] No console.log() or print() statements for debugging
- [ ] No TODO comments (move to issues)
- [ ] No placeholder code (FIX ME, HACK, etc.)
- [ ] No dead code or unused imports
- [ ] Consistent naming conventions
- [ ] No magic numbers (use constants)

## Functionality
- [ ] Code does what PR description says
- [ ] Edge cases handled
- [ ] Error messages are helpful
- [ ] No breaking changes (or documented)
- [ ] Backward compatibility maintained

## Tests
- [ ] Tests actually test the functionality
- [ ] Tests are not just for coverage
- [ ] Test names are descriptive
- [ ] No flaky tests
- [ ] Mocks are appropriate

## Security
- [ ] No secrets or credentials in code
- [ ] Input validation present
- [ ] SQL queries parameterized
- [ ] XSS protection in place
- [ ] Authentication/authorization checked

## Performance
- [ ] No N+1 query problems
- [ ] Efficient algorithms used
- [ ] No unnecessary loops
- [ ] Caching where appropriate
- [ ] Database indexes considered

## Documentation
- [ ] Public functions have docstrings
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] API docs updated
- [ ] Breaking changes documented
```

**Common self-review findings:**
```python
# ❌ Found during self-review: Debug print
def process_data(data):
    print(f"Processing: {data}")  # Remove this!
    return transform(data)

# ✅ Fixed:
def process_data(data):
    logger.debug(f"Processing: {data}")
    return transform(data)

# ❌ Found: Magic number
if len(items) > 100:
    use_batch_processing()

# ✅ Fixed:
MAX_ITEMS_FOR_SINGLE_PROCESS = 100

if len(items) > MAX_ITEMS_FOR_SINGLE_PROCESS:
    use_batch_processing()

# ❌ Found: TODO comment
def calculate_tax(amount):
    # TODO: Handle international tax rates
    return amount * 0.10

# ✅ Fixed: Create issue, reference it
def calculate_tax(amount, country="US"):
    # International tax rates: see issue #456
    return amount * TAX_RATES.get(country, 0.10)

# ❌ Found: Commented code
def get_user(id):
    # Old approach:
    # return db.query(User).filter(User.id == id).first()
    
    # New approach:
    return user_repository.get_by_id(id)

# ✅ Fixed: Remove commented code
def get_user(id):
    return user_repository.get_by_id(id)
```

**Add helpful comments to your own PR:**
```markdown
# Add comments for reviewers on complex sections

📝 Comment on line 145:
"This approach was chosen over XYZ because of performance constraints.
Benchmark results: docs/benchmarks/auth-performance.md"

📝 Comment on line 203:
"Note: This will be refactored in PR #456 to use the new caching layer.
Keeping simple for now to avoid blocking."

📝 Comment on line 312:
"⚠️ Review carefully: This changes the API contract.
Migration guide: docs/migrations/v2-auth.md"
```

**Verification:**
- [ ] Reviewed every line of changed code
- [ ] Removed debug code
- [ ] Removed commented code
- [ ] No obvious issues found
- [ ] Code follows project standards
- [ ] Would approve this if reviewing others' code
- [ ] Added helpful comments for reviewers

**If This Fails:**
→ Fix issues found before marking PR ready
→ If unsure about something, add question in comment
→ If missing tests, add them
→ If breaking change discovered, update documentation

---

### Step 6: Request Review from Appropriate Reviewers

**What:** Assign reviewers who have relevant expertise and can provide quality feedback.

**How:**

**Determine appropriate reviewers:**
```bash
# Check who has worked on these files
git log --format="%an" --follow <filename> | sort | uniq -c | sort -rn | head -5

# Example output:
#    45 Alice Johnson    (main contributor)
#    12 Bob Smith        (recent work)
#     8 Carol White      (initial implementation)

# Check code owners (if CODEOWNERS file exists)
cat .github/CODEOWNERS

# Example CODEOWNERS:
# /src/auth/          @alice @bob
# /src/payments/      @carol @david
# /tests/             @qa-team
# *.sql               @dba-team
```

**Request reviews:**
```bash
# Request review (GitHub)
gh pr create --reviewer alice,bob --title "feat: Add OAuth authentication"

# Or add reviewers to existing PR
gh pr edit <pr-number> --add-reviewer alice,bob

# Request team review
gh pr edit <pr-number> --add-reviewer @org/backend-team

# Set number of required approvals (in repository settings)
# Recommended: 1-2 reviewers for small PRs, 2-3 for large/critical
```

**Reviewer selection guidelines:**
```markdown
Select reviewers based on:

✅ Expertise in affected area
✅ Familiarity with codebase
✅ Available bandwidth
✅ Previous work on related features

Avoid:
❌ Too many reviewers (>3)
❌ Only junior developers
❌ People on vacation/out
❌ Always same person (spread knowledge)

Good combinations:
✅ 1 expert + 1 learner (knowledge sharing)
✅ 1 backend + 1 frontend (for full-stack changes)
✅ 1 developer + 1 QA (for critical features)
```

**Add context in review request:**
```bash
# Create PR with context
gh pr create \
  --reviewer alice,bob \
  --label "backend,auth,high-priority" \
  --title "feat: Add OAuth authentication" \
  --body-file pr-description.md

# Or comment to provide context
gh pr comment <pr-number> --body "
@alice - Please review the OAuth integration, especially token expiration logic
@bob - Please check the database migration and performance impact

This is needed for the Q4 security audit. Target merge: Friday.
"
```

**Set appropriate labels:**
```bash
# Add labels to categorize PR
gh pr edit <pr-number> --add-label "feature,backend,needs-review,high-priority"

# Common labels:
# - Type: feature, bugfix, refactor, documentation
# - Area: backend, frontend, database, devops
# - Priority: critical, high, medium, low
# - Status: needs-review, work-in-progress, blocked
# - Size: small, medium, large
```

**Verification:**
- [ ] Appropriate reviewers assigned
- [ ] Reviewers have relevant expertise
- [ ] Reviewers are available
- [ ] Context provided for reviewers
- [ ] Labels added
- [ ] Priority indicated if urgent
- [ ] Dependencies noted

**If This Fails:**
→ If no one is available, ask in team chat
→ If urgent, escalate to team lead
→ If unsure who to assign, ask team lead
→ If blocked, mark as blocked and explain why

---

### Step 7: Respond to Review Feedback

**What:** Address reviewer comments promptly and professionally, implementing requested changes.

**How:**

**Review feedback workflow:**
```markdown
1. Read all comments before responding
2. Categorize by type:
   - 🔴 Blocking (must fix)
   - 🟡 Suggestions (should fix)
   - 🟢 Nits (nice to have)
   - 💬 Questions (need answers)
3. Acknowledge all feedback
4. Implement changes
5. Respond to each comment
6. Re-request review
```

**Responding to different types of feedback:**
```markdown
## 🔴 Blocking Issue
Reviewer: "This SQL query is vulnerable to injection."

Response:
"Good catch! Fixed in latest commit (abc123). Now using parameterized queries:
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
"

## 🟡 Suggestion
Reviewer: "Consider extracting this validation logic into a separate function."

Response:
"Great idea! Extracted to `validate_user_input()` in commit def456.
Makes it much more reusable."

## 🟢 Nit
Reviewer: "Minor: variable name could be more descriptive."

Response:
"Fixed: `data` → `user_registration_data` in commit ghi789"

## 💬 Question
Reviewer: "Why use Redis here instead of database cache?"

Response:
"Redis was chosen for two reasons:
1. Need sub-10ms response times
2. Automatic TTL expiration
Database cache would require cleanup jobs. 
See benchmark results: docs/benchmarks/cache-comparison.md"

## 💬 Disagreement
Reviewer: "Should refactor this entire module."

Response (if disagree):
"I understand the concern. However, this PR is focused on the auth bug fix.
I've created issue #789 for the refactoring work. Can we address it separately?
This approach:
- Keeps PR focused and small
- Unblocks urgent fix
- Allows proper design discussion for refactor
"
```

**Implement requested changes:**
```bash
# Make changes in response to feedback
# (edit files)

# Commit with reference to PR comment
git commit -am "fix: Use parameterized queries (addresses @alice's comment)"

# Push changes
git push origin feature/your-feature

# GitHub will automatically update the PR

# Respond to each comment
# On GitHub web interface:
# 1. Go to PR conversation
# 2. Reply to each comment
# 3. Click "Resolve conversation" when addressed
```

**Re-request review:**
```bash
# After addressing all blocking feedback
gh pr comment <pr-number> --body "
All feedback addressed! Changes:
- ✅ Fixed SQL injection vulnerability (commit abc123)
- ✅ Extracted validation logic (commit def456)
- ✅ Improved variable names (commit ghi789)
- ✅ Added documentation for Redis choice

@alice @bob - Ready for another look!
"

# Or use GitHub's "Re-request review" button
```

**Handle disagreements professionally:**
```markdown
## When you disagree with feedback:

✅ DO:
- Explain your reasoning
- Provide data/benchmarks if relevant
- Suggest alternatives
- Be open to compromise
- Escalate to team lead if needed

❌ DON'T:
- Dismiss feedback without explanation
- Get defensive
- Ignore comments
- Argue in PR (take to Slack/call)
- Merge without addressing concerns
```

**Verification:**
- [ ] All comments read and categorized
- [ ] Blocking issues fixed
- [ ] Suggestions addressed or explained
- [ ] Questions answered
- [ ] All conversations resolved
- [ ] Changes committed with clear messages
- [ ] Review re-requested
- [ ] Disagreements handled professionally

**If This Fails:**
→ If disagreement can't be resolved, schedule call
→ If too much feedback, ask if PR should be split
→ If reviewer not responding, ping in team chat
→ If blocked indefinitely, escalate to team lead

---

### Step 8: Monitor and Merge

**What:** Monitor PR status, ensure CI stays green, and merge when approved.

**How:**

**Monitor PR status:**
```bash
# Check PR status
gh pr status

# Check CI status
gh pr checks <pr-number>

# View review status
gh pr view <pr-number>

# Set up notifications
# - GitHub: Watch repository → Participating
# - Slack: Integrate GitHub bot for PR updates
# - Email: Enable PR notification emails
```

**Pre-merge checklist:**
```markdown
Before merging, verify:
- [ ] All required approvals received
- [ ] All CI checks passing ✅
- [ ] All conversations resolved
- [ ] No merge conflicts
- [ ] Branch is up to date with main
- [ ] No "DO NOT MERGE" labels
- [ ] Documentation updated
- [ ] Migration scripts tested
- [ ] Feature flags configured (if applicable)
```

**Update branch before merge:**
```bash
# Ensure branch is up to date
git fetch origin
git checkout feature/your-feature

# Method 1: Rebase (preferred for clean history)
git rebase origin/main
git push --force-with-lease origin feature/your-feature

# Method 2: Merge (if team prefers merge commits)
git merge origin/main
git push origin feature/your-feature

# Wait for CI to pass again after update
gh pr checks <pr-number>
```

**Merge strategies:**
```bash
# Squash merge (recommended for most PRs)
# - Creates single commit in main
# - Cleaner history
# - Good for feature branches
gh pr merge <pr-number> --squash --delete-branch

# Merge commit (preserves all commits)
# - Keeps full history
# - Good for complex features
gh pr merge <pr-number> --merge --delete-branch

# Rebase merge (linear history)
# - No merge commit
# - Rewrites history
# - Use with caution
gh pr merge <pr-number> --rebase --delete-branch

# Team typically chooses one strategy consistently
```

**Post-merge actions:**
```bash
# Delete feature branch
git branch -d feature/your-feature
git push origin --delete feature/your-feature

# Or use GitHub's auto-delete feature

# Update local main
git checkout main
git pull origin main

# Close related issues
gh issue close 123 --comment "Fixed in PR #456"

# Deploy to staging/production (if manual)
# This depends on your deployment process

# Monitor for issues
# - Check error tracking (Sentry, Rollbar)
# - Monitor metrics (Datadog, New Relic)
# - Watch logs for anomalies

# Notify stakeholders
# Post in Slack/Teams:
# "🚀 OAuth authentication is now live! PR #456 merged."
```

**If merge is blocked:**
```bash
# Check why merge is blocked
gh pr view <pr-number>

# Common blockers:
# 1. CI failing → Fix and push
# 2. Missing approvals → Follow up with reviewers
# 3. Merge conflicts → Resolve conflicts
# 4. Required status check → Ensure all checks configured correctly

# If blocked indefinitely:
# - Reach out to reviewers via Slack
# - Escalate to team lead
# - Consider closing and creating new PR if too stale
```

**Verification:**
- [ ] All checks passing before merge
- [ ] Required approvals received
- [ ] Branch up to date
- [ ] Merge completed successfully
- [ ] Feature branch deleted
- [ ] Related issues closed
- [ ] Stakeholders notified (if needed)
- [ ] Monitoring checked (no immediate errors)

**If This Fails:**
→ If CI fails after merge, revert immediately
→ If conflicts arise, resolve quickly
→ If production errors, hotfix or revert
→ If major issues, communicate to team

---

## Verification Checklist

After completing PR creation and merge:

- [ ] PR title and description are clear and complete
- [ ] PR size is manageable (< 400 lines ideally)
- [ ] All tests pass and CI is green
- [ ] Code self-reviewed
- [ ] Appropriate reviewers assigned
- [ ] All feedback addressed
- [ ] All approvals received
- [ ] Merge completed successfully
- [ ] Feature branch deleted
- [ ] No production issues detected
- [ ] Documentation updated
- [ ] Team notified (if significant change)

---

## Common Issues & Solutions

### Issue: PR Sitting Without Review

**Symptoms:**
- PR created days ago
- No reviewers assigned or not responding
- Work blocked waiting for review

**Solution:**
```markdown
1. **Ensure reviewers are assigned**
   ```bash
   gh pr edit <pr-number> --add-reviewer alice,bob
   ```

2. **Ping reviewers in team chat**
   "Hey @alice, could you review PR #456 when you have time? 
   It's blocking my next task."

3. **Add more context**
   If PR is unclear, add more details to description

4. **Break up large PR**
   If PR is too large (>400 lines), reviewers may be intimidated

5. **Escalate if urgent**
   If blocking and urgent, escalate to team lead
```

**Prevention:**
- Assign reviewers immediately when creating PR
- Keep PRs small and focused
- Create draft PR early to get feedback
- Establish team SLA for reviews (e.g., 24 hours)

---

### Issue: Too Much Review Feedback

**Symptoms:**
- Dozens of comments on PR
- Reviewer requesting major changes
- Feeling overwhelmed

**Solution:**
```markdown
1. **Schedule synchronous discussion**
   "Hey @alice, lots of feedback here. Can we hop on a call 
   to discuss? Might be faster than back-and-forth."

2. **Clarify scope**
   "Some of these changes seem out of scope for this PR. 
   Should we create separate PRs for X and Y?"

3. **Prioritize feedback**
   - Address blocking issues first
   - Group related feedback
   - Create follow-up issues for non-critical items

4. **Ask for examples**
   If suggestions unclear, ask for code examples
```

**Prevention:**
- Get early feedback (draft PRs, pair programming)
- Follow coding standards
- Keep PRs small and focused
- Self-review thoroughly before requesting review

---

### Issue: Merge Conflicts

**Symptoms:**
- "This branch has conflicts that must be resolved"
- Can't merge PR
- Main branch has diverged

**Solution:**
```bash
# Method 1: Rebase (clean history)
git checkout feature/your-feature
git fetch origin
git rebase origin/main

# Resolve conflicts
# 1. Edit conflicted files
# 2. Remove conflict markers (<<<<, ====, >>>>)
# 3. Keep appropriate changes
git add <resolved-files>
git rebase --continue

# Force push
git push --force-with-lease origin feature/your-feature

# Method 2: Merge (preserves history)
git checkout feature/your-feature
git fetch origin
git merge origin/main

# Resolve conflicts
# 1. Edit conflicted files
# 2. Remove conflict markers
git add <resolved-files>
git commit -m "Merge main into feature branch"
git push origin feature/your-feature
```

**Prevention:**
- Keep PRs short-lived (< 1 week)
- Rebase/merge from main frequently
- Communicate with team about conflicting changes
- Use feature flags for long-running features

---

### Issue: CI Keeps Failing

**Symptoms:**
- CI fails repeatedly
- Different tests fail each time (flaky tests)
- Can't get green build

**Solution:**
```bash
# 1. Identify the issue
gh run view <run-id> --log

# 2. Common failures:

# Flaky tests:
# - Re-run CI (GitHub: "Re-run jobs")
# - If consistently flaky, mark test as flaky or fix
pytest tests/test_flaky.py --lf  # Run last failed

# Environment issues:
# - Check Python/Node version matches CI
# - Verify dependencies are locked (requirements.txt, package-lock.json)

# Test failures:
# - Run tests locally: pytest -v
# - Debug failing tests
# - Ensure tests don't depend on specific order

# Linting issues:
# - Run linter locally: ruff check . --fix
# - Commit fixes

# 3. Ask for help if stuck
# Post in team chat with CI logs
```

**Prevention:**
- Run all checks locally before pushing
- Keep dependencies up to date
- Fix flaky tests immediately
- Use pre-commit hooks

---

## Examples

### Example 1: Small Bug Fix PR

**Context:** Fixing a memory leak in background task processing

**Execution:**
```bash
# 1. Create branch
git checkout -b fix/memory-leak-background-tasks

# 2. Make fix
# (edit src/tasks/processor.py)

# 3. Add test
# (edit tests/test_processor.py)

# 4. Run tests
pytest tests/test_processor.py -v
pytest --cov=src/tasks --cov-report=term

# 5. Commit
git add src/tasks/processor.py tests/test_processor.py
git commit -m "fix: Resolve memory leak in background task processor

- Added explicit connection.close() in finally block
- Implemented connection pooling with max_overflow=10
- Added test to verify connections are released

Closes #789"

# 6. Push
git push origin fix/memory-leak-background-tasks

# 7. Create PR
gh pr create \
  --title "fix: Resolve memory leak in background task processor" \
  --body "## Summary
Fix memory leak causing connection pool exhaustion.

## Problem
Database connections not released after task completion.

## Solution
- Added explicit cleanup in finally block
- Configured connection pooling
- Added regression test

## Testing
- Load tested with 1000 concurrent tasks
- No leaks detected after 24 hours

Closes #789" \
  --reviewer alice,bob \
  --label "bugfix,backend,high-priority"

# 8. Address feedback, merge
```

**Result:** PR reviewed and merged in < 24 hours, bug fixed in production

---

### Example 2: Large Feature PR (Split)

**Context:** Implementing OAuth authentication across frontend and backend

**Execution:**
```bash
# Instead of one large PR, split into 4 smaller PRs:

# PR #1: Database schema
git checkout -b feature/oauth-db-schema
# - Add oauth_tokens table
# - Add migration script
gh pr create --title "feat: Add database schema for OAuth" --draft

# PR #2: Backend API (depends on #1)
git checkout -b feature/oauth-backend-api
# - Implement OAuth flow
# - Add token management
gh pr create --title "feat: Implement OAuth backend API" --draft

# PR #3: Frontend integration (depends on #2)
git checkout -b feature/oauth-frontend
# - Add login UI
# - Integrate with backend
gh pr create --title "feat: Add OAuth frontend integration" --draft

# PR #4: Documentation
git checkout -b feature/oauth-docs
# - API documentation
# - User guide
gh pr create --title "docs: Add OAuth documentation" --draft

# Review and merge in sequence: #1 → #2 → #3 → #4
```

**Result:** Each PR reviewed quickly (< 400 lines), easier to understand, safer to merge

---

### Example 3: Responding to Extensive Feedback

**Context:** PR receives 25 comments requesting changes

**Execution:**
```markdown
## Initial response:
"Thanks for the thorough review @alice! I see several categories of feedback:

🔴 Blocking (must fix):
- SQL injection vulnerability (line 45)
- Missing input validation (line 103)

🟡 Important (should fix):
- Extract validation function (line 78-95)
- Add error handling (line 145)

🟢 Nits:
- Variable names (various)
- Additional comments

💬 Discussion needed:
- Architecture question (line 200)

I'll fix the blocking issues first, then we can discuss the architecture question synchronously?"

## After implementing changes:
"All feedback addressed:

✅ Blocking issues fixed (commits abc123, def456)
✅ Validation logic extracted (commit ghi789)
✅ Error handling improved (commit jkl012)
✅ Variable names improved (commit mno345)

Re: architecture question - I've added a comment explaining the tradeoffs. Happy to discuss further!"

## Result:
Reviewer approves, PR merged
```

**Result:** Structured approach to feedback, clear communication, efficient resolution

---

## Best Practices

### DO:
✅ **Keep PRs small and focused** - Target < 400 lines, single concern  
✅ **Write clear descriptions** - Explain what, why, and how  
✅ **Test thoroughly** - All tests pass, coverage maintained  
✅ **Self-review first** - Catch obvious issues before others  
✅ **Respond promptly** - Address feedback within 24 hours  
✅ **Be professional** - Constructive responses to feedback  
✅ **Update frequently** - Rebase/merge from main regularly  
✅ **Delete branches** - Clean up after merge

### DON'T:
❌ **Create huge PRs** - Break up changes > 400 lines  
❌ **Mix concerns** - Keep refactoring and features separate  
❌ **Skip tests** - Every PR needs tests  
❌ **Ignore CI** - Don't create PR with failing tests  
❌ **Ghost reviewers** - Respond to all feedback  
❌ **Merge force** - Don't merge without approvals  
❌ **Leave WIP public** - Use draft PRs for work in progress  
❌ **Push to main** - Always use PRs

---

## Related Workflows

**Prerequisites:**
- [Test Writing](../development/test_writing.md) - How to write comprehensive tests
- [CI/CD Workflow](../development/ci_cd_workflow.md) - Understanding automated checks
- [Version Control Basics](../version-control/branch_strategy.md) - Git branching strategies

**Next Steps:**
- [Code Review Checklist](./code_review_checklist.md) - How to review others' PRs effectively
- [Test Failure Investigation](./test_failure_investigation.md) - Debugging failing tests
- [Merge Conflict Resolution](../version-control/merge_conflict_resolution.md) - Resolving conflicts

**Related:**
- [Rollback Procedure](../devops/rollback_procedure.md) - If PR causes issues after merge
- [Hotfix Process](../devops/emergency_hotfix.md) - Urgent fixes that skip normal flow

---

## Tags
`quality-assurance` `pull-requests` `code-review` `git` `collaboration` `best-practices` `teamwork`
