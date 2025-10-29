# OpenAI API Key Rotation

**ID:** sec-006  
**Category:** Security  
**Priority:** HIGH  
**Complexity:** Simple  
**Estimated Time:** 15-30 minutes  
**Frequency:** Every 90 days or as needed  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Rotate OpenAI API keys to maintain security and comply with best practices for credential management.

**Why:** Regular key rotation limits the impact of potential compromises, ensures compliance with security policies, and protects against unauthorized usage. Compromised API keys can lead to significant costs, data breaches, and service abuse.

**When to use:**
- Scheduled quarterly rotation (every 90 days)
- After suspected compromise or exposure
- When team member with key access leaves
- After security incident or breach
- Before major product launches
- When updating security practices

---

## Prerequisites

**Required Knowledge:**
- [ ] Understanding of API key management
- [ ] Access to OpenAI Dashboard
- [ ] Familiarity with environment variable management
- [ ] Basic knowledge of your deployment platform

**Required Access:**
- [ ] OpenAI account with API key management permissions
- [ ] Access to production deployment configuration
- [ ] Access to CI/CD secrets management
- [ ] (Optional) Access to secrets management system (Vault, AWS Secrets Manager, etc.)

**Check before starting:**
```bash
# Verify current key works
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
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

**Code Repositories:**
- [ ] Search for hardcoded keys (should be NONE)
```

```bash
# Search codebase for potential hardcoded keys
# OpenAI keys start with "sk-" or "sk-proj-"
grep -rE "sk-[A-Za-z0-9]{48}|sk-proj-[A-Za-z0-9]" . --exclude-dir={node_modules,.git,venv}

# Search git history for leaked keys
git log -p | grep -E "sk-[A-Za-z0-9]{48}|sk-proj-"
```

**Verification:**
- [ ] All key locations documented
- [ ] No hardcoded keys found in code
- [ ] Team members using the key identified

**If This Fails:**
→ If keys found in code, follow [[sec-003]](secret_incident_solo.md) workflow first

---

### Step 2: Create New API Key in OpenAI Dashboard

**What:** Generate a new API key in the OpenAI Platform

**How:**

1. **Log in to OpenAI Platform:**
   - Go to https://platform.openai.com
   - Sign in with your account

2. **Navigate to API Keys:**
   - Click on your profile icon (top right)
   - Select "API keys" or go to https://platform.openai.com/api-keys

3. **Create New Key:**
   - Click "Create new secret key"
   - Give it a descriptive name (e.g., "Production-2025-Q4")
   - Select appropriate permissions:
     - `All` - Full access (default)
     - `Restricted` - Limited to specific APIs (recommended)
   - Copy the key immediately (it won't be shown again!)

4. **Store New Key Securely:**
   ```bash
   # Temporarily store in password manager
   # Label: "OpenAI API Key - NEW (not yet active)"
   # Include: creation date, intended use, rotation date
   ```

**Expected Result:**
```
Key format: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
           or sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Length: 51-64 characters
```

**Verification:**
- [ ] New key copied and saved securely
- [ ] Key name is descriptive
- [ ] Permissions set appropriately
- [ ] Creation date noted

**If This Fails:**
→ Check account permissions or contact OpenAI support

---

### Step 3: Test New Key Before Deployment

**What:** Verify new key works before updating production

**How:**

```bash
# Set new key temporarily (don't commit!)
export OPENAI_API_KEY_NEW="sk-proj-..."

# Test with simple API call - list models
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY_NEW"

# Test chat completion
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY_NEW" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello! This is a test."}],
    "max_tokens": 50
  }'

# Expected response:
# {"id":"chatcmpl-...", "object":"chat.completion", "choices":[...]}
```

**Test with your application:**

**Python:**
```python
# test_new_key.py
import openai

client = openai.OpenAI(api_key="sk-proj-...")  # New key
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Test message"}],
    max_tokens=50
)
print(f"Success: {response.choices[0].message.content}")
```

**Node.js:**
```javascript
// test_new_key.js
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: 'sk-proj-...' }); // New key

async function test() {
  const completion = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Test message' }],
    max_tokens: 50
  });
  console.log('Success:', completion.choices[0].message.content);
}

test();
```

**Verification:**
- [ ] New key returns successful responses
- [ ] No rate limit or permission errors
- [ ] Response format matches expected
- [ ] Can access all required models/APIs

---

### Step 4: Deploy New Key to All Environments

**What:** Update the API key in all identified locations

**How:**

**For Production Servers:**
```bash
# Update environment variable
export OPENAI_API_KEY="sk-proj-NEW_KEY"

# Persist in ~/.bashrc or /etc/environment
echo 'export OPENAI_API_KEY="sk-proj-NEW_KEY"' >> ~/.bashrc
source ~/.bashrc

# For systemd services:
sudo systemctl edit myapp.service
# Add:
[Service]
Environment="OPENAI_API_KEY=sk-proj-NEW_KEY"

sudo systemctl restart myapp.service
```

**For Kubernetes:**
```bash
# Update secret
kubectl create secret generic openai-api-key \
  --from-literal=OPENAI_API_KEY="sk-proj-NEW_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods
kubectl rollout restart deployment/your-app

# Verify pods picked up new secret
kubectl get pods
kubectl logs pod-name | grep -i openai
```

**For AWS Secrets Manager:**
```bash
aws secretsmanager update-secret \
  --secret-id openai-api-key \
  --secret-string "sk-proj-NEW_KEY" \
  --region us-east-1
```

**For Docker:**
```bash
# Update docker-compose.yml or .env file
docker-compose down
docker-compose up -d

# Verify
docker-compose exec app env | grep OPENAI_API_KEY
```

**For GitHub Actions:**
```bash
# Repository → Settings → Secrets and variables → Actions
# Click on OPENAI_API_KEY → Update secret → Paste new key
```

**For Vercel:**
```bash
# Using Vercel CLI:
vercel env add OPENAI_API_KEY production
# Paste new key when prompted

# Redeploy to pick up new environment variable
vercel --prod
```

**For Netlify:**
```bash
# Using Netlify CLI:
netlify env:set OPENAI_API_KEY "sk-proj-NEW_KEY"

# Or through dashboard:
# Site Settings → Environment Variables → OPENAI_API_KEY → Edit
```

**Verification for each location:**
- [ ] Key updated successfully
- [ ] Application restarted/redeployed
- [ ] Application functioning normally
- [ ] No errors in logs
- [ ] Can make successful API calls

---

### Step 5: Verify New Key in Production

**What:** Confirm production is using the new key successfully

**How:**

```bash
# Monitor application logs
tail -f /var/log/myapp/app.log | grep -i "openai"

# Check for errors
tail -f /var/log/myapp/error.log | grep -i "openai\|api\|401"

# Test production endpoint that uses OpenAI
curl https://api.yourapp.com/chat \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Monitor OpenAI usage dashboard
# platform.openai.com/usage
# Verify new requests showing up
```

**Check OpenAI Usage Dashboard:**
1. Go to https://platform.openai.com/usage
2. View recent API calls
3. Confirm requests are being made
4. Check for any error patterns

**Verification:**
- [ ] Production making successful API calls
- [ ] No authentication errors
- [ ] Usage showing in OpenAI dashboard
- [ ] No increase in error rates
- [ ] Response times normal

**If This Fails:**
→ Rollback to old key immediately (keep old key active until resolved)

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
- Background jobs complete
```

**After Wait Period:**

1. **Go to OpenAI Platform:**
   - Navigate to https://platform.openai.com/api-keys
   - Find the OLD key (check by name/creation date)

2. **Revoke Key:**
   - Click the trash/delete icon next to old key
   - Confirm deletion: "Are you sure you want to delete this key?"
   - Click "Delete" or "Revoke"

3. **Verify Deletion:**
   - Key should disappear from list
   - Old key is now invalid

4. **Remove from Local Storage:**
   ```bash
   # Remove from password manager
   # Update any documentation
   # Remove from local .env files
   rm -f .env.old  # If you kept a backup
   ```

**Verification:**
- [ ] Old key deleted from OpenAI dashboard
- [ ] Old key removed from password manager
- [ ] Old key removed from team documentation
- [ ] Production still working with new key
- [ ] No errors in logs

---

### Step 7: Document Rotation

**What:** Record the rotation for compliance and future reference

**How:**

Create or update rotation log:

```markdown
# OpenAI API Key Rotation Log

## 2025-10-27 Rotation
- **Previous Key:** sk-proj-...(last 4: xyz9) - REVOKED
- **New Key:** sk-proj-...(last 4: abc5) - ACTIVE
- **Rotated By:** john.doe@company.com
- **Reason:** Scheduled quarterly rotation
- **Locations Updated:** 
  - ✅ Production servers (AWS EC2)
  - ✅ Kubernetes secrets
  - ✅ GitHub Actions
  - ✅ Vercel environment
  - ✅ Development .env files
- **Models Accessed:** GPT-4, GPT-3.5-Turbo, Embeddings
- **Issues:** None
- **Verification:** All systems operational
- **Next Rotation Due:** 2026-01-27

## 2025-07-15 Rotation
- **Previous Key:** sk-...(last 4: def2) - REVOKED
- **New Key:** sk-proj-...(last 4: xyz9) - REVOKED (2025-10-27)
- **Rotated By:** jane.smith@company.com
- **Reason:** Employee departure
- **Next Rotation Due:** 2025-10-15
```

**Set Calendar Reminder:**
```bash
# Add calendar event for next rotation
# Date: 90 days from today
# Title: "Rotate OpenAI API Key"
# Description: Link to this workflow
```

**Verification:**
- [ ] Rotation documented
- [ ] Team notified of completion
- [ ] Next rotation date scheduled
- [ ] No outstanding issues

---

## Verification Checklist

After completing rotation:

- [ ] New key created in OpenAI Platform
- [ ] New key tested successfully
- [ ] All environments updated with new key
- [ ] Production verified working
- [ ] Usage visible in OpenAI dashboard
- [ ] Old key revoked after wait period
- [ ] Old key removed from all locations
- [ ] Rotation documented
- [ ] Next rotation scheduled (90 days)
- [ ] Team notified
- [ ] No service disruptions

---

## Common Issues & Solutions

### Issue 1: Rate Limits After Key Rotation

**Symptoms:**
- 429 Rate Limit errors
- "You exceeded your current quota"

**Solution:**
```bash
# Check usage limits for the account
# Go to: platform.openai.com/settings/organization/limits

# Verify new key has same rate limits as old key
# If using organization keys, ensure new key in same org

# Check if you're in grace period after key creation
# Some limits may be temporarily reduced for new keys
```

---

### Issue 2: "Invalid API Key" Errors

**Symptoms:**
- 401 Unauthorized
- "Incorrect API key provided"

**Solution:**
```bash
# Verify key format (no spaces, complete key)
echo "$OPENAI_API_KEY" | wc -c  # Should be 51-64 chars
echo "$OPENAI_API_KEY" | head -c 7  # Should be "sk-" or "sk-proj-"

# Check for hidden characters
echo "$OPENAI_API_KEY" | od -c

# Test key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Ensure Bearer prefix in Authorization header
# Correct: "Authorization: Bearer sk-proj-..."
# Wrong: "Authorization: sk-proj-..."
```

---

### Issue 3: Some Services Still Using Old Key

**Symptoms:**
- Authentication errors after revoking old key
- Some features working, others failing

**Solution:**
```bash
# Check all processes/services
ps aux | grep -i your-app

# Search logs for where old key might be cached
grep -r "sk-proj-OLD_LAST_4" /var/log/

# Common culprits:
# - Background workers not restarted
# - Cached environment in Lambda/Serverless
# - CDN edge workers
# - Scheduled cron jobs

# Restart ALL related services
systemctl restart app worker scheduler
```

---

## Best Practices

### DO:
✅ Rotate keys every 90 days minimum  
✅ Use restricted API keys when possible  
✅ Test new key thoroughly before production  
✅ Wait 24-48 hours before revoking old key  
✅ Monitor usage after rotation  
✅ Document all rotations  
✅ Use secrets management systems  
✅ Set up usage alerts in OpenAI dashboard

### DON'T:
❌ Hardcode API keys in source code  
❌ Commit keys to version control  
❌ Share keys via email or chat  
❌ Use same key for dev and production  
❌ Revoke old key immediately after deployment  
❌ Skip testing new key  
❌ Ignore usage patterns after rotation  
❌ Store keys in plain text

---

## Related Workflows

**Related Security Workflows:**
- [[sec-005]](anthropic_key_rotation.md) - Rotate Anthropic keys similarly
- [[sec-004]](secret_management_solo.md) - General secret management
- [[sec-003]](secret_incident_solo.md) - If key was compromised

**After Rotation:**
- [[dvo-001]](../devops/application_monitoring_setup.md) - Monitor API usage
- [[sec-001]](code_buddy_secret_rules.md) - Review secret handling rules

---

## Tags

`security` `api-keys` `openai` `gpt` `rotation` `credentials` `secrets-management` `compliance`
