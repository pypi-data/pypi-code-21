import logging
import os
import shutil

import portinus

log = logging.getLogger(__name__)

class EnvironmentFile(object):

    def __init__(self, name, source_environment_file=None):
        self.name = name
        self._source_environment_file = source_environment_file
        self.path = portinus.get_instance_dir(self.name) + ".environment"
        log.debug("Initialized EnvironmentFile for '{name}' from source: '{source_environment_file}'".format(name=name, source_environment_file=source_environment_file))

        if source_environment_file:
            try:
                with open(source_environment_file):
                    pass
            except FileNotFoundError as e:
                log.error("Unable to access the specified environment file ({source_environment_file})".format(source_environment_file=source_environment_file))
                raise(e)

    def __bool__(self):
        return bool(self._source_environment_file)

    def ensure(self):
        if self:
            log.info("Creating/updating environment file for '{name}' at '{path}'".format(name=self.name, path=self.path))
            shutil.copy(self._source_environment_file, self.path)
        else:
            self.remove()

    def remove(self):
        log.info("Removing environment file for {name}".format(name=self.name))
        try:
            os.remove(self.path)
            log.debug("Sucessfully removed environment file")
        except FileNotFoundError:
            log.debug("No environment file found")
