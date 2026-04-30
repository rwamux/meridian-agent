output "backend_ecr_url" {
  description = "ECR repository URL for the backend image"
  value       = aws_ecr_repository.backend.repository_url
}

output "apprunner_service_url" {
  description = "App Runner service URL (direct HTTPS endpoint)"
  value       = "https://${aws_apprunner_service.backend.service_url}"
}

output "apprunner_service_arn" {
  description = "App Runner service ARN — set as APPRUNNER_SERVICE_ARN secret in GitHub"
  value       = aws_apprunner_service.backend.arn
}

output "cloudfront_domain" {
  description = "CloudFront domain — the public URL for the app"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions OIDC — set as AWS_ROLE_ARN secret in GitHub"
  value       = aws_iam_role.github_actions.arn
}

output "frontend_bucket" {
  description = "S3 bucket name for frontend assets — set as FRONTEND_BUCKET secret in GitHub"
  value       = aws_s3_bucket.frontend.id
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID — set as CLOUDFRONT_DISTRIBUTION_ID secret in GitHub"
  value       = aws_cloudfront_distribution.frontend.id
}
