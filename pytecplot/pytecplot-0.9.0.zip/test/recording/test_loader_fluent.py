import unittest
import tecplot as tp
from tecplot.version import sdk_version_info
import re
from .foreign_loader_util import sv, TestTranslateForeignLoader
from .recording_util import *

from test import skip_if_sdk_version_before, skip_if_connected


class TestTranslateFluentLoader(TestTranslateForeignLoader):
    @skip_if_sdk_version_before(2017, 3, 0, 81450)
    @skip_if_connected
    def setUp(self):
        self.LOADER_NAME = sv.FLUENT_LOADER
        tp.new_layout()

    def test_sample(self):
        result = translate("""$!READDATASET
        '"STANDARDSYNTAX" "1.0" "FILELIST_Files" "1" "shower5.cas" "LoadOption" "MultipleCaseAndData" "UnsteadyOption" "ReadTimeFromDataFiles" "AssignStrandIDs" "Yes" "LoadAdditionalQuantities" "Yes" "SaveUncompressedFiles" "No"'
        DATASETREADER = 'Fluent Data Loader'""")

        self.assertIsNotNone(re.match(
            r"tp\.data\.load_fluent\(case_filenames=\['shower5.cas'\],\s*"
            r"append=False\)",
            result,
            re.MULTILINE))

    def test_instructions(self):
        self.check_match([sv.LOADOPTION, sv.CASEONLY, sv.FILENAME_CASEFILE, 'file.cas'],
        r"^tp\.data\.load_fluent\(case_filenames=\['file.cas'\],"
        r"\s*assign_strand_ids=False,\s*include_additional_quantities=False,"
        r"\s*append=False\)$")

    def test_case_files(self):

        self.assertIn("case_filenames=['file.cas']",
                      self.translate_instr([sv.LOADOPTION, sv.CASEONLY, sv.FILENAME_CASEFILE, 'file.cas']))

        self.assertIn("case_filenames=['file.cas.gz']",
                      self.translate_instr([sv.LOADOPTION, sv.CASEONLY, sv.FILENAME_CASEFILE, 'file.cas.gz']))

    def test_data_files(self):
        self.assertIn("data_filenames=['f.dat']",
                      self.translate_instr([sv.LOADOPTION, sv.RESIDUALSONLY, sv.FILENAME_DATAFILE, 'f.dat']))

        self.assertIn("data_filenames=['f.dat.gz']",
                      self.translate_instr([sv.LOADOPTION, sv.RESIDUALSONLY, sv.FILENAME_DATAFILE, 'f.dat.gz']))

        self.assertIn("data_filenames=['f.dat.xml']",
                      self.translate_instr([sv.LOADOPTION, sv.RESIDUALSONLY, sv.FILENAME_DATAFILE, 'f.dat.xml']))

    def test_case_and_data_files(self):
        result = self.translate_instr([sv.LOADOPTION, sv.CASEANDDATA, sv.FILENAME_CASEFILE, "f-cas.cas", sv.FILENAME_DATAFILE, "f-dat.dat"])
        self.assertIn("case_filenames=['f-cas.cas']", result)
        self.assertIn("data_filenames=['f-dat.dat']", result)

    def test_filelist_files(self):
        result = self.translate_instr([sv.LOADOPTION, sv.CASEANDDATA, sv.FILELIST_FILES, "2", "f-cas.cas", "f-dat.dat"])
        self.assertIn("case_filenames=['f-cas.cas']", result)
        self.assertIn("data_filenames=['f-dat.dat']", result)

    def test_unsteady_option_and_time_interval(self):
        result = self.translate_instr([sv.UNSTEADYOPTION, sv.READTIMEFROMDATAFILES, sv.LOADOPTION, sv.CASEONLY, sv.FILENAME_CASEFILE, "file.cas"])
        self.assertNotIn('time_interval', result)

        result = self.translate_instr([sv.UNSTEADYOPTION, sv.APPLYCONSTANTTIMEINTERVAL, sv.LOADOPTION, sv.CASEONLY, sv.FILENAME_CASEFILE, "file.cas"])
        self.assertIn('time_interval=1', result) # %g formatting of time interval

        result = self.translate_instr([sv.UNSTEADYOPTION, sv.APPLYCONSTANTTIMEINTERVAL,  sv.TIMEINTERVAL, "2.0", sv.LOADOPTION, sv.CASEONLY, sv.FILENAME_CASEFILE, "file.cas"])
        self.assertIn('time_interval=2', result) # %g formatting of time interval

    def test_append(self):
        self.check_append()

    def test_add_zones_to_existing_strands(self):
        self.check_optional_bool('add_zones_to_existing_strands', sv.ADDZONESTOEXISTINGSTRANDS,
                                 python_default=False, loader_default=False)

    def test_grid_zones(self):
        result = self.translate_instr([sv.ZONELIST, "2,4", sv.GRIDZONES, sv.SELECTEDZONES])
        self.assertIn('zones=[1, 3]', result)
        result = self.translate_instr([sv.GRIDZONES, sv.CELLSANDBOUNDARIES])
        self.assertNotIn('zones', result)  # default
        result = self.translate_instr([sv.GRIDZONES, sv.CELLSONLY])
        self.assertIn("zones='CellsOnly'", result)
        result = self.translate_instr([sv.GRIDZONES, sv.BOUNDARIESONLY])
        self.assertIn("zones='BoundariesOnly'", result)

    def test_average_to_nodes(self):
        self.check_average_to_nodes()

    def test_zone_list(self):
        self.check_zone_list()

    def test_var_name_list(self):
        self.check_var_name_list()

    def test_include_particle_data(self):
        self.check_optional_bool('include_particle_data', sv.INCLUDEPARTICLEDATA,
                                 python_default=False, loader_default=False)

    def test_all_poly_zones(self):
        self.check_optional_bool('all_poly_zones', sv.ALLPOLYZONES,
                                 python_default=False, loader_default=False)

    def test_include_additional_quantities(self):
        self.check_optional_bool('include_additional_quantities', sv.LOADADDITIONALQUANTITIES,
                                 python_default=True, loader_default=False)

    def test_assign_strand_ids(self):
        self.check_optional_bool('assign_strand_ids', sv.ASSIGNSTRANDIDS,
                                 python_default=True, loader_default=False)


if __name__ == '__main__':
    from .. import main
    main()
