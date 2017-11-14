from bitpermissions import Permissions


class AppliancePermissions(Permissions):
    """Simple permissions for the Appliance class."""

    # Default to all permissions
    def __init__(self, perms=None, perm_digits=-1):
        if perms is None:
            perms = ['cmd', 'rest', 'ssh']
        super(AppliancePermissions, self).__init__(perms, perm_digits)
