"""
This is where the mainline sits and is responsible for setting up the logging,
the argument parsing and for starting up salm.
"""
from simple_aws_lambda_maker.actions import available_actions
from simple_aws_lambda_maker.collector import Collector
from simple_aws_lambda_maker.errors import NoSuchTask
from simple_aws_lambda_maker import VERSION

from input_algorithms.spec_base import NotSpecified
from delfick_app import App, DelayedFileType
import logging

log = logging.getLogger("simple_aws_lambda_maker.executor")

class App(App):
    VERSION = VERSION
    cli_categories = ['salm']
    cli_description = "Very simple deployer for python lambdas"
    cli_environment_defaults = {"SALM_CONFIG": ("--salm-config", './salm.yml')}
    cli_positional_replacements = [('--task', 'help'), ('--group', NotSpecified)]

    def execute(self, args_obj, args_dict, extra_args, logging_handler, no_docker=False):
        args_dict["salm"]["config"] = args_dict["salm"]["config"](optional=True) or NotSpecified

        config_name = None
        if args_dict["salm"]["config"] is not NotSpecified:
            config_name = args_dict["salm"]["config"].name

        collector = Collector()
        collector.prepare(config_name, args_dict)
        if "term_colors" in collector.configuration:
            self.setup_logging_theme(logging_handler, colors=collector.configuration["term_colors"])

        task = collector.configuration["salm"].task
        group = collector.configuration["salm"].group
        if task not in available_actions:
            raise NoSuchTask(wanted=task)
        else:
            available_actions[task](collector, group=group)

    def setup_other_logging(self, args_obj, verbose=False, silent=False, debug=False):
        logging.getLogger("boto3").setLevel([logging.CRITICAL, logging.ERROR][verbose or debug])
        logging.getLogger("botocore").setLevel([logging.CRITICAL, logging.ERROR][verbose or debug])

    def specify_other_args(self, parser, defaults):
        parser.add_argument("--salm-config"
            , help = "The config file specifying what simple_aws_lambda_maker should care about"
            , type = DelayedFileType("r")
            , **defaults["--salm-config"]
            )

        parser.add_argument("--dry-run"
            , help = "Should salm take any real action or print out what is intends to do"
            , dest = "salm_dry_run"
            , action = "store_true"
            )

        parser.add_argument("--task"
            , help = "The task to run"
            , dest = "salm_task"
            , **defaults["--task"]
            )

        parser.add_argument("--group"
            , help = "The group to work on"
            , dest = "salm_group"
            , **defaults["--group"]
            )

        return parser

main = App.main
if __name__ == '__main__':
    main()
