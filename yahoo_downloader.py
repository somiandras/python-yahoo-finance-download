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


def get_single_data_type(ticker, data_type, start_date=default_start_date):
    '''Returns a dataframe for the specified data type [history|div|split] from the specified start date.
    Start date has to be a datetime object. Defaults to 20 years before today.'''
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
    elif r.status_code == 404:
        raise Exception('Not Found')
    elif r.status_code == 401:
        raise Exception('Authorization Error')
    else:
        r.raise_for_status()


def _get_all_data_types(ticker, start_date):
    '''Returns an iterator of all the three data types. Start date has to be a datetime object.'''
    if _cookie is None or _crumb is None:
        _get_crumb_and_cookies()

    data = None
    for data_type in DATA_TYPES:
        try:
            data = get_single_data_type(ticker, data_type, start_date)
        except Exception as e:
            # In case of occasional authorization error sleep for a while, renew crumb and cookie and fetch data again. 
            # See the issue here: https://github.com/c0redumb/yahoo_quote_download/issues/3
            if e == 'Authorization Error':
                sleep(1)
                _get_crumb_and_cookies()
                data = get_single_data_type(ticker, data_type, start_date)
            else:
                print(e)
        else:
            yield data


def _format_splits(value):
    '''Format x/y splits to float'''
    if value != 1:
        numbers = value.split('/')
        ratio = int(numbers[0]) / int(numbers[1])
        return ratio


def get_history(ticker, start_date=default_start_date):
    '''Returns quotes, dividends and splits in one Pandas DataFrame. Start date
    has to be a datetime object. Defaults to 20 years before today.'''
    frames = list(_get_all_data_types(ticker, start_date))
    try:
        full_data = pd.concat(frames, axis=1)
        full_data['Dividends'].fillna(0, inplace=True)
        full_data['Stock Splits'].fillna(1, inplace=True)
        full_data['Stock Splits'].apply(_format_splits)
        return full_data
    except Exception as e:
        print(e)
        return pd.DataFrame()
