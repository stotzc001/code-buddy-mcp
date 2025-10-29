# Microservices Patterns

**ID:** arc-006  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Architectural patterns and best practices for designing, building, and operating microservices systems

**Why:** Microservices enable independent team scaling (10x faster delivery), independent deployment (100+ deploys/day), technology flexibility, and fault isolation - but require careful pattern application to avoid distributed monoliths

**When to use:**
- Breaking down monolithic applications
- Building systems with independent scaling needs
- Supporting multiple teams working autonomously
- Need for technology diversity across services
- Independent deployment cadences required
- Building cloud-native applications
- High availability requirements (99.99%+)

---

## Prerequisites

**Required:**
- [ ] Container knowledge (Docker basics)
- [ ] API design experience (REST/gRPC)
- [ ] Distributed systems understanding
- [ ] Database design fundamentals
- [ ] Understanding of service discovery
- [ ] Basic knowledge of message queues

**Check before starting:**
```bash
# Check containerization tools
docker --version
docker-compose --version

# Check Kubernetes (optional but recommended)
kubectl version --client

# Check service mesh tools
istioctl version

# Check API tools
curl --version
grpcurl --version
```

---

## Implementation Steps

### Step 1: Service Decomposition Strategy

**What:** Break down monolith into independently deployable microservices

**How:**

**Domain-Driven Design (DDD) Approach:**

```python
# Identify Bounded Contexts

class BoundedContext:
    """
    A bounded context is a logical boundary
    Each microservice should match one bounded context
    """
    pass

# Example: E-commerce system decomposition

"""
Monolith Before:
┌──────────────────────────────────────────────┐
│  E-commerce Application                      │
│  ┌────────┬─────────┬──────────┬──────────┐ │
│  │ Users  │ Products│ Orders   │ Payments │ │
│  │ Auth   │ Catalog │ Cart     │ Shipping │ │
│  │ Profile│ Search  │ Checkout │ Invoices │ │
│  └────────┴─────────┴──────────┴──────────┘ │
│                                              │
│  Single Database, Single Deployment          │
└──────────────────────────────────────────────┘

Microservices After:
┌─────────────┐  ┌──────────────┐  ┌────────────┐
│ User        │  │ Product      │  │ Order      │
│ Service     │  │ Catalog      │  │ Service    │
│             │  │ Service      │  │            │
│ - Auth      │  │ - Products   │  │ - Orders   │
│ - Profile   │  │ - Categories │  │ - Cart     │
│ - Sessions  │  │ - Search     │  │ - Checkout │
│             │  │ - Reviews    │  │            │
│ Own DB      │  │ Own DB       │  │ Own DB     │
└─────────────┘  └──────────────┘  └────────────┘

┌─────────────┐  ┌──────────────┐  ┌────────────┐
│ Payment     │  │ Shipping     │  │ Notification│
│ Service     │  │ Service      │  │ Service    │
│             │  │              │  │            │
│ - Payments  │  │ - Fulfillment│  │ - Email    │
│ - Refunds   │  │ - Tracking   │  │ - SMS      │
│ - Invoicing │  │ - Carriers   │  │ - Push     │
│             │  │              │  │            │
│ Own DB      │  │ Own DB       │  │ Own DB     │
└─────────────┘  └──────────────┘  └────────────┘
"""

# Decomposition Decision Framework

def should_be_separate_service(subdomain):
    """
    Decide if subdomain should be separate microservice
    """
    score = 0
    
    # Business criteria
    if subdomain.has_distinct_business_logic:
        score += 2
    if subdomain.changes_frequently:
        score += 2
    if subdomain.has_different_scalability_needs:
        score += 2
    if subdomain.owned_by_different_team:
        score += 1
    
    # Technical criteria
    if subdomain.has_different_data_model:
        score += 1
    if subdomain.requires_different_technology:
        score += 1
    if subdomain.has_different_security_requirements:
        score += 1
    
    # Complexity cost
    complexity_cost = 3  # Each service adds overhead
    
    return score > complexity_cost

# Example: Payment subdomain
payment_subdomain = {
    'has_distinct_business_logic': True,       # +2
    'changes_frequently': False,
    'has_different_scalability_needs': True,   # +2
    'owned_by_different_team': True,           # +1
    'has_different_data_model': True,          # +1
    'requires_different_technology': True,     # +1 (PCI compliance)
    'has_different_security_requirements': True # +1
}
# Score: 8 > 3 → Separate service ✅

# Example: User profile subdomain
profile_subdomain = {
    'has_distinct_business_logic': False,
    'changes_frequently': False,
    'has_different_scalability_needs': False,
    'owned_by_different_team': False,
    'has_different_data_model': False,
    'requires_different_technology': False,
    'has_different_security_requirements': False
}
# Score: 0 < 3 → Keep in existing service ❌
```

**Service Boundaries:**

```python
# Define clear service boundaries

class UserService:
    """
    User Service - Bounded Context: User Management
    
    Responsibilities:
    - User registration and authentication
    - User profile management
    - Access control
    
    NOT Responsible for:
    - Product preferences (Product Service)
    - Order history (Order Service)
    - Payment methods (Payment Service)
    """
    
    def register_user(self, email, password):
        """Register new user - OWNED by this service"""
        pass
    
    def get_user_profile(self, user_id):
        """Get user basic info - OWNED by this service"""
        pass
    
    # ❌ BAD: Crossing boundaries
    def get_user_orders(self, user_id):
        """DON'T: This belongs to Order Service"""
        pass
    
    # ✅ GOOD: Call Order Service
    def get_user_with_orders(self, user_id):
        """Aggregate from multiple services at API Gateway level"""
        user = self.get_user_profile(user_id)
        orders = order_service_client.get_orders(user_id)
        return {'user': user, 'orders': orders}

class OrderService:
    """
    Order Service - Bounded Context: Order Management
    
    Responsibilities:
    - Order creation and management
    - Order status tracking
    - Order history
    
    NOT Responsible for:
    - User authentication (User Service)
    - Product inventory (Product Service)
    - Payment processing (Payment Service)
    """
    
    def create_order(self, user_id, items):
        """Create order - OWNED by this service"""
        # Validate user_id exists (call User Service)
        # Validate items available (call Product Service)
        # Create order
        pass
    
    def get_orders(self, user_id):
        """Get orders for user - OWNED by this service"""
        pass
```

**Verification:**
- [ ] Services align with business domains
- [ ] Each service has single responsibility
- [ ] Service boundaries clearly defined
- [ ] Data ownership explicit
- [ ] No shared databases between services

**If This Fails:**
→ Start with coarse-grained services (fewer is better)
→ Use Strangler Fig pattern to extract gradually
→ Don't split until you have clear team/scaling reasons

---

### Step 2: Implement API Gateway Pattern

**What:** Single entry point for clients, handles routing, authentication, and aggregation

**How:**

**API Gateway Responsibilities:**

```
Client → API Gateway → Internal Services

API Gateway handles:
1. Routing to services
2. Authentication/Authorization
3. Rate limiting
4. Request/response transformation
5. API composition (aggregation)
6. Protocol translation (REST → gRPC)
7. Caching
8. Load balancing
```

**Python API Gateway (FastAPI):**

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx
from functools import lru_cache
import time

app = FastAPI(title="API Gateway")

# Service URLs (from environment or service discovery)
USER_SERVICE_URL = "http://user-service:8001"
ORDER_SERVICE_URL = "http://order-service:8002"
PRODUCT_SERVICE_URL = "http://product-service:8003"

# HTTP client with connection pooling
http_client = httpx.AsyncClient(
    timeout=10.0,
    limits=httpx.Limits(max_connections=100)
)

# 1. Authentication & Authorization
async def verify_token(authorization: str = Header(None)):
    """Verify JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    
    # Verify token with User Service or decode JWT
    response = await http_client.post(
        f"{USER_SERVICE_URL}/verify-token",
        json={"token": token}
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return response.json()

# 2. Simple Proxy (Routing)
@app.get("/api/users/{user_id}")
async def get_user(
    user_id: int,
    current_user = Depends(verify_token)
):
    """Proxy request to User Service"""
    response = await http_client.get(
        f"{USER_SERVICE_URL}/users/{user_id}"
    )
    
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    
    return response.json()

# 3. API Composition (Aggregation)
@app.get("/api/users/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: int,
    current_user = Depends(verify_token)
):
    """
    Aggregate data from multiple services
    Returns combined response
    """
    # Call services in parallel
    user_task = http_client.get(f"{USER_SERVICE_URL}/users/{user_id}")
    orders_task = http_client.get(f"{ORDER_SERVICE_URL}/orders?user_id={user_id}")
    
    # Wait for all responses
    user_response, orders_response = await asyncio.gather(
        user_task,
        orders_task,
        return_exceptions=True
    )
    
    # Handle errors gracefully
    user_data = user_response.json() if user_response.status_code == 200 else None
    orders_data = orders_response.json() if orders_response.status_code == 200 else []
    
    # Compose response
    return {
        "user": user_data,
        "orders": orders_data,
        "summary": {
            "total_orders": len(orders_data),
            "account_age_days": calculate_age(user_data.get('created_at'))
        }
    }

# 4. Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/orders")
@limiter.limit("10/minute")  # Rate limit per IP
async def create_order(
    request: Request,
    order_data: dict,
    current_user = Depends(verify_token)
):
    """Create order with rate limiting"""
    response = await http_client.post(
        f"{ORDER_SERVICE_URL}/orders",
        json=order_data,
        headers={"X-User-ID": str(current_user['user_id'])}
    )
    return response.json()

# 5. Response Caching
@lru_cache(maxsize=1000)
def get_cached_products(category: str):
    """Cache product listings"""
    return httpx.get(f"{PRODUCT_SERVICE_URL}/products?category={category}").json()

@app.get("/api/products")
async def list_products(category: str = "all"):
    """Get products with caching"""
    # Check cache
    if category in cache:
        return cache[category]
    
    # Fetch from service
    response = await http_client.get(
        f"{PRODUCT_SERVICE_URL}/products",
        params={"category": category}
    )
    
    # Cache result
    cache[category] = response.json()
    return cache[category]

# 6. Circuit Breaker (prevent cascading failures)
from circuit_breaker import CircuitBreaker

service_breakers = {
    'user': CircuitBreaker(failure_threshold=5, timeout=60),
    'order': CircuitBreaker(failure_threshold=5, timeout=60),
}

@app.get("/api/users/{user_id}")
async def get_user_with_cb(user_id: int):
    """Get user with circuit breaker"""
    try:
        return service_breakers['user'].call(
            lambda: http_client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        )
    except CircuitBreakerOpenError:
        # Return cached or default data
        return get_cached_user(user_id) or {"error": "Service temporarily unavailable"}
```

**Kong API Gateway Configuration:**

```yaml
# Kong Gateway (production-ready alternative)

# kong.yml
_format_version: "2.1"

services:
  - name: user-service
    url: http://user-service:8001
    routes:
      - name: user-routes
        paths:
          - /api/users
        methods:
          - GET
          - POST
          - PUT
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 100
          policy: local
      - name: cors
        config:
          origins:
            - "*"

  - name: order-service
    url: http://order-service:8002
    routes:
      - name: order-routes
        paths:
          - /api/orders
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 50

  - name: product-service
    url: http://product-service:8003
    routes:
      - name: product-routes
        paths:
          - /api/products
    plugins:
      - name: proxy-cache
        config:
          strategy: memory
          content_type:
            - application/json
          cache_ttl: 300  # 5 minutes
```

**Verification:**
- [ ] API Gateway deployed
- [ ] All services accessible through gateway
- [ ] Authentication centralized
- [ ] Rate limiting enforced
- [ ] Response aggregation working
- [ ] Circuit breakers prevent cascading failures

**If This Fails:**
→ Use managed API Gateway (AWS API Gateway, Google Cloud Endpoints)
→ Start simple (just routing), add features gradually
→ Use nginx/Envoy as basic reverse proxy initially

---

### Step 3: Implement Service-to-Service Communication

**What:** Enable services to communicate reliably using sync and async patterns

**How:**

**Synchronous Communication (REST/gRPC):**

```python
# REST Client with Service Discovery

import httpx
from consul import Consul

class ServiceClient:
    """Client for calling other microservices"""
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.consul = Consul(host='consul', port=8500)
        self.http_client = httpx.AsyncClient(timeout=5.0)
    
    async def get_service_url(self):
        """Get service URL from Consul"""
        # Get healthy instances
        _, instances = self.consul.health.service(
            self.service_name,
            passing=True
        )
        
        if not instances:
            raise ServiceUnavailableError(self.service_name)
        
        # Simple load balancing (random)
        import random
        instance = random.choice(instances)
        
        address = instance['Service']['Address']
        port = instance['Service']['Port']
        return f"http://{address}:{port}"
    
    async def get(self, endpoint, **kwargs):
        """GET request to service"""
        url = await self.get_service_url()
        response = await self.http_client.get(f"{url}{endpoint}", **kwargs)
        response.raise_for_status()
        return response.json()
    
    async def post(self, endpoint, **kwargs):
        """POST request to service"""
        url = await self.get_service_url()
        response = await self.http_client.post(f"{url}{endpoint}", **kwargs)
        response.raise_for_status()
        return response.json()

# Usage in Order Service
user_service = ServiceClient('user-service')
payment_service = ServiceClient('payment-service')

@app.post("/orders")
async def create_order(order_data: dict):
    # Validate user exists
    user = await user_service.get(f"/users/{order_data['user_id']}")
    
    # Create order
    order = Order.create(order_data)
    db.add(order)
    db.commit()
    
    # Process payment
    try:
        payment = await payment_service.post("/payments", json={
            'order_id': order.id,
            'amount': order.total,
            'user_id': order.user_id
        })
    except httpx.HTTPError as e:
        # Rollback order if payment fails
        db.delete(order)
        db.commit()
        raise HTTPException(status_code=402, detail="Payment failed")
    
    return {"order": order, "payment": payment}
```

**gRPC Communication (High Performance):**

```python
# Install: pip install grpcio grpcio-tools

# user_service.proto
"""
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc CreateUser (CreateUserRequest) returns (User);
}

message GetUserRequest {
  int64 user_id = 1;
}

message User {
  int64 id = 1;
  string email = 2;
  string name = 3;
}
"""

# Generate Python code
# python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user_service.proto

# Server implementation
import grpc
from concurrent import futures
import user_service_pb2
import user_service_pb2_grpc

class UserServiceServicer(user_service_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        user = db.query(User).get(request.user_id)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        
        return user_service_pb2.User(
            id=user.id,
            email=user.email,
            name=user.name
        )

# Start gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
user_service_pb2_grpc.add_UserServiceServicer_to_server(
    UserServiceServicer(), server
)
server.add_insecure_port('[::]:50051')
server.start()

# Client usage
channel = grpc.insecure_channel('user-service:50051')
stub = user_service_pb2_grpc.UserServiceStub(channel)

response = stub.GetUser(user_service_pb2.GetUserRequest(user_id=123))
print(f"User: {response.name}, {response.email}")
```

**Asynchronous Communication (Events):**

```python
# Event-driven communication for loose coupling

class OrderService:
    """Order service publishes events"""
    
    def create_order(self, order_data):
        # Create order
        order = Order.create(order_data)
        db.add(order)
        db.commit()
        
        # Publish event (don't wait for response)
        event_bus.publish('order.created', {
            'order_id': order.id,
            'user_id': order.user_id,
            'total': order.total,
            'items': order.items
        })
        
        return order

class InventoryService:
    """Inventory service subscribes to events"""
    
    @event_bus.subscribe('order.created')
    def handle_order_created(self, event):
        order_id = event['order_id']
        items = event['items']
        
        # Reserve inventory
        for item in items:
            self.reserve_item(item['product_id'], item['quantity'])
        
        # Publish confirmation event
        event_bus.publish('inventory.reserved', {
            'order_id': order_id
        })

class NotificationService:
    """Notification service subscribes to events"""
    
    @event_bus.subscribe('order.created')
    def handle_order_created(self, event):
        # Send order confirmation email
        user_id = event['user_id']
        order_id = event['order_id']
        
        send_email(
            to=get_user_email(user_id),
            subject=f"Order #{order_id} confirmed",
            template='order_confirmation'
        )
```

**Verification:**
- [ ] Services can discover each other
- [ ] REST/gRPC communication working
- [ ] Event-driven async communication working
- [ ] Timeouts configured (prevent hanging)
- [ ] Retries with exponential backoff
- [ ] Circuit breakers prevent cascading failures

**If This Fails:**
→ Start with simple REST + service URLs in config
→ Add service discovery later (Consul, Kubernetes DNS)
→ Use managed service mesh (Istio) for advanced routing

---

### Step 4: Implement Database Per Service Pattern

**What:** Each microservice owns its database, no shared databases

**How:**

**Database Ownership:**

```python
# Each service has its own database

"""
User Service → PostgreSQL (users DB)
Order Service → PostgreSQL (orders DB)
Product Service → Elasticsearch (product search)
Notification Service → MongoDB (notification logs)
Analytics Service → ClickHouse (event analytics)
"""

# ✅ GOOD: Service owns its data
class UserService:
    def __init__(self):
        self.db = PostgreSQL(database='users_db')
    
    def get_user(self, user_id):
        return self.db.query(User).get(user_id)
    
    def update_user(self, user_id, data):
        user = self.db.query(User).get(user_id)
        user.update(data)
        self.db.commit()

# ❌ BAD: Services sharing database
class OrderService:
    def create_order(self, order_data):
        # DON'T query User table directly!
        # user = shared_db.query(User).get(order_data['user_id'])
        
        # ✅ DO: Call User Service API
        user = user_service.get_user(order_data['user_id'])
        
        order = Order.create(order_data)
        self.db.add(order)
        self.db.commit()
```

**Data Duplication (Denormalization):**

```python
# Duplicate data for performance (eventual consistency)

class OrderService:
    """
    Order service caches user data
    Avoids calling User Service for every query
    """
    
    class Order(Base):
        __tablename__ = 'orders'
        
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer)
        
        # Denormalized user data (cached)
        user_email = Column(String)
        user_name = Column(String)
        
        items = relationship('OrderItem')
        total = Column(Numeric)
    
    def create_order(self, order_data):
        # Fetch current user data
        user = user_service.get_user(order_data['user_id'])
        
        # Store denormalized copy
        order = Order(
            user_id=user['id'],
            user_email=user['email'],      # Cached
            user_name=user['name'],          # Cached
            items=order_data['items'],
            total=order_data['total']
        )
        
        db.add(order)
        db.commit()
        return order
    
    # Update cache when user changes
    @event_bus.subscribe('user.updated')
    def handle_user_updated(self, event):
        user_id = event['user_id']
        
        # Update all orders for this user
        orders = db.query(Order).filter_by(user_id=user_id).all()
        for order in orders:
            order.user_email = event['email']
            order.user_name = event['name']
        
        db.commit()
```

**Distributed Queries (API Composition):**

```python
# Query across services via API Gateway

@api_gateway.get("/reports/user-orders")
async def get_user_orders_report(user_id: int):
    """
    Generate report combining data from multiple services
    """
    # Call services in parallel
    user_task = user_service.get(f"/users/{user_id}")
    orders_task = order_service.get(f"/orders?user_id={user_id}")
    payments_task = payment_service.get(f"/payments?user_id={user_id}")
    
    user, orders, payments = await asyncio.gather(
        user_task, orders_task, payments_task
    )
    
    # Combine data
    report = {
        "user": user,
        "total_orders": len(orders),
        "total_spent": sum(p['amount'] for p in payments),
        "orders": orders
    }
    
    return report
```

**Verification:**
- [ ] Each service has its own database
- [ ] No cross-service database queries
- [ ] Data duplication strategy defined
- [ ] Event-driven cache updates working
- [ ] API composition for cross-service queries

**If This Fails:**
→ Start with logical separation (schemas in same DB)
→ Migrate to physical separation gradually
→ Use read replicas for cross-service queries initially

---

### Step 5: Implement Observability (Logging, Metrics, Tracing)

**What:** Comprehensive observability across all microservices

**How:**

**Centralized Logging (ELK Stack):**

```python
# Structured logging with correlation IDs

import logging
import json
from contextvars import ContextVar

# Context variable for request ID
request_id_var = ContextVar('request_id', default=None)

class StructuredLogger:
    """Logger that outputs JSON with context"""
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
    
    def _log(self, level, message, **kwargs):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'level': level,
            'message': message,
            'request_id': request_id_var.get(),
            **kwargs
        }
        
        self.logger.log(
            getattr(logging, level),
            json.dumps(log_data)
        )
    
    def info(self, message, **kwargs):
        self._log('INFO', message, **kwargs)
    
    def error(self, message, **kwargs):
        self._log('ERROR', message, **kwargs)

# Middleware to set request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    request_id_var.set(request_id)
    
    response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    return response

# Usage
logger = StructuredLogger('order-service')

@app.post("/orders")
async def create_order(order_data: dict):
    logger.info(
        "Creating order",
        user_id=order_data['user_id'],
        items_count=len(order_data['items'])
    )
    
    try:
        order = create_order_logic(order_data)
        logger.info("Order created", order_id=order.id)
        return order
    except Exception as e:
        logger.error(
            "Order creation failed",
            error=str(e),
            user_id=order_data['user_id']
        )
        raise
```

**Distributed Tracing (OpenTelemetry):**

```python
# Already covered in arc-004, but here's microservices-specific usage

from opentelemetry import trace
from opentelemetry.propagate import inject, extract

tracer = trace.get_tracer(__name__)

# Service A: Start trace and propagate
@app.post("/orders")
async def create_order(order_data: dict):
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("order.user_id", order_data['user_id'])
        
        # Prepare headers for propagation
        headers = {}
        inject(headers)
        
        # Call Payment Service with trace context
        payment = await http_client.post(
            "http://payment-service/payments",
            json=order_data,
            headers=headers  # Propagate trace
        )
        
        return payment

# Service B: Extract trace context
@app.post("/payments")
async def process_payment(request: Request, payment_data: dict):
    # Extract trace context from headers
    context = extract(dict(request.headers))
    
    with tracer.start_as_current_span("process_payment", context=context):
        # This span is part of same trace as create_order
        result = charge_payment(payment_data)
        return result

# Result: Complete trace across services visible in Jaeger
"""
Trace ID: abc123
  ├─ create_order (order-service) 150ms
  │  ├─ database.insert_order 20ms
  │  └─ process_payment (payment-service) 120ms
  │     ├─ validate_card 30ms
  │     ├─ charge_external_gateway 80ms
  │     └─ database.insert_payment 10ms
"""
```

**Service Mesh Observability (Istio):**

```yaml
# Istio automatically adds observability

# Metrics, traces, and logs without code changes
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
    - order-service
  http:
    - route:
        - destination:
            host: order-service
      timeout: 10s
      retries:
        attempts: 3
        perTryTimeout: 3s

# Istio exports:
# - Request latency (p50, p90, p99)
# - Request volume
# - Error rates
# - Distributed traces
# - Service dependencies
```

**Verification:**
- [ ] Centralized logging configured
- [ ] Logs include correlation IDs
- [ ] Distributed tracing working
- [ ] Metrics exported to Prometheus
- [ ] Dashboards created (Grafana)
- [ ] Alerts configured for critical metrics

**If This Fails:**
→ Start with simple stdout logging + correlation IDs
→ Use managed observability (Datadog, New Relic)
→ Add service mesh (Istio) for automatic instrumentation

---

## Verification Checklist

After completing this workflow:

- [ ] Services decomposed by business domain
- [ ] API Gateway handling routing and auth
- [ ] Service-to-service communication working
- [ ] Each service has its own database
- [ ] Event-driven async communication
- [ ] Distributed tracing configured
- [ ] Centralized logging with correlation IDs
- [ ] Circuit breakers preventing cascading failures
- [ ] Service discovery working
- [ ] Health checks on all services
- [ ] Independent deployment working

---

## Common Issues & Solutions

### Issue: Distributed monolith (tightly coupled services)

**Symptoms:**
- Services can't be deployed independently
- Changes require updating multiple services
- Synchronous calls everywhere

**Solution:**
```python
# Use event-driven architecture for decoupling

# ❌ BAD: Synchronous coupling
def create_order(order_data):
    order = create_order_in_db(order_data)
    inventory_service.reserve(order.items)  # Blocks
    email_service.send_confirmation(order)  # Blocks
    analytics_service.track(order)           # Blocks
    return order

# ✅ GOOD: Event-driven decoupling
def create_order(order_data):
    order = create_order_in_db(order_data)
    
    # Publish event (non-blocking)
    event_bus.publish('order.created', {
        'order_id': order.id,
        'user_id': order.user_id,
        'items': order.items
    })
    
    return order  # Returns immediately

# Other services react independently
@event_bus.subscribe('order.created')
def handle_order_in_inventory(event):
    reserve_inventory(event['items'])

@event_bus.subscribe('order.created')
def handle_order_in_email(event):
    send_confirmation_email(event['user_id'], event['order_id'])
```

**Prevention:**
- Prefer async communication over sync
- Use events for non-critical operations
- Design for independent deployment

---

## Best Practices

### DO:
✅ Decompose by business domain (DDD)
✅ One database per service
✅ Use API Gateway for client access
✅ Implement circuit breakers
✅ Use distributed tracing
✅ Design for failure (retries, timeouts)
✅ Automate deployment (CI/CD)
✅ Monitor everything (metrics, logs, traces)
✅ Use container orchestration (Kubernetes)
✅ Implement health checks

### DON'T:
❌ Share databases between services
❌ Create too many small services (nano-services)
❌ Use synchronous calls for everything
❌ Skip API versioning
❌ Ignore observability
❌ Deploy all services together
❌ Use distributed transactions (use sagas)
❌ Forget about security (service-to-service auth)
❌ Skip testing (integration, contract tests)
❌ Ignore operational complexity

---

## Related Workflows

**Prerequisites:**
- `arc-001`: API Design Best Practices - Service APIs
- `arc-004`: Distributed Systems Patterns - Foundation patterns
- `arc-005`: Event Driven Architecture - Async communication

**Next Steps:**
- `devops-006`: Container Orchestration - Deploy microservices
- `devops-008`: Application Performance Monitoring - Monitor services
- `qa-008`: Integration Testing - Test service interactions

**Alternatives:**
- Monolithic architecture (simpler, less operational overhead)
- Modular monolith (middle ground)
- Serverless (managed infrastructure)

---

## Tags
`architecture` `microservices` `patterns` `distributed-systems` `api-gateway` `service-mesh` `docker` `kubernetes` `observability`
