# Model Monitoring & Observability

**ID:** mac-008  
**Category:** Machine Learning  
**Priority:** HIGH  
**Complexity:** Moderate  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement comprehensive monitoring and observability for production ML models including performance tracking, drift detection, data quality monitoring, and alerting

**Why:** Production models degrade over time due to data drift, concept drift, and changing business conditions - proactive monitoring prevents costly failures and ensures model reliability

**When to use:**
- Models deployed to production
- Need to track model performance
- Detecting data/concept drift
- Monitoring prediction quality
- Setting up alerts
- Debugging production issues
- Compliance and audit requirements
- SLA monitoring

---

## Prerequisites

**Required:**
- [ ] Model deployed to production
- [ ] Prometheus/Grafana knowledge (or similar)
- [ ] Logging infrastructure
- [ ] Alert notification system
- [ ] Access to production logs
- [ ] MLflow tracking configured

**Check before starting:**
```bash
# Check monitoring tools
docker ps | grep prometheus
docker ps | grep grafana

# Check MLflow
curl http://localhost:5000/health

# Verify logging
tail -f logs/model.log
```

---

## Implementation Steps

### Step 1: Implement Model Performance Monitoring

**What:** Track model prediction performance and accuracy metrics in real-time

**How:**

**Performance Metrics Tracker:**
```python
# src/monitoring/performance_tracker.py
"""
Model performance monitoring
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import mlflow
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error
)
import json
import logging
from typing import Dict, Any, List
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor model performance in production."""
    
    def __init__(self, model_name: str, metric_window: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            model_name: Name of the model to monitor
            metric_window: Number of recent predictions to track
        """
        self.model_name = model_name
        self.metric_window = metric_window
        
        # Sliding windows for metrics
        self.predictions = deque(maxlen=metric_window)
        self.actuals = deque(maxlen=metric_window)
        self.timestamps = deque(maxlen=metric_window)
        
        # Performance thresholds
        self.thresholds = {
            'accuracy': 0.85,
            'precision': 0.80,
            'recall': 0.75,
            'f1': 0.80,
            'latency_ms': 100
        }
        
        # Initialize MLflow
        mlflow.set_tracking_uri("http://mlflow:5000")
        
    def log_prediction(self, prediction: float, actual: float = None, 
                      latency_ms: float = None, metadata: Dict = None):
        """
        Log a single prediction.
        
        Args:
            prediction: Model prediction
            actual: Ground truth (if available)
            latency_ms: Prediction latency in milliseconds
            metadata: Additional metadata
        """
        timestamp = datetime.now()
        
        self.predictions.append(prediction)
        self.timestamps.append(timestamp)
        
        if actual is not None:
            self.actuals.append(actual)
        
        # Log to MLflow
        with mlflow.start_run(run_name=f"{self.model_name}_production"):
            mlflow.log_metric("prediction", prediction, step=len(self.predictions))
            
            if latency_ms:
                mlflow.log_metric("latency_ms", latency_ms, step=len(self.predictions))
            
            if actual is not None:
                mlflow.log_metric("actual", actual, step=len(self.predictions))
    
    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate current performance metrics."""
        if len(self.actuals) < 10:
            logger.warning("Insufficient data for metrics calculation")
            return {}
        
        predictions = np.array(list(self.predictions)[-len(self.actuals):])
        actuals = np.array(list(self.actuals))
        
        metrics = {
            'accuracy': accuracy_score(actuals, predictions > 0.5),
            'precision': precision_score(actuals, predictions > 0.5, average='weighted', zero_division=0),
            'recall': recall_score(actuals, predictions > 0.5, average='weighted', zero_division=0),
            'f1': f1_score(actuals, predictions > 0.5, average='weighted', zero_division=0),
            'sample_count': len(actuals)
        }
        
        try:
            metrics['roc_auc'] = roc_auc_score(actuals, predictions)
        except:
            pass
        
        return metrics
    
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check if metrics are below thresholds."""
        metrics = self.calculate_metrics()
        alerts = []
        
        for metric, value in metrics.items():
            if metric in self.thresholds:
                threshold = self.thresholds[metric]
                if value < threshold:
                    alerts.append({
                        'metric': metric,
                        'value': value,
                        'threshold': threshold,
                        'timestamp': datetime.now().isoformat(),
                        'severity': 'warning' if value > threshold * 0.9 else 'critical'
                    })
        
        return alerts
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        metrics = self.calculate_metrics()
        alerts = self.check_thresholds()
        
        report = {
            'model_name': self.model_name,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'alerts': alerts,
            'total_predictions': len(self.predictions),
            'labeled_predictions': len(self.actuals)
        }
        
        return report
    
    def save_report(self, filepath: str):
        """Save performance report to file."""
        report = self.generate_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {filepath}")

# Usage
monitor = PerformanceMonitor("credit_risk_model")

# Log predictions
monitor.log_prediction(prediction=0.75, actual=1, latency_ms=45.2)
monitor.log_prediction(prediction=0.23, actual=0, latency_ms=38.7)

# Check performance
metrics = monitor.calculate_metrics()
print(f"Current metrics: {metrics}")

# Check for alerts
alerts = monitor.check_thresholds()
if alerts:
    print(f"⚠️ Performance alerts: {alerts}")

# Generate report
report = monitor.generate_report()
monitor.save_report('reports/performance_report.json')
```

**Real-Time Dashboard Integration:**
```python
# src/monitoring/dashboard.py
"""
Real-time monitoring dashboard
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# Global monitor instance
monitor = PerformanceMonitor("credit_risk_model")

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics."""
    return jsonify(monitor.calculate_metrics())

@app.route('/api/alerts')
def get_alerts():
    """Get current alerts."""
    return jsonify(monitor.check_thresholds())

@app.route('/api/report')
def get_report():
    """Get full report."""
    return jsonify(monitor.generate_report())

@app.route('/')
def dashboard():
    """Render dashboard."""
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

**Verification:**
- [ ] Metrics tracked
- [ ] Thresholds configured
- [ ] Alerts triggered correctly
- [ ] Reports generated
- [ ] Dashboard accessible

**If This Fails:**
→ Check MLflow connection
→ Verify data collection
→ Review threshold values
→ Test with sample data
→ Check logging

---

### Step 2: Implement Data Drift Detection

**What:** Detect when input data distributions change over time

**How:**

**Drift Detection System:**
```python
# src/monitoring/drift_detector.py
"""
Data drift detection
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import warnings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDriftDetector:
    """Detect data drift in production."""
    
    def __init__(self, reference_data: pd.DataFrame, drift_threshold: float = 0.05):
        """
        Initialize drift detector.
        
        Args:
            reference_data: Training/reference dataset
            drift_threshold: p-value threshold for drift detection
        """
        self.reference_data = reference_data
        self.drift_threshold = drift_threshold
        self.reference_stats = self._calculate_stats(reference_data)
        
    def _calculate_stats(self, data: pd.DataFrame) -> Dict:
        """Calculate statistical properties of data."""
        stats_dict = {}
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                stats_dict[col] = {
                    'mean': float(data[col].mean()),
                    'std': float(data[col].std()),
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'median': float(data[col].median()),
                    'q25': float(data[col].quantile(0.25)),
                    'q75': float(data[col].quantile(0.75))
                }
            else:
                stats_dict[col] = {
                    'value_counts': data[col].value_counts().to_dict()
                }
        
        return stats_dict
    
    def kolmogorov_smirnov_test(self, feature: str, current_data: pd.DataFrame) -> Tuple[float, float]:
        """
        Perform Kolmogorov-Smirnov test for numerical features.
        
        Returns:
            (statistic, p_value)
        """
        if feature not in self.reference_data.columns:
            raise ValueError(f"Feature {feature} not in reference data")
        
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()
        
        statistic, p_value = stats.ks_2samp(ref_values, curr_values)
        
        return statistic, p_value
    
    def chi_square_test(self, feature: str, current_data: pd.DataFrame) -> Tuple[float, float]:
        """
        Perform Chi-square test for categorical features.
        
        Returns:
            (statistic, p_value)
        """
        ref_counts = self.reference_data[feature].value_counts()
        curr_counts = current_data[feature].value_counts()
        
        # Align categories
        all_categories = set(ref_counts.index) | set(curr_counts.index)
        ref_counts = ref_counts.reindex(all_categories, fill_value=0)
        curr_counts = curr_counts.reindex(all_categories, fill_value=0)
        
        # Perform chi-square test
        statistic, p_value = stats.chisquare(curr_counts, ref_counts)
        
        return statistic, p_value
    
    def psi_test(self, feature: str, current_data: pd.DataFrame, bins: int = 10) -> float:
        """
        Calculate Population Stability Index (PSI).
        
        PSI < 0.1: No significant change
        0.1 <= PSI < 0.2: Small change
        PSI >= 0.2: Significant change
        
        Returns:
            PSI value
        """
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()
        
        # Create bins based on reference data
        _, bin_edges = np.histogram(ref_values, bins=bins)
        
        # Calculate distributions
        ref_hist, _ = np.histogram(ref_values, bins=bin_edges)
        curr_hist, _ = np.histogram(curr_values, bins=bin_edges)
        
        # Normalize
        ref_dist = ref_hist / len(ref_values)
        curr_dist = curr_hist / len(curr_values)
        
        # Avoid division by zero
        ref_dist = np.where(ref_dist == 0, 0.0001, ref_dist)
        curr_dist = np.where(curr_dist == 0, 0.0001, curr_dist)
        
        # Calculate PSI
        psi = np.sum((curr_dist - ref_dist) * np.log(curr_dist / ref_dist))
        
        return float(psi)
    
    def detect_drift(self, current_data: pd.DataFrame) -> Dict:
        """
        Detect drift across all features.
        
        Returns:
            Dictionary with drift results per feature
        """
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'features': {},
            'drift_detected': False,
            'drifted_features': []
        }
        
        for col in self.reference_data.columns:
            feature_result = {
                'feature': col,
                'tests': {}
            }
            
            try:
                if pd.api.types.is_numeric_dtype(self.reference_data[col]):
                    # KS test
                    ks_stat, ks_p = self.kolmogorov_smirnov_test(col, current_data)
                    feature_result['tests']['ks_test'] = {
                        'statistic': float(ks_stat),
                        'p_value': float(ks_p),
                        'drift': ks_p < self.drift_threshold
                    }
                    
                    # PSI
                    psi = self.psi_test(col, current_data)
                    feature_result['tests']['psi'] = {
                        'value': float(psi),
                        'drift': psi >= 0.2
                    }
                    
                    # Check if drift detected
                    if ks_p < self.drift_threshold or psi >= 0.2:
                        drift_results['drifted_features'].append(col)
                        drift_results['drift_detected'] = True
                
                else:
                    # Chi-square test for categorical
                    chi_stat, chi_p = self.chi_square_test(col, current_data)
                    feature_result['tests']['chi_square'] = {
                        'statistic': float(chi_stat),
                        'p_value': float(chi_p),
                        'drift': chi_p < self.drift_threshold
                    }
                    
                    if chi_p < self.drift_threshold:
                        drift_results['drifted_features'].append(col)
                        drift_results['drift_detected'] = True
                
                drift_results['features'][col] = feature_result
                
            except Exception as e:
                logger.warning(f"Failed to test drift for {col}: {e}")
                feature_result['error'] = str(e)
        
        return drift_results
    
    def generate_drift_report(self, current_data: pd.DataFrame, save_path: str = None):
        """Generate and optionally save drift report."""
        report = self.detect_drift(current_data)
        
        # Add summary
        report['summary'] = {
            'total_features': len(self.reference_data.columns),
            'drifted_features_count': len(report['drifted_features']),
            'drift_percentage': len(report['drifted_features']) / len(self.reference_data.columns) * 100
        }
        
        # Log summary
        if report['drift_detected']:
            logger.warning(f"⚠️ Drift detected in {len(report['drifted_features'])} features: {report['drifted_features']}")
        else:
            logger.info("✅ No significant drift detected")
        
        # Save report
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Drift report saved to {save_path}")
        
        return report

# Usage
drift_detector = DataDriftDetector(X_train, drift_threshold=0.05)

# Check for drift
drift_report = drift_detector.detect_drift(X_production)

if drift_report['drift_detected']:
    print(f"⚠️ Drift detected in: {drift_report['drifted_features']}")
    
    # Trigger retraining
    print("🔄 Triggering model retraining...")
else:
    print("✅ No drift detected")

# Generate full report
drift_detector.generate_drift_report(X_production, 'reports/drift_report.json')
```

**Automated Drift Monitoring:**
```python
# src/monitoring/drift_monitor.py
"""
Automated drift monitoring
"""

import schedule
import time
from pathlib import Path

class DriftMonitor:
    """Automated drift monitoring service."""
    
    def __init__(self, detector: DataDriftDetector, check_interval_hours: int = 24):
        self.detector = detector
        self.check_interval_hours = check_interval_hours
        
    def check_drift(self):
        """Periodic drift check."""
        logger.info("Running drift detection...")
        
        # Load recent production data
        production_data = self._load_recent_data()
        
        if len(production_data) < 100:
            logger.warning("Insufficient data for drift detection")
            return
        
        # Detect drift
        report = self.detector.generate_drift_report(
            production_data,
            f'reports/drift_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        # Send alerts if drift detected
        if report['drift_detected']:
            self._send_alert(report)
    
    def _load_recent_data(self):
        """Load recent production data."""
        # Implementation depends on your data storage
        # This is a placeholder
        return pd.read_csv('data/production/recent.csv')
    
    def _send_alert(self, report):
        """Send drift alert."""
        logger.critical(f"DRIFT ALERT: {len(report['drifted_features'])} features drifting")
        
        # Send email, Slack, PagerDuty, etc.
        # Implementation depends on your alerting system
    
    def start(self):
        """Start monitoring service."""
        logger.info(f"Starting drift monitor (check every {self.check_interval_hours}h)")
        
        schedule.every(self.check_interval_hours).hours.do(self.check_drift)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

# Usage
monitor = DriftMonitor(drift_detector, check_interval_hours=24)
monitor.start()
```

**Verification:**
- [ ] Drift detection working
- [ ] Statistical tests accurate
- [ ] Alerts triggered
- [ ] Reports generated
- [ ] Monitoring automated

**If This Fails:**
→ Check statistical tests
→ Verify reference data
→ Review thresholds
→ Test with known drift
→ Check data formats

---

### Step 3: Set Up Prometheus Metrics and Grafana Dashboards

**What:** Export metrics to Prometheus and create Grafana dashboards

**How:**

**Prometheus Metrics Exporter:**
```python
# src/monitoring/prometheus_exporter.py
"""
Export model metrics to Prometheus
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import logging

logger = logging.getLogger(__name__)

# Define Prometheus metrics
prediction_counter = Counter(
    'model_predictions_total',
    'Total number of predictions made',
    ['model_name', 'version']
)

prediction_latency = Histogram(
    'model_prediction_latency_seconds',
    'Prediction latency in seconds',
    ['model_name'],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5]
)

prediction_errors = Counter(
    'model_prediction_errors_total',
    'Total number of prediction errors',
    ['model_name', 'error_type']
)

model_accuracy = Gauge(
    'model_accuracy',
    'Current model accuracy',
    ['model_name']
)

model_drift_score = Gauge(
    'model_drift_score',
    'Data drift score (PSI)',
    ['model_name', 'feature']
)

feature_value = Histogram(
    'model_feature_value',
    'Distribution of feature values',
    ['model_name', 'feature'],
    buckets=[i/10 for i in range(11)]
)

class PrometheusExporter:
    """Export ML model metrics to Prometheus."""
    
    def __init__(self, model_name: str, port: int = 8000):
        self.model_name = model_name
        self.port = port
        
    def start_server(self):
        """Start Prometheus metrics server."""
        start_http_server(self.port)
        logger.info(f"Prometheus metrics server started on port {self.port}")
    
    def log_prediction(self, latency: float, version: str = "v1"):
        """Log a prediction event."""
        prediction_counter.labels(
            model_name=self.model_name,
            version=version
        ).inc()
        
        prediction_latency.labels(
            model_name=self.model_name
        ).observe(latency)
    
    def log_error(self, error_type: str):
        """Log a prediction error."""
        prediction_errors.labels(
            model_name=self.model_name,
            error_type=error_type
        ).inc()
    
    def update_accuracy(self, accuracy: float):
        """Update model accuracy metric."""
        model_accuracy.labels(
            model_name=self.model_name
        ).set(accuracy)
    
    def update_drift_score(self, feature: str, psi_score: float):
        """Update drift score for a feature."""
        model_drift_score.labels(
            model_name=self.model_name,
            feature=feature
        ).set(psi_score)
    
    def log_feature_value(self, feature: str, value: float):
        """Log feature value for distribution tracking."""
        feature_value.labels(
            model_name=self.model_name,
            feature=feature
        ).observe(value)

# Integration with FastAPI
from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

app = FastAPI()
exporter = PrometheusExporter("credit_risk_model")

@app.on_event("startup")
async def startup():
    exporter.start_server()

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict")
async def predict(request: PredictionRequest):
    """Prediction endpoint with metrics."""
    start_time = time.time()
    
    try:
        # Make prediction
        result = model.predict(request.features)
        
        # Log metrics
        latency = time.time() - start_time
        exporter.log_prediction(latency)
        
        return {"prediction": result}
        
    except Exception as e:
        exporter.log_error(type(e).__name__)
        raise
```

**Prometheus Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ml-model-api'
    static_configs:
      - targets: ['ml-model-api:8000']
    metrics_path: '/metrics'
```

**Grafana Dashboard JSON:**
```json
{
  "dashboard": {
    "title": "ML Model Monitoring",
    "panels": [
      {
        "title": "Predictions per Second",
        "targets": [
          {
            "expr": "rate(model_predictions_total[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Prediction Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(model_prediction_latency_seconds_bucket[5m]))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Model Accuracy",
        "targets": [
          {
            "expr": "model_accuracy"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Data Drift Score",
        "targets": [
          {
            "expr": "model_drift_score"
          }
        ],
        "type": "heatmap"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(model_prediction_errors_total[5m])"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

**Docker Compose for Monitoring Stack:**
```yaml
# docker-compose-monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  prometheus_data:
  grafana_data:
```

**Verification:**
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards visible
- [ ] Metrics updating
- [ ] Alerts configured
- [ ] Retention configured

**If This Fails:**
→ Check Prometheus targets
→ Verify metrics endpoint
→ Review Grafana datasource
→ Check network connectivity
→ Review logs

---

### Step 4: Implement Comprehensive Logging

**What:** Set up structured logging for model predictions and errors

**How:**

**Structured Logging System:**
```python
# src/monitoring/logging_config.py
"""
Structured logging configuration
"""

import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class ModelLogger:
    """Structured logging for ML models."""
    
    def __init__(self, model_name: str, log_file: str = None):
        self.model_name = model_name
        self.logger = logging.getLogger(model_name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(name)s %(levelname)s %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_prediction(self, prediction_id: str, features: dict, 
                      prediction: float, probability: float = None,
                      latency_ms: float = None):
        """Log a prediction event."""
        log_entry = {
            'event': 'prediction',
            'model_name': self.model_name,
            'prediction_id': prediction_id,
            'features': features,
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        }
        
        if probability is not None:
            log_entry['probability'] = probability
        
        if latency_ms is not None:
            log_entry['latency_ms'] = latency_ms
        
        self.logger.info(json.dumps(log_entry))
    
    def log_error(self, error_type: str, error_message: str, 
                  context: dict = None):
        """Log an error event."""
        log_entry = {
            'event': 'error',
            'model_name': self.model_name,
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            log_entry['context'] = context
        
        self.logger.error(json.dumps(log_entry))
    
    def log_drift_alert(self, features: list, drift_scores: dict):
        """Log a drift detection alert."""
        log_entry = {
            'event': 'drift_alert',
            'model_name': self.model_name,
            'features': features,
            'drift_scores': drift_scores,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.warning(json.dumps(log_entry))
    
    def log_performance_degradation(self, metric: str, 
                                   current_value: float,
                                   threshold: float):
        """Log performance degradation alert."""
        log_entry = {
            'event': 'performance_degradation',
            'model_name': self.model_name,
            'metric': metric,
            'current_value': current_value,
            'threshold': threshold,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.warning(json.dumps(log_entry))

# Usage
model_logger = ModelLogger("credit_risk_model", "logs/model.log")

# Log prediction
model_logger.log_prediction(
    prediction_id="pred_12345",
    features={"age": 35, "income": 75000},
    prediction=0.75,
    probability=0.85,
    latency_ms=45.2
)

# Log error
model_logger.log_error(
    error_type="ValueError",
    error_message="Invalid feature value",
    context={"feature": "age", "value": -5}
)
```

**Log Analysis with ELK Stack:**
```yaml
# docker-compose-logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

**Verification:**
- [ ] Logs structured
- [ ] JSON format correct
- [ ] ELK stack running
- [ ] Logs indexed
- [ ] Searchable in Kibana

**If This Fails:**
→ Check log format
→ Verify ELK connectivity
→ Review Logstash config
→ Check Elasticsearch indices
→ Test log ingestion

---

### Step 5: Set Up Alerting and Incident Response

**What:** Configure alerts and incident response procedures

**How:**

**Alert Configuration:**
```python
# src/monitoring/alerting.py
"""
Alerting system for model monitoring
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class AlertManager:
    """Manage alerts for model monitoring."""
    
    def __init__(self, config: dict):
        self.config = config
        self.slack_webhook = config.get('slack_webhook')
        self.email_config = config.get('email', {})
        self.pagerduty_key = config.get('pagerduty_integration_key')
    
    def send_slack_alert(self, message: str, severity: str = 'warning'):
        """Send alert to Slack."""
        if not self.slack_webhook:
            logger.warning("Slack webhook not configured")
            return
        
        color = {
            'info': '#36a64f',
            'warning': '#ff9900',
            'critical': '#ff0000'
        }.get(severity, '#808080')
        
        payload = {
            'attachments': [{
                'color': color,
                'title': f'ML Model Alert - {severity.upper()}',
                'text': message,
                'footer': 'Model Monitoring System',
                'ts': int(time.time())
            }]
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload)
            response.raise_for_status()
            logger.info("Slack alert sent")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def send_email_alert(self, subject: str, body: str, recipients: list):
        """Send email alert."""
        if not self.email_config:
            logger.warning("Email not configured")
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from']
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        try:
            with smtplib.SMTP(self.email_config['smtp_server'], 
                            self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], 
                           self.email_config['password'])
                server.send_message(msg)
            
            logger.info(f"Email sent to {recipients}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def trigger_pagerduty(self, description: str, severity: str = 'warning'):
        """Trigger PagerDuty incident."""
        if not self.pagerduty_key:
            logger.warning("PagerDuty not configured")
            return
        
        payload = {
            'routing_key': self.pagerduty_key,
            'event_action': 'trigger',
            'payload': {
                'summary': description,
                'severity': severity,
                'source': 'ml-monitoring',
                'custom_details': {
                    'alert_type': 'model_performance'
                }
            }
        }
        
        try:
            response = requests.post(
                'https://events.pagerduty.com/v2/enqueue',
                json=payload
            )
            response.raise_for_status()
            logger.info("PagerDuty incident triggered")
        except Exception as e:
            logger.error(f"Failed to trigger PagerDuty: {e}")
    
    def send_alert(self, alert_type: str, message: str, 
                   severity: str = 'warning', metadata: dict = None):
        """Send alert through all configured channels."""
        logger.info(f"Sending {severity} alert: {message}")
        
        # Send to all channels
        self.send_slack_alert(message, severity)
        
        if severity in ['critical']:
            # Send email for critical alerts
            recipients = self.config.get('alert_recipients', [])
            self.send_email_alert(
                f"Critical Model Alert: {alert_type}",
                message,
                recipients
            )
            
            # Trigger PagerDuty for critical alerts
            self.trigger_pagerduty(message, 'critical')

# Alert rules configuration
alert_rules = {
    'accuracy_drop': {
        'threshold': 0.85,
        'severity': 'critical',
        'message': 'Model accuracy dropped below threshold'
    },
    'drift_detected': {
        'threshold': 0.2,  # PSI
        'severity': 'warning',
        'message': 'Data drift detected'
    },
    'high_latency': {
        'threshold': 100,  # ms
        'severity': 'warning',
        'message': 'Prediction latency above threshold'
    },
    'error_rate_high': {
        'threshold': 0.05,  # 5%
        'severity': 'critical',
        'message': 'Error rate above acceptable threshold'
    }
}

# Usage
alert_config = {
    'slack_webhook': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    'email': {
        'from': 'ml-alerts@company.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@company.com',
        'password': 'your_password'
    },
    'pagerduty_integration_key': 'YOUR_PAGERDUTY_KEY',
    'alert_recipients': ['ml-team@company.com']
}

alert_manager = AlertManager(alert_config)

# Send alert when threshold breached
if current_accuracy < 0.85:
    alert_manager.send_alert(
        'accuracy_drop',
        f'Model accuracy dropped to {current_accuracy:.2%}',
        severity='critical'
    )
```

**Verification:**
- [ ] Alerts configured
- [ ] Slack integration working
- [ ] Email alerts sent
- [ ] PagerDuty triggered
- [ ] Incident response tested

**If This Fails:**
→ Check webhook URLs
→ Verify SMTP settings
→ Test PagerDuty key
→ Review alert rules
→ Check network access

---

## Verification Checklist

After completing this workflow:

- [ ] Performance monitoring active
- [ ] Drift detection configured
- [ ] Prometheus/Grafana running
- [ ] Logging structured
- [ ] Alerts configured
- [ ] Dashboards created
- [ ] Incident response tested
- [ ] Documentation complete

---

## Best Practices

### DO:
✅ Monitor all key metrics
✅ Set appropriate thresholds
✅ Use multiple drift detection methods
✅ Implement structured logging
✅ Set up comprehensive dashboards
✅ Configure multi-channel alerts
✅ Test alert systems regularly
✅ Document monitoring procedures
✅ Track data quality
✅ Monitor latency and throughput
✅ Archive historical metrics
✅ Regular incident response drills

### DON'T:
❌ Ignore drift signals
❌ Set unrealistic thresholds
❌ Skip logging
❌ Alert on every anomaly
❌ Ignore performance trends
❌ Forget to test alerts
❌ Skip dashboard reviews
❌ Ignore minor degradations
❌ Use single detection method
❌ Forget documentation
❌ Skip regular reviews
❌ Ignore alert fatigue

---

## Related Workflows

**Prerequisites:**
- [model_deployment_strategies.md](./model_deployment_strategies.md) - Deployment
- [mlops_pipeline_setup.md](./mlops_pipeline_setup.md) - MLOps

**Next Steps:**
- [ab_testing_models.md](./ab_testing_models.md) - A/B Testing

**Related:**
- [observability_monitoring.md](../devops/observability_monitoring.md) - Observability

---

## Tags
`machine-learning` `monitoring` `observability` `drift-detection` `prometheus` `grafana` `alerting` `logging` `mlops` `performance`
