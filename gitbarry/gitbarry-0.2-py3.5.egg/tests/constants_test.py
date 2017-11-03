from unittest import TestCase
from gitbarry import constants


class ConstantsTests(TestCase):
    def test_constants_exists(self):
        self.assertIsNotNone(constants.START_ACTION)
        self.assertIsNotNone(constants.STOP_ACTION)
        self.assertIsNotNone(constants.FINISH_ACTIONS)

    def test_finish_actions_importing(self):
        from gitbarry.utils import shortcuts
        for action_name, module_path in constants.FINISH_ACTIONS.items():
            self.assertIsNotNone(action_name)
            self.assertIsNotNone(shortcuts.import_from_str(module_path))
