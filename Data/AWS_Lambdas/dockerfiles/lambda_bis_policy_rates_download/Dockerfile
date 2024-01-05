FROM public.ecr.aws/lambda/python:3.11

# Install ODBC Driver to access SQL database
RUN yum update -y \
    && curl https://packages.microsoft.com/config/rhel/8/prod.repo > /etc/yum.repos.d/mssql-release.repo \
    && yum remove unixODBC-utf16 unixODBC-utf16-devel \
    && ACCEPT_EULA=Y yum install -y msodbcsql17  \
    && ACCEPT_EULA=Y yum install -y mssql-tools \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
    && source ~/.bashrc \
    && yum install -y unixODBC-devel \
    && yum install -y gcc-c++ \
    && yum clean all

# Copy function code 
COPY ./src/lambda_bis_policy_rates_download/ ${LAMBDA_TASK_ROOT} 

# Install the function's dependencies using file requirements.txt
RUN  pip3 install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}" 

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile) 
CMD [ "app.handler" ] 