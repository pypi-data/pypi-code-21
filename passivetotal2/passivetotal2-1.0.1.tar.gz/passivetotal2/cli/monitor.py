import json
import sys
from ..output import row_gen, output


def monitor(client, project, artifact, start=None, end=None, **kwargs):
    if not (project or artifact):
        sys.exit('at least one of --project or --artifact is required')
    response = client.get_monitor_alerts(project, artifact, start, end).data
    if 'message' in response:
        sys.exit(response['message'])

    if kwargs.get('json'):
        return json.dumps(response, indent=4)

    result = []
    for i in response['results']:
        result.extend([dict(guid=i, **j) for j in response['results'][i]])

    rows = row_gen(result)
    return output(list(rows), **kwargs)
