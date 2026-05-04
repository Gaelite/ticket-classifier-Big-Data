terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket para los tickets clasificados
resource "aws_s3_bucket" "tickets" {
  bucket        = "${var.project_name}-tickets-${var.environment}-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

data "aws_caller_identity" "current" {}

# Lambda 1: Validate
module "validate_lambda" {
  source        = "./modules/lambda_function"
  function_name = "${var.project_name}-validate"
  source_dir    = "${path.module}/lambdas/validate"
  role_arn      = aws_iam_role.lambda_role.arn
  tags          = { Project = var.project_name }
}

# Lambda 2: Classify
module "classify_lambda" {
  source        = "./modules/lambda_function"
  function_name = "${var.project_name}-classify"
  source_dir    = "${path.module}/lambdas/classify"
  role_arn      = aws_iam_role.lambda_role.arn
  tags          = { Project = var.project_name }
}

# Lambda 3: Route
module "route_lambda" {
  source        = "./modules/lambda_function"
  function_name = "${var.project_name}-route"
  source_dir    = "${path.module}/lambdas/route"
  role_arn      = aws_iam_role.lambda_role.arn

  environment_variables = {
    BUCKET_NAME = aws_s3_bucket.tickets.bucket
  }

  tags = { Project = var.project_name }
}

# Step Function
resource "aws_sfn_state_machine" "ticket_classifier" {
  name     = "${var.project_name}-state-machine"
  role_arn = aws_iam_role.sfn_role.arn

  definition = jsonencode({
    Comment = "Support Ticket Classifier Pipeline"
    StartAt = "Validate"
    States = {
      Validate = {
        Type     = "Task"
        Resource = module.validate_lambda.function_arn
        Next     = "Classify"
        Catch = [{
          ErrorEquals = ["ValidationError"]
          Next        = "ValidationFailed"
        }]
      }

      Classify = {
        Type     = "Task"
        Resource = module.classify_lambda.function_arn
        Next     = "ChooseBranch"
      }

      ChooseBranch = {
        Type = "Choice"
        Choices = [
          {
            Variable     = "$.severity"
            StringEquals = "urgent"
            Next         = "Route"
          },
          {
            Variable     = "$.severity"
            StringEquals = "normal"
            Next         = "Route"
          }
        ]
        Default = "Route"
      }

      Route = {
        Type     = "Task"
        Resource = module.route_lambda.function_arn
        Next     = "Done"
      }

      ValidationFailed = {
        Type  = "Fail"
        Error = "ValidationError"
        Cause = "Ticket failed validation checks"
      }

      Done = {
        Type = "Succeed"
      }
    }
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}