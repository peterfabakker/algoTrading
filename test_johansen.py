#!/usr/bin/python

# USAGE: result = johansen(x,p,k)
# where:      x = input matrix of time-series in levels, (nobs x m)
#             p = order of time polynomial in the null-hypothesis
#                 p = -1, no deterministic part
#                 p =  0, for constant term
#                 p =  1, for constant plus time-trend
#                 p >  1, for higher order polynomial
#             k = number of lagged difference terms used when
#                 computing the estimator
# -------------------------------------------------------
# RETURNS: a results structure:
#          result.eig  = eigenvalues  (m x 1)
#          result.evec = eigenvectors (m x m), where first
#                        r columns are normalized coint vectors
#          result.lr1  = likelihood ratio trace statistic for r=0 to m-1
#                        (m x 1) vector
#          result.lr2  = maximum eigenvalue statistic for r=0 to m-1
#                        (m x 1) vector
#          result.cvt  = critical values for trace statistic
#                        (m x 3) vector [90% 95% 99%]
#          result.cvm  = critical values for max eigen value statistic
#                        (m x 3) vector [90% 95% 99%]
#          result.ind  = index of co-integrating variables ordered by
#                        size of the eigenvalues from large to small


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
import time
import sys
import statsmodels.tsa.johansen as jh
import quandl

from johansen.johansen import Johansen

def test_stocks():
	start = datetime.datetime(2013,1,2)
	end = datetime.datetime(2017,6,22)
	
	quandl.ApiConfig.api_key = 'AfS6bPzj1CsRFyYxCcvz'

	s1 = quandl.get('WIKI/AYI', returns="numpy",start_date=start,end_date=end)
	s2 = quandl.get('WIKI/APA', returns="numpy",start_date=start,end_date=end)
	s3 = quandl.get('WIKI/AMZN', returns="numpy",start_date=start,end_date=end)
	s4 = quandl.get('WIKI/LNT', returns="numpy",start_date=start,end_date=end)
	s5 = quandl.get('WIKI/CTL', returns="numpy",start_date=start,end_date=end)
	s6 = quandl.get('WIKI/ALB', returns="numpy",start_date=start,end_date=end)
	s7 = quandl.get('WIKI/ABBV', returns="numpy",start_date=start,end_date=end)
	s8 = quandl.get('WIKI/AMT', returns="numpy",start_date=start,end_date=end)
	s9 = quandl.get('WIKI/ADM', returns="numpy",start_date=start,end_date=end)
	s10 = quandl.get('WIKI/AON', returns="numpy",start_date=start,end_date=end)
	s11 = quandl.get('WIKI/ORCL', returns="numpy",start_date=start,end_date=end)

	s1 = s1['Adj. Close']
	s2 = s2['Adj. Close']
	s3 = s3['Adj. Close']
	s4 = s4['Adj. Close']
	s5 = s5['Adj. Close']
	s6 = s6['Adj. Close']
	s7 = s7['Adj. Close']
	s8 = s8['Adj. Close']
	s9 = s9['Adj. Close']
	s10 = s10['Adj. Close']
	s11 = s11['Adj. Close']

	s = np.array([s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11])
	matrix = np.column_stack((s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11))
	matrix_centered = matrix - np.mean(matrix,axis=0)
	#johansen = Johansen(matrix_centered, model = 0,significance_level=0)
	#eigenvectors, r = johansen.johansen()
	#print "r values are: {}".format(r)
	#vec = eigenvectors[:, 0]
	#vec_min = np.min(np.abs(vec))
	#vec = vec / vec_min
	#print "The first cointegrating relation: {}".format(vec)
	result = jh.coint_johansen(matrix_centered,0,1)
	#print(result.eig)
	#print(result.evec)
	#print(result.lr1)
	#print(result.lr2)
	#print(result.cvt)
	#print(result.cvm)
	#print(result.ind)
	return(result.evec[:,0])
	
	#df = pd.DataFrame(index=s1.index)
	#df["res"] = np.dot(result.evec[:,0],s)

	# Plot the residuals
	#plot_residuals(df,start,end)

	# Calculate and output the CADF test on the residuals
	#cadf = ts.adfuller(df["res"])
	#pprint.pprint(cadf)
	#print(hurst(df['res']))

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

def hurst(ts):
	"""Returns the Hurst Exponent of the time series vector ts"""
	# Create the range of lag values
	lags = range(2, 100)

	# Calculate the array of the variances of the lagged differences
	tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]

	# Use a linear fit to estimate the Hurst Exponent
	poly = np.polyfit(np.log(lags), np.log(tau), 1)

	# Return the Hurst exponent from the polyfit output
	return poly[0]*2.0

if __name__== "__main__":
	test_stocks()
