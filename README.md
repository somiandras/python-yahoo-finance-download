# Download data from Yahoo Finance API

Get quote, dividend and split history for a given ticker symbol from a specified starting date to today.

Inspired by __c0redumb's__ [yahoo_quote_download](https://github.com/c0redumb/yahoo_quote_download) and __rubenafo's__ [YahooFetcher](https://github.com/rubenafo/YahooFetcher), but implemented using [requests](http://docs.python-requests.org/en/master/) for fetching data, and returning Pandas dataframes.

### New Yahoo API
Yahoo Finance changed how their stock data API works as of May, 2017. The data is still available on Yahoo Finance pages, but the new API uses authentication via a cookie and a 'crumb'. This module obtains these with an initial request and uses them for the subsequent requests.

For the Yahoo Finance API changes read __c0redumb's__ [description](https://github.com/c0redumb/yahoo_quote_download).

## Class

__Downloader()__

``` python
from yahoo_downloader import Downloader

downloader = Downloader()

```

## Methods

#### downloader.get_history(ticker, years=20)

Returns quotes, dividends and splits in single Pandas DataFrame for the given ticker and specified number of years ending today (or the latest available).

Splits are filled with 1s between split dates and dividends filled with 0s between ex-dividend dates (as in the Quandl Python API) to make further adjustments easier. No other transformations are made on Yahoo Finance data.

**Note:** Dividends are adjusted with splits, but adjusted close is not adjusted by dividends... Better do adjusting yourself.

#### downloader.settings()

Return the currently set ticker and year range in `(ticker, years)` tuple.

## Example

``` python
from yahoo_downloader import Downloader

downloader = Downloader()

# Full data:
df = downloader.get_history('MSFT', years=10)

# Check settings:
settings = downloader.settings()
print(settings)

>>> ('MSFT', 10)

print(df.info())

<class 'pandas.core.frame.DataFrame'>
Index: 2518 entries, '2007-06-08' to '2017-06-07'
Data columns (total 8 columns):
Open            2518 non-null float64
High            2518 non-null float64
Low             2518 non-null float64
Close           2518 non-null float64
Adj Close       2518 non-null float64
Volume          2518 non-null int64
Dividends       2518 non-null float64
Stock Splits    2518 non-null int64
dtypes: float64(6), int64(2)
memory usage: 177.0+ KB
```
