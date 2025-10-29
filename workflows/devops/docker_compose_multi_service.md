# Docker Compose Multi-Service

**ID:** devops-006  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for orchestrating multiple Docker containers as a cohesive application stack using Docker Compose

**Why:** Modern applications often consist of multiple services (web app, database, cache, queue, etc.). Docker Compose enables defining, configuring, and managing these services together, ensuring consistent environments across development, testing, and production.

**When to use:**
- Local development with multiple dependent services
- Microservices architecture
- Full-stack applications (frontend, backend, database)
- Applications with background workers and message queues
- Integration testing environments
- Development environment standardization across team

---

## Prerequisites

**Required:**
- [ ] Docker installed and running
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Understanding of individual containers (see Docker Container Creation)
- [ ] Application architecture documented

**Check before starting:**
```bash
# Verify Docker Compose
docker-compose --version
# Expected: Docker Compose version v2.20.0 or higher

# Check Docker daemon
docker ps

# Verify Docker network capabilities
docker network ls

# Check available resources
docker system df

# Ensure ports are available
netstat -tuln | grep -E ':(5432|6379|3306|8080|3000)'
```

---

## Implementation Steps

### Step 1: Design Service Architecture

**What:** Map out all services, their relationships, dependencies, and data flows

**How:**
Create an architecture diagram showing how services communicate, what they depend on, and what data they share.

**Code/Commands:**
```bash
# Document your architecture
cat > ARCHITECTURE.md <<'EOF'
# Multi-Service Architecture

## Services Overview

### Web Application (app)
- **Technology:** Python FastAPI
- **Port:** 8000 (external) → 8000 (internal)
- **Dependencies:** PostgreSQL, Redis, RabbitMQ
- **Purpose:** REST API serving client requests
- **Health:** GET /health

### Database (db)
- **Technology:** PostgreSQL 15
- **Port:** 5432 (internal only)
- **Purpose:** Primary data store
- **Volumes:** Persistent data storage
- **Health:** pg_isready

### Cache (redis)
- **Technology:** Redis 7
- **Port:** 6379 (internal only)
- **Purpose:** Session storage, caching
- **Health:** redis-cli ping

### Message Queue (rabbitmq)
- **Technology:** RabbitMQ 3
- **Ports:** 5672 (AMQP), 15672 (Management UI)
- **Purpose:** Async task queue
- **Health:** Management API

### Background Worker (worker)
- **Technology:** Python Celery
- **Dependencies:** RabbitMQ, Redis, PostgreSQL
- **Purpose:** Process async tasks
- **Scaling:** Can run multiple instances

### Frontend (frontend)
- **Technology:** React (Nginx serving static files)
- **Port:** 3000 (external) → 80 (internal)
- **Dependencies:** Web Application API
- **Purpose:** User interface

## Service Communication

```
┌─────────┐
│ Frontend│ ──HTTP──> │  App   │
└─────────┘           │ (API)  │
                      └────┬───┘
                           │
       ┌───────────────────┼──────────────────┐
       │                   │                  │
       ▼                   ▼                  ▼
  ┌────────┐         ┌─────────┐       ┌──────────┐
  │  Redis │         │   DB    │       │ RabbitMQ │
  │ (Cache)│         │(Postgres)│      │ (Queue)  │
  └────────┘         └─────────┘       └─────┬────┘
                                             │
                                             ▼
                                        ┌────────┐
                                        │ Worker │
                                        └────────┘
```

## Data Flow
1. User request → Frontend
2. Frontend → API (HTTP)
3. API → Database (queries)
4. API → Redis (cache read/write)
5. API → RabbitMQ (publish tasks)
6. Worker → RabbitMQ (consume tasks)
7. Worker → Database (update results)

## Ports Summary
- 3000: Frontend (public)
- 8000: API (public)
- 5432: PostgreSQL (internal)
- 6379: Redis (internal)
- 5672: RabbitMQ AMQP (internal)
- 15672: RabbitMQ UI (optional public)

## Volumes
- postgres-data: Database persistence
- redis-data: Redis persistence (optional)
- rabbitmq-data: Queue persistence
- app-logs: Application logs
EOF

# Create service dependency graph
cat > service-dependencies.txt <<'EOF'
frontend -> app
app -> db
app -> redis
app -> rabbitmq
worker -> rabbitmq
worker -> redis
worker -> db
EOF
```

**Verification:**
- [ ] All services identified
- [ ] Dependencies mapped
- [ ] Port assignments documented
- [ ] Data flows understood
- [ ] Architecture diagram created

**If This Fails:**
→ Start with core services (app + database)
→ Add supporting services incrementally
→ Review similar application architectures
→ Consult with team about requirements

---

### Step 2: Create Docker Compose File

**What:** Define all services in a docker-compose.yml file

**How:**
Write a compose file that declares each service, its configuration, networking, and dependencies.

**Code/Commands:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: myapp-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-myapp}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_HOST_AUTH_METHOD: ${POSTGRES_HOST_AUTH_METHOD:-scram-sha-256}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    ports:
      - "5432:5432"  # Expose for dev tools (remove in prod)
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-changeme}
    volumes:
      - redis-data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # RabbitMQ Message Queue
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: myapp-rabbitmq
    restart: unless-stopped
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER:-admin}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD:-changeme}
      RABBITMQ_DEFAULT_VHOST: /
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Management UI
    networks:
      - backend
    healthcheck:
      test: rabbitmq-diagnostics -q ping
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Web Application
  app:
    build:
      context: ./app
      dockerfile: Dockerfile
      args:
        - BUILD_ENV=development
    image: myapp:latest
    container_name: myapp-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-changeme}@db:5432/${POSTGRES_DB:-myapp}
      - REDIS_URL=redis://default:${REDIS_PASSWORD:-changeme}@redis:6379/0
      - RABBITMQ_URL=amqp://${RABBITMQ_USER:-admin}:${RABBITMQ_PASSWORD:-changeme}@rabbitmq:5672/
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=development
    volumes:
      - ./app:/app:ro  # Read-only for development hot reload
      - app-logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    networks:
      - backend
      - frontend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s

  # Background Worker
  worker:
    build:
      context: ./app
      dockerfile: Dockerfile
    image: myapp:latest
    container_name: myapp-worker
    restart: unless-stopped
    command: celery -A tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-changeme}@db:5432/${POSTGRES_DB:-myapp}
      - REDIS_URL=redis://default:${REDIS_PASSWORD:-changeme}@redis:6379/0
      - RABBITMQ_URL=amqp://${RABBITMQ_USER:-admin}:${RABBITMQ_PASSWORD:-changeme}@rabbitmq:5672/
    volumes:
      - ./app:/app:ro
      - worker-logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    networks:
      - backend
    deploy:
      replicas: 2  # Run 2 worker instances

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    image: myapp-frontend:latest
    container_name: myapp-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - app
    networks:
      - frontend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:80/"]
      interval: 30s
      timeout: 3s
      retries: 3

# Networks
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

# Volumes
volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  rabbitmq-data:
    driver: local
  app-logs:
    driver: local
  worker-logs:
    driver: local
```

**Create .env file:**
```bash
cat > .env <<'EOF'
# Database
POSTGRES_DB=myapp
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_db_password_here

# Redis
REDIS_PASSWORD=secure_redis_password_here

# RabbitMQ
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=secure_rabbitmq_password_here

# Application
SECRET_KEY=your-secret-key-min-32-chars
ENVIRONMENT=development

# Optional: Resource Limits
POSTGRES_MAX_CONNECTIONS=100
REDIS_MAXMEMORY=256mb
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

**Verification:**
- [ ] docker-compose.yml is valid: `docker-compose config`
- [ ] All services defined
- [ ] Networks configured
- [ ] Volumes declared
- [ ] Environment variables set
- [ ] Dependencies specified

**If This Fails:**
→ Validate YAML syntax: `docker-compose config`
→ Check for indentation errors
→ Verify image names exist
→ Review Docker Compose documentation for version

---

### Step 3: Configure Service Networking

**What:** Set up proper network isolation and service discovery

**How:**
Use Docker networks to control which services can communicate with each other.

**Code/Commands:**
```yaml
# Network configuration explained

# Option 1: Separate frontend and backend networks (more secure)
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16

# Services configuration
services:
  app:
    networks:
      - frontend  # Accessible from frontend
      - backend   # Can access backend services
  
  db:
    networks:
      - backend   # Only accessible to backend services
  
  frontend:
    networks:
      - frontend  # Can only reach app, not db directly

# Option 2: Single network (simpler, less isolation)
networks:
  app-network:
    driver: bridge

# Option 3: Use existing network
networks:
  existing-network:
    external: true
    name: my-existing-network
```

```bash
# Test network connectivity between services
docker-compose exec app ping -c 3 db
docker-compose exec app ping -c 3 redis

# Check network configuration
docker network ls
docker network inspect myapp_backend

# View service DNS resolution
docker-compose exec app nslookup db
docker-compose exec app nslookup redis

# Test service communication
docker-compose exec app curl http://db:5432
docker-compose exec app redis-cli -h redis -a password ping
```

**Verification:**
- [ ] Services can reach their dependencies
- [ ] Services cannot reach isolated services
- [ ] DNS resolution working (service names resolve)
- [ ] Network segmentation correct
- [ ] No port conflicts

**If This Fails:**
→ Check networks are created: `docker network ls`
→ Verify services are on correct networks
→ Ensure no firewall blocking
→ Review service names (must match compose file)

---

### Step 4: Manage Volumes and Data Persistence

**What:** Configure data persistence for stateful services

**How:**
Use named volumes for production data and bind mounts for development.

**Code/Commands:**
```yaml
# Volume strategies

volumes:
  # Named volumes (production)
  postgres-data:
    driver: local
    driver_opts:
      type: none
      device: /data/postgres  # Custom host path
      o: bind

  # Anonymous volume (temporary)
  redis-data:

  # External volume (managed separately)
  shared-storage:
    external: true
    name: production-shared-storage

# Service volume mounts
services:
  db:
    volumes:
      # Named volume for data persistence
      - postgres-data:/var/lib/postgresql/data
      
      # Bind mount for initialization scripts
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
      
      # tmpfs mount for temporary files
      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 100M
  
  app:
    volumes:
      # Read-only code mount (development)
      - ./app:/app:ro
      
      # Read-write logs
      - app-logs:/app/logs
      
      # Cached mount for better performance on macOS
      - ./app/node_modules:/app/node_modules:cached
```

```bash
# Volume management commands

# List volumes
docker volume ls

# Inspect volume
docker volume inspect myapp_postgres-data

# Create volume manually
docker volume create --name myapp-shared-data

# Backup volume
docker run --rm \
  -v myapp_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz /data

# Restore volume
docker run --rm \
  -v myapp_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine sh -c "cd /data && tar xzf /backup/postgres-backup-20241026.tar.gz --strip 1"

# Remove unused volumes
docker volume prune -f

# Create backup script
cat > backup-volumes.sh <<'EOF'
#!/bin/bash
set -euo pipefail

BACKUP_DIR="./backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "Backing up volumes..."

# Backup PostgreSQL
docker-compose exec -T db pg_dump -U postgres myapp \
  | gzip > "$BACKUP_DIR/postgres.sql.gz"

# Backup Redis (if using persistence)
docker-compose exec redis redis-cli --rdb /tmp/dump.rdb save
docker cp myapp-redis:/tmp/dump.rdb "$BACKUP_DIR/redis.rdb"

echo "✅ Backup complete: $BACKUP_DIR"
EOF

chmod +x backup-volumes.sh
```

**Verification:**
- [ ] Volumes created and mounted
- [ ] Data persists after container restart
- [ ] Backup/restore procedures work
- [ ] File permissions correct
- [ ] Sufficient disk space

**If This Fails:**
→ Check volume paths exist
→ Verify permissions on host directories
→ Ensure sufficient disk space
→ Review volume driver documentation

---

### Step 5: Handle Service Dependencies and Startup Order

**What:** Ensure services start in the correct order and wait for dependencies to be ready

**How:**
Use depends_on with health checks to orchestrate startup sequence.

**Code/Commands:**
```yaml
# Advanced dependency configuration

services:
  db:
    # Database always starts first
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
  
  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
  
  app:
    depends_on:
      db:
        condition: service_healthy  # Wait for db to be healthy
      redis:
        condition: service_healthy  # Wait for redis to be healthy
    
    # Additional startup delay if needed
    command: >
      sh -c "
        echo 'Waiting for services...'
        sleep 5
        python manage.py migrate
        python manage.py collectstatic --noinput
        uvicorn main:app --host 0.0.0.0 --port 8000
      "
  
  worker:
    depends_on:
      app:
        condition: service_started  # Just wait for app to start
      rabbitmq:
        condition: service_healthy
    
    # Custom wait script
    command: >
      sh -c "
        ./wait-for-it.sh db:5432 --timeout=60
        ./wait-for-it.sh rabbitmq:5672 --timeout=60
        celery -A tasks worker --loglevel=info
      "
```

```bash
# Create wait-for-it script (more reliable than depends_on)
cat > wait-for-it.sh <<'EOF'
#!/bin/bash
# wait-for-it.sh - Wait for service to be available

HOST=$1
PORT=$2
TIMEOUT=${3:-30}

echo "Waiting for $HOST:$PORT..."

for i in $(seq 1 $TIMEOUT); do
  nc -z $HOST $PORT && echo "✅ $HOST:$PORT is available" && exit 0
  echo "Attempt $i/$TIMEOUT: $HOST:$PORT not ready yet..."
  sleep 1
done

echo "❌ Timeout waiting for $HOST:$PORT"
exit 1
EOF

chmod +x wait-for-it.sh

# Test startup order
docker-compose up -d
docker-compose logs -f

# Check which services are running
docker-compose ps

# Restart in correct order
docker-compose down
docker-compose up -d --build
```

**Verification:**
- [ ] Services start in correct order
- [ ] Health checks passing
- [ ] No race conditions
- [ ] Dependencies available before dependents start
- [ ] Logs show successful startup sequence

**If This Fails:**
→ Add explicit wait scripts
→ Increase health check start_period
→ Use docker-compose up --wait
→ Check logs for specific startup errors

---

### Step 6: Configure Environment Variables and Secrets

**What:** Properly manage configuration and sensitive data

**How:**
Use environment files, avoid hardcoding secrets, and prepare for different environments.

**Code/Commands:**
```bash
# Create environment files for different stages

# .env.development
cat > .env.development <<'EOF'
POSTGRES_DB=myapp_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password
REDIS_PASSWORD=dev_redis_pass
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug
EOF

# .env.staging
cat > .env.staging <<'EOF'
POSTGRES_DB=myapp_staging
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${STAGING_DB_PASSWORD}
REDIS_PASSWORD=${STAGING_REDIS_PASSWORD}
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=info
EOF

# .env.production
cat > .env.production <<'EOF'
POSTGRES_DB=myapp_prod
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${PRODUCTION_DB_PASSWORD}
REDIS_PASSWORD=${PRODUCTION_REDIS_PASSWORD}
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning
EOF

# Using different env files
docker-compose --env-file .env.development up -d
docker-compose --env-file .env.production up -d

# Override compose file for production
cat > docker-compose.prod.yml <<'EOF'
version: '3.8'

services:
  app:
    restart: always
    environment:
      - WORKERS=4
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
  
  db:
    restart: always
    # Don't expose port in production
    ports: []
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  redis:
    restart: always
    # Use persistent storage in production
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
EOF

# Use with override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Secret management with Docker secrets (Swarm mode)
echo "my-secret-password" | docker secret create db_password -

cat > docker-compose.secrets.yml <<'EOF'
version: '3.8'

services:
  db:
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    external: true
EOF
```

**Verification:**
- [ ] Environment variables loaded correctly
- [ ] No secrets in git repository
- [ ] Different configs for different environments
- [ ] .env files in .gitignore
- [ ] Production uses secure secret management

**If This Fails:**
→ Check .env file syntax
→ Verify environment variable interpolation
→ Ensure .env file is in same directory as compose file
→ Review logs for missing environment variables

---

### Step 7: Start, Stop, and Manage Services

**What:** Learn all essential docker-compose commands for day-to-day operations

**How:**
Master compose CLI for efficient service management.

**Code/Commands:**
```bash
# === Starting Services ===

# Start all services in background
docker-compose up -d

# Start specific services
docker-compose up -d app db redis

# Start with build
docker-compose up -d --build

# Start with force recreate
docker-compose up -d --force-recreate

# Start and show logs
docker-compose up

# === Stopping Services ===

# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop app

# Stop and remove containers
docker-compose down

# Stop, remove containers and volumes
docker-compose down -v

# Stop, remove everything including images
docker-compose down --rmi all -v

# === Viewing Status ===

# List services
docker-compose ps

# View service details
docker-compose ps app

# Show logs
docker-compose logs

# Follow logs
docker-compose logs -f app

# Show last 100 lines
docker-compose logs --tail=100 app

# Show logs with timestamps
docker-compose logs -f --timestamps

# === Service Management ===

# Restart service
docker-compose restart app

# Restart all services
docker-compose restart

# Pause services (suspend)
docker-compose pause

# Unpause services
docker-compose unpause

# === Scaling ===

# Scale worker to 5 instances
docker-compose up -d --scale worker=5

# Scale multiple services
docker-compose up -d --scale worker=3 --scale app=2

# === Execution ===

# Execute command in running service
docker-compose exec app python manage.py migrate

# Execute with different user
docker-compose exec -u root app apt-get update

# Execute in one-off container
docker-compose run --rm app python manage.py createsuperuser

# === Building ===

# Build all images
docker-compose build

# Build specific service
docker-compose build app

# Build without cache
docker-compose build --no-cache

# Build with arguments
docker-compose build --build-arg VERSION=1.0.0

# === Validation ===

# Validate compose file
docker-compose config

# Show resolved configuration
docker-compose config --services

# Show compose file with variables resolved
docker-compose config --resolve-image-digests

# === Resource Usage ===

# Show resource usage
docker-compose top

# Show container stats
docker stats $(docker-compose ps -q)

# === Create management script ===
cat > manage.sh <<'EOF'
#!/bin/bash
set -euo pipefail

CMD="${1:-help}"

case "$CMD" in
  start)
    echo "Starting all services..."
    docker-compose up -d
    docker-compose ps
    ;;
  stop)
    echo "Stopping all services..."
    docker-compose stop
    ;;
  restart)
    echo "Restarting all services..."
    docker-compose restart
    ;;
  logs)
    SERVICE="${2:-}"
    docker-compose logs -f $SERVICE
    ;;
  shell)
    SERVICE="${2:-app}"
    docker-compose exec $SERVICE /bin/bash
    ;;
  rebuild)
    echo "Rebuilding and restarting..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    ;;
  clean)
    echo "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    ;;
  status)
    docker-compose ps
    echo ""
    echo "Resource usage:"
    docker stats --no-stream $(docker-compose ps -q)
    ;;
  migrate)
    docker-compose exec app python manage.py migrate
    ;;
  test)
    docker-compose exec app pytest
    ;;
  *)
    echo "Usage: ./manage.sh {start|stop|restart|logs|shell|rebuild|clean|status|migrate|test}"
    exit 1
    ;;
esac
EOF

chmod +x manage.sh
```

**Verification:**
- [ ] Services start successfully
- [ ] Can view logs
- [ ] Can execute commands in containers
- [ ] Scaling works
- [ ] Clean shutdown possible

**If This Fails:**
→ Check docker-compose.yml syntax
→ Verify Docker daemon is running
→ Ensure ports aren't already in use
→ Review logs for specific errors

---

### Step 8: Production Deployment Considerations

**What:** Prepare compose configuration for production deployment

**How:**
Add monitoring, logging, resource limits, and high availability configurations.

**Code/Commands:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    # Use specific version tag, not 'latest'
    image: myregistry.com/myapp:1.2.3
    restart: always
    
    # Resource limits
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        order: start-first
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service,environment"
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Don't mount code in production
    volumes:
      - app-logs:/app/logs:rw
      # No code mount for production
  
  db:
    restart: always
    # Don't expose ports externally
    ports: []
    
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    
    # Production backup configuration
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - /backups/postgres:/backups:ro
    
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=1GB
      -c effective_cache_size=3GB
      -c maintenance_work_mem=256MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1

  # Add monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    networks:
      - monitoring
  
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SERVER_ROOT_URL=https://monitoring.example.com
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus

  # Reverse proxy
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx-logs:/var/log/nginx
    networks:
      - frontend
    depends_on:
      - app

volumes:
  prometheus-data:
  grafana-data:
  nginx-logs:

networks:
  monitoring:
    driver: bridge
```

```bash
# Production deployment script
cat > deploy-prod.sh <<'EOF'
#!/bin/bash
set -euo pipefail

echo "🚀 Production Deployment Starting..."

# Load production environment
export $(cat .env.production | xargs)

# Pull latest images
echo "📦 Pulling images..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# Run database migrations
echo "🔄 Running migrations..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm app python manage.py migrate

# Backup before deployment
echo "💾 Creating backup..."
./backup-volumes.sh

# Deploy with zero downtime
echo "🔄 Rolling update..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --build app

# Wait for health checks
echo "🏥 Waiting for health checks..."
sleep 30

# Verify deployment
echo "✅ Verifying deployment..."
curl -f http://localhost:8000/health || {
  echo "❌ Health check failed! Rolling back..."
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml rollback
  exit 1
}

echo "✅ Deployment successful!"
docker-compose ps
EOF

chmod +x deploy-prod.sh

# Create monitoring configuration
cat > prometheus.yml <<'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'app'
    static_configs:
      - targets: ['app:8000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
```

**Verification:**
- [ ] Resource limits enforced
- [ ] Health checks configured
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] High availability (multiple replicas)
- [ ] Automated backups
- [ ] Zero-downtime deployment possible

**If This Fails:**
→ Test in staging environment first
→ Review resource limits
→ Check monitoring endpoints
→ Verify health check accuracy

---

## Verification Checklist

After completing this workflow:

- [ ] All services defined in docker-compose.yml
- [ ] Services start in correct order
- [ ] Health checks passing
- [ ] Service communication working
- [ ] Data persists across restarts
- [ ] Logs accessible
- [ ] Resource limits set (production)
- [ ] Monitoring configured (production)
- [ ] Backup procedures documented
- [ ] Team can run locally with single command

---

## Common Issues & Solutions

### Issue: Port Already in Use

**Symptoms:**
- "Bind for 0.0.0.0:5432 failed: port is already allocated"
- Service fails to start

**Solution:**
```bash
# Find what's using the port
lsof -i :5432
# or
netstat -tuln | grep 5432

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use different external port
```

**Prevention:**
- Document required ports
- Use non-standard external ports
- Check for conflicts before starting

---

### Issue: Services Can't Communicate

**Symptoms:**
- "Connection refused" errors
- Services timeout connecting to each other

**Solution:**
```bash
# Check if services are on same network
docker network inspect myapp_backend

# Verify service names resolve
docker-compose exec app ping db

# Check service is actually listening
docker-compose exec db netstat -tuln | grep 5432

# Use correct service name (from compose file)
# Wrong: localhost, 127.0.0.1
# Correct: db, redis, rabbitmq
```

**Prevention:**
- Use service names from compose file
- Ensure services are on same network
- Don't use localhost for inter-service communication

---

### Issue: Volume Data Not Persisting

**Symptoms:**
- Data lost after restart
- Volume appears empty

**Solution:**
```bash
# Check volume exists
docker volume ls | grep myapp

# Inspect volume
docker volume inspect myapp_postgres-data

# Check mount point in container
docker-compose exec db df -h | grep postgres

# Verify data directory permissions
docker-compose exec db ls -la /var/lib/postgresql/data

# Recreate volume if corrupted
docker-compose down -v
docker volume rm myapp_postgres-data
docker-compose up -d
```

**Prevention:**
- Use named volumes for persistence
- Regular backups
- Test restore procedures
- Document volume locations

---

## Best Practices

### DO:
✅ **Use version control for compose files** - Track infrastructure changes  
✅ **Environment-specific configurations** - dev, staging, production  
✅ **Health checks for all services** - Enable proper orchestration  
✅ **Named volumes for persistence** - Don't lose data  
✅ **Resource limits in production** - Prevent resource exhaustion  
✅ **Logging configuration** - Centralized log management  
✅ **Network segmentation** - Security through isolation  
✅ **Secrets management** - Never commit secrets  
✅ **Regular backups** - Automated backup procedures  
✅ **Documentation** - Architecture diagrams, runbooks

### DON'T:
❌ **Use latest tag in production** - Version pinning required  
❌ **Expose all ports** - Minimize attack surface  
❌ **Run as root** - Security risk  
❌ **Commit .env files** - Contains secrets  
❌ **Skip health checks** - Causes startup issues  
❌ **Ignore resource limits** - Can crash host  
❌ **Mount code in production** - Use built images  
❌ **Use same passwords everywhere** - Separate dev/prod credentials  
❌ **Forget to cleanup** - Regular pruning needed  
❌ **Skip testing locally** - Test before deployment

---

## Related Workflows

**Prerequisites:**
- [Docker Container Creation](./docker_container_creation.md) - Create individual containers first

**Next Steps:**
- [Kubernetes Deployment](./kubernetes_deployment.md) - Scale beyond single host
- [CI/CD Pipeline Setup](./cicd_pipeline_setup.md) - Automate deployments
- [Application Monitoring Setup](./application_monitoring_setup.md) - Production monitoring

**Alternatives:**
- [Infrastructure as Code with Terraform](./infrastructure_as_code_terraform.md) - Infrastructure management

---

## Tags
`devops` `docker` `docker-compose` `microservices` `orchestration` `multi-service` `containers` `infrastructure` `deployment`
