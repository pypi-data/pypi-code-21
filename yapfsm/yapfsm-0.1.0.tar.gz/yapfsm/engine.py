"""Actual FSM implementation."""

# coding=utf-8

import typing

from collections import defaultdict

from .exceptions import ConfigurationError, StateTransitionError

from . import transition

__all__ = [
  'TransitionType',
  'MachineConfiguration',
  'Machine'
]


TransitionType = typing.TypeVar('TransitionType')


def first_true(iterable, default=False, pred=None):
  """Returns the first true value in the iterable.

  If no true value is found, returns *default*

  If *pred* is not None, returns the first item
  for which pred(item) is true.

  """
  # first_true([a,b,c], x) --> a or b or c or x
  # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
  return next(filter(pred, iterable), default)


class MachineConfiguration(typing.Generic[transition.StateType, TransitionType]):
  """
  Immutable FSM configuration, can be shared between many state machines.
  Stores all possible transitions.
  """
  def __init__(self):
    super().__init__()
    self.transitions = defaultdict(list)
    """Maps state to list of legal transitions."""
    self.flat_transitions = set()
    """All transitions in set. Used to detect duplicate transitions."""

  def add_transition(self, trans: TransitionType):
    """
    Adds transition to this configuration.

    :raises ConfigurationError: When such transition exists.
    """
    if trans in self.flat_transitions:
      raise ConfigurationError("Transition already present")
    self.transitions[trans.from_state].append(trans)
    self.flat_transitions.add(trans)

  def get_transitions_from_state(
      self,
      from_state: transition.StateType
  ) -> typing.Iterable[transition.Transition]:
    """
    Returns all possible transitions from state.
    :param from_state: State for which to find transitions. \
    """
    global_transitions = self.transitions.get(None, list())
    local_transitions = self.transitions.get(from_state, list())
    return sorted(global_transitions + local_transitions)

  def transition_by_name(
      self,
      transition_name: str,
      from_state: transition.StateType
  ) -> TransitionType:
    """
    Gets transition by name.
    """
    def match_by_name(trans: TransitionType):
      """Predicate to find transition"""
      return trans.transition_name == transition_name
    result = first_true(
      self.get_transitions_from_state(from_state), None, match_by_name
    )
    if result is None:
      raise ConfigurationError("No such transition")
    return result


class Machine(typing.Generic[transition.StateType, transition.ContextType]):
  """Mutable FSM machine."""

  def __init__(
      self,
      initial_state: transition.StateType,
      machine: MachineConfiguration,
      context: transition.ContextType
  ):
    self.machine = machine
    self.context = context
    self.current_state = initial_state

  def update_state(self, new_state):
    """
    Updates state of the machine. If you need to do some custom action on state update
    do it here.
    """
    self.current_state = new_state

  def perform_transition(self, transition_name: str, extra_args: dict = None):
    """Performs state transition from current state."""
    try:
      trans = self.machine.transition_by_name(transition_name, self.current_state)
    except ConfigurationError as exc:
      raise StateTransitionError(exc.message) from exc
    next_state = trans.transition(
      machine=self.machine,
      from_state=self.current_state,
      context=self.context,
      extra_args=extra_args
    )
    self.update_state(next_state)

  def get_possible_transitions(
      self,
      extra_args: dict = None
  ) -> typing.Iterable[transition.TransitionOption]:
    """
    Returns all transitions for current state, along with information if transition
    is currently legal.
    """
    return [
      t.can_transition(
        machine=self.machine,
        from_state=self.current_state,
        context=self.context,
        extra_args=extra_args
      )
      for t in self.machine.get_transitions_from_state(self.current_state)
    ]
