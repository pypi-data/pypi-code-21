#
#  This is the configuration file that allows to configure values that are
# required to access various S3 stores.
#
# If you want to add a S3 store that is not available as an entry, yet:
#   - create a new (unique!) key within the TYPES dict
#   - add a dict as value to the key, holding the same keys (all of them!)
#     as there are in the existing ones
#   - enter a default endpoint, and
#   - a region (if the new S3 store supports regions)
#   - if the S3 store has regions, add the new key to the REGIONREQUIRED list
#

# the TYPES dict describes the parameters that are used in .hs3sh.conf:
TYPES = {'aws': {'comment': '',
                 'endpoint': 's3.amazonaws.com',
                 'region': 'us-east-1',
                 'https': True,
                 'port': 443,
                 'aws_access_key_id': '',
                 'aws_secret_access_key': ''
                 },
         'cloudian': {'comment': '',
                      'endpoint': 'cloudian.your.domain',
                      'region': 's3-region',
                      'https': True,
                      'port': 443,
                      'aws_access_key_id': '',
                      'aws_secret_access_key': ''
                      },
         'ecs': {'comment': '',
                 'endpoint': 'namespace.ecs.your.domain',
                 'region': '',
                 'https': True,
                 'port': 9021,
                 'aws_access_key_id': '',
                 'aws_secret_access_key': ''
                 },
         'hs3': {'comment': '',
                 'endpoint': 'tenant.hcp.your.domain',
                 'region': '',
                 'https': True,
                 'port': 443,
                 'aws_access_key_id': '',
                 'aws_secret_access_key': ''
                 },
         'compatible': {'comment': '',
                        'endpoint': 'whatever.your.domain',
                        'region': '',
                        'https': True,
                        'port': 443,
                        'aws_access_key_id': '',
                        'aws_secret_access_key': ''
                        },
         }

# these are the S3 store types that require a region to be set:
REGIONREQUIRED = ['aws', 'cloudian']

##### NO CHANGES BELOW THIS LINE, PLEASE #####
# these are boolean tags
BOOLTAGS = ['https']
# these are integer tags
INTTAGS = ['port']
# these are the keys that _need_ to have entries in .hs3sh.conf:
REQUIRED = ['endpoint', 'https', 'port',
            'aws_access_key_id', 'aws_secret_access_key']
# these are the keys that are optional:
OPTIONAL = ['comment', 'region']