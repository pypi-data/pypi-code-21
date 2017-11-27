"""Tools to build a URL using the current URL as defaults."""
from collections import Iterable

from flask import request, url_for
from werkzeug.datastructures import MultiDict


def url_update_args(**kwargs):
	"""Take the current URL and update paramters, keeping all unspecified the same."""
	return url_update_endpoint_args(request.endpoint, **kwargs)


def url_update_endpoint_args(endpoint, **kwargs):
	"""Return the URL for passed endpoint using args from current request and kwargs."""
	# request.args contains parameters from the query string
	# request.view_args contains parameters that matched the view signature
	args = MultiDict(request.args)
	args.update(request.view_args)
	for arg, value in kwargs.items():
		if isinstance(value, Iterable) and not isinstance(value, str):
			args.setlist(arg, value)
		else:
			args[arg] = value
	# Now set any individual args to the object instead of a list of len 1
	args = args.to_dict(flat=False)
	for key in set(args.keys()):
		if len(args[key]) == 1:
			args[key] = args[key][0]
	return url_for(endpoint, **args)
