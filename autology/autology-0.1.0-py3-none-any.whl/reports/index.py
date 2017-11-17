"""Report that builds the index file."""
import datetime
import pathlib

from autology import topics
from autology.publishing import publish

_reports = []

INDEX_TEMPLATE_PATH = pathlib.Path('index', 'index.html')
_index_stats = {}


def register_plugin():
    """ Subscribe to the initialize method and add default configuration values to the settings object. """
    topics.Application.INITIALIZE.subscribe(_initialize)


def _initialize():
    """ Register for all of the required events that will be fired off by the main loop """
    topics.Reporting.REGISTER_REPORT.subscribe(_new_report_handler)
    topics.Reporting.BUILD_MASTER.subscribe(_finish_processing)

    # Topics used for stat generation
    topics.Processing.BEGIN.subscribe(_record_start_time)
    topics.Processing.END.subscribe(_record_end_time)
    topics.Processing.PROCESS_FILE.subscribe(_count_processed_files)
    topics.Processing.DAY_START.subscribe(_count_days)


def _new_report_handler(report=None):
    """Build up a list of all the report objects that have been defined."""
    _reports.append(report)


def _finish_processing():
    _index_stats['generated_date'] = datetime.datetime.now()
    _index_stats['execution_time'] = (_index_stats['end_time'] - _index_stats['start_time']).total_seconds()
    publish(INDEX_TEMPLATE_PATH, 'index.html', reports=_reports, stats=_index_stats)


def _record_start_time():
    _index_stats['start_time'] = datetime.datetime.now()


def _record_end_time():
    _index_stats['end_time'] = datetime.datetime.now()


def _count_processed_files(file, date):
    count = _index_stats.setdefault('processed_files', 0)
    _index_stats['processed_files'] = count + 1


def _count_days(date):
    count = _index_stats.setdefault('num_days', 0)
    _index_stats['num_days'] = count + 1
