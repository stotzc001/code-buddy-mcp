# ML Experiment Setup

**ID:** mac-010  
**Category:** Machine Learning  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 45-75 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Set up a complete ML experiment tracking infrastructure with MLflow, experiment versioning, and reproducible experimentation workflows

**Why:** Systematic experiment tracking enables reproducibility, collaboration, model comparison, and faster iteration on ML projects

**When to use:**
- Starting new ML projects
- Establishing experiment tracking
- Comparing multiple models
- Tracking hyperparameter tuning
- Managing model versions
- Collaborating on ML projects
- Ensuring reproducibility
- Building model registries

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ installed
- [ ] Basic ML knowledge (scikit-learn, pandas)
- [ ] Understanding of experiment tracking concepts
- [ ] Git installed
- [ ] Database for MLflow backend (optional but recommended)

**Check before starting:**
```bash
# Check Python
python --version

# Check pip
pip --version

# Check Git
git --version

# Check system resources
free -h  # Linux/Mac
```

---

## Implementation Steps

### Step 1: Install and Configure MLflow

**What:** Set up MLflow as the experiment tracking system

**How:**

**Install MLflow:**
```bash
# Install MLflow with extras
pip install mlflow[extras]

# Install additional dependencies
pip install scikit-learn pandas numpy matplotlib seaborn

# Verify installation
mlflow --version
```

**Configure MLflow Tracking Server:**
```bash
# Option 1: Local file-based tracking (development)
export MLFLOW_TRACKING_URI=file:///path/to/mlruns

# Option 2: SQLite backend (better for local)
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# Option 3: PostgreSQL backend (production)
export MLFLOW_TRACKING_URI=postgresql://user:pass@localhost:5432/mlflow

# Start MLflow UI
mlflow ui --host 0.0.0.0 --port 5000

# Access at http://localhost:5000
```

**Docker Setup (Production):**
```yaml
# docker-compose.yml
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

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    depends_on:
      - postgres
    environment:
      MLFLOW_BACKEND_STORE_URI: postgresql://mlflow:mlflow@postgres:5432/mlflow
      MLFLOW_DEFAULT_ARTIFACT_ROOT: /mlflow/artifacts
    volumes:
      - mlflow_artifacts:/mlflow/artifacts
    ports:
      - "5000:5000"
    command: >
      mlflow server
      --backend-store-uri postgresql://mlflow:mlflow@postgres:5432/mlflow
      --default-artifact-location /mlflow/artifacts
      --host 0.0.0.0
      --port 5000

volumes:
  postgres_data:
  mlflow_artifacts:
```

```bash
# Start services
docker-compose up -d

# Verify
curl http://localhost:5000/health
```

**Verification:**
- [ ] MLflow installed
- [ ] Tracking server running
- [ ] UI accessible
- [ ] Backend configured
- [ ] Can log experiments

**If This Fails:**
→ Check Python version
→ Verify database connection
→ Review port availability
→ Check firewall settings
→ Review MLflow logs

---

### Step 2: Create Experiment Template Structure

**What:** Set up standardized project structure for ML experiments

**How:**

**Project Structure:**
```bash
# Create project structure
mkdir -p ml_project/{notebooks,src/{data,models,features,evaluation},data/{raw,processed,features},models,experiments,configs}
cd ml_project

# Create files
touch README.md
touch requirements.txt
touch .gitignore
touch configs/experiment_config.yaml
```

**requirements.txt:**
```
mlflow==2.8.0
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
matplotlib==3.8.2
seaborn==0.13.0
jupyter==1.0.0
pyyaml==6.0.1
python-dotenv==1.0.0
optuna==3.4.0
```

**.gitignore:**
```
# ML artifacts
mlruns/
*.pkl
*.joblib
*.h5
*.pth
models/

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Python
__pycache__/
*.py[cod]
*$py.class
.ipynb_checkpoints/
venv/
.env

# IDE
.vscode/
.idea/
```

**Experiment Configuration:**
```yaml
# configs/experiment_config.yaml
experiment:
  name: "customer_churn_prediction"
  description: "Predict customer churn using various ML models"
  tags:
    project: "customer_analytics"
    team: "data_science"

data:
  raw_path: "data/raw/customers.csv"
  processed_path: "data/processed/customers_processed.parquet"
  train_test_split: 0.2
  random_state: 42

features:
  numerical:
    - age
    - tenure
    - monthly_charges
    - total_charges
  categorical:
    - gender
    - contract_type
    - payment_method
  target: churn

models:
  - name: logistic_regression
    params:
      C: [0.01, 0.1, 1, 10]
      max_iter: 1000
  
  - name: random_forest
    params:
      n_estimators: [100, 200, 300]
      max_depth: [10, 20, 30, null]
      min_samples_split: [2, 5, 10]
  
  - name: xgboost
    params:
      n_estimators: [100, 200]
      max_depth: [3, 5, 7]
      learning_rate: [0.01, 0.1, 0.3]

evaluation:
  metrics:
    - accuracy
    - precision
    - recall
    - f1
    - roc_auc
  cv_folds: 5
```

**Base Experiment Class:**
```python
# src/experiment.py
"""
Base experiment class for ML experiments
"""

import mlflow
import mlflow.sklearn
import yaml
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLExperiment:
    """Base class for ML experiments."""
    
    def __init__(self, config_path: str = "configs/experiment_config.yaml"):
        """Initialize experiment."""
        self.config = self._load_config(config_path)
        self.experiment_name = self.config['experiment']['name']
        
        # Set up MLflow
        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment(self.experiment_name)
        
        # Data containers
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        logger.info(f"Initialized experiment: {self.experiment_name}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load experiment configuration."""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def load_data(self) -> pd.DataFrame:
        """Load raw data."""
        data_path = self.config['data']['raw_path']
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} rows")
        return df
    
    def prepare_data(self, df: pd.DataFrame):
        """Prepare data for training."""
        # Extract features and target
        feature_cols = (
            self.config['features']['numerical'] +
            self.config['features']['categorical']
        )
        target_col = self.config['features']['target']
        
        X = df[feature_cols]
        y = df[target_col]
        
        # Train-test split
        test_size = self.config['data']['train_test_split']
        random_state = self.config['data']['random_state']
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        logger.info(f"Train set: {len(self.X_train)} samples")
        logger.info(f"Test set: {len(self.X_test)} samples")
    
    def run_experiment(
        self,
        model,
        model_name: str,
        params: Dict[str, Any],
        tags: Dict[str, str] = None
    ):
        """Run a single experiment."""
        with mlflow.start_run(run_name=model_name):
            # Log parameters
            mlflow.log_params(params)
            
            # Log tags
            if tags:
                mlflow.set_tags(tags)
            
            # Train model
            logger.info(f"Training {model_name}")
            model.fit(self.X_train, self.y_train)
            
            # Evaluate
            train_score = model.score(self.X_train, self.y_train)
            test_score = model.score(self.X_test, self.y_test)
            
            # Log metrics
            mlflow.log_metric("train_score", train_score)
            mlflow.log_metric("test_score", test_score)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            logger.info(f"✅ {model_name}: train={train_score:.4f}, test={test_score:.4f}")
            
            return model

# Usage
experiment = MLExperiment()
df = experiment.load_data()
experiment.prepare_data(df)
```

**Verification:**
- [ ] Project structure created
- [ ] Config file valid
- [ ] Base class working
- [ ] MLflow tracking active
- [ ] Experiments logged

**If This Fails:**
→ Check file permissions
→ Verify YAML syntax
→ Test MLflow connection
→ Review Python imports
→ Check data paths

---

### Step 3: Implement Experiment Tracking

**What:** Create comprehensive experiment tracking with metrics, parameters, and artifacts

**How:**

**Complete Experiment Runner:**
```python
# src/run_experiments.py
"""
Run and track ML experiments
"""

import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import json

class ExperimentRunner:
    """Run and track ML experiments."""
    
    def __init__(self, experiment: MLExperiment):
        self.experiment = experiment
        self.results = []
    
    def evaluate_model(self, model, X, y, prefix=""):
        """Comprehensive model evaluation."""
        y_pred = model.predict(X)
        y_pred_proba = model.predict_proba(X)[:, 1] if hasattr(model, 'predict_proba') else None
        
        metrics = {
            f"{prefix}accuracy": accuracy_score(y, y_pred),
            f"{prefix}precision": precision_score(y, y_pred, average='weighted'),
            f"{prefix}recall": recall_score(y, y_pred, average='weighted'),
            f"{prefix}f1": f1_score(y, y_pred, average='weighted'),
        }
        
        if y_pred_proba is not None:
            metrics[f"{prefix}roc_auc"] = roc_auc_score(y, y_pred_proba)
        
        return metrics, y_pred
    
    def plot_confusion_matrix(self, y_true, y_pred, run_id):
        """Plot and log confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        # Save and log
        cm_path = f"experiments/confusion_matrix_{run_id}.png"
        plt.savefig(cm_path)
        mlflow.log_artifact(cm_path)
        plt.close()
    
    def plot_feature_importance(self, model, feature_names, run_id):
        """Plot and log feature importance."""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            indices = np.argsort(importance)[::-1][:20]
            
            plt.figure(figsize=(10, 6))
            plt.title('Top 20 Feature Importances')
            plt.bar(range(len(indices)), importance[indices])
            plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=90)
            plt.tight_layout()
            
            # Save and log
            fi_path = f"experiments/feature_importance_{run_id}.png"
            plt.savefig(fi_path)
            mlflow.log_artifact(fi_path)
            plt.close()
    
    def run_single_experiment(
        self,
        model_class,
        model_name: str,
        params: dict,
        tags: dict = None
    ):
        """Run single experiment with full tracking."""
        
        with mlflow.start_run(run_name=model_name) as run:
            run_id = run.info.run_id
            
            # Log parameters
            mlflow.log_params(params)
            
            # Log tags
            default_tags = {
                "model_type": model_name,
                "framework": "sklearn"
            }
            if tags:
                default_tags.update(tags)
            mlflow.set_tags(default_tags)
            
            # Initialize and train model
            model = model_class(**params)
            model.fit(self.experiment.X_train, self.experiment.y_train)
            
            # Evaluate on train set
            train_metrics, y_train_pred = self.evaluate_model(
                model,
                self.experiment.X_train,
                self.experiment.y_train,
                prefix="train_"
            )
            
            # Evaluate on test set
            test_metrics, y_test_pred = self.evaluate_model(
                model,
                self.experiment.X_test,
                self.experiment.y_test,
                prefix="test_"
            )
            
            # Log all metrics
            mlflow.log_metrics({**train_metrics, **test_metrics})
            
            # Generate and log artifacts
            self.plot_confusion_matrix(self.experiment.y_test, y_test_pred, run_id)
            
            if hasattr(self.experiment.X_train, 'columns'):
                self.plot_feature_importance(
                    model,
                    self.experiment.X_train.columns.tolist(),
                    run_id
                )
            
            # Log classification report
            report = classification_report(
                self.experiment.y_test,
                y_test_pred,
                output_dict=True
            )
            report_path = f"experiments/classification_report_{run_id}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            mlflow.log_artifact(report_path)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Store results
            self.results.append({
                'run_id': run_id,
                'model_name': model_name,
                'params': params,
                **test_metrics
            })
            
            print(f"✅ {model_name}: Test Accuracy = {test_metrics['test_accuracy']:.4f}")
            
            return model, run_id

# Usage
runner = ExperimentRunner(experiment)

# Run experiments
models = [
    (LogisticRegression, "logistic_regression", {"C": 1.0, "max_iter": 1000}),
    (RandomForestClassifier, "random_forest", {"n_estimators": 100, "max_depth": 10}),
]

for model_class, name, params in models:
    runner.run_single_experiment(model_class, name, params)

# Compare results
results_df = pd.DataFrame(runner.results)
print("\n=== Experiment Results ===")
print(results_df.sort_values('test_accuracy', ascending=False))
```

**Verification:**
- [ ] Experiments tracked
- [ ] Metrics logged
- [ ] Artifacts saved
- [ ] Models registered
- [ ] Results comparable

**If This Fails:**
→ Check MLflow connection
→ Verify data loaded
→ Review metric calculations
→ Check artifact paths
→ Test model training

---

### Step 4: Set Up Hyperparameter Tuning with Tracking

**What:** Integrate automated hyperparameter tuning with experiment tracking

**How:**

**Optuna Integration:**
```python
# src/hyperparameter_tuning.py
"""
Hyperparameter tuning with Optuna and MLflow
"""

import optuna
from optuna.integration.mlflow import MLflowCallback
import mlflow

class HyperparameterTuner:
    """Hyperparameter tuning with tracking."""
    
    def __init__(self, experiment: MLExperiment):
        self.experiment = experiment
    
    def objective_random_forest(self, trial):
        """Objective function for Random Forest."""
        # Suggest hyperparameters
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 5, 50),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2']),
            'random_state': 42
        }
        
        # Train model
        model = RandomForestClassifier(**params)
        model.fit(self.experiment.X_train, self.experiment.y_train)
        
        # Evaluate
        score = model.score(self.experiment.X_test, self.experiment.y_test)
        
        return score
    
    def tune(self, model_name: str, n_trials: int = 50):
        """Run hyperparameter tuning."""
        # MLflow callback
        mlflow_callback = MLflowCallback(
            tracking_uri="http://localhost:5000",
            metric_name="test_accuracy"
        )
        
        # Create study
        study = optuna.create_study(
            study_name=f"{model_name}_tuning",
            direction="maximize",
            storage="sqlite:///optuna.db",
            load_if_exists=True
        )
        
        # Optimize
        study.optimize(
            self.objective_random_forest,
            n_trials=n_trials,
            callbacks=[mlflow_callback]
        )
        
        print(f"\n=== Best Trial ===")
        print(f"Value: {study.best_value:.4f}")
        print(f"Params: {study.best_params}")
        
        return study.best_params

# Usage
tuner = HyperparameterTuner(experiment)
best_params = tuner.tune("random_forest", n_trials=20)
```

**Verification:**
- [ ] Tuning working
- [ ] Trials tracked
- [ ] Best params found
- [ ] Results in MLflow
- [ ] Optimization converged

**If This Fails:**
→ Check Optuna installation
→ Verify objective function
→ Review search space
→ Check trial budget
→ Monitor convergence

---

### Step 5: Implement Model Registry and Versioning

**What:** Set up model registry for production model management

**How:**

**Model Registry:**
```python
# src/model_registry.py
"""
Model registry management
"""

import mlflow
from mlflow.tracking import MlflowClient

class ModelRegistry:
    """Manage model registry."""
    
    def __init__(self):
        self.client = MlflowClient()
    
    def register_model(
        self,
        run_id: str,
        model_name: str,
        description: str = None
    ):
        """Register model from run."""
        model_uri = f"runs:/{run_id}/model"
        
        # Register
        result = mlflow.register_model(model_uri, model_name)
        
        # Add description
        if description:
            self.client.update_model_version(
                name=model_name,
                version=result.version,
                description=description
            )
        
        print(f"✅ Registered {model_name} v{result.version}")
        return result
    
    def promote_to_production(self, model_name: str, version: int):
        """Promote model to production."""
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production"
        )
        print(f"✅ Promoted {model_name} v{version} to Production")
    
    def get_production_model(self, model_name: str):
        """Get current production model."""
        versions = self.client.get_latest_versions(model_name, stages=["Production"])
        if versions:
            return versions[0]
        return None

# Usage
registry = ModelRegistry()
registry.register_model(run_id, "churn_model", "Random Forest classifier")
registry.promote_to_production("churn_model", 1)
```

**Verification:**
- [ ] Models registered
- [ ] Versions tracked
- [ ] Stages managed
- [ ] Production model set
- [ ] Registry accessible

**If This Fails:**
→ Check registry backend
→ Verify permissions
→ Review model URI
→ Check version conflicts
→ Test model loading

---

## Verification Checklist

After completing this workflow:

- [ ] MLflow installed and running
- [ ] Experiment structure set up
- [ ] Tracking working correctly
- [ ] Metrics and artifacts logged
- [ ] Hyperparameter tuning integrated
- [ ] Model registry configured
- [ ] Documentation complete
- [ ] Team trained on tools

---

## Best Practices

### DO:
✅ Track all experiments
✅ Log comprehensive metrics
✅ Version your data
✅ Document experiment goals
✅ Use consistent naming
✅ Tag experiments properly
✅ Save artifacts
✅ Register production models
✅ Compare experiments systematically
✅ Use configuration files
✅ Automate where possible
✅ Version control configs

### DON'T:
❌ Skip experiment tracking
❌ Forget to log parameters
❌ Lose experiment context
❌ Manual result tracking
❌ Skip documentation
❌ Mix environments
❌ Forget data versioning
❌ Ignore reproducibility
❌ Skip model registry
❌ Hard-code configurations
❌ Forget to back up results
❌ Skip team training

---

## Related Workflows

**Prerequisites:**
- [data_preprocessing_pipelines.md](./data_preprocessing_pipelines.md) - Data prep

**Next Steps:**
- [model_training_evaluation.md](./model_training_evaluation.md) - Training
- [automl_hyperparameter_optimization.md](./automl_hyperparameter_optimization.md) - Tuning

**Related:**
- [mlops_pipeline_setup.md](./mlops_pipeline_setup.md) - MLOps
- [model_deployment_strategies.md](./model_deployment_strategies.md) - Deployment

---

## Tags
`machine-learning` `mlflow` `experiment-tracking` `hyperparameter-tuning` `model-registry` `mlops` `optuna` `reproducibility`
