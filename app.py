import sys
import sqlite3
import requests
import time
import datetime
import plotille as ptl

apiKey = 'bv9418748v6ord6gpe1g'
conn = sqlite3.connect('database.db')
c = conn.cursor()

def printtderr(*a): 
    print(*a, file = sys.stderr) 

def read_from_db(table, params = ''):
    query = "SELECT * FROM " + table + params
    c.execute(query)
    data = c.fetchall()

    return data

def convert_print(symbol, currency):
    params = ' WHERE symbol=' + "'" + str(symbol) + "'"
    currencies = requests.get('https://finnhub.io/api/v1/forex/rates?base=USD&token=' + apiKey).json()
    data = read_from_db('stockHistorical', params)
    val = currencies['quote'].get(currency)
    for row in data:
        print('From USD: ' + str(row[1]) + ' To ' + currency + ': ' + str(row[1] * val))

#convert_print('AAPL', 'AUD')

def latest_stock_quote(asset, change = 'USD'):
    r = requests.get('https://finnhub.io/api/v1/quote?symbol=' + asset + '&token=' + apiKey).json()
    res = r['c'] #current price
    if change is not 'USD':
        currencies = requests.get('https://finnhub.io/api/v1/forex/rates?base=USD&token=' + apiKey).json()
        val = currencies['quote'].get(change)
        res = res * val
    print('Current ' + asset + ' price in ' + str(change) + ': ' + str(res))

#latest_stock_quote('AAPL', 'EUR') #second param is optional

def stock_hist_plot(stock):
    params = ' WHERE symbol=' + "'" + str(stock) + "'"
    data = read_from_db('stockHistorical', params)
    x = list()
    y = list()
    for row in data:
        x.append(row[5])
        y.append(row[1])
    print(ptl.plot(x, y, height=30, width=60))

#hist_plot('AAPL') #graph for input

def unix_conv(timestring):
    result = (time.mktime(datetime.datetime.strptime(timestring, "%d/%m/%Y").timetuple()))
    return result

def hist_plot_time_range(stock, fromtime, totime):
    unixfrom = unix_conv(fromtime)
    unixto = unix_conv(totime)
    params = ' WHERE symbol=' + "'" + str(stock) + "'" + ' AND timestamp BETWEEN ' + str(unixfrom) + ' AND ' + str(unixto)
    data = read_from_db('stockHistorical', params)
    x = list()
    y = list()
    for row in data:
        x.append(row[5])
        y.append(row[1])
    print(ptl.plot(x, y, height=30, width=60))

#hist_plot_time_range('AAPL', '02/11/2020', '15/11/2020')

def exchange_hist_plot(currency):
    params = ' WHERE exchange=' + "'" + str(currency) + "'"
    data = read_from_db('exchangeHistorical', params)
    x = list()
    y = list()
    for row in data:
        x.append(row[6])
        y.append(row[2])
    print(ptl.plot(x, y, height=30, width=60))

#exchange_hist_plot('AUD_USD')

function = [func for func in sys.argv[1:] if func.startswith('-')]
opts = [opt for opt in sys.argv[1:] if not opt.startswith('-')]

if '-convertPrint' in function:
    #convert and print historical stock quotes in any foreign currency 
    try:
        convert_print(opts[0], opts[1]) #params ex: AAPL EUR
    except:
        printtderr('Check documentation, there was a problem trying to use the app')
elif '-latestStockQuote' in function:
    #print latest stock quote for a given asset with the option to apply a currency exchange
    if len(opts) == 2:
        try:
            latest_stock_quote(opts[0], opts[1]) #params ex: AAPL EUR
        except:
            printtderr('Check documentation, there was a problem trying to use the app')
    else:
        latest_stock_quote(opts[0]) #params ex: AAPL
elif '-drawExchangeGraph' in function: 
    #draw a graph based on whole historical data for an exchange from/to currency inputs
    try:
        exchange_hist_plot(opts[0]) #param ex: AUD_USD
    except:
        printtderr('Check documentation, there was a problem trying to use the app')
elif '-drawStockGraph' in function:
    if len(opts) == 3:
        #draw a graph based on time inverval and a stock (close prices)
        try:
            hist_plot_time_range(opts[0], opts[1], opts[2]) #params ex: AAPL 02/11/2020 15/11/2020
        except:
            printtderr('Check documentation, there was a problem trying to use the app')
    else:
        #draw a graph based on whole historical data for a stock (close prices)
        try:
            stock_hist_plot(opts[0]) #params ex: AAPL
        except:
            printtderr('Check documentation, there was a problem trying to use the app')
else:
    printtderr('Check documentation, there was a problem trying to use the app')