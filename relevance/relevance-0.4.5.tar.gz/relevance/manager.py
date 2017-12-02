"""
This module provides generic manager objects, that is, objects that can create or save objects
of a specific type and resolve them later.
"""

import typing


class ResourceManager(object):
    """
    The manager class can create, store and resolve objects of a specific type
    later, much like a dictionary, but with additional functionality such as
    duplicates handling.
    """
    def __init__(self, cls: type) -> None:
        """
        :param cls: the type of object that the manager manages.
        """
        self.cls = cls
        self.stack: typing.Dict[str, object] = {}

    def new(self, _name: str, *args, **kwargs) -> object:
        """
        Create a new object in the manager.

        This method basically instantiate the object type defined when the manager
        is created using the arguments and keyword arguments specified. It then
        saves it into the manager stack and can be resolved later by its name.

        :param _name: the name to give the instance in the manager, must be unique.
        :param args: the arguments passed to the managed class initializer.
        :param kwargs: the keyword arguments passed to the managed class initializer.
        :return: an instance of the managed class.
        :raises: :class:`ResourceExistsError`: when the specified `name` already exists
            in the manager.
        """
        if _name in self.stack:
            raise ResourceExistsError(_name)

        result = self.cls(*args, **kwargs)
        self.stack[_name] = result
        return result

    def save(self, name: str, inst: object) -> object:
        """
        Save an instance in the manager.

        :param name: the name to give the instance in the manager, must be unique.
        :param inst: the instance of the object to save.
        :return: the managed instance object.
        :raises: :class:`ResourceExistsError`: when the specified `name` already exists
            in the manager.
        """
        if name in self.stack:
            raise ResourceExistsError(name)

        self.stack[name] = inst
        return inst

    def save_all(self, insts: typing.Dict[str, object]):
        """
        Save multiple instances at once in the manager.

        This method is basically a the :meth:`save` method wrapped in a loop.

        :param insts: a dictionary of instances to save, with the key being the name
            to give the instance, and the value being the instance itself.
        :raises: :class:`ResourceExistsError`: when one of the specified entries
            has a name that already exists. This method is safe, so if the exception
            is raised, it can be assumed that none of the objects have been saved and
            the manager state has not been modified.
        """
        for name in insts:
            if name in self.stack:
                raise ResourceExistsError(name)

        for name, inst in insts.items():
            self.save(name, inst)

    def resolve(self, name: str) -> object:
        """
        Resolve an existing object instance.

        :param name: the name of the object to resolve.
        :return: the managed object with that name.
        :raises: :class:`ResourceNotFoundError`: if the object has not been registered.
        """
        try:
            return self.stack[name]
        except KeyError:
            raise ResourceNotFoundError(name)


class ResourceExistsError(NameError):
    """
    This exception is raised when trying to save or create an object instance in a
    manager, when another object with the same name already exists in that manager.
    """
    pass


class ResourceNotFoundError(NameError):
    """
    This exception is raised when trying to resolve an object instance with a name
    that has not been registered in the manager.
    """
    pass
