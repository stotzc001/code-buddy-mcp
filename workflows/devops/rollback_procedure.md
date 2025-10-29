# Rollback Procedure

**ID:** dvo-015  
**Category:** DevOps  
**Priority:** CRITICAL  
**Complexity:** Intermediate  
**Estimated Time:** 5-30 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic procedure for safely rolling back deployments when issues are detected in production, minimizing downtime and restoring service to a known-good state.

**Why:** Rollbacks are the fastest path to recovery when a deployment introduces bugs, performance issues, or breaks functionality. A well-executed rollback can restore service in minutes, while attempting to fix forward could take hours. Fast, reliable rollbacks are essential for maintaining high availability and user trust.

**When to use:**
- New deployment causing errors or crashes
- Performance degradation after release
- Critical bug discovered in production
- Failed deployment (partial rollout stuck)
- Database migration causing issues
- Configuration change breaking functionality
- Security vulnerability introduced
- Unexpected behavior affecting users

---

## Prerequisites

**Required:**
- [ ] Production access with deployment permissions
- [ ] Version control access (Git)
- [ ] CI/CD pipeline access
- [ ] Kubernetes/deployment platform access
- [ ] Monitoring dashboard access
- [ ] Database backup if schema changed
- [ ] Incident communication channel

**Check before starting:**
```bash
# Verify deployment platform access
kubectl auth can-i update deployments -n production  # Kubernetes
aws sts get-caller-identity  # AWS ECS
gcloud auth list  # GCP

# Check current deployment version
kubectl get deployment myapp -n production -o jsonpath='{.spec.template.spec.containers[0].image}'

# Verify rollback capability
kubectl rollout history deployment/myapp -n production

# Confirm monitoring access
curl -s https://grafana.example.com/api/health

# Check for active incidents
pagerduty-cli incident list --status triggered
```

**Safety considerations:**
- [ ] Database migrations are reversible or backwards compatible
- [ ] No data loss will occur from rollback
- [ ] Rollback tested in staging environment
- [ ] Stakeholders notified of rollback decision
- [ ] Backup of current state available

---

## Implementation Steps

### Step 1: Assess Situation and Make Rollback Decision

**What:** Evaluate whether rollback is the appropriate action and determine the scope.

**How:**

**Decision matrix:**
```markdown
ROLLBACK when:
✅ Service is down or severely degraded
✅ Critical bugs affecting users
✅ Data integrity at risk
✅ Security vulnerability introduced
✅ Performance significantly degraded
✅ Can't find quick fix
✅ Issue reproducible and deployment-related

INVESTIGATE FIRST when:
❓ Minor UI issues
❓ Edge case bugs
❓ Non-user-facing problems
❓ Can fix forward quickly (< 10 min)
❓ Unclear if deployment-related
❓ Isolated to small user subset

DON'T ROLLBACK when:
❌ Database migration is irreversible
❌ Rollback would cause data loss
❌ Issue is in infrastructure, not code
❌ External dependency is the problem
❌ Previous version had same issue
```

**Quick assessment checklist:**
```bash
# 1. When did the issue start?
# Check monitoring for exact time
grafana-cli dashboard view deployment-history

# 2. When was the last deployment?
kubectl rollout history deployment/myapp -n production

# 3. Are they correlated?
# If deployment at 14:00 and issues started 14:05 → Likely related

# 4. Can we confirm the previous version was stable?
# Check metrics for previous version
datadog query "avg:api.requests{version:v2.33,status:error}" --last 24h

# 5. What will we lose by rolling back?
# New features, database changes, etc.
git diff v2.33..v2.34 --stat
```

**Make decision:**
```bash
# Announce rollback decision
slack-notify "#incident-response" \
  "🔄 DECISION: Rolling back deployment
  
  Current version: v2.34 (deployed 14:00 UTC)
  Rolling back to: v2.33
  Reason: API error rate 15% (normal: 0.1%)
  Expected downtime: 2-5 minutes
  
  IC: @oncall-engineer
  Starting rollback in 2 minutes unless objections"

# Document decision
echo "$(date): Decision to rollback v2.34 → v2.33 due to high error rate" \
  >> /var/log/deployments/rollback-log.txt
```

**Verification:**
- [ ] Issue confirmed to be deployment-related
- [ ] Rollback is safe (no data loss)
- [ ] Previous version was stable
- [ ] Team agrees with decision
- [ ] Stakeholders notified

**If This Fails:**
→ If unsure, err on side of rollback (can redeploy later)
→ If previous version also has issues, investigate infrastructure
→ If rollback unsafe due to data changes, fix forward

---

### Step 2: Prepare for Rollback

**What:** Identify target version, verify it's available, and prepare safety measures.

**How:**

**Identify target version:**
```bash
# List recent deployment history
kubectl rollout history deployment/myapp -n production

# Output:
# REVISION  CHANGE-CAUSE
# 43        Deploy v2.31
# 44        Deploy v2.32
# 45        Deploy v2.33
# 46        Deploy v2.34 (current)

# Usually rollback to immediately previous version (45)
TARGET_REVISION=45
TARGET_VERSION="v2.33"

# Verify target version details
kubectl rollout history deployment/myapp -n production --revision=45

# Check target image exists in registry
docker manifest inspect myregistry.io/myapp:v2.33
# or
aws ecr describe-images --repository-name myapp --image-ids imageTag=v2.33
```

**Verify target version health:**
```bash
# Check metrics from when target version was running
datadog query "avg:api.error_rate{version:v2.33}" \
  --from "48 hours ago" \
  --to "24 hours ago"

# Review target version in Git
git log v2.33 --oneline
git show v2.33:CHANGELOG.md

# Check for known issues
gh issue list --label "v2.33"
```

**Create rollback snapshot:**
```bash
# Backup current state before rollback
kubectl get deployment myapp -n production -o yaml > \
  backup-deployment-$(date +%Y%m%d-%H%M%S).yaml

# Backup configmaps and secrets
kubectl get configmap myapp-config -n production -o yaml > \
  backup-configmap-$(date +%Y%m%d-%H%M%S).yaml

# If database involved, verify backup
pg_dump production > backup-$(date +%Y%m%d-%H%M%S).sql
aws s3 cp backup-*.sql s3://backups/pre-rollback/
```

**Prepare communication:**
```markdown
# Status Page Template
**Investigating Service Issues**

We are experiencing issues with [service name] and are 
preparing to rollback to restore service.

Status: Preparing rollback
Expected resolution: 5-10 minutes
Updates: Every 5 minutes

Last update: [timestamp]
```

**Verification:**
- [ ] Target version identified
- [ ] Target version exists in registry
- [ ] Target version was previously stable
- [ ] Current state backed up
- [ ] Communication template ready
- [ ] Team standing by

**If This Fails:**
→ If target version not in registry, rebuild from Git tag
→ If uncertain about target version, consult Git history
→ If backup fails, proceed with caution or wait for backup

---

### Step 3: Execute Rollback

**What:** Perform the actual rollback using the fastest safe method.

**How:**

**Method 1: Kubernetes Rollback (Most Common)**
```bash
# 1. Announce start
slack-notify "#incident-response" \
  "⚠️  STARTING ROLLBACK NOW
  From: v2.34 → To: v2.33
  Watch: https://grafana.example.com/deployment"

# 2. Execute rollback
kubectl rollout undo deployment/myapp -n production

# Or rollback to specific revision
kubectl rollout undo deployment/myapp -n production --to-revision=45

# 3. Monitor rollback progress
kubectl rollout status deployment/myapp -n production --watch

# Output:
# Waiting for deployment "myapp" rollout to finish: 0 of 3 updated replicas are available...
# Waiting for deployment "myapp" rollout to finish: 1 of 3 updated replicas are available...
# Waiting for deployment "myapp" rollout to finish: 2 of 3 updated replicas are available...
# deployment "myapp" successfully rolled out

# 4. Verify pods are running target version
kubectl get pods -n production -l app=myapp \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'

# 5. Check pod health
kubectl get pods -n production -l app=myapp
# All should show STATUS: Running and READY: 1/1
```

**Method 2: Docker Compose**
```bash
# 1. Update docker-compose.yml to previous version
sed -i 's/myapp:v2.34/myapp:v2.33/g' docker-compose.yml

# 2. Pull previous image
docker-compose pull

# 3. Recreate containers
docker-compose up -d --force-recreate

# 4. Monitor logs
docker-compose logs -f --tail=100
```

**Method 3: AWS ECS**
```bash
# 1. Get previous task definition
aws ecs describe-task-definition \
  --task-definition myapp:45 \
  --query 'taskDefinition' \
  > task-definition-v45.json

# 2. Register and deploy previous task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition-v45.json

aws ecs update-service \
  --cluster production \
  --service myapp \
  --task-definition myapp:45 \
  --force-new-deployment

# 3. Monitor deployment
aws ecs wait services-stable \
  --cluster production \
  --services myapp
```

**Method 4: Systemd Service**
```bash
# 1. Stop current version
sudo systemctl stop myapp

# 2. Checkout previous version
cd /opt/myapp
git fetch --all
git checkout v2.33

# 3. Restore dependencies if needed
pip install -r requirements.txt --force-reinstall

# 4. Restart service
sudo systemctl start myapp
sudo systemctl status myapp
```

**Method 5: Blue-Green Deployment Rollback**
```bash
# Simply switch traffic back to blue (old) environment
# AWS
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$BLUE_TG_ARN

# Or update DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file://switch-to-blue.json
```

**Rollback timing expectations:**
```markdown
Kubernetes:          2-5 minutes
Docker Compose:      1-3 minutes
AWS ECS:            5-10 minutes
Systemd:            1-2 minutes
Blue-Green (DNS):   5-60 minutes (DNS propagation)
Blue-Green (LB):    1-2 minutes
```

**Monitor during rollback:**
```bash
# Watch key metrics in real-time
watch -n 5 '
echo "Error Rate:"
curl -s "https://api.example.com/metrics" | grep error_rate
echo ""
echo "Active Pods:"
kubectl get pods -n production | grep myapp | grep Running | wc -l
echo ""
echo "Health Checks:"
curl -s "https://api.example.com/health" | jq .status
'
```

**Verification:**
- [ ] Rollback command executed successfully
- [ ] All pods/containers running target version
- [ ] No crash loops or restart failures
- [ ] Health checks passing
- [ ] Deployment status shows stable

**If This Fails:**
→ Check pod/container logs immediately
→ If new version stuck terminating, force delete pods
→ If rollback hangs, check resource quotas
→ Escalate if unable to complete in 10 minutes

---

### Step 4: Verify Service Recovery

**What:** Confirm the rollback successfully restored service functionality.

**How:**

**Immediate checks (first 2 minutes):**
```bash
# 1. Health endpoint responding
for i in {1..10}; do
  curl -f https://api.example.com/health && echo " ✅ " || echo " ❌ "
  sleep 1
done

# 2. Error rate dropping
kubectl logs -l app=myapp -n production --tail=50 | grep -i error
# Should show decreasing errors

# 3. Response times improving
while true; do
  curl -w "Response time: %{time_total}s\n" -s -o /dev/null https://api.example.com/api/users
  sleep 2
done
# Should see sub-second responses

# 4. Pods stable
kubectl get pods -n production -l app=myapp
# All should be Running, no CrashLoopBackOff
```

**Functional verification (5-10 minutes):**
```bash
# Run smoke tests
./scripts/smoke-tests.sh production

# Example smoke tests:
# - User login works
# - API endpoints return valid data
# - Payment processing functions
# - Database queries succeed
# - File uploads work
# - Email sending functional

# Check critical workflows
curl -X POST https://api.example.com/api/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "product_id": "123"}'
# Should return 201 Created
```

**Metrics verification (10-15 minutes):**
```bash
# Compare metrics before/after rollback
datadog query "avg:api.error_rate{env:production}" --last 1h

# Expected results:
# Before rollback: 10-15% error rate
# After rollback: < 0.5% error rate

# Check key metrics dashboard
grafana-cli dashboard view deployment-metrics

# Verify:
# ✅ Error rate back to normal
# ✅ Response time at baseline
# ✅ Request rate stable
# ✅ CPU/memory normal
# ✅ No new alerts firing
```

**Customer impact assessment:**
```bash
# Check support ticket rate
zendesk-cli tickets list --created-since "1 hour ago" --count
# Should see decreasing trend

# Monitor social media mentions
twitter search "myapp down OR myapp error" --since "1 hour ago"
# Complaints should be decreasing

# Check user-reported issues
select count(*) from error_reports 
where created_at > now() - interval '1 hour'
group by date_trunc('minute', created_at)
order by 1 desc;
# Should see declining reports
```

**Database integrity check:**
```bash
# If database migrations were involved
# Verify data consistency
psql production -c "
  SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables 
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
  LIMIT 10;
"

# Check for orphaned records or data issues
./scripts/data-integrity-check.sh
```

**Verification:**
- [ ] Service responding within normal latency
- [ ] Error rates at baseline levels
- [ ] All smoke tests passing
- [ ] No new incidents or alerts
- [ ] Customer complaints declining
- [ ] Database integrity confirmed
- [ ] Metrics stable for 15+ minutes

**If This Fails:**
→ If errors persist after rollback, issue may not be code-related (check infrastructure)
→ If partial recovery, may need to restart additional services
→ If no improvement, consider rolling back further (to v2.32)

---

### Step 5: Communicate Resolution

**What:** Update stakeholders on rollback status and next steps.

**How:**

**Update status page:**
```markdown
**Service Restored**

The issues affecting [service name] have been resolved through 
a rollback to a previous stable version.

Status: Resolved
Duration: [X minutes]
Action taken: Rolled back from v2.34 to v2.33

We are investigating the root cause and will provide an update
within 24 hours.

All services are now operating normally.

Resolved at: [timestamp]
```

**Post to status page:**
```bash
# Statuspage.io
curl -X PATCH https://api.statuspage.io/v1/incidents/$INCIDENT_ID \
  -H "Authorization: OAuth $TOKEN" \
  -d '{
    "incident": {
      "status": "resolved",
      "body": "Service restored via rollback to v2.33"
    }
  }'
```

**Internal stakeholder update:**
```bash
# Notify engineering team
slack-notify "#engineering" \
  "✅ ROLLBACK COMPLETE
  
  Service: API
  Rolled back: v2.34 → v2.33
  Duration: 8 minutes
  Status: Service fully restored
  
  Metrics:
  - Error rate: 0.3% (normal)
  - Response time: 145ms avg (normal)
  - All health checks: ✅
  
  Next steps:
  - Post-mortem scheduled for tomorrow 2pm
  - v2.34 blocked from production
  - Investigation into root cause starting now
  
  Thanks to response team: @alice @bob @charlie"

# Email executives if SEV-1
mail-send executives@company.com \
  --subject "RESOLVED: Production Incident" \
  --body "Service has been restored through rollback. Full post-mortem to follow."
```

**Update incident ticket:**
```bash
# PagerDuty
pagerduty-cli incident resolve --id $INCIDENT_ID \
  --note "Rollback to v2.33 completed successfully. Service restored."

# Jira
jira-cli issue update INC-12345 \
  --status "Resolved" \
  --comment "Rollback completed at $(date). Service recovered."
```

**Document for handoff:**
```markdown
# Rollback Summary - $(date)

## Actions Taken
- Rolled back deployment from v2.34 to v2.33
- Verified service recovery
- Confirmed no data loss

## Current State
- Service: ✅ Operating normally
- Version: v2.33 (stable)
- Metrics: All green
- Blocked: v2.34 from production until root cause fixed

## Investigation Needed
1. Determine what in v2.34 caused issues
2. Review why this wasn't caught in testing
3. Identify improvements to prevent recurrence

## Handoff Notes
- v2.34 should not be redeployed without fixes
- Normal on-call coverage resumes
- Post-mortem scheduled: [date/time]
```

**Verification:**
- [ ] Status page updated to "Resolved"
- [ ] All stakeholders notified
- [ ] Incident tickets closed
- [ ] Documentation updated
- [ ] Deployment pipeline blocked (for failed version)
- [ ] Handoff notes created for next shift

**If This Fails:**
→ Prioritize status page update (customers first)
→ Internal communication can be asynchronous
→ Document everything even if rushed

---

### Step 6: Block Failed Version and Prevent Redeployment

**What:** Ensure the problematic version cannot be accidentally redeployed.

**How:**

**CI/CD pipeline blocks:**
```bash
# GitHub Actions - Add check to workflow
cat >> .github/workflows/deploy.yml <<'EOF'
jobs:
  check-version:
    runs-on: ubuntu-latest
    steps:
      - name: Block known bad versions
        run: |
          VERSION=${{ github.ref_name }}
          BLOCKED_VERSIONS="v2.34 v2.29"
          
          if echo "$BLOCKED_VERSIONS" | grep -q "$VERSION"; then
            echo "❌ Version $VERSION is blocked from production"
            echo "Reason: Failed rollback on $(date)"
            exit 1
          fi
EOF

# GitLab CI
cat >> .gitlab-ci.yml <<'EOF'
check_version:
  stage: validate
  script:
    - |
      if [ "$CI_COMMIT_TAG" = "v2.34" ]; then
        echo "This version is blocked from deployment"
        exit 1
      fi
  only:
    - tags
EOF
```

**Kubernetes admission controller:**
```yaml
# ValidatingWebhookConfiguration to block image
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: block-bad-versions
webhooks:
  - name: validate-image.example.com
    clientConfig:
      service:
        name: version-validator
        namespace: default
        path: "/validate"
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: ["apps"]
        apiVersions: ["v1"]
        resources: ["deployments"]
    admissionReviewVersions: ["v1"]
    sideEffects: None
```

**Git tag protection:**
```bash
# Add notes to Git tag
git tag -a v2.34 -f -m "⚠️  BLOCKED: Do not deploy
Caused production incident on 2025-10-26
Rolled back after 8 minutes
See incident INC-12345 for details"

git push origin v2.34 --force

# Or delete tag entirely
git tag -d v2.34
git push origin :refs/tags/v2.34
```

**Container registry quarantine:**
```bash
# AWS ECR - add tag to mark bad image
aws ecr put-image-tag-mutability \
  --repository-name myapp \
  --image-tag-mutability IMMUTABLE

aws ecr tag-resource \
  --resource-arn $(aws ecr describe-images \
    --repository-name myapp \
    --image-ids imageTag=v2.34 \
    --query 'imageDetails[0].imageDigest' \
    --output text) \
  --tags Key=Status,Value=BLOCKED

# Docker Hub - delete image
docker rmi myapp:v2.34
docker push --delete myregistry.io/myapp:v2.34
```

**Documentation update:**
```bash
# Update deployment README
cat >> DEPLOYMENT.md <<'EOF'

## Blocked Versions

⚠️ **Do NOT deploy these versions:**

| Version | Date Blocked | Reason | Issue |
|---------|--------------|--------|-------|
| v2.34 | 2025-10-26 | Production incident, high error rate | INC-12345 |

Before deploying, check this list to avoid reintroducing known issues.
EOF

git add DEPLOYMENT.md
git commit -m "docs: Add v2.34 to blocked versions list"
git push
```

**Verification:**
- [ ] CI/CD pipeline blocks failed version
- [ ] Container registry tagged/deleted
- [ ] Git tag annotated or removed
- [ ] Documentation updated
- [ ] Team aware of block
- [ ] Deploy attempted and blocked (test)

**If This Fails:**
→ Minimum: Update README with blocked versions
→ Manual review required before each production deploy
→ Set calendar reminder to review blocks quarterly

---

### Step 7: Analyze Root Cause and Fix Forward

**What:** Investigate what went wrong and prepare a proper fix.

**How:**

**Root cause analysis:**
```bash
# 1. Review code changes in failed version
git diff v2.33..v2.34 --stat
git log v2.33..v2.34 --oneline

# 2. Identify suspicious changes
git diff v2.33..v2.34 -- src/payments.py
# Look for:
# - New dependencies
# - Database queries
# - API calls
# - Configuration changes
# - Resource-intensive operations

# 3. Review logs from failed deployment
kubectl logs -l app=myapp,version=v2.34 -n production --tail=1000 \
  | grep -E "ERROR|FATAL|Exception"

# 4. Check metrics during failure period
datadog query "avg:api.error_rate{version:v2.34}" \
  --from "2 hours ago" \
  --to "1 hour ago"

# 5. Reproduce locally if possible
git checkout v2.34
docker-compose up
# Try to trigger the error
```

**Common root causes:**
```markdown
🔍 Code Bugs
   - Null pointer exceptions
   - Unhandled errors
   - Logic errors in new features
   - Race conditions

🔍 Resource Issues
   - Memory leaks
   - Connection pool exhaustion
   - File descriptor leaks
   - Slow database queries

🔍 Configuration Errors
   - Wrong environment variables
   - Missing secrets
   - Incorrect service URLs
   - Mismatched versions (frontend/backend)

🔍 Dependency Problems
   - Incompatible library versions
   - Broken third-party APIs
   - Certificate expiration
   - DNS resolution issues

🔍 Database Migrations
   - Schema incompatibilities
   - Missing indexes
   - Long-running migrations
   - Data type mismatches
```

**Develop fix:**
```bash
# 1. Create fix branch
git checkout -b fix/incident-INC-12345
git rebase v2.34

# 2. Implement fix
# Example: Fix database connection leak
cat > src/payments.py <<'EOF'
def process_payment(user_id, amount):
    conn = get_db_connection()
    try:
        result = conn.execute(
            "INSERT INTO payments VALUES (%s, %s)",
            (user_id, amount)
        )
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        logger.error(f"Payment failed: {e}")
        raise
    finally:
        conn.close()  # ✅ Fixed: Always close connection
EOF

# 3. Add tests to prevent regression
cat > tests/test_payments.py <<'EOF'
def test_payment_closes_connection_on_error():
    with mock.patch('db.execute') as mock_exec:
        mock_exec.side_effect = Exception("DB Error")
        
        try:
            process_payment("user123", 100)
        except:
            pass
        
        # Verify connection.close() was called
        assert mock_connection.close.called
EOF

# 4. Commit fix
git add src/payments.py tests/test_payments.py
git commit -m "fix: Close database connections in error path

Fixes INC-12345
Without this fix, failed payment processing would leak database
connections, eventually exhausting the connection pool and causing
service outage.

Added test to ensure connections always close, even on errors."
```

**Testing the fix:**
```bash
# 1. Run full test suite
pytest tests/ -v

# 2. Run load test
locust -f tests/load/payments_test.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --host https://staging.example.com

# 3. Deploy to staging
git push origin fix/incident-INC-12345
./scripts/deploy.sh staging

# 4. Verify in staging
curl https://staging.example.com/health
./scripts/smoke-tests.sh staging

# 5. Monitor staging for 1 hour
# Watch for:
# - Memory growth
# - Connection pool usage
# - Error rates
# - Response times
```

**Create new version:**
```bash
# 1. Merge fix
git checkout main
git merge fix/incident-INC-12345

# 2. Create new release
git tag -a v2.35 -m "Release v2.35

Fixes:
- Database connection leak in payments (INC-12345)

Includes all changes from v2.34 plus fix."

git push origin main --tags

# 3. Deploy to production
./scripts/deploy.sh production v2.35

# 4. Monitor closely
watch -n 10 'kubectl get pods -n production && \
  curl -s https://api.example.com/metrics | grep -E "error_rate|connections"'
```

**Verification:**
- [ ] Root cause identified with high confidence
- [ ] Fix developed and tested
- [ ] Fix deployed to staging successfully
- [ ] Staging monitored for 1+ hour
- [ ] New version tagged (v2.35)
- [ ] Fix deployed to production
- [ ] Production stable with new version

**If This Fails:**
→ If root cause unclear, keep investigating (rollback buys time)
→ If fix doesn't work in staging, back to drawing board
→ If fix works but issues recur, deeper problem exists

---

### Step 8: Document and Prevent Recurrence

**What:** Create post-mortem and implement prevention measures.

**How:**

**Immediate documentation:**
```bash
# Update runbook
cat >> docs/runbooks/rollback-playbook.md <<'EOF'
## Recent Rollbacks

### 2025-10-26: v2.34 → v2.33
**Reason:** Database connection leak causing service outage
**Duration:** 8 minutes to rollback
**Impact:** 15% error rate, ~5000 failed requests
**Root cause:** Missing connection.close() in error handler
**Resolution:** Fixed in v2.35
**Lessons:**
- Code review missed resource cleanup
- Load testing didn't simulate error conditions
- Need connection pool monitoring
EOF

git add docs/runbooks/rollback-playbook.md
git commit -m "docs: Add rollback incident 2025-10-26"
```

**Post-mortem (scheduled within 48 hours):**
```markdown
# Post-Mortem: v2.34 Rollback

## Summary
On 2025-10-26, we rolled back deployment v2.34 due to a database
connection leak that caused 15% error rate. Rollback completed in
8 minutes and service was restored. Fixed in v2.35.

## Timeline
14:00 - v2.34 deployed
14:15 - Error alerts start firing
14:17 - Rollback decision made
14:20 - Rollback initiated
14:28 - Rollback complete, service restored
16:00 - Root cause identified
18:00 - Fix (v2.35) deployed successfully

## What Went Well
✅ Fast rollback decision (2 minutes)
✅ Rollback executed smoothly (8 minutes)
✅ Communication clear and frequent
✅ No data loss
✅ Fix developed and deployed same day

## What Could Be Improved
❌ Code review missed resource leak
❌ No connection pool monitoring
❌ Load tests don't simulate failures
❌ Staging deployment too short (only 10 min)

## Action Items
1. Add connection pool metrics to Grafana [P0, @alice, 2025-10-28]
2. Enhance code review checklist for resource cleanup [P1, @bob, 2025-11-01]
3. Add error injection to load tests [P1, @charlie, 2025-11-05]
4. Require 1-hour soak time in staging [P2, @diana, 2025-11-10]
5. Implement automatic rollback on error threshold [P2, @erik, 2025-11-15]

## Prevention Measures
- Add linter rule to detect unclosed connections
- Require integration tests for error paths
- Monitor connection pool utilization
- Alert on connection pool > 80% capacity
```

**Prevention implementation:**
```bash
# 1. Add monitoring
cat >> k8s/prometheus-rules.yml <<'EOF'
- alert: DatabaseConnectionPoolHigh
  expr: db_connection_pool_active / db_connection_pool_max > 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Connection pool usage high"
    description: "Connection pool is {{ $value | humanizePercentage }} full"
EOF

# 2. Add automated rollback
cat >> k8s/deployment.yml <<'EOF'
spec:
  progressDeadlineSeconds: 600
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  minReadySeconds: 300  # Pods must be healthy for 5 minutes
  
  # Automatic rollback on failure
  revisionHistoryLimit: 10
EOF

# 3. Enhance code review checklist
cat >> .github/pull_request_template.md <<'EOF'
## Resource Cleanup Checklist
- [ ] All database connections closed (including error paths)
- [ ] All file handles closed
- [ ] All network connections properly released
- [ ] No memory leaks in long-running processes
- [ ] Resource usage tested under load
EOF

# 4. Add pre-commit hook
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/bash
# Check for common resource leaks

if git diff --cached | grep -E "\.execute\(|\.query\(|open\(" | \
   grep -v "with " | grep -v "finally:"; then
  echo "⚠️  Potential resource leak detected"
  echo "Consider using 'with' statement or 'finally' block"
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

**Verification:**
- [ ] Post-mortem completed and shared
- [ ] All action items assigned with deadlines
- [ ] Monitoring enhancements deployed
- [ ] Process improvements implemented
- [ ] Team trained on new procedures
- [ ] Follow-up review scheduled

**If This Fails:**
→ Don't skip post-mortem even if busy
→ At minimum: Document what happened and one prevention measure
→ Schedule follow-up to complete action items

---

## Verification Checklist

After completing a rollback:

- [ ] Issue assessed and rollback decision made
- [ ] Target version identified and verified
- [ ] Current state backed up
- [ ] Rollback executed successfully
- [ ] Service recovery verified
- [ ] Stakeholders notified
- [ ] Failed version blocked from redeployment
- [ ] Root cause identified
- [ ] Fix developed and tested
- [ ] Documentation updated
- [ ] Post-mortem scheduled
- [ ] Prevention measures implemented

---

## Common Issues & Solutions

### Issue: Rollback Causes New Problems

**Symptoms:**
- Service still broken after rollback
- Different errors appearing
- Rollback hangs or fails
- Pods crash looping

**Solution:**
```bash
# Check if database migration is the issue
# Previous version may not be compatible with new schema

# Option 1: Rollback database migration
./scripts/db-rollback.sh

# Option 2: Deploy intermediate version
# If v2.34 broke and v2.33 incompatible with DB
# Deploy v2.33.1 (compatible with new schema but stable code)
kubectl set image deployment/myapp \
  myapp=myregistry.io/myapp:v2.33.1 \
  -n production

# Option 3: Fix forward
# If rollback not possible, quickly patch v2.34
git cherry-pick <fix-commit>
./scripts/deploy.sh production --emergency
```

**Prevention:**
- Always make database migrations backwards compatible
- Use feature flags for new features requiring schema changes
- Test rollback scenarios in staging

---

### Issue: Rollback Takes Too Long

**Symptoms:**
- Rollback exceeds 15 minutes
- Deployment stuck
- Old pods won't terminate

**Solution:**
```bash
# Force delete stuck pods
kubectl delete pods -n production -l app=myapp --force --grace-period=0

# Check resource limits
kubectl describe nodes | grep -A 5 "Allocated resources"

# Verify image pull
kubectl describe pod <pod-name> -n production | grep -A 10 Events
# Look for ImagePullBackOff

# If image pull slow, use cached image
kubectl set image deployment/myapp \
  myapp=myregistry.io/myapp:v2.33 \
  --image-pull-policy=IfNotPresent \
  -n production
```

**Prevention:**
- Keep recent images cached on nodes
- Pre-pull images during deployment
- Use faster container registry or CDN
- Reduce image size

---

### Issue: Unsure Which Version to Rollback To

**Symptoms:**
- Multiple recent deployments
- Unclear when issue started
- No obvious stable version

**Solution:**
```bash
# Analyze deployment history with metrics
for rev in $(kubectl rollout history deployment/myapp -n production | awk '{print $1}' | grep -v REVISION); do
  version=$(kubectl rollout history deployment/myapp -n production --revision=$rev | grep Image | awk '{print $2}')
  echo "Revision $rev: $version"
  
  # Query metrics for that version
  datadog query "avg:api.error_rate{version:$version}" \
    --from "7 days ago" \
    --to "now"
done

# Usually safe bet: Go back 2-3 versions
# If v2.34 is broken and v2.33 unsure, try v2.32
kubectl rollout undo deployment/myapp \
  -n production \
  --to-revision=$((current_revision - 2))
```

**Prevention:**
- Tag releases with tested/stable markers
- Keep deployment changelog up to date
- Require staging soak time before production

---

### Issue: Database Migration Prevents Rollback

**Symptoms:**
- Database schema changed
- Old code incompatible with new schema
- Rollback would break database operations

**Solution:**
```bash
# Option 1: Forward-compatible migrations
# Write migrations that work with both old and new code
# Example: Add column as nullable first, then make required later

# Option 2: Fix forward quickly
# Fastest path to recovery if true rollback not possible
git cherry-pick <critical-fix-commit>
./scripts/deploy.sh production --hotfix

# Option 3: Database point-in-time recovery
# Last resort: Restore database to before migration
pg_restore -d production \
  --clean \
  backup-before-migration.sql

# Then rollback application
kubectl rollout undo deployment/myapp -n production
```

**Prevention:**
- Always make migrations backwards compatible
- Deploy migrations separate from code changes
- Use multi-phase migrations (add, migrate data, remove old)
- Test rollback with migrated database in staging

---

## Best Practices

### DO:
✅ **Make rollback decision quickly** - Don't waste time trying to fix forward if uncertain  
✅ **Communicate early and clearly** - Status page update within 5 minutes  
✅ **Backup before rollback** - Always save current state  
✅ **Verify recovery thoroughly** - Don't assume rollback worked  
✅ **Block failed version** - Prevent accidental redeployment  
✅ **Document everything** - Timeline, decisions, actions  
✅ **Conduct post-mortem** - Learn and prevent recurrence  
✅ **Test rollback procedures** - Practice makes perfect

### DON'T:
❌ **Hesitate to rollback** - Fastest path to recovery  
❌ **Skip backups** - Always save current state first  
❌ **Assume rollback worked** - Verify metrics and functionality  
❌ **Forget to notify stakeholders** - Communication is critical  
❌ **Leave failed version deployable** - Block it immediately  
❌ **Skip root cause analysis** - Must prevent recurrence  
❌ **Deploy fixes without testing** - Staging first, always  
❌ **Ignore lessons learned** - Action items must be completed

---

## Related Workflows

**Prerequisites:**
- [CI/CD Pipeline Setup](./cicd_pipeline_setup.md) - Automated deployment capability
- [Kubernetes Deployment](./kubernetes_deployment.md) - Container orchestration
- [Application Monitoring](./application_monitoring_setup.md) - Detect issues quickly

**Next Steps:**
- [Incident Response Workflow](./incident_response_workflow.md) - Handle incidents properly
- [Emergency Hotfix](./emergency_hotfix.md) - Quick fixes for critical bugs
- Post-mortem and prevention measures

**Related:**
- [Backup and Disaster Recovery](./backup_disaster_recovery.md) - Database rollback procedures
- [Performance Tuning](./performance_tuning.md) - Optimize to prevent issues
- [Infrastructure as Code](./infrastructure_as_code_terraform.md) - Infrastructure rollbacks

---

## Tags
`devops` `deployment` `rollback` `recovery` `incident-response` `production` `kubernetes` `ci-cd` `reliability` `sre`
