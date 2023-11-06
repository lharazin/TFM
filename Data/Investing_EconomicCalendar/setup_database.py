import sqlalchemy as sal
from sqlalchemy_utils import create_database
import os
from dotenv import load_dotenv
load_dotenv()


db_server_address = os.environ.get("AWS_DB_SERVER_ADDRESS")
db_server_port = 1433
db_name = 'tfm-indicators'
username = os.environ.get("AWS_DB_USERNAME")
password = os.environ.get("AWS_DB_PASSWORD")

engine_url = (f"mssql+pyodbc://{username}:{password}@"
              f"{db_server_address},{db_server_port}/{db_name}"
              "?driver=ODBC+Driver+17+for+SQL+Server")

create_database(engine_url)
print('Created database')

with sal.create_engine(engine_url).connect() as connection:
    connection.execute(sal.text("""
        CREATE TABLE [InvestingEconomicCalendar] (
            [Id] INT IDENTITY(1,1) PRIMARY KEY,
            [ReportDateTime] DATETIME NOT NULL,
            [Country] VARCHAR(50) NOT NULL,
            [Currency] VARCHAR(3) NOT NULL,
            [Indicator] VARCHAR(255) NOT NULL,
            [Actual] VARCHAR(50) NOT NULL,
            [Forecast] VARCHAR(50) NULL,
            [Previous] VARCHAR(50) NULL
        )
    """))
    connection.commit()
    print('Created table InvestingEconomicCalendar')

print('Database setup complete')
