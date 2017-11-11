from copy import deepcopy


def deep_dict_merge(old_dict, new_dict, copy=True, deep=True):
	if copy:
		if deep:
			old_dict = deepcopy(old_dict)
		else:
			old_dict = old_dict.copy()

	for key, value in new_dict.items():
		if key in old_dict and isinstance(old_dict[key], dict) and isinstance(value, dict):
			deep_dict_merge(old_dict[key], value, copy=False, deep=False)
		else:
			old_dict[key] = value

	return old_dict
