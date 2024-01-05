aws ecr delete-repository --repository-name lambda_economic_calendar --region eu-central-1 --force

cd terraform/lambda_economic_calendar
../../terraform.exe destroy -auto-approve
cd ../../
