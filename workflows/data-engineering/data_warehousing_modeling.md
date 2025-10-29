# Data Warehousing & Dimensional Modeling

**ID:** dat-007  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 90-150 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Design and implement dimensional data models using star and snowflake schemas for analytical data warehouses

**Why:** Proper dimensional modeling enables efficient analytics, intuitive querying, and fast performance for business intelligence and reporting

**When to use:**
- Building analytical data warehouses
- Creating data marts for business units
- Designing OLAP cubes
- Optimizing for BI tools
- Supporting ad-hoc analysis
- Implementing enterprise data warehouses

---

## Prerequisites

**Required:**
- [ ] Strong SQL knowledge
- [ ] Understanding of data modeling concepts
- [ ] Business process knowledge
- [ ] Data warehouse platform access (Snowflake, BigQuery, Redshift, etc.)
- [ ] ETL tool knowledge

**Check before starting:**
```bash
# Check database access
snowsql -a account -u user -q "SELECT CURRENT_WAREHOUSE();"

# Or BigQuery
bq ls

# Or Redshift
psql -h cluster.region.redshift.amazonaws.com -U user -d warehouse
```

---

## Implementation Steps

### Step 1: Identify Business Processes and Grain

**What:** Define business processes to model and determine the grain (atomic level) of fact tables

**How:**

**Business Process Identification:**
```markdown
## Business Process Matrix

| Business Process | Data Source | Update Frequency | Priority |
|-----------------|-------------|------------------|----------|
| Order Management | ERP System | Real-time | High |
| Customer Acquisition | CRM | Daily | High |
| Inventory Management | WMS | Hourly | Medium |
| Financial Reporting | Accounting | Daily | High |
| Marketing Campaigns | Marketing Platform | Daily | Medium |

## Grain Definition

### Orders Fact Table
**Grain**: One row per order line item
- Atomic level: Each product in an order
- Allows analysis at order, product, and customer levels
- Supports aggregation to order level or daily sales

### Customer Snapshot Fact
**Grain**: One row per customer per day
- Daily snapshot of customer state
- Enables trend analysis over time
- Supports cohort analysis

### Inventory Snapshot Fact
**Grain**: One row per product per warehouse per day
- Daily inventory levels
- Tracks stock movement over time
```

**Grain Decision Framework:**
```python
"""
Determine appropriate grain for fact tables
"""

from dataclasses import dataclass
from typing import List

@dataclass
class GrainDecision:
    """Define fact table grain."""
    business_process: str
    natural_grain: str  # Most atomic level
    analysis_requirements: List[str]
    recommended_grain: str
    rationale: str

# Examples
order_grain = GrainDecision(
    business_process="Order Processing",
    natural_grain="Order line item (product level)",
    analysis_requirements=[
        "Product sales analysis",
        "Customer purchase patterns",
        "Daily/monthly revenue",
        "Product affinity"
    ],
    recommended_grain="Order line item",
    rationale="Allows all required analysis without aggregation loss"
)

customer_snapshot_grain = GrainDecision(
    business_process="Customer Lifecycle",
    natural_grain="Customer state change event",
    analysis_requirements=[
        "Customer retention trends",
        "Cohort analysis",
        "Lifetime value tracking"
    ],
    recommended_grain="Daily customer snapshot",
    rationale="Daily snapshots balance detail with storage"
)
```

**Verification:**
- [ ] Business processes identified
- [ ] Grain clearly defined
- [ ] Atomic level determined
- [ ] Analysis requirements documented
- [ ] Stakeholders aligned

**If This Fails:**
→ Interview business users
→ Review existing reports
→ Analyze query patterns
→ Start with one process
→ Iterate based on feedback

---

### Step 2: Design Dimension Tables

**What:** Create dimension tables with descriptive attributes

**How:**

**Customer Dimension (SCD Type 2):**
```sql
-- dim_customer.sql
CREATE TABLE dim_customer (
    -- Surrogate key
    customer_key INTEGER PRIMARY KEY,
    
    -- Natural key
    customer_id VARCHAR(50) NOT NULL,
    
    -- Descriptive attributes
    customer_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    
    -- Demographics
    birth_date DATE,
    gender VARCHAR(20),
    age_group VARCHAR(50),
    
    -- Location
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    
    -- Segmentation
    customer_segment VARCHAR(50),  -- VIP, Gold, Silver, Bronze
    customer_lifecycle_stage VARCHAR(50),  -- Active, At Risk, Churned
    
    -- Type 2 SCD tracking
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Audit columns
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Version tracking
    version_number INTEGER DEFAULT 1,
    
    -- Row metadata
    row_hash VARCHAR(64),  -- For change detection
    source_system VARCHAR(50)
);

-- Indexes for performance
CREATE INDEX idx_customer_natural_key ON dim_customer(customer_id, is_current);
CREATE INDEX idx_customer_email ON dim_customer(email) WHERE is_current = TRUE;
CREATE INDEX idx_customer_segment ON dim_customer(customer_segment) WHERE is_current = TRUE;
```

**Product Dimension:**
```sql
-- dim_product.sql
CREATE TABLE dim_product (
    -- Surrogate key
    product_key INTEGER PRIMARY KEY,
    
    -- Natural key
    product_id VARCHAR(50) NOT NULL,
    sku VARCHAR(100),
    
    -- Product attributes
    product_name VARCHAR(200) NOT NULL,
    product_description TEXT,
    brand VARCHAR(100),
    
    -- Hierarchy (denormalized for query performance)
    category_level1 VARCHAR(100),  -- Department
    category_level2 VARCHAR(100),  -- Category
    category_level3 VARCHAR(100),  -- Subcategory
    
    -- Product details
    unit_of_measure VARCHAR(20),
    package_size VARCHAR(50),
    weight_kg DECIMAL(10,2),
    
    -- Pricing
    standard_cost DECIMAL(10,2),
    list_price DECIMAL(10,2),
    
    -- Status
    product_status VARCHAR(50),  -- Active, Discontinued, Seasonal
    introduction_date DATE,
    discontinuation_date DATE,
    
    -- Attributes for filtering
    is_organic BOOLEAN,
    is_vegan BOOLEAN,
    is_gluten_free BOOLEAN,
    
    -- Type 2 SCD
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Audit
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_natural_key ON dim_product(product_id, is_current);
CREATE INDEX idx_product_category ON dim_product(category_level1, category_level2) WHERE is_current = TRUE;
```

**Date Dimension:**
```sql
-- dim_date.sql
-- Pre-populate with all dates
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,  -- YYYYMMDD format
    
    -- Date components
    full_date DATE NOT NULL UNIQUE,
    day_of_week INTEGER,
    day_of_week_name VARCHAR(20),
    day_of_month INTEGER,
    day_of_year INTEGER,
    
    -- Week
    week_of_year INTEGER,
    week_start_date DATE,
    week_end_date DATE,
    
    -- Month
    month_number INTEGER,
    month_name VARCHAR(20),
    month_abbrev VARCHAR(10),
    month_start_date DATE,
    month_end_date DATE,
    
    -- Quarter
    quarter_number INTEGER,
    quarter_name VARCHAR(10),  -- Q1, Q2, Q3, Q4
    quarter_start_date DATE,
    quarter_end_date DATE,
    
    -- Year
    year INTEGER,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    
    -- Flags
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100),
    is_business_day BOOLEAN,
    
    -- Relative periods
    is_current_day BOOLEAN,
    is_current_week BOOLEAN,
    is_current_month BOOLEAN,
    is_current_quarter BOOLEAN,
    is_current_year BOOLEAN
);

-- Generate date dimension data
INSERT INTO dim_date
SELECT
    TO_CHAR(date_value, 'YYYYMMDD')::INTEGER as date_key,
    date_value as full_date,
    EXTRACT(DOW FROM date_value) as day_of_week,
    TO_CHAR(date_value, 'Day') as day_of_week_name,
    EXTRACT(DAY FROM date_value) as day_of_month,
    EXTRACT(DOY FROM date_value) as day_of_year,
    EXTRACT(WEEK FROM date_value) as week_of_year,
    DATE_TRUNC('week', date_value) as week_start_date,
    DATE_TRUNC('week', date_value) + INTERVAL '6 days' as week_end_date,
    EXTRACT(MONTH FROM date_value) as month_number,
    TO_CHAR(date_value, 'Month') as month_name,
    TO_CHAR(date_value, 'Mon') as month_abbrev,
    DATE_TRUNC('month', date_value) as month_start_date,
    (DATE_TRUNC('month', date_value) + INTERVAL '1 month' - INTERVAL '1 day') as month_end_date,
    EXTRACT(QUARTER FROM date_value) as quarter_number,
    'Q' || EXTRACT(QUARTER FROM date_value) as quarter_name,
    DATE_TRUNC('quarter', date_value) as quarter_start_date,
    (DATE_TRUNC('quarter', date_value) + INTERVAL '3 months' - INTERVAL '1 day') as quarter_end_date,
    EXTRACT(YEAR FROM date_value) as year,
    CASE 
        WHEN EXTRACT(MONTH FROM date_value) >= 7 THEN EXTRACT(YEAR FROM date_value) + 1
        ELSE EXTRACT(YEAR FROM date_value)
    END as fiscal_year,
    CASE 
        WHEN EXTRACT(MONTH FROM date_value) >= 7 THEN EXTRACT(QUARTER FROM date_value)
        ELSE EXTRACT(QUARTER FROM date_value) + 2
    END as fiscal_quarter,
    CASE WHEN EXTRACT(DOW FROM date_value) IN (0,6) THEN TRUE ELSE FALSE END as is_weekend,
    FALSE as is_holiday,  -- Populate separately
    NULL as holiday_name,
    CASE WHEN EXTRACT(DOW FROM date_value) BETWEEN 1 AND 5 THEN TRUE ELSE FALSE END as is_business_day,
    date_value = CURRENT_DATE as is_current_day,
    DATE_TRUNC('week', date_value) = DATE_TRUNC('week', CURRENT_DATE) as is_current_week,
    DATE_TRUNC('month', date_value) = DATE_TRUNC('month', CURRENT_DATE) as is_current_month,
    DATE_TRUNC('quarter', date_value) = DATE_TRUNC('quarter', CURRENT_DATE) as is_current_quarter,
    EXTRACT(YEAR FROM date_value) = EXTRACT(YEAR FROM CURRENT_DATE) as is_current_year
FROM generate_series(
    '2020-01-01'::DATE,
    '2030-12-31'::DATE,
    '1 day'::INTERVAL
) as date_value;
```

**Verification:**
- [ ] All dimensions designed
- [ ] Attributes comprehensive
- [ ] Hierarchies included
- [ ] SCDs implemented correctly
- [ ] Indexes created

**If This Fails:**
→ Review business requirements
→ Interview end users
→ Analyze existing data
→ Start with core dimensions
→ Iterate based on usage

---

### Step 3: Design Fact Tables

**What:** Create fact tables with measures and foreign keys to dimensions

**How:**

**Order Fact Table (Transaction Fact):**
```sql
-- fct_order_line.sql
CREATE TABLE fct_order_line (
    -- Surrogate key (optional for fact tables)
    order_line_key BIGINT PRIMARY KEY,
    
    -- Foreign keys to dimensions
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    order_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    ship_date_key INTEGER REFERENCES dim_date(date_key),
    
    -- Degenerate dimensions (transaction identifiers)
    order_id VARCHAR(50) NOT NULL,
    order_line_number INTEGER NOT NULL,
    
    -- Additive measures (can be summed across all dimensions)
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    line_total DECIMAL(10,2) NOT NULL,
    cost_amount DECIMAL(10,2),
    profit_amount DECIMAL(10,2),
    
    -- Semi-additive measures (can't sum across time)
    -- None in this fact
    
    -- Non-additive measures (can't sum at all)
    unit_cost DECIMAL(10,2),
    profit_margin_percent DECIMAL(5,2),
    discount_percent DECIMAL(5,2),
    
    -- Audit columns
    etl_insert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    etl_update_date TIMESTAMP,
    source_system VARCHAR(50)
);

-- Indexes for common query patterns
CREATE INDEX idx_fct_order_customer ON fct_order_line(customer_key);
CREATE INDEX idx_fct_order_product ON fct_order_line(product_key);
CREATE INDEX idx_fct_order_date ON fct_order_line(order_date_key);
CREATE INDEX idx_fct_order_natural_key ON fct_order_line(order_id, order_line_number);

-- For BigQuery/Snowflake: Cluster by common filter columns
-- ALTER TABLE fct_order_line CLUSTER BY (order_date_key, customer_key);
```

**Daily Snapshot Fact Table:**
```sql
-- fct_inventory_daily.sql
CREATE TABLE fct_inventory_daily (
    -- Foreign keys
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    warehouse_key INTEGER NOT NULL REFERENCES dim_warehouse(warehouse_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    
    -- Semi-additive measures (can sum across product/warehouse, not time)
    quantity_on_hand INTEGER NOT NULL,
    quantity_on_order INTEGER DEFAULT 0,
    quantity_reserved INTEGER DEFAULT 0,
    quantity_available INTEGER NOT NULL,
    
    -- Additive measures (daily activity)
    quantity_received_today INTEGER DEFAULT 0,
    quantity_shipped_today INTEGER DEFAULT 0,
    quantity_adjusted_today INTEGER DEFAULT 0,
    
    -- Non-additive measures
    days_of_supply INTEGER,
    inventory_value DECIMAL(15,2),
    avg_unit_cost DECIMAL(10,2),
    
    -- Audit
    snapshot_date DATE NOT NULL,
    etl_insert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (product_key, warehouse_key, date_key)
);

CREATE INDEX idx_fct_inventory_date ON fct_inventory_daily(date_key);
```

**Accumulating Snapshot Fact:**
```sql
-- fct_order_fulfillment.sql
-- Tracks order lifecycle through multiple milestones
CREATE TABLE fct_order_fulfillment (
    order_key BIGINT PRIMARY KEY,
    
    -- Foreign keys to dimensions
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    
    -- Multiple date foreign keys for lifecycle events
    order_date_key INTEGER REFERENCES dim_date(date_key),
    payment_date_key INTEGER REFERENCES dim_date(date_key),
    ship_date_key INTEGER REFERENCES dim_date(date_key),
    delivery_date_key INTEGER REFERENCES dim_date(date_key),
    
    -- Degenerate dimension
    order_id VARCHAR(50) NOT NULL,
    
    -- Measures
    order_amount DECIMAL(10,2),
    
    -- Lag measures (days between milestones)
    days_to_payment INTEGER,
    days_to_ship INTEGER,
    days_to_delivery INTEGER,
    total_fulfillment_days INTEGER,
    
    -- Status
    current_status VARCHAR(50),
    is_fulfilled BOOLEAN DEFAULT FALSE,
    
    -- Audit
    etl_insert_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    etl_update_date TIMESTAMP  -- Updated as order progresses
);
```

**Verification:**
- [ ] Grain correct
- [ ] Measures appropriate
- [ ] Foreign keys defined
- [ ] Indexes created
- [ ] Partitioning considered

**If This Fails:**
→ Review grain definition
→ Validate measure calculations
→ Check dimension relationships
→ Verify data volumes
→ Test query performance

---

### Step 4: Implement Slowly Changing Dimensions

**What:** Handle dimension changes over time using SCD patterns

**How:**

**SCD Type 1 (Overwrite):**
```sql
-- Simply update the record
UPDATE dim_product
SET 
    product_name = 'New Product Name',
    list_price = 49.99,
    updated_date = CURRENT_TIMESTAMP
WHERE product_id = 'PROD-123'
  AND is_current = TRUE;
```

**SCD Type 2 (Track History):**
```sql
-- scd_type2_procedure.sql
CREATE OR REPLACE PROCEDURE update_customer_scd2(
    p_customer_id VARCHAR,
    p_customer_name VARCHAR,
    p_email VARCHAR,
    p_segment VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_existing_key INTEGER;
    v_new_key INTEGER;
    v_existing_hash VARCHAR;
    v_new_hash VARCHAR;
BEGIN
    -- Calculate hash of new values
    v_new_hash := MD5(
        COALESCE(p_customer_name, '') || '|' ||
        COALESCE(p_email, '') || '|' ||
        COALESCE(p_segment, '')
    );
    
    -- Get current record
    SELECT customer_key, row_hash
    INTO v_existing_key, v_existing_hash
    FROM dim_customer
    WHERE customer_id = p_customer_id
      AND is_current = TRUE;
    
    -- Check if data changed
    IF v_existing_hash != v_new_hash THEN
        -- Expire old record
        UPDATE dim_customer
        SET 
            is_current = FALSE,
            expiration_date = CURRENT_DATE - INTERVAL '1 day',
            updated_date = CURRENT_TIMESTAMP
        WHERE customer_key = v_existing_key;
        
        -- Insert new record
        INSERT INTO dim_customer (
            customer_id,
            customer_name,
            email,
            customer_segment,
            effective_date,
            expiration_date,
            is_current,
            version_number,
            row_hash
        )
        SELECT 
            p_customer_id,
            p_customer_name,
            p_email,
            p_segment,
            CURRENT_DATE,
            '9999-12-31'::DATE,
            TRUE,
            COALESCE(MAX(version_number), 0) + 1,
            v_new_hash
        FROM dim_customer
        WHERE customer_id = p_customer_id;
        
        RAISE NOTICE 'Created new version for customer %', p_customer_id;
    ELSE
        RAISE NOTICE 'No changes detected for customer %', p_customer_id;
    END IF;
END;
$$;
```

**SCD Type 3 (Previous Value Column):**
```sql
-- Add columns for previous values
ALTER TABLE dim_product ADD COLUMN previous_list_price DECIMAL(10,2);
ALTER TABLE dim_product ADD COLUMN price_change_date DATE;

-- Update with previous value tracking
UPDATE dim_product
SET 
    previous_list_price = list_price,
    list_price = 59.99,
    price_change_date = CURRENT_DATE,
    updated_date = CURRENT_TIMESTAMP
WHERE product_id = 'PROD-123';
```

**Verification:**
- [ ] SCD logic correct
- [ ] History preserved
- [ ] Current flag maintained
- [ ] Performance acceptable
- [ ] Tested with sample data

**If This Fails:**
→ Review SCD requirements
→ Test with edge cases
→ Check effective dating logic
→ Verify hash calculations
→ Monitor table growth

---

### Step 5: Create Data Mart Views

**What:** Build simplified views and aggregates for business users

**How:**

**Customer Analytics Mart:**
```sql
-- mart_customer_analytics.sql
CREATE VIEW mart_customer_analytics AS
SELECT
    c.customer_key,
    c.customer_id,
    c.customer_name,
    c.email,
    c.customer_segment,
    c.city,
    c.state,
    c.country,
    
    -- Order metrics
    COUNT(DISTINCT f.order_id) as lifetime_orders,
    SUM(f.line_total) as lifetime_revenue,
    AVG(f.line_total) as avg_order_value,
    
    -- Recency
    MAX(d.full_date) as last_order_date,
    DATEDIFF('day', MAX(d.full_date), CURRENT_DATE) as days_since_last_order,
    
    -- Frequency
    COUNT(DISTINCT EXTRACT(YEAR FROM d.full_date) || '-' || EXTRACT(MONTH FROM d.full_date)) as months_active,
    
    -- Product preferences
    STRING_AGG(DISTINCT p.category_level1, ', ') as preferred_categories

FROM dim_customer c
LEFT JOIN fct_order_line f ON c.customer_key = f.customer_key
LEFT JOIN dim_date d ON f.order_date_key = d.date_key
LEFT JOIN dim_product p ON f.product_key = p.product_key

WHERE c.is_current = TRUE

GROUP BY 
    c.customer_key,
    c.customer_id,
    c.customer_name,
    c.email,
    c.customer_segment,
    c.city,
    c.state,
    c.country;
```

**Sales Performance Mart:**
```sql
-- mart_sales_performance.sql
CREATE MATERIALIZED VIEW mart_sales_performance AS
SELECT
    d.year,
    d.quarter_name,
    d.month_name,
    d.full_date,
    
    p.category_level1 as department,
    p.category_level2 as category,
    
    c.country,
    c.customer_segment,
    
    -- Measures
    COUNT(DISTINCT f.order_id) as order_count,
    COUNT(*) as line_count,
    SUM(f.quantity) as units_sold,
    SUM(f.line_total) as revenue,
    SUM(f.cost_amount) as cost,
    SUM(f.profit_amount) as profit,
    AVG(f.unit_price) as avg_price,
    AVG(f.discount_percent) as avg_discount_pct

FROM fct_order_line f
INNER JOIN dim_date d ON f.order_date_key = d.date_key
INNER JOIN dim_product p ON f.product_key = p.product_key
INNER JOIN dim_customer c ON f.customer_key = c.customer_key

WHERE d.year >= 2020
  AND c.is_current = TRUE
  AND p.is_current = TRUE

GROUP BY
    d.year,
    d.quarter_name,
    d.month_name,
    d.full_date,
    p.category_level1,
    p.category_level2,
    c.country,
    c.customer_segment;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW mart_sales_performance;
```

**Verification:**
- [ ] Marts created
- [ ] Queries optimized
- [ ] Materialized views refreshed
- [ ] Performance tested
- [ ] Business logic validated

**If This Fails:**
→ Test underlying joins
→ Check for Cartesian products
→ Verify aggregations
→ Profile query performance
→ Consider pre-aggregation

---

## Verification Checklist

After completing this workflow:

- [ ] Business processes identified
- [ ] Grain defined clearly
- [ ] Dimensions designed
- [ ] Fact tables created
- [ ] SCDs implemented
- [ ] Data marts built
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Users trained

---

## Common Issues & Solutions

### Issue: Fact Table Growing Too Large

**Symptoms:**
- Queries slowing down
- Storage costs high
- ETL taking too long

**Solution:**
- Implement partitioning by date
- Use clustered indexes
- Archive old data
- Consider aggregate tables
- Use columnar storage

---

## Best Practices

### DO:
✅ Use star schema for simplicity
✅ Keep dimensions denormalized
✅ Implement date dimension
✅ Use surrogate keys for dimensions
✅ Document grain explicitly
✅ Partition large fact tables
✅ Create aggregate tables
✅ Use meaningful names
✅ Implement SCD appropriately
✅ Build data marts for users
✅ Monitor query patterns
✅ Version dimension changes

### DON'T:
❌ Over-normalize dimensions
❌ Create snowflake unnecessarily
❌ Mix grains in fact tables
❌ Skip slowly changing dimensions
❌ Forget about performance
❌ Create too many dimensions
❌ Ignore data quality
❌ Skip documentation
❌ Forget audit columns
❌ Create complex joins
❌ Ignore user requirements
❌ Skip testing queries

---

## Related Workflows

**Prerequisites:**
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture

**Next Steps:**
- [data_transformation_dbt.md](./data_transformation_dbt.md) - dbt modeling
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks

**Related:**
- [data_lake_architecture.md](./data_lake_architecture.md) - Data lakes
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL patterns

---

## Tags
`data-engineering` `data-warehouse` `modeling` `dimensional` `star-schema` `kimball` `sql` `analytics` `bi`
