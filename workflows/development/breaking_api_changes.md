# Managing Breaking API Changes

**ID:** dev-022  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 2-4 hours  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Systematic workflow for planning, implementing, and rolling out breaking changes to APIs while minimizing disruption to consumers

**Why:** Breaking changes are inevitable as products evolve, but poor management leads to broken client applications, frustrated users, and costly emergency fixes. Proper handling maintains trust and enables innovation.

**When to use:**
- Removing deprecated endpoints or fields
- Changing response/request schemas
- Modifying authentication mechanisms
- Updating error handling behavior
- Renaming resources or endpoints
- Changing HTTP methods or status codes

---

## Prerequisites

**Required:**
- [ ] API versioning strategy established
- [ ] List of API consumers and their versions
- [ ] Deprecation policy documented
- [ ] Communication channels with API users
- [ ] Staging/testing environment

**Check before starting:**
```bash
# Check current API version
curl https://api.example.com/version

# Review API analytics for endpoint usage
# Check which endpoints are being used and by whom

# Verify you have access to:
# - API documentation system
# - User communication tools
# - Deployment pipeline
# - Monitoring/analytics dashboards
```

---

## Implementation Steps

### Step 1: Analyze Breaking Change Impact

**What:** Understand exactly what's changing, why, and who will be affected

**How:**
Document the current behavior, desired new behavior, and the gap between them. Identify all consumers and their integration points.

**Code/Commands:**
```bash
# Analyze API usage patterns
# Using access logs
grep "/api/v1/users" /var/log/nginx/access.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# Check endpoint usage metrics (example with application logs)
grep "GET /api/v1/users" application.log | wc -l

# Identify breaking changes in OpenAPI spec
# Use tools to detect schema changes
npx openapi-diff oldspec.yaml newspec.yaml --format markdown > breaking-changes.md

# Create impact analysis document
cat > BREAKING_CHANGE_ANALYSIS.md <<'EOF'
# Breaking Change Impact Analysis

## Change Summary
**Endpoint:** GET /api/v1/users
**Change Type:** Response schema modification
**Date Planned:** 2025-12-01

## Current Behavior
```json
{
  "users": [
    {"id": 1, "name": "John", "email": "john@example.com"}
  ]
}
```

## New Behavior
```json
{
  "data": {
    "users": [
      {"id": 1, "fullName": "John Doe", "contactEmail": "john@example.com"}
    ]
  },
  "meta": {
    "total": 1,
    "page": 1
  }
}
```

## Breaking Changes
1. Root key changed from `users` to `data.users`
2. Field `name` renamed to `fullName`
3. Field `email` renamed to `contactEmail`
4. Added pagination metadata

## Affected Consumers
- Mobile App v2.3-v2.7 (500 active users)
- Web Dashboard v1.0+ (200 active sessions/day)
- Partner API Integration (3 partners)
- Internal Admin Tool (50 employees)

## Migration Effort
- Mobile: High (requires app update)
- Web: Medium (JavaScript changes)
- Partners: High (requires coordination)
- Internal: Low (fast deployment cycle)
EOF
```

**Verification:**
- [ ] All breaking changes documented
- [ ] Consumer list complete
- [ ] Impact severity assessed
- [ ] Migration effort estimated

**If This Fails:**
→ Interview engineering teams about their integrations
→ Check API analytics/monitoring dashboards
→ Review support tickets for integration issues
→ Survey known API consumers

---

### Step 2: Design Migration Strategy

**What:** Create a plan that allows old and new versions to coexist safely

**How:**
Choose the right versioning approach (URL path, header, or query parameter) and design backward compatibility layers.

**Code/Commands:**
```python
# Option 1: URL Path Versioning (Recommended)
# /api/v1/users -> /api/v2/users
# Both versions run simultaneously

# FastAPI example
from fastapi import FastAPI, APIRouter

app = FastAPI()

# V1 router (legacy)
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/users")
def get_users_v1():
    """Legacy endpoint - deprecated"""
    return {
        "users": [
            {"id": 1, "name": "John", "email": "john@example.com"}
        ]
    }

# V2 router (new)
v2_router = APIRouter(prefix="/api/v2")

@v2_router.get("/users")
def get_users_v2():
    """New endpoint with improved schema"""
    return {
        "data": {
            "users": [
                {
                    "id": 1,
                    "fullName": "John Doe",
                    "contactEmail": "john@example.com"
                }
            ]
        },
        "meta": {"total": 1, "page": 1}
    }

app.include_router(v1_router)
app.include_router(v2_router)

# Option 2: Header-based versioning
from fastapi import Header

@app.get("/api/users")
def get_users(api_version: str = Header(default="1")):
    if api_version == "2":
        return get_users_v2()
    return get_users_v1()

# Option 3: Accept header negotiation
@app.get("/api/users")
def get_users(accept: str = Header(default="application/json")):
    if "application/vnd.myapi.v2+json" in accept:
        return get_users_v2()
    return get_users_v1()
```

**Verification:**
- [ ] Versioning strategy chosen
- [ ] Both versions implemented
- [ ] Version selection working correctly
- [ ] Tests cover both versions

**If This Fails:**
→ Use URL path versioning as simplest option
→ Review major API providers (Stripe, GitHub) for inspiration
→ Ensure infrastructure supports multiple versions
→ Document version routing logic clearly

---

### Step 3: Implement Deprecation Warnings

**What:** Add visible warnings to old API version to inform consumers

**How:**
Include deprecation headers, response metadata, and logging to track who's still using old versions.

**Code/Commands:**
```python
# Add deprecation headers to V1 responses
from datetime import datetime, timedelta
from fastapi import Response

@v1_router.get("/users")
def get_users_v1(response: Response):
    """Legacy endpoint - deprecated"""
    
    # Add deprecation headers
    sunset_date = (datetime.now() + timedelta(days=90)).isoformat()
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = sunset_date
    response.headers["Link"] = '</api/v2/users>; rel="successor-version"'
    response.headers["X-API-Warn"] = (
        "This API version is deprecated and will be removed on "
        f"{sunset_date}. Please migrate to /api/v2/users"
    )
    
    # Log usage for analytics
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(
        f"Deprecated API v1 accessed: /users "
        f"(sunset: {sunset_date})"
    )
    
    return {
        "users": [...],
        "_deprecated": {
            "message": "This endpoint is deprecated",
            "sunset_date": sunset_date,
            "new_endpoint": "/api/v2/users",
            "migration_guide": "https://docs.example.com/migration-v1-to-v2"
        }
    }

# Create middleware to track deprecated usage
from collections import defaultdict

class DeprecationTracker:
    def __init__(self):
        self.usage = defaultdict(int)
    
    async def track(self, request):
        if "/api/v1/" in str(request.url):
            # Extract client identifier (API key, IP, etc.)
            client_id = request.headers.get("X-API-Key", request.client.host)
            endpoint = str(request.url.path)
            self.usage[f"{client_id}:{endpoint}"] += 1
    
    def get_report(self):
        return dict(self.usage)

tracker = DeprecationTracker()

# Use in endpoint
@v1_router.get("/users")
async def get_users_v1(request: Request, response: Response):
    await tracker.track(request)
    # ... rest of implementation
```

**Verification:**
- [ ] Deprecation headers present in responses
- [ ] Warnings logged for monitoring
- [ ] Migration guide URL working
- [ ] Tracking system capturing usage data

**If This Fails:**
→ Check response headers with curl: `curl -I https://api.example.com/v1/users`
→ Verify logging configuration
→ Test with API client (Postman, Insomnia)
→ Ensure deprecation visible in API documentation

---

### Step 4: Create Comprehensive Migration Guide

**What:** Document exactly how consumers should migrate from v1 to v2

**How:**
Provide clear before/after examples, code samples, and common pitfalls.

**Code/Commands:**
```markdown
# API v1 to v2 Migration Guide

## Overview
API v2 introduces improved data structures and better error handling.
All v1 endpoints will be sunset on 2025-12-01.

## Breaking Changes

### 1. Response Structure Changed
**v1:**
```json
{
  "users": [...]
}
```

**v2:**
```json
{
  "data": {
    "users": [...]
  },
  "meta": {}
}
```

**Migration:**
```javascript
// Old code
const users = response.users;

// New code
const users = response.data.users;
```

### 2. Field Renames
| v1 Field | v2 Field | Type | Notes |
|----------|----------|------|-------|
| `name` | `fullName` | string | Full name instead of first name only |
| `email` | `contactEmail` | string | More descriptive |
| `created` | `createdAt` | ISO8601 | Standardized timestamp format |

**Migration:**
```python
# Old code
user_name = user["name"]
user_email = user["email"]

# New code  
user_name = user["fullName"]
user_email = user["contactEmail"]
```

### 3. Pagination Added
All list endpoints now return paginated results.

**v1:**
```bash
GET /api/v1/users
# Returns all users
```

**v2:**
```bash
GET /api/v2/users?page=1&limit=20
# Returns paginated results with meta information
```

**Migration:**
```javascript
// Old code - single request
const response = await fetch('/api/v1/users');
const users = await response.json().users;

// New code - handle pagination
async function getAllUsers() {
  let allUsers = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const response = await fetch(`/api/v2/users?page=${page}&limit=100`);
    const data = await response.json();
    allUsers = allUsers.concat(data.data.users);
    hasMore = data.meta.page < data.meta.totalPages;
    page++;
  }
  
  return allUsers;
}
```

## Quick Start

### Update Base URL
```javascript
// Before
const API_BASE = 'https://api.example.com/v1';

// After
const API_BASE = 'https://api.example.com/v2';
```

### Adapter Pattern (Temporary)
Use this adapter during migration to minimize code changes:

```javascript
class APIv2Adapter {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  
  async getUsers() {
    const response = await fetch(`${this.baseURL}/v2/users`);
    const data = await response.json();
    
    // Transform v2 response to look like v1 (temporary)
    return {
      users: data.data.users.map(user => ({
        id: user.id,
        name: user.fullName,  // Map back to old field name
        email: user.contactEmail
      }))
    };
  }
}

// Use adapter
const api = new APIv2Adapter('https://api.example.com');
const result = await api.getUsers();
// result.users works like v1 response
```

## Testing Checklist
- [ ] Update API base URL to /v2
- [ ] Update field references (name → fullName, email → contactEmail)
- [ ] Handle pagination in list endpoints
- [ ] Update error handling for new error format
- [ ] Test with staging environment
- [ ] Update API key if required
- [ ] Monitor for errors after deployment

## Rollback Plan
If issues occur:
1. Change base URL back to /v1
2. v1 will remain available until sunset date
3. Report issues to support@example.com

## Support
- Migration guide: https://docs.example.com/v2-migration
- API v2 reference: https://docs.example.com/api/v2
- Support: support@example.com
- Migration deadline: 2025-12-01
```

**Save as:** `docs/API_V2_MIGRATION.md`

**Verification:**
- [ ] All breaking changes documented
- [ ] Code examples in multiple languages
- [ ] Rollback plan included
- [ ] Support contact information provided
- [ ] Published and accessible to users

**If This Fails:**
→ Review migration guides from major APIs (Stripe, Twilio, GitHub)
→ Include before/after code samples for every change
→ Provide working examples in common languages (JS, Python, etc.)
→ Get feedback from early adopters before full publication

---

### Step 5: Communicate with API Consumers

**What:** Proactively notify all API consumers about upcoming changes

**How:**
Use multiple communication channels with adequate notice period (typically 90 days minimum for breaking changes).

**Code/Commands:**
```bash
# Send email notifications to registered developers
cat > announcement_email.html <<'EOF'
Subject: [Important] API v1 Deprecation - Action Required

Dear API User,

We're writing to inform you about an important upcoming change to our API.

## What's Changing
API v1 will be deprecated and shut down on December 1, 2025.

## Action Required
Please migrate to API v2 before the deadline. We've prepared a comprehensive 
migration guide: https://docs.example.com/v2-migration

## Timeline
- Today: API v2 is available
- November 1, 2025: v1 will return deprecation warnings
- December 1, 2025: v1 will be shut down

## Breaking Changes
- Response structure updated (see migration guide)
- Pagination added to list endpoints
- Field names updated for clarity

## Support
Our team is here to help with your migration:
- Migration guide: https://docs.example.com/v2-migration
- Support email: support@example.com
- Office hours: Tuesdays 2-4 PM EST

Thank you for using our API!
EOF

# Create dashboard notification banner
cat > banner.json <<'EOF'
{
  "type": "warning",
  "message": "API v1 will be deprecated on Dec 1, 2025. Migrate to v2 now!",
  "link": "https://docs.example.com/v2-migration",
  "dismissible": false,
  "expires": "2025-12-01"
}
EOF

# Post to status page / changelog
gh api repos/owner/repo/releases \
  --method POST \
  -f tag_name='api-v2.0.0' \
  -f name='API v2.0 Release - Breaking Changes' \
  -f body='## API v2.0 Released

  This release includes breaking changes. Please review the migration guide.
  
  ### Timeline
  - v2 available: Now
  - v1 deprecated: Nov 1, 2025
  - v1 sunset: Dec 1, 2025
  
  [Migration Guide](https://docs.example.com/v2-migration)'

# Track who has been notified
cat > notifications_sent.csv <<'EOF'
date,method,audience,count
2025-10-25,email,all_users,1500
2025-10-25,dashboard,logged_in_users,800
2025-10-25,docs,public,all
EOF
```

**Verification:**
- [ ] Email sent to all registered users
- [ ] Dashboard banner visible
- [ ] Documentation updated
- [ ] Blog post published
- [ ] Social media announcement made
- [ ] Partner organizations contacted directly

**If This Fails:**
→ Verify email list is current
→ Check spam filters aren't blocking
→ Use multiple channels (email, SMS, in-app)
→ Follow up with high-value customers personally

---

### Step 6: Monitor Migration Progress

**What:** Track who's migrating and who needs additional help

**How:**
Use API analytics to monitor v1/v2 traffic patterns and identify laggards.

**Code/Commands:**
```python
# Create migration dashboard
import pandas as pd
from datetime import datetime, timedelta

class MigrationTracker:
    def __init__(self):
        self.v1_usage = {}  # {client_id: request_count}
        self.v2_usage = {}
    
    def record_request(self, client_id, version):
        if version == "v1":
            self.v1_usage[client_id] = self.v1_usage.get(client_id, 0) + 1
        else:
            self.v2_usage[client_id] = self.v2_usage.get(client_id, 0) + 1
    
    def get_migration_status(self):
        all_clients = set(self.v1_usage.keys()) | set(self.v2_usage.keys())
        
        status = []
        for client in all_clients:
            v1_requests = self.v1_usage.get(client, 0)
            v2_requests = self.v2_usage.get(client, 0)
            total = v1_requests + v2_requests
            
            if v1_requests == 0:
                migration_status = "Migrated"
            elif v2_requests == 0:
                migration_status = "Not Started"
            else:
                migration_status = "In Progress"
            
            status.append({
                "client_id": client,
                "v1_requests": v1_requests,
                "v2_requests": v2_requests,
                "v2_percentage": (v2_requests / total * 100) if total > 0 else 0,
                "status": migration_status
            })
        
        return pd.DataFrame(status)
    
    def get_laggards(self, threshold_percentage=50):
        """Clients still using >50% v1 traffic"""
        df = self.get_migration_status()
        return df[df['v2_percentage'] < threshold_percentage]

# Generate weekly migration report
def generate_migration_report(tracker):
    df = tracker.get_migration_status()
    
    print("=== Migration Status Report ===")
    print(f"Total Clients: {len(df)}")
    print(f"Fully Migrated: {len(df[df['status'] == 'Migrated'])}")
    print(f"In Progress: {len(df[df['status'] == 'In Progress'])}")
    print(f"Not Started: {len(df[df['status'] == 'Not Started'])}")
    print(f"\nv2 Adoption Rate: {df['v2_percentage'].mean():.1f}%")
    
    print("\n=== Clients Needing Attention ===")
    laggards = tracker.get_laggards()
    for _, row in laggards.iterrows():
        print(f"Client: {row['client_id']} - "
              f"v2 Usage: {row['v2_percentage']:.1f}%")

# SQL query for database analytics
sql_query = """
SELECT 
    DATE(timestamp) as date,
    api_version,
    client_id,
    COUNT(*) as request_count
FROM api_logs
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY date, api_version, client_id
ORDER BY date DESC, api_version;
"""

# Create automated alert for lagging migrations
def check_migration_deadline():
    days_until_sunset = (datetime(2025, 12, 1) - datetime.now()).days
    
    if days_until_sunset <= 30:
        laggards = tracker.get_laggards(threshold_percentage=80)
        if len(laggards) > 0:
            send_urgent_notification(
                laggards,
                f"Only {days_until_sunset} days until v1 sunset!"
            )
```

**Verification:**
- [ ] Analytics tracking v1 vs v2 usage
- [ ] Dashboard showing migration progress
- [ ] Alerts configured for laggards
- [ ] Weekly reports generated
- [ ] High-touch customers identified

**If This Fails:**
→ Implement basic logging if analytics unavailable
→ Manual surveys of key customers
→ Review support tickets for migration issues
→ Set up simple request counting

---

### Step 7: Support Migration Period

**What:** Provide hands-on help during the migration window

**How:**
Offer office hours, direct support, and temporary compatibility layers if needed.

**Code/Commands:**
```python
# Create temporary adapter endpoint for gradual migration
@app.get("/api/v1/users-compat")
async def users_compat_endpoint():
    """
    Temporary compatibility endpoint that returns v2 data in v1 format.
    Helps clients migrate gradually.
    """
    # Get v2 data
    v2_response = await get_users_v2()
    
    # Transform to v1 format
    v1_compatible = {
        "users": [
            {
                "id": user["id"],
                "name": user["fullName"],  # v2 field -> v1 name
                "email": user["contactEmail"],
                "created": user["createdAt"]
            }
            for user in v2_response["data"]["users"]
        ]
    }
    
    # Add warning header
    response.headers["X-API-Notice"] = (
        "Using compatibility endpoint. "
        "Please migrate to /api/v2/users for full features."
    )
    
    return v1_compatible

# Schedule migration office hours
cat > office_hours.md <<'EOF'
# API Migration Office Hours

## Schedule
Every Tuesday, 2:00-4:00 PM EST
October 25 - November 30, 2025

## Join Us
Zoom: https://zoom.us/j/123456789
No registration required

## What We'll Cover
- Live migration assistance
- Code review for your integration
- Answer questions
- Debug issues
- Best practices

## Preparation
Please have ready:
- Your current API integration code
- Questions about specific endpoints
- Test environment for trying changes
EOF

# Track support requests
cat > support_tracker.csv <<'EOF'
date,client,issue,status,resolution
2025-10-25,client-A,pagination-confusion,resolved,provided-code-sample
2025-10-26,client-B,field-mapping-error,resolved,updated-docs
2025-10-27,client-C,auth-issues,in-progress,investigating
EOF

# Create FAQ document from common questions
cat > migration_faq.md <<'EOF'
# API v2 Migration FAQ

## Q: Do I need to update my API key?
A: No, existing API keys work with both v1 and v2.

## Q: Can I use v1 and v2 simultaneously?
A: Yes! Both versions will run in parallel until Dec 1, 2025.

## Q: What happens if I don't migrate by the deadline?
A: Your API calls to v1 endpoints will start returning 410 Gone errors.

## Q: Will v2 have different rate limits?
A: No, rate limits remain the same.

## Q: How do I test v2 without affecting production?
A: Use our staging environment: https://staging-api.example.com/v2

## Q: Where can I get help?
A: Email support@example.com or join office hours (Tuesdays 2-4 PM EST)
EOF
```

**Verification:**
- [ ] Support channels publicized
- [ ] Office hours scheduled and announced
- [ ] FAQ document published
- [ ] Response time for support < 24 hours
- [ ] All major blockers resolved

**If This Fails:**
→ Extend migration deadline if many users struggling
→ Create more code examples
→ Offer 1:1 assistance to high-value customers
→ Consider creating automated migration tools

---

### Step 8: Execute Sunset and Cleanup

**What:** Safely shut down old API version and clean up deprecated code

**How:**
Follow the timeline strictly, communicate final warnings, then redirect/disable old endpoints.

**Code/Commands:**
```python
# Week before sunset - final warnings
@v1_router.get("/users")
def get_users_v1_final_warning(response: Response):
    days_until_sunset = 7  # Calculate actual days
    
    if days_until_sunset <= 7:
        response.headers["X-API-Critical-Warning"] = (
            f"URGENT: This endpoint will be shut down in {days_until_sunset} days. "
            "Migrate to /api/v2/users immediately!"
        )
        response.status_code = 299  # Warning status code
    
    return {
        "users": [...],
        "_critical_warning": {
            "message": f"API v1 shuts down in {days_until_sunset} days",
            "action_required": "Migrate to /api/v2/users",
            "sunset_date": "2025-12-01",
            "migration_guide": "https://docs.example.com/v2-migration"
        }
    }

# On sunset date - return 410 Gone
@v1_router.get("/users")
def get_users_v1_sunset(response: Response):
    response.status_code = 410
    return {
        "error": {
            "code": "API_VERSION_DISCONTINUED",
            "message": "API v1 has been discontinued as of 2025-12-01",
            "sunset_date": "2025-12-01",
            "new_version": "/api/v2/users",
            "migration_guide": "https://docs.example.com/v2-migration"
        }
    }

# Or redirect to v2 (if schema compatible enough)
from fastapi.responses import RedirectResponse

@v1_router.get("/users")
def get_users_v1_redirect():
    return RedirectResponse(
        url="/api/v2/users",
        status_code=301  # Permanent redirect
    )

# Cleanup checklist script
cat > sunset_cleanup.sh <<'EOF'
#!/bin/bash
# Run this script after v1 sunset

echo "Starting API v1 cleanup..."

# 1. Remove v1 routes from codebase
echo "Removing v1 routes..."
git rm -r src/api/v1/
git commit -m "Remove API v1 (sunset 2025-12-01)"

# 2. Update documentation
echo "Updating documentation..."
sed -i 's/\/api\/v1\//\/api\/v2\//g' docs/**/*.md
git add docs/
git commit -m "Update docs to reference only v2"

# 3. Remove v1 tests
echo "Removing v1 tests..."
git rm tests/api/v1/
git commit -m "Remove API v1 tests"

# 4. Update CI/CD pipelines
echo "Updating CI/CD..."
# Remove v1 deployment steps

# 5. Update monitoring
echo "Updating monitoring..."
# Remove v1 alerts and dashboards

# 6. Archive v1 code for reference
echo "Archiving v1..."
git tag "api-v1-archived-$(date +%Y%m%d)"
git push --tags

echo "✅ Cleanup complete!"
EOF

chmod +x sunset_cleanup.sh

# Send final sunset notification
cat > sunset_notification.txt <<'EOF'
Subject: API v1 Has Been Sunset

Dear API User,

As previously announced, API v1 has been shut down as of December 1, 2025.

All requests to v1 endpoints now return 410 Gone status codes.

If you haven't migrated yet:
1. Update your API base URL to /v2
2. Follow the migration guide: https://docs.example.com/v2-migration
3. Contact support for urgent assistance: support@example.com

Thank you for your cooperation during this transition.
EOF
```

**Verification:**
- [ ] V1 endpoints returning 410 Gone
- [ ] No critical systems still using v1
- [ ] Documentation updated (v1 references removed)
- [ ] V1 code removed from codebase
- [ ] Monitoring updated
- [ ] Final notifications sent

**If This Fails:**
→ Emergency rollback if critical systems still depend on v1
→ Extend deadline with clear communication
→ Offer hotline for emergency support
→ Document what went wrong for next time

---

## Verification Checklist

After completing this workflow:

- [ ] All API consumers notified (90+ days notice)
- [ ] Migration guide published and accessible
- [ ] V2 API fully functional and tested
- [ ] Deprecation warnings implemented
- [ ] Migration progress tracked and monitored
- [ ] Support provided during migration period
- [ ] V1 successfully sunset on schedule
- [ ] Codebase cleaned up (v1 code removed)
- [ ] Documentation reflects only v2
- [ ] Retrospective completed to improve future migrations

---

## Common Issues & Solutions

### Issue: Clients Ignore Deprecation Warnings

**Symptoms:**
- Low migration rate despite notifications
- Clients continue using v1 without concern

**Solution:**
```python
# Implement progressive degradation
# Start returning partial data or slower responses in v1

@v1_router.get("/users")
def get_users_v1_degraded():
    # Add artificial delay to encourage migration
    import time
    time.sleep(2)  # 2 second delay
    
    response.headers["X-API-Performance-Notice"] = (
        "v1 endpoints are throttled. Migrate to v2 for full performance."
    )
    
    # Return limited data
    return {
        "users": [...],  # Only return first 10 users
        "_warning": "Partial results. v2 returns complete data."
    }
```

**Prevention:**
- Start warnings 120+ days before sunset
- Use multiple communication channels
- Implement rate limiting on deprecated endpoints
- Make v2 clearly better (faster, more features)

---

### Issue: Breaking Change Discovered After Launch

**Symptoms:**
- Unexpected behavior in production
- Clients reporting errors not covered in migration guide

**Solution:**
```python
# Implement quick compatibility shim
@v2_router.get("/users")
def get_users_v2_with_shim(
    compat_mode: bool = Header(default=False, alias="X-V1-Compat-Mode")
):
    """Add compatibility mode header to ease migration"""
    users = fetch_users()
    
    if compat_mode:
        # Return data in v1-compatible format
        return {
            "users": [
                {
                    "id": u["id"],
                    "name": u["fullName"],  # Use v1 field names
                    "email": u["contactEmail"]
                }
                for u in users
            ]
        }
    
    # Normal v2 response
    return {"data": {"users": users}, "meta": {}}
```

**Prevention:**
- Extensive testing with real consumer code
- Beta testing period with select users
- Gradual rollout (feature flags)
- Comprehensive API diff tools

---

### Issue: Partner Refuses to Migrate by Deadline

**Symptoms:**
- Critical integration partner won't update
- Business risk of breaking their integration

**Solution:**
1. **Negotiate extension** - Provide 30-60 day extension for specific client
2. **Implement client-specific compatibility layer:**
```python
GRANDFATHERED_CLIENTS = ["partner-api-key-123"]

@v1_router.get("/users")
def get_users_v1(api_key: str = Header(...)):
    if api_key in GRANDFATHERED_CLIENTS:
        # Allow v1 access temporarily
        return get_users_v1_impl()
    
    # Everyone else gets 410
    raise HTTPException(status_code=410, detail="API v1 discontinued")
```

3. **Charge for extended support** - Financial incentive to migrate

**Prevention:**
- Identify critical partners early
- Offer dedicated migration assistance
- Negotiate migration timeline in contracts
- Build migration cost into partnership agreements

---

## Best Practices

### DO:
✅ **Give 90+ days notice** - Minimum notice period for breaking changes  
✅ **Use API versioning** - URL path versioning (/v1, /v2) is clearest  
✅ **Run versions in parallel** - Old and new together during migration  
✅ **Track migration progress** - Know who's migrated and who hasn't  
✅ **Provide comprehensive migration guide** - Code examples in multiple languages  
✅ **Offer direct support** - Office hours, email, dedicated help  
✅ **Deprecation warnings** - Headers and response fields warning of sunset  
✅ **Monitor error rates** - Watch for spikes after changes  
✅ **Document the process** - Help future teams avoid same mistakes  
✅ **Learn from major APIs** - Study how Stripe, GitHub, Twitter handle breaking changes

### DON'T:
❌ **Make breaking changes without notice** - Respect your consumers  
❌ **Shutdown old version too quickly** - 90 days minimum, 6 months better  
❌ **Communicate only once** - Multiple reminders needed  
❌ **Ignore migration analytics** - Track who's migrating  
❌ **Break changes in minor versions** - Follow semantic versioning  
❌ **Change multiple things at once** - Batch changes thoughtfully  
❌ **Provide inadequate examples** - Show actual code, not just descriptions  
❌ **Skip the retrospective** - Learn for next time  
❌ **Forget about automated tests** - Update tests for both versions  
❌ **Sunset during holidays** - Avoid year-end, summer vacation periods

---

## Related Workflows

**Prerequisites:**
- [API Design Best Practices](../architecture/api_design_best_practices.md) - Design versioning from start
- [CI/CD Pipeline](./ci_cd_workflow.md) - Deploy multiple versions

**Next Steps:**
- [Version Release Tagging](./version_release_tagging.md) - Semantic versioning for APIs
- [Third-Party API Integration](./third_party_api_integration.md) - Handle breaking changes from vendors
- [Technical Debt Management](./technical_debt_mgmt.md) - Plan for removing deprecated code

**Alternatives:**
- [Feature Flags](../devops/feature_flags.md) - Gradual rollouts without versioning
- [Blue-Green Deployment](../devops/blue_green_deployment.md) - Zero-downtime migrations

---

## Tags
`api` `breaking-changes` `versioning` `deprecation` `migration` `backward-compatibility` `semver` `api-design` `sunset` `communication`
