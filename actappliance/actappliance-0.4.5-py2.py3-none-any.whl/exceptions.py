from actappliance.act_errors import ACTError


class ApplianceError(Exception):
    """Generic Appliance exception to raise and log different fatal errors.

    This exists for legacy. ACTError and act_errors dictionary should be used for future cases"""

    def __init__(self, msg):
        super(ApplianceError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg
