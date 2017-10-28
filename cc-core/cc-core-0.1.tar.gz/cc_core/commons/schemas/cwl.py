_cwl_types = ['string', 'int', 'long', 'float', 'double', 'null', 'array', 'record', 'File', 'Any']

cwl_schema = {
    'type': 'object',
    'properties': {
        'cwlVersion': {'enum': ['v1.0']},
        'class': {'enum': ['CommandLineTool']},
        'baseCommand': {'type': 'string'},
        'hints': {
            'type': 'object',
            'properties': {
                'DockerRequirement': {
                    'type': 'object',
                    'properties': {
                        'dockerPull': {'type': 'string'}
                    },
                    'additionalProperties': False,
                    'required': ['dockerPull']
                }
            },
            'additionalProperties': False
        },
        'inputs': {
            'type': 'object',
            'patternProperties': {
                '^[a-zA-Z0-9_-]+$': {
                    'type': 'object',
                    'properties': {
                        'type': {'enum': _cwl_types + ['{}?'.format(t) for t in _cwl_types]},
                        'inputBinding': {
                            'type': 'object',
                            'properties': {
                                'prefix': {'type': 'string'}
                            },
                            'additionalProperties': False,
                            'required': ['prefix']
                        },
                        'doc': {'type': 'string'}
                    },
                    'additionalProperties': False,
                    'required': ['type', 'inputBinding']
                }
            }
        }
    },
    'additionalProperties': False,
    'required': ['cwlVersion', 'class', 'baseCommands', 'inputs']
}
