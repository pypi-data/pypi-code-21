import autest.core.setupitem as setupitem
from autest.exceptions.setuperror import SetupError
import autest.api as api

class RunCommand(setupitem.SetupItem):
    def __init__(self, command, pass_value=0):
        super(RunCommand, self).__init__(itemname="RunCommand")
        self.command = command
        self.pass_value = pass_value
        self.Description = "Run command '{0}' expecting exit code '{1}'".\
                format(command, pass_value)

    def setup(self):
        try:
            actual_value = self.RunCommand(self.command)
            if self.pass_value != actual_value:
                raise Exception(("Actual exit code '{0}' "+\
                        "did not match expected value '{1}'").\
                        format(actual_value, self.pass_value))
        except Exception as e:
            raise SetupError("Failed to run command '{0}' because:\n {1}"\
                    .format(self.command, str(e)))

api.AddSetupItem(RunCommand, "__call__", ns='RunCommand')
