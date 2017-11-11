import difflib


def get_diff_string(contents_before, contents_after):
	"""Get the diff of two strings, as a string."""
	return ''.join(difflib.unified_diff(
		[line + '\n' for line in contents_before.splitlines()],
		[line + '\n' for line in contents_after.splitlines()]
	))
