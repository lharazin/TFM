import pandas as pd
import numpy as np
from SqlAlquemySelectDataHandler import SqlAlquemySelectDataHandler
from sklearn.decomposition import PCA
from InvestingCalendarPreprocessor import InvestingCalendarPreprocessor


class DataProviderLite:
    """ Lite version of DataProvided used by Daily DNN Model. """

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

        self.key_indicators = [
            'GDP Annual Growth Rate',
            'GDP Growth Rate',
            'Unemployment Rate',
            'Inflation Rate',
            'Inflation Rate MoM',
            'Manufacturing PMI'
        ]

        self.corr_dict = {}

    def initialize_current_correlations(self, limit_date, read_date):
        sql_handler = SqlAlquemySelectDataHandler()
        etfs_in_usd = sql_handler.read_market_symbols('ETF in USD')
        df_etfs_recent = pd.DataFrame(
            index=pd.date_range(limit_date, read_date, freq='B'),
            columns=self.selected_countries)

        for country in self.selected_countries:
            symbol = etfs_in_usd.loc[country]['Code']
            df_etfs_recent.loc[:, country] = sql_handler.read_market_data(
                symbol, limit_date)

        df_etfs_recent = df_etfs_recent.dropna().astype(float)
        corr_recent = df_etfs_recent.corr()

        period = pd.period_range(limit_date, read_date, freq='M')
        period = period.to_timestamp()
        for date in period:
            month = f'{date:%Y-%m}'
            self.corr_dict[month] = corr_recent

    def fill_missing_values(self, df):
        df = df.ffill(limit=3).bfill(limit=3)
        countries_with_missing_data = df.columns[df.isna().sum() > 0]

        for country in countries_with_missing_data:
            missing_dates = df[df[country].isna()].index

            for date in missing_dates:
                month = f'{date:%Y-%m}'
                corr = self.corr_dict[month]

                most_corr_countries = corr[country].sort_values()[
                    ::-1][1:].index
                most_correlated_countries_with_data = most_corr_countries[
                    ~most_corr_countries.isin(
                        countries_with_missing_data)][:5]

                mean_values = df.loc[
                    date, most_correlated_countries_with_data].mean().round(2)

                df.loc[date, country] = mean_values

        return df

    def normilize_dataframe(self, df):
        df_mean = df.to_numpy().mean()
        df_std = df.to_numpy().std()
        df_normalized = (df - df_mean) / df_std
        return df_normalized

    def calculate_principal_component_from_calendar(
            self, read_date, no_months, limit_date=''):
        preprocessor = InvestingCalendarPreprocessor()
        indicators_norm = pd.DataFrame(
            data=np.zeros((no_months*len(self.selected_countries),
                           len(self.key_indicators))),
            columns=self.key_indicators)

        for indicator in self.key_indicators:
            df = preprocessor.read_key_indicator(indicator, limit_date)
            is_quarterly = (indicator == 'GDP Annual Growth Rate' or
                            indicator == 'GDP Growth Rate')
            df_recent = preprocessor.get_most_recent_values(
                df, read_date, no_months, is_quarterly)

            df_recent_filled = self.fill_missing_values(df_recent)
            df_normalized = self.normilize_dataframe(df_recent_filled)
            indicators_norm.loc[:, indicator] = (
                df_normalized.values.reshape(-1))

        pca = PCA(n_components=1)
        principal_component = pca.fit_transform(indicators_norm)

        principal_component_arr = principal_component.reshape(
            -1, len(self.selected_countries))
        principal_component_df = pd.DataFrame(
            principal_component_arr,
            index=range(no_months),
            columns=self.selected_countries)
        return principal_component_df
