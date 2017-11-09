def print_dict(_dict):
    for foo in _dict.keys():
        print(foo + ": " + str(_dict[foo]))


def init_function_params_code_builder(params_as_string):
    for p in params_as_string.split(", "):
        print "self.{} = {}".format(p, p)


def pairs_in_list(l):
    pairs = []
    i = 0
    while i < len(l):
        j = i + 1
        while j < len(l):
            pairs.append([l[i], l[j]])
            j += 1
        i += 1
    return pairs
