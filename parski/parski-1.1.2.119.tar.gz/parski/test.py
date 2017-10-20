import parski

API_URL = "https://pctapi.cloudpod.apps.ge.com/aws/v2.0/"

parski.get_data(url=API_URL + 'accounts', source="api", key_var="PCT")