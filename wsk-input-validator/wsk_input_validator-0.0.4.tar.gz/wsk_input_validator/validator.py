import os.path
import yaml

def validate(name):
    def decorator(function):
        def wrapper(input):
            type_map = {
                "String" : ["str","string","String"],
                "Integer": ["int","Integer","integer"],
                "Object": ["dict", "Dictionary", "dictionary", "Object", "object"],
                "Array": ["list", "Array", "array"]
            }
            if os.path.isfile("annotations.yaml"):
                f = open("annotations.yaml", "r")
            elif os.path.isfile("../annotations.yaml"):
                f = open("../annotations.yaml", "r")
            else:
                raise IOError("Missing annotations file")
            annos = yaml.load(f)
            for param in annos[name].get("parameters",[]):
                if input.get(param["name"],None) is not None:
                    if(type(input[param["name"]]).__name__ not in type_map.get(param["type"],[])):
                        raise TypeError(param["name"] + " has type " + type(input[param["name"]]).__name__ + " but require " + param["type"])
            return function(input)
        return wrapper
    return decorator
