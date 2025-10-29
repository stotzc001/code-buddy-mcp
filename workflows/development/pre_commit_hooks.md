# Pre-Commit Hook Setup

**ID:** dev-024  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 20-30 minutes  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Configure automated code quality checks that run before every git commit to enforce standards and catch issues early.

**Why:** Pre-commit hooks prevent bad code from entering the repository by automatically running formatters, linters, and tests. This catches issues in seconds rather than minutes (CI/CD) or hours (code review), saving time and improving code quality.

**When to use:**
- Setting up a new project
- Standardizing code quality across team
- Reducing code review feedback cycles
- Enforcing consistent code style
- Preventing common mistakes (secrets, large files, etc.)
- Automating repetitive quality checks

---

## Prerequisites

**Required Tools:**
- [ ] Git installed and repository initialized
- [ ] Python 3.7+ with pip
- [ ] Virtual environment activated
- [ ] Write access to repository

**Required Knowledge:**
- [ ] Basic git usage (commit, add)
- [ ] Understanding of linters and formatters
- [ ] Command line basics

**Project Requirements:**
- [ ] Repository has .git directory
- [ ] pyproject.toml or requirements.txt exists
- [ ] Code formatters/linters decided (black, ruff, mypy, etc.)

**Check before starting:**
```bash
# Verify git repo
git status

# Verify Python
python --version  # 3.7+

# Verify in virtual environment
which python  # Should point to venv

# Check pre-commit not already installed
pre-commit --version 2>/dev/null || echo "Not installed (good)"
```

---

## Implementation Steps

### Step 1: Install Pre-Commit Framework

**What:** Install the pre-commit package that manages git hooks.

**How:**
```bash
# Install via pip
pip install pre-commit

# Verify installation
pre-commit --version

# Add to requirements
echo "pre-commit>=3.5.0" >> requirements-dev.txt

# Or add to pyproject.toml
# [project.optional-dependencies]
# dev = ["pre-commit>=3.5.0", ...]
```

**Verification:**
- [ ] pre-commit installed: `pre-commit --version` shows version 3.5+
- [ ] Command available: `which pre-commit` points to venv
- [ ] Added to dependency file

**If This Fails:**
→ **Command not found:** Ensure virtual environment is activated
→ **Permission error:** Don't use sudo; use venv
→ **Old version:** Upgrade with `pip install --upgrade pre-commit`

---

### Step 2: Create Pre-Commit Configuration

**What:** Create `.pre-commit-config.yaml` defining which hooks to run.

**How:**

**Basic configuration (recommended start):**
```bash
cat > .pre-commit-config.yaml << 'EOF'
# Pre-commit hooks configuration
# See https://pre-commit.com for more information

repos:
  # General pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace        # Remove trailing whitespace
      - id: end-of-file-fixer          # Ensure files end with newline
      - id: check-yaml                 # Check YAML syntax
      - id: check-json                 # Check JSON syntax
      - id: check-toml                 # Check TOML syntax
      - id: check-added-large-files    # Prevent large files (>1MB)
        args: ['--maxkb=1000']
      - id: check-merge-conflict       # Check for merge conflict strings
      - id: debug-statements           # Check for debugger imports
      - id: mixed-line-ending          # Ensure consistent line endings

  # Python code formatting
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11
        args: ['--line-length=88']

  # Python linting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.7
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  # Type checking (optional - can be slow)
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports, --no-strict-optional]
EOF
```

**Advanced configuration with more hooks:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: debug-statements
      - id: mixed-line-ending
      - id: check-docstring-first      # Docstring before code
      - id: check-case-conflict        # Filename case conflicts
      - id: check-executables-have-shebangs
      - id: name-tests-test            # Test files named test_*.py
        args: ['--pytest-test-first']

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.7
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  # Import sorting
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ['--profile=black']

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
        additional_dependencies: ['bandit[toml]']

  # Secrets detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Documentation
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: ['--convention=google']

  # Jupyter notebooks (if using)
  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.7.1
    hooks:
      - id: nbqa-black
      - id: nbqa-isort
```

**Minimal configuration (fast, for beginners):**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
```

**Verification:**
- [ ] `.pre-commit-config.yaml` created in repository root
- [ ] YAML syntax is valid: `pre-commit validate-config`
- [ ] Hooks are defined for your needs

**If This Fails:**
→ **Invalid YAML:** Check indentation and syntax
→ **Wrong repo:** Ensure repos exist and versions are valid

---

### Step 3: Install Git Hooks

**What:** Install pre-commit hooks into `.git/hooks/` directory.

**How:**
```bash
# Install hooks
pre-commit install

# Verify installation
ls -la .git/hooks/pre-commit

# The hook should contain pre-commit content
cat .git/hooks/pre-commit | head -5
```

**Optional: Install hooks for commit messages and push:**
```bash
# Install commit message hook
pre-commit install --hook-type commit-msg

# Install pre-push hook
pre-commit install --hook-type pre-push

# Install all hook types
pre-commit install --install-hooks
```

**Verification:**
- [ ] Hooks installed: `.git/hooks/pre-commit` exists
- [ ] Hook is executable: `test -x .git/hooks/pre-commit && echo "Executable"`
- [ ] Hook contains pre-commit shebang

**If This Fails:**
→ **Permission denied:** Ensure `.git/hooks` is writable
→ **Already exists:** Previous hooks will be backed up automatically
→ **Not a git repository:** Run `git init` first

---

### Step 4: Run Initial Check

**What:** Test pre-commit hooks on all files to fix existing issues.

**How:**
```bash
# Run on all files (first time setup)
pre-commit run --all-files

# This will:
# 1. Download hook repositories
# 2. Install hook environments
# 3. Run hooks on all files
# 4. Show what was fixed/failed

# Example output:
# Trim Trailing Whitespace...........................................Passed
# Fix End of Files..................................................Failed
# - hook id: end-of-file-fixer
# - exit code: 1
# - files were modified by this hook
#
# Fixing src/main.py

# If fixes were made, stage and commit them
git add -u
git commit -m "Apply pre-commit fixes to existing code"
```

**If many issues found:**
```bash
# Run specific hook
pre-commit run black --all-files

# Run only on staged files
pre-commit run

# Skip hooks temporarily (not recommended)
git commit --no-verify -m "message"

# Update hook versions
pre-commit autoupdate
```

**Verification:**
- [ ] All hooks downloaded and installed
- [ ] Hooks run successfully or with expected failures
- [ ] Code formatted/fixed as needed
- [ ] Changes committed if modifications made

**If This Fails:**
→ **Hook fails on valid code:** Adjust hook configuration
→ **Too many issues:** Fix incrementally or adjust hooks
→ **Slow execution:** Consider removing slow hooks (mypy) from pre-commit

---

### Step 5: Configure Hook Behavior

**What:** Customize hook behavior for your project needs.

**How:**

**Skip specific files:**
```yaml
# In .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        exclude: |
          (?x)^(
              path/to/skip/.*|
              another/path/.*\.py|
              migrations/.*
          )$
```

**Skip hooks on specific commits:**
```bash
# Skip all hooks once
SKIP=black,ruff git commit -m "WIP commit"

# Skip specific hook
SKIP=mypy git commit -m "Fix later"

# Never skip in CI/CD - only local development
```

**Set hook to warning only (don't block commit):**
```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        verbose: true        # Show output even on pass
        always_run: false    # Only run on typed files
```

**Add custom hook:**
```yaml
# Local hooks defined in repository
repos:
  - repo: local
    hooks:
      - id: check-commit-message
        name: Check commit message format
        entry: python scripts/check_commit_msg.py
        language: python
        stages: [commit-msg]

      - id: run-tests
        name: Run quick tests
        entry: pytest tests/unit -x
        language: system
        pass_filenames: false
        stages: [push]
```

**Verification:**
- [ ] Hook behavior customized for project
- [ ] Exclusions work as expected
- [ ] Custom hooks run correctly

---

### Step 6: Update Project Documentation

**What:** Document pre-commit setup for team members.

**How:**

**Add to README.md:**
```markdown
## Development Setup

### Install Pre-Commit Hooks

This project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (first time)
pre-commit run --all-files
```

Hooks will now run automatically on `git commit`.

To skip hooks temporarily (not recommended):
```bash
git commit --no-verify
```
```

**Create .pre-commit-troubleshooting.md:**
```markdown
# Pre-Commit Troubleshooting

## Hooks are slow
- Remove mypy from pre-commit (run in CI instead)
- Use `--no-verify` sparingly
- Check if you need all hooks

## Hook keeps failing
- Run hook in isolation: `pre-commit run hook-id`
- Check hook output for specific error
- Update hook: `pre-commit autoupdate`

## Need to skip hooks
```bash
# Temporarily skip (local only)
SKIP=hook-name git commit -m "message"

# Never use --no-verify in shared commits
```

## Update hooks
```bash
pre-commit autoupdate
```
```

**Verification:**
- [ ] README documents pre-commit setup
- [ ] Setup instructions are clear
- [ ] Troubleshooting guide created

---

### Step 7: Configure CI/CD Integration

**What:** Run same checks in CI/CD to enforce standards.

**How:**

**Add to GitHub Actions (.github/workflows/ci.yml):**
```yaml
name: CI

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - uses: pre-commit/action@v3.0.0
```

**Alternative: Run specific checks:**
```yaml
jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install black ruff mypy
    
    - name: Run black
      run: black --check src/ tests/
    
    - name: Run ruff
      run: ruff check src/ tests/
    
    - name: Run mypy
      run: mypy src/
```

**Verification:**
- [ ] CI runs same checks as pre-commit
- [ ] CI fails if code doesn't pass checks
- [ ] Tests confirm hooks work

---

### Step 8: Commit Configuration

**What:** Commit pre-commit configuration to repository.

**How:**
```bash
# Stage configuration files
git add .pre-commit-config.yaml
git add README.md  # If updated

# Commit
git commit -m "Add pre-commit hooks configuration

- Configure black, ruff, mypy hooks
- Add pre-commit hook documentation
- Set up CI/CD integration"

# Push
git push
```

**Verification:**
- [ ] `.pre-commit-config.yaml` in repository
- [ ] Team members can install hooks
- [ ] CI/CD enforces same checks

---

## Verification Checklist

After completing this workflow, verify:

**Installation:**
- [ ] pre-commit installed: `pre-commit --version`
- [ ] Configuration file exists: `.pre-commit-config.yaml`
- [ ] Hooks installed in git: `.git/hooks/pre-commit`

**Functionality:**
- [ ] Hooks run on commit: `git commit` triggers checks
- [ ] Can run manually: `pre-commit run --all-files`
- [ ] Hooks catch issues: Intentionally break style and try to commit

**Configuration:**
- [ ] Appropriate hooks selected for project
- [ ] Hook versions are recent
- [ ] Custom exclusions work

**Documentation:**
- [ ] README explains setup
- [ ] Team knows how to use hooks
- [ ] CI/CD mirrors hooks

**Team Adoption:**
- [ ] All developers have hooks installed
- [ ] Hooks don't slow down workflow too much
- [ ] Issues are caught before CI/CD

---

## Common Issues & Solutions

### Issue: Hooks are too slow

**Symptoms:**
- Commits take >10 seconds
- Developers skip hooks with --no-verify
- Frustration with workflow

**Causes:**
- Mypy type checking on every commit
- Too many files checked
- Slow hooks on every file

**Solution:**
```yaml
# Remove slow hooks from pre-commit
# Run them in CI instead

# Keep fast hooks:
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.7
    hooks:
      - id: ruff
        args: [--fix]

# Move mypy to CI/CD only
# Or run mypy only on changed files:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        pass_filenames: true  # Only check changed files
```

**Prevention:**
- Profile hooks: `time pre-commit run --all-files`
- Keep only essential fast hooks
- Run expensive checks in CI only

---

### Issue: Hook fails with "command not found"

**Symptoms:**
- `black: command not found`
- `ruff: command not found`
- Hooks fail immediately

**Causes:**
- Hook dependencies not installed in hook environment
- Wrong Python version in hook

**Solution:**
```bash
# Update hooks to re-download environments
pre-commit clean
pre-commit install --install-hooks

# Specify Python version explicitly
# In .pre-commit-config.yaml:
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11  # Specify version

# For local hooks, install dependencies:
pip install black ruff mypy
```

**Prevention:**
- Let pre-commit manage hook dependencies
- Don't rely on local installations
- Specify language_version when needed

---

### Issue: Files were modified by hook

**Symptoms:**
- Hook shows "Files were modified"
- Commit is blocked
- Need to re-add files

**Causes:**
- This is expected behavior!
- Formatter (black) fixed code
- Need to stage changes and re-commit

**Solution:**
```bash
# This is normal! Just re-add and commit:

# Hooks fixed your code
pre-commit run --all-files

# Stage the fixes
git add -u

# Commit again
git commit -m "Your message"

# Now hooks will pass
```

**Not really an issue - this is how formatters work:**
1. You commit poorly formatted code
2. Hook reformats it
3. You stage the formatted version
4. You commit successfully

**Prevention:**
- Format code before committing: `black src/`
- Use IDE auto-format on save
- This is actually preventing problems!

---

### Issue: Hook fails with SSL/network errors

**Symptoms:**
- `SSL: CERTIFICATE_VERIFY_FAILED`
- `Could not find a version`
- Timeout errors

**Causes:**
- Corporate proxy/firewall
- Network restrictions
- SSL certificate issues

**Solution:**
```bash
# Use specific hook versions (avoid dynamic)
# In .pre-commit-config.yaml:
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0  # Pin specific version

# Or install manually and use local hooks:
pip install black ruff mypy

# Then configure as local hooks:
repos:
  - repo: local
    hooks:
      - id: black
        name: black
        entry: black
        language: system
        types: [python]
```

**Prevention:**
- Pin hook versions
- Configure proxy if needed
- Use cached environments

---

### Issue: Pre-commit hook not running

**Symptoms:**
- Commits go through without checks
- No hook output
- Hooks seem disabled

**Causes:**
- Hooks not installed
- Using --no-verify
- Hooks disabled

**Solution:**
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify hook is there
cat .git/hooks/pre-commit

# Test manually
pre-commit run

# Check if SKIP environment variable is set
echo $SKIP

# Ensure not using --no-verify
alias git  # Check for alias with --no-verify
```

**Prevention:**
- Run `pre-commit install` after clone
- Add to setup documentation
- Don't use --no-verify habitually

---

### Issue: Merge conflicts in `.pre-commit-config.yaml`

**Symptoms:**
- Merge conflict in hook configuration
- Different hook versions

**Causes:**
- Multiple developers updating hooks
- Auto-update on different branches

**Solution:**
```bash
# Accept both changes and deduplicate
git checkout --ours .pre-commit-config.yaml   # Take your version
# or
git checkout --theirs .pre-commit-config.yaml  # Take their version

# Or manually merge in editor

# Then update to latest versions
pre-commit autoupdate

# Verify configuration is valid
pre-commit validate-config

# Test
pre-commit run --all-files
```

**Prevention:**
- Coordinate hook updates
- Update hooks in separate PR
- Use autoupdate regularly

---

## Examples

### Example 1: Python Web Application (FastAPI)

**Context:** Setting up pre-commit for FastAPI project.

**Execution:**
```bash
# Step 1: Install
pip install pre-commit

# Step 2: Configure
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.7
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all, pydantic]
EOF

# Step 3: Install and run
pre-commit install
pre-commit run --all-files

# Step 4: Commit
git add .
git commit -m "Add pre-commit hooks"
```

**Result:**
- Code automatically formatted on commit
- Import errors caught
- Type checking enforced
- Team has consistent style

**Time:** ~15 minutes

---

### Example 2: Data Science Project (with Notebooks)

**Context:** Project with Jupyter notebooks needs quality checks.

**Execution:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  # Notebook-specific hooks
  - repo: https://github.com/nbQA-dev/nbQA
    rev: 1.7.1
    hooks:
      - id: nbqa-black
      - id: nbqa-isort
      - id: nbqa-ruff

  # Clear notebook outputs before commit
  - repo: https://github.com/kynan/nbstripout
    rev: 0.6.1
    hooks:
      - id: nbstripout
```

**Result:**
- Notebooks formatted consistently
- Outputs cleared before commit (reduces repo size)
- Code in notebooks follows same standards as .py files

---

### Example 3: Minimal Fast Configuration

**Context:** Small project, wants fast commits.

**Execution:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
```

**Result:**
- Commits take <2 seconds
- Essential checks only
- More thorough checks in CI

---

## Best Practices

### DO:
✅ **Install hooks early** - Set up before writing code
✅ **Keep hooks fast** - Under 5 seconds for common case
✅ **Run on all files initially** - Fix existing issues once
✅ **Use standard tools** - black, ruff, mypy are well supported
✅ **Document for team** - Clear setup instructions
✅ **Match CI/CD** - Same checks in both places
✅ **Update regularly** - `pre-commit autoupdate` monthly
✅ **Test after install** - Ensure hooks work
✅ **Skip expensive checks** - Run slow tools in CI only
✅ **Version control config** - Commit `.pre-commit-config.yaml`

### DON'T:
❌ **Make hooks too slow** - Developers will skip them
❌ **Run all checks always** - Mypy can be slow
❌ **Skip hooks regularly** - Defeats the purpose
❌ **Ignore failures** - Fix issues promptly
❌ **Add too many hooks** - Start minimal, add as needed
❌ **Forget CI integration** - Hooks can be bypassed
❌ **Use outdated hooks** - Update regularly
❌ **Make hooks optional** - Should be standard
❌ **Block on style issues** - Auto-fix when possible
❌ **Forget documentation** - Team needs to know setup

---

## Related Workflows

**Prerequisites:**
- [[dev-023]](new_repo_scaffolding.md) - New Repo Scaffolding
- [[dev-022]](environment_initialization.md) - Environment Initialization

**Next Steps:**
- [[dev-025]](ci_cd_workflow.md) - CI/CD Workflow Setup
- [[qua-008]](../quality-assurance/quality_gate_execution.md) - Quality Gate Execution
- [[qua-001]](../quality-assurance/code_review_checklist.md) - Code Review Checklist

**Alternatives:**
- Husky (for JavaScript/Node.js projects)
- Git hooks without pre-commit framework
- IDE-only formatting (not recommended)

**Complementary:**
- [[qua-009]](../quality-assurance/ruff_error_resolution.md) - Ruff Error Resolution
- [[qua-006]](../quality-assurance/mypy_type_fixing.md) - Mypy Type Error Fixing
- [[dev-004]](type_annotation_addition.md) - Type Annotation Addition

---

## Tags
`development` `git-hooks` `pre-commit` `automation` `code-quality` `linting` `formatting` `black` `ruff` `mypy` `ci-cd`
