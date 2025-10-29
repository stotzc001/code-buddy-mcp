# Secret Incident Response

**ID:** sec-003  
**Category:** Security  
**Priority:** CRITICAL  
**Complexity:** Intermediate  
**Estimated Time:** 30-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Immediate response workflow for exposed secrets (API keys, passwords, tokens, credentials) discovered in code repositories, logs, or public locations.

**Why:** Exposed secrets can lead to unauthorized access, data breaches, financial loss, and compliance violations. Immediate action is required to minimize damage and prevent exploitation.

**When to use:**
- Secret detected in git commit history
- API key found in public repository
- Credentials accidentally shared in Slack/email
- Automated security scanner alerts on exposed secrets
- Manual discovery of hardcoded passwords
- Third-party notification of credential exposure

---

## Prerequisites

**Required:**
- [ ] Access to secret management system (AWS Secrets Manager, Vault, etc.)
- [ ] Permissions to rotate credentials
- [ ] Access to monitoring/logging systems
- [ ] GitHub/GitLab admin access (if repository-related)
- [ ] Communication channel to stakeholders

**Check before starting:**
```bash
# Verify you can access secret management
aws secretsmanager list-secrets --max-results 1
# or
vault status

# Verify git access
git remote -v

# Check if BFG Repo-Cleaner is available (for history cleanup)
bfg --version
# or install: brew install bfg (Mac) or download JAR file
```

---

## Implementation Steps

### Step 1: Immediate Containment

**What:** Stop the bleeding - immediately invalidate the exposed secret to prevent further unauthorized access.

**How:**
Prioritize speed over perfection. The exposed secret must be rotated/revoked within minutes, not hours.

**Actions:**

1. **Rotate the Secret Immediately**
```bash
# AWS - Rotate IAM access key
aws iam create-access-key --user-name <username>
aws iam delete-access-key --access-key-id <exposed-key-id> --user-name <username>

# AWS - Rotate secret in Secrets Manager
aws secretsmanager rotate-secret --secret-id prod/database/password

# GitHub - Revoke personal access token (via UI or CLI)
gh auth token | gh api user/tokens -X DELETE

# Database - Immediately change password
psql -U postgres -c "ALTER USER app_user PASSWORD 'new-secure-password';"

# API Service - Revoke API key via provider's dashboard
curl -X POST https://api.example.com/v1/keys/revoke \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -d '{"key_id": "exposed-key-id"}'
```

2. **Verify Rotation Worked**
```bash
# Test that old secret no longer works
curl -H "Authorization: Bearer ${OLD_TOKEN}" https://api.example.com/test
# Should return 401 Unauthorized

# Test that new secret does work
curl -H "Authorization: Bearer ${NEW_TOKEN}" https://api.example.com/test
# Should return 200 OK
```

**Verification:**
- [ ] Old secret has been revoked/deleted
- [ ] New secret has been generated
- [ ] New secret is stored securely
- [ ] Old secret no longer provides access
- [ ] New secret provides expected access

**If This Fails:**
→ If unable to rotate immediately, temporarily disable the service/account  
→ If service disruption occurs, have rollback plan ready  
→ If locked out, escalate to admin with higher permissions  

---

### Step 2: Assess the Exposure Scope

**What:** Determine how widely the secret was exposed and for how long.

**How:**
Document the exposure timeline and blast radius for incident reporting.

**Investigation:**
```bash
# Check git history for when secret was added
git log -S "exposed-api-key" --source --all

# Find all commits containing the secret
git log --all --full-history --source -- path/to/file

# Check if repository is public
gh repo view --json visibility

# Search for secret in all branches
git grep "exposed-secret" $(git rev-list --all)

# Check GitHub activity for potential access
gh api repos/:owner/:repo/traffic/clones
gh api repos/:owner/:repo/traffic/views
```

**Exposure Locations Checklist:**
- [ ] Git commit history (how many commits?)
- [ ] Pull request descriptions/comments
- [ ] Issue tracker comments
- [ ] CI/CD logs
- [ ] Container images
- [ ] Documentation sites
- [ ] Slack/Discord messages
- [ ] Email communications
- [ ] Stack Overflow posts

**Verification:**
- [ ] Timeline documented (first exposure to discovery)
- [ ] All exposure locations identified
- [ ] Visibility determined (public vs private)
- [ ] Potential access window calculated
- [ ] Screenshot/evidence collected

**If This Fails:**
→ If timeline unclear, assume worst-case scenario (exposed since first commit)  
→ If unable to determine visibility, treat as publicly exposed  
→ Use `git log --all --format="%H %an %ae %ai"` for comprehensive history  

---

### Step 3: Check for Unauthorized Access

**What:** Investigate logs and monitoring systems for signs of compromise.

**How:**
Look for unusual activity patterns that might indicate the secret was exploited.

**Analysis Commands:**
```bash
# AWS CloudTrail - Check for unauthorized API calls
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<exposed-key> \
  --start-time 2025-10-01 \
  --max-results 50

# Database logs - Check for unusual queries
psql -U postgres -c "SELECT * FROM pg_stat_statements 
WHERE query LIKE '%suspicious_table%' 
ORDER BY calls DESC LIMIT 20;"

# Application logs - Check for API usage with exposed key
grep "exposed-api-key" /var/log/application/*.log | tail -50

# GitHub audit log (organization level)
gh api orgs/:org/audit-log

# Check for unusual IP addresses
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -20
```

**Indicators of Compromise:**
```python
# Python script to analyze API usage patterns
import json
from collections import Counter
from datetime import datetime

def analyze_access_logs(log_file):
    """Identify suspicious patterns in access logs"""
    
    with open(log_file) as f:
        logs = [json.loads(line) for line in f]
    
    # Check for unusual spike in requests
    requests_per_hour = Counter(log['timestamp'][:13] for log in logs)
    baseline = sum(requests_per_hour.values()) / len(requests_per_hour)
    
    for hour, count in requests_per_hour.items():
        if count > baseline * 3:
            print(f"⚠️  Spike detected at {hour}: {count} requests (baseline: {baseline:.0f})")
    
    # Check for new IP addresses
    recent_ips = {log['ip'] for log in logs if log['timestamp'] > '2025-10-25'}
    historical_ips = {log['ip'] for log in logs if log['timestamp'] < '2025-10-20'}
    new_ips = recent_ips - historical_ips
    
    if new_ips:
        print(f"⚠️  {len(new_ips)} new IP addresses detected: {new_ips}")
    
    # Check for unusual endpoints
    endpoint_counts = Counter(log['endpoint'] for log in logs)
    for endpoint, count in endpoint_counts.most_common(10):
        print(f"  {endpoint}: {count} requests")

analyze_access_logs('/var/log/api/access.log')
```

**Verification:**
- [ ] Log analysis completed for exposure window
- [ ] No unauthorized data exfiltration detected
- [ ] No unauthorized resource creation detected
- [ ] Unusual activity documented (if any)
- [ ] Compliance team notified (if required)

**If This Fails:**
→ If logs unavailable, assume compromise and initiate breach protocol  
→ If suspicious activity found, escalate to security team immediately  
→ If data exfiltration suspected, initiate data breach response plan  

---

### Step 4: Remove Secret from Exposure Points

**What:** Clean up the secret from all locations where it was exposed.

**How:**
Systematically remove the secret from git history, documentation, and other locations.

**Git History Cleanup (BFG Repo-Cleaner - Recommended):**
```bash
# Clone a fresh copy of the repository
git clone --mirror git@github.com:username/repo.git repo-cleanup.git
cd repo-cleanup.git

# Remove secret using BFG (faster and safer than filter-branch)
# Replace passwords/secrets from all branches
bfg --replace-text ../secrets-to-remove.txt

# secrets-to-remove.txt format:
# OLD_SECRET==>REMOVED
# sk_live_abc123==>REMOVED
# password123==>REMOVED

# Or delete files containing secrets
bfg --delete-files credentials.json

# Clean up the repository
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: This rewrites history)
git push --force --all
git push --force --tags
```

**Alternative: git-filter-repo (More Powerful):**
```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove secret from all commits
git filter-repo --replace-text <(echo 'literal:old-secret==>REMOVED')

# Or remove entire file
git filter-repo --path credentials.json --invert-paths

# Force push
git push --force --all origin
```

**Cleanup Other Locations:**
```bash
# Remove from CI/CD logs (example: GitHub Actions)
# Go to repository Settings → Actions → delete old workflow runs

# Remove from Docker images
# Re-build images without the secret and update all tags

# Remove from documentation sites
# If using MkDocs, Docusaurus, etc., rebuild and redeploy

# Remove from container registries
docker rmi registry.example.com/app:with-secret
# Then re-push clean version

# Remove from Slack/Discord
# Manually delete messages containing secret (use search)
```

**Verification:**
- [ ] Secret removed from git history (all branches/tags)
- [ ] Team members notified to re-clone repository
- [ ] CI/CD pipeline updated to use new secret
- [ ] Docker images rebuilt and redeployed
- [ ] Documentation updated/redeployed
- [ ] Communication platforms cleaned

**If This Fails:**
→ If BFG fails, use `git filter-branch` as fallback (slower)  
→ If force-push blocked, temporarily disable branch protection  
→ If team has local clones with old history, require fresh clones  
→ Document that old history may exist in backups/archives  

---

### Step 5: Update Applications and Systems

**What:** Deploy the new secret to all systems that depend on it.

**How:**
Update secret references systematically to prevent service disruptions.

**Secret Management Best Practices:**
```bash
# Store in AWS Secrets Manager
aws secretsmanager create-secret \
  --name prod/api/third-party-key \
  --description "Third party API key" \
  --secret-string '{"api_key":"new-secure-key","api_secret":"new-secure-secret"}'

# Store in HashiCorp Vault
vault kv put secret/prod/api \
  api_key="new-secure-key" \
  api_secret="new-secure-secret"

# Store in Kubernetes secrets
kubectl create secret generic api-credentials \
  --from-literal=api-key=new-secure-key \
  --from-literal=api-secret=new-secure-secret \
  -n production
```

**Application Update Pattern:**
```python
# Before (WRONG - hardcoded)
API_KEY = "sk_live_abc123"

# After (CORRECT - environment variable)
import os
API_KEY = os.environ['API_KEY']

# Or use secret management SDK
from aws_secretsmanager import get_secret
API_KEY = get_secret('prod/api/third-party-key')['api_key']
```

**Deployment Checklist:**
```bash
# Update environment variables in deployment
kubectl set env deployment/app API_KEY=$NEW_API_KEY -n production

# Verify pods picked up new secret
kubectl get pods -n production
kubectl logs deployment/app -n production | grep "API initialized"

# Update local development .env.example
cat > .env.example << EOF
# API Credentials (get from secret manager)
API_KEY=<get-from-aws-secrets-manager>
API_SECRET=<get-from-aws-secrets-manager>
EOF

# Update CI/CD pipeline secrets
gh secret set API_KEY --body "$NEW_API_KEY"
gh secret set API_SECRET --body "$NEW_API_SECRET"
```

**Verification:**
- [ ] New secret stored in secret manager
- [ ] Production applications updated
- [ ] Staging/development environments updated
- [ ] CI/CD pipeline updated
- [ ] Local development documentation updated
- [ ] Health checks passing

**If This Fails:**
→ If deployment fails, have rollback procedure ready  
→ If service disruption, communicate with stakeholders immediately  
→ If missing systems, maintain list of all systems using the secret  

---

### Step 6: Implement Preventive Controls

**What:** Add safeguards to prevent future secret exposure incidents.

**How:**
Implement automated detection and prevent secrets from entering the codebase.

**Pre-commit Hooks:**
```bash
# Install pre-commit framework
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package-lock.json
  
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks-docker
EOF

# Install hooks
pre-commit install

# Generate baseline (if you have existing secrets to ignore)
detect-secrets scan > .secrets.baseline

# Test the hooks
pre-commit run --all-files
```

**GitHub Secret Scanning:**
```bash
# Enable secret scanning (requires GitHub Enterprise or public repos)
# Go to: Settings → Security & Analysis → Enable secret scanning

# Add custom patterns for proprietary secrets
# Settings → Security & Analysis → Custom patterns
# Example pattern: (sk|pk)_live_[0-9a-zA-Z]{24,}
```

**CI/CD Pipeline Scanning:**
```yaml
# GitHub Actions workflow
name: Security Scan
on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Run TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

**Code Review Checklist:**
```markdown
# Security Review Checklist (add to PR template)

## Secrets & Credentials
- [ ] No hardcoded API keys, passwords, or tokens
- [ ] All secrets use environment variables or secret manager
- [ ] No sensitive data in log messages
- [ ] No credentials in test files or fixtures
- [ ] .env files are gitignored
- [ ] No secrets in comments or documentation
```

**Verification:**
- [ ] Pre-commit hooks installed and tested
- [ ] GitHub secret scanning enabled
- [ ] CI/CD pipeline includes security scans
- [ ] PR template includes security checklist
- [ ] Team trained on secret management
- [ ] Documentation updated with best practices

**If This Fails:**
→ If pre-commit hooks slow down workflow, optimize patterns  
→ If false positives are high, tune detection patterns  
→ If team resistance, demonstrate value with examples  

---

### Step 7: Notify Stakeholders

**What:** Communicate the incident to relevant parties according to severity and impact.

**How:**
Provide clear, factual communication without causing unnecessary alarm.

**Notification Template (Internal):**
```markdown
Subject: [SECURITY INCIDENT] Exposed API Key - Resolved

Priority: HIGH
Status: RESOLVED
Incident ID: SEC-2025-001

## Summary
An API key for [SERVICE_NAME] was accidentally committed to the [REPO_NAME]
repository on [DATE]. The key has been rotated and the exposure has been
contained.

## Timeline
- 2025-10-26 14:23 UTC: Secret committed to repository
- 2025-10-26 15:45 UTC: Exposure discovered
- 2025-10-26 15:52 UTC: Secret rotated (7 minutes)
- 2025-10-26 16:30 UTC: Git history cleaned
- 2025-10-26 17:00 UTC: All systems updated

## Impact
- Exposure Duration: 1 hour 22 minutes
- Repository Visibility: Private (team access only)
- Unauthorized Access: None detected
- Data Breach: No
- Service Disruption: None

## Actions Taken
✅ API key immediately rotated
✅ Logs analyzed for unauthorized access
✅ Secret removed from git history
✅ All applications updated with new key
✅ Pre-commit hooks installed to prevent recurrence

## Recommendations
- All team members should re-clone the repository
- Review other repositories for similar issues
- Complete security awareness training

## Questions or Concerns
Contact: security@company.com or Slack #security-incidents
```

**Notification Matrix:**

| Severity | Who to Notify | Timeline | Method |
|----------|---------------|----------|--------|
| CRITICAL (Public exposure) | CISO, Legal, PR, Engineering | Immediate | Phone + Email |
| HIGH (Private repo, team access) | Engineering Manager, Security Team | Within 1 hour | Email + Slack |
| MEDIUM (Development secret) | Team Lead, Developer | Within 4 hours | Slack |
| LOW (Test environment) | Developer | Next business day | Ticket |

**Compliance Considerations:**
```bash
# If customer data potentially accessed, check breach notification requirements
# GDPR: 72 hours
# CCPA: Without unreasonable delay
# HIPAA: 60 days

# Document for compliance
cat > incident-report-SEC-2025-001.md << 'EOF'
# Incident Report: SEC-2025-001

**Date:** 2025-10-26
**Reporter:** John Doe
**Severity:** HIGH

## Incident Details
[Comprehensive incident documentation]

## Affected Systems
- Production API (no unauthorized access)
- Database (no unauthorized queries)

## Customer Impact
- No customer data accessed
- No service disruption

## Remediation
[Complete remediation steps]

## Lessons Learned
[Process improvements]
EOF
```

**Verification:**
- [ ] Internal team notified
- [ ] Management informed (if required)
- [ ] Security team updated
- [ ] Incident documented
- [ ] Compliance requirements met (if applicable)
- [ ] Post-incident review scheduled

**If This Fails:**
→ If unsure about severity, escalate to security team  
→ If compliance risk, consult legal counsel immediately  
→ If media attention possible, involve PR team early  

---

### Step 8: Post-Incident Review

**What:** Conduct a blameless retrospective to prevent future incidents.

**How:**
Focus on systemic improvements rather than individual mistakes.

**Review Meeting Agenda:**
```markdown
# Post-Incident Review: SEC-2025-001
Date: 2025-10-28
Attendees: Engineering Team, Security Team, Management

## What Happened (Facts)
- Timeline of events
- Root cause analysis
- Contributing factors

## What Went Well
- Fast detection (1 hour 22 minutes)
- Quick rotation (7 minutes)
- No unauthorized access

## What Could Be Improved
- Earlier detection needed
- Better secret management practices
- More thorough code review

## Action Items
- [ ] Deploy automated secret scanning (Owner: Security, Due: 2025-11-01)
- [ ] Conduct security training (Owner: Eng Manager, Due: 2025-11-15)
- [ ] Audit all repositories (Owner: DevOps, Due: 2025-11-30)
- [ ] Update onboarding materials (Owner: HR, Due: 2025-12-01)

## Lessons Learned
- Process gaps identified
- Tool improvements needed
- Training requirements
```

**Root Cause Analysis (5 Whys):**
```
Why was the secret exposed?
→ Developer committed .env file

Why was .env committed?
→ .gitignore was missing .env

Why was .gitignore missing .env?
→ Used incomplete template

Why was incomplete template used?
→ No standardized project initialization

Why was there no standard initialization?
→ No documented process

ACTION: Create standardized project template with security defaults
```

**Documentation Updates:**
```bash
# Update team wiki
cat >> team-wiki/security-best-practices.md << 'EOF'
## Secret Management Best Practices

### Never Commit
❌ API keys, passwords, tokens
❌ .env files with real secrets
❌ Private keys or certificates
❌ Database connection strings with credentials

### Always Use
✅ Environment variables
✅ Secret management services (AWS Secrets Manager, Vault)
✅ .env.example with placeholder values
✅ Pre-commit hooks for secret detection

### If You Accidentally Commit a Secret
1. Rotate it immediately (< 10 minutes)
2. Follow the [Secret Incident Response workflow]
3. Notify security team
4. Clean git history

Last updated: 2025-10-26
EOF
```

**Verification:**
- [ ] Post-incident review completed
- [ ] Root cause identified
- [ ] Action items assigned with due dates
- [ ] Documentation updated
- [ ] Training scheduled (if needed)
- [ ] Follow-up review scheduled (30 days)

**If This Fails:**
→ If team defensive, reinforce blameless culture  
→ If no clear root cause, dig deeper with incident timeline  
→ If action items stall, escalate to management  

---

## Verification Checklist

After completing this workflow:

- [ ] Exposed secret has been rotated/revoked
- [ ] New secret is securely stored
- [ ] Logs analyzed for unauthorized access
- [ ] No signs of compromise detected
- [ ] Secret removed from git history
- [ ] All applications updated with new secret
- [ ] Pre-commit hooks installed
- [ ] CI/CD security scanning enabled
- [ ] Stakeholders notified appropriately
- [ ] Incident documented
- [ ] Post-incident review scheduled
- [ ] Process improvements identified

---

## Common Issues & Solutions

### Issue: "I can't rotate the secret immediately"

**Symptoms:**
- Don't have permissions to access secret manager
- Service account locked
- On-call rotation needed

**Solution:**
```bash
# Escalate to someone with permissions
# Contact on-call security team
# Use break-glass procedure if available

# Temporary mitigation: Disable the service
kubectl scale deployment app --replicas=0 -n production
# Or
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

**Prevention:**
- Maintain on-call rotation with proper access
- Document escalation procedures
- Test break-glass procedures quarterly

---

### Issue: "BFG Repo-Cleaner isn't working"

**Symptoms:**
- BFG exits with errors
- Secret still present after cleanup
- Repository corruption

**Solution:**
```bash
# Fallback to git filter-repo
pip install git-filter-repo

git filter-repo --replace-text <(cat <<EOF
literal:old-api-key==>REMOVED
literal:sk_live_abc123==>REMOVED
EOF
)

# Or manual filter-branch (slowest option)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
git push origin --force --tags
```

**Prevention:**
- Test BFG on a clone first
- Keep backup before history rewrite
- Use git-filter-repo as primary tool

---

### Issue: "Team members still have old repository"

**Symptoms:**
- Developers pull old history
- Secret reappears after cleanup
- Confusion about repository state

**Solution:**
```bash
# Send clear communication
cat << 'EOF'
🚨 IMPORTANT: Repository History Rewritten 🚨

The [REPO_NAME] repository history has been rewritten to remove an
exposed secret. You MUST take these actions:

1. Stash or commit any local changes:
   git stash

2. Delete your local repository:
   rm -rf /path/to/repo

3. Fresh clone:
   git clone git@github.com:org/repo.git

4. Re-apply stashed changes if needed:
   git stash pop

Questions? Contact #engineering-support

DO NOT force push old commits back!
EOF

# Protect default branch temporarily
gh api repos/:owner/:repo/branches/main/protection \
  -X PUT \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true}'
```

**Prevention:**
- Clear communication protocol
- Monitor for force-push attempts
- Verify all team members have new clone

---

### Issue: "Application broke after rotating secret"

**Symptoms:**
- Authentication failures
- 401/403 errors
- Service unavailable

**Solution:**
```bash
# Verify secret is correctly set
kubectl get secret api-credentials -o yaml -n production

# Check application picked up new secret
kubectl logs deployment/app -n production | grep -i "secret\|auth\|api"

# Restart pods if needed
kubectl rollout restart deployment/app -n production

# Test the new secret manually
curl -H "Authorization: Bearer ${NEW_SECRET}" https://api.example.com/health
```

**Prevention:**
- Test new secret before rotating old one
- Implement graceful secret rotation
- Monitor application health during rotation

---

### Issue: "Can't determine exposure timeline"

**Symptoms:**
- Unclear when secret was first exposed
- Missing git history
- No audit logs available

**Solution:**
```bash
# Assume worst-case scenario
EXPOSURE_DATE="first commit date"

# Treat as if exposed since:
git log --diff-filter=A -- path/to/file | tail -1

# If in doubt, assume:
# - Public repository: exposed to everyone
# - Private repository: exposed to all team members
# - Duration: since file was added

# Proceed with maximum caution
ASSUME_COMPROMISED=true
```

**Prevention:**
- Enable audit logging
- Regular security scans
- Automated secret detection

---

## Examples

### Example 1: AWS API Key in Public Repository

**Context:**
Developer accidentally committed AWS access key to a public GitHub repository. Key was exposed for 2 hours before detection.

**Execution:**
```bash
# 1. IMMEDIATE: Rotate AWS key (< 5 minutes)
aws iam list-access-keys --user-name app-user
aws iam create-access-key --user-name app-user
aws iam delete-access-key --access-key-id AKIAEXPOSEDKEY123 --user-name app-user

# 2. Check CloudTrail for unauthorized activity
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIAEXPOSEDKEY123 \
  --max-results 50 \
  --output table

# 3. Clean git history with BFG
git clone --mirror git@github.com:company/app.git app-cleanup.git
cd app-cleanup.git
echo "AKIAEXPOSEDKEY123==>REMOVED" > ../secrets.txt
bfg --replace-text ../secrets.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force

# 4. Update all systems
aws secretsmanager put-secret-value \
  --secret-id prod/aws/access-key \
  --secret-string '{"AccessKeyId":"AKIANEWKEY456","SecretAccessKey":"new-secret"}'

# 5. Notify team
echo "Repository history rewritten. Fresh clone required."
```

**Result:**
- Key rotated in 4 minutes
- No unauthorized AWS activity detected
- History cleaned within 30 minutes
- Zero customer impact

---

### Example 2: Database Password in Private Repository

**Context:**
Database credentials committed to private repository, exposed to 12 team members for 3 days before discovery during code review.

**Execution:**
```bash
# 1. IMMEDIATE: Change database password
psql -U postgres -d production << EOF
ALTER USER app_user WITH PASSWORD 'new-secure-password-123';
EOF

# 2. Check database logs
psql -U postgres -d production -c "
SELECT datname, usename, client_addr, query, query_start
FROM pg_stat_activity
WHERE usename = 'app_user'
ORDER BY query_start DESC
LIMIT 100;"

# 3. Clean git history
git filter-repo --replace-text <(echo 'literal:old-password==>REMOVED')

# 4. Update applications
kubectl create secret generic db-credentials \
  --from-literal=password=new-secure-password-123 \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/app

# 5. Verify
kubectl get pods | grep app
kubectl logs deployment/app | tail -20
```

**Result:**
- Password changed in 2 minutes
- Log analysis showed only legitimate team access
- Applications updated with zero downtime
- Post-incident review improved onboarding

---

### Example 3: API Key in Slack Message

**Context:**
Team member accidentally pasted API key in public Slack channel. Key was visible for 30 minutes with 50+ team members online.

**Execution:**
```bash
# 1. IMMEDIATE: Revoke API key via provider dashboard
curl -X POST https://api.stripe.com/v1/api_keys/sk_live_abc123/revoke \
  -u "${STRIPE_ADMIN_KEY}:"

# 2. Generate new key
curl -X POST https://api.stripe.com/v1/api_keys \
  -u "${STRIPE_ADMIN_KEY}:" \
  -d "name=Production API Key"

# 3. Delete Slack message
# (Done manually in Slack - search for key and delete message)

# 4. Update application
gh secret set STRIPE_API_KEY --body "$NEW_STRIPE_KEY"

# 5. Verify in application logs
gh run list --workflow=deploy.yml --limit 5
gh run view <run-id> --log | grep "Stripe initialized"
```

**Result:**
- Key revoked in 90 seconds
- No fraudulent charges detected
- Message deleted from Slack
- Team reminded about #security-questions channel

---

## Best Practices

### DO:
✅ Rotate secrets immediately upon discovery (< 10 minutes)  
✅ Assume worst-case scenario if timeline unclear  
✅ Use automated tools (BFG, git-filter-repo) over manual cleanup  
✅ Document everything for post-incident review  
✅ Communicate clearly with stakeholders  
✅ Implement preventive controls after every incident  
✅ Use secret management services (never hardcode)  
✅ Enable automated secret scanning in CI/CD  
✅ Conduct blameless post-mortems  
✅ Test incident response procedures regularly  

### DON'T:
❌ Delay rotation while investigating  
❌ Assume private repository means safe  
❌ Skip log analysis (always check for compromise)  
❌ Blame individuals for security incidents  
❌ Reuse secrets after exposure  
❌ Push secrets to "secure" branches  
❌ Ignore compliance notification requirements  
❌ Skip cleanup because "nobody accessed it"  
❌ Forget to update all dependent systems  
❌ Ignore false positives from scanning tools  

---

## Related Workflows

**Prerequisites:**
- **secret_management_solo.md** - Proper secret storage and rotation
- **development/pre_commit_hooks.md** - Setting up pre-commit secret scanning

**Next Steps:**
- **git_history_cleanup_solo.md** - Detailed guide for cleaning git history
- **code_buddy_secret_rules.md** - Code Buddy specific secret handling rules

**Alternatives:**
- **devops/incident_response_workflow.md** - General incident response for non-security issues

---

## Tags
`security` `incident-response` `secrets` `critical` `compliance` `git`
