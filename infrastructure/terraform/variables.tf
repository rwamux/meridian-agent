variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name used for naming/tagging resources"
  type        = string
  default     = "meridian"
}

variable "environment" {
  description = "Deployment environment (staging | production)"
  type        = string
  default     = "production"
}

variable "backend_image_tag" {
  description = "Docker image tag for the backend (overridden by CI)"
  type        = string
  default     = "latest"
}

variable "backend_cpu" {
  description = "App Runner vCPU allocation: '256' (0.25), '512' (0.5), '1024' (1), '2048' (2), '4096' (4)"
  type        = string
  default     = "512"
}

variable "backend_memory" {
  description = "App Runner memory in MB: '512', '1024', '2048', '3072', '4096'"
  type        = string
  default     = "1024"
}

variable "openrouter_api_key" {
  description = "OpenRouter API key — stored in Secrets Manager"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "Secret used to sign JWTs — minimum 32 chars"
  type        = string
  sensitive   = true
}

variable "mcp_server_url" {
  description = "Meridian MCP server URL"
  type        = string
  default     = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
}

variable "model" {
  description = "OpenRouter model identifier"
  type        = string
  default     = "anthropic/claude-haiku-4-5"
}
