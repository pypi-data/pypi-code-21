def printLOL(lists, indent=False, level=0):
	for item in lists:
		if (isinstance(item,list)):
			printLOL(item, indent, level+1)
		else:
			if(indent):
				print("\t"*level,end="")
			print(item)