import sys
import imp

class Finder(object):

    def __init__(self, path_to_module,sub_module_name, class_name, src_func_name, target_ptr):
        self.path_to_module = path_to_module
        self.sub_module_name = sub_module_name
        self.class_name = class_name
        self.src_func_name = src_func_name
        self.target_ptr = target_ptr

    def find_module(self, fullname, path=None):
        if fullname == self.path_to_module:
            return self
        return

    def load_module(self, fullname):
        keras =  imp.load_module(fullname, *imp.find_module(fullname))
        keras_models = getattr(keras,self.sub_module_name)
        keras_models_Model = getattr(keras_models,self.class_name)
        keras_models_Model_fit = getattr(keras_models_Model,self.src_func_name)
        source_func_logged = self.target_ptr(keras_models_Model_fit)
        setattr(keras_models_Model, self.src_func_name, source_func_logged)



        return keras



