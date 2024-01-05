aws configure

aws ecr get-login-password | docker login --username AWS --password-stdin \
    669885634214.dkr.ecr.eu-central-1.amazonaws.com

aws ecr create-repository --repository-name lambda_investing_indices_web_scrapping --region eu-central-1

docker build -t lambda_investing_indices_web_scrapping \
    -f ./dockerfiles/lambda_investing_indices_web_scrapping/Dockerfile .
    
docker tag lambda_investing_indices_web_scrapping \
    669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_investing_indices_web_scrapping

docker push 669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_investing_indices_web_scrapping


read -p "Enter db password: " db_password
read -p "Enter DB address URL: " db_server_address

cd terraform/lambda_investing_indices_web_scrapping
../../terraform.exe init
../../terraform.exe plan
../../terraform.exe apply -auto-approve -var="db_server_address=$db_server_address" -var="db_password=$db_password"
cd ../../