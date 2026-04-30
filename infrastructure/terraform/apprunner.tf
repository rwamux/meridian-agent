resource "aws_apprunner_service" "backend" {
  service_name = "${local.name_prefix}-backend"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_access.arn
    }

    image_repository {
      image_configuration {
        port = "8000"

        runtime_environment_variables = {
          MCP_SERVER_URL     = var.mcp_server_url
          MODEL              = var.model
          CORS_ORIGINS       = "[\"*\"]"
          # Secrets injected here on first apply; CI keeps them current on every deploy
          OPENROUTER_API_KEY = var.openrouter_api_key
          JWT_SECRET         = var.jwt_secret
        }
      }

      image_identifier      = "${aws_ecr_repository.backend.repository_url}:${var.backend_image_tag}"
      image_repository_type = "ECR"
    }

    auto_deployments_enabled = false
  }

  instance_configuration {
    cpu               = var.backend_cpu
    memory            = var.backend_memory
    instance_role_arn = aws_iam_role.apprunner_instance.arn
  }

  health_check_configuration {
    path                = "/api/health"
    protocol            = "HTTP"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  lifecycle {
    # CI manages the image tag — prevent Terraform from reverting deployments
    ignore_changes = [source_configuration]
  }
}
