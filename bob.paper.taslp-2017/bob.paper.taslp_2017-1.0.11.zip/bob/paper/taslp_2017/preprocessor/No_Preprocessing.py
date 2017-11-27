#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""No preprocessing: returns the speech signal as it is"""

import numpy
import logging

from bob.bio.spear.preprocessor.Base import Base
from bob.bio.base.preprocessor import Preprocessor

logger = logging.getLogger("bob.paper.taslp_2017")


class No_Preprocessing(Base):
  def __init__(
      self,
      **kwargs
  ):
      # call base class constructor with its set of parameters
    Preprocessor.__init__(
        self,
    )

  def __call__(self, input_signal, annotations=None):
    """labels speech (1) and non-speech (0) parts of the given input wave file using 4Hz modulation energy and energy
        Input parameter:
           * input_signal[0] --> rate
           * input_signal[1] --> signal
    """
    rate = input_signal[0]
    data = input_signal[1]
    labels = numpy.ones(len(data))
#   returns data as it is, i.e., no preprocessing.
    return rate, data, labels
