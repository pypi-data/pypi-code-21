"""
All exceptions raised by yapfsm
"""

# coding=utf-8

__all__ = [
  "FSMError", "ConfigurationError", "StateTransitionError",
]


class FSMError(Exception):
  """Base exception."""
  def __init__(self, message):
    super().__init__()
    self.message = message


class ConfigurationError(FSMError):
  """Raised when FSM has configuration issues (e.g. duplicate transition)."""
  pass


class StateTransitionError(FSMError):
  """Raised when user requested illegal transition."""
  pass
