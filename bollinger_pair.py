#!/usr/bin/python

import pyfolio as pf
import numpy as np
import pandas as pd
import sys
import subprocess
import logbook
import pytz
import datetime
import matplotlib.pyplot as plt

zipline_logging= logbook.NestedSetup([logbook.NullHandler(level=logbook.DEBUG),logbook.StreamHandler(sys.stdout,level=logbook.INFO),logbook.StreamHandler(sys.stderr,level=logbook.ERROR),])
zipline_logging.push_application()

from zipline.data.bundles import register,ingest,yahoo_equities
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol, schedule_function, date_rules, time_rules, get_environment

process= subprocess.check_output(['python','/home/sowen/algorithmic_trading/zipline/zipline/algorithms/adf.py'])

beta_hr= float(process)


def initialize(context):
	context.long= symbol('GWW')
	context.short= symbol('PCAR')
	
	context.stocks= [context.long,context.short]

	context.amlong= False
	context.amshort= False
	context.wait= False
	context.days=0	

	schedule_function(place_orders, date_rules.every_day(), time_rules.market_open(hours=1,minutes=30))
	schedule_function(stop_loss,date_rules.every_day(), time_rules.every_minute())

def before_trading_start(context,data):

	shortclose= data.history(context.short,'close',20,'1d')
	longclose= data.history(context.long,'close',20,'1d')
	
	res= longclose - beta_hr*shortclose
	
	context.shortvg= res.mean()
	context.std= res.std()
	
	if context.wait == True:
		if context.days == 20:
			context.wait = False
			context.days= 0
		else:
			context.days +=1

def stop_loss(context,data):
	shortc= data.current(context.short,'price')
	longc= data.current(context.long,'price')
	resc= longc- beta_hr*shortc
	if context.amlong== True or context.amshort == True:
		returns= (resc - context.rescur)/context.rescur
		print(returns)
		if returns < -0.2:
			order_target_percent(context.long,0)
			order_target_percent(context.short,0)
			context.amlong = False
			context.amshort = False
			context.wait = True

def place_orders(context,data):
	
	if context.account.leverage > 1.0:
		print('Leverage > 1')

	long_percent= (0.9/(1.0+beta_hr))
	short_percent = (0.9- long_percent)
	
	shortcur= data.current(context.short,'price')
	longcur= data.current(context.long,'price')

	rescur= longcur - beta_hr*shortcur
 
	if context.amlong == True:
		if rescur >= context.shortvg:
			order_target_percent(context.long, 0)
			order_target_percent(context.short,0)
			context.amlong = False
	elif context.amshort == True:
		if rescur <= context.shortvg:
			order_target_percent(context.long, 0)
			order_target_percent(context.short,0)
			context.amshort = False

	elif rescur >= context.shortvg + 2*context.std and context.wait == False:
		
		order_target_percent(context.long, -long_percent)
		order_target_percent(context.short, short_percent)
		context.rescur= rescur
		context.amshort= True

	elif rescur <= context.shortvg - 2*context.std and context.wait == False:
		
		order_target_percent(context.long, long_percent)
		order_target_percent(context.short, -short_percent)
		context.rescur= rescur
		
		context.amlong= True


start= datetime.datetime(2010,1,1,0,0,0,0,pytz.utc)
end = datetime.datetime(2011,1,1,0,0,0,0,pytz.utc)

register('my_bundle',yahoo_equities(('GWW','PCAR',)))
ingest('my_bundle')

results= run_algorithm(start=start,end=end,initialize=initialize,capital_base=10000,before_trading_start=before_trading_start,data_frequency='daily',bundle='my_bundle')
