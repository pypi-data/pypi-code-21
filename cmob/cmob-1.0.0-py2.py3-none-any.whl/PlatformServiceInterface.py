from mrpUtils import util


class PlatformServiceInterface(object):
    """
    This class servers as an interface to the mobility platform.
    """
    def __init__(self):
        self.name = 'PlatformServiceInterface'

    @staticmethod
    def send_cli_command(command):
        """
        This method sends a cli command.
        :param command: the command to execute.
        :return: The std_out of the command sent.
        """
        return util.subprocess_cmd(command)

    @staticmethod
    def get_service_status(service_name):
        """
        This method gets the is-active state as seen by systemctl for a given service name.
        :param service_name: The name of the server to check is-active.
        :return: The output of systemctl is-active.
        """
        return util.subprocess_cmd('systemctl is-active ' + service_name)

    @staticmethod
    def restart_service(service_name):
        """
        This method restarts a given service by service name.
        :param service_name: The name of the server to restart.
        :return: The output of systemctl restart.
        """
        return util.subprocess_cmd('systemctl restart ' + service_name)

    @staticmethod
    def stop_service(service_name):
        """
        This method stops a given service by service name.
        :param service_name: The name of the server to stop.
        :return: The output of systemctl stop.
        """
        return util.subprocess_cmd('systemctl stop ' + service_name)

    @staticmethod
    def start_service(service_name):
        """
        This method starts a given service by service name.
        :param service_name: The name of the service to start.
        :return: The output of systemctl start.
        """
        return util.subprocess_cmd('systemctl start ' + service_name)

    @staticmethod
    def get_active_bank():
        """
        This method gets the active bank sw.
        :return: bankA or bankB.
        """
        cmd = 'installUtil activeSwBank'
        active_bank = util.subprocess_cmd(cmd).split('/')[2]
        return active_bank

    @staticmethod
    def get_enabled_services():
        """
        This method gets all enabled services as seen by systemctl for a given service name.
        :return: A list of enabled services
        """
        list_of_enabled_services = list()
        service_to_add = ''
        # This call returns a list of letters that we need to build a service name out of
        # ['a', 'i', 'r', 'c', 'r', 'a', 'f', 't', 'd', '.', 's', 'e', 'r', 'v', 'i', 'c', 'e', '\n']
        # We need to turn the above into aircraftd.service below is said logic
        for service_letter in util.subprocess_cmd("systemctl list-unit-files | grep enabled | awk '{print $1}'"):
            if service_letter != '\n':
                service_to_add += service_letter
                continue
            list_of_enabled_services.append(service_to_add)
            service_to_add = ''