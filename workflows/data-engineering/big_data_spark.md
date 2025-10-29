# Big Data Processing with Spark

**ID:** dat-001  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-150 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Process large-scale datasets efficiently using Apache Spark for distributed data processing, ETL, and analytics

**Why:** Spark enables processing terabytes to petabytes of data in distributed clusters with fault tolerance, in-memory computing, and unified APIs

**When to use:**
- Processing TB+ datasets
- Large-scale ETL pipelines
- Machine learning at scale
- Real-time stream processing
- Complex data transformations
- Data lake processing

---

## Prerequisites

**Required:**
- [ ] Understanding of distributed computing concepts
- [ ] Python or Scala knowledge
- [ ] SQL proficiency
- [ ] Cluster access (local, cloud, or on-premise)
- [ ] Basic understanding of RDDs and DataFrames

**Check before starting:**
```bash
# Check Java (required for Spark)
java -version  # Should be 8 or 11

# Check Python
python --version  # Should be 3.8+

# Check Spark installation
spark-submit --version

# Check PySpark
python -c "import pyspark; print(pyspark.__version__)"
```

---

## Implementation Steps

### Step 1: Set Up Spark Environment

**What:** Install and configure Apache Spark for local or cluster execution

**How:**

**Local Installation:**
```bash
# Install PySpark
pip install pyspark==3.5.0

# Install additional dependencies
pip install pandas numpy pyarrow

# Verify installation
python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.appName('test').getOrCreate(); print(spark.version)"
```

**Initialize Spark Session:**
```python
# spark_setup.py
"""
Initialize Spark session with optimal configuration
"""

from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

def create_spark_session(
    app_name: str = "DataProcessing",
    mode: str = "local"  # local, yarn, kubernetes
):
    """Create optimized Spark session."""
    
    # Build configuration
    conf = SparkConf()
    
    if mode == "local":
        # Local development configuration
        conf.setAll([
            ("spark.master", "local[*]"),
            ("spark.driver.memory", "4g"),
            ("spark.executor.memory", "4g"),
            ("spark.sql.shuffle.partitions", "8"),
        ])
    
    elif mode == "yarn":
        # YARN cluster configuration
        conf.setAll([
            ("spark.master", "yarn"),
            ("spark.submit.deployMode", "cluster"),
            ("spark.driver.memory", "8g"),
            ("spark.driver.cores", "4"),
            ("spark.executor.memory", "16g"),
            ("spark.executor.cores", "4"),
            ("spark.executor.instances", "10"),
            ("spark.sql.shuffle.partitions", "200"),
            ("spark.dynamicAllocation.enabled", "true"),
            ("spark.dynamicAllocation.minExecutors", "2"),
            ("spark.dynamicAllocation.maxExecutors", "50"),
        ])
    
    # Performance optimizations
    conf.setAll([
        # Adaptive Query Execution
        ("spark.sql.adaptive.enabled", "true"),
        ("spark.sql.adaptive.coalescePartitions.enabled", "true"),
        
        # Compression
        ("spark.sql.parquet.compression.codec", "snappy"),
        
        # Memory management
        ("spark.memory.fraction", "0.8"),
        ("spark.memory.storageFraction", "0.3"),
        
        # Serialization
        ("spark.serializer", "org.apache.spark.serializer.KryoSerializer"),
        
        # Broadcast
        ("spark.sql.autoBroadcastJoinThreshold", "10485760"),  # 10MB
    ])
    
    # Create session
    spark = SparkSession.builder \
        .appName(app_name) \
        .config(conf=conf) \
        .enableHiveSupport() \
        .getOrCreate()
    
    # Set log level
    spark.sparkContext.setLogLevel("WARN")
    
    print(f"✅ Spark {spark.version} session created")
    print(f"   Master: {spark.sparkContext.master}")
    print(f"   App ID: {spark.sparkContext.applicationId}")
    
    return spark

# Usage
spark = create_spark_session("MyETL", mode="local")
```

**Docker Spark Cluster (Development):**
```yaml
# docker-compose.yml
version: '3.8'

services:
  spark-master:
    image: bitnami/spark:3.5.0
    container_name: spark-master
    environment:
      - SPARK_MODE=master
      - SPARK_MASTER_HOST=spark-master
    ports:
      - "8080:8080"
      - "7077:7077"
    volumes:
      - ./data:/data
      - ./scripts:/scripts

  spark-worker-1:
    image: bitnami/spark:3.5.0
    container_name: spark-worker-1
    depends_on:
      - spark-master
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=4G
      - SPARK_WORKER_CORES=2
    volumes:
      - ./data:/data
      - ./scripts:/scripts

  spark-worker-2:
    image: bitnami/spark:3.5.0
    container_name: spark-worker-2
    depends_on:
      - spark-master
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=4G
      - SPARK_WORKER_CORES=2
    volumes:
      - ./data:/data
      - ./scripts:/scripts
```

**Verification:**
- [ ] Spark session created
- [ ] Configuration applied
- [ ] Cluster accessible (if using)
- [ ] UI accessible (http://localhost:4040)
- [ ] Sample job runs

**If This Fails:**
→ Check Java installation
→ Verify memory settings
→ Review Spark logs
→ Check network connectivity
→ Ensure sufficient resources

---

### Step 2: Read and Write Data with Spark

**What:** Load data from various sources and write to different formats

**How:**

**Reading Data:**
```python
# data_io.py
"""
Read data from various sources with Spark
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import *

spark = create_spark_session()

# Read CSV
df_csv = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("delimiter", ",") \
    .csv("data/customers.csv")

# Read with explicit schema (better performance)
schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("signup_date", DateType(), True),
    StructField("total_spent", DoubleType(), True),
])

df_csv_schema = spark.read \
    .schema(schema) \
    .csv("data/customers.csv")

# Read Parquet (columnar, efficient)
df_parquet = spark.read.parquet("data/orders.parquet")

# Read JSON
df_json = spark.read.json("data/events.json")

# Read from multiple files with pattern
df_multi = spark.read.parquet("data/sales/year=2024/month=*/")

# Read from database
df_db = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/mydb") \
    .option("dbtable", "customers") \
    .option("user", "user") \
    .option("password", "password") \
    .option("driver", "org.postgresql.Driver") \
    .load()

# Read with partitions for parallelism
df_db_parallel = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/mydb") \
    .option("dbtable", "orders") \
    .option("user", "user") \
    .option("password", "password") \
    .option("numPartitions", "10") \
    .option("partitionColumn", "order_id") \
    .option("lowerBound", "1") \
    .option("upperBound", "1000000") \
    .load()

# Read Delta Lake (supports ACID transactions)
df_delta = spark.read.format("delta").load("data/delta/customers")

# Read from S3
df_s3 = spark.read.parquet("s3a://my-bucket/data/")
```

**Writing Data:**
```python
# Write Parquet (recommended for analytics)
df.write \
    .mode("overwrite") \
    .partitionBy("year", "month") \
    .parquet("output/customers.parquet")

# Write with compression
df.write \
    .mode("overwrite") \
    .option("compression", "snappy") \
    .parquet("output/compressed.parquet")

# Write CSV
df.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv("output/customers.csv")

# Write to database
df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://localhost:5432/mydb") \
    .option("dbtable", "customers_processed") \
    .option("user", "user") \
    .option("password", "password") \
    .mode("overwrite") \
    .save()

# Write to Delta Lake
df.write \
    .format("delta") \
    .mode("overwrite") \
    .save("output/delta/customers")

# Append mode
df.write \
    .mode("append") \
    .parquet("output/incremental.parquet")

# Dynamic partitioning
df.write \
    .mode("overwrite") \
    .partitionBy("country", "signup_year") \
    .parquet("output/partitioned/")
```

**Verification:**
- [ ] Data reads successfully
- [ ] Schema correct
- [ ] Data writes successfully
- [ ] Partitioning works
- [ ] Compression applied

**If This Fails:**
→ Check file paths
→ Verify schema compatibility
→ Review permissions
→ Check disk space
→ Validate data format

---

### Step 3: Transform Data with DataFrames

**What:** Perform data transformations using Spark DataFrames

**How:**

**Basic Transformations:**
```python
# transformations.py
"""
Spark DataFrame transformations
"""

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Select columns
df_select = df.select("customer_id", "name", "email")

# Filter rows
df_filter = df.filter(F.col("total_spent") > 1000)
# or
df_filter = df.where("total_spent > 1000")

# Add new columns
df_new_col = df.withColumn(
    "signup_year",
    F.year(F.col("signup_date"))
)

df_new_col = df.withColumn(
    "high_value",
    F.when(F.col("total_spent") > 5000, "Yes").otherwise("No")
)

# Rename columns
df_renamed = df.withColumnRenamed("total_spent", "lifetime_value")

# Drop columns
df_dropped = df.drop("temp_column", "another_temp")

# Handle nulls
df_filled = df.fillna({
    "email": "unknown@example.com",
    "total_spent": 0
})

df_dropped_nulls = df.dropna(subset=["email", "customer_id"])

# Remove duplicates
df_deduped = df.dropDuplicates(["customer_id"])

# Sort
df_sorted = df.orderBy(F.col("total_spent").desc())

# Limit
df_top10 = df.orderBy(F.col("total_spent").desc()).limit(10)
```

**Aggregations:**
```python
# Group by and aggregate
df_agg = df.groupBy("country") \
    .agg(
        F.count("*").alias("customer_count"),
        F.sum("total_spent").alias("total_revenue"),
        F.avg("total_spent").alias("avg_spent"),
        F.min("signup_date").alias("first_signup"),
        F.max("signup_date").alias("last_signup")
    )

# Multiple aggregations
df_multi_agg = df.groupBy("country", "signup_year") \
    .agg(
        F.count("*").alias("count"),
        F.sum("total_spent").alias("revenue"),
        F.avg("total_spent").alias("avg_revenue"),
        F.stddev("total_spent").alias("stddev_revenue"),
        F.countDistinct("customer_id").alias("unique_customers")
    )

# Pivot (wide format)
df_pivot = df.groupBy("country") \
    .pivot("signup_year") \
    .sum("total_spent")
```

**Joins:**
```python
# Inner join
df_joined = customers.join(
    orders,
    customers.customer_id == orders.customer_id,
    "inner"
)

# Left join
df_left = customers.join(
    orders,
    "customer_id",  # When column names match
    "left"
)

# Broadcast join (for small tables)
from pyspark.sql.functions import broadcast

df_broadcast = large_df.join(
    broadcast(small_df),
    "key",
    "inner"
)

# Multiple conditions
df_complex = df1.join(
    df2,
    (df1.customer_id == df2.customer_id) & 
    (df1.order_date == df2.ship_date),
    "inner"
)
```

**Window Functions:**
```python
# Define window
window = Window.partitionBy("country").orderBy(F.col("total_spent").desc())

# Row number
df_ranked = df.withColumn(
    "rank",
    F.row_number().over(window)
)

# Running total
df_running = df.withColumn(
    "cumulative_spent",
    F.sum("total_spent").over(
        Window.partitionBy("customer_id")
              .orderBy("order_date")
              .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )
)

# Lag/Lead
df_lag = df.withColumn(
    "previous_order",
    F.lag("order_date", 1).over(
        Window.partitionBy("customer_id").orderBy("order_date")
    )
)
```

**Complex Transformations:**
```python
# Explode arrays
df_exploded = df.withColumn("tag", F.explode(F.col("tags")))

# Collect to array
df_collected = df.groupBy("customer_id") \
    .agg(F.collect_list("product_id").alias("products"))

# String operations
df_string = df.withColumn(
    "email_domain",
    F.split(F.col("email"), "@").getItem(1)
)

df_string = df.withColumn(
    "name_upper",
    F.upper(F.col("name"))
)

# Date operations
df_date = df.withColumn(
    "days_since_signup",
    F.datediff(F.current_date(), F.col("signup_date"))
)

df_date = df.withColumn(
    "signup_month",
    F.date_format(F.col("signup_date"), "yyyy-MM")
)

# Conditional logic
df_segment = df.withColumn(
    "customer_segment",
    F.when(F.col("total_spent") > 10000, "VIP")
     .when(F.col("total_spent") > 1000, "Gold")
     .when(F.col("total_spent") > 100, "Silver")
     .otherwise("Bronze")
)

# UDF (User Defined Function)
from pyspark.sql.types import StringType

def categorize_amount(amount):
    if amount > 1000:
        return "high"
    elif amount > 100:
        return "medium"
    else:
        return "low"

categorize_udf = F.udf(categorize_amount, StringType())

df_udf = df.withColumn(
    "amount_category",
    categorize_udf(F.col("total_spent"))
)
```

**Verification:**
- [ ] Transformations correct
- [ ] No data loss
- [ ] Performance acceptable
- [ ] Results validated
- [ ] Schema as expected

**If This Fails:**
→ Check column names
→ Verify data types
→ Review transformation logic
→ Check for null handling
→ Profile performance

---

### Step 4: Optimize Spark Performance

**What:** Apply performance optimization techniques

**How:**

**Partitioning:**
```python
# Check current partitions
print(f"Current partitions: {df.rdd.getNumPartitions()}")

# Repartition (full shuffle)
df_repartitioned = df.repartition(200)

# Repartition by column (for joins/groupBy)
df_repartitioned = df.repartition(100, "customer_id")

# Coalesce (reduce partitions without shuffle)
df_coalesced = df.coalesce(10)

# Optimal partition size: 128MB - 1GB per partition
total_size_gb = 100
optimal_partitions = int((total_size_gb * 1024) / 128)
df_optimized = df.repartition(optimal_partitions)
```

**Caching:**
```python
# Cache in memory (lazy)
df_cached = df.cache()

# Persist with storage level
from pyspark import StorageLevel

df_persisted = df.persist(StorageLevel.MEMORY_AND_DISK)

# Use cached DataFrame
result = df_cached.filter(F.col("amount") > 100).count()

# Unpersist when done
df_cached.unpersist()
```

**Broadcast Joins:**
```python
# Broadcast small DataFrame to all executors
from pyspark.sql.functions import broadcast

# Manual broadcast
df_result = large_df.join(
    broadcast(small_df),
    "key"
)

# Configure auto-broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10485760)  # 10MB
```

**Avoid Wide Transformations:**
```python
# ❌ BAD: Multiple shuffles
df_bad = df \
    .groupBy("col1").agg(F.sum("amount")) \
    .join(other_df, "col1") \
    .groupBy("col2").agg(F.avg("amount"))

# ✅ GOOD: Minimize shuffles
df_good = df \
    .join(other_df, "col1") \
    .groupBy("col1", "col2") \
    .agg(
        F.sum("amount").alias("total"),
        F.avg("amount").alias("average")
    )
```

**Adaptive Query Execution:**
```python
# Enable AQE (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

**Performance Monitoring:**
```python
# Enable query explanation
df.explain(mode="formatted")

# Check execution plan
df.explain(mode="cost")

# Monitor with UI
# Access Spark UI at http://localhost:4040
```

**Verification:**
- [ ] Partition count optimal
- [ ] Caching used appropriately
- [ ] Broadcast joins working
- [ ] Query plans reviewed
- [ ] Performance acceptable

**If This Fails:**
→ Review Spark UI
→ Check for data skew
→ Profile memory usage
→ Optimize transformations
→ Adjust cluster resources

---

### Step 5: Implement Complete ETL Pipeline

**What:** Build production-ready Spark ETL pipeline

**How:**

**Complete ETL Example:**
```python
# etl_pipeline.py
"""
Production Spark ETL pipeline
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkETL:
    """Spark ETL pipeline."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
    
    def extract(self, source_path: str, file_format: str = "parquet") -> DataFrame:
        """Extract data from source."""
        logger.info(f"Extracting data from {source_path}")
        
        if file_format == "parquet":
            df = self.spark.read.parquet(source_path)
        elif file_format == "csv":
            df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(source_path)
        elif file_format == "json":
            df = self.spark.read.json(source_path)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
        
        logger.info(f"Extracted {df.count()} rows")
        return df
    
    def transform(self, df: DataFrame) -> DataFrame:
        """Transform data."""
        logger.info("Starting transformations")
        
        # Clean data
        df_clean = df \
            .dropna(subset=["customer_id", "order_id"]) \
            .dropDuplicates(["order_id"]) \
            .filter(F.col("amount") > 0)
        
        # Add derived columns
        df_transformed = df_clean \
            .withColumn("order_year", F.year(F.col("order_date"))) \
            .withColumn("order_month", F.month(F.col("order_date"))) \
            .withColumn(
                "customer_segment",
                F.when(F.col("amount") > 1000, "High")
                 .when(F.col("amount") > 100, "Medium")
                 .otherwise("Low")
            ) \
            .withColumn("processed_at", F.current_timestamp())
        
        # Aggregations
        df_agg = df_transformed.groupBy("customer_id", "order_year") \
            .agg(
                F.count("*").alias("order_count"),
                F.sum("amount").alias("total_spent"),
                F.avg("amount").alias("avg_order_value"),
                F.min("order_date").alias("first_order"),
                F.max("order_date").alias("last_order")
            )
        
        logger.info(f"Transformed to {df_agg.count()} rows")
        return df_agg
    
    def validate(self, df: DataFrame) -> bool:
        """Validate transformed data."""
        logger.info("Validating data quality")
        
        # Check for nulls in key columns
        null_counts = df.select([
            F.sum(F.col(c).isNull().cast("int")).alias(c)
            for c in df.columns
        ]).collect()[0].asDict()
        
        if any(count > 0 for count in null_counts.values()):
            logger.error(f"Null values found: {null_counts}")
            return False
        
        # Check row count
        if df.count() == 0:
            logger.error("No data after transformation")
            return False
        
        # Check for negative values
        negative_count = df.filter(F.col("total_spent") < 0).count()
        if negative_count > 0:
            logger.error(f"Found {negative_count} negative values")
            return False
        
        logger.info("✅ Validation passed")
        return True
    
    def load(self, df: DataFrame, target_path: str, mode: str = "overwrite"):
        """Load data to target."""
        logger.info(f"Loading data to {target_path}")
        
        df.write \
            .mode(mode) \
            .partitionBy("order_year", "order_month") \
            .parquet(target_path)
        
        logger.info("✅ Data loaded successfully")
    
    def run(self, source_path: str, target_path: str):
        """Run complete ETL pipeline."""
        try:
            # Extract
            df = self.extract(source_path)
            
            # Transform
            df_transformed = self.transform(df)
            
            # Validate
            if not self.validate(df_transformed):
                raise ValueError("Data validation failed")
            
            # Load
            self.load(df_transformed, target_path)
            
            logger.info("✅ ETL pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"❌ ETL pipeline failed: {e}")
            raise

# Usage
spark = create_spark_session("ProductionETL", mode="yarn")
etl = SparkETL(spark)
etl.run("s3://input/orders/", "s3://output/customer_metrics/")
spark.stop()
```

**Verification:**
- [ ] Pipeline runs end-to-end
- [ ] Data quality validated
- [ ] Error handling robust
- [ ] Monitoring in place
- [ ] Performance acceptable

**If This Fails:**
→ Check each stage independently
→ Review logs
→ Validate input data
→ Check permissions
→ Monitor resources

---

## Verification Checklist

After completing this workflow:

- [ ] Spark environment set up
- [ ] Data I/O working
- [ ] Transformations correct
- [ ] Performance optimized
- [ ] ETL pipeline complete
- [ ] Tests passing
- [ ] Monitoring configured
- [ ] Documentation complete

---

## Common Issues & Solutions

### Issue: Out of Memory Errors

**Symptoms:**
- Executor OOM errors
- Driver memory exhausted
- Job fails during shuffle

**Solution:**
```python
# Increase memory
spark.conf.set("spark.executor.memory", "16g")
spark.conf.set("spark.driver.memory", "8g")

# Adjust memory fractions
spark.conf.set("spark.memory.fraction", "0.8")

# Reduce data loaded
df_sample = df.sample(0.1)  # 10% sample

# Increase parallelism
df = df.repartition(400)
```

---

## Best Practices

### DO:
✅ Use DataFrames over RDDs
✅ Partition data appropriately
✅ Cache wisely
✅ Use broadcast for small tables
✅ Enable adaptive query execution
✅ Monitor Spark UI
✅ Write to columnar formats (Parquet)
✅ Use appropriate file sizes
✅ Implement data validation
✅ Handle schema evolution
✅ Use compression
✅ Profile before optimizing

### DON'T:
❌ Collect large datasets to driver
❌ Use too many shuffles
❌ Ignore data skew
❌ Over-partition small data
❌ Cache everything
❌ Use UDFs unnecessarily
❌ Skip error handling
❌ Forget to unpersist
❌ Create small files
❌ Ignore query plans
❌ Hard-code configurations
❌ Skip testing at scale

---

## Related Workflows

**Prerequisites:**
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture patterns

**Next Steps:**
- [stream_processing_kafka.md](./stream_processing_kafka.md) - Streaming
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks

**Related:**
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL patterns
- [pipeline_orchestration_airflow.md](./pipeline_orchestration_airflow.md) - Orchestration

---

## Tags
`data-engineering` `spark` `big-data` `distributed-computing` `pyspark` `etl` `performance` `scala` `python`
