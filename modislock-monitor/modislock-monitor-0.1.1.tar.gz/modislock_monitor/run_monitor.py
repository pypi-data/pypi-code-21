import signal
import time
from modislock_monitor import Monitor
from modislock_monitor.extensions import log


def signal_handler(signal, frame):
    """Used to handle termination signals from the OS
    :param signal:
    :param frame:
    :return:
    """
    signals = {2: 'SIGINT', 15: 'SIGTERM'}
    log.info('Monitor stopped with signal: {}'.format(signals[signal]))
    raise ServiceExit


class ServiceExit(Exception):
    """Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def main():
    monitor = Monitor()

    log.info('****Monitor Starting****')
    # Registers signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        monitor.run()
    except (KeyboardInterrupt, ServiceExit):
        monitor.stop()
        log.info('****Monitor Closing in 5 seconds***')
        time.sleep(5)


if __name__ == '__main__':
    main()
