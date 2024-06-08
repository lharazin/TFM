aws ecr delete-repository --repository-name lambda_daily_dnn_model --region eu-central-1 --force

cd terraform
../terraform.exe destroy -auto-approve
cd ../
