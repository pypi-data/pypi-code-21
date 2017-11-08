import os.path
import yaml

def validate(name):
    def decorator(function):
        def wrapper(input):
            type_map = {
                "String" : ["str","string","String"],
                "Integer": ["int","Integer","integer"],
                "Object": ["dict", "Dictionary", "dictionary", "Object", "object"],
                "Array": ["list", "Array", "array"],
                "Boolean": ["bool", "Boolean", "boolean"]
            }
            return function(input)
        return wrapper
    return decorator
