from __future__ import unicode_literals, print_function

from operator import itemgetter

from qordoba.project import ProjectAPI


def prepare_milestones(milestones):
    """
    :type milestones: list of dicts
    :return: The sorted list of milestones
    """
    names = []
    values = []
    for milestone in sorted(milestones, key=itemgetter('order')):
        names.append(milestone['name'].upper())
        values.append('{}%'.format(milestone['percent']))

    return names, values


DEFAULT_HEADERS = ('LOCALE', '#WORDS', '#SEGMENTS')


def status_command(config):
    """
    """
    api = ProjectAPI(config)
    report = api.get_report_progress()['languages']

    header = None

    for lang in report:
        names, percentage = prepare_milestones(lang['milestones'])
        if header is None:
            header = list(DEFAULT_HEADERS)
            header.extend(names)
            yield header

        row = [
            lang['code'],
            lang['total_words'],
            lang['segments'],
        ]
        row.extend(percentage)

        yield row
