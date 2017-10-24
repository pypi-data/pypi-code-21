# Decision tree operators
_OPERATORS = {
  "is": lambda context, value: context == value,
  ">=": lambda context, value: context >= value,
  "<": lambda context, value: context < value,
  "[in[": lambda context, value:
          context >= value[0] and context < value[1] if value[0] < value[1]
          else context >= value[0] or context < value[1]
}
