# A/B Testing ML Models

**ID:** mac-001  
**Category:** Machine Learning  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement A/B testing framework for comparing ML model performance in production with experiment design, traffic splitting, statistical analysis, and decision-making

**Why:** A/B testing enables data-driven model deployment decisions, validates improvements in real-world conditions, and minimizes risk when updating production models

**When to use:**
- Comparing new vs existing models
- Testing model improvements  
- Validating algorithm changes
- Model version rollout
- Risk mitigation
- Production validation

---

## Prerequisites

**Required:**
- [ ] Two or more trained models
- [ ] Production deployment infrastructure
- [ ] Traffic routing capability
- [ ] Metrics collection system
- [ ] Statistical analysis knowledge
- [ ] MLflow or experiment tracking

**Check before starting:**
```bash
# Check models available
ls -lh models/

# Verify deployment
kubectl get deployments -n ml-production

# Check metrics collection
curl http://prometheus:9090/api/v1/query?query=model_predictions_total
```

---

## Implementation Steps

### Step 1: Design A/B Test Experiment

**What:** Design statistically sound A/B test for model comparison

**How:**

**Experiment Design:**
```python
# src/ab_testing/experiment_design.py
"""
A/B test experiment design
"""

import numpy as np
from scipy import stats
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ExperimentConfig:
    """A/B test configuration."""
    name: str
    control_model: str
    treatment_model: str
    metric: str
    minimum_effect: float  # Minimum detectable effect
    alpha: float = 0.05   # Significance level  
    power: float = 0.80   # Statistical power
    traffic_split: dict = None
    
    def __post_init__(self):
        if not self.traffic_split:
            self.traffic_split = {'control': 0.5, 'treatment': 0.5}

class ExperimentDesigner:
    """Design A/B test experiments."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
    
    def calculate_sample_size(self, baseline_mean: float, baseline_std: float):
        """Calculate required sample size per variant."""
        effect_size = self.config.minimum_effect / baseline_std
        z_alpha = stats.norm.ppf(1 - self.config.alpha/2)
        z_beta = stats.norm.ppf(self.config.power)
        
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        self.required_sample_size = int(np.ceil(n))
        
        logger.info(f"Required sample size per variant: {self.required_sample_size:,}")
        return self.required_sample_size
    
    def estimate_duration(self, daily_traffic: int):
        """Estimate experiment duration in days."""
        control_traffic = daily_traffic * self.config.traffic_split['control']
        treatment_traffic = daily_traffic * self.config.traffic_split['treatment']
        
        days_control = self.required_sample_size / control_traffic
        days_treatment = self.required_sample_size / treatment_traffic
        days = max(days_control, days_treatment)
        
        logger.info(f"Estimated duration: {days:.1f} days")
        return days

# Usage
config = ExperimentConfig(
    name="model_v2_vs_v1",
    control_model="model_v1",
    treatment_model="model_v2",
    metric="accuracy",
    minimum_effect=0.02,  # 2% improvement
)

designer = ExperimentDesigner(config)
sample_size = designer.calculate_sample_size(baseline_mean=0.85, baseline_std=0.05)
duration = designer.estimate_duration(daily_traffic=10000)
```

**Verification:**
- [ ] Sample size calculated
- [ ] Duration estimated
- [ ] Config validated
- [ ] Plan documented

**If This Fails:**
→ Review baseline metrics
→ Adjust effect size
→ Check power calculation
→ Verify traffic estimates

---

### Step 2: Implement Traffic Splitting

**What:** Route traffic between control and treatment models

**How:**

**Traffic Splitter:**
```python
# src/ab_testing/traffic_splitter.py
"""
Traffic splitting for A/B testing
"""

import hashlib
import random

class TrafficSplitter:
    """Split traffic between variants."""
    
    def __init__(self, variants: dict, sticky=True):
        """
        Initialize traffic splitter.
        
        Args:
            variants: {'control': 0.5, 'treatment': 0.5}
            sticky: Use consistent hashing per user
        """
        self.variants = variants
        self.sticky = sticky
        
        # Create cumulative distribution
        self.cumulative = {}
        cumsum = 0
        for variant, allocation in sorted(variants.items()):
            cumsum += allocation
            self.cumulative[variant] = cumsum
    
    def assign_variant(self, user_id: str = None) -> str:
        """Assign user to variant."""
        if self.sticky and user_id:
            # Consistent hashing
            hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            random_value = (hash_value % 10000) / 10000.0
        else:
            random_value = random.random()
        
        for variant, threshold in self.cumulative.items():
            if random_value <= threshold:
                return variant
        
        return list(self.variants.keys())[0]

# FastAPI Integration
from fastapi import FastAPI, Header

app = FastAPI()
splitter = TrafficSplitter({'control': 0.5, 'treatment': 0.5})

@app.post("/predict")
async def predict(data: dict, x_user_id: str = Header(None)):
    """Prediction with A/B testing."""
    
    # Assign variant
    variant = splitter.assign_variant(x_user_id)
    
    # Load appropriate model
    model = load_model(f'models/model_{variant}.pkl')
    
    # Predict
    prediction = model.predict([data['features']])
    
    # Log for analysis
    log_prediction(x_user_id, variant, prediction)
    
    return {'prediction': prediction.tolist(), 'variant': variant}
```

**Verification:**
- [ ] Traffic split working
- [ ] Assignments consistent
- [ ] Routing correct
- [ ] Logging functional

**If This Fails:**
→ Check hash function
→ Verify split ratios  
→ Test with sample IDs
→ Check load balancing

---

### Step 3: Collect Experiment Data

**What:** Collect and store metrics from both variants

**How:**

**Data Collector:**
```python
# src/ab_testing/data_collector.py
"""
Collect A/B test data
"""

import pandas as pd
from datetime import datetime
import json

class ExperimentDataCollector:
    """Collect A/B test data."""
    
    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        self.data_file = f'experiments/{experiment_name}_data.jsonl'
    
    def log_prediction(self, user_id: str, variant: str, 
                      prediction: float, latency_ms: float,
                      actual: float = None):
        """Log a prediction."""
        record = {
            'experiment': self.experiment_name,
            'user_id': user_id,
            'variant': variant,
            'prediction': prediction,
            'actual': actual,
            'latency_ms': latency_ms,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.data_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def load_data(self) -> pd.DataFrame:
        """Load collected data."""
        records = []
        with open(self.data_file, 'r') as f:
            for line in f:
                records.append(json.loads(line))
        return pd.DataFrame(records)
    
    def get_variant_data(self, variant: str) -> pd.DataFrame:
        """Get data for specific variant."""
        df = self.load_data()
        return df[df['variant'] == variant]
    
    def calculate_metrics(self, variant: str) -> dict:
        """Calculate metrics for variant."""
        df = self.get_variant_data(variant)
        df_actuals = df[df['actual'].notna()]
        
        if len(df_actuals) == 0:
            return {}
        
        return {
            'sample_size': len(df_actuals),
            'accuracy': (df_actuals['prediction'].round() == df_actuals['actual']).mean(),
            'mean_latency_ms': df['latency_ms'].mean(),
            'p50_latency_ms': df['latency_ms'].quantile(0.5),
            'p95_latency_ms': df['latency_ms'].quantile(0.95)
        }

# Usage
collector = ExperimentDataCollector("model_v2_vs_v1")
collector.log_prediction("user123", "treatment", 0.75, 45.2, actual=1)

metrics = collector.calculate_metrics("treatment")
print(f"Treatment metrics: {metrics}")
```

**Verification:**
- [ ] Data logging working
- [ ] Metrics calculated
- [ ] Storage functional
- [ ] Queries working

**If This Fails:**
→ Check file permissions
→ Verify data format
→ Review storage path
→ Test with sample data

---

### Step 4: Perform Statistical Analysis

**What:** Analyze results and make data-driven decision

**How:**

**Statistical Analyzer:**
```python
# src/ab_testing/analyzer.py
"""
Statistical analysis for A/B tests
"""

from scipy import stats
import numpy as np

class ABTestAnalyzer:
    """Analyze A/B test results."""
    
    def __init__(self, collector: ExperimentDataCollector):
        self.collector = collector
    
    def t_test(self, control_variant='control', treatment_variant='treatment'):
        """Perform t-test comparing variants."""
        
        control_df = self.collector.get_variant_data(control_variant)
        treatment_df = self.collector.get_variant_data(treatment_variant)
        
        # Filter for actuals
        control_actuals = control_df[control_df['actual'].notna()]['actual'].values
        treatment_actuals = treatment_df[treatment_df['actual'].notna()]['actual'].values
        
        if len(control_actuals) == 0 or len(treatment_actuals) == 0:
            return {'error': 'Insufficient data'}
        
        # Perform t-test
        statistic, p_value = stats.ttest_ind(treatment_actuals, control_actuals)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(control_actuals) + np.var(treatment_actuals)) / 2)
        effect_size = (np.mean(treatment_actuals) - np.mean(control_actuals)) / pooled_std
        
        return {
            'control_mean': np.mean(control_actuals),
            'treatment_mean': np.mean(treatment_actuals),
            'absolute_difference': np.mean(treatment_actuals) - np.mean(control_actuals),
            'relative_lift': (np.mean(treatment_actuals) - np.mean(control_actuals)) / np.mean(control_actuals),
            'p_value': p_value,
            'effect_size': effect_size,
            'statistically_significant': p_value < 0.05,
            'control_n': len(control_actuals),
            'treatment_n': len(treatment_actuals)
        }
    
    def generate_report(self):
        """Generate comprehensive analysis report."""
        results = self.t_test()
        
        print("=== A/B Test Analysis Report ===\n")
        print(f"Control Mean: {results['control_mean']:.4f}")
        print(f"Treatment Mean: {results['treatment_mean']:.4f}")
        print(f"Absolute Difference: {results['absolute_difference']:.4f}")
        print(f"Relative Lift: {results['relative_lift']:.2%}")
        print(f"\nP-value: {results['p_value']:.4f}")
        print(f"Effect Size (Cohen's d): {results['effect_size']:.4f}")
        print(f"Sample Sizes: Control={results['control_n']}, Treatment={results['treatment_n']}")
        
        if results['statistically_significant']:
            if results['absolute_difference'] > 0:
                print("\n✅ DECISION: Deploy treatment model (statistically significant improvement)")
            else:
                print("\n❌ DECISION: Keep control model (treatment performed worse)")
        else:
            print("\n⚠️  DECISION: Continue testing (not statistically significant)")
        
        return results

# Usage
analyzer = ABTestAnalyzer(collector)
results = analyzer.generate_report()
```

**Verification:**
- [ ] Statistical tests working
- [ ] P-values calculated
- [ ] Effect size computed
- [ ] Decision clear
- [ ] Report generated

**If This Fails:**
→ Check sample sizes
→ Verify data quality
→ Review statistical assumptions
→ Test with known data
→ Check significance level

---

### Step 5: Make Deployment Decision

**What:** Make data-driven decision on model deployment

**How:**

**Decision Framework:**
```python
# src/ab_testing/decision.py
"""
Decision framework for A/B tests
"""

class DeploymentDecision:
    """Make deployment decision based on A/B test."""
    
    def __init__(self, experiment_config: ExperimentConfig):
        self.config = experiment_config
    
    def evaluate(self, analysis_results: dict) -> dict:
        """
        Evaluate if treatment should be deployed.
        
        Returns:
            Decision dict with recommendation and reasoning
        """
        checks = []
        passed = []
        
        # Check 1: Statistical significance
        if analysis_results['statistically_significant']:
            passed.append("Statistical significance achieved")
        else:
            checks.append("Not statistically significant")
        
        # Check 2: Minimum effect size
        if analysis_results['absolute_difference'] >= self.config.minimum_effect:
            passed.append(f"Effect size ({analysis_results['absolute_difference']:.4f}) >= minimum ({self.config.minimum_effect})")
        else:
            checks.append(f"Effect size too small: {analysis_results['absolute_difference']:.4f}")
        
        # Check 3: Sample size
        required_n = 100  # Simplified
        if analysis_results['control_n'] >= required_n and analysis_results['treatment_n'] >= required_n:
            passed.append("Sufficient sample size")
        else:
            checks.append("Insufficient sample size")
        
        # Check 4: Practical significance
        if analysis_results['relative_lift'] >= 0.01:  # 1% improvement
            passed.append("Practically significant improvement")
        else:
            checks.append("Improvement not practically significant")
        
        # Make decision
        deploy = len(checks) == 0
        
        decision = {
            'deploy_treatment': deploy,
            'recommendation': 'DEPLOY' if deploy else 'DO NOT DEPLOY',
            'passed_checks': passed,
            'failed_checks': checks,
            'confidence': 'HIGH' if deploy else 'LOW'
        }
        
        return decision
    
    def print_decision(self, decision: dict):
        """Print decision with reasoning."""
        print("\n" + "="*50)
        print(f"DEPLOYMENT DECISION: {decision['recommendation']}")
        print("="*50)
        
        print("\n✅ Passed Checks:")
        for check in decision['passed_checks']:
            print(f"  - {check}")
        
        if decision['failed_checks']:
            print("\n❌ Failed Checks:")
            for check in decision['failed_checks']:
                print(f"  - {check}")
        
        print(f"\nConfidence: {decision['confidence']}")

# Usage
decision_maker = DeploymentDecision(config)
results = analyzer.t_test()
decision = decision_maker.evaluate(results)
decision_maker.print_decision(decision)

if decision['deploy_treatment']:
    print("\n🚀 Proceeding with deployment...")
    # Deploy treatment model
else:
    print("\n⏸️  Keeping control model...")
```

**Verification:**
- [ ] Decision logic working
- [ ] All criteria checked
- [ ] Reasoning clear
- [ ] Action recommended
- [ ] Documentation generated

**If This Fails:**
→ Review decision criteria
→ Check thresholds
→ Validate logic
→ Test edge cases
→ Get stakeholder input

---

## Verification Checklist

After completing this workflow:

- [ ] Experiment designed
- [ ] Traffic splitting implemented
- [ ] Data collection working
- [ ] Statistical analysis complete
- [ ] Decision made
- [ ] Results documented
- [ ] Deployment executed or deferred

---

## Best Practices

### DO:
✅ Calculate required sample size upfront
✅ Use consistent user assignment (sticky)
✅ Monitor experiment continuously
✅ Check statistical assumptions
✅ Consider practical significance
✅ Document decision rationale
✅ Set clear success criteria
✅ Have rollback plan ready
✅ Monitor secondary metrics
✅ Communicate results clearly

### DON'T:
❌ Stop experiment early
❌ Change allocation mid-test
❌ Ignore statistical power
❌ Deploy without validation
❌ Forget about latency impact
❌ Skip confidence intervals
❌ Ignore business context
❌ Make decisions on p-value alone
❌ Forget to log outcomes
❌ Skip post-deployment monitoring

---

## Related Workflows

**Prerequisites:**
- [model_training_evaluation.md](./model_training_evaluation.md) - Training
- [model_deployment_strategies.md](./model_deployment_strategies.md) - Deployment

**Next Steps:**
- [model_monitoring_observability.md](./model_monitoring_observability.md) - Monitoring

**Related:**
- [mlops_pipeline_setup.md](./mlops_pipeline_setup.md) - MLOps

---

## Tags
`machine-learning` `ab-testing` `experimentation` `statistical-analysis` `model-comparison` `production` `deployment` `decision-making`
