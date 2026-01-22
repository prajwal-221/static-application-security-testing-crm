# SSM Parameters for Secrets Management

resource "aws_ssm_parameter" "access_token_secret" {
  name        = "/${var.environment}/backend/ACCESS_TOKEN_SECRET"
  description = "JWT Access Token Secret"
  type        = "SecureString"
  value       = var.access_token_secret
}

resource "aws_ssm_parameter" "refresh_token_secret" {
  name        = "/${var.environment}/backend/REFRESH_TOKEN_SECRET"
  description = "JWT Refresh Token Secret"
  type        = "SecureString"
  value       = var.refresh_token_secret
}

resource "aws_ssm_parameter" "mongodb_root_password" {
  name        = "/${var.environment}/mongodb/root-password"
  description = "MongoDB Root Password"
  type        = "SecureString"
  value       = var.mongodb_root_password
}
