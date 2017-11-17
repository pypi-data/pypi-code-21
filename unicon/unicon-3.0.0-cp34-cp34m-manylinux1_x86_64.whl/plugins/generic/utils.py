""" Generic utilities. """

import re

from unicon.utils import Utils, AttributeDict

class GenericUtils(Utils):

    def get_redundancy_details(self, connection, timeout, who):
        """
        :arg  connection:  device connection object
        :return: device role and redundancy mode of the device
        """
        timeout = timeout or connection.settings.EXEC_TIMEOUT
        redundancy_details = AttributeDict()
        if who == "peer":
            show_red_out = connection.execute("show redundancy sta |  in peer",
                                              timeout=timeout)
        else:
            show_red_out = connection.execute("show redundancy sta |  in my",
                                              timeout=timeout)

        if re.search("ACTIVE|active", show_red_out):
            redundancy_details['role'] = "active"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        elif re.search("standby|STANDBY", show_red_out):
            redundancy_details['role'] = "standby"
            redundancy_details['state'] =\
                show_red_out[show_red_out.find('-') + 1:].strip()
        show_red_out = connection.execute(
            "show redundancy sta | inc Redundancy State")
        redundancy_details['mode'] =\
            show_red_out[show_red_out.find("=") + 1:].strip()
        return redundancy_details
