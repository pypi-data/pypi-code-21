"""
Events that are used in the publish subscription values.
"""
import enum
from pubsub import pub


class PubSubEnumMixin:
    """Mixin that allows for the enumerations to publish and subscribe themselves."""

    def subscribe(self, listener):
        return pub.subscribe(listener, self._build_topic_name())

    def publish(self, **kwargs):
        pub.sendMessage(self._build_topic_name(), **kwargs)

    def _build_topic_name(self):
        return "{}.{}".format(self.__class__.__name__.lower(), self.value)


@enum.unique
class Processing(PubSubEnumMixin, enum.Enum):
    """
    Enumeration that defines the lifecycle of processing the collection of files in the logs.
    DAY_START -
      parameters: date - datetime.date object for the day that is being processed.
    DAY_END -
      parameters: date - datetime.date object for the day that was processed.
    PROCESS_FILE -
      parameters:
        file - the file that should be looked over.
        date - the date that the file was saved in.
    BEGIN -
      Event that is fired off before processing files.
      parameters: none
    END -
      Event that is fired off when all of the files have been processed.
      parameters: none
    """
    DAY_START = 'day_start'
    DAY_END = 'day_end'
    PROCESS_FILE = 'process_file'
    BEGIN = 'begin'
    END = 'end'


@enum.unique
class Reporting(PubSubEnumMixin, enum.Enum):
    """
    Topics related to notifying of new reports based on the processed data.

    REGISTER_REPORT -
      parameters:
        report - definition named tuple
    BUILD_MASTER -
      parameters: none
    """
    REGISTER_REPORT = 'register_report'
    BUILD_MASTER = 'build_master'


@enum.unique
class Application(PubSubEnumMixin, enum.Enum):
    """
    Topics related to notifying the lifecycle of the application.

    INITIALIZE - initialize the plugins based on the configuration values
      parameter: none
    FINALIZE - called before shutting down the application
      parameter: none
    """
    INITIALIZE = 'initialize'
    FINALIZE = 'finalize'


@enum.unique
class Storage(PubSubEnumMixin, enum.Enum):
    """
    Topics related to notifying the storage container about file system modifications.

    FILE_ADDED - add a new file to the storage container
      parameter:
        file - relative path to the file that was created
    FINISHED_MODIFICATIONS - all of the storage changes have been completed, and are ready to be pushed up
      parameter:
        message - text message describing the changes in case of logging
    PUSH_CHANGES - push the changes to any remote storage capability
      parameter: none
    PULL_CHANGES - retrieve changes from the remote storage capability
      parameter: none
    """
    FILE_ADDED = 'file_added'
    FINISHED_MODIFICATIONS = 'finished_modifications'
    PUSH_CHANGES = 'push_changes'
    PULL_CHANGES = 'pull_changes'
