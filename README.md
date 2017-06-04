# Download data from Yahoo Finance

Yahoo Finance changed how their stock data API works as of May, 2017. The data is still available on Yahoo Finance pages, but the new API uses authorization via a cookie and a 'crumb'. This module obtains these with an initial request and uses them for the subsequent requests.

This was heavily influenced by __c0redumb's__ [yahoo_quote_download](https://github.com/c0redumb/yahoo_quote_download). In fact, the logic is quite similar using a slightly different way just for fun and learning purposes.

For the Yahoo Finance API changes read __c0redumb's__ [description](https://github.com/c0redumb/yahoo_quote_download). 

#### get_series(ticker, data_type, start_date)

Returns the csv data for the specified data type (history, div or split) from the specified start date. Start date has to be a datetime object.

#### get_all_data(ticker[, start_date])

Returns an iterator of all the three data types. Start date has to be a datetime object, defaults to same day 20 years before.

Any comments and suggestions are welcome.