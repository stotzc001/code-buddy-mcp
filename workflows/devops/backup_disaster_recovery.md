# Backup and Disaster Recovery

**ID:** devops-003  
**Category:** DevOps  
**Priority:** CRITICAL  
**Complexity:** Intermediate-Advanced  
**Estimated Time:** 4-6 hours (initial setup)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for implementing comprehensive backup strategies and disaster recovery (DR) procedures to protect against data loss and ensure business continuity

**Why:** Data loss from hardware failures, human errors, cyber attacks, or natural disasters can devastate businesses. A robust backup and DR strategy ensures you can recover data and restore operations quickly, minimizing downtime and data loss. Without proper backups, businesses risk permanent data loss, regulatory penalties, and loss of customer trust.

**When to use:**
- Setting up new production systems
- Implementing data protection policies
- Meeting compliance requirements (SOC 2, GDPR, HIPAA)
- Planning for business continuity
- After significant infrastructure changes
- Regular DR testing (quarterly/annually)

---

## Prerequisites

**Required:**
- [ ] Production systems documented
- [ ] RPO (Recovery Point Objective) defined
- [ ] RTO (Recovery Time Objective) defined
- [ ] Backup storage location (S3, Azure Blob, etc.)
- [ ] Backup tools selected (native tools, Velero, etc.)
- [ ] Disaster recovery plan template

**Check before starting:**
```bash
# Identify systems requiring backup
kubectl get pv  # Kubernetes volumes
docker volume ls  # Docker volumes
df -h  # File systems

# Check available backup storage
aws s3 ls s3://backup-bucket/
# or
gsutil ls gs://backup-bucket/

# Test network connectivity to backup destination
ping backup-server.example.com
nc -zv backup-server.example.com 22

# Verify backup tools installed
which pg_dump mysqldump mongodump
which restic duplicity
```

---

## Implementation Steps

### Step 1: Define Backup and DR Requirements

**What:** Establish recovery objectives, backup scope, and compliance needs

**How:**
Document RPO, RTO, backup requirements, and create disaster recovery plan.

**Code/Commands:**
```bash
# Create DR requirements document
cat > DR_REQUIREMENTS.md <<'EOF'
# Disaster Recovery Requirements

## Recovery Objectives

### RPO (Recovery Point Objective)
**Maximum acceptable data loss**

| System | RPO | Backup Frequency | Justification |
|--------|-----|------------------|---------------|
| Production Database | 1 hour | Continuous (WAL) + Hourly snapshots | Financial transactions |
| Application Code | 0 (Git) | Real-time | Version controlled |
| User Uploads | 24 hours | Daily | User-generated content |
| Logs | 24 hours | Daily | Debugging/compliance |
| Configuration | 0 (Git) | Real-time | Infrastructure as Code |

### RTO (Recovery Time Objective)
**Maximum acceptable downtime**

| System | RTO | Recovery Method | Priority |
|--------|-----|----------------|----------|
| Production Database | 1 hour | Automated restore | Critical |
| Application Services | 30 minutes | Container redeploy | Critical |
| Admin Dashboard | 4 hours | Manual restore | High |
| Analytics | 24 hours | Manual restore | Medium |

## Backup Scope

### Data to Backup
- ✅ Production databases (PostgreSQL, MySQL, MongoDB)
- ✅ File storage (S3, user uploads)
- ✅ Kubernetes persistent volumes
- ✅ Configuration files and secrets
- ✅ Application logs (30-90 days)
- ✅ Docker images and registries
- ❌ Caches (Redis) - Rebuildable
- ❌ Temporary files - Not needed

### Backup Locations

**Primary:** AWS S3 (us-east-1)
- Versioning enabled
- Lifecycle policies configured
- Cross-region replication to us-west-2

**Secondary:** Azure Blob Storage (offsite)
- Geographic redundancy
- Air-gapped copy for ransomware protection

## Compliance Requirements

### Retention Policies
- **Transactional Data:** 7 years (SOX compliance)
- **User Data:** As per GDPR (Right to be forgotten)
- **Financial Records:** 7 years
- **Security Logs:** 1 year (SOC 2)

### Encryption
- At-rest: AES-256
- In-transit: TLS 1.3
- Key management: AWS KMS / Azure Key Vault

## Disaster Scenarios

### Covered Scenarios
1. **Hardware Failure:** Single server/node failure
2. **Data Corruption:** Accidental deletion, bad deployment
3. **Cyber Attack:** Ransomware, data breach
4. **Regional Outage:** AWS region unavailable
5. **Human Error:** Accidental DROP TABLE, rm -rf

### Recovery Strategies
- **Database:** Point-in-time recovery (PITR)
- **Applications:** Blue-green deployment, immutable infrastructure
- **Infrastructure:** Terraform state backup, multi-region setup
- **Data:** Versioned backups, immutable storage

## Team Responsibilities

### Backup Operations
- **Primary:** DevOps Team
- **Escalation:** Engineering Manager
- **Testing:** QA Team (quarterly)

### Recovery Operations  
- **Incident Commander:** On-call engineer
- **Database Recovery:** Database Admin
- **Application Recovery:** DevOps + Dev Team
- **Validation:** QA Team
EOF
```

**Verification:**
- [ ] RPO/RTO defined for all systems
- [ ] Backup scope documented
- [ ] Retention policies comply with regulations
- [ ] Disaster scenarios identified
- [ ] Team roles assigned

**If This Fails:**
→ Conduct risk assessment workshop with stakeholders
→ Review compliance requirements with legal team
→ Start with critical systems only
→ Refine iteratively based on business needs

---

### Step 2: Set Up Database Backups

**What:** Implement automated, encrypted database backups with point-in-time recovery

**How:**
Configure native database backup tools with automation and verification.

**Code/Commands:**

**PostgreSQL Backups:**
```bash
# Create backup script
cat > /opt/scripts/postgres-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-production}"
BACKUP_DIR="/var/backups/postgres"
S3_BUCKET="${S3_BUCKET:-s3://my-backups/postgres}"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql.gz"

# Backup database
echo "Starting backup of $DB_NAME..."
pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" \
  | gzip > "$BACKUP_FILE"

# Verify backup
if [ ! -s "$BACKUP_FILE" ]; then
  echo "ERROR: Backup file is empty!"
  exit 1
fi

# Encrypt backup
openssl enc -aes-256-cbc -salt \
  -in "$BACKUP_FILE" \
  -out "${BACKUP_FILE}.enc" \
  -pass pass:"$BACKUP_ENCRYPTION_KEY"

rm "$BACKUP_FILE"  # Remove unencrypted

# Upload to S3
aws s3 cp "${BACKUP_FILE}.enc" "$S3_BUCKET/"

# Verify upload
if ! aws s3 ls "${S3_BUCKET}/$(basename ${BACKUP_FILE}.enc)"; then
  echo "ERROR: S3 upload failed!"
  exit 1
fi

# Calculate checksums
md5sum "${BACKUP_FILE}.enc" > "${BACKUP_FILE}.enc.md5"
aws s3 cp "${BACKUP_FILE}.enc.md5" "$S3_BUCKET/"

# Cleanup old local backups
find "$BACKUP_DIR" -name "*.enc" -mtime +7 -delete

# Cleanup old S3 backups (lifecycle handles this but good to verify)
aws s3 ls "$S3_BUCKET/" \
  | grep '.sql.gz.enc$' \
  | sort -r \
  | tail -n +$((RETENTION_DAYS + 1)) \
  | awk '{print $4}' \
  | while read file; do
    echo "Deleting old backup: $file"
    aws s3 rm "${S3_BUCKET}/${file}"
  done

echo "Backup completed successfully: $(basename $BACKUP_FILE).enc"

# Log to monitoring
curl -X POST http://prometheus-pushgateway:9091/metrics/job/backup/instance/postgres \
  --data-binary @- <<METRICS
# TYPE postgres_backup_success gauge
postgres_backup_success{database="$DB_NAME"} 1
# TYPE postgres_backup_size_bytes gauge
postgres_backup_size_bytes{database="$DB_NAME"} $(stat -f%z "${BACKUP_FILE}.enc")
# TYPE postgres_backup_timestamp gauge
postgres_backup_timestamp{database="$DB_NAME"} $(date +%s)
METRICS
EOF

chmod +x /opt/scripts/postgres-backup.sh

# Add to crontab (hourly)
(crontab -l 2>/dev/null; echo "0 * * * * /opt/scripts/postgres-backup.sh") | crontab -

# Enable WAL archiving for point-in-time recovery
cat >> postgresql.conf <<EOF
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f'
max_wal_senders = 3
EOF

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**MySQL/MariaDB Backups:**
```bash
# Create MySQL backup script
cat > /opt/scripts/mysql-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

DB_USER="backup_user"
DB_PASSWORD="${MYSQL_BACKUP_PASSWORD}"
BACKUP_DIR="/var/backups/mysql"
S3_BUCKET="s3://my-backups/mysql"

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Full backup with mysqldump
mysqldump --user="$DB_USER" \
  --password="$DB_PASSWORD" \
  --single-transaction \
  --quick \
  --lock-tables=false \
  --all-databases \
  | gzip > "$BACKUP_DIR/full_backup_${TIMESTAMP}.sql.gz"

# Binary log backup (point-in-time recovery)
mysql --user="$DB_USER" \
  --password="$DB_PASSWORD" \
  --batch --skip-column-names \
  -e "SHOW MASTER STATUS" \
  > "$BACKUP_DIR/binlog_position_${TIMESTAMP}.txt"

# Upload to S3
aws s3 sync "$BACKUP_DIR/" "$S3_BUCKET/" --exclude "*" --include "*${TIMESTAMP}*"

# Cleanup
find "$BACKUP_DIR" -mtime +7 -delete

echo "MySQL backup completed"
EOF

chmod +x /opt/scripts/mysql-backup.sh

# Ensure binary logging enabled
# /etc/mysql/my.cnf
[mysqld]
log-bin=mysql-bin
expire_logs_days=7
```

**MongoDB Backups:**
```bash
# MongoDB backup script
cat > /opt/scripts/mongodb-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

MONGO_HOST="localhost:27017"
MONGO_DB="production"
BACKUP_DIR="/var/backups/mongodb"
S3_BUCKET="s3://my-backups/mongodb"

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"

# Backup with mongodump
mongodump \
  --host="$MONGO_HOST" \
  --db="$MONGO_DB" \
  --out="$BACKUP_PATH" \
  --gzip

# Create tarball
tar -czf "${BACKUP_PATH}.tar.gz" -C "$BACKUP_DIR" "$TIMESTAMP"
rm -rf "$BACKUP_PATH"

# Upload to S3
aws s3 cp "${BACKUP_PATH}.tar.gz" "$S3_BUCKET/"

# Cleanup
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "MongoDB backup completed"
EOF

chmod +x /opt/scripts/mongodb-backup.sh
```

**Kubernetes Persistent Volume Backups (Velero):**
```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket velero-backups \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --secret-file ./credentials-velero

# Create backup schedule
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces production \
  --ttl 720h0m0s

# Manual backup
velero backup create production-backup-$(date +%Y%m%d) \
  --include-namespaces production \
  --wait

# List backups
velero backup get
```

**Verification:**
- [ ] Backup scripts created and tested
- [ ] Backups running on schedule
- [ ] Backups encrypted
- [ ] Backups uploaded to remote storage
- [ ] Backup monitoring in place

**If This Fails:**
→ Test backup script manually first
→ Check database credentials
→ Verify storage connectivity
→ Review logs for specific errors

---

### Step 3: Implement File and Object Storage Backups

**What:** Back up file systems, user uploads, and object storage

**How:**
Use rsync, restic, or cloud-native replication for file backups.

**Code/Commands:**

**Restic for File Backups:**
```bash
# Install restic
wget https://github.com/restic/restic/releases/download/v0.16.0/restic_0.16.0_linux_amd64.bz2
bunzip2 restic_0.16.0_linux_amd64.bz2
chmod +x restic_0.16.0_linux_amd64
sudo mv restic_0.16.0_linux_amd64 /usr/local/bin/restic

# Initialize repository
export RESTIC_PASSWORD="your-secure-password"
export RESTIC_REPOSITORY="s3:s3.amazonaws.com/my-backup-bucket/restic"

restic init

# Create backup script
cat > /opt/scripts/file-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

export RESTIC_PASSWORD="${RESTIC_PASSWORD}"
export RESTIC_REPOSITORY="s3:s3.amazonaws.com/my-backup-bucket/restic"

# Directories to backup
BACKUP_DIRS=(
  "/var/www/uploads"
  "/opt/application/data"
  "/etc/nginx"
  "/etc/ssl"
)

# Exclude patterns
EXCLUDE_FILE="/opt/scripts/restic-exclude.txt"

# Create backup
restic backup "${BACKUP_DIRS[@]}" \
  --exclude-file="$EXCLUDE_FILE" \
  --tag daily \
  --tag "$(hostname)"

# Prune old backups (keep policy)
restic forget \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 12 \
  --keep-yearly 2 \
  --prune

# Check repository
restic check

echo "File backup completed"
EOF

# Exclude file
cat > /opt/scripts/restic-exclude.txt <<'EOF'
*.tmp
*.cache
*.log
node_modules/
.git/
EOF

chmod +x /opt/scripts/file-backup.sh

# Schedule backup
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/scripts/file-backup.sh") | crontab -
```

**AWS S3 Replication:**
```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-source-bucket \
  --versioning-configuration Status=Enabled

# Create replication rule
cat > replication-config.json <<EOF
{
  "Role": "arn:aws:iam::123456789:role/s3-replication-role",
  "Rules": [
    {
      "Status": "Enabled",
      "Priority": 1,
      "DeleteMarkerReplication": { "Status": "Enabled" },
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::my-backup-bucket",
        "ReplicationTime": {
          "Status": "Enabled",
          "Time": { "Minutes": 15 }
        },
        "Metrics": {
          "Status": "Enabled",
          "EventThreshold": { "Minutes": 15 }
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-replication \
  --bucket my-source-bucket \
  --replication-configuration file://replication-config.json
```

**Rsync for Server-to-Server:**
```bash
# Create rsync backup script
cat > /opt/scripts/rsync-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

SOURCE_DIR="/var/www"
DEST_SERVER="backup-server.example.com"
DEST_DIR="/backups/$(hostname)"
SSH_KEY="/root/.ssh/backup_key"

# Create backup with rsync
rsync -avz --delete \
  --exclude '*.tmp' \
  --exclude 'cache/*' \
  -e "ssh -i $SSH_KEY" \
  "$SOURCE_DIR/" \
  "backup@${DEST_SERVER}:${DEST_DIR}/"

echo "Rsync backup completed"
EOF

chmod +x /opt/scripts/rsync-backup.sh
```

**Verification:**
- [ ] File backups running
- [ ] Backup retention policy applied
- [ ] Incremental backups working
- [ ] Backup integrity verified
- [ ] Remote storage accessible

**If This Fails:**
→ Check file permissions
→ Verify storage space available
→ Test network connectivity
→ Review exclude patterns

---

### Step 4: Back Up Configuration and Infrastructure

**What:** Protect infrastructure configuration, Kubernetes resources, and secrets

**How:**
Version control infrastructure code and backup cluster state.

**Code/Commands:**

**Kubernetes Resource Backup:**
```bash
# Backup all resources
kubectl get all --all-namespaces -o yaml > k8s-backup-$(date +%Y%m%d).yaml

# Backup specific resources
kubectl get configmaps --all-namespaces -o yaml > configmaps-backup.yaml
kubectl get secrets --all-namespaces -o yaml > secrets-backup.yaml
kubectl get pv,pvc --all-namespaces -o yaml > volumes-backup.yaml

# Automated backup script
cat > /opt/scripts/k8s-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/var/backups/kubernetes"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# Backup all resources
for resource in pods deployments services configmaps secrets pv pvc; do
  kubectl get "$resource" --all-namespaces -o yaml \
    > "$BACKUP_DIR/$TIMESTAMP/${resource}.yaml"
done

# Backup ETCD (if direct access)
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save "$BACKUP_DIR/$TIMESTAMP/etcd-snapshot.db"

# Upload to S3
tar -czf "$BACKUP_DIR/k8s-backup-${TIMESTAMP}.tar.gz" \
  -C "$BACKUP_DIR" "$TIMESTAMP"

aws s3 cp "$BACKUP_DIR/k8s-backup-${TIMESTAMP}.tar.gz" \
  s3://my-backups/kubernetes/

# Cleanup
rm -rf "$BACKUP_DIR/$TIMESTAMP"
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Kubernetes backup completed"
EOF

chmod +x /opt/scripts/k8s-backup.sh
```

**Terraform State Backup:**
```bash
# Enable S3 versioning for state
aws s3api put-bucket-versioning \
  --bucket terraform-state-bucket \
  --versioning-configuration Status=Enabled

# Enable lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket terraform-state-bucket \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json
cat > lifecycle.json <<'EOF'
{
  "Rules": [
    {
      "Id": "ArchiveOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 30,
          "StorageClass": "GLACIER"
        }
      ],
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 365
      }
    }
  ]
}
EOF
```

**Docker Registry Backup:**
```bash
# Backup Docker registry
cat > /opt/scripts/registry-backup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

REGISTRY_HOST="registry.example.com"
BACKUP_DIR="/var/backups/registry"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# List all images
images=$(curl -s https://${REGISTRY_HOST}/v2/_catalog | jq -r '.repositories[]')

# Pull and save each image
for image in $images; do
  tags=$(curl -s https://${REGISTRY_HOST}/v2/${image}/tags/list | jq -r '.tags[]')
  for tag in $tags; do
    echo "Backing up ${image}:${tag}..."
    docker pull "${REGISTRY_HOST}/${image}:${tag}"
    docker save "${REGISTRY_HOST}/${image}:${tag}" \
      | gzip > "$BACKUP_DIR/${image//\//_}_${tag}_${TIMESTAMP}.tar.gz"
  done
done

# Upload to S3
aws s3 sync "$BACKUP_DIR/" s3://my-backups/registry/

# Cleanup old backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Registry backup completed"
EOF

chmod +x /opt/scripts/registry-backup.sh
```

**Verification:**
- [ ] Kubernetes resources backed up
- [ ] ETCD snapshots created
- [ ] Terraform state versioned
- [ ] Docker images backed up
- [ ] Configuration in version control

**If This Fails:**
→ Check kubectl/API access
→ Verify ETCD access
→ Review permissions
→ Test restore procedure

---

### Step 5: Implement Backup Monitoring and Alerting

**What:** Monitor backup health and alert on failures

**How:**
Create monitoring for backup success, size, and freshness.

**Code/Commands:**

**Prometheus Metrics:**
```bash
# Add to backup scripts
cat >> /opt/scripts/backup-metrics.sh <<'EOF'
#!/bin/bash

# Function to push metrics
push_backup_metrics() {
  local job_name="$1"
  local backup_name="$2"
  local success="$3"
  local size_bytes="$4"
  
  cat <<METRICS | curl --data-binary @- \
    http://prometheus-pushgateway:9091/metrics/job/${job_name}/instance/${backup_name}
# TYPE backup_last_success_timestamp gauge
backup_last_success_timestamp{backup="${backup_name}"} $(date +%s)
# TYPE backup_success gauge
backup_success{backup="${backup_name}"} ${success}
# TYPE backup_size_bytes gauge
backup_size_bytes{backup="${backup_name}"} ${size_bytes}
METRICS
}

# Usage in backup scripts
if [ $? -eq 0 ]; then
  push_backup_metrics "database" "postgres-production" 1 $(stat -f%z "$BACKUP_FILE")
else
  push_backup_metrics "database" "postgres-production" 0 0
fi
EOF
```

**Prometheus Alert Rules:**
```yaml
# prometheus/alerts/backup-alerts.yml
groups:
  - name: backup_alerts
    interval: 1m
    rules:
      # Backup failed
      - alert: BackupFailed
        expr: backup_success == 0
        for: 5m
        labels:
          severity: critical
          team: devops
        annotations:
          summary: "Backup failed for {{ $labels.backup }}"
          description: "Backup {{ $labels.backup }} has failed"
      
      # Backup too old
      - alert: BackupTooOld
        expr: (time() - backup_last_success_timestamp) > 86400
        for: 1h
        labels:
          severity: warning
          team: devops
        annotations:
          summary: "Backup {{ $labels.backup }} is stale"
          description: "Last successful backup was {{ $value | humanizeDuration }} ago"
      
      # Backup size anomaly
      - alert: BackupSizeAnomaly
        expr: |
          abs(
            backup_size_bytes - 
            avg_over_time(backup_size_bytes[7d])
          ) / avg_over_time(backup_size_bytes[7d]) > 0.5
        for: 30m
        labels:
          severity: warning
          team: devops
        annotations:
          summary: "Backup size anomaly for {{ $labels.backup }}"
          description: "Backup size differs significantly from average"
```

**Backup Verification Script:**
```bash
# Create verification script
cat > /opt/scripts/verify-backups.sh <<'EOF'
#!/bin/bash
set -euo pipefail

BACKUP_CHECKS=(
  "postgres:daily:s3://my-backups/postgres/"
  "mysql:daily:s3://my-backups/mysql/"
  "files:daily:s3://my-backups/restic/"
  "kubernetes:daily:s3://my-backups/kubernetes/"
)

echo "Verifying backups..."

for check in "${BACKUP_CHECKS[@]}"; do
  IFS=':' read -r name frequency location <<< "$check"
  
  # Check if backup exists from today
  today=$(date +%Y%m%d)
  if aws s3 ls "$location" | grep -q "$today"; then
    echo "✅ $name backup found for today"
    # Push success metric
    echo "backup_verified{backup=\"$name\"} 1" | \
      curl --data-binary @- http://prometheus-pushgateway:9091/metrics/job/backup_verification
  else
    echo "❌ $name backup NOT found for today!"
    # Push failure metric
    echo "backup_verified{backup=\"$name\"} 0" | \
      curl --data-binary @- http://prometheus-pushgateway:9091/metrics/job/backup_verification
    # Send alert
    curl -X POST http://alertmanager:9093/api/v1/alerts -d '[{
      "labels": {"alertname":"BackupMissing","backup":"'$name'","severity":"critical"},
      "annotations": {"summary":"Backup missing for '$name'"}
    }]'
  fi
done

echo "Backup verification complete"
EOF

chmod +x /opt/scripts/verify-backups.sh

# Run daily
(crontab -l 2>/dev/null; echo "0 10 * * * /opt/scripts/verify-backups.sh") | crontab -
```

**Verification:**
- [ ] Backup metrics being collected
- [ ] Alerts configured
- [ ] Verification script running
- [ ] Team receiving notifications
- [ ] Dashboard showing backup status

**If This Fails:**
→ Check Prometheus connectivity
→ Verify Pushgateway accessible
→ Test alert routing
→ Review metric format

---

### Step 6: Document and Test Recovery Procedures

**What:** Create detailed recovery runbooks and test them regularly

**How:**
Document step-by-step recovery procedures and perform DR drills.

**Code/Commands:**

**Database Recovery Runbook:**
```bash
cat > docs/runbooks/POSTGRES_RECOVERY.md <<'EOF'
# PostgreSQL Disaster Recovery Runbook

## Scenario 1: Point-in-Time Recovery

### When to Use
- Accidental data deletion
- Bad migration/deployment
- Data corruption

### Prerequisites
- Backup files accessible in S3
- Empty or corrupted database
- Downtime window approved

### Recovery Steps

1. **Stop Application**
   ```bash
   kubectl scale deployment myapp --replicas=0 -n production
   ```

2. **Download Latest Backup**
   ```bash
   BACKUP_FILE=$(aws s3 ls s3://my-backups/postgres/ | \
     grep 'backup_production' | sort | tail -1 | awk '{print $4}')
   
   aws s3 cp "s3://my-backups/postgres/$BACKUP_FILE" /tmp/
   ```

3. **Decrypt Backup**
   ```bash
   openssl enc -aes-256-cbc -d \
     -in "/tmp/$BACKUP_FILE" \
     -out "/tmp/backup.sql.gz" \
     -pass pass:"$BACKUP_ENCRYPTION_KEY"
   ```

4. **Stop PostgreSQL**
   ```bash
   sudo systemctl stop postgresql
   ```

5. **Clear Data Directory**
   ```bash
   sudo rm -rf /var/lib/postgresql/*/main/*
   ```

6. **Restore Base Backup**
   ```bash
   gunzip -c /tmp/backup.sql.gz | \
     sudo -u postgres psql production
   ```

7. **Restore WAL Files (for PITR)**
   ```bash
   # Copy WAL files to pg_wal directory
   aws s3 sync s3://my-backups/postgres/wal_archive/ \
     /var/lib/postgresql/*/main/pg_wal/
   ```

8. **Configure Recovery**
   ```bash
   cat > /var/lib/postgresql/*/main/recovery.conf <<EOF
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_time = '2024-10-26 10:00:00'
recovery_target_action = 'promote'
EOF
   ```

9. **Start PostgreSQL**
   ```bash
   sudo systemctl start postgresql
   ```

10. **Verify Recovery**
    ```bash
    psql -U postgres production -c "SELECT NOW(), pg_last_xact_replay_timestamp();"
    ```

11. **Start Application**
    ```bash
    kubectl scale deployment myapp --replicas=3 -n production
    ```

### Verification
- [ ] Database accessible
- [ ] Data integrity verified
- [ ] Application functioning
- [ ] No errors in logs

### Estimated Recovery Time
- Download backup: 5-10 minutes
- Restore database: 10-30 minutes
- WAL replay: 1-60 minutes (depends on recovery window)
- **Total RTO:** 20-100 minutes

### Rollback
If recovery fails:
1. Stop PostgreSQL
2. Clear data directory
3. Try previous backup
4. Escalate to database team
EOF
```

**Kubernetes Disaster Recovery:**
```bash
cat > docs/runbooks/KUBERNETES_RECOVERY.md <<'EOF'
# Kubernetes Cluster Disaster Recovery

## Scenario: Complete Cluster Loss

### Prerequisites
- Velero backups exist
- New Kubernetes cluster provisioned
- Access to backup storage

### Recovery Steps

1. **Install Velero on New Cluster**
   ```bash
   velero install \
     --provider aws \
     --plugins velero/velero-plugin-for-aws:v1.8.0 \
     --bucket velero-backups \
     --backup-location-config region=us-east-1 \
     --secret-file ./credentials-velero
   ```

2. **List Available Backups**
   ```bash
   velero backup get
   ```

3. **Restore Latest Backup**
   ```bash
   velero restore create --from-backup production-backup-20241026
   ```

4. **Monitor Restore Progress**
   ```bash
   velero restore describe <restore-name>
   velero restore logs <restore-name>
   ```

5. **Verify Resources**
   ```bash
   kubectl get all --all-namespaces
   kubectl get pv,pvc --all-namespaces
   ```

6. **Update DNS/Load Balancer**
   ```bash
   # Point DNS to new cluster
   # Update load balancer target groups
   ```

7. **Verify Applications**
   ```bash
   kubectl logs -f deployment/myapp -n production
   curl https://example.com/health
   ```

### Estimated Recovery Time
- Velero setup: 10 minutes
- Restore execution: 30-60 minutes
- DNS propagation: 5-60 minutes
- **Total RTO:** 45-130 minutes
EOF
```

**DR Testing Schedule:**
```bash
cat > docs/DR_TESTING_SCHEDULE.md <<'EOF'
# Disaster Recovery Testing Schedule

## Quarterly Full DR Test
**Frequency:** Every 3 months  
**Duration:** 4 hours  
**Team:** DevOps + Dev + QA  

### Test Scenarios
1. Database corruption recovery
2. Complete cluster rebuild
3. Regional failover
4. Ransomware recovery (from immutable backup)

### Success Criteria
- RPO < 1 hour (max 1 hour data loss)
- RTO < 2 hours (restored in under 2 hours)
- All applications functional
- Data integrity verified

## Monthly Backup Verification
**Frequency:** Monthly  
**Duration:** 1 hour  

### Tests
1. Restore database to staging
2. Verify file backup integrity
3. Test configuration restore
4. Validate backup encryption

## Weekly Monitoring
**Frequency:** Weekly  
**Duration:** 30 minutes  

### Checks
- Backup success rates
- Backup sizes trending
- Storage capacity
- Alert functionality

## Testing Log Template
```
Date: YYYY-MM-DD
Test Type: [Full DR / Backup Verification / Monitoring]
Participants: [Names]
Scenarios Tested: [List]
Results:
  - Scenario 1: [PASS/FAIL] - Duration: XX minutes
  - Scenario 2: [PASS/FAIL] - Duration: XX minutes
Issues Identified: [List]
Action Items: [List with owners]
Next Test Date: YYYY-MM-DD
```
EOF
```

**Verification:**
- [ ] Recovery runbooks created
- [ ] DR testing scheduled
- [ ] Team trained on procedures
- [ ] Recovery tested successfully
- [ ] Documentation up to date

**If This Fails:**
→ Start with simple restore tests
→ Document actual steps during test
→ Update procedures based on findings
→ Train team on updated procedures

---

### Step 7: Implement Backup Security and Compliance

**What:** Secure backups and meet compliance requirements

**How:**
Encrypt backups, implement access controls, and audit logging.

**Code/Commands:**

**Backup Encryption:**
```bash
# Generate encryption key
openssl rand -base64 32 > /etc/backup-key

# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 backup.sql

# Encrypt with OpenSSL
openssl enc -aes-256-cbc -salt \
  -in backup.sql \
  -out backup.sql.enc \
  -pass file:/etc/backup-key
```

**S3 Bucket Security:**
```bash
# Enable encryption at rest
aws s3api put-bucket-encryption \
  --bucket my-backups \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789:key/abc-123"
      }
    }]
  }'

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-backups \
  --versioning-configuration Status=Enabled

# Enable MFA delete (extra protection)
aws s3api put-bucket-versioning \
  --bucket my-backups \
  --versioning-configuration Status=Enabled,MFADelete=Enabled \
  --mfa "arn:aws:iam::123456789:mfa/root-account-mfa-device 123456"

# Block public access
aws s3api put-public-access-block \
  --bucket my-backups \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Enable logging
aws s3api put-bucket-logging \
  --bucket my-backups \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "my-logs-bucket",
      "TargetPrefix": "backup-logs/"
    }
  }'
```

**Immutable Backups (Ransomware Protection):**
```bash
# Enable Object Lock (prevents deletion for retention period)
aws s3api put-object-lock-configuration \
  --bucket my-backups \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Days": 90
      }
    }
  }'

# Alternatively, use Glacier Vault Lock
aws glacier initiate-vault-lock \
  --vault-name my-backup-vault \
  --policy '{
    "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Deny\",\"Principal\":\"*\",\"Action\":\"glacier:DeleteArchive\",\"Resource\":\"arn:aws:glacier:us-east-1:123456789:vaults/my-backup-vault\",\"Condition\":{\"NumericLessThan\":{\"glacier:ArchiveAgeInDays\":\"90\"}}}]}"
  }'
```

**Access Control and Audit:**
```bash
# IAM policy for backup user (least privilege)
cat > backup-user-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::my-backups/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::my-backups"
    },
    {
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
      ],
      "Resource": "arn:aws:s3:::my-backups/*"
    }
  ]
}
EOF

aws iam put-user-policy \
  --user-name backup-user \
  --policy-name BackupWriteOnly \
  --policy-document file://backup-user-policy.json

# Enable CloudTrail for audit
aws cloudtrail create-trail \
  --name backup-audit-trail \
  --s3-bucket-name my-audit-logs \
  --include-global-service-events \
  --is-multi-region-trail

aws cloudtrail start-logging --name backup-audit-trail
```

**Compliance Checklist:**
```bash
cat > COMPLIANCE_CHECKLIST.md <<'EOF'
# Backup Compliance Checklist

## Encryption
- [ ] Backups encrypted at rest (AES-256)
- [ ] Backups encrypted in transit (TLS 1.3)
- [ ] Key management documented
- [ ] Keys rotated regularly

## Access Control
- [ ] Least privilege access
- [ ] MFA required for backup deletion
- [ ] Service accounts for automation only
- [ ] Regular access reviews

## Retention
- [ ] Retention policy documented
- [ ] Retention meets regulatory requirements
  - [ ] SOX: 7 years
  - [ ] GDPR: Per data subject rights
  - [ ] HIPAA: 6 years
  - [ ] Industry-specific: ____ years
- [ ] Automated retention enforcement

## Immutability
- [ ] Backups protected from deletion (Object Lock/Vault Lock)
- [ ] Ransomware protection enabled
- [ ] Air-gapped/offline copies exist

## Testing
- [ ] Quarterly DR tests
- [ ] Monthly restore tests
- [ ] Test results documented
- [ ] Procedures updated based on tests

## Monitoring
- [ ] Backup success/failure alerts
- [ ] Backup freshness monitoring
- [ ] Storage capacity monitoring
- [ ] Audit log review

## Documentation
- [ ] Recovery runbooks current
- [ ] Team training completed
- [ ] Contact lists updated
- [ ] Compliance attestation signed
EOF
```

**Verification:**
- [ ] Backups encrypted
- [ ] Access controls implemented
- [ ] Immutability configured
- [ ] Audit logging enabled
- [ ] Compliance requirements met

**If This Fails:**
→ Review compliance requirements with legal
→ Implement controls incrementally
→ Document exceptions with risk acceptance
→ Plan remediation timeline

---

### Step 8: Create Disaster Recovery Dashboard

**What:** Centralized view of backup and DR status

**How:**
Build Grafana dashboard showing backup health and recovery readiness.

**Code/Commands:**

**Backup Dashboard (Grafana):**
```json
{
  "dashboard": {
    "title": "Backup & Disaster Recovery Status",
    "panels": [
      {
        "title": "Backup Success Rate (24h)",
        "targets": [{
          "expr": "sum(rate(backup_success[24h])) / sum(rate(backup_attempts[24h]))"
        }],
        "type": "singlestat",
        "thresholds": "0.95,0.99"
      },
      {
        "title": "Backup Freshness",
        "targets": [{
          "expr": "(time() - backup_last_success_timestamp) / 3600",
          "legendFormat": "{{ backup }}"
        }],
        "type": "graph"
      },
      {
        "title": "Backup Size Trend",
        "targets": [{
          "expr": "backup_size_bytes",
          "legendFormat": "{{ backup }}"
        }],
        "type": "graph"
      },
      {
        "title": "Storage Usage",
        "targets": [{
          "expr": "sum(backup_size_bytes) by (location)"
        }],
        "type": "piechart"
      },
      {
        "title": "Last Successful Backups",
        "targets": [{
          "expr": "backup_last_success_timestamp"
        }],
        "type": "table",
        "transform": "timeseries_to_rows"
      },
      {
        "title": "DR Test Results",
        "targets": [{
          "expr": "dr_test_success"
        }],
        "type": "table"
      }
    ]
  }
}
```

**Backup Status Script:**
```bash
# Create comprehensive status report
cat > /opt/scripts/backup-status-report.sh <<'EOF'
#!/bin/bash
set -euo pipefail

echo "=== Backup & DR Status Report ==="
echo "Generated: $(date)"
echo ""

# Check backup freshness
echo "## Backup Freshness"
for backup in postgres mysql files k8s; do
  last_backup=$(aws s3 ls "s3://my-backups/$backup/" | \
    grep -v "/$" | tail -1 | awk '{print $1, $2}')
  
  if [ -n "$last_backup" ]; then
    age=$(($(date +%s) - $(date -d "$last_backup" +%s)))
    hours=$((age / 3600))
    
    if [ $hours -lt 24 ]; then
      status="✅"
    elif [ $hours -lt 48 ]; then
      status="⚠️"
    else
      status="❌"
    fi
    
    echo "$status $backup: $hours hours ago ($last_backup)"
  else
    echo "❌ $backup: No backups found!"
  fi
done

echo ""
echo "## Storage Usage"
aws s3 ls s3://my-backups/ | \
  awk '{sum+=$3} END {print "Total: " sum/1024/1024/1024 " GB"}'

echo ""
echo "## Last DR Test"
if [ -f /var/log/dr-test-last.txt ]; then
  cat /var/log/dr-test-last.txt
else
  echo "❌ No DR test record found"
fi

echo ""
echo "## Recent Backup Failures"
journalctl -u backup-* --since "24 hours ago" --grep "ERROR" | tail -10

echo ""
echo "=== End of Report ==="
EOF

chmod +x /opt/scripts/backup-status-report.sh

# Email report weekly
(crontab -l 2>/dev/null; echo "0 9 * * MON /opt/scripts/backup-status-report.sh | mail -s 'Weekly Backup Report' team@example.com") | crontab -
```

**Verification:**
- [ ] Dashboard accessible
- [ ] All metrics displaying
- [ ] Status report generating
- [ ] Team has access
- [ ] Alerts configured

**If This Fails:**
→ Check Grafana datasource
→ Verify metrics being collected
→ Test queries in Prometheus
→ Review dashboard permissions

---

## Verification Checklist

- [ ] RPO/RTO defined
- [ ] Database backups automated
- [ ] File backups automated
- [ ] Infrastructure backups configured
- [ ] Backups encrypted
- [ ] Backups monitored
- [ ] Recovery procedures documented
- [ ] DR testing scheduled
- [ ] Team trained
- [ ] Compliance requirements met

---

## Common Issues & Solutions

### Issue: Backup Taking Too Long

**Symptoms:**
- Backup exceeds time window
- Impacts production performance
- Backup jobs queuing up

**Solution:**
```bash
# Optimize PostgreSQL backup
pg_dump --jobs=4 \  # Parallel dump
  --format=directory \
  --file=/backup \
  production

# Use incremental backups (restic)
restic backup / --parent <previous-backup-id>

# Schedule during off-peak hours
# Update cron: 0 3 * * * (3 AM instead of peak)

# Increase compression level
gzip -1  # Fast compression (instead of -9)
```

**Prevention:**
- Benchmark backup duration
- Use incremental backups
- Optimize backup schedule
- Scale backup infrastructure

---

### Issue: Restore Fails

**Symptoms:**
- Backup file corrupted
- Incompatible versions
- Missing dependencies

**Solution:**
```bash
# Verify backup integrity
restic check
pg_restore --list backup.dump  # Verify PostgreSQL backup

# Check backup file
gunzip -t backup.sql.gz
tar -tzf backup.tar.gz

# Use earlier backup version
aws s3api list-object-versions \
  --bucket my-backups \
  --prefix postgres/backup.sql.gz

# Restore from specific version
aws s3api get-object \
  --bucket my-backups \
  --key postgres/backup.sql.gz \
  --version-id <version-id> \
  backup.sql.gz
```

**Prevention:**
- Regular restore testing
- Verify backups after creation
- Keep multiple backup versions
- Test restoration procedures

---

## Best Practices

### DO:
✅ **Define clear RPO/RTO** - Understand business requirements  
✅ **Automate everything** - Manual backups fail  
✅ **Encrypt backups** - Protect sensitive data  
✅ **Test restores regularly** - Backups are useless if restore fails  
✅ **Monitor backup health** - Know when backups fail  
✅ **Use immutable storage** - Protect against ransomware  
✅ **Document procedures** - Enable fast recovery  
✅ **Implement 3-2-1 rule** - 3 copies, 2 media types, 1 offsite  
✅ **Version control infrastructure** - IaC is your infrastructure backup  
✅ **Train the team** - Everyone should know recovery procedures

### DON'T:
❌ **Skip testing** - Untested backups are not backups  
❌ **Store backups only locally** - Regional disasters happen  
❌ **Use same credentials** - Compromised accounts affect backups  
❌ **Ignore backup failures** - Fix immediately  
❌ **Over-retain everything** - Balance cost and compliance  
❌ **Forget about secrets** - Back up safely or recreate  
❌ **Assume backups work** - Verify and monitor  
❌ **Skip encryption** - Data breaches include backup data  
❌ **Make backups deletable** - Immutability protects against attacks  
❌ **Neglect documentation** - Recovery requires clear procedures

---

## Related Workflows

**Prerequisites:**
- [Infrastructure as Code with Terraform](./infrastructure_as_code_terraform.md) - Version control infrastructure
- [Kubernetes Deployment](./kubernetes_deployment.md) - Cluster backup targets

**Next Steps:**
- [Incident Response Workflow](./incident_response_workflow.md) - Use backups during incidents
- [Security Audit Logging](../security/security_audit_logging.md) - Audit backup access
- [Cloud Provider Setup](./cloud_provider_setup.md) - Cloud-native backup services

**Alternatives:**
- **Veeam** - Enterprise backup solution
- **Commvault** - Enterprise data protection
- **AWS Backup** - AWS-native backup service
- **Azure Backup** - Azure-native backup
- **Google Cloud Backup** - GCP-native backup

---

## Tags
`devops` `backup` `disaster-recovery` `dr` `business-continuity` `data-protection` `rpo` `rto` `restic` `velero` `compliance` `ransomware-protection`
