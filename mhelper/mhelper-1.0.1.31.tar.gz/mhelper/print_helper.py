import traceback


def print_exception(exception, traceback_ = None):
    if not traceback_:
        traceback_ = traceback.format_exc()
        
    print( str( exception ) )
    print( traceback_ )

