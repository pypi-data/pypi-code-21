def join_dicts(old_dicts, *new_dicts):
  joined_dicts = old_dicts.copy()

  for dictionary in new_dicts:
    joined_dicts.update(dictionary)

  return joined_dicts

def dict_depth(collection):
  if isinstance(collection, dict) and collection:
    return 1 + max(dict_depth(collection[a]) for a in collection)
  if isinstance(collection, list) and collection:
    return 1 + max(dict_depth(a) for a in collection)
  return 0
