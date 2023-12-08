FROM public.ecr.aws/lambda/python:3.11 as stage

# Hack to install chromium dependencies
RUN yum install -y -q sudo unzip
# Install Chromium
COPY setup/install-browser.sh /tmp/
RUN /usr/bin/bash /tmp/install-browser.sh

FROM public.ecr.aws/lambda/python:3.11 as base

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

COPY setup/chrome-deps.txt /tmp/
RUN yum install -y $(cat /tmp/chrome-deps.txt)
COPY --from=stage /opt/chrome /opt/chrome
COPY --from=stage /opt/chromedriver /opt/chromedriver

# Copy function code 
COPY ./src/ ${LAMBDA_TASK_ROOT} 

# Install the function's dependencies using file requirements.txt
RUN  pip3 install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target "${LAMBDA_TASK_ROOT}" 

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile) 
CMD [ "app.handler" ] 