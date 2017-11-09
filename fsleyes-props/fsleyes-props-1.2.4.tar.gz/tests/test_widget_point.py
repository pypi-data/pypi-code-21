#!/usr/bin/env python
#
# test_widget_point.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import numpy as np

import fsleyes_props               as props
import fsleyes_widgets.floatslider as floatslider


from . import (run_with_wx, simtext, simclick, addall, realYield)


def setup_module():
    props.initGUI()


class MyObj(props.HasProperties):

    mypointi = props.Point(ndims=2, real=False)
    mypointf = props.Point(ndims=2)


def  test_widget_point(): run_with_wx(_test_widget_point)
def _test_widget_point(parent):

    sim = wx.UIActionSimulator()
    obj = MyObj()

    obj.mypointi.setLimits(0, 0, 100)
    obj.mypointi.setLimits(1, 0, 100)
    obj.mypointf.setLimits(0, 0, 100)
    obj.mypointf.setLimits(1, 0, 100)

    obj.mypointi.x = 25
    obj.mypointi.y = 75
    obj.mypointf.x = 20
    obj.mypointf.y = 80

    mypointi = props.makeWidget(parent, obj, 'mypointi', showLimits=False)
    mypointf = props.makeWidget(parent, obj, 'mypointf', showLimits=False)

    xi, yi = mypointi.GetChildren()
    xf, yf = mypointf.GetChildren()

    for s in [xi, yi, xf, yf]:
        assert isinstance(s, floatslider.SliderSpinPanel)

    assert xi.GetValue() == 25
    assert yi.GetValue() == 75
    assert xf.GetValue() == 20
    assert yf.GetValue() == 80

    addall(parent, [mypointi, mypointf])

    tests = [
        (xi, 'mypointi', 'x'),
        (yi, 'mypointi', 'y'),
        (xf, 'mypointf', 'x'),
        (yf, 'mypointf', 'y')]


    for widget, prop, att in tests:
        val = np.random.randint(0, 100)
        setattr(getattr(obj, prop), att, val)
        realYield(2)
        assert np.isclose(widget.GetValue(), val)

        val = np.random.randint(0, 100)

        simclick(sim, widget.slider, pos=(val / 100.0, 0.5))

        assert abs(getattr(getattr(obj, prop), att) - val) < 10
