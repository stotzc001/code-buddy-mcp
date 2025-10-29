# Data Lake Architecture

**ID:** dat-003  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-150 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design and implement scalable, well-organized data lake architectures using cloud storage with proper zone organization, metadata management, and governance

**Why:** Data lakes enable storing massive amounts of structured, semi-structured, and unstructured data cost-effectively while supporting diverse analytics, ML, and processing workloads

**When to use:**
- Building enterprise data platforms
- Centralizing multi-source data storage
- Supporting diverse analytics workloads
- Enabling machine learning at scale
- Storing raw and processed data
- Implementing lakehouse architecture
- Managing structured and unstructured data
- Supporting real-time and batch processing

---

## Prerequisites

**Required:**
- [ ] Cloud platform account (AWS, Azure, or GCP)
- [ ] Understanding of data zones (bronze/silver/gold)
- [ ] Basic cloud storage knowledge (S3, ADLS, GCS)
- [ ] Data partitioning concepts
- [ ] IAM/access control understanding
- [ ] Infrastructure as Code knowledge (Terraform)

**Check before starting:**
```bash
# Check AWS CLI
aws --version
aws s3 ls  # Test access

# Or Azure CLI
az --version
az storage account list

# Or Google Cloud SDK
gcloud --version
gsutil ls

# Check Terraform
terraform --version
```

---

## Implementation Steps

### Step 1: Design Data Lake Zone Architecture

**What:** Define the multi-zone architecture (bronze/silver/gold or raw/curated/refined)

**How:**

**Zone Architecture Definition:**
```markdown
## Data Lake Zones

### Bronze Zone (Raw)
**Purpose**: Land raw data exactly as received from source systems
**Characteristics**:
- Immutable raw data
- Original file formats
- Minimal processing
- Full history retained
- Schema on read
- Partition by ingestion date

**Structure**:
```
bronze/
├── source_system_1/
│   ├── table_1/
│   │   └── year=2024/
│   │       └── month=10/
│   │           └── day=26/
│   │               └── data.parquet
│   └── table_2/
├── source_system_2/
└── metadata/
    └── ingestion_logs/
```

### Silver Zone (Curated)
**Purpose**: Cleaned, validated, and conformed data
**Characteristics**:
- Data quality rules applied
- Schema enforced
- Deduplication
- Standard formats (Parquet, ORC)
- Partition by business keys
- SCD handling

**Structure**:
```
silver/
├── domain_1/
│   ├── customers/
│   │   └── year=2024/
│   │       └── month=10/
│   └── orders/
├── domain_2/
└── metadata/
```

### Gold Zone (Refined/Analytics)
**Purpose**: Business-level aggregates and analytics-ready datasets
**Characteristics**:
- Aggregated data
- Business logic applied
- Optimized for consumption
- Denormalized for performance
- Dimensional models
- Metrics and KPIs

**Structure**:
```
gold/
├── business_unit_1/
│   ├── customer_360/
│   ├── sales_metrics/
│   └── marketing_kpis/
├── business_unit_2/
└── metadata/
```
```

**Zoning Decision Framework:**
```python
# zone_design.py
"""
Data lake zone design framework
"""

from dataclasses import dataclass
from enum import Enum
from typing import List

class Zone(Enum):
    """Data lake zones."""
    BRONZE = "bronze"  # Raw
    SILVER = "silver"  # Curated
    GOLD = "gold"      # Analytics-ready

class DataFormat(Enum):
    """Supported data formats."""
    PARQUET = "parquet"
    ORC = "orc"
    AVRO = "avro"
    JSON = "json"
    CSV = "csv"
    DELTA = "delta"

@dataclass
class ZoneSpecification:
    """Specification for a data lake zone."""
    zone: Zone
    purpose: str
    retention_days: int
    format: DataFormat
    compression: str
    partitioning_strategy: str
    quality_checks: List[str]
    access_pattern: str

# Define zone specifications
BRONZE_SPEC = ZoneSpecification(
    zone=Zone.BRONZE,
    purpose="Raw data ingestion",
    retention_days=365 * 2,  # 2 years
    format=DataFormat.PARQUET,
    compression="snappy",
    partitioning_strategy="year/month/day/hour",
    quality_checks=["schema_validation", "null_check"],
    access_pattern="write_once_read_many"
)

SILVER_SPEC = ZoneSpecification(
    zone=Zone.SILVER,
    purpose="Cleaned and conformed data",
    retention_days=365 * 5,  # 5 years
    format=DataFormat.PARQUET,
    compression="snappy",
    partitioning_strategy="business_key/year/month",
    quality_checks=["completeness", "uniqueness", "validity", "consistency"],
    access_pattern="read_optimized"
)

GOLD_SPEC = ZoneSpecification(
    zone=Zone.GOLD,
    purpose="Analytics and reporting",
    retention_days=365 * 7,  # 7 years
    format=DataFormat.DELTA,  # ACID transactions
    compression="zstd",
    partitioning_strategy="business_dimension",
    quality_checks=["accuracy", "timeliness"],
    access_pattern="high_concurrency_read"
)
```

**Verification:**
- [ ] Zones defined clearly
- [ ] Purpose documented
- [ ] Retention policies set
- [ ] Formats chosen
- [ ] Partitioning strategy defined

**If This Fails:**
→ Review business requirements
→ Analyze access patterns
→ Consider data volumes
→ Evaluate tools and queries
→ Consult stakeholders

---

### Step 2: Implement Infrastructure with Terraform

**What:** Provision cloud storage infrastructure using Infrastructure as Code

**How:**

**AWS S3 Data Lake (Terraform):**
```hcl
# main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "analytics-data-lake"
}

variable "environment" {
  default = "production"
}

# S3 Buckets for Data Lake Zones
resource "aws_s3_bucket" "bronze" {
  bucket = "${var.project_name}-bronze-${var.environment}"
  
  tags = {
    Name        = "Bronze Zone"
    Environment = var.environment
    Zone        = "bronze"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "silver" {
  bucket = "${var.project_name}-silver-${var.environment}"
  
  tags = {
    Name        = "Silver Zone"
    Environment = var.environment
    Zone        = "silver"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "gold" {
  bucket = "${var.project_name}-gold-${var.environment}"
  
  tags = {
    Name        = "Gold Zone"
    Environment = var.environment
    Zone        = "gold"
    ManagedBy   = "terraform"
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "silver" {
  bucket = aws_s3_bucket.silver.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "gold" {
  bucket = aws_s3_bucket.gold.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "silver" {
  bucket = aws_s3_bucket.silver.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "gold" {
  bucket = aws_s3_bucket.gold.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle policies
resource "aws_s3_bucket_lifecycle_configuration" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  
  rule {
    id     = "transition-to-glacier"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
    
    expiration {
      days = 730  # 2 years
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "silver" {
  bucket = aws_s3_bucket.silver.id
  
  rule {
    id     = "transition-to-ia"
    status = "Enabled"
    
    transition {
      days          = 180
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 365
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 1825  # 5 years
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "silver" {
  bucket = aws_s3_bucket.silver.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "gold" {
  bucket = aws_s3_bucket.gold.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Policies
resource "aws_iam_role" "data_engineer" {
  name = "${var.project_name}-data-engineer"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "data_lake_access" {
  name = "${var.project_name}-data-lake-access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.bronze.arn}/*",
          "${aws_s3_bucket.silver.arn}/*",
          "${aws_s3_bucket.gold.arn}/*",
          aws_s3_bucket.bronze.arn,
          aws_s3_bucket.silver.arn,
          aws_s3_bucket.gold.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "data_engineer_policy" {
  role       = aws_iam_role.data_engineer.name
  policy_arn = aws_iam_policy.data_lake_access.arn
}

# AWS Lake Formation (Data Catalog and Governance)
resource "aws_lakeformation_data_lake_settings" "main" {
  admins = [aws_iam_role.data_engineer.arn]
}

resource "aws_glue_catalog_database" "bronze" {
  name = "${var.project_name}_bronze"
  
  description = "Bronze zone - raw data"
  
  location_uri = "s3://${aws_s3_bucket.bronze.bucket}/"
}

resource "aws_glue_catalog_database" "silver" {
  name = "${var.project_name}_silver"
  
  description = "Silver zone - curated data"
  
  location_uri = "s3://${aws_s3_bucket.silver.bucket}/"
}

resource "aws_glue_catalog_database" "gold" {
  name = "${var.project_name}_gold"
  
  description = "Gold zone - analytics-ready data"
  
  location_uri = "s3://${aws_s3_bucket.gold.bucket}/"
}

# Outputs
output "bronze_bucket" {
  value = aws_s3_bucket.bronze.bucket
}

output "silver_bucket" {
  value = aws_s3_bucket.silver.bucket
}

output "gold_bucket" {
  value = aws_s3_bucket.gold.bucket
}

output "data_engineer_role_arn" {
  value = aws_iam_role.data_engineer.arn
}
```

**Deploy Infrastructure:**
```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -out=tfplan

# Apply the infrastructure
terraform apply tfplan

# Get outputs
terraform output
```

**Azure Data Lake (Terraform):**
```hcl
# azure_datalake.tf
resource "azurerm_resource_group" "data_lake" {
  name     = "${var.project_name}-rg"
  location = var.location
}

resource "azurerm_storage_account" "data_lake" {
  name                     = "${var.project_name}datalake"
  resource_group_name      = azurerm_resource_group.data_lake.name
  location                 = azurerm_resource_group.data_lake.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true  # Enable hierarchical namespace for ADLS Gen2
  
  blob_properties {
    versioning_enabled = true
  }
  
  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}
```

**Verification:**
- [ ] Infrastructure deployed
- [ ] Buckets/containers created
- [ ] Encryption enabled
- [ ] Access controls set
- [ ] Lifecycle policies active

**If This Fails:**
→ Check cloud credentials
→ Verify permissions
→ Review Terraform logs
→ Check resource quotas
→ Validate configuration

---

### Step 3: Implement Data Ingestion Patterns

**What:** Create robust ingestion pipelines for bronze zone

**How:**

**Batch Ingestion Pipeline:**
```python
# batch_ingestion.py
"""
Batch data ingestion into bronze zone
"""

import boto3
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BronzeIngestion:
    """Ingest data into bronze zone."""
    
    def __init__(self, bucket_name: str, source_system: str):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name
        self.source_system = source_system
    
    def ingest_file(
        self,
        local_file_path: str,
        table_name: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Ingest file to bronze zone with partitioning."""
        
        # Generate partition path
        now = datetime.now()
        partition_path = (
            f"{self.source_system}/"
            f"{table_name}/"
            f"year={now.year}/"
            f"month={now.month:02d}/"
            f"day={now.day:02d}/"
            f"hour={now.hour:02d}/"
        )
        
        # Generate unique filename
        file_name = f"{table_name}_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
        s3_key = partition_path + file_name
        
        # Upload file
        logger.info(f"Uploading {local_file_path} to s3://{self.bucket_name}/{s3_key}")
        
        extra_args = {
            'Metadata': metadata or {},
            'ServerSideEncryption': 'AES256'
        }
        
        self.s3.upload_file(
            local_file_path,
            self.bucket_name,
            s3_key,
            ExtraArgs=extra_args
        )
        
        logger.info(f"✅ Successfully ingested to bronze zone")
        return s3_key
    
    def ingest_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Ingest DataFrame to bronze zone."""
        
        # Save to temp file
        temp_file = f"/tmp/{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        df.to_parquet(temp_file, compression='snappy', index=False)
        
        # Ingest file
        s3_key = self.ingest_file(temp_file, table_name, metadata)
        
        # Clean up
        Path(temp_file).unlink()
        
        return s3_key
    
    def ingest_from_database(
        self,
        query: str,
        table_name: str,
        connection_string: str
    ) -> str:
        """Ingest data from database to bronze zone."""
        
        logger.info(f"Extracting data for {table_name}")
        
        # Read from database
        import sqlalchemy
        engine = sqlalchemy.create_engine(connection_string)
        df = pd.read_sql(query, engine)
        
        logger.info(f"Extracted {len(df)} rows")
        
        # Add metadata
        metadata = {
            'source_query': query[:500],  # Truncate long queries
            'row_count': str(len(df)),
            'extraction_timestamp': datetime.now().isoformat(),
        }
        
        # Ingest
        return self.ingest_dataframe(df, table_name, metadata)

# Usage
ingestion = BronzeIngestion(
    bucket_name="analytics-data-lake-bronze-production",
    source_system="erp_system"
)

# Ingest from database
ingestion.ingest_from_database(
    query="SELECT * FROM customers WHERE updated_at >= CURRENT_DATE - 1",
    table_name="customers",
    connection_string="postgresql://user:pass@localhost:5432/erp"
)
```

**Streaming Ingestion:**
```python
# streaming_ingestion.py
"""
Real-time streaming ingestion to bronze zone
"""

import boto3
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StreamingIngestion:
    """Ingest streaming data to bronze zone."""
    
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name
        self.buffer = []
        self.buffer_size_mb = 5
        self.buffer_time_seconds = 60
    
    def add_event(self, event: dict, source_system: str):
        """Add event to buffer."""
        self.buffer.append({
            'event': event,
            'ingestion_timestamp': datetime.now().isoformat(),
            'source_system': source_system
        })
        
        # Flush if buffer is full
        if self._should_flush():
            self.flush(source_system)
    
    def _should_flush(self) -> bool:
        """Check if buffer should be flushed."""
        import sys
        buffer_size = sys.getsizeof(json.dumps(self.buffer))
        return buffer_size > (self.buffer_size_mb * 1024 * 1024)
    
    def flush(self, source_system: str):
        """Flush buffer to S3."""
        if not self.buffer:
            return
        
        now = datetime.now()
        partition_path = (
            f"{source_system}/"
            f"events/"
            f"year={now.year}/"
            f"month={now.month:02d}/"
            f"day={now.day:02d}/"
            f"hour={now.hour:02d}/"
        )
        
        file_name = f"events_{now.strftime('%Y%m%d_%H%M%S')}.json"
        s3_key = partition_path + file_name
        
        # Upload buffer
        data = json.dumps(self.buffer)
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=data.encode('utf-8'),
            ServerSideEncryption='AES256'
        )
        
        logger.info(f"✅ Flushed {len(self.buffer)} events to {s3_key}")
        self.buffer = []

# Usage with Kafka
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'events-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

streaming = StreamingIngestion("analytics-data-lake-bronze-production")

for message in consumer:
    event = message.value
    streaming.add_event(event, source_system="kafka_events")
```

**Verification:**
- [ ] Ingestion working
- [ ] Partitioning correct
- [ ] Metadata captured
- [ ] Error handling robust
- [ ] Monitoring in place

**If This Fails:**
→ Check permissions
→ Verify network access
→ Review logs
→ Test with small datasets
→ Validate file formats

---

### Step 4: Implement Data Processing Layers

**What:** Create processing pipelines to move data through zones

**How:**

**Bronze to Silver Processing:**
```python
# bronze_to_silver.py
"""
Process data from bronze to silver zone
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BronzeToSilver:
    """Process bronze data to silver zone."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
    
    def read_bronze(
        self,
        bronze_path: str,
        source_system: str,
        table_name: str
    ) -> DataFrame:
        """Read data from bronze zone."""
        
        path = f"{bronze_path}/{source_system}/{table_name}/"
        logger.info(f"Reading from bronze: {path}")
        
        df = self.spark.read.parquet(path)
        logger.info(f"Read {df.count()} rows from bronze")
        
        return df
    
    def clean_data(self, df: DataFrame) -> DataFrame:
        """Apply data cleaning rules."""
        
        logger.info("Cleaning data")
        
        # Remove duplicates
        df_clean = df.dropDuplicates()
        
        # Remove nulls in key columns
        df_clean = df_clean.dropna(subset=['customer_id', 'order_id'])
        
        # Standardize column names
        for col in df_clean.columns:
            df_clean = df_clean.withColumnRenamed(
                col,
                col.lower().replace(' ', '_')
            )
        
        # Trim strings
        for col_name, col_type in df_clean.dtypes:
            if col_type == 'string':
                df_clean = df_clean.withColumn(
                    col_name,
                    F.trim(F.col(col_name))
                )
        
        logger.info(f"Cleaned to {df_clean.count()} rows")
        return df_clean
    
    def validate_data(self, df: DataFrame) -> DataFrame:
        """Validate data quality."""
        
        logger.info("Validating data")
        
        # Add validation flags
        df_validated = df.withColumn(
            'is_valid_email',
            F.col('email').rlike(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        )
        
        df_validated = df_validated.withColumn(
            'is_positive_amount',
            F.col('amount') > 0
        )
        
        # Filter invalid records
        invalid_count = df_validated.filter(
            ~(F.col('is_valid_email') & F.col('is_positive_amount'))
        ).count()
        
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} invalid records")
        
        # Keep only valid records
        df_valid = df_validated.filter(
            F.col('is_valid_email') & F.col('is_positive_amount')
        )
        
        # Drop validation columns
        df_valid = df_valid.drop('is_valid_email', 'is_positive_amount')
        
        return df_valid
    
    def add_metadata(self, df: DataFrame) -> DataFrame:
        """Add processing metadata."""
        
        return df \
            .withColumn('processed_at', F.current_timestamp()) \
            .withColumn('processing_date', F.current_date()) \
            .withColumn('data_source', F.lit('bronze_zone'))
    
    def write_silver(
        self,
        df: DataFrame,
        silver_path: str,
        domain: str,
        table_name: str
    ):
        """Write to silver zone with partitioning."""
        
        path = f"{silver_path}/{domain}/{table_name}/"
        logger.info(f"Writing to silver: {path}")
        
        df.write \
            .mode('overwrite') \
            .partitionBy('processing_date') \
            .parquet(path)
        
        logger.info("✅ Successfully wrote to silver zone")
    
    def process(
        self,
        bronze_path: str,
        silver_path: str,
        source_system: str,
        domain: str,
        table_name: str
    ):
        """Run complete bronze to silver processing."""
        
        try:
            # Read
            df = self.read_bronze(bronze_path, source_system, table_name)
            
            # Clean
            df_clean = self.clean_data(df)
            
            # Validate
            df_valid = self.validate_data(df_clean)
            
            # Add metadata
            df_final = self.add_metadata(df_valid)
            
            # Write
            self.write_silver(df_final, silver_path, domain, table_name)
            
            logger.info("✅ Processing completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Processing failed: {e}")
            raise

# Usage
spark = SparkSession.builder \
    .appName("BronzeToSilver") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

processor = BronzeToSilver(spark)

processor.process(
    bronze_path="s3://analytics-data-lake-bronze-production",
    silver_path="s3://analytics-data-lake-silver-production",
    source_system="erp_system",
    domain="sales",
    table_name="orders"
)
```

**Silver to Gold Processing:**
```python
# silver_to_gold.py
"""
Create analytics-ready datasets in gold zone
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

class SilverToGold:
    """Create gold zone analytics datasets."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
    
    def create_customer_360(
        self,
        silver_path: str,
        gold_path: str
    ):
        """Create customer 360 view."""
        
        # Read silver tables
        customers = self.spark.read.parquet(f"{silver_path}/sales/customers/")
        orders = self.spark.read.parquet(f"{silver_path}/sales/orders/")
        
        # Calculate customer metrics
        customer_metrics = orders.groupBy('customer_id').agg(
            F.count('*').alias('total_orders'),
            F.sum('amount').alias('lifetime_value'),
            F.avg('amount').alias('avg_order_value'),
            F.min('order_date').alias('first_order_date'),
            F.max('order_date').alias('last_order_date'),
        )
        
        # Add RFM scores
        window = Window.orderBy('last_order_date')
        
        customer_360 = customers.join(customer_metrics, 'customer_id', 'left') \
            .withColumn(
                'recency_days',
                F.datediff(F.current_date(), F.col('last_order_date'))
            ) \
            .withColumn(
                'customer_segment',
                F.when(F.col('lifetime_value') > 10000, 'VIP')
                 .when(F.col('lifetime_value') > 1000, 'Gold')
                 .when(F.col('lifetime_value') > 100, 'Silver')
                 .otherwise('Bronze')
            )
        
        # Write to gold
        customer_360.write \
            .mode('overwrite') \
            .format('delta') \
            .save(f"{gold_path}/analytics/customer_360/")
        
        logger.info("✅ Created customer 360 view")

# Usage
spark = SparkSession.builder \
    .appName("SilverToGold") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

processor = SilverToGold(spark)
processor.create_customer_360(
    silver_path="s3://analytics-data-lake-silver-production",
    gold_path="s3://analytics-data-lake-gold-production"
)
```

**Verification:**
- [ ] Processing pipelines working
- [ ] Data quality improved
- [ ] Transformations correct
- [ ] Performance acceptable
- [ ] Monitoring in place

**If This Fails:**
→ Check Spark configuration
→ Review data quality
→ Profile performance
→ Validate transformations
→ Check resource allocation

---

### Step 5: Implement Governance and Access Control

**What:** Set up data governance, cataloging, and access controls

**How:**

**AWS Lake Formation Permissions:**
```python
# lake_formation_governance.py
"""
Configure Lake Formation governance
"""

import boto3

lf_client = boto3.client('lakeformation')
glue_client = boto3.client('glue')

def grant_database_permissions(
    principal_arn: str,
    database_name: str,
    permissions: list
):
    """Grant database-level permissions."""
    
    response = lf_client.grant_permissions(
        Principal={'DataLakePrincipalIdentifier': principal_arn},
        Resource={'Database': {'Name': database_name}},
        Permissions=permissions,
        PermissionsWithGrantOption=[]
    )
    
    print(f"✅ Granted {permissions} on {database_name}")

def grant_table_permissions(
    principal_arn: str,
    database_name: str,
    table_name: str,
    permissions: list,
    column_names: list = None
):
    """Grant table-level permissions."""
    
    resource = {
        'Table': {
            'DatabaseName': database_name,
            'Name': table_name
        }
    }
    
    # Column-level permissions
    if column_names:
        resource = {
            'TableWithColumns': {
                'DatabaseName': database_name,
                'Name': table_name,
                'ColumnNames': column_names
            }
        }
    
    response = lf_client.grant_permissions(
        Principal={'DataLakePrincipalIdentifier': principal_arn},
        Resource=resource,
        Permissions=permissions,
        PermissionsWithGrantOption=[]
    )
    
    print(f"✅ Granted {permissions} on {database_name}.{table_name}")

# Grant permissions
data_engineer_role = "arn:aws:iam::123456789012:role/analytics-data-lake-data-engineer"
analyst_role = "arn:aws:iam::123456789012:role/data-analyst"

# Data engineers get full access
grant_database_permissions(
    principal_arn=data_engineer_role,
    database_name="analytics_data_lake_bronze",
    permissions=['ALL']
)

# Analysts get read-only access to gold
grant_table_permissions(
    principal_arn=analyst_role,
    database_name="analytics_data_lake_gold",
    table_name="customer_360",
    permissions=['SELECT']
)

# Column-level security - hide PII
grant_table_permissions(
    principal_arn=analyst_role,
    database_name="analytics_data_lake_gold",
    table_name="customer_360",
    column_names=['customer_id', 'segment', 'lifetime_value'],  # Exclude email, phone
    permissions=['SELECT']
)
```

**Verification:**
- [ ] Permissions configured
- [ ] Access controls tested
- [ ] Audit logging enabled
- [ ] Compliance requirements met
- [ ] Documentation complete

**If This Fails:**
→ Review IAM policies
→ Check Lake Formation settings
→ Test with different roles
→ Verify resource permissions
→ Review audit logs

---

## Verification Checklist

After completing this workflow:

- [ ] Zone architecture defined
- [ ] Infrastructure deployed
- [ ] Ingestion pipelines working
- [ ] Processing layers functional
- [ ] Governance implemented
- [ ] Access controls set
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Performance optimized
- [ ] Disaster recovery planned

---

## Common Issues & Solutions

### Issue: Data Swamp Formation

**Symptoms:**
- Unorganized data
- Duplicate datasets
- No metadata
- Unknown data quality

**Solution:**
- Enforce zone structure
- Implement data catalog
- Apply governance policies
- Monitor data quality
- Document all datasets

---

## Best Practices

### DO:
✅ Use zone architecture (bronze/silver/gold)
✅ Partition data appropriately
✅ Implement data quality checks
✅ Use columnar formats (Parquet, ORC)
✅ Enable compression
✅ Track metadata and lineage
✅ Implement access controls
✅ Version data when needed
✅ Monitor costs and usage
✅ Document data flows
✅ Use lifecycle policies
✅ Automate governance

### DON'T:
❌ Create flat structure
❌ Skip data quality checks
❌ Ignore governance
❌ Use inefficient formats
❌ Skip partitioning
❌ Forget about costs
❌ Mix processed and raw data
❌ Skip documentation
❌ Ignore access control
❌ Over-engineer initially
❌ Skip monitoring
❌ Forget disaster recovery

---

## Related Workflows

**Prerequisites:**
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture

**Next Steps:**
- [big_data_spark.md](./big_data_spark.md) - Processing at scale
- [data_catalog_governance.md](./data_catalog_governance.md) - Governance

**Related:**
- [data_warehousing_modeling.md](./data_warehousing_modeling.md) - Warehousing
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL patterns

---

## Tags
`data-engineering` `data-lake` `architecture` `aws` `azure` `gcp` `s3` `adls` `lakehouse` `bronze-silver-gold` `terraform` `spark`
