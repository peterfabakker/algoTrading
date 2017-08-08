input = open('adf3.out','r')
next = False
num_list = list()
previous = str()
max_num = 0
for line in input:
	string = line.split()
	if next:
		num = float(string[0])
		if num < max_num:
			max_num = num
			max_val = previous
		next = False
	if len(string) >= 2:
		if string[1] == 'and':
			next = True
	previous = string

print(max_val)
print(max_num)
