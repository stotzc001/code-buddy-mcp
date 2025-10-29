# Deployment Strategy

**ID:** dev-036  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 2-4 hours (planning), ongoing implementation  
**Prerequisites:** Understanding of your application architecture  

---

## Overview

A deployment strategy defines how new versions of your application are released to production. This workflow helps you choose and implement the right deployment approach for your needs.

**When to Use:**
- Setting up deployment process for new application
- Improving existing deployment workflow
- Reducing deployment risk
- Planning for zero-downtime deployments
- Scaling deployment process

---

## Quick Start

```bash
# Choose your strategy based on needs:
# 1. Simple apps: Rolling deployment
# 2. Risk-averse: Blue-green deployment  
# 3. Gradual testing: Canary deployment
# 4. Instant rollback: Feature flags

# Example: Rolling deployment
kubectl set image deployment/api-server api-server=v1.2.3
kubectl rollout status deployment/api-server
```

---

## Deployment Strategies Overview

### Strategy Comparison

```markdown
| Strategy | Downtime | Rollback Speed | Complexity | Cost | Best For |
|----------|----------|----------------|------------|------|----------|
| Recreate | Yes (full) | Slow | Very Low | Low | Dev/test environments |
| Rolling | None | Moderate | Low | Low | Most applications |
| Blue-Green | None | Instant | Moderate | High (2x resources) | Critical apps |
| Canary | None | Fast | Moderate | Low | Risk reduction |
| A/B Testing | None | Fast | High | Moderate | Feature testing |
| Shadow | None | N/A | Moderate | Moderate | Testing at scale |
```

---

## Strategy Details

### 1. Recreate Deployment

**What:** Shut down old version, deploy new version

```yaml
# Kubernetes example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  strategy:
    type: Recreate  # All pods stopped, then new ones created
  template:
    spec:
      containers:
      - name: api-server
        image: myapp:v1.2.3
```

**Process:**
```bash
# 1. Stop old version
kubectl scale deployment/api-server --replicas=0

# 2. Deploy new version
kubectl set image deployment/api-server api-server=v1.2.3
kubectl scale deployment/api-server --replicas=3

# 3. Wait for readiness
kubectl wait --for=condition=ready pod -l app=api-server
```

**Pros:**
- ✅ Simplest strategy
- ✅ No resource overhead
- ✅ Clean transition
- ✅ No version conflicts

**Cons:**
- ❌ Downtime during deployment
- ❌ Slow rollback
- ❌ All-or-nothing risk

**Best For:** Development, staging, maintenance windows

---

### 2. Rolling Deployment

**What:** Gradually replace old pods with new ones

```yaml
# Kubernetes example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # Max 2 extra pods during update
      maxUnavailable: 1  # Max 1 pod down during update
  template:
    spec:
      containers:
      - name: api-server
        image: myapp:v1.2.3
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Process:**
```bash
# 1. Start rolling update
kubectl set image deployment/api-server api-server=v1.2.3

# 2. Monitor progress
kubectl rollout status deployment/api-server

# 3. Verify deployment
kubectl get pods -l app=api-server

# 4. Check application health
curl https://api.example.com/health

# If problems occur, rollback
kubectl rollout undo deployment/api-server
```

**Pros:**
- ✅ Zero downtime
- ✅ Low resource overhead
- ✅ Gradual transition
- ✅ Easy to automate

**Cons:**
- ❌ Slow rollback (must roll forward through all replicas)
- ❌ Both versions running simultaneously (potential issues)
- ❌ No instant traffic switch

**Best For:** Most web applications, stateless services

---

### 3. Blue-Green Deployment

**What:** Two identical environments, switch traffic between them

```yaml
# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server-blue
  labels:
    version: blue
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: api-server
        image: myapp:v1.2.2  # Current version

---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server-green
  labels:
    version: green
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: api-server
        image: myapp:v1.2.3  # New version

---
# Service that switches between blue and green
apiVersion: v1
kind: Service
metadata:
  name: api-server
spec:
  selector:
    app: api-server
    version: blue  # Switch to 'green' to cutover
  ports:
    - port: 80
      targetPort: 8080
```

**Process:**
```bash
# 1. Current state: Blue environment active
kubectl get svc api-server
# selector: version=blue

# 2. Deploy green environment
kubectl apply -f deployment-green.yaml
kubectl wait --for=condition=ready pod -l version=green

# 3. Test green environment
curl http://green-api-server/health
# Run smoke tests against green

# 4. Switch traffic to green
kubectl patch service api-server -p '{"spec":{"selector":{"version":"green"}}}'

# 5. Monitor green environment
# Watch metrics, logs, alerts

# 6. If issues, instantly switch back to blue
kubectl patch service api-server -p '{"spec":{"selector":{"version":"blue"}}}'

# 7. Once stable, tear down blue
kubectl delete deployment api-server-blue
```

**Pros:**
- ✅ Instant rollback (flip traffic back)
- ✅ Full testing before cutover
- ✅ Zero downtime
- ✅ Clean separation of old/new

**Cons:**
- ❌ Double resource cost (both environments running)
- ❌ Database migration complexity
- ❌ More infrastructure to manage

**Best For:** Critical applications, risk-averse organizations, large deployments

---

### 4. Canary Deployment

**What:** Route small percentage of traffic to new version

```yaml
# Main deployment (stable version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server-stable
spec:
  replicas: 9
  template:
    metadata:
      labels:
        app: api-server
        version: stable
    spec:
      containers:
      - name: api-server
        image: myapp:v1.2.2

---
# Canary deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server-canary
spec:
  replicas: 1  # 10% of traffic
  template:
    metadata:
      labels:
        app: api-server
        version: canary
    spec:
      containers:
      - name: api-server
        image: myapp:v1.2.3

---
# Service routes to both
apiVersion: v1
kind: Service
metadata:
  name: api-server
spec:
  selector:
    app: api-server  # Matches both stable and canary
  ports:
    - port: 80
      targetPort: 8080
```

**Process:**
```bash
# 1. Deploy canary with 10% traffic
kubectl apply -f deployment-canary.yaml

# 2. Monitor canary metrics
# - Error rate
# - Response time
# - Resource usage
# Compare canary vs stable

# 3. Gradually increase canary percentage
# 10% → 25% → 50% → 100%
kubectl scale deployment/api-server-canary --replicas=2  # 20%
kubectl scale deployment/api-server-stable --replicas=8

# 4. Monitor at each stage

# 5. Full cutover when confident
kubectl scale deployment/api-server-canary --replicas=10
kubectl scale deployment/api-server-stable --replicas=0

# 6. Clean up old deployment
kubectl delete deployment api-server-stable
```

**Pros:**
- ✅ Gradual risk exposure
- ✅ Real-world testing
- ✅ Fast rollback
- ✅ Metrics-driven decisions

**Cons:**
- ❌ More complex to manage
- ❌ Requires good monitoring
- ❌ Longer deployment time

**Best For:** High-risk changes, performance optimization, new features

---

### 5. Feature Flag Deployment

**What:** Deploy code but control feature enablement

```python
# Deploy new code with feature disabled
from feature_flags import is_enabled

def process_payment(user, amount):
    if is_enabled('new_payment_processor', user_id=user.id):
        return new_payment_flow(user, amount)
    else:
        return legacy_payment_flow(user, amount)

# Gradually enable:
# 1% → 10% → 25% → 50% → 100%
# Can disable instantly if issues found
```

**Process:**
```bash
# 1. Deploy code with feature flag off
git push origin main
# CI/CD deploys with new_payment_processor=false

# 2. Test with feature flag on for test users
# Enable for internal users first

# 3. Gradually roll out
# Day 1: 1% of users
# Day 2: 10% of users
# Day 3: 25% of users
# Day 4: 100% of users

# 4. Remove flag once stable
# Delete feature flag checks from code
```

**Pros:**
- ✅ Instant enable/disable
- ✅ Gradual rollout
- ✅ A/B testing capable
- ✅ No redeployment for changes

**Cons:**
- ❌ Code complexity (two paths)
- ❌ Technical debt (flags must be removed)
- ❌ Requires flag management system

**Best For:** Frequent deployments, gradual rollouts, A/B testing

---

## Choosing Your Strategy

### Decision Tree

```markdown
Do you need zero downtime?
├─ NO → Use Recreate (simplest)
└─ YES → Continue
    │
    Do you need instant rollback?
    ├─ YES → Use Blue-Green or Feature Flags
    └─ NO → Continue
        │
        Is this a high-risk change?
        ├─ YES → Use Canary
        └─ NO → Use Rolling Update

Cost concerns?
├─ YES → Rolling or Canary (no double resources)
└─ NO → Blue-Green (safest)
```

### Common Combinations

```markdown
## Recommended Combinations:

**Small Startup:**
- Rolling deployment for most changes
- Feature flags for risky features
- Blue-green for major releases

**Growing Company:**
- Canary for backend services
- Feature flags for frontend
- Blue-green for critical services

**Enterprise:**
- Blue-green for all production deployments
- Canary for gradual rollouts
- Feature flags for feature management
- Shadow deployment for load testing
```

---

## Implementation Examples

### Complete CI/CD Pipeline with Multiple Strategies

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
      - uses: actions/checkout@v2
      
      - name: Build and Push Image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push myapp:${{ github.sha }}
      
      - name: Deploy Canary (10%)
        run: |
          kubectl set image deployment/api-server-canary \
            api-server=myapp:${{ github.sha }}
          kubectl wait --for=condition=ready \
            pod -l app=api-server,version=canary
      
      - name: Monitor Canary
        run: |
          # Wait 5 minutes and check error rates
          sleep 300
          ERROR_RATE=$(./check_error_rate.sh canary)
          if [ $ERROR_RATE -gt 5 ]; then
            echo "Canary error rate too high"
            exit 1
          fi
      
      - name: Promote to Production
        if: success()
        run: |
          kubectl set image deployment/api-server-stable \
            api-server=myapp:${{ github.sha }}
          kubectl rollout status deployment/api-server-stable
```

---

## Best Practices

### DO:
✅ **Always have health checks** - Critical for automated deployments  
✅ **Monitor key metrics** - Error rate, latency, resource usage  
✅ **Test rollback procedure** - Practice before you need it  
✅ **Automate everything** - Reduce human error  
✅ **Use staging environment** - Test deployment process  
✅ **Document runbooks** - Clear instructions for team  

### DON'T:
❌ **Deploy on Fridays** - Unless you enjoy weekend work  
❌ **Skip monitoring** - How else will you know if it works?  
❌ **Ignore failed health checks** - They fail for a reason  
❌ **Deploy without rollback plan** - Hope is not a strategy  
❌ **Over-complicate** - Start simple, add complexity if needed  

---

## Related Workflows

**Prerequisites:**
- [[dvo-006]] CI/CD Pipeline Setup - Setting up automation
- [[dvo-012]] Kubernetes Deployment - Container orchestration

**Next Steps:**
- [[dev-012]] Feature Flag Management - Feature toggle strategy
- [[dvo-015]] Rollback Procedure - Handling failed deployments
- [[dvo-009]] Incident Response Workflow - When things go wrong

---

## Tags

`development` `deployment` `devops` `ci-cd` `blue-green` `canary` `rolling` `zero-downtime` `kubernetes` `production`
