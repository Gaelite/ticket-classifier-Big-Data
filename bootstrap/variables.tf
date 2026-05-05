variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Prefijo para los recursos del bootstrap."
  default     = "ticket-classifier-bigdata"
}

variable "main_project_name" {
  type        = string
  description = "Prefijo del proyecto principal."
  default     = "ticket-classifier-bigdata"
}

variable "github_repo" {
  type        = string
  description = "Repo de GitHub. Formato: 'owner/repo'."
  default     = "Gaelite/ticket-classifier-Big-Data"
}