from flask.cli import DispatchingApp, pass_script_info
from flask.helpers import get_debug_flag
import click
import os
import sys
import pipes
from collections import OrderedDict
import honcho.environ
import honcho.manager
import honcho.process
from frasco.utils import get_reloader_extra_files
from frasco.commands import shell_exec


def join_process_args(args):
    return " ".join([(pipes.quote(s) if not s.startswith("$") else s) for s in args])


def procfile_processes(processes, info):
    procfile = OrderedDict()
    for name, args in processes:
        args = list(args)
        base = []
        if args[0] == "frasco":
            del args[0]
            base = ["python", "-m", "frasco"]
            if info.app_import_path:
                base.extend(["-a", info.app_import_path])
        procfile[name] = join_process_args(base + map(str, args))
    return procfile


def get_app_processes(info):
    app = info.load_app()
    serve_process = ("web", ["frasco", "serve", "--host", "$HOST", "--port", "$PORT"])
    return procfile_processes([serve_process] + app.processes, info)


def start_honcho(processes, env=None):
    manager = honcho.manager.Manager()
    for p in honcho.environ.expand_processes(processes, env=env):
        e = os.environ.copy()
        e.update(p.env)
        manager.add_process(p.name, p.cmd, env=e)
    manager.loop()
    sys.exit(manager.returncode)


@click.command('run', short_help='Runs a development server and associated workers.')
@click.option('--host', '-h', default='127.0.0.1',
              help='The interface to bind to.')
@click.option('--port', '-p', default=5000,
              help='The port to bind to.')
@click.option('--procfile/--no-procfile', default=False,
              help='Whether to look for a Procfile.')
@click.argument('process', required=False)
@pass_script_info
def run_command(info, host, port, procfile, process):
    processes = None
    if procfile:
        for filename in ["Procfile.%s" % info.env, "Procfile"]:
            if os.path.exists(filename):
                click.echo("Using %s" % filename)
                with open(filename) as f:
                    content = f.read()
                processes = honcho.environ.parse_procfile(content).processes
                break

    if not processes:
        processes = get_app_processes(info)

    if process:
        if process not in processes:
            click.echo('Unknown process %s' % process)
            sys.exit(1)
        click.echo('Only running process %s' % process)
        processes = dict([(process, processes[process])])

    start_honcho(processes, {"HOST": host, "PORT": port})


@click.command('start', short_help='Start a single named process')
@click.argument('process')
@pass_script_info
def start_command(info, process):
    processes = get_app_processes(info)
    if process not in processes:
        click.echo('Unknown process %s' % process)
        sys.exit(1)
    processes = dict([(process, processes[process])])
    start_honcho(processes)


@click.command('echo-process-cmd', short_help='Echo the command line needed to run a process')
@click.argument('process')
@pass_script_info
def echo_process_command(info, process):
    processes = get_app_processes(info)
    if process not in processes:
        click.echo('Unknown process %s' % process)
        sys.exit(1)
    click.echo(processes[process])


# Unfortunately, there are no way to add options to run_simple
# without redifining the whole command

@click.command('serve', short_help='Runs a development server.')
@click.option('--host', '-h', default='127.0.0.1',
              help='The interface to bind to.')
@click.option('--port', '-p', default=5000,
              help='The port to bind to.')
@click.option('--reload/--no-reload', default=None,
              help='Enable or disable the reloader.  By default the reloader '
              'is active if debug is enabled.')
@click.option('--debugger/--no-debugger', default=None,
              help='Enable or disable the debugger.  By default the debugger '
              'is active if debug is enabled.')
@click.option('--eager-loading/--lazy-loader', default=None,
              help='Enable or disable eager loading.  By default eager '
              'loading is enabled if the reloader is disabled.')
@click.option('--with-threads/--without-threads', default=False,
              help='Enable or disable multithreading.')
@pass_script_info
def serve_command(info, host, port, reload, debugger, eager_loading,
                with_threads):
    """Runs a local development server for the Flask application.
    This local server is recommended for development purposes only but it
    can also be used for simple intranet deployments.  By default it will
    not support any sort of concurrency at all to simplify debugging.  This
    can be changed with the --with-threads option which will enable basic
    multithreading.
    The reloader and debugger are by default enabled if the debug flag of
    Flask is enabled and disabled otherwise.
    """
    from werkzeug.serving import run_simple

    debug = get_debug_flag()
    if reload is None:
        reload = bool(debug)
    if debugger is None:
        debugger = bool(debug)
    if eager_loading is None:
        eager_loading = not reload

    app = DispatchingApp(info.load_app, use_eager_loading=eager_loading)

    # Extra startup messages.  This depends a but on Werkzeug internals to
    # not double execute when the reloader kicks in.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # If we have an import path we can print it out now which can help
        # people understand what's being served.  If we do not have an
        # import path because the app was loaded through a callback then
        # we won't print anything.
        if info.app_import_path is not None:
            print(' * Serving Flask app "%s"' % info.app_import_path)
        if debug is not None:
            print(' * Forcing debug mode %s' % (debug and 'on' or 'off'))

    reloader_path = '.'
    if info.app_import_path:
        if os.path.isdir(info.app_import_path):
            reloader_path = info.app_import_path
        elif os.path.isfile(info.app_import_path):
            reloader_path = os.path.dirname(info.app_import_path)
    extra_files = get_reloader_extra_files(reloader_path)

    run_simple(host, port, app, use_reloader=reload, extra_files=extra_files,
               use_debugger=debugger, threaded=with_threads)