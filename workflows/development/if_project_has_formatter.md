# Check and Configure Code Formatter

**ID:** dev-017  
**Category:** Development  
**Priority:** MEDIUM  
**Complexity:** Simple  
**Estimated Time:** 10-20 minutes  
**Frequency:** Once per project  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Check if a project has a code formatter configured, identify which formatter is being used, and set up or configure the formatter if missing or improperly configured.

**Why:** Consistent code formatting reduces code review friction, improves readability, and eliminates debates about style. Automated formatters save time and maintain consistency across the codebase.

**When to use:**
- Starting work on a new project
- Onboarding to an existing codebase
- Setting up a new repository
- Before contributing to open-source projects
- When encountering inconsistent code formatting

---

## Prerequisites

**Required Knowledge:**
- [ ] Basic understanding of code formatters
- [ ] Familiarity with configuration files (JSON, TOML, YAML)
- [ ] Basic command line usage

**Required Tools:**
- [ ] Access to project directory
- [ ] Text editor or IDE
- [ ] Package manager (pip, npm, yarn, etc.)

**Check before starting:**
```bash
# Check if you're in a git repository
git status

# Check Python version (if Python project)
python --version

# Check Node version (if JavaScript/TypeScript project)
node --version
```

---

## Implementation Steps

### Step 1: Identify Project Type and Common Formatters

**What:** Determine the programming language(s) and likely formatter options

**How:**

**For Python Projects, check for:**
- Black (most popular)
- Ruff (modern, fast)
- autopep8
- yapf
- isort (for imports only)

**For JavaScript/TypeScript Projects, check for:**
- Prettier (most popular)
- ESLint (with --fix)
- StandardJS
- Biome (modern alternative)

**For Multi-language Projects:**
- Prettier (supports JS, TS, JSON, YAML, Markdown, etc.)
- EditorConfig (basic formatting rules)

**Verification:**
- [ ] Identified primary programming language
- [ ] Know which formatters to look for

---

### Step 2: Check for Existing Formatter Configuration

**What:** Look for formatter configuration files and tool configurations

**How:**

```bash
# Check for common Python formatter configs
ls -la | grep -E "(pyproject.toml|setup.cfg|.ruff.toml|.black)"

# Check for common JavaScript formatter configs
ls -la | grep -E "(.prettierrc|.prettierrc.json|.prettierrc.js|prettier.config)"

# Check for EditorConfig
ls -la .editorconfig

# Check pyproject.toml for formatter settings
cat pyproject.toml | grep -A 10 "\[tool.black\]"
cat pyproject.toml | grep -A 10 "\[tool.ruff\]"

# Check package.json for Prettier
cat package.json | grep -A 5 "prettier"
```

**Common Configuration Files:**

**Python:**
- `pyproject.toml` - Black, Ruff, isort config
- `.ruff.toml` - Ruff-specific config
- `setup.cfg` - Legacy config location
- `.black` - Black-specific config

**JavaScript/TypeScript:**
- `.prettierrc` / `.prettierrc.json` / `.prettierrc.js`
- `prettier.config.js`
- `package.json` (with "prettier" key)
- `.editorconfig`

**Verification:**
- [ ] Found configuration file(s)
- [ ] Identified which formatter is configured

**If This Fails:**
→ No formatter configured, proceed to Step 4 to set one up

---

### Step 3: Verify Formatter is Installed

**What:** Check if the formatter tool is actually installed and accessible

**How:**

**For Python:**
```bash
# Check if Black is installed
python -m black --version
# or
black --version

# Check if Ruff is installed  
ruff --version

# Check if isort is installed
isort --version

# Check via pip
pip list | grep black
pip list | grep ruff
pip list | grep isort
```

**For JavaScript/TypeScript:**
```bash
# Check if Prettier is installed
npx prettier --version
# or if installed globally
prettier --version

# Check in package.json
cat package.json | grep prettier

# Check in node_modules
ls node_modules | grep prettier
```

**Verification:**
- [ ] Formatter tool is installed
- [ ] Version is compatible with project requirements

**If This Fails:**
→ Install the formatter (proceed to Step 4)

---

### Step 4: Install and Configure Formatter (if missing)

**What:** Set up a formatter for the project if one doesn't exist

**How:**

#### Option A: Python Project with Black (Recommended)

```bash
# Install Black
pip install black

# Or add to requirements
echo "black>=23.0.0" >> requirements-dev.txt

# Create basic configuration in pyproject.toml
cat >> pyproject.toml << 'EOF'

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''
EOF
```

#### Option B: Python Project with Ruff (Modern, Faster)

```bash
# Install Ruff
pip install ruff

# Or add to requirements
echo "ruff>=0.1.0" >> requirements-dev.txt

# Create configuration in pyproject.toml
cat >> pyproject.toml << 'EOF'

[tool.ruff]
line-length = 100
target-version = "py38"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
ignore = []
EOF
```

#### Option C: JavaScript/TypeScript Project with Prettier

```bash
# Install Prettier
npm install --save-dev prettier

# Or with yarn
yarn add --dev prettier

# Create configuration file
cat > .prettierrc.json << 'EOF'
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
EOF

# Create ignore file
cat > .prettierignore << 'EOF'
node_modules
dist
build
coverage
*.min.js
EOF

# Add script to package.json
npm pkg set scripts.format="prettier --write \"src/**/*.{js,ts,tsx,json,css,md}\""
npm pkg set scripts.format:check="prettier --check \"src/**/*.{js,ts,tsx,json,css,md}\""
```

**Verification:**
- [ ] Formatter installed successfully
- [ ] Configuration file created
- [ ] Configuration matches project style preferences

---

### Step 5: Test Formatter on Sample Files

**What:** Run the formatter on a test file to ensure it works correctly

**How:**

**For Black:**
```bash
# Format a single file (dry run)
black --check src/main.py

# Format a single file (actual format)
black src/main.py

# Format entire project
black .
```

**For Ruff:**
```bash
# Check formatting
ruff format --check .

# Apply formatting
ruff format .
```

**For Prettier:**
```bash
# Check formatting
npx prettier --check "src/**/*.{js,ts,tsx}"

# Apply formatting
npx prettier --write "src/**/*.{js,ts,tsx}"

# Or use npm script
npm run format
```

**Expected Result:**
- Files are formatted according to configuration
- No errors during formatting
- Style is consistent across files

**Verification:**
- [ ] Formatter runs without errors
- [ ] File formatting looks correct
- [ ] No unexpected changes

**If This Fails:**
→ Check configuration syntax and file paths

---

### Step 6: Integrate with Pre-commit Hooks (Recommended)

**What:** Automatically run formatter before each commit

**How:**

**For Python with pre-commit:**
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
EOF

# Install the hooks
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

**For JavaScript with husky + lint-staged:**
```bash
# Install husky and lint-staged
npm install --save-dev husky lint-staged

# Initialize husky
npx husky init

# Add lint-staged configuration to package.json
npm pkg set lint-staged="{'*.{js,ts,tsx,json,css,md}': 'prettier --write'}"

# Create pre-commit hook
cat > .husky/pre-commit << 'EOF'
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
EOF

chmod +x .husky/pre-commit
```

**Verification:**
- [ ] Pre-commit hooks installed
- [ ] Hooks run on `git commit`
- [ ] Only staged files are formatted

---

### Step 7: Update CI/CD to Check Formatting

**What:** Add formatter checks to CI pipeline

**How:**

**GitHub Actions Example (Python):**
```yaml
# .github/workflows/format-check.yml
name: Format Check

on: [push, pull_request]

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install formatter
        run: pip install black ruff
      
      - name: Check formatting with Black
        run: black --check .
      
      - name: Check formatting with Ruff
        run: ruff format --check .
```

**GitHub Actions Example (JavaScript):**
```yaml
# .github/workflows/format-check.yml
name: Format Check

on: [push, pull_request]

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Check formatting
        run: npm run format:check
```

**Verification:**
- [ ] CI workflow file created
- [ ] Workflow runs on push/PR
- [ ] Formatting violations fail the build

---

## Verification Checklist

After setting up formatter:

- [ ] Formatter is configured (configuration file exists)
- [ ] Formatter tool is installed (runs successfully)
- [ ] Configuration matches team/project style preferences
- [ ] Formatter works on test files
- [ ] Pre-commit hooks installed (optional but recommended)
- [ ] CI/CD checks formatting (optional but recommended)
- [ ] Team members know how to run formatter
- [ ] Documentation updated with formatter instructions

---

## Common Issues & Solutions

### Issue 1: Formatter Not Found After Installation

**Symptoms:**
```bash
black: command not found
```

**Solution:**
```bash
# Make sure it's installed in the right environment
python -m pip list | grep black

# Run using python -m
python -m black .

# Or ensure your PATH includes pip installation directory
export PATH="$HOME/.local/bin:$PATH"  # Linux/Mac
# On Windows, check Python Scripts folder is in PATH
```

---

### Issue 2: Formatter Configuration Conflicts

**Symptoms:**
- Formatter keeps changing code back and forth
- Different formatters disagree on style

**Solution:**
Pick ONE formatter and disable others:
```toml
# pyproject.toml - Use Ruff's formatter, disable Black
[tool.ruff]
format = true

# Don't have both [tool.black] and [tool.ruff.format]
```

---

### Issue 3: Formatting Breaks Code

**Symptoms:**
- Formatter changes break tests
- Formatter modifies strings incorrectly

**Solution:**
Use format disable comments:
```python
# fmt: off
data = [
    "keep", "this",
    "exact", "formatting"
]
# fmt: on
```

```javascript
// prettier-ignore
const matrix = [
  1, 0, 0,
  0, 1, 0,
  0, 0, 1
];
```

---

## Best Practices

### DO:
✅ Choose ONE formatter per language  
✅ Commit configuration files to version control  
✅ Run formatter automatically (pre-commit hooks)  
✅ Check formatting in CI/CD  
✅ Format entire codebase when initially adopting  
✅ Document formatter choice in README  
✅ Use standard configurations when possible  
✅ Keep formatter up to date

### DON'T:
❌ Use multiple formatters that conflict  
❌ Manually fix formatting (let the tool do it)  
❌ Skip formatting on "legacy" files  
❌ Override formatter decisions excessively  
❌ Forget to install formatter in CI  
❌ Leave formatter configuration ambiguous  
❌ Format files not tracked in git  
❌ Commit formatter-ignored files without reviewing

---

## Examples

### Example 1: Discovering Black in Python Project

```bash
# Step 1: Check for configuration
$ cat pyproject.toml | grep black
[tool.black]
line-length = 88

# Step 2: Check if installed
$ black --version
black, 23.12.1 (compiled: yes)

# Step 3: Test it
$ black --check src/
All done! ✨ 🍰 ✨
12 files would be left unchanged.

# Result: Black is configured and working!
```

---

### Example 2: Setting Up Prettier in New React Project

```bash
# Step 1: No formatter found
$ ls -la | grep prettier
# (nothing found)

# Step 2: Install Prettier
$ npm install --save-dev prettier
$ npm install --save-dev eslint-config-prettier  # Disable ESLint formatting rules

# Step 3: Create configuration
$ cat > .prettierrc.json << 'EOF'
{
  "semi": true,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "es5"
}
EOF

# Step 4: Add scripts
$ npm pkg set scripts.format="prettier --write 'src/**/*.{js,jsx,ts,tsx,json,css}'"

# Step 5: Format existing code
$ npm run format

# Result: Prettier configured and code formatted!
```

---

### Example 3: Migrating from No Formatter to Ruff

```bash
# Current state: No formatter, inconsistent style
$ ls *.py
main.py  utils.py  helpers.py

# Install Ruff
$ pip install ruff
$ echo "ruff>=0.1.0" >> requirements-dev.txt

# Create configuration
$ cat >> pyproject.toml << 'EOF'

[tool.ruff]
line-length = 100

[tool.ruff.format]
quote-style = "double"
EOF

# Format all files
$ ruff format .
12 files reformatted

# Set up pre-commit
$ pip install pre-commit
$ cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
EOF
$ pre-commit install

# Result: Project now uses Ruff with pre-commit hooks!
```

---

## Related Workflows

**Before This Workflow:**
- [[dev-022]](environment_initialization.md) - Set up development environment
- [[dev-023]](new_repo_scaffolding.md) - Create project structure

**After This Workflow:**
- [[dev-024]](pre_commit_hooks.md) - Set up comprehensive pre-commit hooks
- [[qua-009]](../quality-assurance/ruff_error_resolution.md) - Fix linting issues

**Complementary Workflows:**
- [[qua-001]](../quality-assurance/code_review_checklist.md) - Code review standards
- [[cfg-003]](../configuration-management/project_formatter_setup.md) - Detailed formatter setup

---

## Tags

`code-formatting` `black` `prettier` `ruff` `automation` `code-quality` `development` `tooling` `setup`
