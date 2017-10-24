import time
import random
import psyco
psyco.full ()

class IOBench:
	def __init__ (self):
		self.f = open ("c:\\.corpus", "rb")
		self.pointers = [random.randrange (13000000) for i in range (1024 * 1024 / 8)]
		
	def close (self):
		self.f.close ()
		
	def read (self, kb, num = 3):
		read = 0
		readsize = 1024 * kb
		loop = 1024 * 1024 / kb
		t = 0
		for i in range (num):
			s = time.time ()
			for k in range (loop):
				self.f.seek (self.pointers [k])
				data = self.f.read (readsize)
				read += len (data)
			t += time.time () - s
		
		print("file reading %d bytes, per each %d Kbytes reading, %2.3f seconds" % (read, kb, t / num))


f = IOBench ()

f.read (512, 3)
f.read (256, 3)
f.read (128, 3)
f.read (64, 3)
f.read (32, 3)
f.read (16, 3)
f.read (8, 3)
f.read (8, 3)
f.read (16, 3)
f.read (32, 3)
f.read (64, 3)
f.read (128, 3)
f.read (256, 3)
f.read (512, 3)

f.close ()
