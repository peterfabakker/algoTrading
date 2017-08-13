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
from pandas.stats.api import ols
import time
import sys
import statsmodels.tsa.johansen as jh
import requests

from johansen.johansen import Johansen
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
		for i in range(0,len(obj)-2):
			for j in range(i+1,len(obj)-1):
				for k in range(j+1,len(obj)):
					while True:
						try:
							s1 = web.DataReader(obj[i], "yahoo", start, end)
							s2 = web.DataReader(obj[j], "yahoo", start, end)
							s3 = web.DataReader(obj[k], "yahoo", start,end)
						except (requests.ConnectionError, requests.exceptions.ChunkedEncodingError):
							print 'Connection Error'
						else:
							break
					s1 = s1['Adj Close']
					s2 = s2['Adj Close']
					s3 = s3['Adj Close']
					if len(s1) == len(s2) == len(s3):
						outFile.write('Start = '+str(start)+'\n End = '+str(end)+'\n')
					else:
						arr = [len(s1),len(s2),len(s3)]
						mini = min(arr)
						mini = mini*-1
						if len(s1) > mini:
							s1 = s1[mini:]
						if len(s2) > mini:
							s2 = s2[mini:]
						if len(s3) > mini:
							s3 = s3[mini:]
						outFile.write('Start = '+str(s1.index[0])+'\n End = '+str(end)+'\n')
							
					s = np.array([s1,s2,s3])
					outFile.write('Johansen Test \n')
					outFile.write(obj[i]+' and '+obj[j]+' and '+obj[k]+'\n')
					matrix = np.column_stack((s1,s2,s3))
					matrix_centered = matrix - np.mean(matrix,axis=0)
					result = jh.coint_johansen(matrix_centered,0,1)
					outFile.write('eigenvalues: '+str(result.eig)+'\n')
					outFile.write('eigenvectors: '+str(result.evec)+'\n')
					outFile.write('trace statistic: '+str(result.lr1)+'\n')
					outFile.write('max eig stat: '+str(result.lr2)+'\n')
					outFile.write('critical value trace: '+str(result.cvt)+'\n')
					outFile.write('critical value eig: '+str(result.cvm)+'\n')
					
					df = pd.DataFrame(index=s1.index)
					df["res"] = np.dot(result.evec[:,0],s)

					cadf = ts.adfuller(df["res"])
					outFile.write('Augemented Dickey Fuller Test \n')
					outFile.write(obj[i]+' and '+obj[j]+' and '+obj[k]+'\n test statistic: '+str(cadf[0])+'\n p value: '+str(cadf[1])+'\n critical values: '+str(cadf[4])+'\n')
					outFile.write('Hurst exponent: '+str(hurst(df['res']))+'\n\n')


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
	outFile.write('Ran for '+str(time.time() - start_time))
