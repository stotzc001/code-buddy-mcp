# Feature Flag Management

**Category:** Development  
**Complexity:** Intermediate  
**Estimated Time:** 1-3 hours (initial setup), 15 minutes (per flag)  
**Prerequisites:** Basic understanding of feature toggles  

---

## Overview

Feature flags (also called feature toggles) allow you to enable or disable functionality without deploying new code. This workflow covers implementing, managing, and safely removing feature flags.

**When to Use:**
- Rolling out new features gradually
- Testing in production with subset of users
- Enabling features for specific customers
- Emergency kill switches for problematic features
- A/B testing different implementations
- Decoupling deployment from release

**Benefits:**
- Deploy code at any time, even if feature isn't ready
- Instant rollback without redeployment
- Gradual rollout to manage risk
- Test in production safely
- Trunk-based development without long-lived branches

---

## Quick Start

```python
# 1. Install feature flag library
pip install flagsmith-python  # or LaunchDarkly, Unleash, etc.

# 2. Add feature flag check
from feature_flags import flags

if flags.is_enabled('new_checkout_flow', user_id=user.id):
    return new_checkout_process()
else:
    return legacy_checkout_process()

# 3. Control flag via admin dashboard
# 4. Gradually roll out: 1% → 10% → 50% → 100%
# 5. Remove flag after full rollout
```

---

## Step-by-Step Guide

### Phase 1: Setup Feature Flag System (1-2 hours, one-time)

**Choose a Feature Flag Solution:**

```markdown
## Options Comparison

**Self-Hosted Options:**
1. **Unleash** (Open Source)
   - Self-hosted, full control
   - Good UI, multiple strategies
   - Requires maintenance

2. **FlagSmith** (Open Source)
   - Self-hosted or cloud
   - Simple, modern UI
   - Good SDK support

3. **Custom Solution**
   - Database table + cache
   - Full control, no dependencies
   - More maintenance required

**Cloud Options:**
1. **LaunchDarkly**
   - Enterprise features
   - Excellent SDK support
   - $$$ pricing

2. **Split.io**
   - A/B testing focused
   - Good analytics
   - Mid-tier pricing

3. **ConfigCat**
   - Simple, affordable
   - Good for smaller teams
   - Limited advanced features
```

**Install and Configure:**

```bash
# Example: Using Unleash
docker-compose.yml:
```
```yaml
version: '3'
services:
  unleash:
    image: unleashorg/unleash-server:latest
    ports:
      - "4242:4242"
    environment:
      DATABASE_URL: postgres://unleash:unleash@postgres/unleash
      DATABASE_SSL: false
    depends_on:
      - postgres
  
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: unleash
      POSTGRES_USER: unleash
      POSTGRES_PASSWORD: unleash
```

```bash
# Start the service
docker-compose up -d

# Access UI at http://localhost:4242
# Default: admin / unleash4all
```

**Initialize in Application:**

```python
# config/feature_flags.py
from unleashclient import UnleashClient
import os

client = UnleashClient(
    url=os.getenv("UNLEASH_URL", "http://localhost:4242/api/"),
    app_name="my-app",
    custom_headers={'Authorization': os.getenv("UNLEASH_API_KEY")},
)

client.initialize_client()

def is_enabled(flag_name: str, context: dict = None) -> bool:
    """Check if a feature flag is enabled."""
    return client.is_enabled(
        flag_name,
        context=context
    )

# Usage
from config.feature_flags import is_enabled

if is_enabled('new_payment_flow', {'userId': str(user.id)}):
    return new_payment_handler()
else:
    return legacy_payment_handler()
```

---

### Phase 2: Create and Use Feature Flags (15-30 minutes per flag)

**Flag Naming Conventions:**

```python
# Naming Pattern: <category>_<feature>_<variant?>

# ✅ GOOD names:
'payment_stripe_integration'
'ui_new_dashboard'
'api_v2_endpoints'
'optimization_cached_queries'
'experiment_checkout_flow_v2'

# ❌ BAD names:
'test'
'new_stuff'
'fix'
'temporary'
```

**Create Flag in System:**

```python
# Via API (example)
import requests

response = requests.post(
    'http://unleash:4242/api/admin/features',
    headers={'Authorization': f'Bearer {ADMIN_TOKEN}'},
    json={
        'name': 'payment_stripe_integration',
        'description': 'Enable new Stripe payment integration',
        'type': 'release',  # release, experiment, ops, permission
        'enabled': False,  # Start disabled
        'strategies': [
            {
                'name': 'default',
                'parameters': {}
            }
        ]
    }
)
```

**Implement in Code:**

```python
# Example 1: Simple boolean flag
def process_payment(user, amount):
    if is_enabled('payment_stripe_integration'):
        return stripe_payment(user, amount)
    else:
        return legacy_payment(user, amount)

# Example 2: Gradual rollout
def get_dashboard_view(user):
    if is_enabled('ui_new_dashboard', {'userId': str(user.id)}):
        return render('dashboard_v2.html')
    else:
        return render('dashboard_v1.html')

# Example 3: Multi-variant testing
def get_checkout_flow(user):
    variant = get_variant('experiment_checkout_flow', {'userId': str(user.id)})
    
    if variant == 'one_page':
        return render('checkout_single_page.html')
    elif variant == 'multi_step':
        return render('checkout_multi_step.html')
    else:
        return render('checkout_default.html')

# Example 4: Kill switch
def run_expensive_operation():
    if not is_enabled('kill_switch_expensive_ops'):
        return expensive_calculation()
    else:
        return cached_result()  # Fallback when disabled
```

---

### Phase 3: Rollout Strategy (varies by approach)

**Gradual Percentage Rollout:**

```python
# Day 1: Enable for 1% of users
# Configure in Unleash UI:
# Strategy: Gradual rollout
# Percentage: 1%
# Sticky: Yes (same users get same experience)

# Monitor metrics for 24 hours

# Day 2: Increase to 10% if stable
# Day 3: Increase to 25%
# Day 4: Increase to 50%
# Day 5: Increase to 100%

# At each stage, monitor:
# - Error rates
# - Performance metrics
# - User feedback
# - Business metrics
```

**Target Specific Users:**

```python
# Strategy: User ID targeting
# Enable for specific users (beta testers, employees)

# Via Unleash constraints:
{
    'name': 'userIdConstraint',
    'parameters': {
        'userIds': 'user-1,user-2,user-3'
    }
}

# Or via custom logic:
def is_enabled_for_user(flag_name, user):
    if user.is_staff or user.is_beta_tester:
        return True
    return is_enabled(flag_name, {'userId': str(user.id)})
```

**A/B Testing:**

```python
# Split traffic 50/50 between variants
def show_pricing_page(user):
    variant = get_variant('experiment_pricing_page', {
        'userId': str(user.id)
    })
    
    if variant == 'monthly_first':
        return render('pricing_monthly_first.html')
    elif variant == 'annual_first':
        return render('pricing_annual_first.html')
    else:
        return render('pricing_default.html')

# Track metrics for each variant
analytics.track('pricing_page_viewed', {
    'variant': variant,
    'userId': user.id
})
```

---

### Phase 4: Monitor and Evaluate (ongoing)

**Set Up Monitoring:**

```python
# Log flag evaluations
import logging

logger = logging.getLogger(__name__)

def is_enabled_with_logging(flag_name, context=None):
    result = is_enabled(flag_name, context)
    logger.info(f"Feature flag {flag_name} evaluated to {result}", extra={
        'flag_name': flag_name,
        'result': result,
        'context': context
    })
    return result

# Track in analytics
from analytics import track

def is_enabled_with_tracking(flag_name, user_id):
    result = is_enabled(flag_name, {'userId': user_id})
    track('feature_flag_evaluated', {
        'flag_name': flag_name,
        'result': result,
        'user_id': user_id
    })
    return result
```

**Dashboard Example:**

```markdown
## Feature Flag Dashboard

| Flag | Status | Rollout % | Users Affected | Error Rate | Conversion |
|------|--------|-----------|----------------|------------|------------|
| payment_stripe | 🟢 Active | 100% | 10,432 | 0.02% | +2.3% |
| ui_new_dashboard | 🟡 Rolling | 50% | 5,216 | 0.01% | +5.1% |
| api_v2_endpoints | 🔴 Disabled | 0% | 0 | N/A | N/A |
```

---

### Phase 5: Remove Feature Flags (15-30 minutes)

**When to Remove:**
- Feature fully rolled out to 100% for 2+ weeks
- No issues reported
- Business metrics stable or improved
- Team confident in keeping the feature

**Removal Process:**

```python
# Step 1: Ensure flag is at 100% and stable
# Monitor for 1-2 weeks at 100%

# Step 2: Remove flag checks from code
# BEFORE:
def process_payment(user, amount):
    if is_enabled('payment_stripe_integration'):
        return stripe_payment(user, amount)
    else:
        return legacy_payment(user, amount)

# AFTER:
def process_payment(user, amount):
    return stripe_payment(user, amount)

# Step 3: Remove old code paths
# Delete legacy_payment() function if no longer needed

# Step 4: Remove flag from feature flag system
# Via UI or API

# Step 5: Deploy and monitor
# Ensure no errors from removed flag checks
```

**Stale Flag Cleanup:**

```bash
# Find flags not checked in code
# Script to detect unused flags

# List all flags in system
curl -H "Authorization: Bearer $TOKEN" \
  http://unleash:4242/api/admin/features \
  | jq -r '.[].name'

# Search codebase for each flag
for flag in $(cat flags.txt); do
  if ! grep -r "$flag" src/; then
    echo "Unused flag: $flag"
  fi
done
```

---

## Best Practices

### DO:
✅ **Use descriptive names** - Clear, consistent naming convention  
✅ **Set expiration dates** - Flags should be temporary  
✅ **Monitor flag usage** - Track evaluation and outcomes  
✅ **Document flags** - Why they exist, when to remove  
✅ **Clean up old flags** - Remove after full rollout  
✅ **Test both paths** - Ensure flag on AND off work correctly  

### DON'T:
❌ **Use flags for configuration** - Use config management instead  
❌ **Let flags accumulate** - Remove after rollout  
❌ **Skip testing both paths** - Both code paths must work  
❌ **Use flags for permissions** - Use proper authorization  
❌ **Over-use flags** - Not every feature needs a flag  
❌ **Forget flag context** - Remember to remove them later  

---

## Common Patterns

### Kill Switch Pattern

```python
# Emergency disable for problematic features

if is_enabled('feature_enabled') and not is_enabled('kill_switch_feature'):
    return new_feature()
else:
    return fallback_safe_behavior()

# Can instantly disable via kill switch without redeployment
```

### Progressive Rollout Pattern

```python
# Gradual rollout with automatic progression

# Week 1: Internal employees only
if is_enabled('new_feature', {'userType': 'employee'}):
    return new_feature()

# Week 2: Beta users (5%)
if is_enabled('new_feature', {'userType': 'beta'}) or \
   is_enabled('new_feature_5pct', {'userId': user.id}):
    return new_feature()

# Week 3: 25%
# Week 4: 100%
```

### Dependency Flag Pattern

```python
# Flags that depend on other flags

def get_feature_state():
    # Parent flag must be enabled
    if not is_enabled('parent_feature'):
        return 'disabled'
    
    # Child flag only matters if parent enabled
    if is_enabled('child_enhancement'):
        return 'enhanced'
    else:
        return 'basic'
```

---

## Troubleshooting

### Issue: Flag State Cached Incorrectly

**Symptoms:**
- Flag changes not reflected immediately
- Users see old behavior after flag toggle
- Inconsistent behavior across servers

**Solution:**
```python
# Implement flag refresh mechanism
from threading import Thread
import time

def refresh_flags_periodically():
    while True:
        client.refresh()
        time.sleep(60)  # Refresh every minute

# Start background thread
Thread(target=refresh_flags_periodically, daemon=True).start()

# Or use webhook to invalidate cache immediately
@app.route('/webhooks/feature-flags', methods=['POST'])
def feature_flag_webhook():
    client.refresh()
    return '', 200
```

---

### Issue: Too Many Feature Flags

**Symptoms:**
- Dozens of active flags
- Team losing track of what flags do
- Code becoming hard to understand

**Solution:**
```markdown
# Regular Flag Cleanup

## Monthly Review Process:

1. **List all active flags**
   - Export from feature flag system
   - Check last evaluation date

2. **Categorize flags**
   - Fully rolled out (remove immediately)
   - Rolling out (keep monitoring)
   - Experimental (review results)
   - Kill switches (keep but document)

3. **Clean up stale flags**
   - Remove flags at 100% for >2 weeks
   - Remove experiment flags with clear winner
   - Archive killed features

4. **Update documentation**
   - Document remaining flags
   - Set removal dates
```

---

## Related Workflows

**Prerequisites:**
- `dev-xxx_environment_initialization.md` - Setting up feature flag system
- `dev-xxx_deployment_strategy.md` - Understanding deployment approaches

**Next Steps:**
- `dev-xxx_hotfix_procedure.md` - Using flags instead of hotfixes
- `devops-xxx_rollback_procedure.md` - Instant rollback via flags
- `qa-xxx_production_testing.md` - Testing features in production

**Related:**
- `dev-xxx_breaking_api_changes.md` - Managing breaking changes with flags
- `frontend-xxx_ab_testing.md` - A/B testing implementation

---

## Tags

`development` `feature-flags` `feature-toggles` `deployment` `gradual-rollout` `ab-testing` `production` `release-management`
