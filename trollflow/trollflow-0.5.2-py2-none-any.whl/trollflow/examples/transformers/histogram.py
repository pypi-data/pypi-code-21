from trollflow.workflow_component import AbstractWorkflowComponent
from matplotlib import pyplot as plt


class Histogramer(AbstractWorkflowComponent):

    def pre_invoke(self):
        pass

    def invoke(self, context):
        """..."""
        try:
            plt.hist(context[self.slots[0]]["content"])
            plt.show()
        except Exception, e:
            raise e

    def post_invoke(self):
        pass
