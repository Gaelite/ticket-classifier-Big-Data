terraform {
  backend "s3" {
    bucket         = "ticket-classifier-bigdata-state-28d764d2"
    key            = "ticket-classifier/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "ticket-classifier-bigdata-locks"
  }
}