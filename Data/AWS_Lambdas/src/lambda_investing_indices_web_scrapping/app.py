import pandas as pd
from datetime import date, timedelta
from SqlAlquemyInsertMarketDataHandler import SqlAlquemyInsertMarketDataHandler
from InvestingIndicesWebScrapper import InvestingIndicesWebScrapper


def handler(event, context):
    yesterday = date.today() - timedelta(days=1)
    sql_handler = SqlAlquemyInsertMarketDataHandler()
    web_scrapper = InvestingIndicesWebScrapper()
    indicators = sql_handler.read_max_dates_by_symbols(source='Investing')
    indicators_to_update = indicators[indicators.MaxDate != yesterday]

    investing_pages = {
        'OMXC20': 'omx-copenhagen-20-historical-data',
        'OBX': 'oslo-obx-historical-data',
        'JTOPI': 'ftse-jse-top-40-historical-data',
        'WIG20': 'wig-20-historical-data',
        'SPIPSA': 'ipsa-historical-data',
        'FTWIHUNL': 'ftse-hungary-historical-data',
        'PX': 'px-historical-data',
        'FTWICOLL': 'ftse-colombia-historical-data'
    }

    for i in range(indicators_to_update.shape[0]):
        symbol_code = indicators_to_update.iloc[i, 0]
        max_date = indicators_to_update.iloc[i, 1]

        start_date = max_date + timedelta(days=1)
        start_date = str(start_date)
        end_date = str(yesterday)
        path = investing_pages[symbol_code]

        print('Reading', symbol_code, 'from', start_date)
        prices = web_scrapper.retrieve_prices_from_investing(path, linux=True)
        if (len(prices) > 0):
            values_to_save = pd.Series(
                index=pd.date_range(start_date, end_date, freq='B'),
                data=prices.round(2), name=symbol_code)
            values_to_save = values_to_save.ffill()
            values_to_save = values_to_save.bfill()
            sql_handler.save_to_db(symbol_code, values_to_save)

    print('Done')
