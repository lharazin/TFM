import pandas as pd
import numpy as np
import requests
import urllib3
import ssl
import io

import warnings
warnings.simplefilter("ignore", UserWarning)
pd.options.mode.chained_assignment = None  # default='warn'


all_countries = [
    'United States', 'Japan', 'United Kingdom', 'Canada', 'France',
    'Switzerland', 'Germany', 'Australia', 'Netherlands', 'Denmark',
    'Sweden', 'Spain', 'Hong Kong', 'Italy', 'Singapore', 'Finland',
    'Belgium', 'Norway', 'Israel', 'Ireland', 'New Zealand', 'Austria',
    'Portugal', 'Eurozone', 'China', 'Taiwan', 'India', 'Korea',
    'Brazil', 'Saudi Arabia', 'South Africa', 'Mexico', 'Thailand',
    'Indonesia', 'Malaysia', 'United Arab Emirates', 'Qatar', 'Kuwait',
    'Turkiye', 'Philippines', 'Poland', 'Chile', 'Greece', 'Peru',
    'Hungary', 'Czechia', 'Egypt', 'Colombia', 'Argentina', 'Russia']

all_countries_in_oecd = [
    'United States', 'Japan', 'United Kingdom', 'Canada', 'France',
    'Switzerland', 'Germany', 'Australia', 'Netherlands', 'Denmark',
    'Sweden', 'Spain', 'Italy', 'Finland', 'Belgium', 'Norway',
    'Israel', 'Ireland', 'New Zealand', 'Austria', 'Portugal', 'Eurozone',
    'China', 'India', 'Korea', 'Brazil', 'Saudi Arabia', 'South Africa',
    'Mexico', 'Indonesia', 'Turkiye', 'Poland', 'Chile', 'Greece',
    'Hungary', 'Czechia', 'Colombia', 'Argentina', 'Russia']

selected_countries = [
    'United States', 'Japan', 'United Kingdom', 'Canada', 'France',
    'Switzerland', 'Germany', 'Australia', 'Netherlands', 'Sweden',
    'Spain', 'Italy', 'Belgium', 'Norway', 'Israel', 'Ireland',
    'Austria', 'China', 'Taiwan', 'India', 'Korea', 'Brazil',
    'Saudi Arabia', 'South Africa', 'Mexico', 'Indonesia',
    'Turkiye',  'Poland', 'Argentina', 'Russia']


def format_oecd_data(df):
    df_formatted = pd.DataFrame(index=df['TIME'].unique())

    for country in df['Country'].unique():
        df_formatted[country] = df[df['Country'] == country]['Value']

    df_formatted.rename(columns={
        'Czech Republic': 'Czechia',
        'Türkiye': 'Turkiye',
        "China (People's Republic of)": 'China',
        'Euro area (19 countries)': 'Eurozone'
    }, inplace=True)

    df_formatted = df_formatted.reindex(columns=all_countries_in_oecd)
    df_formatted.index = pd.to_datetime(df_formatted.index.astype(str))
    return df_formatted


def check_data_coverage(df):
    total_na = df.isna().sum().sum()
    total_na_not_in_oecd = len(df.index)*(len(all_countries)-len(df.columns))
    total_cells = len(df.index)*len(all_countries)

    data_coverage_pct = round(
        (total_cells-total_na-total_na_not_in_oecd)/total_cells*100, 1)
    print('Data coverage since 1999 (50 countries): ', data_coverage_pct, '%')

    df_recent = df['2013':]
    if 'Taiwan' not in df_recent.columns:
        df_recent.loc[:, 'Taiwan'] = np.nan
    df_recent = df_recent[selected_countries]
    nas = df_recent.isna().sum().sum()
    total = df_recent.shape[0]*len(selected_countries)
    coverage_11y = round((total - nas)/total*100, 1)
    print('Data coverage since 2013 (30 countries):', coverage_11y, '%')
    print()

    available_countries = df.columns[~df.isna().all()]
    print('Available countries:')
    print(available_countries)
    print()

    no_data = df.columns[df.isna().all()]
    print('No data:')
    print(no_data)
    print()

    print('Missing first:')
    for country in df.columns:
        first_valid = df[country].first_valid_index()
        if first_valid is not None and (
                not str(first_valid).startswith('1999')):
            print(country, first_valid)
    print()

    print('Missing last:')
    for country in df.columns:
        last_valid = df[country].last_valid_index()
        if last_valid is not None and (not str(last_valid).startswith('2023')):
            print(country, last_valid)

    print()
    print('Done')


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session


countries = ('AUS+AUT+BEL+CAN+CHL+COL+CZE+DNK+FIN+FRA+DEU+GRC+HUN+IRL+'
             'ISR+ITA+JPN+KOR+MEX+NLD+NZL+NOR+POL+PRT+ESP+SWE+CHE+TUR+'
             'GBR+USA+ARG+BRA+CHN+IND+IDN+RUS+SAU+ZAF+EA19')


def get_oecd_data(indicator, subject, measure, freq, file_name,
                  countries_before_subject=False, with_measure=True,
                  filter_measure_on_df=False, with_freq=True):
    if freq == 'Q':
        startTime = '1999-Q1'
    else:
        startTime = '1999-01'

    if countries_before_subject:
        countries_and_subject = f'{countries}.{subject}'
    else:
        countries_and_subject = f'{subject}.{countries}'

    base_url = f'https://stats.oecd.org/SDMX-JSON/data/{indicator}/'
    params = f'all?startTime={startTime}&contentType=csv'
    if with_measure:
        url = f'{base_url}{countries_and_subject}.{measure}.{freq}/{params}'
    elif with_freq:
        url = f'{base_url}{countries_and_subject}.{freq}/{params}'
    else:
        url = f'{base_url}/{countries_and_subject}/{params}'

    print(url)
    res = get_legacy_session().get(url)
    df = pd.read_csv(io.BytesIO(res.content), sep=',')

    if filter_measure_on_df:
        df = df[df['MEASURE'] == measure]

    df.index = df['TIME']

    df_formatted = format_oecd_data(df)
    df_formatted = df_formatted.sort_index()
    df_formatted = df_formatted.round(4)
    check_data_coverage(df_formatted)
    df_formatted.to_csv(f'Indicators/OECD_{file_name}.csv')
    return df_formatted
