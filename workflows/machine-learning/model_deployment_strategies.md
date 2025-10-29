# Model Deployment Strategies

**ID:** mac-007  
**Category:** Machine Learning  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Deploy machine learning models to production using various deployment strategies (REST API, batch, streaming, edge) with proper versioning and rollback capabilities

**Why:** Proper deployment strategies ensure models are available, scalable, reliable, and can be updated safely without downtime

**When to use:**
- Deploying ML models to production
- Setting up model serving infrastructure
- Implementing API endpoints for predictions
- Deploying batch prediction jobs
- Edge deployment requirements
- Multi-model serving
- A/B testing models
- Blue-green deployments

---

## Prerequisites

**Required:**
- [ ] Trained and validated ML model
- [ ] Docker knowledge
- [ ] API development basics
- [ ] Cloud platform familiarity
- [ ] Kubernetes basics (optional)
- [ ] MLOps pipeline set up

**Check before starting:**
```bash
# Check installations
docker --version
python --version
pip show fastapi uvicorn mlflow

# Check model availability
ls -lh models/
```

---

## Implementation Steps

### Step 1: Create REST API Deployment with FastAPI

**What:** Build a production-ready REST API for real-time model serving

**How:**

**FastAPI Model Server:**
```python
# src/deployment/api/app.py
"""
FastAPI model serving application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="ML Model Serving API",
    description="Production ML model serving with FastAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
MODEL_URI = "models:/credit_risk_model/Production"
model = None

@app.on_event("startup")
async def load_model():
    """Load model on startup."""
    global model
    try:
        mlflow.set_tracking_uri("http://mlflow:5000")
        model = mlflow.sklearn.load_model(MODEL_URI)
        logger.info(f"✅ Model loaded: {MODEL_URI}")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise

# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Request schema for predictions."""
    features: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "features": [
                    {
                        "age": 35,
                        "income": 75000,
                        "credit_score": 720,
                        "employment_years": 5
                    }
                ]
            }
        }

class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    predictions: List[float]
    probabilities: List[List[float]] = None
    model_version: str
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    model_uri: str
    timestamp: str

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "ML Model Serving API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_uri=MODEL_URI,
        timestamp=datetime.now().isoformat()
    )

@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(request: PredictionRequest):
    """
    Make predictions using the loaded model.
    
    Args:
        request: Prediction request with features
        
    Returns:
        Predictions and probabilities
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.features)
        
        # Make predictions
        predictions = model.predict(df).tolist()
        
        # Get probabilities if available
        probabilities = None
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(df).tolist()
        
        return PredictionResponse(
            predictions=predictions,
            probabilities=probabilities,
            model_version=MODEL_URI,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch", tags=["Predictions"])
async def predict_batch(request: PredictionRequest):
    """
    Batch predictions endpoint.
    
    Optimized for larger batches of data.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        df = pd.DataFrame(request.features)
        
        # Batch prediction
        predictions = model.predict(df)
        
        return {
            "predictions": predictions.tolist(),
            "count": len(predictions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get model information."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    info = {
        "model_uri": MODEL_URI,
        "model_type": type(model).__name__,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add feature names if available
    if hasattr(model, 'feature_names_in_'):
        info["features"] = model.feature_names_in_.tolist()
    
    return info

# Run with: uvicorn src.deployment.api.app:app --host 0.0.0.0 --port 8000
```

**Dockerfile for API:**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "src.deployment.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose for Development:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    volumes:
      - ./src:/app/src
      - ./models:/app/models
    depends_on:
      - mlflow
    restart: unless-stopped

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    command: mlflow server --host 0.0.0.0 --port 5000
    volumes:
      - mlflow_data:/mlflow

volumes:
  mlflow_data:
```

**Build and Run:**
```bash
# Build image
docker build -t ml-model-api:latest .

# Run locally
docker run -p 8000:8000 ml-model-api:latest

# Or use docker-compose
docker-compose up -d

# Test API
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      {"age": 35, "income": 75000, "credit_score": 720, "employment_years": 5}
    ]
  }'
```

**Verification:**
- [ ] API running
- [ ] Health check working
- [ ] Predictions successful
- [ ] Error handling proper
- [ ] Docker image built

**If This Fails:**
→ Check model path
→ Verify dependencies
→ Review logs
→ Test locally first
→ Check port availability

---

### Step 2: Implement Batch Prediction Pipeline

**What:** Create batch prediction pipeline for offline scoring

**How:**

**Batch Prediction Script:**
```python
# src/deployment/batch/batch_predict.py
"""
Batch prediction pipeline
"""

import pandas as pd
import mlflow
import mlflow.sklearn
import argparse
from pathlib import Path
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchPredictor:
    """Batch prediction pipeline."""
    
    def __init__(self, model_uri, chunk_size=1000):
        """
        Initialize batch predictor.
        
        Args:
            model_uri: MLflow model URI
            chunk_size: Number of rows to process at once
        """
        self.model_uri = model_uri
        self.chunk_size = chunk_size
        self.model = None
        
    def load_model(self):
        """Load model from MLflow."""
        logger.info(f"Loading model: {self.model_uri}")
        mlflow.set_tracking_uri("http://mlflow:5000")
        self.model = mlflow.sklearn.load_model(self.model_uri)
        logger.info("✅ Model loaded")
    
    def predict_batch(self, input_path, output_path):
        """
        Run batch predictions.
        
        Args:
            input_path: Path to input data
            output_path: Path to save predictions
        """
        if self.model is None:
            self.load_model()
        
        logger.info(f"Reading data from {input_path}")
        
        # Read input data in chunks
        chunks = pd.read_csv(input_path, chunksize=self.chunk_size)
        
        all_predictions = []
        total_rows = 0
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1} ({len(chunk)} rows)")
            
            # Make predictions
            predictions = self.model.predict(chunk)
            
            # Get probabilities if available
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(chunk)
                chunk['prediction'] = predictions
                chunk['probability_0'] = probabilities[:, 0]
                chunk['probability_1'] = probabilities[:, 1]
            else:
                chunk['prediction'] = predictions
            
            all_predictions.append(chunk)
            total_rows += len(chunk)
        
        # Combine all predictions
        logger.info("Combining predictions...")
        result_df = pd.concat(all_predictions, ignore_index=True)
        
        # Save results
        logger.info(f"Saving predictions to {output_path}")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path, index=False)
        
        # Save metadata
        metadata = {
            'model_uri': self.model_uri,
            'input_path': str(input_path),
            'output_path': str(output_path),
            'total_rows': total_rows,
            'timestamp': datetime.now().isoformat()
        }
        
        metadata_path = Path(output_path).with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Batch prediction complete: {total_rows} rows processed")
        
        return result_df

def main():
    """Main batch prediction function."""
    parser = argparse.ArgumentParser(description='Batch prediction')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', required=True, help='Output CSV file')
    parser.add_argument('--model-uri', required=True, help='MLflow model URI')
    parser.add_argument('--chunk-size', type=int, default=1000, help='Chunk size')
    
    args = parser.parse_args()
    
    # Run batch prediction
    predictor = BatchPredictor(args.model_uri, args.chunk_size)
    predictor.predict_batch(args.input, args.output)

if __name__ == '__main__':
    main()

# Usage:
# python src/deployment/batch/batch_predict.py \
#   --input data/to_score.csv \
#   --output results/predictions.csv \
#   --model-uri models:/credit_risk_model/Production
```

**Scheduled Batch Job (Airflow DAG):**
```python
# dags/batch_prediction_dag.py
"""
Airflow DAG for scheduled batch predictions
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'batch_prediction_daily',
    default_args=default_args,
    description='Daily batch predictions',
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

extract_data = BashOperator(
    task_id='extract_data',
    bash_command='python src/data/extract_scoring_data.py',
    dag=dag,
)

run_predictions = BashOperator(
    task_id='run_predictions',
    bash_command='''
        python src/deployment/batch/batch_predict.py \
            --input data/scoring/latest.csv \
            --output results/predictions_{{ ds }}.csv \
            --model-uri models:/credit_risk_model/Production
    ''',
    dag=dag,
)

upload_results = BashOperator(
    task_id='upload_results',
    bash_command='aws s3 cp results/predictions_{{ ds }}.csv s3://my-bucket/predictions/',
    dag=dag,
)

extract_data >> run_predictions >> upload_results
```

**Verification:**
- [ ] Batch script working
- [ ] Predictions accurate
- [ ] Large files handled
- [ ] Results saved correctly
- [ ] Scheduled job configured

**If This Fails:**
→ Check memory usage
→ Adjust chunk size
→ Verify input data
→ Check file permissions
→ Review error logs

---

### Step 3: Deploy to Kubernetes

**What:** Deploy model API to Kubernetes for scalability

**How:**

**Kubernetes Deployment:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-api
  namespace: ml-production
  labels:
    app: ml-model-api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-api
  template:
    metadata:
      labels:
        app: ml-model-api
        version: v1
    spec:
      containers:
      - name: api
        image: ml-model-api:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow-service:5000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: model-storage
          mountPath: /app/models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: ml-model-api-service
  namespace: ml-production
spec:
  selector:
    app: ml-model-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-api-hpa
  namespace: ml-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Deploy to Kubernetes:**
```bash
# Create namespace
kubectl create namespace ml-production

# Apply configurations
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n ml-production
kubectl get svc -n ml-production

# View logs
kubectl logs -n ml-production -l app=ml-model-api --tail=100

# Scale deployment
kubectl scale deployment ml-model-api -n ml-production --replicas=5

# Check HPA
kubectl get hpa -n ml-production
```

**Verification:**
- [ ] Pods running
- [ ] Service accessible
- [ ] HPA configured
- [ ] Health checks passing
- [ ] Load balancing working

**If This Fails:**
→ Check pod logs
→ Verify resource limits
→ Review service configuration
→ Check networking
→ Verify image pull

---

### Step 4: Implement Blue-Green Deployment

**What:** Set up blue-green deployment for zero-downtime updates

**How:**

**Blue-Green Deployment Strategy:**
```yaml
# k8s/blue-green-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-api-blue
  namespace: ml-production
  labels:
    app: ml-model-api
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-api
      version: blue
  template:
    metadata:
      labels:
        app: ml-model-api
        version: blue
    spec:
      containers:
      - name: api
        image: ml-model-api:v1.0.0
        ports:
        - containerPort: 8000

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-api-green
  namespace: ml-production
  labels:
    app: ml-model-api
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-api
      version: green
  template:
    metadata:
      labels:
        app: ml-model-api
        version: green
    spec:
      containers:
      - name: api
        image: ml-model-api:v2.0.0  # New version
        ports:
        - containerPort: 8000

---
apiVersion: v1
kind: Service
metadata:
  name: ml-model-api-service
  namespace: ml-production
spec:
  selector:
    app: ml-model-api
    version: blue  # Switch to 'green' to route to new version
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

**Deployment Script:**
```python
# scripts/blue_green_deploy.py
"""
Blue-green deployment automation
"""

import subprocess
import time
import requests
import sys

def run_command(cmd):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def health_check(url, max_attempts=10):
    """Check if service is healthy."""
    for i in range(max_attempts):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                print(f"✅ Health check passed")
                return True
        except Exception as e:
            print(f"⏳ Attempt {i+1}/{max_attempts}: {e}")
            time.sleep(5)
    
    return False

def deploy_blue_green(new_version, namespace="ml-production"):
    """
    Perform blue-green deployment.
    
    Args:
        new_version: New image version to deploy
        namespace: Kubernetes namespace
    """
    print(f"\\n=== Starting Blue-Green Deployment ===")
    print(f"New version: {new_version}")
    
    # Get current active environment
    cmd = f"kubectl get svc ml-model-api-service -n {namespace} -o jsonpath='{{.spec.selector.version}}'"
    current_env = run_command(cmd).strip()
    new_env = "green" if current_env == "blue" else "blue"
    
    print(f"Current environment: {current_env}")
    print(f"New environment: {new_env}")
    
    # Deploy to new environment
    print(f"\\n[1/5] Deploying to {new_env} environment...")
    deployment_name = f"ml-model-api-{new_env}"
    cmd = f"kubectl set image deployment/{deployment_name} api=ml-model-api:{new_version} -n {namespace}"
    run_command(cmd)
    
    # Wait for rollout
    print(f"\\n[2/5] Waiting for rollout to complete...")
    cmd = f"kubectl rollout status deployment/{deployment_name} -n {namespace}"
    run_command(cmd)
    
    # Get service URL (assuming port-forward for testing)
    print(f"\\n[3/5] Running health checks...")
    service_url = "http://localhost:8000"  # Update with actual service URL
    
    if not health_check(service_url):
        print("❌ Health check failed. Rolling back...")
        cmd = f"kubectl rollout undo deployment/{deployment_name} -n {namespace}"
        run_command(cmd)
        sys.exit(1)
    
    # Switch traffic to new environment
    print(f"\\n[4/5] Switching traffic to {new_env}...")
    cmd = f"kubectl patch svc ml-model-api-service -n {namespace} -p '{{\"spec\":{{\"selector\":{{\"version\":\"{new_env}\"}}}}}}'"
    run_command(cmd)
    
    print(f"\\n[5/5] Verifying traffic switch...")
    time.sleep(5)
    
    if health_check(service_url):
        print(f"\\n✅ Deployment successful!")
        print(f"Traffic switched to {new_env} environment")
        print(f"Old {current_env} environment still running for rollback")
    else:
        print("❌ Verification failed. Consider rollback.")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True, help='New image version')
    parser.add_argument('--namespace', default='ml-production')
    args = parser.parse_args()
    
    deploy_blue_green(args.version, args.namespace)

# Usage:
# python scripts/blue_green_deploy.py --version v2.0.0
```

**Verification:**
- [ ] Blue environment running
- [ ] Green environment deployed
- [ ] Traffic switched successfully
- [ ] Rollback possible
- [ ] Zero downtime achieved

**If This Fails:**
→ Check deployment status
→ Verify service selector
→ Review health checks
→ Check pod readiness
→ Rollback if needed

---

### Step 5: Implement Model Versioning and Rollback

**What:** Set up model versioning with easy rollback capability

**How:**

**Model Version Management:**
```python
# src/deployment/version_manager.py
"""
Model version management
"""

import mlflow
from mlflow.tracking import MlflowClient
import logging

logger = logging.getLogger(__name__)

class ModelVersionManager:
    """Manage model versions and deployments."""
    
    def __init__(self, tracking_uri="http://mlflow:5000"):
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
    
    def list_versions(self, model_name):
        """List all versions of a model."""
        versions = self.client.search_model_versions(f"name='{model_name}'")
        
        print(f"\\n=== Model Versions for {model_name} ===")
        for version in versions:
            print(f"Version {version.version}:")
            print(f"  Stage: {version.current_stage}")
            print(f"  Created: {version.creation_timestamp}")
            print(f"  Run ID: {version.run_id}")
        
        return versions
    
    def promote_to_production(self, model_name, version):
        """Promote model version to production."""
        print(f"\\nPromoting {model_name} v{version} to Production...")
        
        # Archive current production model
        current_prod = self.client.get_latest_versions(model_name, stages=["Production"])
        for model in current_prod:
            self.client.transition_model_version_stage(
                name=model_name,
                version=model.version,
                stage="Archived"
            )
            print(f"  Archived v{model.version}")
        
        # Promote new version
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production"
        )
        
        print(f"✅ v{version} promoted to Production")
    
    def rollback_production(self, model_name):
        """Rollback to previous production model."""
        print(f"\\nRolling back {model_name}...")
        
        # Get current production
        current = self.client.get_latest_versions(model_name, stages=["Production"])
        
        if not current:
            print("❌ No production model to rollback from")
            return
        
        current_version = current[0].version
        
        # Get previous archived version
        archived = self.client.get_latest_versions(model_name, stages=["Archived"])
        
        if not archived:
            print("❌ No archived version to rollback to")
            return
        
        previous_version = archived[0].version
        
        # Rollback
        self.client.transition_model_version_stage(
            name=model_name,
            version=current_version,
            stage="Archived"
        )
        
        self.client.transition_model_version_stage(
            name=model_name,
            version=previous_version,
            stage="Production"
        )
        
        print(f"✅ Rolled back from v{current_version} to v{previous_version}")
    
    def delete_version(self, model_name, version):
        """Delete a model version."""
        self.client.delete_model_version(model_name, version)
        print(f"✅ Deleted v{version}")

# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-name', required=True)
    parser.add_argument('--action', choices=['list', 'promote', 'rollback', 'delete'])
    parser.add_argument('--version', type=int)
    
    args = parser.parse_args()
    
    manager = ModelVersionManager()
    
    if args.action == 'list':
        manager.list_versions(args.model_name)
    elif args.action == 'promote':
        manager.promote_to_production(args.model_name, args.version)
    elif args.action == 'rollback':
        manager.rollback_production(args.model_name)
    elif args.action == 'delete':
        manager.delete_version(args.model_name, args.version)

# Usage:
# python src/deployment/version_manager.py --model-name credit_risk_model --action list
# python src/deployment/version_manager.py --model-name credit_risk_model --action promote --version 3
# python src/deployment/version_manager.py --model-name credit_risk_model --action rollback
```

**Verification:**
- [ ] Versions tracked
- [ ] Promotion working
- [ ] Rollback tested
- [ ] Version history maintained
- [ ] Metadata preserved

**If This Fails:**
→ Check MLflow connection
→ Verify model registry
→ Review version status
→ Check permissions
→ Test with dummy model

---

## Verification Checklist

After completing this workflow:

- [ ] REST API deployed
- [ ] Batch predictions working
- [ ] Kubernetes deployment successful
- [ ] Blue-green deployment tested
- [ ] Version management operational
- [ ] Monitoring configured
- [ ] Rollback procedures tested
- [ ] Documentation complete

---

## Best Practices

### DO:
✅ Use container orchestration
✅ Implement health checks
✅ Version all models
✅ Enable easy rollback
✅ Monitor deployment metrics
✅ Use blue-green or canary deployments
✅ Test in staging first
✅ Automate deployments
✅ Document deployment process
✅ Set resource limits
✅ Use load balancing
✅ Implement proper logging

### DON'T:
❌ Deploy directly to production
❌ Skip health checks
❌ Ignore versioning
❌ Forget rollback plan
❌ Skip load testing
❌ Use manual processes
❌ Ignore resource limits
❌ Skip staging environment
❌ Deploy without testing
❌ Ignore monitoring
❌ Hard-code configurations
❌ Skip documentation

---

## Related Workflows

**Prerequisites:**
- [model_training_evaluation.md](./model_training_evaluation.md) - Training
- [mlops_pipeline_setup.md](./mlops_pipeline_setup.md) - MLOps

**Next Steps:**
- [model_monitoring_observability.md](./model_monitoring_observability.md) - Monitoring
- [ab_testing_models.md](./ab_testing_models.md) - A/B Testing

**Related:**
- [container_orchestration_kubernetes.md](../devops/container_orchestration_kubernetes.md) - Kubernetes

---

## Tags
`machine-learning` `deployment` `fastapi` `kubernetes` `docker` `mlops` `blue-green` `batch-prediction` `model-serving` `production`
