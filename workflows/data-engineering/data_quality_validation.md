# Data Quality Validation

**ID:** dat-005  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement comprehensive data quality validation frameworks to ensure data accuracy, completeness, consistency, and reliability across pipelines

**Why:** Data quality issues cost organizations millions in bad decisions, lost productivity, and customer trust. Automated validation catches issues early and maintains data trust

**When to use:**
- Building data pipelines
- Migrating data systems
- Implementing data governance
- Setting up monitoring for production data
- Establishing data SLAs
- Creating data quality dashboards

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ installed
- [ ] Access to data sources
- [ ] Understanding of data profiling
- [ ] SQL knowledge
- [ ] Data quality framework (Great Expectations, Soda, dbt tests)

**Check before starting:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check data quality tools
pip list | grep great-expectations
pip list | grep soda-core
dbt --version

# Verify database access
psql -h database.example.com -U user -c "SELECT 1;"
```

---

## Implementation Steps

### Step 1: Choose Data Quality Framework

**What:** Select appropriate data quality validation framework

**How:**

**Framework Comparison:**
```python
"""
Data Quality Framework Selection Guide
"""

from dataclasses import dataclass
from typing import List, Literal

@dataclass
class ProjectRequirements:
    """Define project requirements."""
    team_technical_level: Literal["low", "medium", "high"]
    existing_stack: List[str]  # ["dbt", "airflow", "spark"]
    validation_complexity: Literal["simple", "moderate", "complex"]
    integration_needs: List[str]  # ["slack", "email", "pagerduty"]
    budget: Literal["low", "medium", "high"]

def recommend_framework(reqs: ProjectRequirements) -> str:
    """Recommend data quality framework."""
    
    # Already using dbt? Use dbt tests
    if "dbt" in reqs.existing_stack:
        return "dbt tests (native)"
    
    # Need complex statistical validation?
    if reqs.validation_complexity == "complex":
        return "Great Expectations (comprehensive, powerful)"
    
    # Simple SQL-based checks?
    if reqs.validation_complexity == "simple":
        return "Soda Core (SQL-based, easy to learn)"
    
    # Python-heavy team with custom needs?
    if reqs.team_technical_level == "high":
        return "Custom validation with pandas + pytest"
    
    return "Great Expectations (good all-around choice)"

# Example
reqs = ProjectRequirements(
    team_technical_level="medium",
    existing_stack=["airflow", "postgres"],
    validation_complexity="moderate",
    integration_needs=["slack", "email"],
    budget="medium"
)

print(recommend_framework(reqs))
# Output: Great Expectations (good all-around choice)
```

**Installation:**
```bash
# Option 1: Great Expectations
pip install great-expectations

# Option 2: Soda Core
pip install soda-core-postgres
# or
pip install soda-core-snowflake

# Option 3: dbt (for dbt projects)
pip install dbt-postgres

# Option 4: Custom with pandas
pip install pandas pytest pandera
```

**Verification:**
- [ ] Framework selected
- [ ] Tool installed
- [ ] Team aligned on choice
- [ ] Integration requirements met

**If This Fails:**
→ Review team skills
→ Consider starting with simpler tools
→ Pilot multiple frameworks
→ Evaluate based on actual use cases

---

### Step 2: Profile Data and Define Quality Rules

**What:** Understand data characteristics and define quality expectations

**How:**

**Data Profiling with pandas:**
```python
"""
Profile data to understand quality baseline
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive data profile."""
    
    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": {}
    }
    
    for col in df.columns:
        col_profile = {
            "dtype": str(df[col].dtype),
            "null_count": df[col].isnull().sum(),
            "null_percentage": (df[col].isnull().sum() / len(df)) * 100,
            "unique_count": df[col].nunique(),
            "unique_percentage": (df[col].nunique() / len(df)) * 100,
        }
        
        # Numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            col_profile.update({
                "min": df[col].min(),
                "max": df[col].max(),
                "mean": df[col].mean(),
                "median": df[col].median(),
                "std": df[col].std(),
            })
        
        # String columns
        elif pd.api.types.is_string_dtype(df[col]):
            col_profile.update({
                "min_length": df[col].str.len().min(),
                "max_length": df[col].str.len().max(),
                "avg_length": df[col].str.len().mean(),
            })
        
        # Date columns
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_profile.update({
                "min_date": df[col].min(),
                "max_date": df[col].max(),
            })
        
        profile["columns"][col] = col_profile
    
    return profile

# Usage
df = pd.read_sql("SELECT * FROM customers LIMIT 10000", connection)
profile = profile_dataframe(df)

print(f"Total rows: {profile['row_count']}")
for col, stats in profile['columns'].items():
    print(f"\n{col}:")
    print(f"  Null %: {stats['null_percentage']:.2f}%")
    print(f"  Unique values: {stats['unique_count']}")
```

**Define Quality Rules:**
```yaml
# data_quality_rules.yml

# Rules for customers table
customers:
  # Completeness rules
  completeness:
    - column: customer_id
      expectation: no_nulls
      severity: error
    
    - column: email
      expectation: null_percentage_less_than
      threshold: 5
      severity: warning
    
    - column: created_at
      expectation: no_nulls
      severity: error
  
  # Validity rules
  validity:
    - column: email
      expectation: matches_regex
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      severity: error
    
    - column: age
      expectation: between
      min_value: 18
      max_value: 120
      severity: error
    
    - column: country_code
      expectation: in_set
      values: ["US", "UK", "CA", "AU", "DE", "FR"]
      severity: error
  
  # Uniqueness rules
  uniqueness:
    - column: customer_id
      expectation: unique
      severity: error
    
    - column: email
      expectation: unique
      severity: error
  
  # Consistency rules
  consistency:
    - name: order_dates_logical
      expectation: column_a_greater_than_column_b
      column_a: updated_at
      column_b: created_at
      severity: error
  
  # Timeliness rules
  timeliness:
    - column: created_at
      expectation: not_in_future
      severity: error
    
    - column: updated_at
      expectation: freshness_within_hours
      hours: 24
      severity: warning

# Rules for orders table
orders:
  completeness:
    - column: order_id
      expectation: no_nulls
      severity: error
    
    - column: customer_id
      expectation: no_nulls
      severity: error
  
  validity:
    - column: total_amount
      expectation: greater_than
      value: 0
      severity: error
    
    - column: order_status
      expectation: in_set
      values: ["pending", "confirmed", "shipped", "delivered", "cancelled"]
      severity: error
  
  referential_integrity:
    - column: customer_id
      expectation: foreign_key_exists
      references_table: customers
      references_column: customer_id
      severity: error
```

**Verification:**
- [ ] Data profiled
- [ ] Quality dimensions identified
- [ ] Rules documented
- [ ] Severity levels assigned
- [ ] Stakeholders aligned

**If This Fails:**
→ Start with smaller sample
→ Focus on critical columns first
→ Interview data producers/consumers
→ Review existing documentation

---

### Step 3: Implement Validation with Great Expectations

**What:** Set up Great Expectations for comprehensive data validation

**How:**

**Initialize Great Expectations:**
```bash
# Create Great Expectations project
great_expectations init

# Project structure created:
# great_expectations/
# ├── great_expectations.yml        # Project config
# ├── expectations/                 # Expectation suites
# ├── checkpoints/                  # Validation checkpoints
# ├── plugins/                      # Custom expectations
# └── uncommitted/                  # Local artifacts
```

**Configure Data Source:**
```python
# create_datasource.py
"""
Configure data source for Great Expectations
"""

import great_expectations as gx

# Initialize context
context = gx.get_context()

# Add PostgreSQL datasource
datasource_config = {
    "name": "my_postgres_db",
    "class_name": "Datasource",
    "execution_engine": {
        "class_name": "SqlAlchemyExecutionEngine",
        "connection_string": "postgresql://user:password@host:5432/database",
    },
    "data_connectors": {
        "default_runtime_data_connector": {
            "class_name": "RuntimeDataConnector",
            "batch_identifiers": ["default_identifier_name"],
        },
        "default_inferred_data_connector": {
            "class_name": "InferredAssetSqlDataConnector",
            "include_schema_name": True,
        },
    },
}

context.add_datasource(**datasource_config)

# Or add a pandas datasource
pandas_datasource_config = {
    "name": "pandas_datasource",
    "class_name": "Datasource",
    "execution_engine": {
        "class_name": "PandasExecutionEngine",
    },
    "data_connectors": {
        "default_runtime_data_connector": {
            "class_name": "RuntimeDataConnector",
            "batch_identifiers": ["default_identifier_name"],
        },
    },
}

context.add_datasource(**pandas_datasource_config)
```

**Create Expectation Suite:**
```python
# create_expectations.py
"""
Define expectations for customers table
"""

import great_expectations as gx

context = gx.get_context()

# Create expectation suite
suite = context.add_expectation_suite("customers_suite")

# Get batch
batch_request = {
    "datasource_name": "my_postgres_db",
    "data_connector_name": "default_inferred_data_connector",
    "data_asset_name": "public.customers",
}

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="customers_suite"
)

# Add expectations

# 1. Table-level expectations
validator.expect_table_row_count_to_be_between(min_value=1000, max_value=10000000)
validator.expect_table_column_count_to_equal(value=15)

# 2. Column existence
validator.expect_table_columns_to_match_ordered_list([
    "customer_id", "email", "first_name", "last_name",
    "phone", "country", "created_at", "updated_at"
])

# 3. Nulls and completeness
validator.expect_column_values_to_not_be_null("customer_id")
validator.expect_column_values_to_not_be_null("email")
validator.expect_column_values_to_be_null("phone", mostly=0.2)  # Allow 20% nulls

# 4. Uniqueness
validator.expect_column_values_to_be_unique("customer_id")
validator.expect_column_values_to_be_unique("email")

# 5. Data types
validator.expect_column_values_to_be_of_type("customer_id", "INTEGER")
validator.expect_column_values_to_be_of_type("email", "TEXT")
validator.expect_column_values_to_be_of_type("created_at", "TIMESTAMP")

# 6. Value ranges
validator.expect_column_min_to_be_between("customer_id", min_value=1)
validator.expect_column_values_to_be_between(
    "created_at",
    min_value="2020-01-01",
    max_value="2030-12-31"
)

# 7. Regex patterns
validator.expect_column_values_to_match_regex(
    "email",
    regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

# 8. Set membership
validator.expect_column_values_to_be_in_set(
    "country",
    value_set=["US", "UK", "CA", "AU", "DE", "FR", "JP", "CN"]
)

# 9. Column pair comparisons
validator.expect_column_pair_values_A_to_be_greater_than_B(
    column_A="updated_at",
    column_B="created_at",
    or_equal=True
)

# 10. Custom SQL expectations
validator.expect_column_values_to_be_in_set(
    "customer_id",
    value_set=validator.execution_engine.execute_query(
        "SELECT DISTINCT customer_id FROM orders"
    )
)

# Save suite
validator.save_expectation_suite(discard_failed_expectations=False)
```

**Create Checkpoint:**
```python
# create_checkpoint.py
"""
Create checkpoint for automated validation
"""

import great_expectations as gx

context = gx.get_context()

checkpoint_config = {
    "name": "customers_checkpoint",
    "config_version": 1.0,
    "class_name": "SimpleCheckpoint",
    "validations": [
        {
            "batch_request": {
                "datasource_name": "my_postgres_db",
                "data_connector_name": "default_inferred_data_connector",
                "data_asset_name": "public.customers",
            },
            "expectation_suite_name": "customers_suite",
        }
    ],
    "action_list": [
        {
            "name": "store_validation_result",
            "action": {"class_name": "StoreValidationResultAction"},
        },
        {
            "name": "update_data_docs",
            "action": {"class_name": "UpdateDataDocsAction"},
        },
        {
            "name": "send_slack_notification",
            "action": {
                "class_name": "SlackNotificationAction",
                "slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                "notify_on": "failure",
                "notify_with": [
                    "DataDocsLink",
                ],
            },
        },
    ],
}

context.add_checkpoint(**checkpoint_config)

# Run checkpoint
result = context.run_checkpoint(checkpoint_name="customers_checkpoint")

if not result["success"]:
    print("Validation FAILED!")
    for validation_result in result["run_results"].values():
        print(f"  {validation_result['validation_result']['statistics']}")
else:
    print("Validation PASSED!")
```

**Verification:**
- [ ] Great Expectations initialized
- [ ] Data source configured
- [ ] Expectation suite created
- [ ] Checkpoint configured
- [ ] Validation runs successfully

**If This Fails:**
→ Check database connectivity
→ Verify permissions
→ Review expectation syntax
→ Check Great Expectations logs
→ Start with simpler expectations

---

### Step 4: Implement Validation with Soda Core

**What:** Set up Soda Core for SQL-based data quality checks

**How:**

**Initialize Soda:**
```bash
# Create configuration directory
mkdir soda_checks
cd soda_checks
```

**Configure Connection (configuration.yml):**
```yaml
# configuration.yml
data_source postgres_warehouse:
  type: postgres
  host: database.example.com
  port: 5432
  username: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
  database: analytics
  schema: public

# Or for Snowflake
data_source snowflake_warehouse:
  type: snowflake
  account: my_account.us-east-1
  user: ${SNOWFLAKE_USER}
  password: ${SNOWFLAKE_PASSWORD}
  database: ANALYTICS
  warehouse: COMPUTE_WH
  schema: PUBLIC
  role: TRANSFORMER
```

**Define Checks (checks.yml):**
```yaml
# checks/customers.yml
checks for customers:
  # Table-level checks
  - row_count > 0
  - row_count between 1000 and 10000000
  
  # Completeness checks
  - missing_count(customer_id) = 0:
      name: Customer ID should never be null
  
  - missing_count(email) = 0:
      name: Email should never be null
  
  - missing_percent(phone) < 20:
      name: Phone can be missing but not more than 20%
  
  # Validity checks
  - invalid_count(email) = 0:
      valid format: email
      name: All emails should be valid
  
  - invalid_count(country) = 0:
      valid values: ['US', 'UK', 'CA', 'AU', 'DE', 'FR']
      name: Country should be from approved list
  
  # Uniqueness checks
  - duplicate_count(customer_id) = 0:
      name: Customer ID should be unique
  
  - duplicate_count(email) = 0:
      name: Email should be unique
  
  # Freshness checks
  - freshness(updated_at) < 1d:
      name: Data should be updated daily
  
  # Custom SQL checks
  - failed rows:
      name: Created date should not be in future
      fail query: |
        SELECT customer_id, created_at
        FROM customers
        WHERE created_at > CURRENT_DATE
  
  - failed rows:
      name: Updated date should be after created date
      fail query: |
        SELECT customer_id, created_at, updated_at
        FROM customers
        WHERE updated_at < created_at
  
  # Numeric checks
  - avg(lifetime_value) > 100:
      name: Average customer lifetime value should be healthy
  
  - min(lifetime_value) >= 0:
      name: Lifetime value cannot be negative
  
  # Schema checks
  - schema:
      name: Verify expected schema
      fail when required column missing: [customer_id, email, created_at]
      fail when wrong column type:
        customer_id: integer
        email: varchar
        created_at: timestamp

# checks/orders.yml
checks for orders:
  - row_count > 0
  
  - missing_count(order_id) = 0
  - missing_count(customer_id) = 0
  - missing_count(total_amount) = 0
  
  - duplicate_count(order_id) = 0
  
  - invalid_count(order_status) = 0:
      valid values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
  
  - min(total_amount) >= 0:
      name: Order amount cannot be negative
  
  # Referential integrity
  - failed rows:
      name: All orders must have valid customer
      fail query: |
        SELECT o.order_id, o.customer_id
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
  
  # Business rules
  - failed rows:
      name: Shipped orders must have ship date
      fail query: |
        SELECT order_id, order_status, shipped_date
        FROM orders
        WHERE order_status IN ('shipped', 'delivered')
          AND shipped_date IS NULL
```

**Run Soda Scans:**
```bash
# Scan all checks
soda scan -d postgres_warehouse -c configuration.yml checks/

# Scan specific table
soda scan -d postgres_warehouse -c configuration.yml checks/customers.yml

# Generate HTML report
soda scan -d postgres_warehouse -c configuration.yml checks/ --reports reports/
```

**Integrate with Python:**
```python
# run_soda_checks.py
"""
Run Soda checks programmatically
"""

from soda.scan import Scan

def run_data_quality_checks():
    """Execute Soda data quality scans."""
    
    scan = Scan()
    scan.set_data_source_name("postgres_warehouse")
    scan.add_configuration_yaml_file("configuration.yml")
    scan.add_sodacl_yaml_files("checks/")
    
    # Execute scan
    exit_code = scan.execute()
    
    # Check results
    scan_results = scan.get_scan_results()
    
    if exit_code != 0:
        print("❌ Data quality checks FAILED")
        for check in scan_results['checks']:
            if check['outcome'] == 'fail':
                print(f"  Failed: {check['name']}")
                print(f"  Message: {check['diagnostics']['fail_message']}")
        return False
    else:
        print("✅ Data quality checks PASSED")
        return True

if __name__ == "__main__":
    success = run_data_quality_checks()
    exit(0 if success else 1)
```

**Verification:**
- [ ] Soda Core installed
- [ ] Configuration file created
- [ ] Check files defined
- [ ] Scans run successfully
- [ ] Reports generated

**If This Fails:**
→ Check database connection
→ Verify YAML syntax
→ Review check logic
→ Test with simpler checks first
→ Check Soda documentation

---

### Step 5: Implement Validation with dbt Tests

**What:** Use dbt's native testing framework for data quality

**How:**

**Generic dbt Tests:**
```yaml
# models/schema.yml
version: 2

models:
  - name: stg_customers
    description: Staged customer data
    
    tests:
      - dbt_utils.equal_rowcount:
          compare_model: source('raw', 'customers')
    
    columns:
      - name: customer_id
        description: Primary key
        tests:
          - unique
          - not_null
          - dbt_utils.at_least_one
      
      - name: email
        tests:
          - not_null
          - unique
          - dbt_utils.not_null_proportion:
              at_least: 0.95
      
      - name: country
        tests:
          - accepted_values:
              values: ['US', 'UK', 'CA', 'AU', 'DE', 'FR']
              quote: false
      
      - name: created_at
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "<= current_date"
      
      - name: updated_at
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= created_at"

  - name: fct_orders
    columns:
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

**Custom Singular Tests:**
```sql
-- tests/assert_valid_order_amounts.sql
-- Orders should have positive amounts

SELECT
    order_id,
    total_amount
FROM {{ ref('fct_orders') }}
WHERE total_amount <= 0
```

```sql
-- tests/assert_no_orphan_orders.sql
-- All orders should have valid customers

SELECT o.order_id
FROM {{ ref('fct_orders') }} o
LEFT JOIN {{ ref('dim_customers') }} c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
```

**Custom Generic Tests:**
```sql
-- macros/test_freshness_in_hours.sql

{% test freshness_in_hours(model, column_name, max_age_hours) %}

SELECT *
FROM {{ model }}
WHERE DATEDIFF('hour', {{ column_name }}, CURRENT_TIMESTAMP) > {{ max_age_hours }}

{% endtest %}
```

**Use Custom Test:**
```yaml
columns:
  - name: updated_at
    tests:
      - freshness_in_hours:
          max_age_hours: 24
```

**Run dbt Tests:**
```bash
# Run all tests
dbt test

# Test specific model
dbt test --select stg_customers

# Test specific column
dbt test --select stg_customers,column:email

# Run with fail fast
dbt test --fail-fast

# Store test results
dbt test --store-failures
```

**Verification:**
- [ ] dbt tests defined
- [ ] Generic tests added
- [ ] Custom tests created
- [ ] All tests passing
- [ ] Test coverage adequate

**If This Fails:**
→ Run tests individually to isolate issues
→ Check data quality at source
→ Review test logic
→ Start with essential tests only

---

### Step 6: Set Up Monitoring and Alerting

**What:** Configure automated monitoring and alerts for data quality

**How:**

**Monitoring Dashboard (Python):**
```python
# quality_dashboard.py
"""
Create data quality monitoring dashboard
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class DataQualityDashboard:
    """Monitor data quality metrics over time."""
    
    def __init__(self, results_db_connection):
        self.conn = results_db_connection
    
    def get_quality_score_trend(self, days=30):
        """Get quality score trend over time."""
        
        query = f"""
            SELECT 
                DATE(validation_time) as date,
                COUNT(*) as total_checks,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as passed_checks,
                ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as quality_score
            FROM validation_results
            WHERE validation_time >= CURRENT_DATE - INTERVAL '{days} days'
            GROUP BY DATE(validation_time)
            ORDER BY date
        """
        
        df = pd.read_sql(query, self.conn)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['quality_score'],
            mode='lines+markers',
            name='Quality Score',
            line=dict(color='#2ecc71', width=3)
        ))
        
        fig.update_layout(
            title='Data Quality Score Trend',
            xaxis_title='Date',
            yaxis_title='Quality Score (%)',
            yaxis_range=[0, 100]
        )
        
        return fig
    
    def get_failure_breakdown(self):
        """Get breakdown of failures by check type."""
        
        query = """
            SELECT 
                check_type,
                table_name,
                COUNT(*) as failure_count
            FROM validation_results
            WHERE success = FALSE
              AND validation_time >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY check_type, table_name
            ORDER BY failure_count DESC
            LIMIT 20
        """
        
        df = pd.read_sql(query, self.conn)
        
        fig = px.bar(
            df,
            x='failure_count',
            y='table_name',
            color='check_type',
            orientation='h',
            title='Top Data Quality Issues (Last 7 Days)'
        )
        
        return fig
    
    def get_table_health_matrix(self):
        """Get health score for each table."""
        
        query = """
            SELECT 
                table_name,
                check_type,
                ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 1) as score
            FROM validation_results
            WHERE validation_time >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY table_name, check_type
        """
        
        df = pd.read_sql(query, self.conn)
        pivot = df.pivot(index='table_name', columns='check_type', values='score')
        
        fig = px.imshow(
            pivot,
            labels=dict(x="Check Type", y="Table", color="Score %"),
            title="Table Health Matrix",
            color_continuous_scale='RdYlGn',
            zmin=0,
            zmax=100
        )
        
        return fig

# Usage
dashboard = DataQualityDashboard(db_connection)
dashboard.get_quality_score_trend().show()
dashboard.get_failure_breakdown().show()
```

**Alerting System:**
```python
# alerting.py
"""
Send alerts for data quality failures
"""

import requests
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class QualityAlert:
    """Data quality alert."""
    severity: str  # 'error', 'warning', 'info'
    table: str
    check_name: str
    message: str
    failed_count: int
    timestamp: str

class AlertManager:
    """Manage data quality alerts."""
    
    def __init__(self, slack_webhook: str, pagerduty_key: str = None):
        self.slack_webhook = slack_webhook
        self.pagerduty_key = pagerduty_key
    
    def send_alert(self, alert: QualityAlert):
        """Send alert through appropriate channels."""
        
        if alert.severity == 'error':
            self.send_to_slack(alert)
            if self.pagerduty_key:
                self.send_to_pagerduty(alert)
        
        elif alert.severity == 'warning':
            self.send_to_slack(alert)
    
    def send_to_slack(self, alert: QualityAlert):
        """Send alert to Slack."""
        
        color = {
            'error': '#e74c3c',
            'warning': '#f39c12',
            'info': '#3498db'
        }[alert.severity]
        
        emoji = {
            'error': ':rotating_light:',
            'warning': ':warning:',
            'info': ':information_source:'
        }[alert.severity]
        
        message = {
            "attachments": [{
                "color": color,
                "title": f"{emoji} Data Quality Alert - {alert.severity.upper()}",
                "fields": [
                    {"title": "Table", "value": alert.table, "short": True},
                    {"title": "Check", "value": alert.check_name, "short": True},
                    {"title": "Failed Rows", "value": str(alert.failed_count), "short": True},
                    {"title": "Time", "value": alert.timestamp, "short": True},
                    {"title": "Message", "value": alert.message, "short": False},
                ],
            }]
        }
        
        requests.post(self.slack_webhook, json=message)
    
    def send_to_pagerduty(self, alert: QualityAlert):
        """Send critical alert to PagerDuty."""
        
        payload = {
            "routing_key": self.pagerduty_key,
            "event_action": "trigger",
            "payload": {
                "summary": f"Data Quality Error: {alert.table}.{alert.check_name}",
                "severity": "error",
                "source": "data-quality-pipeline",
                "custom_details": {
                    "table": alert.table,
                    "check": alert.check_name,
                    "failed_count": alert.failed_count,
                    "message": alert.message
                }
            }
        }
        
        requests.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload
        )

# Usage
alert_manager = AlertManager(
    slack_webhook="https://hooks.slack.com/services/...",
    pagerduty_key="your_pagerduty_integration_key"
)

# When validation fails
alert = QualityAlert(
    severity='error',
    table='customers',
    check_name='email_validity',
    message='Found 150 invalid email addresses',
    failed_count=150,
    timestamp=datetime.now().isoformat()
)

alert_manager.send_alert(alert)
```

**Verification:**
- [ ] Dashboard created
- [ ] Metrics tracked
- [ ] Alerts configured
- [ ] Notifications working
- [ ] Thresholds tuned

**If This Fails:**
→ Test alert channels
→ Verify webhook URLs
→ Check permissions
→ Review alerting logic
→ Start with simple alerts

---

### Step 7: Integrate Quality Checks into Pipeline

**What:** Embed quality checks into data pipelines

**How:**

**Airflow Integration:**
```python
# dags/quality_enabled_pipeline.py
"""
ETL pipeline with integrated data quality checks
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import great_expectations as gx

def extract_data(**context):
    """Extract data from source."""
    # Extraction logic
    pass

def validate_source_data(**context):
    """Validate extracted data before transformation."""
    
    ge_context = gx.get_context()
    
    result = ge_context.run_checkpoint(
        checkpoint_name="source_data_checkpoint"
    )
    
    if not result["success"]:
        raise ValueError("Source data validation failed!")
    
    return True

def transform_data(**context):
    """Transform data."""
    # Transformation logic
    pass

def validate_transformed_data(**context):
    """Validate transformed data before loading."""
    
    ge_context = gx.get_context()
    
    result = ge_context.run_checkpoint(
        checkpoint_name="transformed_data_checkpoint"
    )
    
    if not result["success"]:
        raise ValueError("Transformed data validation failed!")
    
    return True

def load_data(**context):
    """Load data to warehouse."""
    # Loading logic
    pass

def validate_loaded_data(**context):
    """Validate data after loading."""
    
    ge_context = gx.get_context()
    
    result = ge_context.run_checkpoint(
        checkpoint_name="loaded_data_checkpoint"
    )
    
    if not result["success"]:
        raise ValueError("Loaded data validation failed!")
    
    return True

with DAG(
    'quality_enabled_etl',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data
    )
    
    validate_source = PythonOperator(
        task_id='validate_source',
        python_callable=validate_source_data
    )
    
    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data
    )
    
    validate_transformed = PythonOperator(
        task_id='validate_transformed',
        python_callable=validate_transformed_data
    )
    
    load = PythonOperator(
        task_id='load',
        python_callable=load_data
    )
    
    validate_loaded = PythonOperator(
        task_id='validate_loaded',
        python_callable=validate_loaded_data
    )
    
    # Pipeline flow with quality gates
    extract >> validate_source >> transform >> validate_transformed >> load >> validate_loaded
```

**Verification:**
- [ ] Quality checks integrated
- [ ] Pipeline fails on quality issues
- [ ] Quality gates at appropriate stages
- [ ] Alerts triggered on failures
- [ ] Team trained on quality process

**If This Fails:**
→ Test quality checks independently
→ Review integration points
→ Check error handling
→ Verify alert notifications

---

## Verification Checklist

After completing this workflow:

- [ ] Framework selected and installed
- [ ] Data profiled
- [ ] Quality rules defined
- [ ] Validation implemented
- [ ] Tests passing
- [ ] Monitoring configured
- [ ] Alerts working
- [ ] Pipeline integration complete
- [ ] Documentation created
- [ ] Team trained

---

## Common Issues & Solutions

### Issue: Too Many False Positives

**Symptoms:**
- Alerts firing constantly
- Team ignoring alerts
- Quality checks failing on valid data

**Solution:**
- Review and tune thresholds
- Add context to checks
- Implement alert aggregation
- Distinguish between errors and warnings
- Add grace periods for known issues

---

### Issue: Performance Impact

**Symptoms:**
- Pipeline slowing down
- Quality checks taking too long
- Resource exhaustion

**Solution:**
- Sample data for checks where possible
- Run checks in parallel
- Optimize query performance
- Schedule heavy checks off-peak
- Use incremental validation

---

## Best Practices

### DO:
✅ Start with critical data quality dimensions
✅ Define clear quality rules
✅ Automate all quality checks
✅ Monitor quality trends over time
✅ Alert on regressions
✅ Document quality standards
✅ Integrate checks into pipelines
✅ Make quality visible to stakeholders
✅ Review and update checks regularly
✅ Set appropriate thresholds
✅ Use severity levels
✅ Track quality metrics

### DON'T:
❌ Skip data profiling
❌ Create checks without context
❌ Ignore failed checks
❌ Over-alert
❌ Run expensive checks unnecessarily
❌ Hard-code thresholds
❌ Forget to test your tests
❌ Make quality someone else's problem
❌ Treat all issues equally
❌ Set and forget
❌ Ignore performance impact
❌ Skip documentation

---

## Related Workflows

**Prerequisites:**
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL patterns

**Next Steps:**
- [pipeline_orchestration_airflow.md](./pipeline_orchestration_airflow.md) - Orchestration
- [data_transformation_dbt.md](./data_transformation_dbt.md) - Transformations

**Related:**
- [../testing/test_writing.md](../testing/test_writing.md) - Testing patterns
- [../devops/application_monitoring_setup.md](../devops/application_monitoring_setup.md) - Monitoring

---

## Tags
`data-engineering` `data-quality` `validation` `testing` `monitoring` `great-expectations` `soda` `dbt` `data-governance`
