# Security Groups

# -------------------------------------------------------------------------------------------------
# ALB Security Group
# -------------------------------------------------------------------------------------------------

resource "aws_security_group" "alb" {
  name        = "${var.environment}-alb-sg"
  description = "Allow HTTP/HTTPS traffic from internet"
  vpc_id      = local.vpc_id

  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-alb-sg"
  }
}

# -------------------------------------------------------------------------------------------------
# ECS Instance Security Group (EC2 Host)
# -------------------------------------------------------------------------------------------------

resource "aws_security_group" "ecs_instances" {
  name        = "${var.environment}-ecs-instances-sg"
  description = "Security group for ECS instances"
  vpc_id      = local.vpc_id

  # Allow dynamic port mapping range and direct service ports from ALB
  ingress {
    description     = "Allow traffic from ALB"
    from_port       = 0
    to_port         = 65535 # Allow all ports from ALB (Dynamic ports)
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow internal traffic between instances (if we had multiple) and container-to-container
  ingress {
    description = "Allow internal traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }
  
  # Allow SSH (optional, removing for security/workshop simplicity to avoid key handling)
  # If needed, use SSM Session Manager

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-ecs-instances-sg"
  }
}
