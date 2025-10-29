# Model Training & Evaluation

**ID:** mac-009  
**Category:** Machine Learning  
**Priority:** MEDIUM  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Train machine learning models systematically with proper evaluation, cross-validation, and comprehensive metrics

**Why:** Rigorous training and evaluation ensures models generalize well, prevents overfitting, and enables confident deployment decisions

**When to use:**
- Training new ML models
- Comparing different algorithms
- Evaluating model performance
- Tuning model parameters
- Validating model quality
- Preparing models for production
- Benchmarking approaches
- Detecting overfitting

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ with scikit-learn, pandas, numpy
- [ ] Preprocessed and feature-engineered data
- [ ] Train/test split completed
- [ ] Understanding of ML metrics
- [ ] MLflow or experiment tracking setup

**Check before starting:**
```bash
# Check installations
pip show scikit-learn pandas numpy matplotlib seaborn mlflow

# Verify data
python -c "import pandas as pd; X = pd.read_csv('data/X_train.csv'); y = pd.read_csv('data/y_train.csv'); print(f'Train: {X.shape}, Target: {y.shape}')"
```

---

## Implementation Steps

### Step 1: Set Up Training Infrastructure

**What:** Create robust training infrastructure with logging and checkpointing

**How:**

**Training Framework:**
```python
# src/training/trainer.py
"""
Model training framework
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import mlflow
import mlflow.sklearn
import joblib
from pathlib import Path
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Train and evaluate ML models."""
    
    def __init__(self, model, model_name, experiment_name="ml_training"):
        """
        Parameters:
        -----------
        model : sklearn estimator
            Model to train
        model_name : str
            Name for logging
        experiment_name : str
            MLflow experiment name
        """
        self.model = model
        self.model_name = model_name
        self.experiment_name = experiment_name
        
        # Set up MLflow
        mlflow.set_experiment(experiment_name)
        
        self.metrics = {}
        self.trained_model = None
    
    def train(self, X_train, y_train, params=None):
        """Train the model."""
        logger.info(f"Training {self.model_name}")
        
        # Set parameters if provided
        if params:
            self.model.set_params(**params)
        
        # Train
        start_time = datetime.now()
        self.model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        self.trained_model = self.model
        self.metrics['training_time_seconds'] = training_time
        
        logger.info(f"✅ Training completed in {training_time:.2f}s")
        return self.model
    
    def evaluate(self, X, y, dataset_name="test"):
        """Evaluate model on dataset."""
        logger.info(f"Evaluating on {dataset_name} set")
        
        # Predictions
        y_pred = self.model.predict(X)
        y_pred_proba = None
        if hasattr(self.model, 'predict_proba'):
            y_pred_proba = self.model.predict_proba(X)[:, 1]
        
        # Calculate metrics
        metrics = {
            f'{dataset_name}_accuracy': accuracy_score(y, y_pred),
            f'{dataset_name}_precision': precision_score(y, y_pred, average='weighted', zero_division=0),
            f'{dataset_name}_recall': recall_score(y, y_pred, average='weighted', zero_division=0),
            f'{dataset_name}_f1': f1_score(y, y_pred, average='weighted', zero_division=0),
        }
        
        if y_pred_proba is not None:
            metrics[f'{dataset_name}_roc_auc'] = roc_auc_score(y, y_pred_proba)
        
        self.metrics.update(metrics)
        
        # Print metrics
        logger.info(f"=== {dataset_name.upper()} Metrics ===")
        for key, value in metrics.items():
            logger.info(f"  {key}: {value:.4f}")
        
        return metrics, y_pred, y_pred_proba
    
    def cross_validate(self, X, y, cv=5, scoring='accuracy'):
        """Perform cross-validation."""
        logger.info(f"Running {cv}-fold cross-validation")
        
        cv_splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        
        scores = cross_val_score(
            self.model, X, y,
            cv=cv_splitter,
            scoring=scoring,
            n_jobs=-1
        )
        
        cv_metrics = {
            'cv_mean': scores.mean(),
            'cv_std': scores.std(),
            'cv_min': scores.min(),
            'cv_max': scores.max()
        }
        
        self.metrics.update(cv_metrics)
        
        logger.info(f"CV {scoring}: {cv_metrics['cv_mean']:.4f} (+/- {cv_metrics['cv_std']:.4f})")
        
        return cv_metrics
    
    def save_model(self, filepath):
        """Save trained model."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.trained_model, filepath)
        logger.info(f"✅ Model saved to {filepath}")
    
    def log_to_mlflow(self, params=None, artifacts=None):
        """Log to MLflow."""
        with mlflow.start_run(run_name=self.model_name):
            # Log parameters
            if params:
                mlflow.log_params(params)
            
            # Log metrics
            mlflow.log_metrics(self.metrics)
            
            # Log model
            mlflow.sklearn.log_model(self.trained_model, "model")
            
            # Log artifacts
            if artifacts:
                for artifact in artifacts:
                    mlflow.log_artifact(artifact)
            
            logger.info(f"✅ Logged to MLflow")

# Usage
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
trainer = ModelTrainer(model, "random_forest")

# Train
trainer.train(X_train, y_train)

# Evaluate
train_metrics, _, _ = trainer.evaluate(X_train, y_train, "train")
test_metrics, y_pred, y_pred_proba = trainer.evaluate(X_test, y_test, "test")

# Cross-validate
cv_metrics = trainer.cross_validate(X_train, y_train, cv=5)

# Save
trainer.save_model('models/random_forest.pkl')

# Log to MLflow
trainer.log_to_mlflow(params={'n_estimators': 100, 'random_state': 42})
```

**Verification:**
- [ ] Training infrastructure set up
- [ ] Logging working
- [ ] Metrics calculated correctly
- [ ] Models saved
- [ ] MLflow tracking active

**If This Fails:**
→ Check data shapes
→ Verify model compatibility
→ Review metric calculations
→ Test MLflow connection
→ Check file permissions

---

### Step 2: Implement Comprehensive Evaluation

**What:** Create detailed evaluation with multiple metrics and visualizations

**How:**

**Evaluation Suite:**
```python
# src/training/evaluation.py
"""
Comprehensive model evaluation
"""

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc, precision_recall_curve,
    average_precision_score, classification_report
)
import numpy as np
import pandas as pd

class ModelEvaluator:
    """Comprehensive model evaluation."""
    
    def __init__(self, model_name):
        self.model_name = model_name
        self.reports = {}
    
    def confusion_matrix_plot(self, y_true, y_pred, save_path=None):
        """Plot confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title(f'Confusion Matrix - {self.model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved confusion matrix to {save_path}")
        
        plt.close()
    
    def roc_curve_plot(self, y_true, y_pred_proba, save_path=None):
        """Plot ROC curve."""
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {self.model_name}')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved ROC curve to {save_path}")
        
        plt.close()
        
        return roc_auc
    
    def precision_recall_curve_plot(self, y_true, y_pred_proba, save_path=None):
        """Plot precision-recall curve."""
        precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
        avg_precision = average_precision_score(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='blue', lw=2, label=f'PR curve (AP = {avg_precision:.2f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - {self.model_name}')
        plt.legend(loc="lower left")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved PR curve to {save_path}")
        
        plt.close()
        
        return avg_precision
    
    def classification_report_plot(self, y_true, y_pred, save_path=None):
        """Generate and save classification report."""
        report = classification_report(y_true, y_pred, output_dict=True)
        
        # Convert to DataFrame
        report_df = pd.DataFrame(report).transpose()
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(report_df.iloc[:-3, :-1], annot=True, cmap='YlGnBu', fmt='.2f', ax=ax)
        plt.title(f'Classification Report - {self.model_name}')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved classification report to {save_path}")
        
        plt.close()
        
        self.reports['classification_report'] = report
        return report
    
    def learning_curve_plot(self, model, X, y, save_path=None):
        """Plot learning curve."""
        from sklearn.model_selection import learning_curve
        
        train_sizes, train_scores, val_scores = learning_curve(
            model, X, y,
            train_sizes=np.linspace(0.1, 1.0, 10),
            cv=5,
            n_jobs=-1,
            scoring='accuracy'
        )
        
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        plt.figure(figsize=(10, 6))
        plt.plot(train_sizes, train_mean, label='Training score', color='blue', marker='o')
        plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.15, color='blue')
        plt.plot(train_sizes, val_mean, label='Cross-validation score', color='green', marker='s')
        plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.15, color='green')
        
        plt.xlabel('Training Set Size')
        plt.ylabel('Accuracy Score')
        plt.title(f'Learning Curve - {self.model_name}')
        plt.legend(loc='lower right')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved learning curve to {save_path}")
        
        plt.close()
    
    def feature_importance_plot(self, model, feature_names, top_n=20, save_path=None):
        """Plot feature importance."""
        if not hasattr(model, 'feature_importances_'):
            logger.warning("Model does not have feature_importances_ attribute")
            return
        
        importance = model.feature_importances_
        indices = np.argsort(importance)[::-1][:top_n]
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(indices)), importance[indices])
        plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
        plt.xlabel('Feature Importance')
        plt.title(f'Top {top_n} Features - {self.model_name}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved feature importance to {save_path}")
        
        plt.close()
    
    def generate_full_report(self, model, X_train, y_train, X_test, y_test, feature_names=None):
        """Generate complete evaluation report."""
        logger.info(f"\n=== Generating Full Evaluation Report for {self.model_name} ===")
        
        # Get predictions
        y_pred_test = model.predict(X_test)
        y_pred_proba_test = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # Create reports directory
        Path('reports/figures').mkdir(parents=True, exist_ok=True)
        
        # Generate all plots
        self.confusion_matrix_plot(
            y_test, y_pred_test,
            f'reports/figures/{self.model_name}_confusion_matrix.png'
        )
        
        if y_pred_proba_test is not None:
            self.roc_curve_plot(
                y_test, y_pred_proba_test,
                f'reports/figures/{self.model_name}_roc_curve.png'
            )
            
            self.precision_recall_curve_plot(
                y_test, y_pred_proba_test,
                f'reports/figures/{self.model_name}_pr_curve.png'
            )
        
        self.classification_report_plot(
            y_test, y_pred_test,
            f'reports/figures/{self.model_name}_classification_report.png'
        )
        
        self.learning_curve_plot(
            model, X_train, y_train,
            f'reports/figures/{self.model_name}_learning_curve.png'
        )
        
        if feature_names is not None:
            self.feature_importance_plot(
                model, feature_names,
                save_path=f'reports/figures/{self.model_name}_feature_importance.png'
            )
        
        logger.info(f"✅ Full evaluation report generated")

# Usage
evaluator = ModelEvaluator("random_forest")
evaluator.generate_full_report(
    trainer.trained_model,
    X_train, y_train,
    X_test, y_test,
    feature_names=X_train.columns.tolist()
)
```

**Verification:**
- [ ] All metrics calculated
- [ ] Visualizations generated
- [ ] Reports created
- [ ] Plots saved
- [ ] Results interpretable

**If This Fails:**
→ Check predictions
→ Verify data types
→ Review metric requirements
→ Test plotting functions
→ Check file paths

---

### Step 3: Compare Multiple Models

**What:** Train and compare multiple algorithms systematically

**How:**

**Model Comparison:**
```python
# src/training/comparison.py
"""
Compare multiple models
"""

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import xgboost as xgb
import pandas as pd

class ModelComparison:
    """Compare multiple ML models."""
    
    def __init__(self, experiment_name="model_comparison"):
        self.experiment_name = experiment_name
        self.results = []
        self.models = {}
    
    def define_models(self):
        """Define models to compare."""
        self.models = {
            'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss'),
            'svm': SVC(probability=True, random_state=42),
            'knn': KNeighborsClassifier(n_neighbors=5)
        }
        
        return self.models
    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """Train and evaluate all models."""
        logger.info(f"\n=== Training {len(self.models)} models ===")
        
        for name, model in self.models.items():
            logger.info(f"\nTraining {name}...")
            
            # Create trainer
            trainer = ModelTrainer(model, name, self.experiment_name)
            
            # Train
            trainer.train(X_train, y_train)
            
            # Evaluate
            train_metrics, _, _ = trainer.evaluate(X_train, y_train, "train")
            test_metrics, _, _ = trainer.evaluate(X_test, y_test, "test")
            
            # Cross-validate
            cv_metrics = trainer.cross_validate(X_train, y_train, cv=5)
            
            # Store results
            result = {
                'model_name': name,
                **train_metrics,
                **test_metrics,
                **cv_metrics,
                'training_time': trainer.metrics.get('training_time_seconds', 0)
            }
            
            self.results.append(result)
            
            # Log to MLflow
            trainer.log_to_mlflow()
        
        logger.info(f"\n✅ All models trained")
    
    def get_comparison_table(self):
        """Get comparison table."""
        df = pd.DataFrame(self.results)
        
        # Sort by test accuracy
        df = df.sort_values('test_accuracy', ascending=False)
        
        return df
    
    def plot_comparison(self, metric='test_accuracy', save_path=None):
        """Plot model comparison."""
        df = self.get_comparison_table()
        
        plt.figure(figsize=(12, 6))
        plt.barh(df['model_name'], df[metric])
        plt.xlabel(metric.replace('_', ' ').title())
        plt.title('Model Comparison')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def select_best_model(self, metric='test_accuracy'):
        """Select best model based on metric."""
        df = self.get_comparison_table()
        best = df.iloc[0]
        
        logger.info(f"\n=== Best Model ===")
        logger.info(f"Model: {best['model_name']}")
        logger.info(f"{metric}: {best[metric]:.4f}")
        
        return best['model_name'], self.models[best['model_name']]

# Usage
comparison = ModelComparison()
comparison.define_models()
comparison.train_all_models(X_train, y_train, X_test, y_test)

# View results
results_df = comparison.get_comparison_table()
print("\n=== Model Comparison Results ===")
print(results_df[['model_name', 'test_accuracy', 'test_f1', 'cv_mean', 'training_time']])

# Plot
comparison.plot_comparison(save_path='reports/model_comparison.png')

# Select best
best_name, best_model = comparison.select_best_model()
```

**Verification:**
- [ ] All models trained
- [ ] Results compared
- [ ] Best model identified
- [ ] Comparison visualized
- [ ] Results logged

**If This Fails:**
→ Check model imports
→ Verify data compatibility
→ Review training process
→ Test models individually
→ Check resource usage

---

### Step 4: Implement Production Evaluation Pipeline

**What:** Create production-ready evaluation pipeline

**How:**

**Production Pipeline:**
```python
# src/training/production_pipeline.py
"""
Production training and evaluation pipeline
"""

import yaml
from pathlib import Path

class ProductionTrainingPipeline:
    """Complete production training pipeline."""
    
    def __init__(self, config_path='configs/training_config.yaml'):
        """Initialize pipeline."""
        self.config = self._load_config(config_path)
        self.best_model = None
        self.metrics = {}
    
    def _load_config(self, config_path):
        """Load configuration."""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def run_full_pipeline(self, X_train, y_train, X_test, y_test, feature_names=None):
        """Run complete training pipeline."""
        logger.info("\n" + "="*50)
        logger.info("STARTING PRODUCTION TRAINING PIPELINE")
        logger.info("="*50)
        
        # 1. Model comparison
        logger.info("\n[1/4] Comparing models...")
        comparison = ModelComparison(self.config['experiment_name'])
        comparison.define_models()
        comparison.train_all_models(X_train, y_train, X_test, y_test)
        
        # 2. Select best model
        logger.info("\n[2/4] Selecting best model...")
        best_name, best_model = comparison.select_best_model(
            metric=self.config.get('selection_metric', 'test_accuracy')
        )
        self.best_model = best_model
        
        # 3. Detailed evaluation of best model
        logger.info("\n[3/4] Evaluating best model...")
        evaluator = ModelEvaluator(best_name)
        evaluator.generate_full_report(
            best_model, X_train, y_train, X_test, y_test,
            feature_names=feature_names
        )
        
        # 4. Save best model
        logger.info("\n[4/4] Saving best model...")
        model_path = f"models/{best_name}_best.pkl"
        Path("models").mkdir(exist_ok=True)
        joblib.dump(best_model, model_path)
        logger.info(f"✅ Model saved to {model_path}")
        
        # Save metadata
        metadata = {
            'model_name': best_name,
            'model_path': model_path,
            'training_date': datetime.now().isoformat(),
            'metrics': comparison.get_comparison_table().to_dict('records')
        }
        
        metadata_path = 'models/best_model_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Metadata saved to {metadata_path}")
        logger.info("\n" + "="*50)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*50)
        
        return best_model, metadata

# Usage
pipeline = ProductionTrainingPipeline()
best_model, metadata = pipeline.run_full_pipeline(
    X_train, y_train,
    X_test, y_test,
    feature_names=X_train.columns.tolist()
)

print(f"\n✅ Best model: {metadata['model_name']}")
print(f"✅ Saved to: {metadata['model_path']}")
```

**Verification:**
- [ ] Pipeline runs end-to-end
- [ ] Best model selected
- [ ] Evaluation comprehensive
- [ ] Models saved
- [ ] Metadata tracked

**If This Fails:**
→ Test each stage separately
→ Check configuration
→ Verify file paths
→ Review error messages
→ Check resource availability

---

## Verification Checklist

After completing this workflow:

- [ ] Training infrastructure set up
- [ ] Models trained successfully
- [ ] Evaluation comprehensive
- [ ] Multiple models compared
- [ ] Best model selected
- [ ] Production pipeline ready
- [ ] Documentation complete
- [ ] Results reproducible

---

## Best Practices

### DO:
✅ Use cross-validation
✅ Evaluate on separate test set
✅ Track all experiments
✅ Compare multiple models
✅ Use multiple metrics
✅ Check for overfitting
✅ Save trained models
✅ Generate visualizations
✅ Document model selection
✅ Version control models
✅ Monitor training metrics
✅ Test on validation data first

### DON'T:
❌ Tune on test set
❌ Use single metric only
❌ Skip cross-validation
❌ Ignore overfitting
❌ Forget to save models
❌ Skip model comparison
❌ Use biased splits
❌ Ignore class imbalance
❌ Skip documentation
❌ Forget reproducibility
❌ Rush model selection
❌ Skip evaluation visualizations

---

## Related Workflows

**Prerequisites:**
- [data_preprocessing_pipelines.md](./data_preprocessing_pipelines.md) - Preprocessing
- [feature_engineering_selection.md](./feature_engineering_selection.md) - Features

**Next Steps:**
- [model_deployment_strategies.md](./model_deployment_strategies.md) - Deployment
- [model_monitoring_observability.md](./model_monitoring_observability.md) - Monitoring

**Related:**
- [automl_hyperparameter_optimization.md](./automl_hyperparameter_optimization.md) - Optimization
- [mlops_pipeline_setup.md](./mlops_pipeline_setup.md) - MLOps

---

## Tags
`machine-learning` `training` `evaluation` `sklearn` `mlflow` `cross-validation` `metrics` `model-comparison`
