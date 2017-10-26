from trollflow.workflow_component import AbstractWorkflowComponent
import logging
import subprocess

logger = logging.getLogger(__name__)


class Unarchiver(AbstractWorkflowComponent):

    def pre_invoke(self):
        pass

    def invoke(self, context):
        """Unarchiver..."""
        try:
            print context[self.slots[0]]["uri"]
            cmd = ["tar", "-xzvf",
                   context[self.slots[0]]["uri"],
                   "-C", context[self.slots[1]]["uri"]]
            subprocess.call(cmd)
        except Exception, e:
            raise e

    def post_invoke(self):
        pass
