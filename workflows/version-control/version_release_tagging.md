# Version Release Tagging
**ID:** ver-004  
**Category:** Version Control  
**Complexity:** Intermediate  
**Estimated Time:** 30-45 minutes

## Overview

**What:** Systematic process for creating software releases with proper version numbers, git tags, changelogs, and release artifacts following semantic versioning principles.

**Why:** Proper version tagging enables tracking changes, rolling back deployments, managing dependencies, and communicating changes to users. It's essential for professional software development and deployment.

**When to use:**
- Creating new software release
- After completing sprint/milestone
- Deploying to production
- Publishing packages to PyPI/npm
- Creating stable snapshots for deployment
- Before major feature launches

---

## Prerequisites

**Required:**
- [ ] Git repository with clean working tree
- [ ] All changes merged to release branch (main/master)
- [ ] All tests passing in CI
- [ ] Code reviewed and approved
- [ ] Documentation updated

**Required Tools:**
- [ ] Git installed and configured
- [ ] Access to push tags to remote repository
- [ ] GitHub/GitLab access (for releases)
- [ ] Python packaging tools (if publishing to PyPI)

**Decisions Made:**
- [ ] Version number determined (X.Y.Z)
- [ ] Release scope defined (features, fixes)
- [ ] Breaking changes identified
- [ ] Target environment (staging, production)

**Check before starting:**
```bash
# Verify clean git state
git status  # Should show "nothing to commit, working tree clean"

# Verify on correct branch
git branch --show-current  # Should show main or release branch

# Verify latest code
git pull origin main

# Verify all tests pass
pytest

# Verify CI is passing
# Check GitHub Actions / GitLab CI status
```

---

## Implementation Steps

### Step 1: Determine Version Number

**What:** Choose appropriate version number following semantic versioning (SemVer) principles.

**How:** Analyze changes since last release and apply SemVer rules.

**Semantic Versioning format: MAJOR.MINOR.PATCH**

```
Given a version number MAJOR.MINOR.PATCH:

MAJOR: Incompatible API changes (breaking changes)
MINOR: New functionality (backward-compatible)
PATCH: Bug fixes (backward-compatible)
```

**Check current version:**
```bash
# From git tags
git describe --tags --abbrev=0
# Output: v1.2.3

# From pyproject.toml
grep version pyproject.toml
# Output: version = "1.2.3"

# From package
python -c "import mypackage; print(mypackage.__version__)"

# From CHANGELOG
head -20 CHANGELOG.md
```

**Analyze changes since last release:**
```bash
# List commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Categorize commits
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s" | grep -i "^feat:"
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s" | grep -i "^fix:"
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s" | grep -i "^BREAKING"

# Check for breaking changes
git log $(git describe --tags --abbrev=0)..HEAD --grep="BREAKING CHANGE"
```

**Decision tree for version number:**
```bash
# Current version: 1.2.3

# If BREAKING CHANGES found:
# New version: 2.0.0 (increment MAJOR, reset MINOR and PATCH)

# If only new features (feat: commits):
# New version: 1.3.0 (increment MINOR, reset PATCH)

# If only bug fixes (fix: commits):
# New version: 1.2.4 (increment PATCH)

# If pre-release/beta:
# New version: 1.3.0-beta.1 or 1.3.0-rc.1
```

**Examples:**
```bash
# Example 1: Bug fix release
Current: 1.2.3
Changes: Only fix: commits
New: 1.2.4

# Example 2: Feature release
Current: 1.2.3
Changes: feat: and fix: commits
New: 1.3.0

# Example 3: Breaking change
Current: 1.2.3
Changes: BREAKING CHANGE in API
New: 2.0.0

# Example 4: Pre-release
Current: 1.2.3
Changes: New features, not ready for stable
New: 1.3.0-beta.1
```

**Set version variable:**
```bash
# Set new version
NEW_VERSION="1.3.0"

# Verify format
echo $NEW_VERSION | grep -E '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$'

# Create tag name
TAG_NAME="v${NEW_VERSION}"
echo $TAG_NAME  # v1.3.0
```

**Verification:**
- [ ] Version number follows SemVer format
- [ ] Version reflects changes (major/minor/patch)
- [ ] Breaking changes result in major version bump
- [ ] Version higher than current version

**If This Fails:**
→ **No git tags**: Start from v0.1.0 or v1.0.0
→ **Unclear changes**: Review commit messages more carefully
→ **Multiple breaking changes**: Still bump major version once

---

### Step 2: Update Version in Code

**What:** Update version number in all project files.

**How:** Modify version strings in package metadata, documentation, and configuration.

**Update pyproject.toml:**
```bash
# Using sed (Linux/Mac)
sed -i '' "s/version = \".*\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Or manually edit
nano pyproject.toml
# Change: version = "1.2.3" → version = "1.3.0"
```

**Update __init__.py:**
```python
# src/mypackage/__init__.py
__version__ = "1.3.0"
```

```bash
# Using sed
sed -i '' "s/__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" src/mypackage/__init__.py
```

**Update setup.py (if using):**
```python
# setup.py
setup(
    name="mypackage",
    version="1.3.0",  # Update this
    # ...
)
```

**Update documentation:**
```bash
# Update README.md if it mentions version
sed -i '' "s/Version: [0-9.]\+/Version: ${NEW_VERSION}/" README.md

# Update docs/index.md
sed -i '' "s/version [0-9.]\+/version ${NEW_VERSION}/" docs/index.md
```

**Update Dockerfile (if applicable):**
```dockerfile
# Dockerfile
LABEL version="1.3.0"
ENV APP_VERSION="1.3.0"
```

**Update Kubernetes manifests (if applicable):**
```yaml
# k8s/deployment.yaml
metadata:
  labels:
    version: "1.3.0"
spec:
  template:
    metadata:
      labels:
        version: "1.3.0"
```

**Verify version changes:**
```bash
# Check all files updated
grep -r "1.2.3" .  # Should not find old version (except CHANGELOG)

# Verify new version
grep -r "${NEW_VERSION}" .

# Test import
python -c "import mypackage; assert mypackage.__version__ == '${NEW_VERSION}'"
```

**Commit version changes:**
```bash
# Stage version updates
git add pyproject.toml src/mypackage/__init__.py README.md docs/

# Commit with conventional message
git commit -m "chore: bump version to ${NEW_VERSION}"

# Do NOT push yet (will push with tag later)
```

**Verification:**
- [ ] pyproject.toml updated
- [ ] __init__.py updated
- [ ] README/docs updated
- [ ] All version references updated
- [ ] Changes committed locally

**If This Fails:**
→ **Multiple version strings**: Create script to update all at once
→ **Version in binary files**: Rebuild/regenerate those files

---

### Step 3: Generate Changelog

**What:** Document all changes since last release in CHANGELOG.md.

**How:** Review commits and categorize changes into features, fixes, and breaking changes.

**Changelog format (Keep a Changelog):**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.3.0] - 2025-10-25

### Added
- New feature descriptions
- New feature descriptions

### Changed
- Changes in existing functionality
- Changes in existing functionality

### Deprecated
- Features that will be removed in future

### Removed
- Features that have been removed

### Fixed
- Bug fixes
- Bug fixes

### Security
- Security vulnerability fixes
```

**Generate changelog from commits:**
```bash
# Get commits since last tag
LAST_TAG=$(git describe --tags --abbrev=0)
git log ${LAST_TAG}..HEAD --pretty=format:"%s" > recent_commits.txt

# Or use git-changelog tool
pip install git-changelog
git-changelog --output CHANGELOG.md --template keepachangelog

# Manual categorization
cat > changelog_${NEW_VERSION}.md << 'EOF'
## [1.3.0] - $(date +%Y-%m-%d)

### Added
- User authentication with OAuth2 support (#123)
- Export functionality for reports (#145)
- Real-time notifications (#167)

### Changed
- Improved database query performance by 40% (#134)
- Updated UI components to use new design system (#156)

### Fixed
- Fixed memory leak in background job processor (#142)
- Resolved timezone handling in date fields (#148)
- Fixed race condition in concurrent requests (#159)

### Security
- Updated requests library to patch CVE-2023-XXXXX (#151)
EOF
```

**Add to CHANGELOG.md:**
```bash
# Read current CHANGELOG
head -50 CHANGELOG.md

# Insert new version at top (after "Unreleased")
# Using script
python << 'EOF'
with open('CHANGELOG.md', 'r') as f:
    content = f.read()

# New changelog entry
new_entry = """
## [1.3.0] - 2025-10-25

### Added
- User authentication with OAuth2 support
- Export functionality for reports

### Changed
- Improved database query performance

### Fixed
- Fixed memory leak in background jobs

"""

# Insert after "## [Unreleased]"
updated = content.replace('## [Unreleased]\n', f'## [Unreleased]\n{new_entry}')

with open('CHANGELOG.md', 'w') as f:
    f.write(updated)
EOF

# Or manually edit
nano CHANGELOG.md
```

**Good changelog practices:**
```markdown
# ✅ GOOD
### Added
- User authentication with OAuth2 support (#123)
  - Supports Google, GitHub, and GitLab providers
  - Includes PKCE for enhanced security
- Real-time notifications via WebSocket (#167)

### Fixed
- Fixed memory leak in background job processor (#142)
  - Jobs now properly release database connections
  - Memory usage reduced by 60%

# ❌ BAD
### Added
- Added stuff
- Fixed things
- Updated code

### Fixed
- Bug fixes
```

**Commit changelog:**
```bash
# Stage changelog
git add CHANGELOG.md

# Commit
git commit -m "docs: update changelog for ${NEW_VERSION}"
```

**Verification:**
- [ ] CHANGELOG.md updated with new version
- [ ] All significant changes documented
- [ ] Changes categorized appropriately
- [ ] PR/issue references included
- [ ] Release date added
- [ ] Breaking changes highlighted

**If This Fails:**
→ **Missing commits**: Review git log more thoroughly
→ **Unclear categories**: Ask team for clarification

---

### Step 4: Create Git Tag

**What:** Create annotated git tag for the release version.

**How:** Use git tag with descriptive message.

**Create annotated tag:**
```bash
# Annotated tag (recommended - includes metadata)
git tag -a ${TAG_NAME} -m "Release ${NEW_VERSION}

Features:
- User authentication with OAuth2
- Export functionality for reports
- Real-time notifications

Improvements:
- 40% faster database queries
- Updated UI design system

Bug Fixes:
- Fixed memory leak in background jobs
- Resolved timezone issues
- Fixed race condition

Security:
- Updated requests library (CVE fix)"

# Lightweight tag (not recommended for releases)
# git tag ${TAG_NAME}

# Verify tag created
git tag -l ${TAG_NAME}

# View tag details
git show ${TAG_NAME}
```

**Sign tag (recommended for security):**
```bash
# Configure GPG signing
git config user.signingkey YOUR_GPG_KEY_ID

# Create signed tag
git tag -s ${TAG_NAME} -m "Release ${NEW_VERSION}

[Include release notes here]"

# Verify signature
git tag -v ${TAG_NAME}
```

**Tag naming conventions:**
```bash
# Standard formats:
v1.3.0        # Recommended (with v prefix)
1.3.0         # Also common (without v prefix)

# Pre-releases:
v1.3.0-beta.1
v1.3.0-rc.1
v1.3.0-alpha.1

# Build metadata:
v1.3.0+20251025
v1.3.0+build.123
```

**Verification:**
- [ ] Tag created locally
- [ ] Tag is annotated (not lightweight)
- [ ] Tag message includes release notes
- [ ] Tag name follows convention (v1.3.0)
- [ ] Tag points to correct commit

**If This Fails:**
→ **Tag already exists**: Delete with `git tag -d ${TAG_NAME}` and recreate
→ **Wrong commit**: Specify commit: `git tag -a ${TAG_NAME} commit_hash`

---

### Step 5: Push Tag to Remote

**What:** Push the tag to GitHub/GitLab to make it available to the team.

**How:** Push tag and verify it appears on remote.

**Push tag:**
```bash
# Push specific tag
git push origin ${TAG_NAME}

# Or push all tags
git push origin --tags

# Push commits and tag together
git push origin main
git push origin ${TAG_NAME}

# Verify on remote
git ls-remote --tags origin
```

**Check on GitHub/GitLab:**
```bash
# Using GitHub CLI
gh release list

# Or visit web interface
# GitHub: https://github.com/user/repo/tags
# GitLab: https://gitlab.com/user/repo/-/tags

# Verify tag is visible
```

**Create GitHub/GitLab Release:**
```bash
# Using GitHub CLI (recommended)
gh release create ${TAG_NAME} \
  --title "Release ${NEW_VERSION}" \
  --notes-file <(git tag -l --format='%(contents)' ${TAG_NAME})

# Or with auto-generated notes
gh release create ${TAG_NAME} \
  --title "Release ${NEW_VERSION}" \
  --generate-notes

# Manual web interface method:
# 1. Go to repository → Releases → Draft new release
# 2. Choose tag: v1.3.0
# 3. Enter release title: "Release 1.3.0"
# 4. Copy changelog content to description
# 5. Upload artifacts (if any)
# 6. Publish release
```

**Using GitLab:**
```bash
# Using GitLab CLI
glab release create ${TAG_NAME} \
  --name "Release ${NEW_VERSION}" \
  --notes "$(git tag -l --format='%(contents)' ${TAG_NAME})"
```

**Verification:**
- [ ] Tag pushed to remote
- [ ] Tag visible on GitHub/GitLab
- [ ] Release created (GitHub/GitLab)
- [ ] Release notes populated
- [ ] Release is public/visible

**If This Fails:**
→ **Push rejected**: Ensure you have write access to repository
→ **Tag already exists remotely**: Delete remote tag first (with team approval)

---

### Step 6: Build and Publish Release Artifacts

**What:** Build distribution packages and publish to package registries.

**How:** Build wheel/sdist packages and upload to PyPI or other registries.

**Build Python package:**
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Install build tools
pip install build twine

# Build package
python -m build

# Verify build
ls -lh dist/
# Should see:
# mypackage-1.3.0-py3-none-any.whl
# mypackage-1.3.0.tar.gz

# Check package contents
tar -tzf dist/mypackage-1.3.0.tar.gz | head -20

# Validate package
twine check dist/*
```

**Test package locally:**
```bash
# Create fresh virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install dist/mypackage-1.3.0-py3-none-any.whl

# Test import
python -c "import mypackage; print(mypackage.__version__)"

# Run basic tests
python -m pytest test_env/

# Deactivate and clean up
deactivate
rm -rf test_env
```

**Publish to PyPI:**
```bash
# Test on TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Verify on TestPyPI
pip install --index-url https://test.pypi.org/simple/ mypackage

# If successful, publish to PyPI
twine upload dist/*

# Enter credentials (or use token)
# Username: __token__
# Password: pypi-xxxxx...

# Verify published
pip install mypackage==${NEW_VERSION}
```

**Build Docker image (if applicable):**
```bash
# Build with version tag
docker build -t mycompany/myapp:${NEW_VERSION} .
docker build -t mycompany/myapp:latest .

# Test image
docker run --rm mycompany/myapp:${NEW_VERSION} --version

# Push to registry
docker push mycompany/myapp:${NEW_VERSION}
docker push mycompany/myapp:latest
```

**Upload release assets (if needed):**
```bash
# Attach artifacts to GitHub release
gh release upload ${TAG_NAME} dist/*.whl dist/*.tar.gz

# Or manually via web interface:
# Edit release → Attach files → Upload assets
```

**Verification:**
- [ ] Package built successfully
- [ ] Package tested locally
- [ ] Package published to PyPI/registry
- [ ] Docker images built and pushed (if applicable)
- [ ] Release assets uploaded (if needed)
- [ ] Can install package from registry

**If This Fails:**
→ **Build fails**: Check setup.py/pyproject.toml for errors
→ **Upload fails**: Verify PyPI credentials/token
→ **Version conflict**: Version already exists on PyPI (can't overwrite)

---

### Step 7: Deploy to Production

**What:** Deploy the tagged release to production environment.

**How:** Trigger deployment pipeline or manually deploy.

**Trigger automated deployment:**
```bash
# If CI/CD watches tags, pushing tag triggers deployment
# Check CI/CD pipeline status

# Using GitHub Actions
# Workflow should include:
on:
  push:
    tags:
      - 'v*'

# Check deployment status
gh run list --workflow=deploy.yml

# Or manually trigger
gh workflow run deploy.yml --ref ${TAG_NAME}
```

**Manual deployment:**
```bash
# Deploy using deployment script
./scripts/deploy_production.sh ${TAG_NAME}

# Or using kubectl
kubectl set image deployment/myapp myapp=myapp:${NEW_VERSION}
kubectl rollout status deployment/myapp

# Or using other deployment tools
# Ansible, Terraform, etc.
```

**Verify deployment:**
```bash
# Check application version endpoint
curl https://api.example.com/version
# Should return: {"version": "1.3.0"}

# Run smoke tests
./tests/smoke_test_production.sh

# Check health endpoint
curl https://api.example.com/health
# Should return: {"status": "healthy"}

# Monitor logs
kubectl logs -f deployment/myapp
# Look for startup logs showing new version
```

**Verification:**
- [ ] Deployment triggered/completed
- [ ] New version running in production
- [ ] Smoke tests pass
- [ ] No errors in logs
- [ ] Monitoring shows healthy status

**If This Fails:**
→ **Deployment fails**: Check deployment logs, rollback if needed
→ **Health checks fail**: Investigate issues, may need hotfix

---

### Step 8: Post-Release Tasks

**What:** Complete post-release activities like notifications, monitoring, and documentation.

**How:** Notify team, update documentation, monitor release, plan next version.

**Notify team:**
```bash
# Post in Slack/Teams
slack-cli post --channel releases \
  "🚀 Released v${NEW_VERSION} to production!

View release: https://github.com/user/repo/releases/tag/${TAG_NAME}
Changelog: See CHANGELOG.md
Deployed: $(date)

Key features:
- User authentication
- Export functionality
- Real-time notifications"

# Send email (if applicable)
# Notify stakeholders via your communication channels
```

**Update documentation:**
```bash
# Update documentation site (if separate)
cd docs-site
git pull
# Update version references
git commit -m "docs: update for ${NEW_VERSION}"
git push

# Update API documentation
./scripts/generate_api_docs.sh

# Update architecture diagrams (if needed)
```

**Monitor release:**
```bash
# Watch metrics for 24-48 hours
# - Error rates (should stay low)
# - Response times (should be normal)
# - User activity (should be normal)
# - Server resources (CPU, memory)

# Set up alerts for anomalies
# Datadog, New Relic, CloudWatch, etc.

# Check user feedback
# Monitor support channels for issues
```

**Create next version branch (if needed):**
```bash
# For hotfixes
git checkout -b hotfix/1.3.1

# For next minor version
git checkout -b release/1.4.0

# Update version to next development version
# Example: 1.4.0-dev
sed -i '' 's/version = "1.3.0"/version = "1.4.0-dev"/' pyproject.toml
git commit -m "chore: start development of 1.4.0"
```

**Update project management:**
```bash
# Close completed issues
# Link issues to release in GitHub

# Update project board
# Move items to "Released" column

# Plan next sprint/release
# Schedule next release date
```

**Document lessons learned:**
```markdown
# Add to RELEASES.md

## Release 1.3.0 - Lessons Learned

### What Went Well
- Smooth deployment process
- No major issues in production
- Good test coverage caught issues early

### What Could Improve
- Need better pre-release testing
- Documentation should be updated earlier
- Changelog generation could be automated

### Action Items
- [ ] Automate changelog generation
- [ ] Add more integration tests
- [ ] Update release checklist
```

**Verification:**
- [ ] Team notified of release
- [ ] Documentation updated
- [ ] Release being monitored
- [ ] Next version planned
- [ ] Lessons learned documented

**If This Fails:**
→ **Issues found post-release**: Plan hotfix if critical, or include in next release

---

## Verification Checklist

After completing this workflow:

**Pre-Release:**
- [ ] Version number determined
- [ ] All code changes committed
- [ ] All tests passing
- [ ] Documentation updated

**Versioning:**
- [ ] Version updated in all files
- [ ] CHANGELOG.md updated
- [ ] Version follows SemVer
- [ ] Breaking changes documented

**Tagging:**
- [ ] Git tag created
- [ ] Tag is annotated with message
- [ ] Tag pushed to remote
- [ ] Release created on GitHub/GitLab

**Publishing:**
- [ ] Package built successfully
- [ ] Package published to PyPI (if applicable)
- [ ] Docker images built and pushed (if applicable)
- [ ] Release artifacts uploaded

**Deployment:**
- [ ] Deployed to production
- [ ] Smoke tests pass
- [ ] Monitoring looks healthy

**Post-Release:**
- [ ] Team notified
- [ ] Documentation updated
- [ ] Release monitored for issues
- [ ] Next version planned

---

## Best Practices

### DO:
✅ Follow semantic versioning strictly
✅ Write detailed release notes
✅ Use annotated git tags (not lightweight)
✅ Test release candidates before tagging
✅ Automate version bumping where possible
✅ Sign tags with GPG for security
✅ Include breaking changes prominently
✅ Test packages before publishing
✅ Monitor deployments closely
✅ Document lessons learned
✅ Keep CHANGELOG.md up to date
✅ Use consistent tag naming (v1.2.3)

### DON'T:
❌ Tag without updating CHANGELOG
❌ Use vague version numbers (0.0.1 forever)
❌ Skip testing before release
❌ Deploy on Friday afternoon
❌ Forget to push tags to remote
❌ Reuse or delete released tags
❌ Publish without testing package
❌ Include untested changes in release
❌ Release without code review
❌ Forget to notify team
❌ Skip documentation updates

---

## Common Patterns

### Pattern 1: Automated Version Bumping
```bash
# Use tools like bump2version
pip install bump2version

# Configure .bumpversion.cfg
[bumpversion]
current_version = 1.2.3
commit = True
tag = True

[bumpversion:file:pyproject.toml]
[bumpversion:file:src/mypackage/__init__.py]

# Bump version
bump2version patch  # 1.2.3 → 1.2.4
bump2version minor  # 1.2.3 → 1.3.0
bump2version major  # 1.2.3 → 2.0.0
```

### Pattern 2: Release from CI/CD
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

### Pattern 3: Hotfix Releases
```bash
# For urgent production fixes

# 1. Create hotfix branch from production tag
git checkout -b hotfix/1.3.1 v1.3.0

# 2. Fix the issue
# ... make changes ...
pytest  # Ensure fix works

# 3. Bump patch version
echo "1.3.1" > VERSION
git commit -am "fix: critical security issue"

# 4. Tag and release
git tag -a v1.3.1 -m "Hotfix: critical security fix"
git push origin v1.3.1

# 5. Merge back to main
git checkout main
git merge hotfix/1.3.1
git push
```

---

## Troubleshooting

### Issue: Tag already exists

**Symptoms:**
- `git tag` fails with "already exists"
- Can't create tag with same name

**Solution:**
```bash
# Check existing tags
git tag -l ${TAG_NAME}

# If tag is local only, delete and recreate
git tag -d ${TAG_NAME}
git tag -a ${TAG_NAME} -m "Release ${NEW_VERSION}"

# If tag is on remote (requires team approval!)
# Delete remote tag
git push origin --delete ${TAG_NAME}

# Delete local tag
git tag -d ${TAG_NAME}

# Recreate and push
git tag -a ${TAG_NAME} -m "Release ${NEW_VERSION}"
git push origin ${TAG_NAME}
```

**Prevention:**
- Check for existing tags before creating
- Use unique version numbers
- Never reuse version numbers

---

### Issue: Package already exists on PyPI

**Symptoms:**
- `twine upload` fails with "already exists"
- Can't upload version to PyPI

**Solution:**
```bash
# PyPI doesn't allow overwriting versions
# Must use new version number

# 1. Delete local tag
git tag -d ${TAG_NAME}

# 2. Bump to next patch version
NEW_VERSION="1.3.1"
TAG_NAME="v${NEW_VERSION}"

# 3. Update version in files
# ... update version ...

# 4. Rebuild and upload
python -m build
twine upload dist/*
```

**Prevention:**
- Always test on TestPyPI first
- Double-check version doesn't exist before building
- Automate version bumping to avoid conflicts

---

### Issue: Deployment fails after tagging

**Symptoms:**
- Tag created and pushed
- Deployment to production fails
- Need to rollback

**Solution:**
```bash
# Don't delete the tag - it's already released
# Instead, create a new patch version with the fix

# 1. Fix the issue
git checkout main
# ... make fixes ...

# 2. Create hotfix release
NEW_VERSION="1.3.1"
# Update version
# Commit, tag, deploy

# 3. Or rollback deployment to previous version
kubectl rollout undo deployment/myapp

# Tag remains as documentation of what was attempted
```

**Prevention:**
- Test thoroughly before tagging
- Use staging environment to validate
- Have rollback plan ready

---

## Related Workflows

**Prerequisites:**
- [[dev-002]] Test Writing - Must have passing tests
- [[dev-017]] CI/CD Workflow - Automated testing
- [[qa-008]] Quality Gate Execution - Quality checks

**Next Steps:**
- [[dvo-015]] Deployment Process - Actually deploy the release
- [[dev-013]] Rollback Procedure - If release has issues
- [[pm-004]] Release Communication - Announce to users

**Related:**
- [[dev-006]] Dependency Upgrade - Keep dependencies current
- [[dvo-014]] Monitoring Setup - Monitor after release
- [[qa-001]] Code Review - Review before release

---

## Tags
`development` `release` `versioning` `git-tags` `semantic-versioning` `changelog` `deployment` `pypi` `publishing`
