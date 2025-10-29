# AutoML & Hyperparameter Optimization

**ID:** mac-002  
**Category:** Machine Learning  
**Priority:** MEDIUM  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Automate hyperparameter tuning and model selection using AutoML frameworks and optimization algorithms

**Why:** Manual hyperparameter tuning is time-consuming and suboptimal - automated optimization finds better configurations faster and more systematically

**When to use:**
- Optimizing model hyperparameters
- Exploring large parameter spaces
- Comparing many configurations
- Finding optimal model architectures
- Automating model selection
- Maximizing performance
- Reducing manual tuning time
- Building ML pipelines

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ with scikit-learn, optuna, hyperopt
- [ ] Trained baseline models
- [ ] Validation data for tuning
- [ ] Understanding of hyperparameters
- [ ] Computational resources

**Check before starting:**
```bash
# Check installations
pip install optuna hyperopt scikit-optimize auto-sklearn

# Verify installations
python -c "import optuna; import hyperopt; print('Ready')"
```

---

## Implementation Steps

### Step 1: Set Up Optuna for Hyperparameter Optimization

**What:** Configure Optuna for systematic hyperparameter search

**How:**

**Optuna Framework:**
```python
# src/optimization/optuna_tuner.py
"""
Hyperparameter optimization with Optuna
"""

import optuna
from optuna.integration import MLflowCallback
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
import mlflow
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import xgboost as xgb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptunaHyperparameterTuner:
    """Hyperparameter tuning with Optuna."""
    
    def __init__(self, model_type, X_train, y_train, X_val, y_val):
        """
        Parameters:
        -----------
        model_type : str
            Type of model: 'random_forest', 'xgboost', 'svm', etc.
        """
        self.model_type = model_type
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.best_params = None
        self.best_model = None
    
    def objective_random_forest(self, trial):
        """Objective function for Random Forest."""
        # Suggest hyperparameters
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 500),
            'max_depth': trial.suggest_int('max_depth', 5, 50),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
            'bootstrap': trial.suggest_categorical('bootstrap', [True, False]),
            'random_state': 42
        }
        
        # Train model
        model = RandomForestClassifier(**params)
        
        # Cross-validation score
        score = cross_val_score(
            model, self.X_train, self.y_train,
            cv=5, scoring='accuracy', n_jobs=-1
        ).mean()
        
        return score
    
    def objective_xgboost(self, trial):
        """Objective function for XGBoost."""
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 500),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 1),
            'random_state': 42,
            'eval_metric': 'logloss',
            'use_label_encoder': False
        }
        
        model = xgb.XGBClassifier(**params)
        
        score = cross_val_score(
            model, self.X_train, self.y_train,
            cv=5, scoring='accuracy', n_jobs=-1
        ).mean()
        
        return score
    
    def objective_svm(self, trial):
        """Objective function for SVM."""
        params = {
            'C': trial.suggest_float('C', 0.01, 100, log=True),
            'kernel': trial.suggest_categorical('kernel', ['linear', 'rbf', 'poly']),
            'gamma': trial.suggest_categorical('gamma', ['scale', 'auto']),
            'random_state': 42
        }
        
        if params['kernel'] == 'poly':
            params['degree'] = trial.suggest_int('degree', 2, 5)
        
        model = SVC(**params)
        
        score = cross_val_score(
            model, self.X_train, self.y_train,
            cv=5, scoring='accuracy', n_jobs=-1
        ).mean()
        
        return score
    
    def objective_gradient_boosting(self, trial):
        """Objective function for Gradient Boosting."""
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 500),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
            'random_state': 42
        }
        
        model = GradientBoostingClassifier(**params)
        
        score = cross_val_score(
            model, self.X_train, self.y_train,
            cv=5, scoring='accuracy', n_jobs=-1
        ).mean()
        
        return score
    
    def optimize(self, n_trials=100, timeout=None):
        """Run optimization."""
        logger.info(f"\n=== Starting Optuna Optimization for {self.model_type} ===")
        logger.info(f"Trials: {n_trials}, Timeout: {timeout}s")
        
        # Select objective function
        objectives = {
            'random_forest': self.objective_random_forest,
            'xgboost': self.objective_xgboost,
            'svm': self.objective_svm,
            'gradient_boosting': self.objective_gradient_boosting
        }
        
        if self.model_type not in objectives:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        objective = objectives[self.model_type]
        
        # Create study
        study = optuna.create_study(
            study_name=f"{self.model_type}_optimization",
            direction='maximize',
            sampler=TPESampler(seed=42),
            pruner=MedianPruner(n_startup_trials=10, n_warmup_steps=5)
        )
        
        # Optimize
        study.optimize(
            objective,
            n_trials=n_trials,
            timeout=timeout,
            show_progress_bar=True
        )
        
        # Store best parameters
        self.best_params = study.best_params
        
        logger.info(f"\n=== Optimization Complete ===")
        logger.info(f"Best value: {study.best_value:.4f}")
        logger.info(f"Best parameters:")
        for key, value in self.best_params.items():
            logger.info(f"  {key}: {value}")
        
        # Train final model with best parameters
        self._train_best_model()
        
        return study
    
    def _train_best_model(self):
        """Train model with best parameters."""
        logger.info("\nTraining final model with best parameters...")
        
        models = {
            'random_forest': RandomForestClassifier,
            'xgboost': xgb.XGBClassifier,
            'svm': SVC,
            'gradient_boosting': GradientBoostingClassifier
        }
        
        model_class = models[self.model_type]
        self.best_model = model_class(**self.best_params)
        self.best_model.fit(self.X_train, self.y_train)
        
        # Evaluate
        train_score = self.best_model.score(self.X_train, self.y_train)
        val_score = self.best_model.score(self.X_val, self.y_val)
        
        logger.info(f"Train accuracy: {train_score:.4f}")
        logger.info(f"Validation accuracy: {val_score:.4f}")
    
    def plot_optimization_history(self, study, save_path=None):
        """Plot optimization history."""
        from optuna.visualization import plot_optimization_history
        
        fig = plot_optimization_history(study)
        
        if save_path:
            fig.write_image(save_path)
            logger.info(f"Saved optimization history to {save_path}")
    
    def plot_param_importances(self, study, save_path=None):
        """Plot parameter importances."""
        from optuna.visualization import plot_param_importances
        
        fig = plot_param_importances(study)
        
        if save_path:
            fig.write_image(save_path)
            logger.info(f"Saved parameter importances to {save_path}")

# Usage
tuner = OptunaHyperparameterTuner(
    model_type='random_forest',
    X_train=X_train,
    y_train=y_train,
    X_val=X_val,
    y_val=y_val
)

# Optimize
study = tuner.optimize(n_trials=50)

# Get best model
best_model = tuner.best_model
best_params = tuner.best_params
```

**Verification:**
- [ ] Optuna configured
- [ ] Optimization running
- [ ] Best params found
- [ ] Model trained
- [ ] Results tracked

**If This Fails:**
→ Check objective function
→ Verify search space
→ Review trial logs
→ Reduce n_trials
→ Check memory usage

---

### Step 2: Implement Grid Search and Random Search

**What:** Use traditional hyperparameter search methods

**How:**

**Grid/Random Search:**
```python
# src/optimization/sklearn_search.py
"""
Grid Search and Random Search with scikit-learn
"""

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from scipy.stats import randint, uniform
import numpy as np

class SklearnHyperparameterSearch:
    """Hyperparameter search with scikit-learn."""
    
    def __init__(self, model, X_train, y_train):
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.best_estimator = None
        self.cv_results = None
    
    def grid_search(self, param_grid, cv=5, scoring='accuracy', n_jobs=-1):
        """Exhaustive grid search."""
        logger.info(f"\n=== Starting Grid Search ===")
        logger.info(f"Parameter grid: {param_grid}")
        
        grid_search = GridSearchCV(
            estimator=self.model,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=n_jobs,
            verbose=2,
            return_train_score=True
        )
        
        grid_search.fit(self.X_train, self.y_train)
        
        self.best_estimator = grid_search.best_estimator_
        self.cv_results = grid_search.cv_results_
        
        logger.info(f"\n=== Grid Search Complete ===")
        logger.info(f"Best score: {grid_search.best_score_:.4f}")
        logger.info(f"Best parameters: {grid_search.best_params_}")
        
        return grid_search
    
    def random_search(self, param_distributions, n_iter=100, cv=5, scoring='accuracy', n_jobs=-1):
        """Random search over parameters."""
        logger.info(f"\n=== Starting Random Search ===")
        logger.info(f"Iterations: {n_iter}")
        
        random_search = RandomizedSearchCV(
            estimator=self.model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=cv,
            scoring=scoring,
            n_jobs=n_jobs,
            verbose=2,
            random_state=42,
            return_train_score=True
        )
        
        random_search.fit(self.X_train, self.y_train)
        
        self.best_estimator = random_search.best_estimator_
        self.cv_results = random_search.cv_results_
        
        logger.info(f"\n=== Random Search Complete ===")
        logger.info(f"Best score: {random_search.best_score_:.4f}")
        logger.info(f"Best parameters: {random_search.best_params_}")
        
        return random_search

# Usage - Grid Search
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(random_state=42)
searcher = SklearnHyperparameterSearch(model, X_train, y_train)

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_result = searcher.grid_search(param_grid, cv=5)

# Usage - Random Search
param_distributions = {
    'n_estimators': randint(50, 500),
    'max_depth': randint(5, 50),
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': ['sqrt', 'log2', None]
}

random_result = searcher.random_search(param_distributions, n_iter=50)
```

**Verification:**
- [ ] Search methods working
- [ ] Best parameters found
- [ ] Cross-validation done
- [ ] Results comparable
- [ ] Models trained

**If This Fails:**
→ Check parameter grids
→ Verify CV folds
→ Review scoring metric
→ Reduce search space
→ Check computation time

---

### Step 3: Use AutoML Frameworks

**What:** Leverage AutoML for automated model selection and tuning

**How:**

**AutoML with TPOT:**
```python
# src/optimization/automl.py
"""
AutoML with TPOT and Auto-sklearn
"""

from tpot import TPOTClassifier
import logging

logger = logging.getLogger(__name__)

class AutoMLOptimizer:
    """AutoML optimization."""
    
    def __init__(self, X_train, y_train, X_val, y_val):
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.best_pipeline = None
    
    def tpot_optimize(self, generations=10, population_size=20, cv=5, scoring='accuracy'):
        """Optimize with TPOT."""
        logger.info(f"\n=== Starting TPOT Optimization ===")
        logger.info(f"Generations: {generations}, Population: {population_size}")
        
        tpot = TPOTClassifier(
            generations=generations,
            population_size=population_size,
            cv=cv,
            scoring=scoring,
            random_state=42,
            verbosity=2,
            n_jobs=-1,
            config_dict='TPOT light'  # Faster configuration
        )
        
        tpot.fit(self.X_train, self.y_train)
        
        # Evaluate
        train_score = tpot.score(self.X_train, self.y_train)
        val_score = tpot.score(self.X_val, self.y_val)
        
        logger.info(f"\n=== TPOT Optimization Complete ===")
        logger.info(f"Train accuracy: {train_score:.4f}")
        logger.info(f"Validation accuracy: {val_score:.4f}")
        
        # Export pipeline
        tpot.export('models/tpot_pipeline.py')
        logger.info(f"✅ Pipeline exported to models/tpot_pipeline.py")
        
        self.best_pipeline = tpot.fitted_pipeline_
        
        return tpot

# Usage
automl = AutoMLOptimizer(X_train, y_train, X_val, y_val)
tpot_result = automl.tpot_optimize(generations=5, population_size=20)

# Get best pipeline
best_pipeline = automl.best_pipeline
```

**Verification:**
- [ ] AutoML running
- [ ] Pipeline optimized
- [ ] Results better than baseline
- [ ] Pipeline exported
- [ ] Reproducible

**If This Fails:**
→ Reduce generations
→ Smaller population
→ Use lighter config
→ Check memory
→ Review time limits

---

### Step 4: Compare Optimization Methods

**What:** Compare results from different optimization approaches

**How:**

**Optimization Comparison:**
```python
# src/optimization/comparison.py
"""
Compare optimization methods
"""

import pandas as pd
import matplotlib.pyplot as plt

class OptimizationComparison:
    """Compare different optimization methods."""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, method_name, best_params, best_score, time_taken, n_trials=None):
        """Add optimization result."""
        self.results.append({
            'method': method_name,
            'best_score': best_score,
            'time_taken': time_taken,
            'n_trials': n_trials,
            'params': str(best_params)
        })
    
    def get_comparison_table(self):
        """Get comparison table."""
        df = pd.DataFrame(self.results)
        df = df.sort_values('best_score', ascending=False)
        return df
    
    def plot_comparison(self, save_path=None):
        """Plot comparison."""
        df = self.get_comparison_table()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Score comparison
        ax1.barh(df['method'], df['best_score'])
        ax1.set_xlabel('Best Score')
        ax1.set_title('Optimization Method Comparison - Accuracy')
        ax1.grid(alpha=0.3)
        
        # Time comparison
        ax2.barh(df['method'], df['time_taken'])
        ax2.set_xlabel('Time (seconds)')
        ax2.set_title('Optimization Method Comparison - Time')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved comparison to {save_path}")
        
        plt.close()
    
    def select_best_method(self):
        """Select best optimization method."""
        df = self.get_comparison_table()
        best = df.iloc[0]
        
        logger.info(f"\n=== Best Optimization Method ===")
        logger.info(f"Method: {best['method']}")
        logger.info(f"Score: {best['best_score']:.4f}")
        logger.info(f"Time: {best['time_taken']:.2f}s")
        
        return best

# Usage
comparison = OptimizationComparison()

# Add results from different methods
comparison.add_result('Optuna', optuna_best_params, optuna_score, optuna_time, n_trials=50)
comparison.add_result('Grid Search', grid_best_params, grid_score, grid_time, n_trials=len(param_grid))
comparison.add_result('Random Search', random_best_params, random_score, random_time, n_trials=50)
comparison.add_result('TPOT AutoML', tpot_params, tpot_score, tpot_time, n_trials=100)

# View results
print("\n=== Optimization Comparison ===")
print(comparison.get_comparison_table())

# Plot
comparison.plot_comparison('reports/optimization_comparison.png')

# Select best
best_method = comparison.select_best_method()
```

**Verification:**
- [ ] All methods compared
- [ ] Results tabulated
- [ ] Best method identified
- [ ] Visualizations created
- [ ] Trade-offs understood

**If This Fails:**
→ Check result formatting
→ Verify metrics
→ Review time tracking
→ Test plotting
→ Check data types

---

### Step 5: Create Production Optimization Pipeline

**What:** Package optimization for production use

**How:**

**Production Pipeline:**
```python
# src/optimization/production_pipeline.py
"""
Production hyperparameter optimization pipeline
"""

import yaml
import joblib
from pathlib import Path
import json

class ProductionOptimizationPipeline:
    """Production-ready optimization pipeline."""
    
    def __init__(self, config_path='configs/optimization_config.yaml'):
        self.config = self._load_config(config_path)
        self.best_model = None
        self.best_params = None
    
    def _load_config(self, config_path):
        """Load configuration."""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    def run_optimization(self, X_train, y_train, X_val, y_val):
        """Run complete optimization."""
        logger.info("\n" + "="*50)
        logger.info("STARTING OPTIMIZATION PIPELINE")
        logger.info("="*50)
        
        model_type = self.config['model_type']
        optimization_method = self.config['optimization_method']
        
        logger.info(f"\nModel: {model_type}")
        logger.info(f"Method: {optimization_method}")
        
        # Run optimization
        if optimization_method == 'optuna':
            tuner = OptunaHyperparameterTuner(
                model_type, X_train, y_train, X_val, y_val
            )
            study = tuner.optimize(
                n_trials=self.config.get('n_trials', 50)
            )
            self.best_model = tuner.best_model
            self.best_params = tuner.best_params
        
        elif optimization_method == 'automl':
            automl = AutoMLOptimizer(X_train, y_train, X_val, y_val)
            tpot = automl.tpot_optimize(
                generations=self.config.get('generations', 5),
                population_size=self.config.get('population_size', 20)
            )
            self.best_model = automl.best_pipeline
            self.best_params = {}
        
        # Save model
        model_path = f"models/{model_type}_optimized.pkl"
        Path("models").mkdir(exist_ok=True)
        joblib.dump(self.best_model, model_path)
        logger.info(f"\n✅ Model saved to {model_path}")
        
        # Save metadata
        metadata = {
            'model_type': model_type,
            'optimization_method': optimization_method,
            'best_params': self.best_params,
            'model_path': model_path,
            'optimization_date': datetime.now().isoformat()
        }
        
        metadata_path = 'models/optimization_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Metadata saved to {metadata_path}")
        logger.info("\n" + "="*50)
        logger.info("OPTIMIZATION COMPLETED")
        logger.info("="*50)
        
        return self.best_model, metadata

# Usage
pipeline = ProductionOptimizationPipeline()
best_model, metadata = pipeline.run_optimization(X_train, y_train, X_val, y_val)
```

**Verification:**
- [ ] Pipeline runs end-to-end
- [ ] Best model saved
- [ ] Metadata tracked
- [ ] Reproducible
- [ ] Production-ready

**If This Fails:**
→ Check configuration
→ Verify file paths
→ Review optimization settings
→ Test with small dataset
→ Check resource limits

---

## Verification Checklist

After completing this workflow:

- [ ] Optimization framework set up
- [ ] Multiple methods compared
- [ ] Best parameters found
- [ ] Models trained with best params
- [ ] Results documented
- [ ] Production pipeline ready
- [ ] Monitoring configured
- [ ] Reproducible

---

## Best Practices

### DO:
✅ Use validation set for tuning
✅ Set reasonable search spaces
✅ Use early stopping
✅ Track all trials
✅ Compare multiple methods
✅ Consider time budget
✅ Use cross-validation
✅ Monitor convergence
✅ Save best models
✅ Document parameters
✅ Version optimization configs
✅ Test on hold-out set

### DON'T:
❌ Tune on test set
❌ Infinite search space
❌ Ignore computation cost
❌ Skip baseline comparison
❌ Overfit to validation
❌ Forget random seed
❌ Use single trial
❌ Skip documentation
❌ Ignore convergence
❌ Rush optimization
❌ Skip reproducibility checks
❌ Forget resource limits

---

## Related Workflows

**Prerequisites:**
- [model_training_evaluation.md](./model_training_evaluation.md) - Training
- [ml_experiment_setup.md](./ml_experiment_setup.md) - Experiments

**Next Steps:**
- [model_deployment_strategies.md](./model_deployment_strategies.md) - Deployment
- [mlops_pipeline_setup.md](./mlops_pipeline_setup.md) - MLOps

**Related:**
- [feature_engineering_selection.md](./feature_engineering_selection.md) - Features

---

## Tags
`machine-learning` `hyperparameter-optimization` `automl` `optuna` `hyperopt` `grid-search` `random-search` `tpot` `mlops`
