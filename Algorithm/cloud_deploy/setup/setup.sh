aws configure

aws ecr get-login-password | docker login --username AWS --password-stdin \
    669885634214.dkr.ecr.eu-central-1.amazonaws.com

aws ecr create-repository --repository-name lambda_daily_dnn_model --region eu-central-1

docker build -t lambda_daily_dnn_model -f ./dockerfiles/Dockerfile .
    
docker tag lambda_daily_dnn_model \
    669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_daily_dnn_model

docker push 669885634214.dkr.ecr.eu-central-1.amazonaws.com/lambda_daily_dnn_model


read -p "Enter db password: " db_password
read -p "Enter DB address URL: " db_server_address

cd terraform
../terraform.exe init
../terraform.exe plan
../terraform.exe apply -auto-approve -var="db_server_address=$db_server_address" -var="db_password=$db_password"
cd ../