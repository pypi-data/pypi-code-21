import sys
import pexpect
from .file_transfer import FileTransfer
from .log import Logger

class RsyncLib(FileTransfer):
    '''
    Class to perform file transfer using rsync.
    Expected structure of settings:
    settings = {
        'source_path' : '',
        'remote_host' : '', #Username@ip
        'destination_path' : '',
        'options_optional' : '',
        'password_optional' : '',
    }
    '''

    connect = None
    get_delta = None

    def __init__(self, path, filename):
        log_obj = Logger()
        self.logger_obj = log_obj.__get_logger__(path, filename)

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: Flag, success/failure message
    #    Desc: This function is used to validate settings passed for file
    #          transfer using rsync.
    # -------------------------------------------------------------------------
    def verify_settings(self, settings):
        flag, message = super(RsyncLib, self).verify_settings(settings)
        if flag:
            self.logger_obj.info("Set default options if there is none.")
            if len(settings["options_optional"].strip()) == 0 or settings["options_optional"] is None:
                settings["options_optional"] = "avpPz"
            return True, "SUCCESS"
        else:
            return False, message

    # -------------------------------------------------------------------------
    #    Args: command - string command used for rsync
    #          remote_host - remote host parameter from settings
    #          password - password if required to connect to remote host
    # Returns: Flag, success/failure message
    #    Desc: Method to execute rsync command, handle if password is required.
    # -------------------------------------------------------------------------
    def _execute_command(self, command, remote_host, password):
        try:
            self.logger_obj.info("Spawn a child of pexpect")
            child = pexpect.spawn(command)
            self.logger_obj.info("Expect if password is required")
            is_waiting = child.expect([remote_host, "password:", pexpect.EOF], timeout=60*30)
            if is_waiting == 0 or is_waiting == 1:
                child.sendline(password)
                child.expect(pexpect.EOF)
                self.logger_obj.info("Rsync was successful")
                return True, "Rsync was successful"

            if is_waiting == 2:
                self.logger_obj.info("Rsync was successful")
                return True, "Rsync was successful"

        except Exception as e:
            self.logger_obj.exception("Exceptio occurred : {0}".format(e.__str__()))
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: Flag, success/failure message
    #    Desc: This function is used to receive files and / or directories
    #          using rsync.
    # -------------------------------------------------------------------------
    def get(self, settings):
        try:
            self.logger_obj.info("Verify settings for recieving files using rsync")
            flag, message = self.verify_settings(settings)
            if not flag:
                self.logger_obj.error("Settings passed are invalid. So cannot perform rsync.")
                return flag, message

            self.logger_obj.info("Prepare command")
            command = "rsync -{} {}:{} {}".format(settings['options_optional'], settings['remote_host'], settings['source_path'], settings['destination_path'])

            self.logger_obj.info("Execute rsync command")
            flag, message = self._execute_command(command, settings['remote_host'], settings['password_optional'])

            return flag, message

        except Exception as e:
            self.logger_obj.exception("Exceptio occurred : {0}".format(e.__str__()))
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: settings - dictionary
    # Returns: Flag, success/failure message
    #    Desc: This function is used to send files and / or directories
    #          using rsync.
    # -------------------------------------------------------------------------
    def put(self, settings):
        try:
            self.logger_obj.info("Verify settings for sending files using rsync")
            flag, message = self.verify_settings(settings)
            if not flag:
                self.logger_obj.error("Settings passed are invalid. So cannot perform rsync.")
                return flag, message

            self.logger_obj.info("Prepare command")
            command = "rsync -{} {} {}:{}".format(settings['options_optional'], settings['source_path'], settings['remote_host'], settings['destination_path'])

            self.logger_obj.info("Execute rsync command")
            flag, message = self._execute_command(command, settings['remote_host'], settings['password_optional'])

            return flag, message

        except Exception as e:
            self.logger_obj.exception("Exceptio occurred : {0}".format(e.__str__()))
            return False, e.__str__()
    