from copy import deepcopy

def dict_to_paths(search_list, current_path, paths):
    '''
    Convert search_dict to list of paths.
    First call should be dict_to_paths(search_dict, [], [])
    '''
    if isinstance(search_list, dict):
        for key, value in search_list.iteritems():
            temp_path = deepcopy(current_path)
            temp_path.append(key)
            paths = dict_to_paths(search_list[key], temp_path, paths)
    elif isinstance(search_list, list):
        for i, item in enumerate(search_list):
            temp_path = deepcopy(current_path)
            temp_path.append(i)
            paths = dict_to_paths(search_list[i], temp_path, paths)
    else:
        paths.append({'path': current_path, 'value': str(search_list)})
    return paths

def paths_to_dict(input_list):
    #rewrite me to look like dict_to_paths, papa
    #shut up, boy
    search_dict = {}
    for item in input_list:
        sub_dict = search_dict
        for i, step in enumerate(item['path']):
            #check if last step and set value

            if isinstance(step, int):
                #if array extend array until it is the length of step
                while len(sub_dict) <= step:
                    sub_dict.append(None)
            elif isinstance(step, basestring):
                if step not in sub_dict:
                    sub_dict[step] = None

            if i+1 >= len(item['path']):
                sub_dict[step] = item['value']
            #else
            else:
                next_step = item['path'][i+1]
                if isinstance(next_step, int) and sub_dict[step] is None:
                    sub_dict[step] = []
                elif isinstance(next_step, basestring) and sub_dict[step] is None:
                    sub_dict[step] = {}
                sub_dict = sub_dict[step]
    return search_dict