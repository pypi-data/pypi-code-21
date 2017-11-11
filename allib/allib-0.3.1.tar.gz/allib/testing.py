#pylint: disable=unused-import
# in python3, the mock module is included with the unittest module. if you're
# running python2 or want a more recent version, you install it with pip
try:
	import mock
except ImportError:
	from unittest import mock
