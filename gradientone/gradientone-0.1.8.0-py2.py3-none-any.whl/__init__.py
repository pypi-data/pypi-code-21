import ivi
import gateway_helpers
import gateway_client
import controllers
import transmitters
import transformers
import always_on
from version import __version__


__all__ = ['gateway_client', 'gateway_helpers', 'controllers',
           'transmitters', 'transformers',
           'always_on', 'ivi', '__version__']


# Uncomment when deploying pip package
def main():
    """kicks off client"""
    always_on.run()
