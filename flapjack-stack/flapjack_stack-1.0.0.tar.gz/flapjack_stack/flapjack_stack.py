import logging
import os
import sys
import yaml

try:
    xrange
except NameError:
    xrange = range


class Layer(object):
    """ A container to hold stack attributes
    """

    def merge(self, obj):
        """This function merge another object's values with this instance

        :param obj: An object to be merged with into this layer
        :type obj: object
        """
        for attribute in dir(obj):
            if '__' in attribute:
                continue
            setattr(self, attribute, getattr(obj, attribute))


class FlapjackStack(object):
    """A container to hold layers of stack attributes stored in Layer objects
    """

    def __init__(self):
        """Creates a FlapjackStack instance with a bottom empty layer
        """
        super(FlapjackStack, self).__setattr__('layers', [Layer()])

    def add_layer(self, obj=None):
        """This function adds another empty layer (Layer) to the layers
        list and optionally merges a given object into this layer

        :param obj: An object to be merged with this layer
        :type obj: object
        """
        new_layer = Layer()
        if obj:
            new_layer.merge(obj)
        self.layers.append(new_layer)

    def add_layer_from_file(self, filename):
        """This function calls all supported file type handlers which in turn
        populate a new empty layer (Layer) the provided file's contents

        :param filename: The name of a file to read
        :type filename: string
        """
        self.add_layer_from_py_file(filename)
        self.add_layer_from_yaml_file(filename)

    def add_layer_from_py_file(self, filename):
        """This function implements loading a Python file and populating a new
        empty layer (Layer) with its contents

        :param filename: The name of a file to read
        :type filename: string
        """
        if filename.endswith('.py'):
            try:
                path, filename = os.path.split(os.path.abspath(filename))
                sys.path.append(path)
                filename = filename.rsplit('.', 1)[0]
                stack = __import__(filename, fromlist=['*'],)
            except ImportError:
                logging.info("Could not import stack from %s" % filename)
                return

            self.add_layer()
            for attribute in dir(stack):
                setattr(self, attribute, getattr(stack, attribute))
            sys.path.pop()
            del sys.modules[filename]
            del stack

    def add_layer_from_yaml_file(self, filename):
        """This function implements loading a YAML file and populating a new
        empty layer (Layer) with its contents

        :param filename: The name of a file to read
        :type filename: string
        """
        if filename.endswith(('.yaml', '.yml')):
            file_stream = None
            try:
                file_stream = open(os.path.abspath(filename), 'r')
                stack = yaml.safe_load(file_stream)

                self.add_layer()
                for attribute in stack:
                    setattr(self, attribute, stack[attribute])
                del stack
            except (TypeError, IOError):
                logging.info("Could not import stack from %s" % filename)
            finally:
                if file_stream:
                    file_stream.close()

    def remove_layer(self):
        """ Removes the top layer (right most) of the layers

        :returns: the top layer (right most) of the layers as a Layer
        :rtype: object
        """
        self.layers.pop()

    def __getattr__(self, attr):
        """This function reads through the layers from top to bottom
        returning the first occurrence of the requested attribute

        :param attr: An attribute name
        :type attr: string

        :returns: The value of the attribute
        :rtype: object
        """
        num_layers = len(self.layers)
        for i in reversed(xrange(num_layers)):
            obj = self.layers[i]
            if hasattr(obj, attr):
                val = getattr(self.layers[i], attr)
                if i != num_layers - 1:
                    setattr(self.layers[-1], attr, val)
                return val

        raise AttributeError("%s is not an attribute" % attr)

    def __setattr__(self, attr, value):
        """This function sets the supplied attribute to the supplied value at
        the top most layer

        :param attr: An attribute name
        :type attr: string
        :param value: The value to which the attribute should be set
        :type value: object
        """
        super(Layer, self.layers[-1]).__setattr__(attr, value)

    def get_attributes(self):
        """This function through the layers from top to bottom, and creates a
        list of all the attributes found

        :returns: A list of all the attributes names
        :rtype: list
        """
        attributes = []
        for i in reversed(xrange(len(self.layers))):
            obj = self.layers[i]
            stack_attributes = [attribute for attribute in obj.__dict__.keys()
                                if not attribute.startswith('__') and
                                not attribute.endswith('__')]
            attributes = attributes + stack_attributes
        return list(set(attributes))

    def add_layer_from_env(self):
        """This function creates a new layer, gets a list of all the
        current attributes, and attempts to find matching environment variables
        with the prefix of FJS\_. If matches are found it sets those attributes
        in the new layer.
        """
        self.add_layer()
        for attribute in self.get_attributes():
            env_attribute = os.environ.get('FJS_{}'.format(attribute))
            if env_attribute:
                setattr(self, attribute, env_attribute)
