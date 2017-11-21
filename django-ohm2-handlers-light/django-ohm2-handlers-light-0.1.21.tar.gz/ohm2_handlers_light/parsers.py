
def get_as_or_get_default(data, keys):
	params = {}
	for o in keys:
		params[o[0]] = data.get(o[1],o[2])
	return params