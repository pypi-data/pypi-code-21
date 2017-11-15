# Launch the application. This is a crude template, designed to import nothing
# except what the application needs.
import sys

try:
    from _module_ import _func_
    ec = _func_() or 0
except SystemExit as e:
    ec = e.code

with open(_output_file_, 'w', encoding='utf-8') as f:
    f.write(repr({name: getattr(mod, '__file__', None)
                  for name, mod in sys.modules.items()}))

sys.exit(ec)
