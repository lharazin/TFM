import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from SqlAlquemyInsertMarketDataHandler import SqlAlquemyInsertMarketDataHandler


def handler(event, context):
    """ Yahoo Finance Lambda – reads ETFs prices, stock indices values
    and currency rates from API using yfinance library. Can be extended
    to new instruments by simply adding new symbols to the database table
    which will be included automatically in the next update. """

    yesterday = date.today() - timedelta(days=1)
    sql_handler = SqlAlquemyInsertMarketDataHandler()
    indicators = sql_handler.read_max_dates_by_symbols(source='Yahoo')
    indicators_to_update = indicators[indicators.MaxDate != yesterday]

    for i in range(indicators_to_update.shape[0]):
        symbol_code = indicators_to_update.iloc[i, 0]
        max_date = indicators_to_update.iloc[i, 1]

        start_date = max_date + timedelta(days=1)
        start_date = str(start_date)
        end_date = str(yesterday)

        print('Reading', symbol_code, 'from', start_date)
        index_data = yf.download(symbol_code, start=start_date, end=end_date)
        adj_close = index_data['Adj Close']

        if (len(adj_close) > 0):
            values_to_save = pd.Series(
                index=pd.date_range(start_date, end_date, freq='B'),
                data=adj_close.round(2), name=symbol_code)
            values_to_save = values_to_save.ffill()
            values_to_save = values_to_save.bfill()
            sql_handler.save_to_db(symbol_code, values_to_save)

    print('Done')
