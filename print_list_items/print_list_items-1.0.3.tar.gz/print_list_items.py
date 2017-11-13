'''this function is to print all list value which including or not including list'''
def print_lol(the_list,indent=False,level=0):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,indent,level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t",end='')
			print(each_item)
