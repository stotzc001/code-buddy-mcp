# Cross-Repository Changes

**ID:** maint-011  
**Category:** Development  
**Priority:** MEDIUM  
**Complexity:** Intermediate  
**Estimated Time:** 2-4 hours  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Systematic workflow for implementing and coordinating changes across multiple related repositories

**Why:** Modern applications often span multiple repositories (microservices, shared libraries, frontend/backend splits). Coordinated changes prevent integration failures, reduce deployment risks, and maintain system consistency.

**When to use:**
- Shared library/package updates affecting multiple consumers
- API contract changes between services
- Database schema migrations affecting multiple services
- Security patches needed across all repositories
- Configuration updates for multi-repo systems
- Breaking changes in shared dependencies

---

## Prerequisites

**Required:**
- [ ] List of all affected repositories
- [ ] Git access to all repositories
- [ ] Understanding of inter-repository dependencies
- [ ] CI/CD pipeline access
- [ ] Communication channel with other teams

**Check before starting:**
```bash
# List all repositories in organization
gh repo list myorg --limit 1000 --json name,url

# Check your access level to repositories
gh api repos/myorg/repo1 --jq '.permissions'

# Verify CI/CD pipeline access
# (GitHub Actions, GitLab CI, Jenkins, etc.)

# Map dependencies between repositories
# Create a dependency graph showing which repos depend on which
```

---

## Implementation Steps

### Step 1: Map Repository Dependencies

**What:** Create a comprehensive map of how repositories relate to each other

**How:**
Identify all affected repositories and understand their dependency relationships. This prevents making changes in the wrong order.

**Code/Commands:**
```bash
# Create dependency mapping script
cat > map_dependencies.py <<'EOF'
#!/usr/bin/env python3
"""Map dependencies between repositories"""

import json
import subprocess
from collections import defaultdict
from typing import Dict, List, Set

def get_org_repos(org: str) -> List[str]:
    """Get all repository names in organization"""
    result = subprocess.run(
        ["gh", "repo", "list", org, "--json", "name", "--limit", "1000"],
        capture_output=True, text=True
    )
    repos = json.loads(result.stdout)
    return [repo["name"] for repo in repos]

def analyze_repo_dependencies(org: str, repo: str) -> Dict[str, Set[str]]:
    """Analyze what this repo depends on"""
    dependencies = defaultdict(set)
    
    # Clone or check if already cloned
    repo_path = f"./{repo}"
    try:
        subprocess.run(
            ["gh", "repo", "clone", f"{org}/{repo}", repo_path],
            check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        print(f"Repository {repo} already cloned")
    
    # Check package.json (Node.js)
    try:
        with open(f"{repo_path}/package.json") as f:
            pkg = json.load(f)
            for dep_type in ["dependencies", "devDependencies"]:
                if dep_type in pkg:
                    for dep_name in pkg[dep_type].keys():
                        if dep_name.startswith(f"@{org}/"):
                            dependencies["npm"].add(dep_name)
    except FileNotFoundError:
        pass
    
    # Check requirements.txt (Python)
    try:
        with open(f"{repo_path}/requirements.txt") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    pkg_name = line.split("==")[0].split(">=")[0].strip()
                    if org.lower() in pkg_name.lower():
                        dependencies["pip"].add(pkg_name)
    except FileNotFoundError:
        pass
    
    # Check go.mod (Go)
    try:
        with open(f"{repo_path}/go.mod") as f:
            for line in f:
                if "github.com/" + org in line:
                    dependencies["go"].add(line.strip().split()[0])
    except FileNotFoundError:
        pass
    
    return dependencies

def create_dependency_graph(org: str, repos: List[str]):
    """Create full dependency graph"""
    graph = {}
    
    for repo in repos:
        print(f"Analyzing {repo}...")
        deps = analyze_repo_dependencies(org, repo)
        if deps:
            graph[repo] = dict(deps)
    
    # Save to file
    with open("dependency_graph.json", "w") as f:
        json.dump(graph, f, indent=2, default=list)
    
    print(f"\n✅ Dependency graph saved to dependency_graph.json")
    return graph

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python map_dependencies.py <org-name>")
        sys.exit(1)
    
    org = sys.argv[1]
    repos = get_org_repos(org)
    print(f"Found {len(repos)} repositories in {org}")
    
    graph = create_dependency_graph(org, repos)
    
    # Print summary
    print("\n=== Dependency Summary ===")
    for repo, deps in graph.items():
        dep_count = sum(len(v) for v in deps.values())
        if dep_count > 0:
            print(f"{repo}: {dep_count} internal dependencies")
EOF

chmod +x map_dependencies.py

# Run the analysis
python map_dependencies.py myorg

# Visualize dependencies (requires graphviz)
cat > visualize_deps.py <<'EOF'
import json
from graphviz import Digraph

with open("dependency_graph.json") as f:
    graph = json.load(f)

dot = Digraph(comment='Repository Dependencies')
dot.attr(rankdir='LR')

# Add nodes
repos = set(graph.keys())
for repo in repos:
    dot.node(repo, repo)

# Add edges
for repo, deps in graph.items():
    for dep_type, dep_list in deps.items():
        for dep in dep_list:
            # Extract repo name from package name
            dep_repo = dep.split('/')[-1].replace('@' + org + '/', '')
            if dep_repo in repos:
                dot.edge(repo, dep_repo, label=dep_type)

dot.render('dependencies', format='png', cleanup=True)
print("✅ Dependency graph saved to dependencies.png")
EOF

python visualize_deps.py
```

**Verification:**
- [ ] All repositories identified
- [ ] Dependency relationships mapped
- [ ] Dependency graph created (JSON or diagram)
- [ ] Circular dependencies identified

**If This Fails:**
→ Manually review package manifests (package.json, requirements.txt, etc.)
→ Check import statements in code
→ Review API calls between services
→ Ask team members about relationships

---

### Step 2: Plan Change Sequence

**What:** Determine the correct order to make changes across repositories

**How:**
Work from lowest-level dependencies upward. Change shared libraries first, then services that depend on them.

**Code/Commands:**
```bash
# Create change plan document
cat > CROSS_REPO_CHANGE_PLAN.md <<'EOF'
# Cross-Repository Change Plan

## Change Summary
**What:** Update authentication API from v1 to v2 across all services
**Why:** Security improvements, better token handling
**Impact:** 5 repositories, 3 teams
**Estimated Duration:** 2 weeks

## Affected Repositories
1. `auth-library` (shared authentication library)
2. `user-service` (depends on auth-library)
3. `api-gateway` (depends on auth-library)
4. `admin-dashboard` (depends on user-service)
5. `mobile-api` (depends on auth-library, user-service)

## Dependency Order
```
auth-library (base)
    ├── user-service
    ├── api-gateway
    └── mobile-api
         └── admin-dashboard
```

## Change Sequence

### Phase 1: Prepare Shared Library (Days 1-2)
**Repository:** `auth-library`
**Changes:**
- Add v2 authentication functions
- Maintain v1 for backward compatibility
- Add deprecation warnings to v1 functions
- Update tests
- Release version 2.0.0

**Verification:**
- [ ] All tests pass
- [ ] Both v1 and v2 work
- [ ] Published to package registry

### Phase 2: Update Core Services (Days 3-5)
**Repositories:** `user-service`, `api-gateway`
**Changes:**
- Update auth-library dependency to v2.0.0
- Migrate to v2 authentication calls
- Update tests
- Deploy to staging

**Verification:**
- [ ] Services work with v2 auth
- [ ] Integration tests pass
- [ ] Staging deployment successful

### Phase 3: Update Dependent Services (Days 6-8)
**Repositories:** `mobile-api`, `admin-dashboard`
**Changes:**
- Update dependencies
- Migrate authentication code
- Test end-to-end flows

**Verification:**
- [ ] All services using v2 auth
- [ ] End-to-end tests pass
- [ ] Production deployment successful

### Phase 4: Cleanup (Days 9-10)
**Repository:** `auth-library`
**Changes:**
- Remove v1 authentication code
- Release version 3.0.0 (v1 removed)
- Update all services to v3.0.0

## Rollback Plan
If issues discovered:
1. All services support rolling back to auth-library v1.x
2. Each service can independently rollback
3. Database changes are reversible
4. Feature flags control v2 usage

## Communication Plan
- Kick-off meeting: Day 1, 10 AM
- Daily standups: 9 AM
- Phase completion notifications
- Slack channel: #cross-repo-auth-migration

## Risk Mitigation
- Parallel v1/v2 support during migration
- Gradual rollout with feature flags
- Comprehensive testing in staging
- Monitor error rates closely

EOF

git add CROSS_REPO_CHANGE_PLAN.md
git commit -m "Add cross-repository change plan for auth v2 migration"
```

**Verification:**
- [ ] Change sequence determined
- [ ] Dependencies updated in correct order
- [ ] Rollback plan documented
- [ ] Timeline with milestones created
- [ ] Risk mitigation strategies in place

**If This Fails:**
→ Use topological sort on dependency graph
→ Identify any circular dependencies (must break them)
→ Plan for parallel changes where dependencies allow
→ Consider feature flags for gradual rollout

---

### Step 3: Create Coordinating Pull Requests

**What:** Open PRs in all affected repositories with references to each other

**How:**
Use a consistent naming scheme and cross-reference PRs so reviewers understand the full scope.

**Code/Commands:**
```bash
# Script to create coordinated PRs
cat > create_coordinated_prs.sh <<'EOF'
#!/bin/bash
set -euo pipefail

# Configuration
BRANCH_NAME="feat/auth-v2-migration"
PR_TITLE="[Cross-Repo] Migrate to Auth v2"
TRACKING_ISSUE="https://github.com/myorg/tracking/issues/123"

REPOS=(
  "auth-library"
  "user-service"
  "api-gateway"
  "mobile-api"
  "admin-dashboard"
)

echo "Creating coordinated pull requests..."

# Array to store PR URLs
declare -a PR_URLS

# Create PRs in each repository
for repo in "${REPOS[@]}"; do
  echo "Processing $repo..."
  
  cd "$repo" || exit
  
  # Create branch
  git checkout -b "$BRANCH_NAME"
  
  # Make changes (this would be your actual changes)
  # For now, just update a marker file
  echo "Auth v2 migration - $(date)" >> .migration-marker
  git add .migration-marker
  git commit -m "chore: Auth v2 migration marker"
  
  # Push branch
  git push -u origin "$BRANCH_NAME"
  
  # Create PR with template
  PR_BODY="## Cross-Repository Change

This PR is part of a coordinated change across multiple repositories.

**Tracking Issue:** $TRACKING_ISSUE

**Related PRs:**
<!-- Will be updated with other PR links -->

## Changes
- Migrate from Auth v1 to v2
- Update authentication middleware
- Update tests

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Deployed to staging

## Dependencies
This PR depends on:
- [ ] auth-library v2.0.0 released

## Deployment Order
See [deployment plan]($TRACKING_ISSUE) for coordinated deployment sequence.

**⚠️ Important:** Do not merge until all related PRs are approved and ready.
"
  
  # Create PR
  PR_URL=$(gh pr create \
    --title "$PR_TITLE" \
    --body "$PR_BODY" \
    --label "cross-repo" \
    --label "auth-v2-migration" \
    2>&1 | grep "https://" || echo "")
  
  if [ -n "$PR_URL" ]; then
    echo "✅ Created PR: $PR_URL"
    PR_URLS+=("- $repo: $PR_URL")
  else
    echo "❌ Failed to create PR in $repo"
  fi
  
  cd ..
done

# Update all PRs with cross-references
echo ""
echo "Updating PRs with cross-references..."
PR_LIST=$(printf '%s\n' "${PR_URLS[@]}")

for repo in "${REPOS[@]}"; do
  cd "$repo" || continue
  
  # Update PR description with all PR links
  gh pr edit --add-label "ready-for-review" \
    --body "## Cross-Repository Change

This PR is part of a coordinated change across multiple repositories.

**Tracking Issue:** $TRACKING_ISSUE

**Related PRs:**
$PR_LIST

## Changes
[...]
"
  
  cd ..
done

echo ""
echo "✅ All PRs created and cross-referenced!"
echo "📋 PR List:"
printf '%s\n' "${PR_URLS[@]}"
EOF

chmod +x create_coordinated_prs.sh
./create_coordinated_prs.sh
```

**Verification:**
- [ ] PRs created in all repositories
- [ ] All PRs cross-reference each other
- [ ] Consistent labeling applied
- [ ] Clear description of changes in each PR
- [ ] Dependencies documented in each PR

**If This Fails:**
→ Create PRs manually with consistent template
→ Use GitHub project board to track related PRs
→ Document PR links in tracking issue
→ Set up PR notifications for team

---

### Step 4: Implement Changes Incrementally

**What:** Make changes in the planned sequence, one repository at a time

**How:**
Start with the base dependency, test thoroughly, then move up the dependency chain.

**Code/Commands:**
```bash
# Phase 1: Update base library (auth-library)
cd auth-library

# Implement v2 alongside v1
cat > src/auth_v2.py <<'EOF'
"""Authentication v2 - Improved security and token handling"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthV2:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def create_token(
        self,
        user_id: str,
        scopes: list[str],
        expires_in: int = 3600
    ) -> str:
        """Create JWT token with improved claims"""
        payload = {
            "sub": user_id,
            "scopes": scopes,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "version": "v2"
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            if payload.get("version") != "v2":
                return None
            return payload
        except jwt.InvalidTokenError:
            return None

# Add deprecation warning to v1
import warnings

def authenticate_v1(*args, **kwargs):
    warnings.warn(
        "auth_v1.authenticate is deprecated. Use AuthV2 instead. "
        "v1 will be removed in version 3.0.0",
        DeprecationWarning,
        stacklevel=2
    )
    # Original v1 implementation...
    pass
EOF

# Update tests
cat > tests/test_auth_v2.py <<'EOF'
import pytest
from auth_v2 import AuthV2

def test_create_and_verify_token():
    auth = AuthV2(secret_key="test-secret")
    token = auth.create_token("user123", ["read", "write"])
    
    payload = auth.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert "read" in payload["scopes"]
    assert payload["version"] == "v2"

def test_invalid_token():
    auth = AuthV2(secret_key="test-secret")
    assert auth.verify_token("invalid") is None

def test_expired_token():
    auth = AuthV2(secret_key="test-secret")
    token = auth.create_token("user123", ["read"], expires_in=-1)
    assert auth.verify_token(token) is None
EOF

# Run tests
pytest tests/

# Update version and publish
echo "2.0.0" > VERSION
poetry version 2.0.0
poetry publish --build

# Phase 2: Update consuming service
cd ../user-service

# Update dependency
poetry add auth-library@^2.0.0

# Migrate code
cat > src/middleware/auth.py <<'EOF'
from auth_library.auth_v2 import AuthV2
from fastapi import Request, HTTPException

auth = AuthV2(secret_key=settings.AUTH_SECRET)

async def auth_middleware(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    request.state.user_id = payload["sub"]
    request.state.scopes = payload["scopes"]
EOF

# Run integration tests
pytest tests/integration/

# Deploy to staging
./deploy.sh staging

# Monitor for issues
./monitor-errors.sh

echo "✅ Phase complete. Moving to next repository..."
```

**Verification:**
- [ ] Each phase completed successfully
- [ ] Tests pass at each step
- [ ] Staging deployment successful
- [ ] No regressions detected
- [ ] Monitoring shows healthy metrics

**If This Fails:**
→ Rollback to previous version
→ Fix issues before proceeding
→ Don't move to next phase until current phase stable
→ Use feature flags to limit exposure

---

### Step 5: Coordinate Testing Across Repositories

**What:** Ensure all repositories work together with the changes

**How:**
Run integration tests, end-to-end tests, and manual testing across the full system.

**Code/Commands:**
```bash
# Create end-to-end test suite
cat > e2e-tests/test_cross_repo_integration.py <<'EOF'
"""
End-to-end tests for cross-repository changes
Tests the full flow across all updated services
"""

import pytest
import requests

BASE_URL_GATEWAY = "https://staging-api.example.com"
BASE_URL_USER = "https://staging-user-service.example.com"

class TestAuthV2Integration:
    def test_full_authentication_flow(self):
        """Test authentication across all services"""
        # Step 1: Get token from auth service (via gateway)
        response = requests.post(
            f"{BASE_URL_GATEWAY}/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        token = response.json()["token"]
        
        # Verify token is v2 format
        import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["version"] == "v2"
        assert "scopes" in payload
        
        # Step 2: Use token to access user service
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL_USER}/users/me",
            headers=headers
        )
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == "testuser"
        
        # Step 3: Verify scopes are enforced
        response = requests.post(
            f"{BASE_URL_USER}/users/delete",
            headers=headers
        )
        # Should fail if user doesn't have delete scope
        assert response.status_code in [403, 401]
    
    def test_backward_compatibility(self):
        """Verify v1 tokens still work during migration"""
        # Get old v1 token (if still supported)
        response = requests.post(
            f"{BASE_URL_GATEWAY}/auth/login?version=v1",
            json={"username": "testuser", "password": "testpass"}
        )
        
        if response.status_code == 200:
            token = response.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # v1 token should still work
            response = requests.get(
                f"{BASE_URL_USER}/users/me",
                headers=headers
            )
            assert response.status_code == 200
    
    def test_service_dependencies(self):
        """Test that all services are using updated versions"""
        # Check each service's /health endpoint for version info
        services = [
            BASE_URL_GATEWAY,
            BASE_URL_USER,
            "https://staging-mobile-api.example.com",
            "https://staging-admin.example.com"
        ]
        
        for service_url in services:
            response = requests.get(f"{service_url}/health")
            assert response.status_code == 200
            
            health = response.json()
            # Verify auth library version is 2.x
            assert health["dependencies"]["auth_library"].startswith("2.")

EOF

# Run e2e tests
pytest e2e-tests/ -v --tb=short

# Create smoke test script for quick validation
cat > smoke-test.sh <<'EOF'
#!/bin/bash
# Quick smoke tests after deployment

echo "Running smoke tests..."

# Test each service health endpoint
services=(
  "https://staging-api.example.com"
  "https://staging-user-service.example.com"
  "https://staging-mobile-api.example.com"
)

for service in "${services[@]}"; do
  echo "Testing $service..."
  status=$(curl -s -o /dev/null -w "%{http_code}" "$service/health")
  if [ "$status" -eq 200 ]; then
    echo "✅ $service is healthy"
  else
    echo "❌ $service returned $status"
    exit 1
  fi
done

# Test authentication flow
echo "Testing auth flow..."
token=$(curl -s -X POST https://staging-api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}' \
  | jq -r '.token')

if [ -n "$token" ]; then
  echo "✅ Authentication successful"
else
  echo "❌ Authentication failed"
  exit 1
fi

# Test token usage
response=$(curl -s -w "%{http_code}" \
  -H "Authorization: Bearer $token" \
  https://staging-user-service.example.com/users/me)

if [[ "$response" == *"200" ]]; then
  echo "✅ Token validation successful"
else
  echo "❌ Token validation failed"
  exit 1
fi

echo "✅ All smoke tests passed!"
EOF

chmod +x smoke-test.sh
./smoke-test.sh
```

**Verification:**
- [ ] End-to-end tests pass
- [ ] Integration tests pass
- [ ] Smoke tests successful
- [ ] Manual testing completed
- [ ] Performance acceptable

**If This Fails:**
→ Review logs from all services
→ Check for version mismatches
→ Verify network connectivity between services
→ Test services individually first, then together

---

### Step 6: Coordinate Deployments

**What:** Deploy changes in the correct sequence to avoid breaking dependencies

**How:**
Use deployment automation with dependency checks and rollback capability.

**Code/Commands:**
```bash
# Create coordinated deployment script
cat > deploy-coordinated.sh <<'EOF'
#!/bin/bash
set -euo pipefail

# Deployment configuration
REPOS=(
  "auth-library:2.0.0"  # Deploy first (base dependency)
  "user-service:1.5.0"   # Then services that depend on it
  "api-gateway:1.3.0"
  "mobile-api:2.1.0"
  "admin-dashboard:1.2.0"  # Finally, dependent services
)

ENVIRONMENT="${1:-staging}"
DRY_RUN="${2:-false}"

echo "🚀 Coordinated deployment to $ENVIRONMENT"
echo "Dry run: $DRY_RUN"
echo ""

# Function to deploy a service
deploy_service() {
  local repo_version=$1
  local repo=$(echo "$repo_version" | cut -d: -f1)
  local version=$(echo "$repo_version" | cut -d: -f2)
  
  echo "📦 Deploying $repo v$version..."
  
  if [ "$DRY_RUN" = "true" ]; then
    echo "   [DRY RUN] Would deploy $repo v$version to $ENVIRONMENT"
    return 0
  fi
  
  cd "$repo"
  
  # Check health before deployment
  if [ "$ENVIRONMENT" = "production" ]; then
    current_health=$(curl -s "https://api.example.com/$repo/health" | jq -r '.status')
    if [ "$current_health" != "ok" ]; then
      echo "❌ Current deployment unhealthy. Aborting."
      exit 1
    fi
  fi
  
  # Deploy
  ./deploy.sh "$ENVIRONMENT" "$version"
  
  # Wait for deployment to complete
  sleep 30
  
  # Verify deployment
  new_health=$(curl -s "https://$ENVIRONMENT-api.example.com/$repo/health")
  deployed_version=$(echo "$new_health" | jq -r '.version')
  
  if [ "$deployed_version" != "$version" ]; then
    echo "❌ Deployment verification failed. Expected $version, got $deployed_version"
    echo "🔄 Rolling back..."
    ./rollback.sh "$ENVIRONMENT"
    exit 1
  fi
  
  echo "✅ Successfully deployed $repo v$version"
  cd ..
  
  # Wait between deployments
  echo "⏸️  Waiting 60s before next deployment..."
  sleep 60
}

# Deploy each repository in sequence
for repo_version in "${REPOS[@]}"; do
  deploy_service "$repo_version"
  
  # Run smoke tests after each deployment
  if [ "$DRY_RUN" = "false" ]; then
    echo "🧪 Running smoke tests..."
    ./smoke-test.sh
  fi
done

echo ""
echo "✅ All services deployed successfully!"
echo ""
echo "📊 Deployment Summary:"
for repo_version in "${REPOS[@]}"; do
  echo "   ✅ $repo_version"
done

# Final health check
echo ""
echo "🏥 Final health check..."
./smoke-test.sh

echo "🎉 Coordinated deployment complete!"
EOF

chmod +x deploy-coordinated.sh

# Test with dry run first
./deploy-coordinated.sh staging true

# Deploy to staging
./deploy-coordinated.sh staging false

# After validation, deploy to production
./deploy-coordinated.sh production false
```

**Verification:**
- [ ] All services deployed in correct order
- [ ] Health checks passing after each deployment
- [ ] Smoke tests successful
- [ ] No errors in logs
- [ ] Metrics show healthy system

**If This Fails:**
→ Rollback to previous versions immediately
→ Investigate logs for root cause
→ Fix issues before retrying
→ Consider partial rollout with feature flags

---

### Step 7: Monitor Post-Deployment

**What:** Closely watch all affected services for issues after deployment

**How:**
Set up alerts, dashboard monitoring, and log analysis to catch problems quickly.

**Code/Commands:**
```bash
# Set up monitoring dashboard
cat > setup-monitoring.sh <<'EOF'
#!/bin/bash

# Create monitoring queries for common issues
cat > monitor-queries.txt <<'QUERIES'
# Error rate monitoring
service:user-service AND level:error AND "auth" | count by service

# Response time monitoring
service:api-gateway AND http.status_code:200 | avg(duration) by endpoint

# Version tracking
service:* AND "auth_library" | stats count by auth_library_version

# Authentication failures
service:* AND "authentication failed" | count by service, reason

# Deprecated API usage (should decrease over time)
service:* AND "deprecation warning" AND "auth_v1" | count by service
QUERIES

# Set up alerts
cat > alerts.yaml <<'YAML'
alerts:
  - name: "High auth error rate"
    condition: "error_rate > 5%"
    services: ["user-service", "api-gateway"]
    notification: "pagerduty"
    
  - name: "Deprecated auth usage"
    condition: "auth_v1_requests > 100"
    services: ["*"]
    notification: "slack"
    message: "Services still using auth v1: {services}"
    
  - name: "Response time degradation"
    condition: "p95_response_time > 500ms"
    services: ["api-gateway"]
    notification: "email"
YAML

# Create monitoring script
cat > monitor-deployment.sh <<'MONITOR'
#!/bin/bash
# Monitor deployment health for 24 hours

echo "👁️  Monitoring deployment health..."
echo "Press Ctrl+C to stop"

while true; do
  echo "=== $(date) ==="
  
  # Check error rates
  error_rate=$(curl -s "https://monitoring.example.com/api/error-rate?service=all&window=5m" \
    | jq -r '.error_rate')
  echo "Error rate: $error_rate%"
  
  # Check auth v1 usage (should decrease)
  v1_usage=$(curl -s "https://monitoring.example.com/api/auth-version-stats" \
    | jq -r '.v1_percentage')
  echo "Auth v1 usage: $v1_usage%"
  
  # Check response times
  p95=$(curl -s "https://monitoring.example.com/api/latency?percentile=95" \
    | jq -r '.value')
  echo "P95 latency: ${p95}ms"
  
  # Alert if issues detected
  if (( $(echo "$error_rate > 5" | bc -l) )); then
    echo "⚠️  HIGH ERROR RATE DETECTED!"
    # Send alert
  fi
  
  if (( $(echo "$p95 > 500" | bc -l) )); then
    echo "⚠️  HIGH LATENCY DETECTED!"
    # Send alert
  fi
  
  echo ""
  sleep 300  # Check every 5 minutes
done
MONITOR

chmod +x monitor-deployment.sh
EOF

./setup-monitoring.sh

# Start monitoring
./monitor-deployment.sh &
MONITOR_PID=$!

# Generate deployment report after 24 hours
sleep 86400
kill $MONITOR_PID

cat > deployment-report.md <<'EOF'
# Cross-Repository Deployment Report

## Deployment Date
2025-10-25

## Services Updated
- auth-library: v1.5.0 → v2.0.0
- user-service: v1.4.0 → v1.5.0
- api-gateway: v1.2.0 → v1.3.0
- mobile-api: v2.0.0 → v2.1.0
- admin-dashboard: v1.1.0 → v1.2.0

## Metrics (24h post-deployment)
- Error rate: 0.3% (normal: 0.2%)
- P95 latency: 245ms (baseline: 230ms)
- Auth v1 usage: 15% (down from 100%)
- Deployments successful: 5/5

## Issues Encountered
None

## Next Steps
- Continue monitoring for 1 week
- Reach out to services still using v1 auth
- Plan v1 deprecation for 30 days from now
EOF
```

**Verification:**
- [ ] Monitoring dashboards active
- [ ] Alerts configured
- [ ] No critical issues detected
- [ ] Error rates within normal bounds
- [ ] Performance metrics acceptable
- [ ] Deprecated API usage decreasing

**If This Fails:**
→ Rollback if critical issues detected
→ Investigate root cause thoroughly
→ Fix forward if possible
→ Update runbooks based on learnings

---

### Step 8: Document and Communicate Results

**What:** Share outcomes, lessons learned, and update documentation

**How:**
Create comprehensive documentation of the change process and results for future reference.

**Code/Commands:**
```bash
# Create final documentation
cat > docs/cross-repo-changes/auth-v2-migration.md <<'EOF'
# Auth v2 Migration - Post-Mortem

## Summary
Successfully migrated 5 repositories from Auth v1 to v2 over 10 days with zero downtime.

## Timeline
- Day 1-2: Updated auth-library with v2 implementation
- Day 3-5: Migrated user-service and api-gateway
- Day 6-8: Migrated mobile-api and admin-dashboard
- Day 9-10: Cleanup and monitoring

## Repositories Affected
1. auth-library (v1.5.0 → v2.0.0)
2. user-service (v1.4.0 → v1.5.0)
3. api-gateway (v1.2.0 → v1.3.0)
4. mobile-api (v2.0.0 → v2.1.0)
5. admin-dashboard (v1.1.0 → v1.2.0)

## What Went Well
✅ Dependency mapping identified all affected repositories
✅ Phased approach prevented breaking changes
✅ Backward compatibility maintained during transition
✅ Monitoring caught issues early
✅ Team coordination was excellent

## What Could Be Improved
⚠️ Initial dependency mapping took longer than expected
⚠️ Some integration tests were incomplete
⚠️ Communication about deployment timeline could be clearer

## Lessons Learned
1. **Map dependencies first** - Saved us from multiple ordering issues
2. **Parallel v1/v2 support is crucial** - Enabled gradual migration
3. **Automated testing critical** - Caught integration issues early
4. **Monitor closely** - First 24 hours most critical

## Metrics
- Total repositories: 5
- Total PRs: 5
- Lines of code changed: ~2,500
- Tests added/updated: 45
- Deployment time: 10 days
- Downtime: 0 minutes
- Issues encountered: 2 (minor, quickly resolved)

## Future Recommendations
1. Create automated dependency mapping tool
2. Standardize cross-repo change templates
3. Improve integration test coverage
4. Create deployment automation for coordinated changes

## Related Documentation
- [Dependency Map](./dependency-graph.json)
- [Change Plan](./CROSS_REPO_CHANGE_PLAN.md)
- [Deployment Runbook](./deploy-coordinated.sh)
EOF

# Send summary to team
gh issue comment 123 --body "✅ Auth v2 migration complete! See [post-mortem](docs/cross-repo-changes/auth-v2-migration.md) for details."

# Update team wiki/documentation
cat >> team-wiki/development-practices.md <<'EOF'

## Cross-Repository Changes

When making changes that affect multiple repositories:
1. Map dependencies first (use scripts/map_dependencies.py)
2. Create change plan with sequence
3. Open coordinated PRs with cross-references
4. Deploy in dependency order
5. Monitor closely for 24 hours
6. Document lessons learned

See [Auth v2 Migration](../docs/cross-repo-changes/auth-v2-migration.md) as example.
EOF

git add docs/ team-wiki/
git commit -m "docs: Add auth v2 migration post-mortem"
git push
```

**Verification:**
- [ ] Documentation complete
- [ ] Team informed of results
- [ ] Lessons learned captured
- [ ] Runbooks updated
- [ ] Future improvements identified

**If This Fails:**
→ Schedule retrospective meeting
→ Gather feedback from all teams involved
→ Document what went wrong for next time

---

## Verification Checklist

After completing this workflow:

- [ ] All affected repositories identified and mapped
- [ ] Changes deployed in correct dependency order
- [ ] All services working together correctly
- [ ] Integration and E2E tests passing
- [ ] No increase in error rates or latency
- [ ] Monitoring shows healthy system
- [ ] Documentation updated
- [ ] Team informed and lessons learned captured
- [ ] Rollback plan tested (if possible)
- [ ] Deprecation warnings removed from old code

---

## Common Issues & Solutions

### Issue: Dependency Cycle Detected

**Symptoms:**
- Cannot determine correct deployment order
- Service A depends on B, B depends on C, C depends on A

**Solution:**
```bash
# Identify the cycle
cat > find-cycles.py <<'EOF'
import json
from collections import defaultdict, deque

def find_cycles(graph):
    def visit(node, path, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if visit(neighbor, path, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                # Cycle found
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                print(f"Cycle detected: {' -> '.join(cycle)}")
                return True
        
        path.pop()
        rec_stack.remove(node)
        return False
    
    visited = set()
    for node in graph:
        if node not in visited:
            if visit(node, [], visited, set()):
                return True
    return False

# Load dependency graph
with open('dependency_graph.json') as f:
    graph = json.load(f)

find_cycles(graph)
EOF

python find-cycles.py

# Break the cycle by:
# 1. Introducing an interface/abstraction layer
# 2. Using events/message queue instead of direct calls
# 3. Refactoring to remove circular dependency
```

**Prevention:**
- Design services with clear dependency hierarchy
- Use event-driven architecture to decouple
- Regular dependency audits

---

### Issue: Deployment Fails Midway Through Sequence

**Symptoms:**
- Some services updated, others not
- System in inconsistent state
- Integration failures

**Solution:**
```bash
# Immediate rollback script
cat > emergency-rollback.sh <<'EOF'
#!/bin/bash
# Rollback all services to previous versions

REPOS=(
  "auth-library:1.5.0"
  "user-service:1.4.0"
  "api-gateway:1.2.0"
  "mobile-api:2.0.0"
  "admin-dashboard:1.1.0"
)

for repo_version in "${REPOS[@]}"; do
  repo=$(echo "$repo_version" | cut -d: -f1)
  version=$(echo "$repo_version" | cut -d: -f2)
  
  echo "Rolling back $repo to v$version..."
  cd "$repo"
  ./rollback.sh production "$version"
  cd ..
done
EOF

chmod +x emergency-rollback.sh
./emergency-rollback.sh
```

**Prevention:**
- Test deployment script in staging first
- Use feature flags for gradual rollout
- Implement automated rollback on failure detection
- Keep old versions running in parallel initially

---

## Best Practices

### DO:
✅ **Map dependencies first** - Know what depends on what before starting  
✅ **Deploy base dependencies first** - Bottom-up deployment order  
✅ **Maintain backward compatibility** - Support old and new during transition  
✅ **Automate coordination** - Scripts for creating PRs, deploying, testing  
✅ **Cross-reference everything** - Link related PRs, issues, docs  
✅ **Test integration thoroughly** - E2E tests across all services  
✅ **Monitor closely** - Watch for issues after deployment  
✅ **Document the process** - Help future teams avoid same mistakes  
✅ **Communicate proactively** - Keep all teams informed  
✅ **Have rollback plan** - Know how to undo changes quickly

### DON'T:
❌ **Deploy without dependency map** - Will break things  
❌ **Deploy all at once** - Too risky, hard to debug  
❌ **Skip integration testing** - Services may work alone but fail together  
❌ **Make breaking changes without warning** - Coordinate with consumers  
❌ **Deploy during peak hours** - Minimize risk window  
❌ **Forget to update documentation** - Future you will thank you  
❌ **Leave services in inconsistent state** - All or nothing  
❌ **Skip the post-mortem** - Miss opportunity to improve  
❌ **Ignore monitoring alerts** - Catch issues early  
❌ **Proceed if tests fail** - Fix issues before continuing

---

## Related Workflows

**Prerequisites:**
- [Dependency Management](./dependency_update_strategy.md) - Understanding dependencies
- [Version Release Tagging](./version_release_tagging.md) - Semantic versioning

**Next Steps:**
- [Breaking API Changes](./breaking_api_changes.md) - Handle breaking changes
- [Rollback Procedure](./rollback_procedure.md) - When things go wrong
- [Emergency Hotfix](../devops/emergency_hotfix.md) - Quick fixes across repos

**Alternatives:**
- [Monorepo Strategy](../architecture/monorepo_strategy.md) - Avoid multi-repo complexity
- [Feature Flags](../devops/feature_flags.md) - Gradual rollouts

---

## Tags
`multi-repo` `microservices` `coordination` `deployment` `integration` `dependencies` `cross-cutting-changes` `monorepo-alternative` `deployment-orchestration`
