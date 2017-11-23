"""
The Good Library

The Good Library is a collection of programming and syntax tools that makes your
python code more expressive and easier to work with.

Author:  Anshul Kharbanda
Created: 10 - 6 - 2017
"""
class AnnotationType:
    """
    Base class for annotations

    Author:  Anshul Kharbanda
    Created: 11 - 6 - 2017
    """
    _AT_prefix = '_AT_' # Prefix for annotation type
    _attributes = {} # Attribute names array

    @classmethod
    def _AT_get_full_name(cls):
        """
        Return the full name of the annotation

        :return: the full name of the annotation
        """
        return cls._AT_prefix + cls.__name__

    @classmethod
    def get(cls, obj):
        """
        Returns the annotation in the given object (or False)

        :param obj: the object to check

        :return: the annotation in the given object (or False)
        """
        return getattr(obj, cls._AT_get_full_name(), False)

    def __init__(self, **kwargs):
        """
        Initializes Annotation with the given kwargs
        """
        # Set attributes in attr dict (created by constructor)
        for name,typ in self._attributes.items():
            if name in kwargs and type(kwargs[name]) is typ:
                self.__setattr__(name, kwargs[name])
            elif name in kwargs:
                raise Exception('Expected {typ1} for {name} attribute {attr}. Got {typ2}'.format(
                    name=type(self).__name__,
                    attr=name,
                    typ1=typ,
                    typ2=type(kwargs[name])
                ))
            else:
                raise Exception('{name} attribute {attr} not defined!'.format(
                    name=type(self).__name__,
                    attr=name))
        # TODO: Create custom error type for Attributes

    @property
    def _attr_string(self):
        """
        The attributes of the annotation
        """
        return ', '.join(
            '{name}={attr}'.format(name=attr, attr=repr(getattr(self, attr)))
            for attr in self._attributes)

    def __call__(self, obj):
        """
        Attaches the annotation to the given object

        :param obj: the object to annotate

        :return: the annotated object
        """
        setattr(obj, type(self)._AT_get_full_name(), self)
        return obj

    def __bool__(self):
        """
        Returns true to prove existence of the Annotation
        """
        return True

    def __repr__(self):
        """
        String representation of instance
        """
        return '@{name}({attrs})'.format(
            name=type(self).__name__,
            attrs=self._attr_string)

class AnnotationSet:
    """
    A set of Annotations from a given object (includes the object)

    Author:  Anshul Kharbanda
    Created: 11 - 6 - 2017
    """
    def __init__(self, obj, ats):
        """
        Initializes the AnnotationSet with the given object and annotations

        :param obj: the object to which the annotations are bound to
        :param ats: the annotations in the list
        """
        self._obj = obj
        self._ats = ats

    @property
    def obj(self):
        """
        The original objects to which the annotations are bound to
        """
        return self._obj

    def __iter__(self):
        """
        Returns the iterator
        """
        return iter(self._ats)

    def __len__(self):
        """
        The length of the ats list
        """
        return len(self._ats)

    def __getitem__(self, index):
        """
        Returns the item at the given index
        """
        return self._ats[index]

    def __eq__(self, other):
        """
        Tests equality between AnnotationSet objects

        :param other: the other AnnotationSet
        """
        return self._obj == other._obj and self._ats == other._ats

    def __str__(self):
        """
        String representation of instance
        """
        return str(self._ats)

    def __repr__(self):
        """
        Detailed string representation of instance
        """
        return 'AnnotationSet({obj}, {ats})'.join(obj=str(self._obj), ats=str(self._ats))

def get_all(obj):
    """
    Gets all annotations attached to the given object

    :param obj: the object to retrieve annotations from

    :return: all annotations from the given object
    """
    return AnnotationSet(obj,
            { member for member in obj.__dict__.values()
                if isinstance(member, AnnotationType) })

def create(name, attributes=dict()):
    """
    Creates an Annotation or AnnotationType from the given info

    :param name: the name of the annotation
    :param attributes: the attributes of the annotation
    """
    AtType = type(name, (AnnotationType,), dict(_attributes=attributes))
    return AtType if len(attributes) > 0 else AtType()

def Annotation(cskl):
    """
    Decorator function for a Class Skeleton

    :param cskl: the class skeleton to create an annotation from

    :return: Annotation or AnnotationType from the given cskl
    """
    # Prefix for attribute
    attr_prefix = '_attr_'

    # Extract relevant info
    name = cskl.__name__
    attributes = {name[len(attr_prefix):]:typ # Trim prefix
                    for name,typ in cskl.__dict__.items() # Get keys
                    if name.startswith(attr_prefix)} # Filter by prefix

    # Create AnnotationType
    return create(name, attributes)
