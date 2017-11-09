#!/usr/bin/env python
#
# test_widget_number.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import numpy as np

from . import (run_with_wx, simtext, simclick, addall)

import fsleyes_props               as props
import fsleyes_widgets.floatspin   as floatspin
import fsleyes_widgets.floatslider as floatslider


def setup_module():
    props.initGUI()


class MyObj(props.HasProperties):

    myinto  = props.Int()
    myrealo = props.Real()

    myintc  = props.Int( minval=0,   maxval=100, clamped=True)
    myrealc = props.Real(minval=0.0, maxval=1.0, clamped=True)


def  test_widget_number(): run_with_wx(_test_widget_number)
def _test_widget_number(parent):

    sim = wx.UIActionSimulator()

    obj = MyObj()

    myinto  = props.makeWidget(parent, obj, 'myinto')
    myrealo = props.makeWidget(parent, obj, 'myrealo')
    myintc  = props.makeWidget(parent, obj, 'myintc')
    myrealc = props.makeWidget(parent, obj, 'myrealc', slider=True, spin=False)

    assert isinstance(myinto,  floatspin.FloatSpinCtrl)
    assert isinstance(myrealo, floatspin.FloatSpinCtrl)
    assert isinstance(myintc,  floatslider.SliderSpinPanel)
    assert isinstance(myrealc, floatslider.FloatSlider)

    addall(parent, [myinto, myrealo, myintc, myrealc])

    obj.myinto  = 50
    obj.myrealo = 10
    obj.myintc  = 25
    obj.myrealc = 0.5

    assert myinto .GetValue() == 50
    assert myrealo.GetValue() == 10
    assert myintc .GetValue() == 25
    assert np.isclose(myrealc.GetValue(), 0.5)

    simtext( sim, myinto .textCtrl,          '10')
    simtext( sim, myrealo.textCtrl,          '243.56')
    simtext( sim, myintc.spinCtrl.textCtrl,  '99')
    simclick(sim, myrealc,                   pos=(0.75, 0.5))

    assert obj.myinto == 10
    assert np.isclose(obj.myrealo, 243.56)
    assert obj.myintc == 99
    assert abs(obj.myrealc - 0.75) <= 0.05
