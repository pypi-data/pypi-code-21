
import sys

def print_lol2(a_list,intend = False, level=0):
	for each_item in a_list:
			if isinstance(each_item, list):
				print_lol2(each_item, intend, level+1)
			else:
				if intend:
					for l in range(level):
						print("\t", end='')
				print(each_item)


def print_lol(a_list, indent=False, level=0, fh = sys.stdout):
    """Prints each item in a list, recursively descending
       into nested lists (if necessary)."""

    for each_item in a_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1, fh)
        else:
            if indent:
                for l in range(level):
                    print("\t", end='', file=fh)
            print(each_item,file=fh)
