import signal
import asyncio
import logging
import argparse

from nmd import MqttDriver


logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(prog='noolite_mtrf_mqtt', description='NooLite MTRF to MQTT')
    parser.add_argument('--mtrf-serial-port', '-msp', required=True, type=str, help='MTRF-32-USB port name')
    parser.add_argument('--mqtt-scheme', '-ms', default='mqtt', type=str, help='MQTT scheme')
    parser.add_argument('--mqtt-host', '-mh', default='127.0.0.1', type=str, help='MQTT host')
    parser.add_argument('--mqtt-port', '-mp', type=str, help='MQTT port')
    parser.add_argument('--mqtt-user', '-mu', type=str, help='MQTT user')
    parser.add_argument('--mqtt-password', '-mpass', type=str, help='MQTT password')
    parser.add_argument('--commands-delay', '-cd', type=float, default=0.1,
                        help='Delay between sending commands to MTRF')
    parser.add_argument('--logging-level', '-ll', default='INFO', type=str, help='Logging level')
    return parser.parse_args()


def ask_exit():
    for task in asyncio.Task.all_tasks():
        task.cancel()


def run():
    args = get_args()
    logging.basicConfig(level=args.logging_level)

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, ask_exit)

    for can_be_empty_arg in ['mqtt_port', 'mqtt_user', 'mqtt_password']:
        if getattr(args, can_be_empty_arg, None) == '__EMPTY__':
            setattr(args, can_be_empty_arg, '')

    mqtt_uri = '{scheme}://{user}{password}@{host}{port}'.format(
        scheme=args.mqtt_scheme,
        user=args.mqtt_user or '',
        password=':{}'.format(args.mqtt_password) if args.mqtt_password else '',
        host=args.mqtt_host,
        port=':{}'.format(args.mqtt_port) if args.mqtt_port else '',
    )

    md = MqttDriver(mtrf_tty_name=args.mtrf_serial_port, loop=loop, mqtt_uri=mqtt_uri,
                    commands_delay=args.commands_delay)

    try:
        loop.run_until_complete(md.run())
    except asyncio.CancelledError as e:
        logger.debug(e)
    finally:
        loop.close()


if __name__ == '__main__':
    run()
