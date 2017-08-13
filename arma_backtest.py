#!/usr/bin/python

import datetime
import numpy as np
from statsmodels.tsa.arima_model import ARMA

from zipline import run_algorithm
from zipline.api import order_target_percent, symbol, schedule_function, date_rules, time_rules, get_environment

zipline_logging= logbook.NestedSetup([logbook.NullHandler(level=logbook.DEBUG),logbook.StreamHandler(sys.stdout,level=logbook.INFO),logbook.StreamHandler(sys.stderr,level=logbook.ERROR),])
zipline_logging.push_application()

def initialize(context):

	context.tickers = ['AYI','APA','AMZN','LNT','CTL','ALB','ABBV','AMT','ADM','AON','ORCL']
	context.tickers = [ symbol(x) for x in context.tickers ]
	schedule_function(place_orders, data_rules.every_day())
	context.days = int()

def before_trading_start(context,data):

	close = list()
	for tick in context.tickers:
		close.append(data.history(tick,'close',50+context.days,'1d'))
	context.days += 1
	sec_list = SecurityList(data=close)
	ts = sec_list.genTimeSeries()
	model = ARMA(ts, order = (5,0))
	model_fit = model.fit(disp=0)
	output = model_fit.forecast()
	context.predicted = output[0]
