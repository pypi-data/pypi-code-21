class RumetrException (BaseException):
    pass


class RumetrDeveloperNotFound(RumetrException):
    pass


class RumetrComplexNotFound(RumetrException):
    pass


class RumetrHouseNotFound(RumetrException):
    pass


class RumetrApptNotFound(RumetrException):
    pass


class Rumetr404Exception(RumetrException):
    pass


class Rumetr403Exception(RumetrException):
    pass


class RumetrBadServerResponseException(RumetrException):
    pass
