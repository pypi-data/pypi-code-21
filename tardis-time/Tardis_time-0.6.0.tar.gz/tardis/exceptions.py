class TardisError(Exception):
    """
    Base Tardis Exception class
    """

    def __init__(self, msg):
        self.msg = str(msg)
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg


class TardisInvalidTimezone(TardisError):
    """
    Exception that is raised when an invalid timezone is passed in.
    """
    pass


class TardisInvalidDatetime(TardisError):
    """
    Exception that is raised when an improper datetime object is passed
    in.
    """
    pass
