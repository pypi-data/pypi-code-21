import json

from russell.cli.utils import force_unicode
from russell.client.base import RussellHttpClient
from russell.manager.experiment_config import ExperimentConfigManager
from russell.model.experiment import Experiment
from kafka import KafkaConsumer


class ExperimentClient(RussellHttpClient):
    """
    Client to interact with Experiments api
    """
    def __init__(self):
        self.url = "/experiment/{id}"
        super(ExperimentClient, self).__init__()

    def get_all(self):
        experiment_config = ExperimentConfigManager.get_config()
        experiments_dict = self.request("GET",
                                self.url,
                                params="family_id={}".format(experiment_config.family_id))
        return [Experiment.from_dict(expt) for expt in experiments_dict]

    def get(self, id):
        experiment_dict = self.request("GET",
                                       url=self.url.format(id=id))
        return Experiment.from_dict(experiment_dict)


    def stop(self, id):
        self.request("POST",
                     url=self.url.format(id=id),
                     params={'action': 'stop'})
        return True

    def create(self, experiment_request):
        response = self.request("POST",
                                url="/experiment/run",
                                data=json.dumps(experiment_request.to_dict()),
                                timeout=3600)
        return response.get("id")

    def delete(self, id):
        self.request("DELETE",
                     "/experiment/{}".format(id))
        return True

    def get_log_server(self, id):
        log_dict = self.request("GET",
                                "/task/{}/log".format(id))
        if log_dict.get('method') == 'kafka':
            return log_dict.get('server')
        return None

    def get_log_stream(self, id, method='kafka'):
        timeout = 50
        response = self.request("GET",
                                "/logs",
                                params={'method':method, 'id':id},
                                stream=True,
                                timeout=timeout)
        return response.iter_lines()


    def get_log_stream_head(self, id, method='kafka'):
        timeout = 50
        response = self.request("GET",
                                "/logs-part",
                                params={'method':method, 'id':id, 'part': 'head'},
                                stream=True,
                                timeout=timeout)
        return response.iter_lines()

    def get_log_stream_container(self, id, method='kafka'):
        log_server = self.get_log_server(id)
        if not log_server:
            return
        try:
            consumer = KafkaConsumer(id,
                                     bootstrap_servers=log_server,
                                     auto_offset_reset='earliest',
                                     enable_auto_commit=False,
                                     request_timeout_ms=40000,
                                     consumer_timeout_ms=10000)
        except:
            yield "Get log in container failed"
            return
        else:
            try:
                for msg in consumer:
                    yield json.loads(force_unicode(msg.value)).get("log").strip("\n")
            except StopIteration as e:
                return

    def get_log_stream_tail(self, id, method='kafka'):
        timeout = 50
        response = self.request("GET",
                                "/logs-part",
                                params={'method': method, 'id':id, 'part': 'tail'},
                                stream=True,
                                timeout=timeout)
        return response.iter_lines()
