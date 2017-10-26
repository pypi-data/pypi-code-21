import yaml
import logging
try:
    import Queue as queue
except ImportError:
    import queue
from threading import Thread
import time
import gc

from trollflow import workflow_runner
from trollflow import utils

logger = logging.getLogger(__name__)


class WorkflowStreamer(Thread):

    """Class for handling streamed workflows"""

    def __init__(self, path_to_workflow=None, config=None, force_gc=False):

        Thread.__init__(self)
        if path_to_workflow is not None:
            self.workflow = self.read_workflow(path_to_workflow)
        else:
            self.workflow = config

        self.force_gc = force_gc

        self.input_queue = None
        self.output_queue = queue.Queue()
        self._loop = True

        self.prev_lock = None
        self.lock = None

        self.runner = workflow_runner.WorkflowRunner(self.workflow)

    def stop(self):
        """Stop the workflow streamer."""
        self._loop = False

    def run(self):
        """Run the work flow item"""
        while self._loop:
            if self.input_queue is None:
                time.sleep(1)
                continue
            try:
                data = self.input_queue.get(True, 1)
                self.input_queue.task_done()
            except queue.Empty:
                continue
            except ValueError:
                pass
            context = self.build_context(self.workflow)
            context['content'] = data
            self.runner.run(context)

            if self.force_gc:
                num = gc.collect()
                logger.debug("Garbage collection cleaned %s objects", num)

    def read_workflow(self, path_to_workflow):
        """Read the workflow from YAML configuration file"""
        logger.info("Reading workflow %s", path_to_workflow)
        with open(path_to_workflow, "r") as fid:
            config = yaml.safe_load(fid)
        return config

    def build_context(self, config):
        """Build context dictionary holding input and output queues and
        configurations.  The actual data will be added when it becomes
        available from the input queue.
        """
        logger.info("Constructing context.")

        context = {"input_queue": self.input_queue,
                   "output_queue": self.output_queue,
                   "lock": self.lock,
                   "prev_lock": self.prev_lock}
        components = config["Workflow"]

        for component in components:
            module, slots = component.items()[0]
            del module
            for slot_name, slot_details in slots.items():
                if slot_name not in context:
                    slot = {slot_name: slot_details}
                    context.update(slot)

        # add global configuration here
        if "global_config" in config.keys():
            if isinstance(config["global_config"], dict):
                context["global_config"] = config["global_config"]
            elif isinstance(config["global_config"], str):
                # trying to build a dict from configuration code...
                global_config = utils.get_class(config["global_config"])
                context["global_config"] = global_config

        return context
