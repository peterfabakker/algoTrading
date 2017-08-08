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
import quandl

from johansen.johansen import Johansen
start_time= time.time()

outFile= open(sys.argv[1],"w")

np.set_printoptions(threshold='nan')

quandl.ApiConfig.api_key = 'AfS6bPzj1CsRFyYxCcvz'

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
            for i in range(len(ticker)):
               if ticker[i] == '.':
                  new = ticker[:i]+'_'+ticker[(i+1):]
                  ticker = new
            if sector not in sector_tickers:
                sector_tickers[sector] = list()
            sector_tickers[sector].append(ticker)
    return sector_tickers

def test_stocks():

	start = datetime.datetime(1990,1,1)
	end = datetime.datetime.now()
	
	tickers= scrape_list('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')

	for a in range(1,len(tickers.items()[0][1])):
		a1 = quandl.get('WIKI/'+tickers.items()[0][1][a], returns="numpy",start_date=start,end_date=end)
		for b in range(1,len(tickers.items()[1][1])):
			a2 = quandl.get('WIKI/'+tickers.items()[1][1][b], returns="numpy",start_date=start,end_date=end)
			for c in range(1,len(tickers.items()[2][1])):
				a3 = quandl.get('WIKI/'+tickers.items()[2][1][c], returns="numpy",start_date=start,end_date=end)
				for d in range(1,len(tickers.items()[3][1])):
					a4 = quandl.get('WIKI/'+tickers.items()[3][1][d], returns="numpy",start_date=start,end_date=end)
					for e in range(1,len(tickers.items()[4][1])):
						a5 = quandl.get('WIKI/'+tickers.items()[4][1][e], returns="numpy",start_date=start,end_date=end)
						for f in range(1,len(tickers.items()[5][1])):
							a6 = quandl.get('WIKI/'+tickers.items()[5][1][f], returns="numpy",start_date=start,end_date=end)
							for g in range(1,len(tickers.items()[6][1])):
								a7 = quandl.get('WIKI/'+tickers.items()[6][1][g], returns="numpy",start_date=start,end_date=end)
								for h in range(1,len(tickers.items()[7][1])):
									a8 = quandl.get('WIKI/'+tickers.items()[7][1][h], returns="numpy",start_date=start,end_date=end)
									for i in range(1,len(tickers.items()[8][1])):
										a9 = quandl.get('WIKI/'+tickers.items()[8][1][i], returns="numpy",start_date=start,end_date=end)
										for j in range(1,len(tickers.items()[9][1])):
											a10 = quandl.get('WIKI/'+tickers.items()[9][1][j],returns="numpy", start_date=start,end_date=end)
											for k in range(1,len(tickers.items()[10][1])):
												#while True:
													#try:
															a11 = quandl.get('WIKI/'+tickers.items()[10][1][k],returns="numpy", start_date=start,end_date=end)
															s1 = a1['Adj. Close']
															s2 = a2['Adj. Close']
															s3 = a3['Adj. Close']
															s4 = a4['Adj. Close']
															s5 = a5['Adj. Close']
															s6 = a6['Adj. Close']
															s7 = a7['Adj. Close']
															s8 = a8['Adj. Close']
															s9 = a9['Adj. Close']
															s10 = a10['Adj. Close']
															s11 = a11['Adj. Close']
															if len(s1) == len(s2) == len(s3) == len(s4) == len(s5) == len(s6) == len(s7) == len(s8) == len(s9) == len(s10) == len(s11):
																outFile.write('Start = '+str(start)+'\n End = '+str(end)+'\n')
															else:
																arr = [len(s1),len(s2),len(s3),len(s4),len(s5),len(s6),len(s7),len(s8),len(s9),len(s10),len(s11)]
																mini = min(arr)
																mini = mini*-1
																if len(s1) > mini:
																	s1 = s1[mini:]
																if len(s2) > mini:
																	s2 = s2[mini:]
																if len(s3) > mini:
																	s3 = s3[mini:]
																if len(s4) > mini:
																	s4 = s4[mini:]
																if len(s5) > mini:
																	s5 = s5[mini:]
																if len(s6) > mini:
																	s6 = s6[mini:]
																if len(s7) > mini:
																	s7 = s7[mini:]
																if len(s8) > mini:
																	s8 = s8[mini:]
																if len(s9) > mini:
																	s9 = s9[mini:]
																if len(s10) > mini:
																	s10 = s10[mini:]
																if len(s11) > mini:
																	s11 = s11[mini:]
																outFile.write('Start = '+str(a1['Date'][mini])+'\n End = '+str(end)+'\n')
																	
															s = np.array([s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11])
															outFile.write('Johansen Test \n')
															outFile.write(tickers.items()[0][1][a]+' '+
																      tickers.items()[1][1][b]+' '+
																      tickers.items()[2][1][c]+' '+
																      tickers.items()[3][1][d]+' '+
																      tickers.items()[4][1][e]+' '+
																      tickers.items()[5][1][f]+' '+
																      tickers.items()[6][1][g]+' '+
																      tickers.items()[7][1][h]+' '+
																      tickers.items()[8][1][i]+' '+
																      tickers.items()[9][1][j]+' '+
																      tickers.items()[10][1][k]+'\n')
															matrix = np.column_stack((s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11))
															size = matrix.size
															matrix_centered = matrix - np.mean(matrix,axis=0)
															result = jh.coint_johansen(matrix_centered,0,1)
															outFile.write('eigenvalues: '+str(result.eig)+'\n')
															outFile.write('eigenvectors: '+str(result.evec)+'\n')
															outFile.write('trace statistic: '+str(result.lr1)+'\n')
															outFile.write('max eig stat: '+str(result.lr2)+'\n')
															outFile.write('critical value trace: '+str(result.cvt)+'\n')
															outFile.write('critical value eig: '+str(result.cvm)+'\n')
															
															df = pd.DataFrame(index=a1['Date'][mini:])
															df["res"] = np.dot(result.evec[:,0],s)

															cadf = ts.adfuller(df["res"])
															outFile.write('Augemented Dickey Fuller Test \n')
															outFile.write('test statistic: '+str(cadf[0])+'\n p value: '+str(cadf[1])+'\n critical values: '+str(cadf[4])+'\n')
															outFile.write('Hurst exponent: '+str(hurst(df['res']))+'\n\n')
														#except (requests.ConnectionError, requests.exceptions.ChunkedEncodingError, requests.exceptions.ContentDecodingError, ValueError) as z:
														#	print(z)
#														else:
#															break
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
