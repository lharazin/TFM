aws configure

aws ecr get-login-password | docker login --username AWS --password-stdin \
    669885634214.dkr.ecr.eu-central-1.amazonaws.com

aws ecr create-repository --repository-name lambda_yahoo_download --region eu-central-1

docker build -t lambda_yahoo_download \
    -f ./dockerfiles/lambda_yahoo_download/Dockerfile .
    
docker tag lambda_yahoo_download \
    669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_yahoo_download

docker push 669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_yahoo_download


read -p "Enter db password: " db_password
read -p "Enter DB address URL: " db_server_address

cd terraform/lambda_yahoo_download
../../terraform.exe init
../../terraform.exe plan
../../terraform.exe apply -auto-approve -var="db_server_address=$db_server_address" -var="db_password=$db_password"
cd ../../