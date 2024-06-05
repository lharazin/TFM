import sqlalchemy as sal
import os


class SqlAlquemyInsertMarketDataHandler:
    """ Data access class to save records to MarketData table. """

    def __init__(self):
        self.db_name = 'tfm-indicators'
        self.engine = self.__get_sql_alquemy_engine()

    def get_symbol_codes(self, source):
        symbol_codes = []
        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT Code FROM MarketSymbols "
                f"WHERE Source = '{source}'"))
            for row in result:
                symbol_codes.append(row[0])
        return symbol_codes

    def get_symbol_code(self, category, country):
        code = ''
        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT Code FROM MarketSymbols "
                f"WHERE Category = '{category}' AND Country = '{country}'"))
            for row in result:
                code = row[0]
        return code

    def insert_into_table(self, symbol_code, values):
        with self.engine.connect() as connection:
            sql = ("INSERT INTO MarketData(SymbolCode, Date, Value) VALUES ")
            for date, value in values.items():
                sql += (f"('{symbol_code}', '{date:%Y-%m-%d}', {value}),")

            sql = sql[:-1]  # Remove final coma
            connection.execute(sal.text(sql))
            connection.commit()

    def delete_all_records(self, symbol_code, date):
        with self.engine.connect() as connection:
            connection.execute(sal.text("DELETE FROM MarketData "
                                        f"WHERE SymbolCode = '{symbol_code}' "
                                        f"AND Date >= '{date}'"))
            connection.commit()

    def get_indicator_count(self, symbol_code, date):
        id = 0
        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT COUNT(*) FROM MarketData "
                f"WHERE SymbolCode = '{symbol_code}' "
                f"AND Date >= '{date}'"))
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
