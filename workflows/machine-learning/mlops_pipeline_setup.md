# MLOps Pipeline Setup

**ID:** mac-006  
**Category:** Machine Learning  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Build end-to-end MLOps pipelines for automated model training, validation, deployment, and monitoring

**Why:** MLOps automates ML workflows, ensures reproducibility, enables continuous delivery of models, and maintains production model quality

**When to use:**
- Automating ML model lifecycle
- Deploying models to production
- Continuous training and deployment
- Ensuring model reproducibility
- Managing multiple model versions
- Scaling ML operations
- Implementing CI/CD for ML
- Monitoring model performance

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ with MLflow, DVC, Airflow
- [ ] Docker installed
- [ ] Kubernetes basics (optional)
- [ ] CI/CD understanding
- [ ] Cloud platform access (AWS/GCP/Azure)
- [ ] Git version control

**Check before starting:**
```bash
# Check installations
docker --version
python --version
pip show mlflow dvc airflow

# Verify Git
git --version

# Check cloud CLI
aws --version  # or gcloud, az
```

---

## Implementation Steps

### Step 1: Set Up MLflow Tracking and Model Registry

**What:** Configure MLflow as the central ML tracking and model registry system

**How:**

**MLflow Setup:**
```yaml
# docker-compose-mlflow.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow
      POSTGRES_DB: mlflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mlflow"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    depends_on:
      postgres:
        condition: service_healthy
      minio:
        condition: service_healthy
    environment:
      MLFLOW_BACKEND_STORE_URI: postgresql://mlflow:mlflow@postgres:5432/mlflow
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minio
      AWS_SECRET_ACCESS_KEY: minio123
    ports:
      - "5000:5000"
    command: >
      mlflow server
      --backend-store-uri postgresql://mlflow:mlflow@postgres:5432/mlflow
      --default-artifact-root s3://mlflow/
      --host 0.0.0.0
      --port 5000
    volumes:
      - mlflow_data:/mlflow

volumes:
  postgres_data:
  minio_data:
  mlflow_data:
```

```bash
# Start MLflow infrastructure
docker-compose -f docker-compose-mlflow.yml up -d

# Create MinIO bucket
docker exec mlflow-minio-1 mc alias set myminio http://localhost:9000 minio minio123
docker exec mlflow-minio-1 mc mb myminio/mlflow

# Verify
curl http://localhost:5000/health
```

**MLflow Integration:**
```python
# src/mlops/mlflow_config.py
"""
MLflow configuration and utilities
"""

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import os

class MLflowManager:
    """Manage MLflow tracking and registry."""
    
    def __init__(self, tracking_uri="http://localhost:5000"):
        """Initialize MLflow manager."""
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient(tracking_uri)
        
    def create_experiment(self, name, tags=None):
        """Create or get experiment."""
        try:
            experiment_id = mlflow.create_experiment(name, tags=tags)
        except Exception:
            experiment_id = mlflow.get_experiment_by_name(name).experiment_id
        
        mlflow.set_experiment(name)
        return experiment_id
    
    def log_model_with_signature(self, model, artifact_path, signature, input_example=None):
        """Log model with signature."""
        mlflow.sklearn.log_model(
            model,
            artifact_path,
            signature=signature,
            input_example=input_example
        )
    
    def register_model(self, model_uri, name, tags=None):
        """Register model in model registry."""
        result = mlflow.register_model(model_uri, name)
        
        if tags:
            for key, value in tags.items():
                self.client.set_model_version_tag(name, result.version, key, value)
        
        return result
    
    def transition_model_stage(self, name, version, stage):
        """Transition model to stage (Staging/Production/Archived)."""
        self.client.transition_model_version_stage(
            name=name,
            version=version,
            stage=stage
        )
    
    def get_production_model(self, name):
        """Get current production model."""
        versions = self.client.get_latest_versions(name, stages=["Production"])
        if versions:
            return versions[0]
        return None

# Usage
mlflow_manager = MLflowManager()
experiment_id = mlflow_manager.create_experiment(
    "credit_risk_model",
    tags={"project": "credit_scoring", "team": "data_science"}
)
```

**Verification:**
- [ ] MLflow running
- [ ] Postgres connected
- [ ] MinIO artifact storage working
- [ ] Experiments tracked
- [ ] Models registered

**If This Fails:**
→ Check Docker containers
→ Verify port availability
→ Review database connection
→ Check MinIO credentials
→ Review MLflow logs

---

### Step 2: Implement Data Version Control with DVC

**What:** Set up DVC for data and model versioning

**How:**

**DVC Setup:**
```bash
# Initialize DVC
cd /path/to/project
dvc init

# Configure remote storage (S3)
dvc remote add -d myremote s3://my-bucket/dvc-storage
dvc remote modify myremote region us-east-1

# Or use local remote for testing
dvc remote add -d myremote /path/to/local/storage

# Configure credentials
dvc remote modify myremote access_key_id YOUR_AWS_ACCESS_KEY
dvc remote modify myremote secret_access_key YOUR_AWS_SECRET_KEY
```

**Track Data with DVC:**
```bash
# Track datasets
dvc add data/raw/train.csv
dvc add data/raw/test.csv
dvc add data/processed/features.parquet

# Track models
dvc add models/model.pkl

# Commit DVC files
git add data/.gitignore data/raw/train.csv.dvc
git add models/.gitignore models/model.pkl.dvc
git commit -m "Track data and models with DVC"

# Push to remote storage
dvc push
```

**DVC Pipeline:**
```yaml
# dvc.yaml
stages:
  prepare:
    cmd: python src/data/prepare.py
    deps:
      - src/data/prepare.py
      - data/raw/train.csv
    params:
      - prepare.test_split
      - prepare.random_state
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  featurize:
    cmd: python src/features/build_features.py
    deps:
      - src/features/build_features.py
      - data/processed/train.csv
      - data/processed/test.csv
    params:
      - featurize.max_features
      - featurize.ngrams
    outs:
      - data/processed/train_features.pkl
      - data/processed/test_features.pkl

  train:
    cmd: python src/models/train.py
    deps:
      - src/models/train.py
      - data/processed/train_features.pkl
    params:
      - train.n_estimators
      - train.max_depth
      - train.learning_rate
    outs:
      - models/model.pkl
    metrics:
      - metrics/train_metrics.json:
          cache: false

  evaluate:
    cmd: python src/models/evaluate.py
    deps:
      - src/models/evaluate.py
      - models/model.pkl
      - data/processed/test_features.pkl
    metrics:
      - metrics/test_metrics.json:
          cache: false
    plots:
      - plots/confusion_matrix.png
      - plots/roc_curve.png
```

```yaml
# params.yaml
prepare:
  test_split: 0.2
  random_state: 42

featurize:
  max_features: 100
  ngrams: 2

train:
  n_estimators: 100
  max_depth: 10
  learning_rate: 0.1
```

```bash
# Run pipeline
dvc repro

# View metrics
dvc metrics show

# Compare experiments
dvc params diff
dvc metrics diff
```

**Verification:**
- [ ] DVC initialized
- [ ] Remote storage configured
- [ ] Data tracked
- [ ] Pipeline defined
- [ ] Experiments reproducible

**If This Fails:**
→ Check DVC installation
→ Verify remote storage access
→ Review pipeline dependencies
→ Check file paths
→ Review DVC logs

---

### Step 3: Create Automated Training Pipeline with Airflow

**What:** Build Airflow DAGs for automated model training

**How:**

**Airflow DAG for ML Pipeline:**
```python
# dags/ml_training_pipeline.py
"""
Airflow DAG for automated ML training
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import mlflow
import pandas as pd
import joblib

default_args = {
    'owner': 'data-science-team',
    'depends_on_past': False,
    'email': ['ml-team@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_training_pipeline',
    default_args=default_args,
    description='Automated ML model training pipeline',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'training'],
)

def extract_data(**context):
    """Extract data from source."""
    # Extract data logic
    import pandas as pd
    
    # Simulate data extraction
    df = pd.read_csv('s3://my-bucket/data/latest.csv')
    
    # Save locally
    df.to_csv('/tmp/raw_data.csv', index=False)
    
    # Push metadata to XCom
    context['ti'].xcom_push(key='row_count', value=len(df))
    context['ti'].xcom_push(key='data_path', value='/tmp/raw_data.csv')

def validate_data(**context):
    """Validate data quality."""
    data_path = context['ti'].xcom_pull(key='data_path')
    df = pd.read_csv(data_path)
    
    # Validation checks
    assert df.isnull().sum().sum() < len(df) * 0.1, "Too many missing values"
    assert len(df) > 1000, "Insufficient data"
    
    print(f"✅ Data validation passed: {len(df)} rows")

def preprocess_data(**context):
    """Preprocess data."""
    data_path = context['ti'].xcom_pull(key='data_path')
    df = pd.read_csv(data_path)
    
    # Preprocessing logic
    # ... (your preprocessing code)
    
    # Save processed data
    df.to_csv('/tmp/processed_data.csv', index=False)
    context['ti'].xcom_push(key='processed_path', value='/tmp/processed_data.csv')

def train_model(**context):
    """Train ML model."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    
    processed_path = context['ti'].xcom_pull(key='processed_path')
    df = pd.read_csv(processed_path)
    
    X = df.drop('target', axis=1)
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Start MLflow run
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("credit_risk_model")
    
    with mlflow.start_run():
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))
        
        # Log to MLflow
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("train_accuracy", train_acc)
        mlflow.log_metric("test_accuracy", test_acc)
        mlflow.sklearn.log_model(model, "model")
        
        # Save model locally
        model_path = '/tmp/model.pkl'
        joblib.dump(model, model_path)
        
        context['ti'].xcom_push(key='model_path', value=model_path)
        context['ti'].xcom_push(key='test_accuracy', value=test_acc)
        
        print(f"✅ Model trained - Test Accuracy: {test_acc:.4f}")

def evaluate_model(**context):
    """Evaluate model against production baseline."""
    test_accuracy = context['ti'].xcom_pull(key='test_accuracy')
    
    # Get production model baseline
    production_baseline = 0.85  # Should be fetched from model registry
    
    if test_accuracy >= production_baseline:
        print(f"✅ Model passed evaluation: {test_accuracy:.4f} >= {production_baseline:.4f}")
        return 'deploy_model'
    else:
        print(f"❌ Model failed evaluation: {test_accuracy:.4f} < {production_baseline:.4f}")
        return 'alert_team'

def deploy_model(**context):
    """Deploy model to staging."""
    model_path = context['ti'].xcom_pull(key='model_path')
    
    # Copy to deployment location
    import shutil
    shutil.copy(model_path, '/deployment/staging/model.pkl')
    
    print("✅ Model deployed to staging")

def alert_team(**context):
    """Send alert to team."""
    test_accuracy = context['ti'].xcom_pull(key='test_accuracy')
    
    # Send alert (email, Slack, etc.)
    print(f"⚠️ Model performance below threshold: {test_accuracy:.4f}")

# Define tasks
extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

preprocess = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    dag=dag,
)

train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

evaluate = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    dag=dag,
)

deploy = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag,
)

alert = PythonOperator(
    task_id='alert_team',
    python_callable=alert_team,
    dag=dag,
)

# Define dependencies
extract >> validate >> preprocess >> train >> evaluate
evaluate >> [deploy, alert]
```

**Verification:**
- [ ] Airflow DAG created
- [ ] Tasks defined
- [ ] Dependencies correct
- [ ] Schedulable
- [ ] Error handling in place

**If This Fails:**
→ Check Airflow installation
→ Verify DAG syntax
→ Review task dependencies
→ Check Airflow logs
→ Test tasks individually

---

### Step 4: Implement CI/CD for ML Models

**What:** Set up continuous integration and deployment for ML models

**How:**

**GitHub Actions Workflow:**
```yaml
# .github/workflows/ml-ci-cd.yml
name: ML CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  data-validation:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Pull data with DVC
        run: |
          dvc pull
      
      - name: Validate data
        run: |
          python src/data/validate.py

  train-model:
    runs-on: ubuntu-latest
    needs: data-validation
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Pull data
        run: dvc pull
      
      - name: Train model
        run: |
          python src/models/train.py
      
      - name: Evaluate model
        run: |
          python src/models/evaluate.py
      
      - name: Upload model artifacts
        uses: actions/upload-artifact@v3
        with:
          name: model
          path: models/

  deploy-staging:
    runs-on: ubuntu-latest
    needs: train-model
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v3
      
      - name: Download model
        uses: actions/download-artifact@v3
        with:
          name: model
          path: models/
      
      - name: Deploy to staging
        run: |
          # Deploy to staging environment
          aws s3 cp models/model.pkl s3://ml-models-staging/
          
      - name: Update model registry
        run: |
          python scripts/register_model.py --stage staging

  deploy-production:
    runs-on: ubuntu-latest
    needs: train-model
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.production.example.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Download model
        uses: actions/download-artifact@v3
        with:
          name: model
          path: models/
      
      - name: Deploy to production
        run: |
          # Deploy to production
          aws s3 cp models/model.pkl s3://ml-models-production/
      
      - name: Update model registry
        run: |
          python scripts/register_model.py --stage production
      
      - name: Run smoke tests
        run: |
          python tests/smoke_tests.py
```

**Model Registry Script:**
```python
# scripts/register_model.py
"""
Register model in MLflow registry
"""

import mlflow
from mlflow.tracking import MlflowClient
import argparse

def register_model(stage='staging'):
    """Register model in MLflow."""
    mlflow.set_tracking_uri("http://mlflow:5000")
    client = MlflowClient()
    
    # Get latest run
    experiment = client.get_experiment_by_name("credit_risk_model")
    runs = client.search_runs(experiment.experiment_id, order_by=["start_time DESC"], max_results=1)
    
    if not runs:
        raise ValueError("No runs found")
    
    run = runs[0]
    model_uri = f"runs:/{run.info.run_id}/model"
    
    # Register model
    result = mlflow.register_model(model_uri, "credit_risk_model")
    
    # Transition to stage
    client.transition_model_version_stage(
        name="credit_risk_model",
        version=result.version,
        stage=stage.capitalize()
    )
    
    print(f"✅ Model registered: version {result.version}, stage {stage}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', default='staging', choices=['staging', 'production'])
    args = parser.parse_args()
    
    register_model(args.stage)
```

**Verification:**
- [ ] CI/CD pipeline configured
- [ ] Tests running
- [ ] Model training automated
- [ ] Deployment automated
- [ ] Staging and production separated

**If This Fails:**
→ Check GitHub Actions syntax
→ Verify secrets configured
→ Review workflow logs
→ Test locally first
→ Check permissions

---

### Step 5: Implement Model Monitoring and Retraining

**What:** Set up automated model monitoring and retraining triggers

**How:**

**Monitoring System:**
```python
# src/mlops/monitoring.py
"""
Model monitoring and drift detection
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from datetime import datetime
import mlflow

class ModelMonitor:
    """Monitor model performance and data drift."""
    
    def __init__(self, model_name, baseline_data):
        self.model_name = model_name
        self.baseline_data = baseline_data
        self.baseline_stats = self._calculate_stats(baseline_data)
    
    def _calculate_stats(self, data):
        """Calculate baseline statistics."""
        stats = {}
        for col in data.columns:
            stats[col] = {
                'mean': float(data[col].mean()),
                'std': float(data[col].std()),
                'min': float(data[col].min()),
                'max': float(data[col].max())
            }
        return stats
    
    def detect_drift(self, new_data, threshold=0.05):
        """Detect data drift using statistical tests."""
        drift_detected = []
        
        for col in new_data.columns:
            if col in self.baseline_data.columns:
                # Kolmogorov-Smirnov test
                statistic, p_value = stats.ks_2samp(
                    self.baseline_data[col],
                    new_data[col]
                )
                
                if p_value < threshold:
                    drift_detected.append({
                        'feature': col,
                        'p_value': p_value,
                        'statistic': statistic
                    })
        
        return drift_detected
    
    def monitor_performance(self, y_true, y_pred, threshold=0.85):
        """Monitor model performance."""
        from sklearn.metrics import accuracy_score
        
        accuracy = accuracy_score(y_true, y_pred)
        
        # Log to MLflow
        mlflow.log_metric("production_accuracy", accuracy)
        
        # Check if retraining needed
        if accuracy < threshold:
            self._trigger_retraining(accuracy)
            return False
        
        return True
    
    def _trigger_retraining(self, current_performance):
        """Trigger model retraining."""
        print(f"⚠️ Performance below threshold: {current_performance:.4f}")
        print("🔄 Triggering retraining pipeline...")
        
        # Trigger Airflow DAG or send alert
        # Implementation depends on your setup

# Usage
monitor = ModelMonitor("credit_risk_model", X_train)

# Check for drift
drift = monitor.detect_drift(X_production)
if drift:
    print(f"⚠️ Drift detected in {len(drift)} features")

# Monitor performance
if not monitor.monitor_performance(y_true, y_pred):
    print("🔄 Retraining required")
```

**Verification:**
- [ ] Monitoring implemented
- [ ] Drift detection working
- [ ] Performance tracked
- [ ] Retraining triggered
- [ ] Alerts configured

**If This Fails:**
→ Check monitoring logic
→ Verify statistical tests
→ Review thresholds
→ Test with known drift
→ Check alert system

---

## Verification Checklist

After completing this workflow:

- [ ] MLflow tracking configured
- [ ] DVC data versioning set up
- [ ] Airflow pipelines running
- [ ] CI/CD pipeline functional
- [ ] Model registry operational
- [ ] Monitoring implemented
- [ ] Automated retraining configured
- [ ] Documentation complete

---

## Best Practices

### DO:
✅ Version everything (data, code, models)
✅ Automate training pipelines
✅ Implement proper testing
✅ Use model registry
✅ Monitor model performance
✅ Set up alerts
✅ Document pipelines
✅ Separate staging/production
✅ Track experiments
✅ Implement rollback procedures
✅ Use feature stores
✅ Automate retraining

### DON'T:
❌ Manual deployments
❌ Skip versioning
❌ Ignore monitoring
❌ Skip testing
❌ Hard-code configurations
❌ Mix environments
❌ Skip documentation
❌ Forget rollback plans
❌ Ignore drift detection
❌ Skip CI/CD
❌ Manual model updates
❌ Ignore alerts

---

## Related Workflows

**Prerequisites:**
- [ml_experiment_setup.md](./ml_experiment_setup.md) - Experiments
- [model_training_evaluation.md](./model_training_evaluation.md) - Training

**Next Steps:**
- [model_deployment_strategies.md](./model_deployment_strategies.md) - Deployment
- [model_monitoring_observability.md](./model_monitoring_observability.md) - Monitoring

**Related:**
- [cicd_pipeline_setup.md](../devops/cicd_pipeline_setup.md) - CI/CD

---

## Tags
`mlops` `machine-learning` `mlflow` `dvc` `airflow` `ci-cd` `model-registry` `monitoring` `automation` `deployment`
