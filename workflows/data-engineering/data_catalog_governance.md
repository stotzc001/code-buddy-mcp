# Data Catalog & Governance

**ID:** dat-002  
**Category:** Data Engineering  
**Priority:** MEDIUM  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement comprehensive data catalog and governance framework to manage metadata, ensure data quality, and maintain compliance

**Why:** Data governance ensures data discoverability, quality, security, and regulatory compliance while enabling self-service analytics and reducing data silos

**When to use:**
- Building enterprise data platforms
- Ensuring regulatory compliance (GDPR, HIPAA, SOC2)
- Improving data discoverability
- Managing data lineage
- Implementing data quality standards
- Enabling self-service analytics
- Tracking sensitive data
- Documenting data assets

---

## Prerequisites

**Required:**
- [ ] Data platform infrastructure
- [ ] Understanding of data governance principles
- [ ] Basic Python or SQL knowledge
- [ ] Access to data catalog tool (DataHub, Amundsen, Atlas, etc.)
- [ ] Understanding of metadata management

**Check before starting:**
```bash
# Check Docker (for local catalog setup)
docker --version

# Check Python
python --version  # Should be 3.8+

# Check network access to data sources
# (databases, data lakes, etc.)
```

---

## Implementation Steps

### Step 1: Choose and Set Up Data Catalog Platform

**What:** Select and deploy appropriate data catalog solution

**How:**

**Option 1: DataHub (Open Source, Recommended):**
```yaml
# docker-compose-datahub.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: datahub
      MYSQL_USER: datahub
      MYSQL_PASSWORD: datahub
      MYSQL_ROOT_PASSWORD: datahub
    volumes:
      - mysql-data:/var/lib/mysql
    ports:
      - "3306:3306"

  elasticsearch:
    image: elasticsearch:7.17.9
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  neo4j:
    image: neo4j:4.4.11
    environment:
      NEO4J_AUTH: neo4j/datahub
      NEO4J_dbms_default__database: graph.db
    volumes:
      - neo4j-data:/data
    ports:
      - "7474:7474"
      - "7687:7687"

  datahub-gms:
    image: linkedin/datahub-gms:v0.10.5
    depends_on:
      - mysql
      - elasticsearch
      - neo4j
    environment:
      DATAHUB_SERVER_TYPE: gms
      EBEAN_DATASOURCE_USERNAME: datahub
      EBEAN_DATASOURCE_PASSWORD: datahub
      EBEAN_DATASOURCE_URL: jdbc:mysql://mysql:3306/datahub?verifyServerCertificate=false&useSSL=true&useUnicode=yes&characterEncoding=UTF-8
      KAFKA_BOOTSTRAP_SERVER: kafka:9092
      ELASTICSEARCH_HOST: elasticsearch
      ELASTICSEARCH_PORT: 9200
      GRAPH_SERVICE_IMPL: neo4j
      NEO4J_HOST: neo4j:7687
      NEO4J_URI: bolt://neo4j
      NEO4J_USERNAME: neo4j
      NEO4J_PASSWORD: datahub
    ports:
      - "8080:8080"

  datahub-frontend:
    image: linkedin/datahub-frontend-react:v0.10.5
    depends_on:
      - datahub-gms
    environment:
      DATAHUB_GMS_HOST: datahub-gms
      DATAHUB_GMS_PORT: 8080
      DATAHUB_SECRET: YouNeedToChangeThis
    ports:
      - "9002:9002"

volumes:
  mysql-data:
  elasticsearch-data:
  neo4j-data:
```

```bash
# Start DataHub
docker-compose -f docker-compose-datahub.yml up -d

# Verify DataHub is running
curl http://localhost:9002/  # Frontend
curl http://localhost:8080/health  # Backend

# Access UI at http://localhost:9002
```

**Option 2: Amundsen (Lyft's open-source catalog):**
```bash
# Clone Amundsen
git clone https://github.com/amundsen-io/amundsen.git
cd amundsen

# Start with Docker Compose
docker-compose -f docker-amundsen.yml up -d

# Access at http://localhost:5000
```

**Option 3: Apache Atlas:**
```bash
# Pull Atlas image
docker pull apache/atlas:2.3.0

# Run Atlas
docker run -d \
  --name atlas \
  -p 21000:21000 \
  apache/atlas:2.3.0

# Access at http://localhost:21000 (admin/admin)
```

**Verification:**
- [ ] Catalog platform running
- [ ] UI accessible
- [ ] Backend services healthy
- [ ] Database connections working
- [ ] Search functionality available

**If This Fails:**
→ Check Docker resources
→ Verify port availability
→ Review service logs
→ Check network connectivity
→ Ensure sufficient memory

---

### Step 2: Ingest Metadata from Data Sources

**What:** Connect data sources and ingest metadata into the catalog

**How:**

**DataHub Ingestion Framework:**
```python
# ingestion_config.py
"""
Configure DataHub ingestion from various sources
"""

from datahub.ingestion.run.pipeline import Pipeline

# PostgreSQL ingestion
postgres_recipe = {
    "source": {
        "type": "postgres",
        "config": {
            "host_port": "localhost:5432",
            "database": "analytics",
            "username": "user",
            "password": "password",
            "include_tables": True,
            "include_views": True,
            "profiling": {
                "enabled": True,
                "profile_table_level_only": False,
            },
            "stateful_ingestion": {
                "enabled": True,
            }
        }
    },
    "sink": {
        "type": "datahub-rest",
        "config": {
            "server": "http://localhost:8080"
        }
    }
}

# Snowflake ingestion
snowflake_recipe = {
    "source": {
        "type": "snowflake",
        "config": {
            "account_id": "abc12345.us-east-1",
            "username": "user",
            "password": "password",
            "warehouse": "COMPUTE_WH",
            "role": "ACCOUNTADMIN",
            "database_pattern": {
                "allow": ["ANALYTICS", "DATA_WAREHOUSE"]
            },
            "schema_pattern": {
                "deny": [".*_TEMP$"]
            },
            "include_tables": True,
            "include_views": True,
            "include_table_lineage": True,
            "profiling": {
                "enabled": True,
                "profile_table_level_only": False
            }
        }
    },
    "sink": {
        "type": "datahub-rest",
        "config": {
            "server": "http://localhost:8080"
        }
    }
}

# S3/Data Lake ingestion
s3_recipe = {
    "source": {
        "type": "s3",
        "config": {
            "aws_access_key_id": "your-key",
            "aws_secret_access_key": "your-secret",
            "aws_region": "us-east-1",
            "path_specs": [
                {
                    "include": "s3://my-bucket/data/**/*.parquet",
                    "exclude": ["s3://my-bucket/data/temp/**"]
                }
            ],
            "profiling": {
                "enabled": True
            }
        }
    },
    "sink": {
        "type": "datahub-rest",
        "config": {
            "server": "http://localhost:8080"
        }
    }
}

# dbt ingestion (for lineage)
dbt_recipe = {
    "source": {
        "type": "dbt",
        "config": {
            "manifest_path": "./target/manifest.json",
            "catalog_path": "./target/catalog.json",
            "sources_path": "./target/sources.json",
            "target_platform": "snowflake",
            "load_schemas": True,
        }
    },
    "sink": {
        "type": "datahub-rest",
        "config": {
            "server": "http://localhost:8080"
        }
    }
}

def run_ingestion(recipe: dict, pipeline_name: str):
    """Run DataHub ingestion pipeline."""
    pipeline = Pipeline.create(recipe)
    pipeline.run()
    pipeline.pretty_print_summary()

# Run ingestions
run_ingestion(postgres_recipe, "postgres-ingestion")
run_ingestion(snowflake_recipe, "snowflake-ingestion")
run_ingestion(s3_recipe, "s3-ingestion")
run_ingestion(dbt_recipe, "dbt-ingestion")
```

**Schedule Ingestion:**
```yaml
# airflow_ingestion_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email': ['data-team@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def ingest_metadata(source: str):
    """Run DataHub ingestion for specified source."""
    cmd = f"datahub ingest -c /config/{source}_recipe.yml"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"Ingestion failed: {result.stderr}")

dag = DAG(
    'datahub_ingestion',
    default_args=default_args,
    description='Ingest metadata into DataHub',
    schedule_interval='0 */4 * * *',  # Every 4 hours
    catchup=False,
)

# Tasks
ingest_postgres = PythonOperator(
    task_id='ingest_postgres',
    python_callable=ingest_metadata,
    op_kwargs={'source': 'postgres'},
    dag=dag,
)

ingest_snowflake = PythonOperator(
    task_id='ingest_snowflake',
    python_callable=ingest_metadata,
    op_kwargs={'source': 'snowflake'},
    dag=dag,
)

ingest_s3 = PythonOperator(
    task_id='ingest_s3',
    python_callable=ingest_metadata,
    op_kwargs={'source': 's3'},
    dag=dag,
)

# Set dependencies
[ingest_postgres, ingest_snowflake, ingest_s3]
```

**Verification:**
- [ ] Data sources connected
- [ ] Metadata ingested
- [ ] Tables searchable
- [ ] Schemas visible
- [ ] Column details available

**If This Fails:**
→ Check credentials
→ Verify network access
→ Review ingestion logs
→ Test source connectivity
→ Check permissions

---

### Step 3: Implement Data Governance Policies

**What:** Define and enforce data governance policies including classification, ownership, and access control

**How:**

**Data Classification Framework:**
```python
# data_classification.py
"""
Data classification and tagging framework
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
import re

class DataSensitivity(Enum):
    """Data sensitivity levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class DataCategory(Enum):
    """Data categories for governance."""
    PII = "personally_identifiable_information"
    PHI = "protected_health_information"
    PCI = "payment_card_information"
    FINANCIAL = "financial"
    CUSTOMER = "customer_data"
    OPERATIONAL = "operational"

@dataclass
class ClassificationRule:
    """Rule for auto-classifying data."""
    name: str
    pattern: str
    sensitivity: DataSensitivity
    category: DataCategory
    requires_encryption: bool
    retention_days: int

# Define classification rules
CLASSIFICATION_RULES = [
    ClassificationRule(
        name="Social Security Number",
        pattern=r"ssn|social_security",
        sensitivity=DataSensitivity.RESTRICTED,
        category=DataCategory.PII,
        requires_encryption=True,
        retention_days=2555  # 7 years
    ),
    ClassificationRule(
        name="Email Address",
        pattern=r"email|e_mail",
        sensitivity=DataSensitivity.CONFIDENTIAL,
        category=DataCategory.PII,
        requires_encryption=False,
        retention_days=1825  # 5 years
    ),
    ClassificationRule(
        name="Credit Card",
        pattern=r"credit_card|cc_number|card_number",
        sensitivity=DataSensitivity.RESTRICTED,
        category=DataCategory.PCI,
        requires_encryption=True,
        retention_days=90
    ),
    ClassificationRule(
        name="Phone Number",
        pattern=r"phone|mobile|tel",
        sensitivity=DataSensitivity.CONFIDENTIAL,
        category=DataCategory.PII,
        requires_encryption=False,
        retention_days=1825
    ),
    ClassificationRule(
        name="Address",
        pattern=r"address|street|city|state|zip",
        sensitivity=DataSensitivity.CONFIDENTIAL,
        category=DataCategory.PII,
        requires_encryption=False,
        retention_days=1825
    ),
]

def classify_column(column_name: str, table_name: str = None) -> List[ClassificationRule]:
    """Auto-classify column based on name."""
    matches = []
    column_lower = column_name.lower()
    
    for rule in CLASSIFICATION_RULES:
        if re.search(rule.pattern, column_lower, re.IGNORECASE):
            matches.append(rule)
    
    return matches

def apply_classifications_datahub(
    dataset_urn: str,
    column_classifications: Dict[str, List[ClassificationRule]]
):
    """Apply classifications to DataHub."""
    from datahub.emitter.mce_builder import make_data_platform_urn, make_dataset_urn
    from datahub.emitter.mcp import MetadataChangeProposalWrapper
    from datahub.emitter.rest_emitter import DatahubRestEmitter
    from datahub.metadata.schema_classes import (
        DatasetPropertiesClass,
        GlobalTagsClass,
        TagAssociationClass,
    )
    
    emitter = DatahubRestEmitter("http://localhost:8080")
    
    # Apply column-level tags
    for column_name, rules in column_classifications.items():
        for rule in rules:
            # Create tag for sensitivity
            tag_urn = f"urn:li:tag:{rule.sensitivity.value}"
            
            # Apply tag
            tag_association = TagAssociationClass(tag=tag_urn)
            global_tags = GlobalTagsClass(tags=[tag_association])
            
            # Emit metadata
            mcp = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn,
                aspect=global_tags,
            )
            emitter.emit_mcp(mcp)
    
    print(f"✅ Applied classifications to {dataset_urn}")

# Example usage
column_classifications = {
    "customer_email": [classify_column("customer_email")[0]],
    "ssn": [classify_column("ssn")[0]],
    "credit_card_number": [classify_column("credit_card_number")[0]],
}

dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:postgres,analytics.customers,PROD)"
apply_classifications_datahub(dataset_urn, column_classifications)
```

**Data Ownership:**
```python
# data_ownership.py
"""
Assign and manage data ownership
"""

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    OwnershipClass,
    OwnerClass,
    OwnershipTypeClass,
)

def assign_owner(
    dataset_urn: str,
    owner_email: str,
    owner_type: str = "DATAOWNER"  # DATAOWNER, DEVELOPER, STAKEHOLDER
):
    """Assign owner to dataset."""
    
    emitter = DatahubRestEmitter("http://localhost:8080")
    
    # Create owner
    owner = OwnerClass(
        owner=f"urn:li:corpuser:{owner_email}",
        type=OwnershipTypeClass[owner_type],
    )
    
    # Create ownership
    ownership = OwnershipClass(
        owners=[owner],
        lastModified={"time": 0, "actor": "urn:li:corpuser:system"},
    )
    
    # Emit
    mcp = MetadataChangeProposalWrapper(
        entityUrn=dataset_urn,
        aspect=ownership,
    )
    emitter.emit_mcp(mcp)
    
    print(f"✅ Assigned {owner_email} as {owner_type} of {dataset_urn}")

# Assign owners
assign_owner(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customers,PROD)",
    "data-team@company.com",
    "DATAOWNER"
)

assign_owner(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)",
    "product-team@company.com",
    "STAKEHOLDER"
)
```

**Data Quality Rules:**
```python
# data_quality_rules.py
"""
Define data quality rules in governance framework
"""

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DatasetPropertiesClass

def document_quality_rules(dataset_urn: str, rules: dict):
    """Document data quality rules for dataset."""
    
    emitter = DatahubRestEmitter("http://localhost:8080")
    
    # Create custom properties with quality rules
    properties = DatasetPropertiesClass(
        customProperties={
            "quality_rules": str(rules),
            "freshness_sla": rules.get("freshness_sla", "24h"),
            "completeness_threshold": rules.get("completeness_threshold", "95%"),
            "uniqueness_check": rules.get("uniqueness_check", "true"),
        }
    )
    
    mcp = MetadataChangeProposalWrapper(
        entityUrn=dataset_urn,
        aspect=properties,
    )
    emitter.emit_mcp(mcp)
    
    print(f"✅ Documented quality rules for {dataset_urn}")

# Define quality rules
quality_rules = {
    "freshness_sla": "4h",
    "completeness_threshold": "99%",
    "uniqueness_check": True,
    "value_ranges": {
        "amount": {"min": 0, "max": 1000000},
        "quantity": {"min": 1, "max": 10000}
    },
    "required_columns": ["customer_id", "order_date", "amount"]
}

document_quality_rules(
    "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)",
    quality_rules
)
```

**Verification:**
- [ ] Classification rules defined
- [ ] Tags applied automatically
- [ ] Owners assigned
- [ ] Quality rules documented
- [ ] Policies enforced

**If This Fails:**
→ Review classification logic
→ Check tag definitions
→ Verify owner identities
→ Test policy enforcement
→ Review audit logs

---

### Step 4: Track Data Lineage

**What:** Implement end-to-end data lineage tracking

**How:**

**Automated Lineage from dbt:**
```python
# dbt_lineage.py
"""
Extract lineage from dbt and push to DataHub
"""

import json
from pathlib import Path

def extract_dbt_lineage(manifest_path: str = "target/manifest.json"):
    """Extract lineage from dbt manifest."""
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    lineage = []
    
    # Process each model
    for node_id, node in manifest["nodes"].items():
        if node["resource_type"] == "model":
            # Get upstream dependencies
            upstream = node.get("depends_on", {}).get("nodes", [])
            
            lineage.append({
                "downstream": node["unique_id"],
                "upstream": upstream,
                "transform": node.get("raw_sql", ""),
                "database": node["database"],
                "schema": node["schema"],
                "name": node["name"],
            })
    
    return lineage

# Push to DataHub
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    UpstreamLineageClass,
    UpstreamClass,
    DatasetLineageTypeClass,
)

def push_lineage_to_datahub(lineage_info: dict):
    """Push lineage to DataHub."""
    
    emitter = DatahubRestEmitter("http://localhost:8080")
    
    downstream_urn = make_dataset_urn(
        platform="snowflake",
        name=f"{lineage_info['database']}.{lineage_info['schema']}.{lineage_info['name']}",
    )
    
    upstreams = []
    for upstream_id in lineage_info["upstream"]:
        # Parse upstream identifier
        parts = upstream_id.split(".")
        if len(parts) >= 3:
            upstream_urn = make_dataset_urn(
                platform="snowflake",
                name=f"{parts[-3]}.{parts[-2]}.{parts[-1]}",
            )
            upstreams.append(
                UpstreamClass(
                    dataset=upstream_urn,
                    type=DatasetLineageTypeClass.TRANSFORMED,
                )
            )
    
    lineage = UpstreamLineageClass(upstreams=upstreams)
    
    mcp = MetadataChangeProposalWrapper(
        entityUrn=downstream_urn,
        aspect=lineage,
    )
    
    emitter.emit_mcp(mcp)
    print(f"✅ Pushed lineage for {downstream_urn}")

# Extract and push
lineage_data = extract_dbt_lineage()
for item in lineage_data:
    push_lineage_to_datahub(item)
```

**Manual Lineage Documentation:**
```python
# manual_lineage.py
"""
Document custom lineage relationships
"""

def document_lineage(
    source_urn: str,
    target_urn: str,
    transformation_type: str = "TRANSFORMED"
):
    """Manually document lineage between datasets."""
    
    from datahub.emitter.mcp import MetadataChangeProposalWrapper
    from datahub.emitter.rest_emitter import DatahubRestEmitter
    from datahub.metadata.schema_classes import (
        UpstreamLineageClass,
        UpstreamClass,
        DatasetLineageTypeClass,
    )
    
    emitter = DatahubRestEmitter("http://localhost:8080")
    
    upstream = UpstreamClass(
        dataset=source_urn,
        type=DatasetLineageTypeClass[transformation_type],
    )
    
    lineage = UpstreamLineageClass(upstreams=[upstream])
    
    mcp = MetadataChangeProposalWrapper(
        entityUrn=target_urn,
        aspect=lineage,
    )
    
    emitter.emit_mcp(mcp)
    print(f"✅ Documented lineage: {source_urn} -> {target_urn}")

# Example: Document Spark job lineage
document_lineage(
    source_urn="urn:li:dataset:(urn:li:dataPlatform:s3,raw-data/orders,PROD)",
    target_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.orders,PROD)",
    transformation_type="TRANSFORMED"
)
```

**Verification:**
- [ ] Lineage tracked
- [ ] Dependencies visible
- [ ] Impact analysis possible
- [ ] Transformations documented
- [ ] End-to-end trace available

**If This Fails:**
→ Check dbt manifest
→ Verify URN formats
→ Review transformation logic
→ Test impact analysis
→ Check visualization

---

### Step 5: Implement Search and Discovery

**What:** Enable self-service data discovery through search

**How:**

**Enhanced Metadata:**
```python
# enhanced_metadata.py
"""
Add rich metadata for better discoverability
"""

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    EditableDatasetPropertiesClass,
    GlobalTagsClass,
    GlossaryTermsClass,
)

def enrich_dataset_metadata(
    dataset_urn: str,
    description: str,
    tags: list,
    glossary_terms: list,
    custom_properties: dict
):
    """Add rich metadata to dataset."""
    
    emitter = DatahubRestEmitter("http://localhost:8080")
    
    # Add description
    editable_props = EditableDatasetPropertiesClass(
        description=description,
    )
    
    mcp = MetadataChangeProposalWrapper(
        entityUrn=dataset_urn,
        aspect=editable_props,
    )
    emitter.emit_mcp(mcp)
    
    # Add tags
    from datahub.metadata.schema_classes import TagAssociationClass
    tag_associations = [
        TagAssociationClass(tag=f"urn:li:tag:{tag}")
        for tag in tags
    ]
    global_tags = GlobalTagsClass(tags=tag_associations)
    
    mcp = MetadataChangeProposalWrapper(
        entityUrn=dataset_urn,
        aspect=global_tags,
    )
    emitter.emit_mcp(mcp)
    
    # Add custom properties
    properties = DatasetPropertiesClass(
        customProperties=custom_properties,
    )
    
    mcp = MetadataChangeProposalWrapper(
        entityUrn=dataset_urn,
        aspect=properties,
    )
    emitter.emit_mcp(mcp)
    
    print(f"✅ Enriched metadata for {dataset_urn}")

# Example
enrich_dataset_metadata(
    dataset_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customers,PROD)",
    description="Customer master data including demographics, contact information, and segmentation. Updated daily at 2 AM UTC. Source: CRM system.",
    tags=["customer-data", "daily-refresh", "pii"],
    glossary_terms=["Customer", "PII"],
    custom_properties={
        "update_frequency": "daily",
        "data_owner": "customer-team@company.com",
        "sla": "99.9%",
        "retention_period": "7 years",
        "source_system": "Salesforce CRM",
    }
)
```

**Verification:**
- [ ] Search working
- [ ] Metadata comprehensive
- [ ] Tags searchable
- [ ] Discovery intuitive
- [ ] Users can find data

**If This Fails:**
→ Check search index
→ Verify metadata quality
→ Review tag taxonomy
→ Test search queries
→ Gather user feedback

---

## Verification Checklist

After completing this workflow:

- [ ] Catalog platform deployed
- [ ] Metadata ingested
- [ ] Classifications applied
- [ ] Owners assigned
- [ ] Lineage tracked
- [ ] Search functional
- [ ] Policies enforced
- [ ] Documentation complete
- [ ] Users trained
- [ ] Monitoring configured

---

## Common Issues & Solutions

### Issue: Slow Metadata Ingestion

**Symptoms:**
- Ingestion takes hours
- Timeouts occurring
- Catalog not up-to-date

**Solution:**
- Increase parallelism
- Filter unnecessary tables
- Use incremental ingestion
- Optimize source queries
- Scale catalog infrastructure

---

## Best Practices

### DO:
✅ Automate metadata ingestion
✅ Classify data consistently
✅ Assign clear ownership
✅ Track lineage end-to-end
✅ Document transformations
✅ Enable self-service discovery
✅ Enforce governance policies
✅ Monitor catalog usage
✅ Keep metadata up-to-date
✅ Train users on catalog
✅ Integrate with CI/CD
✅ Version governance rules

### DON'T:
❌ Manual metadata entry only
❌ Skip data classification
❌ Ignore ownership
❌ Forget lineage tracking
❌ Over-complicate taxonomy
❌ Restrict access unnecessarily
❌ Skip user training
❌ Ignore data quality
❌ Create stale metadata
❌ Forget about scale
❌ Skip monitoring
❌ Ignore user feedback

---

## Related Workflows

**Prerequisites:**
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture

**Next Steps:**
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks
- [data_transformation_dbt.md](./data_transformation_dbt.md) - Transformations

**Related:**
- [data_lake_architecture.md](./data_lake_architecture.md) - Data lakes
- [data_warehousing_modeling.md](./data_warehousing_modeling.md) - Warehousing

---

## Tags
`data-engineering` `data-catalog` `governance` `metadata` `datahub` `amundsen` `lineage` `compliance` `discovery`
