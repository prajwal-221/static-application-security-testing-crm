# Terraform Outputs

output "alb_dns_name" {
  description = "The DNS name of the load balancer. Access the application here."
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "The URL of the application."
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_frontend_repository_url" {
  description = "The URL of the ECR repository for the frontend."
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_backend_repository_url" {
  description = "The URL of the ECR repository for the backend."
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_login_command" {
  description = "Command to log in to ECR."
  value       = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.backend.repository_url}" # Truncated to base URL usually, but this works for full URI too
}

output "cluster_name" {
  description = "The name of the ECS cluster."
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_backend" {
  description = "The name of the backend ECS service."
  value       = aws_ecs_service.backend.name
}

output "ecs_service_frontend" {
  description = "The name of the frontend ECS service."
  value       = aws_ecs_service.frontend.name
}

output "ecs_service_mongodb" {
  description = "The name of the MongoDB ECS service."
  value       = aws_ecs_service.mongodb.name
}

output "vpc_id" {
  description = " The ID of the VPC."
  value       = local.vpc_id
}
