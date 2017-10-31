"Predefined tasks"

from .exceptions import PipelineTaskException
from .util import coroutine


@coroutine
def beginning(successor, context):
   "pipeline start task"
   while True:
      data = yield
      successor.send(data)


@coroutine
def task(operator, successor, context):
   "regular pipeline worker task"
   while True:
      data = yield
      try:
         result = operator(context, data)
      except Exception as exc:
         raise PipelineTaskException("task %s failed: %s" % (operator.__name__, exc))
      else:
         successor.send(result)


@coroutine
def ending(sinkcontext, sinkcallable=None):
   "pipeline end task"

   def context_sink(data):
      "a sink that just writes result to the pipeline context"
      sinkcontext["result"] = data

   def callable_sink(data):
      "a sink that also writes the result to a given callable"
      sinkcontext["result"] = data
      sinkcallable(data)

   sink = callable_sink if sinkcallable else context_sink

   while True:
      finaldata = yield
      try:
         sink(finaldata)
      except Exception as exc:
         raise PipelineTaskException("sink callable failed: %s" % exc)
