from __future__ import unicode_literals, print_function

import logging
from qordoba.strategies import Extension, Shebang, Filename
# from qordoba.classifier import Classifier
from qordoba.framework import Framework
from qordoba.commands.i18n_base import BaseClass, FilesNotFound
from qordoba.utils import get_data
import os
import yaml
import re
import datetime
import operator

log = logging.getLogger('qordoba')

STRATEGIES = [
    Extension(),
    Filename(),
    # Classifier(),
    Shebang(),
    # Modeline(),
]

FRAMEWORKS = Framework()

class FilesNotFound(Exception):
    """
    Files not found
    """

class FindNewSourceClass(BaseClass):
    def empty(self, fileobj):

        if os.stat(fileobj).st_size == 0:
            return True
        else:
            False

    def isbinaryfile(self, path):

        if path is None:
            return None
        try:
            if not os.path.exists(path):
                return
        except Exception:
            return
        fin = open(path, 'rb')

        try:
            CHUNKSIZE = 1024
            while True:
                chunk = fin.read(CHUNKSIZE)
                if b'\0' in chunk:  # found null byte
                    return True
                if len(chunk) < CHUNKSIZE:
                    break  # done
            return False

        finally:
            fin.close()

    def valid_file(self, fileobj):

        conditions = [
            self.isbinaryfile(fileobj),
            self.empty(fileobj),
        ]
        if any(condition == True for condition in conditions):
            return False
        else:
            return True

    def percentage(self, x, lang_sum):

        return str(round(x * 100.0 / lang_sum, 1)) + "%"

    def regex_file_match(self, regexFile, string):

        try:
            with open(regexFile, 'r') as stream:
                try:
                    output = yaml.load(stream)
                    result = [re.match(pattern, str(string)) for pattern in output]
                    if any(result) is not None:
                        return False
                    return True
                except yaml.YAMLError as exc:
                    print(exc)

        except UnicodeDecodeError:
            return False

    def framework_detect(self, dir_path):

        framework = FRAMEWORKS.find_framework(dir_path)
        log.info('\nFramework Detected: {framework} at path: {path}'.format(framework=framework, path=dir_path))

        return framework

    def find_new_source_command(self, curdir, directory, output):
        pass
        log.info(".. Loading i18n-config.yml")
        blacklist_pattern = get_qorignore(directory)
        # walk through whole path
        log.info('\n Starting to read files from path {}'.format(directory))
        files = []
        framework = "not found"
        if os.path.isdir(directory):

            framework = self.framework_detect(directory)
            for path, dirnames, filenames in os.walk(directory):
                files.extend(os.path.join(path, name) for name in filenames)
            try:
                files = [file for file in files if not any(path in file for path in blacklist_pattern)]
            except TypeError:
                # than .qorignore possibly empty
                pass

        if os.path.isfile(directory):
            files.append(directory)

        if not files:
            raise FilesNotFound('Files not found by pattern `{}`'.format(directory))

        file_source_pool = dict()
        """Start applying the Strategies"""
        files_ignored = 0
        for file_path in files:

            # filtering out vendored code such as library
            vendor_path = get_data('resources/vendor.yml')
            documentation_path = get_data('resources/documentation.yml')
            vendor_code = self.regex_file_match(vendor_path, file_path)
            documentation_code = self.regex_file_match(documentation_path, file_path)
            if not self.valid_file(file_path):
                files_ignored += 1
                continue
            if vendor_code or documentation_code:
                files_ignored += 1
                continue
            # if any(item in file_path for item in CUSTOM_BLACKLIST):
            #     files_ignored += 1
            #     continue

            # Add count of files being ignored and print a log outside the for loop
            log.info('Starting.... processing file {}'.format(file_path))
            results_file = {}
            for strategy in STRATEGIES:
                typo = strategy.find_type(file_path)
                results_file[strategy.strategy_name] = typo
                file_source_pool[file_path] = results_file

        file_sources = dict()
        language_distribution = dict()

        STRATEGY_WEIGHTS = {
            'extension': 0.8,
            'filename': 0.7,
            'shebang': 0.6,
            'modeline': 0.5,
            'classifier': 0.4,

        }

        # weighted source result
        for file_path, value in file_source_pool.items():
            weights = dict()
            for strategy, sources in value.items():

                if sources == []:
                    continue
                for single_source in sources:
                    try:
                        weights[single_source] += STRATEGY_WEIGHTS[strategy]
                    except KeyError:
                        weights[single_source] = STRATEGY_WEIGHTS[strategy]
                source_max = max(weights.items(), key=operator.itemgetter(1))[0]
                file_sources[file_path] = source_max

                try:
                    language_distribution[source_max] += os.stat(file_path).st_size
                except KeyError:
                    language_distribution[source_max] = os.stat(file_path).st_size

        language_distribution_sorted = dict()
        for w in sorted(language_distribution, key=language_distribution.get, reverse=True):
            language_distribution_sorted[w] = language_distribution[w]

        lang_sum = sum(language_distribution.values())

        language_percentage = {k: self.percentage(v, lang_sum) for k, v in language_distribution_sorted.items()}

        timestamp = datetime.datetime.now().isoformat()

        outputdir = self.makeoutputdir()
        output_file = outputdir + '/file_sources_' + str(timestamp) + ".yml"

        with open(output_file, 'w') as outfile:
            yaml.safe_dump("timestamp: " + timestamp, outfile, default_flow_style=False)
            yaml.safe_dump("framework: " + framework, outfile, default_flow_style=False)
            yaml.safe_dump(language_percentage, outfile, default_flow_style=False)
            yaml.safe_dump(file_sources, outfile)

        log.info(
            "\n Source Analyzer finished. Results in {output_file} \n Found total of {total} files in path, trained on {valid} valid files. Framework is {framework}. \n {language_percentage}".format(
                output_file=output_file, total=len(files), valid=(len(files) - files_ignored), framework=framework,
                language_percentage=language_percentage))
