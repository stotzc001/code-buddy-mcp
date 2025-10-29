# Data Pipeline Architecture

**ID:** dat-004  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 60-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design robust, scalable data pipeline architectures using modern patterns and best practices

**Why:** Well-designed pipelines ensure reliable data flow, enable scalability, support business intelligence, and maintain data quality across the organization

**When to use:**
- Designing new data platform
- Modernizing legacy ETL systems
- Building real-time data pipelines
- Creating data integration layer
- Implementing data mesh architecture
- Scaling existing data infrastructure

---

## Prerequisites

**Required:**
- [ ] Understanding of data sources and targets
- [ ] Knowledge of batch vs streaming patterns
- [ ] Familiarity with orchestration tools
- [ ] Basic cloud infrastructure knowledge
- [ ] Understanding of data modeling

**Check before starting:**
```bash
# Check tool availability
docker --version
python --version
terraform --version  # If using IaC

# Verify cloud CLI (if using cloud)
aws --version
# or
gcloud --version
# or
az --version
```

---

## Implementation Steps

### Step 1: Choose Pipeline Architecture Pattern

**What:** Select the appropriate architecture pattern based on requirements

**How:**

**Pattern Decision Matrix:**
```python
"""
Pipeline Architecture Pattern Selection
"""

from dataclasses import dataclass
from typing import List, Literal
from enum import Enum

class ArchitecturePattern(Enum):
    BATCH_ETL = "batch_etl"
    STREAMING = "streaming"
    LAMBDA = "lambda"
    KAPPA = "kappa"
    MEDALLION = "medallion"
    DATA_MESH = "data_mesh"

@dataclass
class PipelineRequirements:
    """Define pipeline requirements."""
    latency: Literal["seconds", "minutes", "hours", "days"]
    data_volume_gb_per_day: float
    data_sources: int
    data_variety: Literal["structured", "semi-structured", "mixed"]
    query_patterns: List[str]  # ["batch_analytics", "real_time_dashboard", "ml"]
    team_size: int
    domain_complexity: Literal["simple", "moderate", "complex"]

def recommend_architecture(reqs: PipelineRequirements) -> ArchitecturePattern:
    """Recommend architecture pattern."""
    
    # Real-time requirements
    if reqs.latency == "seconds":
        if "batch_analytics" in reqs.query_patterns:
            return ArchitecturePattern.LAMBDA
        return ArchitecturePattern.KAPPA
    
    # Complex domain with multiple teams
    if reqs.domain_complexity == "complex" and reqs.team_size > 20:
        return ArchitecturePattern.DATA_MESH
    
    # Layered processing for data quality
    if reqs.data_variety == "mixed" and reqs.data_volume_gb_per_day > 1000:
        return ArchitecturePattern.MEDALLION
    
    # Simple streaming
    if reqs.latency in ["seconds", "minutes"]:
        return ArchitecturePattern.STREAMING
    
    # Default: Batch ETL
    return ArchitecturePattern.BATCH_ETL
```

**Architecture Pattern 1: Batch ETL/ELT**
```yaml
# Traditional batch processing
pattern: Batch ETL/ELT
use_when:
  - Data updated daily/hourly
  - Historical data analysis primary use case
  - Cost optimization important
  - Simpler operational model preferred

components:
  extraction:
    - Scheduled jobs
    - Incremental pulls
    - Full refreshes
  
  transformation:
    - Pandas/Spark for ETL
    - dbt for ELT
    - SQL-based transforms
  
  loading:
    - Bulk inserts
    - Upserts
    - SCD patterns
  
  orchestration:
    - Apache Airflow
    - Prefect
    - Dagster

example_stack:
  - Source: PostgreSQL, APIs
  - Extract: Python scripts
  - Transform: dbt
  - Load: Snowflake
  - Orchestrate: Airflow
```

**Architecture Pattern 2: Lambda Architecture**
```yaml
# Combine batch and stream processing
pattern: Lambda Architecture
use_when:
  - Need both real-time and batch analytics
  - Historical reprocessing required
  - Complex aggregations needed
  - Eventual consistency acceptable

layers:
  batch_layer:
    purpose: Complete, accurate views
    technology: Spark, dbt
    schedule: Daily/hourly
    latency: Hours
  
  speed_layer:
    purpose: Real-time approximate views
    technology: Kafka, Flink, Spark Streaming
    latency: Seconds/minutes
  
  serving_layer:
    purpose: Merge batch + speed views
    technology: Druid, ClickHouse, Cassandra
    query_time: Milliseconds

example_architecture:
  ingestion:
    - Kafka for streaming events
    - S3 for batch dumps
  
  batch:
    - Spark jobs process S3 data
    - Output to Parquet on S3
    - Load to data warehouse
  
  stream:
    - Flink processes Kafka
    - Aggregates to Redis/Druid
    - Update real-time views
  
  serving:
    - Query layer merges views
    - API exposes unified data
```

**Architecture Pattern 3: Kappa Architecture**
```yaml
# Stream-only processing
pattern: Kappa Architecture
use_when:
  - All data arrives as events
  - Single processing logic preferred
  - Reprocessing by replay
  - Real-time focus

components:
  stream_layer:
    purpose: Single processing path
    technology: Kafka, Kinesis, Pulsar
    pattern: Event sourcing
  
  processing:
    technology: Flink, Kafka Streams
    pattern: Stateful stream processing
    reprocessing: Replay from beginning
  
  storage:
    real_time: ClickHouse, Druid
    historical: S3, Delta Lake
    state: RocksDB, DynamoDB

example_flow:
  - Events → Kafka topics
  - Flink consumes and processes
  - Results to ClickHouse
  - Replay for reprocessing
```

**Architecture Pattern 4: Medallion (Bronze/Silver/Gold)**
```yaml
# Lakehouse architecture
pattern: Medallion Architecture
use_when:
  - Data quality critical
  - Multiple processing stages
  - Various consumer needs
  - Governance required

layers:
  bronze:
    purpose: Raw data ingestion
    format: Original format preserved
    schema: Schema-on-read
    quality: No validation
    retention: Long-term (years)
  
  silver:
    purpose: Cleaned, conformed data
    format: Parquet/Delta
    schema: Enforced
    quality: Validated and deduplicated
    retention: Medium-term (months)
  
  gold:
    purpose: Business-level aggregates
    format: Optimized for queries
    schema: Denormalized
    quality: Production-ready
    retention: As needed

example_implementation:
  bronze:
    - Ingest JSON from APIs
    - Store in S3/Delta Lake
    - Partition by date
  
  silver:
    - Clean and standardize
    - Enforce schema
    - Remove duplicates
    - Store as Delta tables
  
  gold:
    - Create fact/dimension tables
    - Aggregate for dashboards
    - Optimize for queries
    - Store in data warehouse
```

**Architecture Pattern 5: Data Mesh**
```yaml
# Decentralized architecture
pattern: Data Mesh
use_when:
  - Large organization
  - Domain-driven design
  - Multiple data teams
  - Scalability issues with central team

principles:
  domain_ownership:
    - Teams own their data products
    - Domain-specific pipelines
    - Accountable for quality
  
  data_as_product:
    - Discoverable
    - Addressable
    - Trustworthy
    - Self-describing
  
  self_serve_platform:
    - Infrastructure as code
    - Standard tooling
    - Automated deployment
  
  federated_governance:
    - Global standards
    - Local implementation
    - Automated policy enforcement

example_structure:
  domains:
    - Customer domain: Owns customer data products
    - Order domain: Owns order data products
    - Analytics domain: Consumes from others
  
  platform:
    - Shared data infrastructure
    - CI/CD pipelines
    - Monitoring and alerting
    - Data catalog
  
  governance:
    - Data contracts
    - Schema registry
    - Access control
    - Quality SLAs
```

**Verification:**
- [ ] Pattern selected based on requirements
- [ ] Technology stack chosen
- [ ] Team skills matched to pattern
- [ ] Costs estimated
- [ ] Scalability requirements met

**If This Fails:**
→ Review requirements with stakeholders
→ Consider hybrid approach
→ Start with simpler pattern
→ Plan for evolution

---

### Step 2: Design Data Ingestion Layer

**What:** Design how data enters the pipeline from various sources

**How:**

**Ingestion Patterns:**
```python
"""
Data Ingestion Layer Design
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass

class IngestionMethod(Enum):
    BATCH_PULL = "batch_pull"
    BATCH_PUSH = "batch_push"
    STREAMING = "streaming"
    CDC = "change_data_capture"
    API_POLLING = "api_polling"

@dataclass
class DataSource:
    """Define a data source."""
    name: str
    type: str  # database, api, file, stream
    method: IngestionMethod
    frequency: str  # cron or "real-time"
    format: str  # json, csv, parquet, avro
    volume_mb_per_day: float
    schema_evolution: bool

class IngestionLayer:
    """Design ingestion layer."""
    
    def __init__(self):
        self.sources: List[DataSource] = []
        self.connectors: Dict[str, str] = {}
    
    def add_source(self, source: DataSource):
        """Add a data source."""
        self.sources.append(source)
        self._configure_connector(source)
    
    def _configure_connector(self, source: DataSource):
        """Configure appropriate connector."""
        if source.method == IngestionMethod.BATCH_PULL:
            if source.type == "database":
                self.connectors[source.name] = "JDBC/ODBC batch connector"
            elif source.type == "api":
                self.connectors[source.name] = "REST API poller"
            elif source.type == "file":
                self.connectors[source.name] = "S3/SFTP reader"
        
        elif source.method == IngestionMethod.STREAMING:
            if source.type == "database":
                self.connectors[source.name] = "Debezium CDC"
            elif source.type == "stream":
                self.connectors[source.name] = "Kafka consumer"
        
        elif source.method == IngestionMethod.CDC:
            self.connectors[source.name] = "Database CDC (Debezium/Maxwell)"
    
    def generate_architecture_diagram(self):
        """Generate architecture documentation."""
        diagram = {
            "sources": [
                {
                    "name": s.name,
                    "type": s.type,
                    "method": s.method.value,
                    "connector": self.connectors.get(s.name),
                    "frequency": s.frequency
                }
                for s in self.sources
            ]
        }
        return diagram

# Example ingestion layer design
ingestion = IngestionLayer()

# Add various sources
ingestion.add_source(DataSource(
    name="postgres_orders",
    type="database",
    method=IngestionMethod.CDC,
    frequency="real-time",
    format="json",
    volume_mb_per_day=5000,
    schema_evolution=True
))

ingestion.add_source(DataSource(
    name="salesforce_api",
    type="api",
    method=IngestionMethod.API_POLLING,
    frequency="0 */6 * * *",  # Every 6 hours
    format="json",
    volume_mb_per_day=500,
    schema_evolution=False
))

ingestion.add_source(DataSource(
    name="s3_logs",
    type="file",
    method=IngestionMethod.BATCH_PULL,
    frequency="0 1 * * *",  # Daily at 1 AM
    format="json",
    volume_mb_per_day=10000,
    schema_evolution=False
))
```

**Batch Ingestion with Airflow:**
```python
"""
Airflow DAG for batch ingestion
"""

from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def ingest_from_postgres(**context):
    """Extract data from PostgreSQL."""
    pg_hook = PostgresHook(postgres_conn_id='source_db')
    
    # Get last watermark
    execution_date = context['execution_date']
    
    # Incremental query
    query = f"""
        SELECT *
        FROM orders
        WHERE updated_at >= '{execution_date}'
        AND updated_at < '{execution_date + timedelta(days=1)}'
    """
    
    df = pg_hook.get_pandas_df(query)
    
    # Write to S3 as Parquet
    s3_hook = S3Hook(aws_conn_id='aws_default')
    
    output_key = f"bronze/orders/date={execution_date.date()}/data.parquet"
    
    df.to_parquet(f"/tmp/data.parquet")
    s3_hook.load_file(
        filename="/tmp/data.parquet",
        key=output_key,
        bucket_name="data-lake",
        replace=True
    )
    
    return output_key

with DAG(
    'ingest_orders',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:
    
    ingest_task = PythonOperator(
        task_id='ingest_from_postgres',
        python_callable=ingest_from_postgres
    )
```

**Streaming Ingestion with Kafka:**
```python
"""
Kafka streaming ingestion
"""

from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json

class StreamIngestion:
    """Manage streaming data ingestion."""
    
    def __init__(self, bootstrap_servers: List[str]):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers
        )
    
    def create_topics(self, topics: List[str]):
        """Create Kafka topics."""
        new_topics = [
            NewTopic(
                name=topic,
                num_partitions=3,
                replication_factor=2
            )
            for topic in topics
        ]
        
        self.admin_client.create_topics(new_topics)
    
    def produce_to_kafka(self, topic: str, data: dict):
        """Produce data to Kafka topic."""
        producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        producer.send(topic, value=data)
        producer.flush()
    
    def consume_from_kafka(self, topic: str, group_id: str):
        """Consume data from Kafka topic."""
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        
        for message in consumer:
            yield message.value

# Usage
stream = StreamIngestion(['localhost:9092'])

# Create topics for different data sources
stream.create_topics([
    'raw.orders',
    'raw.customers',
    'raw.products'
])

# Consume and process
for event in stream.consume_from_kafka('raw.orders', 'processor-group'):
    process_order_event(event)
```

**Change Data Capture (CDC) with Debezium:**
```yaml
# Debezium connector configuration
name: postgres-connector
config:
  connector.class: io.debezium.connector.postgresql.PostgresConnector
  database.hostname: postgres-db.example.com
  database.port: 5432
  database.user: debezium
  database.password: ${DB_PASSWORD}
  database.dbname: production
  database.server.name: prod-db
  
  # Tables to capture
  table.include.list: public.orders,public.customers,public.products
  
  # Plugin
  plugin.name: pgoutput
  publication.name: debezium_publication
  
  # Slot
  slot.name: debezium_slot
  
  # Topics
  topic.prefix: cdc
  topic.creation.default.partitions: 3
  topic.creation.default.replication.factor: 2
  
  # Schema changes
  include.schema.changes: true
  schema.history.internal.kafka.topic: schema-changes.production
  
  # Snapshot
  snapshot.mode: initial
  
  # Output format
  key.converter: org.apache.kafka.connect.json.JsonConverter
  value.converter: org.apache.kafka.connect.json.JsonConverter
```

**Verification:**
- [ ] All sources identified
- [ ] Ingestion methods chosen
- [ ] Connectors configured
- [ ] Error handling in place
- [ ] Monitoring configured

**If This Fails:**
→ Test connectivity to sources
→ Verify credentials
→ Check network policies
→ Review API rate limits

---

### Step 3: Design Processing and Transformation Layer

**What:** Design how data is processed and transformed

**How:**

**Processing Layer Architecture:**
```python
"""
Processing Layer Design
"""

from enum import Enum
from typing import List, Dict

class ProcessingEngine(Enum):
    PANDAS = "pandas"
    SPARK = "spark"
    FLINK = "flink"
    DBT = "dbt"
    SQL = "sql"

class TransformationType(Enum):
    CLEANING = "cleaning"
    ENRICHMENT = "enrichment"
    AGGREGATION = "aggregation"
    JOINING = "joining"
    WINDOWING = "windowing"

@dataclass
class ProcessingStage:
    """Define a processing stage."""
    name: str
    input: str
    output: str
    engine: ProcessingEngine
    transformations: List[TransformationType]
    compute_requirements: Dict[str, any]

class ProcessingLayer:
    """Design processing layer."""
    
    def __init__(self, architecture_pattern: str):
        self.pattern = architecture_pattern
        self.stages: List[ProcessingStage] = []
    
    def add_stage(self, stage: ProcessingStage):
        """Add processing stage."""
        self.stages.append(stage)
    
    def design_batch_processing(self):
        """Design batch processing pipeline."""
        # Bronze → Silver transformation
        self.add_stage(ProcessingStage(
            name="bronze_to_silver",
            input="s3://bucket/bronze/",
            output="s3://bucket/silver/",
            engine=ProcessingEngine.SPARK,
            transformations=[
                TransformationType.CLEANING,
                TransformationType.ENRICHMENT
            ],
            compute_requirements={
                "workers": 4,
                "instance_type": "m5.xlarge",
                "max_runtime_minutes": 60
            }
        ))
        
        # Silver → Gold transformation
        self.add_stage(ProcessingStage(
            name="silver_to_gold",
            input="s3://bucket/silver/",
            output="s3://bucket/gold/",
            engine=ProcessingEngine.DBT,
            transformations=[
                TransformationType.AGGREGATION,
                TransformationType.JOINING
            ],
            compute_requirements={
                "warehouse": "snowflake",
                "warehouse_size": "medium"
            }
        ))
    
    def design_stream_processing(self):
        """Design stream processing pipeline."""
        self.add_stage(ProcessingStage(
            name="stream_enrichment",
            input="kafka://raw-events",
            output="kafka://enriched-events",
            engine=ProcessingEngine.FLINK,
            transformations=[
                TransformationType.ENRICHMENT,
                TransformationType.WINDOWING
            ],
            compute_requirements={
                "task_managers": 2,
                "slots_per_tm": 4,
                "state_backend": "rocksdb"
            }
        ))
```

**Batch Processing with Spark:**
```python
"""
Spark batch processing example
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

class SparkProcessor:
    """Process data with Spark."""
    
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("DataPipeline") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
    
    def process_bronze_to_silver(
        self,
        input_path: str,
        output_path: str,
        processing_date: str
    ):
        """Transform bronze to silver layer."""
        
        # Read bronze data
        df = self.spark.read \
            .format("parquet") \
            .load(f"{input_path}/date={processing_date}")
        
        # Clean and standardize
        silver_df = df \
            .dropDuplicates(["id"]) \
            .filter(F.col("id").isNotNull()) \
            .withColumn("email", F.lower(F.col("email"))) \
            .withColumn("phone", F.regexp_replace(F.col("phone"), "[^0-9]", "")) \
            .withColumn("processed_at", F.current_timestamp())
        
        # Add data quality columns
        silver_df = silver_df \
            .withColumn("is_complete", 
                F.when(
                    (F.col("email").isNotNull()) & 
                    (F.col("phone").isNotNull()),
                    True
                ).otherwise(False)
            )
        
        # Write to silver
        silver_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .partitionBy("processing_date") \
            .save(output_path)
        
        return silver_df.count()
    
    def process_silver_to_gold(
        self,
        silver_path: str,
        gold_path: str
    ):
        """Create gold layer aggregations."""
        
        # Read silver data
        df = self.spark.read \
            .format("delta") \
            .load(silver_path)
        
        # Create aggregations
        daily_metrics = df \
            .groupBy(
                F.col("date"),
                F.col("customer_segment")
            ) \
            .agg(
                F.count("*").alias("total_orders"),
                F.sum("amount").alias("total_revenue"),
                F.avg("amount").alias("avg_order_value"),
                F.countDistinct("customer_id").alias("unique_customers")
            )
        
        # Write to gold
        daily_metrics.write \
            .format("delta") \
            .mode("overwrite") \
            .save(gold_path)
```

**Stream Processing with Flink:**
```python
"""
Flink stream processing example
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table.window import Tumble

class FlinkProcessor:
    """Process streaming data with Flink."""
    
    def __init__(self):
        # Create execution environment
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.set_parallelism(4)
        
        # Create table environment
        settings = EnvironmentSettings.new_instance() \
            .in_streaming_mode() \
            .build()
        
        self.table_env = StreamTableEnvironment.create(
            self.env,
            environment_settings=settings
        )
    
    def process_event_stream(self):
        """Process event stream with windowing."""
        
        # Define source table (Kafka)
        self.table_env.execute_sql("""
            CREATE TABLE events (
                event_id STRING,
                user_id STRING,
                event_type STRING,
                amount DOUBLE,
                event_time TIMESTAMP(3),
                WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
            ) WITH (
                'connector' = 'kafka',
                'topic' = 'raw-events',
                'properties.bootstrap.servers' = 'localhost:9092',
                'properties.group.id' = 'flink-processor',
                'format' = 'json'
            )
        """)
        
        # Define sink table (Kafka)
        self.table_env.execute_sql("""
            CREATE TABLE aggregated_events (
                window_start TIMESTAMP(3),
                window_end TIMESTAMP(3),
                user_id STRING,
                event_count BIGINT,
                total_amount DOUBLE
            ) WITH (
                'connector' = 'kafka',
                'topic' = 'aggregated-events',
                'properties.bootstrap.servers' = 'localhost:9092',
                'format' = 'json'
            )
        """)
        
        # Process with windowing
        result = self.table_env.sql_query("""
            SELECT
                TUMBLE_START(event_time, INTERVAL '1' MINUTE) as window_start,
                TUMBLE_END(event_time, INTERVAL '1' MINUTE) as window_end,
                user_id,
                COUNT(*) as event_count,
                SUM(amount) as total_amount
            FROM events
            GROUP BY
                TUMBLE(event_time, INTERVAL '1' MINUTE),
                user_id
        """)
        
        # Write to sink
        result.execute_insert("aggregated_events")
        
        # Execute
        self.env.execute("Event Stream Processing")
```

**SQL Transformations with dbt:**
```sql
-- models/silver/customers.sql
{{
  config(
    materialized='incremental',
    unique_key='customer_id',
    on_schema_change='sync_all_columns'
  )
}}

WITH source AS (
    SELECT *
    FROM {{ source('bronze', 'raw_customers') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

cleaned AS (
    SELECT
        customer_id,
        LOWER(TRIM(email)) AS email,
        TRIM(first_name) AS first_name,
        TRIM(last_name) AS last_name,
        REGEXP_REPLACE(phone, '[^0-9]', '') AS phone,
        created_at,
        updated_at,
        CURRENT_TIMESTAMP() AS processed_at
    FROM source
    WHERE customer_id IS NOT NULL
        AND email IS NOT NULL
        AND email LIKE '%@%'
)

SELECT * FROM cleaned

-- models/gold/customer_metrics.sql
{{
  config(
    materialized='table',
    tags=['gold', 'metrics']
  )
}}

SELECT
    c.customer_id,
    c.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.amount) AS lifetime_value,
    AVG(o.amount) AS avg_order_value,
    MIN(o.order_date) AS first_order_date,
    MAX(o.order_date) AS last_order_date,
    DATEDIFF(CURRENT_DATE, MAX(o.order_date)) AS days_since_last_order,
    CASE
        WHEN SUM(o.amount) > 10000 THEN 'VIP'
        WHEN SUM(o.amount) > 1000 THEN 'Gold'
        WHEN SUM(o.amount) > 100 THEN 'Silver'
        ELSE 'Bronze'
    END AS customer_segment
FROM {{ ref('customers') }} c
LEFT JOIN {{ ref('orders') }} o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.email
```

**Verification:**
- [ ] Processing stages defined
- [ ] Engines selected appropriately
- [ ] Performance requirements met
- [ ] Error handling in place
- [ ] Testing completed

**If This Fails:**
→ Profile processing performance
→ Optimize Spark/Flink configurations
→ Review data volumes
→ Consider partitioning strategies

---

### Step 4: Design Storage Layer

**What:** Design how and where data is stored

**How:**

**Storage Architecture:**
```python
"""
Storage Layer Design
"""

from enum import Enum
from typing import List

class StorageType(Enum):
    DATA_LAKE = "data_lake"
    DATA_WAREHOUSE = "data_warehouse"
    LAKE_HOUSE = "lake_house"
    OLAP = "olap"
    CACHE = "cache"

class StorageFormat(Enum):
    PARQUET = "parquet"
    DELTA = "delta"
    ICEBERG = "iceberg"
    ORC = "orc"
    AVRO = "avro"

@dataclass
class StorageLayer:
    """Define storage layer configuration."""
    name: str
    type: StorageType
    format: StorageFormat
    location: str
    partitioning: List[str]
    compression: str
    retention_days: int
    access_pattern: str  # "write-once-read-many", "frequent-updates"

def design_medallion_storage():
    """Design medallion architecture storage."""
    
    bronze = StorageLayer(
        name="bronze",
        type=StorageType.DATA_LAKE,
        format=StorageFormat.PARQUET,
        location="s3://data-lake/bronze/",
        partitioning=["source", "date"],
        compression="snappy",
        retention_days=365,
        access_pattern="write-once-read-many"
    )
    
    silver = StorageLayer(
        name="silver",
        type=StorageType.LAKE_HOUSE,
        format=StorageFormat.DELTA,
        location="s3://data-lake/silver/",
        partitioning=["entity", "year", "month"],
        compression="zstd",
        retention_days=180,
        access_pattern="frequent-updates"
    )
    
    gold = StorageLayer(
        name="gold",
        type=StorageType.DATA_WAREHOUSE,
        format=StorageFormat.DELTA,
        location="snowflake://database/schema",
        partitioning=["business_date"],
        compression="zstd",
        retention_days=90,
        access_pattern="read-optimized"
    )
    
    return {"bronze": bronze, "silver": silver, "gold": gold}
```

**Delta Lake Table Creation:**
```python
"""
Create Delta Lake tables
"""

from delta.tables import DeltaTable
from pyspark.sql import SparkSession

def create_delta_tables(spark: SparkSession):
    """Create optimized Delta Lake tables."""
    
    # Create silver table with ZORDER
    spark.sql("""
        CREATE TABLE IF NOT EXISTS silver.customers (
            customer_id STRING,
            email STRING,
            first_name STRING,
            last_name STRING,
            phone STRING,
            segment STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            processed_at TIMESTAMP
        )
        USING DELTA
        PARTITIONED BY (segment)
        LOCATION 's3://data-lake/silver/customers'
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true',
            'delta.logRetentionDuration' = '30 days',
            'delta.deletedFileRetentionDuration' = '7 days'
        )
    """)
    
    # Optimize table with ZORDER
    spark.sql("""
        OPTIMIZE silver.customers
        ZORDER BY (customer_id, email)
    """)
    
    # Vacuum old files
    spark.sql("""
        VACUUM silver.customers RETAIN 168 HOURS
    """)
```

**Partitioning Strategy:**
```python
"""
Implement effective partitioning
"""

def design_partitioning_strategy(
    data_volume_gb: float,
    query_patterns: List[str],
    retention_days: int
) -> Dict[str, any]:
    """Recommend partitioning strategy."""
    
    strategy = {}
    
    # Time-based partitioning for large volumes
    if data_volume_gb > 1000:
        if retention_days > 365:
            strategy["partition_columns"] = ["year", "month", "day"]
        else:
            strategy["partition_columns"] = ["date"]
    
    # Business-key partitioning for frequent lookups
    if "lookup_by_customer" in query_patterns:
        strategy["partition_columns"].append("customer_segment")
    
    # Bucketing for even distribution
    if data_volume_gb > 5000:
        strategy["bucketing"] = {
            "columns": ["customer_id"],
            "num_buckets": 100
        }
    
    return strategy

# Example implementation
spark.sql("""
    CREATE TABLE orders (
        order_id STRING,
        customer_id STRING,
        amount DOUBLE,
        order_date DATE,
        status STRING
    )
    USING DELTA
    PARTITIONED BY (order_date)
    CLUSTERED BY (customer_id) INTO 50 BUCKETS
""")
```

**Verification:**
- [ ] Storage solution selected
- [ ] Partitioning optimized
- [ ] Retention policies defined
- [ ] Compression configured
- [ ] Access patterns considered

**If This Fails:**
→ Benchmark query performance
→ Review partition sizes (aim for 128MB-1GB)
→ Test with production-like queries
→ Monitor storage costs

---

(Continuing in next message due to length...)

**Verification Checklist**

After completing this workflow:

- [ ] Architecture pattern selected
- [ ] Ingestion layer designed
- [ ] Processing layer architected
- [ ] Storage layer optimized
- [ ] Orchestration configured
- [ ] Monitoring implemented
- [ ] Documentation complete
- [ ] Team trained

---

## Common Issues & Solutions

### Issue: Pipeline Bottlenecks

**Symptoms:**
- Slow processing
- Queues backing up
- Timeouts

**Solution:**
- Add parallel processing
- Optimize partitioning
- Scale compute resources
- Use caching layers

---

## Best Practices

### DO:
✅ Design for scalability from the start
✅ Implement idempotency
✅ Use appropriate storage formats
✅ Partition data effectively
✅ Monitor pipeline health
✅ Document architecture decisions
✅ Version control all code
✅ Implement data quality checks
✅ Plan for failure scenarios
✅ Use infrastructure as code

### DON'T:
❌ Over-engineer early
❌ Ignore data lineage
❌ Skip monitoring
❌ Forget about costs
❌ Create tight coupling
❌ Ignore data governance
❌ Skip testing
❌ Forget documentation
❌ Ignore security
❌ Create monolithic pipelines

---

## Related Workflows

**Prerequisites:**
- [database-migration-workflow.md](./database-migration-workflow.md) - Database setup

**Next Steps:**
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL implementation
- [pipeline_orchestration_airflow.md](./pipeline_orchestration_airflow.md) - Orchestration

**Related:**
- [data_transformation_dbt.md](./data_transformation_dbt.md) - SQL transformations
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks

---

## Tags
`data-engineering` `pipelines` `architecture` `etl` `orchestration` `spark` `kafka` `airflow` `medallion` `lambda`
