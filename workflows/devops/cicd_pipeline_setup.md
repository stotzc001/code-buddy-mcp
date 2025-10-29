# CI/CD Pipeline Setup

**ID:** devops-004  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 2-3 hours  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for setting up automated Continuous Integration and Continuous Deployment (CI/CD) pipelines

**Why:** CI/CD automation ensures code changes are automatically tested, validated, and deployed, reducing manual errors, accelerating releases, improving code quality, and enabling rapid feedback loops. It's essential for modern software development practices.

**When to use:**
- Setting up new project deployment automation
- Migrating from manual to automated deployments
- Implementing automated testing and quality gates
- Standardizing deployment processes across teams
- Enabling faster, more reliable releases
- Enforcing code quality and security checks

---

## Prerequisites

**Required:**
- [ ] Version control repository (GitHub, GitLab, Bitbucket)
- [ ] CI/CD platform access (GitHub Actions, GitLab CI, Jenkins, etc.)
- [ ] Understanding of application build/test process
- [ ] Deployment target configured (cloud, Kubernetes, servers)
- [ ] Basic YAML/scripting knowledge

**Check before starting:**
```bash
# Verify git repository
git remote -v
git status

# Check if CI/CD configuration exists
ls -la .github/workflows/  # GitHub Actions
ls -la .gitlab-ci.yml      # GitLab CI
ls -la Jenkinsfile         # Jenkins

# Verify deployment credentials
# AWS example:
aws sts get-caller-identity

# Docker registry access
docker login

# Kubernetes access
kubectl cluster-info
```

---

## Implementation Steps

### Step 1: Choose CI/CD Platform and Design Pipeline

**What:** Select appropriate CI/CD platform and design pipeline stages

**How:**
Evaluate platforms based on your needs and design a multi-stage pipeline with proper gates.

**Code/Commands:**
```bash
# Document pipeline design
cat > PIPELINE_DESIGN.md <<'EOF'
# CI/CD Pipeline Design

## Platform Selection
**Chosen Platform:** GitHub Actions
**Reasons:**
- Native GitHub integration
- Free for public repos, generous free tier for private
- Large marketplace of actions
- Easy YAML configuration

## Pipeline Stages

### 1. Build Stage
- Checkout code
- Install dependencies
- Compile/build application
- Create artifacts

### 2. Test Stage
- Unit tests
- Integration tests
- Code coverage (min 80%)
- Linting and formatting

### 3. Security Stage
- Dependency vulnerability scan
- Container image scan
- SAST (Static Application Security Testing)
- Secret detection

### 4. Quality Stage
- Code quality analysis (SonarQube)
- Performance tests
- Documentation generation

### 5. Package Stage
- Build Docker images
- Tag with version
- Push to registry

### 6. Deploy Stage
- Deploy to staging (auto)
- Run smoke tests
- Deploy to production (manual approval)

## Environments
- **Development:** Auto-deploy on feature branches
- **Staging:** Auto-deploy on main branch
- **Production:** Manual approval required

## Rollback Strategy
- Keep last 3 successful builds
- Automated rollback on health check failure
- Manual rollback capability

## Notifications
- Slack notifications for failures
- Email for production deployments
- GitHub status checks
EOF

# Platform comparison matrix
cat > platform_comparison.md <<'EOF'
# CI/CD Platform Comparison

| Feature | GitHub Actions | GitLab CI | Jenkins | CircleCI |
|---------|---------------|-----------|---------|----------|
| Cost | Free tier: 2000 min/month | Free tier: 400 min/month | Self-hosted (free) | Free tier: 6000 min/month |
| Setup | Easy | Easy | Moderate | Easy |
| Docker support | ✅ Native | ✅ Native | ✅ Plugin | ✅ Native |
| Self-hosted | ✅ | ✅ | ✅ Required | ✅ |
| Marketplace | Large | Medium | Huge (plugins) | Medium |
| YAML config | ✅ | ✅ | ❌ Jenkinsfile | ✅ |
| Matrix builds | ✅ | ✅ | ✅ | ✅ |
| Artifacts | ✅ | ✅ | ✅ | ✅ |
| Secrets mgmt | ✅ Good | ✅ Good | ✅ Plugins | ✅ Good |
EOF
```

**Verification:**
- [ ] Platform selected and documented
- [ ] Pipeline stages defined
- [ ] Environments identified
- [ ] Rollback strategy planned
- [ ] Team alignment on approach

**If This Fails:**
→ Review team requirements and constraints
→ Consider starting with simpler platform
→ Prototype with basic pipeline first
→ Get stakeholder buy-in

---

### Step 2: Set Up Basic Pipeline Configuration

**What:** Create initial CI/CD configuration file with basic stages

**How:**
Start with a simple working pipeline that can be enhanced iteratively.

**Code/Commands:**

**GitHub Actions:**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Job 1: Build and Test
  build-test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
      
      - name: Build application
        run: npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: dist/
          retention-days: 7
  
  # Job 2: Security Scan
  security-scan:
    runs-on: ubuntu-latest
    needs: build-test
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Dependency Review
        uses: actions/dependency-review-action@v3
        if: github.event_name == 'pull_request'
  
  # Job 3: Build Docker Image
  build-image:
    runs-on: ubuntu-latest
    needs: [build-test, security-scan]
    if: github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max
  
  # Job 4: Deploy to Staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-image
    environment:
      name: staging
      url: https://staging.example.com
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n staging
          
          kubectl rollout status deployment/myapp -n staging --timeout=5m
      
      - name: Run smoke tests
        run: |
          curl -f https://staging.example.com/health || exit 1
          npm run test:e2e:staging
  
  # Job 5: Deploy to Production
  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://example.com
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
      
      - name: Deploy to Production
        run: |
          kubectl set image deployment/myapp \
            myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            -n production
          
          kubectl rollout status deployment/myapp -n production --timeout=5m
      
      - name: Verify deployment
        run: |
          curl -f https://example.com/health || exit 1
      
      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment completed!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

**GitLab CI Alternative:**
```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - security
  - package
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

# Build Job
build:
  stage: build
  image: node:20
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/

# Test Job
test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm run lint
    - npm test -- --coverage
  coverage: '/Statements\s+:\s+(\d+\.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

# Security Scan
security_scan:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy fs --exit-code 0 --severity HIGH,CRITICAL .
  allow_failure: true

# Build Docker Image
docker_build:
  stage: package
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG
  only:
    - main

# Deploy to Staging
deploy_staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context staging
    - kubectl set image deployment/myapp myapp=$IMAGE_TAG -n staging
    - kubectl rollout status deployment/myapp -n staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

# Deploy to Production
deploy_production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context production
    - kubectl set image deployment/myapp myapp=$IMAGE_TAG -n production
    - kubectl rollout status deployment/myapp -n production
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
```

**Verification:**
- [ ] Pipeline configuration file created
- [ ] Basic stages defined
- [ ] File syntax valid (YAML linter)
- [ ] Committed to repository
- [ ] Pipeline triggered automatically

**If This Fails:**
→ Validate YAML syntax online
→ Check runner/executor availability
→ Verify permissions to create workflows
→ Start with minimal config and build up

---

### Step 3: Configure Secrets and Environment Variables

**What:** Securely store credentials and configuration needed by pipeline

**How:**
Use platform secret management and never commit secrets to code.

**Code/Commands:**

**GitHub Secrets:**
```bash
# Using GitHub CLI
gh secret set DOCKER_USERNAME -b"myuser"
gh secret set DOCKER_PASSWORD -b"$(cat docker-password.txt)"
gh secret set KUBE_CONFIG_STAGING < kubeconfig-staging.yaml
gh secret set KUBE_CONFIG_PRODUCTION < kubeconfig-prod.yaml
gh secret set SLACK_WEBHOOK -b"https://hooks.slack.com/..."
gh secret set AWS_ACCESS_KEY_ID -b"AKIA..."
gh secret set AWS_SECRET_ACCESS_KEY -b"secret..."

# List secrets (values are hidden)
gh secret list

# Using GitHub UI:
# Repository → Settings → Secrets and variables → Actions → New repository secret

# Environment-specific secrets
# Repository → Settings → Environments → New environment
# Add secrets to specific environment (staging, production)

# Organization-level secrets (for multiple repos)
# Organization → Settings → Secrets → New organization secret
```

**GitLab Secrets:**
```bash
# Using GitLab UI:
# Project → Settings → CI/CD → Variables → Expand → Add variable

# Using GitLab API:
curl --request POST --header "PRIVATE-TOKEN: <token>" \
  "https://gitlab.com/api/v4/projects/<project-id>/variables" \
  --form "key=DOCKER_PASSWORD" \
  --form "value=secret" \
  --form "protected=true" \
  --form "masked=true"

# Environment-specific variables:
# Set environment scope to "production" or "staging"
```

**Jenkins Credentials:**
```groovy
// Jenkinsfile using credentials
pipeline {
    agent any
    environment {
        DOCKER_CREDS = credentials('docker-credentials-id')
        KUBE_CONFIG = credentials('kubeconfig-id')
    }
    stages {
        stage('Build') {
            steps {
                sh 'docker login -u $DOCKER_CREDS_USR -p $DOCKER_CREDS_PSW'
            }
        }
    }
}

// Add credentials via Jenkins UI:
// Dashboard → Manage Jenkins → Credentials → System → Global credentials → Add Credentials
```

**Best Practices Checklist:**
```bash
cat > secrets_checklist.md <<'EOF'
# Secrets Management Checklist

## Storage
- [ ] All secrets stored in CI/CD platform secret manager
- [ ] No secrets in code or configuration files
- [ ] No secrets in commit history
- [ ] .env files in .gitignore

## Access Control
- [ ] Environment-specific secrets configured
- [ ] Production secrets require elevated permissions
- [ ] Secrets rotated regularly (quarterly minimum)
- [ ] Least privilege access applied

## Security
- [ ] Secrets masked in logs
- [ ] Secrets marked as protected/sensitive
- [ ] Audit trail for secret access
- [ ] Secrets encrypted at rest

## Documentation
- [ ] Secret names documented
- [ ] Required secrets listed in README
- [ ] Rotation procedures documented
- [ ] Emergency access procedures defined

## Validation
- [ ] All secrets validated before use
- [ ] Failed secret validation stops pipeline
- [ ] Alerts for missing secrets
- [ ] Expiration warnings for certificates/tokens
EOF
```

**Verification:**
- [ ] All required secrets added
- [ ] Secrets properly scoped (repo/org/environment)
- [ ] Secrets masked in logs
- [ ] Pipeline can access secrets
- [ ] No secrets in code

**If This Fails:**
→ Check secret name matches pipeline reference
→ Verify permissions to add secrets
→ Ensure secrets properly encoded (base64 if needed)
→ Review platform documentation for secret format

---

### Step 4: Implement Automated Testing

**What:** Add comprehensive automated testing to CI pipeline

**How:**
Configure unit tests, integration tests, and code quality checks that run automatically.

**Code/Commands:**

```yaml
# Comprehensive testing job (GitHub Actions)
test-suite:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      node-version: [18, 20]
      os: [ubuntu-latest, windows-latest]
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
    
    # Unit Tests
    - name: Run unit tests
      run: npm test -- --coverage
    
    # Integration Tests
    - name: Run integration tests
      run: npm run test:integration
      env:
        DATABASE_URL: postgresql://test:test@localhost:5432/test
    
    # E2E Tests
    - name: Run E2E tests
      run: |
        npm run build
        npm start &
        sleep 10
        npm run test:e2e
    
    # Code Coverage
    - name: Check coverage threshold
      run: |
        COVERAGE=$(npm test -- --coverage --coverageReporters=json-summary | \
          jq -r '.total.statements.pct')
        if (( $(echo "$COVERAGE < 80" | bc -l) )); then
          echo "Coverage $COVERAGE% is below 80%"
          exit 1
        fi
    
    # Upload coverage to Codecov
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage/coverage-final.json
        flags: unittests
        name: coverage-${{ matrix.node-version }}-${{ matrix.os }}
    
    # Performance Tests
    - name: Run performance tests
      run: npm run test:performance
      if: github.ref == 'refs/heads/main'
    
    # Report test results
    - name: Publish test results
      uses: EnricoMi/publish-unit-test-result-action@v2
      if: always()
      with:
        files: test-results/**/*.xml
```

```bash
# Create test configuration
cat > jest.config.js <<'EOF'
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**'
  ]
};
EOF

# Add test scripts to package.json
cat > package.json <<'EOF'
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:integration": "jest --testMatch='**/*.integration.test.js'",
    "test:e2e": "playwright test",
    "test:performance": "artillery run performance-tests.yml"
  }
}
EOF
```

**Verification:**
- [ ] Unit tests running automatically
- [ ] Integration tests configured
- [ ] Code coverage meeting threshold
- [ ] Test results published
- [ ] Failed tests block deployment

**If This Fails:**
→ Check test command syntax
→ Verify test files exist and are runnable locally
→ Review test timeout settings
→ Check for missing test dependencies

---

### Step 5: Add Code Quality and Security Checks

**What:** Implement automated code quality analysis and security scanning

**How:**
Integrate linting, static analysis, and vulnerability scanning into pipeline.

**Code/Commands:**

```yaml
# Quality and Security Job
quality-security:
  runs-on: ubuntu-latest
  
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for better analysis
    
    # Linting
    - name: Run ESLint
      run: npm run lint -- --format json --output-file eslint-report.json
    
    - name: Annotate code with lint results
      uses: ataylorme/eslint-annotate-action@v2
      with:
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        report-json: eslint-report.json
    
    # SonarCloud Analysis
    - name: SonarCloud Scan
      uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      with:
        args: >
          -Dsonar.projectKey=my-project
          -Dsonar.organization=my-org
          -Dsonar.coverage.exclusions=**/*.test.js
    
    # Dependency vulnerability scan
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
    
    # Container image scan
    - name: Build image for scanning
      run: docker build -t myapp:${{ github.sha }} .
    
    - name: Scan image with Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: myapp:${{ github.sha }}
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH'
    
    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
    
    # Secret detection
    - name: Gitleaks scan
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    # License compliance
    - name: Check licenses
      run: npx license-checker --onlyAllow 'MIT;Apache-2.0;BSD-3-Clause;ISC'
```

```bash
# Configure SonarQube
cat > sonar-project.properties <<'EOF'
sonar.projectKey=my-project
sonar.organization=my-org
sonar.sources=src
sonar.tests=src
sonar.test.inclusions=**/*.test.js,**/*.spec.js
sonar.coverage.exclusions=**/*.test.js,**/*.spec.js
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.qualitygate.wait=true
EOF

# Configure ESLint
cat > .eslintrc.json <<'EOF'
{
  "extends": ["eslint:recommended", "plugin:security/recommended"],
  "plugins": ["security"],
  "rules": {
    "no-console": "warn",
    "no-eval": "error",
    "security/detect-object-injection": "warn"
  }
}
EOF
```

**Verification:**
- [ ] Linting checks passing
- [ ] No critical security vulnerabilities
- [ ] Code quality metrics meet threshold
- [ ] License compliance verified
- [ ] Results visible in PR/commits

**If This Fails:**
→ Fix linting errors locally first
→ Address security vulnerabilities
→ Review quality gate settings
→ Check scanner credentials/tokens

---

### Step 6: Configure Deployment Automation

**What:** Automate deployment to multiple environments with proper controls

**How:**
Set up progressive deployment with environment-specific configurations and approvals.

**Code/Commands:**

```yaml
# Multi-environment deployment workflow
deploy:
  name: Deploy to ${{ matrix.environment }}
  runs-on: ubuntu-latest
  needs: [build-test, quality-security]
  
  strategy:
    matrix:
      environment: [staging, production]
      include:
        - environment: staging
          url: https://staging.example.com
          auto-deploy: true
        - environment: production
          url: https://example.com
          auto-deploy: false
  
  environment:
    name: ${{ matrix.environment }}
    url: ${{ matrix.url }}
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to ECS
      run: |
        # Update task definition
        aws ecs register-task-definition \
          --cli-input-json file://task-definition-${{ matrix.environment }}.json
        
        # Update service
        aws ecs update-service \
          --cluster my-cluster \
          --service my-service-${{ matrix.environment }} \
          --task-definition my-app:latest \
          --force-new-deployment
        
        # Wait for deployment
        aws ecs wait services-stable \
          --cluster my-cluster \
          --services my-service-${{ matrix.environment }}
    
    - name: Run smoke tests
      run: |
        for i in {1..10}; do
          if curl -f ${{ matrix.url }}/health; then
            echo "Health check passed"
            exit 0
          fi
          echo "Attempt $i failed, retrying..."
          sleep 10
        done
        echo "Health check failed after 10 attempts"
        exit 1
    
    - name: Rollback on failure
      if: failure()
      run: |
        aws ecs update-service \
          --cluster my-cluster \
          --service my-service-${{ matrix.environment }} \
          --force-new-deployment \
          --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200"
    
    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: 'Deployed to ${{ matrix.environment }}: ${{ matrix.url }}'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      if: always()
```

**Blue-Green Deployment:**
```yaml
# Blue-Green deployment with AWS
blue-green-deploy:
  runs-on: ubuntu-latest
  steps:
    - name: Deploy green environment
      run: |
        # Deploy new version to green
        aws ecs create-service \
          --cluster my-cluster \
          --service-name my-service-green \
          --task-definition my-app:${{ github.sha }}
        
        # Wait for green to be healthy
        aws ecs wait services-stable \
          --cluster my-cluster \
          --services my-service-green
    
    - name: Switch traffic to green
      run: |
        # Update load balancer to point to green
        aws elbv2 modify-listener \
          --listener-arn $LISTENER_ARN \
          --default-actions Type=forward,TargetGroupArn=$GREEN_TG_ARN
    
    - name: Verify green deployment
      run: |
        sleep 60  # Let traffic flow
        # Check error rates, response times, etc.
    
    - name: Terminate blue environment
      if: success()
      run: |
        aws ecs delete-service \
          --cluster my-cluster \
          --service my-service-blue \
          --force
```

**Verification:**
- [ ] Deployments successful to all environments
- [ ] Environment-specific configs applied
- [ ] Health checks passing
- [ ] Rollback mechanism works
- [ ] Notifications sent

**If This Fails:**
→ Test deployment locally/manually first
→ Verify deployment credentials
→ Check target environment accessibility
→ Review deployment logs
→ Test rollback procedure

---

### Step 7: Implement Monitoring and Notifications

**What:** Add monitoring, alerting, and notifications for pipeline and deployments

**How:**
Integrate with communication tools and monitoring platforms.

**Code/Commands:**

```yaml
# Notification job
notify:
  runs-on: ubuntu-latest
  needs: [deploy-staging, deploy-production]
  if: always()
  
  steps:
    - name: Slack notification
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: |
          Pipeline Status: ${{ job.status }}
          Repository: ${{ github.repository }}
          Branch: ${{ github.ref }}
          Commit: ${{ github.sha }}
          Author: ${{ github.actor }}
          Build: ${{ github.run_number }}
        fields: repo,commit,author,action,ref,took
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
    
    - name: Email notification
      uses: dawidd6/action-send-mail@v3
      with:
        server_address: smtp.gmail.com
        server_port: 587
        username: ${{ secrets.EMAIL_USERNAME }}
        password: ${{ secrets.EMAIL_PASSWORD }}
        subject: Pipeline ${{ job.status }} - ${{ github.repository }}
        to: team@example.com
        from: ci-cd@example.com
        body: |
          Pipeline execution completed with status: ${{ job.status }}
          
          Details:
          - Repository: ${{ github.repository }}
          - Branch: ${{ github.ref }}
          - Commit: ${{ github.sha }}
          - Author: ${{ github.actor }}
          - URL: ${{ github.event.head_commit.url }}
    
    - name: Post to Microsoft Teams
      uses: jdcargile/ms-teams-notification@v1.3
      with:
        github-token: ${{ github.token }}
        ms-teams-webhook-uri: ${{ secrets.TEAMS_WEBHOOK }}
        notification-summary: 'Pipeline ${{ job.status }}'
        notification-color: ${{ job.status == 'success' && '28a745' || 'dc3545' }}
    
    - name: Create Jira ticket on failure
      if: failure()
      uses: atlassian/gajira-create@v3
      with:
        project: DEVOPS
        issuetype: Bug
        summary: 'Pipeline failure: ${{ github.repository }}'
        description: |
          Pipeline failed for commit ${{ github.sha }}
          
          Run URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        fields: '{"labels": ["ci-failure", "auto-created"]}'
      env:
        JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
        JIRA_USER_EMAIL: ${{ secrets.JIRA_USER_EMAIL }}
        JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
```

**Pipeline Metrics Dashboard:**
```bash
# Create metrics collection script
cat > collect_metrics.sh <<'EOF'
#!/bin/bash

# Collect pipeline metrics
PIPELINE_DURATION=$1
PIPELINE_STATUS=$2
DEPLOY_ENV=$3

# Send to monitoring system (DataDog example)
curl -X POST "https://api.datadoghq.com/api/v1/series?api_key=${DD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @- << JSON
{
  "series": [
    {
      "metric": "cicd.pipeline.duration",
      "points": [[$(date +%s), ${PIPELINE_DURATION}]],
      "type": "gauge",
      "tags": ["env:${DEPLOY_ENV}", "status:${PIPELINE_STATUS}"]
    },
    {
      "metric": "cicd.deployment.count",
      "points": [[$(date +%s), 1]],
      "type": "count",
      "tags": ["env:${DEPLOY_ENV}"]
    }
  ]
}
JSON
EOF

chmod +x collect_metrics.sh
```

**Verification:**
- [ ] Notifications working for success/failure
- [ ] Team receives alerts
- [ ] Metrics being collected
- [ ] Dashboard shows pipeline status
- [ ] Escalation procedures documented

**If This Fails:**
→ Test webhook URLs independently
→ Check notification service credentials
→ Verify network access to notification services
→ Review notification thresholds

---

### Step 8: Document and Optimize Pipeline

**What:** Create comprehensive documentation and optimize pipeline performance

**How:**
Document the pipeline, measure performance, and implement optimizations.

**Code/Commands:**

```bash
# Create pipeline documentation
cat > docs/CICD_PIPELINE.md <<'EOF'
# CI/CD Pipeline Documentation

## Overview
Our CI/CD pipeline automatically builds, tests, and deploys code changes.

## Pipeline Stages

### 1. Build & Test (5-10 min)
- Install dependencies
- Run linters
- Execute unit tests
- Generate code coverage

### 2. Security Scan (3-5 min)
- Dependency vulnerability scan
- Container image scan
- Secret detection
- License compliance

### 3. Package (2-3 min)
- Build Docker image
- Tag with version
- Push to registry

### 4. Deploy Staging (5 min)
- Deploy to staging environment
- Run smoke tests
- Automated - no approval needed

### 5. Deploy Production (5 min)
- Deploy to production
- Run smoke tests
- Requires manual approval

## Triggering the Pipeline

**Automatic Triggers:**
- Push to `main` branch → Full pipeline with staging deployment
- Push to `develop` branch → Build and test only
- Pull request → Build, test, security scan

**Manual Triggers:**
- GitHub Actions UI → Run workflow → Run workflow button
- GitHub CLI: `gh workflow run ci-cd.yml`

## Environment Variables

| Variable | Description | Required | Where Set |
|----------|-------------|----------|-----------|
| DOCKER_USERNAME | Docker registry username | Yes | Repo secrets |
| DOCKER_PASSWORD | Docker registry password | Yes | Repo secrets |
| KUBE_CONFIG_STAGING | Kubernetes config for staging | Yes | Environment |
| KUBE_CONFIG_PRODUCTION | Kubernetes config for production | Yes | Environment |
| SLACK_WEBHOOK | Slack notification webhook | No | Repo secrets |

## Deployment Approval

Production deployments require approval from:
- DevOps team member
- Product owner (for major releases)

Approval via: GitHub Actions → Environments → production → Review deployments

## Rollback Procedure

If deployment fails or issues detected:

1. **Automatic Rollback:** Pipeline rolls back automatically on health check failure
2. **Manual Rollback:**
   ```bash
   # Revert to previous version
   kubectl rollout undo deployment/myapp -n production
   
   # Or specific revision
   kubectl rollout undo deployment/myapp -n production --to-revision=2
   ```

## Troubleshooting

### Pipeline Stuck
- Check runner availability
- Review logs for specific errors
- Cancel and restart if necessary

### Tests Failing
- Run tests locally first
- Check test environment setup
- Review test dependencies

### Deployment Failing
- Verify credentials are current
- Check target environment health
- Review deployment logs

## Pipeline Metrics

Track these metrics:
- Build success rate (target: >95%)
- Average build time (target: <15 min)
- Deployment frequency (target: multiple per day)
- Mean time to recovery (target: <30 min)

## Optimization Tips

1. **Cache Dependencies:** Use GitHub Actions cache
2. **Parallel Jobs:** Run independent jobs in parallel
3. **Conditional Execution:** Skip unnecessary steps
4. **Self-Hosted Runners:** For faster builds (if needed)

## Support

Questions? Contact:
- DevOps Team: #devops-help
- On-call: oncall@example.com
EOF

# Pipeline optimization script
cat > optimize_pipeline.sh <<'EOF'
#!/bin/bash

echo "Analyzing pipeline performance..."

# Measure average pipeline duration
echo "Average pipeline duration (last 30 runs):"
gh run list --limit 30 --json durationMs \
  --jq '[.[] | .durationMs] | add/length / 60000'

# Identify slowest jobs
echo ""
echo "Slowest jobs:"
gh run list --limit 10 --json databaseId \
  --jq '.[].databaseId' | while read run_id; do
    gh run view $run_id --json jobs \
      --jq '.jobs[] | "\(.name): \(.durationMs/60000) min"'
  done | sort -t: -k2 -nr | head -5

# Check for failed runs
echo ""
echo "Recent failures:"
gh run list --limit 50 --json conclusion,databaseId,displayTitle \
  --jq '.[] | select(.conclusion=="failure") | .displayTitle'

echo ""
echo "Optimization suggestions:"
echo "1. Cache node_modules between runs"
echo "2. Run tests and linting in parallel"
echo "3. Use matrix builds for multi-version testing"
echo "4. Implement incremental builds"
EOF

chmod +x optimize_pipeline.sh
```

**Performance Optimizations:**
```yaml
# Caching example
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

# Parallel execution
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    # runs in parallel with integration-tests
  
  integration-tests:
    runs-on: ubuntu-latest
    # runs in parallel with unit-tests

# Conditional execution
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**Verification:**
- [ ] Documentation complete and accessible
- [ ] Pipeline performance measured
- [ ] Optimizations implemented
- [ ] Team trained on pipeline usage
- [ ] Runbooks created for common issues

**If This Fails:**
→ Start with basic documentation
→ Add details incrementally
→ Gather team feedback
→ Update based on real usage

---

## Verification Checklist

- [ ] CI/CD platform selected and configured
- [ ] Pipeline file created and committed
- [ ] All secrets/credentials configured
- [ ] Automated tests running
- [ ] Code quality checks integrated
- [ ] Security scans passing
- [ ] Deployments automated to all environments
- [ ] Monitoring and notifications working
- [ ] Documentation complete
- [ ] Team trained on pipeline

---

## Common Issues & Solutions

### Issue: Pipeline Failing to Start

**Symptoms:**
- Workflow doesn't trigger on push
- No pipeline runs visible

**Solution:**
```bash
# Check workflow file location
ls -la .github/workflows/

# Validate YAML syntax
yamllint .github/workflows/ci-cd.yml

# Check branch protection rules
gh api repos/:owner/:repo/branches/main/protection

# Force trigger manually
gh workflow run ci-cd.yml
```

**Prevention:**
- Validate YAML before committing
- Test with manual trigger first
- Check repository settings

---

### Issue: Secrets Not Available in Pipeline

**Symptoms:**
- "Secret not found" errors
- Authentication failures

**Solution:**
```bash
# List available secrets
gh secret list

# Verify secret name matches usage
# In workflow: ${{ secrets.DOCKER_PASSWORD }}
# Secret name must be exactly: DOCKER_PASSWORD

# Check secret scope (repo vs environment)
# Environment secrets need environment: name in job

# Re-create secret
gh secret set DOCKER_PASSWORD < password.txt
```

**Prevention:**
- Document required secrets
- Use consistent naming
- Test secrets after adding

---

### Issue: Deployment Timing Out

**Symptoms:**
- Deployment step exceeds time limit
- Health checks never pass

**Solution:**
```bash
# Increase timeout
timeout-minutes: 30

# Check deployment logs
kubectl logs deployment/myapp -n staging

# Verify health check endpoint
curl https://staging.example.com/health

# Check resource availability
kubectl describe deployment myapp -n staging
```

**Prevention:**
- Set appropriate timeouts
- Implement readiness probes
- Monitor resource usage
- Test deployments manually first

---

## Best Practices

### DO:
✅ **Use version control for pipeline configs** - Track all changes  
✅ **Implement proper secret management** - Never commit secrets  
✅ **Add automated testing** - Catch issues early  
✅ **Use quality gates** - Enforce standards  
✅ **Enable notifications** - Stay informed  
✅ **Document everything** - Enable team success  
✅ **Cache dependencies** - Faster builds  
✅ **Run jobs in parallel** - Reduce total time  
✅ **Use matrix builds** - Test multiple versions  
✅ **Implement gradual rollouts** - Reduce risk

### DON'T:
❌ **Skip testing** - Defeats CI/CD purpose  
❌ **Commit secrets** - Security breach  
❌ **Deploy without approval** - Production needs gates  
❌ **Ignore failures** - Fix broken pipelines immediately  
❌ **Over-complicate** - Start simple, iterate  
❌ **Skip rollback testing** - Must be able to revert  
❌ **Forget monitoring** - Need visibility  
❌ **Hardcode values** - Use variables  
❌ **Deploy untested code** - Quality gates essential  
❌ **Ignore performance** - Slow pipelines hurt productivity

---

## Related Workflows

**Prerequisites:**
- [Docker Container Creation](./docker_container_creation.md) - Container images
- [Kubernetes Deployment](./kubernetes_deployment.md) - Deployment targets
- [Infrastructure as Code with Terraform](./infrastructure_as_code_terraform.md) - Infrastructure setup

**Next Steps:**
- [Application Monitoring Setup](./application_monitoring_setup.md) - Monitor deployments
- [Incident Response Workflow](./incident_response_workflow.md) - Handle production issues
- [Rollback Procedure](./rollback_procedure.md) - Revert bad deployments

**Alternatives:**
- Jenkins - Traditional CI/CD server
- CircleCI - Cloud-based CI/CD
- Travis CI - GitHub-focused CI/CD
- Azure DevOps - Microsoft ecosystem

---

## Tags
`devops` `ci-cd` `automation` `github-actions` `gitlab-ci` `jenkins` `deployment` `continuous-integration` `continuous-deployment` `pipelines`
