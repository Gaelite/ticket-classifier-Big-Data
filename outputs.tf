output "state_machine_arn" {
  description = "ARN of the Step Functions state machine"
  value       = aws_sfn_state_machine.ticket_classifier.arn
}

output "tickets_bucket_name" {
  description = "Name of the S3 bucket for classified tickets"
  value       = aws_s3_bucket.tickets.bucket
}

output "validate_lambda_name" {
  description = "Name of the validate Lambda function"
  value       = module.validate_lambda.function_name
}

output "classify_lambda_name" {
  description = "Name of the classify Lambda function"
  value       = module.classify_lambda.function_name
}

output "route_lambda_name" {
  description = "Name of the route Lambda function"
  value       = module.route_lambda.function_name
}