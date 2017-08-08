#!/usr/bin/python

import numpy as np
import pandas as pd

from zipline.api import symbol, order_target_percent

def initialize(context):
	context.AMD= symbol('AMD')
	context.NVDA= symbol('NVDA')
	context.has_ordered = False

def handle_data(context,data):


	if context.has_ordered == False:

		order_target_percent(context.AMD,50)
		order_target_percent(context.NVDA,50)
		context.has_ordered = True
		



		
