import sqlalchemy as sal
import os
import pandas as pd


class SqlAlquemySelectHandler:

    def __init__(self):
        self.db_name = 'tfm-indicators'
        self.engine = self.__get_sql_alquemy_engine()

    def read_indicator(self, indicator, alt_indicator=''):
        records = []

        if alt_indicator != '':
            alt_indicator = f" OR [Indicator] LIKE '%{alt_indicator}%' "

        with self.engine.connect() as connection:
            result = connection.execute(sal.text(f"""
                SELECT [Id]
                    ,[ReportDateTime]
                    ,[Country]
                    ,[Currency]
                    ,[Indicator]
                    ,[Actual]
                    ,[Forecast]
                    ,[Previous]
                FROM [dbo].[InvestingEconomicCalendar]
                WHERE [Indicator] LIKE '%{indicator}%' {alt_indicator}
                ORDER BY [ReportDateTime]
            """))
            for row in result:
                records.append(row)

        df = pd.DataFrame(records)
        print(len(df), 'indicators read')
        return df

    def read_all_indicators(self, year):
        records = []

        with self.engine.connect() as connection:
            result = connection.execute(sal.text(f"""
                SELECT [Id]
                    ,[ReportDateTime]
                    ,[Country]
                    ,[Currency]
                    ,[Indicator]
                    ,[Actual]
                    ,[Forecast]
                    ,[Previous]
                FROM [dbo].[InvestingEconomicCalendar]
                WHERE [ReportDateTime] BETWEEN '{year}-01-01'
                    AND '{year}-12-31'
                ORDER BY [ReportDateTime]
            """))
            for row in result:
                records.append(row)

        df = pd.DataFrame(records)
        print(len(df), 'indicators read')
        return df

    def read_count_by_country(self):
        records = []

        with self.engine.connect() as connection:
            result = connection.execute(sal.text("""
                SELECT DATEADD(MONTH, DATEDIFF(MONTH, 0,
                        [ReportDateTime]), 0) AS [MonthStart]
                    ,[Country]
                    ,COUNT(*) AS Count
                FROM [dbo].[InvestingEconomicCalendar]
                WHERE [ReportDateTime] <= '2015-12-31'
                GROUP BY DATEADD(MONTH, DATEDIFF(MONTH, 0,
                    [ReportDateTime]), 0), [Country]
            """))
            for row in result:
                records.append(row)

            result2 = connection.execute(sal.text("""
                SELECT DATEADD(MONTH, DATEDIFF(MONTH, 0,
                        [ReportDateTime]), 0) AS [MonthStart]
                    ,[Country]
                    ,COUNT(*) AS Count
                FROM [dbo].[InvestingEconomicCalendar]
                WHERE [ReportDateTime] >= '2016-01-01'
                GROUP BY DATEADD(MONTH, DATEDIFF(MONTH, 0,
                    [ReportDateTime]), 0), [Country]
            """))
            for row in result2:
                records.append(row)

        df = pd.DataFrame(records)
        print(len(df), 'indicators read')
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
