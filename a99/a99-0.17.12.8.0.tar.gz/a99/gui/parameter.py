__all__ = ["Parameter", "Parameters"]


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from collections import OrderedDict


class Parameters(object):
    """
    Collection of parameters (for GUI purposes only)

    Arguments:
      specs -- [(name, {...}), ...] see Parameter.FromSpec() for full documentation.
    """
    def __init__(self, specs=[]):
        # List of Parameter objects
        self.params = []
        self._FromSpecs(specs)

    def __len__(self):
        return len(self.params)

    def __iter__(self):
        return self.params.__iter__()

    def _FromSpecs(self, specs):
        """
        Populates _params using specification

        Arguments:
          specs -- either:
            (a) list as [(name, {...}), ...] (see Parameter.FromSpec() for further information)
            (b) dictionary as {"name": value, ...}
        """

        if isinstance(specs, dict):
            specs_ = []
            for name, value in specs.items():
                specs_.append((name, {"value": value}))
        else:
            specs_ = specs
        for spec in specs_:
            self.params.append(Parameter(spec))

    def AddToLayout(self, layout):
        """
        Arguments:
          layout -- a QFormLayout instance
        """
        for param in self.params:
            widget = param.RenderWidget()
            layout.addRow(param.caption, widget)

    def UpdateFromWidgets(self):
        for param in self.params:
            try:
                param.UpdateValueFromWidget()
            except Exception as e:
                raise
                # raise type(e)("Error in '%s': %s" % (param.name, +str(e)), None, sys.exc_info()[2]


    def GetKwargs(self):
        ret = OrderedDict()
        for param in self.params:
            ret[param.name] = param.value
        return ret


class Parameter(object):
    """Definition of a single parameter, with QWidget rendering facility"""
    def __init__(self, spec=None):
        self.name = None
        self.caption = None
        self.toolTip = None
        self.type = None
        self.value = None
        self.widget = None  # Widget that will edit the thing
        if spec is not None:
            self.FromSpec(spec)

    def FromSpec(self, spec):
        """
        Args:
          spec: (name, {...}), or Parameter object

        Dict keys:
          "caption" -- (optional) text for label in editor. Defaults to the
                 keyword argument name
          "toolTip" (optional)
          "type" -- (optional, defaults to type("value") or int if "value" is
              not specified. Accepts:
                - int
                - float
                - str
                - bool
                - list
          "value" -- (optional) defaults to 1 if numeric, False if bool,
               "" if str

        """
        if isinstance(spec, Parameter):
            self.name = spec.name
            self.caption = spec.caption if spec.caption is not None else spec.name
            self.toolTip = spec.toolTip if spec.toolTip is not None else ""
            self.type = spec.type if spec.type is not None else type(spec.value) if spec.value is not None else int
            self.value = spec.value
        else:
            self.name, d = spec
            self.caption = d.get("caption", self.name)
            self.toolTip = d.get("toolTip", "")
            t = self.type = d.get("type", type(d["value"]) if "value" in d else int)
            if not t in (int, float, bool, str, list):
                raise TypeError("Invalid type: '{0!s}'".format(t.__name__))
            self.value = d.get("value")

        if self.value is None:
            self.value = 0 if self.type == int else \
                0. if self.type == float else \
                False if self.type == bool else ""

    def RenderWidget(self):
        """Returns a QWidget subclass instance. Exact class depends on self.type"""
        t = self.type
        if t == int:
            ret = QSpinBox()
            ret.setMaximum(999999999)
            ret.setValue(self.value)
        elif t == float:
            ret = QLineEdit()
            ret.setText(str(self.value))
        elif t == bool:
            ret = QCheckBox()
            ret.setChecked(self.value)
        else:  # str, list left
            ret = QLineEdit()
            ret.setText(str(self.value))
        self.widget = ret
        return ret

    def UpdateValueFromWidget(self):
        t, w = self.type, self.widget
        if t == int:
            self.value = int(w.value())
        elif t == float:
            self.value = float(eval(str(w.text())))
        elif t == bool:
            self.value = w.isChecked()
        elif t == str:
            self.value = str(w.text())
        else:  # list
            _value = eval(str(w.text()))
            if not isinstance(_value, list):
                raise ValueError("Parameter '{}' must evaluate to a list".format(self.name))
            self.value = _value
