variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, workshop)"
  type        = string
  default     = "workshop"
}

variable "vpc_id" {
  description = "ID of existing VPC to use. If empty, a new VPC will be created."
  type        = string
  default     = ""
}

variable "public_subnet_ids" {
  description = "List of existing public subnet IDs. Required if vpc_id is provided."
  type        = list(string)
  default     = []
}

variable "private_subnet_ids" {
  description = "List of existing private subnet IDs. Required if vpc_id is provided."
  type        = list(string)
  default     = []
}

variable "vpc_cidr" {
  description = "CIDR block for new VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets_cidr" {
  description = "CIDR blocks for new public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets_cidr" {
  description = "CIDR blocks for new private subnets"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "instance_type" {
  description = "EC2 instance type for ECS cluster"
  type        = string
  default     = "t3.medium"
}

variable "mongodb_port" {
  description = "Port for MongoDB"
  type        = number
  default     = 27017
}

variable "task_memory_reservation" {
  description = "Soft memory limit for tasks"
  type        = map(number)
  default = {
    frontend = 256
    backend  = 768
    mongodb  = 512
  }
}

variable "access_token_secret" {
  description = "Secret key for JWT access token"
  type        = string
  sensitive   = true
}

variable "refresh_token_secret" {
  description = "Secret key for JWT refresh token"
  type        = string
  sensitive   = true
}

variable "mongodb_root_password" {
  description = "Root password for MongoDB"
  type        = string
  sensitive   = true
  default     = "password123" # Change this in production!
}
