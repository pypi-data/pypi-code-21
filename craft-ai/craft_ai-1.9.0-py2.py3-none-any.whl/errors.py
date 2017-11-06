class CraftAiError(Exception):
  """Base class for exceptions in the craft ai client."""
  def __init__(self, message):
    self.message = message
    super(CraftAiError, self).__init__(message)

  def __str__(self):
    return repr(self.message)


class CraftAiUnknownError(CraftAiError):
  """Raised when an unknown error happens in the craft ai client."""
  def __init__(self, message):
    self.message = "".join(("Unknown error occured. ", message))
    super(CraftAiUnknownError, self).__init__(message)


class CraftAiNetworkError(CraftAiError):
  """Raised when a network error happens between the client and craft ai"""
  def __init__(self, message):
    self.message = "".join(("Network issue: ", message))
    super(CraftAiNetworkError, self).__init__(message)


class CraftAiCredentialsError(CraftAiError):
  """Raised when the given credentials for a request or the global config
  aren't valid """
  def __init__(self, message):
    self.message = "".join((
      "Credentials error: ",
      message
    ))
    super(CraftAiCredentialsError, self).__init__(message)


class CraftAiInternalError(CraftAiError):
  """Raised when an Internal Server Error (500) happens on craft ai's side"""
  def __init__(self, message):
    self.message = "".join(("Internal error occured", message))
    super(CraftAiInternalError, self).__init__(message)


class CraftAiBadRequestError(CraftAiError):
  """Raised when the asked request is not valid for craft ai's API"""
  def __init__(self, message):
    self.message = "".join(("Bad request: ", message))
    super(CraftAiBadRequestError, self).__init__(message)


class CraftAiNotFoundError(CraftAiError):
  """Raised when craft ai answers with a Not Found Error (404)"""
  def __init__(self, message, obj="URL"):
    self.message = "".join((obj, " not found: ", message))
    super(CraftAiNotFoundError, self).__init__(message)


class CraftAiDecisionError(CraftAiError):
  """Raised when some issue is encountered when trying to find a decision"""
  def __init__(self, message):
    self.message = "".join(("Unable to take decision, ", message))
    super(CraftAiDecisionError, self).__init__(message)


class CraftAiNullDecisionError(CraftAiDecisionError):
  """Raised when some issue is encountered when trying to find a decision"""
  def __init__(self, message):
    self.message = "".join(("Unable to take decision, ", message))
    super(CraftAiNullDecisionError, self).__init__(message)


class CraftAiTimeError(CraftAiError):
  """Raised when trying to create a time object fails"""
  def __init__(self, message):
    self.message = "".join(("Can't create time object: ", message))
    super(CraftAiTimeError, self).__init__(message)

class CraftAiTokenError(CraftAiError):
  """Raised when the given token is invalid"""
  def __init__(self, message):
    self.message = "".join(("Invalid Token: ", message))
    super(CraftAiTokenError, self).__init__(message)

class CraftAiLongRequestTimeOutError(CraftAiError):
  """Raised when a request takes a long time"""
  def __init__(self, message=None):
    self.message = message if message is None else (
      "Request timed out because the computation is not finished, please try again")
    super(CraftAiLongRequestTimeOutError, self).__init__(message)
