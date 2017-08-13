#!/usr/bin/python

import quandl
import numpy as np
import statsmodels.tsa.johansen as jh

quandl.ApiConfig.api_key = 'AfS6bPzj1CsRFyYxCcvz'

class SecurityList():

	def __init__(self,tickers=None,data=list()):
		self.tickers = tickers
		self.data = data

	def downloadQuandl(self,start,end):

		for sec in self.tickers:
			a = quandl.get('WIKI/'+sec, returns="numpy",start_date=start,end_date=end)
			self.data.append(a['Adj. Close'])

	def genTimeSeries(self):

		'''
		Generate Time Series using johansen test
		'''
		ts_length = len(self.data[0])
		matrix = np.zeros((ts_length,len(self.tickers)))
		for i,sec in enumerate(self.data):
			matrix[:,i] = sec
		results = jh.coint_johansen(matrix,0,1)
		ts = np.dot(matrix,results.evec[:,0])
		return ts
