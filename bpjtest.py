#!/usr/bin/python

import numpy as np
import logbook
import pytz
import datetime
from test_johansen import test_stocks
import quandl

zipline_logging= logbook.NestedSetup([logbook.NullHandler(level=logbook.DEBUG),logbook.StreamHandler(sys.stdout,level=logbook.INFO),logbook.StreamHandler(sys.stderr,level=logbook.ERROR),])
zipline_logging.push_application()

from zipline import run_algorithm
from zipline.api import order_target_percent, symbol, schedule_function, date_rules, time_rules, get_environment

evec = test_stocks()

def initialize(context):
    context.s1= symbol('AYI')
    context.s2= symbol('APA')
    context.s3= symbol('AMZN')
    context.s4= symbol('LNT')
    context.s5= symbol('CTL')
    context.s6= symbol('ALB')
    context.s7= symbol('ABBV')
    context.s8= symbol('AMT')
    context.s9= symbol('ADM')
    context.s10= symbol('AON')
    context.s11= symbol('ORCL')
    
    
    context.amlong= False
    context.amshort= False

    schedule_function(place_orders, date_rules.every_day())

def before_trading_start(context,data):

    s1close= data.history(context.s1,'close',50,'1d')
    s2close= data.history(context.s2,'close',50,'1d')
    s3close= data.history(context.s3,'close',50,'1d')
    s4close= data.history(context.s4,'close',50,'1d')
    s5close= data.history(context.s5,'close',50,'1d')
    s6close= data.history(context.s6,'close',50,'1d')
    s7close= data.history(context.s7,'close',50,'1d')
    s8close= data.history(context.s8,'close',50,'1d')
    s9close= data.history(context.s9,'close',50,'1d')
    s10close= data.history(context.s10,'close',50,'1d')
    s11close= data.history(context.s11,'close',50,'1d')
    
    s = np.array([s1close,s2close,s3close,s4close,s5close,s6close,s7close,s8close,s9close,s10close,s11close])
    
    res= np.dot(evec,s)

    context.avg= res.mean()
    context.std= res.std(ddof=0)

def place_orders(context,data): 
    
    s1_percent= evec[0]
    s2_percent= evec[1]
    s3_percent= evec[2]
    s4_percent= evec[3]
    s5_percent= evec[4]
    s6_percent= evec[5]
    s7_percent= evec[6]
    s8_percent= evec[7]
    s9_percent= evec[8]
    s10_percent= evec[9]
    s11_percent= evec[10]

    s1cur= data.current(context.s1,'price')
    s2cur= data.current(context.s2,'price')
    s3cur= data.current(context.s3,'price')
    s4cur= data.current(context.s4,'price')
    s5cur= data.current(context.s5,'price')
    s6cur= data.current(context.s6,'price')
    s7cur= data.current(context.s7,'price')
    s8cur= data.current(context.s8,'price')
    s9cur= data.current(context.s9,'price')
    s10cur= data.current(context.s10,'price')
    s11cur= data.current(context.s11,'price')
    
    s= np.array([s1cur,s2cur,s3cur,s4cur,s5cur,s6cur,s7cur,s8cur,s9cur,s10cur,s11cur])
    
    rescur= np.dot(evec,s)
    
    zscore = (rescur-context.avg)/context.std
 
    if context.amlong == True and zscore >= zExit:
            order_target_percent(context.s1, 0)
            order_target_percent(context.s2,0)
            order_target_percent(context.s3,0)
            order_target_percent(context.s4, 0)
            order_target_percent(context.s5,0)
            order_target_percent(context.s6,0)
            order_target_percent(context.s7, 0)
            order_target_percent(context.s8,0)
            order_target_percent(context.s9,0)
            order_target_percent(context.s10, 0)
            order_target_percent(context.s11,0)
            context.amlong = False
    elif context.amshort == True and zscore <= -zExit:
            order_target_percent(context.s1, 0)
            order_target_percent(context.s2,0)
            order_target_percent(context.s3,0)
            order_target_percent(context.s4, 0)
            order_target_percent(context.s5,0)
            order_target_percent(context.s6,0)
            order_target_percent(context.s7, 0)
            order_target_percent(context.s8,0)
            order_target_percent(context.s9,0)
            order_target_percent(context.s10, 0)
            order_target_percent(context.s11,0)
            context.amshort = False
    elif context.amshort == False and zscore >= zEnter:
        order_target_percent(context.s1, -s1_percent)
        order_target_percent(context.s2, -s2_percent)
        order_target_percent(context.s3, -s3_percent)
        order_target_percent(context.s4, -s4_percent)
        order_target_percent(context.s5, -s5_percent)
        order_target_percent(context.s6, -s6_percent)
        order_target_percent(context.s7, -s7_percent)
        order_target_percent(context.s8, -s8_percent)
        order_target_percent(context.s9, -s9_percent)
        order_target_percent(context.s10, -s10_percent)
        order_target_percent(context.s11, -s11_percent)
        context.rescur= rescur
        context.amshort= True
    elif context.amlong == False and zscore <= -zEnter:
        order_target_percent(context.s1, s1_percent)
        order_target_percent(context.s2, s2_percent)
        order_target_percent(context.s3, s3_percent)
        order_target_percent(context.s4, s4_percent)
        order_target_percent(context.s5, s5_percent)
        order_target_percent(context.s6, s6_percent)
        order_target_percent(context.s7, s7_percent)
        order_target_percent(context.s8, s8_percent)
        order_target_percent(context.s9, s9_percent)
        order_target_percent(context.s10, s10_percent)
        order_target_percent(context.s11, s11_percent)
        context.rescur= rescur
        context.amlong= True

def main(Ent,Ex):

	global zEnter
	global zExit
	zEnter = Ent
	zExit = Ex
	eastern = pytz.timezone('US/Eastern')        
	start= datetime.datetime(2013,1,2,0,0,0,0,eastern)
	end = datetime.datetime(2017,6,22,0,0,0,0,eastern)

	results= run_algorithm(start=start,end=end,initialize=initialize,capital_base=10000,before_trading_start=before_trading_start)
	return results.portfolio_value[-1]
