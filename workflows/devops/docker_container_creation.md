# Docker Container Creation

**ID:** devops-007  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 45-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for creating, building, and deploying Docker containers from scratch

**Why:** Containerization ensures consistent environments across development, testing, and production, eliminates "works on my machine" issues, and enables modern deployment practices like microservices and CI/CD automation.

**When to use:**
- Creating new containerized applications
- Migrating existing applications to Docker
- Building microservices
- Setting up development environments
- Deploying to container orchestration platforms (Kubernetes, ECS)
- Creating reproducible build environments

---

## Prerequisites

**Required:**
- [ ] Docker installed (`docker --version`)
- [ ] Basic understanding of application architecture
- [ ] Source code ready to containerize
- [ ] Understanding of application dependencies

**Check before starting:**
```bash
# Verify Docker installation
docker --version
# Expected: Docker version 24.0.0 or higher

# Check Docker daemon is running
docker ps
# Expected: Container list (even if empty)

# Verify Docker Compose (optional but recommended)
docker-compose --version
# Expected: Docker Compose version v2.0.0 or higher

# Check available disk space (Docker images can be large)
df -h
# Ensure at least 10GB free space
```

---

## Implementation Steps

### Step 1: Analyze Application Requirements

**What:** Understand what your application needs to run in a container

**How:**
Document all dependencies, runtime requirements, configuration files, and environment variables your application needs.

**Code/Commands:**
```bash
# Create project documentation
cat > CONTAINERIZATION_PLAN.md <<'EOF'
# Containerization Plan

## Application Details
- **Name:** my-web-app
- **Type:** Python FastAPI application
- **Runtime:** Python 3.11
- **Framework:** FastAPI + Uvicorn

## Dependencies
### System Dependencies
- Python 3.11
- pip/poetry for package management
- libpq-dev (for PostgreSQL)

### Application Dependencies
- fastapi==0.104.0
- uvicorn[standard]==0.24.0
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9

## Runtime Requirements
- Port: 8000
- Environment Variables:
  - DATABASE_URL (required)
  - SECRET_KEY (required)
  - LOG_LEVEL (optional, default: info)

## Data Volumes
- /app/logs - Application logs
- /app/uploads - User uploads (if any)

## Build Process
1. Install system dependencies
2. Install Python dependencies
3. Copy application code
4. Set up non-root user

## Health Check
- Endpoint: GET /health
- Expected: 200 OK response
EOF

# Document current application structure
tree -L 2 -I '__pycache__|*.pyc|.git' > app_structure.txt

# List Python dependencies
pip freeze > requirements.txt
# Or for Poetry projects
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

**Verification:**
- [ ] All dependencies documented
- [ ] Runtime requirements clear
- [ ] Port mappings identified
- [ ] Environment variables listed
- [ ] Volume mount points defined

**If This Fails:**
→ Review application documentation
→ Test application locally to understand requirements
→ Check existing deployment scripts
→ Consult with development team

---

### Step 2: Create Dockerfile

**What:** Write a Dockerfile that defines how to build your container image

**How:**
Use multi-stage builds, layer caching, and security best practices to create an efficient and secure image.

**Code/Commands:**
```dockerfile
# Dockerfile for Python FastAPI application
# Multi-stage build for smaller final image

# Stage 1: Builder stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt .

# Install Python dependencies to /app/.venv
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set labels for image metadata
LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="FastAPI application container"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Set PATH to include local Python packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Alternative Dockerfiles for different stacks:**

```dockerfile
# Node.js application
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./
USER nodejs
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

```dockerfile
# Go application
FROM golang:1.21-alpine as builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
```

**Create .dockerignore file:**
```bash
cat > .dockerignore <<'EOF'
# Git
.git
.gitignore
.gitattributes

# CI/CD
.github
.gitlab-ci.yml
Jenkinsfile

# Documentation
*.md
docs/

# Development files
.env.local
.env.development
*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.mypy_cache/
venv/
env/

# Node
node_modules/
npm-debug.log
yarn-error.log

# Build artifacts
dist/
build/
target/

# Logs
logs/
*.log

# OS files
.DS_Store
Thumbs.db
EOF
```

**Verification:**
- [ ] Dockerfile created with multi-stage build
- [ ] Non-root user configured
- [ ] Health check defined
- [ ] .dockerignore file created
- [ ] Security best practices followed

**If This Fails:**
→ Start with simple Dockerfile, add complexity incrementally
→ Use official base images from Docker Hub
→ Check Dockerfile syntax: `docker build --check .`
→ Review Docker best practices documentation

---

### Step 3: Build Docker Image

**What:** Compile your Dockerfile into an executable container image

**How:**
Use Docker build with proper tagging, caching, and build arguments.

**Code/Commands:**
```bash
# Basic build
docker build -t my-app:latest .

# Build with tag and version
docker build -t my-app:1.0.0 -t my-app:latest .

# Build with build arguments
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg APP_VERSION=1.0.0 \
  -t my-app:1.0.0 \
  .

# Build with no cache (clean build)
docker build --no-cache -t my-app:latest .

# Build with specific target stage (multi-stage builds)
docker build --target builder -t my-app:builder .

# Build with build kit (better caching, parallel builds)
DOCKER_BUILDKIT=1 docker build -t my-app:latest .

# Build with platform specification (for M1 Macs)
docker build --platform linux/amd64 -t my-app:latest .

# View build history
docker history my-app:latest

# Check image size
docker images my-app:latest

# Inspect image details
docker inspect my-app:latest

# Create build script for automation
cat > build.sh <<'EOF'
#!/bin/bash
set -euo pipefail

APP_NAME="my-app"
VERSION="${1:-latest}"
REGISTRY="${REGISTRY:-docker.io/myorg}"

echo "Building ${APP_NAME}:${VERSION}..."

# Build with BuildKit for better performance
DOCKER_BUILDKIT=1 docker build \
  --build-arg VERSION="${VERSION}" \
  --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
  -t "${REGISTRY}/${APP_NAME}:${VERSION}" \
  -t "${REGISTRY}/${APP_NAME}:latest" \
  .

echo "✅ Build complete!"
echo "Image: ${REGISTRY}/${APP_NAME}:${VERSION}"

# Display image size
docker images "${REGISTRY}/${APP_NAME}:${VERSION}" --format "Size: {{.Size}}"
EOF

chmod +x build.sh
./build.sh 1.0.0
```

**Verification:**
- [ ] Image built successfully
- [ ] Image tagged properly
- [ ] Image size reasonable (<500MB for most apps)
- [ ] No errors in build output
- [ ] Image appears in `docker images`

**If This Fails:**
→ Check Dockerfile syntax errors
→ Verify all COPY paths exist
→ Ensure base image is accessible
→ Check disk space: `df -h`
→ Review build logs for specific errors

---

### Step 4: Test Container Locally

**What:** Run and test your container before deployment

**How:**
Start the container with proper configuration and verify it works correctly.

**Code/Commands:**
```bash
# Run container interactively (for testing)
docker run -it --rm \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://localhost/testdb" \
  -e SECRET_KEY="test-secret-key" \
  my-app:latest

# Run container in detached mode
docker run -d \
  --name my-app-test \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://localhost/testdb" \
  -e SECRET_KEY="test-secret-key" \
  my-app:latest

# Run with environment file
cat > .env.docker <<'EOF'
DATABASE_URL=postgresql://localhost/testdb
SECRET_KEY=my-secret-key
LOG_LEVEL=debug
EOF

docker run -d \
  --name my-app-test \
  -p 8000:8000 \
  --env-file .env.docker \
  my-app:latest

# Run with volume mounts
docker run -d \
  --name my-app-test \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  my-app:latest

# Test the application
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# View logs
docker logs my-app-test

# Follow logs in real-time
docker logs -f my-app-test

# Execute commands inside container
docker exec -it my-app-test /bin/bash

# Check resource usage
docker stats my-app-test

# Stop container
docker stop my-app-test

# Remove container
docker rm my-app-test

# Create test script
cat > test-container.sh <<'EOF'
#!/bin/bash
set -euo pipefail

CONTAINER_NAME="my-app-test"
IMAGE="my-app:latest"

echo "Starting container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  -p 8000:8000 \
  --env-file .env.docker \
  "$IMAGE"

echo "Waiting for container to be healthy..."
sleep 5

# Health check
echo "Testing health endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$response" -eq 200 ]; then
  echo "✅ Health check passed"
else
  echo "❌ Health check failed: HTTP $response"
  docker logs "$CONTAINER_NAME"
  exit 1
fi

# Additional functional tests
echo "Running functional tests..."
# Add your test commands here

echo "✅ All tests passed!"

# Cleanup
echo "Cleaning up..."
docker stop "$CONTAINER_NAME"
docker rm "$CONTAINER_NAME"
EOF

chmod +x test-container.sh
./test-container.sh
```

**Verification:**
- [ ] Container starts successfully
- [ ] Application accessible on expected port
- [ ] Health check endpoint returns 200 OK
- [ ] Logs show no errors
- [ ] Application functions correctly
- [ ] Can execute commands inside container

**If This Fails:**
→ Check container logs: `docker logs <container-name>`
→ Verify port is not already in use: `lsof -i :8000`
→ Check environment variables are set correctly
→ Exec into container to debug: `docker exec -it <container> /bin/bash`
→ Review application logs inside container

---

### Step 5: Optimize Image Size

**What:** Reduce container image size for faster deployments and lower storage costs

**How:**
Use smaller base images, remove build artifacts, and leverage layer caching effectively.

**Code/Commands:**
```bash
# Check current image size
docker images my-app:latest

# Analyze image layers
docker history my-app:latest --human --no-trunc

# Use dive tool for detailed analysis (install first)
# brew install dive  # macOS
# apt-get install dive  # Ubuntu
dive my-app:latest

# Optimization techniques:

# 1. Use slim/alpine base images
# Before: FROM python:3.11 (1GB)
# After: FROM python:3.11-slim (150MB) or python:3.11-alpine (50MB)

# 2. Multi-stage builds (already shown in Step 2)

# 3. Combine RUN commands to reduce layers
# Bad:
# RUN apt-get update
# RUN apt-get install -y package1
# RUN apt-get install -y package2

# Good:
# RUN apt-get update && apt-get install -y \
#     package1 \
#     package2 \
#     && rm -rf /var/lib/apt/lists/*

# 4. Remove build dependencies after use
FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && pip install -r requirements.txt \
    && apt-get purge -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# 5. Use .dockerignore aggressively

# 6. Clean pip cache
RUN pip install --no-cache-dir -r requirements.txt

# 7. Use distroless images for maximum security (Google)
FROM gcr.io/distroless/python3-debian11
COPY --from=builder /app /app
CMD ["/app/main.py"]

# Create optimized Dockerfile comparison
cat > Dockerfile.optimized <<'EOF'
FROM python:3.11-alpine as builder
WORKDIR /app
RUN apk add --no-cache gcc musl-dev libpq-dev
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.11-alpine
RUN apk add --no-cache libpq
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "main.py"]
EOF

# Build and compare sizes
docker build -t my-app:standard -f Dockerfile .
docker build -t my-app:optimized -f Dockerfile.optimized .

docker images | grep my-app
# Compare the SIZE column

# Export image for inspection
docker save my-app:latest | gzip > my-app-latest.tar.gz
ls -lh my-app-latest.tar.gz
```

**Optimization checklist:**
```bash
cat > optimization_checklist.md <<'EOF'
# Docker Image Optimization Checklist

- [ ] Use minimal base image (alpine/slim/distroless)
- [ ] Multi-stage builds implemented
- [ ] Combined RUN commands to reduce layers
- [ ] Removed build dependencies after installation
- [ ] Used --no-cache-dir for pip/npm
- [ ] Cleaned apt cache (rm -rf /var/lib/apt/lists/*)
- [ ] Comprehensive .dockerignore file
- [ ] No unnecessary files in image
- [ ] Static binaries when possible (Go, Rust)
- [ ] Image size < 500MB (target)
- [ ] Layers < 30 (target)

## Size Targets
- Simple app: < 100MB
- Python/Node app: 100-300MB
- Complex app: 300-500MB
- Warning: > 500MB (needs optimization)
- Critical: > 1GB (serious issues)
EOF
```

**Verification:**
- [ ] Image size reduced significantly
- [ ] Application still works correctly
- [ ] No missing dependencies
- [ ] Build time acceptable
- [ ] Layer count reduced

**If This Fails:**
→ Test each optimization incrementally
→ Don't use alpine if it causes issues (use slim instead)
→ Ensure all runtime dependencies included
→ Test thoroughly after each optimization

---

### Step 6: Implement Security Best Practices

**What:** Secure your container against common vulnerabilities

**How:**
Apply security hardening, scan for vulnerabilities, and follow the principle of least privilege.

**Code/Commands:**
```bash
# Scan image for vulnerabilities (using Trivy)
# Install: brew install trivy  # macOS
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image my-app:latest

# Or use Docker Scout (built-in)
docker scout cves my-app:latest

# Security hardening in Dockerfile
cat > Dockerfile.secure <<'EOF'
FROM python:3.11-slim

# 1. Run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 2. Set secure file permissions
WORKDIR /app
COPY --chown=appuser:appuser . .
RUN chmod -R 550 /app

# 3. Drop unnecessary capabilities
# (Done at runtime, see docker run below)

# 4. Use read-only root filesystem
# (Done at runtime)

# 5. Don't include secrets in image
# Use environment variables or secret management

# 6. Update packages for security patches
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

USER appuser
EXPOSE 8000
CMD ["python", "main.py"]
EOF

# Run container with security options
docker run -d \
  --name my-app-secure \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --security-opt=no-new-privileges:true \
  --pids-limit 100 \
  --memory 512m \
  --cpus 1 \
  -p 8000:8000 \
  my-app:latest

# Create security scanning script
cat > security-scan.sh <<'EOF'
#!/bin/bash
set -euo pipefail

IMAGE="${1:-my-app:latest}"

echo "🔒 Running security scans on $IMAGE..."

# Trivy scan
echo "📊 Vulnerability scan with Trivy..."
trivy image --severity HIGH,CRITICAL "$IMAGE"

# Check for secrets
echo "🔍 Checking for exposed secrets..."
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  trufflesecurity/trufflehog:latest \
  docker --image="$IMAGE"

# Dockle best practices check
echo "✅ Best practices check with Dockle..."
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  goodwithtech/dockle:latest \
  "$IMAGE"

echo "✅ Security scans complete!"
EOF

chmod +x security-scan.sh
./security-scan.sh my-app:latest

# Security checklist
cat > security_checklist.md <<'EOF'
# Container Security Checklist

## Image Security
- [ ] Using official base images
- [ ] Base image kept up to date
- [ ] Minimal base image (slim/alpine)
- [ ] No secrets in image layers
- [ ] No sensitive files in image

## Runtime Security
- [ ] Running as non-root user
- [ ] Read-only root filesystem where possible
- [ ] Capabilities dropped (--cap-drop ALL)
- [ ] Security options applied
- [ ] Resource limits set (memory, CPU)
- [ ] Process limits set (--pids-limit)

## Vulnerability Management
- [ ] Regular vulnerability scans
- [ ] Critical vulnerabilities addressed
- [ ] Dependencies kept updated
- [ ] Security patches applied

## Network Security
- [ ] Minimal port exposure
- [ ] Network isolation configured
- [ ] TLS/SSL for external communication

## Access Control
- [ ] File permissions properly set
- [ ] Environment variables for secrets
- [ ] No hardcoded credentials
EOF
```

**Verification:**
- [ ] Vulnerability scan shows no CRITICAL issues
- [ ] Container runs as non-root
- [ ] No secrets in image layers
- [ ] Security best practices checklist complete
- [ ] Resource limits enforced

**If This Fails:**
→ Address vulnerabilities by updating base image
→ Update application dependencies
→ Review Dockerfile security guide
→ Use alternative base images if needed

---

### Step 7: Create Docker Compose Configuration

**What:** Define multi-container setup for local development and testing

**How:**
Create docker-compose.yml for easy orchestration of your application and its dependencies.

**Code/Commands:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - VERSION=1.0.0
    image: my-app:latest
    container_name: my-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - SECRET_KEY=${SECRET_KEY}
      - LOG_LEVEL=info
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    container_name: my-app-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: my-app-redis
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
```

```bash
# Create .env file for docker-compose
cat > .env <<'EOF'
SECRET_KEY=your-secret-key-here
LOG_LEVEL=debug
EOF

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild and start
docker-compose up -d --build

# Scale services
docker-compose up -d --scale app=3

# Execute command in service
docker-compose exec app python manage.py migrate

# Create management scripts
cat > docker-manage.sh <<'EOF'
#!/bin/bash
set -euo pipefail

command="${1:-help}"

case "$command" in
  start)
    echo "Starting services..."
    docker-compose up -d
    echo "✅ Services started"
    docker-compose ps
    ;;
  stop)
    echo "Stopping services..."
    docker-compose down
    echo "✅ Services stopped"
    ;;
  restart)
    echo "Restarting services..."
    docker-compose restart
    echo "✅ Services restarted"
    ;;
  logs)
    docker-compose logs -f "${2:-app}"
    ;;
  shell)
    docker-compose exec app /bin/bash
    ;;
  rebuild)
    echo "Rebuilding and restarting..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Rebuild complete"
    ;;
  clean)
    echo "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    echo "✅ Cleanup complete"
    ;;
  *)
    echo "Usage: ./docker-manage.sh {start|stop|restart|logs|shell|rebuild|clean}"
    exit 1
    ;;
esac
EOF

chmod +x docker-manage.sh
```

**Verification:**
- [ ] docker-compose.yml created
- [ ] All services start successfully
- [ ] Application connects to dependencies
- [ ] Health checks passing
- [ ] Volumes persisting data
- [ ] Networks configured correctly

**If This Fails:**
→ Check port conflicts
→ Verify service dependencies
→ Review environment variables
→ Check network connectivity between containers
→ Review docker-compose logs

---

### Step 8: Publish Image to Registry

**What:** Push your container image to a registry for deployment

**How:**
Tag and push images to Docker Hub, AWS ECR, Google GCR, or private registry.

**Code/Commands:**
```bash
# Docker Hub
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# Tag for Docker Hub
docker tag my-app:latest username/my-app:1.0.0
docker tag my-app:latest username/my-app:latest

# Push to Docker Hub
docker push username/my-app:1.0.0
docker push username/my-app:latest

# AWS ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name my-app --region us-east-1

# Tag for ECR
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.0

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.0

# Google Container Registry (GCR)
gcloud auth configure-docker

# Tag for GCR
docker tag my-app:latest gcr.io/project-id/my-app:1.0.0

# Push to GCR
docker push gcr.io/project-id/my-app:1.0.0

# GitHub Container Registry (GHCR)
echo "$GITHUB_TOKEN" | docker login ghcr.io -u USERNAME --password-stdin

# Tag for GHCR
docker tag my-app:latest ghcr.io/username/my-app:1.0.0

# Push to GHCR
docker push ghcr.io/username/my-app:1.0.0

# Create publish script
cat > publish.sh <<'EOF'
#!/bin/bash
set -euo pipefail

VERSION="${1:-latest}"
REGISTRY="${REGISTRY:-docker.io}"
REPO="${REPO:-myorg/my-app}"

echo "Publishing ${REPO}:${VERSION} to ${REGISTRY}..."

# Login to registry
case "$REGISTRY" in
  docker.io)
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    ;;
  *.ecr.*.amazonaws.com)
    aws ecr get-login-password --region us-east-1 | \
      docker login --username AWS --password-stdin "$REGISTRY"
    ;;
  gcr.io)
    gcloud auth configure-docker
    ;;
  ghcr.io)
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin
    ;;
esac

# Tag image
docker tag my-app:latest "${REGISTRY}/${REPO}:${VERSION}"
docker tag my-app:latest "${REGISTRY}/${REPO}:latest"

# Push image
docker push "${REGISTRY}/${REPO}:${VERSION}"
docker push "${REGISTRY}/${REPO}:latest"

echo "✅ Published ${REGISTRY}/${REPO}:${VERSION}"

# Output pull command
echo ""
echo "To pull this image:"
echo "docker pull ${REGISTRY}/${REPO}:${VERSION}"
EOF

chmod +x publish.sh

# Publish with CI/CD (GitHub Actions example)
cat > .github/workflows/docker-publish.yml <<'EOF'
name: Build and Publish Docker Image

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Log in to registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max
EOF
```

**Verification:**
- [ ] Successfully logged in to registry
- [ ] Image tagged correctly
- [ ] Image pushed successfully
- [ ] Image pullable from registry
- [ ] Version tags applied correctly
- [ ] CI/CD pipeline (if applicable) passing

**If This Fails:**
→ Verify registry credentials
→ Check network connectivity to registry
→ Ensure repository exists (create if needed)
→ Review registry permissions
→ Check image name format matches registry requirements

---

## Verification Checklist

After completing this workflow:

- [ ] Dockerfile created with best practices
- [ ] Image builds successfully
- [ ] Container runs and application works
- [ ] Image size optimized (<500MB target)
- [ ] Security scan shows no critical vulnerabilities
- [ ] Non-root user configured
- [ ] Health check implemented
- [ ] docker-compose.yml created (if applicable)
- [ ] Image published to registry
- [ ] Documentation updated

---

## Common Issues & Solutions

### Issue: "Permission Denied" When Running Container

**Symptoms:**
- Application fails to write to filesystem
- Permission errors in logs

**Solution:**
```bash
# Ensure non-root user has correct permissions
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Or run container with specific user
docker run --user 1000:1000 my-app:latest

# For volumes, ensure host directories have correct permissions
chmod -R 777 ./logs  # Or more restrictive as needed
```

**Prevention:**
- Always test file permissions
- Use COPY --chown in Dockerfile
- Document required permissions

---

### Issue: Image Build Fails with "No Space Left on Device"

**Symptoms:**
- Build fails with disk space error
- Docker daemon reports no space

**Solution:**
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a -f

# Remove unused images
docker image prune -a -f

# Remove stopped containers
docker container prune -f

# Remove unused volumes
docker volume prune -f

# Check Docker's disk usage
docker system df
```

**Prevention:**
- Regular cleanup of unused images
- Monitor disk space
- Use .dockerignore to exclude large files
- Implement automated cleanup in CI/CD

---

### Issue: Container Crashes Immediately After Start

**Symptoms:**
- Container exits immediately
- `docker ps` doesn't show container

**Solution:**
```bash
# Check logs
docker logs <container-name>

# Common causes and fixes:

# 1. Application crashes
# Check logs for error messages
docker logs --tail 100 <container-name>

# 2. Command not found
# Ensure CMD/ENTRYPOINT is correct
# Test manually:
docker run -it --rm my-app:latest /bin/bash

# 3. Missing environment variables
# Check required env vars
docker run -it --rm -e REQUIRED_VAR=value my-app:latest

# 4. Port already in use
lsof -i :8000  # Check what's using the port
docker run -p 8001:8000 my-app:latest  # Use different port

# Debug by overriding entrypoint
docker run -it --rm --entrypoint /bin/bash my-app:latest
```

**Prevention:**
- Test locally before deployment
- Comprehensive health checks
- Proper error handling in application
- Document required environment variables

---

## Examples

### Example 1: Python FastAPI Microservice

**Context:** Creating a production-ready container for a FastAPI application with PostgreSQL

**Execution:**
```dockerfile
# Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t fastapi-app:1.0.0 .
docker run -d -p 8000:8000 --name fastapi fastapi-app:1.0.0
```

**Result:** 250MB optimized image, non-root user, health checks configured

---

### Example 2: Node.js Application with Build Step

**Context:** Frontend application requiring build step (React, Vue, etc.)

**Execution:**
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Result:** 50MB final image with only production assets

---

### Example 3: Go Application with Minimal Image

**Context:** Go microservice requiring smallest possible image

**Execution:**
```dockerfile
FROM golang:1.21-alpine as builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-w -s" -o main .

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/main /main
EXPOSE 8080
CMD ["/main"]
```

**Result:** ~10MB image with just the binary and SSL certificates

---

## Best Practices

### DO:
✅ **Use multi-stage builds** - Minimize final image size  
✅ **Run as non-root user** - Enhance security  
✅ **Implement health checks** - Enable container orchestration  
✅ **Use .dockerignore** - Exclude unnecessary files  
✅ **Tag images properly** - Enable version tracking  
✅ **Scan for vulnerabilities** - Regular security checks  
✅ **Optimize layer caching** - Faster builds  
✅ **Use official base images** - Trusted sources  
✅ **Document Dockerfile** - Comments for future maintainers  
✅ **Pin versions** - Reproducible builds

### DON'T:
❌ **Run as root** - Security risk  
❌ **Include secrets in image** - Use environment variables  
❌ **Use latest tag in production** - Version instability  
❌ **Ignore image size** - Slow deployments  
❌ **Skip vulnerability scans** - Security holes  
❌ **Copy entire directory** - Includes unnecessary files  
❌ **Use ADD when COPY works** - ADD has hidden features  
❌ **Hardcode configuration** - Use environment variables  
❌ **Skip health checks** - Harder orchestration  
❌ **Forget .dockerignore** - Larger images, slower builds

---

## Related Workflows

**Prerequisites:**
- [Environment Initialization](../development/environment_initialization.md) - Set up development environment

**Next Steps:**
- [Docker Compose Multi-Service](./docker_compose_multi_service.md) - Orchestrate multiple containers
- [Kubernetes Deployment](./kubernetes_deployment.md) - Deploy to K8s
- [CI/CD Pipeline Setup](./cicd_pipeline_setup.md) - Automate container builds

**Alternatives:**
- [Infrastructure as Code with Terraform](./infrastructure_as_code_terraform.md) - IaC approach
- [Cloud Provider Setup](./cloud_provider_setup.md) - Cloud-native deployments

---

## Tags
`devops` `docker` `containers` `containerization` `dockerfile` `image-optimization` `security` `deployment` `infrastructure`
