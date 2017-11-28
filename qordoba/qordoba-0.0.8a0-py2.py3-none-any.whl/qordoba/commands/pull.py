from __future__ import unicode_literals, print_function

import errno
import logging
import os
import shutil
from argparse import ArgumentTypeError
import requests, zipfile
# from mock.mock import self

try:
    import StringIO
except ImportError:
    import io

from qordoba.commands.utils import mkdirs, ask_select, ask_question
from qordoba.languages import get_destination_languages, get_source_language, init_language_storage, normalize_language
from qordoba.project import ProjectAPI, PageStatus
from qordoba.settings import get_pull_pattern
from qordoba.sources import create_target_path_by_pattern

log = logging.getLogger('qordoba')


def format_file_name(page):
    if page.get('version_tag'):
        return '{} [{}]'.format(page['url'], page['version_tag'])
    return page['url']


class FileUpdateOptions(object):
    skip = 'Skip'
    replace = 'Replace'
    new_name = 'Set new filename'

    all = skip, replace, new_name

    _actions = {
        'skip': skip,
        'replace': replace,
        'set_new': new_name
    }

    @classmethod
    def get_action(cls, name):
        return cls._actions.get(name, None)


class MilestoneOptions(object):
    def all(self, milestones):
        milestone_list = list()
        for key in milestones.keys():
            milestone_list.append(key)

        return tuple(milestone_list)


def validate_languges_input(languages, project_languages):
    selected_langs = set()
    for l in languages:
        selected_langs.add(normalize_language(l))

    not_valid = selected_langs.difference(set(project_languages))
    if not_valid:
        raise ArgumentTypeError('Selected languages not configured in project as dest languages: `{}`'
                                .format(','.join((str(i) for i in not_valid))))

    return list(selected_langs)


def pull_bulk(api, src_to_dest_paths, dest_languages_page_ids, dest_languages_ids, pattern):
    log.info('Starting bulk download for all files and languages in project')

    # making request to our internal api: export_files_bulk (POST). This request downloads all files for given language
    res = api.download_files(dest_languages_page_ids, dest_languages_ids)

    # the api return a url and accesstoken for the Google Cloud server where Qordoba saves the translated files
    r = requests.get(res, stream=True)

    # unzipping the returned zipfile for python2 or python3
    try:
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
    except:
        z = zipfile.ZipFile(io.BytesIO(r.content))

    if not os.path.exists('bulkDownload'):
        os.makedirs('bulkDownload')

    # extract zip folder to root folder
    log.info('Downloading files...')
    root = os.getcwd() + '/' + 'bulkDownload'
    zip_files = z.namelist()
    z.extractall(root, zip_files)

    log.info('Finished with bulk download. Saved in "qordoba-cli/qordoba/bulkDownload/"')


def pull_command(curdir, config, files=(), force=False, bulk=False, workflow=False, workflow_all=None, version=None, distinct=False, languages=(),
                 in_progress=False, update_action=None, custom=False, **kwargs):
    api = ProjectAPI(config)
    init_language_storage(api)
    project = api.get_project()
    dest_languages = list(get_destination_languages(project))
    if languages:
        languages = validate_languges_input(languages, dest_languages)
    else:
        languages = dest_languages

    # prepare variables for pull_bulk command
    src_language = get_source_language(project)
    src_language_code = src_language.code
    src_language_id = src_language.id
    dest_languages_page_ids = []
    dest_languages_ids = [src_language_id]
    src_to_dest_paths = []

    pattern_list = get_pull_pattern(config, default=None)
    if pattern_list is None:
        pattern_list = [None]

    # based on the configuration in .qordoba.yml the destination for the pulled files will be set. Default path is '.qordoba-cli/qordoba/'
    for pattern in pattern_list:
        for language in languages:
            status_filter = [PageStatus.enabled, ]

            # generally only completed files will be pulled
            if in_progress is False:
                log.debug('Pull only completed translations.')
                status_filter = [PageStatus.completed, ]

            is_started = False
            pages_completed = api.page_search(language.id, status=status_filter)
            pages_all = [pages_completed, ]

            # if workflow flag exists, enabled files will be pulled too
            if workflow or workflow_all:
                pages_enabled = api.page_search(language.id, status=[PageStatus.enabled, ])
                pages_all = [pages_completed, pages_enabled]

            milestone_all = None
            for pages in pages_all:
                for page in pages:
                    is_started = True
                    page_status = api.get_page_details(language.id, page['page_id'], )
                    dest_languages_page_ids.append(page['page_id'])
                    dest_languages_ids.append(language.id)
                    milestone = page_status['status']['id']
                    version_tag  = page_status['version_tag']
                    filename = page['url']

                    if str(version_tag) != str(version) and version is not None:
                        print("dismissing file `{}` with wrong version {}".format(filename, version_tag))
                        continue

                    if distinct:
                        source_name = page_status['name']
                        tag = page_status['version_tag']
                        try:
                            pattern_name = pattern.split('/')[-1]
                        except AttributeError:
                            pattern_name = files[0]

                        if tag:
                            real_filename = tag + '_' + source_name
                        else:
                            real_filename = source_name

                        if real_filename != pattern_name:
                            continue

                    # when '--workflow' parameter is set, user can pick of which workflow files should be downloaded
                    if workflow or workflow_all:
                        milestones_resp = api.get_milestone(language.id, page_status['assignees'][0]['id'])
                        milestone_dict = dict()
                        for i in milestones_resp:
                            milestone_dict[i['name']] = i['id']
                        if workflow:
                            log.info('For file {} and language {} pick workflow step'.format(format_file_name(page),
                                                                                             language))
                            # takes the milestone answer from stdin
                            pick = ask_select(MilestoneOptions().all(milestone_dict), prompt='Pick a milestone: ')
                            milestone = milestone_dict[pick]

                        if workflow_all:
                            if milestone_dict[workflow_all]:
                                milestone = milestone_dict[workflow_all]
                            else:
                                log.info("The given Milestone `{}` does not exists in your project".format(workflow_all))

                    if in_progress:
                        log.debug(
                            'Selected status for page `{}` - {}'.format(page_status['id'], page_status['status']['name']))

                    dest_path = create_target_path_by_pattern(curdir,
                                                              language,
                                                              pattern=pattern,
                                                              distinct=distinct,
                                                              version_tag=page_status['version_tag'],
                                                              source_name=page_status['name'],
                                                              content_type_code=page_status['content_type_code'],
                                                              )

                    if pattern is not None:
                        stripped_dest_path = ((dest_path.native_path).rsplit('/', 1))[0]
                        src_to_dest_paths.append(tuple((language.code, stripped_dest_path)))
                    src_to_dest_paths.append(tuple((language.code, language.code)))

                    # adding the src langauge to the dest_path_of_src_language pattern
                    dest_path_of_src_language = create_target_path_by_pattern(curdir,
                                                                              src_language,
                                                                              pattern=pattern,
                                                                              distinct=distinct,
                                                                              version_tag=page_status['version_tag'],
                                                                              source_name=page_status['name'],
                                                                              content_type_code=page_status[
                                                                                  'content_type_code'],
                                                                              )

                    if pattern is not None:
                        stripped_dest_path_of_src_language = ((dest_path_of_src_language.native_path).rsplit('/', 1))[0]
                        src_to_dest_paths.append(tuple((src_language_code, stripped_dest_path_of_src_language)))
                    src_to_dest_paths.append(tuple((src_language_code, src_language_code)))

                    if not bulk:
                        """
                        Checking if file extension in config file matches downloaded file.
                        If not, continue e.g. *.resx should only download resx files from Qordoba
                        """
                        valid_extension = pattern.split('.')[-1] if pattern else None
                        file_extension = page['url'].split('.')[-1]

                        if not custom and pattern and valid_extension != "<extension>" and valid_extension != file_extension:
                            continue


                        log.info(
                            'Starting Download of translation file(s) for src `{}`, language `{}` and pattern {}'.format(
                                format_file_name(page), language.code, pattern))

                        if os.path.exists(dest_path.native_path) and not force:
                            log.warning('Translation file already exists. `{}`'.format(dest_path.native_path))
                            answer = FileUpdateOptions.get_action(update_action) or ask_select(FileUpdateOptions.all,
                                                                                               prompt='Choice: ')

                            if answer == FileUpdateOptions.skip:
                                log.info('Download translation file `{}` was skipped.'.format(dest_path.native_path))
                                continue
                            elif answer == FileUpdateOptions.new_name:
                                while os.path.exists(dest_path.native_path):
                                    dest_path = ask_question('Set new filename: ', answer_type=dest_path.replace)
                                    # pass to replace file

                        if workflow:
                            log.info('- note: pulls only from workflowstep  `{}` '.format(pick))
                        if workflow_all:
                            assert milestone_dict[workflow_all] == milestone
                            log.info('- note: pulls only from workflowstep  `{}` '.format(workflow_all))

                        res = api.download_file(page_status['id'], language.id, milestone=milestone)
                        res.raw.decode_content = True  # required to decompress content

                        if not os.path.exists(os.path.dirname(dest_path.native_path)):
                            try:
                                os.makedirs(os.path.dirname(dest_path.native_path))
                                log.info("Creating folder path {}".format(dest_path.native_path))
                            except OSError as exc:  # Guard against race condition
                                if exc.errno != errno.EEXIST:
                                    pass

                        with open(dest_path.native_path, 'wb') as f:
                            shutil.copyfileobj(res.raw, f)

                        log.info(
                            'Downloaded translation file `{}` for src `{}` and language `{}`'.format(dest_path.native_path,
                                                                                                     format_file_name(page),
                                                                                                 language.code))
            if not is_started and not bulk:
                log.info(
                    'Nothing to download for language `{}`. Check if your file translation status is `completed`.'.format(
                        language.code))

        if bulk:
            pull_bulk(api, src_to_dest_paths, dest_languages_page_ids, dest_languages_ids, pattern=pattern)
