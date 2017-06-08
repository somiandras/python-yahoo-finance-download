# -*- coding: utf-8 -*-

'''Data downloader for Yahoo Finance, inspired by https://github.com/c0redumb/yahoo_quote_download'''

import requests
import re
from datetime import datetime
from time import sleep
import pandas as pd
import io


class Downloader:
    def __init__(self, ticker=None):
        self.ticker = ticker
        self.DATA_TYPES = ['history', 'div', 'split']
        self._cookie = None
        self._crumb = None
        self._START = datetime.today().replace(year=datetime.today().year - 20)
        self.attempt_counter = 0

    def set_ticker(self, ticker):
        self.ticker = ticker
        return self

    def _get_crumb_and_cookies(self):
        '''Make an initial request to extract cookies and crumb to use in subsequent requests'''
        url = 'https://finance.yahoo.com/quote/^GSPC'
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            self._cookie = r.cookies
            search = re.search('\"CrumbStore\"\:\{\"crumb\"\:\"(.*)\"\}\,\"QuotePageStore\"', r.text)
            if search is None:
                raise Exception('No crumb in initial response')
            else:
                self._crumb = search.group(1)
        else:
            r.raise_for_status()

    def get_single_data_type(self, ticker, data_type, start_date=None):
        '''Returns a dataframe for the specified data type [history|div|split] from the specified start date.
        Start date has to be a datetime object. Defaults to 20 years before today.'''
        if self._cookie is None or self._crumb is None:
            self._get_crumb_and_cookies()

        self.attempt_counter += 1

        start_date = start_date or self._START
        params = {
            'period1': int(start_date.timestamp()),
            'period2': int(datetime.today().timestamp()),
            'events': data_type,
            'crumb': self._crumb,
            'interval': '1d'
        }
        url = 'https://query1.finance.yahoo.com/v7/finance/download/{}'.format(ticker)
        r = requests.get(url, params=params, cookies=self._cookie)
        if r.status_code == requests.codes.ok:
            df = pd.read_csv(io.BytesIO(r.content))
            df.set_index('Date', inplace=True)
            self.attempt_counter = 0
            return df
        elif r.status_code == 404:
            raise Exception('Not Found')
        elif r.status_code == 401:
            # In case of occasional authorization error renew crumb and cookie and fetch data again. Max. 10 attempts.
            # See the issue here: https://github.com/c0redumb/yahoo_quote_download/issues/3
            self._crumb = None
            self._cookie = None

            if self.attempt_counter < 10:
                print('Auth error, retrying...')
                return self.get_single_data_type(ticker, data_type, start_date=None)
            else:
                raise Exception('Permanent Auth Error')
        else:
            r.raise_for_status()

    def _get_all_data_types(self, ticker, start_date):
        '''Returns an iterator of all the three data types. Start date has to be a datetime object.'''
        data = None
        for data_type in self.DATA_TYPES:
            try:
                data = self.get_single_data_type(ticker, data_type, start_date)
            except Exception as e:
                print(e)

            yield data

    def _format_splits(self, value):
        '''Format x/y splits to float'''
        if value != 1:
            numbers = value.split('/')
            ratio = int(numbers[0]) / int(numbers[1])
            return ratio

    def get_history(self, ticker=None, start_date=None):
        '''Returns quotes, dividends and splits in single Pandas DataFrame. Start date
        has to be a datetime object. Defaults to 20 years before today.'''
        self.ticker = ticker
        if self.ticker is None:
            raise Exception('No Ticker')
        start_date = start_date or self._START
        frames = list(self._get_all_data_types(self.ticker, start_date))
        try:
            full_data = pd.concat(frames, axis=1)
            full_data['Dividends'].fillna(0, inplace=True)
            full_data['Stock Splits'].fillna(1, inplace=True)
            full_data['Stock Splits'].apply(self._format_splits)
            return full_data
        except Exception as e:
            print(e)
            return pd.DataFrame()
