<h2 align="center">Master of Science Thesis</h2>
<h1 align="center">Optimizing Global Portfolio Weights using Artificial Intelligence and Macroeconomic Analysis</h3>
<h4 align="center">Master in Artificial Intelligence and Quantum Computing Applied to Financial Markets, 11th edition (mIA-X), Instituto BME</h4>
<h3 align="center">Lukasz Harazin</h3>
<h4 align="center">2024</h4>

---

### Summary of the Thesis

The objective of this thesis was to implement an investment algorithm that would optimize global portfolio allocation using macroeconomic analysis. Processing multiple indicators, an artificial intelligence model would indicate in which countries it would be advantageous to allocate more capital based on promising trends in their economies. That could provide an alternative to passively managed funds tracking performances of broad global indexes like MSCI All Country World Index (ACWI).

In this thesis, extensive research has been performed to examine all available open data providers, identify relevant indicators, and establish data pipelines utilizing cloud services to collect data from a variety of sources. All indicators and market data have been stored in a database, and the data has undergone extensive pre-processing to fill in missing values and format the data into features suitable for model training. Furthermore, target values have been computed as optimal Max Sharpe portfolios using quadratic optimization. Cloud infrastructure diagram for data collection and data storage is presented below.

<p align="center"><img src="/Img/cloud_diagram.png" title="Data Architecture Diagram" /></p>

Subsequently, a variety of neural network architectures and machine learning models have been developed and validated. All models have also been backtested to eliminate the least performing models and select the most promising ones for further hyperparameters tuning. In the end, the top-performing model using Dense Neural Network has managed to achieve promising results, albeit without surpassing the benchmark.

<p align="center"><img src="/Img/returns_comparison.png" title="Returns Comparison" /></p>

Upon analysis of the results, it is observed that the final Dense Neural Network (DNN) Model tracks the Benchmark with relative closeness but yielding slightly lower returns. However, it does exceed the returns from the traditional portfolio optimization method using Risk Parity.

<p align="center"><img src="/Img/backtesting_metrics.png" title="Backtesting Metrics" /></p>

Comparing backtesting metrics, we can observe that the Final DNN Model yields an annual return of 6.21%, which is slightly lower than the Benchmark's annual return of 7.68%. The model also exhibits an annual volatility of 0.2015, marginally lower than the Benchmark's 0.2033. When considering risk-adjusted indicators such as Sharpe Ratio, Sortino Ratio, Max Drawdown, Max Time Under Water, Calmar Ratio, and Information Ratio, the Final DNN Model generally underperforms the Benchmark, indicating a lower risk-adjusted return. 

There are several potential explanations for the underperformance of the developed algorithm. One limitation of the model is the lag in the indicators. Although various indicators are released throughout the month, they are only incorporated during the rebalancing of the following month, well after the market has already included that information in the prices of the assets. Additionally, there isn't always a direct correlation between economic indicators and market performance. For example, a robust economy could potentially lead to higher interest rates, which could adversely affect markets. Lastly, while macroeconomic data offers a snapshot of the current state of the economy, its predictive power for future market movements is limited. Numerous other factors, such as investor sentiment, political events, and technological changes, also influence markets. 

Further development of the algorithm could incorporate more complete economic calendar from paid data providers. That could improve data quality and allow to produce more robust training data with constantly changing indicators. Furthermore, the algorithm could be redesigned to run on the daily basis, executing rebalancing when given turnover threshold is achieved rather than waiting for static monthly rebalancing at the beginning of each month.

In conclusion, although the proposed objectives were not fully realized, the research conducted in this thesis has yielded invaluable insights. It has demonstrated the comprehensive process of developing an investment algorithm, with meticulous attention to details such as an in-depth analysis of the benchmark to circumvent survivorship bias, and the inclusion of transaction fees to achieve the most realistic results. This has been a truly intriguing and thought-provoking endeavour.

---

### Content of the directory

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
