import pandas as pd
from SqlAlquemySelectDataHandler import SqlAlquemySelectDataHandler


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

        self.key_indicators = [
            'GDP Annual Growth Rate',
            'GDP Growth Rate',
            'Unemployment Rate',
            'Inflation Rate',
            'Inflation Rate MoM',
            'Manufacturing PMI',
            'Services PMI',
            'OECD Bussiness Confidence Indicator'
        ]

    def get_etf_data(self):
        sql_handler = SqlAlquemySelectDataHandler()
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

    def get_acwi_weights(self):
        df_weights = self.get_indicator_values(
            'MSCI ACWI Weights', 'MSCI', 'YS')
        return df_weights

    def get_indicator_values(self, indicator, source, freq):
        sql_handler = SqlAlquemySelectDataHandler()
        indicator_id = sql_handler.get_indicator_id(indicator, source)

        indicator_values = sql_handler.get_indicator_count(indicator_id)
        indicator_values.index = indicator_values['Period']

        df_countries = pd.DataFrame(
            columns=self.selected_countries,
            index=pd.date_range('1999', '2023-12-31', freq=freq))

        for country in df_countries.columns:
            df_countries.loc[:, country] = indicator_values[
                indicator_values['Country'] == country]['Value']

        df_countries = df_countries.astype(float).round(2)
        return df_countries

    def get_key_indicator_values(self, indicator):
        if (indicator == 'GDP Annual Growth Rate' or
                indicator == 'GDP Growth Rate'):
            df_investing_indicator = self.get_indicator_values(
                indicator, 'Investing', 'QS')
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'QS')
            df_combined = df_investing_indicator.combine_first(
                df_oecd_indicator)
            return df_combined

        if (indicator == 'Unemployment Rate' or
                indicator == 'Inflation Rate' or
                indicator == 'Inflation Rate MoM'):
            df_investing_indicator = self.get_indicator_values(
                indicator, 'Investing', 'MS')
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'MS')
            df_combined = df_investing_indicator.combine_first(
                df_oecd_indicator)
            return df_combined

        if (indicator == 'Manufacturing PMI' or indicator == 'Services PMI'):
            df_investing_indicator = self.get_indicator_values(
                indicator, 'Investing', 'MS')
            return df_investing_indicator

        if (indicator == 'OECD Bussiness Confidence Indicator'):
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'MS')
            return df_oecd_indicator

    def get_latest_data(self, indicator, df, date, periods):
        if (indicator == 'GDP Annual Growth Rate' or
                indicator == 'GDP Growth Rate'):
            date_minus_2_quarters = date - pd.DateOffset(months=6)
            latest_known_period = pd.to_datetime(
                (f'{date_minus_2_quarters.year}-'
                 f'Q{date_minus_2_quarters.quarter}'))
            return df[:latest_known_period].iloc[-periods:]

        if (indicator == 'Unemployment Rate' or
                indicator == 'Inflation Rate' or
                indicator == 'Inflation Rate MoM' or
                indicator == 'OECD Bussiness Confidence Indicator'):
            date_minus_2_months = date - pd.DateOffset(months=2)
            latest_known_period = pd.to_datetime(
                f'{date_minus_2_months.year}-{date_minus_2_months.month}-1')
            return df[:latest_known_period].iloc[-periods:]

        if (indicator == 'Manufacturing PMI' or indicator == 'Services PMI'):
            months = 1 if date.day >= 6 else 2
            date_minus_1_or_2_month = date - pd.DateOffset(months=months)
            latest_known_period = pd.to_datetime(
                (f'{date_minus_1_or_2_month.year}-'
                 f'{date_minus_1_or_2_month.month}-1'))
            return df[:latest_known_period].iloc[-periods:]
