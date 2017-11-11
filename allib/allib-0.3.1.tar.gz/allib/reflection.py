def get_fn_argnames(func):
	"""
	Given a function, find its argument and keyword argument names.
	"""
	arg_count = func.__code__.co_argcount
	kwarg_count = 0
	if func.__defaults__:
		kwarg_count = len(func.__defaults__)
		arg_count = arg_count - kwarg_count

	fn_args = func.__code__.co_varnames[:arg_count]
	fn_kwargs = func.__code__.co_varnames[arg_count:arg_count + kwarg_count]

	return fn_args, fn_kwargs
