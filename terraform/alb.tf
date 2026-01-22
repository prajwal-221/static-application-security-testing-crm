# Application Load Balancer

resource "aws_lb" "main" {
  name               = "blinkit-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = local.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name = "${var.environment}-alb"
  }
}

# -------------------------------------------------------------------------------------------------
# Target Groups
# -------------------------------------------------------------------------------------------------

resource "aws_lb_target_group" "frontend" {
  name        = "blinkit-${var.environment}-fe-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "instance" # Must be 'instance' for Bridge mode dynamic ports

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 30
    interval            = 60
    matcher             = "200"
  }
}

resource "aws_lb_target_group" "backend" {
  name        = "blinkit-${var.environment}-be-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "instance" # Must be 'instance' for Bridge mode dynamic ports

  health_check {
    path                = "/" # Backend health check path
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 30
    interval            = 60
    matcher             = "200,404" # Accept 404 as healthy if root endpoint returns JSON message
  }
}

# -------------------------------------------------------------------------------------------------
# Listener Rules
# -------------------------------------------------------------------------------------------------

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# Route /api/* requests to backend
resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}
