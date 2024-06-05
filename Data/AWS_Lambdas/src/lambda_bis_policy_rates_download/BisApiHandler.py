import requests
import pandas as pd
import xmltodict


class BisApiHandler:
    """ API Handler class to get central bank rates from BIS API. """

    def get_data(self, start_date, end_date):
        url = ('https://stats.bis.org/api/v1/data/BIS%2CWS_CBPOL_D%2C1.0/'
               f'all/all?startPeriod={start_date}&detail=dataonly')
        response = requests.get(url)
        python_dict = xmltodict.parse(response.text)
        dataset = python_dict['message:StructureSpecificData'][
            'message:DataSet']['Series']

        df = pd.DataFrame(index=pd.date_range(start_date, end_date, freq='B'))

        for i in range(len(dataset)):
            country_code = dataset[i]['@REF_AREA']
            df_parsed = pd.DataFrame(dataset[i]['Obs'])
            df_parsed.index = pd.to_datetime(df_parsed['@TIME_PERIOD'])
            if country_code == 'XM':
                euro_zone_countries = [
                    'AT', 'BE', 'DE', 'ES', 'FI', 'FR',
                    'GR', 'IE', 'IT', 'NL', 'PT']
                for eu_country in euro_zone_countries:
                    df[eu_country +
                        '_IR'] = df_parsed['@OBS_VALUE'].astype(float)
            else:
                df[country_code +
                    '_IR'] = df_parsed['@OBS_VALUE'].astype(float)

        df = df.ffill()
        df = df.bfill()

        return df
