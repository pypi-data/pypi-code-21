"""
Put the variables you want to load/save in a variable called
"variables_to_load"/"variables_to_save" then exec either
load_pickled_variables/save_pickled_variables.
"""

# load_pickle_fmt = '''
# try:
#     with open('{to_load:s}.pkl', 'rb') as f:
#         {to_load:s} = pickle.load(f)
# except FileNotFoundError:
#     pass
# '''
save_pickle_fmt = '''
try:
    {to_save:s}
    with open('{to_save:s}.pkl', 'wb') as f:
        pickle.dump({to_save:s}, f)
except:
    pass
'''

load_pickled_variables = """
import pickle
for var in variables_to_load:
    exec('''
try:
    with open('{to_load:s}.pkl', 'rb') as f:
        {to_load:s} = pickle.load(f)
except FileNotFoundError:
    pass
'''.format(to_load=var))
"""
save_pickled_variables = """
import pickle
for var in variables_to_save:
    exec('''
try:
    {to_save:s}
    with open('{to_save:s}.pkl', 'wb') as f:
        pickle.dump({to_save:s}, f)
except:
    pass
'''.format(to_save=var))
"""
