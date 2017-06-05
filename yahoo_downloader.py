# -*- coding: utf-8 -*-

'''Data downloader for Yahoo Finance, inspired by https://github.com/c0redumb/yahoo_quote_download'''

import requests
import re
from datetime import datetime
import json
from time import sleep
import pandas as pd
import io

DATA_TYPES = ['history', 'div', 'split']
default_start_date = datetime.today().replace(year=datetime.today().year - 20)

_cookie = None
_crumb = None


def _get_crumb_and_cookies():
    '''Make an initial request to extract cookies and crumb to use in subsequent requests'''
    global _crumb
    global _cookie
    url = 'https://finance.yahoo.com/quote/^GSPC'
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        _cookie = r.cookies
        search = re.search('\"CrumbStore\"\:\{\"crumb\"\:\"(.*)\"\}\,\"QuotePageStore\"', r.text)
        if search is None:
            raise Exception('No crumb in initial response')
        else:
            _crumb = search.group(1)
    else:
        r.raise_for_status()


def get_series(ticker, data_type, start_date):
    '''Returns the csv data for the specified data type (history, div or split)
    from the specified start date. Start date has to be a datetime object.'''
    params = {
        'period1': int(start_date.timestamp()),
        'period2': int(datetime.today().timestamp()),
        'events': data_type,
        'crumb': _crumb,
        'interval': '1d'
    }
    url = 'https://query1.finance.yahoo.com/v7/finance/download/{}'.format(ticker)
    r = requests.get(url, params=params, cookies=_cookie)
    if r.status_code == requests.codes.ok:
        df = pd.read_csv(io.BytesIO(r.content))
        df.set_index('Date', inplace=True)
        return df
    else:
        raise Exception(r.text)


def get_all_data(ticker, start_date=default_start_date):
    '''Returns an iterator of all the three data types. Start date has to be
    a datetime object, defaults to same day 20 years before.'''
    if _cookie is None or _crumb is None:
        _get_crumb_and_cookies()
    data = None
    for data_type in DATA_TYPES:
        try:
            data = get_series(ticker, data_type, start_date)
        except Exception as e:
            exc = json.loads(str(e))
            # In case of occasional authorization error sleep for a while, renew crumb and cookie 
            # and fetch data. See the issue here: https://github.com/c0redumb/yahoo_quote_download/issues/3
            if 'finance' in exc:
                sleep(0.5)
                _get_crumb_and_cookies()
                data = get_series(ticker, data_type, start_date)
            # Handle missing ticker error
            elif 'chart' in exc and exc['chart']['error']['code'] == 'Not Found':
                desc = exc['chart']['error']['description']
                print('{} {}: {}'.format(ticker, data_type, desc))
                data = None
        else:
            yield data
