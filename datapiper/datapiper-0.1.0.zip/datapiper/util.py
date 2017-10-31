"Utilities"


def coroutine(func):
   "convenience decorator"

   def wrapper(*args, **kw):
      "initialize the coroutine so it's ready for use"
      coro = func(*args, **kw)
      coro.send(None) # same as calling next() works in Python 2/3
      return coro
   return wrapper
