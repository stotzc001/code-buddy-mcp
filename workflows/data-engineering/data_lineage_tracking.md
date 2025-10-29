# Data Lineage Tracking

**ID:** dat-023  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Advanced  
**Estimated Time:** 4-8 hours (initial setup), ongoing maintenance  
**Prerequisites:** Understanding of data pipelines, metadata management  

---

## Overview

Data lineage tracks the flow and transformation of data from source to destination. This workflow helps you implement and maintain data lineage to understand data origins, transformations, dependencies, and impact analysis.

**When to Use:**
- Debugging data quality issues
- Impact analysis before schema changes
- Regulatory compliance (GDPR, SOX, HIPAA)
- Understanding data dependencies
- Root cause analysis for data incidents
- Documenting data transformations

**Benefits:**
- Quick troubleshooting of data issues
- Confidence in data accuracy
- Compliance with regulations
- Better collaboration across teams
- Impact analysis for changes

---

## Quick Start

```python
# 1. Install lineage tracking library
pip install openlineage-python

# 2. Instrument your pipeline
from openlineage.client import OpenLineageClient

client = OpenLineageClient(url="http://marquez:5000")

# 3. Track data flow
client.emit_run_event({
    "eventType": "START",
    "inputs": [{"namespace": "postgres", "name": "raw_orders"}],
    "outputs": [{"namespace": "warehouse", "name": "processed_orders"}]
})

# 4. Visualize lineage in UI
# Access Marquez UI at http://localhost:3000
```

---

## Step-by-Step Guide

### Phase 1: Choose Lineage Solution (1-2 hours)

**Solution Options:**

```markdown
## Open Source Options

**1. Apache Atlas**
- Comprehensive metadata management
- Good Hadoop ecosystem integration
- Complex setup and maintenance

**2. Marquez (OpenLineage)**
- Modern, simple to use
- Good API support
- Active community
- Recommended for most use cases

**3. DataHub (LinkedIn)**
- Great UI and search
- Good for data discovery
- Requires more resources

**4. Amundsen (Lyft)**
- Focus on data discovery
- Good for catalog + lineage
- Moderate complexity

## Commercial Options

**1. Collibra**
- Enterprise data governance
- Comprehensive features
- High cost

**2. Alation**
- Data catalog focused
- Good collaboration features
- Mid-tier pricing

**3. Select Star**
- Automated lineage
- Low maintenance
- Good for small/mid teams
```

**Recommendation: Marquez (OpenLineage) for most teams**

---

### Phase 2: Set Up Lineage Backend (2-3 hours)

**Install Marquez:**

```yaml
# docker-compose.yml
version: "3.7"
services:
  marquez-api:
    image: marquezproject/marquez:latest
    ports:
      - "5000:5000"
      - "5001:5001"
    environment:
      - MARQUEZ_PORT=5000
      - MARQUEZ_ADMIN_PORT=5001
    depends_on:
      - marquez-db

  marquez-web:
    image: marquezproject/marquez-web:latest
    ports:
      - "3000:3000"
    environment:
      - MARQUEZ_HOST=marquez-api
      - MARQUEZ_PORT=5000

  marquez-db:
    image: postgres:12
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=marquez
      - POSTGRES_PASSWORD=marquez
      - POSTGRES_DB=marquez
    volumes:
      - marquez-db-data:/var/lib/postgresql/data

volumes:
  marquez-db-data:
```

```bash
# Start services
docker-compose up -d

# Verify installation
curl http://localhost:5000/api/v1/namespaces

# Access web UI
open http://localhost:3000
```

---

### Phase 3: Instrument Data Pipelines (2-4 hours)

**Basic Python Pipeline Instrumentation:**

```python
# pipeline/etl_orders.py
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run, Job
from openlineage.client.facet import (
    SqlJobFacet,
    SourceCodeLocationJobFacet
)
from datetime import datetime
import uuid

# Initialize client
client = OpenLineageClient(
    url="http://localhost:5000",
    api_key="your-api-key"  # Optional
)

def emit_lineage_event(
    event_type: str,
    job_name: str,
    inputs: list,
    outputs: list,
    sql: str = None,
    run_id: str = None
):
    """Emit lineage event to OpenLineage."""
    
    run_id = run_id or str(uuid.uuid4())
    
    event = RunEvent(
        eventType=event_type,
        eventTime=datetime.utcnow().isoformat(),
        run=Run(runId=run_id),
        job=Job(
            namespace="etl_pipeline",
            name=job_name,
            facets={
                "sql": SqlJobFacet(query=sql) if sql else {},
                "sourceCodeLocation": SourceCodeLocationJobFacet(
                    type="git",
                    url="https://github.com/org/repo",
                    path="pipeline/etl_orders.py"
                )
            }
        ),
        inputs=inputs,
        outputs=outputs
    )
    
    client.emit(event)
    return run_id

# Example ETL pipeline
def process_orders():
    """Process orders from raw to analytics."""
    
    run_id = str(uuid.uuid4())
    
    # 1. Emit START event
    emit_lineage_event(
        event_type="START",
        job_name="process_orders",
        run_id=run_id,
        inputs=[
            {
                "namespace": "postgres://prod-db",
                "name": "raw.orders",
                "facets": {
                    "schema": {
                        "fields": [
                            {"name": "order_id", "type": "int"},
                            {"name": "customer_id", "type": "int"},
                            {"name": "total", "type": "decimal"},
                            {"name": "created_at", "type": "timestamp"}
                        ]
                    }
                }
            }
        ],
        outputs=[
            {
                "namespace": "snowflake://warehouse",
                "name": "analytics.orders_daily",
                "facets": {
                    "schema": {
                        "fields": [
                            {"name": "date", "type": "date"},
                            {"name": "total_orders", "type": "int"},
                            {"name": "revenue", "type": "decimal"}
                        ]
                    }
                }
            }
        ],
        sql="""
        INSERT INTO analytics.orders_daily
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as total_orders,
            SUM(total) as revenue
        FROM raw.orders
        WHERE created_at >= CURRENT_DATE - 1
        GROUP BY DATE(created_at)
        """
    )
    
    try:
        # Perform actual ETL work
        result = execute_etl()
        
        # 2. Emit COMPLETE event
        emit_lineage_event(
            event_type="COMPLETE",
            job_name="process_orders",
            run_id=run_id,
            inputs=[...],  # Same as above
            outputs=[...]  # Same as above
        )
        
    except Exception as e:
        # 3. Emit FAIL event on error
        emit_lineage_event(
            event_type="FAIL",
            job_name="process_orders",
            run_id=run_id,
            inputs=[...],
            outputs=[...]
        )
        raise
```

**dbt Integration:**

```yaml
# dbt_project.yml
models:
  my_project:
    +meta:
      owner: data-team
      
# models/orders_daily.sql
{{
    config(
        materialized='incremental',
        unique_key='date'
    )
}}

-- dbt automatically tracks lineage via ref() and source()
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_orders,
    SUM(total) as revenue
FROM {{ source('raw', 'orders') }}
WHERE created_at >= CURRENT_DATE - 1
GROUP BY DATE(created_at)

# dbt sends lineage to OpenLineage automatically
# when configured with openlineage adapter
```

**Airflow Integration:**

```python
# dags/orders_etl_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from openlineage.airflow import OpenLineagePlugin
from datetime import datetime

# Airflow OpenLineage plugin automatically tracks:
# - DAG structure
# - Task dependencies
# - Data sources and targets
# - Execution metadata

with DAG(
    'orders_etl',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    extract_orders = PythonOperator(
        task_id='extract_orders',
        python_callable=extract_orders_func,
        # Plugin automatically captures lineage
        op_kwargs={
            'source': 'postgres://prod/raw.orders',
            'target': 's3://bucket/staging/orders/'
        }
    )
    
    transform_orders = PythonOperator(
        task_id='transform_orders',
        python_callable=transform_orders_func,
        op_kwargs={
            'source': 's3://bucket/staging/orders/',
            'target': 'snowflake://warehouse/analytics.orders_daily'
        }
    )
    
    extract_orders >> transform_orders
```

---

### Phase 4: Query and Visualize Lineage (ongoing)

**REST API Queries:**

```bash
# Get lineage for a dataset
curl http://localhost:5000/api/v1/lineage \
  ?nodeId=dataset:snowflake://warehouse:analytics.orders_daily

# Response shows upstream and downstream dependencies

# Get dataset details
curl http://localhost:5000/api/v1/namespaces/snowflake://warehouse/datasets/analytics.orders_daily

# List all jobs
curl http://localhost:5000/api/v1/namespaces/etl_pipeline/jobs

# Get job runs
curl http://localhost:5000/api/v1/namespaces/etl_pipeline/jobs/process_orders/runs
```

**Python API Queries:**

```python
from openlineage.client import OpenLineageClient

client = OpenLineageClient(url="http://localhost:5000")

def get_upstream_datasets(dataset_name: str, namespace: str):
    """Get all upstream datasets for a given dataset."""
    
    lineage = client.get_lineage(
        node_id=f"dataset:{namespace}:{dataset_name}",
        depth=10  # How many levels to traverse
    )
    
    upstream = []
    for node in lineage.graph:
        if node.type == "DATASET" and node.id != dataset_name:
            upstream.append({
                "name": node.data.name,
                "namespace": node.data.namespace,
                "job": node.inEdges[0].origin.name  # Job that created it
            })
    
    return upstream

# Example usage
upstream = get_upstream_datasets(
    dataset_name="analytics.orders_daily",
    namespace="snowflake://warehouse"
)

for dataset in upstream:
    print(f"{dataset['name']} (via {dataset['job']})")
```

**Impact Analysis:**

```python
def analyze_impact(dataset_name: str, namespace: str):
    """Find all downstream datasets affected by changes."""
    
    lineage = client.get_lineage(
        node_id=f"dataset:{namespace}:{dataset_name}",
        depth=10
    )
    
    downstream = []
    for node in lineage.graph:
        if node.type == "DATASET" and node.id != dataset_name:
            if any(edge.origin.id == dataset_name for edge in node.inEdges):
                downstream.append({
                    "name": node.data.name,
                    "namespace": node.data.namespace,
                    "jobs_affected": [
                        edge.origin.name 
                        for edge in node.inEdges
                    ]
                })
    
    return downstream

# Check impact before making changes
print("Changing raw.orders schema will affect:")
impact = analyze_impact("raw.orders", "postgres://prod")
for item in impact:
    print(f"  - {item['name']} (via {', '.join(item['jobs_affected'])})")
```

---

## Best Practices

### DO:
✅ **Track at appropriate granularity** - Table/dataset level, not row level  
✅ **Include transformation logic** - Store SQL queries, code references  
✅ **Automate collection** - Instrument pipelines, don't manual log  
✅ **Version your schemas** - Track schema evolution over time  
✅ **Document data quality** - Link quality checks to lineage  
✅ **Use consistent naming** - Standard namespace and dataset names  

### DON'T:
❌ **Track every column** - Too granular, hard to maintain  
❌ **Ignore failed runs** - Track failures for debugging  
❌ **Skip temporary datasets** - Include staging/intermediate data  
❌ **Forget data quality** - Lineage without quality is incomplete  
❌ **Make it optional** - Lineage should be part of pipeline code  

---

## Common Patterns

### Column-Level Lineage

```python
# Track column-level transformations
from openlineage.client.facet import ColumnLineageDatasetFacet

output_facets = {
    "columnLineage": ColumnLineageDatasetFacet(
        fields={
            "revenue": {
                "inputFields": [
                    {
                        "namespace": "postgres://prod",
                        "name": "raw.orders",
                        "field": "total"
                    }
                ],
                "transformationType": "AGGREGATION",
                "transformationDescription": "SUM(total)"
            },
            "total_orders": {
                "inputFields": [
                    {
                        "namespace": "postgres://prod",
                        "name": "raw.orders",
                        "field": "order_id"
                    }
                ],
                "transformationType": "AGGREGATION",
                "transformationDescription": "COUNT(*)"
            }
        }
    )
}
```

### Multi-Hop Lineage

```python
# Track data flowing through multiple transformations
# raw.orders → staging.orders_cleaned → analytics.orders_daily

# Job 1: Raw to Staging
emit_lineage_event(
    job_name="clean_orders",
    inputs=[{"namespace": "postgres", "name": "raw.orders"}],
    outputs=[{"namespace": "s3", "name": "staging.orders_cleaned"}]
)

# Job 2: Staging to Analytics  
emit_lineage_event(
    job_name="aggregate_orders",
    inputs=[{"namespace": "s3", "name": "staging.orders_cleaned"}],
    outputs=[{"namespace": "snowflake", "name": "analytics.orders_daily"}]
)

# Lineage graph automatically connects these hops
```

---

## Troubleshooting

### Issue: Lineage Not Appearing in UI

**Symptoms:**
- Events emitted but not visible
- Datasets missing from graph
- Jobs not showing connections

**Solution:**
```bash
# Check if events are reaching backend
curl http://localhost:5000/api/v1/events | jq .

# Check Marquez logs
docker logs marquez-api

# Verify namespace exists
curl http://localhost:5000/api/v1/namespaces

# Check dataset registration
curl http://localhost:5000/api/v1/namespaces/{namespace}/datasets

# Common issues:
# 1. Incorrect namespace format
# 2. Missing schema in dataset definition
# 3. Events emitted but job/dataset not registered first
```

---

## Related Workflows

**Prerequisites:**
- [[dat-006]] Data Pipeline Architecture - Understanding pipelines
- [[dat-007]] Data Quality Validation - Data quality checks

**Next Steps:**
- [[dat-003]] Data Catalog Governance - Data discovery and governance
- [[dat-010]] ETL Pipeline Design - Building maintainable pipelines

---

## Tags

`data-engineering` `lineage` `metadata` `governance` `compliance` `observability` `data-quality` `impact-analysis`
