# Merge Conflict Resolution

**ID:** ver-003  
**Category:** Version Control  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 30-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic approach to resolving git merge conflicts when integrating branches, ensuring code integrity and preventing regression.

**Why:** Merge conflicts are inevitable in collaborative development. Resolving them incorrectly can introduce bugs, lose functionality, or create technical debt. A structured approach minimizes errors and preserves intent.

**When to use:**
- Git merge command reports conflicts
- Pull request shows merge conflicts
- Rebase operation halts due to conflicts
- Cherry-pick fails with conflicts
- Attempting to pull with local changes
- Team members edited same code sections

---

## Prerequisites

**Required:**
- [ ] Git installed (2.x+)
- [ ] Understanding of git branching
- [ ] Code editor with merge conflict support
- [ ] Access to commit history
- [ ] Communication with conflicting author (if possible)

**Recommended tools:**
```bash
# Install merge tools
# VS Code (built-in)
code --install-extension eamodio.gitlens

# Vim with Fugitive
# Emacs with Magit
# Meld (graphical)
sudo apt-get install meld  # Linux
brew install meld  # Mac

# Configure git to use VS Code
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait --merge $REMOTE $LOCAL $BASE $MERGED'

# Or configure for other tools
git config --global merge.tool meld
```

**Check before starting:**
```bash
# Verify git status
git status

# Check which branch you're on
git branch --show-current

# Ensure working directory is clean (or stash changes)
git stash list

# View branches involved
git log --all --decorate --oneline --graph | head -20
```

---

## Implementation Steps

### Step 1: Understand the Conflict

**What:** Analyze why the conflict occurred and what changes each branch made.

**How:**
Before touching any code, understand the competing changes and their intent.

**Identify Conflict Context:**
```bash
# See what caused the conflict
git status

# Output shows:
# You have unmerged paths.
#   (fix conflicts and run "git commit")
#
# Unmerged paths:
#   (use "git add <file>..." to mark resolution)
#         both modified:   src/api/users.py
#         both modified:   src/config/settings.py

# View the branches being merged
git log --merge --oneline

# See commits from both branches
git log --oneline --graph --left-right HEAD...MERGE_HEAD

# View what each branch changed
git diff HEAD...MERGE_HEAD -- src/api/users.py
```

**Analyze the Conflicting File:**
```python
# Example conflicted file: src/api/users.py
<<<<<<< HEAD (Current Change - Your Branch)
def get_user(user_id: int) -> User:
    """Get user by ID with caching."""
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)
    if cached:
        return User.from_json(cached)
    
    user = db.query(User).filter(User.id == user_id).first()
    redis.setex(cache_key, 3600, user.to_json())
    return user
=======

 (Incoming Change - Their Branch)
def get_user(user_id: int) -> Optional[User]:
    """Get user by ID with validation."""
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User {user_id} not found")
        return None
    return user
>>>>>>> feature/user-validation

# Conflict analysis:
# - HEAD: Added caching layer
# - feature/user-validation: Added input validation and logging
# - Both modified same function
# - Need to preserve BOTH improvements
```

**Research the Changes:**
```bash
# Who made the changes?
git blame src/api/users.py

# View full commit details
git show HEAD -- src/api/users.py
git show MERGE_HEAD -- src/api/users.py

# Check associated pull request or issue
git log --oneline | grep -i "user validation"
gh pr list --search "user validation"

# View test changes (understand expected behavior)
git diff HEAD...MERGE_HEAD -- tests/
```

**Verification:**
- [ ] Conflict cause understood
- [ ] Both versions analyzed
- [ ] Author intent identified
- [ ] Related changes reviewed
- [ ] Tests examined

**If This Fails:**
→ If unclear about intent, ask the author directly (Slack/PR comment)  
→ If complex conflict, schedule pairing session  
→ If urgent, document assumptions and get review  

---

### Step 2: Choose Resolution Strategy

**What:** Decide how to combine the conflicting changes based on the specific situation.

**How:**
Different conflicts require different resolution strategies.

**Strategy Matrix:**

| Conflict Type | Strategy | When to Use |
|---------------|----------|-------------|
| **Independent Changes** | Merge Both | Changes don't interact, both valuable |
| **Duplicate Work** | Keep One | Same feature implemented twice |
| **Refactor vs Feature** | Adapt Feature | Refactor changes structure, feature adds functionality |
| **Bug Fix vs Feature** | Keep Bug Fix, Adapt Feature | Bug fix is critical |
| **Breaking Change** | Major Decision | Requires team discussion |

**Resolution Strategies:**

```python
# Strategy 1: MERGE BOTH (Most Common)
# Use when both changes are valuable and compatible

# Before (BASE):
def calculate_price(quantity, unit_price):
    return quantity * unit_price

# Branch A (Added tax calculation):
def calculate_price(quantity, unit_price, tax_rate=0.0):
    subtotal = quantity * unit_price
    tax = subtotal * tax_rate
    return subtotal + tax

# Branch B (Added discount):
def calculate_price(quantity, unit_price, discount=0.0):
    subtotal = quantity * unit_price
    final_price = subtotal - discount
    return final_price

# RESOLUTION: Combine both features
def calculate_price(quantity, unit_price, discount=0.0, tax_rate=0.0):
    """Calculate final price with discount and tax."""
    subtotal = quantity * unit_price
    discounted = subtotal - discount
    tax = discounted * tax_rate
    return discounted + tax

# Strategy 2: KEEP ONE (Duplicate Work)
# Use when both branches did the same thing

# Keep the more complete implementation
# Document why the other was discarded

# Strategy 3: ADAPT TO REFACTOR
# Use when structure changed but need to preserve functionality

# Branch A refactored to use classes:
class PriceCalculator:
    def calculate(self, quantity, unit_price):
        return quantity * unit_price

# Branch B added new feature to old structure:
def calculate_price(quantity, unit_price):
    if quantity > 100:
        unit_price *= 0.9  # Bulk discount
    return quantity * unit_price

# RESOLUTION: Add feature to new structure
class PriceCalculator:
    def calculate(self, quantity, unit_price):
        if quantity > 100:
            unit_price *= 0.9  # Bulk discount
        return quantity * unit_price

# Strategy 4: THEIRS or OURS
# Use only when you're certain one side is completely correct

git checkout --ours src/file.py    # Keep your version
git checkout --theirs src/file.py  # Keep their version
# Then manually git add
```

**Decision Documentation:**
```bash
# Document your resolution strategy
cat > .git/MERGE_RESOLUTION_NOTES << 'EOF'
# Merge Resolution Notes

## Conflict: src/api/users.py

### Strategy: MERGE BOTH
Combined caching (HEAD) with validation (feature/user-validation)

### Rationale:
- Caching improves performance
- Validation prevents errors
- Both changes are independent and compatible

### Testing Required:
- Test validation works
- Test caching still functions
- Test validation doesn't bypass cache

### Consulted: @alice (original author of validation)
EOF
```

**Verification:**
- [ ] Resolution strategy selected
- [ ] Strategy appropriate for conflict type
- [ ] Rationale documented
- [ ] Testing plan identified

**If This Fails:**
→ If unsure, choose "merge both" and verify with tests  
→ If breaking change, escalate to team lead  
→ If duplicate work, keep the more complete version  

---

### Step 3: Resolve Conflicts Manually

**What:** Edit the conflicted files to create the correct merged version.

**How:**
Use your editor to combine changes according to your chosen strategy.

**Using VS Code (Recommended):**
```bash
# Open VS Code to conflicted files
code .

# VS Code shows:
# - Current Change (HEAD) - your branch
# - Incoming Change (MERGE_HEAD) - their branch
# - Buttons: Accept Current | Accept Incoming | Accept Both | Compare Changes

# For our example (users.py), choose "Accept Both" then edit:
```

**Manual Resolution:**
```python
# Original conflict:
<<<<<<< HEAD
def get_user(user_id: int) -> User:
    """Get user by ID with caching."""
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)
    if cached:
        return User.from_json(cached)
    
    user = db.query(User).filter(User.id == user_id).first()
    redis.setex(cache_key, 3600, user.to_json())
    return user
=======
def get_user(user_id: int) -> Optional[User]:
    """Get user by ID with validation."""
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User {user_id} not found")
        return None
    return user
>>>>>>> feature/user-validation

# RESOLUTION: Merge both features
def get_user(user_id: int) -> Optional[User]:
    """
    Get user by ID with validation and caching.
    
    Args:
        user_id: User ID to fetch
        
    Returns:
        User object or None if not found
        
    Raises:
        ValueError: If user_id is invalid
    """
    # Validation (from feature/user-validation)
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    
    # Check cache first (from HEAD)
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)
    if cached:
        return User.from_json(cached)
    
    # Query database
    user = db.query(User).filter(User.id == user_id).first()
    
    # Handle not found (from feature/user-validation)
    if not user:
        logger.warning(f"User {user_id} not found")
        return None
    
    # Cache the result (from HEAD)
    redis.setex(cache_key, 3600, user.to_json())
    return user
```

**Using Command Line Merge Tool:**
```bash
# Launch configured merge tool
git mergetool src/api/users.py

# This opens your configured tool (VS Code, Meld, etc.)
# Navigate through conflicts:
# - View: LOCAL (yours), BASE (common ancestor), REMOTE (theirs)
# - Edit: MERGED (final result)
# - Save and quit when done
```

**Handling Multiple Files:**
```bash
# List all conflicted files
git diff --name-only --diff-filter=U

# Resolve them one by one
for file in $(git diff --name-only --diff-filter=U); do
    echo "Resolving: $file"
    code "$file"
    # Or: git mergetool "$file"
    read -p "Press enter when done..."
    git add "$file"
done
```

**Verification:**
- [ ] All conflict markers removed (no <<<<<<<, =======, >>>>>>>)
- [ ] Code syntax valid
- [ ] Both changes preserved (or conscious choice made)
- [ ] Logic makes sense
- [ ] Documentation updated

**If This Fails:**
→ If resolution too complex, abort and reconsider strategy  
→ If unsure, create both versions and A/B test  
→ If breaking existing functionality, add feature flag  

---

### Step 4: Run Tests

**What:** Verify that the merged code works correctly and doesn't introduce regressions.

**How:**
Run comprehensive test suite before committing the resolution.

**Test Execution:**
```bash
# Run ALL tests (not just changed files)
pytest tests/ -v

# Run specific test modules if repo is large
pytest tests/test_users.py -v
pytest tests/test_api.py -v

# Check test coverage
pytest --cov=src tests/

# Run linters
ruff check src/
mypy src/

# Run type checker
mypy src/api/users.py

# Integration tests
pytest tests/integration/ -v
```

**Test-Driven Resolution:**
```python
# If tests are unclear, write new tests for the merge
# tests/test_users_merge.py
"""
Tests for merged get_user functionality.
"""
import pytest
from src.api.users import get_user

def test_get_user_with_invalid_id():
    """Test that validation from feature/user-validation works."""
    with pytest.raises(ValueError, match="Invalid user ID"):
        get_user(-1)
    
    with pytest.raises(ValueError, match="Invalid user ID"):
        get_user(0)

def test_get_user_caching():
    """Test that caching from HEAD still works."""
    # First call should hit database
    user1 = get_user(123)
    
    # Second call should hit cache
    user2 = get_user(123)
    
    # Verify it's cached (check redis mock)
    assert redis.get("user:123") is not None

def test_get_user_not_found_with_cache():
    """Test that not-found case works with caching."""
    # Non-existent user
    user = get_user(99999)
    
    assert user is None
    # Should log warning
    assert "User 99999 not found" in caplog.text

def test_get_user_validation_before_cache():
    """Test that validation happens before cache check."""
    with pytest.raises(ValueError):
        get_user(-1)
    
    # Cache should not be checked for invalid ID
    redis.get.assert_not_called()
```

**Performance Testing:**
```bash
# Check that merge didn't degrade performance
pytest tests/test_performance.py -v

# Or manual benchmark
python -m timeit -s "from src.api.users import get_user" "get_user(123)"
```

**Verification:**
- [ ] All tests pass
- [ ] No new test failures introduced
- [ ] Linters pass
- [ ] Type checking passes
- [ ] Integration tests pass
- [ ] Performance acceptable

**If This Fails:**
→ If tests fail, revisit resolution (may have broken something)  
→ If new test needed, write it before finalizing merge  
→ If performance degraded, investigate optimization  

---

### Step 5: Review the Complete Diff

**What:** Examine the entire set of changes being merged, not just conflict resolutions.

**How:**
Ensure non-conflicted changes are acceptable and aligned with expectations.

**Diff Review:**
```bash
# View complete diff of the merge
git diff HEAD

# View diff with more context
git diff HEAD -U10

# View only the files you resolved
git diff HEAD src/api/users.py

# View the merge result compared to both parents
git diff HEAD^1      # Compare to your branch
git diff HEAD^2      # Compare to their branch (after merge commit)

# Show what changed from base
git diff $(git merge-base HEAD MERGE_HEAD)
```

**Look For:**
```bash
# 1. Unexpected changes
git diff HEAD | grep -A5 -B5 "TODO\|FIXME\|XXX"

# 2. Debugging code left behind
git diff HEAD | grep -i "console.log\|print\|debugger\|pdb"

# 3. Commented out code
git diff HEAD | grep "^+.*#.*"

# 4. Large changes
git diff --stat HEAD

# 5. Changes to critical files
git diff HEAD -- config/ migrations/ requirements.txt
```

**Review Checklist:**
```markdown
## Merge Review Checklist

### Code Quality
- [ ] No debugging statements (print, console.log)
- [ ] No commented-out code
- [ ] No TODOs introduced
- [ ] Error handling appropriate
- [ ] Logging appropriate

### Functionality
- [ ] Core functionality preserved
- [ ] New features work as expected
- [ ] Edge cases handled
- [ ] No regressions

### Dependencies
- [ ] requirements.txt / package.json consistent
- [ ] No conflicting dependency versions
- [ ] Lock files updated properly

### Configuration
- [ ] Config files reviewed
- [ ] Environment variables documented
- [ ] No hardcoded secrets

### Documentation
- [ ] Comments updated
- [ ] Docstrings current
- [ ] README changes appropriate
- [ ] CHANGELOG updated (if applicable)
```

**Verification:**
- [ ] Full diff reviewed
- [ ] No unexpected changes
- [ ] All changes intentional
- [ ] Quality standards met

**If This Fails:**
→ If unexpected changes found, investigate and fix  
→ If unsure about change, consult original author  
→ If too many changes to review, use `git diff --stat` to prioritize  

---

### Step 6: Commit the Merge

**What:** Create a clear, descriptive merge commit that documents the resolution.

**How:**
Write a comprehensive commit message explaining what was merged and how conflicts were resolved.

**Staging Resolved Files:**
```bash
# Mark conflicts as resolved
git add src/api/users.py
git add src/config/settings.py

# Or mark all resolved files
git add .

# Verify staging
git status

# Should show:
# All conflicts fixed but you are still merging.
```

**Merge Commit Message:**
```bash
# Git will provide a default merge commit message
# Customize it to add resolution details

git commit -m "Merge feature/user-validation into main

Resolved conflicts in:
- src/api/users.py: Combined caching (main) with validation (feature)
- src/config/settings.py: Merged timeout settings

Resolution strategy:
- get_user() now includes both validation and caching
- Validation happens before cache check
- Cache still functions as expected
- All tests passing

Reviewed-by: @alice
Tested: Full test suite + manual verification"
```

**Better Commit Message Template:**
```bash
# Create template for complex merges
cat > /tmp/merge-commit-template << 'EOF'
Merge [branch-name] into [target-branch]

## Summary
[Brief description of what's being merged]

## Conflicts Resolved
- [file1]: [resolution strategy]
- [file2]: [resolution strategy]

## Changes Included
- [Major feature 1]
- [Major feature 2]
- [Bug fix]

## Testing
- [X] Unit tests passing
- [X] Integration tests passing
- [X] Manual testing completed

## Reviewers
- @reviewer1: [specific area]
- @reviewer2: [specific area]

## Notes
[Any additional context or decisions made]
EOF

# Use template
git commit -F /tmp/merge-commit-template
# Edit as needed in your editor
```

**Alternative: Using Git Editor:**
```bash
# Just git commit (will open editor with default message)
git commit

# Default message shows:
# Merge branch 'feature/user-validation' into main
# 
# # Conflicts:
# #   src/api/users.py
# #   src/config/settings.py

# Enhance with your details above the conflict list
```

**Verification:**
- [ ] All files staged
- [ ] Commit message clear and descriptive
- [ ] Resolution strategy documented
- [ ] No pending conflicts

**If This Fails:**
→ If forgot to stage files: `git add <file>`  
→ If want to edit commit message: `git commit --amend`  
→ If commit fails due to hooks: fix issues and retry  

---

### Step 7: Verify and Push

**What:** Final verification that the merge is correct before sharing with the team.

**How:**
Run comprehensive checks and push to remote repository.

**Pre-Push Verification:**
```bash
# 1. Verify clean working directory
git status
# Should show: "nothing to commit, working tree clean"

# 2. Run full test suite again
pytest tests/ -v --tb=short

# 3. Check that merge commit looks right
git log --oneline --graph -10

# 4. Verify no files left in conflicted state
git diff --check

# 5. Verify the merge with both parents
git show HEAD --stat

# 6. Run pre-push hooks (if configured)
git push --dry-run
```

**CI/CD Checks:**
```bash
# If using GitHub Actions, check workflow
gh run list --limit 5

# Watch CI after pushing
gh run watch
```

**Push the Merge:**
```bash
# Push to remote
git push origin main

# Or if you're on a feature branch
git push origin feature/my-branch

# Watch for CI failures
echo "Monitor: https://github.com/org/repo/actions"
```

**Post-Push Monitoring:**
```bash
# Monitor for issues
# 1. Watch CI/CD pipeline
# 2. Check for immediate bug reports
# 3. Monitor logs in production (if auto-deployed)

# Notify team
cat > /tmp/merge-notification.md << 'EOF'
🔀 Merged: feature/user-validation → main

## Changes
- Combined caching with input validation
- All tests passing
- No breaking changes

## Highlights
- get_user() now validates input before cache check
- Performance maintained (caching still works)
- Better error messages for invalid user IDs

## Deploy Status
- CI: ✅ Passing
- Staging: Deployed automatically
- Production: Ready for deploy

Questions? #engineering-team
EOF
```

**Verification:**
- [ ] Tests pass locally
- [ ] Merge commit pushed successfully
- [ ] CI/CD pipeline passing
- [ ] No immediate issues reported
- [ ] Team notified (if significant change)

**If This Fails:**
→ If push rejected (someone pushed first): pull and re-resolve if needed  
→ If CI fails: investigate immediately, may need to revert  
→ If tests fail in CI but not locally: check environment differences  

---

### Step 8: Monitor and Document

**What:** Watch for issues after the merge and document any lessons learned.

**How:**
Active monitoring and retrospective documentation improve future merges.

**Monitoring Period (First 24 Hours):**
```bash
# 1. Watch error tracking
# - Sentry, Rollbar, etc.
# - Look for new errors related to changed code

# 2. Monitor metrics
# - Response times
# - Error rates
# - Cache hit rates (for our example)

# 3. Check logs
tail -f /var/log/application.log | grep "user"

# 4. User feedback
# - Support tickets
# - User reports
# - Team feedback
```

**Rollback Plan:**
```bash
# Have rollback plan ready
# If issues emerge:

# Option 1: Revert the merge commit
git revert -m 1 HEAD
git push origin main

# Option 2: Reset to before merge (if not yet deployed)
git reset --hard HEAD^
git push --force origin main  # Use with caution!

# Option 3: Quick fix forward
# Make a fix commit rather than revert
```

**Document Lessons Learned:**
```markdown
# Merge Retrospective: feature/user-validation

## What Went Well
- Clear communication with original author
- Combined features successfully
- Tests caught one edge case
- Clean resolution, no regressions

## What Could Be Better
- Could have caught conflict earlier with rebase
- Tests could be more comprehensive
- Documentation update was delayed

## Action Items
- [ ] Add validation tests to test suite template
- [ ] Document caching patterns in wiki
- [ ] Create guide for validation + caching pattern

## Time Spent
- Conflict resolution: 30 minutes
- Testing: 15 minutes
- Review: 10 minutes
- Total: 55 minutes

## Conflict Difficulty: Medium
## Would I do it the same way? Yes
```

**Update Documentation:**
```bash
# Update relevant documentation
# 1. API documentation (if endpoints changed)
# 2. Architecture docs (if patterns changed)
# 3. Onboarding docs (if new patterns introduced)

# Example:
cat >> docs/caching-patterns.md << 'EOF'
## Validation + Caching Pattern

When combining validation with caching:
1. Validate input BEFORE checking cache
2. Invalid input should throw immediately
3. Cache only valid responses
4. Log warnings for not-found cases

See: src/api/users.py::get_user() for reference implementation
EOF
```

**Verification:**
- [ ] No new errors in monitoring
- [ ] Metrics stable or improved
- [ ] User experience unchanged (or improved)
- [ ] Documentation updated
- [ ] Lessons learned documented

**If This Fails:**
→ If new errors detected: investigate and fix immediately  
→ If metrics degraded: consider rollback and optimization  
→ If user complaints: gather feedback and iterate  

---

## Verification Checklist

After completing this workflow:

- [ ] Conflict cause understood and documented
- [ ] Resolution strategy chosen and applied
- [ ] All conflict markers removed
- [ ] Code compiles/runs without errors
- [ ] All tests pass
- [ ] Full diff reviewed
- [ ] Merge commit created with clear message
- [ ] Changes pushed to remote
- [ ] CI/CD pipeline passing
- [ ] No new issues introduced
- [ ] Team notified (if significant)
- [ ] Lessons documented

---

## Common Issues & Solutions

### Issue: "Too many conflicts to resolve"

**Symptoms:**
- 20+ conflicted files
- Conflicts in every function
- Can't understand what changed

**Solution:**
```bash
# Abort the merge
git merge --abort

# Strategy 1: Break into smaller merges
git merge --no-commit feature-branch -- src/module1/
git add src/module1/
git commit -m "Partial merge: module1"

git merge --no-commit feature-branch -- src/module2/
# Repeat for each module

# Strategy 2: Interactive rebase (rewrite history)
git checkout feature-branch
git rebase -i main
# Resolve conflicts one commit at a time

# Strategy 3: Create intermediate branch
git checkout -b merge-intermediate main
git merge --no-ff --no-commit feature-branch
# Resolve in chunks, test incrementally
```

**Prevention:**
- Merge or rebase frequently (daily)
- Keep feature branches short-lived
- Communicate before large refactors

---

### Issue: "Resolved conflict but tests still fail"

**Symptoms:**
- Conflict resolution looks correct
- But tests fail unexpectedly
- Functionality broken

**Solution:**
```bash
# Step 1: Understand what broke
pytest tests/ -v --tb=long

# Step 2: Compare to both branches
git diff HEAD^1  # Your branch - tests passed here
git diff HEAD^2  # Their branch - tests passed here

# Step 3: Check if resolution broke compatibility
# - Maybe you combined incompatible changes
# - Maybe test expectations changed in both branches

# Step 4: Write failing test first
# Create test/test_merge_issue.py
def test_specific_merge_case():
    # Test the exact scenario that's failing
    assert expected_behavior()

# Step 5: Fix the resolution
# Adjust your merged code until test passes

# Step 6: Verify all tests
pytest tests/ -v
```

**Prevention:**
- Run tests during conflict resolution (not after)
- Understand test changes in both branches
- Add integration tests for merged functionality

---

### Issue: "Accidentally used 'ours' or 'theirs' incorrectly"

**Symptoms:**
- Realized you kept the wrong version
- Lost important changes
- Need to redo resolution

**Solution:**
```bash
# If not yet committed:
git checkout --conflict=merge src/file.py
# Re-opens conflict markers

# If already committed but not pushed:
git reset --soft HEAD^
git checkout --conflict=merge src/file.py
# Redo resolution

# If already pushed:
git revert HEAD
# Then redo merge properly

# To see what you lost:
git show MERGE_HEAD:src/file.py  # Their version
git show HEAD^1:src/file.py      # Your version before merge
```

**Prevention:**
- Never blindly use --ours or --theirs
- Always review the diff before committing
- Use mergetool instead of manual checkout

---

### Issue: "Merge conflict in generated/binary files"

**Symptoms:**
- Conflict in package-lock.json, yarn.lock
- Conflict in .min.js files
- Conflict in compiled binaries

**Solution:**
```bash
# For lock files (package-lock.json, yarn.lock, poetry.lock):
# Step 1: Accept one version
git checkout --theirs package-lock.json

# Step 2: Regenerate from package.json
npm install  # Recreates package-lock.json
# or
yarn install  # Recreates yarn.lock
# or
poetry install  # Recreates poetry.lock

# Step 3: Commit the regenerated file
git add package-lock.json
git commit -m "Regenerate lock file after merge"

# For minified files:
# Regenerate from source
npm run build

# For compiled binaries:
# Recompile
make clean && make
```

**Prevention:**
- Add lock files to merge=union in .gitattributes
- Don't commit generated files (add to .gitignore)
- Use CI to generate binaries

---

## Examples

### Example 1: Simple Feature Merge

**Context:**
Merging a feature branch that added user authentication into main branch.

**Execution:**
```bash
# Start merge
git checkout main
git pull origin main
git merge feature/auth

# Conflict in src/config.py
# BASE: Empty config
# OURS: Added database config
# THEIRS: Added auth config

# RESOLUTION: Merge both
```python
# config.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'myapp'
}

AUTH_CONFIG = {
    'secret_key': os.getenv('SECRET_KEY'),
    'token_expiry': 3600
}
```

```bash
# Test
pytest tests/

# Commit
git add src/config.py
git commit -m "Merge feature/auth: Add authentication config

Combined database config (main) with auth config (feature/auth)."

# Push
git push origin main
```

**Result:**
- Clean merge in 10 minutes
- Both features preserved
- All tests passing

---

### Example 2: Refactor vs Feature Conflict

**Context:**
Main refactored code to use classes, feature branch added new functionality to old functions.

**Execution:**
```bash
# Conflict: src/calculator.py
# OURS (main): Refactored to Calculator class
# THEIRS (feature): Added square root to old functions

# RESOLUTION: Add feature to new class structure
```python
# Before refactor (BASE):
def add(a, b):
    return a + b

# Main branch (refactor to class):
class Calculator:
    def add(self, a, b):
        return a + b

# Feature branch (added sqrt):
def add(a, b):
    return a + b

def sqrt(x):
    return x ** 0.5

# RESOLUTION: Add sqrt to class
class Calculator:
    def add(self, a, b):
        return a + b
    
    def sqrt(self, x):
        """Calculate square root."""
        return x ** 0.5
```

**Result:**
- Feature preserved in refactored structure
- Code remains consistent
- Future features follow new pattern

---

### Example 3: Emergency Hotfix Merge

**Context:**
Production bug fix needs to merge into main while feature work is ongoing.

**Execution:**
```bash
# Hotfix branch from production
git checkout -b hotfix/critical-bug production

# Make fix
# ... fix the bug ...

# Merge back to production
git checkout production
git merge hotfix/critical-bug
git push origin production

# Now merge to main (conflict with ongoing work)
git checkout main
git merge hotfix/critical-bug

# Conflict in same file being refactored
# RESOLUTION: Apply hotfix to refactored code
```python
# Hotfix: Added null check
if user and user.is_active:  # Added 'user and'
    return user

# Main: Refactored to method
def get_active_user(user_id):
    user = get_user(user_id)
    if user.is_active:  # Missing null check
        return user

# RESOLUTION: Apply fix to refactored version
def get_active_user(user_id):
    user = get_user(user_id)
    if user and user.is_active:  # Applied hotfix
        return user
```

**Result:**
- Critical bug fix preserved
- Refactored code maintains fix
- No regression in production

---

## Best Practices

### DO:
✅ Understand the conflict before resolving  
✅ Communicate with the other author  
✅ Test thoroughly after resolution  
✅ Review the complete diff  
✅ Write clear commit messages  
✅ Document complex resolutions  
✅ Merge or rebase frequently  
✅ Keep branches short-lived  
✅ Use merge tools effectively  
✅ Learn from each conflict  

### DON'T:
❌ Blindly accept "ours" or "theirs"  
❌ Resolve conflicts without understanding  
❌ Skip running tests  
❌ Commit without reviewing full diff  
❌ Ignore CI failures  
❌ Let branches diverge too much  
❌ Resolve conflicts alone if confused  
❌ Push without local verification  
❌ Forget to communicate significant merges  
❌ Leave conflict markers in code  

---

## Related Workflows

**Prerequisites:**
- **branch_strategy.md** - Understanding branching models
- **version-control/commit_message_correction.md** - Writing good commit messages

**Next Steps:**
- **development/code_review_checklist.md** - Review merged code
- **testing/test_writing.md** - Add tests for merged functionality

**Related:**
- **development/refactoring_strategy.md** - Preventing conflicts through good refactoring
- **version-control/rebase_vs_merge.md** - Choosing merge strategy

---

## Tags
`version-control` `git` `merge` `conflict-resolution` `collaboration`
