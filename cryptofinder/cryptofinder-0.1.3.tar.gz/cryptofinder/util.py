def datetime_formatted(dt):
  return {
    'date': dt.strftime("%Y-%m-%d"),
    'time': dt.strftime("%I:%M:%S %p")
  }