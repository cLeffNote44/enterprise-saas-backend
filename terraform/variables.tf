variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  default     = "production"
}

variable "db_instance_class" {
  description = "RDS instance class"
  default     = "db.t3.medium"
}

variable "db_username" {
  description = "Database username"
  default     = "foundation"
}

variable "db_password" {
  description = "Database password"
  sensitive   = true
}

variable "redis_node_type" {
  description = "Redis node type"
  default     = "cache.t3.small"
}
