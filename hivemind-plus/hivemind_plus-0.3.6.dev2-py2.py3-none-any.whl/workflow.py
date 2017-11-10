from hivemindplus.api import Api
from hivemindplus.exceptions import ConfigValidationException
from hivemindplus.instance_processor import InstanceProcessor
from hivemindplus.result_processor import ResultProcessor
from hivemindplus.submission_processor import SubmissionProcessor
from hivemindplus.validation import validate


class Workflow:
    def __init__(self, api_url, api_key, task_id, instance_config, result_config, auto_submission):
        self._api = Api(api_url, api_key, task_id)
        self._task_id = task_id
        self._instance_processor = InstanceProcessor(instance_config)
        self._result_processor = ResultProcessor(result_config, task_id)
        self._submission_processor = SubmissionProcessor(auto_submission)

    def start(self):
        """
        Manages the task:
            1. Creates any instances that haven't already been created
            2. Applies custom agreement checking
            3. Stores any new results
            4. Reiterates any instances that require it
        """
        self._api.connect()

        self._instance_processor.process(self._api)
        self._submission_processor.process(self._api)
        self._result_processor.process(self._api)

        self._api.disconnect()


class Builder:
    def __init__(self):
        self._api_url = None
        self._api_key = None
        self._task_id = None
        self._instance_config = None
        self._result_config = None
        self._auto_submission = False

    def with_api_url(self, api_url):
        """
        Sets the REST endpoint for the Hivemind API.
        """
        self._api_url = api_url
        return self

    def with_api_key(self, api_key):
        """
        Sets the API key to authenticate all API calls
        """
        self._api_key = api_key
        return self

    def with_task_id(self, task_id):
        """
        Sets the task id that instances and results will be managed for
        """
        self._task_id = task_id
        return self

    def with_instance_config(self, instance_config):
        """
        Sets the instance configuration for the task
        """
        self._instance_config = instance_config
        return self

    def with_result_config(self, result_config):
        """
        Sets the results configuration for the task
        """
        self._result_config = result_config
        return self

    def with_auto_submission(self):
        """
        (Optional) Sets automatic submission of task to True
        """
        self._auto_submission = True
        return self

    def build(self):
        validate(self, [['_instance_config', '_result_config'], ['_api_key'], ['_api_url'], ['_task_id']])

        return Workflow(
            self._api_url,
            self._api_key,
            self._task_id,
            self._instance_config,
            self._result_config,
            self._auto_submission
        )


