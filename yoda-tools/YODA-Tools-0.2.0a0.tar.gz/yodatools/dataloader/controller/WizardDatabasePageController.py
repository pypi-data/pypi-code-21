from yodatools.dataloader.view.WizardDatabasePageView import WizardDatabasePageView


class WizardDatabasePageController(WizardDatabasePageView):
    def __init__(self, parent, title=''):
        super(WizardDatabasePageController, self).__init__(parent)
        self.title = title
