class ShellException(Exception):
    """Base exception class"""
    pass


class PromptError(ShellException):
    """Errors related to prompts"""
    pass


class RecvError(ShellException):
    """Errors when receiving data"""
    pass


class ResponseError(ShellException):
    """Invalid responses from shell"""
    pass
