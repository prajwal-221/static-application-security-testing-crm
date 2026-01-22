# Route 53 Private Hosted Zone for Internal Service Discovery

resource "aws_route53_zone" "internal" {
  name = "blinkit.internal"
  vpc {
    vpc_id = local.vpc_id
  }
  
  comment = "Internal DNS for Blinkit services"
}

# Fetch the EC2 instance private IP
data "aws_instances" "ecs_nodes" {
  instance_tags = {
    "aws:autoscaling:groupName" = aws_autoscaling_group.ecs_asg.name
  }
}

# Manual A record entry for MongoDB
resource "aws_route53_record" "mongodb" {
  zone_id = aws_route53_zone.internal.zone_id
  name    = "mongodb.blinkit.internal"
  type    = "A"
  ttl     = "60"
  records = [data.aws_instances.ecs_nodes.private_ips[0]]
}
