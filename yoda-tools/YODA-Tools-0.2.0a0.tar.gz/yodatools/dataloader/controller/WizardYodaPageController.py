import wx

from yodatools.dataloader.view.WizardYodaPageView import WizardYodaPageView


class WizardYodaPageViewController(WizardYodaPageView):
    def __init__(self, parent, title=''):
        super(WizardYodaPageViewController, self).__init__(parent)
        self.title = title

    def on_browse_button(self, event):
        dialog = wx.DirDialog(
            self,
            message='Save to...',
            style=wx.DD_CHANGE_DIR
        )

        if dialog.ShowModal() != wx.ID_OK:
            return

        self.file_text_ctrl.SetValue(dialog.GetPath() + '\\yoda_export.yaml')
