# =*= coding: utf-8 =*=
from ..settings import BACKUP_BACKENDS
from ..utils import BackendLoader


class Loader(BackendLoader):
    BACKENDS = BACKUP_BACKENDS

    def add_arguments(self, parser):
        super(Loader, self).add_arguments(parser)
        parser.add_argument(
            '-c', '--config',
            help='Config for %(prog)s. Default:[%(default)s]',
            type=str,
            action="store",
            default="/etc/1c/backup.ini",
        )
        return parser

    def run(self, args):
        backend = super(Loader, self).run(args)
        backend.backup()
