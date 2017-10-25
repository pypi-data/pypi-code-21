"""
	Utils for Impossible FX API
"""
from functools import partial
import inspect


def deep_set_str( root_dict, deep_key, value, skip_name_parts=0 ):
	"""
	Set a value deeply in 'root_dict' creating any necessary sub-dicts.
	'deep_key' is a string in dotted notation

	:param root_dict: the dict to work on
	:type root_dict: dict
	:param deep_key: The "deep" key
	:type deep_key: str
	:param value: the value
	:type value: any
	:param skip_name_parts: how many parts in 'deep_key' to skip
	:type skip_name_parts: int
	"""
	deep_dict = root_dict
	name_parts	 = deep_key.split( "." )[skip_name_parts:]

	latest = name_parts.pop()
	for key in name_parts:
		deep_dict = deep_dict.setdefault( key, {} )
	deep_dict.setdefault( latest, value )


def deep_set( root_dict, key_parts, value ):
	"""
	Set a value deeply in 'root_dict' creating any necessary sub-dicts.
	key_parts is an iterable consisting of one key for each level

	:param root_dict: the dict to work on
	:type root_dict: dict
	:param key_parts: The "deep" key parts
	:type key_parts: list or tuple
	:param value: the value
	:type value: any
	"""
	deep_dict = root_dict

	latest = key_parts[-1]
	for key in key_parts[:-1]:
		deep_dict = deep_dict.setdefault( key, {} )
	deep_dict.setdefault( latest, value )


def update( dict1, dict2 ):
	"""
	Update 'dict1' with 'dict2' and return 'dict1'

	:type dict1: dict
	:type dict2: dict
	:rtype: dict
	"""
	dict1.update( dict2 )
	return dict1


def mixin_service( result_instance, service_instance, arg_name ):
	"""
	Inject all public methods from 'service_instance' that have 'arg_name'
	as first argument after 'self' into 'result_instance'
	"""
	if result_instance.__class__ is service_instance.__class__:
		raise ValueError( "Cannot mix in same class" )
	for name, method in inspect.getmembers( service_instance, predicate=inspect.ismethod ):
		if not name.startswith( "_" ):
			argspec = inspect.getargspec( method )
			if len( argspec.args ) > 1 and argspec.args[1] == arg_name: # 'self' is 0
				# print "injecting method %s( %s ):" % (name, ", ".join( argspec.args ))
				if hasattr( result_instance, name ):
					raise ValueError( "Already have method %s" % name )
				setattr( result_instance, name, partial( method, getattr( result_instance, arg_name ) ) )
