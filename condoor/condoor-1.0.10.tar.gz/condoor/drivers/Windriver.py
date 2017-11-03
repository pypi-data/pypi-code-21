"""This is a Wind River Linux driver implementation."""

from condoor.drivers.generic import Driver as Generic
from condoor import pattern_manager


class Driver(Generic):
    """This is a Driver class implementation for Wind River Linux."""

    platform = 'Windriver'
    inventory_cmd = None
    target_prompt_components = ['prompt_dynamic', 'prompt_default', 'calvados', 'lc']
    prepare_terminal_session = []
    families = {
    }

    def __init__(self, device):
        """Initialize the Wind River Linux driver object."""
        super(Driver, self).__init__(device)

    def get_version_text(self):
        """Return the version information."""
        version_text = self.device.send('cat /etc/issue', timeout=10)
        return version_text

    def update_driver(self, prompt):
        """Return driver name based on prompt analysis."""
        return pattern_manager.platform(prompt, ['Windriver', 'Calvados', 'eXR'])

    def get_os_type(self, version_text):
        """Return Windriver os type."""
        return 'Windriver'
