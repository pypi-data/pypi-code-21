import os
import glob
import shutil
import logging
import argparse

from noolite_mqtt_webserver.server import NooLiteMqttServer


NOOLITE_IMPORT_STRING = "var HomeKitTypesCustom = require('./HomeKitTypes-NooLite');\n"


def add_noolite_characteristics(args):
    print('Init command start')
    search_path = args.homebridge_dir or '/usr'
    print('Searching HomeKitTypes.js in {}'.format(search_path))
    search_path = os.path.join(search_path, '**', 'HomeKitTypes.js')
    homekit_types_path = next(glob.iglob(search_path, recursive=True), None)
    try:
        # Берем последние 5 строчек найденного файла
        with open(homekit_types_path) as f:
            last_five_lines = f.readlines()[-5:]
    except (TypeError, FileNotFoundError):
        print('Cannot find HomeKitTypes.js')
        print('Hint: you can set homebridge dir path with argument "--path-to-homebridge /path/to/homebridge/"')
        return

    # Аппендим строку импорта в HomeKitTypes.js если такой строки еще нет
    if NOOLITE_IMPORT_STRING not in last_five_lines:
        with open(homekit_types_path, 'a') as f:
            f.write(NOOLITE_IMPORT_STRING)

    # Добавляем файл характеристик NooLite если его еще нет
    homekit_types_dir = os.path.split(homekit_types_path)[0]
    homekit_types_noolite_path = os.path.join(homekit_types_dir, 'HomeKitTypes-NooLite.js')
    shutil.copyfile('../HomeKitTypes-NooLite.js', homekit_types_noolite_path)
    print('Init successfully done!')


def run_server(args):
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

    server = NooLiteMqttServer(
        mqtt_read_topic=args.mqtt_read_topic,
        mqtt_write_topic=args.mqtt_write_topic,
        server_ip=args.server_ip,
        server_port=args.server_port,
        mqtt_uri=mqtt_uri
    )
    server.run()


def get_args():
    parser = argparse.ArgumentParser(prog='noolite_server', description='NooLite web server manager')
    parser.add_argument('--server-ip', '-sip', default='0.0.0.0', type=str, help='NooLite web interface ip address')
    parser.add_argument('--server-port', '-srp', default=8080, type=int, help='NooLite web interface port')
    parser.add_argument('--mqtt-read-topic', '-mrt', default='noolite/mtrf/receive', type=str,
                        help='MQTT topic for read data from MTRF adapter')
    parser.add_argument('--mqtt-write-topic', '-mwt', default='noolite/mtrf/send', type=str,
                        help='MQTT topic for send data to MTRF adapter')
    parser.add_argument('--logging-level', '-ll', default='INFO', type=str, help='Logging level')
    parser.add_argument('--mqtt-scheme', '-ms', default='mqtt', type=str, help='MQTT scheme')
    parser.add_argument('--mqtt-host', '-mh', default='127.0.0.1', type=str, help='MQTT host')
    parser.add_argument('--mqtt-port', '-mp', type=str, help='MQTT port')
    parser.add_argument('--mqtt-user', '-mu', type=str, help='MQTT user')
    parser.add_argument('--mqtt-password', '-mpass', type=str, help='MQTT password')
    parser.set_defaults(func=run_server)

    subparsers = parser.add_subparsers(help='Additional commands')
    # Команда установки дополнительных характеристик NooLite в Homebridge
    init = subparsers.add_parser('init', help='Add NooLite characteristics to Homebridge')
    init.add_argument('--homebridge-dir', type=str)
    init.set_defaults(func=add_noolite_characteristics)
    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=args.logging_level)
    args.func(args)


if __name__ == '__main__':
    main()
