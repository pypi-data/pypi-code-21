from trollflow.workflow_component import AbstractWorkflowComponent
import Image


class Writer(AbstractWorkflowComponent):

    def pre_invoke(self):
        pass

    def invoke(self, context):
        """Write a GIF file's contents."""
        try:
            img = Image.fromarray(context[self.slots[0]]["uri"], 'w')
            img.save(context[self.slots[0]]["content"])
        except Exception, e:
            raise e

    def post_invoke(self):
        pass
