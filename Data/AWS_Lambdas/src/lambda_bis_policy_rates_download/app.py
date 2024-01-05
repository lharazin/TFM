from datetime import date
from BisApiHandler import BisApiHandler
from SqlAlquemyInsertMarketDataHandler import SqlAlquemyInsertMarketDataHandler


def handler(event, context):
    start_date = '2023-09-01'
    end_date = str(date.today())

    bis_api_handler = BisApiHandler()
    df = bis_api_handler.get_data(start_date, end_date)

    sql_handler = SqlAlquemyInsertMarketDataHandler()
    symbol_codes = sql_handler.get_symbol_codes(source='BIS')
    df_filtered = df[symbol_codes]

    save_start_date = '2023-10-01'
    df_rates_changes = df_filtered[df_filtered.diff() != 0]
    rates_to_save = df_rates_changes[save_start_date:]

    for symbol_code in rates_to_save:
        records_to_save = rates_to_save[symbol_code].dropna()
        if len(records_to_save) > 0:
            sql_handler.delete_all_records(symbol_code, save_start_date)
            sql_handler.insert_into_table(symbol_code, records_to_save)
            inserted_count = sql_handler.get_indicator_count(
                symbol_code, save_start_date)
            print(f'{symbol_code}: insterted {inserted_count} rates')
        else:
            print(f'{symbol_code}: no new rates since {save_start_date}')

    print('Done')
