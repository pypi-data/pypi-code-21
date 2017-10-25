
from ..const import EVENTS
from batchcompute.utils.functions import ConfigError
from terminal import Logger, white, blue, green,magenta,bold

from ..util import config, client,formater,result_cache,list2table
import json

log = Logger()


def list(show_json=False):

    if show_json:
        print(json.dumps(EVENTS, indent=2))
        return

    t=[]

    for n in EVENTS['CLUSTER']:
        t.append({'Name':n})
    list2table.print_table(t, [('Name', 'For Cluster')], False)

    t2=[]
    for n in EVENTS['JOB']:
        t2.append({"Name": n})
    list2table.print_table(t2, [('Name','For job:')], False)


