# Cloud Provider Setup

**ID:** dvo-014  
**Category:** DevOps  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 45-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive guide for setting up and configuring major cloud providers (AWS, Azure, GCP) for development and production environments.

**Why:** Proper cloud setup ensures secure, cost-effective, and manageable infrastructure with appropriate access controls, monitoring, and resource organization.

**When to use:**
- Starting a new project requiring cloud infrastructure
- Onboarding team members to cloud resources
- Setting up development, staging, or production environments
- Migrating from on-premise to cloud
- Implementing multi-cloud strategy

---

## Prerequisites

**Required:**
- [ ] Administrative access to cloud account(s)
- [ ] Credit card or billing information for account setup
- [ ] Basic understanding of cloud concepts (IaaS, PaaS, regions, zones)
- [ ] Command-line familiarity
- [ ] Organization's security and compliance requirements documented

**Recommended:**
- [ ] Multi-factor authentication device
- [ ] Password manager for credential management
- [ ] Infrastructure-as-Code tool preference defined (Terraform, Pulumi, CloudFormation)
- [ ] Cost budget and alerts defined

**Check before starting:**
```bash
# Verify you have necessary tools
which curl wget || echo "Install curl/wget"
which python3 || echo "Install Python 3.8+"

# Check internet connectivity
ping -c 3 google.com

# Verify you have admin rights (Linux/Mac)
sudo -v

# Windows: Run PowerShell as Administrator
# Get-ExecutionPolicy should return 'RemoteSigned' or 'Unrestricted'
```

---

## Implementation Steps

### Step 1: Choose Your Cloud Provider(s)

**What:** Select the appropriate cloud provider(s) based on your project requirements, budget, and technical needs.

**How:**

**Decision Matrix:**

| Factor | AWS | Azure | GCP |
|--------|-----|-------|-----|
| Market Share | 33% (Largest) | 22% (Second) | 10% (Third) |
| Best For | General purpose, startups, mature services | Microsoft stack, enterprise, hybrid cloud | Data/ML, Kubernetes, cost-conscious |
| Free Tier | 12 months + always free | 12 months + $200 credit | $300 credit (90 days) + always free |
| Pricing | Complex, many options | Similar to AWS | Simpler, often cheaper |
| Learning Curve | Moderate | Moderate-High | Low-Moderate |
| Service Count | 200+ | 200+ | 100+ |
| Kubernetes | EKS (managed) | AKS (best integration) | GKE (originated here) |
| ML/AI Services | Comprehensive | Comprehensive | Best-in-class |

**Common Combinations:**
- **Single Provider:** Start simple, grow complex
- **Multi-Cloud:** AWS for compute + GCP for ML + Azure for Office integration
- **Hybrid:** On-premise + Cloud for compliance/latency

**Selection Criteria:**
```python
# Decision helper
def choose_provider(requirements):
    if 'microsoft_stack' in requirements:
        return 'Azure'
    elif 'ml_heavy' in requirements or 'kubernetes_focus' in requirements:
        return 'GCP'
    elif 'enterprise' in requirements or 'startup' in requirements:
        return 'AWS'
    else:
        return 'AWS'  # Default: largest ecosystem

# Example
requirements = ['startup', 'api_backend', 'scaling_needed']
provider = choose_provider(requirements)  # Returns 'AWS'
```

**Verification:**
- [ ] Provider selection documented with rationale
- [ ] Cost estimates obtained for expected usage
- [ ] Compliance requirements reviewed (GDPR, HIPAA, SOC2)
- [ ] Team skill set assessed for chosen provider

**If This Fails:**
→ Revisit requirements with stakeholders
→ Consider starting with free tier of multiple providers for evaluation
→ Engage with cloud provider sales/solution architects for guidance

---

### Step 2: Create Cloud Account and Set Up Billing

**What:** Register for cloud provider account(s) and configure billing alerts and budgets to prevent unexpected costs.

**How:**

#### AWS Account Setup

```bash
# 1. Create AWS Account
# Visit: https://aws.amazon.com/
# - Click "Create an AWS Account"
# - Provide email, password, account name
# - Enter payment information
# - Verify phone number
# - Select support plan (Basic is free)

# 2. Enable MFA on Root Account (CRITICAL)
# AWS Console → Account (top right) → Security Credentials → MFA
# Use authenticator app (Authy, Google Authenticator)

# 3. Set up AWS Organizations (for multi-account)
aws organizations create-organization --feature-set ALL

# 4. Create billing alerts
aws cloudwatch put-metric-alarm \
  --alarm-name "BillingAlert" \
  --alarm-description "Alert when charges exceed $50" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1

# 5. Create budget
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json:**
```json
{
  "BudgetName": "Monthly-Budget",
  "BudgetType": "COST",
  "TimeUnit": "MONTHLY",
  "BudgetLimit": {
    "Amount": "100",
    "Unit": "USD"
  }
}
```

**notifications.json:**
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  }
]
```

#### Azure Account Setup

```bash
# 1. Create Azure Account
# Visit: https://azure.microsoft.com/free/
# - Sign up with Microsoft account
# - Verify identity (phone/credit card)
# - Get $200 credit for 30 days

# 2. Install Azure CLI
# Mac/Linux:
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows (PowerShell as Admin):
# Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
# Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'

# 3. Login
az login

# 4. Enable MFA
az ad user update --id your-user@domain.com --force-change-password-next-sign-in true

# 5. Create budget alert
az consumption budget create \
  --budget-name "MonthlyBudget" \
  --amount 100 \
  --time-grain Monthly \
  --start-date "2025-11-01" \
  --end-date "2026-10-31" \
  --resource-group "myResourceGroup"
```

#### GCP Account Setup

```bash
# 1. Create GCP Account
# Visit: https://console.cloud.google.com/
# - Sign in with Google account
# - Accept terms, set billing
# - Get $300 free credit (90 days)

# 2. Install gcloud CLI
# Mac:
brew install google-cloud-sdk

# Linux:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Windows: Download installer from cloud.google.com/sdk

# 3. Initialize gcloud
gcloud init
gcloud auth login

# 4. Enable billing alerts
# GCP Console → Billing → Budgets & alerts
# Or via gcloud:
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Monthly Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

**Verification:**
- [ ] Account created and accessible
- [ ] MFA enabled on root/admin account
- [ ] Billing alerts configured ($50, $100, $150 thresholds)
- [ ] Monthly budget set
- [ ] Payment method verified
- [ ] Tax information provided (if applicable)

**If This Fails:**
→ Verify credit card is accepted (international cards may have issues)
→ Check for email verification requirements
→ Contact cloud provider support for account issues
→ Use prepaid cards if credit card unavailable

---

### Step 3: Install and Configure Cloud CLI Tools

**What:** Install official command-line tools for your chosen cloud provider(s) to enable infrastructure management, deployment, and automation.

**How:**

#### AWS CLI Installation

```bash
# Mac/Linux:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version  # Should show aws-cli/2.x.x

# Configure AWS CLI
aws configure
# Enter when prompted:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)

# Test configuration
aws sts get-caller-identity
# Should return your account ID, user ARN

# Configure named profiles for multiple accounts
aws configure --profile production
aws configure --profile development

# Use specific profile
aws s3 ls --profile production
```

**~/.aws/credentials:**
```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[production]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
region = us-east-1

[development]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
region = us-west-2
```

#### Azure CLI Configuration

```bash
# Already installed in Step 2

# Login (opens browser)
az login

# List subscriptions
az account list --output table

# Set default subscription
az account set --subscription "My Subscription Name"

# Configure defaults
az configure --defaults location=eastus group=myResourceGroup

# Test configuration
az account show
```

#### GCP CLI Configuration

```bash
# Already installed in Step 2

# Login
gcloud auth login

# Set default project
gcloud config set project PROJECT_ID

# Set default region/zone
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a

# Create configuration for different environments
gcloud config configurations create production
gcloud config configurations create development

# Activate configuration
gcloud config configurations activate production
gcloud config set project prod-project-id

# List all configurations
gcloud config configurations list

# Test configuration
gcloud compute instances list
```

**Multi-Cloud CLI Script:**

```bash
# ~/bin/cloud-setup.sh
#!/bin/bash

setup_aws() {
    echo "Setting up AWS CLI..."
    if ! command -v aws &> /dev/null; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    fi
    aws configure
    echo "AWS CLI configured!"
}

setup_azure() {
    echo "Setting up Azure CLI..."
    if ! command -v az &> /dev/null; then
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    fi
    az login
    echo "Azure CLI configured!"
}

setup_gcp() {
    echo "Setting up GCP CLI..."
    if ! command -v gcloud &> /dev/null; then
        curl https://sdk.cloud.google.com | bash
        exec -l $SHELL
    fi
    gcloud init
    echo "GCP CLI configured!"
}

# Main menu
echo "Cloud Provider Setup"
echo "1) AWS"
echo "2) Azure"
echo "3) GCP"
echo "4) All"
read -p "Select option: " choice

case $choice in
    1) setup_aws ;;
    2) setup_azure ;;
    3) setup_gcp ;;
    4) setup_aws; setup_azure; setup_gcp ;;
    *) echo "Invalid option" ;;
esac
```

**Verification:**
- [ ] CLI tools installed and in PATH
- [ ] Successfully authenticated to cloud provider
- [ ] Default regions/zones configured
- [ ] Multiple profiles/configurations set up (dev/staging/prod)
- [ ] CLI commands execute without errors
- [ ] Credentials stored securely

**If This Fails:**
→ Check PATH environment variable includes CLI location
→ Verify credentials have correct permissions
→ Ensure firewall/proxy not blocking CLI requests
→ Try alternative authentication methods (SSO, browser-based)
→ Check CLI version compatibility

---

### Step 4: Set Up IAM Users, Roles, and Permissions

**What:** Create Identity and Access Management (IAM) structure with users, service accounts, roles, and policies following principle of least privilege.

**How:**

#### AWS IAM Setup

```bash
# 1. Create IAM admin user (don't use root account)
aws iam create-user --user-name admin-user

# 2. Attach admin policy
aws iam attach-user-policy \
  --user-name admin-user \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# 3. Create access keys
aws iam create-access-key --user-name admin-user > admin-keys.json
# IMPORTANT: Store these keys securely!

# 4. Create developer group with limited permissions
aws iam create-group --group-name Developers

# 5. Attach policies to group
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# 6. Create developer users
aws iam create-user --user-name developer1
aws iam add-user-to-group --user-name developer1 --group-name Developers

# 7. Create service role for EC2 instances
aws iam create-role \
  --role-name EC2-ServiceRole \
  --assume-role-policy-document file://trust-policy.json

# 8. Attach policies to role
aws iam attach-role-policy \
  --role-name EC2-ServiceRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

**trust-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Custom Policy Example (developer-policy.json):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "lambda:InvokeFunction"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "ec2:TerminateInstances",
        "rds:DeleteDBInstance",
        "s3:DeleteBucket"
      ],
      "Resource": "*"
    }
  ]
}
```

```bash
# Apply custom policy
aws iam create-policy \
  --policy-name DeveloperPolicy \
  --policy-document file://developer-policy.json

aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/DeveloperPolicy
```

#### Azure RBAC Setup

```bash
# 1. Create resource group
az group create --name MyResourceGroup --location eastus

# 2. Create service principal (for applications)
az ad sp create-for-rbac --name "myapp-service-principal" --role contributor \
  --scopes /subscriptions/SUBSCRIPTION_ID/resourceGroups/MyResourceGroup

# Output includes credentials - SAVE THESE:
# {
#   "appId": "...",
#   "password": "...",
#   "tenant": "..."
# }

# 3. Create custom role
az role definition create --role-definition developer-role.json
```

**developer-role.json:**
```json
{
  "Name": "Developer Custom Role",
  "Description": "Custom role for developers",
  "Actions": [
    "Microsoft.Compute/virtualMachines/start/action",
    "Microsoft.Compute/virtualMachines/restart/action",
    "Microsoft.Storage/storageAccounts/read",
    "Microsoft.Web/sites/*"
  ],
  "NotActions": [
    "Microsoft.Compute/virtualMachines/delete",
    "Microsoft.Storage/storageAccounts/delete"
  ],
  "AssignableScopes": [
    "/subscriptions/SUBSCRIPTION_ID"
  ]
}
```

```bash
# 4. Assign role to user
az role assignment create \
  --assignee user@domain.com \
  --role "Developer Custom Role" \
  --resource-group MyResourceGroup

# 5. List role assignments
az role assignment list --resource-group MyResourceGroup --output table
```

#### GCP IAM Setup

```bash
# 1. Create service account
gcloud iam service-accounts create my-app-sa \
  --description="Service account for my application" \
  --display-name="My App Service Account"

# 2. Grant roles to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-app-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# 3. Create and download key file
gcloud iam service-accounts keys create ~/key.json \
  --iam-account=my-app-sa@PROJECT_ID.iam.gserviceaccount.com

# 4. Grant role to user
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:developer@example.com" \
  --role="roles/editor"

# 5. Create custom role
gcloud iam roles create developer_role --project=PROJECT_ID \
  --title="Developer Role" \
  --description="Custom role for developers" \
  --permissions=compute.instances.list,compute.instances.get,storage.buckets.list \
  --stage=GA

# 6. List IAM policy
gcloud projects get-iam-policy PROJECT_ID
```

**IAM Best Practices Checklist:**

```bash
# Security audit script
#!/bin/bash

echo "🔒 IAM Security Audit"
echo "===================="

# AWS audit
if command -v aws &> /dev/null; then
    echo "AWS IAM Users:"
    aws iam list-users --output table
    
    echo "Users without MFA:"
    aws iam get-credential-report
    aws iam generate-credential-report
    
    echo "Root account usage (should be none):"
    aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=root
fi

# Check for overly permissive policies
echo "⚠️  Check for Administrator Access:"
aws iam list-entities-for-policy --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

**Verification:**
- [ ] Root/administrator account secured with MFA
- [ ] IAM users created for human access
- [ ] Service accounts/principals created for applications
- [ ] Roles follow principle of least privilege
- [ ] No hard-coded credentials in code
- [ ] Access keys rotated regularly (< 90 days)
- [ ] Unused accounts/keys removed
- [ ] Activity logging enabled (CloudTrail/Azure Monitor/Cloud Audit)

**If This Fails:**
→ Start with pre-built roles, customize later
→ Review permission errors in logs to identify missing permissions
→ Use cloud provider's policy simulator tools
→ Implement temporary elevated access for troubleshooting
→ Document all custom policies for audit purposes

---

### Step 5: Configure Networking and VPC/VNet

**What:** Set up virtual private cloud (VPC) networking with subnets, security groups, and routing for isolated and secure infrastructure.

**How:**

#### AWS VPC Setup

```bash
# 1. Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MyVPC}]'

# Get VPC ID from output
VPC_ID="vpc-xxxxx"

# 2. Enable DNS hostnames
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames

# 3. Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=MyIGW}]'

IGW_ID="igw-xxxxx"

# 4. Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID

# 5. Create public subnet
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=PublicSubnet}]'

PUBLIC_SUBNET_ID="subnet-xxxxx"

# 6. Create private subnet
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=PrivateSubnet}]'

PRIVATE_SUBNET_ID="subnet-xxxxx"

# 7. Create and configure route table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=PublicRT}]'

RT_ID="rtb-xxxxx"

# 8. Add route to Internet Gateway
aws ec2 create-route \
  --route-table-id $RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# 9. Associate route table with public subnet
aws ec2 associate-route-table \
  --subnet-id $PUBLIC_SUBNET_ID \
  --route-table-id $RT_ID

# 10. Create security group
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Security group for web servers" \
  --vpc-id $VPC_ID

SG_ID="sg-xxxxx"

# 11. Add security group rules
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_IP/32  # Replace with your IP
```

**Terraform VPC Module (Recommended):**

```hcl
# vpc.tf
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

#### Azure VNet Setup

```bash
# 1. Create virtual network
az network vnet create \
  --resource-group MyResourceGroup \
  --name MyVNet \
  --address-prefix 10.0.0.0/16 \
  --subnet-name DefaultSubnet \
  --subnet-prefix 10.0.1.0/24

# 2. Create additional subnet
az network vnet subnet create \
  --resource-group MyResourceGroup \
  --vnet-name MyVNet \
  --name PrivateSubnet \
  --address-prefix 10.0.2.0/24

# 3. Create Network Security Group
az network nsg create \
  --resource-group MyResourceGroup \
  --name WebServerNSG

# 4. Add NSG rules
az network nsg rule create \
  --resource-group MyResourceGroup \
  --nsg-name WebServerNSG \
  --name AllowHTTP \
  --priority 100 \
  --source-address-prefixes '*' \
  --destination-port-ranges 80 \
  --access Allow \
  --protocol Tcp

az network nsg rule create \
  --resource-group MyResourceGroup \
  --nsg-name WebServerNSG \
  --name AllowHTTPS \
  --priority 101 \
  --source-address-prefixes '*' \
  --destination-port-ranges 443 \
  --access Allow \
  --protocol Tcp

# 5. Associate NSG with subnet
az network vnet subnet update \
  --resource-group MyResourceGroup \
  --vnet-name MyVNet \
  --name DefaultSubnet \
  --network-security-group WebServerNSG
```

#### GCP VPC Setup

```bash
# 1. Create VPC network
gcloud compute networks create my-vpc --subnet-mode=custom

# 2. Create subnets
gcloud compute networks subnets create public-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.0.1.0/24

gcloud compute networks subnets create private-subnet \
  --network=my-vpc \
  --region=us-central1 \
  --range=10.0.2.0/24

# 3. Create firewall rules
gcloud compute firewall-rules create allow-http \
  --network=my-vpc \
  --allow=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

gcloud compute firewall-rules create allow-https \
  --network=my-vpc \
  --allow=tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

gcloud compute firewall-rules create allow-ssh \
  --network=my-vpc \
  --allow=tcp:22 \
  --source-ranges=YOUR_IP/32 \
  --target-tags=ssh-enabled

# 4. Create NAT gateway for private instances
gcloud compute routers create my-router \
  --network=my-vpc \
  --region=us-central1

gcloud compute routers nats create my-nat \
  --router=my-router \
  --region=us-central1 \
  --auto-allocate-nat-external-ips \
  --nat-all-subnet-ip-ranges
```

**Network Design Best Practices:**

```yaml
# network-design.yaml
vpc_design:
  cidr: "10.0.0.0/16"  # 65,536 IPs
  
  subnets:
    public:
      - name: "public-1a"
        cidr: "10.0.1.0/24"  # 256 IPs
        az: "us-east-1a"
      - name: "public-1b"
        cidr: "10.0.2.0/24"
        az: "us-east-1b"
    
    private:
      - name: "private-1a"
        cidr: "10.0.11.0/24"
        az: "us-east-1a"
      - name: "private-1b"
        cidr: "10.0.12.0/24"
        az: "us-east-1b"
    
    database:
      - name: "db-1a"
        cidr: "10.0.21.0/24"
        az: "us-east-1a"
      - name: "db-1b"
        cidr: "10.0.22.0/24"
        az: "us-east-1b"

  security_groups:
    web:
      ingress:
        - port: 80, source: "0.0.0.0/0"
        - port: 443, source: "0.0.0.0/0"
      egress:
        - all traffic
    
    app:
      ingress:
        - port: 8080, source: "web-sg"
      egress:
        - port: 5432, dest: "db-sg"
    
    db:
      ingress:
        - port: 5432, source: "app-sg"
      egress: []
```

**Verification:**
- [ ] VPC/VNet created with appropriate CIDR block
- [ ] Public and private subnets configured
- [ ] Internet Gateway attached (public access)
- [ ] NAT Gateway configured (private subnet internet access)
- [ ] Route tables properly configured
- [ ] Security groups/NSGs with least-privilege rules
- [ ] Multi-AZ setup for high availability
- [ ] Network ACLs configured (if needed)

**If This Fails:**
→ Check CIDR blocks don't overlap with existing networks
→ Verify route table associations are correct
→ Ensure security groups aren't too restrictive (test with 0.0.0.0/0, then narrow)
→ Use VPC flow logs to debug connectivity issues
→ Review NAT Gateway configuration for private subnet access

---

### Step 6: Configure Resource Tagging and Organization

**What:** Implement consistent tagging strategy for cost allocation, resource organization, automation, and compliance.

**How:**

#### Tagging Strategy

```yaml
# tagging-strategy.yaml
mandatory_tags:
  Environment:
    values: [dev, staging, production]
    description: "Deployment environment"
  
  Project:
    values: [projectA, projectB, infrastructure]
    description: "Project or product name"
  
  Owner:
    format: "email@company.com"
    description: "Team or person responsible"
  
  CostCenter:
    format: "CC-####"
    description: "Billing cost center"

optional_tags:
  Name:
    description: "Human-readable resource name"
  
  Application:
    description: "Application component"
  
  Backup:
    values: [true, false]
    description: "Include in backup policy"
  
  Compliance:
    values: [pci, hipaa, sox, gdpr]
    description: "Compliance requirements"
  
  ManagedBy:
    values: [terraform, cloudformation, manual]
    description: "Infrastructure management tool"
  
  CreatedBy:
    description: "Automation tool or user"
  
  CreatedDate:
    format: "YYYY-MM-DD"
    description: "Resource creation date"
```

#### AWS Tagging Implementation

```bash
# Tag existing resource
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags \
    Key=Name,Value=WebServer \
    Key=Environment,Value=production \
    Key=Project,Value=myapp \
    Key=Owner,Value=devops@company.com

# Tag multiple resources
aws ec2 create-tags \
  --resources i-xxx i-yyy i-zzz \
  --tags Key=Environment,Value=production

# Find untagged resources
aws resourcegroupstaggingapi get-resources \
  --resource-type-filters ec2:instance \
  --tag-filters Key=Environment

# Cost allocation tags
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status \
    Key=Environment,Status=Active \
    Key=Project,Status=Active

# Auto-tagging with Lambda
# lambda-autotag.py
import boto3
import json

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Extract instance ID from CloudWatch event
    instance_id = event['detail']['instance-id']
    
    # Get IAM user who created the instance
    creator = event['detail']['userIdentity']['principalId']
    
    # Apply tags
    ec2.create_tags(
        Resources=[instance_id],
        Tags=[
            {'Key': 'CreatedBy', 'Value': creator},
            {'Key': 'CreatedDate', 'Value': event['time'][:10]},
            {'Key': 'ManagedBy', 'Value': 'auto-tag'}
        ]
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Tagged {instance_id}')
    }
```

#### Azure Tagging Implementation

```bash
# Tag resource
az resource tag \
  --tags Environment=production Project=myapp Owner=devops@company.com \
  --resource-group MyResourceGroup \
  --name MyVM \
  --resource-type Microsoft.Compute/virtualMachines

# Tag resource group (inherited by resources)
az group update \
  --name MyResourceGroup \
  --tags Environment=production CostCenter=CC-1234

# List resources by tag
az resource list --tag Environment=production --output table

# Azure Policy for mandatory tags
# tag-policy.json
{
  "if": {
    "allOf": [
      {
        "field": "type",
        "equals": "Microsoft.Compute/virtualMachines"
      },
      {
        "field": "tags.Environment",
        "exists": "false"
      }
    ]
  },
  "then": {
    "effect": "deny"
  }
}
```

#### GCP Labeling Implementation

```bash
# Add labels to instance
gcloud compute instances add-labels my-instance \
  --labels=environment=production,project=myapp,owner=devops

# Update labels
gcloud compute instances update my-instance \
  --update-labels=new-label=value

# List resources by label
gcloud compute instances list \
  --filter="labels.environment=production"

# Remove label
gcloud compute instances remove-labels my-instance \
  --labels=old-label

# Bulk labeling script
gcloud compute instances list --format="value(name)" | while read instance; do
  gcloud compute instances add-labels $instance \
    --labels=managed-by=terraform,created-date=$(date +%Y-%m-%d)
done
```

#### Terraform Tagging (Cross-Cloud)

```hcl
# variables.tf
variable "common_tags" {
  type = map(string)
  default = {
    Environment = "production"
    ManagedBy   = "terraform"
    Project     = "myapp"
    Owner       = "devops@company.com"
  }
}

# main.tf
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = merge(
    var.common_tags,
    {
      Name = "web-server"
      Role = "webserver"
    }
  )
}

# Azure
resource "azurerm_virtual_machine" "web" {
  name                = "web-vm"
  location            = "eastus"
  resource_group_name = azurerm_resource_group.main.name
  
  tags = merge(
    var.common_tags,
    {
      name = "web-server"
      role = "webserver"
    }
  )
}

# GCP
resource "google_compute_instance" "web" {
  name         = "web-instance"
  machine_type = "e2-micro"
  zone         = "us-central1-a"

  labels = {
    environment = "production"
    managed_by  = "terraform"
    project     = "myapp"
    owner       = "devops"
  }
}
```

**Tag Compliance Monitoring:**

```python
# tag_audit.py
import boto3
from collections import defaultdict

def audit_aws_tags():
    """Audit AWS resources for missing mandatory tags"""
    required_tags = ['Environment', 'Project', 'Owner', 'CostCenter']
    issues = defaultdict(list)
    
    ec2 = boto3.client('ec2')
    
    # Check EC2 instances
    instances = ec2.describe_instances()
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            
            missing = [tag for tag in required_tags if tag not in tags]
            if missing:
                issues[instance_id] = missing
    
    # Report
    if issues:
        print("⚠️  TAGGING ISSUES FOUND:")
        for resource, missing_tags in issues.items():
            print(f"  {resource}: Missing {', '.join(missing_tags)}")
        return False
    else:
        print("✅ All resources properly tagged!")
        return True

if __name__ == '__main__':
    audit_aws_tags()
```

**Verification:**
- [ ] Tagging strategy documented
- [ ] All new resources automatically tagged
- [ ] Mandatory tags enforced via policy
- [ ] Cost allocation tags activated
- [ ] Tag compliance audit script running
- [ ] Tags consistent across all resources
- [ ] Tag-based access controls implemented (if needed)

**If This Fails:**
→ Start with minimal required tags, expand gradually
→ Use cloud provider's Tag Editor for bulk operations
→ Implement tag policies before enforcement (audit mode first)
→ Create automation for common tagging patterns
→ Regular tag audits (weekly/monthly)

---

### Step 7: Set Up Monitoring, Logging, and Alerting

**What:** Configure cloud-native monitoring, logging aggregation, and alerting to maintain visibility into infrastructure health and costs.

**How:**

#### AWS CloudWatch Setup

```bash
# 1. Create CloudWatch dashboard
aws cloudwatch put-dashboard --dashboard-name MyApp \
  --dashboard-body file://dashboard.json

# dashboard.json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "EC2 CPU Utilization"
      }
    }
  ]
}

# 2. Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-alarm \
  --alarm-description "Alarm when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:my-topic

# 3. Create SNS topic for notifications
aws sns create-topic --name infrastructure-alerts
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:infrastructure-alerts \
  --protocol email \
  --notification-endpoint devops@company.com

# 4. Enable CloudTrail for audit logging
aws cloudtrail create-trail \
  --name my-trail \
  --s3-bucket-name my-cloudtrail-bucket

aws cloudtrail start-logging --name my-trail

# 5. Create log group
aws logs create-log-group --log-group-name /aws/application/myapp

# 6. Create metric filter
aws logs put-metric-filter \
  --log-group-name /aws/application/myapp \
  --filter-name ErrorCount \
  --filter-pattern "[time, request_id, level = ERROR, msg]" \
  --metric-transformations \
    metricName=ApplicationErrors,metricNamespace=MyApp,metricValue=1
```

#### Azure Monitor Setup

```bash
# 1. Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group MyResourceGroup \
  --workspace-name MyWorkspace

# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group MyResourceGroup \
  --workspace-name MyWorkspace \
  --query customerId -o tsv)

# 2. Create action group
az monitor action-group create \
  --name DevOpsTeam \
  --resource-group MyResourceGroup \
  --short-name DevOps \
  --email-receiver name=admin email=devops@company.com

# 3. Create metric alert
az monitor metrics alert create \
  --name high-cpu \
  --resource-group MyResourceGroup \
  --scopes /subscriptions/xxx/resourceGroups/MyResourceGroup/providers/Microsoft.Compute/virtualMachines/MyVM \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group DevOpsTeam

# 4. Enable diagnostic settings
az monitor diagnostic-settings create \
  --name MyVMDiagnostics \
  --resource /subscriptions/xxx/resourceGroups/MyResourceGroup/providers/Microsoft.Compute/virtualMachines/MyVM \
  --workspace $WORKSPACE_ID \
  --logs '[{"category": "Administrative","enabled": true}]' \
  --metrics '[{"category": "AllMetrics","enabled": true}]'

# 5. Create availability test
az monitor app-insights web-test create \
  --resource-group MyResourceGroup \
  --name "Homepage Test" \
  --location "eastus" \
  --web-test-kind "ping" \
  --frequency 300 \
  --timeout 30 \
  --enabled true \
  --url "https://myapp.com"
```

#### GCP Monitoring Setup

```bash
# 1. Create alerting policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High CPU Alert" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/cpu/utilization"'

# 2. Create notification channel
gcloud alpha monitoring channels create \
  --display-name="Email DevOps" \
  --type=email \
  --channel-labels=email_address=devops@company.com

# 3. Create uptime check
gcloud monitoring uptime create https-check \
  --display-name="Website Uptime" \
  --resource-type=uptime-url \
  --host=myapp.com \
  --path=/ \
  --port=443

# 4. Create log-based metric
gcloud logging metrics create error_count \
  --description="Count of ERROR logs" \
  --log-filter='severity="ERROR"'

# 5. Create log sink
gcloud logging sinks create my-sink \
  storage.googleapis.com/my-logs-bucket \
  --log-filter='severity >= ERROR'
```

**Monitoring Dashboard (Grafana):**

```yaml
# docker-compose.yml for Grafana + Prometheus
version: '3'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
```

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cloudwatch'
    static_configs:
      - targets: ['cloudwatch-exporter:9090']
  
  - job_name: 'azure'
    static_configs:
      - targets: ['azure-exporter:9090']
  
  - job_name: 'gcp'
    static_configs:
      - targets: ['stackdriver-exporter:9090']
```

**Verification:**
- [ ] Monitoring dashboards created
- [ ] Critical metric alerts configured (CPU, memory, disk, network)
- [ ] Cost alerts and budgets active
- [ ] Log aggregation working
- [ ] Alert notifications tested
- [ ] Audit logging enabled (CloudTrail/Activity Log/Cloud Audit)
- [ ] Uptime checks configured for public endpoints
- [ ] Incident response runbooks linked to alerts

**If This Fails:**
→ Start with high-level metrics, add detailed monitoring incrementally
→ Test alert routing before production deployment
→ Use cloud provider's free tier monitoring first
→ Implement log filtering to reduce costs
→ Set up separate alerting channels for different severities

---

### Step 8: Document and Validate Setup

**What:** Create comprehensive documentation of cloud setup, validate all components, and establish operational procedures.

**How:**

#### Documentation Structure

```markdown
# Cloud Infrastructure Documentation

## 1. Overview
- Cloud Provider: AWS / Azure / GCP
- Account ID: xxx-xxx-xxx
- Primary Region: us-east-1
- Backup Region: us-west-2
- Environment: Production

## 2. Architecture Diagram
[Include network diagram, service map]

## 3. IAM Structure
### Users
- admin-user: Full access (MFA required)
- developer-1: PowerUser access

### Roles
- EC2-ServiceRole: S3 read-only
- Lambda-ExecutionRole: CloudWatch logs

### Policies
- DeveloperPolicy: Custom limited access

## 4. Network Configuration
### VPC: 10.0.0.0/16
- Public Subnets:
  - 10.0.1.0/24 (us-east-1a)
  - 10.0.2.0/24 (us-east-1b)
- Private Subnets:
  - 10.0.11.0/24 (us-east-1a)
  - 10.0.12.0/24 (us-east-1b)

### Security Groups
- web-sg: Ports 80, 443 open
- app-sg: Port 8080 from web-sg
- db-sg: Port 5432 from app-sg

## 5. Tagging Strategy
Mandatory tags: Environment, Project, Owner, CostCenter

## 6. Monitoring & Alerts
- Dashboard: cloudwatch.amazonaws.com/dashboard/MyApp
- Alerts: devops@company.com
- On-call: PagerDuty integration

## 7. Cost Management
- Monthly Budget: $1,000
- Alerts: 80%, 100%, 120%
- Optimization: Weekly reviews

## 8. Backup & DR
- RTO: 4 hours
- RPO: 1 hour
- Backup Location: us-west-2

## 9. Compliance
- Data Residency: US only
- Encryption: At rest and in transit
- Audit Logging: Enabled

## 10. Runbooks
- [Emergency Response](./runbooks/emergency.md)
- [Scaling Procedures](./runbooks/scaling.md)
- [Cost Optimization](./runbooks/cost-optimization.md)
```

#### Validation Checklist

```bash
#!/bin/bash
# cloud-validation.sh

echo "🔍 Cloud Setup Validation"
echo "========================="

# 1. Account Access
echo "1. Verifying account access..."
if aws sts get-caller-identity &> /dev/null; then
    echo "  ✅ AWS CLI configured"
else
    echo "  ❌ AWS CLI not configured"
fi

# 2. VPC Validation
echo "2. Validating VPC setup..."
VPC_COUNT=$(aws ec2 describe-vpcs --query 'Vpcs[*].VpcId' --output text | wc -w)
echo "  VPCs found: $VPC_COUNT"

# 3. Subnet Validation
echo "3. Validating subnets..."
SUBNET_COUNT=$(aws ec2 describe-subnets --query 'Subnets[*].SubnetId' --output text | wc -w)
echo "  Subnets found: $SUBNET_COUNT"

# 4. Security Group Validation
echo "4. Validating security groups..."
SG_COUNT=$(aws ec2 describe-security-groups --query 'SecurityGroups[*].GroupId' --output text | wc -w)
echo "  Security groups found: $SG_COUNT"

# 5. IAM User Validation
echo "5. Validating IAM users..."
USER_COUNT=$(aws iam list-users --query 'Users[*].UserName' --output text | wc -w)
echo "  IAM users found: $USER_COUNT"

# 6. Billing Alert Validation
echo "6. Validating billing alerts..."
ALARM_COUNT=$(aws cloudwatch describe-alarms --alarm-names BillingAlert --query 'MetricAlarms[*].AlarmName' --output text | wc -w)
if [ "$ALARM_COUNT" -gt 0 ]; then
    echo "  ✅ Billing alert configured"
else
    echo "  ❌ No billing alert found"
fi

# 7. CloudTrail Validation
echo "7. Validating CloudTrail..."
TRAIL_COUNT=$(aws cloudtrail describe-trails --query 'trailList[*].Name' --output text | wc -w)
if [ "$TRAIL_COUNT" -gt 0 ]; then
    echo "  ✅ CloudTrail enabled"
else
    echo "  ❌ CloudTrail not enabled"
fi

# 8. Tag Compliance
echo "8. Validating tagging compliance..."
UNTAGGED=$(aws resourcegroupstaggingapi get-resources --resource-type-filters ec2:instance --query 'ResourceTagMappingList[?Tags==`[]`]' | jq length)
echo "  Untagged resources: $UNTAGGED"

# 9. Cost Analysis
echo "9. Current month costs..."
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[*].Total.BlendedCost.Amount' \
  --output text

echo ""
echo "========================="
echo "Validation complete!"
```

#### Operational Procedures

```bash
# Daily Operations Checklist
daily_ops.sh

#!/bin/bash

echo "📋 Daily Operations Checklist"
echo "============================="

# 1. Check for any alerts/incidents
echo "1. Checking active alarms..."
aws cloudwatch describe-alarms --state-value ALARM

# 2. Review costs
echo "2. Yesterday's costs..."
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '1 day ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost

# 3. Check for security issues
echo "3. Checking security findings..."
aws securityhub get-findings --max-results 10

# 4. Review backups
echo "4. Recent backups..."
aws backup list-backup-jobs --max-results 5

# 5. Check for idle resources
echo "5. Checking for idle resources..."
# Find stopped instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=stopped" \
  --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0]]' \
  --output table

echo ""
echo "Daily ops check complete!"
```

**Infrastructure as Code Export:**

```bash
# Export existing infrastructure to Terraform
# AWS
brew install terraformer
terraformer import aws --resources=vpc,subnet,security_group,ec2_instance --regions=us-east-1

# Azure
brew install aztfexport
aztfexport resource-group MyResourceGroup

# GCP (built-in)
gcloud beta resource-config bulk-export \
  --resource-format=terraform \
  --project=my-project
```

**Verification:**
- [ ] Documentation complete and accessible
- [ ] Architecture diagrams created
- [ ] All validation checks pass
- [ ] Runbooks created for common operations
- [ ] Team trained on cloud access and procedures
- [ ] Disaster recovery procedures documented and tested
- [ ] Cost optimization strategies identified
- [ ] Security audit passed
- [ ] Compliance requirements met

**If This Fails:**
→ Document as you build, don't leave it for later
→ Use cloud provider's architecture diagrams tools
→ Export infrastructure to IaC for documentation
→ Schedule regular documentation reviews
→ Create wiki/confluence pages for team collaboration

---

## Verification Checklist

After completing this workflow, verify:

**Account Setup:**
- [ ] Cloud account(s) created with billing configured
- [ ] MFA enabled on root/admin accounts
- [ ] Billing alerts active at multiple thresholds
- [ ] Monthly budget configured

**CLI & Authentication:**
- [ ] CLI tools installed for all providers
- [ ] Successfully authenticated
- [ ] Multiple profiles configured (dev/staging/prod)
- [ ] Credentials stored securely

**IAM & Security:**
- [ ] IAM users created (not using root)
- [ ] Service accounts configured
- [ ] Roles follow least-privilege
- [ ] All accounts have MFA enabled
- [ ] Audit logging enabled

**Networking:**
- [ ] VPC/VNet created with proper CIDR
- [ ] Public and private subnets configured
- [ ] Internet Gateway attached
- [ ] NAT Gateway for private subnets
- [ ] Security groups configured
- [ ] Multi-AZ for high availability

**Organization:**
- [ ] Tagging strategy implemented
- [ ] All resources tagged properly
- [ ] Cost allocation tags active
- [ ] Tag compliance enforced

**Monitoring:**
- [ ] CloudWatch/Monitor/Monitoring dashboard created
- [ ] Critical alerts configured
- [ ] Log aggregation working
- [ ] Uptime checks enabled
- [ ] Alert notifications tested

**Documentation:**
- [ ] Setup documented
- [ ] Architecture diagrams created
- [ ] Runbooks written
- [ ] Team trained
- [ ] Disaster recovery plan documented

---

## Common Issues & Solutions

### Issue: "Access Denied" Errors

**Symptoms:**
- CLI commands fail with permission errors
- Cannot access console/portal
- API calls return 403 errors

**Solution:**
```bash
# 1. Verify credentials
aws sts get-caller-identity
az account show
gcloud auth list

# 2. Check IAM permissions
aws iam get-user-policy --user-name your-username --policy-name YourPolicy
az role assignment list --assignee user@domain.com
gcloud projects get-iam-policy PROJECT_ID

# 3. Ensure using correct profile
export AWS_PROFILE=production
az account set --subscription "Production"
gcloud config set project prod-project

# 4. Refresh credentials
aws configure
az login
gcloud auth login
```

**Prevention:**
- Always use named profiles
- Document required permissions
- Use IAM policy simulator
- Regular permission audits

---

### Issue: High Unexpected Costs

**Symptoms:**
- Billing alerts triggered
- Costs higher than expected
- Unexplained resource usage

**Solution:**
```bash
# 1. Identify cost drivers
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-26 \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=SERVICE

# 2. Find unused resources
# Stopped instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=stopped" \
  --query 'Reservations[*].Instances[*].[InstanceId,LaunchTime]'

# Unattached EBS volumes
aws ec2 describe-volumes \
  --filters "Name=status,Values=available" \
  --query 'Volumes[*].[VolumeId,Size,CreateTime]'

# Unused Elastic IPs
aws ec2 describe-addresses \
  --query 'Addresses[?InstanceId==`null`].[PublicIp,AllocationId]'

# 3. Enable Cost Explorer recommendations
aws ce get-rightsizing-recommendation

# 4. Set up automated cleanup
# terminate-old-instances.sh
#!/bin/bash
# Terminate instances stopped for > 30 days
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=stopped" \
  --query 'Reservations[*].Instances[*].[InstanceId,LaunchTime]' \
  | jq -r '.[] | select(.[1] < (now - 2592000) | strftime("%Y-%m-%dT%H:%M:%S")) | .[0]' \
  | xargs -I {} aws ec2 terminate-instances --instance-ids {}
```

**Prevention:**
- Set aggressive billing alerts
- Tag resources for cost allocation
- Regular cost reviews
- Auto-scaling policies
- Resource cleanup automation
- Use spot/preemptible instances

---

### Issue: VPC Connectivity Problems

**Symptoms:**
- Cannot SSH/RDP to instances
- Services cannot communicate
- NAT Gateway not working

**Solution:**
```bash
# 1. Check security groups
aws ec2 describe-security-groups --group-ids sg-xxx

# 2. Verify route tables
aws ec2 describe-route-tables --route-table-ids rtb-xxx

# 3. Check network ACLs
aws ec2 describe-network-acls --network-acl-ids acl-xxx

# 4. Test connectivity
# From local machine
nc -zv instance-ip 22

# From instance (via Session Manager)
telnet destination-ip port

# 5. Enable VPC Flow Logs for debugging
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs

# 6. Check NAT Gateway
aws ec2 describe-nat-gateways --nat-gateway-ids nat-xxx
```

**Prevention:**
- Document security group rules
- Use infrastructure as code
- Test connectivity after changes
- Maintain network diagrams
- Use VPC Flow Logs

---

## Best Practices

### DO:

✅ **Use Infrastructure as Code from day one**
- Terraform, CloudFormation, Pulumi for all resources
- Version control for infrastructure
- Peer review for infrastructure changes

✅ **Enable all audit logging immediately**
- CloudTrail (AWS), Activity Log (Azure), Cloud Audit (GCP)
- Retain logs for compliance period
- Alert on suspicious activities

✅ **Implement least-privilege access**
- Start restrictive, grant as needed
- Regular access reviews
- Use temporary elevated access

✅ **Set up cost controls before deploying resources**
- Billing alerts at 50%, 80%, 100%
- Monthly budgets
- Cost allocation tags

✅ **Use multiple AWS accounts/Azure subscriptions/GCP projects**
- Separate dev/staging/prod
- Isolate workloads
- Blast radius containment

✅ **Enable MFA on all accounts**
- Hardware keys preferred
- Authenticator apps minimum
- No SMS-based MFA

✅ **Tag everything consistently**
- Automated tagging
- Policy enforcement
- Regular audits

✅ **Plan for disaster recovery from the start**
- Multi-region architecture
- Regular backup testing
- Documented recovery procedures

### DON'T:

❌ **Don't use root account for daily operations**
- Create IAM users immediately
- Lock root credentials
- Only use for account-level tasks

❌ **Don't hardcode credentials**
- Use IAM roles for services
- Secret managers for applications
- No credentials in code/repos

❌ **Don't ignore security recommendations**
- Respond to security alerts
- Apply patches promptly
- Regular security audits

❌ **Don't skip monitoring setup**
- Metrics, logs, alerts from day one
- Dashboards for visibility
- On-call rotation

❌ **Don't deploy without tagging**
- Tags required for billing
- Cost allocation impossible without tags
- Enforcement policies

❌ **Don't use default VPCs in production**
- Custom VPCs only
- Proper network segmentation
- Security group planning

❌ **Don't provision resources manually in production**
- Infrastructure as code only
- No console changes
- Automation for consistency

❌ **Don't forget about data residency**
- Understand compliance requirements
- Data sovereignty laws
- Region selection matters

---

## Related Workflows

**Prerequisites:**
- None (this is typically the first infrastructure workflow)

**Next Steps:**
- **docker_container_creation.md** - Deploy containerized applications
- **infrastructure_as_code_terraform.md** - Manage infrastructure as code
- **cicd_pipeline_setup.md** - Automate deployment pipeline
- **application_monitoring_setup.md** - Set up application monitoring
- **backup_disaster_recovery.md** - Implement backup and DR strategies

**Related:**
- **kubernetes_deployment.md** - Container orchestration
- **security/secret_management_solo.md** - Secure credential management
- **cost_optimization.md** - Cloud cost management

---

## Tags

`devops` `cloud` `aws` `azure` `gcp` `setup` `infrastructure` `iam` `vpc` `monitoring` `cost-management` `security` `networking` `high-priority`
