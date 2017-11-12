from abc import abstractmethod, ABCMeta


class AbstractAdapter(metaclass=ABCMeta):

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Method invocation on an abstract class")

    @abstractmethod
    def prepare_request(self, *args, **kwargs):
        raise NotImplementedError("Method invocation on an abstract class")

    @abstractmethod
    def process_response(self, response, *args, **kwargs):
        raise NotImplementedError("Method invocation on an abstract class")
