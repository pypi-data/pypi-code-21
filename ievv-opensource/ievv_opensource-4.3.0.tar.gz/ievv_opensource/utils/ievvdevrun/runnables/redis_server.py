import sys

from ievv_opensource.utils.ievvdevrun.runnables import base


class RunnableThread(base.ShellCommandRunnableThread):
    """
    redis-server runnable thread.

    Examples:

        You can just add it to your Django development settings with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.redis_server.RunnableThread()
                )
            }

        And you can make it not restart on crash with::

            IEVVTASKS_DEVRUN_RUNNABLES = {
                'default': ievvdevrun.config.RunnableThreadList(
                    ievvdevrun.runnables.redis_server.RunnableThread(
                        autorestart_on_crash=False)
                )
            }

    """
    default_autorestart_on_crash = True

    def __init__(self, port='6379'):
        """
        Args:
            port: The port to run the Redis server on. Defaults to ``"6379"``.
        """
        self.port = port
        super(RunnableThread, self).__init__()

    def get_logger_name(self):
        return 'Redis server'

    def get_command_config(self):
        return {
            'executable': 'redis-server',
            'args': ['--port', self.port]
        }
