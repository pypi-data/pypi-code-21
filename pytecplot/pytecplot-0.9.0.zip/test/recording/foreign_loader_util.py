import unittest
import re
from tecplot.version import sdk_version_info
from .recording_util import *


class sv(object):
    FLUENT_LOADER = "FLUENT DATA LOADER"

    STANDARDSYNTAX = "STANDARDSYNTAX"
    YES = "YES"
    NO = "NO"
    APPEND = "APPEND"
    LOADOPTION = "LOADOPTION"
    FILENAME_CASEFILE = "FILENAME_CASEFILE"
    FILENAME_DATAFILE = "FILENAME_DATAFILE"
    FILELIST_FILES = "FILELIST_FILES"
    UNSTEADYOPTION = "UNSTEADYOPTION"
    TIMEINTERVAL = "TIMEINTERVAL"
    ASSIGNSTRANDIDS = "ASSIGNSTRANDIDS"
    ADDZONESTOEXISTINGSTRANDS = "ADDZONESTOEXISTINGSTRANDS"
    GRIDZONES = "GRIDZONES"
    ZONELIST = "ZONELIST"
    VARNAMELIST = "VARNAMELIST"
    INCLUDEPARTICLEDATA = "INCLUDEPARTICLEDATA"
    ALLPOLYZONES = "ALLPOLYZONES"
    AVERAGETONODES = "AVERAGETONODES"
    AVERAGINGMETHOD = "AVERAGINGMETHOD"
    LOADADDITIONALQUANTITIES = "LOADADDITIONALQUANTITIES"
    SAVEUNCOMPRESSEDFILES = "SAVEUNCOMPRESSEDFILES"
    CASEANDDATA = "CASEANDDATA"
    CASEONLY = "CASEONLY"
    RESIDUALSONLY = "RESIDUALSONLY"
    MULTIPLECASEANDDATA = "MULTIPLECASEANDDATA"
    READTIMEFROMDATAFILES = "READTIMEFROMDATAFILES"
    APPLYCONSTANTTIMEINTERVAL = "APPLYCONSTANTTIMEINTERVAL"
    CELLSANDBOUNDARIES = "CELLSANDBOUNDARIES"
    CELLSONLY = "CELLSONLY"
    BOUNDARIESONLY = "BOUNDARIESONLY"
    SELECTEDZONES = "SELECTEDZONES"
    ARITHMETIC = "ARITHMETIC"
    LAPLACIAN = "LAPLACIAN"


@unittest.skipIf(sdk_version_info < (2017, 3, 0, 81450),
                 '2017 R3 is required for macro translate unit tests.')
class TestTranslateForeignLoader(unittest.TestCase):
    LOADER_NAME = None

    def translate_instr(self, instruction_list):
        instr = '"{}" "1.0"'.format(sv.STANDARDSYNTAX)

        for kw in instruction_list:
            instr += ' "{}"'.format(kw)
        cmd = "$!READDATASET '{}' DATASETREADER = '{}'".format(instr,
                                                             self.LOADER_NAME)
        return translate(cmd)

    def check_match(self, instr, expected):
        translated = self.translate_instr(instr)
        result = re.match(expected, translated, re.MULTILINE)
        self.assertIsNotNone(result)

    def check_search(self, instr, expected):
        translated = self.translate_instr(instr)
        result = re.search(expected, translated, re.MULTILINE)
        self.assertIsNotNone(result)

    def check_optional_bool(self, pytecplot_api, loader_api, python_default, loader_default):
        """
        Check that a boolean parameter is only provided in the translated python API call if it is necessary because
        it is not the default for the pytecplot API.

        The logic here is more complex because the pytecplot API can invert the default of the loader API,
        and we have to check for the correct translation if the parameter is not provided in the source
        instruction list.

        (X = should not exist in the translated API call)

        DEFAULT:                          | param value TRUE  | param value FALSE   | param value NOT PROVIDED
        (python default, loader default)  | in source instr   | in source instr     | in source instruction list.
        ----------------------------------+-------------------+---------------------+---------------------
        (T, T)                            | X                 | param=FALSE         | X
        (T, F)                            | X                 | param=FALSE         | param=FALSE
        (F, F)                            | param=TRUE        | X                   | X
        (F, T)                            | param=TRUE        | X                   | param=TRUE
        """

        def param_is_false(instr):
            return '{}=False'.format(pytecplot_api) in instr

        def param_is_true(instr):
            return "{}=True".format(pytecplot_api) in instr

        def param_is_missing(instr):
            return pytecplot_api not in instr

        default_is_true_true = python_default and loader_default
        default_is_true_false = python_default and not loader_default
        default_is_false_false = not python_default and not loader_default
        default_is_false_true = not python_default and loader_default

        # The test below pivots the table above,
        # so there is one test for each column (Yes, No, Not Provided)

        # Param value is TRUE in source instruction list.
        result = self.translate_instr([loader_api, sv.YES])
        self.assertTrue(IMPLICATION(default_is_true_true or default_is_true_false, param_is_missing(result)))
        self.assertTrue(IMPLICATION(default_is_false_false or default_is_false_true, param_is_true(result)))

        #  Param value is FALSE in source instruction list.
        result = self.translate_instr([loader_api, sv.NO])
        self.assertTrue(IMPLICATION(default_is_true_true or default_is_true_false, param_is_false(result)))
        self.assertTrue(IMPLICATION(default_is_false_false or default_is_false_true, param_is_missing(result)))

        # Param value is NOT PROVIDED in source instruction list.
        result = self.translate_instr([])
        self.assertTrue(IMPLICATION(default_is_true_true or default_is_false_false, param_is_missing(result)))
        self.assertTrue(IMPLICATION(default_is_true_false, param_is_false(result)))
        self.assertTrue(IMPLICATION(default_is_false_true, param_is_true(result)))

    def check_append(self):
        self.check_optional_bool("append", sv.APPEND,
                                 python_default=True, loader_default=False)

    def check_average_to_nodes(self):
        py_param_name = 'average_to_nodes'
        result = self.translate_instr([sv.AVERAGETONODES, sv.YES])
        self.assertNotIn(py_param_name, result)
        result = self.translate_instr([sv.AVERAGETONODES, sv.YES, sv.AVERAGINGMETHOD, sv.ARITHMETIC])
        self.assertNotIn(py_param_name, result)
        result = self.translate_instr([sv.AVERAGETONODES, sv.YES, sv.AVERAGINGMETHOD, sv.LAPLACIAN])
        self.assertIn("{}='Laplacian'".format(py_param_name), result)
        result = self.translate_instr([sv.AVERAGETONODES, sv.NO])
        self.assertIn('{}=None'.format(py_param_name), result)  # force to None

    def check_zone_list(self):
        result = self.translate_instr([sv.ZONELIST, '2,4-5', sv.GRIDZONES, sv.SELECTEDZONES])
        self.assertIn('zones=[1, 3, 4]', result)

    def check_var_name_list(self):
        # VarNameList is tricky because the variable name list is formatted as
        # "V1"+"V2" within the instruction string,
        # so we can't use self.translate_instr()
        instr = '"{}"'.format(sv.GRIDZONES) + ' "{}"'.format(sv.SELECTEDZONES) + ' "{}"'.format(sv.VARNAMELIST)
        instr += '"V1"+"V2"'
        cmd = "$!READDATASET '{}' DATASETREADER = '{}'".format(instr,
                                                             self.LOADER_NAME)
        result = translate(cmd)
        self.assertIn("variables=['V1', 'V2']", result)