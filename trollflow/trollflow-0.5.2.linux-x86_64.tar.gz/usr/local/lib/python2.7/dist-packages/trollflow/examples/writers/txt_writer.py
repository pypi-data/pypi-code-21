from trollflow.workflow_component import AbstractWorkflowComponent


class TXTFileWriter(AbstractWorkflowComponent):

    def pre_invoke(self):
        """Check if file exists."""
        pass

    def invoke(self, context):
        """Write a text file's contents."""
        try:
            txt_file = open(context[self.slots[0]]["uri"], 'w')
            txt_file.write(str(context[self.slots[0]]["content"]))
            txt_file.close()
        except Exception, e:
            raise e

    def post_invoke(self):
        """Close file."""
        pass
