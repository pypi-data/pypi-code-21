from abc import ABCMeta, abstractmethod

class Storer(object):
  """
  Abstract storer class
  """
  __metaclass__ = ABCMeta

  @abstractmethod
  def store(self, result_dict):
    """
    Given a `result_dict` with complete series and episode info, store it
    accordingly
    """
    pass # Leave up to implementation
