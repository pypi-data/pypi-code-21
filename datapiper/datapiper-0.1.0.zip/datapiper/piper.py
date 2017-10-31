"""The data piper implementation"""

import logging
from .exceptions import PipelineValidationException
from .tasks import beginning, task, ending


logging.basicConfig()


class Piper(object):
   "data pipeline runner"

   logger = logging.getLogger("piper")
   logger.setLevel(logging.WARN)

   def __init__(self, operations=None, source=None, sink=None, context=None):
      "initialize the piper and (optionally) the pipeline"

      self.source = source
      self.operations = operations
      self.sink = sink

      # pipeline global context
      self.context = context or {}

      # construct the coroutine pipeline, last task first
      self.tasks = []

      try:
         self.validate_pipeline()
      except PipelineValidationException:
         self.logger.warn("invalid or missing pipeline; use create_pipeline() to create")
      else:
         self.create_pipeline(operations, source=source, sink=sink)


   def validate_pipeline(self):
      "raise PipelineValidationException on invalid pipeline"

      errs = []

      if not self.operations:
         errs.append("no data operations given")

      if not (self.source or self.sink):
         errs.append("no source or sink given")

      if self.source and self.sink:
         errs.append("cannot use both a data source and a sink")

      if errs:
         raise PipelineValidationException("invalid pipeline: %s" % ', '.join(errs))


   def __str__(self):
      src = "source > " if self.source else ""
      sink = " > sink" if self.sink else ""
      out = src +  ' > '.join([dataop.__name__ for dataop in self.operations]) + sink
      return "pipe: " + out


   def create_pipeline(self, operations, source=None, sink=None):
      "create and initialize the pipeline"

      try:
         self.validate_pipeline()
      except PipelineValidationException as exc:
         self.logger.error(exc)
         return

      self.operations = operations
      self.end = ending(self.context, sinkcallable=sink)
      successor = self.end

      for taskop in self.operations[::-1]:
         tsk = task(taskop, successor, self.context)
         self.tasks.insert(0, tsk)
         successor = tsk

      if not source:
         self.begin = beginning(self.tasks[0], self.context)


   def __iter__(self):
      "provide an iterator for reading the pipeline"
      for data in self.source:
         # push each record into the pipeline
         self.tasks[0].send(data)
         # and yield the result
         yield self.context["result"]


   def send(self, data):
      "emulate the coroutine protocol, passing data to the pipeline start"
      self.begin.send(data)
