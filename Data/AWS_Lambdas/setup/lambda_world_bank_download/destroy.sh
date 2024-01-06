aws ecr delete-repository --repository-name lambda_world_bank_download --region eu-central-1 --force

cd terraform/lambda_world_bank_download
../../terraform.exe destroy -auto-approve
cd ../../
