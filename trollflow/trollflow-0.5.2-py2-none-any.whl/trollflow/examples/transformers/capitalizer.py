from trollflow.workflow_component import AbstractWorkflowComponent


class Capitalizer(AbstractWorkflowComponent):

    def pre_invoke(self):
        print self.slots

    def invoke(self, context):
        """Capitalize a string."""
        try:
            content = context[self.slots[0]]["content"]
            context[self.slots[1]]["content"] = content.upper()
        except Exception, e:
            raise e

    def post_invoke(self):
        pass
