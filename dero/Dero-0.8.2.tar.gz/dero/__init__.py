
__version__ = "0.8.2"
__version_info__ = (0, 8, 2)

#Provided for backwards compatibility with old code. In the old code, add to the top:
#import builtins
#builtins.__dero_version__ = '0.1.0'
try: 
    __dero_version__
    if __dero_version__ == '0.1.0':
        from dero.core import *
        from dero.data import *
        from dero.decorators import *
        from dero.latex import *
        from dero.pdf import *
        
        from dero.ext_logging import *
        from dero.ext_matplotlib import *
        from dero.ext_multiprocessing import *
        from dero.ext_pandas import *
        from dero.ext_selenium import *
        from dero.ext_sympy import *
        from dero.ext_time import *
        pandas_to_csv = to_csv
    else: #stuctured this way so that we can support future structuring changes, can add additional if statements
        __dero_version__ = 'current'
except NameError:
    __dero_version__ = 'current'

if __dero_version__ == 'current':
    import dero.core
    import dero.data
    import dero.decorators
    import dero.latex
    import dero.pdf
    import dero.wrds
    import dero.logtimer
    import dero.reg
    import dero.summ
    
    import dero.ext_logging as logging
    import dero.ext_matplotlib as matplotlib
    import dero.ext_multiprocessing as multiprocessing
    import dero.ext_pandas as pandas
    import dero.ext_selenium as selenium
    import dero.ext_sympy as sympy
    import dero.ext_time as time
    import dero.ext_math as math
    
    del dero.ext_logging
    del dero.ext_matplotlib
    del dero.ext_multiprocessing
    del dero.ext_pandas
    del dero.ext_selenium
    del dero.ext_sympy
    del dero.ext_time
    del dero.ext_math
    
#     sys.modules['dero.logging'] = dero.ext_logging
#     sys.modules['dero.matplotlib'] = dero.ext_matplotlib
#     sys.modules['dero.multiprocessing'] = dero.ext_multiprocessing
#     sys.modules['dero.pandas'] = dero.ext_pandas
#     sys.modules['dero.selenium'] = dero.ext_selenium
#     sys.modules['dero.sympy'] = dero.ext_sympy
#     sys.modules['dero.time'] = dero.ext_time
    
#     import dero.logging
#     import dero.matplotlib
#     import dero.multiprocessing
#     import dero.pandas
#     import dero.selenium
#     import dero.sympy
#     import dero.time
    
     

