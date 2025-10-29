# Data Preprocessing Pipelines

**ID:** mac-003  
**Category:** Machine Learning  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Build robust, reusable data preprocessing pipelines for machine learning that handle missing values, scaling, encoding, and feature transformations

**Why:** Consistent preprocessing ensures reproducibility, prevents data leakage, simplifies production deployment, and improves model performance

**When to use:**
- Preparing data for ML models
- Building production ML pipelines
- Ensuring consistent train/test preprocessing
- Automating data transformations
- Handling new data in production
- Creating reusable preprocessing components
- Preventing data leakage
- Standardizing feature engineering

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ installed
- [ ] scikit-learn knowledge
- [ ] Understanding of data preprocessing concepts
- [ ] Pandas proficiency
- [ ] Basic ML pipeline understanding

**Check before starting:**
```bash
# Check Python and packages
python --version
pip show scikit-learn pandas numpy

# Verify data availability
ls -lh data/raw/
```

---

## Implementation Steps

### Step 1: Design Preprocessing Pipeline Architecture

**What:** Define the pipeline architecture based on data types and transformations needed

**How:**

**Pipeline Architecture:**
```python
# src/preprocessing/pipeline_design.py
"""
Preprocessing pipeline architecture
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class ColumnType(Enum):
    """Column types for preprocessing."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"
    DATETIME = "datetime"
    TEXT = "text"
    TARGET = "target"

@dataclass
class ColumnConfig:
    """Configuration for a column."""
    name: str
    type: ColumnType
    transformations: List[str]
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}

@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""
    columns: List[ColumnConfig]
    target_column: str
    handle_outliers: bool = True
    feature_selection: bool = False
    feature_creation: bool = False
    
    def get_columns_by_type(self, column_type: ColumnType) -> List[str]:
        """Get columns of specific type."""
        return [
            col.name for col in self.columns
            if col.type == column_type
        ]

# Example configuration
config = PipelineConfig(
    columns=[
        ColumnConfig(
            name="age",
            type=ColumnType.NUMERICAL,
            transformations=["impute_median", "scale_standard"]
        ),
        ColumnConfig(
            name="income",
            type=ColumnType.NUMERICAL,
            transformations=["impute_median", "log_transform", "scale_standard"]
        ),
        ColumnConfig(
            name="gender",
            type=ColumnType.CATEGORICAL,
            transformations=["impute_mode", "one_hot_encode"]
        ),
        ColumnConfig(
            name="education",
            type=ColumnType.ORDINAL,
            transformations=["impute_mode", "ordinal_encode"],
            params={"categories": ["High School", "Bachelor", "Master", "PhD"]}
        ),
        ColumnConfig(
            name="signup_date",
            type=ColumnType.DATETIME,
            transformations=["extract_features"]
        ),
    ],
    target_column="churn",
    handle_outliers=True
)
```

**Verification:**
- [ ] Architecture defined
- [ ] Column types identified
- [ ] Transformations listed
- [ ] Config validated
- [ ] Dependencies clear

**If This Fails:**
→ Review data schema
→ Identify column types
→ Define transformations needed
→ Check for special cases
→ Consult domain experts

---

### Step 2: Implement Core Preprocessing Components

**What:** Create modular preprocessing components for different data types

**How:**

**Numerical Preprocessing:**
```python
# src/preprocessing/numerical.py
"""
Numerical data preprocessing components
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer
from scipy import stats

class NumericalImputer(BaseEstimator, TransformerMixin):
    """Impute missing numerical values."""
    
    def __init__(self, strategy='median'):
        """
        Parameters:
        -----------
        strategy : str, default='median'
            Options: 'mean', 'median', 'most_frequent', 'constant'
        """
        self.strategy = strategy
        self.imputer = SimpleImputer(strategy=strategy)
    
    def fit(self, X, y=None):
        self.imputer.fit(X)
        return self
    
    def transform(self, X):
        return self.imputer.transform(X)

class OutlierHandler(BaseEstimator, TransformerMixin):
    """Handle outliers in numerical features."""
    
    def __init__(self, method='clip', threshold=3.0):
        """
        Parameters:
        -----------
        method : str, default='clip'
            Options: 'clip', 'remove', 'cap'
        threshold : float, default=3.0
            Number of standard deviations for outlier detection
        """
        self.method = method
        self.threshold = threshold
        self.bounds_ = {}
    
    def fit(self, X, y=None):
        X_array = np.array(X)
        
        for i in range(X_array.shape[1]):
            col_data = X_array[:, i]
            mean = np.mean(col_data)
            std = np.std(col_data)
            
            lower_bound = mean - (self.threshold * std)
            upper_bound = mean + (self.threshold * std)
            
            self.bounds_[i] = (lower_bound, upper_bound)
        
        return self
    
    def transform(self, X):
        X_array = np.array(X).copy()
        
        if self.method == 'clip':
            for i, (lower, upper) in self.bounds_.items():
                X_array[:, i] = np.clip(X_array[:, i], lower, upper)
        
        return X_array

class LogTransformer(BaseEstimator, TransformerMixin):
    """Apply log transformation to skewed features."""
    
    def __init__(self, offset=1e-6):
        """
        Parameters:
        -----------
        offset : float, default=1e-6
            Small constant to add before log to avoid log(0)
        """
        self.offset = offset
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_array = np.array(X)
        return np.log(X_array + self.offset)

class SkewnessReducer(BaseEstimator, TransformerMixin):
    """Automatically reduce skewness using appropriate transformation."""
    
    def __init__(self, threshold=0.5):
        """
        Parameters:
        -----------
        threshold : float, default=0.5
            Skewness threshold to trigger transformation
        """
        self.threshold = threshold
        self.transformations_ = {}
    
    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        
        for col in X_df.columns:
            skewness = X_df[col].skew()
            
            if abs(skewness) > self.threshold:
                if skewness > 0:
                    self.transformations_[col] = 'log'
                else:
                    self.transformations_[col] = 'square'
            else:
                self.transformations_[col] = 'none'
        
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X)
        X_transformed = X_df.copy()
        
        for col, transform in self.transformations_.items():
            if transform == 'log':
                X_transformed[col] = np.log1p(X_df[col])
            elif transform == 'square':
                X_transformed[col] = np.square(X_df[col])
        
        return X_transformed.values

class FeatureScaler(BaseEstimator, TransformerMixin):
    """Scale features using various methods."""
    
    def __init__(self, method='standard'):
        """
        Parameters:
        -----------
        method : str, default='standard'
            Options: 'standard', 'minmax', 'robust'
        """
        self.method = method
        
        if method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
        elif method == 'robust':
            self.scaler = RobustScaler()
    
    def fit(self, X, y=None):
        self.scaler.fit(X)
        return self
    
    def transform(self, X):
        return self.scaler.transform(X)
```

**Categorical Preprocessing:**
```python
# src/preprocessing/categorical.py
"""
Categorical data preprocessing components
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder

class CategoricalImputer(BaseEstimator, TransformerMixin):
    """Impute missing categorical values."""
    
    def __init__(self, strategy='most_frequent', fill_value='missing'):
        """
        Parameters:
        -----------
        strategy : str, default='most_frequent'
            Options: 'most_frequent', 'constant'
        fill_value : str, default='missing'
            Value to use when strategy='constant'
        """
        self.strategy = strategy
        self.fill_value = fill_value
        self.fill_values_ = {}
    
    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        
        if self.strategy == 'most_frequent':
            for col in X_df.columns:
                self.fill_values_[col] = X_df[col].mode()[0] if len(X_df[col].mode()) > 0 else self.fill_value
        else:
            for col in X_df.columns:
                self.fill_values_[col] = self.fill_value
        
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X)
        X_filled = X_df.copy()
        
        for col, fill_value in self.fill_values_.items():
            X_filled[col] = X_df[col].fillna(fill_value)
        
        return X_filled.values

class FrequencyEncoder(BaseEstimator, TransformerMixin):
    """Encode categorical variables by their frequency."""
    
    def __init__(self):
        self.frequency_maps_ = {}
    
    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        
        for col in X_df.columns:
            freq_map = X_df[col].value_counts(normalize=True).to_dict()
            self.frequency_maps_[col] = freq_map
        
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X)
        X_encoded = X_df.copy()
        
        for col, freq_map in self.frequency_maps_.items():
            X_encoded[col] = X_df[col].map(freq_map).fillna(0)
        
        return X_encoded.values

class TargetEncoder(BaseEstimator, TransformerMixin):
    """Encode categorical variables using target mean."""
    
    def __init__(self, smoothing=1.0):
        """
        Parameters:
        -----------
        smoothing : float, default=1.0
            Smoothing parameter for regularization
        """
        self.smoothing = smoothing
        self.target_maps_ = {}
        self.global_mean_ = None
    
    def fit(self, X, y):
        X_df = pd.DataFrame(X)
        self.global_mean_ = np.mean(y)
        
        for col in X_df.columns:
            # Calculate target mean for each category
            target_mean = pd.DataFrame({
                'category': X_df[col],
                'target': y
            }).groupby('category')['target'].agg(['mean', 'count'])
            
            # Apply smoothing
            smoothed_mean = (
                (target_mean['mean'] * target_mean['count'] + 
                 self.global_mean_ * self.smoothing) /
                (target_mean['count'] + self.smoothing)
            )
            
            self.target_maps_[col] = smoothed_mean.to_dict()
        
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X)
        X_encoded = X_df.copy()
        
        for col, target_map in self.target_maps_.items():
            X_encoded[col] = X_df[col].map(target_map).fillna(self.global_mean_)
        
        return X_encoded.values
```

**Datetime Preprocessing:**
```python
# src/preprocessing/datetime.py
"""
Datetime preprocessing components
"""

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class DatetimeFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract features from datetime columns."""
    
    def __init__(self, features=['year', 'month', 'day', 'dayofweek', 'quarter']):
        """
        Parameters:
        -----------
        features : list, default=['year', 'month', 'day', 'dayofweek', 'quarter']
            Features to extract from datetime
        """
        self.features = features
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X)
        output_features = []
        
        for col in X_df.columns:
            dt_col = pd.to_datetime(X_df[col])
            
            if 'year' in self.features:
                output_features.append(dt_col.dt.year.values.reshape(-1, 1))
            if 'month' in self.features:
                output_features.append(dt_col.dt.month.values.reshape(-1, 1))
            if 'day' in self.features:
                output_features.append(dt_col.dt.day.values.reshape(-1, 1))
            if 'dayofweek' in self.features:
                output_features.append(dt_col.dt.dayofweek.values.reshape(-1, 1))
            if 'quarter' in self.features:
                output_features.append(dt_col.dt.quarter.values.reshape(-1, 1))
            if 'hour' in self.features:
                output_features.append(dt_col.dt.hour.values.reshape(-1, 1))
            if 'is_weekend' in self.features:
                is_weekend = (dt_col.dt.dayofweek >= 5).astype(int).values.reshape(-1, 1)
                output_features.append(is_weekend)
        
        return np.hstack(output_features)
```

**Verification:**
- [ ] Components implemented
- [ ] Fit/transform working
- [ ] Edge cases handled
- [ ] Documentation clear
- [ ] Tests passing

**If This Fails:**
→ Review transformations
→ Check data types
→ Test edge cases
→ Verify scikit-learn API
→ Debug with sample data

---

### Step 3: Build Complete Preprocessing Pipeline

**What:** Combine components into a complete, reusable pipeline

**How:**

**Complete Pipeline:**
```python
# src/preprocessing/pipeline.py
"""
Complete preprocessing pipeline
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
import joblib

class DataPreprocessor:
    """Complete data preprocessing pipeline."""
    
    def __init__(self, config: PipelineConfig):
        """Initialize with configuration."""
        self.config = config
        self.pipeline = None
        self._build_pipeline()
    
    def _build_pipeline(self):
        """Build preprocessing pipeline from config."""
        
        # Get columns by type
        numerical_cols = self.config.get_columns_by_type(ColumnType.NUMERICAL)
        categorical_cols = self.config.get_columns_by_type(ColumnType.CATEGORICAL)
        datetime_cols = self.config.get_columns_by_type(ColumnType.DATETIME)
        
        # Numerical pipeline
        numerical_pipeline = Pipeline([
            ('imputer', NumericalImputer(strategy='median')),
            ('outlier_handler', OutlierHandler(method='clip')),
            ('scaler', StandardScaler())
        ])
        
        # Categorical pipeline
        categorical_pipeline = Pipeline([
            ('imputer', CategoricalImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        # Datetime pipeline
        datetime_pipeline = Pipeline([
            ('extractor', DatetimeFeatureExtractor()),
            ('scaler', StandardScaler())
        ])
        
        # Combine pipelines
        transformers = []
        
        if numerical_cols:
            transformers.append(('num', numerical_pipeline, numerical_cols))
        
        if categorical_cols:
            transformers.append(('cat', categorical_pipeline, categorical_cols))
        
        if datetime_cols:
            transformers.append(('dt', datetime_pipeline, datetime_cols))
        
        self.pipeline = ColumnTransformer(
            transformers=transformers,
            remainder='drop'
        )
    
    def fit(self, X, y=None):
        """Fit the preprocessing pipeline."""
        self.pipeline.fit(X, y)
        return self
    
    def transform(self, X):
        """Transform data using fitted pipeline."""
        return self.pipeline.transform(X)
    
    def fit_transform(self, X, y=None):
        """Fit and transform in one step."""
        return self.pipeline.fit_transform(X, y)
    
    def get_feature_names(self):
        """Get output feature names."""
        try:
            return self.pipeline.get_feature_names_out()
        except AttributeError:
            # Fallback for older sklearn versions
            return [f"feature_{i}" for i in range(self.pipeline.transform(X_sample).shape[1])]
    
    def save(self, filepath):
        """Save pipeline to disk."""
        joblib.dump(self.pipeline, filepath)
        print(f"✅ Pipeline saved to {filepath}")
    
    def load(self, filepath):
        """Load pipeline from disk."""
        self.pipeline = joblib.load(filepath)
        print(f"✅ Pipeline loaded from {filepath}")

# Usage example
preprocessor = DataPreprocessor(config)

# Fit on training data
X_train_processed = preprocessor.fit_transform(X_train)

# Transform test data
X_test_processed = preprocessor.transform(X_test)

# Save for production
preprocessor.save('models/preprocessor.pkl')
```

**Advanced Pipeline with Custom Transformers:**
```python
# src/preprocessing/advanced_pipeline.py
"""
Advanced preprocessing pipeline with custom transformers
"""

from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureInteractionCreator(BaseEstimator, TransformerMixin):
    """Create interaction features."""
    
    def __init__(self, interactions):
        """
        Parameters:
        -----------
        interactions : list of tuples
            Pairs of column indices to create interactions
        """
        self.interactions = interactions
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_array = np.array(X)
        interaction_features = []
        
        for col1, col2 in self.interactions:
            interaction = X_array[:, col1] * X_array[:, col2]
            interaction_features.append(interaction.reshape(-1, 1))
        
        if interaction_features:
            return np.hstack([X_array] + interaction_features)
        return X_array

class PolynomialFeaturesCustom(BaseEstimator, TransformerMixin):
    """Create polynomial features for specific columns."""
    
    def __init__(self, degree=2, column_indices=None):
        """
        Parameters:
        -----------
        degree : int, default=2
            Polynomial degree
        column_indices : list, optional
            Indices of columns to create polynomial features for
        """
        self.degree = degree
        self.column_indices = column_indices
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_array = np.array(X)
        
        if self.column_indices is None:
            self.column_indices = list(range(X_array.shape[1]))
        
        poly_features = []
        for idx in self.column_indices:
            for d in range(2, self.degree + 1):
                poly_features.append(np.power(X_array[:, idx], d).reshape(-1, 1))
        
        if poly_features:
            return np.hstack([X_array] + poly_features)
        return X_array

# Complete advanced pipeline
def create_advanced_pipeline():
    """Create advanced preprocessing pipeline."""
    
    pipeline = Pipeline([
        # Stage 1: Basic preprocessing
        ('preprocessor', DataPreprocessor(config)),
        
        # Stage 2: Feature engineering
        ('interactions', FeatureInteractionCreator(interactions=[(0, 1), (2, 3)])),
        
        # Stage 3: Polynomial features
        ('polynomial', PolynomialFeaturesCustom(degree=2, column_indices=[0, 1, 2])),
        
        # Stage 4: Final scaling
        ('scaler', StandardScaler())
    ])
    
    return pipeline
```

**Verification:**
- [ ] Pipeline built correctly
- [ ] All transformations applied
- [ ] Feature names tracked
- [ ] Save/load working
- [ ] Reproducible results

**If This Fails:**
→ Check component compatibility
→ Verify column names
→ Test each stage separately
→ Review transformation order
→ Check for data leakage

---

### Step 4: Implement Data Validation and Quality Checks

**What:** Add validation to ensure data quality before and after preprocessing

**How:**

**Data Validation:**
```python
# src/preprocessing/validation.py
"""
Data validation and quality checks
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ValidationResult:
    """Result of data validation."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]

class DataValidator:
    """Validate data quality."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Validate dataframe."""
        errors = []
        warnings = []
        metrics = {}
        
        # Check required columns
        required_cols = [col.name for col in self.config.columns]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check for excessive missing values
        missing_pct = df.isnull().sum() / len(df) * 100
        for col, pct in missing_pct.items():
            if pct > 50:
                errors.append(f"Column {col} has {pct:.1f}% missing values")
            elif pct > 20:
                warnings.append(f"Column {col} has {pct:.1f}% missing values")
        
        metrics['missing_percentage'] = missing_pct.to_dict()
        
        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            warnings.append(f"Found {dup_count} duplicate rows")
        metrics['duplicate_count'] = int(dup_count)
        
        # Check data types
        for col_config in self.config.columns:
            if col_config.name in df.columns:
                if col_config.type == ColumnType.NUMERICAL:
                    if not pd.api.types.is_numeric_dtype(df[col_config.name]):
                        errors.append(f"Column {col_config.name} should be numerical")
        
        # Check for outliers
        numerical_cols = self.config.get_columns_by_type(ColumnType.NUMERICAL)
        for col in numerical_cols:
            if col in df.columns:
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                outlier_count = (z_scores > 3).sum()
                if outlier_count > len(df) * 0.05:  # More than 5%
                    warnings.append(f"Column {col} has {outlier_count} outliers")
                metrics[f'{col}_outliers'] = int(outlier_count)
        
        passed = len(errors) == 0
        
        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def print_report(self, result: ValidationResult):
        """Print validation report."""
        print("\n=== Data Validation Report ===")
        print(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
        
        if result.errors:
            print("\n❌ Errors:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print("\n📊 Metrics:")
        for key, value in result.metrics.items():
            print(f"  - {key}: {value}")

# Usage
validator = DataValidator(config)
result = validator.validate(df)
validator.print_report(result)

if not result.passed:
    raise ValueError("Data validation failed")
```

**Verification:**
- [ ] Validation implemented
- [ ] Checks comprehensive
- [ ] Reports clear
- [ ] Thresholds appropriate
- [ ] Errors caught

**If This Fails:**
→ Review validation rules
→ Adjust thresholds
→ Add more checks
→ Test with bad data
→ Improve error messages

---

### Step 5: Create Production-Ready Pipeline with Monitoring

**What:** Package pipeline for production with monitoring and logging

**How:**

**Production Pipeline:**
```python
# src/preprocessing/production_pipeline.py
"""
Production-ready preprocessing pipeline
"""

import logging
import time
from pathlib import Path
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionPreprocessor:
    """Production preprocessing pipeline with monitoring."""
    
    def __init__(self, config_path: str, model_path: str = None):
        """Initialize production preprocessor."""
        self.config = self._load_config(config_path)
        self.preprocessor = DataPreprocessor(self.config)
        self.validator = DataValidator(self.config)
        
        if model_path and Path(model_path).exists():
            self.preprocessor.load(model_path)
            logger.info(f"Loaded preprocessor from {model_path}")
    
    def _load_config(self, config_path: str):
        """Load configuration."""
        # Implementation depends on config format
        pass
    
    def process_batch(self, df: pd.DataFrame) -> np.ndarray:
        """Process a batch of data."""
        start_time = time.time()
        
        try:
            # Validate input
            logger.info("Validating input data")
            validation_result = self.validator.validate(df)
            
            if not validation_result.passed:
                logger.error("Data validation failed")
                raise ValueError(f"Validation errors: {validation_result.errors}")
            
            # Transform
            logger.info(f"Processing {len(df)} samples")
            X_transformed = self.preprocessor.transform(df)
            
            # Log metrics
            processing_time = time.time() - start_time
            logger.info(f"✅ Processed {len(df)} samples in {processing_time:.2f}s")
            
            # Save metrics
            self._log_metrics({
                'timestamp': datetime.now().isoformat(),
                'samples_processed': len(df),
                'processing_time': processing_time,
                'validation_warnings': len(validation_result.warnings)
            })
            
            return X_transformed
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    
    def _log_metrics(self, metrics: dict):
        """Log processing metrics."""
        metrics_file = 'logs/preprocessing_metrics.jsonl'
        Path('logs').mkdir(exist_ok=True)
        
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')

# Usage
processor = ProductionPreprocessor(
    config_path='configs/preprocessing_config.yaml',
    model_path='models/preprocessor.pkl'
)

# Process new data
X_processed = processor.process_batch(new_data)
```

**Verification:**
- [ ] Production pipeline ready
- [ ] Monitoring working
- [ ] Logging configured
- [ ] Error handling robust
- [ ] Performance acceptable

**If This Fails:**
→ Review production requirements
→ Add error handling
→ Improve logging
→ Test with production data
→ Monitor performance

---

## Verification Checklist

After completing this workflow:

- [ ] Pipeline architecture designed
- [ ] Components implemented
- [ ] Complete pipeline built
- [ ] Validation added
- [ ] Production-ready
- [ ] Documentation complete
- [ ] Tests passing
- [ ] Performance acceptable

---

## Best Practices

### DO:
✅ Fit only on training data
✅ Use scikit-learn Pipeline
✅ Handle missing values consistently
✅ Scale features appropriately
✅ Validate data before processing
✅ Save fitted preprocessors
✅ Track feature names
✅ Monitor preprocessing metrics
✅ Handle edge cases
✅ Document transformations
✅ Version preprocessing pipelines
✅ Test with production data

### DON'T:
❌ Fit on test data (data leakage)
❌ Inconsistent train/test preprocessing
❌ Skip validation
❌ Hard-code transformations
❌ Forget to save preprocessors
❌ Ignore outliers
❌ Skip documentation
❌ Forget error handling
❌ Mix fit and transform
❌ Lose feature interpretability
❌ Skip testing
❌ Ignore production requirements

---

## Related Workflows

**Prerequisites:**
- [ml_experiment_setup.md](./ml_experiment_setup.md) - Experiment setup

**Next Steps:**
- [feature_engineering_selection.md](./feature_engineering_selection.md) - Feature engineering
- [model_training_evaluation.md](./model_training_evaluation.md) - Model training

**Related:**
- [mlops_pipeline_setup.md](./mlops_pipeline_setup.md) - MLOps pipelines

---

## Tags
`machine-learning` `preprocessing` `sklearn` `pipeline` `data-cleaning` `feature-scaling` `encoding` `imputation` `mlops`
