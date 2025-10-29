# Kubernetes Deployment

**ID:** devops-010  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Advanced  
**Estimated Time:** 2-3 hours  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for deploying applications to Kubernetes clusters with proper configuration, scaling, and monitoring

**Why:** Kubernetes provides container orchestration, automatic scaling, self-healing, and rolling updates for production applications. Proper K8s deployment enables high availability, efficient resource utilization, and simplified operations at scale.

**When to use:**
- Deploying containerized applications to production
- Scaling applications beyond single-host capacity
- Implementing high availability and fault tolerance
- Managing microservices architectures
- Automated rollouts and rollbacks
- Multi-environment deployments (dev, staging, prod)

---

## Prerequisites

**Required:**
- [ ] Kubernetes cluster access (kubectl configured)
- [ ] Docker images built and pushed to registry
- [ ] Understanding of K8s concepts (Pods, Deployments, Services)
- [ ] kubectl installed (`kubectl version`)
- [ ] Application requirements documented

**Check before starting:**
```bash
# Verify kubectl installation
kubectl version --client

# Check cluster connection
kubectl cluster-info

# Verify cluster access
kubectl get nodes

# Check current context
kubectl config current-context

# List available contexts
kubectl config get-contexts

# Test cluster permissions
kubectl auth can-i create deployments
kubectl auth can-i create services
```

---

## Implementation Steps

### Step 1: Prepare Kubernetes Manifests

**What:** Create YAML files defining your application's Kubernetes resources

**How:**
Define Deployment, Service, ConfigMap, and Secret resources for your application.

**Code/Commands:**
```yaml
# deployment.yaml - Main application deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
  labels:
    app: myapp
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: v1.0.0
    spec:
      # Use specific image version, never :latest
      containers:
      - name: myapp
        image: myregistry.com/myapp:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        
        # Resource limits (critical for production)
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # Environment variables
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: redis-url
        
        # Liveness probe (restart if unhealthy)
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe (remove from load balancer if not ready)
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Volume mounts
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: logs
          mountPath: /app/logs
      
      # Volumes
      volumes:
      - name: config
        configMap:
          name: myapp-config
      - name: logs
        emptyDir: {}
      
      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      # Image pull secrets (for private registries)
      imagePullSecrets:
      - name: regcred
---
# service.yaml - Expose application
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: production
  labels:
    app: myapp
spec:
  type: LoadBalancer  # or ClusterIP, NodePort
  selector:
    app: myapp
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
---
# configmap.yaml - Non-sensitive configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: production
data:
  redis-url: "redis://redis-service:6379/0"
  log-level: "info"
  app.conf: |
    max_connections=100
    timeout=30
---
# secret.yaml - Sensitive data (base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
  namespace: production
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BkYjozNDMyL215ZGI=  # base64 encoded
  api-key: YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=  # base64 encoded
---
# ingress.yaml - HTTP routing
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80
```

```bash
# Create namespace
kubectl create namespace production

# Encode secrets
echo -n "postgresql://user:pass@db:5432/mydb" | base64
echo -n "your-api-key" | base64

# Create image pull secret (private registry)
kubectl create secret docker-registry regcred \
  --docker-server=myregistry.com \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=email@example.com \
  -n production

# Validate manifests
kubectl apply --dry-run=client -f deployment.yaml
kubectl apply --dry-run=server -f deployment.yaml
```

**Verification:**
- [ ] All YAML files valid
- [ ] Resources have proper labels
- [ ] Resource limits defined
- [ ] Health checks configured
- [ ] Secrets base64 encoded
- [ ] Namespace specified

**If This Fails:**
→ Validate YAML syntax with kubeval
→ Check indentation (YAML is sensitive)
→ Verify image exists in registry
→ Ensure secrets are properly encoded

---

### Step 2: Deploy to Kubernetes Cluster

**What:** Apply manifests to create resources in the cluster

**How:**
Use kubectl apply to create or update resources.

**Code/Commands:**
```bash
# Create namespace first
kubectl create namespace production

# Apply all manifests
kubectl apply -f k8s/

# Or apply specific files in order
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Watch deployment progress
kubectl rollout status deployment/myapp -n production

# View deployment
kubectl get deployments -n production
kubectl get pods -n production
kubectl get services -n production

# Describe resources for detailed info
kubectl describe deployment myapp -n production
kubectl describe pod myapp-xxx -n production

# View logs
kubectl logs -f deployment/myapp -n production

# Get all resources in namespace
kubectl get all -n production

# Create deployment script
cat > deploy.sh <<'EOF'
#!/bin/bash
set -euo pipefail

NAMESPACE=${1:-production}
VERSION=${2:-latest}

echo "🚀 Deploying to $NAMESPACE..."

# Update image version in deployment
kubectl set image deployment/myapp \
  myapp=myregistry.com/myapp:$VERSION \
  -n $NAMESPACE

# Wait for rollout
kubectl rollout status deployment/myapp -n $NAMESPACE

# Verify deployment
kubectl get pods -n $NAMESPACE -l app=myapp

echo "✅ Deployment complete!"
EOF

chmod +x deploy.sh
./deploy.sh production 1.0.0
```

**Verification:**
- [ ] All resources created successfully
- [ ] Pods running (kubectl get pods)
- [ ] Services accessible
- [ ] No error events
- [ ] Health checks passing

**If This Fails:**
→ Check pod logs: `kubectl logs <pod-name>`
→ Describe pod for events: `kubectl describe pod <pod-name>`
→ Verify image can be pulled
→ Check resource availability (CPU/memory)

---

### Step 3: Configure Auto-Scaling

**What:** Enable automatic scaling based on resource usage or custom metrics

**How:**
Create HorizontalPodAutoscaler (HPA) resource.

**Code/Commands:**
```yaml
# hpa.yaml - Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

```bash
# Apply HPA
kubectl apply -f hpa.yaml

# View HPA status
kubectl get hpa -n production
kubectl describe hpa myapp-hpa -n production

# Manually scale (override HPA temporarily)
kubectl scale deployment myapp --replicas=5 -n production

# Test autoscaling with load
kubectl run -it --rm load-generator --image=busybox -- /bin/sh
# Inside pod: while true; do wget -q -O- http://myapp-service; done

# Watch scaling in action
watch kubectl get hpa,deployment -n production
```

**Verification:**
- [ ] HPA created and active
- [ ] Scales up under load
- [ ] Scales down when idle
- [ ] Respects min/max replicas
- [ ] Metrics available

**If This Fails:**
→ Ensure metrics-server installed: `kubectl get deployment metrics-server -n kube-system`
→ Check resource requests are set
→ Verify metrics available: `kubectl top pods`

---

### Step 4: Implement Rolling Updates and Rollbacks

**What:** Update application with zero downtime and ability to rollback

**How:**
Use kubectl set image and rollout commands.

**Code/Commands:**
```bash
# Update to new version (rolling update)
kubectl set image deployment/myapp \
  myapp=myregistry.com/myapp:1.1.0 \
  -n production

# Watch rollout
kubectl rollout status deployment/myapp -n production

# Pause rollout (if issues detected)
kubectl rollout pause deployment/myapp -n production

# Resume rollout
kubectl rollout resume deployment/myapp -n production

# View rollout history
kubectl rollout history deployment/myapp -n production

# Rollback to previous version
kubectl rollout undo deployment/myapp -n production

# Rollback to specific revision
kubectl rollout undo deployment/myapp --to-revision=2 -n production

# Create blue-green deployment script
cat > blue-green-deploy.sh <<'EOF'
#!/bin/bash
set -euo pipefail

VERSION=$1
NAMESPACE="production"

# Deploy green (new version)
kubectl apply -f - <<YAML
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  namespace: $NAMESPACE
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myregistry.com/myapp:$VERSION
YAML

# Wait for green to be ready
kubectl rollout status deployment/myapp-green -n $NAMESPACE

# Test green deployment
echo "Testing green deployment..."
sleep 10

# Switch traffic to green
kubectl patch service myapp-service -n $NAMESPACE \
  -p '{"spec":{"selector":{"version":"green"}}}'

echo "✅ Traffic switched to green"

# Delete blue (old version) after verification
read -p "Delete blue deployment? (y/n) " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
  kubectl delete deployment myapp-blue -n $NAMESPACE
fi
EOF

chmod +x blue-green-deploy.sh
```

**Verification:**
- [ ] Rolling update completes successfully
- [ ] No downtime during update
- [ ] Rollback works correctly
- [ ] Old pods terminated after update
- [ ] Application functions correctly after update

**If This Fails:**
→ Immediately rollback: `kubectl rollout undo deployment/myapp`
→ Check new image works
→ Review pod events and logs
→ Verify health checks passing

---

### Step 5: Set Up Monitoring and Logging

**What:** Monitor application health, performance, and logs

**How:**
Configure Prometheus metrics, log aggregation, and alerting.

**Code/Commands:**
```yaml
# servicemonitor.yaml - Prometheus monitoring
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp-monitor
  namespace: production
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
---
# prometheusrule.yaml - Alerting rules
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: myapp-alerts
  namespace: production
spec:
  groups:
  - name: myapp
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
    
    - alert: PodNotReady
      expr: kube_pod_status_ready{namespace="production",pod=~"myapp-.*"} == 0
      for: 5m
      labels:
        severity: warning
```

```bash
# View logs
kubectl logs -f deployment/myapp -n production

# Logs from all pods
kubectl logs -f -l app=myapp -n production

# Previous container logs (if crashed)
kubectl logs myapp-xxx --previous -n production

# Stream logs to file
kubectl logs -f deployment/myapp -n production > app.log

# Get pod metrics
kubectl top pods -n production
kubectl top nodes

# Port forward for local debugging
kubectl port-forward service/myapp-service 8000:80 -n production

# Execute command in pod
kubectl exec -it myapp-xxx -n production -- /bin/bash

# Debug with ephemeral container
kubectl debug myapp-xxx -n production -it --image=busybox

# Create monitoring dashboard access
kubectl port-forward -n monitoring service/grafana 3000:3000
```

**Verification:**
- [ ] Logs accessible via kubectl
- [ ] Metrics being collected
- [ ] Alerts configured
- [ ] Dashboard access working
- [ ] Resource usage visible

**If This Fails:**
→ Check log volume permissions
→ Verify Prometheus operator installed
→ Test metrics endpoint accessibility
→ Review pod logs for errors

---

### Step 6: Implement Security Best Practices

**What:** Harden Kubernetes deployment for production

**How:**
Apply security contexts, network policies, and RBAC.

**Code/Commands:**
```yaml
# networkpolicy.yaml - Restrict traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: myapp-netpol
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
---
# podsecuritypolicy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
```

```bash
# Scan for vulnerabilities
trivy image myregistry.com/myapp:1.0.0

# Check security context
kubectl get pod myapp-xxx -n production -o yaml | grep -A 10 securityContext

# Audit RBAC permissions
kubectl auth can-i --list --as=system:serviceaccount:production:default

# Create service account with limited permissions
kubectl create serviceaccount myapp-sa -n production

# Create role and binding
kubectl create role myapp-role \
  --verb=get,list,watch \
  --resource=pods,services \
  -n production

kubectl create rolebinding myapp-binding \
  --role=myapp-role \
  --serviceaccount=production:myapp-sa \
  -n production
```

**Verification:**
- [ ] Pods run as non-root
- [ ] Network policies applied
- [ ] RBAC configured
- [ ] No privileged containers
- [ ] Secrets encrypted at rest
- [ ] Image vulnerabilities scanned

**If This Fails:**
→ Review security policy errors
→ Adjust security context
→ Check RBAC permissions
→ Update images to fix vulnerabilities

---

### Step 7: Manage Persistent Storage

**What:** Configure persistent storage for stateful applications

**How:**
Create PersistentVolumeClaims and StatefulSets for stateful workloads.

**Code/Commands:**
```yaml
# statefulset.yaml - For stateful apps like databases
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: production
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 10Gi
---
# pvc.yaml - Persistent Volume Claim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myapp-data
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 5Gi
```

```bash
# View storage classes
kubectl get storageclass

# View PVs and PVCs
kubectl get pv
kubectl get pvc -n production

# Backup PVC data
kubectl get pvc myapp-data -n production -o yaml > pvc-backup.yaml

# Resize PVC (if storage class supports it)
kubectl patch pvc myapp-data -n production \
  -p '{"spec":{"resources":{"requests":{"storage":"10Gi"}}}}'
```

**Verification:**
- [ ] PVCs bound to PVs
- [ ] Data persists across pod restarts
- [ ] Backup procedures in place
- [ ] Storage class appropriate
- [ ] Sufficient capacity

**If This Fails:**
→ Check storage class exists and is default
→ Verify PV available with matching spec
→ Check storage provisioner status
→ Review PVC events

---

### Step 8: Implement CI/CD Integration

**What:** Automate deployment through CI/CD pipeline

**How:**
Integrate kubectl commands into your CI/CD workflow.

**Code/Commands:**
```yaml
# .github/workflows/deploy.yml - GitHub Actions example
name: Deploy to Kubernetes

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push image
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
      
      - name: Install kubectl
        uses: azure/setup-kubectl@v3
      
      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
      
      - name: Deploy to cluster
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n production
          
          kubectl rollout status deployment/myapp -n production
      
      - name: Verify deployment
        run: |
          kubectl get pods -n production -l app=myapp
          kubectl exec -n production deployment/myapp -- curl -f http://localhost:8000/health
```

```bash
# Helm chart for easier management (alternative)
helm create myapp
helm install myapp ./myapp -n production
helm upgrade myapp ./myapp -n production
helm rollback myapp -n production
```

**Verification:**
- [ ] CI/CD pipeline successfully deploys
- [ ] Automated rollout status check
- [ ] Deployment verified automatically
- [ ] Rollback on failure
- [ ] Proper credential management

**If This Fails:**
→ Verify kubeconfig access
→ Check CI/CD service account permissions
→ Test kubectl commands locally first
→ Review pipeline logs

---

## Verification Checklist

- [ ] All manifests applied successfully
- [ ] Pods running and healthy
- [ ] Services accessible
- [ ] Auto-scaling configured
- [ ] Rolling updates work
- [ ] Rollback tested
- [ ] Monitoring and logging setup
- [ ] Security policies applied
- [ ] Persistent storage configured (if needed)
- [ ] CI/CD integration complete

---

## Common Issues & Solutions

### Issue: ImagePullBackOff

**Symptoms:**
- Pod stuck in ImagePullBackOff state
- Cannot pull image from registry

**Solution:**
```bash
# Check image exists
docker pull myregistry.com/myapp:1.0.0

# Verify image pull secret
kubectl get secret regcred -n production -o yaml

# Recreate secret
kubectl create secret docker-registry regcred \
  --docker-server=myregistry.com \
  --docker-username=user \
  --docker-password=pass \
  -n production --dry-run=client -o yaml | kubectl apply -f -
```

**Prevention:**
- Verify image exists before deploying
- Test image pull secrets
- Use correct registry URL

---

### Issue: CrashLoopBackOff

**Symptoms:**
- Pod repeatedly crashing and restarting

**Solution:**
```bash
# View logs
kubectl logs myapp-xxx -n production --previous

# Describe pod for events
kubectl describe pod myapp-xxx -n production

# Common causes:
# 1. Missing environment variables
# 2. Application startup errors
# 3. Health check failures
# 4. Resource limits too low

# Temporarily disable health checks to debug
kubectl patch deployment myapp -n production -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "myapp",
          "livenessProbe": null,
          "readinessProbe": null
        }]
      }
    }
  }
}'
```

**Prevention:**
- Test containers locally first
- Proper health check configuration
- Adequate resource limits
- Comprehensive logging

---

## Best Practices

### DO:
✅ **Use specific image tags** - Never use `:latest` in production  
✅ **Set resource limits** - Prevent resource exhaustion  
✅ **Configure health checks** - Enable self-healing  
✅ **Use namespaces** - Organize and isolate resources  
✅ **Implement RBAC** - Principle of least privilege  
✅ **Network policies** - Restrict traffic  
✅ **Monitor everything** - Metrics, logs, traces  
✅ **Automate deployments** - CI/CD integration  
✅ **Version control manifests** - Track infrastructure changes  
✅ **Test in staging first** - Validate before production

### DON'T:
❌ **Run as root** - Security vulnerability  
❌ **Store secrets in code** - Use Kubernetes Secrets  
❌ **Skip health checks** - No auto-recovery  
❌ **Ignore resource limits** - Can crash nodes  
❌ **Deploy without testing** - Always test first  
❌ **Use latest tag** - Version instability  
❌ **Expose everything** - Minimize attack surface  
❌ **Skip monitoring** - No visibility  
❌ **Manual deployments** - Error-prone  
❌ **Forget backups** - Data loss risk

---

## Related Workflows

**Prerequisites:**
- [Docker Container Creation](./docker_container_creation.md) - Build container images
- [Docker Compose Multi-Service](./docker_compose_multi_service.md) - Local multi-container setup

**Next Steps:**
- [Application Monitoring Setup](./application_monitoring_setup.md) - Comprehensive monitoring
- [Infrastructure as Code with Terraform](./infrastructure_as_code_terraform.md) - Manage K8s with IaC
- [CI/CD Pipeline Setup](./cicd_pipeline_setup.md) - Automated deployments

**Alternatives:**
- [Cloud Provider Setup](./cloud_provider_setup.md) - Managed Kubernetes services (EKS, GKE, AKS)

---

## Tags
`devops` `kubernetes` `k8s` `deployment` `orchestration` `containers` `cloud-native` `microservices` `production` `scaling`
