import inflection

## Note that we tried using MetaClasses to register our api/mangers etc 
## we found that when dealing with Python Base Model, which also uses MetaClasses to register things...
## proved too annoying to deal with, hence we have swapped back to manually registering things.
## This was tested on Oct 25, 2017 


class Registry(object):
    '''A class to hold other Django related classes by their name so that we can retrieve them
    from a central location!'''
    
    REGISTRY_TYPE = None # the caps is important
    REGISTER = None
    
    SHOULD_CHECK_TYPE = True # the Model for Django naming convention is a bit different...
    
    def __init__(self):
        pass
    

    def register(self, cls):
        '''Register a Class so that it can be used later!'''
        if cls == None:
            raise TypeError('{type} Registry: Are you sure this is a {type}? {name}'.format(type = self.REGISTRY_TYPE, name = str(cls)))
        
        class_name = cls.__name__
        if self.REGISTER.get(class_name) == None:
            if class_name.find(self.REGISTRY_TYPE) < 0  and self.SHOULD_CHECK_TYPE == True:
                raise NameError('{type} Registry: Are you sure this is a {type}? {name}'.format(type = self.REGISTRY_TYPE, name = class_name))
            
            self.REGISTER[class_name] = cls
        else:
            # we raise an error only if the class inputted is different than the one that exists.
            # otherwise it might be someone just being enthusiastic...
            if self.REGISTER.get(class_name) != cls:
#                 print('Inputs', class_name, cls, self.REGISTER.get(class_name))
                raise NameError('{type} Registry: REGISTRY_TYPE CONFLICT.  There is already a {class_name} with that name!'.format(type = self.REGISTRY_TYPE, class_name = class_name))
            else:
                print('{type} Registry: You are registering an existing {class_name} again...'.format(type = self.REGISTRY_TYPE, class_name = class_name))
        
    def get(self, name):
        '''Input a manager's name and get back the manager of interest.
        We allow to input a model name, omitting the word manager.'''
        cleaned_name = self.clean_name(name = name)
        _obj = self.REGISTER.get(cleaned_name) 
        if _obj == None:
            raise AttributeError('{type} Registry: Could not find {name}'.format(name = cleaned_name, type = self.REGISTRY_TYPE))
        return _obj
    
    def get_name(self, cls):
        '''Will return two versions of the name, first one with the full name
        the second one with the Register type stripped from it.'''
        
        full_name = cls.__name__ if hasattr(cls, "__name__") else cls.__class__.__name__
        name = full_name.replace(self.REGISTRY_TYPE, '')
        
        if full_name == name and self.SHOULD_CHECK_TYPE == True:
            raise TypeError('Unable to confirm that the input was a class of type {type}'.format(type = self.REGISTRY_TYPE))
        
        return full_name, name

    def get_name_list(self):
        '''Return a list of all registered classes by full name'''
        return self.REGISTER.keys()

    
    def clean_name(self, name):
        try:  # might not get passed a name?
            name = inflection.camelize(name)
            if name.find(self.REGISTRY_TYPE) <= 0 and self.SHOULD_CHECK_TYPE == True:
                name += self.REGISTRY_TYPE
        except:
            pass
        return name
    
    @classmethod
    def set_instance(self):
        raise NotImplementedError('This needs to be implemented by the inheritor! since its sets a local instance')
########## EXAMPLE #########
#         if instance == None:
#             global instance
#             instance = ManagerRegistry()
########## EXAMPLE #########
    