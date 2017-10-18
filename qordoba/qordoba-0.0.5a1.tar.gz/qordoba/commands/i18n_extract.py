from qordoba.commands.i18n_base import BaseClass, IGNOREFILES

import logging
import pprint
from subprocess import Popen,PIPE
import pandas as pd
import os

pp = pprint.PrettyPrinter(indent=4)
log = logging.getLogger('qordoba')

class i18nExtractClass(BaseClass):
    """
    The FindNewString class is created to find StringLiterals within a project directory (currently python, Scala)
    input: Directory of the files to be converted
    output: location where the CSV with all info should be stored

    when the stringLiterals are found, it will run through the project and
    """

    def extract(self,directory, output):

        directory = self.change_dir_path_to_default(directory)
        output = self.change_dir_path_to_default(output)

        log.info('\b')
        log.info( " loading resources from outer space ..." + '\b')
        log.info('\b')
        log.info("       ... "+ u"\U0001F4E1"+" ...")
        log.info('\b')
        log.info("       ... "+ u"\U0001F4E1"+" ...")
        log.info('\b')
        log.info("strings are now being exported from your files")
        log.info('\b')

        Process = Popen('./string-extractor/bin/start-container.sh %s %s' % (directory, output), shell=True)
        log.info(Process.communicate())

        log.info('\b')

        output = self.change_dir_path_to_default(output)
        file_path = output + '/' + 'string-literals.csv'

        df_file = pd.read_csv(file_path, sep=',', names=['filename', 'startLineNumber', 'startCharIdx', 'endLineNumber', 'endCharIdx', 'text'])
        os.remove(file_path)
        df_file.to_csv(file_path, encoding='utf-8', index=False)
        log.info('Extraction completed. All exported Strings can be found within the ' + u"\U0001F4C1" + ' file `string-literal.csv`')
        log.info('\b')
