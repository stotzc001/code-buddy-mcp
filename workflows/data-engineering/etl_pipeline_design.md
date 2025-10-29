# ETL Pipeline Design

**ID:** dat-008  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 60-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design and implement Extract, Transform, Load (ETL) pipelines for moving and transforming data between systems

**Why:** ETL pipelines enable reliable data integration, support analytics and ML, ensure data quality, and maintain data consistency across systems

**When to use:**
- Integrating data from multiple sources
- Building data warehouses or lakes
- Creating reporting and analytics pipelines
- Migrating data between systems
- Consolidating data from acquisitions
- Building master data management systems

---

## Prerequisites

**Required:**
- [ ] Understanding of source and target data schemas
- [ ] SQL knowledge for data transformation
- [ ] Python or similar scripting language
- [ ] Basic understanding of data modeling
- [ ] Access to source and target systems

**Check before starting:**
```bash
# Verify Python environment
python --version  # Should be 3.8+

# Check database connectivity
psql -h source-db.example.com -U user -d database -c "SELECT 1;"
psql -h target-db.example.com -U user -d warehouse -c "SELECT 1;"

# Verify ETL tool installed (if using)
airflow version
# or
dagster --version
```

---

## Implementation Steps

### Step 1: Define ETL Requirements and Choose Pattern

**What:** Understand requirements and decide between ETL, ELT, or hybrid approaches

**How:**

**Requirements Gathering:**
```markdown
## ETL Requirements Checklist

### Data Sources
- [ ] What systems are sources? (APIs, databases, files, streams)
- [ ] What is the data volume? (MB, GB, TB per day)
- [ ] What is the data velocity? (batch daily, hourly, real-time)
- [ ] What is data format? (JSON, CSV, Parquet, Avro)

### Business Requirements
- [ ] What is the SLA? (data freshness requirements)
- [ ] What transformations are needed?
- [ ] What is acceptable latency?
- [ ] What are data quality requirements?

### Technical Constraints
- [ ] Available compute resources
- [ ] Network bandwidth limitations
- [ ] Storage constraints
- [ ] Compliance requirements (GDPR, HIPAA, etc.)
```

**ETL vs ELT Decision Matrix:**
```python
# ETL Pattern (Transform before Load)
# Use when:
# - Target system has limited compute (e.g., simple data warehouse)
# - Data transformations are complex and computationally expensive
# - Need to cleanse/validate before loading
# - Source systems can't be directly queried by analysts

# Example: Extract from MySQL → Transform in Python → Load to PostgreSQL

# ELT Pattern (Load then Transform)  
# Use when:
# - Target system is powerful (e.g., Snowflake, BigQuery, Redshift)
# - Want to preserve raw data for future use
# - Transformations can leverage target's compute power
# - Need flexibility in transformation logic

# Example: Extract from MySQL → Load to Snowflake → Transform with dbt
```

**Architecture Decision:**
```python
"""
ETL Pipeline Architecture Selection Guide
"""

from dataclasses import dataclass
from typing import List, Literal

@dataclass
class PipelineRequirements:
    data_volume_gb_per_day: float
    latency_requirement: Literal["real-time", "near-real-time", "batch"]
    source_count: int
    transformation_complexity: Literal["simple", "moderate", "complex"]
    target_system_compute_power: Literal["limited", "moderate", "powerful"]

def recommend_pattern(reqs: PipelineRequirements) -> str:
    """Recommend ETL pattern based on requirements."""
    
    # Real-time requirements
    if reqs.latency_requirement == "real-time":
        return "Stream Processing (Kafka + Flink/Spark Streaming)"
    
    # Large volume + powerful target = ELT
    if (reqs.data_volume_gb_per_day > 100 and 
        reqs.target_system_compute_power == "powerful"):
        return "ELT (Load raw → Transform in warehouse with dbt/SQL)"
    
    # Complex transformations + limited target = ETL
    if (reqs.transformation_complexity == "complex" and
        reqs.target_system_compute_power == "limited"):
        return "ETL (Transform before load using Spark/Python)"
    
    # Default: Batch ETL
    return "Batch ETL (Scheduled transformation pipeline)"

# Example usage
reqs = PipelineRequirements(
    data_volume_gb_per_day=50,
    latency_requirement="batch",
    source_count=5,
    transformation_complexity="moderate",
    target_system_compute_power="moderate"
)

pattern = recommend_pattern(reqs)
print(f"Recommended: {pattern}")
```

**Verification:**
- [ ] Requirements documented
- [ ] Pattern selected (ETL/ELT/Hybrid)
- [ ] Data sources identified
- [ ] Target schema defined
- [ ] SLA documented

**If This Fails:**
→ Schedule stakeholder meetings to clarify requirements
→ Review existing data architecture
→ Assess current tooling capabilities
→ Start with small pilot to validate approach

---

### Step 2: Design Data Extraction Strategy

**What:** Define how to extract data from source systems efficiently and reliably

**How:**

**Extraction Patterns:**
```python
"""
Common Data Extraction Patterns
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import psycopg2
import requests

# Pattern 1: Full Extraction (for small datasets)
def full_extract(connection_string: str, table: str) -> List[Dict]:
    """Extract all records from source."""
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table}")
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

# Pattern 2: Incremental Extraction (timestamp-based)
def incremental_extract_timestamp(
    connection_string: str,
    table: str,
    timestamp_column: str,
    last_extract_time: datetime
) -> List[Dict]:
    """Extract only records modified since last extraction."""
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    query = f"""
        SELECT * FROM {table}
        WHERE {timestamp_column} > %s
        ORDER BY {timestamp_column}
    """
    cursor.execute(query, (last_extract_time,))
    
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

# Pattern 3: Incremental Extraction (ID-based)
def incremental_extract_id(
    connection_string: str,
    table: str,
    id_column: str,
    last_extracted_id: int,
    batch_size: int = 1000
) -> List[Dict]:
    """Extract records with ID greater than last extracted."""
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    query = f"""
        SELECT * FROM {table}
        WHERE {id_column} > %s
        ORDER BY {id_column}
        LIMIT %s
    """
    cursor.execute(query, (last_extracted_id, batch_size))
    
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

# Pattern 4: API Extraction with Pagination
def extract_from_api(
    api_url: str,
    api_key: str,
    page_size: int = 100
) -> List[Dict]:
    """Extract data from paginated REST API."""
    all_records = []
    page = 1
    has_more = True
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    while has_more:
        response = requests.get(
            api_url,
            headers=headers,
            params={"page": page, "page_size": page_size}
        )
        response.raise_for_status()
        
        data = response.json()
        records = data.get("results", [])
        all_records.extend(records)
        
        has_more = data.get("has_more", False)
        page += 1
    
    return all_records

# Pattern 5: Change Data Capture (CDC)
def extract_with_cdc(
    connection_string: str,
    cdc_table: str,
    last_lsn: int
) -> List[Dict]:
    """
    Extract changes using database CDC (Change Data Capture).
    Example for PostgreSQL logical replication or SQL Server CDC.
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    # PostgreSQL logical decoding example
    query = """
        SELECT lsn, operation, table_name, data
        FROM pg_logical_slot_get_changes('my_slot', NULL, NULL, 
                                          'format-version', '1',
                                          'add-tables', 'public.*')
        WHERE lsn > %s
    """
    cursor.execute(query, (last_lsn,))
    
    changes = cursor.fetchall()
    conn.close()
    
    return [
        {
            "lsn": change[0],
            "operation": change[1],
            "table": change[2],
            "data": change[3]
        }
        for change in changes
    ]
```

**Extraction State Management:**
```python
"""
Track extraction state for incremental loads
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

class ExtractionStateManager:
    """Manage extraction watermarks and state."""
    
    def __init__(self, state_file: str = "extraction_state.json"):
        self.state_file = Path(state_file)
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_state(self):
        """Persist state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def get_watermark(self, source: str, table: str) -> Optional[datetime]:
        """Get last extraction timestamp for table."""
        key = f"{source}.{table}"
        watermark = self.state.get(key)
        
        if watermark:
            return datetime.fromisoformat(watermark)
        return None
    
    def set_watermark(self, source: str, table: str, timestamp: datetime):
        """Update extraction watermark."""
        key = f"{source}.{table}"
        self.state[key] = timestamp.isoformat()
        self._save_state()
    
    def get_last_id(self, source: str, table: str) -> Optional[int]:
        """Get last extracted ID."""
        key = f"{source}.{table}.last_id"
        return self.state.get(key)
    
    def set_last_id(self, source: str, table: str, last_id: int):
        """Update last extracted ID."""
        key = f"{source}.{table}.last_id"
        self.state[key] = last_id
        self._save_state()

# Usage
state_mgr = ExtractionStateManager()

# Get last watermark
last_extract = state_mgr.get_watermark("crm_db", "customers")
if last_extract is None:
    # First run - full extraction
    last_extract = datetime(2020, 1, 1)

# Extract data
new_records = incremental_extract_timestamp(
    connection_string="postgresql://...",
    table="customers",
    timestamp_column="updated_at",
    last_extract_time=last_extract
)

# Update watermark
if new_records:
    latest_timestamp = max(r["updated_at"] for r in new_records)
    state_mgr.set_watermark("crm_db", "customers", latest_timestamp)
```

**Verification:**
- [ ] Extraction method chosen
- [ ] State management implemented
- [ ] Connection pooling configured
- [ ] Error handling added
- [ ] Extraction tested with sample data

**If This Fails:**
→ Check network connectivity to sources
→ Verify credentials and permissions
→ Test queries in database client first
→ Start with smaller batch sizes
→ Add retry logic for transient failures

---

### Step 3: Implement Data Transformation Logic

**What:** Transform extracted data to match target schema and business rules

**How:**

**Transformation Patterns:**
```python
"""
Common ETL Transformation Patterns
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import hashlib

# Pattern 1: Schema Mapping
def map_schema(records: List[Dict], mapping: Dict[str, str]) -> List[Dict]:
    """Map source schema to target schema."""
    return [
        {target_col: record.get(source_col)
         for target_col, source_col in mapping.items()}
        for record in records
    ]

# Example usage
source_data = [
    {"first_name": "John", "last_name": "Doe", "email_address": "john@example.com"}
]

schema_mapping = {
    "full_name": lambda r: f"{r['first_name']} {r['last_name']}",
    "email": "email_address"
}

# Pattern 2: Data Type Conversion
def convert_types(df: pd.DataFrame, type_mapping: Dict[str, str]) -> pd.DataFrame:
    """Convert column data types."""
    df = df.copy()
    
    for col, dtype in type_mapping.items():
        if dtype == "datetime":
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif dtype == "numeric":
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif dtype == "string":
            df[col] = df[col].astype(str)
    
    return df

# Pattern 3: Data Cleaning
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize data."""
    df = df.copy()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Trim whitespace from string columns
    string_cols = df.select_dtypes(include=['object']).columns
    df[string_cols] = df[string_cols].apply(lambda x: x.str.strip())
    
    # Standardize null values
    df = df.replace(['', 'NULL', 'null', 'N/A', 'nan'], pd.NA)
    
    # Handle missing values
    # Option 1: Fill with defaults
    df['country'] = df['country'].fillna('Unknown')
    
    # Option 2: Forward fill for time series
    df['value'] = df['value'].fillna(method='ffill')
    
    # Option 3: Drop rows with critical nulls
    df = df.dropna(subset=['id', 'email'])
    
    return df

# Pattern 4: Business Logic Transformation
def apply_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Apply business logic transformations."""
    df = df.copy()
    
    # Calculate derived fields
    df['order_total'] = df['quantity'] * df['unit_price']
    df['discount_amount'] = df['order_total'] * df['discount_rate']
    df['final_amount'] = df['order_total'] - df['discount_amount']
    
    # Categorization
    df['customer_segment'] = pd.cut(
        df['lifetime_value'],
        bins=[0, 1000, 5000, float('inf')],
        labels=['Bronze', 'Silver', 'Gold']
    )
    
    # Flag anomalies
    df['is_high_value'] = df['order_total'] > df['order_total'].quantile(0.95)
    
    return df

# Pattern 5: Aggregation
def aggregate_data(df: pd.DataFrame, group_by: List[str]) -> pd.DataFrame:
    """Aggregate data for analytics."""
    agg_df = df.groupby(group_by).agg({
        'order_id': 'count',
        'order_total': ['sum', 'mean', 'min', 'max'],
        'customer_id': 'nunique'
    }).reset_index()
    
    # Flatten column names
    agg_df.columns = ['_'.join(col).strip('_') for col in agg_df.columns]
    
    return agg_df

# Pattern 6: Join/Enrich Data
def enrich_data(
    main_df: pd.DataFrame,
    lookup_df: pd.DataFrame,
    join_key: str,
    join_type: str = 'left'
) -> pd.DataFrame:
    """Enrich main dataset with lookup data."""
    return main_df.merge(
        lookup_df,
        on=join_key,
        how=join_type,
        suffixes=('', '_lookup')
    )

# Pattern 7: Slowly Changing Dimensions (SCD Type 2)
def implement_scd_type2(
    existing_df: pd.DataFrame,
    new_df: pd.DataFrame,
    business_key: str
) -> pd.DataFrame:
    """
    Implement SCD Type 2 for historical tracking.
    Adds: valid_from, valid_to, is_current, version
    """
    # Close out existing records that have changed
    existing_df['is_current'] = False
    existing_df['valid_to'] = datetime.now()
    
    # Add new records as current
    new_df['is_current'] = True
    new_df['valid_from'] = datetime.now()
    new_df['valid_to'] = datetime(9999, 12, 31)
    new_df['version'] = 1
    
    # Combine
    result = pd.concat([existing_df, new_df], ignore_index=True)
    
    return result

# Pattern 8: Data Quality Checks
def validate_data(df: pd.DataFrame) -> tuple[pd.DataFrame, List[str]]:
    """Validate data quality and return clean data + errors."""
    errors = []
    
    # Check for required fields
    required_cols = ['id', 'email', 'created_at']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    
    # Check data types
    if 'email' in df.columns:
        invalid_emails = df[~df['email'].str.contains('@', na=False)]
        if not invalid_emails.empty:
            errors.append(f"Found {len(invalid_emails)} invalid emails")
            df = df[df['email'].str.contains('@', na=False)]
    
    # Check value ranges
    if 'age' in df.columns:
        invalid_ages = df[(df['age'] < 0) | (df['age'] > 120)]
        if not invalid_ages.empty:
            errors.append(f"Found {len(invalid_ages)} invalid ages")
            df = df[(df['age'] >= 0) & (df['age'] <= 120)]
    
    # Check for duplicates
    duplicates = df[df.duplicated(subset=['id'], keep=False)]
    if not duplicates.empty:
        errors.append(f"Found {len(duplicates)} duplicate IDs")
        df = df.drop_duplicates(subset=['id'], keep='last')
    
    return df, errors
```

**Complete Transformation Pipeline:**
```python
"""
Complete transformation pipeline orchestration
"""

import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLTransformer:
    """Orchestrate all transformation steps."""
    
    def __init__(self):
        self.metrics = {
            "records_in": 0,
            "records_out": 0,
            "records_filtered": 0,
            "errors": []
        }
    
    def transform(self, records: List[Dict]) -> pd.DataFrame:
        """Run complete transformation pipeline."""
        self.metrics["records_in"] = len(records)
        logger.info(f"Starting transformation of {len(records)} records")
        
        # Step 1: Convert to DataFrame
        df = pd.DataFrame(records)
        logger.info(f"Loaded {len(df)} records into DataFrame")
        
        # Step 2: Schema mapping
        df = self._map_schema(df)
        logger.info("Schema mapping complete")
        
        # Step 3: Data type conversion
        df = self._convert_types(df)
        logger.info("Type conversion complete")
        
        # Step 4: Data cleaning
        df = clean_data(df)
        logger.info(f"Data cleaning complete, {len(df)} records remaining")
        
        # Step 5: Business rules
        df = apply_business_rules(df)
        logger.info("Business rules applied")
        
        # Step 6: Data validation
        df, errors = validate_data(df)
        self.metrics["errors"] = errors
        if errors:
            logger.warning(f"Validation errors: {errors}")
        
        self.metrics["records_out"] = len(df)
        self.metrics["records_filtered"] = (
            self.metrics["records_in"] - self.metrics["records_out"]
        )
        
        logger.info(f"Transformation complete: {self.metrics}")
        return df
    
    def _map_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map source schema to target."""
        # Implementation specific to your schemas
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert data types."""
        type_mapping = {
            "created_at": "datetime",
            "amount": "numeric",
            "email": "string"
        }
        return convert_types(df, type_mapping)

# Usage
transformer = ETLTransformer()
transformed_df = transformer.transform(extracted_records)
print(f"Transformation metrics: {transformer.metrics}")
```

**Verification:**
- [ ] Transformations tested with sample data
- [ ] Data quality checks implemented
- [ ] Business rules validated
- [ ] Performance acceptable
- [ ] Error handling in place

**If This Fails:**
→ Test transformations incrementally
→ Use smaller sample datasets first
→ Add logging for each transformation step
→ Profile code to identify bottlenecks
→ Consider using Spark for large volumes

---

### Step 4: Implement Data Loading Strategy

**What:** Load transformed data into target system efficiently

**How:**

**Loading Patterns:**
```python
"""
Data Loading Strategies
"""

import psycopg2
from psycopg2.extras import execute_batch, execute_values
import pandas as pd
from typing import List, Dict

# Pattern 1: Bulk Insert (fastest for new data)
def bulk_insert(
    connection_string: str,
    table: str,
    df: pd.DataFrame,
    batch_size: int = 1000
):
    """Bulk insert using COPY (PostgreSQL) or equivalent."""
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    # PostgreSQL COPY is fastest
    from io import StringIO
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    
    cursor.copy_from(
        buffer,
        table,
        sep=',',
        null='',
        columns=df.columns.tolist()
    )
    
    conn.commit()
    conn.close()

# Pattern 2: Upsert (Update or Insert)
def upsert_data(
    connection_string: str,
    table: str,
    df: pd.DataFrame,
    conflict_columns: List[str]
):
    """
    Insert or update on conflict.
    PostgreSQL example using ON CONFLICT.
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    # Build column lists
    columns = df.columns.tolist()
    columns_str = ', '.join(columns)
    values_placeholder = ', '.join(['%s'] * len(columns))
    
    # Build update clause
    update_clause = ', '.join([
        f"{col} = EXCLUDED.{col}"
        for col in columns
        if col not in conflict_columns
    ])
    
    conflict_str = ', '.join(conflict_columns)
    
    query = f"""
        INSERT INTO {table} ({columns_str})
        VALUES ({values_placeholder})
        ON CONFLICT ({conflict_str})
        DO UPDATE SET {update_clause}
    """
    
    # Batch insert
    records = [tuple(row) for row in df.values]
    execute_batch(cursor, query, records, page_size=1000)
    
    conn.commit()
    conn.close()

# Pattern 3: Incremental Load with Staging
def incremental_load_with_staging(
    connection_string: str,
    target_table: str,
    df: pd.DataFrame,
    merge_key: str
):
    """
    Load to staging table, then merge to target.
    Best for complex merge logic.
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    staging_table = f"{target_table}_staging"
    
    try:
        # 1. Create staging table
        cursor.execute(f"""
            CREATE TEMP TABLE {staging_table}
            (LIKE {target_table} INCLUDING ALL)
        """)
        
        # 2. Load data to staging
        bulk_insert(connection_string, staging_table, df)
        
        # 3. Merge staging to target
        cursor.execute(f"""
            -- Update existing records
            UPDATE {target_table} t
            SET 
                column1 = s.column1,
                column2 = s.column2,
                updated_at = CURRENT_TIMESTAMP
            FROM {staging_table} s
            WHERE t.{merge_key} = s.{merge_key};
            
            -- Insert new records
            INSERT INTO {target_table}
            SELECT s.* 
            FROM {staging_table} s
            LEFT JOIN {target_table} t ON s.{merge_key} = t.{merge_key}
            WHERE t.{merge_key} IS NULL;
        """)
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Pattern 4: Slowly Changing Dimension Load (Type 2)
def load_scd_type2(
    connection_string: str,
    table: str,
    df: pd.DataFrame,
    business_key: str,
    track_columns: List[str]
):
    """
    Load with full history tracking (SCD Type 2).
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    try:
        for _, row in df.iterrows():
            # Check if record exists and has changed
            cursor.execute(f"""
                SELECT * FROM {table}
                WHERE {business_key} = %s
                AND is_current = true
            """, (row[business_key],))
            
            existing = cursor.fetchone()
            
            if existing:
                # Check if any tracked columns changed
                has_changes = any(
                    row[col] != existing[col]
                    for col in track_columns
                    if col in row
                )
                
                if has_changes:
                    # Close out old record
                    cursor.execute(f"""
                        UPDATE {table}
                        SET is_current = false,
                            valid_to = CURRENT_TIMESTAMP
                        WHERE {business_key} = %s
                        AND is_current = true
                    """, (row[business_key],))
                    
                    # Insert new version
                    cursor.execute(f"""
                        INSERT INTO {table} 
                        VALUES (%s, ..., true, CURRENT_TIMESTAMP, '9999-12-31')
                    """, tuple(row))
            else:
                # New record - insert as current
                cursor.execute(f"""
                    INSERT INTO {table}
                    VALUES (%s, ..., true, CURRENT_TIMESTAMP, '9999-12-31')
                """, tuple(row))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Pattern 5: Partition-Aware Loading
def load_to_partitioned_table(
    connection_string: str,
    table: str,
    df: pd.DataFrame,
    partition_column: str
):
    """
    Load data to correct partition based on date/key.
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    # Group by partition value
    for partition_value, group_df in df.groupby(partition_column):
        # Determine partition table name
        # Example for date partitioning: table_2024_01
        partition_name = f"{table}_{partition_value}"
        
        # Load to specific partition
        bulk_insert(connection_string, partition_name, group_df)
    
    conn.close()

# Pattern 6: Load with Error Handling and Dead Letter Queue
def load_with_error_handling(
    connection_string: str,
    table: str,
    records: List[Dict],
    error_table: str = "etl_load_errors"
):
    """
    Load records individually, logging failures to error table.
    """
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    for record in records:
        try:
            # Attempt to insert
            columns = ', '.join(record.keys())
            placeholders = ', '.join(['%s'] * len(record))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, tuple(record.values()))
            conn.commit()
            success_count += 1
            
        except Exception as e:
            conn.rollback()
            error_count += 1
            
            # Log to error table
            cursor.execute(f"""
                INSERT INTO {error_table} 
                (table_name, record_data, error_message, error_timestamp)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (table, str(record), str(e)))
            conn.commit()
    
    conn.close()
    return success_count, error_count
```

**Verification:**
- [ ] Load tested with sample data
- [ ] Transaction handling implemented
- [ ] Performance benchmarked
- [ ] Error records captured
- [ ] Indexes considered

**If This Fails:**
→ Check target database permissions
→ Verify network connectivity
→ Test with smaller batches first
→ Review database logs for errors
→ Consider temporarily disabling indexes during bulk load

---

### Step 5: Implement Error Handling and Monitoring

**What:** Add robust error handling, logging, and monitoring

**How:**

**Error Handling Framework:**
```python
"""
Comprehensive ETL Error Handling
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Callable
from functools import wraps
import smtplib
from email.mime.text import MIMEText

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Error tracking
class ETLError(Exception):
    """Base exception for ETL errors."""
    pass

class ExtractionError(ETLError):
    """Error during data extraction."""
    pass

class TransformationError(ETLError):
    """Error during data transformation."""
    pass

class LoadError(ETLError):
    """Error during data loading."""
    pass

# Retry decorator
def retry(max_attempts: int = 3, delay: int = 5):
    """Retry decorator for transient failures."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                    import time
                    time.sleep(delay)
        return wrapper
    return decorator

# Circuit breaker pattern
class CircuitBreaker:
    """Circuit breaker for external dependencies."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "open":
            if (datetime.now() - self.last_failure_time).seconds > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened after {self.failures} failures")
            raise e

# Monitoring and Alerting
class ETLMonitor:
    """Monitor ETL pipeline execution."""
    
    def __init__(self):
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "records_extracted": 0,
            "records_transformed": 0,
            "records_loaded": 0,
            "errors": [],
            "status": "not_started"
        }
    
    def start(self):
        """Mark pipeline start."""
        self.metrics["start_time"] = datetime.now()
        self.metrics["status"] = "running"
        logger.info("ETL pipeline started")
    
    def complete(self):
        """Mark pipeline completion."""
        self.metrics["end_time"] = datetime.now()
        self.metrics["status"] = "completed"
        
        duration = (self.metrics["end_time"] - self.metrics["start_time"]).seconds
        logger.info(f"ETL pipeline completed in {duration}s")
        logger.info(f"Metrics: {self.metrics}")
        
        # Send success notification
        self._send_notification("ETL Pipeline Success", self._format_metrics())
    
    def fail(self, error: Exception):
        """Mark pipeline failure."""
        self.metrics["end_time"] = datetime.now()
        self.metrics["status"] = "failed"
        self.metrics["errors"].append(str(error))
        
        logger.error(f"ETL pipeline failed: {error}")
        logger.error(traceback.format_exc())
        
        # Send failure alert
        self._send_alert("ETL Pipeline Failure", str(error))
    
    def record_extraction(self, count: int):
        """Record extraction metrics."""
        self.metrics["records_extracted"] = count
        logger.info(f"Extracted {count} records")
    
    def record_transformation(self, count: int):
        """Record transformation metrics."""
        self.metrics["records_transformed"] = count
        logger.info(f"Transformed {count} records")
    
    def record_load(self, count: int):
        """Record load metrics."""
        self.metrics["records_loaded"] = count
        logger.info(f"Loaded {count} records")
    
    def _format_metrics(self) -> str:
        """Format metrics for notification."""
        return f"""
        ETL Pipeline Metrics:
        - Duration: {(self.metrics['end_time'] - self.metrics['start_time']).seconds}s
        - Records Extracted: {self.metrics['records_extracted']}
        - Records Transformed: {self.metrics['records_transformed']}
        - Records Loaded: {self.metrics['records_loaded']}
        - Status: {self.metrics['status']}
        """
    
    def _send_notification(self, subject: str, body: str):
        """Send email notification."""
        # Implementation depends on email service
        logger.info(f"Notification: {subject}")
    
    def _send_alert(self, subject: str, body: str):
        """Send urgent alert."""
        # Could integrate with PagerDuty, Slack, etc.
        logger.error(f"Alert: {subject} - {body}")

# Usage in ETL pipeline
@retry(max_attempts=3, delay=5)
def extract_with_retry():
    """Extract with automatic retry."""
    return extract_data()

# Complete pipeline with error handling
def run_etl_pipeline():
    """Run complete ETL pipeline with error handling."""
    monitor = ETLMonitor()
    circuit_breaker = CircuitBreaker()
    
    try:
        monitor.start()
        
        # Extract
        records = circuit_breaker.call(extract_with_retry)
        monitor.record_extraction(len(records))
        
        # Transform
        transformed = transform_data(records)
        monitor.record_transformation(len(transformed))
        
        # Load
        loaded = load_data(transformed)
        monitor.record_load(loaded)
        
        monitor.complete()
        
    except Exception as e:
        monitor.fail(e)
        raise
```

**Verification:**
- [ ] Error handling tested
- [ ] Logging configured
- [ ] Monitoring dashboard set up
- [ ] Alerts configured
- [ ] Retry logic validated

**If This Fails:**
→ Review logs for specific errors
→ Test notification system
→ Verify monitoring endpoints accessible
→ Check alert thresholds

---

### Step 6: Implement Idempotency and Data Quality

**What:** Ensure pipeline can run multiple times safely with data quality checks

**How:**

**Idempotency Patterns:**
```python
"""
Idempotent ETL Execution
"""

import hashlib
import json

# Pattern 1: Execution ID Tracking
class IdempotentPipeline:
    """Ensure pipeline runs are idempotent."""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def should_run(self, execution_id: str) -> bool:
        """Check if execution already completed."""
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT status FROM pipeline_executions
            WHERE execution_id = %s
        """, (execution_id,))
        
        result = cursor.fetchone()
        
        if result and result[0] == 'completed':
            logger.info(f"Execution {execution_id} already completed")
            return False
        return True
    
    def mark_started(self, execution_id: str):
        """Mark execution as started."""
        cursor = self.db_conn.cursor()
        cursor.execute("""
            INSERT INTO pipeline_executions (execution_id, status, start_time)
            VALUES (%s, 'running', CURRENT_TIMESTAMP)
            ON CONFLICT (execution_id) DO UPDATE
            SET status = 'running', start_time = CURRENT_TIMESTAMP
        """, (execution_id,))
        self.db_conn.commit()
    
    def mark_completed(self, execution_id: str):
        """Mark execution as completed."""
        cursor = self.db_conn.cursor()
        cursor.execute("""
            UPDATE pipeline_executions
            SET status = 'completed', end_time = CURRENT_TIMESTAMP
            WHERE execution_id = %s
        """, (execution_id,))
        self.db_conn.commit()

# Pattern 2: Content-Based Deduplication
def generate_record_hash(record: Dict) -> str:
    """Generate stable hash for record deduplication."""
    # Sort keys for consistent hashing
    sorted_record = {k: record[k] for k in sorted(record.keys())}
    record_str = json.dumps(sorted_record, sort_keys=True, default=str)
    return hashlib.sha256(record_str.encode()).hexdigest()

def deduplicate_records(records: List[Dict]) -> List[Dict]:
    """Remove duplicate records based on content hash."""
    seen_hashes = set()
    unique_records = []
    
    for record in records:
        record_hash = generate_record_hash(record)
        if record_hash not in seen_hashes:
            seen_hashes.add(record_hash)
            unique_records.append(record)
    
    return unique_records

# Pattern 3: Truncate and Load for Full Refresh
def safe_truncate_load(
    connection_string: str,
    table: str,
    df: pd.DataFrame
):
    """Safely replace all data in table."""
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN")
        
        # Truncate table
        cursor.execute(f"TRUNCATE TABLE {table}")
        
        # Load new data
        bulk_insert(connection_string, table, df)
        
        # Commit
        cursor.execute("COMMIT")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e
    finally:
        conn.close()
```

**Data Quality Framework:**
```python
"""
Data Quality Validation Framework
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class DataQualityRule:
    """Define a data quality rule."""
    name: str
    description: str
    check_function: Callable
    severity: str  # 'error', 'warning', 'info'

class DataQualityChecker:
    """Validate data quality with configurable rules."""
    
    def __init__(self):
        self.rules: List[DataQualityRule] = []
        self.violations: List[Dict] = []
    
    def add_rule(self, rule: DataQualityRule):
        """Add a quality rule."""
        self.rules.append(rule)
    
    def validate(self, df: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """Run all quality checks."""
        self.violations = []
        passed = True
        
        for rule in self.rules:
            try:
                result = rule.check_function(df)
                
                if not result:
                    violation = {
                        "rule": rule.name,
                        "description": rule.description,
                        "severity": rule.severity
                    }
                    self.violations.append(violation)
                    
                    if rule.severity == 'error':
                        passed = False
                    
                    logger.warning(f"Quality check failed: {rule.name}")
            
            except Exception as e:
                logger.error(f"Error running quality check {rule.name}: {e}")
                passed = False
        
        return passed, self.violations

# Define common quality checks
def check_no_nulls_in_key_columns(df: pd.DataFrame) -> bool:
    """Ensure key columns have no nulls."""
    key_columns = ['id', 'created_at']
    for col in key_columns:
        if col in df.columns and df[col].isnull().any():
            return False
    return True

def check_email_format(df: pd.DataFrame) -> bool:
    """Validate email format."""
    if 'email' not in df.columns:
        return True
    return df['email'].str.contains('@', na=False).all()

def check_date_range(df: pd.DataFrame) -> bool:
    """Ensure dates are within acceptable range."""
    if 'created_at' not in df.columns:
        return True
    
    min_date = pd.Timestamp('2020-01-01')
    max_date = pd.Timestamp.now()
    
    dates = pd.to_datetime(df['created_at'], errors='coerce')
    return ((dates >= min_date) & (dates <= max_date)).all()

def check_no_duplicates(df: pd.DataFrame) -> bool:
    """Check for duplicate IDs."""
    return not df.duplicated(subset=['id']).any()

def check_referential_integrity(df: pd.DataFrame) -> bool:
    """Check foreign key relationships."""
    # Example: all customer_ids should exist in customers table
    # Implementation depends on your schema
    return True

# Usage
quality_checker = DataQualityChecker()

quality_checker.add_rule(DataQualityRule(
    name="no_null_keys",
    description="Key columns must not have null values",
    check_function=check_no_nulls_in_key_columns,
    severity="error"
))

quality_checker.add_rule(DataQualityRule(
    name="valid_emails",
    description="Email addresses must be valid",
    check_function=check_email_format,
    severity="warning"
))

quality_checker.add_rule(DataQualityRule(
    name="valid_dates",
    description="Dates must be within acceptable range",
    check_function=check_date_range,
    severity="error"
))

# Validate before loading
passed, violations = quality_checker.validate(transformed_df)

if not passed:
    logger.error(f"Data quality check failed: {violations}")
    raise DataQualityError(violations)
```

**Verification:**
- [ ] Pipeline can run multiple times safely
- [ ] Duplicate handling tested
- [ ] Quality rules defined
- [ ] Violations logged
- [ ] Failed quality checks block load

**If This Fails:**
→ Test with duplicate data
→ Review quality rule logic
→ Check transaction isolation
→ Verify execution tracking table exists

---

### Step 7: Schedule and Orchestrate Pipeline

**What:** Schedule pipeline execution and handle dependencies

**How:**

**Scheduling with Airflow:**
```python
"""
Apache Airflow DAG for ETL Pipeline
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Define default args
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# Create DAG
with DAG(
    'customer_data_etl',
    default_args=default_args,
    description='Extract customer data from CRM and load to warehouse',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['etl', 'customers'],
) as dag:
    
    # Task 1: Extract
    extract_task = PythonOperator(
        task_id='extract_customer_data',
        python_callable=extract_customer_data,
        op_kwargs={
            'source': 'crm_db',
            'table': 'customers'
        }
    )
    
    # Task 2: Transform
    transform_task = PythonOperator(
        task_id='transform_customer_data',
        python_callable=transform_customer_data
    )
    
    # Task 3: Validate Quality
    quality_check_task = PythonOperator(
        task_id='quality_check',
        python_callable=validate_data_quality
    )
    
    # Task 4: Load
    load_task = PythonOperator(
        task_id='load_to_warehouse',
        python_callable=load_to_warehouse,
        op_kwargs={
            'target': 'warehouse',
            'table': 'dim_customers'
        }
    )
    
    # Task 5: Update Metadata
    metadata_task = BashOperator(
        task_id='update_metadata',
        bash_command='python scripts/update_data_catalog.py'
    )
    
    # Define dependencies
    extract_task >> transform_task >> quality_check_task >> load_task >> metadata_task
```

**Verification:**
- [ ] DAG validated
- [ ] Schedule configured
- [ ] Dependencies correct
- [ ] Retries configured
- [ ] Alerts working

**If This Fails:**
→ Test DAG with `airflow dags test`
→ Check Airflow scheduler is running
→ Verify Python callables are importable
→ Review Airflow logs

---

### Step 8: Document and Maintain Pipeline

**What:** Create documentation and maintenance procedures

**How:**

**Pipeline Documentation:**
```markdown
# Customer Data ETL Pipeline

## Overview
Extracts customer data from Salesforce CRM, transforms for analytics, and loads to Snowflake warehouse.

## Schedule
- **Frequency:** Daily at 2 AM UTC
- **Duration:** ~45 minutes
- **SLA:** Data available by 3 AM UTC

## Data Flow
```
Salesforce CRM (customers table)
  ↓ Extract (incremental, timestamp-based)
Python Transformation Layer
  ↓ Clean, enrich, deduplicate
Snowflake Warehouse (dim_customers table)
```

## Dependencies
- **Upstream:** Salesforce CRM
- **Downstream:** Analytics dashboards, ML models

## Monitoring
- **Dashboard:** https://monitoring.company.com/etl/customers
- **Alerts:** #data-alerts Slack channel
- **Metrics:** Extract count, transform duration, load success rate

## Runbook
### Normal Operation
1. Check Airflow UI for DAG status
2. Verify row counts match expectations
3. Check data quality dashboard

### Troubleshooting
**Issue: Pipeline fails at extraction**
- Check Salesforce API limits
- Verify credentials in Secrets Manager
- Check network connectivity

**Issue: Data quality check fails**
- Review quality_violations table
- Check for schema changes in source
- Validate business rules

### Recovery
**Full Reload:**
```bash
airflow dags backfill customer_data_etl -s 2024-01-01 -e 2024-01-31
```

**Rerun Failed Tasks:**
```bash
airflow tasks clear customer_data_etl -t load_to_warehouse -s 2024-01-15
```

## Contacts
- **Owner:** Data Engineering Team
- **On-call:** #data-oncall
- **Escalation:** data-engineering-lead@company.com
```

**Verification:**
- [ ] Documentation complete
- [ ] Runbook tested
- [ ] Contacts updated
- [ ] Monitoring configured
- [ ] Alerts validated

**If This Fails:**
→ Review with team for completeness
→ Test runbook procedures
→ Update based on feedback

---

## Verification Checklist

After completing this workflow:

- [ ] ETL requirements documented
- [ ] Pattern selected (ETL/ELT/Hybrid)
- [ ] Extraction strategy implemented
- [ ] Transformation logic tested
- [ ] Loading strategy validated
- [ ] Error handling comprehensive
- [ ] Data quality checks active
- [ ] Idempotency ensured
- [ ] Monitoring and alerts configured
- [ ] Pipeline scheduled
- [ ] Documentation complete
- [ ] Runbook created

---

## Common Issues & Solutions

### Issue: Pipeline Performance Degrading

**Symptoms:**
- Increasing execution time
- Timeouts
- Resource exhaustion

**Solution:**
```python
# 1. Add batch processing
def extract_in_batches(batch_size=10000):
    offset = 0
    while True:
        batch = extract_batch(offset, batch_size)
        if not batch:
            break
        yield batch
        offset += batch_size

# 2. Use parallel processing
from multiprocessing import Pool

def transform_parallel(records, num_workers=4):
    with Pool(num_workers) as pool:
        chunks = chunk_records(records, num_workers)
        results = pool.map(transform_chunk, chunks)
    return flatten(results)

# 3. Optimize database queries
# Add indexes on timestamp columns
# Use EXPLAIN ANALYZE to identify slow queries
# Consider materialized views for complex joins
```

**Prevention:**
- Monitor execution metrics
- Set up performance alerts
- Review and optimize regularly
- Use profiling tools

---

### Issue: Data Quality Failures

**Symptoms:**
- Unexpected null values
- Duplicates in data
- Invalid formats
- Out-of-range values

**Solution:**
```python
# Implement comprehensive validation
def validate_record(record):
    errors = []
    
    # Required fields
    if not record.get('id'):
        errors.append("Missing ID")
    
    # Format validation
    if 'email' in record and '@' not in record['email']:
        errors.append("Invalid email format")
    
    # Range validation
    if 'age' in record and (record['age'] < 0 or record['age'] > 120):
        errors.append("Age out of range")
    
    # Referential integrity
    if not customer_exists(record.get('customer_id')):
        errors.append("Invalid customer reference")
    
    return errors

# Log quality issues
for record in records:
    errors = validate_record(record)
    if errors:
        log_quality_issue(record, errors)
```

**Prevention:**
- Define clear data contracts
- Implement validation at source
- Set up data quality monitoring
- Regular data profiling

---

## Best Practices

### DO:
✅ Design for idempotency (reruns don't cause duplicates)
✅ Implement comprehensive error handling
✅ Use incremental loads when possible
✅ Add data quality checks before loading
✅ Monitor pipeline performance
✅ Log detailed execution metrics
✅ Version control pipeline code
✅ Document data lineage
✅ Test with production-like data
✅ Use orchestration tools (Airflow, Prefect)
✅ Implement proper retry logic
✅ Maintain execution history

### DON'T:
❌ Skip error handling
❌ Load without validation
❌ Hard-code credentials
❌ Ignore failed records silently
❌ Create tightly coupled components
❌ Skip documentation
❌ Ignore performance degradation
❌ Forget about data lineage
❌ Deploy without testing
❌ Skip monitoring setup
❌ Ignore data quality issues
❌ Create monolithic pipelines

---

## Related Workflows

**Prerequisites:**
- [database-migration-workflow.md](./database-migration-workflow.md) - Database setup

**Next Steps:**
- [pipeline_orchestration_airflow.md](./pipeline_orchestration_airflow.md) - Orchestration
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks

**Related:**
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture patterns
- [data_transformation_dbt.md](./data_transformation_dbt.md) - SQL transformations

---

## Tags
`data-engineering` `etl` `pipelines` `data-integration` `orchestration` `data-quality` `airflow` `python`
