from mrpUtils import util

class MobilityServerControllerInterface(object):
    """
    This class servers as an interface to the mobility server controller.
    """

    def __init__(self, address='127.0.0.1'):
        self.name = 'MobilityServerControllerInterface'
        self.status_port = 9874
        self.uri = 'http://' + str(address) + ':' + str(self.status_port)

    def get_flight_status(self):
        """
        This method gets the MSC flight status.
        :return: JSON flight status comparable to naustat -f.
        """
        return util.send_requests(self.uri +'/' + 'flightStatus')

    def get_health_status(self):
        """
        This method gets the MSC health status.
        :return: JSON health status comparable to naustat -h.
        """
        return util.send_requests(self.uri +'/' + 'healthStatus')

    def get_aircraft_status(self):
        """
        This method gets the MSC aircraft status.
        :return: JSON aircraft status comparable to naustat -A.
        """
        return util.send_requests(self.uri +'/' + 'aircraftStatus')

    def get_modem_status(self):
        """
        This method gets the MSC modem status.
        :return: JSON modem status comparable to naustat -m.
        """
        return util.send_requests(self.uri +'/' + 'modemStatus')

    def get_device_status(self):
        """
        This method gets the MSC device status.
        :return: JSON nau status comparable to naustat -d.
        """
        return util.send_requests(self.uri + '/' + 'deviceStatus')

    def get_system_status(self):
        """
        This method gets the MSC nau status.
        :return: JSON nau status comparable to naustat -n.
        """
        return util.send_requests(self.uri + '/' + 'nauStatus')

    @staticmethod
    def get_tail_id():
        """
        This method gets the tail ID as set in settings.json
        :return: Tail id
        """
        return util.loads(util.subprocess_cmd('cat /data/settings.json'))['tail_id']

    @staticmethod
    def get_msc_config():
        """
        This method gets the MSC config as JSON.
        :return: JSON of the MSC config.
        """
        try:
            with open('/etc/ifcp/nauconfig.json','r') as msc_config:
                return util.loads(msc_config)
        except IOError as io_error:
            raise IOError("Failed to read MSC config: " + str(io_error))

