# System Architecture Design

**ID:** arc-008  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 60-120 minutes  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Comprehensive system architecture design workflow for creating scalable, maintainable, and robust software systems

**Why:** 
- Prevents costly redesigns and technical debt accumulation
- Ensures system meets functional and non-functional requirements
- Provides clear blueprint for implementation teams
- Facilitates communication between stakeholders
- Enables informed technology decisions and trade-off analysis

**When to use:**
- Starting new projects or products
- Major system refactoring or modernization
- Migrating to new technology stacks
- Scaling existing systems to handle growth
- Architecture reviews and audits
- Merging systems after acquisitions
- Addressing significant technical debt

---

## Prerequisites

**Required:**
- [ ] Business requirements and objectives documented
- [ ] Stakeholder interviews completed
- [ ] Current system analysis (for migrations/refactoring)
- [ ] Non-functional requirements defined (performance, security, compliance)
- [ ] Budget and timeline constraints identified
- [ ] Team capabilities and skills assessed

**Helpful:**
- [ ] Understanding of domain-driven design principles
- [ ] Knowledge of architectural patterns and styles
- [ ] Experience with similar system architectures
- [ ] Familiarity with target technology ecosystem
- [ ] Access to architecture decision records (ADRs)

---

## Implementation Steps

### Step 1: Gather and Analyze Requirements

**What:** Collect comprehensive functional and non-functional requirements from all stakeholders

**How:**

1. **Document functional requirements:**
```yaml
# requirements.yaml
functional_requirements:
  user_management:
    - User registration and authentication
    - Role-based access control (RBAC)
    - Profile management
  
  core_features:
    - Real-time data processing
    - Batch job scheduling
    - Reporting and analytics
  
  integrations:
    - Third-party payment gateway
    - Email notification service
    - CRM system sync
```

2. **Define non-functional requirements:**
```yaml
non_functional_requirements:
  performance:
    - Response time: < 200ms (p95)
    - Throughput: 10,000 requests/second
    - Concurrent users: 100,000
  
  scalability:
    - Horizontal scaling capability
    - Auto-scaling based on load
    - Multi-region deployment
  
  availability:
    - Uptime: 99.9% (3 nines)
    - Recovery time objective (RTO): 1 hour
    - Recovery point objective (RPO): 5 minutes
  
  security:
    - OWASP Top 10 compliance
    - SOC 2 Type II certification
    - GDPR compliance
    - End-to-end encryption for sensitive data
  
  maintainability:
    - Code coverage: > 80%
    - Deployment frequency: Multiple times per day
    - Mean time to recovery (MTTR): < 1 hour
  
  constraints:
    - Budget: $500K annually
    - Timeline: 6 months to MVP
    - Team size: 8 developers
    - Technology: Must use existing cloud provider (AWS)
```

3. **Create user journey maps:**
```python
# Example: User journey for key workflows
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TouchPoint:
    step: str
    system: str
    latency_sla: str
    failure_mode: str

class UserJourney:
    def __init__(self, name: str):
        self.name = name
        self.touchpoints: List[TouchPoint] = []
    
    def add_touchpoint(self, step: str, system: str, 
                       latency_sla: str, failure_mode: str):
        self.touchpoints.append(
            TouchPoint(step, system, latency_sla, failure_mode)
        )

# E-commerce checkout journey
checkout_journey = UserJourney("Checkout Flow")
checkout_journey.add_touchpoint(
    "Add to Cart", "Product Service", "< 100ms", "Degrade to async add"
)
checkout_journey.add_touchpoint(
    "View Cart", "Cart Service", "< 150ms", "Show cached cart"
)
checkout_journey.add_touchpoint(
    "Payment", "Payment Gateway", "< 2s", "Queue for retry"
)
checkout_journey.add_touchpoint(
    "Confirmation", "Order Service", "< 300ms", "Async processing"
)
```

**Verification:**
- [ ] All stakeholders have reviewed and approved requirements
- [ ] Non-functional requirements are quantified (not just "fast" or "secure")
- [ ] Constraints and trade-offs are explicitly documented
- [ ] Success metrics and KPIs are defined

---

### Step 2: Select Architecture Style and Patterns

**What:** Choose the high-level architecture style that best fits your requirements

**How:**

1. **Evaluate architecture styles:**

```markdown
## Architecture Style Comparison

### Monolithic Architecture
**Pros:**
- Simple development and deployment
- Easy to test end-to-end
- Lower operational complexity
- Good for small teams

**Cons:**
- Scaling entire application (not components)
- Technology stack lock-in
- Deployment risk (all or nothing)
- Longer build times as code grows

**Best for:** MVPs, small applications, simple domains

---

### Microservices Architecture
**Pros:**
- Independent scaling of services
- Technology diversity
- Team autonomy
- Fault isolation

**Cons:**
- Distributed system complexity
- Data consistency challenges
- Operational overhead
- Network latency

**Best for:** Large systems, multiple teams, evolving requirements

---

### Event-Driven Architecture
**Pros:**
- Loose coupling
- Asynchronous processing
- Easy to add new consumers
- Natural fit for real-time systems

**Cons:**
- Eventual consistency
- Debugging complexity
- Message ordering challenges
- Event schema evolution

**Best for:** Real-time processing, IoT, complex event processing

---

### Serverless Architecture
**Pros:**
- No server management
- Automatic scaling
- Pay per use
- Fast time to market

**Cons:**
- Vendor lock-in
- Cold start latency
- Limited execution time
- Debugging challenges

**Best for:** Variable traffic, background jobs, APIs
```

2. **Decision matrix for architecture style:**

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict

class ArchitectureStyle(Enum):
    MONOLITHIC = "monolithic"
    MICROSERVICES = "microservices"
    EVENT_DRIVEN = "event_driven"
    SERVERLESS = "serverless"
    LAYERED = "layered"

@dataclass
class ArchitectureScore:
    style: ArchitectureStyle
    scores: Dict[str, int]  # Criteria -> Score (1-10)
    
    def total_score(self) -> int:
        return sum(self.scores.values())

def evaluate_architecture_styles(requirements):
    """
    Score each architecture style against requirements.
    Higher score = better fit
    """
    scores = []
    
    # Example: Microservices evaluation
    microservices_scores = {
        "scalability": 9,        # Excellent
        "team_size": 8,          # Good for large teams
        "complexity_tolerance": 5, # Medium complexity
        "time_to_market": 4,     # Slower initial development
        "budget": 5,             # Higher operational costs
        "technology_diversity": 9 # Supports polyglot
    }
    scores.append(ArchitectureScore(
        ArchitectureStyle.MICROSERVICES, 
        microservices_scores
    ))
    
    # Example: Monolithic evaluation
    monolithic_scores = {
        "scalability": 4,        # Limited
        "team_size": 9,          # Great for small teams
        "complexity_tolerance": 9, # Low complexity
        "time_to_market": 9,     # Fast MVP
        "budget": 9,             # Lower operational costs
        "technology_diversity": 3 # Limited
    }
    scores.append(ArchitectureScore(
        ArchitectureStyle.MONOLITHIC, 
        monolithic_scores
    ))
    
    # Sort by total score
    scores.sort(key=lambda x: x.total_score(), reverse=True)
    return scores

# Use the evaluation
results = evaluate_architecture_styles(requirements={})
print(f"Recommended: {results[0].style.value} (Score: {results[0].total_score()})")
```

3. **Select supporting patterns:**

```yaml
# architecture_patterns.yaml
selected_patterns:
  api_gateway:
    why: "Centralized entry point, authentication, rate limiting"
    alternatives: ["Direct service calls", "Service mesh"]
    
  cqrs:
    why: "Separate read and write models for complex domain"
    alternatives: ["Shared model", "Materialized views"]
  
  event_sourcing:
    why: "Audit trail, temporal queries, event replay"
    alternatives: ["CRUD", "Change data capture"]
  
  strangler_fig:
    why: "Gradual migration from legacy system"
    alternatives: ["Big bang rewrite", "Parallel run"]
  
  circuit_breaker:
    why: "Prevent cascading failures in distributed system"
    alternatives: ["Retry with backoff", "Timeout only"]
  
  saga_pattern:
    why: "Distributed transactions across microservices"
    alternatives: ["2PC", "Compensating transactions"]
```

**Verification:**
- [ ] Architecture style aligns with team capabilities
- [ ] Selected patterns solve identified problems
- [ ] Trade-offs are explicitly documented
- [ ] Alternatives were considered and rejected with reasoning

---

### Step 3: Design High-Level System Components

**What:** Break down the system into major components with clear boundaries and responsibilities

**How:**

1. **Create component diagram:**

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
│                  (AWS ALB / HAProxy)                     │
└────────────┬────────────────────────────┬────────────────┘
             │                            │
   ┌─────────▼──────────┐      ┌─────────▼──────────┐
   │   API Gateway       │      │   Web Server        │
   │   (Kong/AWS API GW) │      │   (Nginx/React)     │
   └─────────┬───────────┘      └─────────────────────┘
             │
    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
┌───▼────┐  ┌────────▼────┐  ┌──────▼─────┐  ┌────▼─────┐
│ Auth   │  │ Product     │  │ Order      │  │ Payment  │
│Service │  │ Service     │  │ Service    │  │ Service  │
└───┬────┘  └────┬────────┘  └──────┬─────┘  └────┬─────┘
    │            │                   │             │
    │       ┌────▼────────┐     ┌────▼────┐       │
    │       │ PostgreSQL  │     │  Redis  │       │
    │       │ (Products)  │     │ (Cache) │       │
    │       └─────────────┘     └─────────┘       │
    │                                              │
    │            ┌─────────────────────────────────┘
    │            │
┌───▼────────────▼──────┐    ┌──────────────────┐
│   Message Broker      │    │  S3 / Blob Store │
│   (Kafka/RabbitMQ)   │    │  (Static Assets) │
└───────────────────────┘    └──────────────────┘
```

2. **Define component responsibilities:**

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class DataStore(Enum):
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    S3 = "s3"
    ELASTICSEARCH = "elasticsearch"

@dataclass
class Component:
    name: str
    responsibility: str
    technology: str
    data_stores: List[DataStore]
    dependencies: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    events_published: List[str] = field(default_factory=list)
    events_consumed: List[str] = field(default_factory=list)
    scaling_strategy: str = ""
    sla: Dict[str, str] = field(default_factory=dict)

# Define components
auth_service = Component(
    name="Auth Service",
    responsibility="User authentication, authorization, token management",
    technology="Python/FastAPI",
    data_stores=[DataStore.POSTGRESQL, DataStore.REDIS],
    api_endpoints=[
        "POST /api/v1/auth/register",
        "POST /api/v1/auth/login",
        "POST /api/v1/auth/refresh",
        "POST /api/v1/auth/logout"
    ],
    events_published=["user.registered", "user.logged_in"],
    scaling_strategy="Horizontal (stateless with Redis sessions)",
    sla={"availability": "99.9%", "latency_p95": "100ms"}
)

product_service = Component(
    name="Product Service",
    responsibility="Product catalog, inventory, search",
    technology="Java/Spring Boot",
    data_stores=[DataStore.POSTGRESQL, DataStore.ELASTICSEARCH],
    dependencies=["Auth Service"],
    api_endpoints=[
        "GET /api/v1/products",
        "GET /api/v1/products/:id",
        "POST /api/v1/products",
        "PATCH /api/v1/products/:id"
    ],
    events_published=["product.created", "product.updated", "inventory.changed"],
    events_consumed=["order.completed"],
    scaling_strategy="Horizontal with read replicas",
    sla={"availability": "99.95%", "latency_p95": "150ms"}
)

order_service = Component(
    name="Order Service",
    responsibility="Order processing, order lifecycle management",
    technology="Node.js/Express",
    data_stores=[DataStore.POSTGRESQL, DataStore.REDIS],
    dependencies=["Auth Service", "Product Service", "Payment Service"],
    api_endpoints=[
        "POST /api/v1/orders",
        "GET /api/v1/orders/:id",
        "GET /api/v1/orders/user/:userId"
    ],
    events_published=["order.created", "order.completed", "order.failed"],
    events_consumed=["payment.completed", "payment.failed"],
    scaling_strategy="Horizontal with event sourcing",
    sla={"availability": "99.9%", "latency_p95": "300ms"}
)

# Component registry
COMPONENTS = [auth_service, product_service, order_service]
```

3. **Document component interactions:**

```python
from dataclasses import dataclass
from enum import Enum

class CommunicationType(Enum):
    SYNC_HTTP = "synchronous_http"
    ASYNC_EVENT = "asynchronous_event"
    MESSAGE_QUEUE = "message_queue"
    GRPC = "grpc"

@dataclass
class Interaction:
    source: str
    target: str
    communication_type: CommunicationType
    protocol: str
    data_flow: str
    failure_handling: str
    
# Define interactions
interactions = [
    Interaction(
        source="API Gateway",
        target="Auth Service",
        communication_type=CommunicationType.SYNC_HTTP,
        protocol="REST/HTTPS",
        data_flow="User credentials -> JWT token",
        failure_handling="Retry 3x with exponential backoff, return 503"
    ),
    Interaction(
        source="Order Service",
        target="Payment Service",
        communication_type=CommunicationType.SYNC_HTTP,
        protocol="REST/HTTPS",
        data_flow="Order details -> Payment confirmation",
        failure_handling="Saga pattern with compensating transaction"
    ),
    Interaction(
        source="Order Service",
        target="Product Service",
        communication_type=CommunicationType.ASYNC_EVENT,
        protocol="Kafka",
        data_flow="order.completed event -> inventory update",
        failure_handling="Dead letter queue after 3 retries"
    )
]
```

**Verification:**
- [ ] Each component has a single, well-defined responsibility
- [ ] Component boundaries align with domain boundaries
- [ ] Dependencies flow in one direction (no circular dependencies)
- [ ] Each component can be developed and deployed independently

---

### Step 4: Design Data Architecture

**What:** Define data models, storage strategies, and data flow patterns

**How:**

1. **Select data storage per component:**

```yaml
# data_architecture.yaml
data_stores:
  
  auth_service:
    primary_store:
      type: PostgreSQL
      reason: "ACID compliance for user accounts and permissions"
      schema: "Normalized relational (3NF)"
    
    cache:
      type: Redis
      reason: "Session storage and JWT blacklist"
      ttl: "1 hour for sessions, 24 hours for blacklist"
  
  product_service:
    primary_store:
      type: PostgreSQL
      reason: "Structured product data with relationships"
      schema: "Normalized with JSON fields for attributes"
    
    search_index:
      type: Elasticsearch
      reason: "Full-text search and faceted navigation"
      sync_strategy: "CDC via Debezium"
    
    cache:
      type: Redis
      reason: "Product catalog cache for hot products"
      ttl: "5 minutes"
  
  order_service:
    primary_store:
      type: PostgreSQL
      reason: "Transactional integrity for orders"
      schema: "Event sourcing pattern"
    
    event_store:
      type: PostgreSQL (separate table)
      reason: "Immutable event log"
      retention: "7 years for compliance"
    
    read_model:
      type: PostgreSQL (materialized views)
      reason: "Optimized queries for order history"
      refresh: "Real-time via triggers"
  
  analytics_service:
    primary_store:
      type: Snowflake
      reason: "Data warehousing for analytics"
      sync_strategy: "Daily batch from operational DBs"
    
    streaming:
      type: Kafka + ksqlDB
      reason: "Real-time analytics and dashboards"
```

2. **Define data models:**

```python
# Example: Order service data models

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAYMENT_PROCESSING = "payment_processing"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(decimal_places=2)
    total_price: Decimal = Field(decimal_places=2)

class Order(BaseModel):
    """
    Aggregate root for Order bounded context.
    Follows DDD principles with value objects and entities.
    """
    order_id: str
    user_id: str
    status: OrderStatus
    items: List[OrderItem]
    
    # Value objects
    shipping_address: Address
    billing_address: Address
    
    # Money
    subtotal: Decimal = Field(decimal_places=2)
    tax: Decimal = Field(decimal_places=2)
    shipping_cost: Decimal = Field(decimal_places=2)
    total: Decimal = Field(decimal_places=2)
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    payment_method: str
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None
    
    # Audit
    version: int  # For optimistic locking
    events: List["OrderEvent"] = []  # Event sourcing

class OrderEvent(BaseModel):
    """
    Immutable event in event store.
    """
    event_id: str
    order_id: str
    event_type: str
    payload: dict
    timestamp: datetime
    user_id: str
    version: int
```

3. **Plan data consistency strategy:**

```python
from enum import Enum

class ConsistencyModel(Enum):
    STRONG = "strong"           # Immediate consistency
    EVENTUAL = "eventual"       # Eventually consistent
    CAUSAL = "causal"           # Causally consistent
    SESSION = "session"         # Session consistency

# Define consistency requirements per operation
consistency_requirements = {
    "user_login": {
        "model": ConsistencyModel.STRONG,
        "reason": "Security critical - must validate current password",
        "implementation": "Synchronous DB read"
    },
    
    "product_search": {
        "model": ConsistencyModel.EVENTUAL,
        "reason": "Acceptable for search results to be slightly stale",
        "implementation": "Elasticsearch with CDC sync (< 1 second lag)"
    },
    
    "order_creation": {
        "model": ConsistencyModel.STRONG,
        "reason": "Must validate inventory and process payment",
        "implementation": "Distributed transaction with Saga pattern"
    },
    
    "product_view_count": {
        "model": ConsistencyModel.EVENTUAL,
        "reason": "Exact count not critical",
        "implementation": "Async counter service with eventual flush"
    },
    
    "order_history": {
        "model": ConsistencyModel.SESSION,
        "reason": "User should see their own orders immediately",
        "implementation": "Read from leader for user's own orders"
    }
}
```

4. **Design data migration strategy:**

```python
# Database migration versioning and strategy

from typing import List
from dataclasses import dataclass

@dataclass
class Migration:
    version: str
    description: str
    up_sql: str
    down_sql: str
    is_breaking: bool
    estimated_downtime: str

# Example migrations
migrations = [
    Migration(
        version="001",
        description="Create users table",
        up_sql="""
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX idx_users_email ON users(email);
        """,
        down_sql="DROP TABLE users;",
        is_breaking=False,
        estimated_downtime="0 seconds"
    ),
    Migration(
        version="002",
        description="Add user roles - expand-contract pattern",
        up_sql="""
            -- Phase 1: Add new column (nullable)
            ALTER TABLE users ADD COLUMN role VARCHAR(50);
            
            -- Phase 2: Backfill data
            UPDATE users SET role = 'user' WHERE role IS NULL;
            
            -- Phase 3: Make non-nullable (do in next release)
            -- ALTER TABLE users ALTER COLUMN role SET NOT NULL;
        """,
        down_sql="ALTER TABLE users DROP COLUMN role;",
        is_breaking=False,
        estimated_downtime="0 seconds"
    )
]

# Zero-downtime migration strategy
migration_strategy = """
1. Expand-Contract Pattern:
   - Phase 1 (Deploy 1): Add new column/table (nullable)
   - Phase 2 (Deploy 2): Write to both old and new
   - Phase 3 (Deploy 3): Read from new, write to both
   - Phase 4 (Deploy 4): Read from new, write to new only
   - Phase 5 (Deploy 5): Remove old column/table

2. Read Replicas:
   - Run long migrations on replicas first
   - Promote replica to primary after verification

3. Dual-Write Period:
   - Write to both old and new schema
   - Allows rollback without data loss

4. Feature Flags:
   - Toggle between old and new code paths
   - Quick rollback if issues detected
"""
```

**Verification:**
- [ ] Data models are normalized appropriately
- [ ] Consistency requirements match business needs
- [ ] Data migration strategy supports zero-downtime deployments
- [ ] Data retention and archival policies are defined

---

### Step 5: Define API Contracts and Communication Protocols

**What:** Design clear, versioned APIs for inter-service and client-service communication

**How:**

1. **Design REST API standards:**

```yaml
# api_standards.yaml
rest_api_guidelines:
  
  base_url:
    format: "https://api.{domain}.com/v{version}/{resource}"
    example: "https://api.example.com/v1/orders"
  
  versioning:
    strategy: "URL path versioning"
    deprecation_period: "6 months"
    sunset_header: true
  
  http_methods:
    GET: "Retrieve resource(s) - idempotent, safe"
    POST: "Create new resource"
    PUT: "Replace entire resource - idempotent"
    PATCH: "Partial update - idempotent"
    DELETE: "Remove resource - idempotent"
  
  status_codes:
    200: "OK - successful GET, PUT, PATCH"
    201: "Created - successful POST"
    204: "No Content - successful DELETE"
    400: "Bad Request - validation error"
    401: "Unauthorized - authentication required"
    403: "Forbidden - insufficient permissions"
    404: "Not Found - resource doesn't exist"
    409: "Conflict - resource already exists"
    422: "Unprocessable Entity - semantic error"
    429: "Too Many Requests - rate limit exceeded"
    500: "Internal Server Error"
    503: "Service Unavailable - temporary failure"
  
  request_format:
    content_type: "application/json"
    character_encoding: "UTF-8"
    date_format: "ISO 8601 (YYYY-MM-DDTHH:mm:ss.sssZ)"
  
  response_format:
    success:
      structure: |
        {
          "data": {},
          "meta": {
            "request_id": "uuid",
            "timestamp": "ISO 8601"
          }
        }
    
    error:
      structure: |
        {
          "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": [],
            "request_id": "uuid"
          }
        }
  
  pagination:
    strategy: "Cursor-based for consistency"
    parameters: ["limit", "cursor"]
    response_fields: ["data", "next_cursor", "has_more"]
  
  filtering:
    format: "?field=value&field2=value2"
    operators: ["eq", "ne", "gt", "lt", "in", "like"]
    example: "?status=active&created_at[gt]=2024-01-01"
  
  rate_limiting:
    headers:
      - "X-RateLimit-Limit: 1000"
      - "X-RateLimit-Remaining: 999"
      - "X-RateLimit-Reset: 1640995200"
```

2. **Create OpenAPI specification:**

```yaml
# openapi.yaml
openapi: 3.0.3
info:
  title: Order Service API
  version: 1.0.0
  description: Manages order lifecycle and processing
  contact:
    name: API Support
    email: api@example.com

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://api-staging.example.com/v1
    description: Staging

paths:
  /orders:
    post:
      summary: Create new order
      operationId: createOrder
      tags:
        - Orders
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
            examples:
              simple_order:
                summary: Simple order with one item
                value:
                  items:
                    - product_id: "prod_123"
                      quantity: 2
                  shipping_address:
                    street: "123 Main St"
                    city: "San Francisco"
                    state: "CA"
                    postal_code: "94102"
                    country: "US"
      responses:
        '201':
          description: Order created successfully
          headers:
            Location:
              description: URL of created order
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '422':
          $ref: '#/components/responses/UnprocessableEntity'

    get:
      summary: List orders
      operationId: listOrders
      tags:
        - Orders
      security:
        - BearerAuth: []
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, confirmed, shipped, delivered]
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: cursor
          in: query
          schema:
            type: string
      responses:
        '200':
          description: List of orders
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/OrderResponse'
                  meta:
                    $ref: '#/components/schemas/PaginationMeta'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    CreateOrderRequest:
      type: object
      required:
        - items
        - shipping_address
      properties:
        items:
          type: array
          minItems: 1
          items:
            $ref: '#/components/schemas/OrderItem'
        shipping_address:
          $ref: '#/components/schemas/Address'
    
    OrderResponse:
      type: object
      properties:
        order_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        status:
          type: string
          enum: [pending, confirmed, shipped, delivered]
        items:
          type: array
          items:
            $ref: '#/components/schemas/OrderItem'
        total:
          type: number
          format: decimal
        created_at:
          type: string
          format: date-time
```

3. **Define event schemas for async communication:**

```python
# Event schema definitions using JSON Schema

from typing import Dict, Any
import json

# Event schema registry
event_schemas: Dict[str, Dict[str, Any]] = {
    "order.created": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["event_id", "event_type", "timestamp", "data"],
        "properties": {
            "event_id": {
                "type": "string",
                "format": "uuid",
                "description": "Unique event identifier"
            },
            "event_type": {
                "type": "string",
                "const": "order.created"
            },
            "timestamp": {
                "type": "string",
                "format": "date-time"
            },
            "data": {
                "type": "object",
                "required": ["order_id", "user_id", "items", "total"],
                "properties": {
                    "order_id": {"type": "string", "format": "uuid"},
                    "user_id": {"type": "string", "format": "uuid"},
                    "items": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["product_id", "quantity", "price"],
                            "properties": {
                                "product_id": {"type": "string"},
                                "quantity": {"type": "integer", "minimum": 1},
                                "price": {"type": "number", "minimum": 0}
                            }
                        }
                    },
                    "total": {"type": "number", "minimum": 0}
                }
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "correlation_id": {"type": "string"},
                    "causation_id": {"type": "string"}
                }
            }
        }
    }
}

# Event validation
from jsonschema import validate, ValidationError

def validate_event(event: dict, event_type: str) -> bool:
    """Validate event against schema."""
    try:
        schema = event_schemas.get(event_type)
        if not schema:
            raise ValueError(f"Unknown event type: {event_type}")
        validate(instance=event, schema=schema)
        return True
    except ValidationError as e:
        print(f"Event validation failed: {e.message}")
        return False

# Example usage
order_created_event = {
    "event_id": "550e8400-e29b-41d4-a716-446655440000",
    "event_type": "order.created",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        "order_id": "ord_123",
        "user_id": "usr_456",
        "items": [
            {"product_id": "prod_789", "quantity": 2, "price": 29.99}
        ],
        "total": 59.98
    },
    "metadata": {
        "source": "order-service",
        "correlation_id": "cor_abc",
        "causation_id": "cau_def"
    }
}

is_valid = validate_event(order_created_event, "order.created")
```

4. **Implement API versioning strategy:**

```python
from fastapi import FastAPI, APIRouter, Header
from typing import Optional

# V1 API
v1_router = APIRouter(prefix="/v1")

@v1_router.get("/orders/{order_id}")
async def get_order_v1(order_id: str):
    """
    V1: Returns order with basic information.
    Deprecated: Will be removed on 2025-01-01
    """
    return {
        "order_id": order_id,
        "status": "shipped",
        "total": 99.99
    }

# V2 API with enhanced response
v2_router = APIRouter(prefix="/v2")

@v2_router.get("/orders/{order_id}")
async def get_order_v2(order_id: str):
    """
    V2: Returns order with detailed tracking and history.
    """
    return {
        "order_id": order_id,
        "status": "shipped",
        "total": 99.99,
        "tracking": {
            "carrier": "USPS",
            "tracking_number": "123456789",
            "estimated_delivery": "2024-01-20"
        },
        "history": [
            {"status": "pending", "timestamp": "2024-01-15T10:00:00Z"},
            {"status": "confirmed", "timestamp": "2024-01-15T10:05:00Z"},
            {"status": "shipped", "timestamp": "2024-01-16T14:30:00Z"}
        ]
    }

app = FastAPI()
app.include_router(v1_router)
app.include_router(v2_router)

# Add deprecation headers for V1
@app.middleware("http")
async def add_deprecation_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/v1"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "Fri, 01 Jan 2025 00:00:00 GMT"
        response.headers["Link"] = '</v2/orders>; rel="successor-version"'
    return response
```

**Verification:**
- [ ] API contracts are documented with OpenAPI/AsyncAPI
- [ ] Versioning strategy supports backward compatibility
- [ ] Error responses are consistent and informative
- [ ] Event schemas are versioned and validated

---

### Step 6: Plan for Scalability and Performance

**What:** Design the system to handle growth in users, data, and traffic

**How:**

1. **Define scaling dimensions:**

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ScalingStrategy:
    dimension: str
    current_capacity: str
    target_capacity: str
    approach: str
    estimated_cost: str
    
scaling_plan = [
    ScalingStrategy(
        dimension="Request Throughput",
        current_capacity="1,000 req/sec",
        target_capacity="10,000 req/sec",
        approach="Horizontal scaling with auto-scaling groups",
        estimated_cost="+$2,000/month"
    ),
    ScalingStrategy(
        dimension="Database Reads",
        current_capacity="5,000 queries/sec",
        target_capacity="50,000 queries/sec",
        approach="Read replicas (5 replicas) + Redis cache",
        estimated_cost="+$1,500/month"
    ),
    ScalingStrategy(
        dimension="Database Writes",
        current_capacity="1,000 writes/sec",
        target_capacity="10,000 writes/sec",
        approach="Partition/shard by user_id (10 shards)",
        estimated_cost="+$3,000/month"
    ),
    ScalingStrategy(
        dimension="Storage",
        current_capacity="1 TB",
        target_capacity="100 TB",
        approach="S3 for cold data, DB for hot data",
        estimated_cost="+$1,000/month"
    ),
    ScalingStrategy(
        dimension="Geographic Distribution",
        current_capacity="1 region (us-east-1)",
        target_capacity="3 regions (US, EU, Asia)",
        approach="Multi-region deployment with CDN",
        estimated_cost="+$4,000/month"
    )
]
```

2. **Design caching strategy:**

```python
from enum import Enum
from typing import Optional
from dataclasses import dataclass

class CacheLevel(Enum):
    CLIENT = "client"          # Browser/app cache
    CDN = "cdn"                # Edge cache
    GATEWAY = "gateway"        # API gateway cache
    APPLICATION = "application" # App-level cache (Redis)
    DATABASE = "database"      # Query cache

@dataclass
class CachingRule:
    resource: str
    levels: List[CacheLevel]
    ttl: str
    invalidation_strategy: str
    
caching_rules = [
    CachingRule(
        resource="Static assets (images, CSS, JS)",
        levels=[CacheLevel.CLIENT, CacheLevel.CDN],
        ttl="1 year",
        invalidation_strategy="Cache busting via versioned URLs"
    ),
    CachingRule(
        resource="Product catalog",
        levels=[CacheLevel.APPLICATION],
        ttl="5 minutes",
        invalidation_strategy="Event-based (on product.updated)"
    ),
    CachingRule(
        resource="User session",
        levels=[CacheLevel.APPLICATION],
        ttl="1 hour",
        invalidation_strategy="Explicit logout or TTL expiry"
    ),
    CachingRule(
        resource="Search results",
        levels=[CacheLevel.APPLICATION],
        ttl="1 minute",
        invalidation_strategy="TTL expiry only"
    ),
    CachingRule(
        resource="API responses (GET requests)",
        levels=[CacheLevel.GATEWAY],
        ttl="30 seconds",
        invalidation_strategy="Cache-Control headers"
    )
]

# Redis cache implementation example
import redis
import json
from typing import Any, Optional

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with TTL."""
        self.redis.setex(
            key,
            ttl_seconds,
            json.dumps(value)
        )
    
    def invalidate(self, pattern: str):
        """Invalidate all keys matching pattern."""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def get_or_compute(
        self, 
        key: str, 
        compute_fn: callable, 
        ttl_seconds: int
    ) -> Any:
        """Get from cache or compute and store."""
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = compute_fn()
        self.set(key, value, ttl_seconds)
        return value
```

3. **Implement database optimization strategies:**

```sql
-- Indexing strategy
CREATE INDEX CONCURRENTLY idx_orders_user_id_created_at 
    ON orders(user_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_orders_status_created_at 
    ON orders(status, created_at DESC)
    WHERE status IN ('pending', 'processing');

-- Partitioning strategy for large tables
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL,
    status VARCHAR(50),
    -- other columns...
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Materialized views for analytics
CREATE MATERIALIZED VIEW daily_order_stats AS
SELECT 
    DATE(created_at) as order_date,
    status,
    COUNT(*) as order_count,
    SUM(total) as total_revenue
FROM orders
GROUP BY DATE(created_at), status
WITH DATA;

-- Refresh strategy (can be scheduled)
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_order_stats;

-- Database sharding strategy
-- Hash-based sharding by user_id
-- Shard 0: user_id hash % 10 = 0
-- Shard 1: user_id hash % 10 = 1
-- ...

-- Connection pooling configuration
-- Configure in application:
-- pool_size: 20 connections per instance
-- max_overflow: 10
-- pool_timeout: 30 seconds
-- pool_recycle: 3600 seconds (1 hour)
```

4. **Design for performance:**

```python
# Performance optimization patterns

import asyncio
from typing import List, Dict, Any
import aiohttp

class PerformanceOptimizer:
    """
    Collection of performance optimization patterns.
    """
    
    async def parallel_fetch(self, urls: List[str]) -> List[Dict]:
        """
        Fetch multiple resources in parallel instead of sequentially.
        
        Before: 3 requests × 100ms = 300ms total
        After: max(100ms, 100ms, 100ms) = 100ms total
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_url(session, url) for url in urls]
            return await asyncio.gather(*tasks)
    
    async def _fetch_url(self, session, url: str):
        async with session.get(url) as response:
            return await response.json()
    
    def batch_database_operations(self, records: List[Dict]):
        """
        Batch database operations to reduce round trips.
        
        Before: 100 INSERT queries = 100 round trips
        After: 1 batch INSERT = 1 round trip
        """
        # Using SQLAlchemy bulk operations
        from sqlalchemy import insert
        
        stmt = insert(Order).values(records)
        session.execute(stmt)
        session.commit()
    
    def n_plus_one_prevention(self):
        """
        Prevent N+1 query problem with eager loading.
        
        Before: 1 query for orders + N queries for items = N+1 queries
        After: 1 query with JOIN = 1 query
        """
        from sqlalchemy.orm import joinedload
        
        # Bad: N+1 queries
        orders = session.query(Order).all()
        for order in orders:
            items = order.items  # Triggers separate query each time
        
        # Good: Single query with JOIN
        orders = session.query(Order)\
            .options(joinedload(Order.items))\
            .all()
    
    async def dataloader_pattern(self):
        """
        Batch and cache data loading (Facebook's DataLoader pattern).
        """
        from aiodataloader import DataLoader
        
        class ProductLoader(DataLoader):
            async def batch_load_fn(self, product_ids: List[str]):
                # Single query for all products
                products = await fetch_products_by_ids(product_ids)
                return [products.get(id) for id in product_ids]
        
        loader = ProductLoader()
        
        # These will be batched into a single query
        product_1 = await loader.load("prod_1")
        product_2 = await loader.load("prod_2")
        product_3 = await loader.load("prod_3")
```

**Verification:**
- [ ] Load testing performed for target capacity
- [ ] Caching strategy reduces database load by > 50%
- [ ] Database queries are optimized with proper indexes
- [ ] Auto-scaling policies are configured and tested

---

### Step 7: Implement Security and Compliance

**What:** Build security into the architecture from the ground up

**How:**

1. **Define security layers:**

```yaml
# security_architecture.yaml
security_layers:
  
  network_security:
    firewall:
      type: "AWS Security Groups / Network ACLs"
      rules:
        - "Allow HTTPS (443) from 0.0.0.0/0"
        - "Allow SSH (22) from VPN only"
        - "Deny all other inbound traffic"
    
    ddos_protection:
      service: "AWS Shield Standard + WAF"
      rate_limiting: "1000 requests/minute per IP"
    
    tls:
      version: "TLS 1.3"
      certificate: "Let's Encrypt with auto-renewal"
      cipher_suites: "ECDHE-RSA-AES256-GCM-SHA384"
  
  application_security:
    authentication:
      method: "OAuth 2.0 + OpenID Connect"
      token_type: "JWT with RS256 signing"
      token_expiry: "1 hour (access), 30 days (refresh)"
      mfa: "Required for admin users"
    
    authorization:
      model: "RBAC (Role-Based Access Control)"
      enforcement: "API gateway + service-level checks"
      
    input_validation:
      - "Validate all inputs against schema"
      - "Sanitize HTML/SQL to prevent injection"
      - "Limit request size to 1MB"
      - "Rate limit per user: 100 req/minute"
    
    secrets_management:
      service: "AWS Secrets Manager"
      rotation: "Automatic every 90 days"
      access: "IAM roles with least privilege"
  
  data_security:
    encryption_at_rest:
      database: "AES-256 (AWS RDS encryption)"
      storage: "AES-256 (S3 server-side encryption)"
      backups: "Encrypted with KMS"
    
    encryption_in_transit:
      internal: "TLS 1.3 for service-to-service"
      external: "TLS 1.3 for client-to-service"
    
    pii_handling:
      - "Tokenize credit card numbers (PCI DSS)"
      - "Hash passwords with bcrypt (cost 12)"
      - "Encrypt SSN and sensitive fields"
      - "Anonymize logs (remove PII)"
  
  compliance:
    gdpr:
      - "Data portability API"
      - "Right to erasure implementation"
      - "Consent management"
      - "Data processing agreements"
    
    pci_dss:
      - "No storage of full card numbers"
      - "Payment gateway integration"
      - "Quarterly vulnerability scans"
      - "Annual compliance audit"
    
    soc2:
      - "Access controls and logging"
      - "Change management procedures"
      - "Incident response plan"
      - "Annual Type II audit"
```

2. **Implement authentication and authorization:**

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token creation
SECRET_KEY = "your-secret-key"  # Load from secrets manager
ALGORITHM = "RS256"  # Use RSA for production
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# RBAC implementation
from enum import Enum
from typing import List

class Permission(str, Enum):
    READ_ORDERS = "orders:read"
    WRITE_ORDERS = "orders:write"
    DELETE_ORDERS = "orders:delete"
    READ_USERS = "users:read"
    WRITE_USERS = "users:write"

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS,
        Permission.DELETE_ORDERS,
        Permission.READ_USERS,
        Permission.WRITE_USERS,
    ],
    Role.USER: [
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS,
    ],
    Role.GUEST: [
        Permission.READ_ORDERS,
    ]
}

def has_permission(user_role: Role, required_permission: Permission) -> bool:
    """Check if role has required permission."""
    return required_permission in ROLE_PERMISSIONS.get(user_role, [])

# Authorization decorator
from functools import wraps

def require_permission(permission: Permission):
    """Decorator to enforce permission checks."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request context
            user = kwargs.get('current_user')
            if not user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            if not has_permission(user.role, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage example
@require_permission(Permission.DELETE_ORDERS)
async def delete_order(order_id: str, current_user: User):
    """Only admins can delete orders."""
    # Delete logic here
    pass
```

3. **Implement security monitoring:**

```python
import logging
from typing import Dict, Any
from datetime import datetime

class SecurityEventLogger:
    """Log security-relevant events for monitoring and auditing."""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        # Configure to send to SIEM (Splunk, DataDog, etc.)
    
    def log_authentication_attempt(
        self,
        user_id: str,
        success: bool,
        ip_address: str,
        user_agent: str
    ):
        """Log authentication attempts for anomaly detection."""
        event = {
            "event_type": "authentication_attempt",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        if success:
            self.logger.info("Authentication successful", extra=event)
        else:
            self.logger.warning("Authentication failed", extra=event)
    
    def log_authorization_failure(
        self,
        user_id: str,
        resource: str,
        action: str,
        reason: str
    ):
        """Log authorization failures for security review."""
        event = {
            "event_type": "authorization_failure",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "reason": reason
        }
        self.logger.warning("Authorization denied", extra=event)
    
    def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str
    ):
        """Log access to sensitive data for audit trail."""
        event = {
            "event_type": "data_access",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action
        }
        self.logger.info("Data accessed", extra=event)
    
    def log_suspicious_activity(
        self,
        user_id: str,
        activity_type: str,
        details: Dict[str, Any]
    ):
        """Log suspicious activity for investigation."""
        event = {
            "event_type": "suspicious_activity",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details
        }
        self.logger.critical("Suspicious activity detected", extra=event)

# Anomaly detection
class AnomalyDetector:
    """Detect suspicious patterns in user behavior."""
    
    def check_login_rate(self, user_id: str, time_window_minutes: int = 5):
        """Alert if too many login attempts."""
        # Query logs for login attempts
        attempts = self.count_login_attempts(user_id, time_window_minutes)
        
        if attempts > 10:
            SecurityEventLogger().log_suspicious_activity(
                user_id=user_id,
                activity_type="excessive_login_attempts",
                details={"attempts": attempts, "window_minutes": time_window_minutes}
            )
            # Trigger account lockout
            self.lock_account(user_id, duration_minutes=30)
    
    def check_access_patterns(self, user_id: str):
        """Detect unusual access patterns."""
        # Check for access from multiple locations
        # Check for unusual times
        # Check for unusual resource access
        pass
```

**Verification:**
- [ ] Security threat modeling completed (STRIDE analysis)
- [ ] Authentication and authorization tested
- [ ] Penetration testing passed
- [ ] Compliance requirements mapped to controls

---

### Step 8: Document and Review Architecture

**What:** Create comprehensive documentation and conduct architecture review

**How:**

1. **Create C4 diagrams:**

```
Level 1: System Context Diagram
┌─────────────────────────────────────────────────────────────┐
│                      E-commerce Platform                     │
│                                                               │
│  ┌──────────┐              ┌──────────┐                     │
│  │  Mobile  │─────────────▶│   Web    │                     │
│  │   App    │              │ Frontend │                     │
│  └──────────┘              └─────┬────┘                     │
│                                  │                           │
│                            ┌─────▼─────┐                    │
│                            │           │                     │
│                            │  Backend  │                     │
│                            │  System   │                     │
│                            │           │                     │
│                            └─────┬─────┘                    │
│                                  │                           │
│              ┌───────────────────┼───────────────┐          │
│              │                   │               │          │
│         ┌────▼────┐        ┌────▼────┐    ┌────▼────┐     │
│         │ Payment │        │  Email  │    │   CRM   │     │
│         │ Gateway │        │ Service │    │ System  │     │
│         │ (Stripe)│        │(SendGrid│    │(Salesfrc│     │
│         └─────────┘        └─────────┘    └─────────┘     │
└─────────────────────────────────────────────────────────────┘


Level 2: Container Diagram
┌─────────────────────────────────────────────────────────────┐
│                      Backend System                          │
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │     Web      │────────▶│     API      │                 │
│  │  Application │         │   Gateway    │                 │
│  │   (React)    │         │    (Kong)    │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                  │                           │
│              ┌───────────────────┼───────────────┐          │
│              │                   │               │          │
│         ┌────▼────┐        ┌────▼────┐    ┌────▼────┐     │
│         │  Auth   │        │ Product │    │  Order  │     │
│         │ Service │        │ Service │    │ Service │     │
│         │(FastAPI)│        │(Spring) │    │ (Node)  │     │
│         └────┬────┘        └────┬────┘    └────┬────┘     │
│              │                  │              │           │
│         ┌────▼────┐        ┌────▼────┐    ┌────▼────┐     │
│         │Postgres │        │Postgres │    │Postgres │     │
│         │   DB    │        │   DB    │    │   DB    │     │
│         └─────────┘        └─────────┘    └─────────┘     │
│                                                              │
│                     ┌──────────────┐                        │
│                     │    Redis     │                        │
│                     │    Cache     │                        │
│                     └──────────────┘                        │
│                                                              │
│                     ┌──────────────┐                        │
│                     │    Kafka     │                        │
│                     │    (Events)  │                        │
│                     └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

2. **Create Architecture Decision Records (ADRs):**

```markdown
# ADR 001: Use Microservices Architecture

## Status
Accepted

## Context
We need to choose an architecture style for our e-commerce platform. The system will:
- Handle 100,000 concurrent users
- Be developed by 3 separate teams
- Require frequent deployments
- Need to scale different components independently

## Decision
We will use a microservices architecture with the following services:
- Auth Service
- Product Service
- Order Service
- Payment Service
- Notification Service

## Consequences

### Positive
- Independent scaling of services
- Technology diversity per service
- Team autonomy
- Faster deployments
- Better fault isolation

### Negative
- Increased operational complexity
- Need for service mesh/API gateway
- Distributed transaction challenges
- More difficult end-to-end testing

### Mitigation
- Invest in observability (tracing, logging, metrics)
- Use Kubernetes for orchestration
- Implement circuit breakers and retries
- Use saga pattern for distributed transactions

## Alternatives Considered
1. **Monolithic Architecture**: Rejected due to scaling and team size
2. **Serverless**: Rejected due to vendor lock-in and cold starts
```

```markdown
# ADR 002: Use PostgreSQL as Primary Database

## Status
Accepted

## Context
We need to select a database for our microservices. Requirements:
- ACID transactions
- Complex queries with joins
- Mature ecosystem and tooling
- Good performance up to millions of records
- Strong consistency

## Decision
Use PostgreSQL as the primary database for most services, with service-specific databases.

## Consequences

### Positive
- ACID compliance for critical operations
- Rich query capabilities (JSON, full-text search)
- Excellent performance with proper indexing
- Mature replication and backup tools
- Strong community support

### Negative
- Vertical scaling limits (though high)
- More complex sharding than NoSQL
- Need to design schema carefully

### Mitigation
- Use read replicas for read-heavy workloads
- Implement caching layer (Redis)
- Plan for sharding if needed (by user_id)
- Use connection pooling

## Alternatives Considered
1. **MongoDB**: Rejected due to need for ACID transactions
2. **MySQL**: Close second, but PostgreSQL has better JSON support
3. **DynamoDB**: Rejected due to vendor lock-in and learning curve
```

3. **Document deployment architecture:**

```yaml
# deployment_architecture.yaml
environments:
  
  development:
    purpose: "Local development and testing"
    infrastructure:
      - Docker Compose for local services
      - LocalStack for AWS services
      - Local Kubernetes (Minikube/Kind)
    databases:
      - Containerized PostgreSQL
      - Containerized Redis
    deployment: "Manual via docker-compose up"
  
  staging:
    purpose: "Pre-production testing with production-like data"
    infrastructure:
      cloud: AWS
      region: us-east-1
      compute: EKS (Kubernetes)
      instances: t3.medium (2 per service)
    databases:
      primary: RDS PostgreSQL (db.t3.medium)
      cache: ElastiCache Redis (cache.t3.medium)
    networking:
      vpc: "10.0.0.0/16"
      subnets:
        public: ["10.0.1.0/24", "10.0.2.0/24"]
        private: ["10.0.10.0/24", "10.0.20.0/24"]
      load_balancer: Application Load Balancer
    deployment:
      method: "GitOps with ArgoCD"
      trigger: "Push to staging branch"
      approval: "Automatic"
  
  production:
    purpose: "Live customer-facing environment"
    infrastructure:
      cloud: AWS
      regions: [us-east-1, us-west-2, eu-west-1]
      compute: EKS (Kubernetes)
      instances: t3.large (5 per service per region)
      auto_scaling:
        min: 5
        max: 50
        metric: CPU > 70% or requests > 1000/min
    databases:
      primary: RDS PostgreSQL Multi-AZ (db.r5.2xlarge)
      replicas: 5 read replicas per region
      cache: ElastiCache Redis Cluster (cache.r5.xlarge)
      backup:
        automated: Daily snapshots
        retention: 30 days
        point_in_time_recovery: 7 days
    networking:
      vpc: Multi-region VPC with peering
      cdn: CloudFront with edge locations
      waf: AWS WAF with rate limiting
      ddos: AWS Shield Standard
    deployment:
      method: "GitOps with ArgoCD"
      trigger: "Push to production branch"
      approval: "Manual approval required"
      strategy: "Blue-green deployment"
      rollback: "Automated on failure"
      canary: "10% → 50% → 100% over 30 minutes"
    monitoring:
      apm: DataDog
      logging: CloudWatch Logs + DataDog
      tracing: DataDog APM
      metrics: CloudWatch + DataDog
      alerting: PagerDuty integration
    disaster_recovery:
      rto: "1 hour"
      rpo: "5 minutes"
      backup_region: "us-west-2"
      failover: "Automated with Route53"
```

4. **Conduct architecture review:**

```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class ReviewCriteria(Enum):
    SCALABILITY = "scalability"
    AVAILABILITY = "availability"
    SECURITY = "security"
    COST = "cost"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"

@dataclass
class ArchitectureReviewItem:
    criteria: ReviewCriteria
    question: str
    answer: str
    concerns: List[str]
    mitigations: List[str]

architecture_review = [
    ArchitectureReviewItem(
        criteria=ReviewCriteria.SCALABILITY,
        question="Can the system handle 10x current load?",
        answer="Yes, with horizontal scaling and caching",
        concerns=[
            "Database write scaling may become bottleneck",
            "Single API gateway may be SPOF"
        ],
        mitigations=[
            "Plan for database sharding by user_id",
            "Deploy API gateway in HA mode with auto-scaling"
        ]
    ),
    ArchitectureReviewItem(
        criteria=ReviewCriteria.AVAILABILITY,
        question="What is the failure mode for each component?",
        answer="Multi-AZ deployment with automatic failover",
        concerns=[
            "Database failover takes 60-120 seconds",
            "No multi-region failover currently"
        ],
        mitigations=[
            "Acceptable for 99.9% SLA",
            "Phase 2: Add multi-region deployment"
        ]
    ),
    ArchitectureReviewItem(
        criteria=ReviewCriteria.SECURITY,
        question="Are all attack vectors addressed?",
        answer="Standard security controls in place",
        concerns=[
            "No DDoS protection beyond WAF",
            "Secrets in environment variables"
        ],
        mitigations=[
            "Add AWS Shield Advanced",
            "Migrate to AWS Secrets Manager"
        ]
    ),
    ArchitectureReviewItem(
        criteria=ReviewCriteria.COST,
        question="What is the monthly operational cost?",
        answer="Estimated $15,000/month for initial scale",
        concerns=[
            "Data transfer costs may exceed estimate",
            "Multi-region deployment will double costs"
        ],
        mitigations=[
            "Monitor and set up cost alerts",
            "Delay multi-region until necessary"
        ]
    )
]
```

**Verification:**
- [ ] All stakeholders have reviewed documentation
- [ ] C4 diagrams cover all levels (context, container, component)
- [ ] ADRs document all major decisions
- [ ] Architecture review identified and mitigated risks

---

## Verification Checklist

After completing all implementation steps:

### Requirements Coverage
- [ ] All functional requirements mapped to components
- [ ] Non-functional requirements have measurable metrics
- [ ] Success criteria defined and testable

### Architecture Quality
- [ ] Component responsibilities are clear and single-purpose
- [ ] No circular dependencies between components
- [ ] Data flow is documented and logical
- [ ] APIs are versioned and documented

### Scalability & Performance
- [ ] System can handle 10x current load
- [ ] Caching strategy reduces backend load
- [ ] Database queries are optimized
- [ ] Load testing performed

### Security & Compliance
- [ ] Authentication and authorization implemented
- [ ] Data encryption (at rest and in transit)
- [ ] Security monitoring and alerting
- [ ] Compliance requirements addressed

### Operational Readiness
- [ ] Deployment strategy defined
- [ ] Monitoring and observability plan
- [ ] Disaster recovery plan
- [ ] Runbooks for common operations

### Documentation
- [ ] Architecture diagrams (C4 model)
- [ ] API documentation (OpenAPI/AsyncAPI)
- [ ] ADRs for major decisions
- [ ] Deployment architecture documented

---

## Common Issues and Solutions

### Issue 1: Analysis Paralysis
**Problem:** Spending too much time on architecture design without implementation

**Solution:**
- Time-box architecture design (1-2 weeks max)
- Start with MVP architecture, iterate based on feedback
- Use proven patterns from similar systems
- Schedule regular architecture review sessions

### Issue 2: Over-Engineering
**Problem:** Designing for problems you don't have yet

**Solution:**
```python
# YAGNI (You Aren't Gonna Need It) checklist
questions_to_ask = [
    "Do we have this problem TODAY?",
    "Will this problem occur in the next 6 months?",
    "What is the cost of adding this now vs. later?",
    "Can we validate this assumption first?"
]

# Start simple, add complexity when needed
# ❌ Don't: Build for 1M users when you have 100
# ✅ Do: Build for 10,000 users, plan for scaling
```

### Issue 3: Technology Selection Paralysis
**Problem:** Unable to choose between technology options

**Solution:**
```python
# Decision framework for technology selection
def evaluate_technology(tech_name: str) -> int:
    """Score technology on multiple dimensions."""
    score = 0
    
    # Team familiarity (weight: 30%)
    score += team_has_experience(tech_name) * 30
    
    # Community support (weight: 20%)
    score += has_active_community(tech_name) * 20
    
    # Meets requirements (weight: 25%)
    score += meets_technical_requirements(tech_name) * 25
    
    # Operational maturity (weight: 15%)
    score += is_production_ready(tech_name) * 15
    
    # Cost (weight: 10%)
    score += is_cost_effective(tech_name) * 10
    
    return score

# Prefer boring technology that works over exciting but unproven
```

### Issue 4: Ignoring Non-Functional Requirements
**Problem:** Focusing only on features, neglecting performance, security, etc.

**Solution:**
```yaml
# Make NFRs explicit and measurable
non_functional_requirements:
  performance:
    metric: "p95 latency"
    target: "< 200ms"
    measurement: "Load testing with k6"
  
  availability:
    metric: "uptime percentage"
    target: "> 99.9%"
    measurement: "Prometheus + Grafana"
  
  security:
    metric: "OWASP Top 10 compliance"
    target: "100% compliant"
    measurement: "SAST + DAST scans"

# Include NFRs in definition of done
```

### Issue 5: Not Planning for Failure
**Problem:** Architecture assumes everything works perfectly

**Solution:**
```python
# Chaos engineering mindset
failure_scenarios = [
    "Database goes down for 5 minutes",
    "Payment gateway times out",
    "Network partition between services",
    "Cache eviction causes thundering herd",
    "Deployment rolls out bad code",
    "DDoS attack overwhelms system"
]

# For each scenario, ask:
# 1. How do we detect it?
# 2. How do we handle it gracefully?
# 3. How do we recover automatically?
# 4. What is the user experience during failure?
```

---

## Best Practices

### DO:
✅ **Start with requirements, not technology**
   - Understand the problem before choosing solutions
   - Let requirements drive architecture decisions

✅ **Use proven patterns and practices**
   - Don't reinvent the wheel
   - Learn from successful systems in similar domains

✅ **Design for evolution**
   - Architecture will change as you learn
   - Make it easy to modify and extend

✅ **Document decisions and trade-offs**
   - Future you will thank you
   - ADRs help new team members understand "why"

✅ **Consider operational concerns early**
   - How will you deploy, monitor, and debug?
   - Operations is part of architecture

✅ **Get feedback early and often**
   - Validate assumptions with prototypes
   - Review architecture with team and stakeholders

### DON'T:
❌ **Design for imaginary scale**
   - "We might have 1 million users someday"
   - Build for current + near-term needs

❌ **Choose technology based on resume building**
   - Pick tools that solve your problems
   - Not tools that look good on LinkedIn

❌ **Create a waterfall architecture phase**
   - Architecture is continuous, not one-time
   - Evolve architecture with the product

❌ **Ignore team capabilities**
   - Microservices with 2 developers = bad idea
   - Architecture must match team maturity

❌ **Skip the "why" documentation**
   - Documenting "what" without "why" is incomplete
   - Explain reasoning and trade-offs

❌ **Design in isolation**
   - Involve developers, ops, security early
   - Get input from people who will build/maintain it

---

## Related Workflows

- [Architecture Decision Records](./architecture_decision_records.md) - Document key decisions
- [API Design Best Practices](./api_design_best_practices.md) - Design robust APIs
- [Microservices Patterns](./microservices_patterns.md) - Microservice architecture patterns
- [Scalability Patterns](./scalability_patterns.md) - Scale from 100 to 1M+ users
- [Distributed Systems Patterns](./distributed_systems_patterns.md) - Handle distributed challenges
- [Event-Driven Architecture](./event_driven_architecture.md) - Event-driven design
- [Caching Strategies](./caching_strategies.md) - Improve performance with caching
- [System Monitoring Setup](../devops/monitoring_setup.md) - Observability
- [Security Best Practices](../security/security_best_practices.md) - Security design

---

## Tags
`architecture` `system-design` `requirements` `scalability` `security` `documentation` `adr` `patterns` `best-practices` `microservices` `design-patterns` `trade-offs`
