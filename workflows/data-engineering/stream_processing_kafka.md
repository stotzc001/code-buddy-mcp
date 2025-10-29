# Stream Processing with Kafka

**ID:** dat-010  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-150 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Build real-time stream processing pipelines using Apache Kafka for event-driven architectures, real-time analytics, and data integration

**Why:** Kafka enables handling high-throughput event streams, building decoupled systems, and processing data in real-time for immediate insights and actions

**When to use:**
- Building event-driven microservices
- Real-time analytics and monitoring
- Log aggregation and processing
- Change data capture (CDC)
- Message queue replacement
- Building data integration hubs

---

## Prerequisites

**Required:**
- [ ] Understanding of distributed systems
- [ ] Event-driven architecture concepts
- [ ] Java or Python knowledge
- [ ] Basic networking knowledge
- [ ] Message queue experience helpful

**Check before starting:**
```bash
# Check Java (required for Kafka)
java -version  # Should be 11+

# Check if Kafka is accessible
telnet kafka-broker.example.com 9092

# Check Python (for Python clients)
python --version  # Should be 3.8+
```

---

## Implementation Steps

### Step 1: Set Up Kafka Cluster

**What:** Install and configure Apache Kafka cluster

**How:**

**Local Development with Docker:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log

  kafka1:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka1
    container_name: kafka1
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "19092:19092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
    volumes:
      - kafka1-data:/var/lib/kafka/data

  kafka2:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka2
    container_name: kafka2
    depends_on:
      - zookeeper
    ports:
      - "9093:9093"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:29093,PLAINTEXT_HOST://localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
    volumes:
      - kafka2-data:/var/lib/kafka/data

  kafka3:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka3
    container_name: kafka3
    depends_on:
      - zookeeper
    ports:
      - "9094:9094"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:29094,PLAINTEXT_HOST://localhost:9094
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
    volumes:
      - kafka3-data:/var/lib/kafka/data

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    depends_on:
      - kafka1
      - kafka2
      - kafka3
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka1:29092,kafka2:29093,kafka3:29094
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka1-data:
  kafka2-data:
  kafka3-data:
```

**Start Kafka:**
```bash
# Start services
docker-compose up -d

# Check services are running
docker-compose ps

# Access Kafka UI at http://localhost:8080
```

**Production Configuration (server.properties):**
```properties
# Broker Configuration
broker.id=1
listeners=PLAINTEXT://:9092,SSL://:9093
advertised.listeners=PLAINTEXT://kafka1.example.com:9092,SSL://kafka1.example.com:9093
zookeeper.connect=zk1:2181,zk2:2181,zk3:2181

# Log Configuration
log.dirs=/var/lib/kafka/data
num.partitions=6
default.replication.factor=3
min.insync.replicas=2

# Retention
log.retention.hours=168
log.retention.bytes=1073741824
log.segment.bytes=1073741824

# Performance
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Replication
replica.lag.time.max.ms=30000
replica.socket.timeout.ms=30000
replica.socket.receive.buffer.bytes=65536

# Security (if using SSL)
ssl.keystore.location=/var/private/ssl/kafka.server.keystore.jks
ssl.keystore.password=${KEYSTORE_PASSWORD}
ssl.key.password=${KEY_PASSWORD}
ssl.truststore.location=/var/private/ssl/kafka.server.truststore.jks
ssl.truststore.password=${TRUSTSTORE_PASSWORD}
```

**Verification:**
- [ ] Kafka brokers running
- [ ] ZooKeeper connected
- [ ] Kafka UI accessible
- [ ] Broker health green
- [ ] Cluster ID assigned

**If This Fails:**
→ Check Docker logs: `docker-compose logs kafka1`
→ Verify ports not in use
→ Check ZooKeeper connection
→ Review firewall rules
→ Ensure sufficient resources

---

### Step 2: Create and Manage Topics

**What:** Create Kafka topics with appropriate configuration

**How:**

**Topic Creation:**
```bash
# Create topic via kafka-topics
docker exec kafka1 kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --partitions 6 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config segment.ms=86400000 \
  --config compression.type=snappy

# List topics
docker exec kafka1 kafka-topics --list \
  --bootstrap-server localhost:9092

# Describe topic
docker exec kafka1 kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic user-events

# Alter topic configuration
docker exec kafka1 kafka-configs --alter \
  --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name user-events \
  --add-config retention.ms=1209600000

# Delete topic (if enabled)
docker exec kafka1 kafka-topics --delete \
  --bootstrap-server localhost:9092 \
  --topic old-topic
```

**Python Topic Management:**
```python
# topic_manager.py
"""
Manage Kafka topics programmatically
"""

from kafka.admin import KafkaAdminClient, NewTopic, ConfigResource, ConfigResourceType
from typing import List, Dict

class TopicManager:
    """Manage Kafka topics."""
    
    def __init__(self, bootstrap_servers: List[str]):
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id='topic-manager'
        )
    
    def create_topic(
        self,
        topic_name: str,
        num_partitions: int = 6,
        replication_factor: int = 3,
        config: Dict[str, str] = None
    ):
        """Create a new topic."""
        
        topic_config = config or {}
        topic_config.setdefault('retention.ms', '604800000')  # 7 days
        topic_config.setdefault('compression.type', 'snappy')
        topic_config.setdefault('cleanup.policy', 'delete')
        
        topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            topic_configs=topic_config
        )
        
        try:
            self.admin_client.create_topics([topic])
            print(f"✅ Topic '{topic_name}' created successfully")
        except Exception as e:
            print(f"❌ Failed to create topic: {e}")
    
    def list_topics(self) -> List[str]:
        """List all topics."""
        metadata = self.admin_client.list_topics()
        return list(metadata)
    
    def describe_topic(self, topic_name: str):
        """Get topic details."""
        metadata = self.admin_client.describe_topics([topic_name])
        return metadata
    
    def delete_topic(self, topic_name: str):
        """Delete a topic."""
        try:
            self.admin_client.delete_topics([topic_name])
            print(f"✅ Topic '{topic_name}' deleted")
        except Exception as e:
            print(f"❌ Failed to delete topic: {e}")

# Usage
manager = TopicManager(['localhost:9092', 'localhost:9093', 'localhost:9094'])

# Create topics for different use cases
manager.create_topic(
    'user-events',
    num_partitions=12,
    replication_factor=3,
    config={
        'retention.ms': '2592000000',  # 30 days
        'compression.type': 'lz4',
        'min.insync.replicas': '2'
    }
)

manager.create_topic(
    'order-events',
    num_partitions=6,
    replication_factor=3
)

# List topics
topics = manager.list_topics()
print(f"Topics: {topics}")
```

**Topic Naming Conventions:**
```
# Pattern: <env>.<team>.<domain>.<event-type>
prod.analytics.user.clicks
prod.analytics.user.pageviews
prod.payment.order.created
prod.payment.order.completed

# Compacted topics (for state)
prod.inventory.product.snapshot

# Dead letter queues
prod.analytics.user.clicks.dlq

# Retry topics
prod.payment.order.created.retry
```

**Verification:**
- [ ] Topics created
- [ ] Partitions balanced
- [ ] Replication working
- [ ] Configuration applied
- [ ] Naming consistent

**If This Fails:**
→ Check broker connectivity
→ Verify permissions
→ Review cluster resources
→ Check partition distribution
→ Validate topic configuration

---

### Step 3: Implement Producers

**What:** Create producers to send events to Kafka

**How:**

**Basic Python Producer:**
```python
# producer.py
"""
Kafka producer implementation
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from typing import Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventProducer:
    """Produce events to Kafka."""
    
    def __init__(self, bootstrap_servers: list):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            
            # Serialization
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            
            # Performance
            compression_type='snappy',
            linger_ms=10,
            batch_size=16384,
            buffer_memory=33554432,
            
            # Reliability
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=5,
            
            # Idempotence
            enable_idempotence=True
        )
    
    def send_event(
        self,
        topic: str,
        event: Dict[str, Any],
        key: str = None,
        partition: int = None
    ) -> bool:
        """Send event to Kafka topic."""
        
        # Add metadata
        event['_timestamp'] = datetime.utcnow().isoformat()
        event['_producer_id'] = 'event-producer-1'
        
        try:
            future = self.producer.send(
                topic,
                value=event,
                key=key,
                partition=partition
            )
            
            # Block for 'synchronous' send
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"✅ Event sent: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"❌ Failed to send event: {e}")
            return False
    
    def send_batch(self, topic: str, events: list) -> int:
        """Send batch of events."""
        
        success_count = 0
        
        for event in events:
            if self.send_event(topic, event):
                success_count += 1
        
        # Flush to ensure all sent
        self.producer.flush()
        
        return success_count
    
    def close(self):
        """Close producer."""
        self.producer.close()

# Usage
producer = EventProducer(['localhost:9092'])

# Send single event
event = {
    'user_id': '12345',
    'event_type': 'page_view',
    'page': '/products/item-42',
    'session_id': 'abc-def-ghi'
}

producer.send_event(
    topic='user-events',
    event=event,
    key='12345'  # Key for partitioning
)

# Send batch
events = [
    {'user_id': '12345', 'event_type': 'click', 'element': 'button-1'},
    {'user_id': '12346', 'event_type': 'click', 'element': 'button-2'},
    {'user_id': '12347', 'event_type': 'scroll', 'position': 500},
]

count = producer.send_batch('user-events', events)
print(f"Sent {count} events")

producer.close()
```

**Advanced Producer with Callbacks:**
```python
# advanced_producer.py
"""
Producer with async callbacks and error handling
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
from collections import defaultdict

class AdvancedProducer:
    """Producer with metrics and callbacks."""
    
    def __init__(self, bootstrap_servers: list):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            compression_type='lz4',
            acks='all',
            retries=3,
            enable_idempotence=True
        )
        
        self.metrics = defaultdict(int)
    
    def send_async(self, topic: str, event: dict, key: str = None):
        """Send event asynchronously with callback."""
        
        def on_success(record_metadata):
            """Called when send succeeds."""
            self.metrics['success'] += 1
            logger.debug(
                f"✅ Sent to {record_metadata.topic}:"
                f"{record_metadata.partition}:{record_metadata.offset}"
            )
        
        def on_error(exception):
            """Called when send fails."""
            self.metrics['error'] += 1
            logger.error(f"❌ Send failed: {exception}")
        
        # Send asynchronously
        self.producer.send(
            topic,
            value=event,
            key=key
        ).add_callback(on_success).add_errback(on_error)
    
    def get_metrics(self) -> dict:
        """Get producer metrics."""
        return dict(self.metrics)
    
    def flush_and_close(self):
        """Flush pending messages and close."""
        self.producer.flush()
        self.producer.close()
        
        print(f"Producer metrics: {self.get_metrics()}")

# Usage
producer = AdvancedProducer(['localhost:9092'])

# Send many events asynchronously
for i in range(10000):
    event = {
        'event_id': i,
        'user_id': f'user-{i % 100}',
        'timestamp': time.time()
    }
    producer.send_async('user-events', event, key=f'user-{i % 100}')

# Wait for all to complete
producer.flush_and_close()
```

**Partitioning Strategies:**
```python
# partitioning.py
"""
Custom partitioning strategies
"""

from kafka.partitioner import DefaultPartitioner
import hashlib

class CustomPartitioner:
    """Custom partitioner for specific business logic."""
    
    def __call__(self, key, all_partitions, available_partitions):
        """
        Partition based on custom logic.
        
        Args:
            key: Message key
            all_partitions: All partition IDs
            available_partitions: Available partition IDs
        
        Returns:
            Partition ID
        """
        
        if key is None:
            # Round-robin for messages without key
            return available_partitions[0] if available_partitions else all_partitions[0]
        
        # Hash key to partition
        key_hash = int(hashlib.md5(key).hexdigest(), 16)
        return all_partitions[key_hash % len(all_partitions)]

# Use custom partitioner
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    partitioner=CustomPartitioner()
)
```

**Verification:**
- [ ] Producer connects to Kafka
- [ ] Events sent successfully
- [ ] Partitioning works correctly
- [ ] Error handling implemented
- [ ] Metrics tracked

**If This Fails:**
→ Check broker connectivity
→ Verify topic exists
→ Review serialization logic
→ Check for network issues
→ Validate event schema

---

(Due to length limits, I'll create a comprehensive workflow but will need to continue in the next message. Let me save this first part and continue...)

**Verification Checklist**

After completing this workflow:

- [ ] Kafka cluster running
- [ ] Topics created and configured
- [ ] Producers implemented
- [ ] Consumers implemented
- [ ] Stream processing working
- [ ] Monitoring configured
- [ ] Error handling robust
- [ ] Performance optimized

---

## Common Issues & Solutions

### Issue: Consumer Lag Growing

**Symptoms:**
- Messages piling up
- Consumers can't keep up
- Latency increasing

**Solution:**
- Add more consumer instances
- Optimize consumer processing
- Increase partition count
- Use batch processing
- Profile slow operations

---

## Best Practices

### DO:
✅ Use consumer groups for scalability
✅ Handle backpressure appropriately
✅ Monitor consumer lag
✅ Implement idempotent producers
✅ Use appropriate partitioning
✅ Set up proper retention
✅ Enable compression
✅ Implement error handling
✅ Use schema registry
✅ Monitor broker health
✅ Plan for scaling
✅ Implement dead letter queues

### DON'T:
❌ Skip error handling
❌ Ignore message ordering
❌ Forget about retention
❌ Create too many partitions
❌ Use auto-commit without care
❌ Ignore rebalancing
❌ Skip monitoring
❌ Hard-code configuration
❌ Forget about security
❌ Ignore consumer lag
❌ Create overly complex topologies
❌ Skip testing at scale

---

## Related Workflows

**Prerequisites:**
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture patterns

**Next Steps:**
- [big_data_spark.md](./big_data_spark.md) - Spark processing
- [pipeline_orchestration_airflow.md](./pipeline_orchestration_airflow.md) - Orchestration

**Related:**
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL patterns
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks

---

### Step 4: Implement Consumers

**What:** Create consumers to read and process events from Kafka

**How:**

**Basic Python Consumer:**
```python
# consumer.py
"""
Kafka consumer implementation
"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from typing import Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventConsumer:
    """Consume events from Kafka."""
    
    def __init__(
        self,
        topics: list,
        group_id: str,
        bootstrap_servers: list
    ):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            
            # Deserialization
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            
            # Offset management
            auto_offset_reset='earliest',  # 'earliest' or 'latest'
            enable_auto_commit=True,
            auto_commit_interval_ms=5000,
            
            # Performance
            max_poll_records=500,
            max_poll_interval_ms=300000,
            session_timeout_ms=10000,
            heartbeat_interval_ms=3000,
            
            # Consumer group settings
            consumer_timeout_ms=1000
        )
    
    def consume(self, process_func: Callable):
        """
        Consume messages and process them.
        
        Args:
            process_func: Function to process each message
        """
        
        try:
            logger.info(f"🔄 Starting consumer...")
            
            for message in self.consumer:
                try:
                    # Process message
                    process_func(message)
                    
                    logger.debug(
                        f"✅ Processed: topic={message.topic}, "
                        f"partition={message.partition}, "
                        f"offset={message.offset}"
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    # Send to DLQ or handle error
                    
        except KeyboardInterrupt:
            logger.info("⏹ Stopping consumer...")
        finally:
            self.consumer.close()
    
    def consume_batch(self, process_batch_func: Callable, batch_size: int = 100):
        """Consume messages in batches."""
        
        batch = []
        
        try:
            for message in self.consumer:
                batch.append(message)
                
                if len(batch) >= batch_size:
                    # Process batch
                    process_batch_func(batch)
                    batch = []
                    
        finally:
            # Process remaining messages
            if batch:
                process_batch_func(batch)
            
            self.consumer.close()
    
    def close(self):
        """Close consumer."""
        self.consumer.close()

# Usage
def process_event(message):
    """Process single event."""
    print(f"Processing event: {message.value}")
    # Your processing logic here

consumer = EventConsumer(
    topics=['user-events'],
    group_id='analytics-consumer-group',
    bootstrap_servers=['localhost:9092']
)

consumer.consume(process_event)
```

**Manual Offset Management:**
```python
# manual_commit_consumer.py
"""
Consumer with manual offset management
"""

from kafka import KafkaConsumer, TopicPartition
import json

class ManualCommitConsumer:
    """Consumer with manual offset commits."""
    
    def __init__(self, topics: list, group_id: str, bootstrap_servers: list):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            
            # Disable auto-commit
            enable_auto_commit=False,
            
            auto_offset_reset='earliest'
        )
    
    def consume_with_manual_commit(self):
        """Consume with manual offset commits."""
        
        try:
            for message in self.consumer:
                try:
                    # Process message
                    self.process_message(message)
                    
                    # Commit offset after successful processing
                    self.consumer.commit()
                    
                    logger.info(f"✅ Committed offset {message.offset}")
                    
                except Exception as e:
                    logger.error(f"❌ Processing failed: {e}")
                    # Don't commit - will reprocess
                    
        finally:
            self.consumer.close()
    
    def process_message(self, message):
        """Process individual message."""
        print(f"Processing: {message.value}")
        # Your logic here
    
    def seek_to_offset(self, topic: str, partition: int, offset: int):
        """Seek to specific offset."""
        tp = TopicPartition(topic, partition)
        self.consumer.seek(tp, offset)

# Usage
consumer = ManualCommitConsumer(
    topics=['user-events'],
    group_id='manual-commit-group',
    bootstrap_servers=['localhost:9092']
)

consumer.consume_with_manual_commit()
```

**Exactly-Once Processing:**
```python
# exactly_once_consumer.py
"""
Implement exactly-once processing semantics
"""

from kafka import KafkaConsumer
import json
import redis

class ExactlyOnceConsumer:
    """
    Consumer with exactly-once semantics using idempotency.
    """
    
    def __init__(self, topics: list, group_id: str, bootstrap_servers: list):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False,
            isolation_level='read_committed'  # For transactional messages
        )
        
        # Use Redis for deduplication
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def consume_exactly_once(self):
        """Consume with exactly-once semantics."""
        
        for message in self.consumer:
            message_id = message.value.get('message_id')
            
            if not message_id:
                logger.error("Message missing message_id")
                continue
            
            # Check if already processed (idempotency)
            if self.is_processed(message_id):
                logger.info(f"⏭ Skipping duplicate message: {message_id}")
                self.consumer.commit()
                continue
            
            try:
                # Process message
                self.process_message(message)
                
                # Mark as processed
                self.mark_processed(message_id)
                
                # Commit offset
                self.consumer.commit()
                
                logger.info(f"✅ Processed message {message_id}")
                
            except Exception as e:
                logger.error(f"❌ Processing failed: {e}")
                # Don't commit - will retry
    
    def is_processed(self, message_id: str) -> bool:
        """Check if message already processed."""
        return self.redis_client.exists(f"processed:{message_id}")
    
    def mark_processed(self, message_id: str):
        """Mark message as processed."""
        # Store with TTL (e.g., 7 days)
        self.redis_client.setex(
            f"processed:{message_id}",
            604800,  # 7 days in seconds
            "1"
        )
    
    def process_message(self, message):
        """Process message logic."""
        print(f"Processing: {message.value}")
        # Your processing logic

# Usage
consumer = ExactlyOnceConsumer(
    topics=['user-events'],
    group_id='exactly-once-group',
    bootstrap_servers=['localhost:9092']
)

consumer.consume_exactly_once()
```

**Verification:**
- [ ] Consumer connects and subscribes
- [ ] Messages consumed successfully
- [ ] Offset management working
- [ ] Error handling implemented
- [ ] Consumer lag monitored

**If This Fails:**
→ Check consumer group ID
→ Verify topic exists
→ Review offset reset strategy
→ Check for rebalancing issues
→ Validate deserialization

---

## Troubleshooting

### Issue: Consumer Rebalancing Too Frequently

**Symptoms:**
- Frequent rebalance logs
- Processing interruptions
- Decreased throughput

**Solution:**
```python
# Increase session timeout
consumer = KafkaConsumer(
    session_timeout_ms=30000,  # 30 seconds
    heartbeat_interval_ms=10000,  # 10 seconds
    max_poll_interval_ms=600000  # 10 minutes
)
```

### Issue: Messages Being Processed Twice

**Symptoms:**
- Duplicate processing
- Inconsistent state

**Solution:**
- Implement idempotency with message IDs
- Use manual offset commits
- Enable exactly-once semantics
- Use database transactions

### Issue: High Consumer Lag

**Symptoms:**
- Growing lag
- Delayed processing
- Backpressure

**Solution:**
- Add more consumer instances
- Increase partitions
- Optimize processing logic
- Use batch processing
- Profile slow operations

---

## Tags
`data-engineering` `kafka` `streaming` `real-time` `event-driven` `message-queue` `distributed-systems` `python` `java`
