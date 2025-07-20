# Architecture Documentation

## System Architecture

The 8byte application follows a modern cloud-native architecture pattern with clear separation of concerns across multiple tiers.

### High-Level Architecture

```
                                    ┌─────────────────┐
                                    │   GitHub        │
                                    │   Actions       │
                                    │   CI/CD         │
                                    └─────────┬───────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                 AWS Cloud                                         │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              Internet Gateway                                │ │
│  └─────────────────────────┬───────────────────────────────────────────────────┘ │
│                            │                                                     │
│  ┌─────────────────────────▼───────────────────────────────────────────────────┐ │
│  │                    Application Load Balancer                                │ │
│  │                         (Public Subnets)                                   │ │
│  └─────────────────────────┬───────────────────────────────────────────────────┘ │
│                            │                                                     │
│  ┌─────────────────────────▼───────────────────────────────────────────────────┐ │
│  │                      Private Subnets                                       │ │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │ │
│  │  │    EC2      │    │    EC2      │    │    EC2      │    │    EC2      │  │ │
│  │  │  Instance   │    │  Instance   │    │  Instance   │    │  Instance   │  │ │
│  │  │     AZ-A    │    │     AZ-B    │    │     AZ-A    │    │     AZ-B    │  │ │
│  │  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │ │
│  └─────────────────────────┬───────────────────────────────────────────────────┘ │
│                            │                                                     │
│  ┌─────────────────────────▼───────────────────────────────────────────────────┐ │
│  │                     Database Subnets                                       │ │
│  │                  ┌─────────────────────┐                                   │ │
│  │                  │   RDS PostgreSQL    │                                   │ │
│  │                  │     Multi-AZ        │                                   │ │
│  │                  │   Primary + Standby │                                   │ │
│  │                  └─────────────────────┘                                   │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Monitoring & Logging                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │ CloudWatch  │  │ CloudWatch  │  │    S3       │  │  Secrets Manager    │ │ │
│  │  │ Dashboards  │  │Log Groups   │  │ALB Logs     │  │  DB Credentials     │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Load Balancer Tier

**Application Load Balancer (ALB)**
- **Purpose**: Distributes incoming traffic across multiple EC2 instances
- **Features**:
  - Health checks on `/health` endpoint
  - SSL/TLS termination (when configured)
  - Access logging to S3
  - Integration with Auto Scaling Groups

**Configuration**:
- Listeners: HTTP (port 80), HTTPS (port 443) ready
- Target Groups: Routes to application instances on port 8000
- Health Check: HTTP GET `/health` with 30-second intervals

### 2. Application Tier

**EC2 Auto Scaling Group**
- **Purpose**: Provides scalable compute capacity for the application
- **Configuration**:
  - Launch Template with user data for application setup
  - Cross-AZ deployment for high availability
  - Auto scaling based on CPU utilization
  - Integration with CloudWatch for monitoring

**Application Runtime**:
- Python Flask application
- Gunicorn WSGI server (4 workers)
- CloudWatch agent for custom metrics
- Systemd service for process management

**Scaling Policies**:
- Scale Up: CPU > 80% for 2 evaluation periods
- Scale Down: CPU < 20% for 2 evaluation periods
- Cooldown: 5 minutes between scaling activities

### 3. Database Tier

**Amazon RDS PostgreSQL**
- **Purpose**: Managed relational database service
- **Configuration**:
  - Engine: PostgreSQL 15.4
  - Multi-AZ deployment for high availability
  - Automated backups with 7-day retention
  - Encryption at rest and in transit
  - Performance Insights enabled

**Security**:
- Database subnet group in private subnets
- Security group allowing access only from application tier
- Credentials stored in AWS Secrets Manager

### 4. Network Architecture

**VPC Design**:
```
VPC CIDR: 10.0.0.0/16

Public Subnets:
- 10.0.1.0/24 (AZ-A) - ALB, NAT Gateway
- 10.0.2.0/24 (AZ-B) - ALB, NAT Gateway

Private Subnets:
- 10.0.11.0/24 (AZ-A) - Application instances
- 10.0.12.0/24 (AZ-B) - Application instances

Database Subnets:
- 10.0.21.0/24 (AZ-A) - RDS Primary
- 10.0.22.0/24 (AZ-B) - RDS Standby
```

**Routing**:
- Public subnets route to Internet Gateway
- Private subnets route through NAT Gateways
- Database subnets have no external routing

### 5. Security Architecture

**Defense in Depth**:

1. **Network Security**:
   - VPC isolation
   - Security groups with least privilege
   - Private subnets for sensitive resources
   - NACLs for additional protection

2. **Application Security**:
   - Non-root container execution
   - Secrets management integration
   - Input validation and sanitization
   - Security headers implementation

3. **Data Security**:
   - Encryption at rest (RDS, S3, EBS)
   - Encryption in transit (HTTPS, SSL)
   - Database access controls
   - Audit logging

## Design Patterns

### 1. Immutable Infrastructure

- Infrastructure defined as code (Terraform)
- No manual server configuration
- Replacement rather than modification
- Version-controlled infrastructure changes

### 2. Auto Scaling

- Horizontal scaling based on metrics
- Health check integration
- Graceful instance replacement
- Cost optimization through demand-based scaling

### 3. High Availability

- Multi-AZ deployment
- Database failover capability
- Load balancer health checks
- Redundant NAT Gateways

### 4. Observability

- Comprehensive logging strategy
- Custom application metrics
- Infrastructure monitoring
- Alerting and notification

## Data Flow

### Request Flow

1. **User Request** → Internet Gateway
2. **Internet Gateway** → Application Load Balancer
3. **ALB** → Health check and route to healthy instance
4. **EC2 Instance** → Process request, query database if needed
5. **Database Query** → RDS PostgreSQL in database subnet
6. **Response** → Back through the same path

### Deployment Flow

1. **Code Push** → GitHub repository
2. **CI Pipeline** → Run tests, security scans, build image
3. **CD Pipeline** → Deploy to staging, manual approval, deploy to production
4. **Health Checks** → Verify deployment success
5. **Monitoring** → Continuous monitoring and alerting

## Performance Considerations

### Caching Strategy

- Application-level caching with Redis (future enhancement)
- CloudFront CDN for static assets (future enhancement)
- Database query optimization

### Database Performance

- Connection pooling
- Query optimization
- Performance Insights monitoring
- Read replicas for read-heavy workloads (future enhancement)

### Application Performance

- Gunicorn multi-worker configuration
- Async request handling
- Resource monitoring and alerting
- Auto scaling based on performance metrics

## Disaster Recovery

### Backup Strategy

- RDS automated backups (7-day retention)
- Cross-region backup replication (configurable)
- Infrastructure code in version control
- Immutable infrastructure for quick recovery

### Recovery Procedures

1. **Database Recovery**: Point-in-time recovery from RDS backups
2. **Infrastructure Recovery**: Terraform apply from version control
3. **Application Recovery**: Container image redeployment from ECR
4. **Configuration Recovery**: Secrets and configuration from AWS services

### RTO/RPO Targets

- **Recovery Time Objective (RTO)**: 30 minutes
- **Recovery Point Objective (RPO)**: 5 minutes
- **Multi-AZ failover**: < 2 minutes
- **Infrastructure rebuild**: 15-20 minutes