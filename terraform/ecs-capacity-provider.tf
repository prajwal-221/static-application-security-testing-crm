# EC2 Capacity Provider for ECS Cluster

# -------------------------------------------------------------------------------------------------
# ECS Optimized AMI
# -------------------------------------------------------------------------------------------------

data "aws_ssm_parameter" "ecs_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}

# -------------------------------------------------------------------------------------------------
# Launch Template
# -------------------------------------------------------------------------------------------------

resource "aws_launch_template" "ecs_instance" {
  name_prefix   = "blinkit-${var.environment}-ecs-lt-"
  image_id      = data.aws_ssm_parameter.ecs_ami.value
  instance_type = var.instance_type

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }

  network_interfaces {
    associate_public_ip_address = true # Since we are in public subnets (or private with NAT) - wait, plan says single NAT, so instances in private subnet
    security_groups             = [aws_security_group.ecs_instances.id]
  }

  user_data = base64encode(<<EOF
#!/bin/bash
echo "ECS_CLUSTER=blinkit-${var.environment}-cluster" >> /etc/ecs/ecs.config
EOF
  )

  # EBS Volume for container storage and MongoDB data mount
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 30
      volume_type = "gp3"
    }
  }
  
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "blinkit-${var.environment}-ecs-instance"
    }
  }
}

# -------------------------------------------------------------------------------------------------
# Auto Scaling Group
# -------------------------------------------------------------------------------------------------

resource "aws_autoscaling_group" "ecs_asg" {
  name                = "blinkit-${var.environment}-asg"
  vpc_zone_identifier = local.private_subnet_ids # Deploy instances in private subnets
  max_size            = 1 # Cost optimization - max 1 instance
  min_size            = 1
  desired_capacity    = 1

  launch_template {
    id      = aws_launch_template.ecs_instance.id
    version = "$Latest"
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = true
    propagate_at_launch = true
  }
  
  # Refresh instances when launch template changes
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 0 # Allow going to 0 for update since we only have 1 instance
    }
  }
}

# -------------------------------------------------------------------------------------------------
# Capacity Provider
# -------------------------------------------------------------------------------------------------

resource "aws_ecs_capacity_provider" "ec2" {
  name = "blinkit-${var.environment}-ec2-cp"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.ecs_asg.arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      maximum_scaling_step_size = 1
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }
}
