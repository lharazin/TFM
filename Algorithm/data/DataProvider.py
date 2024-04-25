import pandas as pd
import numpy as np
import os
from SqlAlquemySelectDataHandler import SqlAlquemySelectDataHandler
from sklearn.decomposition import PCA


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
            'Manufacturing PMI'
        ]

        self.corr_dict = {}

    def get_etf_data(self):
        countries_file_path = 'cache/df_countries.csv'
        benchmark_file_path = 'cache/benchmark.csv'

        if (os.path.isfile(countries_file_path) and
                os.path.isfile(benchmark_file_path)):
            df_countries = pd.read_csv(
                countries_file_path, index_col=0, parse_dates=True)
            df_benchmark = pd.read_csv(
                benchmark_file_path, index_col=0, parse_dates=True)
            benchmark = df_benchmark.iloc[:, 0]
            return df_countries, benchmark

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

        df_countries.to_csv(countries_file_path)
        benchmark.to_csv(benchmark_file_path)

        return df_countries, benchmark

    def get_acwi_weights(self):
        acwi_weights_file_path = 'cache/acwi_weights.csv'
        if os.path.isfile(acwi_weights_file_path):
            df_weights = pd.read_csv(acwi_weights_file_path,
                                     index_col=0, parse_dates=True)
            return df_weights

        df_weights = self.get_indicator_values(
            'MSCI ACWI Weights', 'MSCI', 'YS')
        df_weights.dropna(inplace=True)
        df_weights.to_csv(acwi_weights_file_path)
        return df_weights

    def get_indicator_values(self, indicator, source, freq):
        sql_handler = SqlAlquemySelectDataHandler()
        indicator_id = sql_handler.get_indicator_id(indicator, source)

        indicator_values = sql_handler.get_indicator_count(indicator_id)
        indicator_values.index = indicator_values['Period']

        df_indicator = pd.DataFrame(
            columns=self.selected_countries,
            index=pd.date_range('1999-01-01', '2023-12-31', freq='MS'))

        for country in df_indicator.columns:
            df_indicator.loc[:, country] = indicator_values[
                indicator_values['Country'] == country]['Value']

        df_indicator = df_indicator.astype(float).round(2)

        # Convert quarterly data to monthly one
        if freq == 'QS':
            df_indicator = df_indicator.ffill(limit=2)

        return df_indicator

    def get_key_indicator_values(self, indicator):
        file_name = indicator.lower().replace(' ', '_')
        file_path = f'cache/{file_name}.csv'
        if os.path.isfile(file_path):
            df_cache = pd.read_csv(file_path, index_col=0, parse_dates=True)
            return df_cache

        if (indicator == 'GDP Annual Growth Rate' or
                indicator == 'GDP Growth Rate'):
            df_investing_indicator = self.get_indicator_values(
                indicator, 'Investing', 'QS')
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'QS')
            df_combined = df_investing_indicator.combine_first(
                df_oecd_indicator)
            df_combined = self.fill_missing_values(df_combined)

            df_combined.to_csv(file_path)
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
            df_combined = self.fill_missing_values(df_combined)

            df_combined.to_csv(file_path)
            return df_combined

        if (indicator == 'Manufacturing PMI'):
            df_investing_indicator = self.get_indicator_values(
                indicator, 'Investing', 'MS')

            df_investing_indicator = self.fill_manufacturing_pmi(
                df_investing_indicator)
            df_investing_indicator = self.fill_missing_values(
                df_investing_indicator)
            df_investing_indicator.to_csv(file_path)
            return df_investing_indicator

        if (indicator == 'OECD Bussiness Confidence Indicator'):
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'MS')

            df_oecd_indicator.to_csv(file_path)
            return df_oecd_indicator

    def calculate_correlations_for_returns(self, month):
        if month.startswith('1999'):
            month = '1999-12'  # take minimum 1 year of data

        df_countries, _ = self.get_etf_data()
        bdays_in_year = 252
        df_prices_last_12_months = df_countries[:month].iloc[-bdays_in_year:]
        df_returns = np.log(df_prices_last_12_months).diff().dropna()
        corr = df_returns.corr()
        return corr

    def fill_missing_values(self, df):
        # Cache corr matrix to avoid recalculating multiple times
        if len(self.corr_dict) == 0:
            for date in df.index:
                month = f'{date:%Y-%m}'
                corr = self.calculate_correlations_for_returns(month)
                self.corr_dict[month] = corr

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

    def fill_manufacturing_pmi(self, df_manufacturing_pmi):
        df_bussiness_confidence = self.get_key_indicator_values(
            'OECD Bussiness Confidence Indicator')

        countries_with_missing_data = df_manufacturing_pmi.columns[
            df_manufacturing_pmi.isna().sum() > 0]

        for country in countries_with_missing_data:
            missing_dates = df_manufacturing_pmi[df_manufacturing_pmi[
                country].isna()].index

            values_from_bussines_confidence = df_bussiness_confidence.loc[
                missing_dates, country] - 50

            df_manufacturing_pmi.loc[
                missing_dates, country] = values_from_bussines_confidence

        df_manufacturing_pmi = df_manufacturing_pmi.round(2)
        return df_manufacturing_pmi

    def normilize_dataframe(self, df):
        df_mean = df.to_numpy().mean()
        df_std = df.to_numpy().std()
        df_normalized = (df - df_mean) / df_std
        return df_normalized

    def get_latest_data(self, indicator, df, date, periods):
        if (indicator == 'GDP Annual Growth Rate' or
                indicator == 'GDP Growth Rate'):
            date_minus_2_quarters = date - pd.DateOffset(months=6)
            latest_known_period = pd.to_datetime(
                (f'{date_minus_2_quarters.year}-'
                 f'Q{date_minus_2_quarters.quarter}')) + pd.DateOffset(
                     months=2)
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

    def calculate_simple_composite_indicator(self, date, periods):
        df_composite = pd.DataFrame(
            data=np.zeros((periods, len(self.selected_countries))),
            columns=self.selected_countries)

        for indicator in self.key_indicators:
            df = self.get_key_indicator_values(indicator)
            df_normalized = self.normilize_dataframe(df)
            df_last_values = self.get_latest_data(indicator, df_normalized,
                                                  date, periods)

            # Standarize indexes as indicators release values differently
            df_last_values.index = range(periods)

            # Give more weight to Manufacturing PMI being the most
            # recent value and the most relevant to predict economic cycle
            weight = 0.5 if indicator == 'Manufacturing PMI' else 0.1
            df_composite += df_last_values*weight

        return df_composite

    def calculate_principal_component_from_indicators(self, date, periods):
        indicators_norm = pd.DataFrame(
            data=np.zeros((periods*len(self.selected_countries),
                           len(self.key_indicators))),
            columns=self.key_indicators)

        for indicator in self.key_indicators:
            df = self.get_key_indicator_values(indicator)
            df_normalized = self.normilize_dataframe(df)
            df_last_values = self.get_latest_data(indicator, df_normalized,
                                                  date, periods=periods)

            indicators_norm.loc[:, indicator] = (
                df_last_values.values.reshape(-1))

        pca = PCA(n_components=1)
        principal_component = pca.fit_transform(indicators_norm)

        principal_component_arr = principal_component.reshape(
            -1, len(self.selected_countries))
        principal_component_df = pd.DataFrame(principal_component_arr,
                                              index=range(periods),
                                              columns=self.selected_countries)
        return principal_component_df

    def get_days_to_recalculate(self):
        file_path = 'cache/days_to_rebalance.csv'
        if os.path.isfile(file_path):
            df_cache = pd.read_csv(file_path, index_col=0)
            return df_cache['Days to rebalance']

        df_countries, _ = self.get_etf_data()

        sql_handler = SqlAlquemySelectDataHandler()
        max_report_date = sql_handler.get_max_pmi_report_day()

        # Add extra 2 days for years 1999 to 2012 where PMI are mainly
        # extrapolated from Bussiness Confidence Indicators
        max_report_date[max_report_date.dt.day == 1] += pd.DateOffset(days=2)

        # Get next trading day after last PMI index is published
        days_to_rebalance = []
        for month_start in max_report_date.values:
            from_date = month_start.astype(str)[:10]

            days_to_rebalance.append(df_countries[
                from_date:].index.values[1].astype(str)[:10])

        days_to_rebalance_series = pd.Series(days_to_rebalance,
                                             name='Days to rebalance')
        days_to_rebalance_series.to_csv(file_path)
        return days_to_rebalance_series
