import os
import unittest

from openergy import LocalDatabase

module_path = os.path.realpath(os.path.dirname(__file__))


class LocalDBTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = LocalDatabase(os.path.join(module_path, "resources", "local_db"))

    def test_iter_all(self):
        series = set()
        for local_se in self.db.iter_local_series("Monte Carlo Analysis"):
            series.add((local_se.project_name, local_se.generator_model, local_se.generator_name, local_se.name))
            se = local_se.data
            self.assertEqual(10, len(se))
            self.assertEqual(se.name, local_se.name)
        self.assertEqual({
            ('monte-carlo-analysis', 'importer', 'puissance-chauffage', 'PuisChaufTot (W) avec PAC'),
            ('monte-carlo-analysis', 'importer', 'puissance-chauffage', 'PuisChaufTot (W) hors PAC'),
            ('monte-carlo-analysis', 'cleaner', 'puissance-chauffage', 'Heating Power with PAC'),
            ('monte-carlo-analysis', 'cleaner', 'importerdeouf', 'pctot_hpac'),
            ('monte-carlo-analysis', 'importer', 'importerdeouf', 'PuisChaufTot (W) avec PAC'),
            ('monte-carlo-analysis', 'importer', 'importerdeouf', 'PuisChaufTot (W) hors PAC'),
            ('monte-carlo-analysis', 'cleaner', 'importerdeouf', 'pctot')},
            series
        )
