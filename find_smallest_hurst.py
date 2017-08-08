#!/usr/bin/env python

import sys

f = open(sys.argv[1],'r')

hurst = 100000000

f.seek(0)

for line in f:
	string = line.split()
	if len(string) > 1:
		if string[0] == 'test' and string[1] == 'statistic:':
			if float(string[2]) < hurst:
				hurst = float(string[2])

print(str(hurst))

date = 1000000000

f.seek(0)

for line in f:
	string = line.split()
	if len(string) >1:
		if string[0] == 'Start':
			if int(line[8:12]) < date:
				date = int(line[8:12])

print(str(date))
