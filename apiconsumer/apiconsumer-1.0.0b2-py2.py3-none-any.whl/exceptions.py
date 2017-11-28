class ApiConsumerException(Exception):
    pass


class ApiConsumerRequestException(ApiConsumerException):
    pass


class ApiConsumerResponseError(ApiConsumerException):
    pass

