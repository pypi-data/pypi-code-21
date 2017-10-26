#!/usr/bin/env python
#
# test_widget_bounds.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import numpy as np

import fsleyes_props               as props
import fsleyes_widgets.rangeslider as rangeslider


from . import (run_with_wx, simtext, simclick, addall, realYield)

import logging
logging.basicConfig()

logging.getLogger('fsleyes_props').setLevel(logging.DEBUG)


def setup_module():
    props.initGUI()


class MyObj(props.HasProperties):

    mybounds = props.Bounds(ndims=1)


def  test_widget_bounds(): run_with_wx(_test_widget_bounds)
def _test_widget_bounds(parent):

    sim = wx.UIActionSimulator()

    obj = MyObj()

    obj.mybounds.xlim = 0, 100
    obj.mybounds.x    = 25, 75

    slispin = props.makeWidget(parent, obj, 'mybounds', showLimits=False)
    sli     = props.makeWidget(parent, obj, 'mybounds', showLimits=False,
                               spin=False, slider=True)

    addall(parent, [slispin, sli])

    slispin = slispin.GetChildren()[0]
    sli     = sli    .GetChildren()[0]

    assert isinstance(slispin, rangeslider.RangeSliderSpinPanel)
    assert isinstance(sli,     rangeslider.RangePanel)

    assert np.all(np.isclose(slispin.GetRange(), (25, 75)))
    assert np.all(np.isclose(sli.GetRange(),     (25, 75)))

    simclick(sim, slispin.lowSlider, pos=(0.5, 0.5))
    val = slispin.GetLow()
    assert np.isclose(obj.mybounds.xlo, val)
    assert np.isclose(sli.GetLow(),     val)

    simclick(sim, slispin.highSlider, pos=(0.9, 0.5))
    val = slispin.GetHigh()
    assert np.isclose(obj.mybounds.xhi, val)
    assert np.isclose(sli.GetHigh(),    val)

    simclick(sim, sli.lowWidget, pos=(0.1, 0.5))
    val = sli.GetLow()
    assert np.isclose(obj.mybounds.xlo, val)
    assert np.isclose(slispin.GetLow(), val)

    simclick(sim, sli.highWidget, pos=(0.6, 0.5))
    val = sli.GetHigh()
    assert np.isclose(obj.mybounds.xhi,  val)
    assert np.isclose(slispin.GetHigh(), val)

    obj.mybounds.x = (66, 99)
    assert np.all(np.isclose(slispin.GetRange(), (66, 99)))
    assert np.all(np.isclose(sli.GetRange(),     (66, 99)))
