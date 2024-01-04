aws ecr delete-repository --repository-name lambda_yahoo_download --region eu-central-1 --force

cd terraform/lambda_yahoo_download
../../terraform.exe destroy -auto-approve
cd ../../
