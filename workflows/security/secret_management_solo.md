---
title: Secret Management (Solo Developer)
description: Practical workflow for solo developers to securely manage API keys, passwords, and other secrets without enterprise tooling
category: Security
subcategory: Secrets Management
tags: [security, secrets, credentials, environment-variables, solo-developer]
technologies: [Git, dotenv, 1Password, Bitwarden, GitHub Secrets]
complexity: intermediate
estimated_time_minutes: 45
use_cases: [Securing API keys, Managing environment variables, Preventing secret leaks, Setting up new projects, Rotating credentials]
problem_statement: Solo developers need to manage secrets securely without enterprise secret management infrastructure, balancing security with development velocity
author: Code Buddy Team
---

# Secret Management (Solo Developer)

**ID:** sec-004  
**Category:** Security  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 45-60 minutes (initial setup)  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Establish secure practices for managing API keys, passwords, and other secrets as a solo developer.

**Why:**
- Prevent credential leaks to public repositories
- Enable secure credential sharing across devices
- Facilitate key rotation without code changes
- Protect against unauthorized access
- Maintain audit trail of secret access

**When to use:**
- Starting a new project
- Setting up API integrations
- Onboarding to existing projects
- After a credential leak
- Rotating expired credentials

---

## Prerequisites

**Required:**
- [ ] Password manager installed (1Password, Bitwarden, LastPass)
- [ ] Git installed and configured
- [ ] Code editor (VS Code, PyCharm, etc.)
- [ ] Command line access
- [ ] Project repository created

**Recommended:**
```bash
# Install useful tools
# For .env file management
npm install -g dotenv-cli

# For secret scanning
brew install gitleaks  # macOS
# or: https://github.com/gitleaks/gitleaks/releases

# For safe secret generation
brew install pwgen
```

**Check before starting:**
```bash
# Verify git is configured
git config --get user.name
git config --get user.email

# Check for existing .gitignore
ls -la .gitignore

# Verify password manager CLI
op whoami  # 1Password
bw login   # Bitwarden
```

---

## Implementation Steps

### Step 1: Never Commit Secrets to Git

**What:** Set up protections to prevent accidental secret commits.

**How:**

**Create comprehensive .gitignore:**
```bash
# Create/update .gitignore
cat >> .gitignore << 'EOF'
# Environment variables
.env
.env.local
.env.*.local
.envrc

# IDE files with secrets
.vscode/settings.json
.idea/workspace.xml

# Cloud provider credentials
.aws/credentials
.gcloud/credentials.json
gcloud-key.json
serviceaccount.json

# SSH keys
*.pem
*.key
id_rsa
id_ed25519

# Database dumps (may contain sensitive data)
*.sql
*.dump

# Certificates
*.crt
*.cer
*.pfx

# Secret management
secrets.yml
.secrets
vault.json

# Application-specific
config/secrets.yml
config/credentials.yml.enc  # Keep the encrypted version
EOF

# Commit .gitignore immediately
git add .gitignore
git commit -m "Add comprehensive .gitignore for secrets"
```

**Install pre-commit hook:**
```bash
# Install gitleaks pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Scan for secrets before commit

echo "🔍 Scanning for secrets..."
gitleaks detect --verbose --no-git

if [ $? -ne 0 ]; then
    echo "❌ Secret detected! Commit blocked."
    echo "Remove the secret and try again."
    exit 1
fi

echo "✅ No secrets detected"
exit 0
EOF

chmod +x .git/hooks/pre-commit

# Test it
echo "API_KEY=sk_test_1234567890" >> test.txt
git add test.txt
git commit -m "test"  # Should fail
rm test.txt
```

**Alternative: Use pre-commit framework:**
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=500']
EOF

# Install hooks
pre-commit install
```

**Verification:**
- [ ] .gitignore created with secret patterns
- [ ] Pre-commit hook installed and working
- [ ] Test commit with fake secret blocked
- [ ] .gitignore committed to repository

**If This Fails:**
→ If gitleaks not installed, use simpler hook that checks for common patterns
→ If pre-commit fails, at least add .env to .gitignore

---

### Step 2: Use Environment Variables

**What:** Store secrets in environment variables, not code.

**How:**

**Create .env file:**
```bash
# .env (NEVER commit this file)
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# API Keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
STRIPE_API_KEY=sk_live_yyyyyyyyyyyyyyyyyyy
SENDGRID_API_KEY=SG.zzzzzzzzzzz

# Authentication
JWT_SECRET=your-super-secret-jwt-key-here
SESSION_SECRET=another-random-secret-string

# External Services
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Feature Flags
FEATURE_BETA_ENABLED=false
DEBUG=false
```

**Create .env.example (for documentation):**
```bash
# .env.example (SAFE to commit)
# Copy this to .env and fill in your secrets

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API Keys
OPENAI_API_KEY=sk-your-key-here
STRIPE_API_KEY=sk_live_your-key-here
SENDGRID_API_KEY=SG.your-key-here

# Authentication
JWT_SECRET=generate-a-random-string
SESSION_SECRET=generate-another-random-string

# External Services
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# Feature Flags
FEATURE_BETA_ENABLED=false
DEBUG=false
```

**Load environment variables in your application:**

**Python:**
```python
# requirements.txt
python-dotenv

# config.py
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access secrets
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate required secrets
required_secrets = [
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "JWT_SECRET"
]

for secret in required_secrets:
    if not os.getenv(secret):
        raise ValueError(f"Missing required secret: {secret}")
```

**Node.js:**
```javascript
// package.json dependencies
// "dotenv": "^16.0.0"

// config.js
require('dotenv').config();

const config = {
  database: {
    url: process.env.DATABASE_URL
  },
  api: {
    openai: process.env.OPENAI_API_KEY,
    stripe: process.env.STRIPE_API_KEY
  },
  auth: {
    jwtSecret: process.env.JWT_SECRET
  }
};

// Validate
const required = ['DATABASE_URL', 'OPENAI_API_KEY', 'JWT_SECRET'];
required.forEach(key => {
  if (!process.env[key]) {
    throw new Error(`Missing required env var: ${key}`);
  }
});

module.exports = config;
```

**Verification:**
- [ ] .env file created and populated
- [ ] .env in .gitignore
- [ ] .env.example committed (without real secrets)
- [ ] Application loads secrets from environment
- [ ] Required secrets validated on startup

---

### Step 3: Store Secrets in Password Manager

**What:** Use a password manager as your source of truth for secrets.

**How:**

**Using 1Password:**
```bash
# Install 1Password CLI
# https://developer.1password.com/docs/cli/get-started/

# Sign in
op signin

# Create vault for project secrets
op vault create "MyProject"

# Store secret
op item create \
  --category=password \
  --title="OpenAI API Key" \
  --vault="MyProject" \
  "password[password]=sk-xxxxxxxxxxxx" \
  "notes[notes]=Used for GPT-4 integration"

# Retrieve secret
op item get "OpenAI API Key" --vault="MyProject" --fields password

# Generate secure secret
op item create \
  --category=password \
  --title="JWT Secret" \
  --vault="MyProject" \
  --generate-password='letters,digits,symbols,32'
```

**Using Bitwarden:**
```bash
# Install Bitwarden CLI
npm install -g @bitwarden/cli

# Login
bw login

# Unlock and save session
export BW_SESSION=$(bw unlock --raw)

# Create secret
bw create item "{
  \"organizationId\": null,
  \"collectionIds\": null,
  \"folderId\": null,
  \"type\": 1,
  \"name\": \"OpenAI API Key\",
  \"notes\": \"Used for GPT-4 integration\",
  \"login\": {
    \"username\": \"api_key\",
    \"password\": \"sk-xxxxxxxxxxxx\"
  }
}"

# Retrieve secret
bw get password "OpenAI API Key"

# Generate random password
bw generate -uln --length 32
```

**Sync secrets to .env from password manager:**
```bash
# Create sync script: scripts/sync-secrets.sh
#!/bin/bash
set -e

echo "🔐 Syncing secrets from 1Password..."

# Check if signed in
if ! op whoami &> /dev/null; then
    echo "❌ Not signed in to 1Password"
    echo "Run: op signin"
    exit 1
fi

# Generate .env from 1Password
cat > .env << EOF
# Auto-generated from 1Password
# Last updated: $(date)

DATABASE_URL=$(op item get "Database URL" --vault="MyProject" --fields password)
OPENAI_API_KEY=$(op item get "OpenAI API Key" --vault="MyProject" --fields password)
STRIPE_API_KEY=$(op item get "Stripe API Key" --vault="MyProject" --fields password)
JWT_SECRET=$(op item get "JWT Secret" --vault="MyProject" --fields password)
EOF

echo "✅ Secrets synced to .env"
echo "⚠️  Remember: .env is in .gitignore"
```

**Make script executable:**
```bash
chmod +x scripts/sync-secrets.sh
./scripts/sync-secrets.sh
```

**Verification:**
- [ ] Secrets stored in password manager
- [ ] Can retrieve secrets programmatically
- [ ] Sync script created and tested
- [ ] Multiple devices can access secrets
- [ ] Secrets backed up automatically

---

### Step 4: Rotate Secrets Regularly

**What:** Change secrets periodically to limit exposure window.

**How:**

**Rotation schedule:**
```
🔄 Rotation Frequency:
- High risk (prod API keys): 90 days
- Medium risk (dev API keys): 180 days
- Low risk (feature flags): As needed
- Emergency: Immediately after suspected leak
```

**Rotation checklist:**
```markdown
For each secret:
1. [ ] Generate new secret
2. [ ] Update password manager
3. [ ] Deploy to production (if applicable)
4. [ ] Verify new secret works
5. [ ] Revoke old secret
6. [ ] Update .env.example documentation
7. [ ] Notify team (if applicable)
```

**Example: Rotate OpenAI API Key:**
```bash
# 1. Generate new key at OpenAI dashboard
# https://platform.openai.com/api-keys

# 2. Update password manager
op item edit "OpenAI API Key" \
  "password[password]=sk-new-key-here" \
  --vault="MyProject"

# 3. Sync to .env
./scripts/sync-secrets.sh

# 4. Test in staging
export OPENAI_API_KEY=$(op item get "OpenAI API Key" --vault="MyProject" --fields password)
python -c "import openai; print(openai.models.list())"

# 5. Update production (if using)
gh secret set OPENAI_API_KEY --body "sk-new-key-here"
# Or update in hosting provider (Heroku, Railway, etc.)

# 6. Verify production works
curl https://api.myapp.com/health

# 7. Delete old key from OpenAI dashboard
```

**Set rotation reminders:**
```bash
# Add to calendar
# Every 90 days: "Rotate production API keys"
# Every 180 days: "Rotate development secrets"

# Or use script with notification
# scripts/check-secret-age.sh
#!/bin/bash
LAST_ROTATION=$(op item get "OpenAI API Key" --vault="MyProject" --fields "Modified")
DAYS_AGO=$(( ($(date +%s) - $(date -d "$LAST_ROTATION" +%s)) / 86400 ))

if [ $DAYS_AGO -gt 90 ]; then
    echo "⚠️  OpenAI API Key is $DAYS_AGO days old - time to rotate!"
fi
```

**Verification:**
- [ ] Rotation schedule established
- [ ] Reminders set
- [ ] Rotation process tested
- [ ] Old secrets revoked after rotation

---

### Step 5: Handle Secrets in CI/CD

**What:** Securely provide secrets to automated builds and deployments.

**How:**

**GitHub Actions:**
```bash
# Add secrets via GitHub web UI or CLI
gh secret set OPENAI_API_KEY --body "sk-xxxx"
gh secret set DATABASE_URL --body "postgresql://..."

# Use in workflow
# .github/workflows/test.yml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python -m pytest
```

**GitLab CI:**
```bash
# Add via GitLab UI: Settings > CI/CD > Variables

# Use in .gitlab-ci.yml
test:
  stage: test
  script:
    - pytest
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
    DATABASE_URL: $DATABASE_URL
```

**Deployment platforms:**
```bash
# Heroku
heroku config:set OPENAI_API_KEY=sk-xxxx --app myapp
heroku config:set DATABASE_URL=postgresql://... --app myapp

# Railway
railway variables set OPENAI_API_KEY=sk-xxxx
railway variables set DATABASE_URL=postgresql://...

# Vercel
vercel env add OPENAI_API_KEY production
vercel env add DATABASE_URL production

# AWS (using Parameter Store)
aws ssm put-parameter \
  --name "/myapp/prod/OPENAI_API_KEY" \
  --value "sk-xxxx" \
  --type "SecureString"
```

**Verification:**
- [ ] Secrets configured in CI/CD
- [ ] Tests pass with CI secrets
- [ ] Production deployments use secure secrets
- [ ] Secrets not logged in CI output

---

### Step 6: Respond to Secret Leaks

**What:** Quick response plan if secrets are accidentally committed.

**How:**

**If you catch it BEFORE pushing:**
```bash
# Remove from staging
git reset HEAD~1

# Or amend commit
git commit --amend

# Clean file
rm .env
./scripts/sync-secrets.sh
```

**If you catch it AFTER pushing (not yet public):**
```bash
# 1. IMMEDIATELY rotate the leaked secret
# (See Step 4 for rotation process)

# 2. Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (if private repo only)
git push origin --force --all

# 4. Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**If secret is in public repository:**
```bash
# 1. IMMEDIATELY revoke the secret
# - API provider dashboard
# - Generate new key
# - Update password manager

# 2. Use GitHub's official tool
# https://github.com/newren/git-filter-repo
pip install git-filter-repo

git filter-repo --invert-paths --path .env

# 3. Force push
git push origin --force --all
git push origin --force --tags

# 4. Contact GitHub support
# https://support.github.com
# Request cache invalidation

# 5. Monitor for abuse
# Check API usage dashboards
# Watch for unauthorized charges
```

**See also:** [[sec-002]](./git_history_cleanup_solo.md) and [[sec-003]](./secret_incident_solo.md)

**Verification:**
- [ ] Leaked secret rotated
- [ ] Git history cleaned
- [ ] No secret in any commit
- [ ] Force push completed
- [ ] Monitoring for abuse

---

## Verification Checklist

After completing this workflow:

- [ ] .gitignore blocks all common secret patterns
- [ ] Pre-commit hook prevents secret commits
- [ ] All secrets in .env file
- [ ] .env file in .gitignore
- [ ] .env.example documented and committed
- [ ] Secrets stored in password manager
- [ ] Sync script working
- [ ] Rotation schedule established
- [ ] CI/CD secrets configured
- [ ] Leak response plan documented

---

## Common Issues & Solutions

### Issue: Accidentally Committed .env File

**Symptoms:**
- .env file in git history
- Secrets visible in commits

**Solution:**
```bash
# If not yet pushed
git rm --cached .env
git commit --amend -m "Remove .env file"

# If already pushed
git filter-repo --invert-paths --path .env
git push --force

# Then rotate all secrets in that file
./scripts/rotate-all-secrets.sh
```

**Prevention:**
- Pre-commit hooks
- Regular .gitignore audits
- Team training

---

### Issue: Lost Access to Password Manager

**Symptoms:**
- Can't retrieve secrets
- Locked out of projects

**Solution:**
```markdown
Recovery plan:
1. Use password manager recovery key
2. Check .env files on other computers
3. Regenerate secrets from service providers
4. Update password manager
5. Sync to all devices

Prevention:
- Store recovery key safely (offline)
- Backup vault regularly
- Document service providers for regeneration
```

---

### Issue: Secret Works Locally But Not in Production

**Symptoms:**
- Local development fine
- Production fails with auth errors

**Solution:**
```bash
# Check if secret exists in production
heroku config:get OPENAI_API_KEY

# Check if secret format correct
# (no quotes, spaces, newlines)

# Redeploy with fresh secrets
heroku config:set OPENAI_API_KEY="$(op item get 'OpenAI API Key' --fields password)"

# Verify application restart
heroku ps:restart
```

---

## Examples

### Example 1: New Project Setup

**Context:** Starting a new Python FastAPI project.

**Execution:**
```bash
# 1. Create project
mkdir my-project && cd my-project
git init

# 2. Create .gitignore
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
echo ".env" >> .gitignore

# 3. Install pre-commit
pip install pre-commit
pre-commit sample-config > .pre-commit-config.yaml
# Add gitleaks hook
pre-commit install

# 4. Create .env and .env.example
cat > .env << 'EOF'
DATABASE_URL=postgresql://localhost/mydb
OPENAI_API_KEY=sk-xxxx
EOF

cat > .env.example << 'EOF'
DATABASE_URL=postgresql://localhost/dbname
OPENAI_API_KEY=sk-your-key-here
EOF

# 5. Store in 1Password
op item create --category=password \
  --title="MyProject Database" \
  "password[password]=postgresql://localhost/mydb"

op item create --category=password \
  --title="MyProject OpenAI" \
  "password[password]=sk-xxxx"

# 6. Commit
git add .gitignore .env.example .pre-commit-config.yaml
git commit -m "Initial setup with secret management"
```

**Result:** Secure project foundation established.

---

## Best Practices

### DO:
✅ Use .env files for local development
✅ Store secrets in password manager
✅ Rotate secrets regularly (90-180 days)
✅ Use different secrets for dev/staging/prod
✅ Generate random secrets (pwgen, 1Password)
✅ Document secrets in .env.example
✅ Use pre-commit hooks
✅ Audit git history for leaked secrets
✅ Revoke secrets immediately after leaks

### DON'T:
❌ Commit .env files
❌ Share secrets via email/Slack
❌ Use same secret across environments
❌ Hardcode secrets in code
❌ Store secrets in comments
❌ Skip secret rotation
❌ Ignore security warnings
❌ Use weak/predictable secrets

---

## Related Workflows

**Prerequisites:**
- Git repository initialized
- Password manager account created

**Next Steps:**
- [[sec-001]](./code_buddy_secret_rules.md) - Code Buddy Secret Management Rules
- [[sec-002]](./git_history_cleanup_solo.md) - Git History Cleanup (if leak occurs)
- [[sec-003]](./secret_incident_solo.md) - Secret Incident Response

**Complementary:**
- [[dev-022]](../development/environment_initialization.md) - Environment Initialization
- [[dev-023]](../development/new_repo_scaffolding.md) - New Repo Scaffolding

**Alternatives:**
- HashiCorp Vault (for teams/complex needs)
- AWS Secrets Manager (cloud-native)
- Doppler (secret management service)

---

## Tags
`security` `secrets` `credentials` `environment-variables` `solo-developer` `api-keys` `passwords` `dotenv`
