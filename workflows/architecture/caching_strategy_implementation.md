# Caching Strategy Implementation

**ID:** arc-003  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement practical caching solutions in applications using Redis and modern frameworks

**Why:** Proper cache implementation reduces response times by 80-95%, enables 10x scale, and cuts infrastructure costs by 60% while maintaining data consistency

**When to use:**
- Implementing caching in existing applications
- Optimizing slow endpoints or queries
- Scaling systems to handle more traffic
- Building high-performance APIs
- Reducing cloud infrastructure costs

---

## Prerequisites

**Required:**
- [ ] Caching strategy defined (see arc-002)
- [ ] Redis or Memcached installed
- [ ] Application framework (FastAPI, Flask, Express, etc.)
- [ ] Monitoring tools configured
- [ ] Understanding of cache patterns

**Check before starting:**
```bash
# Verify Redis is running
redis-cli ping
# Should return: PONG

# Check Redis version
redis-cli INFO server | grep redis_version

# Test Python Redis client
python -c "import redis; r = redis.Redis(); print(r.ping())"

# Check application can connect
curl -s http://localhost:6379 || echo "Redis not accessible"
```

---

## Implementation Steps

### Step 1: Set Up Redis Infrastructure

**What:** Configure Redis for production use with connection pooling and resilience

**How:**

**Redis Installation:**

```bash
# Docker (recommended for development)
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes

# Verify
docker ps | grep redis
redis-cli ping

# Production: Use managed Redis
# AWS: ElastiCache for Redis
# Google Cloud: Memorystore
# Azure: Azure Cache for Redis
```

**Python Redis Client Setup:**

```python
# requirements.txt
redis==5.0.1
hiredis==2.3.2  # C parser for better performance

# config.py
import redis
from redis.connection import ConnectionPool
import os

# Configuration
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD'),
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'socket_keepalive': True,
    'health_check_interval': 30,
    'decode_responses': True,  # Auto-decode bytes to strings
    'max_connections': 50,  # Connection pool size
}

# Create connection pool (reuse connections)
redis_pool = ConnectionPool(**REDIS_CONFIG)

# Get Redis client
def get_redis_client():
    """Get Redis client from connection pool"""
    return redis.Redis(connection_pool=redis_pool)

# Test connection
try:
    client = get_redis_client()
    client.ping()
    print("✅ Redis connected successfully")
except redis.ConnectionError as e:
    print(f"❌ Redis connection failed: {e}")
    raise

# Singleton pattern for application-wide client
redis_client = get_redis_client()
```

**Node.js Redis Client Setup:**

```javascript
// package.json dependencies
// "redis": "^4.6.0"

// config/redis.js
const redis = require('redis');

const REDIS_CONFIG = {
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  db: process.env.REDIS_DB || 0,
  socket: {
    connectTimeout: 5000,
    keepAlive: 5000,
  },
  // Connection pool
  maxRetriesPerRequest: 3,
};

// Create client
const client = redis.createClient(REDIS_CONFIG);

// Error handling
client.on('error', (err) => {
  console.error('Redis Client Error:', err);
});

client.on('connect', () => {
  console.log('✅ Redis connected successfully');
});

// Connect
await client.connect();

module.exports = client;
```

**Redis Configuration (redis.conf):**

```conf
# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (for important cached data)
appendonly yes
appendfsync everysec

# Network
timeout 300
tcp-keepalive 300

# Performance
tcp-backlog 511
databases 16

# Security
requirepass your_secure_password_here
bind 127.0.0.1  # Only local connections (change for distributed)
```

**Verification:**
- [ ] Redis installed and running
- [ ] Connection pool configured
- [ ] Client library installed
- [ ] Test connection successful
- [ ] Error handling implemented
- [ ] Configuration externalized (env vars)

**If This Fails:**
→ Check firewall rules (port 6379)
→ Verify Redis is running: `systemctl status redis`
→ Test connection: `redis-cli -h localhost -p 6379 ping`
→ Check logs: `docker logs redis` or `/var/log/redis`

---

### Step 2: Implement Basic Caching Layer

**What:** Create reusable caching utilities and decorators

**How:**

**Cache Utility Class:**

```python
# utils/cache.py
import json
import hashlib
from functools import wraps
from typing import Any, Optional, Callable
import redis
from datetime import timedelta

class CacheManager:
    """Centralized cache management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except redis.RedisError as e:
            # Log error but don't fail application
            print(f"Cache GET error for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized = json.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except (redis.RedisError, TypeError) as e:
            print(f"Cache SET error for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return self.redis.delete(key) > 0
        except redis.RedisError as e:
            print(f"Cache DELETE error for {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = list(self.redis.scan_iter(match=pattern))
            if keys:
                return self.redis.delete(*keys)
            return 0
        except redis.RedisError as e:
            print(f"Cache DELETE_PATTERN error for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.redis.exists(key) > 0
        except redis.RedisError as e:
            print(f"Cache EXISTS error for {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get remaining TTL for key (-1 if no TTL, -2 if doesn't exist)"""
        try:
            return self.redis.ttl(key)
        except redis.RedisError as e:
            print(f"Cache TTL error for {key}: {e}")
            return -2
    
    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Increment counter (useful for rate limiting)"""
        try:
            pipe = self.redis.pipeline()
            pipe.incr(key, amount)
            if ttl:
                pipe.expire(key, ttl)
            result = pipe.execute()
            return result[0]
        except redis.RedisError as e:
            print(f"Cache INCREMENT error for {key}: {e}")
            return 0

# Create singleton
cache = CacheManager(redis_client)
```

**Caching Decorator:**

```python
# decorators/cache.py
from functools import wraps
import hashlib
import json
from typing import Callable, Optional

def cache_result(ttl: int = 3600, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Optional custom key prefix
    
    Usage:
        @cache_result(ttl=3600, key_prefix='user')
        def get_user(user_id: int):
            return db.query(User).get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            prefix = key_prefix or func.__name__
            
            # Create stable hash from arguments
            args_str = json.dumps({
                'args': args,
                'kwargs': {k: v for k, v in sorted(kwargs.items())}
            }, sort_keys=True)
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            
            cache_key = f"{prefix}:{args_hash}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Cache miss - execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
        
        # Add method to invalidate this cached function
        def invalidate(*args, **kwargs):
            prefix = key_prefix or func.__name__
            args_str = json.dumps({
                'args': args,
                'kwargs': {k: v for k, v in sorted(kwargs.items())}
            }, sort_keys=True)
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            cache_key = f"{prefix}:{args_hash}"
            return cache.delete(cache_key)
        
        wrapper.invalidate = invalidate
        return wrapper
    
    return decorator

# Usage examples
@cache_result(ttl=3600, key_prefix='user')
def get_user(user_id: int):
    """Get user with 1 hour cache"""
    return db.query(User).filter_by(id=user_id).first()

@cache_result(ttl=600, key_prefix='search')
def search_products(query: str, category: str = None):
    """Search products with 10 minute cache"""
    q = db.query(Product).filter(Product.name.contains(query))
    if category:
        q = q.filter_by(category=category)
    return q.all()

# Invalidate cache when data changes
def update_user(user_id: int, data: dict):
    user = db.query(User).get(user_id)
    user.update(data)
    db.commit()
    
    # Invalidate cached user
    get_user.invalidate(user_id)
    
    return user
```

**Context Manager for Cache:**

```python
# context_managers.py
from contextlib import contextmanager

@contextmanager
def cache_context(key: str, ttl: int = 3600):
    """
    Context manager for caching
    
    Usage:
        with cache_context('expensive_operation', ttl=3600) as ctx:
            if ctx.cached:
                return ctx.value
            
            # Do expensive operation
            result = expensive_computation()
            ctx.value = result
        
        # Result is automatically cached
        return result
    """
    class CacheContext:
        def __init__(self, key, ttl):
            self.key = key
            self.ttl = ttl
            self.value = cache.get(key)
            self.cached = self.value is not None
            self._new_value = None
        
        @property
        def value(self):
            return self._new_value if self._new_value is not None else self.value
        
        @value.setter
        def value(self, val):
            self._new_value = val
    
    ctx = CacheContext(key, ttl)
    
    try:
        yield ctx
    finally:
        # Save new value if set
        if ctx._new_value is not None:
            cache.set(key, ctx._new_value, ttl)
```

**Verification:**
- [ ] CacheManager class implemented
- [ ] cache_result decorator working
- [ ] Error handling prevents cache failures from breaking app
- [ ] Cache keys generated consistently
- [ ] Invalidation methods available

**If This Fails:**
→ Test CacheManager methods individually
→ Verify Redis connection before using cache
→ Add logging to debug cache misses
→ Start with simple get/set before decorators

---

### Step 3: Implement Caching in FastAPI Application

**What:** Add caching to FastAPI endpoints for immediate performance gains

**How:**

**FastAPI with Caching:**

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import time

app = FastAPI(title="Cached API")

# Models
class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float

# Cache TTL constants
class CacheTTL:
    USER = 3600          # 1 hour
    PRODUCT = 14400      # 4 hours
    SEARCH = 600         # 10 minutes
    LIST = 1800          # 30 minutes

# Endpoint with caching
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user with caching"""
    cache_key = f"user:{user_id}"
    
    # Try cache
    cached_user = cache.get(cache_key)
    if cached_user:
        return cached_user
    
    # Cache miss - fetch from database
    user = db.query(UserModel).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_dict = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }
    
    # Cache result
    cache.set(cache_key, user_dict, CacheTTL.USER)
    
    return user_dict

# List endpoint with pagination caching
@app.get("/products", response_model=List[Product])
async def list_products(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """List products with caching"""
    # Cache key includes pagination params
    cache_key = f"products:category:{category or 'all'}:page:{page}:per_page:{per_page}"
    
    # Try cache
    cached_products = cache.get(cache_key)
    if cached_products:
        return cached_products
    
    # Fetch from database
    query = db.query(ProductModel)
    if category:
        query = query.filter_by(category=category)
    
    offset = (page - 1) * per_page
    products = query.offset(offset).limit(per_page).all()
    
    products_list = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "price": float(p.price)
        }
        for p in products
    ]
    
    # Cache result
    cache.set(cache_key, products_list, CacheTTL.PRODUCT)
    
    return products_list

# POST endpoint with cache invalidation
@app.post("/users", response_model=User, status_code=201)
async def create_user(user_data: dict):
    """Create user and invalidate related caches"""
    # Create user
    user = UserModel(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Note: Don't cache POST responses (they create new data)
    # But invalidate related caches if needed
    cache.delete_pattern("users:list:*")  # Invalidate user lists
    
    return user

# PATCH endpoint with cache invalidation
@app.patch("/users/{user_id}", response_model=User)
async def update_user(user_id: int, updates: dict):
    """Update user and invalidate cache"""
    user = db.query(UserModel).get(user_id)
    if not user:
        raise HTTPException(status_code=404)
    
    # Update user
    for key, value in updates.items():
        setattr(user, key, value)
    db.commit()
    
    # Invalidate user cache
    cache_key = f"user:{user_id}"
    cache.delete(cache_key)
    
    # Also invalidate user lists
    cache.delete_pattern("users:list:*")
    
    return user

# Search endpoint with short TTL
@app.get("/search", response_model=List[Product])
async def search_products(q: str = Query(..., min_length=1)):
    """Search products with short-lived cache"""
    import hashlib
    
    # Hash query for cache key (queries can be long)
    query_hash = hashlib.md5(q.encode()).hexdigest()[:8]
    cache_key = f"search:{query_hash}"
    
    # Try cache
    cached_results = cache.get(cache_key)
    if cached_results:
        return cached_results
    
    # Search database
    products = db.query(ProductModel).filter(
        ProductModel.name.contains(q)
    ).limit(50).all()
    
    results = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "price": float(p.price)
        }
        for p in products
    ]
    
    # Cache with short TTL (search results change frequently)
    cache.set(cache_key, results, CacheTTL.SEARCH)
    
    return results
```

**Caching Middleware:**

```python
# middleware/cache_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
import json

class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware to cache GET requests automatically"""
    
    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Generate cache key from URL and query params
        cache_key = self._generate_cache_key(request)
        
        # Try cache
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(
                content=cached_response['body'],
                status_code=cached_response['status_code'],
                headers=cached_response['headers'],
                media_type=cached_response['media_type']
            )
        
        # Execute request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Store in cache
            cache_data = {
                'body': body.decode(),
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'media_type': response.media_type
            }
            cache.set(cache_key, cache_data, ttl=300)  # 5 minutes
            
            # Return response
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request"""
        url = str(request.url)
        hash_key = hashlib.md5(url.encode()).hexdigest()
        return f"http_cache:{hash_key}"

# Add to FastAPI app
app.add_middleware(CacheMiddleware)
```

**Verification:**
- [ ] GET endpoints return cached responses
- [ ] Cache hits improve response time significantly
- [ ] POST/PUT/PATCH invalidate related caches
- [ ] Search results cached with appropriate TTL
- [ ] Pagination cached correctly
- [ ] Cache middleware working (if used)

**If This Fails:**
→ Test endpoints without cache first
→ Add logging to see cache hits/misses
→ Verify cache keys are being generated
→ Check Redis has data: `redis-cli KEYS "*"`

---

### Step 4: Implement Advanced Caching Patterns

**What:** Add sophisticated caching patterns for complex use cases

**How:**

**Pattern 1: Cache-Aside with Locking (Prevent Stampede):**

```python
import threading
from contextlib import contextmanager

class CacheWithLock:
    """Cache-aside pattern with locking to prevent thundering herd"""
    
    def __init__(self):
        self.locks = {}
        self.lock_mutex = threading.Lock()
    
    @contextmanager
    def lock_key(self, key: str):
        """Get or create lock for key"""
        with self.lock_mutex:
            if key not in self.locks:
                self.locks[key] = threading.Lock()
            lock = self.locks[key]
        
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
            with self.lock_mutex:
                if key in self.locks:
                    del self.locks[key]
    
    def get_or_compute(self, key: str, compute_func, ttl: int = 3600):
        """
        Get from cache or compute with locking
        Only one thread computes at a time per key
        """
        # Try cache first
        cached = cache.get(key)
        if cached is not None:
            return cached
        
        # Need to compute - acquire lock
        with self.lock_key(key):
            # Double-check cache (might have been filled while waiting)
            cached = cache.get(key)
            if cached is not None:
                return cached
            
            # Compute value
            result = compute_func()
            
            # Store in cache
            cache.set(key, result, ttl)
            
            return result

# Usage
cache_with_lock = CacheWithLock()

def expensive_operation(user_id):
    # Expensive database query or API call
    time.sleep(2)  # Simulate slow operation
    return db.query(User).get(user_id)

# Multiple requests for same data won't all hit database
result = cache_with_lock.get_or_compute(
    f"user:{user_id}",
    lambda: expensive_operation(user_id),
    ttl=3600
)
```

**Pattern 2: Proactive Cache Warming:**

```python
from apscheduler.schedulers.background import BackgroundScheduler

class CacheWarmer:
    """Proactively warm cache with popular items"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def warm_popular_products(self):
        """Pre-load popular products into cache"""
        # Get list of popular product IDs
        popular_ids = db.query(Product.id).filter(
            Product.is_popular == True
        ).limit(100).all()
        
        for (product_id,) in popular_ids:
            cache_key = f"product:{product_id}"
            
            # Skip if already cached
            if cache.exists(cache_key):
                continue
            
            # Load into cache
            product = db.query(Product).get(product_id)
            if product:
                cache.set(
                    cache_key,
                    product.to_dict(),
                    CacheTTL.PRODUCT
                )
        
        print(f"Warmed cache with {len(popular_ids)} products")
    
    def warm_user_sessions(self):
        """Pre-load active user sessions"""
        # Get active user IDs from last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        active_users = db.query(User.id).filter(
            User.last_active > one_hour_ago
        ).all()
        
        for (user_id,) in active_users:
            cache_key = f"user:{user_id}"
            
            if not cache.exists(cache_key):
                user = db.query(User).get(user_id)
                if user:
                    cache.set(cache_key, user.to_dict(), CacheTTL.USER)
        
        print(f"Warmed cache with {len(active_users)} user sessions")
    
    def start(self):
        """Start scheduled cache warming"""
        # Warm popular products every 30 minutes
        self.scheduler.add_job(
            self.warm_popular_products,
            'interval',
            minutes=30
        )
        
        # Warm user sessions every 15 minutes
        self.scheduler.add_job(
            self.warm_user_sessions,
            'interval',
            minutes=15
        )
        
        self.scheduler.start()
        print("Cache warmer started")

# Start on application startup
warmer = CacheWarmer()
warmer.start()
```

**Pattern 3: Multi-Layer Caching:**

```python
class MultiLayerCache:
    """Two-layer cache: In-memory + Redis"""
    
    def __init__(self, redis_client, local_cache_size=1000):
        self.redis = redis_client
        # Local in-memory cache (LRU)
        from cachetools import LRUCache
        self.local_cache = LRUCache(maxsize=local_cache_size)
    
    def get(self, key: str):
        """Try local cache, then Redis"""
        # L1: Local cache (fastest)
        if key in self.local_cache:
            return self.local_cache[key]
        
        # L2: Redis cache
        cached = cache.get(key)
        if cached:
            # Promote to local cache
            self.local_cache[key] = cached
            return cached
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set in both local and Redis cache"""
        # Store in both layers
        self.local_cache[key] = value
        cache.set(key, value, ttl)
    
    def delete(self, key: str):
        """Delete from both layers"""
        if key in self.local_cache:
            del self.local_cache[key]
        cache.delete(key)

# Usage
multi_cache = MultiLayerCache(redis_client, local_cache_size=1000)

def get_product(product_id):
    key = f"product:{product_id}"
    
    # Check multi-layer cache
    cached = multi_cache.get(key)
    if cached:
        return cached
    
    # Fetch from database
    product = db.query(Product).get(product_id)
    if product:
        multi_cache.set(key, product.to_dict(), CacheTTL.PRODUCT)
    
    return product.to_dict() if product else None
```

**Pattern 4: Write-Through Cache:**

```python
class WriteThroughCache:
    """Write to cache and database simultaneously"""
    
    def update_user(self, user_id: int, data: dict):
        """Update user with write-through caching"""
        # Update database
        user = db.query(User).get(user_id)
        if not user:
            return None
        
        user.update(data)
        db.commit()
        db.refresh(user)
        
        # Update cache immediately with fresh data
        cache_key = f"user:{user_id}"
        cache.set(cache_key, user.to_dict(), CacheTTL.USER)
        
        return user
    
    def create_product(self, product_data: dict):
        """Create product and cache it"""
        # Create in database
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Store in cache
        cache_key = f"product:{product.id}"
        cache.set(cache_key, product.to_dict(), CacheTTL.PRODUCT)
        
        return product
```

**Pattern 5: Read-Through Cache:**

```python
class ReadThroughCache:
    """Cache automatically fetches from database on miss"""
    
    def __init__(self, fetch_func, cache_key_func, ttl=3600):
        self.fetch_func = fetch_func
        self.cache_key_func = cache_key_func
        self.ttl = ttl
    
    def get(self, *args, **kwargs):
        """Get with automatic fetch on cache miss"""
        # Generate cache key
        cache_key = self.cache_key_func(*args, **kwargs)
        
        # Try cache
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Cache miss - fetch from source
        data = self.fetch_func(*args, **kwargs)
        
        # Store in cache
        if data:
            cache.set(cache_key, data, self.ttl)
        
        return data

# Usage
def fetch_user_from_db(user_id):
    user = db.query(User).get(user_id)
    return user.to_dict() if user else None

def user_cache_key(user_id):
    return f"user:{user_id}"

user_cache = ReadThroughCache(
    fetch_func=fetch_user_from_db,
    cache_key_func=user_cache_key,
    ttl=CacheTTL.USER
)

# Simple API - cache is transparent
user = user_cache.get(user_id=123)
```

**Verification:**
- [ ] Locking prevents cache stampede
- [ ] Cache warming reduces cold start latency
- [ ] Multi-layer cache improves performance further
- [ ] Write-through keeps cache consistent
- [ ] Read-through simplifies cache logic

**If This Fails:**
→ Start with simple cache-aside pattern
→ Add locking only for expensive operations
→ Implement warming only for critical paths

---

### Step 5: Add Cache Monitoring and Metrics

**What:** Track cache performance and health in production

**How:**

**Prometheus Metrics Integration:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

cache_latency = Histogram(
    'cache_latency_seconds',
    'Cache operation latency',
    ['cache_name', 'operation']
)

cache_size_bytes = Gauge(
    'cache_size_bytes',
    'Current cache size in bytes'
)

# Instrumented cache operations
class InstrumentedCache:
    """Cache with Prometheus metrics"""
    
    def __init__(self, cache_name='default'):
        self.cache_name = cache_name
    
    def get(self, key: str):
        with cache_latency.labels(self.cache_name, 'get').time():
            result = cache.get(key)
        
        if result:
            cache_hits.labels(self.cache_name).inc()
        else:
            cache_misses.labels(self.cache_name).inc()
        
        return result
    
    def set(self, key: str, value: Any, ttl: int):
        with cache_latency.labels(self.cache_name, 'set').time():
            return cache.set(key, value, ttl)
    
    def update_size_metric(self):
        """Update cache size gauge"""
        info = redis_client.info('memory')
        cache_size_bytes.set(info['used_memory'])

# Use instrumented cache
product_cache = InstrumentedCache('product_cache')
user_cache = InstrumentedCache('user_cache')
```

**Cache Health Dashboard:**

```python
from fastapi import APIRouter

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    info = redis_client.info()
    stats = redis_client.info('stats')
    
    # Calculate hit rate
    hits = stats.get('keyspace_hits', 0)
    misses = stats.get('keyspace_misses', 0)
    total = hits + misses
    hit_rate = (hits / total * 100) if total > 0 else 0
    
    # Memory usage
    memory_info = redis_client.info('memory')
    used_mb = memory_info['used_memory'] / (1024 * 1024)
    max_mb = memory_info.get('maxmemory', 0) / (1024 * 1024)
    
    # Key statistics
    keyspace = info.get('db0', {})
    total_keys = keyspace.get('keys', 0) if keyspace else 0
    
    return {
        "status": "healthy" if hit_rate > 70 else "warning",
        "hit_rate": f"{hit_rate:.2f}%",
        "total_hits": hits,
        "total_misses": misses,
        "memory_used_mb": f"{used_mb:.2f}",
        "memory_max_mb": f"{max_mb:.2f}",
        "total_keys": total_keys,
        "connected_clients": info.get('connected_clients', 0),
        "uptime_days": info.get('uptime_in_days', 0)
    }

@admin_router.get("/cache/keys")
async def cache_keys(pattern: str = "*", limit: int = 100):
    """List cache keys (for debugging)"""
    keys = []
    for key in redis_client.scan_iter(match=pattern, count=limit):
        ttl = redis_client.ttl(key)
        keys.append({
            "key": key,
            "ttl": ttl if ttl >= 0 else "no expiry"
        })
        if len(keys) >= limit:
            break
    
    return {"keys": keys, "count": len(keys)}

@admin_router.delete("/cache/flush")
async def flush_cache(pattern: str = None):
    """Flush cache (use with caution!)"""
    if pattern:
        deleted = cache.delete_pattern(pattern)
        return {"deleted": deleted, "pattern": pattern}
    else:
        redis_client.flushdb()
        return {"status": "all keys deleted"}

app.include_router(admin_router)
```

**Logging Cache Operations:**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
cache_logger = logging.getLogger('cache')

class LoggingCache:
    """Cache with detailed logging"""
    
    def get(self, key: str):
        result = cache.get(key)
        
        if result:
            cache_logger.debug(f"Cache HIT: {key}")
        else:
            cache_logger.debug(f"Cache MISS: {key}")
        
        return result
    
    def set(self, key: str, value: Any, ttl: int):
        cache_logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
        return cache.set(key, value, ttl)
    
    def delete(self, key: str):
        cache_logger.info(f"Cache DELETE: {key}")
        return cache.delete(key)

# Use in production with appropriate log level
logging_cache = LoggingCache()
```

**Verification:**
- [ ] Prometheus metrics exported
- [ ] Cache stats endpoint working
- [ ] Hit rate calculated correctly
- [ ] Memory usage tracked
- [ ] Logs show cache operations
- [ ] Dashboard shows cache health

**If This Fails:**
→ Start with basic Redis INFO command
→ Add simple hit/miss counters
→ Use Redis MONITOR (dev only) to watch operations

---

## Verification Checklist

After completing this workflow:

- [ ] Redis installed and configured
- [ ] Connection pool working
- [ ] Basic caching utilities implemented
- [ ] Caching decorators working
- [ ] FastAPI endpoints cached
- [ ] Cache invalidation on updates
- [ ] Advanced patterns implemented (if needed)
- [ ] Monitoring and metrics active
- [ ] Cache hit rate > 70%
- [ ] Response times improved by 80%+
- [ ] Documentation updated

---

## Common Issues & Solutions

### Issue: Cache connection failures break application

**Symptoms:**
- Application crashes when Redis is down
- Errors thrown on every request
- No graceful degradation

**Solution:**
```python
class ResilientCache:
    """Cache that gracefully handles failures"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60
        )
    
    def get(self, key: str, default=None):
        """Get with graceful failure"""
        if self.circuit_breaker.is_open():
            logger.warning("Cache circuit breaker open, skipping cache")
            return default
        
        try:
            result = self.redis.get(key)
            self.circuit_breaker.record_success()
            return json.loads(result) if result else default
        except redis.RedisError as e:
            logger.error(f"Cache GET error: {e}")
            self.circuit_breaker.record_failure()
            return default
    
    def set(self, key: str, value: Any, ttl: int):
        """Set with graceful failure"""
        if self.circuit_breaker.is_open():
            return False
        
        try:
            serialized = json.dumps(value)
            result = self.redis.setex(key, ttl, serialized)
            self.circuit_breaker.record_success()
            return result
        except (redis.RedisError, TypeError) as e:
            logger.error(f"Cache SET error: {e}")
            self.circuit_breaker.record_failure()
            return False

class CircuitBreaker:
    """Simple circuit breaker for cache"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = 'open'
            logger.warning("Circuit breaker opened")
    
    def record_success(self):
        if self.state == 'half-open':
            self.state = 'closed'
            self.failures = 0
            logger.info("Circuit breaker closed")
    
    def is_open(self):
        if self.state == 'closed':
            return False
        
        # Try half-open after timeout
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
                logger.info("Circuit breaker half-open, trying cache")
                return False
        
        return True

# Use resilient cache
resilient_cache = ResilientCache(redis_client)
```

**Prevention:**
- Implement circuit breaker pattern
- Always have fallback to source data
- Use connection timeouts
- Monitor cache health

---

### Issue: Stale data in cache

**Symptoms:**
- Users see old data after updates
- Cache not invalidated properly
- Inconsistent state across instances

**Solution:**
```python
# Use Redis Pub/Sub for distributed cache invalidation

class DistributedCacheInvalidation:
    """Invalidate cache across multiple app instances"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('cache_invalidate')
        
        # Start listener thread
        import threading
        self.listener_thread = threading.Thread(
            target=self._listen_for_invalidations,
            daemon=True
        )
        self.listener_thread.start()
    
    def invalidate(self, key_pattern: str):
        """Publish invalidation event to all instances"""
        message = json.dumps({'pattern': key_pattern})
        self.redis.publish('cache_invalidate', message)
    
    def _listen_for_invalidations(self):
        """Listen for invalidation events"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                pattern = data['pattern']
                
                # Delete matching keys
                logger.info(f"Invalidating cache: {pattern}")
                cache.delete_pattern(pattern)

# Initialize on app startup
cache_invalidator = DistributedCacheInvalidation(redis_client)

# Use in update endpoints
def update_product(product_id: int, data: dict):
    product = db.query(Product).get(product_id)
    product.update(data)
    db.commit()
    
    # Invalidate across all instances
    cache_invalidator.invalidate(f"product:{product_id}")
    cache_invalidator.invalidate(f"products:category:{product.category}:*")
    
    return product
```

**Prevention:**
- Use pub/sub for distributed invalidation
- Implement versioning in cache keys
- Use shorter TTLs for frequently changing data
- Test cache invalidation in staging

---

## Best Practices

### DO:
✅ Use connection pooling for Redis
✅ Handle cache failures gracefully (fallback to database)
✅ Implement circuit breaker for cache resilience
✅ Monitor cache hit rate (target > 70%)
✅ Invalidate cache on updates
✅ Use appropriate TTLs for each data type
✅ Add jitter to TTLs to prevent thundering herd
✅ Use namespaced cache keys
✅ Log cache operations for debugging
✅ Warm cache with popular items

### DON'T:
❌ Let cache failures break your application
❌ Cache sensitive data without encryption
❌ Forget to invalidate related caches
❌ Use very short TTLs (<10s) for frequently accessed data
❌ Cache everything without analysis
❌ Hardcode cache keys
❌ Ignore cache memory limits
❌ Skip monitoring cache performance
❌ Cache data that changes every second
❌ Use GET requests to modify cached data

---

## Related Workflows

**Prerequisites:**
- `arc-002`: Caching Strategies - Strategy and patterns
- `devops-006`: Redis Setup - Infrastructure setup

**Next Steps:**
- `devops-008`: Application Performance Monitoring - Monitor cache
- `devops-012`: Performance Tuning - Optimize further
- `arc-004`: CDN Configuration - Add CDN layer

**Alternatives:**
- CDN for static content (Cloudflare, CloudFront)
- Application-level in-memory cache (local cache)
- Database query cache (materialized views)

---

## Tags
`architecture` `caching` `implementation` `redis` `performance` `optimization` `fastapi` `python` `nodejs`
