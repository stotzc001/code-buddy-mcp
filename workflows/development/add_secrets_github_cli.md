# Add Secrets via GitHub CLI

**ID:** dev-021  
**Category:** Development  
**Priority:** MEDIUM  
**Complexity:** Simple  
**Estimated Time:** 15-30 minutes  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Systematic workflow for securely managing repository secrets using GitHub CLI

**Why:** Proper secret management prevents credential exposure, enables secure CI/CD pipelines, and maintains security compliance across repositories without manual console access

**When to use:**
- Setting up CI/CD pipeline secrets
- Rotating API keys and tokens
- Configuring deployment credentials
- Managing secrets across multiple repositories
- Automating secret provisioning

---

## Prerequisites

**Required:**
- [ ] GitHub CLI installed (`gh --version`)
- [ ] GitHub account with repository admin access
- [ ] Authenticated with GitHub (`gh auth status`)
- [ ] Target repository exists

**Check before starting:**
```bash
# Verify GitHub CLI installation
gh --version
# Expected: gh version 2.0.0 or higher

# Check authentication status
gh auth status
# Expected: Logged in to github.com as [username]

# Verify repository access
gh repo view owner/repo
# Expected: Repository details displayed
```

---

## Implementation Steps

### Step 1: Authenticate GitHub CLI

**What:** Establish secure authenticated session with GitHub

**How:**
If not already authenticated, log in using one of these methods:
- Web-based authentication (recommended)
- Personal access token
- SSH key authentication

**Code/Commands:**
```bash
# Interactive web authentication (recommended)
gh auth login

# Follow prompts:
# ? What account do you want to log into? GitHub.com
# ? What is your preferred protocol for Git operations? HTTPS
# ? Authenticate Git with your GitHub credentials? Yes
# ? How would you like to authenticate? Login with a web browser

# Or authenticate with token
echo "ghp_YOUR_TOKEN" | gh auth login --with-token

# Verify authentication
gh auth status
```

**Verification:**
- [ ] Authentication successful
- [ ] Correct GitHub account shown
- [ ] Git operations authenticated
- [ ] API access confirmed

**If This Fails:**
→ Check internet connectivity
→ Verify token has correct scopes (repo, workflow, admin:repo_hook)
→ Clear cached credentials: `gh auth logout && gh auth login`

---

### Step 2: Identify Secret Requirements

**What:** Catalog all secrets needed for your repository

**How:**
Review your workflows, configurations, and deployment needs to identify all required secrets. Document their purpose and required scope.

**Code/Commands:**
```bash
# List existing secrets in repository
gh secret list --repo owner/repo

# Review workflow files that use secrets
cat .github/workflows/*.yml | grep -A 2 "secrets\."

# Common secret categories to consider:
# - API Keys (third-party services)
# - Database credentials
# - Cloud provider keys (AWS, Azure, GCP)
# - Deploy keys and tokens
# - Signing certificates
# - Webhook secrets
```

**Verification:**
- [ ] All workflow dependencies identified
- [ ] Secret names documented
- [ ] Access scopes determined
- [ ] Existing secrets reviewed

**If This Fails:**
→ Review CI/CD workflow files for secret references
→ Check deployment documentation
→ Consult with team about required integrations

---

### Step 3: Prepare Secret Values Securely

**What:** Generate or retrieve secret values using secure methods

**How:**
Never hardcode secrets in scripts. Use secure generation methods and temporary storage.

**Code/Commands:**
```bash
# Generate strong random secrets
openssl rand -hex 32  # For API tokens
openssl rand -base64 32  # For passwords

# Read secret from secure file (not in git)
SECRET_VALUE=$(cat ~/.secrets/api_key.txt)

# Or read from password manager
SECRET_VALUE=$(op read "op://vault/item/field")  # 1Password
SECRET_VALUE=$(bw get password "item-name")  # Bitwarden

# For multi-line secrets (certificates, keys)
SECRET_VALUE=$(cat <<'EOF'
-----BEGIN RSA PRIVATE KEY-----
[your key content]
-----END RSA PRIVATE KEY-----
EOF
)

# Verify secret is not empty
[ -z "$SECRET_VALUE" ] && echo "ERROR: Secret value is empty" || echo "Secret loaded"
```

**Verification:**
- [ ] Secret values generated securely
- [ ] No secrets in shell history (use space prefix)
- [ ] Values not displayed in terminal
- [ ] Multi-line secrets properly formatted

**If This Fails:**
→ Use `set +o history` before handling secrets, `set -o history` after
→ Clear shell history: `history -c`
→ Never echo secret values for debugging

---

### Step 4: Add Secret to Repository

**What:** Store secret securely in GitHub repository settings

**How:**
Use GitHub CLI to add secrets without manual console access. Secrets are encrypted before storage.

**Code/Commands:**
```bash
# Add a secret from command line (interactive, won't show in history)
gh secret set SECRET_NAME --repo owner/repo

# Add secret from variable (use with caution)
echo "$SECRET_VALUE" | gh secret set SECRET_NAME --repo owner/repo

# Add secret from file
gh secret set SECRET_NAME --repo owner/repo < secret_file.txt

# Add secret for organization (requires org admin)
gh secret set SECRET_NAME --org organization-name

# Add secret with specific visibility
gh secret set SECRET_NAME --org org-name --visibility selected \
  --repos "repo1,repo2,repo3"

# Common secrets to add:
echo "$AWS_ACCESS_KEY_ID" | gh secret set AWS_ACCESS_KEY_ID --repo owner/repo
echo "$AWS_SECRET_ACCESS_KEY" | gh secret set AWS_SECRET_ACCESS_KEY --repo owner/repo
echo "$DATABASE_URL" | gh secret set DATABASE_URL --repo owner/repo
```

**Verification:**
- [ ] Secret added successfully
- [ ] Secret appears in list: `gh secret list --repo owner/repo`
- [ ] No plaintext secret in shell history
- [ ] Correct repository targeted

**If This Fails:**
→ Verify repository admin permissions
→ Check repository ownership
→ Ensure secret name follows naming conventions (UPPERCASE_SNAKE_CASE)
→ Verify no conflicting environment variables

---

### Step 5: Add Multiple Secrets via Script

**What:** Automate adding multiple secrets for consistent deployment

**How:**
Create a reusable script that reads secrets from a secure source and adds them all at once.

**Code/Commands:**
```bash
#!/bin/bash
# add_secrets.sh - Bulk secret provisioning

set -euo pipefail

REPO="owner/repo"
SECRETS_FILE=".secrets.env"  # NOT in git!

# Check prerequisites
if [ ! -f "$SECRETS_FILE" ]; then
  echo "Error: $SECRETS_FILE not found"
  exit 1
fi

# Load and add secrets
while IFS='=' read -r name value; do
  # Skip comments and empty lines
  [[ "$name" =~ ^#.*$ ]] && continue
  [ -z "$name" ] && continue
  
  echo "Adding secret: $name"
  echo "$value" | gh secret set "$name" --repo "$REPO"
done < "$SECRETS_FILE"

echo "✅ All secrets added successfully"

# Cleanup
unset name value
```

**Example .secrets.env file (NEVER commit this):**
```bash
# .secrets.env - Add to .gitignore
API_KEY=your-api-key-here
DATABASE_URL=postgresql://user:pass@host:5432/db
DEPLOY_TOKEN=ghp_abcdefghij123456789
```

**Verification:**
- [ ] Script executes without errors
- [ ] All secrets listed: `gh secret list`
- [ ] .secrets.env in .gitignore
- [ ] No secrets committed to git

**If This Fails:**
→ Check file permissions on .secrets.env
→ Verify no special characters breaking parsing
→ Test with a single secret first
→ Check for trailing whitespace in secret values

---

### Step 6: Configure Secret Access for Workflows

**What:** Update GitHub Actions workflows to use the new secrets

**How:**
Reference secrets in workflow files using the correct syntax.

**Code/Commands:**
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Use secrets in environment variables
      - name: Deploy to production
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          # Deploy script has access to secrets via env vars
          ./deploy.sh
      
      # Use secrets in action inputs
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      # Mask secrets in logs (automatic but can be explicit)
      - name: Use secret in command
        run: |
          echo "::add-mask::${{ secrets.DEPLOY_TOKEN }}"
          curl -H "Authorization: Bearer ${{ secrets.DEPLOY_TOKEN }}" \
            https://api.example.com/deploy
```

**Verification:**
- [ ] Workflow syntax valid: `gh workflow view workflow-name`
- [ ] Test workflow run succeeds
- [ ] Secrets not exposed in logs
- [ ] All required secrets accessible

**If This Fails:**
→ Check secret names match exactly (case-sensitive)
→ Verify workflow has access to repository secrets
→ Test with a simple echo workflow first (be careful not to leak secrets)
→ Check branch protection rules

---

### Step 7: Rotate and Update Secrets

**What:** Update existing secrets when credentials change or rotate periodically

**How:**
GitHub CLI allows updating secrets without deleting and recreating.

**Code/Commands:**
```bash
# Update existing secret (same command as adding)
echo "$NEW_SECRET_VALUE" | gh secret set SECRET_NAME --repo owner/repo

# Rotate API key workflow
OLD_KEY=$(gh secret get API_KEY --repo owner/repo 2>/dev/null || echo "")
NEW_KEY=$(openssl rand -hex 32)
echo "$NEW_KEY" | gh secret set API_KEY --repo owner/repo

# Bulk rotation script
for secret in API_KEY DATABASE_PASSWORD DEPLOY_TOKEN; do
  echo "Rotating $secret..."
  NEW_VALUE=$(generate_secure_value)  # Your generation logic
  echo "$NEW_VALUE" | gh secret set "$secret" --repo owner/repo
  
  # Update external services
  update_external_service "$secret" "$NEW_VALUE"
done

# Delete secret if no longer needed
gh secret delete SECRET_NAME --repo owner/repo

# Confirm deletion
gh secret list --repo owner/repo | grep -v "SECRET_NAME"
```

**Verification:**
- [ ] Secret updated successfully
- [ ] Workflow runs use new value
- [ ] External services updated
- [ ] Old credentials revoked

**If This Fails:**
→ Verify new secret value is valid
→ Test in non-production first
→ Keep old secret until new one verified
→ Check dependent services updated

---

### Step 8: Verify and Document

**What:** Confirm all secrets are properly configured and document for team

**How:**
Create comprehensive documentation of what secrets exist and their purpose.

**Code/Commands:**
```bash
# List all secrets with descriptions
gh secret list --repo owner/repo

# Create secrets documentation (without values!)
cat > SECRETS.md <<'EOF'
# Repository Secrets

## Production Secrets

### AWS_ACCESS_KEY_ID
- **Purpose:** AWS S3 bucket access for deployments
- **Rotation:** Every 90 days
- **Owner:** DevOps team
- **Used in:** `.github/workflows/deploy.yml`

### DATABASE_URL
- **Purpose:** Production database connection
- **Rotation:** On security incidents
- **Owner:** Backend team
- **Format:** `postgresql://user:pass@host:5432/dbname`

### DEPLOY_TOKEN
- **Purpose:** GitHub deployment token
- **Rotation:** Every 6 months
- **Owner:** CI/CD admin
- **Scopes:** `repo`, `workflow`

## Development Secrets

[Document non-production secrets]
EOF

# Add to git (no actual secret values!)
git add SECRETS.md
git commit -m "docs: Add secrets documentation"

# Test workflow with secrets
gh workflow run deploy.yml --ref main
gh run watch
```

**Verification:**
- [ ] All secrets documented
- [ ] Workflow runs successfully
- [ ] Team aware of secret locations
- [ ] Rotation schedule documented
- [ ] No secret values in documentation

**If This Fails:**
→ Review workflow logs for secret-related errors
→ Verify all secrets are set correctly
→ Check secret names in workflow files
→ Ensure documentation is accessible to team

---

## Verification Checklist

After completing this workflow:

- [ ] All required secrets added to repository
- [ ] Secrets not exposed in logs or git history
- [ ] Workflows successfully use secrets
- [ ] Documentation created (without secret values)
- [ ] Team informed about secret management process
- [ ] .secrets.env file in .gitignore
- [ ] No plaintext secrets in scripts or configs
- [ ] Rotation schedule established

---

## Common Issues & Solutions

### Issue: "Resource not accessible by integration" Error

**Symptoms:**
- Secret creation fails with permissions error
- `gh secret set` returns 403 Forbidden

**Solution:**
```bash
# Verify you have admin access
gh api repos/owner/repo --jq '.permissions'

# Re-authenticate with correct scopes
gh auth refresh -s repo,admin:repo_hook

# Check if using fine-grained token with wrong permissions
gh auth status  # Verify token type
```

**Prevention:**
Ensure GitHub token or authentication has `repo` and `admin:repo_hook` scopes

---

### Issue: Secret Not Available in Workflow

**Symptoms:**
- Workflow fails with "secret not found"
- Environment variable is empty in Actions

**Solution:**
```bash
# Verify secret exists
gh secret list --repo owner/repo | grep SECRET_NAME

# Check exact name (case-sensitive)
# In workflow: ${{ secrets.API_KEY }}
# Must match secret name exactly

# For organization secrets, check visibility
gh secret list --org org-name

# Verify repository has access to org secret
gh api orgs/org-name/actions/secrets/SECRET_NAME/repositories
```

**Prevention:**
- Use consistent naming (UPPERCASE_SNAKE_CASE)
- Document all secret names
- Test in development workflow first

---

### Issue: Multi-line Secret Formatting Issues

**Symptoms:**
- Certificate or key files don't work
- Line breaks lost or corrupted

**Solution:**
```bash
# Method 1: Use heredoc
gh secret set CERT_FILE --repo owner/repo <<'EOF'
-----BEGIN CERTIFICATE-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
[certificate content]
-----END CERTIFICATE-----
EOF

# Method 2: Base64 encode
base64 -w 0 cert.pem | gh secret set CERT_FILE_B64 --repo owner/repo

# In workflow, decode:
# echo "${{ secrets.CERT_FILE_B64 }}" | base64 -d > cert.pem

# Method 3: From file directly
gh secret set CERT_FILE --repo owner/repo < cert.pem
```

**Prevention:**
- Always test multi-line secrets in workflows
- Consider base64 encoding for complex formats
- Document decoding steps in workflow

---

### Issue: Secret Exposed in Git History

**Symptoms:**
- Secret accidentally committed
- Found in git log or old commits

**Solution:**
```bash
# IMMEDIATE ACTIONS:
# 1. Revoke the exposed secret immediately
gh secret delete SECRET_NAME --repo owner/repo

# 2. Generate and add new secret
NEW_SECRET=$(openssl rand -hex 32)
echo "$NEW_SECRET" | gh secret set SECRET_NAME --repo owner/repo

# 3. Remove from git history (DESTRUCTIVE)
# Use BFG Repo-Cleaner or git-filter-repo
git filter-repo --invert-paths --path path/to/secret/file

# 4. Force push (coordinate with team!)
git push origin --force --all

# 5. Notify all team members to re-clone
```

**Prevention:**
- Always use .gitignore for secret files
- Add pre-commit hooks to detect secrets
- Use tools like `git-secrets` or `gitleaks`
- Never put secrets in config files committed to git

---

## Examples

### Example 1: Setting Up CI/CD Secrets for New Project

**Context:** New project needs AWS and database secrets for deployment

**Execution:**
```bash
# Create secrets file (not in git!)
cat > .secrets.env <<'EOF'
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DATABASE_URL=postgresql://dbuser:dbpass@localhost:5432/mydb
GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz123456
EOF

# Add to .gitignore
echo ".secrets.env" >> .gitignore

# Add all secrets
while IFS='=' read -r name value; do
  echo "$value" | gh secret set "$name" --repo myorg/myproject
done < .secrets.env

# Verify
gh secret list --repo myorg/myproject

# Clean up
rm .secrets.env  # or keep in secure location
```

**Result:** All secrets added, workflow can deploy to AWS and access database

---

### Example 2: Rotating Secrets Across Multiple Repositories

**Context:** Security audit requires rotating API key across 10 repositories

**Execution:**
```bash
#!/bin/bash
# rotate_api_key.sh

REPOS=(
  "myorg/repo1"
  "myorg/repo2"
  "myorg/repo3"
  # ... add all repos
)

# Generate new key
NEW_KEY=$(curl -X POST https://api.example.com/keys/rotate \
  -H "Authorization: Bearer $OLD_KEY" \
  --silent | jq -r '.key')

# Update all repositories
for repo in "${REPOS[@]}"; do
  echo "Updating $repo..."
  echo "$NEW_KEY" | gh secret set API_KEY --repo "$repo"
  
  # Trigger workflow to test
  gh workflow run test.yml --repo "$repo"
done

echo "✅ Key rotated across ${#REPOS[@]} repositories"

# Verify old key is revoked
curl https://api.example.com/keys/verify \
  -H "Authorization: Bearer $OLD_KEY" || echo "Old key successfully revoked"
```

**Result:** API key rotated across all repositories with zero downtime

---

### Example 3: Organization-Wide Secret with Selective Access

**Context:** Shared API key needed for specific repositories only

**Execution:**
```bash
# Add organization secret
echo "$SHARED_API_KEY" | gh secret set SHARED_API_KEY \
  --org myorg \
  --visibility selected \
  --repos "frontend-app,backend-api,mobile-app"

# Verify repository access
gh api orgs/myorg/actions/secrets/SHARED_API_KEY/repositories \
  --jq '.repositories[].name'

# Add new repository to allowed list
gh api -X PUT \
  orgs/myorg/actions/secrets/SHARED_API_KEY/repositories/123456

# Remove repository access
gh api -X DELETE \
  orgs/myorg/actions/secrets/SHARED_API_KEY/repositories/123456
```

**Result:** Secret available only to authorized repositories, reducing exposure

---

## Best Practices

### DO:
✅ **Use GitHub CLI for automation** - Enables scripting and CI/CD integration  
✅ **Rotate secrets regularly** - Follow security best practices (90 days for sensitive keys)  
✅ **Document secret purpose** - Include ownership, rotation schedule, and usage  
✅ **Use organization secrets** - Share common secrets across repos securely  
✅ **Keep secrets in password manager** - Never store in plain text files  
✅ **Test secret rotation** - Verify workflows succeed with new values  
✅ **Add .gitignore entries** - Prevent accidental secret commits  
✅ **Use descriptive names** - UPPERCASE_SNAKE_CASE (e.g., `DATABASE_URL`)  
✅ **Implement least privilege** - Only grant access to repositories that need it  
✅ **Use secret scanning** - Enable GitHub secret scanning alerts

### DON'T:
❌ **Commit secrets to git** - Even in "private" repositories  
❌ **Echo secrets in logs** - Use `echo "::add-mask::$SECRET"` in workflows  
❌ **Share secrets via chat** - Use secure sharing mechanisms  
❌ **Use production secrets in development** - Maintain separate environments  
❌ **Set secrets manually in UI** - Automate with CLI for consistency  
❌ **Hardcode secrets in Dockerfiles** - Use build args or runtime env vars  
❌ **Store secrets in workflow files** - Always use GitHub Secrets  
❌ **Reuse secrets across environments** - Separate dev/staging/prod  
❌ **Leave secrets in shell history** - Clear history after operations  
❌ **Skip secret rotation** - Treat expired secrets as compromised

---

## Related Workflows

**Prerequisites:**
- [Repository Setup](./new_repo_scaffolding.md) - Create repository before adding secrets
- [CI/CD Pipeline Setup](./ci_cd_workflow.md) - Understand workflow configuration

**Next Steps:**
- [Environment Initialization](./environment_initialization.md) - Use secrets in environment setup
- [Third-Party API Integration](./third_party_api_integration.md) - Secure API credentials
- [Emergency Hotfix](../devops/emergency_hotfix.md) - Rotate compromised secrets

**Alternatives:**
- [Secret Management Solo](../security/secret_management_solo.md) - Solo developer secret management
- [Vault Integration](../security/vault_integration.md) - Enterprise secret management (if available)

---

## Tags
`development` `security` `secrets` `github` `automation` `cli` `github-actions` `credentials` `api-keys` `devops`
