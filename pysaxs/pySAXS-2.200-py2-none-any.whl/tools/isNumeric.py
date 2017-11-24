'''
tools package for numbers
'''
def isNumeric(val):
    ''' return true if val is a numeric value
    '''
    try:
        i = float(val)
    except ValueError, TypeError:
        # not numeric
        return False
    else:
        # numeric
        return True