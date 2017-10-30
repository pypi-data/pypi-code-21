"""
The collector is responsible for collecting configuration
"""
from simple_aws_lambda_maker.formatter import MergedOptionStringFormatter
from simple_aws_lambda_maker.errors import BadYaml, BadConfiguration
from simple_aws_lambda_maker.options import Salm, function_spec

from input_algorithms.spec_base import NotSpecified
from input_algorithms import spec_base as sb
from input_algorithms.dictobj import dictobj
from input_algorithms.meta import Meta

from option_merge.collector import Collector
from option_merge import MergedOptions

import yaml
import os

class Collector(Collector):
    """
    This is based off
    http://option-merge.readthedocs.io/en/latest/docs/api/collector.html
    """
    _merged_options_formattable = True

    BadFileErrorKls = BadYaml
    BadConfigurationErrorKls = BadConfiguration

    def alter_clone_args_dict(self, new_collector, new_args_dict, options=None):
        return MergedOptions.using(
              new_args_dict
            , {"salm": self.configuration["salm"].as_dict()}
            , options or {}
            )

    def extra_prepare(self, configuration, args_dict):
        """
        Called before the configuration.converters are activated
        """
        salm = self.find_salm_options(configuration, args_dict)

        # Make sure functions is started
        if "functions" not in self.configuration:
            self.configuration["functions"] = {}

        # Add our special stuff to the configuration
        self.configuration.update(
            { "collector": self
            , "salm": salm
            }
        , source = "<collector>"
        )

    def find_salm_options(self, configuration, args_dict):
        """Return us all the salm options"""
        d = lambda r: {} if r in (None, "", NotSpecified) else r
        return MergedOptions.using(
              dict(d(configuration.get('salm')).items())
            , dict(d(args_dict.get("salm")).items())
            ).as_dict()

    def home_dir_configuration_location(self):
        return os.path.expanduser("~/.salmrc.yml")

    def start_configuration(self):
        """Create the base of the configuration"""
        return MergedOptions(dont_prefix=[dictobj])

    def read_file(self, location):
        """Read in a yaml file and return as a python object"""
        try:
            return yaml.load(open(location))
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
            raise self.BadFileErrorKls("Failed to read yaml"
                , location=location
                , error_type=error.__class__.__name__
                , error="{0}{1}".format(error.problem, error.problem_mark)
                )

    def add_configuration(self, configuration, collect_another_source, done, result, src):
        """
        Used to add a file to the configuration, result here is the yaml.load
        of the src.

        If the configuration we're reading in has ``salm.extra_files``
        then this is treated as a list of strings of other files to collect.
        """
        # Make sure to maintain the original config_root
        if "config_root" in configuration:
            # if we already have a config root then we only keep new config root if it's not the home location
            # i.e. if it is the home configuration, we don't delete the new config_root
            if configuration["config_root"] != os.path.dirname(self.home_dir_configuration_location()):
                if "config_root" in result:
                    del result["config_root"]

        config_root = configuration.get("config_root")
        if config_root and src.startswith(config_root):
            src = "{{config_root}}/{0}".format(src[len(config_root) + 1:])

        configuration.update(result, source=src)

        if "salm" in result:
            if "extra_files" in result["salm"]:
                spec = sb.listof(sb.formatted(sb.string_spec(), formatter=MergedOptionStringFormatter))
                config_root = {"config_root": result.get("config_root", configuration.get("config_root"))}
                meta = Meta(MergedOptions.using(result, config_root), []).at("harpoon").at("extra_files")
                for extra in spec.normalise(meta, result["salm"]["extra_files"]):
                    if os.path.abspath(extra) not in done:
                        if not os.path.exists(extra):
                            raise BadConfiguration("Specified extra file doesn't exist", extra=extra, source=src)
                        collect_another_source(extra)

    def extra_configuration_collection(self, configuration):
        """
        Hook to do any extra configuration collection or converter registration
        """
        self.register_converters(
              { (0, ("functions", )): sb.dictof(sb.string_spec(), sb.listof(function_spec()))
              , (0, ("salm", )): Salm.FieldSpec(formatter=MergedOptionStringFormatter)
              }
            , Meta, configuration, sb.NotSpecified
            )
