import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from io import StringIO
import uuid
import os


class InvestingIndicesWebScrapper:

    def get_driver(self, linux):
        if linux:
            self._tmp_folder = '/tmp/{}'.format(uuid.uuid4())
            if not os.path.exists(self._tmp_folder):
                os.makedirs(self._tmp_folder)

            if not os.path.exists(self._tmp_folder + '/chrome-user-data'):
                os.makedirs(self._tmp_folder + '/chrome-user-data')

            if not os.path.exists(self._tmp_folder + '/data-path'):
                os.makedirs(self._tmp_folder + '/data-path')

            if not os.path.exists(self._tmp_folder + '/cache-dir'):
                os.makedirs(self._tmp_folder + '/cache-dir')

            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = "/opt/chrome/chrome"
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-tools")
            chrome_options.add_argument("--no-zygote")
            chrome_options.add_argument("--single-process")
            chrome_options.add_argument("window-size=2560x1440")
            chrome_options.add_argument(
                f"--user-data-dir={self._tmp_folder}/chrome-user-data")
            chrome_options.add_argument(
                f"--data-path={self._tmp_folder}/data-path")
            chrome_options.add_argument(
                f"--disk-cache-dir={self._tmp_folder}/cache-dir")
            chrome_options.add_argument("--remote-debugging-port=9222")
            return webdriver.Chrome("/opt/chromedriver",
                                    options=chrome_options)
        else:
            service = Service(executable_path='../chromedriver.exe')
            options = webdriver.ChromeOptions()
            return webdriver.Chrome(service=service, options=options)

    def retrieve_prices_from_investing(self, path, linux):
        driver = self.get_driver(linux)

        base_url = 'https://www.investing.com/indices/'
        driver.get(f'{base_url}{path}')
        time.sleep(1)

        botton_cookies = driver.find_elements(
            By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'
        )
        if len(botton_cookies) == 1 and botton_cookies[0].is_displayed():
            botton_cookies[0].click()
        time.sleep(1)

        table = driver.find_element(
            By.XPATH, '//*[@id="__next"]'
        )
        dfs = pd.read_html(StringIO(table.get_attribute('innerHTML')))
        if (path == 'oslo-obx-historical-data' or
                path == 'ftse-jse-top-40-historical-data'):
            df_raw = dfs[1]
        else:
            df_raw = dfs[0]

        driver.close()

        df_raw.index = pd.to_datetime(df_raw['Date'])
        df_raw = df_raw.sort_index()
        return df_raw['Price']
