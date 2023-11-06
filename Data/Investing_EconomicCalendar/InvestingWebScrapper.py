import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from io import StringIO


class InvestingWebScrapper:

    def __init__(self):
        service = Service(executable_path='../chromedriver.exe')
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)

    def open_economic_calendar(self):
        self.driver.get('https://www.investing.com/economic-calendar/')
        time.sleep(2)

        botton_cookies = self.driver.find_element(
            By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'
        )
        botton_cookies.click()
        time.sleep(2)

        for _ in range(30):
            botton_signup = self.driver.find_element(
                By.XPATH, '//*[@id="PromoteSignUpPopUp"]/div[2]/i')
            print('.', end='')
            if botton_signup.is_displayed():
                botton_signup.click()
                break
            else:
                time.sleep(2)

    def read_all_indicators(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        table = self.driver.find_element(
            By.XPATH, '//*[@class="eCalNew eCalMainNew ecoCalCont"]'
        )
        dfs = pd.read_html(StringIO(table.get_attribute('innerHTML')))
        df_raw = dfs[0]
        if type(df_raw.columns[0]) is tuple:  # Fix for multi-indexes
            df_raw.columns = [c[0] for c in df_raw.columns]

        df_filtered = df_raw[~df_raw['Cur.'].isna()]  # Exclude holidays
        # Get dates for all rows
        df_filtered.loc[:, 'Date'] = df_filtered['Imp.'].ffill()
        # Remove rows with dates
        df_filtered = df_filtered[df_filtered['Imp.'].isna()]

        flags = self.driver.find_elements(
            By.XPATH, '//*[@class="left flagCur noWrap"]/span'
        )
        countries = []
        for flag in flags:
            countries.append(flag.get_attribute('title'))
        df_filtered['Country'] = countries

        # Get only indicators
        df_filtered = df_filtered[(~df_filtered['Actual'].isna()) &
                                  (df_filtered['Time'].str.len() == 5)]
        df_filtered.rename(columns={'Cur.': 'Currency'}, inplace=True)
        df_filtered['DateTime'] = pd.to_datetime(
            df_filtered['Date'] + ' ' + df_filtered['Time'])

        df = df_filtered[['DateTime', 'Country', 'Currency', 'Event',
                          'Actual', 'Forecast', 'Previous']]
        return df
