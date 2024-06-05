import pandas as pd
import wbgapi as wb
from SqlAlquemyInsertIndicatorsHandler import SqlAlquemyInsertIndicatorsHandler


class WorldBankApiHandler:
    """ API Handler class to indicators from WorldBankData API. """

    def __init__(self):
        self.country_codes = {
            'United States': 'USA',
            'Japan': 'JPN',
            'United Kingdom': 'GBR',
            'Canada': 'CAN',
            'France': 'FRA',
            'Switzerland': 'CHE',
            'Germany': 'DEU',
            'Australia': 'AUS',
            'Netherlands': 'NLD',
            'Denmark': 'DNK',
            'Sweden': 'SWE',
            'Spain': 'ESP',
            'Hong Kong': 'HKG',
            'Italy': 'ITA',
            'Singapore': 'SGP',
            'Finland': 'FIN',
            'Belgium': 'BEL',
            'Norway': 'NOR',
            'Israel': 'ISR',
            'Ireland': 'IRL',
            'New Zealand': 'NZL',
            'Austria': 'AUT',
            'Portugal': 'PRT',
            'Eurozona': 'EMU',

            'China': 'CHN',
            'Taiwan': '',
            'India': 'IND',
            'Korea': 'KOR',
            'Brazil': 'BRA',
            'Saudi Arabia': 'SAU',
            'South Africa': 'ZAF',
            'Mexico': 'MEX',
            'Thailand': 'THA',
            'Indonesia': 'IDN',
            'Malaysia': 'MYS',
            'United Arab Emirates': 'ARE',
            'Qatar': 'QAT',
            'Kuwait': 'KWT',
            'Turkiye': 'TUR',
            'Philippines': 'PHL',
            'Poland': 'POL',
            'Chile': 'CHL',
            'Greece': 'GRC',
            'Peru': 'PER',
            'Hungary': 'HUN',
            'Czechia': 'CZE',
            'Egypt': 'EGY',
            'Colombia': 'COL',
            'Argentina': 'ARG',
            'Russia': 'RUS'
        }

    def read_world_bank_indicator(self, symbol_code, no_years):
        df = wb.data.DataFrame(symbol_code, self.country_codes.values(),
                               mrv=no_years)
        df.index.name = None
        df = df.T
        df.index = pd.to_datetime(df.index.str[2:])
        inv_map = {v: k for k, v in self.country_codes.items()}
        df.columns = df.columns.map(inv_map)
        return df

    def update_world_bank_indicators(self, no_of_years):
        sql_handler = SqlAlquemyInsertIndicatorsHandler()
        wb_indicators = sql_handler.get_symbol_codes('World Bank')

        for _, row in wb_indicators.iterrows():
            indicator_id = row.iloc[0]
            indicator = row.iloc[1]
            symbol_code = row.iloc[2]

            df = self.read_world_bank_indicator(symbol_code, no_of_years)
            start_year = df.first_valid_index().year
            end_year = df.last_valid_index().year

            sql_handler.delete_all_records(indicator_id, start_year)
            for country in df.columns:
                values = df[country].dropna()
                if (len(values) > 0):
                    sql_handler.insert_into_table(indicator_id,
                                                  country, values)

            count = sql_handler.get_indicator_count(indicator_id, start_year)
            print(f'{indicator} (id={indicator_id}): inserted {count}',
                  f'records from {start_year} to {end_year}')
