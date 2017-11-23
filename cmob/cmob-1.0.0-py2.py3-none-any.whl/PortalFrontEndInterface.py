from mrpUtils import util

class PortalFrontEndInterface(object):
    """
    This class servers as an interface to the mobility portal front end.
    """
    def __init__(self, address='192.168.5.1'):
        self.name = 'PortalFrontEndInterface'
        self.status_port = 9879
        self.uri = 'http://' + str(address) + ':' + str(self.status_port)

    def get_pfe_summary(self):
        """
        This method gets the PFE summary.
        :return: JSON PFE summary comparable to pfe-summary.
        """
        return util.send_requests(self.uri + '/' +'summary')

    @staticmethod
    def get_pfe_config():
        """
        This method gets the PFE config as JSON.
        :return: JSON of the PF config.
        """
        try:
            with open('/etc/ifcp/pfe.conf','r') as pfe_config:
                return pfe_config
        except IOError as io_error:
            raise IOError("Failed to read PFE config: " + str(io_error))
