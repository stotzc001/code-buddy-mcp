# Code Buddy Secret Management Rules

**ID:** sec-001  
**Category:** Security  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 20-30 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Specific rules and best practices for handling secrets, credentials, and sensitive data when using Code Buddy MCP (Model Context Protocol) system.

**Why:** Code Buddy workflows access and manipulate code repositories, making proper secret handling critical. Exposing secrets through MCP tools or in workflow documentation creates persistent security vulnerabilities.

**When to use:**
- Setting up new Code Buddy workflows
- Creating workflow documentation
- Reviewing existing workflows for security issues
- Onboarding new developers to Code Buddy
- Auditing workflow security practices
- Updating workflows with sensitive operations

---

## Prerequisites

**Required:**
- [ ] Code Buddy MCP system installed and configured
- [ ] Understanding of secret management principles
- [ ] Access to secret management system (AWS Secrets Manager, Vault, etc.)
- [ ] Familiarity with environment variables

**Check before starting:**
```bash
# Verify Code Buddy is configured
code-buddy status

# Check for pre-commit hooks
pre-commit --version
ls -la .git/hooks/

# Verify secret manager access
aws secretsmanager list-secrets --max-results 1
# or
vault status
```

---

## Implementation Steps

### Step 1: Understand Code Buddy Context

**What:** Learn how Code Buddy handles code and what data it can access.

**How:**
Code Buddy operates through MCP tools that can read files, execute commands, and analyze repositories. Understanding its access patterns is crucial for security.

**Code Buddy Capabilities:**
```python
# Code Buddy can:
# 1. Read any file in the workspace
code_buddy.read_file("config/database.yml")  # ❌ Risk if contains secrets

# 2. Search for patterns across files
code_buddy.search_files(pattern="API_KEY")  # ❌ Will find hardcoded secrets

# 3. Execute commands
code_buddy.execute("cat .env")  # ❌ Could expose environment secrets

# 4. Analyze git history
code_buddy.git_log()  # ❌ Could reveal committed secrets

# 5. Create/modify files
code_buddy.write_file("config.yml", content)  # ❌ Risk of writing secrets
```

**Security Implications:**
```yaml
# Code Buddy workflows operate in context where:

Access Level: FULL READ/WRITE to workspace
Logging: All operations are logged
History: Workflow execution traces are stored
Sharing: Workflows can be shared across team
Documentation: Examples may be committed to git

# Therefore:
# ❌ Never hardcode secrets in workflow definitions
# ❌ Never commit examples with real credentials
# ❌ Never log sensitive data in workflow outputs
# ✅ Always use secret management tools
# ✅ Always use environment variables or secret managers
```

**Verification:**
- [ ] Understand Code Buddy's file access capabilities
- [ ] Understand logging and history implications
- [ ] Understand workflow sharing implications
- [ ] Secret management system identified for use

**If This Fails:**
→ Review Code Buddy MCP documentation at `/docs/security`  
→ Consult with security team about appropriate practices  
→ Complete security training before proceeding  

---

### Step 2: Configure Secret Storage

**What:** Set up proper secret storage that Code Buddy can access securely.

**How:**
Use environment variables or dedicated secret management systems rather than hardcoding secrets.

**Environment Variables (Development):**
```bash
# Create .env file for local development (NEVER commit this)
cat > .env << 'EOF'
# Database credentials
DB_HOST=localhost
DB_PORT=5432
DB_USER=dev_user
DB_PASSWORD=secure_dev_password_here
DB_NAME=myapp_dev

# API credentials
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Third-party services
STRIPE_KEY=sk_test_...
SENDGRID_API_KEY=SG....
EOF

# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore

# Create example template (safe to commit)
cat > .env.example << 'EOF'
# Database credentials (get from AWS Secrets Manager)
DB_HOST=localhost
DB_PORT=5432
DB_USER=<your-username>
DB_PASSWORD=<get-from-secrets-manager>
DB_NAME=myapp_dev

# API credentials (get from 1Password)
API_KEY=<your-api-key>
API_SECRET=<your-api-secret>

# Third-party services
STRIPE_KEY=<test-key-from-stripe>
SENDGRID_API_KEY=<key-from-sendgrid>
EOF

# Verify .env is gitignored
git check-ignore .env || echo "⚠️  WARNING: .env is NOT ignored!"
```

**AWS Secrets Manager (Production):**
```python
# workflows/utils/secrets.py
"""
Secure secret retrieval for Code Buddy workflows.
"""
import os
import json
import boto3
from functools import lru_cache

@lru_cache(maxsize=128)
def get_secret(secret_name: str, region: str = "us-east-1") -> dict:
    """
    Retrieve secret from AWS Secrets Manager with caching.
    
    Args:
        secret_name: Name of the secret (e.g., 'prod/database/credentials')
        region: AWS region
        
    Returns:
        dict: Secret key-value pairs
        
    Example:
        >>> db_creds = get_secret('prod/database/credentials')
        >>> connection_string = f"postgresql://{db_creds['username']}:{db_creds['password']}@{db_creds['host']}"
    """
    client = boto3.client('secretsmanager', region_name=region)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        # Log error without exposing sensitive information
        print(f"Error retrieving secret '{secret_name}': {type(e).__name__}")
        raise

def get_env_or_secret(key: str, secret_name: str = None) -> str:
    """
    Get value from environment variable or Secrets Manager.
    
    Tries environment variable first (for dev), then Secrets Manager (for prod).
    
    Args:
        key: Environment variable name
        secret_name: Optional secret name in format 'secret/path:key'
        
    Returns:
        str: Secret value
        
    Example:
        >>> api_key = get_env_or_secret('API_KEY', 'prod/api:api_key')
    """
    # Try environment variable first
    value = os.getenv(key)
    if value:
        return value
    
    # Try Secrets Manager if secret_name provided
    if secret_name and ':' in secret_name:
        secret_id, secret_key = secret_name.split(':', 1)
        secrets = get_secret(secret_id)
        return secrets[secret_key]
    
    raise ValueError(f"Secret '{key}' not found in environment or Secrets Manager")

# Usage in Code Buddy workflows
def initialize_api_client():
    """Initialize API client with secure credentials."""
    api_key = get_env_or_secret('API_KEY', 'prod/api:api_key')
    api_secret = get_env_or_secret('API_SECRET', 'prod/api:api_secret')
    
    return APIClient(api_key=api_key, api_secret=api_secret)
```

**HashiCorp Vault (Alternative):**
```python
# workflows/utils/vault_secrets.py
"""
Vault integration for Code Buddy workflows.
"""
import hvac
import os

def get_vault_client():
    """Initialize Vault client with token auth."""
    return hvac.Client(
        url=os.getenv('VAULT_ADDR', 'http://localhost:8200'),
        token=os.getenv('VAULT_TOKEN')
    )

def get_vault_secret(path: str) -> dict:
    """
    Retrieve secret from Vault.
    
    Args:
        path: Secret path (e.g., 'secret/data/prod/database')
        
    Returns:
        dict: Secret data
    """
    client = get_vault_client()
    response = client.secrets.kv.v2.read_secret_version(path=path)
    return response['data']['data']
```

**Verification:**
- [ ] .env file created and gitignored
- [ ] .env.example created (safe template)
- [ ] Secret management utility functions created
- [ ] Secrets accessible from workflows
- [ ] No secrets hardcoded in code

**If This Fails:**
→ If AWS Secrets Manager unavailable, use environment variables temporarily  
→ If Vault not accessible, fall back to .env files with clear warnings  
→ Document any temporary secret storage for future migration  

---

### Step 3: Sanitize Workflow Examples

**What:** Ensure all workflow documentation and examples use placeholder values instead of real secrets.

**How:**
Review all workflow files and replace any real credentials with obvious placeholders.

**Placeholder Patterns:**
```yaml
# ❌ WRONG - Real values
database:
  host: prod-db.company.com
  username: admin
  password: P@ssw0rd123!
  
api_config:
  stripe_key: sk_live_51Hqp2jKl...
  aws_access_key: AKIAIOSFODNN7EXAMPLE
  aws_secret_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ✅ CORRECT - Placeholders
database:
  host: <your-database-host>
  username: <database-username>
  password: <get-from-secrets-manager>
  
api_config:
  stripe_key: <stripe-secret-key>  # Get from Stripe Dashboard
  aws_access_key: <aws-access-key-id>  # Use IAM role instead
  aws_secret_key: <aws-secret-access-key>  # Use IAM role instead
```

**Automated Sanitization:**
```python
# scripts/sanitize_workflows.py
"""
Scan and sanitize workflow files for secrets.
"""
import re
from pathlib import Path
from typing import List, Tuple

# Patterns that look like secrets
SECRET_PATTERNS = [
    # AWS
    (r'AKIA[0-9A-Z]{16}', '<aws-access-key-id>'),
    (r'aws_secret_access_key["\s:=]+[A-Za-z0-9/+=]{40}', 'aws_secret_access_key: <aws-secret-key>'),
    
    # Stripe
    (r'sk_live_[a-zA-Z0-9]{24,}', '<stripe-secret-key>'),
    (r'pk_live_[a-zA-Z0-9]{24,}', '<stripe-publishable-key>'),
    
    # Generic API keys
    (r'api[_-]?key["\s:=]+[a-zA-Z0-9]{32,}', 'api_key: <your-api-key>'),
    
    # Passwords in configs
    (r'password["\s:=]+[^\s"]{8,}', 'password: <your-password>'),
    
    # JWT tokens
    (r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', '<jwt-token>'),
    
    # Private keys
    (r'-----BEGIN (RSA |)PRIVATE KEY-----[\s\S]+?-----END (RSA |)PRIVATE KEY-----', 
     '<private-key-removed>'),
]

def scan_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Scan file for potential secrets.
    
    Returns:
        List of (line_number, matched_text, suggested_replacement)
    """
    findings = []
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            for pattern, replacement in SECRET_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    findings.append((line_num, match.group(0), replacement))
    
    return findings

def sanitize_workflow_directory(workflow_dir: Path):
    """Scan all workflow files for secrets."""
    for filepath in workflow_dir.rglob('*.md'):
        findings = scan_file(filepath)
        
        if findings:
            print(f"\n⚠️  Found potential secrets in {filepath}:")
            for line_num, matched, replacement in findings:
                print(f"  Line {line_num}: {matched[:30]}...")
                print(f"  Suggest: {replacement}")

if __name__ == '__main__':
    sanitize_workflow_directory(Path('workflows'))
```

**Documentation Template:**
```markdown
# Workflow: API Integration

## Configuration

Create a `.env` file with your credentials:

\```bash
# NEVER commit this file!
API_KEY=<your-api-key-here>
API_SECRET=<your-api-secret-here>
\```

Get your API credentials from:
1. Log in to https://api.example.com
2. Navigate to Settings > API Keys
3. Generate new key pair
4. Save securely in your password manager

## Example Usage

\```python
import os

# ✅ CORRECT - Read from environment
api_key = os.getenv('API_KEY')

# ❌ WRONG - Never hardcode
# api_key = "sk_live_abc123..."  # DON'T DO THIS!
\```
```

**Verification:**
- [ ] All workflow files reviewed
- [ ] Real secrets replaced with placeholders
- [ ] Sanitization script runs clean
- [ ] Documentation includes setup instructions
- [ ] Examples use environment variables

**If This Fails:**
→ If unsure whether value is real secret, replace it with placeholder  
→ If many files to review, automate with sanitization script  
→ If secrets already committed, follow git_history_cleanup_solo.md  

---

### Step 4: Implement Pre-Commit Secret Scanning

**What:** Prevent secrets from being committed to the repository by blocking commits that contain sensitive data.

**How:**
Install and configure pre-commit hooks that scan for secrets before allowing commits.

**Install Pre-Commit Framework:**
```bash
# Install pre-commit
pip install pre-commit

# Create configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  # Secret detection with detect-secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package-lock.json
  
  # Alternative: Gitleaks
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  
  # Check for hardcoded passwords
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=1000']
  
  # Custom Code Buddy secret patterns
  - repo: local
    hooks:
      - id: code-buddy-secrets
        name: Code Buddy Secret Patterns
        entry: python scripts/check_code_buddy_secrets.py
        language: python
        files: '^workflows/.*\.md$'
EOF

# Generate baseline for existing files
detect-secrets scan > .secrets.baseline

# Install hooks
pre-commit install

# Test on all files
pre-commit run --all-files
```

**Custom Code Buddy Secret Checker:**
```python
# scripts/check_code_buddy_secrets.py
"""
Custom pre-commit hook for Code Buddy specific secret patterns.
"""
import re
import sys
from pathlib import Path

# Code Buddy specific patterns
CODE_BUDDY_PATTERNS = [
    # Real AWS credentials
    r'AKIA[0-9A-Z]{16}',
    
    # Real Stripe keys (not test)
    r'sk_live_[a-zA-Z0-9]{24,}',
    
    # Database connection strings with passwords
    r'postgresql://[^:]+:[^@]+@',
    r'mysql://[^:]+:[^@]+@',
    
    # Hardcoded tokens in workflow examples
    r'Bearer [a-zA-Z0-9\-._~+/]+=*',
    
    # Common password patterns
    r'password["\s]*[:=]["\s]*[^\s<]{8,}',
    
    # Generic API keys (32+ chars, no spaces)
    r'api[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9]{32,}',
]

def check_file(filepath: Path) -> bool:
    """
    Check file for Code Buddy specific secret patterns.
    
    Returns:
        True if file is clean, False if secrets found
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Skip checking code blocks that are explicitly marked as examples
    # Remove blocks between `` ` `` (code blocks)
    code_blocks = re.finditer(r'```[\s\S]*?```', content)
    clean_content = content
    
    for block in code_blocks:
        block_text = block.group(0)
        # Keep blocks with placeholders, remove ones with real-looking secrets
        if '<' in block_text and '>' in block_text:
            # Has placeholders, likely safe
            continue
        clean_content = clean_content.replace(block_text, '')
    
    found_secrets = []
    
    for pattern in CODE_BUDDY_PATTERNS:
        matches = re.finditer(pattern, clean_content)
        for match in matches:
            # Exclude obvious placeholders
            matched_text = match.group(0)
            if any(placeholder in matched_text for placeholder in 
                   ['<', '>', 'example', 'placeholder', 'your-', 'get-from']):
                continue
            
            found_secrets.append(matched_text[:30])
    
    if found_secrets:
        print(f"❌ Potential secrets found in {filepath}:")
        for secret in found_secrets:
            print(f"  - {secret}...")
        return False
    
    return True

def main():
    """Check all staged files."""
    files_to_check = sys.argv[1:]
    
    all_clean = True
    for filepath in files_to_check:
        if not check_file(Path(filepath)):
            all_clean = False
    
    if not all_clean:
        print("\n⚠️  Commit blocked: Remove secrets before committing")
        print("   If these are false positives, update .secrets.baseline")
        sys.exit(1)
    
    print("✅ No Code Buddy secrets detected")
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**Testing Pre-Commit Hooks:**
```bash
# Test that secrets are blocked
cat > test-secret.md << 'EOF'
# Test File
API_KEY=sk_live_abc123xyz456def
EOF

git add test-secret.md
git commit -m "Test commit"
# Should be blocked!

# Clean up test
rm test-secret.md
git reset
```

**Verification:**
- [ ] Pre-commit framework installed
- [ ] Secret detection hooks configured
- [ ] Custom Code Buddy patterns added
- [ ] Hooks tested and working
- [ ] Team members have hooks installed
- [ ] False positives documented in baseline

**If This Fails:**
→ If hooks too slow, optimize patterns or use faster tool  
→ If false positives high, tune patterns or update baseline  
→ If team bypass hooks, enforce with server-side checks  

---

### Step 5: Code Review Secret Checklist

**What:** Create a checklist for code reviewers to verify secret handling in Code Buddy workflows.

**How:**
Standardized review process ensures consistent security practices.

**Pull Request Template:**
```markdown
## Code Buddy Workflow Security Checklist

### Secrets & Credentials
- [ ] No hardcoded API keys, passwords, or tokens
- [ ] All secrets use environment variables or secret manager
- [ ] No sensitive data in example code blocks
- [ ] No credentials in log messages
- [ ] .env files are gitignored
- [ ] .env.example provided with placeholders
- [ ] No secrets in comments or documentation

### Configuration Files
- [ ] Database credentials use placeholders or env vars
- [ ] API configurations reference env vars
- [ ] No connection strings with embedded passwords
- [ ] Config files have .example versions

### Workflow Examples
- [ ] All examples use `<placeholder>` format
- [ ] Real credentials replaced with descriptive placeholders
- [ ] Setup instructions include secret retrieval steps
- [ ] No copy-paste examples with real secrets

### Testing & Development
- [ ] Test data uses fake/generated values
- [ ] Development secrets separate from production
- [ ] Local .env not committed
- [ ] Test credentials clearly marked as test-only

### Documentation
- [ ] README includes secret management section
- [ ] Instructions for getting credentials documented
- [ ] Links to secret manager provided
- [ ] Security best practices linked

---

## Automated Checks
- [ ] Pre-commit hooks passing
- [ ] Secret scanning CI passing
- [ ] No detect-secrets alerts
```

**Reviewer Guidelines:**
```markdown
# Code Buddy Workflow Review Guide

## What to Look For

### 🔴 BLOCK IMMEDIATELY
- Real AWS access keys (AKIA...)
- Real Stripe keys (sk_live_...)
- Database passwords in plain text
- Private keys or certificates
- Personal access tokens

### 🟡 REQUEST CHANGES
- API keys without env var reference
- Hardcoded URLs with credentials
- Examples that could be mistaken for real
- Missing .env.example file
- Config files without placeholders

### 🟢 APPROVE IF PRESENT
- All secrets use os.getenv() or secret manager
- Clear placeholder format (<your-api-key>)
- Documentation explains secret setup
- Pre-commit hooks prevent secret commits
- .env is gitignored

## Review Process

1. **Scan for patterns**
   ```bash
   # Quick scan for common issues
   grep -r "password.*=.*[^<]" workflows/
   grep -r "api_key.*=.*[^<]" workflows/
   grep -r "AKIA" workflows/
   grep -r "sk_live" workflows/
   ```

2. **Check configuration**
   ```bash
   # Verify .env is ignored
   git check-ignore .env || echo "⚠️  WARNING"
   
   # Check for .env.example
   ls .env.example || echo "⚠️  Missing example"
   ```

3. **Verify secret usage**
   ```python
   # Good patterns:
   api_key = os.getenv('API_KEY')
   db_password = get_secret('prod/database/password')
   
   # Bad patterns:
   api_key = "sk_live_abc123"  # ❌
   password = "mypassword"  # ❌
   ```

4. **Test secret detection**
   ```bash
   # Run pre-commit on changed files
   pre-commit run --files $(git diff --name-only main)
   ```
```

**Verification:**
- [ ] PR template includes security checklist
- [ ] Reviewer guidelines documented
- [ ] Team trained on secret review process
- [ ] Automated checks in place
- [ ] Process tested with sample PRs

**If This Fails:**
→ If reviewers unsure, provide training session  
→ If checklist too long, create tiered approach (critical vs nice-to-have)  
→ If frequently missed, add automated enforcement  

---

### Step 6: Secure Workflow Execution

**What:** Ensure Code Buddy workflows execute securely without exposing secrets in logs or output.

**How:**
Implement logging best practices and output sanitization.

**Logging Best Practices:**
```python
# workflows/utils/secure_logging.py
"""
Secure logging utilities for Code Buddy workflows.
"""
import re
import logging
from typing import Any, Dict

# Patterns to redact from logs
SECRET_PATTERNS = [
    r'(api[_-]?key["\s:=]+)([a-zA-Z0-9]{20,})',
    r'(password["\s:=]+)([^\s"]+)',
    r'(token["\s:=]+)([a-zA-Z0-9\-._~+/]+=*)',
    r'(Bearer\s+)([a-zA-Z0-9\-._~+/]+=*)',
]

def redact_secrets(text: str) -> str:
    """
    Redact secrets from text for safe logging.
    
    Args:
        text: Text potentially containing secrets
        
    Returns:
        str: Text with secrets redacted
        
    Example:
        >>> redact_secrets("api_key=abc123xyz")
        'api_key=***REDACTED***'
    """
    redacted = text
    
    for pattern in SECRET_PATTERNS:
        redacted = re.sub(pattern, r'\1***REDACTED***', redacted)
    
    return redacted

class SecureLogger:
    """Logger that automatically redacts secrets."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _sanitize(self, msg: str) -> str:
        """Sanitize message before logging."""
        return redact_secrets(str(msg))
    
    def info(self, msg: str, *args, **kwargs):
        """Log info with secret redaction."""
        self.logger.info(self._sanitize(msg), *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log error with secret redaction."""
        self.logger.error(self._sanitize(msg), *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log debug with secret redaction."""
        self.logger.debug(self._sanitize(msg), *args, **kwargs)

# Usage in workflows
logger = SecureLogger(__name__)

def api_call(api_key: str):
    """Make API call with secure logging."""
    # ✅ CORRECT - Secret is redacted
    logger.info(f"Making API call with key: {api_key}")
    # Logs: "Making API call with key: ***REDACTED***"
    
    # ❌ WRONG - Would log actual secret
    # print(f"API Key: {api_key}")  # DON'T DO THIS
```

**Sanitize Command Output:**
```python
# workflows/utils/secure_execution.py
"""
Secure command execution for Code Buddy.
"""
import subprocess
import os
from typing import List, Dict

def execute_safely(
    command: List[str],
    env: Dict[str, str] = None,
    redact_patterns: List[str] = None
) -> tuple[str, str, int]:
    """
    Execute command with secret redaction in output.
    
    Args:
        command: Command to execute
        env: Environment variables (secrets will be redacted in output)
        redact_patterns: Additional patterns to redact
        
    Returns:
        tuple: (stdout, stderr, return_code) with secrets redacted
    """
    # Build environment with secrets
    exec_env = os.environ.copy()
    if env:
        exec_env.update(env)
    
    # Execute command
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=exec_env
    )
    
    # Redact secrets from output
    stdout = result.stdout
    stderr = result.stderr
    
    # Redact any environment variable values that look like secrets
    for key, value in exec_env.items():
        if any(secret_key in key.upper() for secret_key in 
               ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
            stdout = stdout.replace(value, f"***{key}***")
            stderr = stderr.replace(value, f"***{key}***")
    
    # Additional custom redactions
    if redact_patterns:
        for pattern in redact_patterns:
            import re
            stdout = re.sub(pattern, '***REDACTED***', stdout)
            stderr = re.sub(pattern, '***REDACTED***', stderr)
    
    return stdout, stderr, result.returncode

# Usage
stdout, stderr, code = execute_safely(
    ['curl', '-H', f'Authorization: Bearer {api_token}', 'https://api.example.com'],
    env={'API_TOKEN': api_token}
)
# Output will have API_TOKEN redacted
```

**Workflow Execution Best Practices:**
```python
# Example secure workflow
def secure_deployment_workflow():
    """Deploy application with secure secret handling."""
    
    # ✅ Get secrets securely
    from utils.secrets import get_secret
    db_creds = get_secret('prod/database/credentials')
    
    # ✅ Use secure logger
    from utils.secure_logging import SecureLogger
    logger = SecureLogger(__name__)
    
    logger.info("Starting deployment")
    
    # ✅ Execute commands with output sanitization
    from utils.secure_execution import execute_safely
    stdout, stderr, code = execute_safely(
        ['psql', '-h', db_creds['host'], '-U', db_creds['username']],
        env={'PGPASSWORD': db_creds['password']}
    )
    
    if code != 0:
        logger.error(f"Database connection failed: {stderr}")
        # stderr will have password redacted
    else:
        logger.info("Database connected successfully")
    
    # ❌ DON'T DO THIS
    # print(f"Connected with password: {db_creds['password']}")  # Exposed in logs!
    # subprocess.run(['echo', db_creds['password']])  # Exposed in process list!
```

**Verification:**
- [ ] Secure logging utilities created
- [ ] Automatic secret redaction implemented
- [ ] Command execution sanitizes output
- [ ] Workflow logs reviewed for leaks
- [ ] Team trained on secure execution

**If This Fails:**
→ If redaction too aggressive, tune patterns  
→ If secrets still in logs, review logging calls  
→ If performance impact, optimize redaction logic  

---

### Step 7: Document Secret Management Process

**What:** Create comprehensive documentation for team members on proper secret handling with Code Buddy.

**How:**
Clear, accessible documentation ensures consistent practices across the team.

**Team Documentation:**
```markdown
# Code Buddy Secret Management Guide

## Quick Start

### For Developers

1. **Never commit secrets**
   ```bash
   # ❌ WRONG
   git add config/secrets.json
   
   # ✅ CORRECT
   echo "config/secrets.json" >> .gitignore
   ```

2. **Use environment variables**
   ```python
   # ✅ CORRECT
   import os
   api_key = os.getenv('API_KEY')
   
   # ❌ WRONG
   api_key = "sk_live_abc123"
   ```

3. **Use placeholders in examples**
   ```python
   # ✅ CORRECT
   api_key = "<your-api-key>"  # Get from API dashboard
   
   # ❌ WRONG
   api_key = "sk_live_51Hqp2jKl..."
   ```

### For Workflow Authors

1. **Always use secret utilities**
   ```python
   from workflows.utils.secrets import get_env_or_secret
   api_key = get_env_or_secret('API_KEY', 'prod/api:api_key')
   ```

2. **Always use secure logging**
   ```python
   from workflows.utils.secure_logging import SecureLogger
   logger = SecureLogger(__name__)
   logger.info(f"Using API key: {api_key}")  # Auto-redacted
   ```

3. **Test with fake secrets**
   ```python
   # Use test credentials only
   TEST_API_KEY = "test_key_12345"  # Clearly marked as test
   ```

## Where to Store Secrets

| Environment | Method | Example |
|-------------|--------|---------|
| Local Development | .env file | `DB_PASSWORD=dev123` |
| CI/CD | GitHub Secrets | `${{ secrets.API_KEY }}` |
| Staging | AWS Secrets Manager | `get_secret('staging/api')` |
| Production | AWS Secrets Manager | `get_secret('prod/api')` |

## Getting Secrets

### AWS Secrets Manager
```bash
# List secrets
aws secretsmanager list-secrets

# Get specific secret
aws secretsmanager get-secret-value --secret-id prod/api/keys
```

### Local Development
```bash
# Copy example
cp .env.example .env

# Fill in your values
nano .env

# Verify it's gitignored
git check-ignore .env
```

## Common Mistakes

### ❌ Hardcoding Secrets
```python
# DON'T
DATABASE_URL = "postgresql://user:password@host/db"
```

### ✅ Using Environment Variables
```python
# DO
import os
DATABASE_URL = os.getenv('DATABASE_URL')
```

### ❌ Logging Secrets
```python
# DON'T
print(f"API Key: {api_key}")
```

### ✅ Using Secure Logger
```python
# DO
logger.info(f"API Key: {api_key}")  # Auto-redacted
```

### ❌ Committing .env
```bash
# DON'T
git add .env
git commit -m "Add env"
```

### ✅ Gitignoring .env
```bash
# DO
echo ".env" >> .gitignore
git add .env.example
git commit -m "Add env template"
```

## Emergency: I Committed a Secret!

1. **Rotate immediately** (< 5 minutes)
   ```bash
   # Revoke old secret
   aws iam delete-access-key --access-key-id EXPOSED_KEY
   
   # Generate new secret
   aws iam create-access-key --user-name app-user
   ```

2. **Follow incident response**
   See: `workflows/security/secret_incident_solo.md`

3. **Clean git history**
   See: `workflows/security/git_history_cleanup_solo.md`

## Training & Resources

- [Secret Management Workshop] (monthly)
- [Security Best Practices] (wiki)
- [Incident Response Guide] (workflows/security/)
- [Pre-commit Hooks Setup] (docs/pre-commit.md)

## Questions?

- Slack: #security-questions
- Email: security@company.com
- On-call: PagerDuty "Security Team"
```

**Onboarding Checklist:**
```markdown
# New Developer Security Checklist

Before you write your first Code Buddy workflow:

## Setup (30 minutes)
- [ ] Read Secret Management Guide
- [ ] Install pre-commit hooks
- [ ] Set up local .env file
- [ ] Verify AWS Secrets Manager access
- [ ] Test secret retrieval functions
- [ ] Complete security awareness training

## Verification
- [ ] Can retrieve secrets locally
- [ ] Pre-commit hooks block secret commits
- [ ] Know where to find credentials
- [ ] Know who to contact for security questions

## Knowledge Check
- [ ] Why do we never hardcode secrets?
- [ ] What's the difference between .env and .env.example?
- [ ] How do you access secrets in workflows?
- [ ] What do you do if you accidentally commit a secret?
```

**Verification:**
- [ ] Documentation created and accessible
- [ ] Onboarding checklist integrated
- [ ] Team trained on secret management
- [ ] Common mistakes documented
- [ ] Emergency procedures documented

**If This Fails:**
→ If documentation too long, create quick reference guide  
→ If team not reading, conduct training session  
→ If confusion about process, add more examples  

---

### Step 8: Regular Security Audits

**What:** Schedule and conduct periodic security audits of Code Buddy workflows and secret handling practices.

**How:**
Regular reviews catch issues before they become incidents.

**Audit Schedule:**
```yaml
# Security Audit Schedule

Monthly (1st Monday):
  - Review new workflows for secret handling
  - Check pre-commit hook effectiveness
  - Verify no .env files committed
  - Review secret scanner alerts

Quarterly (Every 3 months):
  - Full repository secret scan
  - Audit secret manager access logs
  - Review and rotate credentials
  - Update security documentation
  - Team security training refresher

Annually (January):
  - Comprehensive security assessment
  - Review incident response procedures
  - Update secret patterns and detection rules
  - Evaluate secret management tooling
  - Security policy review
```

**Automated Audit Script:**
```bash
#!/bin/bash
# scripts/security-audit.sh
# Regular security audit for Code Buddy workflows

echo "🔒 Code Buddy Security Audit"
echo "================================"

# 1. Check for committed secrets
echo "1. Scanning for committed secrets..."
gitleaks detect --source . --verbose || echo "⚠️  Secrets detected!"

# 2. Check .env is ignored
echo "2. Verifying .env is gitignored..."
if git check-ignore .env > /dev/null 2>&1; then
  echo "✅ .env is properly ignored"
else
  echo "❌ .env is NOT ignored!"
fi

# 3. Check for .env files in repo
echo "3. Checking for committed .env files..."
if git ls-files | grep -q "\.env$"; then
  echo "❌ Found .env files in repo:"
  git ls-files | grep "\.env$"
else
  echo "✅ No .env files in repo"
fi

# 4. Scan workflow files for patterns
echo "4. Scanning workflow files..."
python scripts/sanitize_workflows.py

# 5. Check pre-commit hooks
echo "5. Verifying pre-commit hooks..."
if [ -f .git/hooks/pre-commit ]; then
  echo "✅ Pre-commit hooks installed"
else
  echo "❌ Pre-commit hooks NOT installed"
fi

# 6. Test secret detection
echo "6. Testing secret detection..."
echo "test_api_key=sk_live_abc123" > /tmp/test-secret.txt
git add /tmp/test-secret.txt 2>&1 | grep -q "blocked" && echo "✅ Secret detection working" || echo "❌ Secret detection failed"
git reset HEAD /tmp/test-secret.txt 2>/dev/null
rm /tmp/test-secret.txt

# 7. Report summary
echo ""
echo "================================"
echo "Audit Complete: $(date)"
echo "================================"
```

**Audit Report Template:**
```markdown
# Code Buddy Security Audit Report

**Date:** 2025-10-26
**Auditor:** Security Team
**Scope:** Code Buddy workflows and secret management

## Findings

### ✅ Passing
- Pre-commit hooks installed on all developer machines
- No .env files in repository
- All workflows use environment variables
- Secret scanner detecting 98% of test cases

### ⚠️  Warnings
- 3 workflows missing .env.example files
- 1 developer bypassing pre-commit hooks
- Secret rotation overdue by 45 days

### ❌ Critical
- None

## Action Items

| Issue | Owner | Due Date | Status |
|-------|-------|----------|--------|
| Add .env.example to 3 workflows | @alice | 2025-10-28 | Open |
| Enforce pre-commit hooks | @bob | 2025-10-27 | Open |
| Rotate production secrets | @security | 2025-10-26 | In Progress |

## Recommendations

1. Implement server-side secret scanning (bypass prevention)
2. Automate secret rotation (90-day schedule)
3. Add security training to onboarding (mandatory)

## Next Audit

**Scheduled:** 2025-11-26
**Focus:** Follow-up on action items + new workflow reviews
```

**Verification:**
- [ ] Audit schedule documented
- [ ] Automated audit script created
- [ ] Audit process tested
- [ ] Report template created
- [ ] Action item tracking system in place

**If This Fails:**
→ If audits too time-consuming, automate more checks  
→ If action items not completed, escalate to management  
→ If team resistance, demonstrate value with examples  

---

## Verification Checklist

After completing this workflow:

- [ ] Code Buddy context and security implications understood
- [ ] Secret storage configured (env vars or secret manager)
- [ ] Workflow examples sanitized (no real secrets)
- [ ] Pre-commit hooks installed and tested
- [ ] Code review checklist implemented
- [ ] Secure logging and execution utilities created
- [ ] Team documentation complete and accessible
- [ ] Security audit schedule established
- [ ] Team trained on secret management practices
- [ ] Emergency response procedures documented

---

## Common Issues & Solutions

### Issue: "Pre-commit hooks slow down workflow"

**Symptoms:**
- Commits take 10+ seconds
- Team members bypass hooks
- Complaints about productivity

**Solution:**
```yaml
# Optimize .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        # Only scan changed files, not entire repo
        args: ['--baseline', '.secrets.baseline']
        # Exclude large or irrelevant files
        exclude: |
          (?x)^(
            package-lock.json|
            poetry.lock|
            yarn.lock|
            .*\.min\.js|
            node_modules/.*
          )$
```

**Prevention:**
- Profile hook performance: `pre-commit run --verbose`
- Exclude large files that don't contain secrets
- Use faster tools (BFG is faster than filter-branch)

---

### Issue: "Team keeps committing .env files"

**Symptoms:**
- .env files appear in commits despite warnings
- Git history has multiple .env commits
- Secrets exposed in repository

**Solution:**
```bash
# 1. Add to global gitignore (all repositories)
git config --global core.excludesfile ~/.gitignore_global
echo ".env" >> ~/.gitignore_global
echo ".env.*" >> ~/.gitignore_global

# 2. Make pre-commit hook strict
cat >> .pre-commit-config.yaml << 'EOF'
  - repo: local
    hooks:
      - id: block-env-files
        name: Block .env files
        entry: bash -c 'git diff --cached --name-only | grep -q "\.env$" && exit 1 || exit 0'
        language: system
        always_run: true
EOF

# 3. Server-side protection (GitHub/GitLab)
# Add push rule to reject .env files
```

**Prevention:**
- Regular training on why .env is dangerous
- Automated detection in CI/CD
- Clear consequences for violations

---

### Issue: "Secrets in logs despite using secure logger"

**Symptoms:**
- API keys visible in application logs
- Passwords in error messages
- Tokens in debug output

**Solution:**
```python
# Enhance redaction patterns
SECRET_PATTERNS = [
    r'(api[_-]?key["\s:=]+)([a-zA-Z0-9]{20,})',
    r'(password["\s:=]+)([^\s"]+)',
    r'(token["\s:=]+)([a-zA-Z0-9\-._~+/]+=*)',
    r'(Bearer\s+)([a-zA-Z0-9\-._~+/]+=*)',
    # Add more specific patterns
    r'(sk_live_)([a-zA-Z0-9]{24,})',
    r'(AKIA)([0-9A-Z]{16})',
]

# Use context managers for temporary secret exposure
from contextlib import contextmanager

@contextmanager
def temporarily_log_secret(secret_value: str):
    """Temporarily allow secret in logs for debugging."""
    original_redact = redact_secrets
    
    def no_redact(text):
        return text
    
    # Disable redaction temporarily
    globals()['redact_secrets'] = no_redact
    
    try:
        yield
    finally:
        # Re-enable redaction
        globals()['redact_secrets'] = original_redact

# Usage (only for debugging, remove before commit)
# with temporarily_log_secret(api_key):
#     logger.debug(f"Full API key: {api_key}")
```

**Prevention:**
- Review all logger.debug() calls
- Never use print() for debugging
- Test logging output in staging first

---

## Examples

### Example 1: Setting Up New Workflow with Secrets

**Context:**
Creating new Code Buddy workflow that needs to access third-party API requiring authentication.

**Execution:**
```python
# workflows/integrations/new_api_workflow.py
"""
New API integration workflow with proper secret handling.
"""
from workflows.utils.secrets import get_env_or_secret
from workflows.utils.secure_logging import SecureLogger

logger = SecureLogger(__name__)

def integrate_third_party_api():
    """
    Integrate with third-party API using secure secret management.
    """
    # Step 1: Get secrets securely
    api_key = get_env_or_secret('THIRD_PARTY_API_KEY', 'prod/third-party:api_key')
    api_secret = get_env_or_secret('THIRD_PARTY_API_SECRET', 'prod/third-party:api_secret')
    
    # Step 2: Initialize client (secrets auto-redacted in logs)
    logger.info(f"Initializing client with key: {api_key}")
    
    from third_party_sdk import Client
    client = Client(api_key=api_key, api_secret=api_secret)
    
    # Step 3: Make API call
    try:
        response = client.fetch_data()
        logger.info("API call successful")
        return response
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise

# Create .env.example
cat > .env.example << 'EOF'
# Third Party API Credentials
# Get from: https://third-party.com/dashboard/api-keys
THIRD_PARTY_API_KEY=<your-api-key>
THIRD_PARTY_API_SECRET=<your-api-secret>
EOF
```

**Result:**
- Workflow uses proper secret management
- No secrets hardcoded
- Logging automatically redacted
- Template provided for developers

---

### Example 2: Migrating Legacy Workflow

**Context:**
Old workflow has hardcoded secrets that need to be migrated to proper secret management.

**Execution:**
```python
# Before (INSECURE)
def legacy_database_backup():
    db_password = "P@ssw0rd123!"  # ❌ Hardcoded
    subprocess.run([
        'pg_dump',
        '-h', 'prod-db.company.com',
        '-U', 'backup_user',
        '-d', 'production',
        '-f', 'backup.sql'
    ], env={'PGPASSWORD': db_password})

# After (SECURE)
from workflows.utils.secrets import get_secret
from workflows.utils.secure_execution import execute_safely
from workflows.utils.secure_logging import SecureLogger

logger = SecureLogger(__name__)

def secure_database_backup():
    # Get credentials from secret manager
    db_creds = get_secret('prod/database/backup-user')
    
    logger.info(f"Backing up database: {db_creds['host']}")
    
    # Execute with output sanitization
    stdout, stderr, code = execute_safely(
        ['pg_dump',
         '-h', db_creds['host'],
         '-U', db_creds['username'],
         '-d', db_creds['database'],
         '-f', 'backup.sql'],
        env={'PGPASSWORD': db_creds['password']}
    )
    
    if code == 0:
        logger.info("Backup completed successfully")
    else:
        logger.error(f"Backup failed: {stderr}")
        # Password is redacted in stderr
```

**Result:**
- Hardcoded secrets removed
- Secret manager integrated
- Secure logging implemented
- Output sanitized

---

## Best Practices

### DO:
✅ Use environment variables or secret managers  
✅ Use `<placeholder>` format in documentation  
✅ Install and enforce pre-commit hooks  
✅ Use secure logging utilities  
✅ Sanitize command output  
✅ Provide .env.example templates  
✅ Document where to get credentials  
✅ Review workflows for secrets before merging  
✅ Rotate secrets regularly (90 days)  
✅ Conduct regular security audits  

### DON'T:
❌ Hardcode secrets in code  
❌ Commit .env files  
❌ Use real secrets in examples  
❌ Log sensitive data  
❌ Share secrets in Slack/email  
❌ Reuse secrets across environments  
❌ Skip pre-commit hooks  
❌ Copy-paste credentials  
❌ Store secrets in comments  
❌ Ignore security warnings  

---

## Related Workflows

**Prerequisites:**
- **development/pre_commit_hooks.md** - Setting up pre-commit hooks
- **development/environment_initialization.md** - Environment setup

**Next Steps:**
- **secret_incident_solo.md** - What to do if secret is exposed
- **git_history_cleanup_solo.md** - Removing secrets from git history

**Related:**
- **security/secret_management_solo.md** - General secret management guide
- **devops/cicd_pipeline_setup.md** - Managing secrets in CI/CD

---

## Tags
`security` `code-buddy` `secrets` `best-practices` `mcp` `credentials`
