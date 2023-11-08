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

    def open_economic_calendar(self, select_yesterday=True):
        self.driver.get('https://www.investing.com/economic-calendar/')
        time.sleep(1)

        botton_cookies = self.driver.find_element(
            By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'
        )
        botton_cookies.click()
        time.sleep(1)

        self.select_all_countries()

        if select_yesterday:
            self.driver.execute_script(
                "window.scrollTo(0, 0);")
            time.sleep(1)

            self.close_sign_in_if_open()
            botton_yesterday = self.driver.find_element(
                By.XPATH, '//*[@id="timeFrame_yesterday"]'
            )
            botton_yesterday.click()
            time.sleep(1)

    def read_all_indicators(self, scroll_wait=1):
        self.scroll_to_bottom(scroll_wait)

        self.close_sign_in_if_open()
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

        df_filtered['Country'] = self.read_countries_from_flags()

        # Get only indicators
        df_filtered = df_filtered[(~df_filtered['Actual'].isna()) &
                                  (df_filtered['Time'].str.len() == 5)]
        df_filtered.rename(columns={'Cur.': 'Currency'}, inplace=True)
        df_filtered['DateTime'] = pd.to_datetime(
            df_filtered['Date'] + ' ' + df_filtered['Time'])

        df = df_filtered[['DateTime', 'Country', 'Currency', 'Event',
                          'Actual', 'Forecast', 'Previous']]

        df = self.filter_countries(df)
        return df

    def close_sign_in_if_open(self):
        botton_signup = self.driver.find_element(
            By.XPATH, '//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        if botton_signup.is_displayed():
            botton_signup.click()

    def select_all_countries(self):
        self.close_sign_in_if_open()
        botton_filter = self.driver.find_element(
            By.XPATH, '//*[@id="filterStateAnchor"]'
        )
        botton_filter.click()
        time.sleep(1)

        self.close_sign_in_if_open()
        botton_select_all = self.driver.find_element(
            By.XPATH, '//*[@onclick="selectAll(\'country[]\');"]'
        )
        botton_select_all.click()
        time.sleep(1)

        self.close_sign_in_if_open()
        botton_submit = self.driver.find_element(
            By.XPATH, '//*[@id="ecSubmitButton"]'
        )
        botton_submit.click()
        time.sleep(3)

    def scroll_to_bottom(self, sleep_time):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_time)

    def read_countries_from_flags(self):
        flags = self.driver.find_elements(
            By.XPATH, '//*[@class="left flagCur noWrap"]/span'
        )
        countries = []
        for flag in flags:
            countries.append(flag.get_attribute('title'))
        return countries

    def filter_countries(self, df):
        all_countries = ['United States', 'Japan', 'United Kingdom', 'Canada',
                         'France', 'Switzerland', 'Germany', 'Australia',
                         'Netherlands', 'Sweden', 'Spain', 'Hong Kong',
                         'Italy', 'Singapore', 'Belgium', 'Norway', 'Israel',
                         'Ireland', 'New Zealand', 'Austria', 'Euro Zone',
                         'China', 'Taiwan', 'India', 'South Korea', 'Brazil',
                         'Saudi Arabia', 'South Africa', 'Mexico', 'Indonesia',
                         'Türkiye', 'Poland', 'Argentina', 'Russia']

        df_to_save = df[df['Country'].isin(all_countries)]
        return df_to_save

    def close_browser(self):
        self.driver.close()
