import aiohttp

from time import time

from oshino import Agent
from oshino.agents.http_agent import HttpAgent


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


class ElasticSearchAgent(HttpAgent):

    async def retrieve_cluster_health(self):
        path = "{0}/_cluster/health".format(self.url)
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
        event_fn(service=self.prefix + "health",
                 metric_f=span,
                 state=str(state),
                 description=self.url)

        # Other cluster info
        del cluster_health["cluster_name"]
        del cluster_health["timed_out"]
        del cluster_health["status"]


        for key, val in cluster_health.items():
            event_fn(service=self.prefix + key,
                     metric_f=float(val),
                     state="ok",
                     description=self.url)

