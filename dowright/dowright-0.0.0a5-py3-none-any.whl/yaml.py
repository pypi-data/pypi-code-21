import logging
from pathlib import Path
from typing import Any, Union

import ruamel.yaml as yaml
from ruamel.yaml.comments import CommentedMap

log = logging.getLogger('yaml')
log.addHandler(logging.NullHandler())

def dump(*a, **kw) -> str:
    kw['Dumper'] = yaml.RoundTripDumper
    kw['default_flow_style'] = False
    return yaml.dump(*a, **kw)

def load(*a, **kw) -> Any:
    kw['Loader'] = yaml.RoundTripLoader
    return yaml.load(*a, **kw)
    
def read_yaml(path:Union[str,Path]) -> Any:
    path = str(path) # for Path objects
    with open(path) as rfp:
        data = load(rfp)
    return data

def write_yaml(data:Any, path:Union[str,Path]) -> None:
    path = str(path) # for Path objects
    with open(path,'w') as wfp:
        dump(CommentedMap(data), wfp)

