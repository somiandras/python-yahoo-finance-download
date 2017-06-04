# Download data from Yahoo Finance

Yahoo Finance changed how their stock data API works as of May, 2017. The data is still available on Yahoo Finance pages, but the new API uses authorization via a cookie and a 'crumb'. This module obtains these with an initial request and uses them for the subsequent requests.

This was heavily influenced by __c0redumb's__ [yahoo_quote_download](https://github.com/c0redumb/yahoo_quote_download). In fact, the logic is quite similar using a slightly different way just for fun and learning purposes.

For the Yahoo Finance API changes read __c0redumb's__ [description](https://github.com/c0redumb/yahoo_quote_download). 

#### get_series(ticker, data_type[, start_date])

Returns the csv data for the specified data type (history, div or split) from the specified start date. Start date has to be a datetime object, it defaults to 20 years before today.

#### get_all_data(ticker[, start_date])

Returns an iterator of all the three data types. Start date has to be a datetime object, it defaults to 20 years before today.

Any comments and suggestions are welcome.

MIT License

Copyright (c) [2017] [Andras Somi]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
