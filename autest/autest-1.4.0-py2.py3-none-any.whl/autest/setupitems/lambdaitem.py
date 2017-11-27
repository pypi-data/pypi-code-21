from __future__ import absolute_import, division, print_function
import autest.core.setupitem as setupitem
import autest.api as api


class Lambda(setupitem.SetupItem):
    def __init__(self, func_setup=None, func_cleanup=None, description=""):
        super(Lambda, self).__init__(itemname="Lamda")
        self.func_setup = func_setup
        self.func_cleanup = func_cleanup
        self.Description = description

    def setup(self):
        if self.func_setup:
            self.func_setup()

    def cleanup(self):
        if self.func_cleanup:
            self.func_cleanup()

api.AddSetupItem(Lambda, "__call__", ns='Lambda')
