from django.core.management.base import BaseCommand, CommandError
from morango.controller import MorangoProfileController


def create_callback(encoder):
    encoder_len = encoder.len
    bar = ProgressBar(expected_size=encoder_len, filled_char="=")

    def callback(monitor):
        bar.show(monitor.bytes_read)

    return callback


class Command(BaseCommand):
    help = "Generalizable command line sync"

    def add_arguments(self, parser):
        parser.add_argument('connection_type', type=str)
        parser.add_argument('direction', type=str)
        parser.add_argument('host', type=str)
        parser.add_argument('profile', type=str)
        parser.add_argument('scope_def_id', type=int)
        parser.add_argument('main_partition_val', type=str)
        parser.add_argument('scope_params', type=str)
        parser.add_argument('--userargs', default=None, type=str)
        parser.add_argument('--password', default=None, type=str)

    def handle(self, *args, **options):
        controller = MorangoProfileController(options['profile'])
        network_connection = controller.create_network_connection(options['host'])
        remote_certs = network_connection.get_remote_certificates(options['main_partition_val'])
        for cert in remote_certs:
            if cert.scope_definition_id == options['scope_def_id']:
                server_cert = cert
        if options['--userargs'] and options['--password']:
            client_cert = network_connection.certificate_signing_request(server_cert, options['scope_def_id'], options['scope_params'],
                                                                         userargs=options['--userargs'], password=options['--password'])
        sync_client = network_connection.create_sync_session(client_cert, server_cert)
        if options['direction'] == 'push':
            sync_client.initiate_push()  # pass in filter
        elif options['direction'] == 'pull':
            sync_client.initiate_pull()  # pass in filter
        else:
            raise CommandError("`direction` parameter must be `push` or `pull`")
