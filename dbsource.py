import sqlite3
import requests
import time
import datetime

apiKey = 'apiKey'
conn = sqlite3.connect('database.db')
c = conn.cursor()

#Tables creation
def create_stockAnagraphic():
    c.execute('CREATE TABLE IF NOT EXISTS stockAnagraphic(country TEXT, currency TEXT, exchange TEXT, ipo TEXT, marketCapitalization REAL, name TEXT, phone TEXT, shareOutstanding REAL, ticker TEXT, weburl TEXT, logo TEXT, finnhubIndustry TEXT)')

def create_stockHistorical():
    c.execute('CREATE TABLE IF NOT EXISTS stockHistorical(symbol TEXT, closePrices REAL, highPrices REAL, lowPrices REAL, openPrices REAL, timestamp REAL, volume REAL)')

def create_exchangeAnagraphic():
    c.execute('CREATE TABLE IF NOT EXISTS exchangeAnagraphic(market TEXT, description TEXT, displaySymbol TEXT, symbol TEXT)')

def create_exchangeHistorical():
    c.execute('CREATE TABLE IF NOT EXISTS exchangeHistorical(market TEXT, exchange TEXT, closePrices REAL, highPrices REAL, lowPrices REAL, openPrices REAL, timestamp REAL, volume REAL)')

#Insert's functions
def insert_stockAnagraphic(country, currency, exchange, ipo, marketCapitalization, name, phone, shareOutstanding, ticker, weburl, logo, finnhubIndustry):
    c.execute("INSERT INTO stockAnagraphic (country, currency, exchange, ipo, marketCapitalization, name, phone, shareOutstanding, ticker, weburl, logo, finnhubIndustry) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (country, currency, exchange, ipo, marketCapitalization, name, phone, shareOutstanding, ticker, weburl, logo, finnhubIndustry))
    conn.commit()

def insert_stockHistorical(symbol, closePrices, highPrices, lowPrices, openPrices, timestamp, volume):
    c.execute("INSERT INTO stockHistorical (symbol, closePrices, highPrices, lowPrices, openPrices, timestamp, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (symbol, closePrices, highPrices, lowPrices, openPrices, timestamp, volume))
    conn.commit()

def insert_exchangeAnagraphic(market, description, displaySymbol, symbol):
    c.execute("INSERT INTO exchangeAnagraphic (market, description, displaySymbol, symbol) VALUES (?, ?, ?, ?)",
                (market, description, displaySymbol, symbol))
    conn.commit()

def insert_exchangeHistorical(market, exchange, closePrices, highPrices, lowPrices, openPrices, timestamp, volume):
    c.execute("INSERT INTO exchangeHistorical (market, exchange, closePrices, highPrices, lowPrices, openPrices, timestamp, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (market, exchange, closePrices, highPrices, lowPrices, openPrices, timestamp, volume))
    conn.commit()

#CLI App 

def get_symbols():
    #Symbols block
    r = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token=' + apiKey)
    symbols = list()
    i = 0
    for s in r.json():
        symbols.append(s.get('symbol'))
        i += 1
        if(i == 150): #hard coded 150 symbol limit
            break
    return symbols

def get_stockAnagraphic():  
    symbols = get_symbols()
    #Anagraphic data block (around 2min to complete)
    for symbol in symbols:
        r = requests.get('https://finnhub.io/api/v1/stock/profile2?symbol=' + symbol + '&token=' + apiKey)      
        while r.status_code != 200:
            time.sleep(1) #Workaround required sometimes I'm getting 429 - APIs limit reached 
            r = requests.get('https://finnhub.io/api/v1/stock/profile2?symbol=' + symbol + '&token=' + apiKey)
        r = r.json()
        if len(r) == 12: #Get only companies with complete profile
            insert_stockAnagraphic(r.get('country'), r.get('currency'), r.get('exchange'), r.get('ipo'), r.get('marketCapitalization'), r.get('name'), r.get('phone'), r.get('shareOutstanding'), r.get('ticker'), r.get('weburl'), r.get('logo'), r.get('finnhubIndustry'))
            print('Got anagraphic data for: ' + str(symbol))
    
    c.close()
    conn.close()

#create_stockAnagraphic()
#get_stockAnagraphic()

def get_stockHistorical():
    symbols = get_symbols()
    for symbol in symbols:
        r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + symbol +'&resolution=D&from=1604188800&to=1606694400&token=' + apiKey)
        while r.status_code != 200:
            time.sleep(1)
            r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + symbol +'&resolution=D&from=1604188800&to=1606694400&token=' + apiKey)
        i = 0
        if len(r.json()) == 7:
            for c in r.json()['c']:
                insert_stockHistorical(symbol, c, r.json()['h'][i], r.json()['l'][i], r.json()['o'][i], r.json()['t'][i], r.json()['v'][i])
                i += 1
                print('Got candles data for: ' + str(symbol))
            i += 1

#create_stockHistorical()
#get_stockHistorical()

def get_exchangeAnagraphic():
    r = requests.get('https://finnhub.io/api/v1/forex/exchange?token=' + apiKey).json()
    for mkt in r:
        r = requests.get('https://finnhub.io/api/v1/forex/symbol?exchange='+ mkt +'&token=' + apiKey)
        if r.status_code == 200:
            for x in r.json():
                if(x['displaySymbol'] == 'AUD/USD' or x['displaySymbol'] == 'EUR/USD' or x['displaySymbol'] == 'GBP/USD'):
                    insert_exchangeAnagraphic(mkt, x['description'], x['displaySymbol'], x['symbol'])
                    print('Got exchange data for: ' + str(mkt) + str(x['displaySymbol']))

#create_exchangeAnagraphic()
#get_exchangeAnagraphic()

def get_exchangeHistoric():
    changes = ['AUD_USD', 'EUR_USD', 'GBP_USD']
    for change in changes:
        r = requests.get('https://finnhub.io/api/v1/forex/candle?symbol=' + 'OANDA' + ':' + change + '&resolution=D&from=1604188800&to=1606694400&token=' + apiKey) #OANDA is the only one with data so i decided to hard code it. Even if it's not flexible
        i = 0
        for c in r.json()['c']:
            insert_exchangeHistorical('OANDA', change, c, r.json()['h'][i], r.json()['l'][i], r.json()['o'][i], r.json()['t'][i], r.json()['v'][i])
            i += 1
            print('Got candles data for: ' + str(change))

#create_exchangeHistorical()
#get_exchangeHistoric()
