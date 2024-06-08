import pandas as pd
import numpy as np
import os
from cvxpy.error import SolverError
from SqlAlquemySelectDataHandler import SqlAlquemySelectDataHandler
from sklearn.decomposition import PCA
from PortfolioOptimizer import PortfolioOptimizer
from InvestingCalendarPreprocessor import InvestingCalendarPreprocessor
import warnings
warnings.filterwarnings('ignore')


class DataProvider:
    """Comprehensive helper class used in all models. It encapsulates logic
    for reading data from the database, filling missing data, preprocessing,
    formatting and caching. Basically serves as a Data Access Layer.
    """

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

        self.additional_indicators = [
            'Producer Price Index',
            'Central Bank Rate',
            'Short Term Interest Rate',
            'Long Term Interest Rate',
            'Current Account to GDP',
            'Total Manufacturing',
            'Industrial Production',
            'OECD Consumer Confidence Indicator',
            'Retail Sales'
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

    def read_central_bank_rates(self):
        sql_handler = SqlAlquemySelectDataHandler()
        interest_rates = sql_handler.read_market_symbols('Central Bank Rate')

        df_rates = pd.DataFrame(
            index=pd.date_range('1999-01-01', '2023-12-29', freq='D'),
            columns=self.selected_countries)

        for country in df_rates.columns:
            if country in interest_rates.index:
                symbol = interest_rates.loc[country]['Code']
                df_rates.loc[:, country] = sql_handler.read_market_data(symbol)

        df_rates_filled = df_rates.ffill().bfill()
        df_rates_filled = df_rates_filled.asfreq('MS')
        return df_rates_filled

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
                indicator == 'Inflation Rate MoM' or
                indicator == 'Industrial Production'):
            df_investing_indicator = self.get_indicator_values(
                indicator, 'Investing', 'MS')
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'MS')
            df_combined = df_investing_indicator.combine_first(
                df_oecd_indicator)
            df_combined = self.fill_missing_values(df_combined)

            df_combined.to_csv(file_path)
            return df_combined

        if indicator == 'Central Bank Rate':
            df_interest_rate = self.read_central_bank_rates()
            df_interest_rate = self.fill_missing_values(df_interest_rate)

            df_interest_rate.to_csv(file_path)
            return df_interest_rate

        if (indicator == 'Manufacturing PMI' or
                indicator == 'Producer Price Index' or
                indicator == 'Retail Sales'):
            df_investing_indicator = self.get_indicator_values(
                indicator, 'Investing', 'MS')

            if (indicator == 'Manufacturing PMI'):
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

        if (indicator == 'Short Term Interest Rate' or
                indicator == 'Long Term Interest Rate' or
                indicator == 'Total Manufacturing' or
                indicator == 'OECD Consumer Confidence Indicator'):
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'MS')
            df_oecd_indicator = self.fill_missing_values(df_oecd_indicator)

            df_oecd_indicator.to_csv(file_path)
            return df_oecd_indicator

        if (indicator == 'Current Account to GDP'):
            df_oecd_indicator = self.get_indicator_values(
                indicator, 'OECD', 'QS')
            df_oecd_indicator = self.fill_missing_values(df_oecd_indicator)

            df_oecd_indicator.to_csv(file_path)
            return df_oecd_indicator

        if (indicator == 'Monthly Returns'):
            df_countries, _ = self.get_etf_data()
            days_to_recalculate = self.get_days_to_recalculate(
                months_to_skip=0)
            df_returns = np.log(df_countries.loc[
                days_to_recalculate]).diff().dropna()

            df_returns.to_csv(file_path)
            return df_returns

        if (indicator == 'Economic Cycle X'):
            pmi_indicator = 'Manufacturing PMI'
            df_pmi_indicator = self.get_key_indicator_values(pmi_indicator)
            index_moving_avg = df_pmi_indicator.ewm(com=1.5).mean().dropna()

            economic_cycle_x = (index_moving_avg - 50)[1:]
            economic_cycle_x.to_csv(file_path)
            return economic_cycle_x

        if (indicator == 'Economic Cycle Y'):
            pmi_indicator = 'Manufacturing PMI'
            df_pmi_indicator = self.get_key_indicator_values(pmi_indicator)
            index_moving_avg = df_pmi_indicator.ewm(com=1.5).mean().dropna()

            economic_cycle_y = index_moving_avg.diff().dropna()
            economic_cycle_y.to_csv(file_path)
            return economic_cycle_y

    def calculate_correlations_for_returns(self, month):
        if month.startswith('1999'):
            month = '1999-12'  # take minimum 1 year of data

        df_countries, _ = self.get_etf_data()
        bdays_in_year = 252
        df_prices_last_12_months = df_countries[:month].iloc[-bdays_in_year:]
        df_returns = np.log(df_prices_last_12_months).diff().dropna()
        corr = df_returns.corr()
        return corr

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

                if month in self.corr_dict.keys():
                    corr = self.corr_dict[month]
                else:
                    corr = self.calculate_correlations_for_returns(month)
                    self.corr_dict[month] = corr

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
                indicator == 'GDP Growth Rate' or
                indicator == 'Current Account to GDP'):
            date_minus_2_quarters = date - pd.DateOffset(months=6)
            latest_known_period = pd.to_datetime(
                (f'{date_minus_2_quarters.year}-'
                 f'Q{date_minus_2_quarters.quarter}')) + pd.DateOffset(
                     months=2)

        if (indicator == 'Unemployment Rate' or
                indicator == 'Inflation Rate' or
                indicator == 'Inflation Rate MoM' or
                indicator == 'OECD Bussiness Confidence Indicator' or
                indicator == 'Short Term Interest Rate' or
                indicator == 'Long Term Interest Rate' or
                indicator == 'Total Manufacturing' or
                indicator == 'OECD Consumer Confidence Indicator' or
                indicator == 'Producer Price Index'):
            date_minus_2_months = date - pd.DateOffset(months=2)
            latest_known_period = pd.to_datetime(
                f'{date_minus_2_months.year}-{date_minus_2_months.month}-1')

        if (indicator == 'Manufacturing PMI' or
                indicator == 'Services PMI' or
                indicator == 'Economic Cycle X' or
                indicator == 'Economic Cycle Y'):
            date_minus_1_or_2_month = date - pd.DateOffset(months=1)
            latest_known_period = pd.to_datetime(
                (f'{date_minus_1_or_2_month.year}-'
                 f'{date_minus_1_or_2_month.month}-1'))

        if (indicator == 'Central Bank Rate'):
            latest_known_period = pd.to_datetime(
                f'{date.year}-{date.month}-1')

        if (indicator == 'Industrial Production' or
                indicator == 'Retail Sales'):
            date_minus_3_months = date - pd.DateOffset(months=3)
            latest_known_period = pd.to_datetime(
                f'{date_minus_3_months.year}-{date_minus_3_months.month}-1')

        if (indicator == 'Monthly Returns'):
            latest_known_period = date

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

    def calculate_principal_component_from_indicators(
            self, date, periods, indicators, n_components=1):
        indicators_norm = pd.DataFrame(
            data=np.zeros((periods*len(self.selected_countries),
                           len(indicators))),
            columns=indicators)

        for indicator in indicators:
            df = self.get_key_indicator_values(indicator)
            df_normalized = self.normilize_dataframe(df)
            df_last_values = self.get_latest_data(indicator, df_normalized,
                                                  date, periods=periods)

            indicators_norm.loc[:, indicator] = (
                df_last_values.values.reshape(-1))

        pca = PCA(n_components=n_components)
        principal_component = pca.fit_transform(indicators_norm)

        principal_component_arr = principal_component.reshape(
            -1, len(self.selected_countries))
        principal_component_df = pd.DataFrame(
            principal_component_arr,
            index=range(periods*n_components),
            columns=self.selected_countries)
        return principal_component_df

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

    def get_days_to_recalculate(self, months_to_skip=12):
        file_path = 'cache/days_to_rebalance.csv'
        if os.path.isfile(file_path):
            df_cache = pd.read_csv(file_path, index_col=0)
            days_to_rebalance_series = df_cache['Days to rebalance']
        else:
            df_countries, _ = self.get_etf_data()

            sql_handler = SqlAlquemySelectDataHandler()
            max_report_date = sql_handler.get_max_pmi_report_day()

            # Add extra 2 days for years 1999 to 2012 where PMI are mainly
            # extrapolated from Bussiness Confidence Indicators
            max_report_date[max_report_date.dt.day ==
                            1] += pd.DateOffset(days=2)

            # Get next trading day after last PMI index is published
            days_to_rebalance = []
            for month_start in max_report_date.values:
                from_date = month_start.astype(str)[:10]

                days_to_rebalance.append(df_countries[
                    from_date:].index.values[1].astype(str)[:10])

            days_to_rebalance_series = pd.Series(days_to_rebalance,
                                                 name='Days to rebalance')
            days_to_rebalance_series.to_csv(file_path)

        # Start after 1 year to have enough historic data for first rebalancing
        days_to_recalculate = days_to_rebalance_series.iloc[months_to_skip:]
        days_to_recalculate = pd.DatetimeIndex(days_to_recalculate)
        return days_to_recalculate

    def get_formatted_features(self, no_months=6, flatten=False):
        days_to_recalculate = self.get_days_to_recalculate()
        all_indicators = self.key_indicators + self.additional_indicators + [
            'Monthly Returns']

        x = []
        for date in days_to_recalculate:
            indicators = self.calculate_principal_component_from_indicators(
                date, periods=no_months, indicators=all_indicators)
            x.append(indicators.values)

        x_arr = np.array(x)
        if flatten:
            x_arr = x_arr.reshape(x_arr.shape[0], -1)

        return x_arr

    def get_formatted_targets(self, contraint_degree=0):
        days_to_recalculate = self.get_days_to_recalculate()
        df_countries, _ = self.get_etf_data()
        acwi_weights = self.get_acwi_weights()

        y = []
        for i in range(0, len(days_to_recalculate)):
            if i == len(days_to_recalculate) - 1:
                data_period = df_countries.loc[days_to_recalculate[i]:]
            else:
                data_period = df_countries.loc[
                    days_to_recalculate[i]:days_to_recalculate[i+1]]
            i += 1

            year_str = str(data_period.index[0].year)
            acwi_weights_year = acwi_weights.loc[year_str]

            try:
                optimizer = PortfolioOptimizer()
                if contraint_degree == 0:
                    w, constraints = optimizer.get_tight_constraints(
                        acwi_weights_year)
                elif contraint_degree == 1:
                    w, constraints = optimizer.get_normal_constraints(
                        acwi_weights_year)
                else:
                    w, constraints = optimizer.get_loose_constraints(
                        acwi_weights_year)

                optimal_portfolio = optimizer.get_optimal_portfolio(
                    data_period, w, constraints)
            except SolverError:
                summed_weight = acwi_weights_year.sum(axis=1)
                scaled_acwi_weights = acwi_weights_year.iloc[0] / \
                    summed_weight.values[0]
                optimal_portfolio = scaled_acwi_weights.round(3)

            y.append(optimal_portfolio.values)

        y_arr = np.array(y)
        return y_arr

    def train_train_split(self, x, y, with_val=True):
        test_split = int(0.8 * x.shape[0])

        if with_val:
            val_split = int(0.7 * x.shape[0])
            x_train = x[:val_split]
            y_train = y[:val_split]
            x_val = x[val_split:test_split]
            y_val = y[val_split:test_split]
        else:
            x_train = x[:test_split]
            y_train = y[:test_split]
            x_val = np.empty(0)
            y_val = np.empty(0)

        x_test = x[test_split:]
        y_test = y[test_split:]

        return x_train, y_train, x_val, y_val, x_test, y_test

    def apply_output_contraints(self, predictions, contraint_degree=0):
        days_to_recalculate = self.get_days_to_recalculate()
        df_countries, _ = self.get_etf_data()
        acwi_weights = self.get_acwi_weights()
        count = predictions.shape[0]

        predictions_df = pd.DataFrame(predictions,
                                      columns=df_countries.columns,
                                      index=days_to_recalculate[-count:])
        restricted_predictions_df = pd.DataFrame(
            np.zeros(predictions.shape), columns=df_countries.columns,
            index=days_to_recalculate[-count:])

        for index, row in predictions_df.iterrows():
            data_period = df_countries[:index].iloc[-22:-1]
            year_str = str(index.year)
            acwi_weights_year = acwi_weights.loc[year_str]
            original_predictions = row.values

            optimizer = PortfolioOptimizer()
            if contraint_degree == 0:
                w, constraints = optimizer.get_tight_constraints(
                    acwi_weights_year)
            elif contraint_degree == 1:
                w, constraints = optimizer.get_normal_constraints(
                    acwi_weights_year)
            else:
                w, constraints = optimizer.get_loose_constraints(
                    acwi_weights_year)

            restricted_predictions = optimizer.apply_output_contraints(
                original_predictions, data_period, w, constraints)
            restricted_predictions_df.loc[index, :] = restricted_predictions

        return restricted_predictions_df.values
