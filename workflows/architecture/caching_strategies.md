# Caching Strategies

**ID:** arc-002  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 45-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design and select effective caching strategies to improve system performance and scalability

**Why:** Proper caching reduces latency by 80-95%, decreases backend load by 60-90%, cuts infrastructure costs, and enables systems to handle 10x more traffic with the same resources

**When to use:**
- Optimizing slow database queries or API calls
- Reducing load on backend services
- Improving application response times
- Scaling to handle traffic spikes
- Reducing cloud infrastructure costs
- Implementing CDN strategies
- Building offline-first applications

---

## Prerequisites

**Required:**
- [ ] Understanding of cache invalidation patterns
- [ ] Familiarity with Redis, Memcached, or similar systems
- [ ] Knowledge of TTL (Time To Live) concepts
- [ ] Understanding of application access patterns
- [ ] Monitoring infrastructure in place

**Check before starting:**
```bash
# Check if Redis is available
redis-cli ping
# Should return: PONG

# Or Memcached
telnet localhost 11211
stats

# Check application monitoring
curl -s http://localhost:9090/metrics | grep cache
```

---

## Implementation Steps

### Step 1: Analyze Access Patterns and Identify Cacheable Data

**What:** Understand what data is accessed, how often, and whether it can be cached

**How:**

**Data Access Analysis:**

```python
# Analyze which data gets accessed most frequently
# Example: Query logs analysis

import pandas as pd
from collections import Counter

def analyze_query_patterns(query_logs):
    """Analyze database query patterns to find caching candidates"""
    
    queries = pd.read_csv(query_logs)
    
    # Group by query type
    query_counts = Counter(queries['query_signature'])
    
    # Find hot queries (top 20%)
    total = sum(query_counts.values())
    hot_queries = []
    
    for query, count in query_counts.most_common():
        if sum(q[1] for q in hot_queries) > total * 0.8:
            break  # 80/20 rule: 20% of queries = 80% of traffic
        hot_queries.append((query, count))
    
    print("Top queries accounting for 80% of traffic:")
    for query, count in hot_queries:
        print(f"{query}: {count} ({count/total*100:.1f}%)")
    
    return hot_queries

# Example output:
# SELECT * FROM products WHERE category=?: 45000 (45%)
# SELECT * FROM users WHERE id=?: 20000 (20%)
# SELECT * FROM orders WHERE user_id=?: 15000 (15%)
```

**Cacheability Decision Matrix:**

```
┌─────────────────────┬──────────┬─────────┬────────────────┐
│ Data Type           │ Read/    │ Change  │ Caching        │
│                     │ Write    │ Rate    │ Strategy       │
├─────────────────────┼──────────┼─────────┼────────────────┤
│ User Profile        │ 90/10    │ Daily   │ ✅ Cache (1hr) │
│ Product Catalog     │ 95/5     │ Weekly  │ ✅ Cache (24hr)│
│ Shopping Cart       │ 50/50    │ Seconds │ ⚠️ Short TTL   │
│ Order History       │ 99/1     │ Never*  │ ✅ Cache (∞)   │
│ Real-time Prices    │ 100/0    │ Seconds │ ❌ Don't cache │
│ Session Data        │ 80/20    │ Minutes │ ✅ Cache (30m) │
│ Search Results      │ 100/0    │ Varies  │ ✅ Cache (1hr) │
│ Live Inventory      │ 100/0    │ Seconds │ ⚠️ Short TTL   │
└─────────────────────┴──────────┴─────────┴────────────────┘

* Append-only data (immutable after creation)
```

**Caching Candidates:**

```
✅ GOOD caching candidates:
- Reference data (countries, currencies, categories)
- User profiles (updated infrequently)
- Product catalogs (change daily at most)
- Computed results (reports, aggregations)
- External API responses (weather, geocoding)
- Static content (images, CSS, JS)
- Expensive database queries
- Session data

❌ POOR caching candidates:
- Real-time data (stock prices, live scores)
- Personalized recommendations (unless pre-computed)
- Data with complex invalidation (many dependencies)
- Frequently changing data (live inventory)
- Transactional data during modification
- Sensitive data without encryption

⚠️ CACHE WITH CAUTION:
- Shopping carts (short TTL, user-specific)
- Search results (pagination issues)
- Aggregations (may become stale)
- Data with consistency requirements
```

**Verification:**
- [ ] Identified top 20% of queries by volume
- [ ] Determined read/write ratio for each data type
- [ ] Documented change frequency
- [ ] Listed caching candidates with rationale
- [ ] Considered data consistency requirements

**If This Fails:**
→ Start with most obvious candidates (product catalogs, user profiles)
→ Monitor production metrics if logs unavailable
→ Use application profiling to find slow queries

---

### Step 2: Choose Caching Layer and Architecture

**What:** Select appropriate caching technology and architectural pattern

**How:**

**Caching Layers:**

```
┌─────────────────────────────────────────────────────┐
│ Client Side (Browser/Mobile)                        │
│ • HTTP Cache (Cache-Control, ETag)                  │
│ • LocalStorage / IndexedDB                          │
│ • Service Workers                                   │
│ TTL: Minutes to hours                               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ CDN (Cloudflare, CloudFront, Fastly)                │
│ • Static assets                                     │
│ • API responses (with headers)                      │
│ TTL: Hours to days                                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Application Cache (Redis, Memcached)                │
│ • Session data                                      │
│ • Database query results                            │
│ • Computed values                                   │
│ TTL: Seconds to hours                               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ Database Query Cache                                │
│ • Query result cache                                │
│ • Materialized views                                │
│ TTL: Automatic or manual invalidation               │
└─────────────────────────────────────────────────────┘
```

**Technology Comparison:**

```
┌──────────────┬─────────┬──────────┬────────────┬─────────────┐
│ Technology   │ Speed   │ Features │ Complexity │ Use Case    │
├──────────────┼─────────┼──────────┼────────────┼─────────────┤
│ Redis        │ Fast    │ Rich     │ Medium     │ General     │
│              │ <1ms    │ Pub/Sub  │            │ Application │
│              │         │ Data     │            │ Cache       │
│              │         │ Structures│           │             │
├──────────────┼─────────┼──────────┼────────────┼─────────────┤
│ Memcached    │ Fast    │ Simple   │ Low        │ Simple      │
│              │ <1ms    │ KV only  │            │ KV Cache    │
├──────────────┼─────────┼──────────┼────────────┼─────────────┤
│ CDN          │ Fastest │ HTTP     │ Low        │ Static      │
│              │ <50ms   │ only     │            │ Content     │
├──────────────┼─────────┼──────────┼────────────┼─────────────┤
│ Local Cache  │ Fastest │ Simple   │ Low        │ In-Process  │
│ (in-memory)  │ <0.1ms  │          │            │ Cache       │
├──────────────┼─────────┼──────────┼────────────┼─────────────┤
│ DynamoDB DAX │ Fast    │ AWS      │ High       │ AWS         │
│              │ <1ms    │ Native   │            │ DynamoDB    │
└──────────────┴─────────┴──────────┴────────────┴─────────────┘
```

**Recommended: Redis for Application Cache:**

```python
# Why Redis:
# ✅ Supports complex data structures (strings, lists, sets, hashes)
# ✅ Built-in TTL per key
# ✅ Pub/Sub for cache invalidation
# ✅ Atomic operations
# ✅ Persistence options
# ✅ Clustering and replication
# ✅ Mature ecosystem

# Redis Setup
import redis
from functools import wraps
import json

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_keepalive=True,
    health_check_interval=30
)

# Test connection
try:
    redis_client.ping()
    print("✅ Redis connected")
except redis.ConnectionError:
    print("❌ Redis connection failed")
```

**Caching Patterns:**

```python
# Pattern 1: Cache-Aside (Lazy Loading)
# Most common pattern

def get_user(user_id):
    cache_key = f"user:{user_id}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss - fetch from database
    user = db.query(User).get(user_id)
    if user:
        # Store in cache
        redis_client.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(user.to_dict())
        )
    
    return user

# Pattern 2: Write-Through
# Write to cache and database simultaneously

def update_user(user_id, data):
    cache_key = f"user:{user_id}"
    
    # Update database
    user = db.query(User).get(user_id)
    user.update(data)
    db.commit()
    
    # Update cache immediately
    redis_client.setex(
        cache_key,
        3600,
        json.dumps(user.to_dict())
    )
    
    return user

# Pattern 3: Write-Behind (Write-Back)
# Write to cache immediately, sync to DB async

from celery import Celery

def update_user_async(user_id, data):
    cache_key = f"user:{user_id}"
    
    # Update cache immediately
    cached_user = json.loads(redis_client.get(cache_key) or "{}")
    cached_user.update(data)
    redis_client.setex(cache_key, 3600, json.dumps(cached_user))
    
    # Schedule async DB write
    sync_to_database.delay(user_id, data)
    
    return cached_user

@celery.task
def sync_to_database(user_id, data):
    user = db.query(User).get(user_id)
    user.update(data)
    db.commit()

# Pattern 4: Read-Through
# Cache handles database fetching

class CachingRepository:
    def get_user(self, user_id):
        cache_key = f"user:{user_id}"
        
        # If in cache, return
        # If not, fetch from DB and cache automatically
        return self.get_or_compute(
            cache_key,
            lambda: db.query(User).get(user_id),
            ttl=3600
        )
```

**Verification:**
- [ ] Caching technology selected based on needs
- [ ] Caching layer architecture designed
- [ ] Pattern chosen (cache-aside, write-through, etc.)
- [ ] Redis/cache system deployed and tested
- [ ] Connection pooling configured

**If This Fails:**
→ Start with simple cache-aside pattern
→ Use managed Redis (AWS ElastiCache, Redis Cloud)
→ Begin with single Redis instance, scale later

---

### Step 3: Design Cache Key Structure and Namespacing

**What:** Create consistent, collision-free cache key naming convention

**How:**

**Cache Key Design Principles:**

```python
# Good cache key structure:
# {namespace}:{entity}:{id}[:qualifier]

# Examples:
"user:123"                    # User with ID 123
"product:456"                 # Product with ID 456
"search:electronics:page:2"   # Search results
"api:weather:SF:94102"        # External API cache
"session:abc123"              # User session
"rate_limit:user:123:hour"    # Rate limiting counter

# BAD examples:
"123"                         # ❌ No context
"get_user_123"                # ❌ Verb in key
"UserCache_123"               # ❌ Mixed case
"u:123"                       # ❌ Cryptic abbreviation
```

**Key Naming Conventions:**

```python
class CacheKeys:
    """Centralized cache key management"""
    
    # Version prefix for cache invalidation
    VERSION = "v1"
    
    @classmethod
    def user(cls, user_id: int) -> str:
        return f"{cls.VERSION}:user:{user_id}"
    
    @classmethod
    def user_posts(cls, user_id: int, page: int = 1) -> str:
        return f"{cls.VERSION}:user:{user_id}:posts:page:{page}"
    
    @classmethod
    def product(cls, product_id: int) -> str:
        return f"{cls.VERSION}:product:{product_id}"
    
    @classmethod
    def product_list(cls, category: str, page: int = 1) -> str:
        return f"{cls.VERSION}:products:category:{category}:page:{page}"
    
    @classmethod
    def search_results(cls, query: str, page: int = 1) -> str:
        # Hash long queries to keep keys short
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"{cls.VERSION}:search:{query_hash}:page:{page}"
    
    @classmethod
    def api_response(cls, service: str, endpoint: str, **params) -> str:
        # Stable key from params
        param_str = ":".join(f"{k}:{v}" for k, v in sorted(params.items()))
        return f"{cls.VERSION}:api:{service}:{endpoint}:{param_str}"

# Usage
cache_key = CacheKeys.user(123)  # "v1:user:123"
cache_key = CacheKeys.product_list("electronics", page=2)
# "v1:products:category:electronics:page:2"
```

**Namespace Benefits:**

```python
# Easy bulk invalidation by namespace

def invalidate_user_cache(user_id):
    """Invalidate all cached data for a user"""
    pattern = f"v1:user:{user_id}:*"
    
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
    
    # Also delete user object
    redis_client.delete(f"v1:user:{user_id}")

def invalidate_category_cache(category):
    """Invalidate all product lists for a category"""
    pattern = f"v1:products:category:{category}:*"
    
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)

# Version-based cache busting
def clear_all_cache_on_deploy():
    """Increment version to invalidate all cached data"""
    # Simply change VERSION = "v2" in CacheKeys class
    # Old v1:* keys will expire naturally
    pass
```

**Key Length Optimization:**

```python
# For very long keys, use hashing

def create_cache_key(prefix: str, *parts, max_length: int = 250) -> str:
    """Create cache key, hashing if too long"""
    key = ":".join([prefix] + [str(p) for p in parts])
    
    if len(key) > max_length:
        import hashlib
        # Keep prefix readable, hash the rest
        hash_part = hashlib.sha256(key.encode()).hexdigest()[:16]
        return f"{prefix}:hash:{hash_part}"
    
    return key

# Example
long_query = "SELECT * FROM products WHERE category='electronics' AND ..."
key = create_cache_key("query", long_query)
# Result: "query:hash:a1b2c3d4e5f6g7h8"
```

**Verification:**
- [ ] Key naming convention documented
- [ ] Centralized key generation (CacheKeys class)
- [ ] Namespace pattern established
- [ ] Version prefix for cache busting
- [ ] Long keys handled appropriately
- [ ] No key collisions possible

**If This Fails:**
→ Start with simple "{entity}:{id}" pattern
→ Add namespaces as complexity grows
→ Use key generator functions, not manual strings

---

### Step 4: Set Appropriate TTL (Time To Live) Values

**What:** Determine how long cached data should live based on staleness tolerance

**How:**

**TTL Decision Framework:**

```
Data Change Frequency → Maximum Acceptable Staleness → TTL

Seconds    → 0 (real-time)    → ❌ Don't cache
Minutes    → 1-5 minutes      → 60-300 seconds
Hourly     → 10-30 minutes    → 600-1800 seconds
Daily      → 1-4 hours        → 3600-14400 seconds
Weekly     → 12-24 hours      → 43200-86400 seconds
Never*     → ∞ (until event)  → No TTL or very long
                                (use invalidation)

* Immutable data or explicit invalidation strategy
```

**TTL Examples by Data Type:**

```python
class CacheTTL:
    """Standard TTL values in seconds"""
    
    # Short TTLs (< 5 minutes)
    SHOPPING_CART = 300         # 5 minutes
    LIVE_INVENTORY = 30         # 30 seconds
    RATE_LIMIT = 60             # 1 minute
    
    # Medium TTLs (5 minutes - 1 hour)
    SESSION_DATA = 1800         # 30 minutes
    SEARCH_RESULTS = 600        # 10 minutes
    USER_PROFILE = 3600         # 1 hour
    
    # Long TTLs (1 hour - 24 hours)
    PRODUCT_CATALOG = 14400     # 4 hours
    CATEGORY_LIST = 43200       # 12 hours
    CONFIG_DATA = 86400         # 24 hours
    
    # Very Long TTLs (> 24 hours)
    REFERENCE_DATA = 604800     # 7 days
    STATIC_CONTENT = 2592000    # 30 days
    
    # Infinite (use invalidation)
    ORDER_HISTORY = None        # Never expires (immutable)

# Usage
redis_client.setex(
    CacheKeys.user(123),
    CacheTTL.USER_PROFILE,
    json.dumps(user_data)
)
```

**TTL with Jitter (Avoid Thundering Herd):**

```python
import random

def set_cache_with_jitter(key, value, base_ttl, jitter_percent=0.1):
    """
    Set cache with randomized TTL to prevent thundering herd
    
    Thundering herd: Many cache entries expire simultaneously,
    causing spike in database load
    """
    # Add random jitter (e.g., ±10%)
    jitter = int(base_ttl * jitter_percent)
    ttl = base_ttl + random.randint(-jitter, jitter)
    
    redis_client.setex(key, ttl, value)
    
    return ttl

# Example: TTL will be 3600 ± 360 seconds (54-66 minutes)
set_cache_with_jitter(
    "user:123",
    user_json,
    base_ttl=3600,
    jitter_percent=0.1
)
```

**Adaptive TTL (Based on Access Patterns):**

```python
def adaptive_ttl(key, value, min_ttl=300, max_ttl=3600):
    """
    Set TTL based on access frequency
    Frequently accessed items get longer TTL
    """
    # Track access count
    access_key = f"access_count:{key}"
    access_count = int(redis_client.get(access_key) or 0)
    redis_client.incr(access_key)
    redis_client.expire(access_key, max_ttl)
    
    # More accesses = longer TTL
    if access_count > 100:
        ttl = max_ttl  # Very popular
    elif access_count > 10:
        ttl = max_ttl // 2  # Popular
    else:
        ttl = min_ttl  # Less popular
    
    redis_client.setex(key, ttl, value)
    return ttl

# Example: Popular items cached longer
adaptive_ttl("product:bestseller:1", product_json)  # → 3600s
adaptive_ttl("product:obscure:9999", product_json)  # → 300s
```

**TTL for Different Scenarios:**

```python
# Scenario 1: E-commerce product catalog
# - Changes: Daily inventory updates
# - Staleness tolerance: 1-4 hours acceptable
TTL = 4 * 3600  # 4 hours

# Scenario 2: User session data
# - Changes: On every user action
# - Staleness tolerance: Must be fresh (but temporary)
TTL = 30 * 60  # 30 minutes (session timeout)

# Scenario 3: API rate limiting
# - Changes: Every request
# - Staleness tolerance: None (must be accurate)
TTL = 3600  # 1 hour (window size)
# Use atomic INCR to avoid race conditions

# Scenario 4: External API cache (weather)
# - Changes: Hourly
# - Staleness tolerance: 30-60 minutes acceptable
TTL = 45 * 60  # 45 minutes (with jitter)

# Scenario 5: Immutable data (order history)
# - Changes: Never (append-only)
# - Staleness tolerance: N/A (always accurate)
TTL = None  # Use explicit invalidation or very long TTL
```

**Verification:**
- [ ] TTL values documented for each data type
- [ ] TTL matches data change frequency
- [ ] Jitter implemented for popular caches
- [ ] No hardcoded TTLs in code (use constants)
- [ ] TTL values tested under load

**If This Fails:**
→ Start with conservative short TTLs (5-10 minutes)
→ Monitor cache hit rates and adjust
→ Use longer TTLs for stable data, shorter for volatile

---

### Step 5: Implement Cache Invalidation Strategy

**What:** Design how and when to remove or update stale cached data

**How:**

**Cache Invalidation Strategies:**

```python
# 1. TTL-based (Passive Expiration)
# Simplest: Let cache expire naturally

redis_client.setex("user:123", 3600, user_json)
# Cache expires automatically after 1 hour

# Pros: Simple, no explicit invalidation needed
# Cons: May serve stale data until expiration

# 2. Event-based (Active Invalidation)
# Delete cache when data changes

def update_user(user_id, data):
    # Update database
    user = db.query(User).get(user_id)
    user.update(data)
    db.commit()
    
    # Invalidate cache
    cache_key = CacheKeys.user(user_id)
    redis_client.delete(cache_key)
    
    # Also invalidate related caches
    redis_client.delete(CacheKeys.user_posts(user_id))
    
    return user

# Pros: Always fresh data
# Cons: Must track all cache dependencies

# 3. Tag-based Invalidation
# Tag related caches for bulk invalidation

def set_cache_with_tags(key, value, ttl, tags=None):
    """Cache with tags for easy bulk invalidation"""
    # Store value
    redis_client.setex(key, ttl, value)
    
    # Store tags
    if tags:
        for tag in tags:
            tag_key = f"tag:{tag}"
            redis_client.sadd(tag_key, key)
            redis_client.expire(tag_key, ttl)

def invalidate_by_tag(tag):
    """Invalidate all caches with given tag"""
    tag_key = f"tag:{tag}"
    keys = redis_client.smembers(tag_key)
    
    if keys:
        redis_client.delete(*keys)
        redis_client.delete(tag_key)

# Usage
set_cache_with_tags(
    "product:123",
    product_json,
    ttl=3600,
    tags=["products", "category:electronics", "brand:apple"]
)

# Invalidate all products in electronics category
invalidate_by_tag("category:electronics")

# 4. Write-Through Cache
# Update cache when updating database

def update_product(product_id, data):
    # Update database
    product = db.query(Product).get(product_id)
    product.update(data)
    db.commit()
    
    # Update cache immediately with fresh data
    cache_key = CacheKeys.product(product_id)
    redis_client.setex(
        cache_key,
        CacheTTL.PRODUCT_CATALOG,
        json.dumps(product.to_dict())
    )
    
    return product

# Pros: Cache always has latest data
# Cons: Extra write on every update

# 5. Cache Versioning
# Increment version to invalidate entire cache

class CacheVersion:
    @classmethod
    def get_current_version(cls):
        version = redis_client.get("cache:version")
        if not version:
            cls.bump_version()
            version = redis_client.get("cache:version")
        return version
    
    @classmethod
    def bump_version(cls):
        """Increment version to invalidate all caches"""
        redis_client.incr("cache:version")
    
    @classmethod
    def versioned_key(cls, key):
        version = cls.get_current_version()
        return f"{version}:{key}"

# Usage
key = CacheVersion.versioned_key("user:123")  # "1:user:123"
redis_client.set(key, user_json)

# Invalidate ALL caches by incrementing version
CacheVersion.bump_version()  # Now version is 2
# Old "1:*" keys will expire, new keys use "2:*"
```

**Pub/Sub for Cache Invalidation (Distributed Systems):**

```python
# Server 1: Publish invalidation event
def update_user_with_pubsub(user_id, data):
    # Update database
    user = db.query(User).get(user_id)
    user.update(data)
    db.commit()
    
    # Publish invalidation event
    redis_client.publish(
        "cache:invalidate",
        json.dumps({"type": "user", "id": user_id})
    )

# Server 2,3,4...: Subscribe to invalidation events
pubsub = redis_client.pubsub()
pubsub.subscribe("cache:invalidate")

for message in pubsub.listen():
    if message['type'] == 'message':
        event = json.loads(message['data'])
        
        if event['type'] == 'user':
            # Remove from local cache
            local_cache.delete(f"user:{event['id']}")
            
            # Remove from Redis cache
            redis_client.delete(CacheKeys.user(event['id']))
```

**Dependency Tracking:**

```python
class CacheDependencies:
    """Track cache dependencies for cascade invalidation"""
    
    @staticmethod
    def track_dependency(cache_key, depends_on):
        """Record that cache_key depends on depends_on"""
        dep_key = f"deps:{depends_on}"
        redis_client.sadd(dep_key, cache_key)
        redis_client.expire(dep_key, CacheTTL.REFERENCE_DATA)
    
    @staticmethod
    def invalidate_with_deps(cache_key):
        """Invalidate cache and all dependent caches"""
        # Invalidate the cache
        redis_client.delete(cache_key)
        
        # Find and invalidate dependent caches
        dep_key = f"deps:{cache_key}"
        dependent_keys = redis_client.smembers(dep_key)
        
        if dependent_keys:
            redis_client.delete(*dependent_keys)
            redis_client.delete(dep_key)

# Usage
user_key = CacheKeys.user(123)
posts_key = CacheKeys.user_posts(123)

# Track that posts depend on user
CacheDependencies.track_dependency(posts_key, user_key)

# When user changes, invalidate user and posts
CacheDependencies.invalidate_with_deps(user_key)
```

**Verification:**
- [ ] Invalidation strategy chosen
- [ ] Cache invalidated on data updates
- [ ] Related caches invalidated (dependencies)
- [ ] Pub/sub configured for distributed systems
- [ ] Tag-based invalidation for bulk operations
- [ ] Version bumping for emergency cache clear

**If This Fails:**
→ Start with simple TTL-based expiration
→ Add event-based invalidation for critical data
→ Use conservative short TTLs if invalidation is complex

---

### Step 6: Monitor Cache Performance

**What:** Track cache effectiveness and optimize based on metrics

**How:**

**Key Cache Metrics:**

```python
import time
from functools import wraps

class CacheMetrics:
    """Track cache hit/miss rates and latency"""
    
    hits = 0
    misses = 0
    total_latency = 0.0
    
    @classmethod
    def record_hit(cls, latency):
        cls.hits += 1
        cls.total_latency += latency
    
    @classmethod
    def record_miss(cls):
        cls.misses += 1
    
    @classmethod
    def get_hit_rate(cls):
        total = cls.hits + cls.misses
        return cls.hits / total if total > 0 else 0
    
    @classmethod
    def get_avg_latency(cls):
        return cls.total_latency / cls.hits if cls.hits > 0 else 0
    
    @classmethod
    def report(cls):
        hit_rate = cls.get_hit_rate() * 100
        return {
            "hits": cls.hits,
            "misses": cls.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "avg_latency_ms": f"{cls.get_avg_latency() * 1000:.2f}"
        }

def cached(ttl=3600):
    """Decorator with metrics tracking"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Try cache
            start = time.time()
            cached_value = redis_client.get(cache_key)
            cache_latency = time.time() - start
            
            if cached_value:
                CacheMetrics.record_hit(cache_latency)
                return json.loads(cached_value)
            
            # Cache miss
            CacheMetrics.record_miss()
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=3600)
def get_product(product_id):
    return db.query(Product).get(product_id)

# Check metrics
print(CacheMetrics.report())
# {
#   "hits": 8500,
#   "misses": 1500,
#   "hit_rate": "85.00%",
#   "avg_latency_ms": "0.52"
# }
```

**Prometheus Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Cache metrics for Prometheus
cache_hits = Counter('cache_hits_total', 'Total cache hits', ['cache_name'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['cache_name'])
cache_latency = Histogram('cache_latency_seconds', 'Cache operation latency', ['cache_name'])
cache_size = Gauge('cache_size_bytes', 'Current cache size', ['cache_name'])

def get_cached_user(user_id):
    cache_name = "user_cache"
    cache_key = f"user:{user_id}"
    
    with cache_latency.labels(cache_name).time():
        cached = redis_client.get(cache_key)
    
    if cached:
        cache_hits.labels(cache_name).inc()
        return json.loads(cached)
    
    cache_misses.labels(cache_name).inc()
    
    # Fetch and cache
    user = db.query(User).get(user_id)
    redis_client.setex(cache_key, 3600, json.dumps(user.to_dict()))
    
    return user

# Track cache size
def update_cache_size():
    info = redis_client.info('memory')
    cache_size.labels('redis').set(info['used_memory'])
```

**Cache Health Dashboard:**

```python
def cache_health_check():
    """Generate cache health report"""
    info = redis_client.info()
    
    # Calculate hit rate
    keyspace = info.get('keyspace', {})
    hits = info.get('keyspace_hits', 0)
    misses = info.get('keyspace_misses', 0)
    total = hits + misses
    hit_rate = (hits / total * 100) if total > 0 else 0
    
    # Memory usage
    used_memory_mb = info['used_memory'] / (1024 * 1024)
    max_memory_mb = info.get('maxmemory', 0) / (1024 * 1024)
    memory_usage_pct = (used_memory_mb / max_memory_mb * 100) if max_memory_mb > 0 else 0
    
    # Evictions (cache full, keys removed)
    evicted_keys = info.get('evicted_keys', 0)
    
    # Connections
    connected_clients = info.get('connected_clients', 0)
    
    return {
        "status": "healthy" if hit_rate > 70 else "warning",
        "hit_rate": f"{hit_rate:.2f}%",
        "memory_used_mb": f"{used_memory_mb:.2f}",
        "memory_usage_pct": f"{memory_usage_pct:.2f}%",
        "evicted_keys": evicted_keys,
        "connected_clients": connected_clients,
        "total_keys": sum(keyspace.values()) if keyspace else 0
    }

# Example output:
# {
#   "status": "healthy",
#   "hit_rate": "87.50%",
#   "memory_used_mb": "245.32",
#   "memory_usage_pct": "24.53%",
#   "evicted_keys": 0,
#   "connected_clients": 12,
#   "total_keys": 15234
# }
```

**Alerting Thresholds:**

```python
# Configure alerts for cache health

ALERT_THRESHOLDS = {
    "hit_rate_min": 70,          # Alert if < 70%
    "memory_usage_max": 90,      # Alert if > 90%
    "evictions_per_sec_max": 10, # Alert if > 10/sec
    "latency_p99_max_ms": 5,     # Alert if p99 > 5ms
}

def check_cache_alerts():
    health = cache_health_check()
    alerts = []
    
    if float(health["hit_rate"].rstrip('%')) < ALERT_THRESHOLDS["hit_rate_min"]:
        alerts.append({
            "severity": "warning",
            "message": f"Low cache hit rate: {health['hit_rate']}"
        })
    
    if float(health["memory_usage_pct"].rstrip('%')) > ALERT_THRESHOLDS["memory_usage_max"]:
        alerts.append({
            "severity": "critical",
            "message": f"High memory usage: {health['memory_usage_pct']}"
        })
    
    if health["evicted_keys"] > ALERT_THRESHOLDS["evictions_per_sec_max"]:
        alerts.append({
            "severity": "warning",
            "message": f"High eviction rate: {health['evicted_keys']} keys/sec"
        })
    
    return alerts
```

**Verification:**
- [ ] Cache hit/miss metrics tracked
- [ ] Latency metrics monitored
- [ ] Memory usage monitored
- [ ] Dashboard created for cache health
- [ ] Alerts configured for anomalies
- [ ] Metrics exported to monitoring system

**If This Fails:**
→ Start with Redis INFO command for basic metrics
→ Use Redis MONITOR (dev only) to watch operations
→ Add simple logging before full monitoring

---

## Verification Checklist

After completing this workflow:

- [ ] Access patterns analyzed and documented
- [ ] Cacheable data identified
- [ ] Caching technology selected (Redis recommended)
- [ ] Cache key naming convention established
- [ ] TTL values determined for each data type
- [ ] Cache invalidation strategy implemented
- [ ] Monitoring and metrics in place
- [ ] Cache hit rate > 70% (target)
- [ ] Latency reduced significantly (80%+ improvement)
- [ ] Documentation updated with caching strategy

---

## Common Issues & Solutions

### Issue: Low cache hit rate (<50%)

**Symptoms:**
- Cache metrics show < 50% hit rate
- Database load not reduced significantly
- Cache not providing expected performance improvement

**Solution:**
```python
# Diagnose low hit rate causes

def diagnose_low_hit_rate():
    """Identify why cache hit rate is low"""
    issues = []
    
    # Check 1: Are TTLs too short?
    sample_keys = redis_client.keys("*")[:100]
    ttls = [redis_client.ttl(key) for key in sample_keys]
    avg_ttl = sum(t for t in ttls if t > 0) / len([t for t in ttls if t > 0])
    
    if avg_ttl < 300:  # Less than 5 minutes
        issues.append("TTLs are very short, data expires quickly")
    
    # Check 2: Are keys being accessed multiple times?
    # (This requires tracking, see adaptive_ttl example)
    
    # Check 3: Is cache size too small (evictions)?
    info = redis_client.info()
    evicted = info.get('evicted_keys', 0)
    
    if evicted > 1000:
        issues.append(f"High evictions: {evicted} keys evicted (cache too small)")
    
    # Check 4: Are cache keys consistent?
    # Look for similar but different keys (sign of poor key design)
    
    return issues

# Fix strategies:
# 1. Increase TTL for stable data
# 2. Increase cache memory (scale up Redis)
# 3. Improve cache key consistency
# 4. Pre-warm cache with popular items
```

**Prevention:**
- Monitor hit rate from day one
- Set realistic hit rate targets (70-90%)
- Pre-warm cache with popular items
- Use appropriate TTLs (not too short)

---

### Issue: Cache grows too large (memory exhaustion)

**Symptoms:**
- Redis OOM errors
- Keys being evicted frequently
- Performance degradation
- Application errors due to cache unavailable

**Solution:**
```python
# Configure Redis eviction policy

# redis.conf or runtime config
"""
maxmemory 2gb
maxmemory-policy allkeys-lru

Eviction policies:
- noeviction: Return error when memory limit reached (default)
- allkeys-lru: Evict least recently used keys
- allkeys-lfu: Evict least frequently used keys  
- volatile-lru: Evict LRU keys with TTL set
- volatile-lfu: Evict LFU keys with TTL set
- volatile-ttl: Evict keys with shortest TTL
- allkeys-random: Evict random keys
- volatile-random: Evict random keys with TTL
"""

# Set policy programmatically
redis_client.config_set('maxmemory', '2gb')
redis_client.config_set('maxmemory-policy', 'allkeys-lru')

# Monitor cache size and set alerts
def monitor_cache_size():
    info = redis_client.info('memory')
    used_mb = info['used_memory'] / (1024 * 1024)
    max_mb = info.get('maxmemory', 0) / (1024 * 1024)
    
    if max_mb > 0:
        usage_pct = used_mb / max_mb * 100
        
        if usage_pct > 90:
            logger.warning(f"Cache nearly full: {usage_pct:.1f}%")
        
        return usage_pct
    
    return 0
```

**Prevention:**
- Set reasonable maxmemory limit
- Configure appropriate eviction policy
- Monitor memory usage with alerts
- Use TTLs to expire old data
- Scale Redis vertically or horizontally

---

### Issue: Thundering herd on cache expiration

**Symptoms:**
- Periodic database spikes
- Multiple requests fetching same data simultaneously
- Cache stampede when popular items expire

**Solution:**
```python
# Solution 1: Add jitter to TTL (done in Step 4)

# Solution 2: Use cache locking
import threading

cache_locks = {}
lock_mutex = threading.Lock()

def get_with_lock(cache_key, fetch_func, ttl=3600):
    """Prevent multiple simultaneous fetches of same data"""
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Get or create lock for this key
    with lock_mutex:
        if cache_key not in cache_locks:
            cache_locks[cache_key] = threading.Lock()
        lock = cache_locks[cache_key]
    
    # Try to acquire lock
    acquired = lock.acquire(blocking=False)
    
    if acquired:
        try:
            # Double-check cache (might have been filled while waiting)
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Fetch data
            data = fetch_func()
            
            # Cache it
            redis_client.setex(cache_key, ttl, json.dumps(data))
            
            return data
        finally:
            lock.release()
            with lock_mutex:
                del cache_locks[cache_key]
    else:
        # Another thread is fetching, wait briefly and retry
        time.sleep(0.1)
        return get_with_lock(cache_key, fetch_func, ttl)

# Solution 3: Probabilistic early expiration
import random

def get_with_early_recompute(cache_key, fetch_func, ttl=3600):
    """Probabilistically refresh cache before expiration"""
    
    cached = redis_client.get(cache_key)
    if cached:
        # Check TTL
        remaining_ttl = redis_client.ttl(cache_key)
        
        # If close to expiration, randomly trigger refresh
        if remaining_ttl < ttl * 0.1:  # Last 10% of TTL
            # 50% chance to refresh early
            if random.random() < 0.5:
                data = fetch_func()
                redis_client.setex(cache_key, ttl, json.dumps(data))
                return data
        
        return json.loads(cached)
    
    # Cache miss, fetch normally
    data = fetch_func()
    redis_client.setex(cache_key, ttl, json.dumps(data))
    return data
```

**Prevention:**
- Add jitter to TTLs (10-20%)
- Use cache locking for expensive operations
- Implement probabilistic early expiration
- Stagger cache warming for popular items

---

## Examples

### Example 1: E-commerce Product Catalog Caching

**Context:** Cache product catalog to reduce database load

**Implementation:**
```python
class ProductCatalogCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_product(self, product_id):
        """Get product with caching"""
        cache_key = f"product:{product_id}"
        
        # Try cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Cache miss - fetch from database
        product = db.query(Product).get(product_id)
        if not product:
            return None
        
        # Cache for 4 hours (products change daily)
        self.redis.setex(
            cache_key,
            4 * 3600,
            json.dumps(product.to_dict())
        )
        
        return product.to_dict()
    
    def get_category_products(self, category, page=1, per_page=20):
        """Get products by category with pagination caching"""
        cache_key = f"category:{category}:page:{page}"
        
        # Try cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Fetch from database
        offset = (page - 1) * per_page
        products = db.query(Product).filter(
            Product.category == category
        ).offset(offset).limit(per_page).all()
        
        result = [p.to_dict() for p in products]
        
        # Cache for 1 hour
        self.redis.setex(cache_key, 3600, json.dumps(result))
        
        return result
    
    def invalidate_product(self, product_id):
        """Invalidate product and related caches"""
        # Delete product cache
        self.redis.delete(f"product:{product_id}")
        
        # Delete category caches (if product category changed)
        product = db.query(Product).get(product_id)
        if product:
            pattern = f"category:{product.category}:*"
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)

# Usage
cache = ProductCatalogCache()
product = cache.get_product(123)
products = cache.get_category_products("electronics", page=1)
```

**Result:**
- 95% cache hit rate
- Database queries reduced by 90%
- Page load time reduced from 500ms to 50ms

---

## Best Practices

### DO:
✅ Analyze access patterns before implementing cache
✅ Use consistent cache key naming (namespace:entity:id)
✅ Set appropriate TTLs based on data change frequency
✅ Add jitter to TTLs to prevent thundering herd
✅ Implement cache invalidation for critical data
✅ Monitor cache hit rate (target > 70%)
✅ Use Redis for general application caching
✅ Cache expensive operations (database queries, API calls)
✅ Use write-through cache for frequently updated data
✅ Configure maxmemory and eviction policy

### DON'T:
❌ Cache everything without analysis
❌ Use infinite TTLs without invalidation
❌ Ignore cache invalidation
❌ Hardcode cache keys (use key generators)
❌ Cache sensitive data without encryption
❌ Forget to monitor cache performance
❌ Use GET requests to modify cached data
❌ Cache data that changes every second
❌ Ignore cache memory limits
❌ Skip testing cache failures

---

## Related Workflows

**Prerequisites:**
- `arc-001`: API Design Best Practices - API response caching
- `devops-008`: Application Performance Monitoring - Cache monitoring

**Next Steps:**
- `arc-003`: Caching Strategy Implementation - Practical implementation
- `devops-012`: Performance Tuning - Performance optimization
- `devops-003`: CDN Setup - Static content caching

**Alternatives:**
- CDN for static content (CloudFront, Cloudflare)
- Database query cache (materialized views)
- Application-level in-memory cache (local cache)

---

## Tags
`architecture` `caching` `performance` `redis` `optimization` `scalability` `ttl` `cache-invalidation` `distributed-systems`
