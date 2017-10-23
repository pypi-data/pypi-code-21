from uvtor.core.management.base import BaseCommand, CommandError
from uvtor.db.migrations import Router
from uvtor.conf import settings
from playhouse.pool import PooledPostgresqlExtDatabase
import os

CURDIR = os.getcwd()
DEFAULT_MODEL_DIR = os.path.join(CURDIR, 'models')


class Command(BaseCommand):
    def check(self):
        if not os.path.exists('.uvtor'):
            raise CommandError('Invalid uvtor project')

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-e', '--env', type=str,
                            help='Env.', default='TEST')
        parser.add_argument(
            '-m',
            '--model',
            type=str,
            help='Set path to your models module.',
            default='')

    def execute(self, *args, **options):
        self.check()
        _env = options.get('env')
        _model = options.get('model')
        conf = getattr(settings, 'ENVS')[_env]
        db = PooledPostgresqlExtDatabase(
            conf.get('database'), user=conf.get('user'),
            host=conf.get('host'),
            password=conf.get('password'),
            register_hstore=False)
        db.connect()
        router = Router(db)
        if _model == '':
            files = os.listdir(DEFAULT_MODEL_DIR)
            for file in files:
                if not file.startswith('__init__') and file.endswith('.py'):
                    _model = file[:len(file) - 3]
                    _model = 'models.%s' % _model
                    router.create(auto=_model)
        else:
            _model = 'models.%s' % _model
            router.create(auto=_model)
        db.close()
