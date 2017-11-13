from keyword import kwlist
import re

class GenClass():
    ''' 
    dotdicts act similar to javascript objects. you can assign new
    attributes with the dot.new_attr = new_val. and non exsistant
    attributes simple return None when accessed. eg.
    
    dot.does_not_exist is None == True
    '''
    def __init__(self, dict_={}):
        self.add_dict(dict_)

    def __setattr__(self, name, val):
        # sanitize the name
        name = self._sanitize(name)
       
        if type(val) is dict:
            self.__dict__[name] = GenClass(val)
        elif type(val) is list:
            self.__dict__[name] = self._genlist(val)
        else:
            self.__dict__[name] = val

    def _genlist(self, list_):
        l = []
        for elem in list_:
            if type(elem) is dict:
                l.append(GenClass(elem))
            elif type(elem) is list:
                l.append(self._genlist(elem))
            else:
                l.append(elem)
        
        return l

    def __getitem__(self, name):
        return self.__dict__.get(name)

    def __setitem__(self, name, val):
        self.__setattr__(name, val)

    def _sanitize_keywords(self, name):
        return name if name not in kwlist else ''.join([name, '_'])

    def _sanitize_bad_chars(self, name):
        return '_'.join(re.split('[^_a-zA-Z0-9]+', name))

    def _sanitize(self, name):
        name = self._sanitize_bad_chars(name)
        name = self._sanitize_keywords(name)
        return name
        
    def add_dict(self, dict_):
        for name, val in dict_.items():
            self.__setattr__(name, val)
            
    def keys(self):
        return self.__dict__.keys()

