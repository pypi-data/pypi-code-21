import sys
import logging
import traceback
import click
import click_log
import crayons

from pathlib import Path

from cvbuilder.__version__ import __version__, __cv2version__
from cvbuilder import builder, utils, systems

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    logger.info(__version__)
    ctx.exit()


def format_help(help):
    """Formats the help string."""
    # help = help.replace('Options:', str(crayons.white('Options:', bold=True)))

    help = help.replace('Usage: cvbuilder', str('Usage: {0}'.format(crayons.normal('cvbuilder', bold=True))))

    help = help.replace('  build', str(crayons.green('  build', bold=True)))
    help = help.replace('  system', str(crayons.yellow('  system', bold=True)))
    help = help.replace('  dump', str(crayons.yellow('  dump', bold=False)))
    help = help.replace('  configure', str(crayons.white('  configure', bold=False)))
    help = help.replace('  download', str(crayons.white('  download', bold=False)))
    help = help.replace('  make', str(crayons.white('  make', bold=False)))
    help = help.replace('  install', str(crayons.white('  install', bold=False)))

    additional_help = """
Usage Examples:
   Download, configure, build and install OpenCV in one step:
   $ {build}
   If you want to run the process again, without downloading the sources:
   $ {clean}
   Check other available command via:
   $ {plain}
   or via:
   $ {help}
   
Commands:""".format(**{
        "build": crayons.green('cvbuilder build', bold=True),
        "clean": crayons.green('cvbuilder build {}'.format(crayons.yellow("--clean", bold=True)), bold=True),
        "plain": crayons.yellow('cvbuilder'),
        "help": crayons.yellow('cvbuilder {}'.format(crayons.yellow('--help', bold=True)))},
                    )

    help = help.replace('Commands:', additional_help)

    return help


def verify_virtual_env(ctx, param, value):
    if value is not None:
        current_venv = sys.exec_prefix

        if value != current_venv:
            logger.warning("The virtual environment environment variable does not match the current: {} vs. {}"
                           .format(crayons.red(value, bold=True), crayons.red(current_venv, bold=True)))

            if not value or value == "":
                return Path(current_venv)

        return Path(value)


def verify_temp_dir(ctx, param, value):
    if value is not None:
        tmp_dir = Path(value)

        if not tmp_dir.exists():
            tmp_dir.mkdir()

        # TODO add size check

        return tmp_dir


# TODO args required?
def safe_command(name=None, cls=None, *args, **kwargs):
    def decorator(f):
        # holy mackerel
        def func_wrapper(*args, **kwargs):
            command = crayons.yellow(f.__name__)

            try:
                f(*args, **kwargs)
            except KeyboardInterrupt:
                logger.warning("Manually interrupted {} command .".format(command))
            except Exception as ex:
                logger.error('An exception occurred: {} {}!'.format(crayons.red(ex, bold=True), traceback.format_exc()))
                sys.exit(1)
            else:
                logger.info("Successfully finished {} command.".format(command))
                sys.exit(0)
            return

        return click.command(name=f.__name__, **kwargs)(func_wrapper)

    return decorator


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option(prog_name=crayons.clean('cvbuilder', ), version=__version__)
@click.pass_context
def cli(
        ctx, help=False, completion=False
):
    print("Command", ctx.invoked_subcommand)
    # Check this again before exiting for empty ``pipenv`` command.
    if ctx.invoked_subcommand is None:
        # Display help to user, if no commands were passed.
        logger.info(format_help(ctx.get_help()))



@click.option('--enable-video/--disable-video', default=True, help='enable video capabilities')
@click.option('--enable-gui/--disable-gui', default=True, help='enable GUI (GTK) capabilities')
@safe_command(short_help="""Installs system dependencies.""")
@click_log.simple_verbosity_option(logger)
def system(enable_video: bool, enable_gui: bool):
    settings = ""
    settings += "video: " + crayons.green("enabled") if enable_video else "disabled"
    settings += " | gui: " + crayons.green("enabled") if enable_gui else "disabled"
    logger.info(settings)

    # TODO move to systems or cvbuilder?
    lsb = systems.get_system()
    deps = systems.get_system_dependencies(lsb)
    packages = deps.get("packages")

    install_command = packages.get("command")
    package_list = utils.select_packages(packages=packages, enable_gui=enable_gui, enable_video=enable_video)
    utils.install_packages(command=install_command, package_list=package_list, requires_sudo=True)


@click.option('--preserve/--clean', default=True, help='Preserve the downloaded packages')
@click.option('tempdir', '--tmpdir', multiple=False, type=click.Path(), callback=verify_temp_dir,
              default=str(builder.tmp_dir), help="The temporary download directory.")
@safe_command(short_help="""Downloads the OpenCV sources to the specified temporary directory."""
              .format(__cv2version__), context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click_log.simple_verbosity_option(logger)
def download(preserve: bool, tempdir: Path):
    settings = ""
    settings += "source: " + crayons.green("preserve") if preserve else "clean"
    settings += " | tempdir: " + crayons.green(tempdir, bold=True)
    logger.info(settings)

    builder.download(preserve=preserve, tempdir=tempdir)


@click.option('tempdir', '--tmpdir', multiple=False, type=click.Path(), callback=verify_temp_dir,
              default=str(builder.tmp_dir), help="The temporary download directory.")
@safe_command(short_help="""Configures the downloaded OpenCV sources in the specified temporary directory.""",
              context_settings=dict(
                  ignore_unknown_options=True,
                  allow_extra_args=True
              ))
@click_log.simple_verbosity_option(logger)
def configure(tempdir: Path, verbose: bool = False):
    settings = ""
    settings += " | tempdir: " + crayons.green(tempdir, bold=True)
    settings += " | verbose: " + crayons.green(verbose, bold=True)
    logger.info(settings)
    # FIXME verbosity
    build_dir = builder.configure(tempdir=tempdir, verbose=True)


@click.option('tempdir', '--tmpdir', multiple=False, type=click.Path(), callback=verify_temp_dir,
              default=str(builder.tmp_dir), help="The temporary download directory.")
@safe_command(
    short_help="""Compiles the OpenCV sources in the specified temporary directory according to the CMake configuration.""".format(
        __cv2version__),
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    ))
@click_log.simple_verbosity_option(logger)
def make(tempdir: Path):
    settings = ""
    settings += " | tempdir: " + crayons.green(tempdir, bold=True)
    logger.info(settings)
    builder.build(tempdir=tempdir)


@click.option('tempdir', '--tmpdir', multiple=False, type=click.Path(), callback=verify_temp_dir,
              default=str(builder.tmp_dir), help="The temporary download directory.")
@safe_command(short_help="""Installs OpenCV from the specified temporary 
                    directory.""".format(__cv2version__),
              context_settings=dict(
                  ignore_unknown_options=True,
                  allow_extra_args=True
              ))
@click_log.simple_verbosity_option(logger)
def install(tempdir: Path):
    settings = ""
    settings += " | tempdir: " + crayons.green(tempdir, bold=True)
    logger.info(settings)
    builder.install(tempdir=tempdir)


@safe_command(short_help="""Checks whether OpenCV is correctly configured.""".format(__cv2version__),
              context_settings=dict(
                  ignore_unknown_options=True,
                  allow_extra_args=True
              ))
@click_log.simple_verbosity_option(logger)
def check():
    builder.check()


@click.option('--preserve/--clean', default=True, help='Preserve the downloaded packages')
@click.option('virtualenv', '--venv', envvar='VIRTUAL_ENV', multiple=False, type=click.Path(),
              callback=verify_virtual_env)
@click.option('user', '--user', envvar='USER', multiple=False, type=click.STRING)
@click.version_option(prog_name=crayons.normal('cvbuilder', bold=True), version=__version__)
@safe_command(
    short_help="""Configures, makes and installs the current OpenCV version in the current (virtual) python environment.""",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    ))
@click_log.simple_verbosity_option(logger)
def build(preserve: bool = True, virtualenv: Path = None, user: str = None, verbose: bool = False):
    settings = ""
    settings += "source: " + crayons.green("preserve") if preserve else "clean"
    settings += " | user: " + crayons.green(user, bold=True)
    settings += " | venv: " + crayons.green(virtualenv, bold=True)
    settings += " | verbose: " + crayons.green(verbose, bold=True)
    logger.info(settings)

    builder.download(preserve=preserve, tempdir=builder.tmp_dir)
    builder.configure(tempdir=builder.tmp_dir, verbose=verbose)
    builder.build(tempdir=builder.tmp_dir)
    builder.install(tempdir=builder.tmp_dir)
    builder.check()


@safe_command(short_help="""Dumps environment and system information.""".format(__cv2version__),
              context_settings=dict(
                  ignore_unknown_options=True,
                  allow_extra_args=True
              ))
@click_log.simple_verbosity_option(logger)
def dump():
    builder.dump()


cli.add_command(build)
cli.add_command(system)
cli.add_command(check)
cli.add_command(download)
cli.add_command(configure)
cli.add_command(make)
cli.add_command(install)
cli.add_command(dump)

# Only invoke the "did you mean" when an argument wasn't passed (it breaks those).
if '-' not in ''.join(sys.argv) and len(sys.argv) > 1:
    cli = click.CommandCollection(sources=[cli])

if __name__ == "__main__":
    cli()
