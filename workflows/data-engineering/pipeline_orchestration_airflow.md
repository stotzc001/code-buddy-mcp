# Pipeline Orchestration with Airflow

**ID:** dat-009  
**Category:** Data Engineering  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** 60-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Orchestrate data pipelines using Apache Airflow to schedule, monitor, and manage complex workflows

**Why:** Airflow provides reliable scheduling, dependency management, monitoring, and error handling for data pipelines at scale

**When to use:**
- Scheduling batch data pipelines
- Managing complex workflow dependencies
- Implementing retry and failure handling
- Monitoring pipeline execution
- Creating dynamic workflows
- Building data platform automation

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ installed
- [ ] Basic understanding of DAG concepts
- [ ] SQL and Python knowledge
- [ ] Understanding of data pipeline concepts
- [ ] Database for Airflow metadata

**Check before starting:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check if Docker available (for local setup)
docker --version

# Verify pip
pip --version
```

---

## Implementation Steps

### Step 1: Install and Configure Airflow

**What:** Set up Apache Airflow locally or in production environment

**How:**

**Local Installation with Docker:**
```yaml
# docker-compose.yml
version: '3.8'

x-airflow-common:
  &airflow-common
  image: apache/airflow:2.7.3
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth'
    AIRFLOW__SCHEDULER__ENABLE_HEALTH_CHECK: 'true'
    _PIP_ADDITIONAL_REQUIREMENTS: apache-airflow-providers-amazon[s3] apache-airflow-providers-postgres
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./config/airflow.cfg:/opt/airflow/airflow.cfg
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    &airflow-common-depends-on
    redis:
      condition: service_healthy
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5
      start_period: 5s
    restart: always

  redis:
    image: redis:latest
    expose:
      - 6379
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 30s
      retries: 50
      start_period: 30s
    restart: always

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8974/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-worker:
    <<: *airflow-common
    command: celery worker
    healthcheck:
      test:
        - "CMD-SHELL"
        - 'celery --app airflow.executors.celery_executor.app inspect ping -d "celery@$${HOSTNAME}"'
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins}
        exec /entrypoint airflow version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow}
    user: "0:0"
    volumes:
      - .:/sources

volumes:
  postgres-db-volume:
```

**Start Airflow:**
```bash
# Set Airflow UID
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Initialize database
docker-compose up airflow-init

# Start all services
docker-compose up -d

# Access UI at http://localhost:8080
# Default credentials: airflow / airflow
```

**Production Configuration (airflow.cfg):**
```ini
[core]
# Executor
executor = CeleryExecutor
# or for Kubernetes
# executor = KubernetesExecutor

# DAG folder
dags_folder = /opt/airflow/dags

# Plugin folder
plugins_folder = /opt/airflow/plugins

# Parallelism settings
parallelism = 32
max_active_tasks_per_dag = 16
max_active_runs_per_dag = 3

# DAG processing
dagbag_import_timeout = 30
dag_file_processor_timeout = 50

[database]
sql_alchemy_conn = postgresql+psycopg2://airflow:${AIRFLOW_PASSWORD}@postgres:5432/airflow
sql_alchemy_pool_size = 5
sql_alchemy_max_overflow = 10

[scheduler]
# Scheduler settings
scheduler_heartbeat_sec = 5
num_runs = -1
processor_poll_interval = 1
min_file_process_interval = 30
dag_dir_list_interval = 300

# Health check
enable_health_check = True
health_check_threshold = 30

[webserver]
# Web server settings
base_url = http://airflow.company.com
web_server_port = 8080
web_server_worker_timeout = 120
workers = 4

# Authentication
auth_backend = airflow.contrib.auth.backends.password_auth

[celery]
# Celery settings
broker_url = redis://redis:6379/0
result_backend = db+postgresql://airflow:${AIRFLOW_PASSWORD}@postgres:5432/airflow
worker_concurrency = 16
worker_log_server_port = 8793

[logging]
# Logging configuration
base_log_folder = /opt/airflow/logs
remote_logging = True
remote_log_conn_id = aws_default
remote_base_log_folder = s3://airflow-logs/
encrypt_s3_logs = True

[smtp]
# Email configuration
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = airflow@company.com
smtp_password = ${SMTP_PASSWORD}
smtp_port = 587
smtp_mail_from = airflow@company.com
```

**Verification:**
- [ ] Airflow webserver accessible
- [ ] Scheduler running
- [ ] Workers healthy
- [ ] Database connected
- [ ] Example DAGs appear (if enabled)

**If This Fails:**
→ Check Docker logs: `docker-compose logs`
→ Verify ports not in use
→ Check database connection
→ Review firewall settings
→ Ensure sufficient resources

---

### Step 2: Create Your First DAG

**What:** Build a basic DAG to understand Airflow concepts

**How:**

**Basic DAG Structure:**
```python
# dags/hello_world_dag.py
"""
Simple Hello World DAG to demonstrate Airflow basics.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default arguments for all tasks
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

# Define Python function for task
def print_context(**context):
    """Print execution context."""
    print(f"Execution date: {context['execution_date']}")
    print(f"DAG run ID: {context['dag_run'].run_id}")
    print(f"Task instance: {context['task_instance']}")
    return "Success!"

# Create DAG
with DAG(
    'hello_world',
    default_args=default_args,
    description='A simple Hello World DAG',
    schedule_interval='@daily',  # Run once per day
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Don't backfill
    tags=['example', 'tutorial'],
    max_active_runs=1,
) as dag:
    
    # Task 1: Bash command
    task_hello = BashOperator(
        task_id='say_hello',
        bash_command='echo "Hello from Airflow!"',
    )
    
    # Task 2: Python function
    task_print_date = PythonOperator(
        task_id='print_date',
        python_callable=lambda: print(f"Current date: {datetime.now()}"),
    )
    
    # Task 3: Python function with context
    task_print_context = PythonOperator(
        task_id='print_context',
        python_callable=print_context,
        provide_context=True,
    )
    
    # Task 4: Final task
    task_goodbye = BashOperator(
        task_id='say_goodbye',
        bash_command='echo "Goodbye from Airflow!"',
    )
    
    # Define task dependencies
    task_hello >> [task_print_date, task_print_context] >> task_goodbye
```

**DAG Components Explained:**
```python
"""
Understanding DAG Components
"""

# 1. Default Args - Apply to all tasks
default_args = {
    'owner': 'data-team',           # Task owner
    'depends_on_past': False,       # Don't wait for previous runs
    'email': ['alerts@company.com'], # Email for notifications
    'email_on_failure': True,       # Send email on task failure
    'email_on_retry': False,        # Don't email on retry
    'retries': 3,                   # Number of retries
    'retry_delay': timedelta(minutes=5), # Wait between retries
    'execution_timeout': timedelta(hours=2), # Max task duration
    'sla': timedelta(hours=1),      # Service Level Agreement
}

# 2. DAG Parameters
dag = DAG(
    dag_id='my_pipeline',           # Unique DAG identifier
    description='ETL pipeline',      # Human-readable description
    schedule_interval='0 2 * * *',  # Cron: daily at 2 AM
    # schedule_interval='@hourly'   # Alternative: preset interval
    # schedule_interval=timedelta(hours=6) # Alternative: timedelta
    # schedule_interval=None        # Manual trigger only
    
    start_date=datetime(2024, 1, 1), # When DAG becomes active
    end_date=None,                    # Optional: when to stop
    catchup=False,                    # Don't backfill historical runs
    max_active_runs=1,                # Limit concurrent DAG runs
    tags=['production', 'etl'],       # Organize in UI
    default_view='graph',             # Default UI view
)

# 3. Task Dependencies
# Method 1: Bitshift operators
task_a >> task_b >> task_c  # Linear: a then b then c

# Method 2: Lists for parallel
task_a >> [task_b, task_c] >> task_d  # b and c run in parallel

# Method 3: set_downstream / set_upstream
task_a.set_downstream(task_b)
task_b.set_upstream(task_a)  # Same as above

# Method 4: Using lists for complex dependencies
task_a >> [task_b, task_c]
[task_b, task_c] >> task_d
```

**Verification:**
- [ ] DAG appears in Airflow UI
- [ ] No import errors
- [ ] Tasks visible in graph view
- [ ] Dependencies correct
- [ ] Schedule configured

**If This Fails:**
→ Check DAG file syntax: `python dags/hello_world_dag.py`
→ Review Airflow logs for import errors
→ Ensure file is in dags folder
→ Verify Python dependencies installed
→ Check for naming conflicts

---

### Step 3: Implement ETL Pipeline DAG

**What:** Create a production-ready ETL pipeline

**How:**

**Complete ETL DAG:**
```python
# dags/customer_etl_pipeline.py
"""
Customer Data ETL Pipeline
Extracts from Postgres, transforms in Python, loads to Snowflake
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.email import EmailOperator
from airflow.utils.trigger_rule import TriggerRule
import pandas as pd
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

def extract_customers(**context):
    """Extract customer data from PostgreSQL."""
    execution_date = context['execution_date']
    next_execution_date = context['next_execution_date']
    
    logger.info(f"Extracting customers from {execution_date} to {next_execution_date}")
    
    # Get PostgreSQL connection
    pg_hook = PostgresHook(postgres_conn_id='source_postgres')
    
    # Incremental query
    query = f"""
        SELECT 
            customer_id,
            email,
            first_name,
            last_name,
            phone,
            created_at,
            updated_at
        FROM customers
        WHERE updated_at >= '{execution_date}'
          AND updated_at < '{next_execution_date}'
    """
    
    # Execute and get DataFrame
    df = pg_hook.get_pandas_df(query)
    
    logger.info(f"Extracted {len(df)} customers")
    
    # Save to XCom (for small datasets) or file
    if len(df) < 10000:
        context['task_instance'].xcom_push(key='customer_data', value=df.to_dict('records'))
    else:
        # For larger datasets, save to file
        filename = f"/tmp/customers_{execution_date.date()}.parquet"
        df.to_parquet(filename)
        context['task_instance'].xcom_push(key='customer_file', value=filename)
    
    return len(df)

def transform_customers(**context):
    """Transform customer data."""
    task_instance = context['task_instance']
    
    # Get data from previous task
    customer_data = task_instance.xcom_pull(task_ids='extract_customers', key='customer_data')
    
    if not customer_data:
        # Try file path
        filename = task_instance.xcom_pull(task_ids='extract_customers', key='customer_file')
        df = pd.read_parquet(filename)
    else:
        df = pd.DataFrame(customer_data)
    
    logger.info(f"Transforming {len(df)} customers")
    
    # Clean and transform
    df['email'] = df['email'].str.lower().str.strip()
    df['phone'] = df['phone'].str.replace(r'[^0-9]', '', regex=True)
    df['full_name'] = df['first_name'] + ' ' + df['last_name']
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['customer_id'])
    
    # Add processing timestamp
    df['processed_at'] = datetime.now()
    
    # Validate
    df = df[df['email'].notna()]
    df = df[df['email'].str.contains('@')]
    
    logger.info(f"Transformed {len(df)} valid customers")
    
    # Save transformed data
    filename = f"/tmp/transformed_{context['execution_date'].date()}.parquet"
    df.to_parquet(filename)
    
    task_instance.xcom_push(key='transformed_file', value=filename)
    task_instance.xcom_push(key='record_count', value=len(df))
    
    return len(df)

def load_to_snowflake(**context):
    """Load transformed data to Snowflake."""
    task_instance = context['task_instance']
    
    # Get transformed data
    filename = task_instance.xcom_pull(task_ids='transform_customers', key='transformed_file')
    df = pd.read_parquet(filename)
    
    logger.info(f"Loading {len(df)} customers to Snowflake")
    
    # Get Snowflake connection
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    # Create staging table
    snowflake_hook.run("""
        CREATE TEMPORARY TABLE staging_customers LIKE dim_customers
    """)
    
    # Load to staging
    snowflake_hook.insert_rows(
        table='staging_customers',
        rows=df.values.tolist(),
        target_fields=df.columns.tolist()
    )
    
    # Merge to target
    snowflake_hook.run("""
        MERGE INTO dim_customers AS target
        USING staging_customers AS source
        ON target.customer_id = source.customer_id
        WHEN MATCHED THEN UPDATE SET
            email = source.email,
            first_name = source.first_name,
            last_name = source.last_name,
            phone = source.phone,
            full_name = source.full_name,
            updated_at = source.updated_at,
            processed_at = source.processed_at
        WHEN NOT MATCHED THEN INSERT (
            customer_id, email, first_name, last_name,
            phone, full_name, created_at, updated_at, processed_at
        ) VALUES (
            source.customer_id, source.email, source.first_name, source.last_name,
            source.phone, source.full_name, source.created_at, 
            source.updated_at, source.processed_at
        )
    """)
    
    logger.info("Successfully loaded to Snowflake")
    
    return len(df)

def validate_load(**context):
    """Validate data was loaded correctly."""
    task_instance = context['task_instance']
    expected_count = task_instance.xcom_pull(task_ids='transform_customers', key='record_count')
    
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    
    # Check row count
    result = snowflake_hook.get_first("""
        SELECT COUNT(*) 
        FROM dim_customers 
        WHERE processed_at >= CURRENT_DATE
    """)
    
    actual_count = result[0]
    
    logger.info(f"Expected: {expected_count}, Actual: {actual_count}")
    
    if actual_count < expected_count * 0.95:  # Allow 5% tolerance
        raise ValueError(f"Validation failed: expected ~{expected_count}, got {actual_count}")
    
    return True

# Create DAG
with DAG(
    'customer_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for customer data',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'customers', 'production'],
    max_active_runs=1,
) as dag:
    
    # Extract task
    extract_task = PythonOperator(
        task_id='extract_customers',
        python_callable=extract_customers,
        provide_context=True,
    )
    
    # Transform task
    transform_task = PythonOperator(
        task_id='transform_customers',
        python_callable=transform_customers,
        provide_context=True,
    )
    
    # Load task
    load_task = PythonOperator(
        task_id='load_to_snowflake',
        python_callable=load_to_snowflake,
        provide_context=True,
    )
    
    # Validation task
    validate_task = PythonOperator(
        task_id='validate_load',
        python_callable=validate_load,
        provide_context=True,
    )
    
    # Success notification
    success_email = EmailOperator(
        task_id='send_success_email',
        to='data-team@company.com',
        subject='Customer ETL Success - {{ ds }}',
        html_content="""
        <h3>Customer ETL Pipeline Completed Successfully</h3>
        <p>Execution Date: {{ ds }}</p>
        <p>Records Processed: {{ task_instance.xcom_pull(task_ids='transform_customers', key='record_count') }}</p>
        """,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )
    
    # Failure notification
    failure_email = EmailOperator(
        task_id='send_failure_email',
        to='data-alerts@company.com',
        subject='Customer ETL FAILED - {{ ds }}',
        html_content="""
        <h3>Customer ETL Pipeline Failed</h3>
        <p>Execution Date: {{ ds }}</p>
        <p>Check logs for details</p>
        """,
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    
    # Define task dependencies
    extract_task >> transform_task >> load_task >> validate_task
    validate_task >> [success_email, failure_email]
```

**Verification:**
- [ ] DAG runs successfully
- [ ] Data extracted correctly
- [ ] Transformations applied
- [ ] Data loaded to target
- [ ] Validation passes
- [ ] Notifications sent

**If This Fails:**
→ Check connections in Airflow UI
→ Verify credentials in Connections
→ Test database connectivity
→ Review task logs
→ Check for data quality issues

---

### Step 4: Implement Advanced DAG Patterns

**What:** Use advanced Airflow features for complex workflows

**How:**

**Pattern 1: Dynamic Task Generation:**
```python
"""
Generate tasks dynamically based on configuration
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def process_table(table_name, **context):
    """Process a specific table."""
    print(f"Processing table: {table_name}")
    # Implementation here
    return f"Processed {table_name}"

# Configuration
TABLES_TO_PROCESS = ['customers', 'orders', 'products', 'inventory']

with DAG(
    'dynamic_table_processing',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    # Dynamically create tasks
    tasks = {}
    for table in TABLES_TO_PROCESS:
        task = PythonOperator(
            task_id=f'process_{table}',
            python_callable=process_table,
            op_kwargs={'table_name': table},
        )
        tasks[table] = task
    
    # Set up dependencies
    # All tables processed in parallel
    # Or create dependencies:
    tasks['customers'] >> tasks['orders']  # Orders depends on customers
```

**Pattern 2: Branching:**
```python
"""
Branch execution based on conditions
"""

from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator

def decide_branch(**context):
    """Decide which branch to take."""
    execution_date = context['execution_date']
    
    # Example: weekend vs weekday processing
    if execution_date.weekday() >= 5:  # Weekend
        return 'weekend_processing'
    else:
        return 'weekday_processing'

with DAG('branching_dag', ...) as dag:
    
    branch_task = BranchPythonOperator(
        task_id='branch_decision',
        python_callable=decide_branch,
        provide_context=True,
    )
    
    weekend_task = PythonOperator(
        task_id='weekend_processing',
        python_callable=process_weekend_data,
    )
    
    weekday_task = PythonOperator(
        task_id='weekday_processing',
        python_callable=process_weekday_data,
    )
    
    join_task = DummyOperator(
        task_id='join',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )
    
    branch_task >> [weekend_task, weekday_task] >> join_task
```

**Pattern 3: SubDAGs:**
```python
"""
Organize complex workflows with SubDAGs
"""

from airflow.operators.subdag import SubDagOperator
from airflow.utils.task_group import TaskGroup

# Better alternative: TaskGroup (recommended over SubDAG)
with DAG('main_dag', ...) as dag:
    
    start = DummyOperator(task_id='start')
    
    # Group related tasks
    with TaskGroup('data_quality_checks') as quality_group:
        
        check_nulls = PythonOperator(
            task_id='check_nulls',
            python_callable=check_null_values,
        )
        
        check_duplicates = PythonOperator(
            task_id='check_duplicates',
            python_callable=check_duplicate_records,
        )
        
        check_formats = PythonOperator(
            task_id='check_formats',
            python_callable=check_data_formats,
        )
        
        # Tasks within group
        [check_nulls, check_duplicates, check_formats]
    
    end = DummyOperator(task_id='end')
    
    start >> quality_group >> end
```

**Pattern 4: Sensor Tasks:**
```python
"""
Wait for external conditions with Sensors
"""

from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

with DAG('sensor_example', ...) as dag:
    
    # Wait for file to appear
    wait_for_file = FileSensor(
        task_id='wait_for_data_file',
        filepath='/data/input/data.csv',
        poke_interval=60,  # Check every 60 seconds
        timeout=3600,      # Give up after 1 hour
        mode='poke',       # or 'reschedule'
    )
    
    # Wait for S3 object
    wait_for_s3 = S3KeySensor(
        task_id='wait_for_s3_file',
        bucket_name='data-bucket',
        bucket_key='raw/data_{{ ds }}.parquet',
        aws_conn_id='aws_default',
        poke_interval=300,
        timeout=7200,
    )
    
    # Wait for another DAG to complete
    wait_for_upstream = ExternalTaskSensor(
        task_id='wait_for_upstream_dag',
        external_dag_id='upstream_pipeline',
        external_task_id='final_task',
        execution_delta=timedelta(hours=1),
        poke_interval=60,
        timeout=3600,
    )
    
    # Process after sensors succeed
    process_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    [wait_for_file, wait_for_s3, wait_for_upstream] >> process_task
```

**Pattern 5: Trigger Rules:**
```python
"""
Control task execution with trigger rules
"""

from airflow.utils.trigger_rule import TriggerRule

with DAG('trigger_rules_example', ...) as dag:
    
    task_a = PythonOperator(task_id='task_a', ...)
    task_b = PythonOperator(task_id='task_b', ...)
    task_c = PythonOperator(task_id='task_c', ...)
    
    # Run only if ALL upstream tasks succeed (default)
    cleanup_success = PythonOperator(
        task_id='cleanup_success',
        python_callable=cleanup_temp_files,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )
    
    # Run if ANY upstream task fails
    alert_failure = PythonOperator(
        task_id='alert_failure',
        python_callable=send_failure_alert,
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    
    # Run if AT LEAST ONE upstream succeeds
    partial_success = PythonOperator(
        task_id='partial_success',
        python_callable=handle_partial_success,
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )
    
    # ALWAYS run (even if upstream fails)
    always_cleanup = PythonOperator(
        task_id='always_cleanup',
        python_callable=final_cleanup,
        trigger_rule=TriggerRule.ALL_DONE,
    )
    
    [task_a, task_b, task_c] >> cleanup_success
    [task_a, task_b, task_c] >> alert_failure
    [task_a, task_b, task_c] >> partial_success
    [task_a, task_b, task_c] >> always_cleanup
```

**Verification:**
- [ ] Dynamic tasks generated
- [ ] Branching logic correct
- [ ] Task groups organized
- [ ] Sensors waiting appropriately
- [ ] Trigger rules working

**If This Fails:**
→ Test logic in isolation
→ Check task dependencies
→ Review trigger rules
→ Verify sensor timeouts reasonable
→ Check for circular dependencies

---

### Step 5: Implement Monitoring and Alerting

**What:** Set up comprehensive monitoring and alerting

**How:**

**Custom Alerting:**
```python
"""
Implement custom alerting callbacks
"""

from airflow.models import TaskInstance
from airflow.utils.email import send_email
import requests

def task_success_callback(context):
    """Called when task succeeds."""
    task_instance: TaskInstance = context['task_instance']
    
    message = f"""
    Task {task_instance.task_id} succeeded!
    DAG: {task_instance.dag_id}
    Execution Date: {context['execution_date']}
    Duration: {task_instance.duration} seconds
    """
    
    print(message)
    # Could send to Slack, PagerDuty, etc.

def task_failure_callback(context):
    """Called when task fails."""
    task_instance: TaskInstance = context['task_instance']
    
    message = f"""
    ⚠️ ALERT: Task Failed
    Task: {task_instance.task_id}
    DAG: {task_instance.dag_id}
    Execution Date: {context['execution_date']}
    Exception: {context.get('exception')}
    Log URL: {task_instance.log_url}
    """
    
    # Send to Slack
    send_slack_alert(message)
    
    # Send email
    send_email(
        to='data-oncall@company.com',
        subject=f'Airflow Task Failed: {task_instance.task_id}',
        html_content=message
    )

def dag_success_callback(context):
    """Called when entire DAG succeeds."""
    dag_run = context['dag_run']
    
    message = f"""
    ✅ DAG Completed Successfully
    DAG: {dag_run.dag_id}
    Execution Date: {context['execution_date']}
    Duration: {dag_run.duration} seconds
    """
    
    send_slack_alert(message, channel='#data-success')

def send_slack_alert(message, channel='#data-alerts'):
    """Send alert to Slack."""
    webhook_url = Variable.get('slack_webhook_url')
    
    payload = {
        'channel': channel,
        'text': message,
        'username': 'Airflow Bot',
        'icon_emoji': ':airflow:'
    }
    
    requests.post(webhook_url, json=payload)

# Use in DAG
with DAG(
    'monitored_pipeline',
    on_success_callback=dag_success_callback,
    default_args={
        'on_failure_callback': task_failure_callback,
        'on_success_callback': task_success_callback,
    }
) as dag:
    
    task = PythonOperator(
        task_id='important_task',
        python_callable=critical_operation,
        # Can override at task level
        on_failure_callback=lambda ctx: escalate_to_oncall(ctx),
    )
```

**SLA Monitoring:**
```python
"""
Set up SLA monitoring
"""

from datetime import timedelta

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Called when SLA is missed."""
    message = f"""
    ⚠️ SLA Miss Alert
    DAG: {dag.dag_id}
    Tasks: {[task.task_id for task in task_list]}
    """
    
    send_slack_alert(message, channel='#data-sla-alerts')
    
    # Could escalate to PagerDuty
    trigger_pagerduty_incident(message)

with DAG(
    'sla_monitored_pipeline',
    sla_miss_callback=sla_miss_callback,
    default_args={
        'sla': timedelta(hours=2),  # Tasks should complete in 2 hours
    }
) as dag:
    
    # This task has specific SLA
    critical_task = PythonOperator(
        task_id='critical_task',
        python_callable=process_data,
        sla=timedelta(minutes=30),  # Override: 30 min SLA
    )
```

**Custom Metrics:**
```python
"""
Track custom metrics with StatsD
"""

from airflow.stats import Stats

def process_with_metrics(**context):
    """Process data and track metrics."""
    start_time = time.time()
    
    try:
        # Process data
        records = extract_data()
        
        # Track metrics
        Stats.gauge('custom.records_processed', len(records))
        Stats.incr('custom.pipeline_runs')
        
        # Process
        result = transform_data(records)
        
        duration = time.time() - start_time
        Stats.timing('custom.processing_duration', duration)
        
        return result
        
    except Exception as e:
        Stats.incr('custom.pipeline_failures')
        raise
```

**Verification:**
- [ ] Alerts configured
- [ ] SLAs set
- [ ] Metrics tracked
- [ ] Notifications working
- [ ] Dashboard updated

**If This Fails:**
→ Test callback functions
→ Verify webhook URLs
→ Check email configuration
→ Review SLA thresholds
→ Validate metrics format

---

### Step 6: Optimize Performance

**What:** Improve DAG and task performance

**How:**

**Performance Best Practices:**
```python
"""
Optimize Airflow Performance
"""

# 1. Use connection pooling
from airflow.providers.postgres.hooks.postgres import PostgresHook

def efficient_database_access():
    """Use connection pooling efficiently."""
    # Reuse connections
    hook = PostgresHook(postgres_conn_id='my_db')
    
    # Use bulk operations
    hook.insert_rows(
        table='customers',
        rows=data,  # List of tuples
        target_fields=['id', 'name', 'email']
    )

# 2. Parallelize independent tasks
with DAG('parallel_processing', ...) as dag:
    
    start = DummyOperator(task_id='start')
    
    # These can run in parallel
    tasks = []
    for table in ['customers', 'orders', 'products']:
        task = PythonOperator(
            task_id=f'process_{table}',
            python_callable=process_table,
            op_kwargs={'table': table},
            pool='data_processing',  # Use pool to limit concurrency
        )
        tasks.append(task)
        start >> task

# 3. Use XCom efficiently
def pass_large_data(**context):
    """For large data, use file storage instead of XCom."""
    # ❌ BAD: Large data in XCom
    # context['task_instance'].xcom_push(key='data', value=large_df)
    
    # ✅ GOOD: Use file storage
    filename = f"/tmp/data_{context['execution_date']}.parquet"
    large_df.to_parquet(filename)
    context['task_instance'].xcom_push(key='filename', value=filename)

# 4. Configure pools for resource management
# UI: Admin > Pools
# Or via CLI: airflow pools set data_processing 10 "Data processing pool"

# 5. Use appropriate executors
# LocalExecutor: Single machine, good for development
# CeleryExecutor: Distributed, good for production
# KubernetesExecutor: Dynamic scaling with Kubernetes

# 6. Optimize DAG loading
# Keep DAG files simple
# Avoid expensive operations in DAG definition
# Use dag_discovery_safe_mode = False for faster parsing

# 7. Use smart sensors (Airflow 2.2+)
from airflow.sensors.base import BaseSensorOperator

sensor = S3KeySensor(
    task_id='wait_for_file',
    bucket_name='my-bucket',
    bucket_key='data.csv',
    mode='reschedule',  # Better than 'poke' for long waits
    poke_interval=300,
)
```

**Verification:**
- [ ] DAGs parse quickly
- [ ] Tasks run in parallel
- [ ] Pools configured
- [ ] XCom usage optimized
- [ ] Executor appropriate

**If This Fails:**
→ Profile DAG parsing time
→ Review task dependencies
→ Check pool configurations
→ Monitor resource usage
→ Consider upgrading Airflow

---

## Verification Checklist

After completing this workflow:

- [ ] Airflow installed and running
- [ ] Basic DAGs created
- [ ] ETL pipeline implemented
- [ ] Advanced patterns used
- [ ] Monitoring configured
- [ ] Alerts working
- [ ] Performance optimized
- [ ] Team trained on Airflow

---

## Common Issues & Solutions

### Issue: DAG Not Appearing in UI

**Symptoms:**
- DAG file in dags folder but not visible
- Import errors in logs

**Solution:**
```bash
# Check for Python errors
python dags/my_dag.py

# Check Airflow logs
docker-compose logs airflow-scheduler

# List DAGs via CLI
airflow dags list

# Test DAG
airflow dags test my_dag 2024-01-01
```

**Prevention:**
- Validate syntax before deploying
- Use DAG validation in CI/CD
- Monitor scheduler logs

---

### Issue: Tasks Taking Too Long

**Symptoms:**
- Tasks timing out
- Long execution times
- Resource exhaustion

**Solution:**
```python
# 1. Increase timeout
task = PythonOperator(
    task_id='long_task',
    python_callable=process_data,
    execution_timeout=timedelta(hours=4),
)

# 2. Break into smaller tasks
# Instead of one large task, create pipeline:
extract >> transform >> load

# 3. Use appropriate resources
task = PythonOperator(
    task_id='heavy_task',
    python_callable=process_large_data,
    executor_config={
        "KubernetesExecutor": {
            "request_memory": "4Gi",
            "request_cpu": "2",
        }
    }
)
```

**Prevention:**
- Profile task execution
- Set reasonable timeouts
- Monitor resource usage
- Optimize queries and transformations

---

## Best Practices

### DO:
✅ Use meaningful task and DAG IDs
✅ Set appropriate retry policies
✅ Implement proper error handling
✅ Use connections for credentials
✅ Set SLAs for critical tasks
✅ Monitor DAG performance
✅ Version control DAGs
✅ Document complex workflows
✅ Use task groups for organization
✅ Test DAGs before deploying
✅ Implement alerting
✅ Use pools for resource management

### DON'T:
❌ Store credentials in code
❌ Use expensive operations in DAG definition
❌ Create very large DAGs
❌ Ignore failed tasks
❌ Skip monitoring setup
❌ Use heavy computations in Airflow
❌ Create circular dependencies
❌ Forget about timezones
❌ Overuse XCom for large data
❌ Skip documentation
❌ Deploy without testing
❌ Ignore performance issues

---

## Related Workflows

**Prerequisites:**
- [etl_pipeline_design.md](./etl_pipeline_design.md) - ETL patterns
- [data_pipeline_architecture.md](./data_pipeline_architecture.md) - Architecture

**Next Steps:**
- [data_quality_validation.md](./data_quality_validation.md) - Quality checks
- [data_transformation_dbt.md](./data_transformation_dbt.md) - SQL transforms

**Related:**
- [../devops/cicd_pipeline_setup.md](../devops/cicd_pipeline_setup.md) - CI/CD for DAGs
- [../devops/application_monitoring_setup.md](../devops/application_monitoring_setup.md) - Monitoring

---

## Tags
`data-engineering` `airflow` `orchestration` `scheduling` `workflows` `dag` `etl` `automation` `python`
