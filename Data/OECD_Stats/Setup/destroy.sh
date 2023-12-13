aws ecr delete-repository --repository-name lambda_oecd_download --region eu-central-1 --force

cd terraform/lambda_oecd_download
../../terraform.exe destroy -auto-approve
cd ../../
