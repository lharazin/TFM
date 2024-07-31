#### Master of Science Thesis
# Optimizing Global Portfolio Weights using Artificial Intelligence and Macroeconomic Analysis
#### Master in Artificial Intelligence and Quantum Computing Applied to Financial Markets, 11th edition (mIA-X)
#### Lukasz Tadeusz Harazin

---

## Content of the directory

1. [Algorithm](Algorithm) - All code ralated with data preparation, model definition, training, validation and backtesting.<br>
1.1. [Algorithm/classical_models](Algorithm/classical_models) - Code for portfolio rebalancing and backtesting for traditional portfoio optimization methods.<br>
1.2. [Algorithm/cloud_deploy](Algorithm/cloud_deploy) - Code for AWS Lambda function to deploy Daily DNN model.<br>
1.2.1. [Algorithm/cloud_deploy/dockerfiles](Algorithm/cloud_deploy/dockerfiles) - Dockerfiles to build Lambda function with all required dependencies.<br>
1.2.2. [Algorithm/cloud_deploy/setup](Algorithm/cloud_deploy/setup) - Bash scripts to deploy and destroy Lambda function with Terraform.<br>
1.2.3. [Algorithm/cloud_deploy/src](Algorithm/cloud_deploy/src) - Source code for Lambda Daily DNN Model function.<br>
1.2.4. [Algorithm/cloud_deploy/terraform](Algorithm/cloud_deploy/terraform) - Terraform code to deploy automatically Lambda function with connected iam roles, cloudwatch events and permissions.<br>
1.3. [Algorithm/data](Algorithm/data) - Code for data retrieval and preprocessing.<br>
1.4. [Algorithm/models](Algorithm/models)- Various AI models explored in this Thesis.<br>
1.4.1. [Algorithm/models/base_models](Algorithm/models/base_models) - Base models backtested when researching various inputs, targets and architectures.<br>
1.4.2. [Algorithm/models/daily_models](Algorithm/models/daily_models) - Daily model based on indicators from Investing.com economic calendar.<br>
1.4.3. [Algorithm/models/tuning](Algorithm/models/tuning) - Hyperparameters tuning for the best performing models.<br>
2. [Data](Data) - All code for initial data exploration, collection and storage. Also contains datasets in CSV formats, used before they were saved to the database.<br>
2.1. [Data/AWS_Lambdas](Data/AWS_Lambdas) - Code for six AWS Lambdas functions to collect all indicators and market data.<br>
2.1.1. [Data/AWS_Lambdas/dockerfiles](Data/AWS_Lambdas/dockerfiles) - Dockerfiles to build functions with all required dependencies.<br>
2.1.2. [Data/AWS_Lambdas/setup](Data/AWS_Lambdas/setup) - Bash scripts to deploy and destroy Lambda functions with Terraform.<br>
2.1.3. [Data/AWS_Lambdas/sql](Data/AWS_Lambdas/sql) - All sql scripts required to create all database tables and insert all market symbols and indicators.<br>
2.1.4. [Data/AWS_Lambdas/src](Data/AWS_Lambdas/src) - Source code for AWS Lambdas functions.<br>
2.1.5. [Data/AWS_Lambdas/terraform](Data/AWS_Lambdas/terraform) - Terraform code to deploy automatically all Lambda functions with connected iam roles, cloudwatch events and permissions.<br>
2.2. [Data/BIS_CentralBankRates](Data/BIS_CentralBankRates) - Exploring central bank rates from Bank of International Settlement.<br>
2.3. [Data/IMF_Stats](Data/IMF_Stats) - Exploring indicators available on International Monetary Fund Stats page.<br>
2.4. [Data/Investing_EconomicCalendar](Data/Investing_EconomicCalendar) - Web Scrapping and pre-processing of economic calendar from Investing.com web site.<br>
2.5. [Data/Investing_PMI](Data/Investing_PMI) - Web Scrapping of Manufacturing PMI index from Investing.com web site<br>
2.6. [Data/MSCI](Data/MSCI) - Processing MSCI indexes and MSCI ACWI weights.<br>
2.7. [Data/OECD_Stats](Data/OECD_Stats) - Exploring multiple indicators available in OECD datasets and cataloged into different categories.<br>
2.8. [Data/WorldBankData_Stats](Data/WorldBankData_Stats) - Exploring yearly indicators available in World Bank Data datasets.<br>
2.9. [Data/YahooFinance](Data/YahooFinance) - Downloading and saving to database stock indices, currency rates and ETFs from YahooFinance API<br>