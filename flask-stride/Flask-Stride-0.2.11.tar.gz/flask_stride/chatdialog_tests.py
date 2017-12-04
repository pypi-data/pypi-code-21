import unittest
from .chatdialog import ChatDialog, ChatDialogAction

class ChatDialogTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view'}

        self.assertEqual(dlg_descriptor, expected)

    def test_size_adg_invalid(self):
        """Test setting the size option to an invalid ADG size."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        self.assertRaises(ValueError, setattr, dlg, 'size', 'large2')

    def test_size_adg_small(self):
        """Test setting the size option to an ADG size."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        dlg.size = 'small'

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'size': 'small'}}
        self.assertEqual(dlg_descriptor, expected)

    def test_size_custom(self):
        """Test setting the size option to a custom size."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        dlg.size = {'width': '50%', 'height': '50%'}

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'size': {'width': '50%', 'height': '50%'}}}
        self.assertEqual(dlg_descriptor, expected)

    def test_size_custom_invalid(self):
        """Test setting the size option to an invalid custom size."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        self.assertRaises(ValueError, setattr, dlg, 'size', {'width': '', 'height': '50%'})

    def test_hint_string(self):
        """Test setting the hint option to a string."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        dlg.hint = 'this is a hint string.'

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'hint': {'value': 'this is a hint string.'}}}
        self.assertEqual(dlg_descriptor, expected)

    def test_hint_dict(self):
        """Test setting the hint option using a dict."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        dlg.hint = {'value': 'this is a hint string.', 'i18n': 'hint_token or something.'}

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'hint': {'value': 'this is a hint string.', 'i18n': 'hint_token or something.'}}}
        self.assertEqual(dlg_descriptor, expected)

    def test_filter(self):
        """Test setting the filter option."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        dlg.filter = {'placeholder': { 'value': 'my filter', 'i18n': 'hint_token or something.'}}

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'filter': {'placeholder': { 'value': 'my filter', 'i18n': 'hint_token or something.'}}}}
        self.assertEqual(dlg_descriptor, expected)

    def test_primary_action(self):
        """Test setting the primaryAction option."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')
        dlg_act = ChatDialogAction(key='dlg-act-key-1', name='MyDialogAction1')

        dlg.primary_action = dlg_act

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'primaryAction': {'name': {'value': 'MyDialogAction1'}, 'key': 'dlg-act-key-1', 'enabled': True}}}

        self.assertEqual(dlg_descriptor, expected)

    def test_secondary_actions(self):
        """Test setting the secondaryActions option."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        dlg_sec_act_1 = ChatDialogAction(key='sec-act-1', name='Almost done')
        dlg_sec_act_2 = ChatDialogAction(key='sec-act-2', name='Haven\'t even started')
        dlg_sec_acts = [dlg_sec_act_1, dlg_sec_act_2]

        dlg.secondary_actions = dlg_sec_acts

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'secondaryActions': [ {'name': {'value': 'Almost done'}, 'key': 'sec-act-1', 'enabled': True}, {'name': {'value': 'Haven\'t even started'}, 'key': 'sec-act-2', 'enabled': True}]}}

        self.assertEqual(dlg_descriptor, expected)

    def test_add_secondary_action(self):
        """Test adding an action to secondaryAction option."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        new_action = ChatDialogAction(key='my-key-1', name='my other button')

        dlg.add_secondary_action(new_action)

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view', 'options': {'secondaryActions': [ {'name': {'value': 'my other button'}, 'key': 'my-key-1', 'enabled': True}]}}

        self.assertEqual(dlg_descriptor, expected)

    def test_del_secondary_action(self):
        """Test adding an action to secondaryAction option."""
        dlg = ChatDialog(key='dialog-key', title='My Dialog Box', url='/dialog-view')

        new_action = ChatDialogAction(key='my-key-1', name='my other button')

        dlg.add_secondary_action(new_action)
        dlg.del_secondary_action('my other button')

        dlg_descriptor = dlg.to_descriptor()
        expected = {'key': 'dialog-key', 'title': {'value': 'My Dialog Box'}, 'url': '/dialog-view'}

        self.assertEqual(dlg_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
