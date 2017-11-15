def printmovie (the_list):
	for m in the_list:
		if isinstance(m,list):
			printmovie(m)
		else:
			print(m)
