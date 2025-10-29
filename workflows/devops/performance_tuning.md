# Performance Tuning

**ID:** dvo-016  
**Category:** DevOps  
**Priority:** MEDIUM  
**Complexity:** Advanced  
**Estimated Time:** 120-180 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive guide for identifying performance bottlenecks and optimizing application and infrastructure performance across multiple layers (application, database, network, infrastructure).

**Why:** Performance tuning improves user experience, reduces infrastructure costs, increases application capacity, enables better scalability, and prevents production issues caused by slow responses or resource exhaustion.

**When to use:**
- Application response times exceeding SLA targets
- High resource utilization (CPU, memory, network)
- Slow database queries or transactions
- Preparing for increased traffic (launch, campaign, scale-up)
- Cost optimization through efficiency improvements
- After code changes that may impact performance
- Periodic performance review and optimization cycles

---

## Prerequisites

**Required:**
- [ ] Application deployed and accessible
- [ ] Monitoring and observability tools configured (APM, metrics, logs)
- [ ] Access to production metrics and logs
- [ ] Load testing tools available
- [ ] Database access for query analysis
- [ ] Understanding of application architecture and critical paths
- [ ] Performance baselines documented

**Recommended:**
- [ ] Profiling tools installed (py-spy, async-profiler, perf)
- [ ] Distributed tracing configured (Jaeger, Zipkin, X-Ray)
- [ ] CDN configured for static assets
- [ ] Caching layer available (Redis, Memcached)
- [ ] Performance testing environment (staging)

**Check before starting:**
```bash
# Verify monitoring is active
curl -I https://your-app.com/health
curl -I https://your-app.com/metrics

# Check if profiling tools are installed
python3 -m pip show py-spy  # Python
which async-profiler  # Java
which perf  # Linux

# Verify load testing tools
which ab hey wrk  # HTTP load testing
which locust  # Python load testing framework

# Check database performance monitoring
psql -c "SELECT * FROM pg_stat_statements LIMIT 1;"  # PostgreSQL
mysql -e "SELECT * FROM performance_schema.events_statements_summary_by_digest LIMIT 1;"  # MySQL

# Verify APM agent is running
ps aux | grep -i "newrelic\|datadog\|dynatrace"
```

---

## Implementation Steps

### Step 1: Establish Performance Baseline and Identify Bottlenecks

**What:** Measure current performance metrics, establish baselines, and identify the most impactful bottlenecks using profiling, monitoring, and distributed tracing tools.

**How:**

#### Establish Baseline Metrics

```python
# baseline_metrics.py
import time
import statistics
from dataclasses import dataclass
from typing import List
import requests

@dataclass
class PerformanceBaseline:
    """Store performance baseline measurements"""
    endpoint: str
    response_times: List[float]
    error_rate: float
    throughput_rps: float
    p50: float
    p95: float
    p99: float
    
    @classmethod
    def measure(cls, endpoint: str, num_requests: int = 100):
        """Measure baseline performance for an endpoint"""
        response_times = []
        errors = 0
        
        start_time = time.time()
        
        for _ in range(num_requests):
            try:
                req_start = time.time()
                response = requests.get(endpoint, timeout=30)
                req_time = time.time() - req_start
                
                response_times.append(req_time)
                
                if response.status_code >= 500:
                    errors += 1
            except Exception as e:
                errors += 1
                response_times.append(30.0)  # Timeout
        
        total_time = time.time() - start_time
        
        return cls(
            endpoint=endpoint,
            response_times=response_times,
            error_rate=errors / num_requests,
            throughput_rps=num_requests / total_time,
            p50=statistics.quantiles(response_times, n=100)[49],
            p95=statistics.quantiles(response_times, n=100)[94],
            p99=statistics.quantiles(response_times, n=100)[98]
        )
    
    def report(self):
        """Print performance baseline report"""
        print(f"\n📊 Performance Baseline: {self.endpoint}")
        print("=" * 60)
        print(f"Total Requests: {len(self.response_times)}")
        print(f"Error Rate: {self.error_rate * 100:.2f}%")
        print(f"Throughput: {self.throughput_rps:.2f} req/s")
        print(f"\nResponse Times:")
        print(f"  P50 (median): {self.p50 * 1000:.2f}ms")
        print(f"  P95: {self.p95 * 1000:.2f}ms")
        print(f"  P99: {self.p99 * 1000:.2f}ms")
        print(f"  Min: {min(self.response_times) * 1000:.2f}ms")
        print(f"  Max: {max(self.response_times) * 1000:.2f}ms")
        print(f"  Avg: {statistics.mean(self.response_times) * 1000:.2f}ms")

# Usage
baseline = PerformanceBaseline.measure('https://your-app.com/api/products')
baseline.report()

# Measure multiple endpoints
endpoints = [
    'https://your-app.com/',
    'https://your-app.com/api/products',
    'https://your-app.com/api/orders',
    'https://your-app.com/api/users/profile'
]

baselines = {ep: PerformanceBaseline.measure(ep) for ep in endpoints}

# Identify slowest endpoints
slowest = sorted(baselines.items(), key=lambda x: x[1].p95, reverse=True)
print("\n🐌 Slowest Endpoints (P95):")
for endpoint, baseline in slowest[:5]:
    print(f"  {baseline.p95 * 1000:.2f}ms - {endpoint}")
```

#### Application Profiling

```bash
# Python profiling with py-spy
pip install py-spy

# Profile running application
sudo py-spy record -o profile.svg --pid $(pgrep -f "python.*app")
# Wait 60 seconds, then view profile.svg in browser

# Live top-like view
sudo py-spy top --pid $(pgrep -f "python.*app")

# Sample specific duration
sudo py-spy record -o profile.svg --duration 60 --pid $(pgrep -f "python.*app")
```

**Python cProfile Integration:**
```python
# app.py - Add profiling middleware
import cProfile
import pstats
from io import StringIO
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def profile_request(request: Request, call_next):
    """Profile each request in development"""
    
    if request.query_params.get('profile') == '1':
        profiler = cProfile.Profile()
        profiler.enable()
        
        response = await call_next(request)
        
        profiler.disable()
        
        # Print stats
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(20)
        
        print(s.getvalue())
        
        return response
    
    return await call_next(request)

# Access with ?profile=1 to see profiling output
```

#### Database Query Analysis

```sql
-- PostgreSQL: Enable pg_stat_statements
-- In postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.track = all

-- Find slowest queries
SELECT 
    query,
    calls,
    total_exec_time / 1000 as total_time_sec,
    mean_exec_time / 1000 as mean_time_ms,
    max_exec_time / 1000 as max_time_ms,
    stddev_exec_time / 1000 as stddev_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Find most frequently called queries
SELECT 
    query,
    calls,
    mean_exec_time / 1000 as mean_time_ms
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;

-- Find queries with highest total time
SELECT 
    query,
    calls,
    total_exec_time / 1000 as total_time_sec,
    (total_exec_time / sum(total_exec_time) OVER ()) * 100 as pct_total
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

```sql
-- MySQL: Enable performance schema
-- In my.cnf:
-- performance_schema = ON

-- Find slowest queries
SELECT 
    DIGEST_TEXT as query,
    COUNT_STAR as exec_count,
    AVG_TIMER_WAIT/1000000000000 as avg_time_sec,
    MAX_TIMER_WAIT/1000000000000 as max_time_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 20;

-- Find queries with most rows examined
SELECT 
    DIGEST_TEXT as query,
    SUM_ROWS_EXAMINED as rows_examined,
    COUNT_STAR as exec_count
FROM performance_schema.events_statements_summary_by_digest
WHERE DIGEST_TEXT IS NOT NULL
ORDER BY SUM_ROWS_EXAMINED DESC
LIMIT 20;
```

#### Distributed Tracing Analysis

```python
# With OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument code
@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    with tracer.start_as_current_span("get_product") as span:
        span.set_attribute("product.id", product_id)
        
        # Database query
        with tracer.start_as_current_span("db.query"):
            product = await db.fetch_product(product_id)
        
        # External API call
        with tracer.start_as_current_span("api.pricing"):
            pricing = await fetch_pricing(product_id)
        
        # Cache check
        with tracer.start_as_current_span("cache.get"):
            cached = await redis.get(f"product:{product_id}")
        
        return product

# View traces in Jaeger UI at http://localhost:16686
# Identify spans taking the most time
```

**Verification:**
- [ ] Performance baselines documented for all critical endpoints
- [ ] Slowest endpoints identified (P95/P99 > target)
- [ ] Application profiling completed and flame graphs generated
- [ ] Slowest database queries identified
- [ ] Distributed traces analyzed for latency sources
- [ ] Bottlenecks prioritized by impact (frequency × slowness)

**If This Fails:**
→ Ensure monitoring and APM tools are properly configured
→ Verify profiling tools have necessary permissions (sudo for py-spy)
→ Check database performance schema is enabled
→ Use production-like data in staging for realistic profiling
→ Profile under realistic load, not idle systems

---

### Step 2: Optimize Application Code

**What:** Implement code-level optimizations based on profiling results, focusing on algorithmic improvements, reducing I/O operations, and eliminating unnecessary work.

**How:**

#### Common Optimization Patterns

**1. Reduce N+1 Query Problem:**

```python
# ❌ BAD: N+1 queries
async def get_users_with_posts():
    users = await db.fetch_all("SELECT * FROM users")
    
    for user in users:
        # This executes one query per user!
        user['posts'] = await db.fetch_all(
            "SELECT * FROM posts WHERE user_id = ?", user['id']
        )
    
    return users

# ✅ GOOD: Single query with JOIN or eager loading
async def get_users_with_posts():
    query = """
        SELECT 
            u.id, u.name, u.email,
            p.id as post_id, p.title, p.content
        FROM users u
        LEFT JOIN posts p ON p.user_id = u.id
    """
    rows = await db.fetch_all(query)
    
    # Group results
    users_dict = {}
    for row in rows:
        user_id = row['id']
        if user_id not in users_dict:
            users_dict[user_id] = {
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'posts': []
            }
        
        if row['post_id']:
            users_dict[user_id]['posts'].append({
                'id': row['post_id'],
                'title': row['title'],
                'content': row['content']
            })
    
    return list(users_dict.values())
```

**2. Implement Caching:**

```python
# Cache decorator
from functools import wraps
import redis
import json
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache(ttl=300):
    """Cache decorator with TTL"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )
            
            return result
        
        return wrapper
    return decorator

# Usage
@cache(ttl=600)  # Cache for 10 minutes
async def get_product(product_id: int):
    return await db.fetch_one(
        "SELECT * FROM products WHERE id = ?", product_id
    )
```

**3. Use Connection Pooling:**

```python
# Database connection pooling
from databases import Database

# ❌ BAD: New connection per query
async def get_user(user_id):
    db = await asyncpg.connect('postgresql://...')
    user = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    await db.close()
    return user

# ✅ GOOD: Connection pool
DATABASE_URL = "postgresql://user:pass@localhost/dbname"
database = Database(DATABASE_URL, min_size=10, max_size=50)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

async def get_user(user_id):
    return await database.fetch_one(
        "SELECT * FROM users WHERE id = :user_id",
        values={"user_id": user_id}
    )
```

**4. Async/Concurrent Processing:**

```python
import asyncio

# ❌ BAD: Sequential processing
async def process_orders(order_ids):
    results = []
    for order_id in order_ids:
        result = await process_order(order_id)  # Takes 1 second each
        results.append(result)
    return results  # Takes N seconds for N orders

# ✅ GOOD: Concurrent processing
async def process_orders(order_ids):
    # Process all orders concurrently
    tasks = [process_order(order_id) for order_id in order_ids]
    results = await asyncio.gather(*tasks)
    return results  # Takes ~1 second regardless of N

# ✅ BETTER: Concurrent with semaphore (limit concurrency)
async def process_orders(order_ids, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_process(order_id):
        async with semaphore:
            return await process_order(order_id)
    
    tasks = [limited_process(order_id) for order_id in order_ids]
    results = await asyncio.gather(*tasks)
    return results
```

**5. Lazy Loading and Pagination:**

```python
# ❌ BAD: Load all data
@app.get("/api/products")
async def get_products():
    products = await db.fetch_all("SELECT * FROM products")  # 10,000+ rows
    return products

# ✅ GOOD: Pagination
@app.get("/api/products")
async def get_products(page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    
    products = await db.fetch_all(
        "SELECT * FROM products ORDER BY id LIMIT ? OFFSET ?",
        page_size, offset
    )
    
    total = await db.fetch_val("SELECT COUNT(*) FROM products")
    
    return {
        'products': products,
        'page': page,
        'page_size': page_size,
        'total': total,
        'pages': (total + page_size - 1) // page_size
    }
```

**6. Optimize JSON Serialization:**

```python
# Use faster JSON library
import orjson  # Much faster than built-in json

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(default_response_class=ORJSONResponse)

@app.get("/api/products")
async def get_products():
    products = await db.fetch_all("SELECT * FROM products")
    # Automatically serialized with orjson (3-5x faster)
    return products
```

**7. Batch Operations:**

```python
# ❌ BAD: Individual inserts
async def create_users(users_data):
    for user in users_data:
        await db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            user['name'], user['email']
        )

# ✅ GOOD: Batch insert
async def create_users(users_data):
    values = [(user['name'], user['email']) for user in users_data]
    
    await db.execute_many(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        values
    )
```

#### Algorithmic Optimization

```python
# ❌ BAD: O(n²) complexity
def find_duplicates(items):
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other:
                duplicates.append(item)
    return duplicates

# ✅ GOOD: O(n) complexity with set
def find_duplicates(items):
    seen = set()
    duplicates = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    
    return list(duplicates)

# Performance difference:
# n=1000: 0.1s vs 50s (500x faster)
# n=10000: 1s vs 5000s (5000x faster)
```

**Verification:**
- [ ] N+1 queries eliminated
- [ ] Caching implemented for frequently accessed data
- [ ] Connection pooling configured
- [ ] Async processing for I/O-bound operations
- [ ] Pagination implemented for large datasets
- [ ] Batch operations for bulk data changes
- [ ] Algorithmic improvements (O(n²) → O(n))
- [ ] Performance improved by measured amount (e.g., 2x faster)

**If This Fails:**
→ Profile after each change to measure impact
→ Start with highest-impact changes (most frequently called code)
→ Ensure changes don't introduce bugs (add tests)
→ Monitor production metrics after deployment
→ Roll back if performance degrades

---

### Step 3: Optimize Database Performance

**What:** Tune database configuration, add appropriate indexes, optimize queries, and implement query caching to reduce database latency and improve throughput.

**How:**

#### Index Optimization

```sql
-- PostgreSQL: Find missing indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    AND n_distinct > 100
    AND correlation < 0.5
ORDER BY n_distinct DESC;

-- Find tables with sequential scans
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan as avg_seq_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;

-- Create indexes for common queries
-- Before: Sequential scan (slow)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- Create composite index
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- After: Index scan (fast)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- Partial index for common filters
CREATE INDEX idx_orders_pending ON orders(user_id) 
WHERE status = 'pending';

-- Index for sorting
CREATE INDEX idx_orders_created ON orders(created_at DESC);
```

#### Query Optimization

```sql
-- ❌ BAD: SELECT *
SELECT * FROM users WHERE email = 'user@example.com';

-- ✅ GOOD: Select only needed columns
SELECT id, name, email FROM users WHERE email = 'user@example.com';

-- ❌ BAD: Function in WHERE clause (can't use index)
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- ✅ GOOD: Use functional index or store lowercase
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
-- Or better: store email in lowercase

-- ❌ BAD: OR conditions (often can't use index efficiently)
SELECT * FROM products WHERE category = 'electronics' OR price < 100;

-- ✅ GOOD: Use UNION if selective
SELECT * FROM products WHERE category = 'electronics'
UNION
SELECT * FROM products WHERE price < 100;

-- ❌ BAD: Implicit type conversion
SELECT * FROM users WHERE id = '123';  -- id is integer

-- ✅ GOOD: Explicit types
SELECT * FROM users WHERE id = 123;

-- ❌ BAD: NOT IN with subquery (slow for large sets)
SELECT * FROM products WHERE id NOT IN (
    SELECT product_id FROM out_of_stock
);

-- ✅ GOOD: LEFT JOIN with NULL check
SELECT p.* 
FROM products p
LEFT JOIN out_of_stock o ON p.id = o.product_id
WHERE o.product_id IS NULL;

-- ❌ BAD: COUNT(*) on large tables
SELECT COUNT(*) FROM orders;  -- Scans entire table

-- ✅ GOOD: Approximate count for UI display
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'orders';

-- Or use with filter for better accuracy
SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '30 days';
```

#### Query Plan Analysis

```sql
-- Analyze query execution plan
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT 
    o.id,
    o.total,
    u.name,
    u.email
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.created_at > NOW() - INTERVAL '7 days'
    AND o.status = 'completed'
ORDER BY o.created_at DESC
LIMIT 100;

-- Look for:
-- 1. Sequential Scans → Add indexes
-- 2. High execution time → Optimize query
-- 3. High buffer usage → Needs more memory or better indexes
-- 4. Nested Loops with many rows → Consider hash join
```

#### Database Configuration Tuning

```bash
# PostgreSQL configuration (postgresql.conf)

# Memory settings
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM
work_mem = 50MB                   # Per operation memory
maintenance_work_mem = 1GB        # For VACUUM, CREATE INDEX

# Connection settings
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# Query planner
random_page_cost = 1.1           # SSD value (default 4.0 for HDD)
effective_io_concurrency = 200   # SSD value

# WAL settings
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 1GB

# Logging
log_min_duration_statement = 1000  # Log slow queries (>1s)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Autovacuum tuning
autovacuum_max_workers = 4
autovacuum_naptime = 10s
autovacuum_vacuum_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.02
```

#### Materialized Views for Complex Queries

```sql
-- Create materialized view for expensive aggregation
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT 
    DATE(created_at) as sale_date,
    COUNT(*) as order_count,
    SUM(total) as total_revenue,
    AVG(total) as avg_order_value
FROM orders
WHERE status = 'completed'
GROUP BY DATE(created_at);

-- Create index on materialized view
CREATE INDEX idx_daily_sales_date ON daily_sales_summary(sale_date);

-- Refresh periodically (use cron or trigger)
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales_summary;

-- Now queries are instant
SELECT * FROM daily_sales_summary 
WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days';
```

#### Read Replicas for Read-Heavy Workloads

```python
# Configure read replicas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Primary database (writes)
primary_engine = create_engine(
    'postgresql://user:pass@primary.db.internal:5432/mydb',
    pool_size=20,
    max_overflow=0
)

# Read replicas (reads)
replica_engines = [
    create_engine(f'postgresql://user:pass@replica{i}.db.internal:5432/mydb')
    for i in range(1, 4)
]

import random

def get_db_session(read_only=False):
    """Get database session, using replica for reads"""
    if read_only:
        engine = random.choice(replica_engines)
    else:
        engine = primary_engine
    
    Session = sessionmaker(bind=engine)
    return Session()

# Usage
@app.get("/api/products")
async def get_products():
    with get_db_session(read_only=True) as session:
        products = session.query(Product).all()
        return products

@app.post("/api/products")
async def create_product(product: ProductCreate):
    with get_db_session(read_only=False) as session:
        new_product = Product(**product.dict())
        session.add(new_product)
        session.commit()
        return new_product
```

**Verification:**
- [ ] Slow queries identified and optimized
- [ ] Appropriate indexes created
- [ ] Query plans reviewed (no sequential scans on large tables)
- [ ] Database configuration tuned for workload
- [ ] Materialized views created for complex reports
- [ ] Read replicas configured (if read-heavy)
- [ ] Query performance improved by measured amount

**If This Fails:**
→ Use EXPLAIN ANALYZE before and after optimization
→ Monitor index usage (pg_stat_user_indexes)
→ Don't over-index (each index has write cost)
→ Test with production data volume
→ Consider partitioning for very large tables

---

### Step 4: Implement Caching Strategy

**What:** Deploy multi-layer caching (application, HTTP, CDN) to reduce database load, decrease latency, and improve scalability.

**How:**

#### Application-Level Caching with Redis

```python
# redis_cache.py
import redis
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps

class CacheManager:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
    
    def delete(self, key: str):
        """Delete from cache"""
        self.redis_client.delete(key)
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def cached(self, ttl: int = 300, key_prefix: str = ''):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                key_data = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
                cache_key = f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
                
                # Try cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key_data = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
                cache_key = f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
                
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            # Return appropriate wrapper
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        
        return decorator

# Initialize cache manager
cache = CacheManager()

# Usage
@cache.cached(ttl=600)  # Cache for 10 minutes
async def get_product(product_id: int):
    return await db.fetch_one(
        "SELECT * FROM products WHERE id = ?", product_id
    )

@cache.cached(ttl=3600, key_prefix='user:')
async def get_user_profile(user_id: int):
    return await db.fetch_one(
        "SELECT * FROM users WHERE id = ?", user_id
    )

# Cache invalidation on update
@app.put("/api/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    await db.execute(
        "UPDATE products SET name = ?, price = ? WHERE id = ?",
        product.name, product.price, product_id
    )
    
    # Invalidate cache
    cache.delete(f"cache:get_product:{product_id}")
    cache.invalidate_pattern(f"cache:*product*")
    
    return {"status": "updated"}
```

#### HTTP Caching Headers

```python
from fastapi import FastAPI, Response
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/api/products/{product_id}")
async def get_product(product_id: int, response: Response):
    product = await db.fetch_one(
        "SELECT * FROM products WHERE id = ?", product_id
    )
    
    # Set cache headers
    response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes
    response.headers["ETag"] = f'"{product["updated_at"].timestamp()}"'
    response.headers["Last-Modified"] = product["updated_at"].strftime(
        '%a, %d %b %Y %H:%M:%S GMT'
    )
    
    return product

@app.get("/api/products")
async def list_products(response: Response):
    products = await db.fetch_all("SELECT * FROM products")
    
    # Cache for 1 minute, but allow stale for 5 minutes while revalidating
    response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=300"
    
    return products
```

#### CDN Configuration

```nginx
# nginx.conf - CDN edge server configuration

http {
    # Cache settings
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m 
                     max_size=10g inactive=60m use_temp_path=off;
    
    upstream backend {
        server app1.internal:8000;
        server app2.internal:8000;
    }
    
    server {
        listen 80;
        server_name api.example.com;
        
        # Static assets - cache aggressively
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
            proxy_pass http://backend;
            proxy_cache my_cache;
            proxy_cache_valid 200 7d;
            proxy_cache_valid 404 1m;
            add_header X-Cache-Status $upstream_cache_status;
            expires 7d;
        }
        
        # API responses - cache briefly
        location /api/ {
            proxy_pass http://backend;
            proxy_cache my_cache;
            proxy_cache_valid 200 1m;
            proxy_cache_key "$scheme$request_method$host$request_uri";
            proxy_cache_bypass $http_cache_control;
            add_header X-Cache-Status $upstream_cache_status;
        }
        
        # Health check - don't cache
        location /health {
            proxy_pass http://backend;
            proxy_no_cache 1;
            proxy_cache_bypass 1;
        }
    }
}
```

#### CloudFront/CDN Setup

```bash
# AWS CloudFront with caching
aws cloudfront create-distribution --distribution-config file://distribution-config.json
```

**distribution-config.json:**
```json
{
  "CallerReference": "my-api-cdn-2025",
  "Comment": "CDN for API with caching",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "my-api-origin",
        "DomainName": "api.myapp.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "my-api-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    },
    "ForwardedValues": {
      "QueryString": true,
      "Headers": {
        "Quantity": 3,
        "Items": ["Authorization", "Accept", "Content-Type"]
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 300,
    "MaxTTL": 3600,
    "Compress": true
  },
  "CacheBehaviors": {
    "Quantity": 1,
    "Items": [
      {
        "PathPattern": "/static/*",
        "TargetOriginId": "my-api-origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "MinTTL": 86400,
        "DefaultTTL": 604800,
        "MaxTTL": 31536000
      }
    ]
  }
}
```

**Verification:**
- [ ] Redis caching implemented for frequently accessed data
- [ ] HTTP cache headers configured appropriately
- [ ] CDN configured for static assets and API responses
- [ ] Cache hit rate > 70% for cacheable content
- [ ] Cache invalidation strategy implemented
- [ ] Response times reduced for cached content

**If This Fails:**
→ Monitor cache hit/miss rates
→ Adjust TTL based on data change frequency
→ Implement cache warming for predictable access patterns
→ Use cache tags for efficient invalidation
→ Monitor Redis memory usage and eviction policy

---

(Continuing in next message due to length...)

**Verification:**
- [ ] Cloud provider setup complete
- [ ] VPC/VNet configured with proper networking
- [ ] IAM/security configured
- [ ] Monitoring and cost management active
- [ ] Documentation complete

**If This Fails:**
→ Follow cloud provider documentation carefully
→ Start with smallest viable setup, expand as needed
→ Use infrastructure-as-code from the beginning
→ Test disaster recovery procedures
→ Regular security audits

---

## Related Workflows

**Prerequisites:**
- None (foundational workflow)

**Next Steps:**
- **docker_container_creation.md** - Container deployment
- **infrastructure_as_code_terraform.md** - IaC management
- **cicd_pipeline_setup.md** - Automated deployments
- **kubernetes_deployment.md** - Container orchestration

**Related:**
- **auto_scaling_configuration.md** - Scale infrastructure
- **application_monitoring_setup.md** - Monitor applications
- **backup_disaster_recovery.md** - DR planning

---

## Tags

`devops` `cloud` `aws` `azure` `gcp` `infrastructure` `setup` `networking` `iam` `monitoring` `high-priority`
