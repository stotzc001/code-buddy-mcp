# Infrastructure as Code with Terraform

**ID:** devops-009  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Advanced  
**Estimated Time:** 2-4 hours  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for managing infrastructure as code using Terraform to provision, modify, and version cloud resources programmatically

**Why:** Infrastructure as Code (IaC) eliminates manual configuration, ensures consistency across environments, enables version control of infrastructure, facilitates disaster recovery, and makes infrastructure changes reviewable and auditable like application code.

**When to use:**
- Provisioning cloud infrastructure (AWS, Azure, GCP, etc.)
- Creating reproducible environments (dev, staging, production)
- Managing multi-cloud deployments
- Implementing disaster recovery infrastructure
- Enforcing infrastructure standards and compliance
- Scaling infrastructure programmatically

---

## Prerequisites

**Required:**
- [ ] Terraform installed (`terraform version`)
- [ ] Cloud provider account and credentials
- [ ] Understanding of cloud provider resources
- [ ] Version control (Git) setup
- [ ] Text editor with HCL syntax support

**Check before starting:**
```bash
# Verify Terraform installation
terraform version
# Expected: Terraform v1.5.0 or higher

# Check cloud provider CLI (AWS example)
aws --version
aws sts get-caller-identity

# Or for Azure
az --version
az account show

# Or for GCP
gcloud --version
gcloud config list

# Verify you have necessary permissions
# AWS: AdministratorAccess or specific resource permissions
# Azure: Contributor role
# GCP: Editor or specific roles
```

---

## Implementation Steps

### Step 1: Initialize Terraform Project

**What:** Set up Terraform project structure and configuration files

**How:**
Create a well-organized directory structure with proper state management and provider configuration.

**Code/Commands:**
```bash
# Create project structure
mkdir -p terraform-infrastructure/{environments,modules,scripts}
cd terraform-infrastructure

# Create directory structure
mkdir -p environments/{dev,staging,production}
mkdir -p modules/{networking,compute,database,monitoring}
mkdir -p scripts

# Main configuration files
cat > main.tf <<'EOF'
# Main Terraform configuration
# This file aggregates all module calls

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Remote state backend (critical for teams)
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
    }
  }
}
EOF

cat > variables.tf <<'EOF'
# Input variables
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}
EOF

cat > outputs.tf <<'EOF'
# Output values
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = module.networking.public_subnet_ids
}

output "instance_public_ip" {
  description = "Public IP of EC2 instance"
  value       = module.compute.instance_public_ip
  sensitive   = false
}
EOF

# Create terraform.tfvars for environment-specific values
cat > terraform.tfvars <<'EOF'
aws_region   = "us-east-1"
environment  = "dev"
project_name = "myapp"
vpc_cidr     = "10.0.0.0/16"
EOF

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

**Verification:**
- [ ] Terraform initialized successfully
- [ ] .terraform directory created
- [ ] Provider plugins downloaded
- [ ] No validation errors
- [ ] Files properly formatted

**If This Fails:**
→ Check Terraform version compatibility
→ Verify internet connectivity (for provider downloads)
→ Review provider configuration syntax
→ Ensure credentials are configured

---

### Step 2: Create Reusable Modules

**What:** Build modular, reusable infrastructure components

**How:**
Create modules for common patterns (VPC, compute, database) that can be reused across projects.

**Code/Commands:**
```hcl
# modules/networking/main.tf - VPC Module
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-vpc"
    }
  )
}

resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]
  
  map_public_ip_on_launch = true
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-subnet-${count.index + 1}"
      Type = "Public"
    }
  )
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-igw"
    }
  )
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-rt"
    }
  )
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# modules/networking/variables.tf
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}

# modules/networking/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}
```

```hcl
# modules/compute/main.tf - EC2 Module
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_security_group" "instance" {
  name_prefix = "${var.instance_name}-sg"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
    description = "SSH access"
  }
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.instance_name}-sg"
    }
  )
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.instance.id]
  key_name               = var.key_name
  
  user_data = templatefile("${path.module}/user-data.sh", {
    environment = var.environment
  })
  
  root_block_device {
    volume_size           = var.root_volume_size
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }
  
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # Enforce IMDSv2
    http_put_response_hop_limit = 1
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = var.instance_name
    }
  )
}

# modules/compute/user-data.sh
#!/bin/bash
set -euo pipefail

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | bash
usermod -aG docker ubuntu

# Install monitoring agent
# ...

echo "Instance setup complete for ${environment}"
```

**Use modules in main configuration:**
```hcl
# main.tf - Using modules
module "networking" {
  source = "./modules/networking"
  
  vpc_cidr           = var.vpc_cidr
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  project_name       = var.project_name
  
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

module "compute" {
  source = "./modules/compute"
  
  instance_name     = "${var.project_name}-app"
  instance_type     = var.environment == "production" ? "t3.large" : "t3.micro"
  vpc_id            = module.networking.vpc_id
  subnet_id         = module.networking.public_subnet_ids[0]
  key_name          = var.ssh_key_name
  environment       = var.environment
  allowed_ssh_cidrs = var.allowed_ssh_cidrs
  
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  depends_on = [module.networking]
}
```

**Verification:**
- [ ] Modules created with inputs/outputs
- [ ] Module documentation complete
- [ ] Variables properly typed
- [ ] Outputs defined
- [ ] Tags consistent

**If This Fails:**
→ Check module path references
→ Verify variable types match
→ Review module dependencies
→ Test modules in isolation

---

### Step 3: Plan Infrastructure Changes

**What:** Preview changes before applying to avoid surprises

**How:**
Use terraform plan to see what will be created, modified, or destroyed.

**Code/Commands:**
```bash
# Generate execution plan
terraform plan

# Save plan to file for review
terraform plan -out=tfplan

# Show saved plan in human-readable format
terraform show tfplan

# Show in JSON format for automation
terraform show -json tfplan | jq .

# Plan for specific target
terraform plan -target=module.compute

# Plan with different variable file
terraform plan -var-file=environments/production.tfvars

# Refresh state and plan
terraform plan -refresh-only

# Create detailed plan review script
cat > review-plan.sh <<'EOF'
#!/bin/bash
set -euo pipefail

ENV=${1:-dev}

echo "Reviewing Terraform plan for $ENV environment..."

# Generate plan
terraform plan \
  -var-file="environments/$ENV.tfvars" \
  -out="plans/$ENV.tfplan"

# Show plan
terraform show "plans/$ENV.tfplan"

# Extract resource changes
echo ""
echo "=== Resource Changes Summary ==="
terraform show -json "plans/$ENV.tfplan" | \
  jq -r '.resource_changes[] | "\(.change.actions[0]) \(.address)"' | \
  sort

# Check for destroys
DESTROYS=$(terraform show -json "plans/$ENV.tfplan" | \
  jq '[.resource_changes[] | select(.change.actions[] == "delete")] | length')

if [ "$DESTROYS" -gt 0 ]; then
  echo ""
  echo "⚠️  WARNING: Plan includes $DESTROYS resource deletions!"
  echo "Review carefully before applying."
fi
EOF

chmod +x review-plan.sh
./review-plan.sh dev
```

**Plan output analysis:**
```
# Terraform plan output symbols:
+ create       # New resource will be created
~ update       # Resource will be modified
- destroy      # Resource will be deleted
-/+ replace    # Resource will be destroyed and recreated
<= read        # Data source will be read

# Force replacement scenarios:
# - AMI change
# - Instance type change (sometimes)
# - Subnet change
# - Security group change (if not using vpc_security_group_ids)
```

**Verification:**
- [ ] Plan completes without errors
- [ ] Changes match expectations
- [ ] No unexpected deletions
- [ ] Dependencies correct
- [ ] Resource counts accurate

**If This Fails:**
→ Review error messages carefully
→ Check provider authentication
→ Verify resource dependencies
→ Check for circular dependencies

---

### Step 4: Apply Infrastructure Changes

**What:** Execute the plan to create/modify/destroy resources

**How:**
Use terraform apply with proper safeguards and approval.

**Code/Commands:**
```bash
# Apply changes interactively (requires approval)
terraform apply

# Apply saved plan (no approval needed)
terraform apply tfplan

# Apply with auto-approve (use with caution)
terraform apply -auto-approve

# Apply specific targets
terraform apply -target=module.networking

# Apply with parallelism control
terraform apply -parallelism=10

# Create safe apply script
cat > apply.sh <<'EOF'
#!/bin/bash
set -euo pipefail

ENV=${1:-dev}
PLAN_FILE="plans/$ENV.tfplan"

echo "🚀 Applying Terraform for $ENV environment..."

# Ensure we have a plan
if [ ! -f "$PLAN_FILE" ]; then
  echo "No plan file found. Run: terraform plan -out=$PLAN_FILE"
  exit 1
fi

# Show plan one more time
echo "Plan to be applied:"
terraform show "$PLAN_FILE"

# Confirm
read -p "Apply this plan? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
  echo "Apply cancelled"
  exit 0
fi

# Apply
terraform apply "$PLAN_FILE"

# Cleanup plan file
rm "$PLAN_FILE"

echo "✅ Apply complete!"

# Show outputs
terraform output
EOF

chmod +x apply.sh

# Safe application process
terraform plan -out=tfplan
# Review the plan
./apply.sh dev

# Verify changes
terraform show
```

**Rollback strategy:**
```bash
# If apply fails or causes issues:

# 1. Check current state
terraform show

# 2. Taint resources for recreation
terraform taint module.compute.aws_instance.app

# 3. Or destroy and recreate specific resources
terraform destroy -target=module.compute.aws_instance.app
terraform apply -target=module.compute.aws_instance.app

# 4. Or rollback by reverting code and reapplying
git revert HEAD
terraform apply

# 5. Or restore from state backup
cp terraform.tfstate.backup terraform.tfstate
terraform apply
```

**Verification:**
- [ ] Apply completed successfully
- [ ] All resources created
- [ ] Outputs displayed
- [ ] State file updated
- [ ] Resources accessible

**If This Fails:**
→ Review error messages for specific resource
→ Check resource limits/quotas
→ Verify permissions
→ Check for API rate limiting
→ Review Terraform logs: `TF_LOG=DEBUG terraform apply`

---

### Step 5: Manage Terraform State

**What:** Properly handle state files for collaboration and safety

**How:**
Use remote state backend with locking and implement state management best practices.

**Code/Commands:**
```bash
# Set up S3 backend for remote state
cat > backend.tf <<'EOF'
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    
    # Enable versioning on S3 bucket for state history
  }
}
EOF

# Create S3 bucket and DynamoDB table for backend
cat > backend-setup.tf <<'EOF'
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-terraform-state-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "Terraform State"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  tags = {
    Name        = "Terraform State Locks"
    ManagedBy   = "Terraform"
  }
}

data "aws_caller_identity" "current" {}
EOF

# Initialize backend
terraform apply  # Create backend resources
terraform init -migrate-state  # Migrate to remote backend

# State management commands
terraform state list  # List all resources in state
terraform state show module.networking.aws_vpc.main  # Show specific resource
terraform state mv module.old.aws_instance.app module.new.aws_instance.app  # Move resource
terraform state rm module.compute.aws_instance.app  # Remove from state (doesn't destroy)
terraform state pull > terraform.tfstate.backup  # Backup state
terraform state push terraform.tfstate.backup  # Restore state (dangerous!)

# Import existing resources
terraform import module.compute.aws_instance.app i-1234567890abcdef0

# Refresh state from actual infrastructure
terraform refresh

# Create state management script
cat > manage-state.sh <<'EOF'
#!/bin/bash
set -euo pipefail

ACTION=${1:-list}

case "$ACTION" in
  backup)
    terraform state pull > "backups/terraform.tfstate.$(date +%Y%m%d-%H%M%S)"
    echo "State backed up"
    ;;
  list)
    terraform state list
    ;;
  show)
    terraform state show "$2"
    ;;
  unlock)
    terraform force-unlock "$2"
    ;;
  *)
    echo "Usage: $0 {backup|list|show|unlock}"
    exit 1
    ;;
esac
EOF

chmod +x manage-state.sh
```

**Verification:**
- [ ] State stored remotely
- [ ] State locking working
- [ ] State versioning enabled
- [ ] State encrypted
- [ ] Backups automated

**If This Fails:**
→ Check S3 bucket permissions
→ Verify DynamoDB table exists
→ Review state lock timeout
→ Manually unlock if needed: `terraform force-unlock <lock-id>`

---

### Step 6: Implement Environment-Specific Configurations

**What:** Manage multiple environments (dev, staging, production) with Terraform

**How:**
Use workspaces or separate directories with shared modules.

**Code/Commands:**
```bash
# Method 1: Terraform Workspaces
terraform workspace list
terraform workspace new dev
terraform workspace new staging
terraform workspace new production
terraform workspace select dev

# Use workspace in configuration
locals {
  environment = terraform.workspace
  
  instance_type = {
    dev        = "t3.micro"
    staging    = "t3.small"
    production = "t3.large"
  }
}

resource "aws_instance" "app" {
  instance_type = local.instance_type[local.environment]
  # ...
}

# Method 2: Separate Directories (Recommended)
# terraform-infrastructure/
# ├── modules/
# │   ├── networking/
# │   └── compute/
# ├── environments/
# │   ├── dev/
# │   │   ├── main.tf
# │   │   ├── variables.tf
# │   │   └── terraform.tfvars
# │   ├── staging/
# │   │   ├── main.tf
# │   │   ├── variables.tf
# │   │   └── terraform.tfvars
# │   └── production/
# │       ├── main.tf
# │       ├── variables.tf
# │       └── terraform.tfvars

# environments/dev/terraform.tfvars
cat > environments/dev/terraform.tfvars <<'EOF'
aws_region        = "us-east-1"
environment       = "dev"
instance_type     = "t3.micro"
min_instances     = 1
max_instances     = 2
enable_monitoring = false
EOF

# environments/production/terraform.tfvars
cat > environments/production/terraform.tfvars <<'EOF'
aws_region        = "us-east-1"
environment       = "production"
instance_type     = "t3.large"
min_instances     = 3
max_instances     = 10
enable_monitoring = true
enable_backups    = true
EOF

# Deploy specific environment
cd environments/dev
terraform init
terraform plan
terraform apply

# Or use from root with var-file
terraform plan -var-file=environments/dev/terraform.tfvars
```

**Verification:**
- [ ] Multiple environments configured
- [ ] Environment-specific values set
- [ ] Resources properly isolated
- [ ] State separated per environment
- [ ] Naming conventions consistent

**If This Fails:**
→ Check variable precedence
→ Verify state backend configuration
→ Review workspace selection
→ Ensure variable files loaded correctly

---

### Step 7: Implement Testing and Validation

**What:** Test Terraform code before applying to production

**How:**
Use terraform validate, tflint, and automated testing frameworks.

**Code/Commands:**
```bash
# Install tflint
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Install checkov (security scanner)
pip install checkov

# Create pre-commit hooks
cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
      - id: terraform_tfsec
EOF

# Validation script
cat > validate.sh <<'EOF'
#!/bin/bash
set -euo pipefail

echo "🔍 Running Terraform validation..."

# Format check
echo "Checking formatting..."
terraform fmt -check -recursive || {
  echo "❌ Code not formatted. Run: terraform fmt -recursive"
  exit 1
}

# Validate
echo "Validating configuration..."
terraform validate || {
  echo "❌ Validation failed"
  exit 1
}

# TFLint
echo "Running tflint..."
tflint --init
tflint || {
  echo "❌ TFLint found issues"
  exit 1
}

# Checkov security scan
echo "Running security scan..."
checkov -d . --quiet || {
  echo "⚠️  Security issues found"
}

echo "✅ All validations passed!"
EOF

chmod +x validate.sh
./validate.sh

# Terratest for automated testing (Go)
cat > test/terraform_test.go <<'EOF'
package test

import (
  "testing"
  "github.com/gruntwork-io/terratest/modules/terraform"
  "github.com/stretchr/testify/assert"
)

func TestTerraformInfrastructure(t *testing.T) {
  terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
    TerraformDir: "../environments/dev",
  })
  
  defer terraform.Destroy(t, terraformOptions)
  terraform.InitAndApply(t, terraformOptions)
  
  vpcId := terraform.Output(t, terraformOptions, "vpc_id")
  assert.NotEmpty(t, vpcId)
}
EOF
```

**Verification:**
- [ ] Validation passes
- [ ] Linting rules enforced
- [ ] Security scans clean
- [ ] Tests automated
- [ ] Pre-commit hooks working

**If This Fails:**
→ Fix linting errors
→ Address security findings
→ Update test cases
→ Review validation errors

---

### Step 8: Document and Version Infrastructure

**What:** Maintain comprehensive documentation and version control

**How:**
Generate docs automatically and follow version control best practices.

**Code/Commands:**
```bash
# Generate documentation
terraform-docs markdown table . > README.md

# Create comprehensive README
cat > README.md <<'EOF'
# Infrastructure as Code

## Architecture Overview
[Include architecture diagram]

## Prerequisites
- Terraform >= 1.5.0
- AWS CLI configured
- S3 bucket for state

## Usage

### Initialize
```bash
terraform init
```

### Deploy Development
```bash
cd environments/dev
terraform plan
terraform apply
```

### Deploy Production
```bash
cd environments/production
terraform plan -out=tfplan
# Review plan carefully
terraform apply tfplan
```

## Modules
- `networking`: VPC, subnets, routing
- `compute`: EC2 instances, ASG
- `database`: RDS instances
- `monitoring`: CloudWatch, alerting

## Inputs
[Auto-generated by terraform-docs]

## Outputs
[Auto-generated by terraform-docs]

## State Management
State is stored remotely in S3 with DynamoDB locking.

## Contributing
1. Create feature branch
2. Make changes
3. Run validation: `./validate.sh`
4. Submit PR
5. Apply after approval
EOF

# Version control best practices
cat > .gitignore <<'EOF'
# Terraform files
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
.terraform.lock.hcl

# Sensitive files
*.pem
*.key
terraform.tfvars  # Only if contains secrets

# OS files
.DS_Store
EOF

# Create CHANGELOG
cat > CHANGELOG.md <<'EOF'
# Changelog

## [1.2.0] - 2024-10-26
### Added
- Auto-scaling for production environment
- CloudWatch monitoring

### Changed
- Upgraded to Terraform 1.5.0
- Updated AWS provider to 5.0

### Fixed
- Security group rules for database access
EOF

# Tag infrastructure versions
git tag -a v1.2.0 -m "Production release 1.2.0"
git push origin v1.2.0
```

**Verification:**
- [ ] Documentation complete
- [ ] README up to date
- [ ] Changelog maintained
- [ ] Version tagged
- [ ] .gitignore configured

**If This Fails:**
→ Install terraform-docs
→ Review documentation completeness
→ Update diagrams

---

## Verification Checklist

- [ ] Terraform initialized
- [ ] Modules created and tested
- [ ] Infrastructure planned
- [ ] Changes applied successfully
- [ ] State managed remotely
- [ ] Multiple environments configured
- [ ] Validation automated
- [ ] Documentation complete
- [ ] Version controlled
- [ ] Team can collaborate

---

## Common Issues & Solutions

### Issue: State Lock Timeout

**Symptoms:**
- "Error acquiring state lock"
- Terraform operations blocked

**Solution:**
```bash
# Force unlock (use with caution!)
terraform force-unlock <lock-id>

# Check DynamoDB for lock
aws dynamodb scan --table-name terraform-locks

# Delete stale lock manually
aws dynamodb delete-item \
  --table-name terraform-locks \
  --key '{"LockID":{"S":"my-terraform-state/infrastructure/terraform.tfstate"}}'
```

**Prevention:**
- Use proper CI/CD to avoid concurrent runs
- Implement lock timeout in backend config
- Monitor lock table for stale locks

---

### Issue: Provider Authentication Failed

**Symptoms:**
- "Error configuring provider"
- Authentication errors

**Solution:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check profile
export AWS_PROFILE=myprofile

# Or use environment variables
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# Or use assume role
aws sts assume-role --role-arn arn:aws:iam::123456789:role/terraform
```

**Prevention:**
- Document authentication requirements
- Use IAM roles for CI/CD
- Rotate credentials regularly

---

## Best Practices

### DO:
✅ **Use remote state** - Enable collaboration  
✅ **State locking** - Prevent concurrent modifications  
✅ **Version control everything** - Track infrastructure changes  
✅ **Modularize code** - Reusable components  
✅ **Use variables** - Parameterize configurations  
✅ **Implement validation** - Catch errors early  
✅ **Document thoroughly** - Enable team understanding  
✅ **Tag resources** - Enable cost tracking  
✅ **Test before production** - Validate in lower environments  
✅ **Use semantic versioning** - Track infrastructure versions

### DON'T:
❌ **Commit state files** - Contains sensitive data  
❌ **Use local state in teams** - Causes conflicts  
❌ **Hardcode credentials** - Security risk  
❌ **Skip state backups** - Risk data loss  
❌ **Apply without plan** - Unexpected changes  
❌ **Use auto-approve in production** - Safety net removal  
❌ **Ignore validation errors** - Technical debt  
❌ **Mix manual and Terraform changes** - State drift  
❌ **Use latest versions without testing** - Compatibility issues  
❌ **Skip documentation** - Team confusion

---

## Related Workflows

**Prerequisites:**
- [Cloud Provider Setup](./cloud_provider_setup.md) - Configure cloud accounts

**Next Steps:**
- [Kubernetes Deployment](./kubernetes_deployment.md) - Deploy K8s with Terraform
- [CI/CD Pipeline Setup](./cicd_pipeline_setup.md) - Automate Terraform
- [Application Monitoring Setup](./application_monitoring_setup.md) - Monitor infrastructure

**Alternatives:**
- CloudFormation (AWS-specific)
- Pulumi (Programming languages)
- Ansible (Configuration management)

---

## Tags
`devops` `terraform` `infrastructure-as-code` `iac` `automation` `cloud` `aws` `azure` `gcp` `infrastructure`
