# Anthropic Claude API Key Rotation

**ID:** sec-005  
**Category:** Security  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 15-30 minutes  
**Frequency:** Every 90 days or as needed  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Rotate Anthropic Claude API keys to maintain security and comply with best practices for credential management.

**Why:** Regular key rotation limits the impact of potential compromises, ensures compliance with security policies, and demonstrates security hygiene. Compromised API keys can lead to unauthorized usage, data breaches, and significant API costs.

**When to use:**
- Scheduled quarterly rotation (every 90 days)
- After suspected compromise or exposure
- When team member with key access leaves
- After security incident or breach
- When updating security practices
- Before major product launches

---

## Prerequisites

**Required Knowledge:**
- [ ] Understanding of API key management
- [ ] Access to Anthropic Console
- [ ] Familiarity with environment variable management
- [ ] Basic knowledge of your deployment platform

**Required Access:**
- [ ] Anthropic Console account with API key creation permissions
- [ ] Access to production deployment configuration
- [ ] Access to CI/CD secrets management
- [ ] (Optional) Access to secrets management system (Vault, AWS Secrets Manager, etc.)

**Check before starting:**
```bash
# Verify current key works
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-sonnet-20240229","messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

---

## Implementation Steps

### Step 1: Document Current Key Usage

**What:** Identify all locations where the current API key is used

**How:**

Create an inventory checklist:

```markdown
## Current Key Locations

**Production:**
- [ ] Production server environment variables
- [ ] Docker container configs
- [ ] Kubernetes secrets
- [ ] Cloud provider secrets (AWS Secrets Manager, etc.)

**Development:**
- [ ] Local .env files
- [ ] Development server configs
- [ ] Docker Compose files

**CI/CD:**
- [ ] GitHub Actions secrets
- [ ] GitLab CI/CD variables
- [ ] CircleCI environment variables
- [ ] Jenkins credentials

**Team Access:**
- [ ] Shared team password manager
- [ ] Documentation (remove after rotation!)
- [ ] Slack/email threads (NEVER store here)

**Code Repositories:**
- [ ] Search for hardcoded keys (should be NONE)
```

```bash
# Search codebase for potential hardcoded keys
# Anthropic keys start with "sk-ant-"
grep -r "sk-ant-" . --exclude-dir={node_modules,.git,venv}

# Search for common patterns
git log -p | grep "sk-ant-" 
```

**Verification:**
- [ ] All key locations documented
- [ ] No hardcoded keys found in code
- [ ] Team members using the key identified

**If This Fails:**
→ If keys found in code, follow [[sec-003]](secret_incident_solo.md) workflow first

---

### Step 2: Create New API Key in Anthropic Console

**What:** Generate a new API key in the Anthropic Console

**How:**

1. **Log in to Anthropic Console:**
   - Go to https://console.anthropic.com
   - Sign in with your account

2. **Navigate to API Keys:**
   - Click on your profile/organization
   - Select "API Keys" or "Settings"
   - Go to "API Keys" section

3. **Create New Key:**
   - Click "Create Key" or "Generate New Key"
   - Give it a descriptive name (e.g., "Production-2025-Q4")
   - Optionally set permissions/restrictions if available
   - Copy the key immediately (it won't be shown again!)

4. **Store New Key Securely:**
   ```bash
   # Temporarily store in password manager
   # Label: "Anthropic API Key - NEW (not yet active)"
   # Include: creation date, intended use, rotation date
   ```

**Expected Result:**
```
Key format: sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx...
Length: ~108 characters
```

**Verification:**
- [ ] New key copied and saved securely
- [ ] Key name is descriptive
- [ ] Creation date noted

**If This Fails:**
→ Contact Anthropic support or check account permissions

---

### Step 3: Test New Key Before Deployment

**What:** Verify new key works before updating production

**How:**

```bash
# Set new key temporarily (don't commit!)
export ANTHROPIC_API_KEY_NEW="sk-ant-api03-..."

# Test with simple API call
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY_NEW" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [{"role": "user", "content": "Hello! This is a test."}],
    "max_tokens": 50
  }'

# Expected response:
# {"id":"msg_...", "type":"message", "content":[{"text":"Hello! ..."}]}
```

**Test with your application:**
```python
# test_new_key.py
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-api03-...")  # New key
message = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=50,
    messages=[{"role": "user", "content": "Test message"}]
)
print(f"Success: {message.content[0].text}")
```

**Verification:**
- [ ] New key returns successful responses
- [ ] No rate limit or permission errors
- [ ] Response format matches expected

---

### Step 4: Deploy New Key to All Environments

**What:** Update the API key in all identified locations

**How:**

**For Production Servers:**
```bash
# Update environment variable
# Method varies by deployment platform

# Direct server:
export ANTHROPIC_API_KEY="sk-ant-api03-NEW_KEY"
# Add to ~/.bashrc or /etc/environment for persistence

# Systemd service:
sudo systemctl edit myapp.service
# Add:
[Service]
Environment="ANTHROPIC_API_KEY=sk-ant-api03-NEW_KEY"

sudo systemctl restart myapp.service
```

**For Kubernetes:**
```bash
# Update secret
kubectl create secret generic anthropic-api-key \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-api03-NEW_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment/your-app
```

**For AWS Secrets Manager:**
```bash
aws secretsmanager update-secret \
  --secret-id anthropic-api-key \
  --secret-string "sk-ant-api03-NEW_KEY"

# Application should automatically fetch new value on next rotation
```

**For Docker:**
```bash
# Update .env file or docker-compose.yml
# Then:
docker-compose down
docker-compose up -d

# Or for single container:
docker stop container_name
docker rm container_name
docker run -e ANTHROPIC_API_KEY="sk-ant-api03-NEW_KEY" ...
```

**For GitHub Actions:**
```bash
# Go to: Repository → Settings → Secrets and variables → Actions
# Click on ANTHROPIC_API_KEY
# Click "Update secret"
# Paste new value
# Click "Update secret"
```

**For Vercel:**
```bash
# Using Vercel CLI:
vercel env add ANTHROPIC_API_KEY production
# Paste new key when prompted

# Or through dashboard:
# Project Settings → Environment Variables → ANTHROPIC_API_KEY → Edit
```

**Verification for each location:**
- [ ] Key updated successfully
- [ ] Application restarted/redeployed
- [ ] Application functioning normally
- [ ] No errors in logs

---

### Step 5: Verify New Key in Production

**What:** Confirm production is using the new key successfully

**How:**

```bash
# Monitor application logs
# Look for successful API calls

# Check for errors
tail -f /var/log/myapp/error.log | grep -i "anthropic\|api"

# Test production endpoint that uses Claude
curl https://api.yourapp.com/chat \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -d '{"message": "test"}'

# Monitor Anthropic Console usage dashboard
# Verify new requests showing up under new key
```

**Verification:**
- [ ] Production making successful API calls
- [ ] No authentication errors
- [ ] Usage showing in Anthropic Console under new key
- [ ] No increase in error rates

**If This Fails:**
→ Rollback to old key immediately (Step 7)

---

### Step 6: Revoke Old API Key

**What:** Delete the old API key to prevent its use

**How:**

**Wait Period (Recommended):**
```markdown
⏳ Wait 24-48 hours after deployment before revoking old key
This ensures:
- No cached/delayed requests using old key
- Time to catch any missed locations
- Safer rollback window if issues arise
```

**After Wait Period:**

1. **Go to Anthropic Console:**
   - Navigate to API Keys section
   - Find the OLD key (check by name/creation date)

2. **Revoke Key:**
   - Click "Delete" or "Revoke" on the old key
   - Confirm deletion
   - Old key is now invalid

3. **Remove from Local Storage:**
   ```bash
   # Remove from password manager
   # Remove from any local .env files
   # Remove from documentation
   ```

**Verification:**
- [ ] Old key deleted from Anthropic Console
- [ ] Old key removed from all local storage
- [ ] Old key removed from team password manager
- [ ] Production still working (using new key)

---

### Step 7: Document Rotation

**What:** Record the rotation for compliance and future reference

**How:**

Create or update rotation log:

```markdown
# Anthropic API Key Rotation Log

## 2025-10-27 Rotation
- **Previous Key:** sk-ant-...(last 4: xyz9) - REVOKED
- **New Key:** sk-ant-...(last 4: abc5) - ACTIVE
- **Rotated By:** john.doe@company.com
- **Reason:** Scheduled quarterly rotation
- **Locations Updated:** 
  - ✅ Production servers (AWS)
  - ✅ Kubernetes secrets
  - ✅ GitHub Actions
  - ✅ Vercel environment
- **Issues:** None
- **Next Rotation Due:** 2026-01-27

## 2025-07-15 Rotation
- **Previous Key:** sk-ant-...(last 4: def2) - REVOKED
- **New Key:** sk-ant-...(last 4: xyz9) - REVOKED (2025-10-27)
- **Rotated By:** jane.smith@company.com
- **Reason:** Employee departure
- **Next Rotation Due:** 2025-10-15
```

**Set Calendar Reminder:**
```bash
# Add reminder for next rotation (90 days)
# Subject: "Rotate Anthropic API Key"
# Date: 90 days from today
# Include: Link to this workflow
```

**Verification:**
- [ ] Rotation documented
- [ ] Next rotation date set
- [ ] Team notified of completion

---

## Verification Checklist

After completing rotation:

- [ ] New key created in Anthropic Console
- [ ] New key tested successfully
- [ ] All environments updated with new key
- [ ] Production verified working
- [ ] Old key revoked after wait period
- [ ] Old key removed from all locations
- [ ] Rotation documented
- [ ] Next rotation scheduled
- [ ] Team notified
- [ ] No service disruptions

---

## Common Issues & Solutions

### Issue 1: Old Key Still in Use Somewhere

**Symptoms:**
- Authentication errors after revoking old key
- Some requests failing

**Solution:**
```bash
# Quickly recreate old key temporarily if possible
# Or update missed location with new key

# Find the failing service
grep -r "401\|authentication" /var/log/

# Update that specific location
# Then test thoroughly
```

**Prevention:**
- Complete Step 1 thoroughly before rotation
- Wait 24-48 hours before revoking old key

---

### Issue 2: New Key Not Working

**Symptoms:**
- 401 Unauthorized errors
- "Invalid API key" messages

**Solution:**
```bash
# Verify key format
echo $ANTHROPIC_API_KEY | wc -c  # Should be ~108 characters
echo $ANTHROPIC_API_KEY | head -c 10  # Should start with "sk-ant-api"

# Check for extra spaces/newlines
echo "$ANTHROPIC_API_KEY" | od -c

# Test key directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-sonnet-20240229","messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

---

### Issue 3: Kubernetes Pods Not Picking Up New Secret

**Symptoms:**
- Secret updated but pods still use old key

**Solution:**
```bash
# Force pod restart
kubectl rollout restart deployment/your-app

# Or delete pods to force recreation
kubectl delete pods -l app=your-app

# Verify new secret
kubectl get secret anthropic-api-key -o jsonpath='{.data.ANTHROPIC_API_KEY}' | base64 -d
```

---

## Best Practices

### DO:
✅ Rotate keys every 90 days minimum  
✅ Test new key before production deployment  
✅ Wait 24-48 hours before revoking old key  
✅ Document all rotations  
✅ Use secrets management systems  
✅ Monitor usage after rotation  
✅ Rotate after any potential compromise  
✅ Set calendar reminders for next rotation

### DON'T:
❌ Hardcode API keys in source code  
❌ Commit keys to version control  
❌ Share keys via email or chat  
❌ Revoke old key immediately after deployment  
❌ Skip testing the new key  
❌ Forget to update all environments  
❌ Ignore authentication errors  
❌ Store keys in plain text files

---

## Related Workflows

**Related Security Workflows:**
- [[sec-006]](openai_key_rotation.md) - Rotate OpenAI keys similarly
- [[sec-004]](secret_management_solo.md) - General secret management
- [[sec-003]](secret_incident_solo.md) - If key was compromised

**After Rotation:**
- [[dvo-001]](../devops/application_monitoring_setup.md) - Monitor API usage
- [[sec-001]](code_buddy_secret_rules.md) - Review secret handling rules

---

## Tags

`security` `api-keys` `anthropic` `claude` `rotation` `credentials` `secrets-management` `compliance`
