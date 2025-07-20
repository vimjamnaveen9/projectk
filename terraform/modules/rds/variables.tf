variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "db_subnet_group_name" {
  description = "Database subnet group name"
  type        = string
}

variable "db_security_group_id" {
  description = "Database security group ID"
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database master username"
  type        = string
}

variable "db_allocated_storage" {
  description = "Database allocated storage in GB"
  type        = number
}

variable "db_max_allocated_storage" {
  description = "Database maximum allocated storage in GB"
  type        = number
}

variable "backup_retention_period" {
  description = "Database backup retention period in days"
  type        = number
}

variable "backup_window" {
  description = "Database backup window"
  type        = string
}

variable "maintenance_window" {
  description = "Database maintenance window"
  type        = string
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for RDS"
  type        = bool
}

variable "multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
}