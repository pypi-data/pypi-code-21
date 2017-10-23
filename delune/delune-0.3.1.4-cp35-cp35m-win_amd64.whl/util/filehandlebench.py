import threading
import time
import random
import math

gf = open (r"G:\database\classification_Log.LDF", "rb")
glock = threading.Lock ()

READ = 0

def run ():
	global READ
	f = open (r"G:\database\asean_Log.LDF", "rb")
	for i in range (100):
		time.sleep (random.randrange (2))
		f.seek (random.randrange (200000000, 300000000))		
		for j in range (10):
			k = [math.log (k) for k in range (1, 1000)]
			d = f.read (65536)
			glock.acquire ()
			READ += len (d)
			glock.release ()
	f.close ()

def run2 ():
	global gf, glock, READ
	for i in range (100):
		time.sleep (random.randrange (2))
		sp = random.randrange (200000000, 300000000)
		for j in range (10):
			k = [math.log (k) for k in range (1, 1000)]
			glock.acquire ()
			gf.seek (sp + (j * 65536))			
			d = gf.read (65536)
			READ += len (d)
			glock.release ()
	

s = time.time ()	
for i in range (4):
	f = threading.Thread (target = run)
	f.start ()
	
while threading.activeCount () > 1:
	time.sleep (0.1)

print(time.time () - s, READ)

READ = 0
s = time.time ()	
for i in range (4):
	f = threading.Thread (target = run2)
	f.start ()
	
while threading.activeCount () > 1:
	time.sleep (0.1)

print(time.time () - s, READ)

gf.close ()
