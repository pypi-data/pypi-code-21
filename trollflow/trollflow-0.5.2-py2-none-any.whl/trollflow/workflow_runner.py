import logging

from trollflow import utils

logger = logging.getLogger(__name__)


class WorkflowRunner(object):

    def __init__(self, workflow):
        self.components = [component.keys()[0] for component in
                           workflow["Workflow"]]
        self.workflow = dict((component.items()[0] for component in
                              workflow["Workflow"]))
        self.classes = []
        for module in self.components:
            clazz = self.get_class(module)
            component_clazz = clazz()
            component_clazz.slots = sorted(self.workflow[module].keys())
            self.classes.append(component_clazz)

    def get_class(self, clazz_path):
        return utils.get_class(clazz_path)

    def run(self, context):
        logger.debug("Running invokes")
        for component_clazz in self.classes:
            component_clazz.pre_invoke()
            component_clazz.invoke(context)
            component_clazz.post_invoke()


class WorkflowException(Exception):
    pass
