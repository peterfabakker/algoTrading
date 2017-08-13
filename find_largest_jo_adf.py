#!/usr/bin/python

from datetime import datetime

input = open('jo_adf_3.txt','r')
max_val = 0
temp_max_val = 0
start = False
realstr = str()
largStr = str()
test = False
'''
previous = False
stocks = str()
eig = str()
realeig = str()
next = 0
'''
for line in input:
	if start:
		largStr += line
	'''if next > 0:
		eig += line+'\n'
		next +=1
		if next == 3:
			next = 0
	if previous:
		stocks = line
		previous = False
	
	if line == 'Johansen Test \n':
		previous = True
	'''
	string = line.split()
	if len(string) >1:
		#if string[0] == 'eigenvectors:':
		#	eig += line+'\n'
		#	next = 1
		if string[0] == 'Start':
			start = True
			largStr += line
			start_date = datetime.strptime(string[2],'%Y-%m-%d')
		if string[0] == 'test' and string[1] == 'statistic:':
			if float(string[2]) < max_val:
				temp_max_val = float(string[2])
				temp_realstr = largStr
				test = True
				#max_stocks = stocks
				#realeig = eig
			#eig = str()
		if string[0] == 'Hurst' and test:
			if float(string[2]) <= 0.1:
				max_val = temp_max_val
				realstr = temp_realstr
			largStr = str()
			test = False

print(max_val)
print(realstr)
#print(max_stocks)
#print(realeig)
