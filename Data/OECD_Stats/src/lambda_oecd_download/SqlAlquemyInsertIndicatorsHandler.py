import sqlalchemy as sal
import os


class SqlAlquemyInsertIndicatorsHandler:

    def __init__(self):
        self.db_name = 'tfm-indicators'
        self.engine = self.__get_sql_alquemy_engine()

    def get_indicator_id(self, name, source):
        id = 0
        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT IndicatorId FROM EconomicIndicators "
                f"WHERE Indicator = '{name}' AND Source = '{source}'"))
            for row in result:
                id = row[0]
        return id

    def insert_into_table(self, indicator_id, country, values):
        with self.engine.connect() as connection:
            sql = ("INSERT INTO IndicatorsValues "
                   "(IndicatorId, Period, Country, Value) "
                   "VALUES ")
            for period, value in values.items():
                sql += (f"({indicator_id}, '{period:%Y-%m-%d}', "
                        f"'{country}', {value}),")

            sql = sql[:-1]  # Remove final coma
            connection.execute(sal.text(sql))
            connection.commit()

    def delete_all_records(self, indicator_id, year=1999):
        with self.engine.connect() as connection:
            connection.execute(sal.text("DELETE FROM IndicatorsValues "
                                        f"WHERE IndicatorId = {indicator_id} "
                                        f"AND Period >= '{year}-01-01'"))
            connection.commit()

    def get_indicator_count(self, indicator_id, year=1999):
        id = 0
        with self.engine.connect() as connection:
            result = connection.execute(sal.text(
                "SELECT COUNT(*) FROM IndicatorsValues "
                f"WHERE IndicatorId = {indicator_id} "
                f"AND Period >= '{year}-01-01'"))
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
