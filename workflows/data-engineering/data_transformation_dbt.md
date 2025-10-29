# Data Transformation with dbt

**ID:** dat-006  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Transform raw data into analytics-ready datasets using dbt (Data Build Tool) with SQL-based transformations, testing, and documentation

**Why:** dbt enables version-controlled, testable, and documented data transformations that can be collaboratively developed and maintained by data teams

**When to use:**
- Building data transformation pipelines in SQL
- Creating analytics-ready datasets
- Implementing data quality tests
- Documenting data lineage
- Version controlling transformations
- Enabling analytics engineering workflows

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ installed
- [ ] SQL knowledge (proficient)
- [ ] Data warehouse account (Snowflake, BigQuery, Redshift, etc.)
- [ ] Git for version control
- [ ] Understanding of data modeling concepts

**Check before starting:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip
pip --version

# Verify git
git --version

# Check database CLI (optional)
snowsql --version
# or
bq version
```

---

## Implementation Steps

### Step 1: Install and Initialize dbt Project

**What:** Set up dbt and create a new project

**How:**

**Install dbt:**
```bash
# Install dbt for your data warehouse
# For Snowflake
pip install dbt-snowflake

# For BigQuery
pip install dbt-bigquery

# For Redshift
pip install dbt-redshift

# For Postgres
pip install dbt-postgres

# Verify installation
dbt --version
```

**Initialize Project:**
```bash
# Create new dbt project
dbt init my_dbt_project

# Project structure created:
# my_dbt_project/
# ├── dbt_project.yml          # Project configuration
# ├── profiles.yml             # Connection profiles (in ~/.dbt/)
# ├── models/                  # SQL transformation models
# │   └── example/
# ├── tests/                   # Custom data tests
# ├── macros/                  # Reusable SQL functions
# ├── seeds/                   # CSV files to load
# ├── snapshots/               # Slowly changing dimensions
# └── analysis/                # Ad-hoc queries

cd my_dbt_project
```

**Configure Connection (profiles.yml):**
```yaml
# ~/.dbt/profiles.yml
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: my_account.us-east-1
      user: dbt_user
      password: "{{ env_var('DBT_PASSWORD') }}"
      role: transformer
      database: analytics_dev
      warehouse: transforming
      schema: dbt_dev
      threads: 4
      client_session_keep_alive: False
      
    prod:
      type: snowflake
      account: my_account.us-east-1
      user: dbt_prod_user
      password: "{{ env_var('DBT_PROD_PASSWORD') }}"
      role: transformer
      database: analytics_prod
      warehouse: transforming
      schema: dbt_prod
      threads: 8
      client_session_keep_alive: False

# For BigQuery
bigquery_project:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: my-gcp-project
      dataset: dbt_dev
      threads: 4
      keyfile: /path/to/service-account.json
      timeout_seconds: 300
      location: US
      priority: interactive
```

**Configure Project (dbt_project.yml):**
```yaml
name: 'my_dbt_project'
version: '1.0.0'
config-version: 2

# Profile to use
profile: 'my_dbt_project'

# Directories
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

# Model configurations
models:
  my_dbt_project:
    # Staging models (bronze → silver)
    staging:
      +materialized: view
      +schema: staging
      
    # Intermediate models (silver transformations)
    intermediate:
      +materialized: ephemeral
      
    # Marts (gold - business ready)
    marts:
      +materialized: table
      +schema: marts
      
      # Core business entities
      core:
        +tags: ["core", "daily"]
        
      # Finance mart
      finance:
        +tags: ["finance", "daily"]
        +schema: finance
        
      # Marketing mart
      marketing:
        +tags: ["marketing", "hourly"]
        +schema: marketing

# Seeds configuration
seeds:
  my_dbt_project:
    +schema: seed_data
    +quote_columns: false

# Snapshot configuration
snapshots:
  my_dbt_project:
    +target_schema: snapshots
    +strategy: timestamp
    +unique_key: id

# Documentation
docs-paths: ["docs"]

# Dispatch configuration
dispatch:
  - macro_namespace: dbt_utils
    search_order: ['my_dbt_project', 'dbt_utils']
```

**Test Connection:**
```bash
# Test database connection
dbt debug

# Expected output:
# Connection test: [OK connection ok]
# All checks passed!
```

**Verification:**
- [ ] dbt installed successfully
- [ ] Project initialized
- [ ] profiles.yml configured
- [ ] Connection test passed
- [ ] Project structure created

**If This Fails:**
→ Check database credentials
→ Verify network connectivity
→ Review profiles.yml syntax
→ Check data warehouse permissions
→ Ensure correct dbt adapter installed

---

### Step 2: Create Source Configurations

**What:** Define source tables that dbt will transform

**How:**

**Define Sources (models/staging/_sources.yml):**
```yaml
# models/staging/_sources.yml
version: 2

sources:
  - name: raw
    description: Raw data from application database
    database: raw_data
    schema: production
    
    # Source freshness checks
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    
    # Metadata
    meta:
      owner: "data-engineering"
      contains_pii: true
    
    # Tables
    tables:
      - name: customers
        description: Customer master table
        columns:
          - name: customer_id
            description: Primary key
            tests:
              - unique
              - not_null
          
          - name: email
            description: Customer email address
            tests:
              - not_null
          
          - name: created_at
            description: Account creation timestamp
        
        # Loaded timestamp
        loaded_at_field: _loaded_at
        
        # Source freshness
        freshness:
          warn_after: {count: 6, period: hour}
      
      - name: orders
        description: Order transactions
        columns:
          - name: order_id
            description: Primary key
            tests:
              - unique
              - not_null
          
          - name: customer_id
            description: Foreign key to customers
            tests:
              - not_null
              - relationships:
                  to: source('raw', 'customers')
                  field: customer_id
          
          - name: order_date
            description: Order placement date
          
          - name: amount
            description: Order total amount
            tests:
              - not_null
      
      - name: order_items
        description: Individual items in orders
        columns:
          - name: order_item_id
            tests:
              - unique
              - not_null
          
          - name: order_id
            tests:
              - not_null
              - relationships:
                  to: source('raw', 'orders')
                  field: order_id
          
          - name: product_id
            tests:
              - not_null
          
          - name: quantity
            tests:
              - not_null
          
          - name: unit_price
            tests:
              - not_null

  # Another source system
  - name: salesforce
    description: Data from Salesforce CRM
    database: salesforce_replica
    schema: public
    
    tables:
      - name: accounts
        description: Salesforce accounts
        identifier: Account  # If table name differs
        
      - name: opportunities
        description: Sales opportunities
        identifier: Opportunity
```

**Verification:**
- [ ] Sources defined
- [ ] Freshness checks configured
- [ ] Column tests specified
- [ ] Relationships documented
- [ ] Metadata added

**If This Fails:**
→ Check source database access
→ Verify table names and schemas
→ Review YAML syntax
→ Test source freshness: `dbt source freshness`

---

### Step 3: Build Staging Models

**What:** Create staging models that clean and standardize source data

**How:**

**Staging Model Pattern:**
```sql
-- models/staging/stg_customers.sql

{{
  config(
    materialized='view',
    tags=['staging', 'customers']
  )
}}

WITH source AS (
    
    SELECT * FROM {{ source('raw', 'customers') }}

),

renamed AS (

    SELECT
        -- Primary key
        customer_id,
        
        -- Identifiers
        LOWER(TRIM(email)) AS email,
        
        -- Attributes
        TRIM(first_name) AS first_name,
        TRIM(last_name) AS last_name,
        REGEXP_REPLACE(phone, '[^0-9]', '') AS phone,
        LOWER(TRIM(country)) AS country,
        
        -- Dates
        created_at,
        updated_at,
        
        -- Metadata
        _loaded_at

    FROM source

),

validated AS (

    SELECT *
    FROM renamed
    
    -- Data quality filters
    WHERE email IS NOT NULL
        AND email LIKE '%@%'
        AND created_at IS NOT NULL

)

SELECT * FROM validated
```

**Staging with Incremental Loading:**
```sql
-- models/staging/stg_orders.sql

{{
  config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns',
    tags=['staging', 'orders', 'incremental']
  )
}}

WITH source AS (

    SELECT * FROM {{ source('raw', 'orders') }}
    
    {% if is_incremental() %}
    -- Only new/updated records
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}

),

renamed AS (

    SELECT
        -- Primary key
        order_id,
        
        -- Foreign keys
        customer_id,
        
        -- Attributes
        order_status,
        CAST(amount AS DECIMAL(10,2)) AS amount,
        CAST(tax_amount AS DECIMAL(10,2)) AS tax_amount,
        CAST(total_amount AS DECIMAL(10,2)) AS total_amount,
        
        -- Dates
        order_date::DATE AS order_date,
        shipped_date::DATE AS shipped_date,
        delivered_date::DATE AS delivered_date,
        
        -- Timestamps
        created_at,
        updated_at

    FROM source

)

SELECT * FROM renamed
```

**Staging with Custom Tests (stg_customers.yml):**
```yaml
# models/staging/stg_customers.yml
version: 2

models:
  - name: stg_customers
    description: Cleaned and standardized customer data
    
    columns:
      - name: customer_id
        description: Primary key
        tests:
          - unique
          - not_null
      
      - name: email
        description: Customer email (cleaned and lowercase)
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_length: 5
              max_length: 255
      
      - name: country
        description: Customer country (lowercase)
        tests:
          - accepted_values:
              values: ['us', 'uk', 'ca', 'au', 'de', 'fr']
              quote: false
      
      - name: created_at
        description: Account creation timestamp
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= '2020-01-01'"
```

**Verification:**
- [ ] Staging models created
- [ ] Source references correct
- [ ] Column naming standardized
- [ ] Data types cast appropriately
- [ ] Tests defined

**If This Fails:**
→ Run `dbt run --models staging` to test
→ Check SQL syntax
→ Verify source table access
→ Review test results: `dbt test --models staging`

---

### Step 4: Build Intermediate Models

**What:** Create intermediate transformation layers

**How:**

**Intermediate Model - Joins:**
```sql
-- models/intermediate/int_customer_orders.sql

{{
  config(
    materialized='ephemeral',
    tags=['intermediate']
  )
}}

WITH customers AS (
    
    SELECT * FROM {{ ref('stg_customers') }}

),

orders AS (
    
    SELECT * FROM {{ ref('stg_orders') }}

),

customer_orders AS (

    SELECT
        c.customer_id,
        c.email,
        c.first_name,
        c.last_name,
        c.country,
        
        o.order_id,
        o.order_date,
        o.order_status,
        o.total_amount

    FROM customers c
    INNER JOIN orders o
        ON c.customer_id = o.customer_id

)

SELECT * FROM customer_orders
```

**Intermediate Model - Aggregations:**
```sql
-- models/intermediate/int_customer_metrics.sql

{{
  config(
    materialized='table',
    tags=['intermediate', 'metrics']
  )
}}

WITH customer_orders AS (

    SELECT * FROM {{ ref('int_customer_orders') }}

),

metrics AS (

    SELECT
        customer_id,
        
        -- Order metrics
        COUNT(DISTINCT order_id) AS lifetime_orders,
        SUM(total_amount) AS lifetime_value,
        AVG(total_amount) AS avg_order_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        
        -- Recency
        DATEDIFF('day', MAX(order_date), CURRENT_DATE) AS days_since_last_order,
        
        -- Frequency
        CASE
            WHEN COUNT(DISTINCT order_id) = 1 THEN 'One-time'
            WHEN COUNT(DISTINCT order_id) BETWEEN 2 AND 5 THEN 'Occasional'
            WHEN COUNT(DISTINCT order_id) > 5 THEN 'Frequent'
        END AS purchase_frequency

    FROM customer_orders
    
    GROUP BY customer_id

)

SELECT * FROM metrics
```

**Verification:**
- [ ] Intermediate models created
- [ ] Join logic correct
- [ ] Aggregations accurate
- [ ] Ephemeral vs table materialization chosen appropriately
- [ ] Dependencies clear

**If This Fails:**
→ Run `dbt run --models intermediate`
→ Check model references with `dbt ls --models +int_customer_metrics`
→ Review lineage in dbt docs

---

### Step 5: Build Mart Models (Business Layer)

**What:** Create final analytics-ready tables for business users

**How:**

**Dimension Table:**
```sql
-- models/marts/core/dim_customers.sql

{{
  config(
    materialized='table',
    tags=['marts', 'core', 'dimension']
  )
}}

WITH customers AS (

    SELECT * FROM {{ ref('stg_customers') }}

),

metrics AS (

    SELECT * FROM {{ ref('int_customer_metrics') }}

),

final AS (

    SELECT
        -- Surrogate key
        {{ dbt_utils.generate_surrogate_key(['c.customer_id']) }} AS customer_key,
        
        -- Natural key
        c.customer_id,
        
        -- Attributes
        c.email,
        c.first_name,
        c.last_name,
        c.first_name || ' ' || c.last_name AS full_name,
        c.phone,
        c.country,
        
        -- Metrics
        COALESCE(m.lifetime_orders, 0) AS lifetime_orders,
        COALESCE(m.lifetime_value, 0) AS lifetime_value,
        COALESCE(m.avg_order_value, 0) AS avg_order_value,
        m.first_order_date,
        m.last_order_date,
        m.days_since_last_order,
        m.purchase_frequency,
        
        -- Segmentation
        CASE
            WHEN COALESCE(m.lifetime_value, 0) > 10000 THEN 'VIP'
            WHEN COALESCE(m.lifetime_value, 0) > 1000 THEN 'Gold'
            WHEN COALESCE(m.lifetime_value, 0) > 100 THEN 'Silver'
            ELSE 'Bronze'
        END AS customer_segment,
        
        CASE
            WHEN m.days_since_last_order IS NULL THEN 'Never Purchased'
            WHEN m.days_since_last_order <= 30 THEN 'Active'
            WHEN m.days_since_last_order <= 90 THEN 'At Risk'
            WHEN m.days_since_last_order <= 180 THEN 'Churning'
            ELSE 'Churned'
        END AS lifecycle_stage,
        
        -- Metadata
        c.created_at,
        c.updated_at,
        CURRENT_TIMESTAMP() AS dbt_updated_at

    FROM customers c
    LEFT JOIN metrics m
        ON c.customer_id = m.customer_id

)

SELECT * FROM final
```

**Fact Table:**
```sql
-- models/marts/core/fct_orders.sql

{{
  config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns',
    partition_by={
      "field": "order_date",
      "data_type": "date",
      "granularity": "day"
    },
    cluster_by=['customer_id', 'order_status'],
    tags=['marts', 'core', 'fact', 'incremental']
  )
}}

WITH orders AS (

    SELECT * FROM {{ ref('stg_orders') }}
    
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}

),

customers AS (

    SELECT * FROM {{ ref('dim_customers') }}

),

final AS (

    SELECT
        -- Keys
        o.order_id,
        c.customer_key,
        o.customer_id,
        
        -- Dates
        o.order_date,
        o.shipped_date,
        o.delivered_date,
        
        -- Metrics
        o.amount,
        o.tax_amount,
        o.total_amount,
        
        -- Attributes
        o.order_status,
        c.customer_segment,
        c.lifecycle_stage,
        c.country,
        
        -- Derived metrics
        DATEDIFF('day', o.order_date, o.shipped_date) AS days_to_ship,
        DATEDIFF('day', o.order_date, o.delivered_date) AS days_to_deliver,
        
        -- Flags
        CASE WHEN o.order_date = c.first_order_date THEN TRUE ELSE FALSE END AS is_first_order,
        CASE WHEN o.shipped_date IS NOT NULL THEN TRUE ELSE FALSE END AS is_shipped,
        CASE WHEN o.delivered_date IS NOT NULL THEN TRUE ELSE FALSE END AS is_delivered,
        
        -- Metadata
        o.created_at,
        o.updated_at,
        CURRENT_TIMESTAMP() AS dbt_updated_at

    FROM orders o
    LEFT JOIN customers c
        ON o.customer_id = c.customer_id

)

SELECT * FROM final
```

**Aggregate Mart:**
```sql
-- models/marts/finance/fct_daily_revenue.sql

{{
  config(
    materialized='table',
    tags=['marts', 'finance', 'daily']
  )
}}

WITH orders AS (

    SELECT * FROM {{ ref('fct_orders') }}

),

daily_revenue AS (

    SELECT
        order_date,
        
        -- Revenue metrics
        COUNT(DISTINCT order_id) AS order_count,
        COUNT(DISTINCT customer_id) AS customer_count,
        SUM(amount) AS gross_revenue,
        SUM(tax_amount) AS tax_revenue,
        SUM(total_amount) AS total_revenue,
        AVG(total_amount) AS avg_order_value,
        
        -- Order status breakdown
        SUM(CASE WHEN order_status = 'completed' THEN total_amount ELSE 0 END) AS completed_revenue,
        SUM(CASE WHEN order_status = 'pending' THEN total_amount ELSE 0 END) AS pending_revenue,
        SUM(CASE WHEN order_status = 'cancelled' THEN total_amount ELSE 0 END) AS cancelled_revenue,
        
        -- Customer segment breakdown
        SUM(CASE WHEN customer_segment = 'VIP' THEN total_amount ELSE 0 END) AS vip_revenue,
        SUM(CASE WHEN customer_segment = 'Gold' THEN total_amount ELSE 0 END) AS gold_revenue,
        SUM(CASE WHEN customer_segment = 'Silver' THEN total_amount ELSE 0 END) AS silver_revenue,
        SUM(CASE WHEN customer_segment = 'Bronze' THEN total_amount ELSE 0 END) AS bronze_revenue,
        
        -- First-time customers
        COUNT(DISTINCT CASE WHEN is_first_order THEN customer_id END) AS new_customers,
        SUM(CASE WHEN is_first_order THEN total_amount ELSE 0 END) AS new_customer_revenue

    FROM orders
    
    GROUP BY order_date

)

SELECT * FROM daily_revenue
```

**Verification:**
- [ ] Mart models created
- [ ] Dimensions and facts defined
- [ ] Business logic implemented
- [ ] Aggregations correct
- [ ] Performance optimized

**If This Fails:**
→ Run `dbt run --models marts`
→ Check for missing references
→ Verify business logic with stakeholders
→ Profile query performance

---

### Step 6: Implement Tests and Data Quality

**What:** Add comprehensive data quality tests

**How:**

**Generic Tests (schema.yml):**
```yaml
# models/marts/core/schema.yml
version: 2

models:
  - name: dim_customers
    description: Customer dimension table
    
    tests:
      - dbt_utils.expression_is_true:
          expression: "lifetime_orders >= 0"
      - dbt_utils.expression_is_true:
          expression: "lifetime_value >= 0"
    
    columns:
      - name: customer_key
        description: Surrogate key
        tests:
          - unique
          - not_null
      
      - name: customer_id
        description: Natural key
        tests:
          - unique
          - not_null
      
      - name: email
        tests:
          - not_null
          - dbt_utils.not_null_proportion:
              at_least: 0.95
      
      - name: customer_segment
        tests:
          - accepted_values:
              values: ['VIP', 'Gold', 'Silver', 'Bronze']
      
      - name: lifecycle_stage
        tests:
          - accepted_values:
              values: ['Never Purchased', 'Active', 'At Risk', 'Churning', 'Churned']

  - name: fct_orders
    description: Orders fact table
    
    tests:
      - dbt_utils.expression_is_true:
          expression: "total_amount = amount + tax_amount"
      - dbt_utils.expression_is_true:
          expression: "order_date <= CURRENT_DATE"
    
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      
      - name: total_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              inclusive: true
```

**Custom Singular Tests:**
```sql
-- tests/assert_positive_revenue.sql
-- Test that daily revenue is always positive

SELECT
    order_date,
    total_revenue
FROM {{ ref('fct_daily_revenue') }}
WHERE total_revenue < 0
```

```sql
-- tests/assert_no_future_orders.sql
-- Test that no orders are dated in the future

SELECT
    order_id,
    order_date
FROM {{ ref('fct_orders') }}
WHERE order_date > CURRENT_DATE
```

**Custom Generic Test (Macro):**
```sql
-- macros/test_reasonable_value_range.sql

{% test reasonable_value_range(model, column_name, min_value, max_value) %}

WITH validation AS (

    SELECT
        {{ column_name }} AS test_column
    FROM {{ model }}
    WHERE {{ column_name }} < {{ min_value }}
       OR {{ column_name }} > {{ max_value }}

)

SELECT * FROM validation

{% endtest %}
```

**Use Custom Test:**
```yaml
# In schema.yml
columns:
  - name: avg_order_value
    tests:
      - reasonable_value_range:
          min_value: 0
          max_value: 100000
```

**Verification:**
- [ ] Generic tests added
- [ ] Custom tests created
- [ ] Relationships validated
- [ ] All tests passing
- [ ] Test coverage adequate

**If This Fails:**
→ Run `dbt test` to see failures
→ Review test logic
→ Check for data quality issues in source
→ Run specific test: `dbt test --select dim_customers`

---

### Step 7: Create Macros for Reusability

**What:** Build reusable SQL functions with Jinja macros

**How:**

**Date Macros:**
```sql
-- macros/date_utils.sql

{% macro get_fiscal_year(date_column) %}
    CASE
        WHEN EXTRACT(MONTH FROM {{ date_column }}) >= 7 THEN EXTRACT(YEAR FROM {{ date_column }}) + 1
        ELSE EXTRACT(YEAR FROM {{ date_column }})
    END
{% endmacro %}

{% macro date_spine(start_date, end_date, datepart='day') %}

    {{
      dbt_utils.date_spine(
        datepart=datepart,
        start_date=start_date,
        end_date=end_date
      )
    }}

{% endmacro %}
```

**String Macros:**
```sql
-- macros/string_utils.sql

{% macro clean_string(column_name) %}
    TRIM(LOWER({{ column_name }}))
{% endmacro %}

{% macro concatenate_with_separator(columns, separator=', ') %}
    CONCAT(
        {% for column in columns %}
            COALESCE(CAST({{ column }} AS STRING), '')
            {% if not loop.last %} || '{{ separator }}' || {% endif %}
        {% endfor %}
    )
{% endmacro %}
```

**Pivot Macro:**
```sql
-- macros/pivot.sql

{% macro pivot(column_to_pivot, values_column, relation) %}

{% set pivot_values_query %}
    SELECT DISTINCT {{ column_to_pivot }}
    FROM {{ relation }}
    ORDER BY 1
{% endset %}

{% set results = run_query(pivot_values_query) %}

{% if execute %}
    {% set pivot_values = results.columns[0].values() %}
{% else %}
    {% set pivot_values = [] %}
{% endif %}

SELECT
    *,
    {% for value in pivot_values %}
        SUM(CASE WHEN {{ column_to_pivot }} = '{{ value }}' THEN {{ values_column }} ELSE 0 END) AS {{ value }}
        {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ relation }}
GROUP BY 1

{% endmacro %}
```

**Use Macros in Models:**
```sql
-- models/marts/finance/revenue_by_segment.sql

WITH orders AS (

    SELECT * FROM {{ ref('fct_orders') }}

),

pivoted AS (

    {{
      pivot(
        column_to_pivot='customer_segment',
        values_column='total_amount',
        relation=ref('fct_orders')
      )
    }}

)

SELECT
    order_date,
    {{ get_fiscal_year('order_date') }} AS fiscal_year,
    VIP,
    Gold,
    Silver,
    Bronze
FROM pivoted
```

**Verification:**
- [ ] Macros created
- [ ] Macros tested
- [ ] Documentation added
- [ ] Reused across models
- [ ] Performance acceptable

**If This Fails:**
→ Test macro with `dbt run --models model_using_macro`
→ Check Jinja syntax
→ Review macro logic
→ Add logging: `{{ log("Debug: " ~ variable, info=True) }}`

---

### Step 8: Generate and Deploy Documentation

**What:** Create and publish dbt documentation

**How:**

**Add Descriptions:**
```yaml
# models/schema.yml
version: 2

models:
  - name: dim_customers
    description: |
      Customer dimension table containing current state of all customers.
      
      This table is the **single source of truth** for customer data across
      the organization. It includes:
      
      - Customer demographics
      - Lifetime purchase metrics
      - Customer segmentation
      - Lifecycle stage
      
      **Refresh Schedule:** Daily at 2 AM UTC
      **SLA:** Available by 3 AM UTC
      **Owner:** Data Engineering Team
    
    columns:
      - name: customer_key
        description: |
          Surrogate key generated using dbt_utils.generate_surrogate_key()
          
          This key is stable across environments and can be used for:
          - Joins across models
          - Tracking in downstream systems
      
      - name: customer_segment
        description: |
          Customer value segment based on lifetime spend:
          - **VIP**: > $10,000 lifetime value
          - **Gold**: $1,000 - $10,000
          - **Silver**: $100 - $1,000
          - **Bronze**: < $100
```

**Add docs blocks:**
```
<!-- docs/overview.md -->
{% docs __overview__ %}

# Analytics Data Platform

Welcome to the analytics dbt project! This project transforms raw data
from our application database into analytics-ready datasets.

## Architecture

Our dbt project follows the **Medallion Architecture**:

- **Staging** (`stg_`): Cleaned and standardized source data
- **Intermediate** (`int_`): Business logic and calculations
- **Marts** (`dim_`, `fct_`): Final analytics-ready tables

## Data Sources

- **Application Database**: Customer, order, and product data
- **Salesforce**: CRM data
- **Marketing Platform**: Campaign and engagement data

## Getting Started

1. Clone the repository
2. Run `dbt deps` to install packages
3. Run `dbt seed` to load seed data
4. Run `dbt run` to build models
5. Run `dbt test` to validate data

{% enddocs %}
```

**Generate Documentation:**
```bash
# Generate documentation
dbt docs generate

# Serve documentation locally
dbt docs serve

# Opens browser at http://localhost:8080
```

**Deploy Documentation:**
```bash
# Option 1: dbt Cloud (automatic)

# Option 2: Deploy to S3/GCS
dbt docs generate
aws s3 sync target/ s3://dbt-docs-bucket/

# Option 3: Use dbt-docs-to-pages
# Deploys to GitHub Pages
```

**Verification:**
- [ ] Documentation generated
- [ ] All models documented
- [ ] DAG visualization correct
- [ ] Column descriptions complete
- [ ] Overview page created

**If This Fails:**
→ Check for compilation errors
→ Verify all models compile: `dbt compile`
→ Review documentation syntax
→ Check for circular dependencies

---

## Verification Checklist

After completing this workflow:

- [ ] dbt project initialized
- [ ] Sources configured
- [ ] Staging models created
- [ ] Intermediate models built
- [ ] Mart models implemented
- [ ] Tests passing
- [ ] Macros created
- [ ] Documentation generated
- [ ] CI/CD configured
- [ ] Team trained

---

## Common Issues & Solutions

### Issue: Model Not Updating

**Symptoms:**
- Changes not reflected in database
- Stale data in tables

**Solution:**
```bash
# Full refresh a specific model
dbt run --models dim_customers --full-refresh

# Clear compiled artifacts
dbt clean

# Rebuild everything
dbt build --full-refresh
```

**Prevention:**
- Use incremental models correctly
- Set up proper unique keys
- Monitor model freshness

---

### Issue: Slow Model Performance

**Symptoms:**
- Models taking too long to run
- Timeouts during execution

**Solution:**
```sql
-- Add performance optimizations
{{
  config(
    materialized='table',
    
    -- Snowflake optimizations
    cluster_by=['customer_id', 'order_date'],
    
    -- BigQuery optimizations
    partition_by={
      "field": "order_date",
      "data_type": "date"
    },
    cluster_by=['customer_id'],
    
    -- Redshift optimizations
    dist='customer_id',
    sort=['order_date', 'customer_id']
  )
}}
```

**Prevention:**
- Profile query performance
- Add appropriate indexes/clusters
- Use incremental models
- Partition large tables

---

## Best Practices

### DO:
✅ Follow naming conventions (stg_, int_, dim_, fct_)
✅ Add tests to all models
✅ Document models and columns
✅ Use staging models for all sources
✅ Keep SQL DRY with macros
✅ Use incremental models for large tables
✅ Version control everything
✅ Use dbt packages for common utilities
✅ Implement CI/CD
✅ Monitor model run times
✅ Use refs() for dependencies
✅ Keep models focused and modular

### DON'T:
❌ Hard-code table names (use source() and ref())
❌ Skip testing
❌ Create circular dependencies
❌ Mix business logic in staging
❌ Forget to document
❌ Ignore performance issues
❌ Skip source freshness checks
❌ Use SELECT * in production
❌ Create overly complex models
❌ Ignore failed tests
❌ Deploy without testing
❌ Mix concerns across layers

---

## Related Workflows

**Prerequisites:**
- [database-migration-workflow.md](./database-migration-workflow.md) - Database setup
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture

**Next Steps:**
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks
- [pipeline_orchestration_airflow.md](./pipeline_orchestration_airflow.md) - Orchestration

**Related:**
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL patterns
- [../development/ci_cd_workflow.md](../development/ci_cd_workflow.md) - CI/CD

---

## Tags
`data-engineering` `dbt` `transformation` `sql` `analytics` `data-modeling` `testing` `documentation` `elt`
