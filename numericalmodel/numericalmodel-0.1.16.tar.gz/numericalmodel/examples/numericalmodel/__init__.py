# system modules
import argparse
import logging


class NumericalModelExampleArgumentParser(argparse.ArgumentParser):
    """
    An :any:`ArgumentParser` with predefined arguments useful for command-line
    examples of :any:`NumericalModel`.
    """
    def __init__(self, *args, **kwargs):
        parser_kwargs = {"description":"NumericalModel example"}
        parser_kwargs.update(kwargs)

        super().__init__(*args, **parser_kwargs)

        self.add_argument("-g","--gui",help="run the gui (after integrating)?",
            action="store_true", default=False)
        self.add_argument("-f","--fallback", help="use gui fallback mode?",
            action="store_true", default=False)
        self.add_argument("-i","--integrate",
            help="how many seconds to integrate the model",
            type = int, required = False, default = False)
        self.add_argument("-v","--verbose", help="run verbosely",
            action = "store_true")
        self.add_argument("-d","-vv","--debug", help="run with debug output",
            action = "store_true")

        def var_value_pair(arg):
            try:
                var,value = arg.split("=")
                var,value = str(var), float(value)
            except ValueError:
                msg = "'{}' is not an assignment like VAR=VALUE".format(arg)
                raise argparse.ArgumentTypeError(msg)
            return [var,value]

        self.add_argument("plan",nargs = "*",
            help="The integration plan. Specify data changes as NAME=VALUE and "
                "add '+integrate=SECONDS' to integrate SECONDS forward",
            type = var_value_pair, default = [])

    def cli(self, model): # pragma: no cover
        """
        Run the command-line interface

        Args:
            model (NumericalModel): the model to use
        """
        clilogger = logging.getLogger("NumericalModelCLI")
        args = self.parse_args()

        loglevel = logging.WARNING
        if args.verbose:
            loglevel = min(loglevel,logging.INFO)
        if args.debug:
            loglevel = min(loglevel,logging.DEBUG)
        logging.basicConfig(level = loglevel)
        for n,l in logging.Logger.manager.loggerDict.items():
            l.level = loglevel

        clilogger.info("Model:\n{}".format(model))

        found = {}
        for var,value in args.plan:
            if var.lower() == "+integrate":
                model.integrate(model.model_time + value)
                continue
            found[var] = False
            for n in ["variables","parameters","forcing","observations"]:
                try:
                    getattr(model,n)[var].value = value
                    found[var] = True
                    break
                except KeyError:
                    pass
            if not found[var]:
                clilogger.warning("name '{}' not found in model".format(var))

        clilogger.info("Model:\n{}".format(model))

        if args.gui:
            model.gui(use_fallback = args.fallback)


