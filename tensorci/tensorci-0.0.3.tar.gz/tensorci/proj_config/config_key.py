import re
from slugify import slugify
from importlib import import_module


class ConfigKey(object):

  def __init__(self, value=None, required=False, validation='truthy'):
     self.value = value
     self.required = required
     self.validation = validation

  def set_value(self, val):
    self.value = val

  def validate(self):
    if type(self.validation).__name__ == 'function':
      return self.validation()

    if not hasattr(self, self.validation):
      self.validation = 'truthy'

    return getattr(self, '{}_validator'.format(self.validation))()

  # --- Validators ---

  def truthy_validator(self):
    if not self.required and not self.value:
      return True

    return bool(self.value)

  def slug_validator(self):
    if not self.required and not self.value:
      return True

    return self.value == slugify(self.value, separator='-', to_lower=True)

  def url_validator(self):
    if not self.required and not self.value:
      return True

    if self.required and not self.value:
      return False

    url_regex = re.compile(
      r'^(?:http)s?://'  # http:// or https://
      r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
      r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
      r'(?::\d+)?'  # optional port
      r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(url_regex, self.value) is not None

  def mod_function_validator(self):
    if not self.required and not self.value:
      return True

    if self.required and not self.value:
      return False

    module_str, func_str = self.value.split(':')

    if not module_str:
      return False

    if not func_str:
      return False

    try:
      module = import_module(module_str)
    except:
      return False

    if not module:
      return False

    if not hasattr(module, func_str):
      return False

    func = getattr(module, func_str)

    return type(func).__name__ == 'function'