# Commit Message Correction

**ID:** ver-002  
**Category:** Version Control  
**Priority:** MEDIUM  
**Complexity:** Simple  
**Estimated Time:** 5-15 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Fix, improve, or rewrite git commit messages to be clear, descriptive, and follow team conventions.

**Why:** Commit messages are permanent documentation of code changes. Poor messages make it difficult to understand why changes were made, track down bugs, generate changelogs, or review project history. Good messages save hours of investigation and support maintainability.

**When to use:**
- Typo or error in recent commit message
- Forgot to include ticket number in message
- Message is too vague ("fix stuff")
- Need to add details or context
- Message doesn't follow conventions
- Combining multiple commits with better description

---

## Prerequisites

**Required:**
- [ ] Git installed (2.x+)
- [ ] Understanding of git rebase/amend
- [ ] Access to repository
- [ ] Clean working directory

**Check before starting:**
```bash
# Verify git version
git --version

# Check status (should be clean)
git status

# View recent commits
git log --oneline -10

# Check if commits are pushed
git log --branches --not --remotes
```

**⚠️ WARNING:**
- Never rewrite commits that have been pushed and merged to shared branches
- Rewriting history requires `--force` push (coordinate with team)
- Affects anyone who pulled the commits

---

## Implementation Steps

### Step 1: Determine Scope of Change

**What:** Identify which commits need correction and whether they've been shared with others.

**How:**
Check if commits are local-only or already pushed to remote branches.

**Check Commit Status:**
```bash
# List unpushed commits (safe to modify)
git log origin/main..HEAD --oneline

# Or check what would be pushed
git log @{u}..HEAD --oneline

# Check if specific commit is on remote
git branch -r --contains <commit-sha>

# Safe to modify if:
# ✅ Commit is only on your local branch
# ✅ Commit is on your feature branch (not merged to main)
# ✅ You're the only one working on the branch

# UNSAFE to modify if:
# ❌ Commit is on main/develop
# ❌ Commit has been merged via PR
# ❌ Other people have pulled your branch
```

**Scope Decision Matrix:**

| Scenario | Safe to Rewrite? | Method |
|----------|------------------|--------|
| Last commit, not pushed | ✅ Yes | `git commit --amend` |
| Multiple commits, not pushed | ✅ Yes | `git rebase -i` |
| Pushed to feature branch (you're alone) | ⚠️ Careful | Amend + force push |
| Pushed to shared branch | ❌ No | Add new commit with explanation |
| Already merged to main | ❌ Never | Leave as-is or document separately |

**Verification:**
- [ ] Identified commits needing correction
- [ ] Determined if commits are pushed
- [ ] Checked if others have pulled commits
- [ ] Selected appropriate correction method

**If This Fails:**
→ If unsure about push status, assume it's pushed (safer)  
→ If doubt about others pulling, ask in team chat  
→ When in doubt, use safest method (new commit)  

---

### Step 2: Fix Last Commit (Simple Case)

**What:** Correct the most recent commit message before pushing.

**How:**
Use `git commit --amend` for quick fixes to the latest commit.

**Amend Last Commit Message:**
```bash
# Modify last commit message (opens editor)
git commit --amend

# Or specify message directly
git commit --amend -m "fix: Correct user authentication timeout issue"

# Amend without changing message (if you just added files)
git commit --amend --no-edit

# Preview what will change
git log --oneline -2
```

**Common Improvements:**

```bash
# Before (vague)
git commit -m "updates"

# After (descriptive)
git commit --amend -m "feat: Add user profile photo upload with image validation"

# Before (typo)
git commit -m "fix: Reolve login eror"

# After (corrected)
git commit --amend -m "fix: Resolve login error"

# Before (missing context)
git commit -m "fix bug"

# After (with context)
git commit --amend -m "fix: Prevent null pointer exception in user service (closes #423)"

# Before (no type)
git commit -m "added tests"

# After (with type)
git commit --amend -m "test: Add unit tests for authentication module"
```

**Amend with Additional Changes:**
```bash
# Forgot to add a file to last commit
git add forgot_this_file.py
git commit --amend --no-edit

# Or add and update message
git add forgot_this_file.py
git commit --amend -m "fix: Complete authentication refactor (includes tests)"
```

**Push Amended Commit:**
```bash
# If not yet pushed - normal push
git push origin feature/my-branch

# If already pushed - force with lease (safer than --force)
git push --force-with-lease origin feature/my-branch

# Only use --force if you understand the risks
git push --force origin feature/my-branch
```

**Verification:**
- [ ] Message corrected as intended
- [ ] Commit hash changed (expected)
- [ ] Changes still present
- [ ] Pushed successfully (if needed)

**If This Fails:**
→ If editor opens and confuses you, save and exit (`:wq` in vim)  
→ If accidentally amended wrong commit, use `git reset --soft HEAD@{1}`  
→ If force push rejected, check branch protection rules  

---

### Step 3: Fix Multiple Recent Commits

**What:** Correct several commit messages using interactive rebase.

**How:**
Use `git rebase -i` to edit multiple commits at once.

**Interactive Rebase:**
```bash
# Edit last 3 commits
git rebase -i HEAD~3

# Edit commits since branching from main
git rebase -i main

# Edit specific range
git rebase -i <commit-sha>^

# Example: Fix last 5 commits
git rebase -i HEAD~5
```

**Rebase Editor Appears:**
```bash
# Git opens editor with commits (oldest first):
pick abc1234 fix: Update user model
pick def5678 feat: Add profile page
pick ghi9012 updates
pick jkl3456 fix stuff
pick mno7890 feat: Complete user dashboard

# Commands:
# p, pick = use commit
# r, reword = use commit, but edit message
# e, edit = use commit, but stop for amending
# s, squash = meld into previous commit
# f, fixup = like squash, discard this commit's message
# d, drop = remove commit

# Change 'pick' to 'reword' for commits to fix:
pick abc1234 fix: Update user model
pick def5678 feat: Add profile page
reword ghi9012 updates
reword jkl3456 fix stuff
pick mno7890 feat: Complete user dashboard

# Save and close editor
```

**Git Stops for Each Reword:**
```bash
# For each 'reword', git opens editor:

# Original message:
updates

# Change to:
feat: Add user preferences API endpoint

# Save and close

# Next reword opens:
fix stuff

# Change to:
fix: Resolve cache invalidation bug in user service

# Save and close

# Rebase completes
```

**Common Rebase Operations:**

```bash
# Combine multiple commits into one with better message
pick abc1234 WIP: Start feature
squash def5678 WIP: Continue feature
squash ghi9012 WIP: Finish feature

# Becomes:
# feat: Add complete user notification system
#
# - Implemented email notifications
# - Added SMS integration
# - Created notification preferences UI

# Remove commit entirely
pick abc1234 feat: Add feature A
drop def5678 debug: Add console.logs  # Remove debugging commit
pick ghi9012 feat: Add feature B

# Reorder commits
pick ghi9012 feat: Add dashboard
pick abc1234 test: Add dashboard tests
pick def5678 docs: Update dashboard docs
# Reorder logically: code → tests → docs

# Edit commit content
pick abc1234 feat: Add user service
edit def5678 feat: Add user tests  # Stop here to modify
pick ghi9012 feat: Add user docs

# When it stops:
git add additional_test.py
git commit --amend --no-edit
git rebase --continue
```

**Handle Conflicts During Rebase:**
```bash
# If conflicts occur:
# error: could not apply abc1234... feat: Add user dashboard

# 1. View conflicted files
git status

# 2. Resolve conflicts manually
# Edit files, remove conflict markers (<<<<< ===== >>>>>)

# 3. Stage resolved files
git add src/users.py

# 4. Continue rebase
git rebase --continue

# If stuck, abort and try again
git rebase --abort
```

**Verification:**
- [ ] All intended commits reworded
- [ ] Commit history looks correct
- [ ] No unintended changes
- [ ] Conflicts resolved (if any)

**If This Fails:**
→ If confused in rebase, `git rebase --abort` and start over  
→ If conflicts too complex, abort and fix one at a time  
→ If lost commits, use `git reflog` to recover  

---

### Step 4: Write Good Commit Messages

**What:** Follow conventions for clear, useful commit messages.

**How:**
Use a structured format that provides context and clarity.

**Conventional Commits Format:**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
```bash
feat:     # New feature for user
fix:      # Bug fix
docs:     # Documentation only
style:    # Formatting, missing semicolons, etc.
refactor: # Code change that neither fixes bug nor adds feature
test:     # Adding or updating tests
chore:    # Build process, dependency updates, tooling
perf:     # Performance improvement
ci:       # CI configuration changes
revert:   # Revert a previous commit
```

**Examples:**

```bash
# Simple bug fix
git commit -m "fix: Resolve null pointer in user authentication"

# Feature with scope
git commit -m "feat(api): Add user profile endpoints"

# With body for context
git commit -m "fix: Prevent race condition in cache layer

The cache was not properly locked during updates, causing
occasional stale data reads. Added mutex to synchronize
access to cache entries.

Fixes #452"

# Breaking change (important!)
git commit -m "feat!: Change user API response format

BREAKING CHANGE: User API now returns camelCase instead of snake_case.
Update clients to use new field names:
- user_id → userId
- first_name → firstName
- last_name → lastName

Migration guide: docs/api-migration.md"

# Multiple ticket references
git commit -m "fix: Resolve multiple authentication issues

Fixes #123, #456, #789"

# Co-authored commit
git commit -m "feat: Add real-time notifications

Co-authored-by: Alice Smith <alice@example.com>
Co-authored-by: Bob Jones <bob@example.com>"
```

**Message Quality Checklist:**

```markdown
## Good Commit Message Qualities

### ✅ DO:
- Use imperative mood: "Add feature" not "Added feature"
- Be specific: "Fix login timeout" not "Fix bug"
- Explain WHY, not just WHAT
- Reference issues/tickets: "Closes #123"
- Keep first line under 72 characters
- Use body for details (if needed)
- Include breaking changes prominently

### ❌ DON'T:
- "WIP", "temp", "asdf"
- "Fix stuff", "Updates"
- "Fixed the thing"
- Commit messages without context
- Assume readers know the problem
- Use vague pronouns ("it", "that")
```

**Message Templates:**

```bash
# Feature
feat(scope): Add [what]

[Why this feature is needed]
[How it works]
[Any important details]

Closes #issue

# Bug Fix
fix(scope): Resolve [what problem]

[What was broken]
[Root cause]
[How the fix works]

Fixes #issue

# Refactor
refactor(scope): Improve [what]

[Why refactoring was needed]
[What changed]
[Performance impact, if any]

# Documentation
docs(scope): Update [what]

[What information was added/changed]
[Why documentation needed updating]
```

**Configuration (Commitizen):**

```bash
# Install commitizen for commit message prompts
npm install -g commitizen cz-conventional-changelog

# Initialize
commitizen init cz-conventional-changelog --save-dev --save-exact

# Use instead of git commit
git cz

# Or
cz

# Prompts:
# ? Select type: (Use arrow keys)
# > feat:     A new feature
#   fix:      A bug fix
#   docs:     Documentation only changes
#   ...
#
# ? Scope: (optional)
# api
#
# ? Short description:
# Add user profile endpoints
#
# ? Longer description: (optional)
# Implements /api/users/:id/profile for fetching and updating profiles
#
# ? Are there breaking changes? (y/N)
# N
#
# ? Issues closed: (optional)
# #123, #456
```

**Verification:**
- [ ] Type specified (feat, fix, etc.)
- [ ] Description is clear and specific
- [ ] Imperative mood used
- [ ] Ticket references included (if applicable)
- [ ] Breaking changes noted (if applicable)
- [ ] Under 72 characters (first line)

**If This Fails:**
→ If unsure about type, choose most specific one  
→ If description too long, move details to body  
→ If no ticket, that's okay (but useful when available)  

---

### Step 5: Fix Commit After Push (Force Push)

**What:** Correct commits that have been pushed to a feature branch.

**How:**
Use force-with-lease for safer force pushing.

**⚠️ Important Warnings:**
```bash
# NEVER force push to:
# ❌ main
# ❌ develop  
# ❌ Any branch others are working on
# ❌ Any branch with open PRs from others

# Safe to force push to:
# ✅ Your personal feature branch
# ✅ Branches where you're sole developer
# ✅ Before PR is reviewed
```

**Force Push Process:**

```bash
# 1. Make corrections locally (amend or rebase)
git commit --amend -m "fix: Correct commit message"

# 2. Verify changes look correct
git log --oneline -5

# 3. Use force-with-lease (safer than --force)
git push --force-with-lease origin feature/my-branch

# What --force-with-lease does:
# - Checks if remote has commits you don't have locally
# - Rejects push if someone else pushed
# - Prevents accidentally overwriting others' work

# If force-with-lease fails:
error: failed to push some refs to 'origin'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing

# Solution:
git fetch origin
git rebase origin/feature/my-branch
git push --force-with-lease origin feature/my-branch
```

**When Others Have Pulled Your Branch:**

```bash
# Notify team BEFORE force pushing
# In Slack/Teams:
⚠️  I need to force push to feature/user-auth
Please don't pull until I give the all-clear (~5 min)

# After force push:
✅ Force push complete on feature/user-auth
Please run:
  git fetch origin
  git reset --hard origin/feature/user-auth

# Team members update:
git fetch origin
git reset --hard origin/feature/user-auth
# This discards their local changes! Make sure they're okay with this
```

**Alternative: Avoid Force Push:**
```bash
# Instead of rewriting history, add correction commit
git commit -m "fix: Correct previous commit message

Previous commit had typo. This commit provides correct description:
- Actually implemented user profile endpoints
- Not 'updates' as previously stated"

# Pros:
# ✅ No force push needed
# ✅ Safe for shared branches
# ✅ History preserved

# Cons:
# ❌ Clutters history
# ❌ Original bad message still visible
```

**Verification:**
- [ ] Team notified (if branch is shared)
- [ ] Force push completed successfully
- [ ] Remote branch matches local
- [ ] Team has updated their local copies

**If This Fails:**
→ If push rejected by branch protection, temporarily disable  
→ If others have changes, coordinate merge/rebase first  
→ If unsure, create new branch and PR instead  

---

### Step 6: Fix Old Commits (Advanced)

**What:** Correct commits deep in history that require rewriting many commits.

**How:**
Use interactive rebase with careful planning.

**Deep History Rewrite:**

```bash
# Find the commit needing correction
git log --oneline -20
# abc1234 Recent commit
# def5678 Another commit
# ghi9012 Target commit (bad message)
# jkl3456 Old commit
# ...

# Rebase from parent of target commit
git rebase -i ghi9012^

# Or specify number of commits
git rebase -i HEAD~15

# Editor opens with commit list:
pick jkl3456 Old commit
pick ghi9012 bad mesage  # ← Fix this
pick def5678 Another commit
pick abc1234 Recent commit

# Change to 'reword':
pick jkl3456 Old commit
reword ghi9012 bad mesage
pick def5678 Another commit
pick abc1234 Recent commit

# Save, close editor
# Git opens editor for reword
# Change message and save
# All subsequent commits get new SHAs
```

**Rewriting Merged Commits:**

```bash
# If target commit was part of a merge:
git log --oneline --graph -20

# More complex - may need to preserve merge commit
git rebase -i -p <commit>^  # -p preserves merges

# Or rebase and re-merge
git rebase -i <commit>^  # Without -p
# Manually recreate merge if needed
```

**Large-Scale Rewrites:**

```bash
# Rewrite commit messages matching pattern
git filter-branch --msg-filter '
  if echo "$GIT_COMMIT_MSG" | grep -q "WIP"; then
    echo "$GIT_COMMIT_MSG" | sed "s/WIP/feat/"
  else
    echo "$GIT_COMMIT_MSG"
  fi
' --all

# Warning: filter-branch is powerful and dangerous
# Creates backup refs in refs/original/
# Always test on a copy first

# Modern alternative: git-filter-repo
pip install git-filter-repo

git filter-repo --message-callback '
  return message.replace(b"WIP", b"feat")
'
```

**Recovery If Things Go Wrong:**

```bash
# View reflog (history of HEAD changes)
git reflog

# Output:
abc1234 HEAD@{0}: rebase -i (finish): returning to refs/heads/main
def5678 HEAD@{1}: rebase -i (reword): fix: Correct commit message
ghi9012 HEAD@{2}: rebase -i (start): checkout HEAD~5
jkl3456 HEAD@{3}: commit: bad mesage

# Reset to before rebase
git reset --hard HEAD@{3}

# Or to specific commit
git reset --hard ghi9012

# Create backup branch before risky operations
git branch backup-before-rebase
git rebase -i HEAD~10
# If it goes wrong:
git reset --hard backup-before-rebase
```

**Verification:**
- [ ] Backup created before starting
- [ ] Target commits corrected
- [ ] No unintended changes
- [ ] All commits still present
- [ ] Tests still pass

**If This Fails:**
→ If rebase gets too complex, abort and try smaller sections  
→ If lost commits, check `git reflog` for recovery  
→ If truly stuck, restore from backup branch  

---

### Step 7: Correct Commit Message in Pull Request

**What:** Fix commit messages after creating a pull request.

**How:**
Amend and force push, or use GitHub/GitLab features.

**GitHub Method (Squash and Merge):**

```bash
# When PR is set to "Squash and merge"
# You can edit the commit message during merge

# 1. In PR, click "Squash and merge"
# 2. Edit commit message in the dialog
# 3. Merge

# Result: All commits squashed into one with your message
```

**GitLab Method:**

```bash
# Similar to GitHub:
# Merge Request → Squash commits → Edit commit message
```

**Fix Before Review:**

```bash
# If PR not yet reviewed, fix freely
git commit --amend -m "fix: Correct authentication timeout (fixes #423)"
git push --force-with-lease origin feature/auth

# PR automatically updates
```

**Fix After Review Started:**

```bash
# Option 1: Add fixup commit (preserves review context)
git commit --fixup abc1234  # Fixup specific commit
git push origin feature/auth

# Later, before merge, squash interactively:
git rebase -i --autosquash main

# Option 2: Ask reviewer if force push is okay
# In PR comments:
"I need to fix commit messages. Ok to force push?
Reviews won't be lost but line comments may move."

# Wait for approval
git commit --amend -m "Better message"
git push --force-with-lease origin feature/auth
```

**PR Title and Description:**

```markdown
# Good PR Title (becomes commit message)
feat: Add user authentication with OAuth2

# Description (becomes commit body)
## Changes
- Implemented OAuth2 flow
- Added JWT token validation  
- Created user session management

## Testing
- Added unit tests for auth flow
- Manual testing with Google OAuth

## Breaking Changes
None

Closes #423, #456
```

**Verification:**
- [ ] PR title is clear and descriptive
- [ ] PR description provides context
- [ ] Commit messages follow conventions
- [ ] Reviewer notified if force push needed

**If This Fails:**
→ If reviewer objects to force push, use squash merge  
→ If PR already approved, ask before changing  
→ If line comments important, avoid rewriting  

---

### Step 8: Prevent Future Issues

**What:** Set up tools and habits to write good commit messages from the start.

**How:**
Use commit templates, hooks, and tooling.

**Commit Message Template:**

```bash
# Create template
cat > ~/.gitmessage << 'EOF'
# <type>(<scope>): <subject> (Max 72 characters)
# |<----  Using a Maximum Of 72 Characters  ---->|

# Explain why this change is being made
# |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|

# Provide links or keys to any relevant tickets, articles or resources
# Example: Closes #123

# --- COMMIT END ---
# Type can be
#    feat     (new feature)
#    fix      (bug fix)
#    refactor (refactoring code)
#    style    (formatting, missing semicolons, etc.)
#    doc      (changes to documentation)
#    test     (adding or refactoring tests)
#    chore    (updating grunt tasks etc.)
# --------------------
# Remember to
#    Capitalize the subject line
#    Use the imperative mood in the subject line
#    Do not end the subject line with a period
#    Separate subject from body with a blank line
#    Use the body to explain what and why vs. how
#    Can use multiple lines with "-" for bullet points in body
EOF

# Configure git to use template
git config --global commit.template ~/.gitmessage

# Now 'git commit' opens template
git commit
```

**Commit Message Validation Hook:**

```bash
# .git/hooks/commit-msg
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# Validate commit message format

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check for conventional commit format
pattern="^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,72}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
  echo "❌ Invalid commit message format"
  echo ""
  echo "Format: <type>(<scope>): <description>"
  echo ""
  echo "Valid types: feat, fix, docs, style, refactor, test, chore"
  echo "Example: feat(auth): Add OAuth2 login"
  echo ""
  echo "Your message:"
  echo "$commit_msg"
  exit 1
fi

echo "✅ Commit message format valid"
EOF

chmod +x .git/hooks/commit-msg

# Test it
git commit -m "updates"
# ❌ Invalid commit message format

git commit -m "feat: Add user authentication"
# ✅ Commit message format valid
```

**Pre-commit Hook:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v2.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args:
          - feat
          - fix
          - docs
          - style
          - refactor
          - test
          - chore
          - revert
          - ci
          - perf

# Install pre-commit
pip install pre-commit
pre-commit install --hook-type commit-msg

# Now all commits are validated
git commit -m "bad message"
# Conventional Commit......................................................Failed
```

**IDE Integration:**

```bash
# VS Code: Conventional Commits extension
# Install: code --install-extension vivaxy.vscode-conventional-commits

# Usage: Ctrl+Shift+P → "Conventional Commits"
# Prompts for type, scope, description

# IntelliJ/WebStorm: Git Commit Template plugin
# Preferences → Plugins → Git Commit Template

# Vim: vim-gitcommit plugin
# Shows commit message examples in Vim
```

**Team Guidelines:**

```markdown
# docs/commit-guidelines.md

## Commit Message Guidelines

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Examples
- `feat(api): Add user endpoints`
- `fix: Resolve cache timeout`
- `docs: Update README`

### Enforcement
- Pre-commit hooks validate format
- CI checks message format
- PRs require conventional commits

### Resources
- [Conventional Commits](https://conventionalcommits.org)
- [Our commit template](~/.gitmessage)
- [Slack: #git-help](slack://channel/git-help)
```

**Verification:**
- [ ] Commit template installed
- [ ] Validation hooks configured
- [ ] Team guidelines documented
- [ ] IDE tools installed (optional)
- [ ] Team trained on conventions

**If This Fails:**
→ If hooks too strict, adjust patterns  
→ If team forgets, add reminders  
→ If tooling conflicts, simplify setup  

---

## Verification Checklist

After completing this workflow:

- [ ] Identified commits needing correction
- [ ] Determined if commits are safe to rewrite
- [ ] Applied appropriate correction method
- [ ] Messages follow conventions
- [ ] Changes pushed successfully
- [ ] Team notified (if force push)
- [ ] Prevention measures in place
- [ ] Validation hooks configured

---

## Common Issues & Solutions

### Issue: "Can't remember what I changed"

**Symptoms:**
- Need to write message but forgot what was modified
- Committed without reviewing changes

**Solution:**
```bash
# View what changed in commit
git show HEAD

# Or just the files
git show HEAD --name-only

# Or detailed diff
git show HEAD --stat

# Compare with previous commit
git diff HEAD^ HEAD

# View specific file changes
git show HEAD -- src/users.py
```

**Prevention:**
- Review changes before committing: `git diff --staged`
- Commit frequently with incremental changes
- Use `git add -p` for selective staging

---

### Issue: "Rebased wrong number of commits"

**Symptoms:**
- Rebased too many commits
- Included commits you didn't want to change

**Solution:**
```bash
# Abort rebase if still in progress
git rebase --abort

# If rebase completed, use reflog
git reflog
# Find the commit before rebase (HEAD@{n})

git reset --hard HEAD@{5}  # Before rebase

# Try again with correct number
git rebase -i HEAD~3  # Not HEAD~10
```

**Prevention:**
- Count commits carefully: `git log --oneline -10`
- Use commit SHAs instead of HEAD~N
- Create backup branch first

---

### Issue: "Force push rejected"

**Symptoms:**
```
! [rejected]        feature/my-branch -> feature/my-branch (fetch first)
error: failed to push some refs
```

**Solution:**
```bash
# Check what's on remote
git fetch origin
git log origin/feature/my-branch..HEAD

# If you have newer commits remote doesn't have
git pull --rebase origin feature/my-branch
git push origin feature/my-branch

# If you REALLY want to overwrite
git push --force-with-lease origin feature/my-branch

# If --force-with-lease fails, someone else pushed
git fetch origin
git rebase origin/feature/my-branch
git push --force-with-lease origin feature/my-branch
```

**Prevention:**
- Always fetch before force pushing
- Coordinate with team on shared branches
- Use --force-with-lease instead of --force

---

## Examples

### Example 1: Fix Typo in Last Commit

**Context:**
Just committed with typo in message.

**Execution:**
```bash
# Current message (typo)
git log --oneline -1
# abc1234 fix: Reolve login eror

# Fix message
git commit --amend -m "fix: Resolve login error"

# Verify
git log --oneline -1
# def5678 fix: Resolve login error

# Push (if needed)
git push --force-with-lease origin feature/auth
```

**Result:**
- Message corrected in seconds
- Clean commit history

---

### Example 2: Add Missing Ticket Number

**Context:**
Committed without issue reference.

**Execution:**
```bash
# Current message
git log --oneline -1
# abc1234 feat: Add user profile endpoints

# Add ticket reference
git commit --amend -m "feat: Add user profile endpoints

Implements /api/users/:id/profile GET and PUT endpoints.

Closes #423"

# Push if needed
git push --force-with-lease origin feature/api
```

**Result:**
- Ticket automatically linked
- Better traceability

---

### Example 3: Improve Multiple Vague Messages

**Context:**
3 commits with messages like "WIP", "updates", "fix".

**Execution:**
```bash
# View commits
git log --oneline -3
# abc1234 fix
# def5678 updates  
# ghi9012 WIP

# Interactive rebase
git rebase -i HEAD~3

# Editor shows:
pick ghi9012 WIP
pick def5678 updates
pick abc1234 fix

# Change all to 'reword':
reword ghi9012 WIP
reword def5678 updates
reword abc1234 fix

# For each, git opens editor with better messages:
feat: Add user authentication API

test: Add authentication test coverage

fix: Resolve JWT token expiration bug

# Push
git push --force-with-lease origin feature/auth
```

**Result:**
- Clear, descriptive messages
- Professional commit history
- Easy to understand changes

---

## Best Practices

### DO:
✅ Write messages in imperative mood ("Add feature" not "Added")  
✅ Be specific about what changed  
✅ Reference tickets/issues when applicable  
✅ Explain WHY, not just WHAT  
✅ Keep first line under 72 characters  
✅ Use body for additional details  
✅ Follow team conventions  
✅ Use --force-with-lease over --force  
✅ Communicate before force pushing  
✅ Test corrections before pushing  

### DON'T:
❌ Use vague messages ("fix stuff", "updates")  
❌ Force push to main/shared branches  
❌ Rewrite history after merge  
❌ Include code in commit message  
❌ Use past tense  
❌ End subject with period  
❌ Make subject too long  
❌ Skip commit message entirely  
❌ Force push without coordination  
❌ Forget to verify after correction  

---

## Related Workflows

**Prerequisites:**
- **version-control/branch_strategy.md** - Understanding branching workflow

**Next Steps:**
- **development/code_review_checklist.md** - Reviewing commit messages in PRs
- **version-control/merge_conflict_resolution.md** - Handling merge conflicts

**Related:**
- **development/pre_commit_hooks.md** - Automating commit message validation
- **project-management/knowledge_transfer.md** - Documenting standards for new team members

---

## Tags
`version-control` `git` `commit-messages` `best-practices` `conventional-commits`
