import typing


class ResourceExistsError(NameError):
    """
    Exception raised when a proxy with that name already exists in the pipeline.
    """
    pass


class ResourceNotFoundError(NameError):
    """
    Exception raised when a proxy with that name already exists in the pipeline.
    """
    pass


class ResourceManager(object):
    """
    Manager class for pipelines.
    """
    def __init__(self, cls: type):
        """
        Initialize the manager.
        """
        self.cls = cls
        self.stack = {}

    def new(self, name: str, *args, **kwargs) -> object:
        """
        Create a new pipeline in the manager.

        :param name: the name to give the pipeline.
        :param worker: the worker object for the pipeline.
        :returns: a pipeline object.
        """
        if name in self.stack:
            raise ResourceExistsError(name)

        result = self.cls(*args, **kwargs)
        self.stack[name] = result
        return result

    def save(self, name: str, item: object) -> object:
        if name in self.stack:
            raise ResourceExistsError(name)

        self.stack[name] = item
        return item

    def save_all(self, items: typing.Dict[str, object]):
        for name, item in items.items():
            self.save(name, item)

    def resolve(self, name: str) -> object:
        """
        Get an existing pipeline object.

        :param name: the name of the pipeline.
        :returns: the pipeline object.
        """
        try:
            return self.stack[name]
        except KeyError:
            raise ResourceNotFoundError(name)
