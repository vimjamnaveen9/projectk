<<<<<<< HEAD
# 8byte - Full-Stack DevOps Infrastructure

A comprehensive cloud-native application demonstrating enterprise-grade DevOps practices with AWS, Terraform, and GitHub Actions.

## 🏗️ Architecture Overview

This project implements a modern, scalable, and secure cloud infrastructure featuring:

- **Infrastructure as Code**: Terraform for AWS resource management
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **Containerized Application**: Python Flask app with Docker
- **Monitoring & Logging**: CloudWatch dashboards and centralized logging
- **High Availability**: Multi-AZ deployment with auto-scaling
- **Security**: Least privilege access, secrets management, and encryption

### Infrastructure Components

```
┌─────────────────────────────────────────────────────────┐
│                     Internet                            │
└─────────────────────┬───────────────────────────────────┘
                      │
            ┌─────────▼─────────┐
            │  Application      │
            │  Load Balancer    │
            │  (ALB)           │
            └─────────┬─────────┘
                      │
        ┌─────────────▼─────────────┐
        │        VPC Network        │
        │  ┌─────────┬─────────┐   │
        │  │ Public  │ Public  │   │
        │  │Subnet AZ│Subnet AZ│   │
        │  │    A    │    B    │   │
        │  └─────────┼─────────┘   │
        │  ┌─────────▼─────────┐   │
        │  │Private  │Private  │   │
        │  │Subnet AZ│Subnet AZ│   │
        │  │    A    │    B    │   │
        │  │ ┌─────┐ │ ┌─────┐ │   │
        │  │ │ EC2 │ │ │ EC2 │ │   │
        │  │ │ ASG │ │ │ ASG │ │   │
        │  │ └─────┘ │ └─────┘ │   │
        │  └─────────┼─────────┘   │
        │  ┌─────────▼─────────┐   │
        │  │   Database        │   │
        │  │   Subnets         │   │
        │  │ ┌─────────────┐   │   │
        │  │ │ RDS         │   │   │
        │  │ │ PostgreSQL  │   │   │
        │  │ │ Multi-AZ    │   │   │
        │  │ └─────────────┘   │   │
        │  └───────────────────┘   │
        └─────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- Terraform >= 1.5.7
- Git
- AWS CLI configured

### 1. Clone and Setup

```bash
git clone https://github.com/Harish-Apps/8byte.git
cd 8byte
```

### 2. Configure Terraform Backend

Create an S3 bucket and DynamoDB table for Terraform state management:

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://your-terraform-state-bucket-name --region us-west-2

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-west-2
```

### 3. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your specific values
```

### 4. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply infrastructure
terraform apply
```

### 5. Access Application

After deployment, get the application URL:

```bash
terraform output application_url
```

## 📋 Configuration

### Terraform Variables

Key configuration options in `terraform.tfvars`:

```hcl
# Project Configuration
project_name = "8byte-app"
environment  = "dev"
aws_region   = "us-west-2"

# Network Configuration
vpc_cidr               = "10.0.0.0/16"
availability_zones     = ["us-west-2a", "us-west-2b"]

# Compute Configuration
instance_type    = "t3.micro"
min_size         = 2
max_size         = 6
desired_capacity = 2

# Database Configuration
db_instance_class = "db.t3.micro"
db_name          = "appdb"
multi_az         = true  # Set to true for production
```

### GitHub Secrets Configuration

For CI/CD pipeline, configure these GitHub secrets:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
TERRAFORM_STATE_BUCKET
TERRAFORM_LOCK_TABLE
EMAIL_USERNAME
EMAIL_PASSWORD
NOTIFICATION_EMAIL
```

## 🔄 CI/CD Pipeline

### Continuous Integration (CI)

Triggered on push to main/develop branches:

1. **Code Quality**: Linting with flake8
2. **Security Scanning**: Bandit for code, Safety for dependencies
3. **Unit Testing**: pytest with coverage reporting
4. **Terraform Validation**: Format check and validation
5. **Container Security**: Trivy vulnerability scanning
6. **Integration Testing**: Database connectivity tests

### Continuous Deployment (CD)

Triggered after successful CI:

1. **Build & Push**: Docker image to Amazon ECR
2. **Staging Deployment**: Automated deployment to staging
3. **Manual Approval**: Required for production deployment
4. **Production Deployment**: Blue-green deployment strategy
5. **Health Checks**: Automated verification of deployment
6. **Notifications**: Email alerts on success/failure

## 📊 Monitoring & Logging

### CloudWatch Dashboards

Two comprehensive dashboards are automatically created:

1. **Infrastructure Dashboard**:
   - ALB metrics (requests, response time, error rates)
   - EC2 metrics (CPU, network, auto-scaling)
   - RDS metrics (CPU, connections, latency)

2. **Application Dashboard**:
   - Custom application metrics
   - Memory and disk usage
   - Application logs analysis

### Log Groups

Centralized logging with retention policies:

- **Application Logs**: 14 days retention
- **System Logs**: 7 days retention
- **Security Logs**: 30 days retention
- **ALB Access Logs**: 7 days retention

### Alerting

CloudWatch alarms for:

- High CPU utilization (EC2 and RDS)
- High database connections
- Elevated ALB response times
- HTTP 5XX error rates

## 🔒 Security Best Practices

### Infrastructure Security

- **Network Isolation**: Private subnets for application and database tiers
- **Security Groups**: Least privilege access rules
- **Encryption**: At rest and in transit for all data
- **IAM Roles**: Fine-grained permissions for EC2 instances

### Application Security

- **Secrets Management**: AWS Secrets Manager for database credentials
- **Container Security**: Non-root user, minimal base image
- **Dependency Scanning**: Automated vulnerability detection
- **Code Scanning**: Static analysis with Bandit

### Access Control

- **Multi-Factor Authentication**: Required for production deployments
- **Audit Logging**: CloudTrail for API calls
- **Network ACLs**: Additional layer of network security

## 💰 Cost Optimization

### Infrastructure Costs

- **Auto Scaling**: Automatic scaling based on demand
- **Reserved Instances**: Recommended for production workloads
- **Spot Instances**: Consider for non-critical workloads
- **Resource Rightsizing**: t3.micro instances for development

### Storage Optimization

- **S3 Lifecycle Policies**: Automatic log archival and deletion
- **RDS Storage**: Auto-scaling enabled to prevent over-provisioning
- **EBS Optimization**: GP2 storage for cost-effective performance

### Monitoring Costs

- **CloudWatch**: Efficient log retention policies
- **Detailed Monitoring**: Enabled only where necessary
- **Custom Metrics**: Optimized collection intervals

## 🔄 Backup Strategy

### Database Backups

- **Automated Backups**: 7-day retention (configurable)
- **Backup Window**: Scheduled during low-traffic periods
- **Cross-Region Backups**: Optional for disaster recovery
- **Point-in-Time Recovery**: Enabled for data protection

### Terraform State Backups

- **S3 Versioning**: Enabled for state file history
- **Cross-Region Replication**: Optional for disaster recovery
- **State Locking**: DynamoDB prevents concurrent modifications

### Application Backups

- **Container Images**: Stored in ECR with lifecycle policies
- **Configuration**: Version controlled in Git
- **Infrastructure Code**: Immutable infrastructure approach

## 🛠️ Troubleshooting

### Common Issues

1. **Terraform Init Fails**
   ```bash
   # Check AWS credentials and permissions
   aws sts get-caller-identity
   ```

2. **Application Health Check Fails**
   ```bash
   # Check application logs
   aws logs tail /aws/ec2/8byte-app-dev-app-logs --follow
   ```

3. **Database Connection Issues**
   ```bash
   # Verify security groups and network connectivity
   # Check database credentials in Secrets Manager
   ```

### Logs and Debugging

- **CloudWatch Logs**: Centralized application and system logs
- **EC2 Instance Connect**: Secure shell access for debugging
- **RDS Performance Insights**: Database performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests locally
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Additional Resources

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)

---

**Note**: This infrastructure is designed for demonstration and development purposes. For production deployments, ensure proper security reviews, compliance checks, and disaster recovery planning.
=======
# projectk
>>>>>>> 20ca0f58b7607035707a20725a19e78a40cad1f3
