# Scalability Patterns

**ID:** arc-007  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Proven patterns and techniques for building systems that scale from 100 to 1M+ users

**Why:** Scalability patterns enable systems to handle 100-1000x growth in users/traffic without complete rewrites, reduce costs through efficient resource use, and maintain performance under load (response times <200ms even at peak)

**When to use:**
- Planning for user/traffic growth
- System experiencing performance degradation
- Building high-traffic applications (10k+ req/sec)
- Optimizing infrastructure costs
- Preparing for viral growth or traffic spikes
- Designing globally distributed systems
- Building SaaS platforms with multi-tenant needs

---

## Prerequisites

**Required:**
- [ ] Load balancing fundamentals
- [ ] Caching strategies (see arc-002)
- [ ] Database optimization knowledge
- [ ] Understanding of horizontal vs vertical scaling
- [ ] Basic cloud infrastructure knowledge (AWS/GCP/Azure)
- [ ] Monitoring and metrics setup

**Check before starting:**
```bash
# Check load testing tools
ab -V  # Apache Bench
wrk --version
locust --version

# Check container orchestration
kubectl version --client
docker --version

# Check monitoring tools
prometheus --version
```

---

## Implementation Steps

### Step 1: Identify Bottlenecks Through Load Testing

**What:** Measure system performance and identify constraints before scaling

**How:**

**Load Testing Strategy:**

```python
# Load testing with Locust

from locust import HttpUser, task, between
import json

class WebsiteUser(HttpUser):
    """Simulate user behavior"""
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post("/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()['token']
    
    @task(3)  # Weight: 3x more likely than other tasks
    def view_products(self):
        """Most common operation"""
        self.client.get("/api/products", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(2)
    def view_product_detail(self):
        """View individual product"""
        product_id = random.randint(1, 1000)
        self.client.get(f"/api/products/{product_id}")
    
    @task(1)
    def create_order(self):
        """Less frequent operation"""
        self.client.post("/api/orders", 
            json={
                "items": [{"product_id": 1, "quantity": 2}],
                "total": 59.98
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )

# Run load test
# locust -f load_test.py --host=http://localhost:8000 --users 100 --spawn-rate 10

# Analyze results:
# - Response time (p50, p95, p99)
# - Requests per second
# - Error rate
# - Resource usage (CPU, memory, disk I/O)
```

**Bottleneck Identification:**

```python
# Common bottlenecks and how to identify them

class BottleneckDetector:
    """Analyze metrics to find bottlenecks"""
    
    def analyze_performance_metrics(self, metrics):
        """Identify likely bottlenecks"""
        bottlenecks = []
        
        # 1. High CPU (>80%)
        if metrics['cpu_usage'] > 80:
            bottlenecks.append({
                'type': 'CPU',
                'severity': 'high',
                'solution': 'Horizontal scaling or optimize code'
            })
        
        # 2. High memory (>85%)
        if metrics['memory_usage'] > 85:
            bottlenecks.append({
                'type': 'Memory',
                'severity': 'high',
                'solution': 'Memory leak? Add caching? Scale up?'
            })
        
        # 3. Slow database queries (>100ms avg)
        if metrics['db_query_time_avg'] > 100:
            bottlenecks.append({
                'type': 'Database',
                'severity': 'critical',
                'solution': 'Add indexes, optimize queries, read replicas'
            })
        
        # 4. High disk I/O wait
        if metrics['disk_io_wait'] > 20:
            bottlenecks.append({
                'type': 'Disk I/O',
                'severity': 'medium',
                'solution': 'Use faster disks (SSD), reduce disk writes'
            })
        
        # 5. Network saturation
        if metrics['network_usage'] > 80:
            bottlenecks.append({
                'type': 'Network',
                'severity': 'medium',
                'solution': 'CDN, compression, reduce payload size'
            })
        
        # 6. Connection pool exhaustion
        if metrics['db_connection_pool_usage'] > 90:
            bottlenecks.append({
                'type': 'Connection Pool',
                'severity': 'high',
                'solution': 'Increase pool size or fix connection leaks'
            })
        
        return bottlenecks

# Example usage
metrics = {
    'cpu_usage': 45,
    'memory_usage': 60,
    'db_query_time_avg': 250,  # Bottleneck!
    'disk_io_wait': 5,
    'network_usage': 30,
    'db_connection_pool_usage': 95  # Bottleneck!
}

detector = BottleneckDetector()
bottlenecks = detector.analyze_performance_metrics(metrics)

for b in bottlenecks:
    print(f"⚠️  {b['type']} bottleneck ({b['severity']}): {b['solution']}")

# Output:
# ⚠️  Database bottleneck (critical): Add indexes, optimize queries, read replicas
# ⚠️  Connection Pool bottleneck (high): Increase pool size or fix connection leaks
```

**Performance Profiling:**

```python
# Profile code to find slow functions

import cProfile
import pstats
from functools import wraps
import time

def profile_function(func):
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        profiler.disable()
        
        # Print stats
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        print(f"\n{'='*50}")
        print(f"Profile for {func.__name__} ({end_time - start_time:.3f}s)")
        print('='*50)
        stats.print_stats(10)  # Top 10 slowest functions
        
        return result
    return wrapper

@profile_function
def slow_api_endpoint():
    """Endpoint to profile"""
    users = db.query(User).all()  # Slow query?
    for user in users:
        orders = db.query(Order).filter_by(user_id=user.id).all()  # N+1 query!
    return users

# Find N+1 query problems, slow algorithms, etc.
```

**Verification:**
- [ ] Load tests completed with realistic traffic
- [ ] Bottlenecks identified (CPU, memory, DB, network)
- [ ] Baseline metrics established (p50, p95, p99 latency)
- [ ] Resource usage profiled
- [ ] Slow queries identified

**If This Fails:**
→ Start with small load (10 users), increase gradually
→ Use cloud load testing (AWS, LoadImpact)
→ Monitor production metrics if load testing not possible

---

### Step 2: Implement Horizontal Scaling (Scale Out)

**What:** Add more servers/instances rather than making existing ones bigger

**How:**

**Stateless Application Design:**

```python
# Make application stateless for easy horizontal scaling

# ❌ BAD: Stateful (stores session in memory)
class StatefulApp:
    def __init__(self):
        self.sessions = {}  # In-memory storage
    
    def login(self, user_id, token):
        self.sessions[user_id] = token  # Stored in this instance only
    
    def is_authenticated(self, user_id):
        return user_id in self.sessions  # Only works on same instance!

# ✅ GOOD: Stateless (stores session in Redis)
class StatelessApp:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def login(self, user_id, token):
        # Store in shared Redis (accessible by all instances)
        self.redis.setex(f"session:{user_id}", 3600, token)
    
    def is_authenticated(self, user_id):
        # Any instance can check authentication
        return self.redis.exists(f"session:{user_id}")

# With stateless design, we can scale horizontally:
# User → Load Balancer → [Instance 1, Instance 2, Instance 3, ...] → Redis
```

**Load Balancing:**

```python
# nginx load balancer configuration

"""
# /etc/nginx/nginx.conf

upstream backend {
    # Load balancing algorithm
    least_conn;  # Send to server with least connections
    
    # Backend servers
    server backend1.example.com:8000 weight=3;
    server backend2.example.com:8000 weight=2;
    server backend3.example.com:8000 weight=1;
    
    # Health checks
    server backend4.example.com:8000 backup;  # Only used if others fail
    
    # Keep-alive connections
    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }
}
"""
```

**Auto-Scaling (Kubernetes):**

```yaml
# Kubernetes Horizontal Pod Autoscaler

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 100
  metrics:
  # Scale based on CPU
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Target 70% CPU
  
  # Scale based on memory
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # Target 80% memory
  
  # Scale based on custom metrics (requests per second)
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"  # Target 1000 req/sec per pod
  
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50  # Scale up by 50% at a time
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 10  # Scale down by 10% at a time
        periodSeconds: 60

---
# Deployment definition
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3  # Initial replicas
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: myapp:latest
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        ports:
        - containerPort: 8000
```

**Cloud Auto-Scaling (AWS):**

```python
# AWS Auto Scaling configuration (boto3)

import boto3

autoscaling = boto3.client('autoscaling')

# Create Auto Scaling Group
autoscaling.create_auto_scaling_group(
    AutoScalingGroupName='web-app-asg',
    LaunchTemplate={
        'LaunchTemplateId': 'lt-0123456789abcdef',
        'Version': '$Latest'
    },
    MinSize=3,
    MaxSize=100,
    DesiredCapacity=5,
    HealthCheckType='ELB',
    HealthCheckGracePeriod=300,
    TargetGroupARNs=[
        'arn:aws:elasticloadbalancing:...'
    ],
    Tags=[
        {'Key': 'Name', 'Value': 'web-app-instance'}
    ]
)

# Create scaling policy (target tracking)
autoscaling.put_scaling_policy(
    AutoScalingGroupName='web-app-asg',
    PolicyName='target-tracking-cpu',
    PolicyType='TargetTrackingScaling',
    TargetTrackingConfiguration={
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ASGAverageCPUUtilization'
        },
        'TargetValue': 70.0  # Target 70% CPU
    }
)
```

**Verification:**
- [ ] Application is stateless
- [ ] Load balancer distributes traffic
- [ ] Multiple instances running
- [ ] Auto-scaling configured and tested
- [ ] Health checks working
- [ ] No session affinity issues

**If This Fails:**
→ Identify stateful components (sessions, file uploads)
→ Move state to external stores (Redis, S3)
→ Test with sticky sessions initially, then remove

---

### Step 3: Implement Database Scaling Patterns

**What:** Scale database tier to handle increased read/write load

**How:**

**Read Replicas (Read Scaling):**

```python
# Database read replicas for read-heavy workloads

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

class DatabaseRouter:
    """Route reads to replicas, writes to primary"""
    
    def __init__(self, primary_url, replica_urls):
        # Primary database (writes)
        self.primary_engine = create_engine(primary_url)
        self.PrimarySession = sessionmaker(bind=self.primary_engine)
        
        # Read replicas (reads)
        self.replica_engines = [
            create_engine(url) for url in replica_urls
        ]
        self.ReplicaSessions = [
            sessionmaker(bind=engine) for engine in self.replica_engines
        ]
    
    def get_write_session(self):
        """Get session for writes (primary only)"""
        return self.PrimarySession()
    
    def get_read_session(self):
        """Get session for reads (random replica)"""
        # Round-robin or random selection
        session_class = random.choice(self.ReplicaSessions)
        return session_class()

# Usage
db_router = DatabaseRouter(
    primary_url='postgresql://primary:5432/mydb',
    replica_urls=[
        'postgresql://replica1:5432/mydb',
        'postgresql://replica2:5432/mydb',
        'postgresql://replica3:5432/mydb'
    ]
)

# Write operations use primary
def create_user(user_data):
    session = db_router.get_write_session()
    user = User(**user_data)
    session.add(user)
    session.commit()
    return user

# Read operations use replicas
def get_users():
    session = db_router.get_read_session()
    return session.query(User).all()

# Analytics queries use replicas (don't impact primary)
def get_analytics():
    session = db_router.get_read_session()
    return session.query(Order).join(User).all()
```

**Database Sharding (Write Scaling):**

```python
# Horizontal partitioning (sharding) for write scaling

class ShardedDatabase:
    """Distribute data across multiple databases"""
    
    def __init__(self, shard_configs):
        self.shards = {
            shard_id: create_engine(config['url'])
            for shard_id, config in shard_configs.items()
        }
    
    def get_shard_id(self, user_id):
        """Determine which shard holds this user's data"""
        # Simple modulo sharding
        return user_id % len(self.shards)
    
    def get_shard_engine(self, user_id):
        """Get database engine for user"""
        shard_id = self.get_shard_id(user_id)
        return self.shards[shard_id]
    
    def create_order(self, order_data):
        """Create order on appropriate shard"""
        user_id = order_data['user_id']
        engine = self.get_shard_engine(user_id)
        
        with engine.connect() as conn:
            result = conn.execute(
                "INSERT INTO orders (user_id, total, items) VALUES (?, ?, ?)",
                (user_id, order_data['total'], order_data['items'])
            )
            return result.lastrowid
    
    def get_user_orders(self, user_id):
        """Get orders from user's shard"""
        engine = self.get_shard_engine(user_id)
        
        with engine.connect() as conn:
            result = conn.execute(
                "SELECT * FROM orders WHERE user_id = ?",
                (user_id,)
            )
            return result.fetchall()
    
    def get_all_orders(self):
        """Query across all shards (expensive!)"""
        all_orders = []
        
        # Query each shard
        for shard_id, engine in self.shards.items():
            with engine.connect() as conn:
                result = conn.execute("SELECT * FROM orders")
                all_orders.extend(result.fetchall())
        
        return all_orders

# Shard configuration
shard_config = {
    0: {'url': 'postgresql://shard0:5432/mydb'},
    1: {'url': 'postgresql://shard1:5432/mydb'},
    2: {'url': 'postgresql://shard2:5432/mydb'},
    3: {'url': 'postgresql://shard3:5432/mydb'},
}

sharded_db = ShardedDatabase(shard_config)

# User 123 always goes to same shard
order = sharded_db.create_order({
    'user_id': 123,
    'total': 99.99,
    'items': [...]
})
```

**Connection Pooling:**

```python
# Efficient connection pooling

from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

# Configure connection pool
engine = create_engine(
    'postgresql://localhost/mydb',
    
    # Pool configuration
    poolclass=QueuePool,
    pool_size=20,          # Normal connections
    max_overflow=10,       # Additional connections under load
    pool_timeout=30,       # Wait 30s for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connections before use
    
    # Connection options
    connect_args={
        'connect_timeout': 10,
        'application_name': 'myapp'
    }
)

# Monitor pool usage
@app.middleware("http")
async def monitor_db_pool(request, call_next):
    pool = engine.pool
    
    # Log pool stats
    logger.info(
        "DB Pool Status",
        size=pool.size(),
        checked_in=pool.checkedin(),
        checked_out=pool.checkedout(),
        overflow=pool.overflow()
    )
    
    # Alert if pool exhausted
    if pool.overflow() >= pool._max_overflow * 0.9:
        logger.warning("⚠️  Database connection pool nearly exhausted!")
    
    response = await call_next(request)
    return response
```

**Database Caching (Query Results):**

```python
# Cache expensive queries

from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def cache_query(ttl=300):
    """Cache database query results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"query:{func.__name__}:{args}:{kwargs}"
            
            # Try cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute query
            result = func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_query(ttl=600)  # Cache for 10 minutes
def get_popular_products():
    """Expensive aggregation query"""
    return db.query(
        Product.id,
        Product.name,
        func.count(OrderItem.id).label('order_count')
    ).join(OrderItem).group_by(Product.id)\
     .order_by(desc('order_count')).limit(100).all()
```

**Verification:**
- [ ] Read replicas handling read traffic
- [ ] Write load distributed (if sharding)
- [ ] Connection pooling configured
- [ ] Database caching reduces query load
- [ ] No connection pool exhaustion
- [ ] Query performance acceptable (<100ms)

**If This Fails:**
→ Start with read replicas (easiest)
→ Optimize queries before sharding (indexes, query tuning)
→ Use managed database services (AWS RDS, Google Cloud SQL)

---

### Step 4: Implement CDN and Edge Caching

**What:** Distribute static content globally for low latency

**How:**

**CDN Configuration (CloudFront):**

```python
# AWS CloudFront CDN setup

import boto3

cloudfront = boto3.client('cloudfront')

# Create CloudFront distribution
response = cloudfront.create_distribution(
    DistributionConfig={
        'CallerReference': str(time.time()),
        'Comment': 'CDN for myapp.com',
        'Enabled': True,
        
        # Origin (your application servers)
        'Origins': {
            'Quantity': 1,
            'Items': [{
                'Id': 'myapp-origin',
                'DomainName': 'api.myapp.com',
                'CustomOriginConfig': {
                    'HTTPPort': 80,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'https-only'
                }
            }]
        },
        
        # Cache behavior
        'DefaultCacheBehavior': {
            'TargetOriginId': 'myapp-origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 7,
                'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE']
            },
            'Compress': True,
            'MinTTL': 0,
            'DefaultTTL': 86400,  # 24 hours
            'MaxTTL': 31536000,   # 1 year
            
            # Forward headers
            'ForwardedValues': {
                'QueryString': True,
                'Headers': {
                    'Quantity': 3,
                    'Items': ['Host', 'Authorization', 'CloudFront-Forwarded-Proto']
                },
                'Cookies': {'Forward': 'all'}
            }
        },
        
        # Cache behaviors for different paths
        'CacheBehaviors': {
            'Quantity': 2,
            'Items': [
                {
                    # Static assets (long cache)
                    'PathPattern': '/static/*',
                    'TargetOriginId': 'myapp-origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'MinTTL': 31536000,  # 1 year
                    'DefaultTTL': 31536000,
                    'MaxTTL': 31536000,
                    'Compress': True
                },
                {
                    # API calls (short cache or no cache)
                    'PathPattern': '/api/*',
                    'TargetOriginId': 'myapp-origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'MinTTL': 0,
                    'DefaultTTL': 0,  # No cache for API
                    'MaxTTL': 0
                }
            ]
        }
    }
)
```

**Cache Headers for CDN:**

```python
# Set appropriate cache headers

from fastapi import FastAPI, Response
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/api/products")
async def get_products(response: Response):
    """API endpoint with caching"""
    products = db.query(Product).all()
    
    # Cache for 5 minutes
    max_age = 300
    response.headers['Cache-Control'] = f'public, max-age={max_age}'
    response.headers['Expires'] = (
        datetime.utcnow() + timedelta(seconds=max_age)
    ).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # ETag for conditional requests
    etag = generate_etag(products)
    response.headers['ETag'] = etag
    
    return products

@app.get("/static/{file_path}")
async def serve_static(file_path: str, response: Response):
    """Serve static files with long cache"""
    
    # Cache for 1 year (immutable)
    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    
    # Serve file
    return FileResponse(f'static/{file_path}')

# Vary header for personalized content
@app.get("/api/user/profile")
async def get_profile(response: Response, user_id: int):
    """User-specific content"""
    profile = get_user_profile(user_id)
    
    # Don't cache in shared caches (CDN), only in browser
    response.headers['Cache-Control'] = 'private, max-age=300'
    response.headers['Vary'] = 'Authorization'  # Cache per user
    
    return profile
```

**Edge Functions (Cloudflare Workers):**

```javascript
// Cloudflare Worker for edge logic

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // 1. Cache static assets at edge
  if (url.pathname.startsWith('/static/')) {
    // Check edge cache
    const cache = caches.default
    let response = await cache.match(request)
    
    if (!response) {
      // Fetch from origin
      response = await fetch(request)
      
      // Cache at edge for 1 year
      const headers = new Headers(response.headers)
      headers.set('Cache-Control', 'public, max-age=31536000')
      
      response = new Response(response.body, {
        status: response.status,
        headers: headers
      })
      
      event.waitUntil(cache.put(request, response.clone()))
    }
    
    return response
  }
  
  // 2. A/B testing at edge
  if (url.pathname === '/') {
    const variant = Math.random() < 0.5 ? 'A' : 'B'
    
    // Modify request
    const modifiedRequest = new Request(request)
    modifiedRequest.headers.set('X-Variant', variant)
    
    return fetch(modifiedRequest)
  }
  
  // 3. Geolocation-based routing
  const country = request.headers.get('CF-IPCountry')
  if (country === 'CN') {
    return fetch('https://china-origin.example.com')
  }
  
  // Default: pass through to origin
  return fetch(request)
}
```

**Verification:**
- [ ] CDN serving static assets
- [ ] Cache hit ratio > 70%
- [ ] Latency reduced (especially for global users)
- [ ] Cache headers configured correctly
- [ ] Edge logic working (if used)

**If This Fails:**
→ Start with simple CDN (Cloudflare free tier)
→ Use object storage CDN (S3 + CloudFront, GCS + Cloud CDN)
→ Add versioning to static files (cache busting)

---

### Step 5: Implement Asynchronous Processing

**What:** Offload long-running tasks to background workers

**How:**

**Task Queue with Celery:**

```python
# Celery for async task processing

# celery_app.py
from celery import Celery

celery_app = Celery(
    'myapp',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Task configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'myapp.tasks.send_email': {'queue': 'emails'},
        'myapp.tasks.process_video': {'queue': 'video'},
        'myapp.tasks.generate_report': {'queue': 'reports'}
    },
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Define tasks
@celery_app.task(bind=True, max_retries=3)
def send_email(self, to, subject, body):
    """Send email asynchronously"""
    try:
        email_service.send(to=to, subject=subject, body=body)
        return {'status': 'sent', 'to': to}
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery_app.task
def process_order(order_id):
    """Process order in background"""
    order = db.query(Order).get(order_id)
    
    # Long-running operations
    validate_inventory(order)
    charge_payment(order)
    send_confirmation_email(order.user.email)
    update_analytics(order)
    
    return {'order_id': order_id, 'status': 'processed'}

@celery_app.task
def generate_monthly_report(month, year):
    """Generate report (very slow)"""
    data = aggregate_data_for_month(month, year)
    pdf = generate_pdf_report(data)
    
    # Upload to S3
    s3_url = upload_to_s3(pdf, f'reports/{year}-{month}.pdf')
    
    # Notify user
    send_email.delay(
        to='admin@example.com',
        subject=f'Monthly report {month}/{year}',
        body=f'Report available at {s3_url}'
    )
    
    return {'url': s3_url}

# Use in API
from fastapi import FastAPI, BackgroundTasks

@app.post("/orders")
async def create_order(order_data: dict):
    """Create order and process async"""
    # Save order to database (fast)
    order = Order.create(order_data)
    db.add(order)
    db.commit()
    
    # Process order asynchronously (slow operations)
    process_order.delay(order.id)
    
    # Return immediately
    return {
        'order_id': order.id,
        'status': 'pending',
        'message': 'Order is being processed'
    }

@app.post("/reports/monthly")
async def request_report(month: int, year: int):
    """Generate report asynchronously"""
    # Start task
    task = generate_monthly_report.delay(month, year)
    
    return {
        'task_id': task.id,
        'status': 'processing',
        'message': 'Report generation started'
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Check task status"""
    task = celery_app.AsyncResult(task_id)
    
    if task.ready():
        return {
            'task_id': task_id,
            'status': 'completed',
            'result': task.result
        }
    else:
        return {
            'task_id': task_id,
            'status': 'processing'
        }
```

**Start Celery Workers:**

```bash
# Start different workers for different queues

# Email worker (high priority, many workers)
celery -A celery_app worker --queue=emails --concurrency=10

# Video worker (low priority, fewer workers, more resources)
celery -A celery_app worker --queue=video --concurrency=2

# Report worker (scheduled tasks)
celery -A celery_app worker --queue=reports --concurrency=5

# Beat scheduler (cron-like)
celery -A celery_app beat

# Monitor workers
celery -A celery_app flower  # Web UI at localhost:5555
```

**Verification:**
- [ ] Tasks executing asynchronously
- [ ] Workers processing tasks
- [ ] Failed tasks retried
- [ ] Queue lengths monitored
- [ ] No task backlog
- [ ] API responds quickly (offloads slow work)

**If This Fails:**
→ Use managed queue service (AWS SQS + Lambda, Google Cloud Tasks)
→ Start with FastAPI BackgroundTasks (simpler, single-server)
→ Monitor queue depths to detect issues

---

## Verification Checklist

After completing this workflow:

- [ ] Load testing completed and bottlenecks identified
- [ ] Horizontal scaling implemented (auto-scaling)
- [ ] Database scaled (read replicas, connection pooling)
- [ ] CDN serving static content
- [ ] Async processing offloads slow operations
- [ ] Caching at multiple layers
- [ ] Monitoring and alerting configured
- [ ] System handles 10x current load
- [ ] Response times acceptable under load (<200ms p95)
- [ ] Cost-optimized (efficient resource use)

---

## Common Issues & Solutions

### Issue: Uneven load distribution

**Symptoms:**
- Some instances overloaded, others idle
- Hot shards in database
- Slow response times for some users

**Solution:**
```python
# Use consistent hashing for better distribution

import hashlib

class ConsistentHashing:
    """Consistent hashing for even distribution"""
    
    def __init__(self, nodes, virtual_nodes=150):
        self.nodes = nodes
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self._build_ring()
    
    def _hash(self, key):
        """Hash function"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def _build_ring(self):
        """Build hash ring with virtual nodes"""
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = node
    
    def get_node(self, key):
        """Get node for key"""
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        
        # Find first node >= hash_value
        for ring_hash in sorted(self.ring.keys()):
            if ring_hash >= hash_value:
                return self.ring[ring_hash]
        
        # Wrap around to first node
        return self.ring[min(self.ring.keys())]

# Usage
nodes = ['server1', 'server2', 'server3', 'server4']
ch = ConsistentHashing(nodes)

# Evenly distribute users
for user_id in range(1000):
    node = ch.get_node(f"user:{user_id}")
    print(f"User {user_id} → {node}")
```

**Prevention:**
- Use consistent hashing
- Monitor node utilization
- Avoid fixed partitioning (modulo)
- Use managed load balancers with health checks

---

## Best Practices

### DO:
✅ Design for horizontal scaling from the start
✅ Make applications stateless
✅ Use read replicas for read-heavy workloads
✅ Implement multi-layer caching
✅ Use CDN for static assets
✅ Offload slow operations to async workers
✅ Load test regularly
✅ Monitor everything (metrics, logs, traces)
✅ Auto-scale based on metrics
✅ Optimize database queries and indexes

### DON'T:
❌ Rely only on vertical scaling
❌ Store session state in application memory
❌ Skip caching layers
❌ Ignore database optimization
❌ Serve static assets from application servers
❌ Run long operations synchronously
❌ Scale without measuring
❌ Over-engineer early (premature optimization)
❌ Forget about costs (auto-scaling can be expensive)
❌ Ignore security when scaling

---

## Related Workflows

**Prerequisites:**
- `arc-002`: Caching Strategies - Multi-layer caching
- `arc-004`: Distributed Systems Patterns - Scaling foundations
- `arc-006`: Microservices Patterns - Service scaling

**Next Steps:**
- `devops-006`: Container Orchestration - Deploy scaled systems
- `devops-008`: Application Performance Monitoring - Monitor at scale
- `devops-012`: Performance Tuning - Fine-tune performance

**Alternatives:**
- Serverless architecture (auto-scaling managed)
- PaaS platforms (Heroku, Google App Engine)

---

## Tags
`architecture` `scalability` `patterns` `performance` `horizontal-scaling` `load-balancing` `caching` `cdn` `database-scaling` `async-processing`
