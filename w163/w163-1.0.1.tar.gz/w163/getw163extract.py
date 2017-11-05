#Please enter website for crawl
#Example python getw163extract.py 'http://www.163.com'


#!/usr/bin/env python
from getw163 import *
import time as t
import threading
import sys

def main():
	start = t.time()
	#url = sys.argv[1]
	links = getw163link('http://www.163.com').getalllink()

	threads = []
	loops = range(len(links))
	print (start)
	for i in loops:
		test = retrieve(links[i])
		th = threading.Thread(target=test.getcontent)
		threads.append(th)

	for i in loops:
		threads[i].start()

	for i in loops:
		threads[i].join()

	end = t.time()
	times = end - start
	with open('time','a') as f:
		f.write('\n')
		f.write(t.ctime())
		f.write('\n')
		f.write(str(times))	
	print (times)

if __name__== '__main__':
	main()
