import os
import os.path


def transform_filename(static_dir, orig_filename, bust_extensions):
	file_path = os.path.join(static_dir, orig_filename)
	if os.path.isfile(file_path):
		directory, filename = os.path.split(orig_filename)
		filename, extension = filename.split('.', 1)
		if bust_extensions is True or extension in bust_extensions or \
				extension.split('.')[-1] in bust_extensions:
			timestamp = int(os.stat(file_path).st_mtime)
			filename = '{}.{}.{}'.format(filename, timestamp, extension)
			return os.path.join(directory, filename)
	return orig_filename


def cache_busting_url_defaults_factory(app, bust_extensions): #pylint: disable=invalid-name
	# keep a dict of rewritten URLs to prevent a `stat` every time url_for is
	# called on a static file.
	url_cache = {}

	def url_default(endpoint, values):
		if endpoint == 'static':
			filename = values.get('filename')
			if filename:
				if filename not in url_cache:
					transformed_filename = transform_filename(
						app.static_folder, filename, bust_extensions
					)
					if transformed_filename == filename:
						url_cache[filename] = False
					else:
						url_cache[filename] = transformed_filename
				if url_cache[filename]:
					values['filename'] = url_cache[filename]

	return url_default


def setup_cache_busting(app, bust_extensions=True):
	"""
	Extend Flask's URL resolver to support cache busting of static files.
	Requires that you have your web server set up to rewrite these URLs,
	i.e. "foo.12345678.css" should be rewritten to "foo.css". Example:

	setup_cache_busting(app, app.config['CACHE_BUST_URLS'])
	"""
	app.url_defaults(cache_busting_url_defaults_factory(app, bust_extensions))


def cache_busting_url_for(app, old_url_for, bust_extensions=True):
	"""
	Replace flask's url_for with one that supports cache busting of static
	files. Requires that you have your web server set up to rewrite these URLs,
	i.e. "foo.12345678.css" should be rewritten to "foo.css". Example:

	flask.url_for = cache_busting_url_for(
		app, flask.url_for, app.config['CACHE_BUST_URLS']
	)
	"""

	if not bust_extensions:
		return old_url_for

	url_default = cache_busting_url_defaults_factory(app, bust_extensions)

	def url_for_wrapper(endpoint, **values):
		url_default(endpoint, values)
		return old_url_for(endpoint, **values)

	return url_for_wrapper
