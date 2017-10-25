import requests
import json
from functools import reduce

class Package:
    def __init__(self, package_data):
        self.package_data = package_data

    def __str__(self):
        return "{:30} {}\t{:>8,}".format(self.id, self.version, self.total_downloads)
    
    @property
    def id(self):
        return self.package_data['id']
    @property
    def version(self):
        return self.package_data['version']
    @property
    def project_url(self):
        projectUrlKey = 'projectUrl'
        if projectUrlKey in self.package_data:
            return self.package_data[projectUrlKey]
        else:
            return None
    @property
    def total_downloads(self):
        return self.package_data['totalDownloads']

class PackageManager:
    def get_packages(self,owner='PluginsForXamarin'):
        response = requests.get('https://api-v2v3search-0.nuget.org/query?q={}&prerelease=false&includeDelisted=false'.format(owner))
        if response.ok:
            package_data = json.loads(response.content)['data']
            items = map(lambda x: Package(x), package_data)
            return list(items)
        else:
            response.raise_for_status()