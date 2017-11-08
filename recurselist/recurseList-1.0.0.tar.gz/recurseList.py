'''iterate print item in nested list which in another list'''

def recurseList(srcList):
	for item in srcList:
		if isinstance(item,list):
			recurseList(item)
		else:
			print(item)
