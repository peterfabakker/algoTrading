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
import pytz


def test_stocks():
	start = datetime.datetime(1994,9,29)
	end = datetime.datetime(2017,4,5,0,0,0,0,pytz.utc)
	

	gld = web.DataReader('MMM', "yahoo", start, end)
	gdx = web.DataReader('BA', "yahoo", start, end)

	df = pd.DataFrame(index=gld.index)
	df['MMM'] = gld["Adj Close"]
	df['BA'] = gdx["Adj Close"]

	# Plot the two time series
	#plot_price_series(df, 'MMM', 'BA',start,end)

	# Display a scatter plot of the two time series
	#plot_scatter_series(df, 'MMM', 'BA')

	# Calculate optimal hedge ratio "beta"
	res = ols(y=df['MMM'], x=df['BA'])
	beta_hr = res.beta.x
	return beta_hr

	# Calculate the residuals of the linear combination
	df["res"] = df['MMM'] - beta_hr*df['BA']

	# Plot the residuals
	#plot_residuals(df,start,end)

	# Calculate and output the CADF test on the residuals
	cadf = ts.adfuller(df["res"])
	#pprint.pprint(cadf)
	#print(beta_hr)


def plot_price_series(df, ts1, ts2,start,end):
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.plot(df.index, df[ts1], label=ts1)
    ax.plot(df.index, df[ts2], label=ts2)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(start, end)
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

def plot_residuals(df,start,end):
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.plot(df.index, df["res"], label="Residuals")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(start, end)
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
