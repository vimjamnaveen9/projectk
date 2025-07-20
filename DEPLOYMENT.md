# 🚀 Quick Deployment Guide

## Prerequisites

1. **AWS Account** with administrative access
2. **AWS CLI** configured with appropriate permissions
3. **Terraform** >= 1.5.7 installed
4. **Git** for cloning the repository

## Step 1: Initial Setup

```bash
# Clone the repository
git clone https://github.com/Harish-Apps/8byte.git
cd 8byte

# Verify AWS credentials
aws sts get-caller-identity
```

## Step 2: Create Terraform Backend Resources

```bash
# Create S3 bucket for Terraform state (replace with unique name)
BUCKET_NAME="your-terraform-state-bucket-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-west-2

# Wait for table to be created
aws dynamodb wait table-exists --table-name terraform-state-lock --region us-west-2
```

## Step 3: Configure Terraform

```bash
cd terraform

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars

# Update backend configuration
cat > backend.tf << EOF
terraform {
  backend "s3" {
    bucket         = "$BUCKET_NAME"
    key            = "dev/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
EOF
```

## Step 4: Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review the planned changes
terraform plan

# Deploy infrastructure (takes ~15-20 minutes)
terraform apply

# Get application URL
terraform output application_url
```

## Step 5: Verify Deployment

```bash
# Get the application URL
APP_URL=$(terraform output -raw application_url)

# Test the application
curl $APP_URL/health
curl $APP_URL/api/info
```

## Step 6: Setup CI/CD (Optional)

1. **Fork the repository** to your GitHub account

2. **Add GitHub Secrets**:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `TERRAFORM_STATE_BUCKET` (the bucket name from Step 2)
   - `TERRAFORM_LOCK_TABLE` (terraform-state-lock)
   - `EMAIL_USERNAME` (for notifications)
   - `EMAIL_PASSWORD` (for notifications)
   - `NOTIFICATION_EMAIL` (for notifications)

3. **Push changes** to trigger CI/CD pipeline

## Access Your Infrastructure

### Application URLs
- **Application**: `http://<alb-dns-name>`
- **Health Check**: `http://<alb-dns-name>/health`
- **API Info**: `http://<alb-dns-name>/api/info`

### AWS Console Links
- **CloudWatch Dashboards**: Check outputs for direct links
- **RDS Instance**: AWS Console > RDS
- **Load Balancer**: AWS Console > EC2 > Load Balancers
- **Auto Scaling Group**: AWS Console > EC2 > Auto Scaling Groups

## Cleanup

To destroy all resources (⚠️ **This will delete everything**):

```bash
cd terraform
terraform destroy
```

Don't forget to delete the S3 bucket and DynamoDB table:

```bash
# Empty and delete S3 bucket
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3 rb s3://$BUCKET_NAME

# Delete DynamoDB table
aws dynamodb delete-table --table-name terraform-state-lock --region us-west-2
```

## Troubleshooting

### Common Issues

1. **"Access Denied" errors**: Verify AWS credentials and permissions
2. **"Bucket already exists"**: Use a unique bucket name
3. **"Resource not found"**: Ensure you're in the correct AWS region
4. **Terraform state issues**: Check S3 bucket permissions

### Support

- Check the detailed documentation in `/docs/`
- Review CloudWatch logs for application issues
- Use AWS support for infrastructure problems

## Next Steps

1. **Configure HTTPS**: Add SSL certificate to ALB
2. **Setup Custom Domain**: Configure Route 53 DNS
3. **Add Monitoring**: Enhance CloudWatch dashboards
4. **Scale for Production**: Adjust instance types and counts
5. **Implement Backup**: Configure additional backup strategies

---

**🎉 Congratulations!** You now have a production-ready, scalable, and secure cloud infrastructure running your application with comprehensive monitoring and automated CI/CD pipeline.