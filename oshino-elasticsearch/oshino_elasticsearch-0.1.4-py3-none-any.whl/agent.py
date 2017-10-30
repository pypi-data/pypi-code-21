import aiohttp

from time import time
from logbook import Logger

from oshino import Agent
from oshino.agents.http_agent import HttpAgent

logger = Logger("ElasticSearchAgent")


def translate_cluster_status(status):
    if status == "green":
        return "ok"
    elif status == "yellow":
        return "warn"
    else:
        return "error"


async def _pull_data(path):
    async with aiohttp.ClientSession() as session:
        async with session.get(path) as resp:
            return await resp.json()


def unwrap_metric(event_fn, path, key, metric):
    if isinstance(metric, (int, float)):
        event_fn(service=path + ".{0}".format(key),
                 metric_f=float(metric),
                 state="ok")

    elif isinstance(metric, dict):
        for k, v in metric.items():
            unwrap_metric(event_fn, path + ".{0}".format(key), k, v)
    else:
        logger.debug("Skipping metric: {0}:{1} because it is not numeric"
                    .format(key, metric))


class ElasticSearchAgent(HttpAgent):

    @property
    def api_version(self):
        return self._data.get("api_version", "5.6")

    @property
    def fields(self):
        default_fields = [
                "transport",
                "http",
                "process",
                "jvm",
                "indices",
                "thread_pool"
        ]

        return self._data.get("fields", default_fields)

    async def retrieve_cluster_health(self):
        path = "{0}/_cluster/health".format(self.url)
        return await _pull_data(path)

    async def retrieve_nodes_info(self, node="_all"):
        path = ("{0}/_nodes/{1}/stats/{2}"
                .format(self.url, node, ",".join(self.fields)))
        return await _pull_data(path)

    async def process(self, event_fn):
        logger = self.get_logger()
        ts = time()

        # Parsing cluster health state
        cluster_health = await self.retrieve_cluster_health()
        logger.trace("Got content from ElasticSearch cluster health: {0}"
                     .format(cluster_health))
        state = translate_cluster_status(cluster_health["status"])

        te = time()
        span = int((te - ts) * 1000)
        event_fn(service=self.prefix + "cluster.health",
                 metric_f=span,
                 state=str(state),
                 description=self.url)

        # Other cluster info
        del cluster_health["cluster_name"]
        del cluster_health["timed_out"]
        del cluster_health["status"]


        for key, val in cluster_health.items():
            event_fn(service=self.prefix + "cluster." + key,
                     metric_f=float(val),
                     state="ok",
                     description=self.url)

        # Retrieving technical info
        technical_info = await self.retrieve_nodes_info("_all")
        logger.trace("Got node technical info: {0}".format(technical_info))
        for h, node in technical_info["nodes"].items():
            name = node["name"]
            host = node["host"]

            for field in self.fields:
                unwrap_metric(event_fn,
                              self.prefix + "nodes." + name,
                              field,
                              node[field])
