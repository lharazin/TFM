import sqlalchemy as sal
import os
import pandas as pd


class SqlAlquemyInsertMarketDataHandler:
    """ Data access class to save records to MarketData table. """

    def __init__(self):
        self.db_name = 'tfm-indicators'
        self.engine = self.__get_sql_alquemy_engine()

    def get_symbol_code(self, category, country):
        code = ''
        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT Code FROM MarketSymbols "
                f"WHERE Category = '{category}' AND Country = '{country}'"))
            for row in result:
                code = row[0]
        return code

    def read_max_dates_by_symbols(self, source):
        records = []

        with self.engine.connect() as connection:
            result = connection.execute(sal.text(f"""
                SELECT [SymbolCode], MAX([Date]) AS MaxDate
                FROM [dbo].[MarketData] AS D
                    INNER JOIN [dbo].[MarketSymbols] AS S
                        ON D.[SymbolCode] = S.[Code]
                WHERE S.[Source] = '{source}'
                GROUP BY [SymbolCode]
            """))
            for row in result:
                records.append(row)

        df = pd.DataFrame(records)
        print(len(df), 'indicators read')
        return df

    def save_to_db(self, symbol_code, values):
        initial_count = self.get_indicator_count(symbol_code)
        chunks = self.split_into_chunks(values)
        for chunk in chunks:
            self.insert_into_table(symbol_code, chunk)

        final_count = self.get_indicator_count(symbol_code)
        print('Inserted', (final_count - initial_count), 'records for',
              symbol_code)

    def split_into_chunks(self, df, chunk_size=200):
        chunks = list()
        num_chunks = len(df)//chunk_size + 1
        for i in range(num_chunks):
            chunks.append(df[i*chunk_size:(i+1)*chunk_size])
        return chunks

    def insert_into_table(self, symbol_code, values):
        if len(values) == 0:
            return

        with self.engine.connect() as connection:
            sql = ("INSERT INTO MarketData(SymbolCode, Date, Value) VALUES ")
            for date, value in values.items():
                sql += (f"('{symbol_code}', '{date:%Y-%m-%d}', {value}),")

            sql = sql[:-1]  # Remove final coma
            connection.execute(sal.text(sql))
            connection.commit()
            print('.', end='')

    def delete_all_records(self, symbol_code, year=1999):
        with self.engine.connect() as connection:
            connection.execute(sal.text("DELETE FROM MarketData "
                                        f"WHERE SymbolCode = '{symbol_code}' "
                                        f"AND Date >= '{year}-01-01'"))
            connection.commit()

    def get_indicator_count(self, symbol_code, year=1999):
        id = 0
        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT COUNT(*) FROM MarketData "
                f"WHERE SymbolCode = '{symbol_code}' "
                f"AND Date >= '{year}-01-01'"))
            for row in result:
                id = row[0]
        return id

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
