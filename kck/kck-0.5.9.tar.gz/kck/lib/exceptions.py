import traceback


class BaseKCKException(Exception):

    msg = None

    def failure_info_dict(self):
        ret = dict(
            error=dict(
                name=self.__class__.__name__,
                args=self.args,
                traceback=traceback.format(self.__traceback__)
            )
        )

        if self.msg is not None:
            ret["error"]["message"] = self.msg

        return ret


class KCKKeyNotSetException(BaseKCKException):
    key = None
    tbl = None

    def __init__(self, key, tbl, msg="primer found, but compute() returned no results"):
        self.key = key
        self.tbl = tbl
        self.msg = msg


class KCKKeyNotRegistered(BaseKCKException):
    key = None

    def __init__(self, key):
        self.key = key


class UnexpectedPrimerType(BaseKCKException):
    pass


class KCKUnknownKey(BaseKCKException):
    key = None

    def __init__(self, key):
        self.key = key


class PrimerComputerReturnedNoResults(BaseKCKException):
    pass


class AuthTokenInvalid(BaseKCKException):
    msg = "Invalid authorization token"
    token = None

    def __init__(self, token):
        self.token = token


class AuthTokenExpired(BaseKCKException):
    msg = "Expire authorization token"
    token = None

    def __init__(self, token):
        self.token = token


class AuthHeaderNotPresent(BaseKCKException):
    msg = "Authorization header not present"


class AuthLoginUnknownUser(BaseKCKException):
    msg = "Unknown user or bad password"
    username = None

    def __init__(self, username):
        self.username = username