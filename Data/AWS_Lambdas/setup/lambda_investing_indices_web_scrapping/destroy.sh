aws ecr delete-repository --repository-name lambda_investing_indices_web_scrapping --region eu-central-1 --force

cd terraform/lambda_investing_indices_web_scrapping
../../terraform.exe destroy -auto-approve
cd ../../
