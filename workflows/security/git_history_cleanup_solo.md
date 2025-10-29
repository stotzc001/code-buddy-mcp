# Git History Cleanup for Exposed Secrets

**ID:** sec-002  
**Category:** Security  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 45-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive workflow for removing sensitive data (secrets, credentials, PII, large files) from git repository history permanently.

**Why:** Once committed to git, data exists in history forever unless explicitly removed. Exposed secrets in history create persistent security vulnerabilities, and large files bloat repository size.

**When to use:**
- Secret accidentally committed to git history
- Credentials found in old commits during security audit
- Need to remove PII (Personally Identifiable Information)
- Large files accidentally committed causing repo bloat
- Preparing repository for open-sourcing
- Compliance requirement to purge sensitive data

---

## Prerequisites

**Required:**
- [ ] Git repository with admin access
- [ ] Permission to force-push and rewrite history
- [ ] Backup of repository (clone or archive)
- [ ] Communication plan for team members
- [ ] List of items to remove

**Tools to install:**
```bash
# Option 1: BFG Repo-Cleaner (Recommended - Fast & Safe)
# Mac
brew install bfg

# Linux
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
alias bfg='java -jar /path/to/bfg-1.14.0.jar'

# Windows
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
# Run with: java -jar bfg.jar

# Option 2: git-filter-repo (Most Powerful)
pip install git-filter-repo

# Option 3: Built-in git filter-branch (Slowest - Use as last resort)
# Already included with git

# Verify installation
bfg --version
git-filter-repo --version
```

**Check before starting:**
```bash
# Verify you have a clean working directory
git status

# Verify you can force push
git push --force --dry-run

# Create backup
git clone --mirror git@github.com:org/repo.git repo-backup-$(date +%Y%m%d).git
cd repo-backup-$(date +%Y%m%d).git
git bundle create ../backup-bundle.bundle --all
cd ..
```

---

## Implementation Steps

### Step 1: Create Complete Backup

**What:** Create multiple backups before rewriting history to ensure recovery is possible.

**How:**
Multiple backup strategies provide safety net for this destructive operation.

**Backup Commands:**
```bash
# 1. Create mirror clone (includes all refs)
git clone --mirror git@github.com:company/repo.git repo-backup-mirror
cd repo-backup-mirror
git bundle create ../repo-full-backup-$(date +%Y%m%d).bundle --all
cd ..

# 2. Create regular clone with all branches
git clone git@github.com:company/repo.git repo-backup-regular
cd repo-backup-regular
git fetch --all
git branch -r | grep -v '\->' | while read remote; do 
  git branch --track "${remote#origin/}" "$remote"
done
cd ..

# 3. Archive to tarball
tar -czf repo-backup-$(date +%Y%m%d).tar.gz repo-backup-regular/

# 4. Verify backup integrity
cd repo-backup-mirror
git fsck --full
cd ..
```

**Documentation:**
```bash
# Document current state
cat > cleanup-plan-$(date +%Y%m%d).md << 'EOF'
# Git History Cleanup Plan

**Date:** $(date)
**Repository:** company/repo
**Reason:** Remove exposed API key

## Items to Remove
- [ ] API key: sk_live_YOUR_KEY_HERE (committed in abc123def)
- [ ] Database password in config/database.yml
- [ ] Large file: assets/video.mp4 (250MB)

## Backups Created
- Mirror clone: repo-backup-mirror/
- Bundle: repo-full-backup-20251026.bundle
- Tarball: repo-backup-20251026.tar.gz

## Team Members to Notify (12 people)
- @alice, @bob, @charlie, @diana, @eve, @frank
- @grace, @henry, @iris, @jack, @karen, @leo

## Timeline
- Backup: 2025-10-26 14:00 UTC
- Cleanup: 2025-10-26 14:30 UTC
- Verification: 2025-10-26 15:00 UTC
- Force push: 2025-10-26 15:30 UTC
- Team notification: 2025-10-26 15:35 UTC
EOF
```

**Verification:**
- [ ] Mirror clone created successfully
- [ ] Bundle file created and verified
- [ ] Tarball created
- [ ] All backups stored in safe location (not just local)
- [ ] Backup integrity verified with `git fsck`
- [ ] Cleanup plan documented

**If This Fails:**
→ If disk space insufficient, use external drive or cloud storage  
→ If clone fails, check network connectivity and credentials  
→ If bundle creation fails, ensure git version is recent (2.x+)  

---

### Step 2: Identify All Instances

**What:** Find every occurrence of the sensitive data across all branches, tags, and commits.

**How:**
Thorough search ensures no instances are missed during cleanup.

**Search Commands:**
```bash
# Search for string in all commits
git log -S "api-key-to-remove" --source --all --oneline

# More detailed view
git log -S "api-key-to-remove" --source --all --patch

# Find in which files
git log --all --full-history --source -- "**/config.yml" "**/secrets.json"

# Search across all branches with context
git grep "api-key-to-remove" $(git rev-list --all)

# Find large files in history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  tail -20 | \
  numfmt --field=2 --to=iec-i --suffix=B --padding=7

# List files larger than 10MB
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '$1 == "blob" && $3 > 10485760 {print $3, $4}' | \
  numfmt --field=1 --to=iec-i
```

**Create Inventory:**
```bash
# Document all findings
cat > items-to-remove.txt << 'EOF'
# Secrets to remove (BFG format)
sk_live_YOUR_KEY_HERE==>***REMOVED***
db-password-prod-2024==>***REMOVED***
AKIAIOSFODNN7EXAMPLE==>***REMOVED***

# Regex patterns (git-filter-repo format)
regex:sk_live_[a-zA-Z0-9]{24}==>***REMOVED***
regex:AKIA[0-9A-Z]{16}==>***REMOVED***
regex:password["\s]*[:=]["\s]*[^\s"]+==>***REMOVED***
EOF

# Files to delete entirely
cat > files-to-delete.txt << 'EOF'
config/production.yml
credentials.json
assets/large-video.mp4
data/dump.sql
.env
.env.production
EOF

# Folders to delete
cat > folders-to-delete.txt << 'EOF'
backups/
node_modules/
.idea/
EOF
```

**Verification:**
- [ ] All occurrences of sensitive data found
- [ ] Large files identified (if applicable)
- [ ] Files and folders to delete listed
- [ ] Regex patterns tested (if using)
- [ ] Team reviewed list for completeness

**If This Fails:**
→ If grep returns too many results, use more specific patterns  
→ If uncertain about content, manually inspect with `git show <commit>:<file>`  
→ If secret might be encoded, search for base64/hex variations  

---

### Step 3: Choose Cleanup Method

**What:** Select the appropriate tool based on repository size, complexity, and cleanup requirements.

**How:**
Different tools have different strengths - choose based on your specific needs.

**Decision Matrix:**

| Tool | Best For | Speed | Safety | Complexity |
|------|----------|-------|--------|------------|
| **BFG Repo-Cleaner** | Simple text replacement, file deletion | ⚡⚡⚡ Very Fast | ✅ Safe | ⭐ Easy |
| **git-filter-repo** | Complex patterns, folder restructuring | ⚡⚡ Fast | ✅ Safe | ⭐⭐ Moderate |
| **git filter-branch** | Edge cases, maximum control | ⚡ Slow | ⚠️ Risky | ⭐⭐⭐ Complex |

**Recommendation:**
1. Use **BFG** for 90% of cases (secrets, large files, simple deletions)
2. Use **git-filter-repo** for complex transformations or folder moves
3. Use **git filter-branch** only as absolute last resort

**Test on Clone First:**
```bash
# ALWAYS test on a fresh clone before running on main repository
git clone git@github.com:company/repo.git test-cleanup
cd test-cleanup

# Run cleanup method here (see next steps)

# Verify results
git log --all --oneline | head -20
git grep "secret-string-to-remove" $(git rev-list --all) || echo "✅ Not found"

# If satisfied, proceed to main cleanup
```

**Verification:**
- [ ] Cleanup method selected
- [ ] Test clone created
- [ ] Team aware of upcoming force-push
- [ ] Maintenance window scheduled (if needed)

**If This Fails:**
→ If unsure which tool to use, start with BFG  
→ If BFG doesn't handle your case, try git-filter-repo  
→ If both fail, seek help before using filter-branch  

---

### Step 4: Execute Cleanup (BFG Method)

**What:** Use BFG Repo-Cleaner to remove secrets and unwanted files from history.

**How:**
BFG is the safest and fastest tool for most cleanup operations.

**Setup:**
```bash
# Clone a fresh bare/mirror repository for cleanup
git clone --mirror git@github.com:company/repo.git repo-cleanup.git
cd repo-cleanup.git
```

**Remove Secrets/Text:**
```bash
# Option A: Replace specific strings
bfg --replace-text ../items-to-remove.txt

# items-to-remove.txt format:
# OLD_SECRET==>REMOVED
# password123==>***REMOVED***
# regex:api_key\s*=\s*['"]([^'"]+)['"]==>api_key="***REMOVED***"

# Option B: Remove passwords globally (any password= lines)
bfg --replace-text passwords.txt

# passwords.txt:
# regex:password\s*=\s*[^\s]+==>password=***REMOVED***
```

**Remove Files:**
```bash
# Delete specific files by name
bfg --delete-files credentials.json

# Delete all files matching pattern
bfg --delete-files '*.{log,tmp,cache}'

# Delete files larger than 10M
bfg --strip-blobs-bigger-than 10M

# Delete entire folders
bfg --delete-folders node_modules
bfg --delete-folders .idea
```

**Remove by Date:**
```bash
# Keep only commits from last year
bfg --delete-files '*' --no-blob-protection --only-refs refs/heads/old-branch
```

**Verification:**
```bash
# Check what BFG found and replaced
# BFG outputs detailed report showing:
# - Protected commits (HEAD): X
# - Commits: Y
# - Protected blobs: Z
# - Updated references: N

# Manually verify a few commits
git log --all --oneline | head -10
git show <commit-hash>

# Search to verify removal
git grep "secret-string" $(git rev-list --all) || echo "✅ Successfully removed"
```

**Verification:**
- [ ] BFG completed without errors
- [ ] Protected commits (HEAD) were not modified
- [ ] Spot-check confirms secrets removed
- [ ] Repository size reduced (if removing large files)
- [ ] All branches/tags cleaned

**If This Fails:**
→ If BFG refuses to delete, add `--no-blob-protection` (use cautiously)  
→ If secret remains in HEAD, first commit a clean version then re-run BFG  
→ If pattern doesn't match, verify syntax in items-to-remove.txt  

---

### Step 5: Execute Cleanup (git-filter-repo Method)

**What:** Alternative method using git-filter-repo for more complex cleanup scenarios.

**How:**
git-filter-repo provides more powerful filtering and transformation capabilities.

**Setup:**
```bash
# Clone fresh copy (NOT --mirror for filter-repo)
git clone git@github.com:company/repo.git repo-cleanup-filter
cd repo-cleanup-filter
```

**Replace Text:**
```bash
# Replace literal strings
git filter-repo --replace-text ../replacements.txt

# replacements.txt format:
# literal:old-secret==>REMOVED
# literal:password123==>***REDACTED***
# regex:api[_-]key\s*=\s*['"].*?['"]==>api_key="***REMOVED***"
```

**Remove Files:**
```bash
# Remove specific file from all history
git filter-repo --path credentials.json --invert-paths

# Remove multiple files
git filter-repo --path-glob '*.log' --invert-paths
git filter-repo --path-glob '*.tmp' --invert-paths

# Remove entire directory
git filter-repo --path backups/ --invert-paths
```

**Advanced Filtering:**
```bash
# Remove files larger than 10MB
git filter-repo --strip-blobs-bigger-than 10M

# Keep only specific paths
git filter-repo --path src/ --path docs/

# Rename/move files
git filter-repo --path-rename old-dir/:new-dir/

# Custom Python callback for complex logic
cat > filter-script.py << 'EOF'
import re

def blob_filter(blob, metadata):
    # Remove secrets matching pattern
    blob.data = re.sub(
        rb'sk_live_[a-zA-Z0-9]{24}',
        b'***REMOVED***',
        blob.data
    )
    
def filename_filter(filename):
    # Skip sensitive files
    if filename.endswith(b'.env') or b'secret' in filename:
        return b''  # Delete file
    return filename
EOF

git filter-repo --blob-callback 'from filter-script import blob_filter; blob_filter(blob, metadata)' \
                --filename-callback 'from filter-script import filename_filter; filename_filter(filename)'
```

**Verification:**
```bash
# Check results
git log --all --oneline | head -20
git diff-tree --no-commit-id --name-only -r HEAD

# Verify secrets removed
git grep "secret-pattern" $(git rev-list --all) || echo "✅ Removed"

# Check repository size
du -sh .git
```

**Verification:**
- [ ] filter-repo completed successfully
- [ ] Secrets verified removed from history
- [ ] File structure intact (for files to keep)
- [ ] No unexpected deletions
- [ ] Commit history makes sense

**If This Fails:**
→ If filter-repo errors, ensure fresh clone (not --mirror)  
→ If pattern doesn't match, test regex with `echo "test" | grep -P "pattern"`  
→ If repository corrupted, restore from backup and retry  

---

### Step 6: Cleanup and Optimize Repository

**What:** Complete the cleanup by expiring reflogs and garbage collecting.

**How:**
Remove all traces of deleted data from the repository.

**Cleanup Commands:**
```bash
# If using BFG (in mirror/bare repo)
cd repo-cleanup.git

# Expire all reflog entries immediately
git reflog expire --expire=now --all

# Run aggressive garbage collection
git gc --prune=now --aggressive

# Verify repository integrity
git fsck --full --strict

# If using git-filter-repo (already done automatically)
# filter-repo handles cleanup automatically

# Check final size
du -sh .

# Compare with original
echo "Original size: $(du -sh ../repo-backup-mirror | cut -f1)"
echo "New size: $(du -sh . | cut -f1)"
```

**Verify Cleanup:**
```bash
# Ensure no reflog references remain
git reflog show

# Check that unreachable objects are pruned
git fsck --unreachable

# Final search to confirm removal
git grep -i "secret-string" $(git rev-list --all) || echo "✅ Confirmed removed"
git grep -i "password" $(git rev-list --all) || echo "✅ Confirmed removed"

# List all remaining large objects
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '$1 == "blob" && $3 > 1048576' | \
  sort -k3 -n | \
  tail -20
```

**Verification:**
- [ ] Reflog expired
- [ ] Garbage collection completed
- [ ] Repository integrity verified
- [ ] Size reduction confirmed (if removing files)
- [ ] Final search confirms secrets removed
- [ ] No unreachable objects with sensitive data

**If This Fails:**
→ If `git gc` fails, try without `--aggressive` first  
→ If fsck reports corruption, restore backup and investigate  
→ If secrets still found, re-run cleanup steps  

---

### Step 7: Force Push to Remote

**What:** Push the cleaned history to remote repository, overwriting the old history.

**How:**
Carefully coordinate with team to minimize disruption.

**Pre-Push Checklist:**
```bash
# 1. Verify local cleanup succeeded
git log --all --oneline | head -20
git grep "secret-to-remove" $(git rev-list --all) || echo "✅ Clean"

# 2. Notify team BEFORE pushing
cat > team-notification.md << 'EOF'
🚨 URGENT: Repository History Rewrite Scheduled 🚨

**Repository:** company/repo
**Time:** 2025-10-26 15:30 UTC (in 30 minutes)
**Duration:** ~15 minutes

**Action Required:**
Before 15:30 UTC:
1. Commit and push all your changes
2. Wait for confirmation email

After confirmation email:
1. Delete local repository: rm -rf repo/
2. Fresh clone: git clone git@github.com:company/repo.git
3. Re-apply any local changes from stash/backup

**Why:** Removing exposed secrets from git history

**Questions:** #security-incidents or security@company.com
EOF

# 3. Optional: Lock repository temporarily
gh repo edit --enable-security-and-analysis

# 4. Disable branch protection temporarily (if needed)
gh api repos/:owner/:repo/branches/main/protection -X DELETE
```

**Force Push:**
```bash
# From cleaned mirror repository (BFG)
cd repo-cleanup.git
git push origin --force --all
git push origin --force --tags

# Verify push succeeded
git ls-remote origin

# Re-enable branch protection
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -f required_status_checks='{"strict":true,"contexts":[]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true}'
```

**Post-Push Notification:**
```bash
cat > completion-notification.md << 'EOF'
✅ Repository History Cleanup Complete

**Status:** COMPLETE
**Repository:** company/repo
**Time:** 2025-10-26 15:45 UTC

**IMMEDIATE ACTION REQUIRED:**

1. Delete your local repository:
   rm -rf /path/to/repo

2. Fresh clone from GitHub:
   git clone git@github.com:company/repo.git
   cd repo

3. If you had local changes, re-apply them now

**DO NOT:**
❌ Try to merge old branches
❌ Force push old commits
❌ Keep old local copies

**Verification:**
After cloning, this should return nothing:
git grep "old-secret-string" $(git rev-list --all)

**Questions?** Reply to this message or #engineering-support
EOF
```

**Verification:**
- [ ] Force push completed successfully
- [ ] All branches pushed
- [ ] All tags pushed
- [ ] Remote repository verified clean
- [ ] Team notified with clear instructions
- [ ] Branch protection re-enabled

**If This Fails:**
→ If force push rejected, verify you have admin permissions  
→ If branch protection blocks push, temporarily disable it  
→ If push times out, increase git buffer: `git config http.postBuffer 524288000`  
→ If partial push, re-push missing refs: `git push origin --force <ref>`  

---

### Step 8: Verify and Communicate

**What:** Ensure cleanup was successful and all team members have updated their local repositories.

**How:**
Systematic verification and follow-up with team members.

**Verification Script:**
```bash
#!/bin/bash
# verify-cleanup.sh

REPO_URL="git@github.com:company/repo.git"
TEMP_DIR="/tmp/verify-cleanup-$(date +%s)"
SECRET_PATTERN="sk_live_YOUR_KEY_HERE"

echo "🔍 Verifying repository cleanup..."

# Fresh clone
git clone "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"

# Check all branches
echo "Checking all branches..."
for branch in $(git branch -r | grep -v HEAD); do
  git checkout -q "${branch#origin/}"
  if git grep "$SECRET_PATTERN" 2>/dev/null; then
    echo "❌ Found secret in branch: $branch"
    exit 1
  fi
done

# Check all history
echo "Checking entire history..."
if git grep "$SECRET_PATTERN" $(git rev-list --all) 2>/dev/null; then
  echo "❌ Found secret in history"
  exit 1
fi

# Check repository size
SIZE=$(du -sm .git | cut -f1)
echo "📊 Repository size: ${SIZE}MB"

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo "✅ Verification complete - repository is clean!"
```

**Team Follow-up:**
```bash
# Track team compliance (manual or automated)
cat > team-status.csv << 'EOF'
Name,Email,Status,Verified,Notes
Alice,alice@company.com,Completed,Yes,Confirmed fresh clone
Bob,bob@company.com,Pending,No,Following up
Charlie,charlie@company.com,Completed,Yes,No issues
Diana,diana@company.com,Blocked,No,Permission issue - resolved
EOF

# Send reminder to team members who haven't updated
cat > reminder.md << 'EOF'
🚨 REMINDER: Fresh Repository Clone Required

You have not yet completed the required repository cleanup steps.

**Action Required NOW:**
1. Delete local copy: rm -rf repo/
2. Fresh clone: git clone git@github.com:company/repo.git

This is required for security. Old commits contain exposed secrets.

**Verification:**
git log --oneline | head -5
# Should show recent commit IDs starting with different hashes

**Need help?** #engineering-support
EOF
```

**Monitoring:**
```bash
# Set up monitoring for old commits being pushed back
cat > .github/workflows/monitor-history.yml << 'EOF'
name: Monitor for Old Commits
on: [push]

jobs:
  check-history:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Check for secrets
        run: |
          # Search for patterns that should not exist
          if git grep -E "sk_live_[a-zA-Z0-9]{24}" $(git rev-list --all); then
            echo "❌ Found exposed secret in history!"
            exit 1
          fi
          echo "✅ No secrets found"
EOF
```

**Verification:**
- [ ] Fresh clone verified clean
- [ ] All team members notified
- [ ] At least 80% of team confirmed updated
- [ ] Monitoring in place for old commits
- [ ] Documentation updated
- [ ] Post-mortem scheduled

**If This Fails:**
→ If team members push old commits, immediately notify and have them re-clone  
→ If secrets still found, re-run entire cleanup process  
→ If team resistance, involve management for mandate  

---

## Verification Checklist

After completing this workflow:

- [ ] Complete backup created and verified
- [ ] All instances of sensitive data identified
- [ ] Cleanup method selected and tested
- [ ] Cleanup executed successfully (BFG or git-filter-repo)
- [ ] Repository cleaned and optimized
- [ ] Force push completed
- [ ] Remote repository verified clean
- [ ] Team members notified with clear instructions
- [ ] At least 80% of team has fresh clones
- [ ] Monitoring in place for old commits
- [ ] Documentation updated
- [ ] Incident properly documented

---

## Common Issues & Solutions

### Issue: "BFG won't delete files because they're in HEAD"

**Symptoms:**
- BFG reports "protected commits" and skips cleaning HEAD
- Recent commits still contain sensitive data

**Solution:**
```bash
# First, update HEAD to remove the sensitive data
cd original-repo
git rm credentials.json  # or edit file to remove secret
git commit -m "Remove sensitive data from current commit"
git push

# Now BFG will clean the rest of history
git clone --mirror git@github.com:org/repo.git cleanup.git
cd cleanup.git
bfg --delete-files credentials.json
# HEAD is now clean, so BFG cleans history
```

**Prevention:**
- Always clean current files before running BFG
- Use `--no-blob-protection` only if you understand the risks

---

### Issue: "Repository corruption after cleanup"

**Symptoms:**
- `git fsck` reports errors
- Missing commits or broken references
- Cannot push or pull

**Solution:**
```bash
# Restore from backup
cd /path/to/project
rm -rf repo-cleanup/

# Restore from bundle
git clone repo-full-backup-20251026.bundle repo-cleanup-retry
cd repo-cleanup-retry

# Convert to normal repository
git remote add origin git@github.com:org/repo.git
git fetch origin

# Try cleanup again with more conservative settings
```

**Prevention:**
- Always verify backups before cleanup
- Test on clone first
- Use BFG or git-filter-repo (more reliable than filter-branch)

---

### Issue: "Team member pushed old commits back"

**Symptoms:**
- Secret reappears in history after cleanup
- Repository size increases again
- Old commit IDs visible in history

**Solution:**
```bash
# Immediately notify team
echo "🚨 Old commits detected. DO NOT PULL. Fixing now..."

# Identify who pushed
git log --all --source --pretty=format:'%h %an %ae %s' | grep <old-commit-id>

# Force push clean version again
cd cleaned-repo-backup
git push origin --force --all
git push origin --force --tags

# Contact team member directly
# Have them delete and re-clone
```

**Prevention:**
```bash
# Add pre-receive hook on server (GitHub Enterprise/GitLab)
#!/bin/bash
while read oldrev newrev refname; do
  # Check if any commit contains the old secret
  if git log $oldrev..$newrev | grep -q "old-secret-pattern"; then
    echo "❌ Push rejected: contains exposed secret"
    exit 1
  fi
done
```

---

### Issue: "Cannot force push due to branch protection"

**Symptoms:**
- Push rejected by GitHub/GitLab
- "protected branch" error
- Missing admin permissions

**Solution:**
```bash
# Option 1: Temporarily disable protection
gh api repos/:owner/:repo/branches/main/protection -X DELETE

# Perform force push
git push origin --force --all

# Re-enable protection
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -f required_status_checks='{"strict":true}' \
  -f enforce_admins=true

# Option 2: Use admin override (GitHub Enterprise)
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -f enforce_admins=false
git push origin --force --all
# Re-enable admin enforcement
```

**Prevention:**
- Document admin override procedure
- Have proper permissions before starting
- Schedule cleanup during maintenance window

---

### Issue: "Cleanup takes too long (hours)"

**Symptoms:**
- BFG or filter-repo running for hours
- Very large repository (>1GB)
- Many commits (>100k)

**Solution:**
```bash
# Option 1: Use BFG (fastest)
# BFG is optimized for large repos
bfg --delete-files credentials.json --no-blob-protection

# Option 2: Limit scope if possible
git filter-repo --path src/ --path docs/  # Only clean specific paths

# Option 3: Shallow clone first (if old history not needed)
git clone --depth 1000 git@github.com:org/repo.git
# Then clean and force push

# Option 4: Clean in stages
# Clean main branch first, then others
git filter-repo --refs refs/heads/main
# Then clean other branches
```

**Prevention:**
- Run cleanup during off-hours
- Use BFG for large repositories
- Consider partial cleanup if full history not required

---

## Examples

### Example 1: Remove AWS Key from Public Repository

**Context:**
AWS access key accidentally committed to public GitHub repository 6 months ago. Need to remove from entire history.

**Execution:**
```bash
# 1. Create backup
git clone --mirror git@github.com:company/repo.git backup.git

# 2. Fresh mirror clone for cleanup
git clone --mirror git@github.com:company/repo.git cleanup.git
cd cleanup.git

# 3. Create replacement file
echo "AKIAIOSFODNN7EXAMPLE==>***REMOVED***" > secrets.txt

# 4. Run BFG
bfg --replace-text secrets.txt

# 5. Cleanup
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 6. Verify
git grep "AKIAIOSFODNN7EXAMPLE" $(git rev-list --all) || echo "✅ Removed"

# 7. Force push
git push origin --force --all
git push origin --force --tags
```

**Result:**
- Cleaned in 15 minutes
- Repository size reduced by 5MB
- All 1,247 commits cleaned
- Zero occurrences in history verified

---

### Example 2: Remove Large Video File (250MB)

**Context:**
Developer accidentally committed large video file causing slow clones. Need to remove to reduce repository size.

**Execution:**
```bash
# 1. Identify large files
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '$1 == "blob" && $3 > 10485760'

# Found: assets/demo-video.mp4 (262144000 bytes)

# 2. Clone and clean
git clone --mirror git@github.com:company/repo.git cleanup.git
cd cleanup.git
bfg --delete-files demo-video.mp4

# 3. Cleanup and verify size
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "Before: 800MB"
du -sh .
echo "After: 550MB"

# 4. Push
git push origin --force --all
```

**Result:**
- Repository size reduced from 800MB to 550MB
- Clone time reduced from 5 minutes to 2 minutes
- Team clones 63% faster

---

### Example 3: Remove Multiple Secrets with Patterns

**Context:**
Security audit found multiple API keys, passwords, and tokens scattered across history. Need comprehensive cleanup.

**Execution:**
```bash
# 1. Create comprehensive replacement file
cat > all-secrets.txt << 'EOF'
# Stripe keys
literal:sk_live_YOUR_KEY_HERE==>***REMOVED_STRIPE_KEY***
regex:sk_live_[a-zA-Z0-9]{24,}==>***REMOVED_STRIPE_KEY***

# AWS keys
regex:AKIA[0-9A-Z]{16}==>***REMOVED_AWS_KEY***

# Passwords
regex:password\s*[:=]\s*['"]([^'"]+)['"]==>password: "***REMOVED***"
regex:DB_PASSWORD\s*=\s*[^\s]+==>DB_PASSWORD=***REMOVED***

# API tokens
regex:Bearer\s+[a-zA-Z0-9\-_.]+={0,2}==>Bearer ***REMOVED***

# Generic secrets
literal:my-secret-api-key-12345==>***REMOVED***
EOF

# 2. Clean with git-filter-repo
git clone git@github.com:company/repo.git cleanup
cd cleanup
git filter-repo --replace-text ../all-secrets.txt --force

# 3. Verify comprehensively
git grep -E "(sk_live|AKIA|password.*=|Bearer)" $(git rev-list --all) || echo "✅ Clean"

# 4. Push
git remote add origin git@github.com:company/repo.git
git push origin --force --all
```

**Result:**
- 47 secrets removed across 234 commits
- 8 different secret types cleaned
- Comprehensive regex patterns prevented future similar leaks

---

## Best Practices

### DO:
✅ Create multiple backups before starting  
✅ Test cleanup on fresh clone first  
✅ Use BFG for 90% of cases (fastest and safest)  
✅ Notify entire team before force-pushing  
✅ Verify cleanup succeeded before declaring complete  
✅ Document exactly what was removed and why  
✅ Require team to delete and re-clone  
✅ Monitor for old commits being pushed back  
✅ Schedule during maintenance window if possible  
✅ Keep backup for at least 90 days after cleanup  

### DON'T:
❌ Skip creating backups  
❌ Use git filter-branch unless necessary  
❌ Force push without team notification  
❌ Allow team to merge old branches  
❌ Assume cleanup worked without verification  
❌ Delete backups immediately after cleanup  
❌ Clean production repository directly (use clone)  
❌ Forget to rotate exposed secrets first  
❌ Skip the garbage collection step  
❌ Re-use exposed secrets after removal  

---

## Related Workflows

**Prerequisites:**
- **secret_incident_solo.md** - Rotate exposed secrets BEFORE cleaning history
- **version-control/branch_strategy.md** - Understanding branching for cleanup coordination

**Next Steps:**
- **code_buddy_secret_rules.md** - Prevent future secret exposure
- **development/pre_commit_hooks.md** - Automated secret detection

**Related:**
- **devops/backup_disaster_recovery.md** - Repository backup strategies

---

## Tags
`security` `git` `secrets` `cleanup` `history-rewriting` `bfg` `sensitive-data`
