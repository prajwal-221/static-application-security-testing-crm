# ECR Repositories

resource "aws_ecr_repository" "frontend" {
  name                 = "blinkit-${var.environment}-frontend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # Easy cleanup for workshops

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "backend" {
  name                 = "blinkit-${var.environment}-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # Easy cleanup for workshops

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Lifecycle Policy to keep only 5 latest images to save storage costs
resource "aws_ecr_lifecycle_policy" "frontend_policy" {
  repository = aws_ecr_repository.frontend.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 5 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 5
      }
      action = {
        type = "expire"
      }
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "backend_policy" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 5 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 5
      }
      action = {
        type = "expire"
      }
    }]
  })
}
