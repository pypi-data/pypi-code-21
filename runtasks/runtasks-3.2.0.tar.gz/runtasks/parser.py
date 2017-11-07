import sys, logging, re
from collections import OrderedDict

logger = logging.getLogger('')

re_int = re.compile(r'^\d+$')


class HelpWanted(Exception):
    pass


def parse(args, tasks):
    """
    Parses command line arguments into groups of tasks and arguments to those tasks.

    Returns a sequence of (Task, args) pairs where the arguments are an inspect.BoundArguments
    instance.  If "--help" was passed as one of the arguments, the args element will simply be
    the string "help".  (I need a better API for this.)
    """
    results = []

    other_names = list(tasks.keys())

    while args:
        task = tasks.get(args[0])
        if not task:
            sys.exit("""There is no task named %r.  Use "run --list" to list available tasks.""" % args[0])
        try:
            boundargs, args = parse_task(task, args, other_names)
            results.append((task, boundargs))
        except HelpWanted:
            results.append((task, "help"))
            break

    return results


def parse_task(task, cmdline, other_names):
    """
    Parses the arguments for a single task.  Raises an exception if all required arguments are
    not provided.

    Since the command line may contain multiple tasks, it stops when all parameters have been
    assigned or when unrecognized tokens are found.

    cmdline:
      An array of strings, originally from sys.argv.  The name of this task will be the first
      item.

    other_names
      Names of other defined tasks.

    Returns the tasks arguments as an inspect.BoundArguments instance and the remaining,
    unparsed arguments: (BoundArguments, remaning-cmdline)
    """
    # How many positional parameters are required?  If there are unrecognized tokens we'll
    # assume they are values for these.  For example:
    #
    #   @task test(arg1, arg2=None)
    #
    #   build test xyz --> arg1=xyz
    #
    # We only read positional parameters like this until we hit the first parameter with
    # equals or dashes ("--arg1" or "arg1=xyz", etc.).  Once we hit one of those, we'll set
    # `positional` to None to indicate so.

    positional = list(task.sig.parameters.values())

    parsed = OrderedDict()
    # We'll copy values from the command line (tokens) to here by parameter name.

    cmdline = cmdline[1:]  # we've now copied it

    while cmdline:
        arg = cmdline[0]

        if arg == '--help' and 'help' not in task.sig.parameters:
            raise HelpWanted()

        if arg.startswith('--'):
            positional = None  # Now that we've seen a named item, no more positional.
            _parse_double_dash(task, cmdline, parsed)

        elif arg.startswith('-'):
            positional = None  # Now that we've seen a named item, no more positional.
            _parse_flags(task, cmdline, parsed)

        elif '=' in arg:
            positional = None  # Now that we've seen a named item, no more positional.
            _parse_equals(task, cmdline, parsed)

        elif task.allow_positional and positional and arg not in other_names:
            param = positional.pop(0)
            _parse_param(task, param, False, None, cmdline, parsed)

        else:
            break

    # Now make sure all of the required arguments have a default value.  Fortunately
    # Signature.bind will do this, raising a TypeError if anything is wrong.  We'll steal
    # the message from the TypeError.

    try:
        b = task.sig.bind(**parsed)

        if hasattr(b, 'apply_defaults'):
            # Use python 3
            b.apply_defaults()
        else:
            # python 2 and funcsigs does not have an equivalent apply_defaults so the remainder of this `else` is
            # basically a copy of python 3's inspect.BoundArguments.apply_defaults.
            import funcsigs
            arguments = b.arguments
            new_arguments = []
            for name, param in task.sig.parameters.items():
                try:
                    new_arguments.append((name, arguments[name]))
                except KeyError:
                    if param.default is not funcsigs.Parameter.empty:
                        val = param.default
                    elif param.kind is funcsigs.Parameter.VAR_POSITIONAL:
                        val = ()
                    elif param.kind is funcsigs.Parameter.VAR_KEYWORD:
                        val = {}
                    else:
                        # This BoundArguments was likely produced by
                        # Signature.bind_partial().
                        continue
                    new_arguments.append((name, val))
            b.arguments = OrderedDict(new_arguments)

        return b, cmdline
    except TypeError as ex:
        sys.exit('Task %s: %s' % (task.name, ex))


def _parse_double_dash(task, cmdline, parsed):
    """
    Parses a "--arg" token.

    If successful, remove the tokens used from `cmdline` and add the values to the `parsed`
    dictionary.
    """
    name  = cmdline.pop(0)[2:]
    value = None

    if '=' in name:
        name, value = name.split('=', 1)

    paramname = name.replace('-', '_')
    param = task.sig.parameters.get(paramname)

    if not param and name.startswith('no-'):
        # If a parameter was defined as "arg=True" then we accept "--no-arg" to set the
        # value to False.
        param = task.sig.parameters.get(paramname[3:])
        if param:
            if value is not None:
                sys.exit('You cannot provide a value for a "no-" prefixed flag')
            value = '0'

    if not param:
        sys.exit('Task %s does not accept an argument %r' % (task.name, name))

    _parse_param(task, param, True, value, cmdline, parsed)


def _parse_param(task, param, named, value, cmdline, parsed):
    """
    A helper to consolidate the parsing of a single parameter, regardless of its format (long
    name or short name).  If successful, the parameter's value will be added to `parsed`.
    Otherwise an error is raised.

    param
      The inspect.Parameter object from the function representing the parameter we are working
      on.

    named
      Pass true if this parameter was named ("--flag" or "-f").  Pass false if only a value was
      passed and the parameter was positional.

    value
      An optional value that was passed as part of this parameter with an equals sign, such as
      `--test=value`.  This must be the string value and should be None if no value was passed.

      If this is provided, it will be used as the value and the type will be checked against
      the parameter's default value.

    cmdline
      The array of unprocessed command line parameters.  If the parameter requires a value, it
      may take the next token in the command line as the value.  If it does, the value will be
      removed from the array.

      This is not used if `value` is provided.

    parsed
      Previously parsed parameters for this command.  This is a dictionary mapping from
      parameter name to the value.  Note that parameters that were not on the command are not
      present even if they have default values.

      If no error is raised, this parameter will be added.
    """
    # REVIEW: The duplicate checking is duplicated, but I can't think of a good way to
    # consolidate it without duplicating the "is counter" check.  I supposed we could set a
    # Boolean at the top and have all code fall through.  The counter code could turn it off.
    # Right now we have 3 small chunks which are easy to reason about - falling through turns
    # it into one large chunk.

    next_token = (cmdline[0] if cmdline else None)

    if isinstance(param.default, bool):
        # The default value is a Boolean, so we normally would not expect a value and would not
        # use the next token - the value is simply set to True: --verbose
        #
        # If a value is provided with an equals, it must be 0 or 1: --verbose=1
        #
        # If the next token is a 0 or 1, we'll take it: --verbose 1

        if param.name in parsed:
            sys.exit('Task %s parameter %s was provided more than once' % (task.name, param.name))

        if value is not None:
            if value not in '01':
                sys.exit('Task %s parameter %s is a Boolean and cannot take the value %r' % (
                    task.name, param.name, value))
            parsed[param.name] = bool(int(value))
        elif next_token and next_token in '01':
            cmdline.pop(0)
            parsed[param.name] = bool(int(next_token))
        else:
            if named:
                parsed[param.name] = True
        return

    if isinstance(param.default, int):

        if value is not None:
            if not re_int.match(value):
                sys.exit('Task %s parameter %s is a Boolean and cannot take the value %r' (
                    task.name, param.name, value))
            if param.name in parsed:
                sys.exit('Task %s parameter %s was provided more than once' % (task.name, param.name))
            parsed[param.name] = int(value)
        elif next_token and re_int.match(next_token):
            if param.name in parsed:
                sys.exit('Task %s parameter %s was provided more than once' % (task.name, param.name))
            cmdline.pop(0)
            parsed[param.name] = int(next_token)
        else:
            # There is no value so we'll treat it as a counter to make it easy to do things like "-vvv"
            parsed[param.name] = parsed.get(param.name, param.default) + 1

        return

    if param.name in parsed:
        sys.exit('Task %s parameter %s was provided more than once' % (task.name, param.name))

    if value:
        parsed[param.name] = value
    elif next_token:
        parsed[param.name] = next_token
        cmdline.pop(0)
    else:
        if not next_token:
            sys.exit('Task %s argument %s was not provided a value' % (task.name, param.name))


def _parse_equals(task, cmdline, parsed):
    """
    Parse a "name=value" arg token.

    The tokens for this argument are removed from the front of cmdline.  (The first token is
    the name of the option.  The second token may be the value.)
    """
    name, value  = cmdline.pop(0).split('=', 1)

    paramname = name.replace('-', '_')
    param = task.sig.parameters.get(paramname)

    if not param:
        sys.exit('Task %s does not accept an argument %r' % (task.name, name))

    _parse_param(task, param, True, value, cmdline, parsed)


def _parse_flags(task, cmdline, parsed):
    """
    Parse "-fx value" type arguments and write their values into `parsed`.

    Removes parsed tokens from `cmdline`.
    """
    flags = cmdline.pop(0)[1:]  # remove the leading dash

    # Cycle through the characters one at a time.

    for i, flag in enumerate(flags):
        name = task.flags.get(flag)
        if not name:
            sys.exit('Task %s does not accept a -%r flag' % (task.name, flag))

        param = task.sig.parameters[name]

        if flags[i + 1:i + 2] == '=':
            # The next character is an equals sign, so everything after it becomes the value
            # for the current letter:
            #
            #     -xyz=test
            #
            # The "z" parameter will be assigned the value "test".
            value = flags[i + 2:]
            _parse_param(task, param, True, value, None, parsed)
            return

        # If not the last flag, like 'x' and 'y' below, no value is provided and the flag is
        # not allowed to take the next token ("test") as its value.  We pass None for both the
        # value and the command line.
        #
        #     -xyz test
        #
        # If this is the last flag, like 'z', then it is allowed to take the next command line
        # token as a value, so we pass cmdline.  If it does take it, it will remove it from
        # cmdline.

        is_last = (i == len(flags) - 1)
        c       = is_last and cmdline or None
        value   = None

        _parse_param(task, param, True, value, c, parsed)
