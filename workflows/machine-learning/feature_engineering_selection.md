# Feature Engineering & Selection

**ID:** mac-005  
**Category:** Machine Learning  
**Priority:** MEDIUM  
**Complexity:** Moderate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Create informative features and select the most relevant ones to improve model performance and reduce dimensionality

**Why:** Good features are the foundation of successful ML models - they can significantly improve performance, reduce training time, and make models more interpretable

**When to use:**
- Starting new ML projects
- Model performance is suboptimal
- Too many features (curse of dimensionality)
- Need model interpretability
- Reducing training time
- Improving model generalization
- Creating domain-specific features
- Handling high-dimensional data

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ with scikit-learn, pandas, numpy
- [ ] Understanding of ML fundamentals
- [ ] Domain knowledge of the problem
- [ ] Clean, preprocessed data
- [ ] Basic statistical knowledge

**Check before starting:**
```bash
# Check installations
pip show scikit-learn pandas numpy scipy matplotlib seaborn

# Check data availability
python -c "import pandas as pd; print(pd.read_csv('data/processed/train.csv').shape)"
```

---

## Implementation Steps

### Step 1: Automated Feature Generation

**What:** Automatically generate features from existing columns

**How:**

**Mathematical Transformations:**
```python
# src/features/transformations.py
"""
Automated feature transformations
"""

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class MathematicalFeatureGenerator(BaseEstimator, TransformerMixin):
    """Generate mathematical features."""
    
    def __init__(self, operations=['log', 'sqrt', 'square', 'reciprocal']):
        """
        Parameters:
        -----------
        operations : list
            Mathematical operations to apply
        """
        self.operations = operations
        self.numerical_cols_ = []
    
    def fit(self, X, y=None):
        # Identify numerical columns
        if isinstance(X, pd.DataFrame):
            self.numerical_cols_ = X.select_dtypes(include=[np.number]).columns.tolist()
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X.copy()
        new_features = []
        
        for col in self.numerical_cols_:
            if col in X_df.columns:
                # Log transform
                if 'log' in self.operations and (X_df[col] > 0).all():
                    new_features.append(
                        pd.Series(np.log1p(X_df[col]), name=f'{col}_log')
                    )
                
                # Square root
                if 'sqrt' in self.operations and (X_df[col] >= 0).all():
                    new_features.append(
                        pd.Series(np.sqrt(X_df[col]), name=f'{col}_sqrt')
                    )
                
                # Square
                if 'square' in self.operations:
                    new_features.append(
                        pd.Series(np.square(X_df[col]), name=f'{col}_squared')
                    )
                
                # Reciprocal
                if 'reciprocal' in self.operations and (X_df[col] != 0).all():
                    new_features.append(
                        pd.Series(1 / X_df[col], name=f'{col}_reciprocal')
                    )
        
        if new_features:
            return pd.concat([X_df] + new_features, axis=1)
        return X_df

class InteractionFeatureGenerator(BaseEstimator, TransformerMixin):
    """Generate interaction features between numerical columns."""
    
    def __init__(self, interaction_type='all', max_interactions=20):
        """
        Parameters:
        -----------
        interaction_type : str
            'multiply', 'add', 'subtract', 'divide', 'all'
        max_interactions : int
            Maximum number of interaction features to create
        """
        self.interaction_type = interaction_type
        self.max_interactions = max_interactions
        self.interactions_ = []
    
    def fit(self, X, y=None):
        X_df = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X
        numerical_cols = X_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Generate all possible pairs
        from itertools import combinations
        pairs = list(combinations(numerical_cols, 2))
        
        # Limit number of interactions
        pairs = pairs[:self.max_interactions]
        self.interactions_ = pairs
        
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X.copy()
        new_features = []
        
        for col1, col2 in self.interactions_:
            if col1 in X_df.columns and col2 in X_df.columns:
                # Multiplication
                if self.interaction_type in ['multiply', 'all']:
                    new_features.append(
                        pd.Series(X_df[col1] * X_df[col2], name=f'{col1}_x_{col2}')
                    )
                
                # Addition
                if self.interaction_type in ['add', 'all']:
                    new_features.append(
                        pd.Series(X_df[col1] + X_df[col2], name=f'{col1}_plus_{col2}')
                    )
                
                # Subtraction
                if self.interaction_type in ['subtract', 'all']:
                    new_features.append(
                        pd.Series(X_df[col1] - X_df[col2], name=f'{col1}_minus_{col2}')
                    )
                
                # Division
                if self.interaction_type in ['divide', 'all'] and (X_df[col2] != 0).all():
                    new_features.append(
                        pd.Series(X_df[col1] / X_df[col2], name=f'{col1}_div_{col2}')
                    )
        
        if new_features:
            return pd.concat([X_df] + new_features, axis=1)
        return X_df

class AggregationFeatureGenerator(BaseEstimator, TransformerMixin):
    """Generate aggregation features across columns."""
    
    def __init__(self, aggregations=['mean', 'std', 'min', 'max']):
        """
        Parameters:
        -----------
        aggregations : list
            Aggregation functions to apply
        """
        self.aggregations = aggregations
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_df = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X.copy()
        numerical_cols = X_df.select_dtypes(include=[np.number]).columns
        new_features = []
        
        if 'mean' in self.aggregations:
            new_features.append(
                pd.Series(X_df[numerical_cols].mean(axis=1), name='row_mean')
            )
        
        if 'std' in self.aggregations:
            new_features.append(
                pd.Series(X_df[numerical_cols].std(axis=1), name='row_std')
            )
        
        if 'min' in self.aggregations:
            new_features.append(
                pd.Series(X_df[numerical_cols].min(axis=1), name='row_min')
            )
        
        if 'max' in self.aggregations:
            new_features.append(
                pd.Series(X_df[numerical_cols].max(axis=1), name='row_max')
            )
        
        if 'median' in self.aggregations:
            new_features.append(
                pd.Series(X_df[numerical_cols].median(axis=1), name='row_median')
            )
        
        if new_features:
            return pd.concat([X_df] + new_features, axis=1)
        return X_df

# Usage
from sklearn.pipeline import Pipeline

feature_generator = Pipeline([
    ('math', MathematicalFeatureGenerator()),
    ('interactions', InteractionFeatureGenerator(interaction_type='multiply', max_interactions=10)),
    ('aggregations', AggregationFeatureGenerator())
])

X_engineered = feature_generator.fit_transform(X_train)
print(f"Original features: {X_train.shape[1]}, New features: {X_engineered.shape[1]}")
```

**Domain-Specific Features:**
```python
# src/features/domain_features.py
"""
Domain-specific feature engineering
"""

class DatetimeFeaturesAdvanced(BaseEstimator, TransformerMixin):
    """Extract advanced datetime features."""
    
    def __init__(self, datetime_cols):
        self.datetime_cols = datetime_cols
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_df = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        new_features = []
        
        for col in self.datetime_cols:
            if col in X_df.columns:
                dt = pd.to_datetime(X_df[col])
                
                # Time-based features
                new_features.append(pd.Series(dt.dt.hour, name=f'{col}_hour'))
                new_features.append(pd.Series(dt.dt.dayofweek, name=f'{col}_dayofweek'))
                new_features.append(pd.Series(dt.dt.day, name=f'{col}_day'))
                new_features.append(pd.Series(dt.dt.month, name=f'{col}_month'))
                new_features.append(pd.Series(dt.dt.quarter, name=f'{col}_quarter'))
                new_features.append(pd.Series(dt.dt.year, name=f'{col}_year'))
                
                # Cyclical encoding
                new_features.append(pd.Series(np.sin(2 * np.pi * dt.dt.hour / 24), name=f'{col}_hour_sin'))
                new_features.append(pd.Series(np.cos(2 * np.pi * dt.dt.hour / 24), name=f'{col}_hour_cos'))
                new_features.append(pd.Series(np.sin(2 * np.pi * dt.dt.dayofweek / 7), name=f'{col}_day_sin'))
                new_features.append(pd.Series(np.cos(2 * np.pi * dt.dt.dayofweek / 7), name=f'{col}_day_cos'))
                
                # Binary features
                new_features.append(pd.Series((dt.dt.dayofweek >= 5).astype(int), name=f'{col}_is_weekend'))
                new_features.append(pd.Series((dt.dt.hour >= 9) & (dt.dt.hour <= 17), name=f'{col}_is_business_hours'))
        
        if new_features:
            return pd.concat([X_df] + new_features, axis=1)
        return X_df

class TextFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract features from text columns."""
    
    def __init__(self, text_cols, max_features=100):
        self.text_cols = text_cols
        self.max_features = max_features
        self.vectorizers_ = {}
    
    def fit(self, X, y=None):
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        X_df = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        
        for col in self.text_cols:
            if col in X_df.columns:
                vectorizer = TfidfVectorizer(
                    max_features=self.max_features,
                    stop_words='english'
                )
                vectorizer.fit(X_df[col].fillna(''))
                self.vectorizers_[col] = vectorizer
        
        return self
    
    def transform(self, X):
        X_df = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        text_features = []
        
        for col, vectorizer in self.vectorizers_.items():
            if col in X_df.columns:
                features = vectorizer.transform(X_df[col].fillna('')).toarray()
                feature_names = [f'{col}_tfidf_{i}' for i in range(features.shape[1])]
                text_features.append(pd.DataFrame(features, columns=feature_names, index=X_df.index))
        
        if text_features:
            return pd.concat([X_df] + text_features, axis=1)
        return X_df
```

**Verification:**
- [ ] Features generated correctly
- [ ] No data leakage
- [ ] Transformations make sense
- [ ] Performance improved
- [ ] Features interpretable

**If This Fails:**
→ Check for null values
→ Verify data types
→ Review domain logic
→ Test with sample data
→ Check feature correlations

---

### Step 2: Feature Importance Analysis

**What:** Analyze which features are most important for prediction

**How:**

**Feature Importance Methods:**
```python
# src/features/importance.py
"""
Feature importance analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.feature_selection import mutual_info_classif

class FeatureImportanceAnalyzer:
    """Analyze feature importance using multiple methods."""
    
    def __init__(self):
        self.importance_scores = {}
    
    def tree_based_importance(self, X, y, feature_names=None):
        """Calculate tree-based feature importance."""
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        importance = pd.DataFrame({
            'feature': feature_names,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.importance_scores['tree_based'] = importance
        return importance
    
    def permutation_importance_analysis(self, X, y, model=None, feature_names=None):
        """Calculate permutation importance."""
        if model is None:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
        
        perm_importance = permutation_importance(
            model, X, y,
            n_repeats=10,
            random_state=42,
            n_jobs=-1
        )
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        importance = pd.DataFrame({
            'feature': feature_names,
            'importance_mean': perm_importance.importances_mean,
            'importance_std': perm_importance.importances_std
        }).sort_values('importance_mean', ascending=False)
        
        self.importance_scores['permutation'] = importance
        return importance
    
    def mutual_information_importance(self, X, y, feature_names=None):
        """Calculate mutual information scores."""
        mi_scores = mutual_info_classif(X, y, random_state=42)
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        importance = pd.DataFrame({
            'feature': feature_names,
            'importance': mi_scores
        }).sort_values('importance', ascending=False)
        
        self.importance_scores['mutual_info'] = importance
        return importance
    
    def correlation_with_target(self, X, y, feature_names=None):
        """Calculate correlation with target."""
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        X_df = pd.DataFrame(X, columns=feature_names)
        correlations = X_df.corrwith(pd.Series(y)).abs()
        
        importance = pd.DataFrame({
            'feature': correlations.index,
            'importance': correlations.values
        }).sort_values('importance', ascending=False)
        
        self.importance_scores['correlation'] = importance
        return importance
    
    def plot_importance(self, method='tree_based', top_n=20):
        """Plot feature importance."""
        if method not in self.importance_scores:
            raise ValueError(f"No importance scores for method: {method}")
        
        importance = self.importance_scores[method].head(top_n)
        
        plt.figure(figsize=(10, 8))
        plt.barh(importance['feature'], importance['importance'])
        plt.xlabel('Importance')
        plt.title(f'Top {top_n} Features - {method.replace("_", " ").title()}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(f'reports/feature_importance_{method}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def get_consensus_ranking(self, top_n=50):
        """Get consensus feature ranking across methods."""
        all_rankings = []
        
        for method, scores in self.importance_scores.items():
            # Normalize scores to 0-1
            scores_copy = scores.copy()
            scores_copy['normalized'] = (
                (scores_copy['importance'] - scores_copy['importance'].min()) /
                (scores_copy['importance'].max() - scores_copy['importance'].min())
            )
            scores_copy['method'] = method
            all_rankings.append(scores_copy[['feature', 'normalized', 'method']])
        
        # Combine and average
        combined = pd.concat(all_rankings)
        consensus = combined.groupby('feature')['normalized'].mean().sort_values(ascending=False)
        
        return consensus.head(top_n)

# Usage
analyzer = FeatureImportanceAnalyzer()

# Run all methods
tree_importance = analyzer.tree_based_importance(X_train, y_train, feature_names)
perm_importance = analyzer.permutation_importance_analysis(X_train, y_train, feature_names=feature_names)
mi_importance = analyzer.mutual_information_importance(X_train, y_train, feature_names)
corr_importance = analyzer.correlation_with_target(X_train, y_train, feature_names)

# Plot
analyzer.plot_importance('tree_based', top_n=20)
analyzer.plot_importance('permutation', top_n=20)

# Get consensus
consensus_features = analyzer.get_consensus_ranking(top_n=50)
print("\n=== Top 20 Features (Consensus) ===")
print(consensus_features.head(20))
```

**Verification:**
- [ ] Importance calculated
- [ ] Multiple methods agree
- [ ] Results make sense
- [ ] Plots generated
- [ ] Top features identified

**If This Fails:**
→ Check for NaN values
→ Verify feature names
→ Review model training
→ Test with known features
→ Compare methods

---

### Step 3: Feature Selection Techniques

**What:** Select the most relevant features to improve model performance

**How:**

**Filter Methods:**
```python
# src/features/selection.py
"""
Feature selection techniques
"""

from sklearn.feature_selection import (
    SelectKBest, f_classif, chi2, mutual_info_classif,
    VarianceThreshold, SelectFromModel
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LassoCV

class FeatureSelector:
    """Select best features using multiple methods."""
    
    def __init__(self):
        self.selected_features_ = {}
    
    def variance_threshold_selection(self, X, threshold=0.01, feature_names=None):
        """Remove low variance features."""
        selector = VarianceThreshold(threshold=threshold)
        selector.fit(X)
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        selected = [f for f, s in zip(feature_names, selector.get_support()) if s]
        self.selected_features_['variance_threshold'] = selected
        
        print(f"Variance threshold: {len(selected)}/{len(feature_names)} features selected")
        return selected, selector
    
    def correlation_threshold_selection(self, X, threshold=0.95, feature_names=None):
        """Remove highly correlated features."""
        X_df = pd.DataFrame(X, columns=feature_names)
        corr_matrix = X_df.corr().abs()
        
        # Find features to drop
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
        
        selected = [f for f in feature_names if f not in to_drop]
        self.selected_features_['correlation_threshold'] = selected
        
        print(f"Correlation threshold: {len(selected)}/{len(feature_names)} features selected")
        return selected
    
    def univariate_selection(self, X, y, k=50, score_func=f_classif, feature_names=None):
        """Select k best features using univariate statistical tests."""
        selector = SelectKBest(score_func=score_func, k=k)
        selector.fit(X, y)
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        selected = [f for f, s in zip(feature_names, selector.get_support()) if s]
        self.selected_features_['univariate'] = selected
        
        print(f"Univariate selection: {len(selected)} features selected")
        return selected, selector
    
    def lasso_selection(self, X, y, feature_names=None):
        """Select features using Lasso regularization."""
        lasso = LassoCV(cv=5, random_state=42, max_iter=10000)
        lasso.fit(X, y)
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        # Select features with non-zero coefficients
        selected = [f for f, c in zip(feature_names, lasso.coef_) if abs(c) > 0]
        self.selected_features_['lasso'] = selected
        
        print(f"Lasso selection: {len(selected)}/{len(feature_names)} features selected")
        return selected, lasso
    
    def tree_based_selection(self, X, y, threshold='median', feature_names=None):
        """Select features using tree-based model."""
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        selector = SelectFromModel(model, threshold=threshold, prefit=True)
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        selected = [f for f, s in zip(feature_names, selector.get_support()) if s]
        self.selected_features_['tree_based'] = selected
        
        print(f"Tree-based selection: {len(selected)}/{len(feature_names)} features selected")
        return selected, selector
    
    def recursive_feature_elimination(self, X, y, n_features_to_select=50, feature_names=None):
        """RFE - recursively remove features."""
        from sklearn.feature_selection import RFE
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        rfe = RFE(estimator=model, n_features_to_select=n_features_to_select)
        rfe.fit(X, y)
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        selected = [f for f, s in zip(feature_names, rfe.support_) if s]
        self.selected_features_['rfe'] = selected
        
        print(f"RFE: {len(selected)} features selected")
        return selected, rfe
    
    def get_consensus_features(self, min_methods=2):
        """Get features selected by at least min_methods."""
        from collections import Counter
        
        all_features = []
        for features in self.selected_features_.values():
            all_features.extend(features)
        
        feature_counts = Counter(all_features)
        consensus = [f for f, count in feature_counts.items() if count >= min_methods]
        
        print(f"\nConsensus features (selected by ≥{min_methods} methods): {len(consensus)}")
        return consensus

# Usage
selector = FeatureSelector()

# Run multiple selection methods
variance_features, _ = selector.variance_threshold_selection(X_train, feature_names=feature_names)
corr_features = selector.correlation_threshold_selection(X_train, feature_names=feature_names)
univariate_features, _ = selector.univariate_selection(X_train, y_train, k=100, feature_names=feature_names)
lasso_features, _ = selector.lasso_selection(X_train, y_train, feature_names=feature_names)
tree_features, _ = selector.tree_based_selection(X_train, y_train, feature_names=feature_names)

# Get consensus
final_features = selector.get_consensus_features(min_methods=3)
print(f"\nFinal selected features: {len(final_features)}")
print(final_features[:20])
```

**Verification:**
- [ ] Features selected
- [ ] Multiple methods used
- [ ] Results compared
- [ ] Dimensionality reduced
- [ ] Model performance checked

**If This Fails:**
→ Try different thresholds
→ Review feature importance
→ Check method assumptions
→ Test on validation set
→ Compare model performance

---

### Step 4: Create Complete Feature Engineering Pipeline

**What:** Combine generation and selection into production pipeline

**How:**

**Complete Pipeline:**
```python
# src/features/pipeline.py
"""
Complete feature engineering pipeline
"""

from sklearn.pipeline import Pipeline

class FeatureEngineeringPipeline:
    """Complete feature engineering workflow."""
    
    def __init__(self, config):
        self.config = config
        self.pipeline = None
        self.selected_features = None
    
    def build_pipeline(self):
        """Build complete feature engineering pipeline."""
        
        # Feature generation
        generation_steps = [
            ('math_features', MathematicalFeatureGenerator()),
            ('interactions', InteractionFeatureGenerator(max_interactions=20)),
            ('aggregations', AggregationFeatureGenerator())
        ]
        
        # Feature selection (applied after generation)
        # Note: Selection requires fitting, so it's done separately
        
        self.pipeline = Pipeline(generation_steps)
        return self.pipeline
    
    def fit_transform(self, X, y):
        """Fit pipeline and select features."""
        
        # Generate features
        X_generated = self.pipeline.fit_transform(X)
        feature_names = X_generated.columns.tolist() if isinstance(X_generated, pd.DataFrame) else None
        
        # Analyze importance
        analyzer = FeatureImportanceAnalyzer()
        analyzer.tree_based_importance(X_generated, y, feature_names)
        analyzer.mutual_information_importance(X_generated, y, feature_names)
        
        # Select features
        selector = FeatureSelector()
        selector.variance_threshold_selection(X_generated, feature_names=feature_names)
        selector.correlation_threshold_selection(X_generated, feature_names=feature_names)
        selector.lasso_selection(X_generated, y, feature_names=feature_names)
        
        self.selected_features = selector.get_consensus_features(min_methods=2)
        
        # Return data with selected features
        X_selected = X_generated[self.selected_features]
        
        print(f"\n=== Feature Engineering Summary ===")
        print(f"Original features: {X.shape[1]}")
        print(f"Generated features: {X_generated.shape[1]}")
        print(f"Selected features: {len(self.selected_features)}")
        
        return X_selected
    
    def transform(self, X):
        """Transform new data."""
        X_generated = self.pipeline.transform(X)
        X_selected = X_generated[self.selected_features]
        return X_selected
    
    def save(self, filepath):
        """Save pipeline."""
        import joblib
        joblib.dump({
            'pipeline': self.pipeline,
            'selected_features': self.selected_features
        }, filepath)
        print(f"✅ Pipeline saved to {filepath}")
    
    def load(self, filepath):
        """Load pipeline."""
        import joblib
        data = joblib.load(filepath)
        self.pipeline = data['pipeline']
        self.selected_features = data['selected_features']
        print(f"✅ Pipeline loaded from {filepath}")

# Usage
fe_pipeline = FeatureEngineeringPipeline(config)
fe_pipeline.build_pipeline()

# Fit and transform training data
X_train_transformed = fe_pipeline.fit_transform(X_train, y_train)

# Transform test data
X_test_transformed = fe_pipeline.transform(X_test)

# Save for production
fe_pipeline.save('models/feature_engineering.pkl')
```

**Verification:**
- [ ] Pipeline built correctly
- [ ] Generation and selection combined
- [ ] Transforms consistently
- [ ] Save/load working
- [ ] Production-ready

**If This Fails:**
→ Test each component separately
→ Check feature name tracking
→ Verify transform consistency
→ Review selection criteria
→ Test with new data

---

### Step 5: Monitor Feature Performance

**What:** Track feature contributions and drift over time

**How:**

**Feature Monitoring:**
```python
# src/features/monitoring.py
"""
Monitor feature performance
"""

import json
from datetime import datetime

class FeatureMonitor:
    """Monitor feature performance and drift."""
    
    def __init__(self):
        self.baseline_stats = {}
        self.drift_threshold = 0.1
    
    def set_baseline(self, X, feature_names):
        """Set baseline statistics."""
        X_df = pd.DataFrame(X, columns=feature_names)
        
        for col in X_df.columns:
            self.baseline_stats[col] = {
                'mean': float(X_df[col].mean()),
                'std': float(X_df[col].std()),
                'min': float(X_df[col].min()),
                'max': float(X_df[col].max()),
                'median': float(X_df[col].median())
            }
        
        print(f"✅ Baseline set for {len(feature_names)} features")
    
    def detect_drift(self, X, feature_names):
        """Detect feature drift."""
        X_df = pd.DataFrame(X, columns=feature_names)
        drift_report = []
        
        for col in X_df.columns:
            if col in self.baseline_stats:
                baseline = self.baseline_stats[col]
                current_mean = X_df[col].mean()
                current_std = X_df[col].std()
                
                # Calculate relative change
                mean_change = abs(current_mean - baseline['mean']) / (baseline['mean'] + 1e-10)
                std_change = abs(current_std - baseline['std']) / (baseline['std'] + 1e-10)
                
                if mean_change > self.drift_threshold or std_change > self.drift_threshold:
                    drift_report.append({
                        'feature': col,
                        'mean_change': mean_change,
                        'std_change': std_change,
                        'baseline_mean': baseline['mean'],
                        'current_mean': current_mean
                    })
        
        if drift_report:
            print(f"⚠️  Drift detected in {len(drift_report)} features")
            for item in drift_report[:5]:
                print(f"  - {item['feature']}: mean changed by {item['mean_change']:.2%}")
        
        return drift_report
    
    def save_baseline(self, filepath):
        """Save baseline statistics."""
        with open(filepath, 'w') as f:
            json.dump(self.baseline_stats, f, indent=2)
    
    def load_baseline(self, filepath):
        """Load baseline statistics."""
        with open(filepath) as f:
            self.baseline_stats = json.load(f)

# Usage
monitor = FeatureMonitor()
monitor.set_baseline(X_train_transformed, selected_features)
monitor.save_baseline('models/feature_baseline.json')

# Later, check for drift
drift = monitor.detect_drift(X_new, selected_features)
```

**Verification:**
- [ ] Monitoring implemented
- [ ] Baseline captured
- [ ] Drift detection working
- [ ] Alerts configured
- [ ] Logs maintained

**If This Fails:**
→ Review drift thresholds
→ Check baseline quality
→ Verify statistics
→ Test with known drift
→ Improve detection logic

---

## Verification Checklist

After completing this workflow:

- [ ] Features generated
- [ ] Importance analyzed
- [ ] Features selected
- [ ] Pipeline created
- [ ] Monitoring set up
- [ ] Performance improved
- [ ] Documentation complete
- [ ] Production-ready

---

## Best Practices

### DO:
✅ Generate domain-specific features
✅ Analyze feature importance
✅ Use multiple selection methods
✅ Create reproducible pipelines
✅ Monitor feature drift
✅ Document feature engineering logic
✅ Test features on validation set
✅ Consider feature interpretability
✅ Version feature pipelines
✅ Track feature performance
✅ Remove redundant features
✅ Validate features make sense

### DON'T:
❌ Create features on test data
❌ Ignore domain knowledge
❌ Skip feature selection
❌ Create too many features
❌ Forget to scale features
❌ Ignore multicollinearity
❌ Skip importance analysis
❌ Hard-code feature logic
❌ Forget to monitor drift
❌ Create uninterpretable features
❌ Skip validation
❌ Ignore computational cost

---

## Related Workflows

**Prerequisites:**
- [data_preprocessing_pipelines.md](./data_preprocessing_pipelines.md) - Preprocessing

**Next Steps:**
- [model_training_evaluation.md](./model_training_evaluation.md) - Training
- [automl_hyperparameter_optimization.md](./automl_hyperparameter_optimization.md) - Optimization

**Related:**
- [ml_experiment_setup.md](./ml_experiment_setup.md) - Experiments

---

## Tags
`machine-learning` `feature-engineering` `feature-selection` `sklearn` `importance` `dimensionality-reduction` `mlops`
