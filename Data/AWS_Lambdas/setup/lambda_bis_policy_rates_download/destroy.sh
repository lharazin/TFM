aws ecr delete-repository --repository-name lambda_bis_policy_rates_download --region eu-central-1 --force

cd terraform/lambda_bis_policy_rates_download
../../terraform.exe destroy -auto-approve
cd ../../
