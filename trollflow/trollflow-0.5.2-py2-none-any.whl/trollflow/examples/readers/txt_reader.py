from trollflow.workflow_component import AbstractWorkflowComponent
import os


class TXTFileReader(AbstractWorkflowComponent):

    def pre_invoke(self):
        """Check if file exists."""
        print self.slots

    def invoke(self, context):
        """Read a text file's contents."""
        try:
            os.path.isfile(context[self.slots[0]]["uri"])
            txt_file = open(context[self.slots[0]]["uri"])
            content = txt_file.read()
            txt_file.close()
            context[self.slots[0]]["content"] = content
        except Exception, e:
            raise e

    def post_invoke(self):
        """Close file."""
        pass
