#!/usr/bin/python

import quandl
import numpy as np
import pandas as pd
import datetime
import statsmodels.tsa.johansen as jh
import matplotlib.pyplot as plt

quandl.ApiConfig.api_key = 'AfS6bPzj1CsRFyYxCcvz'

class SecurityList():

    def __init__(self,tickers):
            self.tickers = tickers
            self.data = pd.DataFrame(columns=self.tickers)
            self.volume = pd.DataFrame(columns=self.tickers)

    def downloadQuandl(self,start,end):
                
        def convert_dt(elem):
            return pd.to_datetime(elem).date()
        for sec in self.tickers:
            a = quandl.get('WIKI/'+sec, start_date=start,end_date=end)
            self.data[sec] = a['Adj. Close']
            self.volume[sec] = a['Volume']
            f = np.vectorize(convert_dt)
            index = f(a.index)
        self.data = self.data.set_index(index)
        self.volume = self.volume.set_index(index)
        
    def genTimeSeries(self):

        '''
        Generate Time Series using johansen test
        '''
        eig = self.genHedgeRatio()
        ts = np.dot(self.data,eig)
        return ts,eig,self.data

    def genHedgeRatio(self):
                    
        matrix = self.genMatrix()
        results = jh.coint_johansen(matrix,0,1)
        return results.evec[:,0]
        
    def genMatrix(self):

        ts_row,ts_col = self.data.shape
        matrix = np.zeros((ts_row,ts_col))
        for i, sec in enumerate(self.data):
            matrix[:,i] = self.data[sec]
        return matrix

    def getVolume(self):
        return self.volume
