from .validate import *
from .error import *
def tiny_int(val):
	try:
		if validate_val(val) and validate_tiny_int(val):
			return True
		else:
			raise TinyIntError()
	except TinyIntError as error:
		print(error)

