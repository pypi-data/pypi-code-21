import traceback



def traceback_to_str(exception = None):
    '''Simple convience function that converts the full stack trace to a string'''
    
    traceback_str = repr(traceback.format_exc())
#     traceback_str = repr(traceback.format_stack())
    return traceback_str


if __name__ == '__main__':         # pragma: no cover
    try:                           # pragma: no cover
        raise AttributeError()     # pragma: no cover
    except Exception, e:           # pragma: no cover
        print(traceback_to_str(e)) # pragma: no cover
