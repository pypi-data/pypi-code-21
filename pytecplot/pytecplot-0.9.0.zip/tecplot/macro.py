import logging
import re
from textwrap import dedent

from .tecutil import _tecutil, lock
from .exception import TecplotLogicError, TecplotSystemError, TecplotMacroError

log = logging.getLogger(__name__)


@lock()
def execute_function(name, parameters=None):
    """Runs a macro function.

    Parameters:
        name: (`string <str>`): Name of the macro function to run. This name
            is not case sensitive. Must be a non-zero length `string <str>`.

        parameters: (`string <str>`): Any parameters which the quick macro
            requires. Pass `None` (default) for macro functions which require no
            parameters. The parameters are passed as a string which includes
            the parenthesis. For example, if the macro function takes a
            string parameter and int parameter, pass
            **'("string_parameter_name", 2)'** Default: `None`

    Macro functions must be defined before they are used. Typically they
    are defined in the 'tecplot.mcr' configuration file which is read
    when |Tecplot Engine| is initialized. Macro functions
    may also be available in the Quick Macro Panel when the Tecplot 360 GUI
    is running.

    .. note::
        See the |Tecplot Macro Scripting Guide| for more information about
        macro functions.

    Run the "Tile Frames" macro functions. This macro function is defined in
    the file "tecplot.mcr", which is located in the Tecplot 360
    installation directory::

        >>> tecplot.macro.execute_function('Tile Frames')

    Run a macro function named "Calculate" which takes no parameters and
    another macro function called "Display" which takes the name of a
    layout file and an integer as parameters::

        >>> tp.macro.execute_function('Calculate')
        >>> tp.macro.execute_function('Display', '("contour.lay", 2)')
    """
    try:
        if not _tecutil.MacroRunFunction(
                name.strip(),
                parameters.strip() if parameters else None):
            raise TecplotMacroError(name)
    except (TecplotLogicError, TecplotSystemError) as e:
        raise TecplotMacroError(str(e))


@lock()
def execute_command(command):
    """Runs a series of tecplot macro commands.

    Parameters:
        command (`string <str>`): The macro commands to be run.

    Raises:
        `TecplotMacroError`: Message will specify the command that failed.

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    This command splits the input into individual commands and runs them one
    at a time. See the |Tecplot Macro Scripting Guide| for details about
    |Tecplot 360|'s macro language.

    .. warning::
        The $!VARSET command is not supported. Tecplot Macro variables should be
        converted to Python variables.

    .. warning::
        Intrinsic variables (that is, variables with pipes such as
        ``|DATASETFNAME|``) are not supported. If you need to use an intrinsic
        variable in the macro command, add the macro command to a text file and
        call `execute_file`.

    See the |Tecplot Macro Scripting Guide| for more information about raw data
    and intrinsic variables.

    The following command will perform the same operations as the
    `Hello, World! example <hello_world>`::

        >>> tecplot.macro.execute_command(r'''
        ...   $!ATTACHTEXT
        ...     ANCHORPOS { X = 35 Y = 50 }
        ...     TEXTSHAPE { HEIGHT = 35 }
        ...     TEXT = 'Hello, World!'
        ...   $!EXPORTSETUP EXPORTFNAME = 'hello_world.png'
        ...   $!EXPORT
        ...     EXPORTREGION = CURRENTFRAME
        ... ''')
    """
    comments = re.compile(r'(?<!\\)(\".*?\"|\'.*?\')|(#[^\r\n]*$)', re.MULTILINE)
    pattern = re.compile(r'(\$!.*?)(?=\$!)|(\$!.*)', re.MULTILINE | re.DOTALL)
    varset = re.compile(r'\$!VARSET.*', re.IGNORECASE)
    command = comments.sub(lambda m: m.group(1) or '', command)
    for match in pattern.finditer(command):
        c = (match.group(1) or match.group(2)).strip()
        if __debug__:
            if varset.match(c):
                msg = ('The $!VARSET command is not supported in\n'
                       'execute_macro(). Python variables should be used\n'
                       'instead of macro variables. Alternatively, you can\n'
                       'execute a macro in a file with '
                       'macro.execute_file().\n'
                       '$!VARSET is supported in execute_file()')
                raise TecplotMacroError(c + '\n' + msg)
            log.debug('executing command:\n' + c)
        try:
            if not _tecutil.MacroExecuteCommand(c):
                raise TecplotMacroError(c)
        except (TecplotLogicError, TecplotSystemError):
            raise TecplotMacroError()


@lock()
def execute_extended_command(command_processor_id, command, raw_data=None):
    """Runs a tecplot macro command defined in an addon.

    Parameters:
        command_processor_id (`string <str>`):  A unique string used to
            determine the API to call when an extended macro command is
            processed. API's are provided by add-ons or applications
            that extend the Tecplot macro language.

            Typically this will be the name of an add-on or application,
            followed by a version number. For example: 'CFDAnalyzer4'.

            Each application or add-on may provide one or more unique
            command processor ID strings corresponding to different API's,
            or different versions of an API.

            For example, a file converter add-on responsible
            for converting DXF files for Tecplot might provide two versions
            of an API:
            "DXFCONVERTTOOL-1.2", and "DXFCONVERTTOOL-2.0".
            In that case either of these strings would be passed in the
            *command_processor_id* parameter to indicate the version of the
            API to use.

        command (`string <str>`): The command to run.
        raw_data (`string <str>`): Raw data required for the command, if any
            (default: `None`).

    Raises:
        `TecplotMacroError`

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    In general, the command string is formatted prior to being fed into the
    |Tecplot Engine| so liberal use of whitespace, including new-lines, are
    acceptable.

    Example::

        >>> tecplot.macro.execute_extended_command(
        ...     'Multi Frame Manager',
        ...     'TILEFRAMESSQUARE')
    """
    try:
        if not _tecutil.MacroExecuteExtendedCommand(
                command_processor_id, command.replace('\n', ' '), raw_data):
            raise TecplotMacroError(command)
    except AttributeError:
        command = dedent('''
                $!EXTENDEDCOMMAND
                  COMMANDPROCESSORID = '{procid}'
                  COMMAND = '{cmd}'
            '''.format(procid=command_processor_id,
                       cmd=' '.join(command. split()).replace(r"'", r"\'")))
        execute_command(command)
    except TecplotLogicError:
        raise TecplotMacroError()


@lock()
def execute_file(filename):
    """Run a macro file.

    Parameters:
        filename (`string <str>`): The file to be run.

    Raises:
        `TecplotMacroError`

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    Example::

        >>> tecplot.macro.execute_file('/path/to/macro_file.mcr')
    """
    try:
        if not _tecutil.MacroRunFile(filename):
            raise TecplotMacroError(filename)
    except (TecplotLogicError, TecplotSystemError) as e:
        raise TecplotMacroError(str(e))
