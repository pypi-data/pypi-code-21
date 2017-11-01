def printArray(cast):
	for k in cast:
		if(isinstance(k, list)):
			for l in k:
				print(l)
		else:
			print(k)

