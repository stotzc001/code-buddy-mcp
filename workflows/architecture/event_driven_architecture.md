# Event Driven Architecture

**ID:** arc-005  
**Category:** Architecture  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design and implement event-driven architectures using message brokers and event streaming

**Why:** Event-driven architecture enables loose coupling, scales independently (10-100x), handles async operations naturally, and processes real-time data streams with sub-second latency

**When to use:**
- Building real-time data processing systems
- Implementing microservices that need to communicate
- Creating reactive, responsive systems
- Handling high-throughput event streams (1000+ events/sec)
- Decoupling services for independent scaling
- Building notification and alerting systems
- Implementing event sourcing or CQRS patterns

---

## Prerequisites

**Required:**
- [ ] Understanding of pub/sub messaging patterns
- [ ] Message broker knowledge (Kafka, RabbitMQ, AWS SNS/SQS)
- [ ] Async programming concepts (promises, async/await)
- [ ] Basic understanding of event sourcing
- [ ] Knowledge of message serialization (JSON, Avro, Protobuf)

**Check before starting:**
```bash
# Check message brokers
kafka-topics.sh --version
rabbitmqctl status

# Check Python/Node async support
python -c "import asyncio; print('✅ Async support available')"
node -e "console.log('✅ Node.js async available')"

# Check Docker (for running brokers locally)
docker --version
```

---

## Implementation Steps

### Step 1: Choose Message Broker and Architecture Pattern

**What:** Select appropriate message broker and event-driven pattern for your use case

**How:**

**Message Broker Comparison:**

```
┌─────────────┬────────────┬───────────┬────────────┬──────────────┐
│ Broker      │ Throughput │ Ordering  │ Replay     │ Use Case     │
├─────────────┼────────────┼───────────┼────────────┼──────────────┤
│ Kafka       │ Very High  │ Per       │ Yes        │ Event        │
│             │ 100k+      │ Partition │ (forever)  │ Streaming    │
│             │ msgs/sec   │           │            │ Logs         │
├─────────────┼────────────┼───────────┼────────────┼──────────────┤
│ RabbitMQ    │ Medium     │ Queue     │ No         │ Task Queues  │
│             │ 10-20k     │ based     │            │ Work         │
│             │ msgs/sec   │           │            │ Distribution │
├─────────────┼────────────┼───────────┼────────────┼──────────────┤
│ AWS SQS     │ Medium     │ FIFO      │ No         │ Cloud-native │
│             │            │ optional  │            │ Queues       │
├─────────────┼────────────┼───────────┼────────────┼──────────────┤
│ Redis       │ High       │ Stream    │ Limited    │ Real-time    │
│ Streams     │ 50k+       │           │ (retention)│ Simple       │
│             │ msgs/sec   │           │            │ Pub/Sub      │
└─────────────┴────────────┴───────────┴────────────┴──────────────┘
```

**Event-Driven Patterns:**

```python
# Pattern 1: Event Notification
# Simple notification that something happened
# Receivers fetch additional data if needed

class EventNotification:
    """
    Minimal event data
    Receivers pull details from source
    """
    
    def notify_order_created(self, order_id):
        event = {
            'event_type': 'order.created',
            'order_id': order_id,
            'timestamp': time.time()
        }
        # Just notify - receivers fetch full order if needed
        event_bus.publish('orders', event)

# Pattern 2: Event-Carried State Transfer
# Event contains all necessary data
# Receivers don't need to call back

class EventCarriedStateTransfer:
    """
    Full state in event
    Receivers have everything they need
    """
    
    def publish_order_created(self, order):
        event = {
            'event_type': 'order.created',
            'order_id': order.id,
            'user_id': order.user_id,
            'items': [
                {'product_id': i.product_id, 'quantity': i.quantity}
                for i in order.items
            ],
            'total_amount': order.total,
            'shipping_address': order.shipping_address,
            'timestamp': time.time()
        }
        # Full state - receivers don't need to fetch
        event_bus.publish('orders', event)

# Pattern 3: Event Sourcing
# Events are the source of truth
# Current state derived from events

class EventSourcing:
    """
    Store events, derive state
    Can replay events to rebuild state
    """
    
    def create_order(self, order_data):
        # Don't store state, store events
        events = [
            {'type': 'OrderCreated', 'data': order_data},
            {'type': 'ItemsAdded', 'data': order_data['items']},
            {'type': 'AddressSet', 'data': order_data['address']}
        ]
        
        for event in events:
            event_store.append('order', order_data['id'], event)
        
        return order_data['id']
    
    def get_order_state(self, order_id):
        # Rebuild state from events
        events = event_store.get_events('order', order_id)
        state = {}
        
        for event in events:
            if event['type'] == 'OrderCreated':
                state = event['data']
            elif event['type'] == 'ItemsAdded':
                state['items'] = event['data']
            elif event['type'] == 'AddressSet':
                state['address'] = event['data']
        
        return state

# Pattern 4: CQRS (Command Query Responsibility Segregation)
# Separate read and write models

class CQRS:
    """
    Write to event store
    Read from optimized read models
    """
    
    # Write side - commands
    def create_order_command(self, order_data):
        # Validate command
        if not self.validate_order(order_data):
            raise ValidationError()
        
        # Generate events
        event = {
            'type': 'OrderCreated',
            'aggregate_id': order_data['id'],
            'data': order_data,
            'timestamp': time.time()
        }
        
        # Store event
        event_store.append(event)
        
        # Publish for read model updates
        event_bus.publish('order.created', event)
    
    # Read side - queries
    def get_order_query(self, order_id):
        # Read from optimized read model (not event store)
        return read_model_db.query(Order).get(order_id)
    
    # Read model updater (subscribes to events)
    @event_bus.subscribe('order.created')
    def update_read_model(self, event):
        # Update denormalized read model
        order = Order(**event['data'])
        read_model_db.add(order)
        read_model_db.commit()
```

**Decision Matrix:**

```python
def choose_pattern(requirements):
    """Choose event-driven pattern"""
    
    if requirements.get('event_replay_needed'):
        if requirements.get('complex_queries'):
            return 'CQRS + Event Sourcing'
        else:
            return 'Event Sourcing'
    
    elif requirements.get('receivers_need_full_data'):
        return 'Event-Carried State Transfer'
    
    elif requirements.get('simple_notifications'):
        return 'Event Notification'
    
    elif requirements.get('read_write_scaling_different'):
        return 'CQRS'
    
    else:
        return 'Event-Carried State Transfer'  # Default

# Examples
print(choose_pattern({
    'event_replay_needed': True,
    'complex_queries': True
}))  # → 'CQRS + Event Sourcing'

print(choose_pattern({
    'receivers_need_full_data': True
}))  # → 'Event-Carried State Transfer'
```

**Verification:**
- [ ] Message broker chosen based on requirements
- [ ] Event-driven pattern selected
- [ ] Team understands trade-offs
- [ ] Infrastructure planned

**If This Fails:**
→ Start with Event-Carried State Transfer (simplest)
→ Use managed service (AWS EventBridge, Google Pub/Sub)
→ Begin with RabbitMQ (easier than Kafka for simple cases)

---

### Step 2: Design Event Schema and Versioning

**What:** Create consistent, evolvable event schemas with proper versioning

**How:**

**Event Schema Best Practices:**

```python
# Good event schema structure
{
    # Event metadata
    "event_id": "uuid-here",
    "event_type": "order.created",
    "event_version": "1.0",
    "timestamp": "2025-10-26T10:00:00Z",
    "source": "order-service",
    "correlation_id": "request-uuid",
    
    # Event data
    "data": {
        "order_id": 12345,
        "user_id": 789,
        "items": [
            {"product_id": 1, "quantity": 2, "price": 29.99}
        ],
        "total_amount": 59.98,
        "status": "pending"
    }
}
```

**Event Schema Definition:**

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid

# Base event class
class BaseEvent(BaseModel):
    """Base class for all events"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    correlation_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Specific events
class OrderCreatedEvent(BaseEvent):
    """Event published when order is created"""
    event_type: str = "order.created"
    
    class OrderData(BaseModel):
        order_id: int
        user_id: int
        items: List[dict]
        total_amount: float
        shipping_address: dict
    
    data: OrderData

class PaymentProcessedEvent(BaseEvent):
    """Event published when payment succeeds"""
    event_type: str = "payment.processed"
    
    class PaymentData(BaseModel):
        payment_id: int
        order_id: int
        amount: float
        payment_method: str
        status: str
    
    data: PaymentData

# Usage
event = OrderCreatedEvent(
    source="order-service",
    correlation_id="request-123",
    data=OrderCreatedEvent.OrderData(
        order_id=12345,
        user_id=789,
        items=[{"product_id": 1, "quantity": 2}],
        total_amount=59.98,
        shipping_address={"city": "SF", "state": "CA"}
    )
)

# Validate and serialize
event_json = event.json()
```

**Event Versioning Strategy:**

```python
class EventVersioning:
    """Handle event schema evolution"""
    
    # Version 1.0 - Original
    class OrderCreatedV1(BaseEvent):
        event_version: str = "1.0"
        
        class Data(BaseModel):
            order_id: int
            user_id: int
            total_amount: float
        
        data: Data
    
    # Version 2.0 - Added items array (breaking change)
    class OrderCreatedV2(BaseEvent):
        event_version: str = "2.0"
        
        class Data(BaseModel):
            order_id: int
            user_id: int
            total_amount: float
            items: List[dict]  # New required field
        
        data: Data
    
    # Version 2.1 - Added optional discount (non-breaking)
    class OrderCreatedV2_1(BaseEvent):
        event_version: str = "2.1"
        
        class Data(BaseModel):
            order_id: int
            user_id: int
            total_amount: float
            items: List[dict]
            discount: Optional[float] = None  # Optional - non-breaking
        
        data: Data
    
    @staticmethod
    def deserialize(event_json):
        """Deserialize event based on version"""
        data = json.loads(event_json)
        version = data.get('event_version', '1.0')
        
        # Route to appropriate class
        if version == '1.0':
            return EventVersioning.OrderCreatedV1(**data)
        elif version == '2.0':
            return EventVersioning.OrderCreatedV2(**data)
        elif version == '2.1':
            return EventVersioning.OrderCreatedV2_1(**data)
        else:
            raise ValueError(f"Unknown event version: {version}")
    
    @staticmethod
    def upgrade_event(old_event):
        """Upgrade old event to new version"""
        if old_event.event_version == '1.0':
            # Upgrade v1 to v2 (add empty items array)
            return EventVersioning.OrderCreatedV2(
                event_id=old_event.event_id,
                timestamp=old_event.timestamp,
                source=old_event.source,
                data=EventVersioning.OrderCreatedV2.Data(
                    order_id=old_event.data.order_id,
                    user_id=old_event.data.user_id,
                    total_amount=old_event.data.total_amount,
                    items=[]  # Default for old events
                )
            )
        return old_event

# Backward-compatible consumer
@event_bus.subscribe('order.created')
def handle_order_created(event_json):
    """Handle any version of order.created event"""
    event = EventVersioning.deserialize(event_json)
    
    # Upgrade to latest version if needed
    if event.event_version != '2.1':
        event = EventVersioning.upgrade_event(event)
    
    # Process event
    process_order(event.data)
```

**Event Schema Registry:**

```python
# Use Schema Registry (Confluent, AWS Glue)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

class SchemaRegistry:
    """Manage event schemas centrally"""
    
    def __init__(self, registry_url='http://localhost:8081'):
        self.client = SchemaRegistryClient({'url': registry_url})
    
    def register_schema(self, subject, schema):
        """Register new schema version"""
        schema_id = self.client.register_schema(subject, schema)
        return schema_id
    
    def get_schema(self, subject, version='latest'):
        """Get schema by version"""
        return self.client.get_version(subject, version)
    
    def check_compatibility(self, subject, schema):
        """Check if new schema is compatible"""
        return self.client.test_compatibility(subject, schema)

# Avro schema (strongly typed, evolvable)
order_created_schema = {
    "type": "record",
    "name": "OrderCreated",
    "namespace": "com.example.events",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "order_id", "type": "long"},
        {"name": "user_id", "type": "long"},
        {"name": "total_amount", "type": "double"},
        {
            "name": "discount",
            "type": ["null", "double"],  # Optional field
            "default": None
        }
    ]
}

registry = SchemaRegistry()
schema_id = registry.register_schema('order.created', order_created_schema)
```

**Verification:**
- [ ] Event schemas defined with Pydantic/Avro
- [ ] Versioning strategy established
- [ ] Schema registry configured (if using)
- [ ] Backward compatibility tested
- [ ] Documentation generated from schemas

**If This Fails:**
→ Start with JSON Schema (simpler than Avro)
→ Use semantic versioning for events
→ Add version to event_type: "order.created.v2"

---

### Step 3: Implement Event Publisher

**What:** Create reliable event publishers that handle failures gracefully

**How:**

**Kafka Event Publisher:**

```python
# Install: pip install confluent-kafka

from confluent_kafka import Producer, KafkaError
import json

class KafkaEventPublisher:
    """Reliable Kafka event publisher"""
    
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': socket.gethostname(),
            'acks': 'all',  # Wait for all replicas
            'retries': 3,
            'max.in.flight.requests.per.connection': 1,  # Ensure ordering
            'enable.idempotence': True,  # Exactly-once delivery
            'compression.type': 'snappy'
        })
    
    def publish(self, topic, event, key=None):
        """
        Publish event to Kafka
        
        Args:
            topic: Kafka topic
            event: Event object (with .json() method)
            key: Partition key (for ordering)
        """
        try:
            # Serialize event
            value = event.json() if hasattr(event, 'json') else json.dumps(event)
            
            # Publish asynchronously
            self.producer.produce(
                topic=topic,
                value=value.encode('utf-8'),
                key=key.encode('utf-8') if key else None,
                callback=self._delivery_callback
            )
            
            # Flush to ensure delivery (optional)
            self.producer.flush(timeout=10)
            
            return True
            
        except KafkaError as e:
            print(f"Failed to publish event: {e}")
            return False
    
    def _delivery_callback(self, err, msg):
        """Callback for delivery confirmation"""
        if err:
            print(f"❌ Event delivery failed: {err}")
        else:
            print(f"✅ Event delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")
    
    def close(self):
        """Flush and close producer"""
        self.producer.flush()

# Usage
publisher = KafkaEventPublisher()

event = OrderCreatedEvent(
    source="order-service",
    data=OrderCreatedEvent.OrderData(
        order_id=12345,
        user_id=789,
        items=[{"product_id": 1, "quantity": 2}],
        total_amount=59.98,
        shipping_address={"city": "SF"}
    )
)

# Publish with order_id as key (ensures ordering per order)
publisher.publish(
    topic='orders',
    event=event,
    key=str(event.data.order_id)
)
```

**RabbitMQ Event Publisher:**

```python
# Install: pip install pika

import pika
import json

class RabbitMQEventPublisher:
    """Reliable RabbitMQ event publisher"""
    
    def __init__(self, host='localhost', exchange='events'):
        self.host = host
        self.exchange = exchange
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                heartbeat=600,
                blocked_connection_timeout=300
            )
        )
        self.channel = self.connection.channel()
        
        # Declare exchange
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type='topic',
            durable=True
        )
    
    def publish(self, routing_key, event):
        """
        Publish event to RabbitMQ
        
        Args:
            routing_key: Routing key (e.g., 'order.created')
            event: Event object
        """
        try:
            # Serialize event
            message = event.json() if hasattr(event, 'json') else json.dumps(event)
            
            # Publish with delivery confirmation
            self.channel.confirm_delivery()
            
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message.encode('utf-8'),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json',
                    message_id=event.event_id if hasattr(event, 'event_id') else None
                )
            )
            
            print(f"✅ Published event: {routing_key}")
            return True
            
        except pika.exceptions.AMQPError as e:
            print(f"❌ Failed to publish event: {e}")
            self._reconnect()
            return False
    
    def _reconnect(self):
        """Reconnect if connection lost"""
        try:
            self.close()
        except:
            pass
        self._connect()
    
    def close(self):
        """Close connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

# Usage
publisher = RabbitMQEventPublisher()

event = OrderCreatedEvent(source="order-service", data={...})
publisher.publish('order.created', event)
```

**Transactional Outbox Pattern:**

```python
# Ensure events are published reliably with database transactions

class TransactionalOutbox:
    """
    Outbox pattern for reliable event publishing
    Events stored in DB, then published asynchronously
    """
    
    def __init__(self, db_session, event_publisher):
        self.db = db_session
        self.publisher = event_publisher
    
    def publish_with_transaction(self, event, db_operation):
        """
        Publish event within database transaction
        Ensures event is sent if and only if DB operation succeeds
        """
        try:
            # 1. Execute business logic
            db_operation()
            
            # 2. Store event in outbox table (same transaction)
            outbox_entry = OutboxEvent(
                event_id=event.event_id,
                event_type=event.event_type,
                payload=event.json(),
                created_at=datetime.utcnow(),
                published=False
            )
            self.db.add(outbox_entry)
            
            # 3. Commit transaction (both business data + outbox)
            self.db.commit()
            
            # 4. Publish event asynchronously
            self._publish_pending_events()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Transaction failed: {e}")
            return False
    
    def _publish_pending_events(self):
        """
        Publish events from outbox
        Called by background worker
        """
        pending = self.db.query(OutboxEvent).filter(
            OutboxEvent.published == False
        ).order_by(OutboxEvent.created_at).limit(100).all()
        
        for entry in pending:
            try:
                # Deserialize and publish
                event = json.loads(entry.payload)
                success = self.publisher.publish(
                    topic=entry.event_type.split('.')[0],
                    event=event
                )
                
                if success:
                    # Mark as published
                    entry.published = True
                    entry.published_at = datetime.utcnow()
                    self.db.commit()
                
            except Exception as e:
                print(f"Failed to publish event {entry.event_id}: {e}")
                self.db.rollback()

# Usage
outbox = TransactionalOutbox(db_session, kafka_publisher)

def create_order_operation():
    order = Order(user_id=789, total=59.98)
    db_session.add(order)

event = OrderCreatedEvent(source="order-service", data={...})
outbox.publish_with_transaction(event, create_order_operation)
```

**Verification:**
- [ ] Events published successfully
- [ ] Delivery confirmations working
- [ ] Failed publishes retried
- [ ] Events idempotent (can be published multiple times safely)
- [ ] Transactional outbox implemented for critical events

**If This Fails:**
→ Use synchronous publishing first (blocking)
→ Add retry logic with exponential backoff
→ Monitor publish failures with alerts

---

### Step 4: Implement Event Consumer

**What:** Create robust event consumers that handle events reliably

**How:**

**Kafka Event Consumer:**

```python
from confluent_kafka import Consumer, KafkaError
import json

class KafkaEventConsumer:
    """Reliable Kafka event consumer"""
    
    def __init__(self, group_id, topics, bootstrap_servers='localhost:9092'):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,  # Manual commit for reliability
            'max.poll.interval.ms': 300000,  # 5 minutes
            'session.timeout.ms': 10000
        })
        
        self.consumer.subscribe(topics)
        self.handlers = {}
    
    def register_handler(self, event_type, handler_func):
        """Register event handler function"""
        self.handlers[event_type] = handler_func
    
    def start_consuming(self):
        """Start consuming events"""
        print(f"🎧 Started consuming events")
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Error: {msg.error()}")
                        continue
                
                # Process message
                self._handle_message(msg)
                
        except KeyboardInterrupt:
            print("Stopping consumer...")
        finally:
            self.consumer.close()
    
    def _handle_message(self, msg):
        """Handle individual message"""
        try:
            # Deserialize
            event = json.loads(msg.value().decode('utf-8'))
            event_type = event.get('event_type')
            
            # Find handler
            handler = self.handlers.get(event_type)
            if not handler:
                print(f"No handler for event type: {event_type}")
                self.consumer.commit(msg)
                return
            
            # Execute handler
            print(f"📨 Processing: {event_type} (offset: {msg.offset()})")
            handler(event)
            
            # Commit offset (only after successful processing)
            self.consumer.commit(msg)
            print(f"✅ Processed: {event_type}")
            
        except Exception as e:
            print(f"❌ Error processing event: {e}")
            # Don't commit - will retry on next poll

# Usage
consumer = KafkaEventConsumer(
    group_id='order-processor',
    topics=['orders', 'payments']
)

# Register handlers
@consumer.register_handler('order.created')
def handle_order_created(event):
    order_id = event['data']['order_id']
    print(f"Processing order {order_id}")
    
    # Business logic
    send_order_confirmation_email(event['data'])
    update_inventory(event['data']['items'])

@consumer.register_handler('payment.processed')
def handle_payment_processed(event):
    order_id = event['data']['order_id']
    print(f"Payment processed for order {order_id}")
    
    # Business logic
    fulfill_order(order_id)

# Start consuming
consumer.start_consuming()
```

**Idempotent Event Handler:**

```python
class IdempotentEventHandler:
    """
    Ensure events are processed exactly once
    Even if delivered multiple times
    """
    
    def __init__(self, redis_client, ttl=86400):
        self.redis = redis_client
        self.ttl = ttl  # 24 hours
    
    def handle_once(self, event_id, handler_func, *args, **kwargs):
        """Execute handler only if not already processed"""
        # Check if already processed
        key = f"processed:event:{event_id}"
        
        if self.redis.get(key):
            print(f"⏭️  Event {event_id} already processed, skipping")
            return None
        
        try:
            # Execute handler
            result = handler_func(*args, **kwargs)
            
            # Mark as processed
            self.redis.setex(key, self.ttl, '1')
            
            print(f"✅ Event {event_id} processed")
            return result
            
        except Exception as e:
            print(f"❌ Event {event_id} processing failed: {e}")
            # Don't mark as processed - will retry
            raise

# Usage
idempotent_handler = IdempotentEventHandler(redis_client)

@consumer.register_handler('order.created')
def handle_order_created(event):
    def process_order():
        # Business logic that should only run once
        order_id = event['data']['order_id']
        charge_customer(order_id)
        send_confirmation_email(order_id)
    
    # Ensure exactly-once processing
    idempotent_handler.handle_once(
        event_id=event['event_id'],
        handler_func=process_order
    )
```

**Dead Letter Queue Pattern:**

```python
class DeadLetterQueue:
    """
    Handle failed events
    Move to DLQ after max retries
    """
    
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.retry_counts = {}
    
    def handle_with_dlq(self, event, handler_func):
        """Handle event with DLQ fallback"""
        event_id = event.get('event_id')
        
        try:
            # Try to process
            handler_func(event)
            
            # Success - reset retry count
            if event_id in self.retry_counts:
                del self.retry_counts[event_id]
            
            return True
            
        except Exception as e:
            # Increment retry count
            self.retry_counts[event_id] = self.retry_counts.get(event_id, 0) + 1
            
            if self.retry_counts[event_id] >= self.max_retries:
                # Max retries exceeded - send to DLQ
                print(f"⚠️  Moving event {event_id} to DLQ after {self.max_retries} failures")
                self._send_to_dlq(event, error=str(e))
                
                # Remove from retry counts
                del self.retry_counts[event_id]
                
                return False
            else:
                # Retry
                retry_count = self.retry_counts[event_id]
                print(f"🔄 Retry {retry_count}/{self.max_retries} for event {event_id}")
                raise  # Let consumer retry
    
    def _send_to_dlq(self, event, error):
        """Send failed event to dead letter queue"""
        dlq_entry = {
            'original_event': event,
            'error': error,
            'retry_count': self.retry_counts.get(event.get('event_id'), 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Publish to DLQ topic
        dlq_publisher.publish('dlq', dlq_entry)
        
        # Also log to database for analysis
        db.execute(
            "INSERT INTO dead_letter_queue (event_id, event_type, payload, error) "
            "VALUES (?, ?, ?, ?)",
            (event['event_id'], event['event_type'], json.dumps(event), error)
        )

# Usage
dlq = DeadLetterQueue(max_retries=3)

@consumer.register_handler('order.created')
def handle_order_created(event):
    def process():
        # Logic that might fail
        order_id = event['data']['order_id']
        external_api.create_order(order_id)
    
    dlq.handle_with_dlq(event, lambda: process())
```

**Verification:**
- [ ] Events consumed and processed
- [ ] Offset committed after successful processing
- [ ] Idempotent handlers (can process same event twice safely)
- [ ] Dead letter queue for failed events
- [ ] Consumer group load balancing working

**If This Fails:**
→ Start with manual offset management
→ Add explicit deduplication with event IDs
→ Test failure scenarios (network issues, handler errors)

---

### Step 5: Implement Event Monitoring and Observability

**What:** Track event flow and detect issues in event-driven systems

**How:**

**Event Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge

class EventMetrics:
    """Track event publishing and consumption metrics"""
    
    # Published events
    events_published = Counter(
        'events_published_total',
        'Total events published',
        ['event_type', 'source']
    )
    
    publish_duration = Histogram(
        'event_publish_duration_seconds',
        'Time to publish event',
        ['event_type']
    )
    
    publish_failures = Counter(
        'event_publish_failures_total',
        'Failed event publishes',
        ['event_type', 'error_type']
    )
    
    # Consumed events
    events_consumed = Counter(
        'events_consumed_total',
        'Total events consumed',
        ['event_type', 'consumer_group']
    )
    
    consumption_duration = Histogram(
        'event_consumption_duration_seconds',
        'Time to process event',
        ['event_type', 'handler']
    )
    
    consumption_failures = Counter(
        'event_consumption_failures_total',
        'Failed event consumptions',
        ['event_type', 'error_type']
    )
    
    # Consumer lag
    consumer_lag = Gauge(
        'consumer_lag',
        'Number of events behind',
        ['consumer_group', 'topic', 'partition']
    )
    
    # Dead letter queue
    dlq_events = Counter(
        'dlq_events_total',
        'Events sent to DLQ',
        ['event_type', 'error_type']
    )

# Instrumented publisher
class InstrumentedPublisher:
    """Publisher with metrics"""
    
    def publish(self, topic, event):
        event_type = event.event_type
        
        with EventMetrics.publish_duration.labels(event_type).time():
            try:
                success = self.kafka_publisher.publish(topic, event)
                
                if success:
                    EventMetrics.events_published.labels(
                        event_type=event_type,
                        source=event.source
                    ).inc()
                else:
                    EventMetrics.publish_failures.labels(
                        event_type=event_type,
                        error_type='publish_error'
                    ).inc()
                
                return success
                
            except Exception as e:
                EventMetrics.publish_failures.labels(
                    event_type=event_type,
                    error_type=type(e).__name__
                ).inc()
                raise

# Instrumented consumer
class InstrumentedConsumer:
    """Consumer with metrics"""
    
    def handle_event(self, event, handler_func):
        event_type = event['event_type']
        
        with EventMetrics.consumption_duration.labels(
            event_type=event_type,
            handler=handler_func.__name__
        ).time():
            try:
                handler_func(event)
                
                EventMetrics.events_consumed.labels(
                    event_type=event_type,
                    consumer_group=self.group_id
                ).inc()
                
            except Exception as e:
                EventMetrics.consumption_failures.labels(
                    event_type=event_type,
                    error_type=type(e).__name__
                ).inc()
                raise
```

**Event Flow Visualization:**

```python
# Grafana dashboard queries

"""
# Events published per second
rate(events_published_total[5m])

# Event consumption lag
consumer_lag

# P99 event processing time
histogram_quantile(0.99, event_consumption_duration_seconds_bucket)

# Failed event rate
rate(event_consumption_failures_total[5m])

# Dead letter queue growth
rate(dlq_events_total[1h])
"""
```

**Event Tracing:**

```python
# Add trace context to events for distributed tracing

class TracedEvent(BaseEvent):
    """Event with trace context"""
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None

def publish_with_trace(topic, event):
    """Publish event with trace context"""
    # Get current trace context
    span = trace.get_current_span()
    span_context = span.get_span_context()
    
    # Add to event
    event.trace_id = format(span_context.trace_id, '032x')
    event.span_id = format(span_context.span_id, '016x')
    
    # Publish
    publisher.publish(topic, event)
    
    # Add event to trace
    span.add_event(
        name=f"event.published.{event.event_type}",
        attributes={
            "event.id": event.event_id,
            "event.type": event.event_type
        }
    )

def consume_with_trace(event, handler):
    """Consume event and continue trace"""
    # Extract trace context
    trace_id = int(event.get('trace_id', '0'), 16)
    span_id = int(event.get('span_id', '0'), 16)
    
    # Create child span
    with tracer.start_as_current_span(
        f"event.consumed.{event['event_type']}",
        context=trace.set_span_in_context(span_id)
    ) as span:
        span.set_attribute("event.id", event['event_id'])
        span.set_attribute("event.type", event['event_type'])
        
        # Process event
        handler(event)
```

**Verification:**
- [ ] Event metrics tracked (published, consumed, failed)
- [ ] Consumer lag monitored
- [ ] DLQ events tracked
- [ ] Trace context propagated
- [ ] Dashboards created for event flow
- [ ] Alerts configured for anomalies

**If This Fails:**
→ Start with basic logging
→ Add Prometheus metrics gradually
→ Use managed monitoring (DataDog, New Relic)

---

## Verification Checklist

After completing this workflow:

- [ ] Message broker deployed and configured
- [ ] Event schemas defined with versioning
- [ ] Event publisher implemented with retries
- [ ] Event consumers processing reliably
- [ ] Idempotent event handlers
- [ ] Dead letter queue for failed events
- [ ] Transactional outbox for critical events
- [ ] Monitoring and metrics in place
- [ ] Consumer lag monitored
- [ ] Trace context propagated across events
- [ ] Documentation updated

---

## Common Issues & Solutions

### Issue: Event ordering issues

**Symptoms:**
- Events processed out of order
- State inconsistencies
- Race conditions

**Solution:**
```python
# Use partition keys to ensure ordering

class OrderedEventPublisher:
    """Ensure events are ordered by key"""
    
    def publish_order_events(self, order_id, events):
        """
        Publish events with order_id as key
        All events for same order go to same partition
        """
        for event in events:
            publisher.publish(
                topic='orders',
                event=event,
                key=str(order_id)  # Same key = same partition = ordered
            )
    
    # Consumer processes events in order within partition
    # But may process different orders concurrently
```

**Prevention:**
- Use partition keys for entities that need ordering
- Design events to be independently processable
- Use event sequence numbers

---

## Best Practices

### DO:
✅ Design events to carry sufficient data
✅ Version events from the start
✅ Make event handlers idempotent
✅ Use dead letter queues
✅ Monitor consumer lag
✅ Implement transactional outbox for critical events
✅ Add trace context to events
✅ Use schema registry for validation
✅ Set appropriate retention periods
✅ Test failure scenarios

### DON'T:
❌ Share state between event handlers
❌ Ignore event ordering requirements
❌ Skip idempotency checks
❌ Let dead letter queue grow unbounded
❌ Publish events without schema validation
❌ Forget to handle event version migration
❌ Use events for request/response patterns
❌ Ignore consumer lag
❌ Hard-code event structure
❌ Skip monitoring and alerting

---

## Related Workflows

**Prerequisites:**
- `arc-004`: Distributed Systems Patterns - Foundation for event systems
- `arc-002`: Caching Strategies - Cache event data

**Next Steps:**
- `arc-006`: Microservices Patterns - Service communication
- `devops-008`: Application Performance Monitoring - Monitor events
- `dev-009`: Data Pipeline Development - Process event streams

**Alternatives:**
- Synchronous REST APIs (simpler, tight coupling)
- gRPC (faster, still synchronous)
- GraphQL Subscriptions (real-time, less complex)

---

## Tags
`architecture` `event-driven` `messaging` `kafka` `rabbitmq` `asynchronous` `pub-sub` `event-sourcing` `cqrs` `microservices`
