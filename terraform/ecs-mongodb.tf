# =================================================================================================
# MongoDB ECS Task Definition (CRM)
# =================================================================================================

resource "aws_ecs_task_definition" "mongodb" {
  family                   = "CRM-${var.environment}-mongodb"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "mongodb"
      image     = "mongo:6.0"
      essential = true

      cpu               = 0
      memoryReservation = var.task_memory_reservation["mongodb"]

      portMappings = [
        {
          containerPort = 27017
          hostPort      = 27017
          protocol      = "tcp"
        }
      ]

      # ---------------- Mongo Init Configuration ----------------
      environment = [
        {
          name  = "MONGO_INITDB_ROOT_USERNAME"
          value = "root"
        },
        {
          name  = "MONGO_INITDB_ROOT_PASSWORD"
          value = "rootpassword"
        },
        {
          name  = "MONGO_INITDB_DATABASE"
          value = "admin"
        }
      ]

      # ---------------- Persistent Storage ----------------
      mountPoints = [
        {
          sourceVolume  = "mongodb_data"
          containerPath = "/data/db"
          readOnly      = false
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_service_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "mongodb"
        }
      }
    }
  ])

  # ---------------- Host Volume (EC2-backed persistence) ----------------
  volume {
    name      = "mongodb_data"
    host_path = "/var/lib/mongo_data_crm"
  }
}

# =================================================================================================
# MongoDB ECS Service (NO Load Balancer)
# =================================================================================================

resource "aws_ecs_service" "mongodb" {
  name            = "CRM-${var.environment}-mongodb"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.mongodb.arn
  desired_count   = 1

  launch_type = "EC2"
}
