# Distributed Systems Patterns

**ID:** arc-004  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design patterns and best practices for building reliable, scalable distributed systems

**Why:** Distributed systems patterns solve common challenges like network failures (50% of issues), data consistency, service coordination, and enable systems to scale horizontally while maintaining reliability

**When to use:**
- Building microservices architectures
- Designing systems that span multiple servers/data centers
- Implementing scalable cloud-native applications
- Handling network partitions and failures
- Coordinating distributed transactions
- Managing distributed data consistency

---

## Prerequisites

**Required:**
- [ ] Understanding of CAP theorem (Consistency, Availability, Partition tolerance)
- [ ] Knowledge of network protocols (HTTP, TCP, gRPC)
- [ ] Familiarity with message queues (RabbitMQ, Kafka)
- [ ] Understanding of eventual consistency
- [ ] Basic distributed computing concepts (consensus, replication)

**Check before starting:**
```bash
# Check if you have distributed system tools
docker --version
kubectl version --client
redis-cli --version

# Check message brokers
rabbitmqctl status  # or
kafka-topics.sh --version

# Check service mesh tools
istioctl version
linkerd version
```

---

## Implementation Steps

### Step 1: Choose Consistency Model (CAP Theorem)

**What:** Understand trade-offs and select appropriate consistency model for your use case

**How:**

**CAP Theorem Explained:**

```
CAP Theorem: You can only have 2 of 3 guarantees:
- Consistency: All nodes see the same data at the same time
- Availability: Every request receives a response
- Partition Tolerance: System works despite network failures

Reality: Partition tolerance is mandatory (networks fail)
Therefore: Choose between Consistency (CP) or Availability (AP)

┌─────────────────┬──────────────┬────────────────┐
│ System Type     │ Guarantees   │ Use Case       │
├─────────────────┼──────────────┼────────────────┤
│ CP (Strong      │ Consistency  │ Banking,       │
│ Consistency)    │ + Partition  │ Inventory,     │
│                 │ Tolerance    │ Reservations   │
├─────────────────┼──────────────┼────────────────┤
│ AP (Eventually  │ Availability │ Social Media,  │
│ Consistent)     │ + Partition  │ Caching,       │
│                 │ Tolerance    │ Read-heavy     │
└─────────────────┴──────────────┴────────────────┘
```

**Consistency Models:**

```python
# 1. Strong Consistency (CP)
# All reads see the most recent write
# Example: Banking transactions

class StronglyConsistentService:
    """
    Uses distributed consensus (Raft, Paxos)
    Trades availability for consistency
    """
    def transfer_money(self, from_account, to_account, amount):
        # Use distributed lock to ensure consistency
        with distributed_lock(f"account:{from_account}"):
            with distributed_lock(f"account:{to_account}"):
                # Both accounts locked - strong consistency
                balance = self.get_balance(from_account)
                if balance >= amount:
                    self.debit(from_account, amount)
                    self.credit(to_account, amount)
                    return True
                return False

# 2. Eventual Consistency (AP)
# Reads may not see latest write immediately
# Example: Social media likes

class EventuallyConsistentService:
    """
    Prioritizes availability over consistency
    Updates propagate asynchronously
    """
    def like_post(self, user_id, post_id):
        # Write locally immediately
        self.local_db.increment_likes(post_id)
        
        # Propagate asynchronously to other nodes
        self.message_queue.publish({
            'event': 'post_liked',
            'post_id': post_id,
            'user_id': user_id,
            'timestamp': time.time()
        })
        
        # Return immediately (available)
        return True

# 3. Causal Consistency
# Reads see writes in causal order
# Example: Comments (see parent before replies)

class CausallyConsistentService:
    """
    Maintains causal relationships
    Parent writes visible before child writes
    """
    def post_comment(self, comment_id, parent_id, content):
        # Ensure parent exists before allowing reply
        if parent_id:
            parent = self.get_comment(parent_id)
            if not parent:
                raise ParentNotFoundError()
        
        # Write comment with causal ordering
        self.write_with_vector_clock(comment_id, {
            'content': content,
            'parent_id': parent_id,
            'vector_clock': self.increment_vector_clock()
        })

# 4. Session Consistency
# Reads see writes from same session
# Example: Shopping cart

class SessionConsistentService:
    """
    Guarantees consistency within a session
    Different sessions may see different states
    """
    def add_to_cart(self, session_id, item_id):
        # Route all session requests to same node
        node = self.get_node_for_session(session_id)
        
        # Within session, all reads/writes consistent
        return node.add_item(session_id, item_id)
```

**Decision Matrix:**

```python
def choose_consistency_model(requirements):
    """Helper to choose consistency model"""
    
    if requirements['financial_transactions']:
        return 'STRONG_CONSISTENCY'  # CP
    
    elif requirements['realtime_updates_critical']:
        return 'STRONG_CONSISTENCY'  # CP
    
    elif requirements['high_availability_critical']:
        return 'EVENTUAL_CONSISTENCY'  # AP
    
    elif requirements['ordered_operations']:
        return 'CAUSAL_CONSISTENCY'
    
    elif requirements['user_session_based']:
        return 'SESSION_CONSISTENCY'
    
    else:
        return 'EVENTUAL_CONSISTENCY'  # Default for scalability

# Examples:
print(choose_consistency_model({
    'financial_transactions': True,
    'high_availability_critical': False
}))  # → 'STRONG_CONSISTENCY'

print(choose_consistency_model({
    'financial_transactions': False,
    'high_availability_critical': True
}))  # → 'EVENTUAL_CONSISTENCY'
```

**Verification:**
- [ ] Consistency requirements documented
- [ ] CAP trade-offs understood
- [ ] Consistency model chosen for each service
- [ ] Team understands implications

**If This Fails:**
→ Start with eventual consistency (simpler)
→ Add strong consistency only where required
→ Use managed services (DynamoDB, CosmosDB) that handle consistency

---

### Step 2: Implement Service Discovery Pattern

**What:** Enable services to find and communicate with each other dynamically

**How:**

**Service Discovery Patterns:**

```python
# Pattern 1: Client-Side Discovery
# Client queries registry and chooses instance

class ClientSideDiscovery:
    """
    Client queries service registry (Consul, Eureka)
    Client implements load balancing
    """
    def __init__(self, consul_client):
        self.consul = consul_client
    
    def call_service(self, service_name, endpoint):
        # Get all healthy instances
        instances = self.consul.health.service(
            service_name,
            passing=True  # Only healthy instances
        )[1]
        
        if not instances:
            raise ServiceUnavailableError(service_name)
        
        # Client-side load balancing
        instance = self.load_balance(instances)
        
        # Make request
        url = f"http://{instance['Address']}:{instance['Port']}{endpoint}"
        return requests.get(url)
    
    def load_balance(self, instances):
        """Simple round-robin load balancing"""
        import random
        return random.choice(instances)['Service']

# Pattern 2: Server-Side Discovery
# Load balancer queries registry

class ServerSideDiscovery:
    """
    Load balancer (nginx, HAProxy) handles discovery
    Client only knows about load balancer
    """
    # nginx.conf with Consul template
    """
    upstream user_service {
        {{range service "user-service"}}
        server {{.Address}}:{{.Port}};
        {{end}}
    }
    
    server {
        location /api/users {
            proxy_pass http://user_service;
        }
    }
    """
    
    def call_service(self, endpoint):
        # Client only knows about load balancer
        return requests.get(f"http://loadbalancer{endpoint}")

# Pattern 3: Service Mesh
# Sidecar proxy handles discovery

class ServiceMeshDiscovery:
    """
    Service mesh (Istio, Linkerd) handles discovery
    Services communicate via sidecar proxies
    """
    # Kubernetes service definition
    """
    apiVersion: v1
    kind: Service
    metadata:
      name: user-service
    spec:
      selector:
        app: user-service
      ports:
      - port: 80
        targetPort: 8080
    """
    
    def call_service(self, service_name, endpoint):
        # Service mesh DNS resolution
        # Just use service name as hostname
        url = f"http://{service_name}{endpoint}"
        return requests.get(url)
```

**Service Registration:**

```python
# Consul service registration
import consul

class ServiceRegistrar:
    """Register service with Consul"""
    
    def __init__(self, consul_host='localhost', consul_port=8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
    
    def register(self, service_name, service_port, health_check_url):
        """Register service on startup"""
        self.consul.agent.service.register(
            name=service_name,
            service_id=f"{service_name}-{socket.gethostname()}",
            address=socket.gethostname(),
            port=service_port,
            check=consul.Check.http(
                url=health_check_url,
                interval='10s',
                timeout='5s',
                deregister='30s'  # Auto-deregister if unhealthy
            ),
            tags=['v1', 'production']
        )
        print(f"✅ Registered {service_name} with Consul")
    
    def deregister(self, service_id):
        """Deregister on shutdown"""
        self.consul.agent.service.deregister(service_id)
        print(f"Deregistered {service_id}")

# FastAPI with automatic registration
from fastapi import FastAPI
import atexit

app = FastAPI()
registrar = ServiceRegistrar()

@app.on_event("startup")
async def startup():
    registrar.register(
        service_name='user-service',
        service_port=8000,
        health_check_url='http://localhost:8000/health'
    )

@app.on_event("shutdown")
async def shutdown():
    registrar.deregister('user-service')

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Kubernetes Service Discovery:**

```yaml
# Kubernetes handles service discovery natively
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP  # Internal service discovery

---
# Services can discover each other via DNS
# http://user-service.default.svc.cluster.local
```

**Verification:**
- [ ] Services registered with discovery system
- [ ] Health checks configured
- [ ] Load balancing implemented
- [ ] Service discovery working across instances
- [ ] Failed instances automatically deregistered

**If This Fails:**
→ Use Kubernetes built-in service discovery (easiest)
→ Start with DNS-based discovery
→ Add Consul/Eureka for advanced features

---

### Step 3: Implement Circuit Breaker Pattern

**What:** Prevent cascading failures by failing fast when dependencies are down

**How:**

**Circuit Breaker States:**

```
CLOSED (Normal)                 OPEN (Failing)
┌─────────────┐                ┌─────────────┐
│  Requests   │  Failures >    │   Reject    │
│   Pass      │  Threshold     │   Fast      │
│  Through    │────────────────→│             │
└─────────────┘                └─────────────┘
       ↑                              │
       │                              │ Timeout
       │                              │
       │         HALF-OPEN           │
       │        ┌─────────────┐      │
       └────────│  Try One    │←─────┘
         Success│  Request    │
                └─────────────┘
```

**Circuit Breaker Implementation:**

```python
import time
from enum import Enum
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    Prevents cascading failures
    """
    def __init__(
        self,
        failure_threshold=5,      # Open after 5 failures
        success_threshold=2,      # Close after 2 successes
        timeout=60,               # Try again after 60 seconds
        expected_exception=Exception
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Try again after {self._time_until_retry()}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._close()
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self._open()
    
    def _open(self):
        """Open circuit (stop allowing requests)"""
        self.state = CircuitState.OPEN
        self.success_count = 0
        print(f"⚠️  Circuit breaker OPEN")
    
    def _close(self):
        """Close circuit (allow requests again)"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        print(f"✅ Circuit breaker CLOSED")
    
    def _should_attempt_reset(self):
        """Check if we should try half-open"""
        return (
            time.time() - self.last_failure_time >= self.timeout
        )
    
    def _time_until_retry(self):
        """Time until circuit attempts reset"""
        if self.last_failure_time:
            elapsed = time.time() - self.last_failure_time
            return max(0, self.timeout - elapsed)
        return 0

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

# Decorator for easy use
def circuit_breaker(
    failure_threshold=5,
    success_threshold=2,
    timeout=60
):
    """Decorator to add circuit breaker to function"""
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        success_threshold=success_threshold,
        timeout=timeout
    )
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        wrapper.circuit_breaker = breaker
        return wrapper
    return decorator

# Usage
@circuit_breaker(failure_threshold=3, timeout=30)
def call_external_api():
    """Call external API with circuit breaker"""
    response = requests.get('https://api.example.com/data', timeout=5)
    response.raise_for_status()
    return response.json()

# Try calling
try:
    data = call_external_api()
except CircuitBreakerOpenError as e:
    print(f"Circuit open: {e}")
    # Use fallback data
    data = get_cached_data()
except requests.RequestException as e:
    print(f"API error: {e}")
    # Will trigger circuit breaker
```

**Circuit Breaker with Metrics:**

```python
from prometheus_client import Counter, Gauge

class InstrumentedCircuitBreaker(CircuitBreaker):
    """Circuit breaker with Prometheus metrics"""
    
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        
        # Metrics
        self.state_gauge = Gauge(
            f'circuit_breaker_state_{name}',
            f'Circuit breaker state for {name}',
            ['state']
        )
        
        self.calls_counter = Counter(
            f'circuit_breaker_calls_{name}',
            f'Circuit breaker calls for {name}',
            ['result']
        )
        
        self._update_metrics()
    
    def _open(self):
        super()._open()
        self._update_metrics()
    
    def _close(self):
        super()._close()
        self._update_metrics()
    
    def _on_success(self):
        super()._on_success()
        self.calls_counter.labels(result='success').inc()
        self._update_metrics()
    
    def _on_failure(self):
        super()._on_failure()
        self.calls_counter.labels(result='failure').inc()
        self._update_metrics()
    
    def _update_metrics(self):
        """Update Prometheus metrics"""
        for state in CircuitState:
            self.state_gauge.labels(state=state.value).set(
                1 if self.state == state else 0
            )
```

**Verification:**
- [ ] Circuit breaker opens after failures
- [ ] Requests fail fast when open
- [ ] Circuit attempts reset after timeout
- [ ] Circuit closes after successful probes
- [ ] Metrics tracked for monitoring

**If This Fails:**
→ Start with simple retry logic
→ Use library like `pybreaker` or `resilience4j`
→ Test circuit breaker behavior explicitly

---

### Step 4: Implement Distributed Tracing

**What:** Track requests across multiple services for debugging and performance analysis

**How:**

**OpenTelemetry Distributed Tracing:**

```python
# Install: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Setup tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Setup Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)

# Add span processor
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Auto-instrument FastAPI
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

# Auto-instrument requests library
RequestsInstrumentor().instrument()

# Manual tracing
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Create span for database query
    with tracer.start_as_current_span("database.query.user"):
        user = await db.query(User).get(user_id)
    
    # Create span for external API call
    with tracer.start_as_current_span("api.call.permissions"):
        permissions = requests.get(f"http://auth-service/permissions/{user_id}")
    
    return {"user": user, "permissions": permissions.json()}

# Add custom attributes to spans
@app.post("/orders")
async def create_order(order_data: dict):
    span = trace.get_current_span()
    span.set_attribute("order.amount", order_data['amount'])
    span.set_attribute("order.items_count", len(order_data['items']))
    
    # Process order...
    with tracer.start_as_current_span("payment.process") as payment_span:
        payment_span.set_attribute("payment.method", order_data['payment_method'])
        result = process_payment(order_data)
    
    return result
```

**Trace Context Propagation:**

```python
# Service A: Create trace and propagate
from opentelemetry.propagate import inject

def call_service_b():
    # Create headers dict for propagation
    headers = {}
    inject(headers)  # Injects trace context into headers
    
    # Call Service B with trace context
    response = requests.get(
        'http://service-b/api/data',
        headers=headers
    )
    return response.json()

# Service B: Extract trace context
from opentelemetry.propagate import extract

@app.get("/api/data")
async def get_data(request: Request):
    # Extract trace context from headers
    context = extract(dict(request.headers))
    
    # This span will be part of the same trace
    with tracer.start_as_current_span("service_b.get_data", context=context):
        data = fetch_data()
        return data
```

**Distributed Tracing Visualization:**

```
Request Flow with Trace IDs:

Client Request [trace_id: abc123]
    │
    ├─→ API Gateway [span_id: 001] (5ms)
    │   │
    │   ├─→ User Service [span_id: 002] (20ms)
    │   │   │
    │   │   ├─→ Database Query [span_id: 003] (15ms)
    │   │   └─→ Cache Check [span_id: 004] (2ms)
    │   │
    │   └─→ Auth Service [span_id: 005] (30ms)
    │       │
    │       └─→ Redis Lookup [span_id: 006] (3ms)
    │
    └─→ Response (Total: 55ms)

All spans share trace_id: abc123
Parent-child relationships preserved
```

**Verification:**
- [ ] Traces visible in Jaeger/Zipkin UI
- [ ] Trace context propagated across services
- [ ] Spans have meaningful names
- [ ] Custom attributes added
- [ ] Latency breakdown visible

**If This Fails:**
→ Start with logging request IDs
→ Use managed tracing (AWS X-Ray, Google Cloud Trace)
→ Ensure trace context headers propagated

---

### Step 5: Implement Saga Pattern for Distributed Transactions

**What:** Manage distributed transactions across multiple services without 2PC

**How:**

**Saga Pattern Types:**

```python
# Pattern 1: Choreography-Based Saga
# Services publish events, others react

class OrderSagaChoreography:
    """
    Each service publishes events
    Other services listen and react
    No central coordinator
    """
    
    # Order Service
    def create_order(self, order_data):
        order = Order.create(order_data)
        
        # Publish event
        event_bus.publish('order.created', {
            'order_id': order.id,
            'user_id': order.user_id,
            'amount': order.amount
        })
        
        return order
    
    # Payment Service (listens for order.created)
    @event_bus.subscribe('order.created')
    def process_payment(self, event):
        try:
            payment = charge_payment(event['amount'])
            
            # Publish success
            event_bus.publish('payment.completed', {
                'order_id': event['order_id'],
                'payment_id': payment.id
            })
        except PaymentError:
            # Publish failure (triggers compensation)
            event_bus.publish('payment.failed', {
                'order_id': event['order_id'],
                'reason': 'insufficient_funds'
            })
    
    # Inventory Service (listens for payment.completed)
    @event_bus.subscribe('payment.completed')
    def reserve_inventory(self, event):
        try:
            inventory.reserve(event['order_id'])
            
            event_bus.publish('inventory.reserved', {
                'order_id': event['order_id']
            })
        except OutOfStockError:
            # Compensate payment
            event_bus.publish('inventory.failed', {
                'order_id': event['order_id']
            })
    
    # Order Service (listens for failures)
    @event_bus.subscribe('payment.failed')
    @event_bus.subscribe('inventory.failed')
    def cancel_order(self, event):
        order = Order.get(event['order_id'])
        order.cancel()
        
        # Trigger compensating transactions
        event_bus.publish('order.cancelled', {
            'order_id': event['order_id']
        })

# Pattern 2: Orchestration-Based Saga
# Central coordinator manages saga

class OrderSagaOrchestrator:
    """
    Central orchestrator coordinates saga
    Explicitly manages compensations
    """
    
    def __init__(self):
        self.saga_log = SagaLog()
    
    async def execute_order_saga(self, order_data):
        saga_id = self.saga_log.start_saga('create_order')
        
        try:
            # Step 1: Create Order
            order = await self.create_order_step(saga_id, order_data)
            
            # Step 2: Process Payment
            payment = await self.process_payment_step(saga_id, order)
            
            # Step 3: Reserve Inventory
            reservation = await self.reserve_inventory_step(saga_id, order)
            
            # Step 4: Send Notification
            await self.send_notification_step(saga_id, order)
            
            # Success - mark saga complete
            self.saga_log.complete_saga(saga_id)
            return order
            
        except SagaStepError as e:
            # Failure - run compensating transactions
            await self.compensate(saga_id)
            raise
    
    async def create_order_step(self, saga_id, order_data):
        """Step 1: Create order"""
        self.saga_log.log_step(saga_id, 'create_order', 'started')
        
        try:
            order = await order_service.create(order_data)
            self.saga_log.log_step(saga_id, 'create_order', 'completed', 
                                   data={'order_id': order.id})
            return order
        except Exception as e:
            self.saga_log.log_step(saga_id, 'create_order', 'failed')
            raise SagaStepError('create_order', e)
    
    async def process_payment_step(self, saga_id, order):
        """Step 2: Process payment"""
        self.saga_log.log_step(saga_id, 'process_payment', 'started')
        
        try:
            payment = await payment_service.charge(
                order.user_id,
                order.amount
            )
            self.saga_log.log_step(saga_id, 'process_payment', 'completed',
                                   data={'payment_id': payment.id})
            return payment
        except PaymentError as e:
            self.saga_log.log_step(saga_id, 'process_payment', 'failed')
            raise SagaStepError('process_payment', e)
    
    async def reserve_inventory_step(self, saga_id, order):
        """Step 3: Reserve inventory"""
        self.saga_log.log_step(saga_id, 'reserve_inventory', 'started')
        
        try:
            reservation = await inventory_service.reserve(order.items)
            self.saga_log.log_step(saga_id, 'reserve_inventory', 'completed',
                                   data={'reservation_id': reservation.id})
            return reservation
        except OutOfStockError as e:
            self.saga_log.log_step(saga_id, 'reserve_inventory', 'failed')
            raise SagaStepError('reserve_inventory', e)
    
    async def compensate(self, saga_id):
        """Run compensating transactions in reverse order"""
        print(f"🔄 Running compensations for saga {saga_id}")
        
        steps = self.saga_log.get_completed_steps(saga_id)
        
        # Compensate in reverse order
        for step in reversed(steps):
            if step['name'] == 'reserve_inventory':
                await inventory_service.release(step['data']['reservation_id'])
            
            elif step['name'] == 'process_payment':
                await payment_service.refund(step['data']['payment_id'])
            
            elif step['name'] == 'create_order':
                await order_service.cancel(step['data']['order_id'])
            
            self.saga_log.log_compensation(saga_id, step['name'])
        
        self.saga_log.mark_compensated(saga_id)
        print(f"✅ Compensations completed for saga {saga_id}")

class SagaLog:
    """Persistent log of saga execution"""
    
    def __init__(self):
        self.db = database_connection()
    
    def start_saga(self, saga_type):
        saga_id = str(uuid.uuid4())
        self.db.execute(
            "INSERT INTO saga_log (id, type, status, created_at) "
            "VALUES (?, ?, ?, ?)",
            (saga_id, saga_type, 'started', datetime.utcnow())
        )
        return saga_id
    
    def log_step(self, saga_id, step_name, status, data=None):
        self.db.execute(
            "INSERT INTO saga_steps (saga_id, step_name, status, data, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (saga_id, step_name, status, json.dumps(data), datetime.utcnow())
        )
    
    def get_completed_steps(self, saga_id):
        return self.db.query(
            "SELECT * FROM saga_steps "
            "WHERE saga_id = ? AND status = 'completed' "
            "ORDER BY created_at ASC",
            (saga_id,)
        )
    
    def complete_saga(self, saga_id):
        self.db.execute(
            "UPDATE saga_log SET status = 'completed' WHERE id = ?",
            (saga_id,)
        )
    
    def mark_compensated(self, saga_id):
        self.db.execute(
            "UPDATE saga_log SET status = 'compensated' WHERE id = ?",
            (saga_id,)
        )
```

**Saga Decision Matrix:**

```
Choreography:
✅ Simpler for simple workflows (2-3 services)
✅ No single point of failure
❌ Hard to track saga state
❌ Difficult to debug
❌ Tight coupling through events

Orchestration:
✅ Clear saga state and progress
✅ Easier to debug and monitor
✅ Centralized compensation logic
❌ Orchestrator is single point of failure
❌ More complex implementation

Recommendation: Use Orchestration for complex workflows (4+ services)
```

**Verification:**
- [ ] Saga completes successfully in happy path
- [ ] Compensations run on failures
- [ ] Saga state persisted (can recover from crashes)
- [ ] Idempotent operations (can retry safely)
- [ ] Timeouts configured for each step

**If This Fails:**
→ Start with choreography for simple workflows
→ Use event sourcing to track saga state
→ Add saga recovery process for crashed sagas

---

### Step 6: Implement Leader Election and Consensus

**What:** Coordinate distributed systems using consensus algorithms

**How:**

**Leader Election with Etcd:**

```python
# Install: pip install python-etcd3

import etcd3
import time
from threading import Thread

class LeaderElection:
    """
    Leader election using Etcd
    Only one instance becomes leader at a time
    """
    
    def __init__(self, etcd_host='localhost', etcd_port=2379):
        self.client = etcd3.client(host=etcd_host, port=etcd_port)
        self.lease = None
        self.is_leader = False
        self.election_key = '/leader/election'
    
    def run_for_leader(self, instance_id, on_elected, on_lost):
        """
        Attempt to become leader
        Calls on_elected() when this instance becomes leader
        Calls on_lost() when leadership is lost
        """
        # Create lease (TTL = 10 seconds)
        self.lease = self.client.lease(ttl=10)
        
        while True:
            try:
                # Try to acquire leader lock
                success = self.client.transaction(
                    compare=[
                        self.client.transactions.version(self.election_key) == 0
                    ],
                    success=[
                        self.client.transactions.put(
                            self.election_key,
                            instance_id,
                            lease=self.lease
                        )
                    ],
                    failure=[]
                )[0]
                
                if success and not self.is_leader:
                    # Became leader
                    self.is_leader = True
                    print(f"✅ {instance_id} became LEADER")
                    on_elected()
                    
                    # Keep lease alive
                    self._keep_lease_alive()
                
                elif not success:
                    # Not leader, watch for leader changes
                    if self.is_leader:
                        # Lost leadership
                        self.is_leader = False
                        print(f"⚠️  {instance_id} lost leadership")
                        on_lost()
                    
                    # Wait and retry
                    time.sleep(1)
                
            except Exception as e:
                print(f"Leader election error: {e}")
                if self.is_leader:
                    self.is_leader = False
                    on_lost()
                time.sleep(1)
    
    def _keep_lease_alive(self):
        """Refresh lease to maintain leadership"""
        def refresh():
            while self.is_leader:
                try:
                    self.lease.refresh()
                    time.sleep(5)
                except:
                    self.is_leader = False
                    break
        
        Thread(target=refresh, daemon=True).start()
    
    def resign(self):
        """Voluntarily give up leadership"""
        if self.lease:
            self.lease.revoke()
        self.is_leader = False

# Usage
def on_elected():
    """Called when this instance becomes leader"""
    print("I am now the leader!")
    # Start leader-only tasks (cron jobs, aggregations, etc.)
    start_scheduled_jobs()

def on_lost():
    """Called when this instance loses leadership"""
    print("I am no longer the leader")
    # Stop leader-only tasks
    stop_scheduled_jobs()

instance_id = socket.gethostname()
election = LeaderElection()

# Run election in background thread
Thread(
    target=election.run_for_leader,
    args=(instance_id, on_elected, on_lost),
    daemon=True
).start()
```

**Distributed Locking with Redis:**

```python
import redis
import time
import uuid

class DistributedLock:
    """
    Distributed lock using Redis
    Prevents multiple instances from running same task
    """
    
    def __init__(self, redis_client, lock_name, timeout=10):
        self.redis = redis_client
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.identifier = str(uuid.uuid4())
    
    def acquire(self, blocking=True, block_timeout=None):
        """Acquire lock"""
        end_time = time.time() + block_timeout if block_timeout else None
        
        while True:
            # Try to set lock with NX (only if not exists)
            if self.redis.set(
                self.lock_name,
                self.identifier,
                nx=True,
                ex=self.timeout
            ):
                return True
            
            if not blocking:
                return False
            
            if end_time and time.time() > end_time:
                return False
            
            time.sleep(0.1)
    
    def release(self):
        """Release lock (only if we own it)"""
        # Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        self.redis.eval(lua_script, 1, self.lock_name, self.identifier)
    
    def __enter__(self):
        """Context manager support"""
        if not self.acquire():
            raise LockError("Could not acquire lock")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

# Usage
lock = DistributedLock(redis_client, "process_payments")

with lock:
    # Only one instance executes this at a time
    process_pending_payments()
```

**Verification:**
- [ ] Only one leader elected at a time
- [ ] New leader elected when current leader fails
- [ ] Distributed locks prevent duplicate work
- [ ] Locks released on crashes (TTL)
- [ ] No split-brain scenarios

**If This Fails:**
→ Use managed services (AWS DynamoDB Locks, Consul)
→ Start with simple leader election before complex consensus
→ Test failure scenarios explicitly

---

## Verification Checklist

After completing this workflow:

- [ ] Consistency model chosen for each service
- [ ] Service discovery implemented
- [ ] Circuit breakers prevent cascading failures
- [ ] Distributed tracing configured
- [ ] Saga pattern handles distributed transactions
- [ ] Leader election for singleton tasks
- [ ] Distributed locks prevent duplicate work
- [ ] Timeouts configured on all network calls
- [ ] Retry logic with exponential backoff
- [ ] Monitoring and alerting in place

---

## Common Issues & Solutions

### Issue: Split-brain scenarios in distributed systems

**Symptoms:**
- Two leaders elected simultaneously
- Duplicate processing of tasks
- Inconsistent state across nodes

**Solution:**
```python
# Use quorum-based consensus (majority wins)

class QuorumBasedLeaderElection:
    """
    Require majority of nodes to agree on leader
    Prevents split-brain
    """
    
    def __init__(self, cluster_size):
        self.cluster_size = cluster_size
        self.quorum_size = (cluster_size // 2) + 1
    
    def elect_leader(self, votes):
        """Check if candidate has quorum"""
        vote_counts = {}
        for vote in votes:
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        for candidate, count in vote_counts.items():
            if count >= self.quorum_size:
                return candidate
        
        return None  # No quorum

# Example: 5-node cluster needs 3 votes
election = QuorumBasedLeaderElection(cluster_size=5)
winner = election.elect_leader(['node1', 'node1', 'node1', 'node2', 'node3'])
print(winner)  # 'node1' (has quorum)
```

**Prevention:**
- Use proven consensus algorithms (Raft, Paxos)
- Require quorum for decisions
- Use managed services (Consul, Etcd, Zookeeper)
- Test network partition scenarios

---

### Issue: Cascading failures across services

**Symptoms:**
- One slow service causes entire system to fail
- Timeout errors everywhere
- Resource exhaustion

**Solution:**
```python
# Implement bulkhead pattern + circuit breakers

from concurrent.futures import ThreadPoolExecutor

class BulkheadPattern:
    """
    Isolate resources per service
    Failure in one service doesn't affect others
    """
    
    def __init__(self):
        # Separate thread pools per service
        self.payment_pool = ThreadPoolExecutor(max_workers=10)
        self.inventory_pool = ThreadPoolExecutor(max_workers=10)
        self.notification_pool = ThreadPoolExecutor(max_workers=5)
        
        # Circuit breakers per service
        self.payment_breaker = CircuitBreaker()
        self.inventory_breaker = CircuitBreaker()
    
    def call_payment_service(self, *args):
        """Isolated call to payment service"""
        future = self.payment_pool.submit(
            self.payment_breaker.call,
            payment_api.charge,
            *args
        )
        return future.result(timeout=5)
    
    def call_inventory_service(self, *args):
        """Isolated call to inventory service"""
        future = self.inventory_pool.submit(
            self.inventory_breaker.call,
            inventory_api.reserve,
            *args
        )
        return future.result(timeout=5)
```

**Prevention:**
- Implement circuit breakers
- Use bulkhead pattern (resource isolation)
- Set aggressive timeouts
- Implement graceful degradation

---

## Best Practices

### DO:
✅ Choose consistency model explicitly (CP vs AP)
✅ Implement circuit breakers for all external calls
✅ Use distributed tracing for debugging
✅ Handle network partitions gracefully
✅ Set timeouts on all network operations
✅ Implement idempotent operations
✅ Use message queues for async communication
✅ Implement retry with exponential backoff
✅ Monitor distributed system health
✅ Use saga pattern for distributed transactions

### DON'T:
❌ Assume network is reliable
❌ Use distributed transactions (2PC) in microservices
❌ Ignore partial failures
❌ Forget to implement timeouts
❌ Couple services tightly
❌ Share databases between services
❌ Implement your own consensus algorithm
❌ Ignore CAP theorem trade-offs
❌ Skip testing failure scenarios
❌ Assume clocks are synchronized

---

## Related Workflows

**Prerequisites:**
- `arc-001`: API Design Best Practices - Service interfaces
- `arc-009`: Architecture Decision Records - Document patterns
- `devops-006`: Container Orchestration - Kubernetes deployment

**Next Steps:**
- `arc-005`: Event Driven Architecture - Async messaging
- `arc-006`: Microservices Patterns - Service decomposition
- `devops-008`: Application Performance Monitoring - Distributed monitoring

**Alternatives:**
- Monolithic architecture (simpler, no distributed challenges)
- Serverless architecture (managed scaling, simpler operations)

---

## Tags
`architecture` `distributed-systems` `patterns` `microservices` `scalability` `reliability` `circuit-breaker` `saga` `consensus` `cap-theorem`
