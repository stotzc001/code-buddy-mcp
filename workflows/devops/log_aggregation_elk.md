# Log Aggregation with ELK Stack

**ID:** devops-011  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Intermediate-Advanced  
**Estimated Time:** 3-4 hours  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for setting up centralized log aggregation, search, and analysis using the ELK Stack (Elasticsearch, Logstash, Kibana) or alternatives like Loki

**Why:** Centralized logging enables fast troubleshooting, security analysis, compliance auditing, and insight into application behavior. Distributed systems generate logs across multiple services and instances - without aggregation, debugging becomes impossible at scale.

**When to use:**
- Running microservices or distributed systems
- Multiple application instances or containers
- Need to correlate logs across services
- Compliance or audit requirements
- Debugging production issues
- Security monitoring and analysis
- Performance analysis

---

## Prerequisites

**Required:**
- [ ] Applications generating logs
- [ ] Infrastructure access (Kubernetes, VMs, or Docker)
- [ ] Storage capacity for log retention (estimate: 50-500GB/day)
- [ ] Understanding of log formats and structure
- [ ] Elasticsearch cluster or managed service

**Check before starting:**
```bash
# Check application logs
docker logs <container-name>
# or
kubectl logs <pod-name>

# Verify disk space for log storage
df -h

# Check if logs are being written
tail -f /var/log/application.log

# Estimate log volume
du -sh /var/log/
find /var/log -type f -exec ls -lh {} \; | awk '{sum+=$5} END {print sum}'
```

---

## Implementation Steps

### Step 1: Design Log Architecture

**What:** Plan log collection, storage, retention, and access patterns

**How:**
Define what logs to collect, how long to store them, and who needs access.

**Code/Commands:**
```bash
# Document log architecture
cat > LOG_ARCHITECTURE.md <<'EOF'
# Log Aggregation Architecture

## Log Sources
1. **Application Logs**
   - Web servers (Nginx, Apache)
   - Application services (Node.js, Python, Go)
   - Background workers
   - Batch jobs

2. **System Logs**
   - Syslog
   - Auth logs
   - Kernel logs
   - Docker/containerd logs

3. **Infrastructure Logs**
   - Kubernetes events
   - Load balancer logs
   - Database logs
   - Cache logs (Redis, Memcached)

## Log Levels
- **ERROR:** Application errors, exceptions
- **WARN:** Potential issues, deprecated features
- **INFO:** General informational messages
- **DEBUG:** Detailed debugging information

## Retention Policy
| Log Type | Retention | Storage | Reason |
|----------|-----------|---------|--------|
| Application ERROR | 90 days | Hot | Debugging |
| Application INFO | 30 days | Hot | Recent analysis |
| Application DEBUG | 7 days | Hot | Active debugging |
| Access Logs | 90 days | Warm | Analytics |
| Security Logs | 365 days | Warm/Cold | Compliance |
| Audit Logs | 2555 days (7 years) | Cold | Legal |

## Storage Tiers
- **Hot:** Elasticsearch (fast search, expensive)
- **Warm:** Elasticsearch with slower hardware
- **Cold:** S3/object storage (archive, cheap)

## Access Control
- **Developers:** Read application logs
- **DevOps:** Read all logs
- **Security Team:** Read security/audit logs
- **Compliance:** Read audit logs only

## Stack Selection

### Option 1: ELK Stack (Elasticsearch, Logstash, Kibana)
**Pros:** Powerful search, rich ecosystem, mature
**Cons:** Resource-intensive, complex to operate
**Best for:** Large scale, complex queries, rich visualizations

### Option 2: Loki + Grafana
**Pros:** Lightweight, integrates with Grafana, cost-effective
**Cons:** Limited search capabilities, newer project
**Best for:** Kubernetes, cost-conscious, Grafana users

### Option 3: Managed Services
- **AWS:** CloudWatch Logs, OpenSearch Service
- **GCP:** Cloud Logging
- **Azure:** Azure Monitor
**Pros:** No ops overhead, automatic scaling
**Cons:** Vendor lock-in, can be expensive at scale

## Estimated Resources (ELK)
- **Elasticsearch:** 3 nodes, 16GB RAM each, 500GB SSD
- **Logstash:** 2 nodes, 8GB RAM each
- **Kibana:** 1 node, 4GB RAM
- **Daily ingestion:** ~100GB compressed
- **Monthly storage:** ~3TB (with 30-day retention)
EOF
```

**Verification:**
- [ ] Log sources identified
- [ ] Retention policy defined
- [ ] Storage estimated
- [ ] Stack selected
- [ ] Access control planned

**If This Fails:**
→ Start with application logs only
→ Use managed service to reduce complexity
→ Implement retention policy gradually
→ Scale infrastructure as needed

---

### Step 2: Deploy ELK Stack

**What:** Install and configure Elasticsearch, Logstash, and Kibana

**How:**
Deploy using Docker Compose or Kubernetes with proper configuration.

**Code/Commands:**

**Docker Compose Deployment:**
```yaml
# docker-compose.elk.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - node.name=es01
      - cluster.name=docker-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms4g -Xmx4g"
      - xpack.security.enabled=false
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
      - "9300:9300"
    networks:
      - elk
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: logstash
    volumes:
      - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"  # Beats input
      - "5000:5000/tcp"  # TCP input
      - "5000:5000/udp"  # UDP input
      - "9600:9600"  # Monitoring API
    environment:
      - "LS_JAVA_OPTS=-Xmx2g -Xms2g"
    networks:
      - elk
    depends_on:
      elasticsearch:
        condition: service_healthy

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=changeme
    networks:
      - elk
    depends_on:
      elasticsearch:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5601/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: filebeat
    user: root
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - filebeat-data:/usr/share/filebeat/data
    command: filebeat -e -strict.perms=false
    networks:
      - elk
    depends_on:
      - elasticsearch
      - logstash

volumes:
  elasticsearch-data:
  filebeat-data:

networks:
  elk:
    driver: bridge
```

**Logstash Configuration:**
```yaml
# logstash/config/logstash.yml
http.host: "0.0.0.0"
xpack.monitoring.elasticsearch.hosts: ["http://elasticsearch:9200"]
```

```ruby
# logstash/pipeline/logstash.conf
input {
  beats {
    port => 5044
  }
  
  tcp {
    port => 5000
    codec => json
  }
  
  http {
    port => 8080
  }
}

filter {
  # Parse JSON logs
  if [message] =~ /^{.*}$/ {
    json {
      source => "message"
    }
  }
  
  # Parse application logs
  grok {
    match => { 
      "message" => "%{TIMESTAMP_ISO8601:timestamp} \[%{LOGLEVEL:log_level}\] %{GREEDYDATA:log_message}"
    }
  }
  
  # Add metadata
  mutate {
    add_field => {
      "[@metadata][target_index]" => "logs-%{+YYYY.MM.dd}"
    }
  }
  
  # Parse timestamps
  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
  }
  
  # Remove unnecessary fields
  mutate {
    remove_field => ["agent", "ecs", "host"]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][target_index]}"
    document_type => "_doc"
  }
  
  # Debugging output
  stdout {
    codec => rubydebug
  }
}
```

**Kubernetes Deployment (Elastic Cloud on Kubernetes):**
```bash
# Install ECK operator
kubectl create -f https://download.elastic.co/downloads/eck/2.10.0/crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck/2.10.0/operator.yaml

# Verify operator
kubectl -n elastic-system logs -f statefulset.apps/elastic-operator

# Deploy Elasticsearch cluster
cat <<EOF | kubectl apply -f -
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: quickstart
  namespace: logging
spec:
  version: 8.11.0
  nodeSets:
  - name: default
    count: 3
    config:
      node.store.allow_mmap: false
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 100Gi
        storageClassName: fast-ssd
EOF

# Deploy Kibana
cat <<EOF | kubectl apply -f -
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: quickstart
  namespace: logging
spec:
  version: 8.11.0
  count: 1
  elasticsearchRef:
    name: quickstart
EOF

# Get Kibana password
kubectl get secret quickstart-es-elastic-user -n logging \
  -o go-template='{{.data.elastic | base64decode}}'
```

**Start ELK Stack:**
```bash
# Docker Compose
docker-compose -f docker-compose.elk.yml up -d

# Check status
docker-compose -f docker-compose.elk.yml ps

# View logs
docker-compose -f docker-compose.elk.yml logs -f

# Access UIs
# Elasticsearch: http://localhost:9200
# Kibana: http://localhost:5601
# Logstash: http://localhost:9600/_node/stats
```

**Verification:**
- [ ] Elasticsearch cluster healthy
- [ ] Kibana accessible
- [ ] Logstash accepting inputs
- [ ] No errors in logs
- [ ] Elasticsearch indices created

**If This Fails:**
→ Check container logs
→ Verify resource availability (memory, disk)
→ Ensure ports not in use
→ Review Elasticsearch cluster health

---

### Step 3: Configure Log Shippers (Filebeat)

**What:** Set up log collection agents on application servers

**How:**
Deploy Filebeat to collect and forward logs to Logstash or Elasticsearch.

**Code/Commands:**

**Filebeat Configuration:**
```yaml
# filebeat/filebeat.yml
filebeat.inputs:
  # Collect application logs
  - type: log
    enabled: true
    paths:
      - /var/log/application/*.log
      - /var/log/app/*.log
    fields:
      app: myapp
      env: production
    fields_under_root: true
    multiline:
      pattern: '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
      negate: true
      match: after
  
  # Collect Docker container logs
  - type: container
    enabled: true
    paths:
      - /var/lib/docker/containers/*/*.log
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"
      - decode_json_fields:
          fields: ["message"]
          target: ""
          overwrite_keys: true
  
  # Collect Kubernetes logs
  - type: kubernetes
    enabled: true
    hints.enabled: true
    hints.default_config:
      type: container
      paths:
        - /var/log/containers/*${data.kubernetes.container.id}.log

# Processors
processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~

# Output to Logstash
output.logstash:
  hosts: ["logstash:5044"]
  loadbalance: true
  worker: 2

# OR output directly to Elasticsearch
# output.elasticsearch:
#   hosts: ["elasticsearch:9200"]
#   protocol: "http"
#   username: "elastic"
#   password: "changeme"
#   indices:
#     - index: "logs-app-%{+yyyy.MM.dd}"
#       when.equals:
#         fields.app: "myapp"

# Logging
logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644

# Monitoring
monitoring.enabled: true
monitoring.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

**Install Filebeat on Servers:**
```bash
# Ubuntu/Debian
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.11.0-amd64.deb
sudo dpkg -i filebeat-8.11.0-amd64.deb

# Enable modules
sudo filebeat modules enable system nginx mysql

# Configure
sudo vi /etc/filebeat/filebeat.yml

# Test configuration
sudo filebeat test config
sudo filebeat test output

# Start Filebeat
sudo systemctl enable filebeat
sudo systemctl start filebeat
sudo systemctl status filebeat
```

**Kubernetes DaemonSet:**
```yaml
# filebeat-kubernetes.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: logging
data:
  filebeat.yml: |-
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*.log
      processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
          - logs_path:
              logs_path: "/var/log/containers/"
    
    output.elasticsearch:
      hosts: ['${ELASTICSEARCH_HOST:elasticsearch}:${ELASTICSEARCH_PORT:9200}']
      username: ${ELASTICSEARCH_USERNAME}
      password: ${ELASTICSEARCH_PASSWORD}
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  namespace: logging
spec:
  selector:
    matchLabels:
      app: filebeat
  template:
    metadata:
      labels:
        app: filebeat
    spec:
      serviceAccountName: filebeat
      terminationGracePeriodSeconds: 30
      containers:
      - name: filebeat
        image: docker.elastic.co/beats/filebeat:8.11.0
        args: [
          "-c", "/etc/filebeat.yml",
          "-e",
        ]
        env:
        - name: ELASTICSEARCH_HOST
          value: elasticsearch
        - name: ELASTICSEARCH_PORT
          value: "9200"
        - name: ELASTICSEARCH_USERNAME
          value: elastic
        - name: ELASTICSEARCH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: elasticsearch-credentials
              key: password
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        securityContext:
          runAsUser: 0
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 100Mi
        volumeMounts:
        - name: config
          mountPath: /etc/filebeat.yml
          readOnly: true
          subPath: filebeat.yml
        - name: data
          mountPath: /usr/share/filebeat/data
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: varlog
          mountPath: /var/log
          readOnly: true
      volumes:
      - name: config
        configMap:
          defaultMode: 0640
          name: filebeat-config
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: varlog
        hostPath:
          path: /var/log
      - name: data
        hostPath:
          path: /var/lib/filebeat-data
          type: DirectoryOrCreate
```

**Verification:**
- [ ] Filebeat running on all nodes
- [ ] Logs being shipped to Logstash/Elasticsearch
- [ ] No errors in Filebeat logs
- [ ] Elasticsearch indices receiving data
- [ ] Kubernetes metadata enriched

**If This Fails:**
→ Check Filebeat logs: `journalctl -u filebeat -f`
→ Test output connectivity
→ Verify file permissions
→ Check Elasticsearch cluster health

---

### Step 4: Structure Logs for Optimal Searching

**What:** Implement structured logging in applications

**How:**
Use JSON logging and consistent field names across services.

**Code/Commands:**

**Node.js (Winston):**
```javascript
// logger.js
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { 
    service: 'myapp',
    environment: process.env.NODE_ENV,
    version: process.env.APP_VERSION
  },
  transports: [
    new winston.transports.File({ 
      filename: '/var/log/app/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: '/var/log/app/combined.log' 
    }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Usage examples
logger.info('User logged in', {
  userId: '12345',
  username: 'john.doe',
  ip: '192.168.1.1',
  userAgent: 'Mozilla/5.0...'
});

logger.error('Database connection failed', {
  error: err.message,
  stack: err.stack,
  connectionString: 'postgres://localhost:5432',
  retryAttempt: 3
});

logger.warn('High memory usage detected', {
  memoryUsed: '4.2GB',
  memoryTotal: '8GB',
  percentage: 52.5
});

module.exports = logger;
```

**Python (Structlog):**
```python
# logger.py
import structlog
import logging
import sys

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage examples
logger.info("user_logged_in",
    user_id="12345",
    username="john.doe",
    ip="192.168.1.1")

logger.error("database_connection_failed",
    error=str(err),
    connection_string="postgres://localhost:5432",
    retry_attempt=3)

logger.warning("high_memory_usage",
    memory_used_gb=4.2,
    memory_total_gb=8.0,
    percentage=52.5)
```

**Go (Zap):**
```go
// logger.go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func NewLogger() *zap.Logger {
    config := zap.NewProductionConfig()
    config.OutputPaths = []string{
        "stdout",
        "/var/log/app/application.log",
    }
    
    logger, _ := config.Build()
    return logger
}

// Usage
logger := NewLogger()
defer logger.Sync()

logger.Info("User logged in",
    zap.String("user_id", "12345"),
    zap.String("username", "john.doe"),
    zap.String("ip", "192.168.1.1"))

logger.Error("Database connection failed",
    zap.Error(err),
    zap.String("connection_string", "postgres://localhost:5432"),
    zap.Int("retry_attempt", 3))
```

**Standard Log Fields:**
```json
{
  "@timestamp": "2024-10-26T10:30:00.000Z",
  "level": "info",
  "service": "api-gateway",
  "environment": "production",
  "version": "1.2.3",
  "message": "HTTP request completed",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "user-123",
  "request": {
    "method": "GET",
    "path": "/api/users/123",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  },
  "response": {
    "status_code": 200,
    "duration_ms": 45
  },
  "host": "api-01",
  "container_id": "abc123def456"
}
```

**Verification:**
- [ ] Logs in JSON format
- [ ] Consistent field names
- [ ] Timestamp in ISO8601
- [ ] Service/environment identified
- [ ] Trace IDs for correlation

**If This Fails:**
→ Test log output format
→ Validate JSON structure
→ Check logger configuration
→ Review log parsing in Logstash

---

### Step 5: Create Index Patterns and Manage Retention

**What:** Configure Elasticsearch indices and lifecycle policies

**How:**
Set up index templates, patterns, and automated retention policies.

**Code/Commands:**

**Index Template:**
```bash
# Create index template
curl -X PUT "localhost:9200/_index_template/logs-template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "5s",
      "index.lifecycle.name": "logs-policy",
      "index.lifecycle.rollover_alias": "logs"
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "level": {
          "type": "keyword"
        },
        "service": {
          "type": "keyword"
        },
        "environment": {
          "type": "keyword"
        },
        "message": {
          "type": "text"
        },
        "trace_id": {
          "type": "keyword"
        },
        "user_id": {
          "type": "keyword"
        },
        "response.status_code": {
          "type": "integer"
        },
        "response.duration_ms": {
          "type": "float"
        }
      }
    }
  }
}'
```

**Index Lifecycle Management (ILM):**
```bash
# Create ILM policy
curl -X PUT "localhost:9200/_ilm/policy/logs-policy" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_primary_shard_size": "50GB",
            "max_age": "1d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "set_priority": {
            "priority": 50
          },
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "set_priority": {
            "priority": 0
          },
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'
```

**Index Management Script:**
```bash
cat > manage-indices.sh <<'EOF'
#!/bin/bash
set -euo pipefail

ES_HOST="${ES_HOST:-localhost:9200}"

# List all indices
echo "All indices:"
curl -s "$ES_HOST/_cat/indices?v"

# Get index sizes
echo -e "\nIndex sizes:"
curl -s "$ES_HOST/_cat/indices?v&h=index,store.size&s=store.size:desc"

# Delete indices older than 90 days
echo -e "\nDeleting old indices..."
curator_cli --host "$ES_HOST" delete_indices \
  --filter_list '[{"filtertype":"age","source":"name","direction":"older","timestring":"%Y.%m.%d","unit":"days","unit_count":90}]'

# Optimize indices
echo -e "\nForce merging old indices..."
curator_cli --host "$ES_HOST" forcemerge \
  --filter_list '[{"filtertype":"age","source":"name","direction":"older","timestring":"%Y.%m.%d","unit":"days","unit_count":7}]'

echo "Index management complete!"
EOF

chmod +x manage-indices.sh
```

**Verification:**
- [ ] Index templates created
- [ ] ILM policy applied
- [ ] Indices rolling over correctly
- [ ] Old indices being deleted
- [ ] Disk space managed

**If This Fails:**
→ Check ILM execution logs
→ Verify index naming matches template
→ Review disk space
→ Check ILM policy status

---

### Step 6: Build Kibana Dashboards and Visualizations

**What:** Create dashboards for log analysis and monitoring

**How:**
Use Kibana's Discover, Visualize, and Dashboard features.

**Code/Commands:**

**Create Index Pattern in Kibana:**
1. Navigate to Stack Management → Index Patterns
2. Create pattern: `logs-*`
3. Set time field: `@timestamp`
4. Save

**Essential Dashboards:**

```bash
# Export dashboard (save for version control)
curl -X POST "localhost:5601/api/kibana/dashboards/export" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{"dashboard": ["dashboard-id"]}'

# Import dashboard
curl -X POST "localhost:5601/api/kibana/dashboards/import" \
  -H 'kbn-xsrf: true' \
  --form file=@dashboard.ndjson
```

**Key Visualizations to Create:**

1. **Error Rate Over Time**
   - Visualization: Line chart
   - Query: `level:error`
   - Y-axis: Count
   - X-axis: @timestamp (every 5 minutes)

2. **Top Error Messages**
   - Visualization: Data table
   - Query: `level:error`
   - Aggregation: Terms on `message.keyword`
   - Size: 10

3. **Service Response Times**
   - Visualization: Area chart
   - Field: `response.duration_ms`
   - Aggregation: Average, P95, P99
   - Split by: `service.keyword`

4. **Log Volume by Service**
   - Visualization: Pie chart
   - Aggregation: Terms on `service.keyword`

5. **Failed Requests by Status Code**
   - Visualization: Bar chart
   - Query: `response.status_code >= 400`
   - Aggregation: Terms on `response.status_code`

**Saved Searches:**
```bash
# Create saved searches for common queries
# Application errors
level:error AND service:myapp

# Slow requests (> 1 second)
response.duration_ms > 1000

# 5xx errors
response.status_code >= 500

# Specific user activity
user_id:"user-123"

# Trace ID correlation
trace_id:"abc-123-def"
```

**Verification:**
- [ ] Index pattern created
- [ ] Dashboards functional
- [ ] Visualizations accurate
- [ ] Saved searches useful
- [ ] Team can access dashboards

**If This Fails:**
→ Check index pattern matches data
→ Verify time range selection
→ Review field mappings
→ Test queries in Discover first

---

### Step 7: Set Up Alerts and Notifications

**What:** Configure alerts for critical log patterns

**How:**
Use Elastalert or Kibana Alerting for log-based alerts.

**Code/Commands:**

**Kibana Alerting:**
```bash
# Create alert rule via API
curl -X POST "localhost:5601/api/alerting/rule" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "High Error Rate Alert",
  "tags": ["production", "errors"],
  "rule_type_id": ".index-threshold",
  "consumer": "alerts",
  "schedule": {
    "interval": "5m"
  },
  "actions": [
    {
      "group": "threshold met",
      "id": "slack-connector-id",
      "params": {
        "message": "Error rate exceeded threshold!"
      }
    }
  ],
  "params": {
    "index": ["logs-*"],
    "timeField": "@timestamp",
    "aggType": "count",
    "groupBy": "all",
    "termField": "level.keyword",
    "termSize": 5,
    "timeWindowSize": 5,
    "timeWindowUnit": "m",
    "thresholdComparator": ">",
    "threshold": [100],
    "filterKuery": "level:error"
  },
  "notify_when": "onActionGroupChange"
}'
```

**Elastalert (Alternative):**
```yaml
# elastalert/rules/high_error_rate.yml
name: High Error Rate
type: frequency
index: logs-*
num_events: 100
timeframe:
  minutes: 5

filter:
- query:
    query_string:
      query: "level:error AND environment:production"

alert:
- slack:
    slack_webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
- email:
    email: "team@example.com"

alert_subject: "High Error Rate Detected"
alert_text: |
  Error count exceeded 100 in last 5 minutes
  Environment: production
  Query: level:error
```

**Common Alert Rules:**

1. **High Error Rate**
   - Condition: > 100 errors in 5 minutes
   - Action: Page on-call, Slack notification

2. **Application Crash**
   - Condition: "fatal error" OR "panic" in logs
   - Action: Immediate page

3. **Disk Space Low**
   - Condition: "disk space" AND "critical"
   - Action: Slack notification

4. **Security Events**
   - Condition: Failed login attempts > 10 in 1 minute
   - Action: Security team notification

5. **Performance Degradation**
   - Condition: P95 response time > 2s for 10 minutes
   - Action: Team notification

**Verification:**
- [ ] Alert rules created
- [ ] Test alerts firing correctly
- [ ] Notifications delivered
- [ ] Alert thresholds appropriate
- [ ] No false positives

**If This Fails:**
→ Test query in Kibana Discover
→ Verify connector configuration
→ Check alert execution logs
→ Adjust thresholds based on baseline

---

### Step 8: Implement Security and Access Control

**What:** Secure log data and control access

**How:**
Enable Elasticsearch security features and implement RBAC.

**Code/Commands:**

**Enable Elasticsearch Security:**
```bash
# elasticsearch.yml
xpack.security.enabled: true
xpack.security.authc:
  api_key.enabled: true

# Set built-in user passwords
./bin/elasticsearch-setup-passwords auto

# Or interactive
./bin/elasticsearch-setup-passwords interactive
```

**Create Roles and Users:**
```bash
# Create developer role (read-only)
curl -X POST "localhost:9200/_security/role/developer" \
  -u elastic:password \
  -H 'Content-Type: application/json' -d'
{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["logs-app-*"],
      "privileges": ["read", "view_index_metadata"],
      "field_security": {
        "grant": ["*"],
        "except": ["user.password", "api_key"]
      }
    }
  ]
}'

# Create ops role (read-write)
curl -X POST "localhost:9200/_security/role/ops" \
  -u elastic:password \
  -H 'Content-Type: application/json' -d'
{
  "cluster": ["all"],
  "indices": [
    {
      "names": ["logs-*"],
      "privileges": ["all"]
    }
  ]
}'

# Create user
curl -X POST "localhost:9200/_security/user/john.doe" \
  -u elastic:password \
  -H 'Content-Type: application/json' -d'
{
  "password": "changeme",
  "roles": ["developer"],
  "full_name": "John Doe",
  "email": "john.doe@example.com"
}'
```

**Kibana Spaces (Tenancy):**
```bash
# Create space for team
curl -X POST "localhost:5601/api/spaces/space" \
  -H 'kbn-xsrf: true' \
  -u elastic:password \
  -H 'Content-Type: application/json' -d'
{
  "id": "backend-team",
  "name": "Backend Team",
  "description": "Space for backend team logs",
  "color": "#00bfb3",
  "initials": "BT"
}'
```

**Audit Logging:**
```yaml
# elasticsearch.yml
xpack.security.audit.enabled: true
xpack.security.audit.logfile.events.include: [
  "access_denied",
  "access_granted",
  "authentication_failed",
  "authentication_success",
  "connection_denied",
  "tampered_request"
]
```

**Data Masking:**
```ruby
# logstash.conf - Mask sensitive data
filter {
  # Mask credit card numbers
  mutate {
    gsub => [
      "message", "\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}", "XXXX-XXXX-XXXX-XXXX"
    ]
  }
  
  # Mask email addresses
  mutate {
    gsub => [
      "message", "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "***@***.***"
    ]
  }
  
  # Mask API keys
  mutate {
    gsub => [
      "message", "api[_-]?key[\"']?[=:][\"']?[a-zA-Z0-9]{32,}", "api_key=REDACTED"
    ]
  }
}
```

**Verification:**
- [ ] Security features enabled
- [ ] Users and roles created
- [ ] Access control working
- [ ] Audit logging enabled
- [ ] Sensitive data masked

**If This Fails:**
→ Review security configuration
→ Check user permissions
→ Test authentication
→ Review audit logs

---

## Verification Checklist

- [ ] ELK stack deployed and healthy
- [ ] Log shippers collecting logs
- [ ] Logs structured (JSON)
- [ ] Index templates and ILM configured
- [ ] Kibana dashboards created
- [ ] Alerts configured and tested
- [ ] Security and RBAC implemented
- [ ] Documentation complete
- [ ] Team trained on log searching

---

## Common Issues & Solutions

### Issue: Elasticsearch Out of Memory

**Symptoms:**
- Elasticsearch crashes
- "OutOfMemoryError" in logs
- Cluster becomes unresponsive

**Solution:**
```bash
# Increase heap size (50% of total RAM, max 32GB)
# elasticsearch.yml or environment
ES_JAVA_OPTS="-Xms16g -Xmx16g"

# Check current heap
curl -s localhost:9200/_cat/nodes?v&h=heap.percent,heap.current,heap.max

# Clear field data cache
curl -X POST "localhost:9200/_cache/clear?fielddata=true"

# Check for high cardinality fields
curl -s localhost:9200/_cat/fielddata?v&s=size:desc
```

**Prevention:**
- Right-size heap memory
- Monitor heap usage
- Avoid high cardinality fields
- Use proper data types in mappings

---

### Issue: Log Ingestion Falling Behind

**Symptoms:**
- Filebeat queues growing
- Logs delayed in Elasticsearch
- Logstash lag increasing

**Solution:**
```bash
# Scale Logstash horizontally
docker-compose scale logstash=3

# Increase Logstash workers
# logstash.yml
pipeline.workers: 8
pipeline.batch.size: 250

# Direct to Elasticsearch (bypass Logstash)
# filebeat.yml - Use for high volume
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  worker: 4
  bulk_max_size: 5000

# Monitor ingestion rate
curl -s localhost:9200/_cat/indices?v&h=index,docs.count,store.size
```

**Prevention:**
- Monitor ingestion lag
- Scale infrastructure proactively
- Optimize Logstash pipelines
- Consider direct Filebeat→ES for high volume

---

## Best Practices

### DO:
✅ **Use structured logging (JSON)** - Enables powerful searches  
✅ **Include trace IDs** - Correlate logs across services  
✅ **Set appropriate retention** - Balance cost and compliance  
✅ **Create index templates** - Ensure consistent mappings  
✅ **Implement ILM** - Automatic lifecycle management  
✅ **Monitor log volume** - Control costs  
✅ **Mask sensitive data** - PII, credentials, secrets  
✅ **Create saved searches** - Reusable queries  
✅ **Document common queries** - Team knowledge  
✅ **Alert on actionable events** - Not noise

### DON'T:
❌ **Log everything** - Adds cost and noise  
❌ **Use string for dates** - Use date type  
❌ **Create high-cardinality fields** - Kills performance  
❌ **Ignore mapping types** - Impacts search performance  
❌ **Log sensitive data** - Security/compliance risk  
❌ **Skip index management** - Disk fills up  
❌ **Forget log rotation** - Application disk issues  
❌ **Neglect security** - Log data is sensitive  
❌ **Over-alert** - Creates alert fatigue  
❌ **Ignore log structure** - Harder to search

---

## Related Workflows

**Prerequisites:**
- [Docker Container Creation](./docker_container_creation.md) - Containerized applications
- [Kubernetes Deployment](./kubernetes_deployment.md) - K8s log sources
- [Application Monitoring Setup](./application_monitoring_setup.md) - Complementary monitoring

**Next Steps:**
- [Incident Response Workflow](./incident_response_workflow.md) - Use logs for debugging
- [Security Audit Logging](../security/security_audit_logging.md) - Security-focused logging
- [Performance Tuning](./performance_tuning.md) - Analyze performance from logs

**Alternatives:**
- **Loki + Grafana** - Lightweight alternative
- **Splunk** - Enterprise logging platform
- **CloudWatch Logs** - AWS-native logging
- **Google Cloud Logging** - GCP-native logging
- **Azure Monitor** - Azure-native logging

---

## Tags
`devops` `logging` `elk-stack` `elasticsearch` `logstash` `kibana` `filebeat` `log-aggregation` `observability` `monitoring`
