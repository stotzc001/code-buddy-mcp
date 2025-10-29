# Auto Scaling Configuration

**ID:** dvo-015  
**Category:** DevOps  
**Priority:** MEDIUM  
**Complexity:** Intermediate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive guide for configuring auto-scaling for compute resources (VMs, containers) to automatically adjust capacity based on demand, ensuring high availability and cost efficiency.

**Why:** Auto-scaling eliminates manual capacity planning, reduces costs by scaling down during low traffic, ensures applications remain responsive during traffic spikes, and provides built-in high availability through health checks and automatic replacement of failed instances.

**When to use:**
- Application experiencing variable traffic patterns
- Need to handle unpredictable load spikes
- Want to optimize infrastructure costs
- Implementing high availability architecture
- Preparing for traffic events (launches, sales, marketing campaigns)
- Migrating from over-provisioned static infrastructure

---

## Prerequisites

**Required:**
- [ ] Cloud provider account with appropriate permissions (AWS, Azure, or GCP)
- [ ] Application already containerized or configured for horizontal scaling
- [ ] Load balancer configured (ALB, Azure Load Balancer, or GCP Load Balancer)
- [ ] Application images/AMIs created and tested
- [ ] Monitoring and metrics collection enabled
- [ ] Understanding of application's resource requirements and scaling patterns

**Recommended:**
- [ ] Infrastructure as Code tool (Terraform, CloudFormation)
- [ ] Application health check endpoint implemented
- [ ] Connection draining/graceful shutdown configured
- [ ] Database handles concurrent connections
- [ ] Session management solution (sticky sessions or external session store)

**Check before starting:**
```bash
# Verify cloud CLI is configured
aws --version && aws sts get-caller-identity  # AWS
az --version && az account show              # Azure
gcloud --version && gcloud auth list         # GCP

# Check for existing load balancer
aws elbv2 describe-load-balancers  # AWS
az network lb list                  # Azure
gcloud compute forwarding-rules list # GCP

# Verify monitoring is enabled
aws cloudwatch list-metrics
az monitor metrics list-definitions
gcloud monitoring metric-descriptors list

# Test application health endpoint
curl -I https://your-app.com/health
```

---

## Implementation Steps

### Step 1: Define Scaling Strategy and Metrics

**What:** Determine your scaling approach (horizontal vs vertical), identify key metrics that trigger scaling events, and establish capacity boundaries based on application behavior and business requirements.

**How:**

**Scaling Types:**

| Type | Description | Use Case | Pros | Cons |
|------|-------------|----------|------|------|
| **Horizontal** | Add/remove instances | Stateless apps, microservices | Better availability, no limits | More complex setup |
| **Vertical** | Increase/decrease instance size | Stateful apps, databases | Simple, no code changes | Downtime, size limits |
| **Scheduled** | Scale at specific times | Predictable traffic patterns | Proactive, cost effective | Inflexible |
| **Predictive** | ML-based forecasting | Regular patterns | Optimal capacity | Complex, requires history |

**Key Metrics for Scaling:**

```yaml
# scaling-strategy.yaml
scaling_config:
  strategy: horizontal
  
  metrics:
    primary:
      - name: "CPU Utilization"
        threshold: 70%
        rationale: "General compute load indicator"
        pros: "Simple, widely available"
        cons: "May not reflect true application load"
      
      - name: "Request Count"
        threshold: 1000 requests/min per instance
        rationale: "Direct measure of application load"
        pros: "Application-specific, accurate"
        cons: "Requires instrumentation"
      
      - name: "Response Time"
        threshold: 500ms p95
        rationale: "User experience indicator"
        pros: "User-centric, clear SLA"
        cons: "Can be affected by external factors"
    
    secondary:
      - name: "Memory Utilization"
        threshold: 80%
      
      - name: "Network Throughput"
        threshold: 80% of instance limit
      
      - name: "Queue Depth"
        threshold: 100 messages
        use_case: "Worker instances processing queues"
  
  capacity:
    minimum: 2  # High availability
    desired: 4  # Normal operation
    maximum: 20  # Cost protection
  
  scaling_policies:
    scale_out:
      cooldown: 300s  # 5 minutes
      adjustment: +2 instances  # or +25%
      
    scale_in:
      cooldown: 600s  # 10 minutes (longer to prevent thrashing)
      adjustment: -1 instance  # Conservative
  
  health_checks:
    type: "HTTP"
    path: "/health"
    interval: 30s
    timeout: 5s
    healthy_threshold: 2
    unhealthy_threshold: 3
```

**Capacity Planning Calculator:**

```python
# capacity_calculator.py
def calculate_scaling_params(
    avg_requests_per_minute: int,
    instance_capacity: int,
    peak_multiplier: float = 3.0,
    buffer_percent: float = 0.25
):
    """Calculate auto-scaling parameters based on traffic patterns"""
    
    # Normal capacity
    normal_instances = ceil(avg_requests_per_minute / instance_capacity)
    
    # Peak capacity with buffer
    peak_instances = ceil(
        (avg_requests_per_minute * peak_multiplier * (1 + buffer_percent)) 
        / instance_capacity
    )
    
    # Minimum for HA (at least 2, across 2 AZs)
    min_instances = max(2, ceil(normal_instances * 0.5))
    
    return {
        'minimum': min_instances,
        'desired': normal_instances,
        'maximum': peak_instances,
        'scale_out_threshold': 70,  # CPU%
        'scale_in_threshold': 30,   # CPU%
        'estimated_monthly_cost': estimate_cost(normal_instances, peak_instances)
    }

# Example usage
params = calculate_scaling_params(
    avg_requests_per_minute=5000,
    instance_capacity=100,  # requests per minute per instance
    peak_multiplier=3.0,    # traffic can 3x during peaks
    buffer_percent=0.25     # 25% safety buffer
)

print(f"""
Recommended Auto Scaling Configuration:
- Minimum Instances: {params['minimum']}
- Desired Instances: {params['desired']}
- Maximum Instances: {params['maximum']}
- Scale Out at: {params['scale_out_threshold']}% CPU
- Scale In at: {params['scale_in_threshold']}% CPU
""")
```

**Verification:**
- [ ] Scaling strategy documented and approved
- [ ] Primary scaling metric identified
- [ ] Min/desired/max capacity determined
- [ ] Scaling thresholds defined
- [ ] Cooldown periods configured
- [ ] Health check requirements documented

**If This Fails:**
→ Start with CPU-based scaling (simple and reliable)
→ Analyze historical traffic data to inform capacity planning
→ Use conservative thresholds and refine based on observation
→ Implement monitoring before scaling for baseline data

---

### Step 2: Create Launch Template or Configuration

**What:** Define the instance configuration (AMI, instance type, security groups, user data) that will be used to launch new instances during scale-out events.

**How:**

#### AWS Launch Template

```bash
# 1. Create launch template
aws ec2 create-launch-template \
  --launch-template-name my-app-template \
  --version-description "v1.0 - Initial release" \
  --launch-template-data file://launch-template.json
```

**launch-template.json:**
```json
{
  "ImageId": "ami-0c55b159cbfafe1f0",
  "InstanceType": "t3.medium",
  "KeyName": "my-key-pair",
  "SecurityGroupIds": ["sg-0123456789abcdef0"],
  "IamInstanceProfile": {
    "Arn": "arn:aws:iam::123456789012:instance-profile/MyAppRole"
  },
  "BlockDeviceMappings": [
    {
      "DeviceName": "/dev/xvda",
      "Ebs": {
        "VolumeSize": 30,
        "VolumeType": "gp3",
        "DeleteOnTermination": true,
        "Encrypted": true
      }
    }
  ],
  "TagSpecifications": [
    {
      "ResourceType": "instance",
      "Tags": [
        {"Key": "Name", "Value": "MyApp-AutoScaled"},
        {"Key": "Environment", "Value": "production"},
        {"Key": "ManagedBy", "Value": "AutoScaling"}
      ]
    }
  ],
  "UserData": "IyEvYmluL2Jhc2gKZWNobyAiSGVsbG8gZnJvbSB1c2VyIGRhdGEi",
  "MetadataOptions": {
    "HttpTokens": "required",
    "HttpPutResponseHopLimit": 1
  },
  "Monitoring": {
    "Enabled": true
  }
}
```

**Encoded User Data Script:**
```bash
#!/bin/bash
# user-data.sh (Base64 encode for UserData field)

# Update system
yum update -y

# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json <<EOF
{
  "metrics": {
    "namespace": "MyApp",
    "metrics_collected": {
      "cpu": {"measurement": [{"name": "cpu_usage_idle"}]},
      "mem": {"measurement": [{"name": "mem_used_percent"}]}
    }
  }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json

# Pull and run application
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
docker run -d -p 80:8080 \
  --restart unless-stopped \
  --name myapp \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest

# Signal health to load balancer
echo "Application started successfully"

# Base64 encode for use in template:
# base64 -w 0 user-data.sh
```

#### Azure VM Scale Set Configuration

```bash
# Create scale set with custom image
az vmss create \
  --resource-group MyResourceGroup \
  --name MyAppVMSS \
  --image MyCustomImage \
  --vm-sku Standard_D2s_v3 \
  --instance-count 2 \
  --vnet-name MyVNet \
  --subnet AppSubnet \
  --lb MyLoadBalancer \
  --backend-pool-name MyAppPool \
  --storage-sku Premium_LRS \
  --upgrade-policy-mode Automatic \
  --health-probe /health \
  --custom-data cloud-init.txt
```

**cloud-init.txt:**
```yaml
#cloud-config
package_upgrade: true

packages:
  - docker.io
  - azure-cli

runcmd:
  - systemctl start docker
  - systemctl enable docker
  - docker pull myregistry.azurecr.io/myapp:latest
  - docker run -d -p 80:8080 --restart unless-stopped myregistry.azurecr.io/myapp:latest
  - echo "Application started" > /var/log/startup.log
```

#### GCP Instance Template

```bash
# Create instance template
gcloud compute instance-templates create my-app-template \
  --machine-type=n1-standard-2 \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server \
  --metadata-from-file startup-script=startup.sh \
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

**startup.sh:**
```bash
#!/bin/bash

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Stackdriver agent
curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
bash add-monitoring-agent-repo.sh
apt-get update
apt-get install -y stackdriver-agent

# Pull and run application
docker pull gcr.io/my-project/myapp:latest
docker run -d -p 80:8080 \
  --restart unless-stopped \
  gcr.io/my-project/myapp:latest

# Health check
while ! curl -f http://localhost/health; do
  sleep 5
done

echo "Application ready"
```

#### Terraform Launch Template (Multi-Cloud)

```hcl
# launch-template.tf (AWS)
resource "aws_launch_template" "app" {
  name_prefix   = "myapp-"
  image_id      = data.aws_ami.app.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.app.id]
  
  iam_instance_profile {
    name = aws_iam_instance_profile.app.name
  }

  user_data = base64encode(templatefile("${path.module}/user-data.sh", {
    environment = var.environment
    app_version = var.app_version
  }))

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = 30
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
    }
  }

  tag_specifications {
    resource_type = "instance"
    tags = merge(var.common_tags, {
      Name = "MyApp-AutoScaled"
    })
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

**Verification:**
- [ ] Launch template/configuration created
- [ ] AMI/image tested and validated
- [ ] Instance type appropriate for workload
- [ ] Security groups configured correctly
- [ ] IAM role attached with necessary permissions
- [ ] User data script executes successfully
- [ ] Application starts automatically
- [ ] Health checks pass

**If This Fails:**
→ Test AMI/image manually before using in template
→ Verify user data script with shell validation (shellcheck)
→ Check IAM permissions for instance profile
→ Ensure security groups allow required traffic
→ Review CloudWatch logs for boot errors

---

### Step 3: Set Up Auto Scaling Group

**What:** Create the auto scaling group that will manage your fleet of instances, automatically launching and terminating instances based on defined policies and health checks.

**How:**

#### AWS Auto Scaling Group

```bash
# 1. Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name myapp-asg \
  --launch-template "LaunchTemplateName=my-app-template,Version=1" \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4 \
  --default-cooldown 300 \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --vpc-zone-identifier "subnet-abc123,subnet-def456" \
  --target-group-arns "arn:aws:elasticloadbalancing:region:account:targetgroup/my-targets/abc123" \
  --termination-policies "OldestInstance" \
  --tags "Key=Name,Value=MyApp-ASG,PropagateAtLaunch=true" \
         "Key=Environment,Value=production,PropagateAtLaunch=true"

# 2. Enable metrics collection
aws autoscaling enable-metrics-collection \
  --auto-scaling-group-name myapp-asg \
  --granularity "1Minute" \
  --metrics GroupDesiredCapacity \
           GroupInServiceInstances \
           GroupMaxSize \
           GroupMinSize \
           GroupPendingInstances \
           GroupStandbyInstances \
           GroupTerminatingInstances \
           GroupTotalInstances

# 3. Configure instance protection (optional)
aws autoscaling set-instance-protection \
  --instance-ids i-1234567890abcdef0 \
  --auto-scaling-group-name myapp-asg \
  --protected-from-scale-in
```

**Terraform Auto Scaling Group:**

```hcl
# autoscaling.tf
resource "aws_autoscaling_group" "app" {
  name                = "myapp-asg"
  vpc_zone_identifier = var.subnet_ids
  
  min_size         = 2
  max_size         = 10
  desired_capacity = 4

  health_check_type         = "ELB"
  health_check_grace_period = 300
  default_cooldown          = 300
  
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  target_group_arns = [aws_lb_target_group.app.arn]

  termination_policies = ["OldestInstance"]

  enabled_metrics = [
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupMaxSize",
    "GroupMinSize",
    "GroupPendingInstances",
    "GroupStandbyInstances",
    "GroupTerminatingInstances",
    "GroupTotalInstances",
  ]

  tag {
    key                 = "Name"
    value               = "MyApp-AutoScaled"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [desired_capacity]
  }
}

# Instance refresh for zero-downtime updates
resource "aws_autoscaling_group" "app" {
  # ... previous configuration ...

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 90
      instance_warmup       = 300
    }
  }
}
```

#### Azure VM Scale Set

```bash
# Update scale set configuration
az vmss update \
  --resource-group MyResourceGroup \
  --name MyAppVMSS \
  --set upgradePolicy.mode=Automatic

# Configure auto-scaling rules (see Step 4)
az monitor autoscale create \
  --resource-group MyResourceGroup \
  --name MyAppAutoscale \
  --resource MyAppVMSS \
  --resource-type Microsoft.Compute/virtualMachineScaleSets \
  --min-count 2 \
  --max-count 10 \
  --count 4
```

#### GCP Managed Instance Group

```bash
# Create managed instance group
gcloud compute instance-groups managed create my-app-mig \
  --base-instance-name myapp \
  --template my-app-template \
  --size 4 \
  --zones us-central1-a,us-central1-b \
  --target-distribution-shape EVEN

# Set named ports for load balancer
gcloud compute instance-groups managed set-named-ports my-app-mig \
  --named-ports http:80 \
  --zone us-central1-a

# Configure autoscaling (see Step 4)
gcloud compute instance-groups managed set-autoscaling my-app-mig \
  --max-num-replicas 10 \
  --min-num-replicas 2 \
  --target-cpu-utilization 0.7 \
  --cool-down-period 60 \
  --zone us-central1-a

# Set autohealing policy
gcloud compute instance-groups managed set-autohealing my-app-mig \
  --health-check my-health-check \
  --initial-delay 300 \
  --zone us-central1-a
```

**Multi-Zone Distribution:**

```python
# zone_distribution.py
def calculate_zone_distribution(total_instances: int, zones: list) -> dict:
    """
    Calculate even distribution of instances across availability zones
    """
    base_per_zone = total_instances // len(zones)
    remainder = total_instances % len(zones)
    
    distribution = {}
    for i, zone in enumerate(zones):
        # Distribute remainder to first zones
        distribution[zone] = base_per_zone + (1 if i < remainder else 0)
    
    return distribution

# Example
zones = ['us-east-1a', 'us-east-1b', 'us-east-1c']
instances = 7

dist = calculate_zone_distribution(instances, zones)
# Result: {'us-east-1a': 3, 'us-east-1b': 2, 'us-east-1c': 2}
```

**Verification:**
- [ ] Auto Scaling Group created
- [ ] Min/max/desired capacity configured
- [ ] Instances distributed across multiple AZs
- [ ] Health checks configured
- [ ] Load balancer target group attached
- [ ] Metrics collection enabled
- [ ] Tags propagating to instances

**If This Fails:**
→ Verify subnets are in correct VPC
→ Check target group health check configuration
→ Ensure launch template is valid
→ Review IAM permissions for Auto Scaling service
→ Check for capacity limits in AWS quotas

---

### Step 4: Configure Scaling Policies

**What:** Define rules that determine when and how your auto scaling group should scale in or out based on CloudWatch metrics, scheduled events, or predictive patterns.

**How:**

#### AWS Target Tracking Policy

```bash
# 1. Simple target tracking (CPU-based)
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name myapp-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://target-tracking-policy.json
```

**target-tracking-policy.json:**
```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  },
  "ScaleInCooldown": 300,
  "ScaleOutCooldown": 60
}
```

**Custom Metric Tracking:**
```json
{
  "TargetValue": 1000.0,
  "CustomizedMetricSpecification": {
    "MetricName": "RequestCountPerTarget",
    "Namespace": "AWS/ApplicationELB",
    "Statistic": "Sum",
    "Dimensions": [
      {
        "Name": "TargetGroup",
        "Value": "targetgroup/my-targets/abc123"
      }
    ]
  },
  "ScaleInCooldown": 600,
  "ScaleOutCooldown": 60
}
```

#### AWS Step Scaling Policy

```bash
# Step scaling for more granular control
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name myapp-asg \
  --policy-name scale-out-policy \
  --policy-type StepScaling \
  --adjustment-type PercentChangeInCapacity \
  --metric-aggregation-type Average \
  --step-adjustments file://step-adjustments.json

# Create CloudWatch alarm to trigger policy
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-alarm \
  --alarm-description "Scale out when CPU > 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:autoscaling:region:account:scalingPolicy:policy-id
```

**step-adjustments.json:**
```json
[
  {
    "MetricIntervalLowerBound": 0,
    "MetricIntervalUpperBound": 10,
    "ScalingAdjustment": 10
  },
  {
    "MetricIntervalLowerBound": 10,
    "MetricIntervalUpperBound": 20,
    "ScalingAdjustment": 20
  },
  {
    "MetricIntervalLowerBound": 20,
    "ScalingAdjustment": 30
  }
]
```

#### Scheduled Scaling

```bash
# Scale up before expected traffic
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name myapp-asg \
  --scheduled-action-name scale-up-morning \
  --recurrence "0 8 * * MON-FRI" \
  --min-size 4 \
  --desired-capacity 8 \
  --max-size 10 \
  --time-zone "America/New_York"

# Scale down after hours
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name myapp-asg \
  --scheduled-action-name scale-down-evening \
  --recurrence "0 20 * * MON-FRI" \
  --min-size 2 \
  --desired-capacity 4 \
  --max-size 10 \
  --time-zone "America/New_York"
```

#### Azure Autoscale Rules

```bash
# CPU-based scaling rule (scale out)
az monitor autoscale rule create \
  --resource-group MyResourceGroup \
  --autoscale-name MyAppAutoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 2

# CPU-based scaling rule (scale in)
az monitor autoscale rule create \
  --resource-group MyResourceGroup \
  --autoscale-name MyAppAutoscale \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1

# Schedule-based scaling
az monitor autoscale rule create \
  --resource-group MyResourceGroup \
  --autoscale-name MyAppAutoscale \
  --condition "TimeGrain=PT1M,Statistic=Average,TimeWindow=PT5M" \
  --scale to 8 \
  --recurrence week mon tue wed thu fri \
  --start-time "08:00" \
  --timezone "Eastern Standard Time"
```

#### GCP Autoscaling Policies

```bash
# CPU-based autoscaling
gcloud compute instance-groups managed set-autoscaling my-app-mig \
  --max-num-replicas 10 \
  --min-num-replicas 2 \
  --target-cpu-utilization 0.7 \
  --cool-down-period 60 \
  --zone us-central1-a

# Custom metric-based autoscaling
gcloud compute instance-groups managed set-autoscaling my-app-mig \
  --custom-metric-utilization \
    metric=custom.googleapis.com/requests_per_second,\
    target-type=GAUGE,\
    target-utilization-value=1000 \
  --zone us-central1-a

# Scaling based on load balancer utilization
gcloud compute instance-groups managed set-autoscaling my-app-mig \
  --load-balancing-utilization 0.8 \
  --zone us-central1-a

# Schedule scaling
gcloud compute resource-policies create instance-schedule my-schedule \
  --region us-central1 \
  --vm-start-schedule '0 8 * * MON-FRI' \
  --vm-stop-schedule '0 20 * * MON-FRI' \
  --timezone 'America/New_York'
```

#### Terraform Scaling Policies

```hcl
# Target tracking policy
resource "aws_autoscaling_policy" "target_tracking" {
  name                   = "cpu-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# Step scaling policy
resource "aws_autoscaling_policy" "scale_out" {
  name                   = "scale-out"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "StepScaling"
  adjustment_type        = "PercentChangeInCapacity"

  step_adjustment {
    scaling_adjustment          = 10
    metric_interval_lower_bound = 0
    metric_interval_upper_bound = 10
  }

  step_adjustment {
    scaling_adjustment          = 20
    metric_interval_lower_bound = 10
    metric_interval_upper_bound = 20
  }

  step_adjustment {
    scaling_adjustment          = 30
    metric_interval_lower_bound = 20
  }
}

# Scheduled scaling
resource "aws_autoscaling_schedule" "scale_up_morning" {
  scheduled_action_name  = "scale-up-morning"
  min_size               = 4
  max_size               = 10
  desired_capacity       = 8
  recurrence             = "0 8 * * MON-FRI"
  time_zone              = "America/New_York"
  autoscaling_group_name = aws_autoscaling_group.app.name
}
```

**Advanced: Predictive Scaling**

```bash
# AWS Predictive Scaling (requires 14 days of historical data)
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name myapp-asg \
  --policy-name predictive-scaling \
  --policy-type PredictiveScaling \
  --predictive-scaling-configuration file://predictive-config.json
```

**predictive-config.json:**
```json
{
  "MetricSpecifications": [
    {
      "TargetValue": 70.0,
      "PredefinedMetricPairSpecification": {
        "PredefinedMetricType": "ASGCPUUtilization"
      }
    }
  ],
  "Mode": "ForecastAndScale",
  "SchedulingBufferTime": 600,
  "MaxCapacityBreachBehavior": "IncreaseMaxCapacity",
  "MaxCapacityBuffer": 10
}
```

**Verification:**
- [ ] Scaling policies created
- [ ] CloudWatch alarms configured (if using step scaling)
- [ ] Policy tested with load generation
- [ ] Cooldown periods appropriate
- [ ] Scale-in policies more conservative than scale-out
- [ ] Scheduled scaling aligned with business needs
- [ ] Notifications configured for scaling events

**If This Fails:**
→ Start with simple target tracking, move to step scaling if needed
→ Verify CloudWatch metrics are being published
→ Check alarm thresholds are realistic
→ Ensure sufficient permissions for Auto Scaling to execute policies
→ Monitor scaling activities in Auto Scaling console

---

### Step 5: Configure Health Checks and Instance Lifecycle

**What:** Implement comprehensive health checking to automatically detect and replace unhealthy instances, and configure lifecycle hooks for graceful instance startup and shutdown.

**How:**

#### AWS Health Checks

```bash
# Configure ELB health checks (already done in target group)
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/my-targets/abc123 \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# Update ASG to use ELB health checks
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name myapp-asg \
  --health-check-type ELB \
  --health-check-grace-period 300

# Create lifecycle hook for instance launch
aws autoscaling put-lifecycle-hook \
  --lifecycle-hook-name instance-launching \
  --auto-scaling-group-name myapp-asg \
  --lifecycle-transition autoscaling:EC2_INSTANCE_LAUNCHING \
  --heartbeat-timeout 300 \
  --default-result CONTINUE \
  --notification-target-arn arn:aws:sns:region:account:my-asg-notifications

# Create lifecycle hook for instance termination
aws autoscaling put-lifecycle-hook \
  --lifecycle-hook-name instance-terminating \
  --auto-scaling-group-name myapp-asg \
  --lifecycle-transition autoscaling:EC2_INSTANCE_TERMINATING \
  --heartbeat-timeout 120 \
  --default-result CONTINUE \
  --notification-target-arn arn:aws:sns:region:account:my-asg-notifications
```

**Application Health Check Endpoint:**

```python
# health.py (FastAPI example)
from fastapi import FastAPI, Response, status
import psutil
import requests

app = FastAPI()

@app.get("/health")
async def health_check(response: Response):
    """
    Comprehensive health check for load balancer and monitoring
    """
    checks = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    checks['checks']['cpu'] = {
        'status': 'pass' if cpu_percent < 90 else 'fail',
        'value': cpu_percent
    }
    
    # Check memory usage
    memory = psutil.virtual_memory()
    checks['checks']['memory'] = {
        'status': 'pass' if memory.percent < 90 else 'fail',
        'value': memory.percent
    }
    
    # Check disk usage
    disk = psutil.disk_usage('/')
    checks['checks']['disk'] = {
        'status': 'pass' if disk.percent < 90 else 'fail',
        'value': disk.percent
    }
    
    # Check database connectivity
    try:
        # Example database check
        # db_response = database.ping()
        checks['checks']['database'] = {'status': 'pass'}
    except Exception as e:
        checks['checks']['database'] = {'status': 'fail', 'error': str(e)}
        checks['status'] = 'unhealthy'
    
    # Check critical dependencies
    try:
        # Example external service check
        # api_response = requests.get('https://api.example.com/health', timeout=2)
        checks['checks']['external_api'] = {'status': 'pass'}
    except Exception as e:
        checks['checks']['external_api'] = {'status': 'fail', 'error': str(e)}
        checks['status'] = 'unhealthy'
    
    # Set HTTP status based on overall health
    if checks['status'] == 'unhealthy':
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return checks

@app.get("/health/ready")
async def readiness_check(response: Response):
    """
    Readiness check - is the application ready to serve traffic?
    """
    # Check if application initialization is complete
    if not app.state.initialized:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {'status': 'not ready'}
    
    return {'status': 'ready'}

@app.get("/health/live")
async def liveness_check():
    """
    Liveness check - is the application process alive?
    """
    return {'status': 'alive'}
```

#### Lifecycle Hook Handler

```python
# lifecycle_handler.py
import boto3
import json
import logging

sns = boto3.client('sns')
asg = boto3.client('autoscaling')
ec2 = boto3.client('ec2')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Handle Auto Scaling lifecycle events
    """
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    lifecycle_hook_name = message['LifecycleHookName']
    auto_scaling_group_name = message['AutoScalingGroupName']
    instance_id = message['EC2InstanceId']
    lifecycle_action_token = message['LifecycleActionToken']
    transition = message['LifecycleTransition']
    
    logger.info(f"Processing {transition} for instance {instance_id}")
    
    try:
        if transition == 'autoscaling:EC2_INSTANCE_LAUNCHING':
            # Custom logic before instance enters service
            # Examples:
            # - Wait for application to fully initialize
            # - Register with service discovery
            # - Pre-warm caches
            # - Run configuration management
            
            logger.info(f"Instance {instance_id} launching - performing initialization")
            
            # Simulate initialization work
            import time
            time.sleep(30)
            
            # Complete lifecycle action
            asg.complete_lifecycle_action(
                LifecycleHookName=lifecycle_hook_name,
                AutoScalingGroupName=auto_scaling_group_name,
                LifecycleActionToken=lifecycle_action_token,
                LifecycleActionResult='CONTINUE',
                InstanceId=instance_id
            )
            
            logger.info(f"Instance {instance_id} ready for service")
        
        elif transition == 'autoscaling:EC2_INSTANCE_TERMINATING':
            # Custom logic before instance termination
            # Examples:
            # - Graceful connection draining
            # - Complete in-flight requests
            # - Deregister from service discovery
            # - Upload logs to S3
            # - Clean up resources
            
            logger.info(f"Instance {instance_id} terminating - performing cleanup")
            
            # Graceful shutdown
            # 1. Deregister from service mesh
            # 2. Wait for connections to drain
            # 3. Upload logs/metrics
            
            import time
            time.sleep(60)  # Allow time for cleanup
            
            # Complete lifecycle action
            asg.complete_lifecycle_action(
                LifecycleHookName=lifecycle_hook_name,
                AutoScalingGroupName=auto_scaling_group_name,
                LifecycleActionToken=lifecycle_action_token,
                LifecycleActionResult='CONTINUE',
                InstanceId=instance_id
            )
            
            logger.info(f"Instance {instance_id} cleanup complete")
        
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        logger.error(f"Error processing lifecycle hook: {str(e)}")
        
        # Abandon lifecycle action on error
        asg.complete_lifecycle_action(
            LifecycleHookName=lifecycle_hook_name,
            AutoScalingGroupName=auto_scaling_group_name,
            LifecycleActionToken=lifecycle_action_token,
            LifecycleActionResult='ABANDON',
            InstanceId=instance_id
        )
        
        raise
```

#### Connection Draining Configuration

```bash
# Configure connection draining in target group
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/my-targets/abc123 \
  --attributes \
    Key=deregistration_delay.timeout_seconds,Value=300 \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=lb_cookie \
    Key=stickiness.lb_cookie.duration_seconds,Value=86400
```

**Verification:**
- [ ] Health check endpoint returns 200 for healthy, 503 for unhealthy
- [ ] Health check tests all critical dependencies
- [ ] ELB/load balancer health checks configured
- [ ] Health check grace period allows for application startup
- [ ] Lifecycle hooks configured if needed
- [ ] Connection draining configured
- [ ] Unhealthy instances automatically replaced

**If This Fails:**
→ Test health endpoint manually before deploying
→ Ensure health check path is accessible without authentication
→ Set appropriate timeouts for slow-starting applications
→ Monitor CloudWatch logs for health check failures
→ Verify security groups allow load balancer health checks

---

### Step 6: Test Scaling Behavior

**What:** Validate that your auto scaling configuration works as expected by simulating traffic, monitoring scaling events, and verifying that the system scales appropriately under various conditions.

**How:**

#### Load Testing Setup

```bash
# Install load testing tools
pip install locust

# Or use Apache Bench
sudo apt-get install apache2-utils

# Or use hey (modern alternative to ab)
go install github.com/rakyll/hey@latest
```

**Locust Load Test (locustfile.py):**
```python
from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_homepage(self):
        """Simulate homepage views (most common)"""
        self.client.get("/")
    
    @task(2)
    def view_products(self):
        """Simulate product browsing"""
        product_id = random.randint(1, 1000)
        self.client.get(f"/api/products/{product_id}")
    
    @task(1)
    def create_order(self):
        """Simulate order creation (resource-intensive)"""
        self.client.post("/api/orders", json={
            "product_id": random.randint(1, 1000),
            "quantity": random.randint(1, 5)
        })
    
    def on_start(self):
        """Login on start"""
        self.client.post("/login", json={
            "username": f"user{random.randint(1, 100)}",
            "password": "password"
        })

# Run:
# locust -f locustfile.py --host https://your-app.com
# Then open http://localhost:8089 for web UI
```

#### Scaling Test Scenarios

**Scenario 1: Gradual Traffic Increase**
```bash
# Ramp up slowly to test scale-out
hey -z 10m -q 10 -c 50 https://your-app.com/  # Start: 10 QPS
hey -z 10m -q 50 -c 100 https://your-app.com/ # Increase to 50 QPS
hey -z 10m -q 100 -c 200 https://your-app.com/ # Increase to 100 QPS

# Monitor scaling
watch -n 5 'aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names myapp-asg \
  --query "AutoScalingGroups[0].[DesiredCapacity,MinSize,MaxSize]" \
  --output table'
```

**Scenario 2: Traffic Spike**
```bash
# Sudden traffic spike to test rapid scale-out
# 1000 requests per second for 5 minutes
hey -z 5m -q 1000 -c 500 https://your-app.com/

# Monitor metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=myapp-asg \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average
```

**Scenario 3: Scale-In Test**
```bash
# Stop all load to test scale-in
# (kill load testing processes)

# Watch as instances scale down
watch -n 10 'aws autoscaling describe-auto-scaling-instances \
  --query "AutoScalingInstances[*].[InstanceId,LifecycleState,HealthStatus]" \
  --output table'
```

#### Monitoring Scaling Events

```python
# monitor_scaling.py
import boto3
import time
from datetime import datetime, timedelta

autoscaling = boto3.client('autoscaling')
cloudwatch = boto3.client('cloudwatch')

def monitor_scaling_activities(asg_name, duration_minutes=30):
    """Monitor auto scaling activities and metrics"""
    
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=duration_minutes)
    
    print(f"Monitoring {asg_name} from {start_time} to {end_time}")
    print("=" * 80)
    
    # Get scaling activities
    activities = autoscaling.describe_scaling_activities(
        AutoScalingGroupName=asg_name,
        MaxRecords=50
    )
    
    print("\nRecent Scaling Activities:")
    print("-" * 80)
    for activity in activities['Activities']:
        if activity['StartTime'] > start_time:
            print(f"Time: {activity['StartTime']}")
            print(f"Cause: {activity['Cause']}")
            print(f"Description: {activity['Description']}")
            print(f"Status: {activity['StatusCode']}")
            print("-" * 80)
    
    # Get current state
    groups = autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[asg_name]
    )
    
    group = groups['AutoScalingGroups'][0]
    print(f"\nCurrent State:")
    print(f"Desired Capacity: {group['DesiredCapacity']}")
    print(f"Current Instances: {len(group['Instances'])}")
    print(f"Min Size: {group['MinSize']}")
    print(f"Max Size: {group['MaxSize']}")
    
    # Get CPU metrics
    cpu_metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {'Name': 'AutoScalingGroupName', 'Value': asg_name}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,  # 5 minutes
        Statistics=['Average', 'Maximum']
    )
    
    print(f"\nCPU Utilization (last {duration_minutes} minutes):")
    print("-" * 80)
    for datapoint in sorted(cpu_metrics['Datapoints'], key=lambda x: x['Timestamp']):
        print(f"{datapoint['Timestamp']}: Avg={datapoint['Average']:.2f}%, Max={datapoint['Maximum']:.2f}%")

# Run monitoring
if __name__ == '__main__':
    monitor_scaling_activities('myapp-asg', duration_minutes=60)
```

#### Validation Checklist Script

```bash
#!/bin/bash
# validate-autoscaling.sh

ASG_NAME="myapp-asg"

echo "🔍 Auto Scaling Validation"
echo "=========================="

# 1. Check ASG configuration
echo "1. Auto Scaling Group Configuration:"
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names $ASG_NAME \
  --query 'AutoScalingGroups[0].[MinSize,DesiredCapacity,MaxSize,HealthCheckType,HealthCheckGracePeriod]' \
  --output table

# 2. Check instances
echo -e "\n2. Running Instances:"
aws autoscaling describe-auto-scaling-instances \
  --query "AutoScalingInstances[?AutoScalingGroupName=='$ASG_NAME'].[InstanceId,LifecycleState,HealthStatus,AvailabilityZone]" \
  --output table

# 3. Check scaling policies
echo -e "\n3. Scaling Policies:"
aws autoscaling describe-policies \
  --auto-scaling-group-name $ASG_NAME \
  --query 'ScalingPolicies[*].[PolicyName,PolicyType,Enabled]' \
  --output table

# 4. Check recent scaling activities
echo -e "\n4. Recent Scaling Activities (last hour):"
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name $ASG_NAME \
  --max-records 10 \
  --query 'Activities[*].[StartTime,Cause,StatusCode]' \
  --output table

# 5. Check load balancer target health
echo -e "\n5. Load Balancer Target Health:"
TARGET_GROUP_ARN=$(aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names $ASG_NAME \
  --query 'AutoScalingGroups[0].TargetGroupARNs[0]' \
  --output text)

aws elbv2 describe-target-health \
  --target-group-arn $TARGET_GROUP_ARN \
  --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State,TargetHealth.Reason]' \
  --output table

# 6. Generate load and watch scaling
echo -e "\n6. Starting load test..."
echo "Press Ctrl+C to stop"

# Simple load generation
ab -n 100000 -c 100 https://your-app.com/ &

# Monitor for 5 minutes
for i in {1..10}; do
    echo -e "\n--- Minute $i ---"
    aws autoscaling describe-auto-scaling-groups \
      --auto-scaling-group-names $ASG_NAME \
      --query 'AutoScalingGroups[0].[DesiredCapacity]' \
      --output text
    sleep 30
done

echo -e "\n✅ Validation complete!"
```

**Verification:**
- [ ] Auto scaling group scales out under load
- [ ] New instances pass health checks and receive traffic
- [ ] Scaling respects min/max boundaries
- [ ] Cooldown periods prevent thrashing
- [ ] Auto scaling group scales in when load decreases
- [ ] Terminating instances drain connections gracefully
- [ ] Metrics accurately reflect load
- [ ] Alarms trigger at appropriate thresholds

**If This Fails:**
→ Check if metric thresholds are too aggressive
→ Verify instances can handle expected load
→ Ensure load balancer distributes traffic evenly
→ Review cooldown periods (may be too long/short)
→ Check for instance launch failures
→ Verify application logs for errors under load

---

### Step 7: Implement Cost Optimization

**What:** Configure auto scaling to minimize costs while maintaining performance by using spot instances, scheduled scaling, and right-sizing strategies.

**How:**

#### AWS Spot Instances in ASG

```bash
# Create mixed instance policy (on-demand + spot)
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name myapp-asg \
  --mixed-instances-policy file://mixed-instances-policy.json \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4 \
  --vpc-zone-identifier "subnet-abc123,subnet-def456" \
  --health-check-type ELB \
  --health-check-grace-period 300
```

**mixed-instances-policy.json:**
```json
{
  "LaunchTemplate": {
    "LaunchTemplateSpecification": {
      "LaunchTemplateName": "my-app-template",
      "Version": "$Latest"
    },
    "Overrides": [
      {"InstanceType": "t3.medium", "WeightedCapacity": "1"},
      {"InstanceType": "t3a.medium", "WeightedCapacity": "1"},
      {"InstanceType": "t2.medium", "WeightedCapacity": "1"}
    ]
  },
  "InstancesDistribution": {
    "OnDemandAllocationStrategy": "prioritized",
    "OnDemandBaseCapacity": 2,
    "OnDemandPercentageAboveBaseCapacity": 50,
    "SpotAllocationStrategy": "capacity-optimized",
    "SpotInstancePools": 3,
    "SpotMaxPrice": ""
  }
}
```

**Explanation:**
- `OnDemandBaseCapacity: 2` - Always maintain 2 On-Demand instances for baseline
- `OnDemandPercentageAboveBaseCapacity: 50` - 50% On-Demand, 50% Spot above baseline
- `SpotAllocationStrategy: capacity-optimized` - Choose pools with lowest interruption risk
- `SpotMaxPrice: ""` - Pay current spot price (up to On-Demand price)

#### Azure Low-Priority VMs

```bash
# Create scale set with low-priority VMs
az vmss create \
  --resource-group MyResourceGroup \
  --name MyAppVMSS \
  --image UbuntuLTS \
  --priority Low \
  --eviction-policy Deallocate \
  --max-price 0.05 \
  --instance-count 4 \
  --admin-username azureuser \
  --generate-ssh-keys

# Update existing scale set to use low-priority
az vmss update \
  --resource-group MyResourceGroup \
  --name MyAppVMSS \
  --priority Low \
  --max-price -1  # Pay up to standard price
```

#### GCP Preemptible Instances

```bash
# Create instance template with preemptible instances
gcloud compute instance-templates create my-app-template-preemptible \
  --machine-type=n1-standard-2 \
  --preemptible \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --metadata-from-file startup-script=startup.sh

# Create MIG with mix of regular and preemptible
gcloud compute instance-groups managed create my-app-mig \
  --base-instance-name myapp \
  --template my-app-template-preemptible \
  --size 4 \
  --zone us-central1-a
```

#### Cost Optimization Script

```python
# optimize_costs.py
import boto3
from datetime import datetime, timedelta

autoscaling = boto3.client('autoscaling')
ce = boto3.client('ce')

def analyze_costs_and_optimize(asg_name):
    """
    Analyze auto scaling costs and provide optimization recommendations
    """
    
    # Get cost for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    cost_response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Filter={
            'Tags': {
                'Key': 'aws:autoscaling:groupName',
                'Values': [asg_name]
            }
        },
        Metrics=['UnblendedCost']
    )
    
    total_cost = sum(
        float(day['Total']['UnblendedCost']['Amount'])
        for day in cost_response['ResultsByTime']
    )
    
    print(f"💰 Cost Analysis for {asg_name}")
    print(f"Total cost (last 30 days): ${total_cost:.2f}")
    print(f"Average daily cost: ${total_cost/30:.2f}")
    
    # Get ASG metrics
    group = autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[asg_name]
    )['AutoScalingGroups'][0]
    
    current_capacity = group['DesiredCapacity']
    max_capacity = group['MaxSize']
    min_capacity = group['MinSize']
    
    # Analyze scaling patterns from CloudWatch
    cloudwatch = boto3.client('cloudwatch')
    
    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/AutoScaling',
        MetricName='GroupDesiredCapacity',
        Dimensions=[
            {'Name': 'AutoScalingGroupName', 'Value': asg_name}
        ],
        StartTime=start_date,
        EndTime=end_date,
        Period=3600,  # 1 hour
        Statistics=['Average', 'Maximum', 'Minimum']
    )
    
    capacities = [d['Average'] for d in metrics['Datapoints']]
    avg_capacity = sum(capacities) / len(capacities) if capacities else 0
    max_used = max(capacities) if capacities else 0
    min_used = min(capacities) if capacities else 0
    
    print(f"\n📊 Capacity Analysis:")
    print(f"Average capacity used: {avg_capacity:.1f}")
    print(f"Peak capacity used: {max_used:.0f}")
    print(f"Minimum capacity used: {min_used:.0f}")
    print(f"Current max capacity: {max_capacity}")
    
    # Recommendations
    print(f"\n💡 Optimization Recommendations:")
    
    # 1. Right-size max capacity
    if max_used < max_capacity * 0.7:
        recommended_max = int(max_used * 1.2)  # 20% buffer
        print(f"✅ Reduce max capacity from {max_capacity} to {recommended_max}")
        print(f"   (Peak usage was only {max_used}, so {max_capacity} is over-provisioned)")
    
    # 2. Adjust minimum capacity
    if min_used > min_capacity * 1.5:
        recommended_min = int(min_used * 0.8)
        print(f"✅ Increase min capacity from {min_capacity} to {recommended_min}")
        print(f"   (Minimum usage suggests baseline is too low)")
    
    # 3. Spot instances recommendation
    if 'MixedInstancesPolicy' not in group:
        potential_savings = total_cost * 0.70  # ~70% savings with spot
        print(f"✅ Implement Spot Instances (save ~${potential_savings:.2f}/month)")
    
    # 4. Scheduled scaling
    # Analyze hourly patterns
    hourly_usage = {}
    for datapoint in metrics['Datapoints']:
        hour = datapoint['Timestamp'].hour
        if hour not in hourly_usage:
            hourly_usage[hour] = []
        hourly_usage[hour].append(datapoint['Average'])
    
    avg_by_hour = {h: sum(v)/len(v) for h, v in hourly_usage.items()}
    
    # Find low-usage periods
    low_hours = [h for h, avg in avg_by_hour.items() if avg < avg_capacity * 0.6]
    if low_hours:
        print(f"✅ Consider scheduled scaling during low-usage hours: {sorted(low_hours)}")
        print(f"   Scale down to {int(avg_capacity * 0.6)} instances")
    
    # 5. Instance type optimization
    print(f"✅ Review instance types - consider newer generation for better price/performance")

# Run analysis
if __name__ == '__main__':
    analyze_costs_and_optimize('myapp-asg')
```

#### Scheduled Cost Optimization

```bash
# Scale down during weekends
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name myapp-asg \
  --scheduled-action-name scale-down-weekend \
  --recurrence "0 0 * * SAT" \
  --min-size 1 \
  --desired-capacity 2 \
  --max-size 5

# Scale back up on Monday
aws autoscaling put-scheduled-update-group-action \
  --auto-scaling-group-name myapp-asg \
  --scheduled-action-name scale-up-monday \
  --recurrence "0 6 * * MON" \
  --min-size 2 \
  --desired-capacity 4 \
  --max-size 10
```

**Verification:**
- [ ] Spot/preemptible instances configured (if applicable)
- [ ] Cost savings calculated and documented
- [ ] Scheduled scaling implemented for predictable patterns
- [ ] Instance types right-sized
- [ ] Unused instances terminated
- [ ] Cost alerts configured
- [ ] Regular cost reviews scheduled

**If This Fails:**
→ Start with small percentage of spot instances (10-20%)
→ Ensure application can handle spot instance interruptions
→ Use capacity-optimized spot allocation strategy
→ Implement spot instance interruption handling
→ Monitor cost savings vs stability trade-offs

---

### Step 8: Set Up Monitoring and Alerting

**What:** Implement comprehensive monitoring for your auto scaling infrastructure, create dashboards for visibility, and configure alerts for anomalous scaling behavior or failures.

**How:**

#### CloudWatch Dashboard

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name MyApp-AutoScaling \
  --dashboard-body file://dashboard.json
```

**dashboard.json:**
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/AutoScaling", "GroupDesiredCapacity", {"stat": "Average", "label": "Desired"}],
          [".", "GroupInServiceInstances", {"stat": "Average", "label": "In Service"}],
          [".", "GroupMinSize", {"stat": "Average", "label": "Min"}],
          [".", "GroupMaxSize", {"stat": "Average", "label": "Max"}]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "Auto Scaling Group Capacity",
        "period": 300
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "CPU Utilization",
        "period": 300,
        "yAxis": {
          "left": {
            "min": 0,
            "max": 100
          }
        }
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "TargetResponseTime", {"stat": "Average"}]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "Response Time",
        "period": 300
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "HealthyHostCount", {"stat": "Average", "label": "Healthy"}],
          [".", "UnHealthyHostCount", {"stat": "Average", "label": "Unhealthy"}]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "Target Health",
        "period": 300
      }
    }
  ]
}
```

#### Alerting Configuration

```bash
# Alert on scaling failures
aws cloudwatch put-metric-alarm \
  --alarm-name asg-insufficient-capacity \
  --alarm-description "Alert when ASG cannot meet desired capacity" \
  --metric-name GroupInServiceInstances \
  --namespace AWS/AutoScaling \
  --statistic Average \
  --period 300 \
  --threshold 4 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=AutoScalingGroupName,Value=myapp-asg \
  --alarm-actions arn:aws:sns:region:account:ops-alerts

# Alert on high unhealthy instance rate
aws cloudwatch put-metric-alarm \
  --alarm-name asg-high-unhealthy-rate \
  --alarm-description "Alert when too many instances are unhealthy" \
  --metric-name UnhealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --threshold 2 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:region:account:ops-alerts

# Alert on max capacity reached
aws cloudwatch put-metric-alarm \
  --alarm-name asg-max-capacity-reached \
  --alarm-description "Alert when ASG reaches maximum capacity" \
  --metric-name GroupDesiredCapacity \
  --namespace AWS/AutoScaling \
  --statistic Average \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --dimensions Name=AutoScalingGroupName,Value=myapp-asg \
  --alarm-actions arn:aws:sns:region:account:ops-alerts

# Alert on rapid scaling
aws cloudwatch put-composite-alarm \
  --alarm-name asg-rapid-scaling \
  --alarm-description "Alert on rapid scaling events" \
  --alarm-rule "ALARM(scale-out-alarm) AND ALARM(scale-out-alarm-2)" \
  --actions-enabled \
  --alarm-actions arn:aws:sns:region:account:ops-alerts
```

#### Terraform Monitoring Configuration

```hcl
# cloudwatch.tf
resource "aws_cloudwatch_dashboard" "asg_dashboard" {
  dashboard_name = "MyApp-AutoScaling"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/AutoScaling", "GroupDesiredCapacity", {dimension: {AutoScalingGroupName: aws_autoscaling_group.app.name}}],
            [".", "GroupInServiceInstances", {dimension: {AutoScalingGroupName: aws_autoscaling_group.app.name}}]
          ]
          period = 300
          stat = "Average"
          region = var.region
          title = "ASG Capacity"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "asg_max_capacity" {
  alarm_name          = "asg-max-capacity-reached"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "GroupDesiredCapacity"
  namespace           = "AWS/AutoScaling"
  period              = 300
  statistic           = "Average"
  threshold           = aws_autoscaling_group.app.max_size
  alarm_description   = "Auto Scaling Group reached maximum capacity"
  alarm_actions       = [aws_sns_topic.ops_alerts.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
}

resource "aws_sns_topic" "ops_alerts" {
  name = "ops-alerts"
}

resource "aws_sns_topic_subscription" "ops_email" {
  topic_arn = aws_sns_topic.ops_alerts.arn
  protocol  = "email"
  endpoint  = "devops@company.com"
}
```

**Verification:**
- [ ] CloudWatch dashboard created and accessible
- [ ] Key metrics visible (capacity, CPU, response time, health)
- [ ] Alerts configured for critical conditions
- [ ] Alert notifications tested
- [ ] Ops team subscribed to alerts
- [ ] Runbooks linked to alerts
- [ ] Log aggregation configured

**If This Fails:**
→ Start with basic metrics (capacity, CPU) before adding custom metrics
→ Test alert notifications before production deployment
→ Set appropriate thresholds to avoid alert fatigue
→ Use composite alarms for complex conditions
→ Document alert response procedures

---

## Verification Checklist

After completing this workflow, verify:

**Configuration:**
- [ ] Auto Scaling Group created with correct capacity settings
- [ ] Launch template/configuration tested and working
- [ ] Instances distributed across multiple availability zones
- [ ] Health checks configured and passing
- [ ] Load balancer integration working

**Scaling:**
- [ ] Scaling policies configured (target tracking or step scaling)
- [ ] Cooldown periods set appropriately
- [ ] Scheduled scaling implemented (if applicable)
- [ ] Scaling tested under load
- [ ] Scale-in and scale-out both working correctly

**Health & Reliability:**
- [ ] Unhealthy instances automatically replaced
- [ ] Connection draining configured
- [ ] Lifecycle hooks implemented (if needed)
- [ ] Application health endpoint responding correctly
- [ ] High availability across multiple AZs

**Cost Optimization:**
- [ ] Spot/preemptible instances configured (if applicable)
- [ ] Capacity right-sized based on actual usage
- [ ] Scheduled scaling for predictable patterns
- [ ] Cost monitoring and alerting enabled

**Monitoring:**
- [ ] CloudWatch dashboard created
- [ ] Critical alerts configured
- [ ] Scaling events logged and monitored
- [ ] Runbooks created for common scenarios

---

## Common Issues & Solutions

### Issue: Instances Launching But Immediately Terminating

**Symptoms:**
- Instances appear in ASG then quickly terminate
- Health checks failing
- ASG constantly replacing instances

**Solution:**
```bash
# 1. Check scaling activities for failure reasons
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name myapp-asg \
  --max-records 20

# 2. Check instance system logs
aws ec2 get-console-output --instance-id i-xxxxx

# 3. Verify health check grace period
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name myapp-asg \
  --health-check-grace-period 600  # Increase to 10 minutes

# 4. Check application logs
aws logs tail /aws/ec2/myapp --follow

# Common causes:
# - Application takes too long to start
# - Health check path incorrect or unaccessible
# - Security group blocking load balancer health checks
# - Missing IAM permissions
```

**Prevention:**
- Set adequate health check grace period (5-10 minutes)
- Test application startup time
- Verify health endpoint before deploying
- Monitor instance launch metrics

---

### Issue: ASG Not Scaling Out Under Load

**Symptoms:**
- High CPU/load on instances
- Scaling policies not triggering
- Desired capacity not increasing

**Solution:**
```bash
# 1. Check if cooldown period is too long
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names myapp-asg \
  --query 'AutoScalingGroups[0].DefaultCooldown'

# 2. Check scaling policy configuration
aws autoscaling describe-policies \
  --auto-scaling-group-name myapp-asg

# 3. Verify CloudWatch metrics are being published
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=myapp-asg \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# 4. Check if max capacity is reached
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names myapp-asg \
  --query 'AutoScalingGroups[0].[DesiredCapacity,MaxSize]'

# 5. Review CloudWatch alarm state
aws cloudwatch describe-alarms --alarm-names high-cpu-alarm

# Solutions:
# - Reduce cooldown period if too conservative
# - Lower scaling threshold if too high
# - Increase max capacity if limit reached
# - Fix metric collection if not publishing
```

**Prevention:**
- Set appropriate cooldown periods (60-300s for scale-out)
- Monitor metric collection
- Set max capacity with buffer
- Test scaling policies before production

---

### Issue: Scaling Thrashing (Constant Scale In/Out)

**Symptoms:**
- Instances constantly launching and terminating
- Capacity oscillating
- High infrastructure costs

**Solution:**
```bash
# 1. Increase cooldown periods
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name myapp-asg \
  --default-cooldown 600  # 10 minutes

# 2. Adjust scaling policy thresholds
# Make scale-in more conservative
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name myapp-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "ScaleInCooldown": 900,
    "ScaleOutCooldown": 180
  }'

# 3. Use more stable metrics
# Consider using request count instead of CPU

# 4. Increase metric evaluation periods
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-alarm \
  --evaluation-periods 3  # Require 3 consecutive periods
  --datapoints-to-alarm 2  # Must breach in 2 of 3 periods
```

**Prevention:**
- Longer cooldowns for scale-in (10-15 min) than scale-out (3-5 min)
- Use average metrics over longer periods
- Set dead zones between scale-in/out thresholds
- Use target tracking instead of step scaling

---

## Best Practices

### DO:

✅ **Start with minimum instances for HA**
- Always set min size to at least 2
- Distribute across multiple availability zones
- Plan for zone failures

✅ **Use target tracking scaling policies**
- Simpler than step scaling
- Automatically calculates scale in/out
- Handles both directions

✅ **Set generous health check grace periods**
- Allow 5-10 minutes for application startup
- Account for container pulls, initialization
- Better than premature terminations

✅ **Make scale-in more conservative than scale-out**
- Longer cooldown for scale-in (10-15 min)
- Smaller adjustment steps
- Prevents oscillation

✅ **Use connection draining**
- Configure 2-5 minute deregistration delay
- Allow in-flight requests to complete
- Graceful shutdown procedures

✅ **Implement proper health checks**
- Application-aware health endpoints
- Check dependencies (database, cache)
- Return 503 when unhealthy

✅ **Monitor and alert on scaling events**
- Track scaling activities
- Alert on max capacity reached
- Monitor for launch failures

✅ **Test scaling before production**
- Load test scale-out behavior
- Verify scale-in works correctly
- Test failure scenarios

### DON'T:

❌ **Don't set min size to 1**
- No high availability
- Risk of downtime during deployment
- Always use 2+ for production

❌ **Don't use aggressive scaling thresholds**
- Causes unnecessary scaling
- Increases costs
- Better to slightly over-provision

❌ **Don't ignore cooldown periods**
- Leads to thrashing
- Wastes resources
- Makes costs unpredictable

❌ **Don't scale based on CPU alone**
- May not reflect actual load
- Consider request count, queue depth
- Use multiple metrics

❌ **Don't forget about stateful applications**
- Session state must be external
- Connection pooling limits
- Database connection handling

❌ **Don't skip testing lifecycle hooks**
- Ensure graceful startup/shutdown
- Test connection draining
- Verify cleanup procedures

❌ **Don't over-optimize prematurely**
- Start simple, add complexity as needed
- Monitor before optimizing
- Understand patterns first

❌ **Don't set max capacity too low**
- Prevents handling traffic spikes
- Add 50-100% buffer over peak
- Better to have headroom

---

## Related Workflows

**Prerequisites:**
- **cloud_provider_setup.md** - Cloud account and networking configured
- **docker_container_creation.md** - Application containerized
- **infrastructure_as_code_terraform.md** - IaC for managing ASG configuration

**Next Steps:**
- **application_monitoring_setup.md** - Comprehensive monitoring and alerting
- **cicd_pipeline_setup.md** - Automated deployment with auto scaling
- **performance_tuning.md** - Optimize application and infrastructure performance
- **backup_disaster_recovery.md** - Backup and DR for scaled infrastructure

**Related:**
- **kubernetes_deployment.md** - Container orchestration with auto scaling
- **log_aggregation_elk.md** - Centralized logging for scaled infrastructure
- **cost_optimization.md** - Further cost optimization strategies

---

## Tags

`devops` `auto-scaling` `aws` `azure` `gcp` `high-availability` `cost-optimization` `elasticity` `cloud` `infrastructure` `scalability` `medium-priority`
