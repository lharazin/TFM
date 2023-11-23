import sqlalchemy as sal
import os
import pandas as pd


class SqlAlquemyInsertHandler:

    def __init__(self):
        self.db_name = 'tfm-indicators'
        self.engine = self.__get_sql_alquemy_engine()

    def get_records_count(self):
        count = 0

        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT COUNT(*) FROM [InvestingEconomicCalendar]"))
            for row in result:
                count = row[0]

        return count

    def insert_into_table(self, df):
        chunks = self.split_dataframe(df=df, chunk_size=200)
        for chunk in chunks:
            self.insert_chunk(chunk)

    def split_dataframe(self, df, chunk_size):
        chunks = list()
        num_chunks = len(df)//chunk_size + 1
        for i in range(num_chunks):
            chunks.append(df[i*chunk_size:(i+1)*chunk_size])
        return chunks

    def insert_chunk(self, df):
        with self.engine.connect() as connection:
            sql = ("INSERT INTO [InvestingEconomicCalendar] (ReportDateTime, "
                   "Country, Currency, Indicator, Actual, Forecast, Previous) "
                   "VALUES ")
            for ind, row in df.iterrows():
                indicator = row['Event'].replace("'", "")
                sql += (f"('{row['DateTime']}','{row['Country']}',"
                        f"'{row['Currency']}','{indicator}','{row['Actual']}',"
                        f"'{row['Forecast']}','{row['Previous']}'),")

            sql = sql[:-1]  # Remove final coma

            initial_count = self.get_records_count()
            print('Executing insert sql...')
            connection.execute(sal.text(sql))
            connection.commit()

            final_count = self.get_records_count()
            print(f'Inserted {(final_count - initial_count)} records')

    def delete_all_records(self):
        with self.engine.connect() as connection:
            connection.execute(sal.text(
                "DELETE FROM [InvestingEconomicCalendar]"))
            connection.commit()

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
