# ECS Cluster

resource "aws_ecs_cluster" "main" {
  name = "blinkit-${var.environment}-cluster"

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs_cluster_logs.name
      }
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = [aws_ecs_capacity_provider.ec2.name]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = aws_ecs_capacity_provider.ec2.name
  }
}

resource "aws_cloudwatch_log_group" "ecs_cluster_logs" {
  name              = "/aws/ecs/blinkit-${var.environment}-cluster"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "ecs_service_logs" {
  name              = "/aws/ecs/blinkit-${var.environment}-services"
  retention_in_days = 7
}
