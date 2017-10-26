from trollflow.workflow_component import AbstractWorkflowComponent
from mpop.satellites import PolarFactory
from datetime import datetime


class NOAA19(AbstractWorkflowComponent):

    def pre_invoke(self):
        pass

    def invoke(self, context):
        """..."""
        try:
            orbit = context["global_config"]["orbit"]
            ts = context["global_config"]["time_slot"]
            time_slot = datetime(ts[0], ts[1], ts[2], ts[3], ts[4])
            global_data = PolarFactory.create_scene("noaa", "19", "avhrr",
                                                    time_slot, orbit)
            global_data.load([10.8])
            context[self.slots[0]]["content"] = global_data[10.8].data
        except Exception, e:
            raise e

    def post_invoke(self):
        pass
