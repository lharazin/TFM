from src.preprocessing.SqlAlquemySelectHandler import SqlAlquemySelectHandler
import pandas as pd

from dotenv import load_dotenv
load_dotenv()


class InvestingCalendarPreprocessor:

    def __init__(self):
        self.all_countries = [
            'United States', 'Japan', 'United Kingdom', 'Canada', 'France',
            'Switzerland', 'Germany', 'Australia', 'Netherlands', 'Denmark',
            'Sweden', 'Spain', 'Hong Kong', 'Italy', 'Singapore', 'Finland',
            'Belgium', 'Norway', 'Israel', 'Ireland', 'New Zealand', 'Austria',
            'Portugal', 'Eurozone', 'China', 'Taiwan', 'India', 'Korea',
            'Brazil', 'Saudi Arabia', 'South Africa', 'Mexico', 'Thailand',
            'Indonesia', 'Malaysia', 'United Arab Emirates', 'Qatar', 'Kuwait',
            'Turkiye', 'Philippines', 'Poland', 'Chile', 'Greece', 'Peru',
            'Hungary', 'Czechia', 'Egypt', 'Colombia', 'Argentina', 'Russia']

        self.selected_countries = [
            'United States', 'Japan', 'United Kingdom', 'Canada', 'France',
            'Switzerland', 'Germany', 'Australia', 'Netherlands', 'Sweden',
            'Spain', 'Italy', 'Belgium', 'Norway', 'Israel', 'Ireland',
            'Austria', 'China', 'Taiwan', 'India', 'Korea', 'Brazil',
            'Saudi Arabia', 'South Africa', 'Mexico', 'Indonesia',
            'Turkiye',  'Poland', 'Argentina', 'Russia']

        self.pmi_prefixes = [
            'S&P Global Hong Kong ',
            'S&P Global Canada ',
            'S&P Global/CIPS UK ',
            'S&P Global / CIPS UK ',
            'S&P Global US ',
            'S&P Global Mexico ',
            'S&P Global India ',
            'S&P Global South Korea ',
            'S&P Global Philippines ',
            'S&P Global Greece ',
            'HCOB Germany ',
            'HCOB Eurozone ',
            'S&P Global ',
            'Judo Bank Australia ',
            'au Jibun Bank Japan ',
            'HCOB France ',
            'S&P Global Taiwan ',
            'Unicredit Bank Austria ',
            'Nikkei ',
            'AIB Ireland ',
            'Caixin ',
            'Russian S&P Global ',
            'Poland ',
            'HCOB Spain ',
            'HCOB Italy ',
            'Taiwan ',
            'Riyad Bank Saudi Arabia ',
            'Chinese ',
            'Istanbul Chamber of Industry Turkey '
        ]
        self.standard_prefixes = [
            'Austrian ',
            'Italian ',
            'Chinese ',
            'Dutch ',
            'German ',
            'French ',
            'Spanish ',
            'National ',
            'Irish ',
            'Belgium ',
            'Belgian ',
            'Portuguese ',
            'Finnish ',
            'Turkish ',
            'Brazilian ',
            'Greek ',
            'Philippines ',
            'Electronic Card ',
            'Monthly ',
            'Quarterly ',
            'CB ',
            'FGV ',
            'GfK '
        ]

        self.quarterly_suffixes = [' (Q1)', ' (Q2)', ' (Q3)', ' (Q4)']
        self.monthly_suffixes = [' (Jan)', ' (Feb)', ' (Mar)', ' (Apr)',
                                 ' (May)', ' (Jun)', ' (Jul)', ' (Aug)',
                                 ' (Sep)', ' (Oct)', ' (Nov)', ' (Dec)']

    def explore_indicators(self, year, thres):
        sql_handler = SqlAlquemySelectHandler()
        df = sql_handler.read_all_indicators(year)

        df_processed = df.loc[:, ['ReportDateTime', 'Country', 'Indicator']]

        prefixes = self.pmi_prefixes + self.standard_prefixes
        suffixes = self.quarterly_suffixes + self.monthly_suffixes + [' s.a.']
        self.clean_indicators(df_processed, prefixes, suffixes)

        grouped_indicators = df_processed.groupby(
            'Indicator').count().sort_values(by='ReportDateTime',
                                             ascending=False)

        for indicator in grouped_indicators.index:
            countries = df_processed[
                df_processed['Indicator'] == indicator].groupby(
                    'Country').count().index.shape[0]
            if countries >= thres:
                print(indicator, grouped_indicators.loc[indicator, 'Country'],
                      ',', countries)

    def get_count_by_country_and_month(self):
        sql_handler = SqlAlquemySelectHandler()
        df = sql_handler.read_count_by_country()
        df.index = df['MonthStart']
        df.index.name = None

        period = pd.period_range('1999-01-01', '2023-12-01', freq='M')
        df_summary = pd.DataFrame(index=period.to_timestamp(),
                                  columns=self.all_countries)
        for country in self.all_countries:
            df_summary[country] = df[df['Country'] == country]['Count']

        df_summary = df_summary.fillna(0).astype(int)
        return df_summary

    def process_quaterly_indicator(self, indicator, alt_indicator):
        sql_handler = SqlAlquemySelectHandler()
        df = sql_handler.read_indicator(indicator, alt_indicator)
        df_processed = df.loc[:, ['ReportDateTime', 'Country', 'Indicator']]

        prefixes = self.standard_prefixes
        suffixes = self.quarterly_suffixes
        self.clean_indicators(df_processed, prefixes, suffixes,
                              indicator, alt_indicator)

        periods = pd.PeriodIndex(df_processed['ReportDateTime'], freq='Q')-1
        df_processed['Period'] = periods.to_timestamp()
        df_processed['Value'] = df['Actual'].str.rstrip('%').astype(float)
        df_processed = df_processed[df_processed['Indicator'] == indicator]

        self.print_summary(df_processed, freq='Q')
        return df_processed

    def process_pmi_indicator(self, indicator, alt_indicator=''):
        sql_handler = SqlAlquemySelectHandler()
        df = sql_handler.read_indicator(indicator, alt_indicator)
        df_processed = df.loc[:, ['ReportDateTime', 'Country', 'Indicator']]

        prefixes = self.pmi_prefixes
        suffixes = self.monthly_suffixes + [' (MoM)']
        self.clean_indicators(df_processed, prefixes, suffixes,
                              indicator, alt_indicator)

        periods = pd.PeriodIndex(df_processed['ReportDateTime'], freq='M')
        df_processed['Period'] = periods.to_timestamp()

        # correct period when logged at the beginning of the month
        prev_periods = pd.PeriodIndex(df_processed[
            df_processed['ReportDateTime'].dt.day < 15]['ReportDateTime'],
            freq='M')-1
        df_processed.loc[df_processed['ReportDateTime'].dt.day <
                         15, 'Period'] = prev_periods.to_timestamp()

        df_processed['Value'] = df['Actual'].astype(float)
        df_processed = df_processed[df_processed['Indicator'] == indicator]

        self.print_summary(df_processed, freq='M')
        return df_processed

    def process_monthly_indicator(self, indicator, alt_indicator='',
                                  pct_value=True):
        sql_handler = SqlAlquemySelectHandler()
        df = sql_handler.read_indicator(indicator, alt_indicator)
        df_processed = df.loc[:, ['ReportDateTime', 'Country', 'Indicator']]

        prefixes = self.standard_prefixes
        suffixes = self.monthly_suffixes + self.quarterly_suffixes + [' s.a.']
        self.clean_indicators(df_processed, prefixes, suffixes,
                              indicator, alt_indicator)

        periods = pd.PeriodIndex(df_processed['ReportDateTime'], freq='M')-1
        df_processed['Period'] = periods.to_timestamp()

        if pct_value:
            df_processed['Value'] = df['Actual'].str.rstrip('%').str.replace(
                ',', '').astype(float)
        else:
            df_processed['Value'] = df['Actual'].str.replace(',', '').apply(
                self.money_to_int)

        df_processed = df_processed[df_processed['Indicator'] == indicator]

        self.print_summary(df_processed, freq='M')
        return df_processed

    def transform_to_countries_df(self, df_processed, freq):
        period = pd.period_range('1999-01-01', '2023-12-31', freq=freq)
        period = period.to_timestamp()

        df_processed.index = df_processed['Period']
        df_countries = pd.DataFrame(index=period, columns=self.all_countries)
        for country in self.all_countries:
            values = df_processed[df_processed['Country'] == country]['Value']
            values = values[~values.index.duplicated(keep='first')]
            df_countries.loc[:, country] = values

        return df_countries

    def clean_indicators(self, df_processed, prefixes, suffixes,
                         indicator='', alt_indicator=''):
        for prefix in prefixes:
            df_processed['Indicator'] = df_processed[
                'Indicator'].str.removeprefix(prefix)

        for suffix in suffixes:
            df_processed['Indicator'] = df_processed[
                'Indicator'].str.removesuffix(suffix)

        df_processed['Indicator'].replace(alt_indicator, indicator,
                                          inplace=True)

    def money_to_int(self, str_value):
        try:
            power = 0
            if str_value[-1] == 'K':
                power = 3
            elif str_value[-1] == 'M':
                power = 6
            elif str_value[-1] == 'B':
                power = 9
            elif str_value[-1] == 'T':
                power = 12
            elif str_value[:-1] == '':
                return 0

            return float(str_value[:-1]) * 10**power
        except TypeError:
            return str_value

    def print_summary(self, df_processed, freq):
        missing_countries = [x for x in self.all_countries
                             if x not in df_processed['Country'].unique()]
        print('Missing countries')
        print(missing_countries)

        print('Avg publish delay: ', (df_processed['ReportDateTime'] -
                                      df_processed['Period']).mean())

        df_countries = self.transform_to_countries_df(
            df_processed, freq=freq)
        nas = df_countries.isna().sum().sum()
        total = df_countries.shape[0]*df_countries.shape[1]
        coverage_25y = round((total - nas)/total*100, 1)
        print('Data coverage since 1999 (50 countries):', coverage_25y, '%')

        df_recent = df_countries['2013':][self.selected_countries]
        nas = df_recent.isna().sum().sum()
        total = df_recent.shape[0]*df_recent.shape[1]
        coverage_11y = round((total - nas)/total*100, 1)
        print('Data coverage since 2013 (30 countries):', coverage_11y, '%')
