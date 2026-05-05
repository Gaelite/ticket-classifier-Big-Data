# Support Ticket Classifier Pipeline

## Overview

This project implements an automated support ticket classification pipeline using AWS Step Functions, AWS Lambda, and Amazon S3, deployed entirely with OpenTofu (Infrastructure as Code). The pipeline simulates a real-world support triage system where incoming tickets are automatically validated, classified by severity, and routed to the appropriate S3 folder based on their urgency level.

The motivation behind this project is to eliminate manual ticket triage, which is slow and inconsistent. By automating the classification process, support teams can immediately focus on the most critical issues without spending time reading and sorting every incoming ticket.

## Architecture
Input JSON → Lambda Validate → Lambda Classify → Choice State → Lambda Route → S3
↓
ValidationFailed (Fail)

The pipeline consists of three Lambda functions orchestrated by an AWS Step Functions state machine:

- **Lambda 1 - Validate**: Checks that `priority_score` is a number between 0 and 100, that `description` is not empty, and that `customer` field is present. If any check fails, the execution goes to a `Fail` state.
- **Lambda 2 - Classify**: Determines the severity of the ticket (`urgent`, `normal`, or `low`) by combining the `priority_score` with keyword detection in the description. Keywords like "urgent", "down", "unresponsive", or "critical" raise the severity level.
- **Lambda 3 - Route**: Saves the enriched ticket JSON to the correct S3 folder (`urgent/`, `normal/`, or `low/`) based on the severity determined in the previous step.

## State Machine

The Step Function has exactly 6 states:
1. `Validate` - Task state
2. `Classify` - Task state
3. `ChooseBranch` - Choice state (3 branches: urgent, normal, default/low)
4. `Route` - Task state
5. `ValidationFailed` - Fail state
6. `Done` - Succeed state

## Input Format

```json
{
  "ticket_id": "tk-042",
  "customer": "student@uag.mx",
  "priority_score": 85,
  "description": "The system has been unresponsive for 2 hours, this is urgent"
}
```

## Prerequisites

- AWS CLI configured with valid credentials
- OpenTofu >= 1.8 installed
- A GitHub repository with OIDC configured (handled by bootstrap)

## Deployment

### First time setup

```bash
# 1. Configure the bootstrap
cd bootstrap
tofu init
tofu apply

# 2. Copy the outputs to backend.tf and .github/workflows/tofu.yml
# state_bucket → backend.tf bucket value
# gha_role_arn → workflow role-to-assume value

# 3. Deploy the main project
cd ..
tofu init
tofu apply
```

### CI/CD

Every push to `main` triggers `tofu plan` + `tofu apply` via GitHub Actions using OIDC (no AWS keys stored in GitHub).

Every Pull Request to `main` triggers only `tofu plan`.

## Testing

Run each test case from the CLI:

```bash
SFN_ARN=$(tofu output -raw state_machine_arn)

aws stepfunctions start-execution \
  --state-machine-arn $SFN_ARN \
  --region us-east-1 \
  --input file://tests/urgent.json

aws stepfunctions start-execution \
  --state-machine-arn $SFN_ARN \
  --region us-east-1 \
  --input file://tests/normal.json

aws stepfunctions start-execution \
  --state-machine-arn $SFN_ARN \
  --region us-east-1 \
  --input file://tests/low.json
```

Verify files landed in the correct S3 folders:

```bash
aws s3 ls --recursive s3://$(tofu output -raw tickets_bucket_name)/ --region us-east-1
```

## Cleanup

```bash
# Destroy main project
tofu destroy

# Destroy bootstrap
cd bootstrap
tofu destroy
```

## Project Structure
.
├── .github/workflows/
│   └── tofu.yml              # CI/CD pipeline
├── bootstrap/                # One-time setup: state bucket, OIDC, GHA role
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── modules/
│   └── lambda_function/      # Reusable Lambda module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── lambdas/
│   ├── validate/
│   │   └── lambda_function.py
│   ├── classify/
│   │   └── lambda_function.py
│   └── route/
│       └── lambda_function.py
├── tests/
│   ├── urgent.json
│   ├── normal.json
│   ├── low.json
│   └── invalid.json
├── backend.tf
├── main.tf
├── iam.tf
├── variables.tf
└── outputs.tf

## Notes

- No AWS access keys are stored in GitHub. Authentication uses OIDC.
- `tofu destroy` removes all resources including S3 bucket and its contents.
- The pipeline uses Python 3.12 for all Lambda functions.
- AI tools were used to assist with code generation and debugging. All code was reviewed and understood before submission.