#!/usr/bin/python

import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pandas_datareader.data as web
import pprint
import statsmodels.tsa.stattools as ts
import urllib2
from bs4 import BeautifulSoup
from pandas.stats.api import ols
import time
import sys
start_time= time.time()

outFile= open(sys.argv[1],"w")

def scrape_list(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site, headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page,'html5lib')

    table = soup.find('table', {'class': 'wikitable sortable'})
    sector_tickers = dict()
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            sector = str(col[3].string.strip()).lower().replace(' ', '_')
            ticker = str(col[0].string.strip())
            if sector not in sector_tickers:
                sector_tickers[sector] = list()
            sector_tickers[sector].append(ticker)
    return sector_tickers


def test_stocks():
	start = datetime.datetime(1990,1,1)
	end = datetime.datetime.today()
	
	tickers= scrape_list('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')

	done=dict()

	for key, obj in tickers.items():
		for i in range(0,len(obj)-1):
			for j in range(i+1,len(obj)):
					
				try:

					gld = web.DataReader(obj[i], "yahoo", start, end)
					gdx = web.DataReader(obj[j], "yahoo", start, end)

					df = pd.DataFrame(index=gld.index)
					df[obj[i]] = gld["Adj Close"]
					df[obj[j]] = gdx["Adj Close"]

					# Plot the two time series
					#plot_price_series(df, obj[i], obj[j])

					# Display a scatter plot of the two time series
					#plot_scatter_series(df, obj[i], obj[j])

					# Calculate optimal hedge ratio "beta"
					res = ols(y=df[obj[i]], x=df[obj[j]])
					beta_hr = res.beta.x

					# Calculate the residuals of the linear combination
					df["res"] = df[obj[i]] - beta_hr*df[obj[j]]

					# Plot the residuals
					#plot_residuals(df)

					# Calculate and output the CADF test on the residuals
					cadf = ts.adfuller(df["res"])
					outFile.write(obj[i]+' and '+obj[j]+'\n'+str(cadf[0])+'\n'+str(cadf[4])+'\n\n')
					#pprint.pprint(cadf)

				except:
					pass

def plot_price_series(df, ts1, ts2):
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.plot(df.index, df[ts1], label=ts1)
    ax.plot(df.index, df[ts2], label=ts2)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1))
    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel('Month/Year')
    plt.ylabel('Price ($)')
    plt.title('%s and %s Daily Prices' % (ts1, ts2))
    plt.legend()
    plt.show()

def plot_scatter_series(df, ts1, ts2):
	plt.xlabel('%s Price ($)' % ts1)
	plt.ylabel('%s Price ($)' % ts2)
	plt.title('%s and %s Price Scatterplot' % (ts1, ts2))
	plt.scatter(df[ts1], df[ts2])
	plt.show()

def plot_residuals(df):
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.plot(df.index, df["res"], label="Residuals")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1))
    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel('Month/Year')
    plt.ylabel('Price ($)')
    plt.title('Residual Plot')
    plt.legend()

    plt.plot(df["res"])
    plt.show()

if __name__== "__main__":
	test_stocks()
	print('Ran for',time.time()-start_time)
