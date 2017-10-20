'''
A small util to shallow destructure a dictionary.
'''
def destructure(dictionary):
    ''' Destructures a dictionary. '''
    def destructure_args(*args):
        ''' Return array of values for keys '''
        return [dictionary[key] for key in args]

    return destructure_args
