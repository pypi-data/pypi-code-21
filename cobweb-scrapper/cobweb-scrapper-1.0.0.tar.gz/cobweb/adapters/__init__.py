from abc import abstractmethod, ABCMeta


class AbstractAdapter(metaclass=ABCMeta):

    @abstractmethod
    def invoke(self, url: str):
        raise NotImplementedError("Method invocation on an abstract class")

    @abstractmethod
    def send(self, url: str):
        raise NotImplementedError("Method invocation on an abstract class")

    @abstractmethod
    def prepare_request(self, url: str):
        raise NotImplementedError("Method invocation on an abstract class")

    @abstractmethod
    def process_response(self, response):
        raise NotImplementedError("Method invocation on an abstract class")
