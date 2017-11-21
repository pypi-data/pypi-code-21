from .definitions import RequestException
from functools import wraps
import inspect

def ohm2_handlers_light_safe_request(func, app):

	@wraps(func)
	def wrapper(*args, **kwargs):
		try:
			result = func(*args, **kwargs)
		except Exception as original:
			tr = inspect.trace()[-1]
			
			exc = RequestException(app,
								   getattr(original, "code", None),
								   getattr(original, "message", None),
								   original,
								   ins_filename = tr.filename,
								   ins_lineno = tr.lineno,
								   ins_function = tr.function,
								   ins_code_context = tr.code_context)

			return (None, exc)
		
		else:
			return (result, None)

	return wrapper

