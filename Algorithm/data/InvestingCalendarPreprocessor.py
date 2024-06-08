from SqlAlquemySelectDataHandler import SqlAlquemySelectDataHandler
import pandas as pd
import os

from dotenv import load_dotenv
load_dotenv()


class InvestingCalendarPreprocessor:
    """ Class used to extract and process macroeconomic indicators from
    economic calendar download from Investing.com web site. """

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

        self.key_calendar_indicators = [
            'GDP Annual Growth Rate',
            'GDP Growth Rate',
            'Unemployment Rate',
            'Inflation Rate',
            'Inflation Rate MoM',
            'Producer Price Index',
            'Manufacturing PMI',
            'Industrial Production',
            'Retail Sales'
        ]

    def read_key_indicator(self, indicator, limit_date=''):
        if limit_date == '':
            file_name = indicator.lower().replace(' ', '_')
            file_path = f'cache/{file_name}_calendar.csv'
            if os.path.isfile(file_path):
                df_cache = pd.read_csv(
                    file_path, index_col=0, parse_dates=True)
                return df_cache

        if indicator == 'GDP Annual Growth Rate':
            df_calendar = self.process_quaterly_indicator(
                'GDP (YoY)', 'GDP Quarterly (YoY)', limit_date)
        if indicator == 'GDP Growth Rate':
            df_calendar = self.process_quaterly_indicator(
                'GDP (QoQ)', 'GDP Annualized (QoQ)', limit_date)
        if indicator == 'Unemployment Rate':
            df_calendar = self.process_monthly_indicator(
                'Unemployment Rate', limit_date)
        if indicator == 'Inflation Rate':
            df_calendar = self.process_monthly_indicator(
                'CPI (YoY)', limit_date)
        if indicator == 'Inflation Rate MoM':
            df_calendar = self.process_monthly_indicator(
                'CPI (MoM)', limit_date)
        if indicator == 'Producer Price Index':
            df_calendar = self.process_monthly_indicator(
                'PPI (YoY)', limit_date)
        if indicator == 'Manufacturing PMI':
            df_calendar = self.process_pmi_indicator(
                'Manufacturing PMI', 'procure.ch PMI', limit_date)
        if indicator == 'Industrial Production':
            df_calendar = self.process_monthly_indicator(
                'Industrial Production (YoY)', 'Industrial Output (YoY)',
                limit_date)
        if indicator == 'Retail Sales':
            df_calendar = self.process_monthly_indicator(
                'Retail Sales (YoY)', limit_date)

        if limit_date == '':
            df_calendar.to_csv(file_path)

        return df_calendar

    def process_quaterly_indicator(self, indicator, alt_indicator,
                                   limit_date=''):
        sql_handler = SqlAlquemySelectDataHandler()
        df = sql_handler.read_calendar_indicator(indicator, alt_indicator,
                                                 limit_date)
        df_processed = df.loc[:, ['ReportDateTime', 'Country', 'Indicator']]
        df_processed.loc[:, 'FullName'] = df['Indicator']
        self.assign_period(df_processed, freq='Q')

        df_processed['Value'] = df['Actual'].str.rstrip('%').astype(float)

        prefixes = self.standard_prefixes
        suffixes = self.monthly_suffixes + self.quarterly_suffixes
        self.clean_indicators(df_processed, prefixes, suffixes,
                              indicator, alt_indicator)
        df_processed = df_processed[df_processed['Indicator'] == indicator]
        return df_processed

    def process_pmi_indicator(self, indicator, alt_indicator='',
                              limit_date=''):
        sql_handler = SqlAlquemySelectDataHandler()
        df = sql_handler.read_calendar_indicator(indicator, alt_indicator,
                                                 limit_date)
        df_processed = df.loc[:, ['ReportDateTime', 'Country', 'Indicator']]
        df_processed.loc[:, 'FullName'] = df['Indicator']

        periods = pd.PeriodIndex(df_processed['ReportDateTime'], freq='M')
        df_processed['Period'] = periods.to_timestamp()

        # correct period when logged at the beginning of the month
        prev_periods = pd.PeriodIndex(df_processed[
            df_processed['ReportDateTime'].dt.day < 11]['ReportDateTime'],
            freq='M')-1
        df_processed.loc[df_processed['ReportDateTime'].dt.day <
                         11, 'Period'] = prev_periods.to_timestamp()

        df_processed['Value'] = df['Actual'].astype(float)

        prefixes = self.pmi_prefixes
        suffixes = self.monthly_suffixes + [' (MoM)']
        self.clean_indicators(df_processed, prefixes, suffixes,
                              indicator, alt_indicator)
        df_processed = df_processed[df_processed['Indicator'] == indicator]
        return df_processed

    def process_monthly_indicator(self, indicator, alt_indicator='',
                                  pct_value=True, limit_date=''):
        sql_handler = SqlAlquemySelectDataHandler()
        df = sql_handler.read_calendar_indicator(indicator, alt_indicator,
                                                 limit_date)
        df_processed = df.loc[:, ['ReportDateTime', 'Country', 'Indicator']]
        df_processed.loc[:, 'FullName'] = df['Indicator']
        self.assign_period(df_processed, freq='M')

        if pct_value:
            df_processed.loc[:, 'Value'] = df['Actual'].str.rstrip(
                '%').str.replace(',', '').astype(float)
        else:
            df_processed.loc[:, 'Value'] = df['Actual'].str.replace(
                ',', '').apply(self.money_to_int)

        prefixes = self.standard_prefixes
        suffixes = self.monthly_suffixes + self.quarterly_suffixes + [' s.a.']
        self.clean_indicators(df_processed, prefixes, suffixes,
                              indicator, alt_indicator)
        df_processed = df_processed[df_processed['Indicator'] == indicator]
        return df_processed

    def assign_period(self, df_processed, freq):
        df_processed.loc[:, 'Period'] = None
        for ind, row in df_processed.iterrows():
            indicator = row['Indicator']
            report_date_time = row['ReportDateTime']
            if indicator.endswith(tuple(self.monthly_suffixes)):
                month = indicator[-4:-1]
                if ((month == 'Dec' or month == 'Nov') and
                        report_date_time.month <= 2):
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        month + '-' + str(report_date_time.year-1))
                else:
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        month + '-' + str(report_date_time.year))
            elif indicator.endswith(tuple(self.quarterly_suffixes)):
                quarter = indicator[-3:-1]
                if quarter == 'Q1':
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        '01-' + str(report_date_time.year))
                elif quarter == 'Q2':
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        '04-' + str(report_date_time.year))
                elif quarter == 'Q3' and report_date_time.month < 7:
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        '07-' + str(report_date_time.year-1))
                elif quarter == 'Q3':
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        '07-' + str(report_date_time.year))
                elif quarter == 'Q4' and report_date_time.month < 7:
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        '10-' + str(report_date_time.year-1))
                else:
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        '10-' + str(report_date_time.year))
            elif freq == 'M':
                if report_date_time.day >= 25:
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        str(report_date_time.month) + '-' + str(
                            report_date_time.year))
                elif report_date_time.month == 1:
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        '12-' + str(report_date_time.year-1))
                else:
                    df_processed.loc[ind, 'Period'] = pd.to_datetime(
                        str(report_date_time.month-1) + '-' + str(
                            report_date_time.year))
            else:
                df_processed.loc[ind, 'Period'] = (pd.Period(
                    report_date_time, freq='Q')-1).to_timestamp()

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

    def get_most_recent_values(self, df_calendar, date, no_months,
                               is_quarterly=False):
        date_from = date - pd.DateOffset(months=12)
        date_from = date_from.strftime('%Y-%m-01')
        date_to = date.strftime('%Y-%m-%d')

        period = pd.period_range(date_from, date_to, freq='M')
        period = period.to_timestamp()

        df_processed = df_calendar[df_calendar['ReportDateTime'] < date_to]
        df_processed.index = pd.DatetimeIndex(df_processed['Period'])
        df_countries = pd.DataFrame(
            index=period, columns=self.selected_countries)
        for country in self.selected_countries:
            values = df_processed[df_processed['Country'] == country]['Value']
            values = values[~values.index.duplicated(keep='last')]
            df_countries.loc[:, country] = values

        if is_quarterly:
            df_countries = df_countries.ffill(limit=2)

        df_countries = df_countries.dropna(thresh=10)
        return df_countries.iloc[-no_months:]
