# =================================================================================================
# Backend ECS Task Definition
# =================================================================================================

resource "aws_ecs_task_definition" "backend" {
  family                   = "CRM-${var.environment}-backend"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]

  cpu    = "256"
  memory = "768"

  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.backend.repository_url}:latest"
      essential = true

      cpu               = 0
      memoryReservation = var.task_memory_reservation["backend"]

      portMappings = [
        {
          containerPort = 4000
          hostPort      = 0
          protocol      = "tcp"
        }
      ]

      # ---------------- Runtime Environment Variables ----------------
      environment = [
        {
          name  = "PORT"
          value = "4000"
        },
        {
          name  = "NODE_ENV"
          value = var.environment
        },
        {
          name  = "OPENSSL_CONF"
          value = "/dev/null"
        },
        {
          name  = "PUBLIC_SERVER_FILE"
          value = "https://${aws_lb.main.dns_name}"
        }
      ]

      # ---------------- Secrets from SSM ----------------
      secrets = [
        {
          name      = "DATABASE"
          valueFrom = aws_ssm_parameter.mongodb_uri.arn
        },
        {
          name      = "JWT_SECRET"
          valueFrom = aws_ssm_parameter.jwt_secret.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_service_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "backend"
        }
      }
    }
  ])
}

# =================================================================================================
# Backend ECS Service
# =================================================================================================

resource "aws_ecs_service" "backend" {
  name            = "CRM-${var.environment}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1

  launch_type = "EC2"

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  health_check_grace_period_seconds = 60

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 4000
  }

  depends_on = [
    aws_lb_listener.http,
    aws_lb_listener.https
  ]
}
