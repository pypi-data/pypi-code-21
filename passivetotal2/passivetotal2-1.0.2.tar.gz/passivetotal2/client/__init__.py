'''
The client module provides the `Client` implementation, a thin wrapper which
keeps track of authentication for the most part.
'''
from .artifact import ArtifactClient
from .account import AccountClient
from .actions import ActionsClient
from .dns import DNSClient
from .enrichment import EnrichmentClient
from .host import HostClient
from .project import ProjectClient
from .ssl import SSLClient
from .whois import WhoisClient
from .baseclient import iter_not_none


class Client(ArtifactClient, AccountClient, ActionsClient, DNSClient,
             EnrichmentClient, HostClient,
             ProjectClient, SSLClient, WhoisClient):
    def get_monitor_alerts(self, project=None, artifact=None,
                           start=None, end=None):
        params = dict(iter_not_none(
            project=project, artifact=artifact, start=start, end=end
        ))
        return self.get('/monitor', params=params)

    def get_trackers(self, query, type):
        data = {'query': query, 'type': type}
        return self.get('/trackers/search', data=data)
