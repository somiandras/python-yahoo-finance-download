# -*- coding: utf-8 -*-

'''Data downloader for Yahoo Finance API 2017'''

import requests
import re
from datetime import datetime
import pandas as pd
import io


class Downloader:
    def __init__(self):
        self.DATA_TYPES = ['history', 'div', 'split']
        self._cookie = None
        self._crumb = None
        self.attempt_counter = 0
        self.years = 20
        self.ticker = None

    def set_ticker(self, ticker):
        '''Set the ticker for the downloader instance.'''

        self.ticker = ticker or self.ticker
        if self.ticker is None:
            raise Exception('You should specify a ticker in set_ticker()')
        return self

    def set_years(self, years):
        '''Set the year range for the downloader instance.'''

        if years is None:
            raise Exception('You should specify the number of years in set_years()')
        else:
            self.years = years
        return self

    def settings(self):
        '''Return the currently set ticker and year range in a tuple'''

        return (self.ticker, self.years)

    def _get_crumb_and_cookies(self):
        '''Make an initial request to extract cookies and crumb to use in subsequent requests'''

        url = 'https://finance.yahoo.com/quote/^GSPC'
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            self._cookie = r.cookies
            search = re.search('\"CrumbStore\"\:\{\"crumb\"\:\"(.*)\"\}\,\"QuotePageStore\"', r.text)
            if search is None:
                raise Exception('No crumb found in initial response')
            else:
                self._crumb = search.group(1)
        else:
            r.raise_for_status()

    def get_single_data_type(self, ticker=None, data_type='history', years=20):
        '''Return a dataframe of the specified data type [history|div|split] for the given ticker 
        and specified number of years ending today (or the latest available).
        Defaults to the previously set ticker and 20 years.'''

        if self._cookie is None or self._crumb is None:
            self._get_crumb_and_cookies()

        self.ticker = ticker or self.ticker
        self.years = years

        start_date = datetime.today().replace(year=datetime.today().year - self.years)

        self.attempt_counter += 1
        params = {
            'period1': int(start_date.timestamp()),
            'period2': int(datetime.today().timestamp()),
            'events': data_type,
            'crumb': self._crumb,
            'interval': '1d'
        }
        url = 'https://query1.finance.yahoo.com/v7/finance/download/{}'.format(self.ticker)
        r = requests.get(url, params=params, cookies=self._cookie)
        if r.status_code == requests.codes.ok:
            df = pd.read_csv(io.BytesIO(r.content))
            df.set_index('Date', inplace=True)
            self.attempt_counter = 0
            return df
        elif r.status_code == 401:
            # In case of authorization error renew crumb and cookie and fetch data again. Max. 10 attempts.
            # See the issue here: https://github.com/c0redumb/yahoo_quote_download/issues/3
            self._crumb = None
            self._cookie = None

            if self.attempt_counter < 10:
                print('Auth error, retrying...')
                return self.get_single_data_type(data_type=data_type)
            else:
                raise Exception('Permanent Auth Error')
        else:
            r.raise_for_status()

    def _get_all_data_types(self):
        '''Return an iterator of all the three data types.'''

        data = None
        for data_type in self.DATA_TYPES:
            try:
                data = self.get_single_data_type(data_type=data_type)
            except Exception as e:
                print(e)
            finally:
                yield data

    def _format_splits(self, value):
        '''Format splits to float'''

        if value != 1:
            numbers = value.split('/')
            ratio = int(numbers[0]) / int(numbers[1])
            return ratio
        else:
            return value

    def get_history(self, ticker=None, years=20):
        '''Return quotes, dividends and splits in single Pandas DataFrame
        for the given ticker and specified number of years ending today (or the latest available).
        Defaults to the previously set ticker and 20 years.'''

        self.ticker = ticker or self.ticker
        if self.ticker is None:
            raise Exception('No Ticker')

        self.years = years
        frames = list(self._get_all_data_types())
        try:
            full_data = pd.concat(frames, axis=1)
            full_data['Dividends'].fillna(0, inplace=True)
            full_data['Stock Splits'].fillna(1, inplace=True)
            full_data['Stock Splits'].apply(self._format_splits)
            return full_data
        except Exception as e:
            print(e)
            return pd.DataFrame()
