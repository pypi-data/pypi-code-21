from simple_aws_lambda_maker.errors import NoFunctionsSpecified, NoSuchGroup, GroupNotSpecified
from simple_aws_lambda_maker.maker import LambdaMaker

from input_algorithms import spec_base as sb
from textwrap import dedent

available_actions = {}

def an_action(func):
    available_actions[func.__name__] = func
    return func

@an_action
def help(collector, **kwargs):
    """List the available_tasks"""
    print("Available tasks to choose from are:")
    print("Use the --task option to choose one")
    print("")
    for name, action in sorted(available_actions.items()):
        print("--- {0}".format(name))
        print("----{0}".format("-" * len(name)))
        print("\n".join("\t{0}".format(line) for line in dedent(action.__doc__).split("\n")))
        print("")

@an_action
def deploy(collector, group, **kwargs):
    """Deploy our lambda functions"""
    dry_run = collector.configuration["salm"].dry_run
    functions = collector.configuration["functions"]
    if group is sb.NotSpecified:
        raise GroupNotSpecified()

    if group not in functions:
        raise NoSuchGroup(wanted=group)
    if not functions[group]:
        raise NoFunctionsSpecified()
    LambdaMaker(collector.configuration["functions"][group], dry_run=dry_run).fulfill()
