import logging
import os
import os.path
from optparse import make_option

import shutil
import yaml
from django.core.management import BaseCommand
from django.db.models import get_models

from django_cdc import settings
from django_cdc.models.services import lambda_service, CommonUtils
from django_cdc.models.constants import ServiceType


class Command(BaseCommand):
    # Show this when the user types help
    help = "My test command"

    # support in django 1.6
    option_list = BaseCommand.option_list + (
        make_option(
            "--logging_level",
            dest="logging_level",
            help="specify logging level",
        ),
    )

    def __get_custom_function(self, body, lambda_fn_names, *args, **kwargs):
        if not body["functions"]:
            body["functions"] = {}

        service = lambda_service()
        for lambda_name in lambda_fn_names:
            function_val = service.get_serverless_func(lambda_name)
            body["functions"].update({lambda_name: function_val})
        return body

    def __get_file_version(self, dir_files):
        dir_files.sort(key=lambda f: int(filter(str.isdigit, f)))
        if dir_files:
            latest_file = dir_files[len(dir_files) - 1]
            num = latest_file.split('_')
            value = num[1].split(".")
            value[0] = str(int(value[0]) + 1)
            num[1] = '.'.join(value)
            __version__ = '_'.join(num)
        else:
            __version__ = "serverless_1.yml"
        return __version__

    def set_log_level(self, log_level):
        LEVELS = {'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL}

        if log_level:
            level = LEVELS.get(log_level, logging.NOTSET)
            logging.basicConfig(level=level)

    # A command must define handle()
    def handle(self, *args, **options):
        logging_level = options['logging_level']
        self.set_log_level(logging_level)
        logging.debug("Get all the models which contain djangoCDC manager")
        lambda_fn_names = []
        common_utils = CommonUtils()
        for ct in get_models():
            model_service = getattr(ct.objects, "services", None)
            if model_service and ServiceType.LAMBDA_KINESIS in model_service:
                        lambda_fn_names.append(
                            common_utils.get_function_name(ct._meta.db_table))
        logging.debug("Successfully got all the models:%s"
                      % str(lambda_fn_names))

        if not lambda_fn_names:
            logging.info("Empty list...exit")
            return

        header = {}
        new_file_path = os.path.join(settings.SERVERLESS_DIR,
                                     'serverless.yml')

        back_up_path = os.path.join(settings.SERVERLESS_DIR,
                                    "backup")

        if not os.path.isdir(back_up_path):
            os.makedirs(back_up_path)

        try:
            logging.debug("Reading new file serverless.yml and append"
                          " more functions in it")
            if os.path.isfile(new_file_path):
                logging.debug("Create backup for serverless file")
                dir_files = os.listdir(back_up_path)
                __version__ = self.__get_file_version(dir_files)
                shutil.copy2(new_file_path, os.path.join(back_up_path,
                                                         __version__))
                logging.info("Successfully created backup file:%s"
                             % __version__)
                stream = file(new_file_path, 'r')
                dict = yaml.load(stream)
                header = self.__get_custom_function(
                    body=dict, lambda_fn_names=lambda_fn_names)
            else:
                header = {'service': settings.SERVELESS_CONFIG,
                          'provider': {'name': 'aws', 'runtime': 'python2.7',
                                       'stage': settings.SERVERLESS_STAGE,
                                       'region': settings.AWS_REGION_NAME}}

                body = self.__get_custom_function(
                    body={"functions": {}}, lambda_fn_names=lambda_fn_names)
                header.update(body)
            logging.debug("Successfully updating serverless file")
        except Exception as e:
            logging.error("Error occurred while creating backup or "
                          "updating new file %s" % str(e))
            return

        try:
            logging.debug("replace serverless file with new one")
            new_file_path = os.path.join(settings.SERVERLESS_DIR,
                                         'serverless.yml')
            with open(new_file_path, 'w') as yml:
                yaml.safe_dump(header, yml, default_flow_style=False)
            logging.debug("Sucessfully replaced serverless file "
                          "at location %s" % str(settings.SERVERLESS_DIR))
        except Exception as e:
            logging.error("Error occured while replacing serverless "
                          "file: %s" % str(e))
            return

        try:
            os.chdir(settings.SERVERLESS_DIR)
            if logging_level == 'debug':
                os.system("serverless deploy -v")
            else:
                os.system("serverless deploy")
        except Exception as e:
            logging.error("Error occurred while deploying to"
                          " aws %s" % str(e))