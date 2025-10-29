# Application Monitoring Setup

**ID:** devops-001  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 2-3 hours  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for setting up comprehensive application monitoring with metrics, logs, traces, and alerting

**Why:** Monitoring provides visibility into system health, performance, and user experience. It enables proactive issue detection, faster incident response, capacity planning, and informed decision-making. Without monitoring, you're blind to production issues until users complain.

**When to use:**
- Deploying new applications to production
- Implementing observability for existing systems
- Debugging performance or reliability issues
- Meeting SLA/SLO requirements
- Enabling data-driven capacity planning
- Supporting on-call and incident response

---

## Prerequisites

**Required:**
- [ ] Application deployed and accessible
- [ ] Infrastructure access (Kubernetes, VMs, or cloud)
- [ ] Understanding of key metrics for your application
- [ ] Monitoring platform chosen (Prometheus, DataDog, New Relic, etc.)
- [ ] Alert destination configured (Slack, PagerDuty, email)

**Check before starting:**
```bash
# Verify application is running
curl http://your-app.com/health

# Check if app exposes metrics endpoint
curl http://your-app.com/metrics

# Verify infrastructure access
kubectl get pods  # Kubernetes
# or
ssh user@server  # Traditional servers

# Check monitoring namespace (K8s)
kubectl get namespace monitoring
```

---

## Implementation Steps

### Step 1: Choose Monitoring Stack and Architecture

**What:** Select appropriate monitoring tools and design monitoring architecture

**How:**
Evaluate options based on scale, budget, and requirements, then design the three pillars of observability.

**Code/Commands:**
```bash
# Document monitoring architecture
cat > MONITORING_ARCHITECTURE.md <<'EOF'
# Monitoring Architecture

## Observability Pillars

### 1. Metrics (Prometheus + Grafana)
**What:** Numerical measurements over time
**Examples:** 
- Request rate, error rate, duration (RED metrics)
- CPU, memory, disk usage (Resource metrics)
- Business metrics (signups, transactions, revenue)

**Stack:**
- **Collection:** Prometheus
- **Visualization:** Grafana
- **Alerting:** Alertmanager
- **Retention:** 30 days (Prometheus), 1 year (Thanos/Cortex)

### 2. Logs (ELK Stack or Loki)
**What:** Discrete events with context
**Examples:**
- Application logs (errors, warnings, info)
- Access logs
- Audit logs

**Stack:**
- **Collection:** Fluentd/Fluent Bit
- **Storage:** Elasticsearch / Loki
- **Visualization:** Kibana / Grafana
- **Retention:** 90 days

### 3. Traces (Jaeger or Tempo)
**What:** Request flow through distributed systems
**Examples:**
- API call chains
- Database query performance
- External service calls

**Stack:**
- **Instrumentation:** OpenTelemetry
- **Collection:** Jaeger / Tempo
- **Visualization:** Jaeger UI / Grafana
- **Retention:** 7 days

## Key Metrics to Monitor

### Application Metrics (RED)
- **Rate:** Requests per second
- **Errors:** Error rate/count
- **Duration:** Response time (p50, p95, p99)

### Infrastructure Metrics (USE)
- **Utilization:** % busy
- **Saturation:** Queue depth
- **Errors:** Error count

### Business Metrics
- Active users
- Transaction volume
- Revenue metrics

## Alert Strategy
- **Critical:** Page on-call (5 min SLA)
- **Warning:** Slack notification (15 min SLA)
- **Info:** Dashboard only

## Monitoring Tools Comparison

| Feature | Prometheus+Grafana | DataDog | New Relic | CloudWatch |
|---------|-------------------|---------|-----------|------------|
| Cost | Free (self-hosted) | $$$$ | $$$$ | $$ |
| Setup | Moderate | Easy | Easy | Easy |
| Flexibility | High | Medium | Medium | Low |
| Cloud-native | ✅ | ✅ | ✅ | AWS only |
| Custom metrics | ✅ | ✅ | ✅ | ✅ |
| APM | Addon | ✅ | ✅ | ✅ |
EOF
```

**Decision Matrix:**
```bash
# For open-source, self-hosted (recommended)
METRICS: Prometheus + Grafana
LOGS: Loki or ELK Stack
TRACES: Jaeger or Tempo
ALERTS: Alertmanager

# For managed cloud services
ALL-IN-ONE: DataDog, New Relic, Dynatrace
```

**Verification:**
- [ ] Monitoring tools selected
- [ ] Architecture documented
- [ ] Three pillars defined
- [ ] Alert strategy designed
- [ ] Budget approved

**If This Fails:**
→ Start with basics (metrics only)
→ Use managed service to get started quickly
→ Scale monitoring infrastructure later
→ Prioritize application metrics over infrastructure

---

### Step 2: Deploy Prometheus and Grafana (Metrics)

**What:** Set up Prometheus for metrics collection and Grafana for visualization

**How:**
Deploy using Kubernetes operators or Docker Compose for a production-ready setup.

**Code/Commands:**

**Kubernetes Deployment (Recommended):**
```bash
# Install Prometheus Operator using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Create monitoring namespace
kubectl create namespace monitoring

# Install kube-prometheus-stack (includes Prometheus, Grafana, Alertmanager)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
  --set grafana.adminPassword=changeme \
  --set alertmanager.enabled=true

# Verify deployment
kubectl get pods -n monitoring
kubectl get svc -n monitoring

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Open http://localhost:3000 (admin/changeme)

# Access Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Open http://localhost:9090
```

**Docker Compose Alternative:**
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=changeme
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - monitoring
  
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager-data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:
  alertmanager-data:

networks:
  monitoring:
    driver: bridge
```

**Prometheus Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    environment: 'prod'

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Load rules
rule_files:
  - "alerts/*.yml"

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  # Application metrics
  - job_name: 'myapp'
    static_configs:
      - targets: ['myapp:8080']
    metrics_path: /metrics
    scrape_interval: 10s
  
  # Kubernetes pods (if using K8s)
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

**Verification:**
- [ ] Prometheus running and accessible
- [ ] Grafana running and accessible
- [ ] Prometheus discovering targets
- [ ] Metrics being scraped
- [ ] No errors in Prometheus targets page

**If This Fails:**
→ Check pod/container logs
→ Verify network connectivity
→ Check Prometheus targets page for errors
→ Ensure metrics endpoint accessible

---

### Step 3: Instrument Application for Metrics

**What:** Add metrics collection to your application code

**How:**
Use Prometheus client libraries to expose metrics endpoints.

**Code/Commands:**

**Node.js/Express:**
```javascript
// metrics.js - Prometheus metrics for Node.js
const promClient = require('prom-client');

// Create Registry
const register = new promClient.Registry();

// Default metrics (CPU, memory, etc.)
promClient.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new promClient.Gauge({
  name: 'active_connections',
  help: 'Number of active connections'
});

// Register metrics
register.registerMetric(httpRequestDuration);
register.registerMetric(httpRequestsTotal);
register.registerMetric(activeConnections);

// Middleware to collect metrics
function metricsMiddleware(req, res, next) {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route ? req.route.path : req.path;
    
    httpRequestDuration
      .labels(req.method, route, res.statusCode)
      .observe(duration);
    
    httpRequestsTotal
      .labels(req.method, route, res.statusCode)
      .inc();
  });
  
  next();
}

// Metrics endpoint
function metricsEndpoint(req, res) {
  res.set('Content-Type', register.contentType);
  register.metrics().then(data => res.send(data));
}

module.exports = {
  metricsMiddleware,
  metricsEndpoint,
  activeConnections,
  register
};
```

```javascript
// app.js - Use metrics
const express = require('express');
const { metricsMiddleware, metricsEndpoint, activeConnections } = require('./metrics');

const app = express();

// Apply metrics middleware
app.use(metricsMiddleware);

// Expose metrics endpoint
app.get('/metrics', metricsEndpoint);

// Track active connections
let connections = 0;
app.use((req, res, next) => {
  connections++;
  activeConnections.set(connections);
  res.on('finish', () => {
    connections--;
    activeConnections.set(connections);
  });
  next();
});

// Your routes
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

**Python/Flask:**
```python
# metrics.py - Prometheus metrics for Python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from flask import Response
import time

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

# Middleware
def setup_metrics(app):
    @app.before_request
    def before_request():
        request.start_time = time.time()
        active_requests.inc()
    
    @app.after_request
    def after_request(response):
        request_duration.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown'
        ).observe(time.time() - request.start_time)
        
        request_count.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()
        
        active_requests.dec()
        return response
    
    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(REGISTRY), mimetype='text/plain')
```

**Go:**
```go
// metrics.go - Prometheus metrics for Go
package main

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "net/http"
)

var (
    httpDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "Duration of HTTP requests",
            Buckets: []float64{.1, .3, .5, .7, 1, 3, 5, 7, 10},
        },
        []string{"method", "path", "status"},
    )
    
    httpRequests = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "path", "status"},
    )
)

func init() {
    prometheus.MustRegister(httpDuration)
    prometheus.MustRegister(httpRequests)
}

func metricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        timer := prometheus.NewTimer(prometheus.ObserverFunc(func(v float64) {
            httpDuration.WithLabelValues(r.Method, r.URL.Path, "200").Observe(v)
        }))
        defer timer.ObserveDuration()
        
        next.ServeHTTP(w, r)
        
        httpRequests.WithLabelValues(r.Method, r.URL.Path, "200").Inc()
    })
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.Handle("/", metricsMiddleware(http.HandlerFunc(handler)))
    http.ListenAndServe(":8080", nil)
}
```

**Verification:**
- [ ] Metrics endpoint accessible (/metrics)
- [ ] Metrics in Prometheus format
- [ ] Application metrics appearing in Prometheus
- [ ] No performance impact
- [ ] Custom metrics working

**If This Fails:**
→ Check application logs
→ Verify Prometheus client library installed
→ Test metrics endpoint manually: `curl localhost:8080/metrics`
→ Check Prometheus targets page

---

### Step 4: Create Grafana Dashboards

**What:** Build visualizations for metrics using Grafana

**How:**
Create dashboards showing key metrics, trends, and system health.

**Code/Commands:**

```bash
# Configure Grafana datasource
cat > grafana/provisioning/datasources/prometheus.yml <<'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF

# Create dashboard JSON (example - Application Overview)
cat > grafana/provisioning/dashboards/app-overview.json <<'EOF'
{
  "dashboard": {
    "title": "Application Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
EOF

# Import community dashboards
# Node Exporter Dashboard: 1860
# Kubernetes Dashboard: 315
# Docker Dashboard: 893
```

**Essential Dashboards to Create:**

1. **Application Overview**
   - Request rate (requests/sec)
   - Error rate (%)
   - Response time (p50, p95, p99)
   - Active connections

2. **Infrastructure**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

3. **Business Metrics**
   - User signups
   - Transactions/revenue
   - Active users
   - Feature usage

4. **SLO Dashboard**
   - Availability (%)
   - Error budget remaining
   - Latency targets
   - Success rate

**Quick Dashboard Creation:**
```bash
# Using Grafana API to create dashboard
curl -X POST http://admin:changeme@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboard.json
```

**Verification:**
- [ ] Grafana accessible
- [ ] Prometheus datasource configured
- [ ] Dashboards created
- [ ] Metrics visualized correctly
- [ ] Dashboards auto-refresh

**If This Fails:**
→ Check Grafana datasource configuration
→ Verify Prometheus query syntax
→ Import community dashboards first
→ Test queries in Prometheus UI

---

### Step 5: Configure Alerting Rules

**What:** Set up alerts for critical conditions

**How:**
Define alert rules in Prometheus and route notifications through Alertmanager.

**Code/Commands:**

**Alert Rules:**
```yaml
# alerts/application.yml
groups:
  - name: application_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for {{ $labels.instance }}"
      
      # High response time
      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "High response time"
          description: "P95 latency is {{ $value }}s for {{ $labels.instance }}"
      
      # Application down
      - alert: ApplicationDown
        expr: up{job="myapp"} == 0
        for: 1m
        labels:
          severity: critical
          team: ops
        annotations:
          summary: "Application is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"
      
      # High memory usage
      - alert: HighMemoryUsage
        expr: |
          (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
          team: ops
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"
      
      # Disk space low
      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"} / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: warning
          team: ops
        annotations:
          summary: "Disk space low"
          description: "Only {{ $value | humanizePercentage }} disk space remaining on {{ $labels.instance }}"
```

**Alertmanager Configuration:**
```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

# Templates
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Route tree
route:
  receiver: 'default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  
  routes:
    # Critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true
    
    # Warning alerts to Slack
    - match:
        severity: warning
      receiver: 'slack'
    
    # Team-specific routing
    - match:
        team: backend
      receiver: 'backend-team'
    
    - match:
        team: ops
      receiver: 'ops-team'

# Receivers
receivers:
  - name: 'default'
    slack_configs:
      - channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
        description: '{{ .GroupLabels.alertname }}: {{ .Alerts.Firing | len }} firing'
  
  - name: 'slack'
    slack_configs:
      - channel: '#alerts-warning'
        title: 'Warning: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        color: 'warning'
  
  - name: 'backend-team'
    slack_configs:
      - channel: '#team-backend'
    email_configs:
      - to: 'backend-team@example.com'
  
  - name: 'ops-team'
    slack_configs:
      - channel: '#team-ops'
    email_configs:
      - to: 'ops-team@example.com'

# Inhibition rules
inhibit_rules:
  # If application is down, don't alert on high error rate
  - source_match:
      alertname: 'ApplicationDown'
    target_match:
      alertname: 'HighErrorRate'
    equal: ['instance']
```

**Test Alerts:**
```bash
# Trigger test alert
curl -X POST http://localhost:9093/api/v1/alerts -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "summary": "This is a test alert"
    }
  }
]'

# Check Alertmanager status
curl http://localhost:9093/api/v1/status

# View active alerts
curl http://localhost:9093/api/v1/alerts
```

**Verification:**
- [ ] Alert rules loaded in Prometheus
- [ ] Alertmanager receiving alerts
- [ ] Notifications delivered to channels
- [ ] Alert routing working correctly
- [ ] Test alerts successful

**If This Fails:**
→ Check alert rule syntax in Prometheus
→ Verify Alertmanager configuration
→ Test webhook URLs independently
→ Check alert firing conditions

---

### Step 6: Implement Log Aggregation (Optional but Recommended)

**What:** Centralize logs from all services for analysis

**How:**
Deploy Loki or ELK stack to collect and search logs.

**Code/Commands:**

**Loki + Promtail (Lightweight Option):**
```yaml
# loki-stack.yml - Add to docker-compose
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - monitoring

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - monitoring
```

**Loki Configuration:**
```yaml
# loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

**Application Logging Best Practices:**
```javascript
// Structured logging (Node.js with Winston)
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'myapp' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console()
  ]
});

// Log with context
logger.info('User logged in', {
  userId: '123',
  ip: req.ip,
  userAgent: req.get('user-agent')
});

// Log errors with stack trace
logger.error('Database connection failed', {
  error: err.message,
  stack: err.stack,
  query: sql
});
```

**Verification:**
- [ ] Logs flowing to Loki/ELK
- [ ] Logs searchable in Grafana/Kibana
- [ ] Log retention configured
- [ ] Structured logging in place
- [ ] Error logs easily findable

**If This Fails:**
→ Check log shipper configuration
→ Verify log format is parseable
→ Test log query syntax
→ Check storage capacity

---

### Step 7: Set Up Uptime Monitoring and Synthetic Tests

**What:** Monitor application availability from external perspective

**How:**
Configure uptime checks and synthetic transactions.

**Code/Commands:**

**Blackbox Exporter (Prometheus):**
```yaml
# blackbox.yml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200]
      method: GET
      preferred_ip_protocol: "ip4"
  
  http_post_2xx:
    prober: http
    http:
      method: POST
      headers:
        Content-Type: application/json
      body: '{"test": true}'
  
  tcp_connect:
    prober: tcp
    timeout: 5s
  
  dns_query:
    prober: dns
    dns:
      query_name: "example.com"
      query_type: "A"
```

```yaml
# Add to prometheus.yml
scrape_configs:
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - https://example.com/health
          - https://example.com/api/status
          - https://api.example.com/v1/health
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

**External Monitoring Services:**
```bash
# UptimeRobot API
curl -X POST https://api.uptimerobot.com/v2/newMonitor \
  -d "api_key=YOUR_API_KEY" \
  -d "friendly_name=My App" \
  -d "url=https://example.com" \
  -d "type=1" \
  -d "interval=300"

# Or use managed services:
# - UptimeRobot (free tier available)
# - Pingdom
# - StatusCake
# - Better Uptime
```

**Verification:**
- [ ] Uptime checks running
- [ ] Alerts for downtime configured
- [ ] Response time tracked
- [ ] SSL certificate expiry monitored
- [ ] Multi-region checks (if applicable)

**If This Fails:**
→ Check external firewall rules
→ Verify endpoint accessibility
→ Test checks manually with curl
→ Review alert thresholds

---

### Step 8: Document Monitoring and Create Runbooks

**What:** Create comprehensive monitoring documentation and response procedures

**How:**
Document all monitoring components, alert meanings, and response procedures.

**Code/Commands:**

```bash
# Create monitoring documentation
cat > docs/MONITORING.md <<'EOF'
# Monitoring Documentation

## Quick Links
- **Grafana:** https://grafana.example.com
- **Prometheus:** https://prometheus.example.com
- **Alertmanager:** https://alertmanager.example.com
- **On-Call:** https://pagerduty.example.com

## Dashboards

### Application Overview
**URL:** https://grafana.example.com/d/app-overview
**Purpose:** High-level application health
**Metrics:**
- Request rate (target: > 100 req/s)
- Error rate (target: < 1%)
- P95 latency (target: < 500ms)
- Active users

### Infrastructure
**URL:** https://grafana.example.com/d/infrastructure
**Purpose:** Server and container health
**Metrics:**
- CPU usage (alert: > 80%)
- Memory usage (alert: > 85%)
- Disk usage (alert: > 90%)
- Network throughput

## Alerts

### Critical Alerts (Page)
| Alert | Meaning | Response Time | Runbook |
|-------|---------|---------------|---------|
| ApplicationDown | App not responding | 5 min | [runbooks/app-down.md](./runbooks/app-down.md) |
| HighErrorRate | 5xx errors > 5% | 5 min | [runbooks/high-errors.md](./runbooks/high-errors.md) |
| DatabaseDown | DB connection lost | 5 min | [runbooks/db-down.md](./runbooks/db-down.md) |

### Warning Alerts (Slack)
| Alert | Meaning | Response Time | Runbook |
|-------|---------|---------------|---------|
| HighResponseTime | P95 > 1s | 15 min | [runbooks/slow-response.md](./runbooks/slow-response.md) |
| HighMemoryUsage | Memory > 90% | 30 min | [runbooks/high-memory.md](./runbooks/high-memory.md) |
| DiskSpaceLow | Disk < 10% free | 1 hour | [runbooks/disk-space.md](./runbooks/disk-space.md) |

## SLOs (Service Level Objectives)

### Availability
- **Target:** 99.9% uptime (43 min downtime/month)
- **Measurement:** Uptime checks every 1 min
- **Error Budget:** 0.1% (43 min/month)

### Latency
- **Target:** 95% of requests < 500ms
- **Measurement:** P95 response time
- **Alert:** P95 > 1s for 10 min

### Error Rate
- **Target:** < 0.1% error rate
- **Measurement:** 5xx errors / total requests
- **Alert:** Error rate > 1% for 5 min

## On-Call

### Escalation Path
1. **Primary On-Call** → PagerDuty (auto-escalate: 5 min)
2. **Secondary On-Call** → PagerDuty (auto-escalate: 5 min)
3. **Engineering Manager** → Phone call

### On-Call Responsibilities
- Respond to pages within 5 minutes
- Acknowledge incident in PagerDuty
- Follow runbook procedures
- Escalate if cannot resolve in 15 minutes
- Document incident in postmortem

### After Hours
- Critical alerts only (ApplicationDown, DatabaseDown)
- All other alerts defer to next business day
- Emergency contact: +1-555-0100

## Troubleshooting

### Common Issues

**High CPU**
1. Check Grafana CPU dashboard
2. Identify top consumers: `kubectl top pods`
3. Check for infinite loops in recent deploys
4. Scale horizontally if traffic spike

**High Memory**
1. Check for memory leaks in recent deployments
2. Review application logs for OOM errors
3. Analyze heap dumps if available
4. Consider increasing memory limits

**Slow Responses**
1. Check database query performance
2. Look for N+1 query problems
3. Review external API latencies
4. Check cache hit rates

## Maintenance

### Regular Tasks
- **Daily:** Review dashboards for anomalies
- **Weekly:** Check error budget consumption
- **Monthly:** Review and tune alert thresholds
- **Quarterly:** Update runbooks, test disaster recovery

### Monitoring Health Checks
- Prometheus retention: 30 days
- Grafana datasource: Connected
- Alertmanager: Routing correctly
- Log retention: 90 days
EOF

# Create example runbook
cat > docs/runbooks/app-down.md <<'EOF'
# Runbook: Application Down

## Alert Details
- **Severity:** Critical
- **Response Time:** 5 minutes
- **Auto-resolves:** Yes (when service recovers)

## Symptoms
- Health check endpoint returning errors
- Application pods/containers not running
- Users unable to access application

## Initial Response (First 5 minutes)

1. **Acknowledge alert** in PagerDuty
2. **Check application status:**
   ```bash
   kubectl get pods -n production
   kubectl describe pod <pod-name> -n production
   ```

3. **Check recent deployments:**
   ```bash
   kubectl rollout history deployment/myapp -n production
   ```

4. **Quick fixes to try:**
   - Restart pod: `kubectl delete pod <pod-name> -n production`
   - Rollback deployment: `kubectl rollout undo deployment/myapp -n production`

## Investigation (5-15 minutes)

1. **Check logs:**
   ```bash
   kubectl logs <pod-name> -n production --tail=100
   ```

2. **Check resource usage:**
   ```bash
   kubectl top pods -n production
   ```

3. **Check database connectivity:**
   ```bash
   kubectl exec <pod-name> -n production -- nc -zv database 5432
   ```

4. **Check external dependencies:**
   - API status pages
   - Third-party service status

## Resolution Steps

### If deployment issue:
1. Rollback to last known good version
2. Investigate what changed
3. Fix and redeploy

### If resource issue:
1. Scale up replicas temporarily
2. Investigate resource leak
3. Optimize or increase limits

### If dependency issue:
1. Check dependency health
2. Enable fallback/degraded mode
3. Contact dependency owner

## Escalation

Escalate if:
- Cannot restore service in 15 minutes
- Root cause unclear
- Requires infrastructure changes

Contact:
- Engineering Manager: +1-555-0101
- Platform Team: #platform-oncall

## Postmortem

After resolution:
1. Document incident timeline
2. Identify root cause
3. Create action items to prevent recurrence
4. Schedule postmortem meeting
EOF
```

**Verification:**
- [ ] All dashboards documented
- [ ] Alert runbooks created
- [ ] SLOs defined
- [ ] On-call procedures clear
- [ ] Troubleshooting guides complete

**If This Fails:**
→ Start with critical alerts only
→ Add documentation iteratively
→ Get team feedback
→ Update based on real incidents

---

## Verification Checklist

- [ ] Monitoring stack deployed (Prometheus, Grafana, Alertmanager)
- [ ] Application instrumented with metrics
- [ ] Key dashboards created
- [ ] Alert rules configured
- [ ] Notifications working (Slack, email, PagerDuty)
- [ ] Log aggregation set up (if applicable)
- [ ] Uptime monitoring configured
- [ ] Documentation complete
- [ ] Runbooks created
- [ ] Team trained on monitoring tools

---

## Common Issues & Solutions

### Issue: High Cardinality Metrics

**Symptoms:**
- Prometheus consuming too much memory
- Slow query performance
- "Too many time series" errors

**Solution:**
```bash
# Identify high cardinality metrics
curl -s http://localhost:9090/api/v1/label/__name__/values | jq '.data[]' | \
  while read metric; do
    count=$(curl -s "http://localhost:9090/api/v1/series?match[]=$metric" | jq '.data | length')
    echo "$count $metric"
  done | sort -rn | head -20

# Reduce cardinality:
# 1. Remove unnecessary labels
# 2. Aggregate labels (e.g., use /api/* instead of /api/users/123)
# 3. Increase scrape interval
# 4. Set retention limits
```

**Prevention:**
- Limit label cardinality
- Don't use user IDs as labels
- Use recording rules for expensive queries

---

### Issue: Alert Fatigue

**Symptoms:**
- Too many non-actionable alerts
- Team ignoring alerts
- Important alerts missed

**Solution:**
```yaml
# Tune alert thresholds
- alert: HighErrorRate
  expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05  # Was 0.01
  for: 10m  # Was 5m - wait longer before alerting

# Group related alerts
route:
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m

# Implement alert inhibition
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
```

**Prevention:**
- Review alerts weekly
- Remove non-actionable alerts
- Implement SLO-based alerting
- Use severity levels appropriately

---

## Best Practices

### DO:
✅ **Monitor the four golden signals** - Latency, traffic, errors, saturation  
✅ **Use RED metrics** - Rate, Errors, Duration  
✅ **Set up SLOs** - Define acceptable service levels  
✅ **Create actionable alerts** - Every alert needs runbook  
✅ **Instrument early** - Add metrics from day one  
✅ **Use structured logging** - Easy parsing and searching  
✅ **Monitor dependencies** - External services affect your SLOs  
✅ **Test alerts** - Verify notification delivery  
✅ **Document everything** - Dashboards, alerts, runbooks  
✅ **Review metrics regularly** - Tune and optimize

### DON'T:
❌ **Alert on everything** - Causes alert fatigue  
❌ **Monitor without alerting** - Monitoring must be actionable  
❌ **Skip runbooks** - Alerts without runbooks are useless  
❌ **Ignore high cardinality** - Kills Prometheus performance  
❌ **Use default dashboards only** - Customize for your needs  
❌ **Forget to monitor monitoring** - Who watches the watchers?  
❌ **Neglect log retention** - Balance cost and usefulness  
❌ **Skip documentation** - Team can't use what they don't understand  
❌ **Over-complicate** - Start simple, add complexity as needed  
❌ **Ignore cost** - Monitoring infrastructure costs money

---

## Related Workflows

**Prerequisites:**
- [Docker Container Creation](./docker_container_creation.md) - Containerized applications
- [Kubernetes Deployment](./kubernetes_deployment.md) - K8s deployments to monitor
- [CI/CD Pipeline Setup](./cicd_pipeline_setup.md) - Automated deployments

**Next Steps:**
- [Log Aggregation ELK](./log_aggregation_elk.md) - Detailed log management
- [Incident Response Workflow](./incident_response_workflow.md) - Handle alerts
- [Performance Tuning](./performance_tuning.md) - Optimize based on metrics

**Alternatives:**
- DataDog - All-in-one managed monitoring
- New Relic - APM and monitoring
- Dynatrace - Enterprise monitoring
- CloudWatch - AWS-native monitoring

---

## Tags
`devops` `monitoring` `observability` `prometheus` `grafana` `alerting` `metrics` `logging` `apm` `sre` `incident-response`
