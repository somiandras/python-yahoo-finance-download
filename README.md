# Download data from Yahoo Finance API

Get quote, dividend and split history for a given ticker symbol from a specified starting date to today.

Influenced by __c0redumb's__ [yahoo_quote_download](https://github.com/c0redumb/yahoo_quote_download), but implemented using [requests](http://docs.python-requests.org/en/master/) instead of urllib methods. Functions return Pandas dataframes.

## New Yahoo API
Yahoo Finance changed how their stock data API works as of May, 2017. The data is still available on Yahoo Finance pages, but the new API uses authentication via a cookie and a 'crumb'. This module obtains these with an initial request and uses them for the subsequent requests.

For the Yahoo Finance API changes read __c0redumb's__ [description](https://github.com/c0redumb/yahoo_quote_download).

## Functions

#### get_single_data_type(ticker, data_type[, start_date]):

Returns a dataframe for the specified data type [history|div|split] from the specified start date. Start date has to be a datetime object. Defaults to 20 years before today. Data is unchanged from what Yahoo Finance returns.

#### get_history(ticker[, start_date])

Returns quotes, dividends and splits in one Pandas DataFrame. Start date has to be a datetime object. Defaults to 20 years before today. Splits filled with 1, dividends with 0 for calculation, otherwise the data is unchanged from what Yahoo Finance returns.

### Example

``` python
from yahoo_downloader import get_history
import datetime

start_date = datetime.datetime(2000, 1, 1)
df = get_history('AAPL', start_date)
print(df.info())

<class 'pandas.core.frame.DataFrame'>
Index: 4382 entries, 2000-01-03 to 2017-06-02
Data columns (total 8 columns):
Open            4382 non-null float64
High            4382 non-null float64
Low             4382 non-null float64
Close           4382 non-null float64
Adj Close       4382 non-null float64
Volume          4382 non-null int64
Dividends       4382 non-null float64
Stock Splits    4382 non-null object
dtypes: float64(6), int64(1), object(1)
memory usage: 308.1+ KB
```