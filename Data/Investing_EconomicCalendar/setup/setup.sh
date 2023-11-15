# aws configure

# aws ecr get-login-password | docker login --username AWS --password-stdin \
#     669885634214.dkr.ecr.eu-central-1.amazonaws.com

aws ecr create-repository --repository-name lambda_economic_calendar --region eu-central-1

docker build -t lambda_economic_calendar \
    -f ./dockerfiles/Dockerfile .
    
docker tag lambda_economic_calendar \
    669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_economic_calendar

docker push 669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_economic_calendar


read -p "Enter db password: " db_password
read -p "Enter DB address URL: " db_server_address

cd terraform
../terraform.exe init
../terraform.exe plan
../terraform.exe apply -auto-approve -var="db_server_address=$db_server_address" -var="db_password=$db_password"
cd ../