"""
main parski module
"""
from __future__ import print_function

import sys
import re

from filter_datetime_mod import filter_datetime
from path_dict_conv_mod import dict_to_paths

def filter_data(data, search_input, max_results=5000, metrics=False, silent=False):
    '''
    filter data based on path list or search dict arrays
    '''

    ##check if single path or single path group was used
    try:
        search_input['path']
        search_input['value']
        search_input = [search_input]
    except:
        pass

    try:
        search_input[0]['path']
        search_input[0]['value']
        search_input = [search_input]
    except:
        pass

    ##check if single dict was used
    if isinstance(search_input, dict):
        search_input = [search_input]
    if not silent:
        print("Data length: ", len(data))
        print("Running Search...")
    filtered_results = []
    global metrics_dict
    metrics_dict = {'missing_keys': 0, 'regex_errors': 0}

    for i, search_list in enumerate(search_input):
        if isinstance(search_list, dict):
            search_list = dict_to_paths(search_list, [], [])
        elif isinstance(search_list, list):
            search_list = search_list
        else:
            print("Invalid input type.  Must be 'dicts' or 'lists'")
            sys.exit(1)
        if not silent:
            print("search_list: ", search_list)
        for search in search_list:
            try:
                int(search['path'][0])
            except:
                search['path'] = [i] + search['path']

        #Remove paths where value is None
        temp_paths = []
        for path in search_list:
            if path['value'] != str(None):
                temp_paths.append(path)
        search_list = temp_paths
        for entry in data:
            if len(filtered_results) >= max_results:
                break
            elif __entry_filter(entry, search_list, True) and entry not in filtered_results:
                filtered_results.append(entry)
    if not silent:
        print("Results found: ", len(filtered_results))
    if metrics:
        return {'results': filtered_results, 'metrics': metrics_dict}
    return filtered_results

def __entry_filter(entry, path_list, first):
    '''
    filter single entry with path_list
    '''

    path_groups = []
    #loop through all paths in path_list
    for path in path_list:
        #check if path has ended.  If so, remove from checks if passed, return False if failed
        if len(path['path']) <= 1:
            #One fail is total fail.  One pass is NOT total pass.
            if __value_check(entry, path) is False:
                return False

        #sort remaining paths into groups based on first value
        else:
            found = False
            for group in path_groups:
                if path['path'][0] == group[0]['path'][0]:
                    group.append(path)
                    found = True
                    break
            if not found:
                path_groups.append([path])

    #run each group together
    return __filter_path_groups(entry, path_groups, first)

def __value_check(entry, path):
    '''
    check if end value is equal to the the one defined in the path
    '''

    global metrics_dict
    value = str(path['value'])
    if value == 'null':
        value = 'None'
    entry_index = path['path'][0]

    ##check for key errors
    try:
        entry[entry_index]
    except:
        metrics_dict['missing_keys'] += 1
        return False

    ##check regex and for compile errors
    try:
        regex_value = re.compile(value, re.IGNORECASE)
        if not re.search(regex_value, str(entry[entry_index]).encode('utf-8')) and not filter_datetime(value, entry[entry_index]):
            return False
        return True
    except:
        metrics_dict['regex_errors'] += 1
        return False

def __filter_path_groups(entry, path_groups, first):
    '''
    Groups checks by list to ensure passes are at same index
    '''
    if entry is None:
        return False
    elif not first:
        for group in path_groups:
            current_index = group[0]['path'][0]

            #create new groups with first path removed
            for i, path in enumerate(group):
                group[i] = {'value': path['value'], 'path': path['path'][1:]}

            #check if list, if so run against all
            if isinstance(entry, list):
                match = False
                for item in entry:
                    if __entry_filter(item, group, False):
                        match = True
                if not match:
                    return False
            else:
                if current_index in list(entry):
                    if not __entry_filter(entry[current_index], group, False):
                        return False
                else:
                    return False
        return True
    else:
        for group in path_groups:
            for i, path in enumerate(group):
                group[i] = {'value': path['value'], 'path': path['path'][1:]}
            if __entry_filter(entry, group, False):
                return True
