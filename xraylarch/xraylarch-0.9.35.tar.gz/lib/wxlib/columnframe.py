#!/usr/bin/env python
"""

"""
import os
import numpy as np
np.seterr(all='ignore')

from functools import partial

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.agw.flatnotebook as fnb
from wxmplot import PlotPanel
from wxutils import (SimpleText, FloatCtrl, pack, Button,
                     Choice,  Check, MenuItem, GUIColors,
                     CEN, RCEN, LCEN, FRAMESTYLE, Font)

import larch
from larch import Group
from larch.utils.strutils import fix_varname, file2groupname

CEN |=  wx.ALL
FNB_STYLE = fnb.FNB_NO_X_BUTTON|fnb.FNB_SMART_TABS
FNB_STYLE |= fnb.FNB_NO_NAV_BUTTONS|fnb.FNB_NODRAG


XPRE_OPS = ('', 'log(', '-log(')
YPRE_OPS = ('', 'log(', '-log(')
ARR_OPS = ('+', '-', '*', '/')

YERR_OPS = ('Constant', 'Sqrt(Y)', 'Array')
CONV_OPS  = ('Lorenztian', 'Gaussian')

DATATYPES = ('raw', 'xas')

class EditColumnFrame(wx.Frame) :
    """Edit Column Labels for a larch grouop"""
    def __init__(self, parent, group, on_ok=None):

        self.group = group
        self.on_ok = on_ok
        wx.Frame.__init__(self, None, -1, 'Edit Array Names',
                          style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)

        self.SetFont(Font(10))
        sizer = wx.GridBagSizer(4, 4)

        self.SetMinSize((600, 600))

        self.wids = {}
        cind = SimpleText(self, label='Column')
        cold = SimpleText(self, label='Current Name')
        cnew = SimpleText(self, label='Enter New Name')
        cret = SimpleText(self, label='  Result   ', size=(150, -1))
        cinfo = SimpleText(self, label='   Data Range')

        ir = 0
        sizer.Add(cind,  (ir, 0), (1, 1), LCEN, 3)
        sizer.Add(cold,  (ir, 1), (1, 1), LCEN, 3)
        sizer.Add(cnew,  (ir, 2), (1, 1), LCEN, 3)
        sizer.Add(cret,  (ir, 3), (1, 1), LCEN, 3)
        sizer.Add(cinfo, (ir, 4), (1, 1), LCEN, 3)

        for i, name in enumerate(group.array_labels):
            ir += 1
            cind = SimpleText(self, label='  %i ' % (i+1))
            cold = SimpleText(self, label=' %s ' % name)
            cret = SimpleText(self, label=fix_varname(name), size=(150, -1))
            cnew = wx.TextCtrl(self,  value=name, size=(150, -1))
            cnew.Bind(wx.EVT_KILL_FOCUS, partial(self.update, index=i))
            cnew.Bind(wx.EVT_CHAR, partial(self.update_char, index=i))
            cnew.Bind(wx.EVT_TEXT_ENTER, partial(self.update, index=i))

            # cnew.Bind(wx.EVT_TEXT,       partial(self.update3, index=i))

            arr = group.data[i,:]
            info_str = " [ %8g : %8g ] " % (arr.min(), arr.max())
            cinfo = SimpleText(self, label=info_str)
            self.wids[i] = cnew
            self.wids["ret_%i" % i] = cret

            sizer.Add(cind,  (ir, 0), (1, 1), LCEN, 3)
            sizer.Add(cold,  (ir, 1), (1, 1), LCEN, 3)
            sizer.Add(cnew,  (ir, 2), (1, 1), LCEN, 3)
            sizer.Add(cret,  (ir, 3), (1, 1), LCEN, 3)
            sizer.Add(cinfo, (ir, 4), (1, 1), LCEN, 3)

        sizer.Add(Button(self, 'OK', action=self.onOK), (ir+1, 1), (1, 2), LCEN, 3)
        pack(self, sizer)
        self.Show()
        self.Raise()

    def update(self, evt=None, index=-1):
        newval = fix_varname(self.wids[index].GetValue())
        self.wids["ret_%i" % index].SetLabel(newval)

    def update_char(self, evt=None, index=-1):
        if evt.GetKeyCode() == wx.WXK_RETURN:
            self.update(evt=evt, index=index)
        evt.Skip()

    def onOK(self, evt=None):
        group = self.group
        array_labels = []
        for i in range(len(self.group.array_labels)):
            newname = self.wids["ret_%i" % i].GetLabel()
            array_labels.append(newname)

        if callable(self.on_ok):
            # print(' -> on_ok ', self.on_ok, array_labels)
            self.on_ok(array_labels)
        self.Destroy()

class ColumnDataFileFrame(wx.Frame) :
    """Column Data File, select columns"""
    def __init__(self, parent, filename=None, groupname=None,
                 last_array_sel=None, read_ok_cb=None,
                 edit_groupname=True, _larch=None):
        self.parent = parent
        self._larch = _larch
        self.path = filename

        group = self.initgroup = self.read_column_file(self.path)

        self.subframes = {}
        self.workgroup  = Group(raw=group)
        for attr in ('path', 'filename', 'groupname', 'datatype',
                     'array_labels'):
            setattr(self.workgroup, attr, getattr(group, attr, None))

        arr_labels = [l.lower() for l in self.initgroup.array_labels]
        if self.workgroup.datatype is None:
            self.workgroup.datatype = 'raw'
            if ('energ' in arr_labels[0] or 'energ' in arr_labels[1]):
                self.workgroup.datatype = 'xas'

        self.read_ok_cb = read_ok_cb

        self.array_sel = {'xpop': '',  'xarr': None,
                          'ypop': '',  'yop': '/',
                          'yarr1': None, 'yarr2': None, 'use_deriv': False}

        if last_array_sel is not None:
            self.array_sel.update(last_array_sel)

        if self.array_sel['yarr2'] is None and 'i0' in arr_labels:
            self.array_sel['yarr2'] = 'i0'

        if self.array_sel['yarr1'] is None:
            if 'itrans' in arr_labels:
                self.array_sel['yarr1'] = 'itrans'
            elif 'i1' in arr_labels:
                self.array_sel['yarr1'] = 'i1'
        message = "Data Columns for %s" % group.filename
        wx.Frame.__init__(self, None, -1,
                          'Build Arrays from Data Columns for %s' % group.filename,
                          style=FRAMESTYLE)

        self.SetFont(Font(10))

        panel = wx.Panel(self)
        self.SetMinSize((600, 600))
        self.colors = GUIColors()

        # title row
        title = SimpleText(panel, message, font=Font(13),
                           colour=self.colors.title, style=LCEN)

        opts = dict(action=self.onUpdate, size=(120, -1))

        yarr_labels = self.yarr_labels = arr_labels + ['1.0', '0.0', '']
        xarr_labels = self.xarr_labels = arr_labels + ['<index>']

        self.xarr   = Choice(panel, choices=xarr_labels, **opts)
        self.yarr1  = Choice(panel, choices= arr_labels, **opts)
        self.yarr2  = Choice(panel, choices=yarr_labels, **opts)
        self.yerr_arr = Choice(panel, choices=yarr_labels, **opts)
        self.yerr_arr.Disable()

        self.datatype = Choice(panel, choices=DATATYPES, **opts)
        self.datatype.SetStringSelection(self.workgroup.datatype)


        opts['size'] = (50, -1)
        self.yop =  Choice(panel, choices=ARR_OPS, **opts)

        opts['size'] = (120, -1)

        self.use_deriv = Check(panel, label='use derivative',
                               default=self.array_sel['use_deriv'], **opts)

        self.xpop = Choice(panel, choices=XPRE_OPS, **opts)
        self.ypop = Choice(panel, choices=YPRE_OPS, **opts)

        opts['action'] = self.onYerrChoice
        self.yerr_op = Choice(panel, choices=YERR_OPS, **opts)
        self.yerr_op.SetSelection(0)

        self.yerr_const = FloatCtrl(panel, value=1, precision=4, size=(90, -1))

        ylab = SimpleText(panel, 'Y = ')
        xlab = SimpleText(panel, 'X = ')
        yerr_lab = SimpleText(panel, 'Yerror = ')
        self.xsuf = SimpleText(panel, '')
        self.ysuf = SimpleText(panel, '')

        self.xpop.SetStringSelection(self.array_sel['xpop'])
        self.ypop.SetStringSelection(self.array_sel['ypop'])
        self.yop.SetStringSelection(self.array_sel['yop'])
        if '(' in self.array_sel['ypop']:
            self.ysuf.SetLabel(')')

        ixsel, iysel, iy2sel = 0, 1, len(yarr_labels)-1
        if self.array_sel['xarr'] in xarr_labels:
            ixsel = xarr_labels.index(self.array_sel['xarr'])
        if self.array_sel['yarr1'] in arr_labels:
            iysel = arr_labels.index(self.array_sel['yarr1'])
        if self.array_sel['yarr2'] in yarr_labels:
            iy2sel = yarr_labels.index(self.array_sel['yarr2'])
        self.xarr.SetSelection(ixsel)
        self.yarr1.SetSelection(iysel)
        self.yarr2.SetSelection(iy2sel)


        bpanel = wx.Panel(panel)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        _ok    = Button(bpanel, 'OK', action=self.onOK)
        _cancel = Button(bpanel, 'Cancel', action=self.onCancel)
        _edit   = Button(bpanel, 'Edit Array Names', action=self.onEditNames)
        bsizer.Add(_ok)
        bsizer.Add(_cancel)
        bsizer.Add(_edit)
        _ok.SetDefault()
        pack(bpanel, bsizer)

        sizer = wx.GridBagSizer(4, 8)
        sizer.Add(title,     (0, 0), (1, 7), LCEN, 5)

        ir = 1
        sizer.Add(xlab,      (ir, 0), (1, 1), LCEN, 0)
        sizer.Add(self.xpop, (ir, 1), (1, 1), CEN, 0)
        sizer.Add(self.xarr, (ir, 2), (1, 1), CEN, 0)
        sizer.Add(self.xsuf, (ir, 3), (1, 1), CEN, 0)

        ir += 1
        sizer.Add(ylab,       (ir, 0), (1, 1), LCEN, 0)
        sizer.Add(self.ypop,  (ir, 1), (1, 1), CEN, 0)
        sizer.Add(self.yarr1, (ir, 2), (1, 1), CEN, 0)
        sizer.Add(self.yop,   (ir, 3), (1, 1), CEN, 0)
        sizer.Add(self.yarr2, (ir, 4), (1, 1), CEN, 0)
        sizer.Add(self.ysuf,  (ir, 5), (1, 1), CEN, 0)
        sizer.Add(self.use_deriv, (ir, 6), (1, 1), LCEN, 0)

        ir += 1
        sizer.Add(yerr_lab,      (ir, 0), (1, 1), LCEN, 0)
        sizer.Add(self.yerr_op,  (ir, 1), (1, 1), CEN, 0)
        sizer.Add(self.yerr_arr, (ir, 2), (1, 1), CEN, 0)
        sizer.Add(SimpleText(panel, 'Value:'), (ir, 3), (1, 1), CEN, 0)
        sizer.Add(self.yerr_const, (ir, 4), (1, 2), CEN, 0)

        ir += 1
        sizer.Add(SimpleText(panel, 'Data Type:'),  (ir, 0), (1, 1), LCEN, 0)
        sizer.Add(self.datatype,                    (ir, 1), (1, 2), LCEN, 0)

        ir += 1
        self.wid_groupname = wx.TextCtrl(panel, value=group.groupname,
                                         size=(240, -1))
        if not edit_groupname:
            self.wid_groupname.Disable()

        sizer.Add(SimpleText(panel, 'Group Name:'), (ir, 0), (1, 1), LCEN, 0)
        sizer.Add(self.wid_groupname,               (ir, 1), (1, 2), LCEN, 0)


        ir += 1
        sizer.Add(bpanel,     (ir, 0), (1, 5), LCEN, 3)

        pack(panel, sizer)

        self.nb = fnb.FlatNotebook(self, -1, agwStyle=FNB_STYLE)
        self.nb.SetTabAreaColour(wx.Colour(248,248,240))
        self.nb.SetActiveTabColour(wx.Colour(254,254,195))
        self.nb.SetNonActiveTabTextColour(wx.Colour(40,40,180))
        self.nb.SetActiveTabTextColour(wx.Colour(80,0,0))

        self.plotpanel = PlotPanel(self, messenger=self.plot_messages)
        textpanel = wx.Panel(self)
        ftext = wx.TextCtrl(textpanel, style=wx.TE_MULTILINE|wx.TE_READONLY,
                               size=(400, 250))

        ftext.SetValue(group.text)
        ftext.SetFont(Font(10))

        textsizer = wx.BoxSizer(wx.VERTICAL)
        textsizer.Add(ftext, 1, LCEN|wx.GROW, 1)
        pack(textpanel, textsizer)

        self.nb.AddPage(textpanel, ' Text of Data File ', True)
        self.nb.AddPage(self.plotpanel, ' Plot of Selected Arrays ', True)

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(panel, 0, wx.GROW|wx.ALL, 2)
        mainsizer.Add(self.nb, 1, LCEN|wx.GROW,   2)
        pack(self, mainsizer)

        self.statusbar = self.CreateStatusBar(2, 0)
        self.statusbar.SetStatusWidths([-1, -1])
        statusbar_fields = [group.filename, ""]
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)

        self.Show()
        self.Raise()
        self.onUpdate(self)

    def read_column_file(self, path):
        """read column file, generally as initial read"""
        parent, filename = os.path.split(path)
        with open(path, 'r') as fh:
            lines = fh.readlines()

        text = ''.join(lines)
        line1 = lines[0].lower()

        reader = 'read_ascii'
        if 'epics stepscan file' in line1:
            reader = 'read_gsexdi'
        elif 'xdi' in line1:
            reader = 'read_xdi'
        elif 'epics scan' in line1:
            reader = 'read_gsescan'

        tmpname = '_tmp_file_'
        read_cmd = "%s = %s('%s')" % (tmpname, reader, path)
        self.reader = reader
        self._larch.eval(read_cmd, add_history=False)
        group = self._larch.symtable.get_symbol(tmpname)
        self._larch.symtable.del_symbol(tmpname)

        group.text = text
        group.path = path
        group.filename = filename
        group.groupname = file2groupname(filename,
                                         symtable=self._larch.symtable)
        return group

    def show_subframe(self, name, frameclass, **opts):
        shown = False
        if name in self.subframes:
            try:
                self.subframes[name].Raise()
                shown = True
            except:
                del self.subframes[name]
        if not shown:
            self.subframes[name] = frameclass(self, **opts)

    def onEditNames(self, evt=None):
        self.show_subframe('editcol', EditColumnFrame,
                           group=self.workgroup,
                           on_ok=self.set_array_labels)

    def set_array_labels(self, arr_labels):
        self.workgroup.array_labels = arr_labels
        yarr_labels = self.yarr_labels = arr_labels + ['1.0', '0.0', '']
        xarr_labels = self.xarr_labels = arr_labels + ['<index>']
        def update(wid, choices):
            curstr = wid.GetStringSelection()
            curind = wid.GetSelection()
            wid.SetChoices(choices)
            if curstr in choices:
                wid.SetStringSelection(curstr)
            else:
                wid.SetSelection(curind)
        update(self.xarr,  xarr_labels)
        update(self.yarr1, yarr_labels)
        update(self.yarr2, yarr_labels)
        update(self.yerr_arr, yarr_labels)
        self.onUpdate()

    def onOK(self, event=None):
        """ build arrays according to selection """
        if self.wid_groupname is not None:
            groupname = fix_varname(self.wid_groupname.GetValue())

        yerr_op = self.yerr_op.GetStringSelection().lower()
        yerr_expr = '1'
        if yerr_op.startswith('const'):
            yerr_expr = "%f" % self.yerr_const.GetValue()
        elif yerr_op.startswith('array'):
            yerr_expr = '%%s.data[%i, :]' % self.yerr_arr.GetSelection()
        elif yerr_op.startswith('sqrt'):
            yerr_expr = 'sqrt(%s.ydat)'
        self.expressions['yerr'] = yerr_expr

        # generate script to pass back to calling program:
        labels = ', '.join(self.workgroup.array_labels)
        read_cmd = "%s('{path:s}', labels='%s')" % (self.reader, labels)

        buff = ["{group:s} = %s" % read_cmd,
                "{group:s}.path = '{path:s}'"]

        for attr in ('datatype', 'plot_xlabel', 'plot_ylabel'):
            val = getattr(self.workgroup, attr)
            buff.append("{group:s}.%s = '%s'" % (attr, val))

        for aname in ('xdat', 'ydat', 'yerr'):
            expr = self.expressions[aname].replace('%s', '{group:s}')
            buff.append("{group:s}.%s = %s" % (aname, expr))

        if getattr(self.workgroup, 'datatype', 'raw') == 'xas':
            buff.append("{group:s}.energy = {group:s}.xdat")
            buff.append("{group:s}.mu = {group:s}.ydat")

        script = "\n".join(buff)

        if self.read_ok_cb is not None:
            self.read_ok_cb(script, self.path, groupname=groupname,
                            array_sel=self.array_sel)

        self.Destroy()

    def onCancel(self, event=None):
        self.workgroup.import_ok = False
        self.Destroy()

    def onYerrChoice(self, evt=None):
        yerr_choice = evt.GetString()
        self.yerr_arr.Disable()
        self.yerr_const.Disable()
        if 'const' in yerr_choice.lower():
            self.yerr_const.Enable()
        elif 'array' in yerr_choice.lower():
            self.yerr_arr.Enable()
        self.onUpdate()

    def onUpdate(self, value=None, evt=None):
        """column selections changed calc xdat and ydat"""
        # dtcorr = self.dtcorr.IsChecked()
        # print("Column Frame on Update ")

        dtcorr = False
        use_deriv = self.use_deriv.IsChecked()
        rawgroup = self.initgroup
        workgroup = self.workgroup
        rdata = self.initgroup.data

        # print("onUpdate ", dir(rawgroup))
        ix  = self.xarr.GetSelection()
        xname = self.xarr.GetStringSelection()

        exprs = dict(xdat=None, ydat=None, yerr=None)

        ncol, npts = rdata.shape
        if xname.startswith('<index') or ix >= ncol:
            workgroup.xdat = 1.0*np.arange(npts)
            xname = '_index'
            exprs['xdat'] = 'arange(%i)' % npts
        else:
            workgroup.xdat = rdata[ix, :]
            exprs['xdat'] = '%%s.data[%i, : ]' % ix

        workgroup.datatype = self.datatype.GetStringSelection().strip().lower()

        def pre_op(opwid, arr):
            opstr = opwid.GetStringSelection().strip()
            suf = ''
            if opstr in ('-log(', 'log('):
                suf = ')'
                if opstr == 'log(':
                    arr = np.log(arr)
                elif opstr == '-log(':
                    arr = -np.log(arr)
            return suf, opstr, arr

        try:
            xsuf, xpop, workgroup.xdat = pre_op(self.xpop, workgroup.xdat)
            self.xsuf.SetLabel(xsuf)
            exprs['xdat'] = '%s%s%s' % (xpop, exprs['xdat'], xsuf)
        except:
            return
        try:
            xunits = rawgroup.array_units[ix].strip()
            xlabel = '%s (%s)' % (xname, xunits)
        except:
            xlabel = xname

        yname1  = self.yarr1.GetStringSelection().strip()
        yname2  = self.yarr2.GetStringSelection().strip()
        iy1    = self.yarr1.GetSelection()
        iy2    = self.yarr2.GetSelection()
        yop = self.yop.GetStringSelection().strip()

        ylabel = yname1
        if len(yname2) == 0:
            yname2 = '1.0'
        else:
            ylabel = "%s%s%s" % (ylabel, yop, yname2)

        if yname1 == '0.0':
            yarr1 = np.zeros(npts)*1.0
            yexpr1 = 'zeros(%i)' % npts
        elif len(yname1) == 0 or yname1 == '1.0' or iy1 >= ncol:
            yarr1 = np.ones(npts)*1.0
            yexpr1 = 'ones(%i)' % npts
        else:
            yarr1 = rdata[iy1, :]
            yexpr1 = '%%s.data[%i, : ]' % iy1

        if yname2 == '0.0':
            yarr2 = np.zeros(npts)*1.0
            yexpr2 = '0.0'
        elif len(yname2) == 0 or yname2 == '1.0' or iy2 >= ncol:
            yarr2 = np.ones(npts)*1.0
            yexpr2 = '1.0'
        else:
            yarr2 = rdata[iy2, :]
            yexpr2 = '%%s.data[%i, : ]' % iy2

        workgroup.ydat = yarr1
        exprs['ydat'] = yexpr1
        if yop in ('+', '-', '*', '/'):
            exprs['ydat'] = "%s %s %s" % (yexpr1, yop, yexpr2)
            if yop == '+':
                workgroup.ydat = yarr1.__add__(yarr2)
            elif yop == '-':
                workgroup.ydat = yarr1.__sub__(yarr2)
            elif yop == '*':
                workgroup.ydat = yarr1.__mul__(yarr2)
            elif yop == '/':
                workgroup.ydat = yarr1.__truediv__(yarr2)

        ysuf, ypop, workgroup.ydat = pre_op(self.ypop, workgroup.ydat)
        self.ysuf.SetLabel(ysuf)
        exprs['ydat'] = '%s%s%s' % (ypop, exprs['ydat'], ysuf)

        yerr_op = self.yerr_op.GetStringSelection().lower()
        exprs['yerr'] = '1'
        if yerr_op.startswith('const'):
            yerr = self.yerr_const.GetValue()
            exprs['yerr'] = '%f' % yerr
        elif yerr_op.startswith('array'):
            iyerr = self.yerr_arr.GetSelection()
            yerr = rdata[iyerr, :]
            exprs['yerr'] = '%%s.data[%i, :]' % iyerr
        elif yerr_op.startswith('sqrt'):
            yerr = np.sqrt(workgroup.ydat)
            exprs['yerr'] = 'sqrt(%s.ydat)'

        if use_deriv:
            try:
                workgroup.ydat = (np.gradient(workgroup.ydat) /
                                 np.gradient(workgroup.xdat))
                exprs['ydat'] = 'deriv(%s)/deriv(%s)' % (exprs['ydat'],
                                                         exprs['xdat'])
            except:
                pass

        self.expressions = exprs
        self.array_sel = {'xpop': xpop, 'xarr': xname,
                          'ypop': ypop, 'yop': yop,
                          'yarr1': yname1, 'yarr2': yname2,
                          'use_deriv': use_deriv}

        try:
            npts = min(len(workgroup.xdat), len(workgroup.ydat))
        except AttributeError:
            return

        workgroup.filename    = rawgroup.filename
        workgroup.npts        = npts
        workgroup.plot_xlabel = xlabel
        workgroup.plot_ylabel = ylabel
        workgroup.xdat        = np.array(workgroup.xdat[:npts])
        workgroup.ydat        = np.array(workgroup.ydat[:npts])
        workgroup.y           = workgroup.ydat
        workgroup.yerr        = yerr
        if isinstance(yerr, np.ndarray):
            workgroup.yerr    = np.array(yerr[:npts])

        if workgroup.datatype == 'xas':
            workgroup.energy = workgroup.xdat
            workgroup.mu     = workgroup.ydat

        path, fname = os.path.split(workgroup.filename)
        popts = dict(marker='o', markersize=4, linewidth=1.5,
                     title=fname, ylabel=ylabel, xlabel=xlabel,
                     label="%s: %s" % (fname, workgroup.plot_ylabel))

        self.plotpanel.plot(workgroup.xdat, workgroup.ydat, **popts)

        for i in range(self.nb.GetPageCount()):
            if 'plot' in self.nb.GetPageText(i).lower():
                self.nb.SetSelection(i)

    def plot_messages(self, msg, panel=1):
        self.SetStatusText(msg, panel)
