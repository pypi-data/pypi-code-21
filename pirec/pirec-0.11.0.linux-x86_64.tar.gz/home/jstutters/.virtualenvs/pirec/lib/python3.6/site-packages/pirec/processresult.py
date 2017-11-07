"""Main pirec module containing the Pipeline class and function recording methods."""

# pylint: disable=attribute-defined-outside-init

from __future__ import print_function
from collections import Mapping
import datetime
import json
import os
import os.path
import shutil
from subprocess import check_output, STDOUT, CalledProcessError
import tarfile
import tempfile
import traceback
import wrapt
import pirec.environment
import pirec.artefacts


class Pipeline(object):
    """Main class managing the recording of a processing pipeline."""

    def __init__(self):
        """Initialize members that are referenced by call()."""
        self.processes = []
        self.results = {}

    def run(self, name, pipeline_func, base_dir, *inputs, **kwargs):
        """Execute a function as a recorded pipeline.

        Args:
            name (str): The name of the pipeline - used to name the output file.
            pipeline_function (function): The function to be run.
            base_dir (str): The directory in which to save the pipeline output, also
                used as the root directory for input filenames if the filenames given
                are not absolute.
            *inputs: The inputs to the pipeline.

        Keyword Args:
            metadata (dict): Additional information to be included in the result JSON.
            filename (str): String template for the result filename.
            result_recorder (object): An instance of a class implementing a `write()`
                method that accepts the report dictionary.
            result_names (str): An iterable of strings containing the names for any values
                returned by the pipeline.
            report_name (str): Filename for the JSON report (default: `report.json`).
            sentry (raven.Client): A Sentry.IO client.
        """
        self.processes = []
        self.debug = kwargs.get('debug', False)
        self.metadata = kwargs.get('metadata', None)
        self.result_recorder = kwargs.get('recorder', None)
        self.filename = kwargs.get('filename', '{name}-{start_date:%Y%m%d_%H%M}')
        self.report_name = kwargs.get('report_name', 'report.json')
        result_names = kwargs.get('result_names', None)
        self.results = {}
        self.name = name
        self.inputs = inputs
        self.base_dir = base_dir
        self.launched_dir = os.getcwd()
        self._copy_input_files_to_work_dir()
        self.start_date = datetime.datetime.now()
        sentry = kwargs.get('sentry', None)
        if sentry is not None:
            sentry.user_context({
                'pipeline_name': self.name,
                'metadata': self.metadata
            })
        os.chdir(self.working_dir)
        pipeline_exception = None
        pipeline_return = None
        try:
            pipeline_return = pipeline_func(*inputs)
        except Exception as e:
            if sentry is not None:
                sentry.captureException()
            pipeline_exception = e
            traceback.print_exc()
        finally:
            self._make_results_dict(pipeline_return, result_names)
            self.finish_date = datetime.datetime.now()
            os.chdir(self.launched_dir)
            self.save(pipeline_exception, report_name=self.report_name)
            shutil.rmtree(self.working_dir)

    def _make_results_dict(self, results, result_names=None):
        """Store returned values from the pipeline in a dictionary.

        If an iterable was passed to :func:`run()` this will be used as the keys to the dictionary
        otherwise the keys will be numbered '0', '1'...

        Args:
            results (object or tuple): The result(s) to record.

        Keyword Args:
            result_names (str): An iterable containing the names for the results.

        Raises:
            ValueError: if the number of results and result names does not match.
        """
        if results is not None:
            if not hasattr(results, '__iter__'):
                results = (results,)
            if result_names is None:
                result_names = [str(i) for i in range(len(results))]
            if len(result_names) != len(results):
                raise ValueError
            self.results = dict(zip(
                result_names,
                results
            ))

    def _copy_input_files_to_work_dir(self):
        """Copy any input files to working directory.

        If an input argument is a subclass of
        :class:`pirec.artefacts.Artefact` copy the file it refers to into
        the working directory.
        """
        self.working_dir = tempfile.mkdtemp(prefix='pirec_{0}_'.format(self.name))
        for i in self.inputs:
            if not issubclass(type(i), pirec.artefacts.Artefact):
                continue
            if not i.filename.startswith('/'):
                # path is relative
                dest_dir = os.path.join(self.working_dir, os.path.dirname(i.filename))
                source = os.path.join(self.base_dir, i.filename)
            else:
                # path is absolute
                dest_dir = os.path.join(self.working_dir)
                source = i.filename
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            shutil.copy(source, dest_dir)

    def _store_printed_output(self):
        """Write any printed output from pipeline processes to a file."""
        with open('printed_output.txt', 'w') as printed_output_record:
            for r in self.processes:
                printed_output_record.write(r.output)

    def record(self, process):
        """Record a process in this pipeline.

        Args:
            process (:class:`pirec.processresult.ProcessOutput`): The new result.
        """
        self.processes.append(process)

    def save(self, exception=None, report_name='report.json'):
        """Save a record of the pipeline execution.

        Creates a JSON file with information about the pipeline then saves it
        to a gzipped tar file along with all files used in the pipeline.

        Keyword args:
            exception (:class:`exceptions.Exception` or `None`): The exception which caused the
                pipeline run to fail
        """
        report = {
            'name': self.name,
            'environment': pirec.environment.get_environment(),
            'inputs': [repr(f) for f in self.inputs],
            'dir': self.base_dir,
            'start_date': self.start_date.strftime('%Y%m%d %H:%M'),
            'finish_date': self.finish_date.strftime('%Y%m%d %H:%M'),
            'results': self.results,
        }

        if exception is not None:
            report['pipeline_exception'] = repr(exception)
        if self.metadata is not None:
            report['metadata'] = self.metadata
        report['processes'] = [r.as_dict() for r in self.processes]
        basename = self.filename.format(
            metadata=self.metadata,
            name=self.name,
            start_date=self.start_date
        )
        with open(os.path.join(self.working_dir, report_name), 'w') as f:
            json.dump(report, f, indent=4, separators=(',', ': '))
        archive = tarfile.open(self._clear_filename(self.base_dir, basename, '.tar.gz'), 'w:gz')
        archive.add(self.working_dir, arcname=basename)
        archive.close()
        if self.result_recorder is not None:
            if hasattr(self.result_recorder, '__iter__'):
                for r in self.result_recorder:
                    r.write(report)
            else:
                self.result_recorder.write(report)

    def _clear_filename(self, directory, basename, ext):
        """Build a filename that doesn't already exist by appending then incrementing a number.

        Args:
            directory (str): The directory to use.
            basename (str): The basename part of the filename.
            ext (str): The extension part of the filename.

        Returns:
            str: If it doesn't exist returns `directory/basename.ext` otherwise
            returns the first available `directory/basename-xx.ext` where x is
            a counter from 01.
        """
        tgt = os.path.join(directory, basename + ext)
        if os.path.exists(tgt):
            inc = 1
            tgt = os.path.join(directory, '{0}-{1:02d}{2}'.format(basename, inc, ext))
            while os.path.exists(tgt):
                inc += 1
                tgt = os.path.join(directory, '{0}-{1:02d}{2}'.format(basename, inc, ext))
        return tgt


pipeline = Pipeline()


class OutputRecorder(object):
    """Holds commands used via the call function and their resulting output."""

    def __init__(self):
        """Initialize and clear the recorder."""
        self.reset()

    def reset(self):
        """Clear the stored commands and output."""
        self.commands = []
        self.output = b''


_output_recorder = OutputRecorder()


def call(cmd, cwd=None, shell=False):
    """Execute scripts and applications in a pipeline with output capturing.

    Args:
        cmd (list): List containing the program to be called and any arguments
            e.g. ``['tar', '-x', '-f', 'file.tgz']``.
        cwd (str): Working directory in which to execute the command.
        shell (bool): Execute the command in a shell.

    Returns:
        str: The output from the called command on stdout and stderr.
    """
    output = None
    try:
        _output_recorder.commands.append(cmd)
        output = check_output(cmd, stderr=STDOUT, cwd=cwd, shell=shell)
        _output_recorder.output += output
    except CalledProcessError as e:
        print('An error occurred during: {}'.format(' '.join(cmd)))
        print('Output before failure:')
        print(e.output)
        _output_recorder.output = e.output
        raise
    return output


def record(*output_names):
    """Decorator for wrapping pipeline stages.

    Args:
        *output_names (str): The names of each returned variable.
    """
    @wrapt.decorator
    def process_recorder(wrapped, _, args, kwargs):
        """Execute and record the wrapped function."""
        returned_from_process = None
        exception = None
        _output_recorder.reset()
        started = datetime.datetime.now()
        try:
            returned_from_process = wrapped(*args, **kwargs)
        except:
            exception = traceback.format_exc()
            raise
        finally:
            if not isinstance(returned_from_process, tuple):
                returned_from_process = (returned_from_process,)
            finished = datetime.datetime.now()
            named_returns = dict(zip(output_names, returned_from_process))
            result = ProcessOutput(
                func=wrapped,
                args=args,
                kwargs=kwargs,
                commands=_output_recorder.commands,
                output=_output_recorder.output.strip(),
                exception=exception,
                started=started,
                finished=finished,
                **named_returns
            )
            pipeline.record(result)
        return result
    return process_recorder


class ProcessOutput(Mapping):
    """A record of one stage within a pipeline.

    Args:
        func (function): The function that was run.
        args (list): The arguments passed to the function.
        kwargs (dict): The keyword arguments passed to the function.
        output (str): Text printed to stdout or stderr during execution.
        exception (:class:`exceptions.Exception` or `None`): The exception that occurred
            running the stage if applicable.
        started (:class:`datetime.datetime`): When the stage was started.
        finished (:class:`datetime.datetime`): When the stage finished executing.
        **output_images (:class:`pirec.artefacts.Artefact`): Images produced by the stage.
    """

    def __init__(self, func, args, kwargs, commands, output, exception, started, finished,
                 **output_images):
        """Initialize the record."""
        self._results = output_images
        self.commands = commands
        self.output = output
        self.function = func
        self.input_args = args
        self.input_kwargs = kwargs
        self.exception = exception
        self.started = started
        self.finished = finished

    def __repr__(self):
        r = self.function.__name__ + '('
        if self.input_args:
            r += ', '.join([repr(x) for x in self.input_args])
        if self.input_kwargs:
            r += ', '.join(['{0}={1!r}'.format(x, self.input_kwargs[x]) for x in self.input_kwargs])
        r += ')'
        return r

    def as_dict(self):
        """Serialize this output as a ``dict``."""
        d = {
            'function': self.function.__name__,
            'input_args': [repr(x) for x in self.input_args],
            'input_kwargs': {str(x): repr(self.input_kwargs[x]) for x in self.input_kwargs},
            'called_commands': [' '.join(c) for c in self.commands],
            'printed_output': self.output.decode('utf-8'),
            'returned': [repr(r) for r in self._results.values()],
            'start_time': self.started.strftime('%Y%m%d %H:%M'),
            'finish_time': self.finished.strftime('%Y%m%d %H:%M')
        }
        if self.exception:
            d['exception'] = repr(self.exception)
        return d

    def __getitem__(self, key):
        """Get the item corresponding to ``key`` in the ``_results`` dictionary."""
        return self._results.__getitem__(key)

    def __len__(self):
        """Get the length of the ``_results`` dictionary."""
        return self._results.__len__()

    def __iter__(self):
        """Get an iterable over the keys in the ``_results`` dictionary."""
        return self._results.__iter__()
