"""This is IOS XRv driver implementation."""

from condoor.drivers.XR import Driver as eXR
from condoor import pattern_manager


class Driver(eXR):
    """This is a Driver class implementation for IOS XRv."""

    platform = 'XRv'
    reload_cmd = 'admin reload location all'
    families = {
        "IOS XRv 9000": "IOSXRv-9K",
        "IOS XRv x64": "IOSXRv-X64",
    }

    def update_driver(self, prompt):
        """Return driver name based on prompt analysis."""
        return pattern_manager.platform(prompt, ['XRv', 'Calvados', 'Windriver'])
