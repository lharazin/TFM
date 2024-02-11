import sqlalchemy as sal
import os
import pandas as pd


class SqlAlquemySelectMarketDataHandler:

    def __init__(self):
        self.db_name = 'tfm-indicators'
        self.engine = self.__get_sql_alquemy_engine()

    def read_market_symbols(self, category):
        records = []

        with self.engine.connect() as connection:
            result = connection.execute(sal.text(f"""
                SELECT [Code]
                    ,[Description]
                    ,[Country]
                FROM [dbo].[MarketSymbols]
                WHERE Category = '{category}'
            """))
            for row in result:
                records.append(row)

        df = pd.DataFrame(records)
        print(len(df), 'market symbols read')
        return df

    def read_market_data(self, symbol):
        records = []

        with self.engine.connect() as connection:
            result = connection.execute(sal.text(f"""
                SELECT [Date], [Value]
                FROM [dbo].[MarketData]
                WHERE SymbolCode = '{symbol}'
                ORDER BY [Date]
            """))
            for row in result:
                records.append(row)

        df = pd.DataFrame(records)
        df.index = pd.to_datetime(df['Date'])
        print(len(df), 'market data read')
        return df

    def __get_sql_alquemy_engine(self):
        db_server_address = os.environ.get("AWS_DB_SERVER_ADDRESS")
        db_server_port = 1433
        username = os.environ.get("AWS_DB_USERNAME")
        password = os.environ.get("AWS_DB_PASSWORD")

        engine = sal.create_engine(
            (f"mssql+pyodbc://{username}:{password}@"
             f"{db_server_address},{db_server_port}/{self.db_name}"
             "?driver=ODBC+Driver+17+for+SQL+Server"),
            fast_executemany=True)
        return engine
