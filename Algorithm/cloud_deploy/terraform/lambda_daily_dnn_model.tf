variable "db_server_address" {
  description = "DB server address"
  type        = string
  default     = "default_db_address"
}

variable "db_password" {
  description = "DB password"
  type        = string
  default     = "pass"
}

resource "aws_iam_role" "lambda_execution_role_model" {
  name = "lambda_execution_role_model"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_rds_policy" {
  role       = aws_iam_role.lambda_execution_role_model.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSDataFullAccess"
}

resource "aws_iam_policy" "lambda_execution_policy_model" {
  name        = "LambdaExecutionPolicyModelPolicyRates"
  description = "Policy for Lambda execution role"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "logs:CreateLogGroup",
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = "logs:CreateLogStream",
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = "logs:PutLogEvents",
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_execution_role_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_execution_policy_model.arn
  role       = aws_iam_role.lambda_execution_role_model.name
}

resource "aws_lambda_function" "executable" {
  function_name = "lambda_daily_dnn_model"
  image_uri     = "669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_daily_dnn_model:latest"
  package_type  = "Image"
  role          = aws_iam_role.lambda_execution_role_model.arn
  memory_size   = 1024
  timeout       = 300
  environment {
    variables = {
      AWS_DB_SERVER_ADDRESS = var.db_server_address
      AWS_DB_USERNAME       = "admin"
      AWS_DB_PASSWORD       = var.db_password
    }
  }
}

resource "aws_cloudwatch_event_rule" "schedule" {
    name = "triger_model_policy_rates"
    description = "Schedule for Monday at 8"
    schedule_expression = "cron(0 8 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "schedule_lambda" {
    rule = aws_cloudwatch_event_rule.schedule.name
    arn = aws_lambda_function.executable.arn
}

resource "aws_lambda_permission" "allow_events_bridge_to_run_lambda" {
    function_name = aws_lambda_function.executable.function_name
    
    statement_id = "CloudWatchInvoke"
    action = "lambda:InvokeFunction"

    source_arn = aws_cloudwatch_event_rule.schedule.arn

    principal = "events.amazonaws.com"
}
