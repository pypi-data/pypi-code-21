import unittest
import bot_id
import slackpi
import wray.slacklib
import harrison.slacklib

class TestSlackBotFunctions(unittest.TestCase):

    def test_ci(self):
        self.assertTrue(True)

    def test_slack_client(self):
        self.assertTrue(bot_id.get_id() == None)

    def test_slack_pi(self):
        self.assertTrue(slackpi.handle_command("","") == None)

    def test_wray_handler(self):
        self.assertFalse(wray.slacklib.handle_command('') == None)
        self.assertTrue(len(wray.slacklib.handle_command(
            wray.slacklib.COMMAND1)) > 1)

    #def test_topic_map(self):
    #    self.assertTrue(wray.slacklib.handle_command('topic:python').find('exists') >= 0)
    #    self.assertTrue(wray.slacklib.handle_command('topics').find('python') >= 0)

    #def test_tag_sanner(self):
    #    output = {'text':'lambda','channel':'test','user':'wray'}
    #    self.assertTrue(wray.slacklib.tag_scanner(bot_id,output))
        
    def test_harrison_handler(self):
        self.assertFalse(harrison.slacklib.handle_command('') == None)
        self.assertTrue(len(harrison.slacklib.handle_command(
            harrison.slacklib.COMMAND1)) > 1)


if __name__ == '__main__':
    unittest.main()
