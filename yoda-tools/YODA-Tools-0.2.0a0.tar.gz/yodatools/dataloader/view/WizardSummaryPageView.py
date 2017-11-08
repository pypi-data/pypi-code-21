import wx


class WizardSummaryPageView(wx.Panel):
    def __init__(self, parent):
        super(WizardSummaryPageView, self).__init__(parent)

        # Components
        self.gauge = wx.Gauge(self, range=100)

        # Sizers
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add components to sizer
        sizer.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)
        self.Hide()
