import pandas as pd
from SqlAlquemySelectMarketDataHandler import SqlAlquemySelectMarketDataHandler


class DataProvider:

    def __init__(self):
        self.selected_countries = [
            'United States', 'Japan', 'United Kingdom',
            'Canada', 'France', 'Switzerland', 'Germany',
            'Australia', 'Netherlands', 'Sweden',
            'Hong Kong', 'Spain', 'Italy',
            'Singapore', 'Denmark', 'Finland',
            'Belgium', 'Norway', 'China', 'Taiwan',
            'India', 'Korea', 'Brazil', 'Russia',
            'South Africa', 'Mexico', 'Malaysia']
        self.benchmark = 'ACWI'

    def get_etf_data(self):
        sql_handler = SqlAlquemySelectMarketDataHandler()
        etfs_in_usd = sql_handler.read_market_symbols('ETF in USD')
        syn_etfs_in_usd = sql_handler.read_market_symbols(
            'Synthetic ETF in USD')

        countries_plus_benchmark = self.selected_countries + [self.benchmark]
        df_etfs = pd.DataFrame(
            index=pd.date_range('1999-01-04', '2023-12-29', freq='B'),
            columns=countries_plus_benchmark)

        for country in countries_plus_benchmark:
            symbol = etfs_in_usd.loc[country]['Code']
            df_etfs.loc[:, country] = sql_handler.read_market_data(symbol)

            first_valid = df_etfs[country].first_valid_index().strftime(
                '%Y-%m-%d')
            if first_valid != '1999-01-04':
                syn_symbol = syn_etfs_in_usd.loc[country]['Code']
                df_etfs.loc[:first_valid, country] = (
                    sql_handler.read_market_data(syn_symbol))

        df_etfs = df_etfs.dropna()
        df_etfs = df_etfs.astype(float)

        df_countries = df_etfs.drop(columns=['ACWI'])
        benchmark = df_etfs['ACWI']

        return df_countries, benchmark
