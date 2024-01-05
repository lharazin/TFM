aws ecr delete-repository --repository-name lambda_economic_calendar --region eu-central-1 --force

cd terraform
../terraform.exe destroy -auto-approve
cd ../
