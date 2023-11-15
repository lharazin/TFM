from InvestingWebScrapper import InvestingWebScrapper
from SqlAlquemyInsertHandler import SqlAlquemyInsertHandler


def handler(event, context):
    print('Starting lambda')
    sql_handler = SqlAlquemyInsertHandler()
    web_scrapper = InvestingWebScrapper(linux=True)
    web_scrapper.open_economic_calendar()
    print('Opened browser')

    df = web_scrapper.read_all_indicators()
    web_scrapper.close_browser()
    print('Read', len(df), 'indicators from',
          df.iloc[0, 0], 'to', df.iloc[-1, 0])
    print(df)
    sql_handler.insert_into_table(df)

    return 'Success'
