'''
Abstract class for data plug-in modules.

Every "plug-in" must provide an <Infer> class and a <DataFactory> class
definition. 

A plug-in is represented as a dictionary:
    {  "name" : string,
       "type-ext" : string,
       "data-infer" : <data infer object>,
       "data-factory" : <data access factory class> }
Note: the data-infer object is an instantiated object of the <Infer> class 
the factory is just the class object
       
<Infer> objects must provide 
(1) a method, matched_by : string -> boolean
    which takes the primary path (URL/file name) to the data.
(2) a dictionary field, options : { string : string, ... }

The options may be populated in the process of matching and are
then passed on to the data access factory object when it is 
instantiated (for example, the CSV plugin may infer a delimiter
based on whether the path name contains .csv or .tsv).

<DataFactory> class should provide methods:        
(1) get_options :  -> list
    produces a list of value option names for the data format
(2) get_option : string -> value
    produces the value (or None) of the option with the given name
(3) set_option : string, value -> void

(4) load_data : file-like-object [, string] -> json-like-object
    - the file object should provide bytes data (i.e. open in binary mode)
    - encoding may be provided, e.g. 'utf-8'
    - the returned thing should be a json-like-object made up
      of Python dicts, lists, built-in types (int,float,boolean,string)
'''


class Base_Infer:
    
    def __init__(self):
        self.options = {}
    
    def matched_by(self, path):
        return False
    
    
class Base_Data_Factory:
    
    def __init__(self):
        pass
    
    def load_data(self, fp, encoding=None):
        return None
    
    def get_options(self):
        return []
    
    def get_option(self, name):
        return None    

    def set_option(self, name, value):
        pass

