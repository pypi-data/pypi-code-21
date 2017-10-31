import json
import jsone

new_expires = '7 days'
scope_ignore = 'docker-worker:cache:'

template =  {
    '$merge': [
        {'$eval': 'task'},
        {'created': {'$fromNow': ''}},
        {'deadline': {'$fromNow': '12 hours'}},
        {'expires': {'$fromNow': new_expires}},
        {'scopes': {'$map': {'$eval': 'task.scopes'}, 'each(scope)': {
            '$if': 'scope[:{}] == "{}"'.format(len(scope_ignore), scope_ignore)
        }}},
        {
            'payload': {
                '$merge': [
                    {
                        '$map': {'$eval': 'task.payload'},
                        'each(s)': {
                            '$if': '!(s.key in ["artifacts", "cache"])',
                            'then': {'${s.key}': {'$eval': 's.val'}}
                        }
                    },
                    {
                        'maxRunTime': {'$eval': 'max(task.payload.maxRunTime, 3 * 60 * 60)'},
                        'features': {'interactive': True},
                        'env': {
                            'TASKCLUSTER_INTERACTIVE': 'true',
                        }
                    }
                ]
            }
        }
    ]
}

#template = {
#    '$merge': [
#        {'$eval': 'task'},
#        {'created': {'$fromNow': ''}},
#        {'deadline': {'$fromNow': '1 day'}},
#        {'expires': {'$fromNow': new_expires}},
#        {'payload': {
#            '$merge': [
#                {'$eval': 'task.payload'},
#                {
#                    '$if': '"artifacts" in task.payload',
#                    'then': {
#                        'artifacts': {
#                            '$if': 'typeof(task.payload.artifacts) == "object"',
#                            'then': {
#                                '$map': {'$eval': 'task.payload.artifacts'},
#                                'each(artifact)': {
#                                    '${artifact.key}': {
#                                        '$merge': [
#                                            {'$eval': 'artifact.val'},
#                                            {'expires': {'$fromNow': new_expires}},
#                                        ],
#                                    },
#                                },
#                            },
#                            'else': {
#                                '$map': {'$eval': 'task.payload.artifacts'},
#                                'each(artifact)': {
#                                    '$merge': [
#                                        {'$eval': 'artifact'},
#                                        {'expires': {'$fromNow': new_expires}},
#                                    ],
#                                },
#                            },
#                        },
#                    },
#                    'else': {},
#                }
#            ]
#        }}
#    ]
#}

ttt = """
{
  "provisionerId": "aws-provisioner-v1",
  "workerType": "gecko-decision",
  "schedulerId": "gecko-level-1",
  "taskGroupId": "EMCtoS2eRee4CUM-4_GC_g",
  "dependencies": [],
  "requires": "all-completed",
  "routes": [
    "index.gecko.v2.try.latest.firefox.decision",
    "index.gecko.v2.try.pushlog-id.204690.decision",
    "tc-treeherder.v2.try.19d54f008cbc0a91bad523ffb837020b4d060830.204690",
    "tc-treeherder-stage.v2.try.19d54f008cbc0a91bad523ffb837020b4d060830.204690",
    "notify.email.ecoal95@gmail.com.on-failed",
    "notify.email.ecoal95@gmail.com.on-exception"
  ],
  "priority": "lowest",
  "retries": 5,
  "created": "2017-07-13T13:18:47.833Z",
  "deadline": "2017-07-14T13:18:47.835Z",
  "expires": "2018-07-13T13:18:47.835Z",
  "scopes": [
    "assume:repo:hg.mozilla.org/try:*",
    "queue:route:notify.email.ecoal95@gmail.com.*"
  ],
  "payload": {
    "env": {
      "GECKO_BASE_REPOSITORY": "https://hg.mozilla.org/mozilla-unified",
      "GECKO_HEAD_REPOSITORY": "https://hg.mozilla.org/try/",
      "GECKO_HEAD_REF": "19d54f008cbc0a91bad523ffb837020b4d060830",
      "GECKO_HEAD_REV": "19d54f008cbc0a91bad523ffb837020b4d060830",
      "HG_STORE_PATH": "/home/worker/checkouts/hg-store"
    },
    "cache": {
      "level-1-checkouts": "/home/worker/checkouts"
    },
    "features": {
      "taskclusterProxy": true,
      "chainOfTrust": true
    },
    "image": "taskcluster/decision:0.1.8@sha256:195d8439c8e90d59311d877bd2a8964849b2e43bfc6c234092618518d8b2891b",
    "maxRunTime": 1800,
    "command": [
      "/home/worker/bin/run-task",
      "--vcs-checkout=/home/worker/checkouts/gecko",
      "--",
      "bash",
      "-cx",
      "cd /home/worker/checkouts/gecko && ln -s /home/worker/artifacts artifacts && ./mach --log-no-times taskgraph decision --pushlog-id='204690' --pushdate='1499951882' --project='try' --message='try: -b do -p linux64-stylo,linux64 -u all -t none' --owner='ecoal95@gmail.com' --level='1' --base-repository='https://hg.mozilla.org/mozilla-central' --head-repository='https://hg.mozilla.org/try/' --head-ref='19d54f008cbc0a91bad523ffb837020b4d060830' --head-rev='19d54f008cbc0a91bad523ffb837020b4d060830'"
    ],
    "artifacts": {
      "public": {
        "type": "directory",
        "path": "/home/worker/artifacts",
        "expires": "2018-07-12T13:18:47.836Z"
      }
    }
  },
  "metadata": {
    "owner": "mozilla-taskcluster-maintenance@mozilla.com",
    "source": "https://hg.mozilla.org/try/raw-file/19d54f008cbc0a91bad523ffb837020b4d060830/.taskcluster.yml",
    "name": "Gecko Decision Task",
    "description": "The task that creates all of the other tasks in the task graph"
  },
  "tags": {
    "createdForUser": "ecoal95@gmail.com"
  },
  "extra": {
    "treeherder": {
      "symbol": "D"
    }
  }
}
"""

qqq = """
{
  "provisionerId": "aws-provisioner-v1",
  "workerType": "gecko-1-b-win2012",
  "schedulerId": "gecko-level-1",
  "taskGroupId": "QTkxKDTCTmeLGbi5iUb1Rw",
  "dependencies": [
    "QTkxKDTCTmeLGbi5iUb1Rw"
  ],
  "requires": "all-completed",
  "routes": [
    "index.gecko.v2.try.latest.firefox.win32-debug",
    "index.gecko.v2.try.pushdate.2017.07.14.20170714193701.firefox.win32-debug",
    "index.gecko.v2.try.revision.c4f8143f2d4826ce2283f35158e4b633dae98ba5.firefox.win32-debug",
    "tc-treeherder.v2.try.c4f8143f2d4826ce2283f35158e4b633dae98ba5.205176",
    "tc-treeherder-stage.v2.try.c4f8143f2d4826ce2283f35158e4b633dae98ba5.205176"
  ],
  "priority": "very-low",
  "retries": 5,
  "created": "2017-07-14T19:38:51.594Z",
  "deadline": "2017-07-15T19:38:51.594Z",
  "expires": "2017-08-11T19:38:51.594Z",
  "scopes": [],
  "payload": {
    "env": {
      "MOZ_SIMPLE_PACKAGE_NAME": "target",
      "MOZ_BUILD_DATE": "20170714193701",
      "GECKO_HEAD_REV": "c4f8143f2d4826ce2283f35158e4b633dae98ba5",
      "MOZ_SCM_LEVEL": "1",
      "GECKO_BASE_REPOSITORY": "https://hg.mozilla.org/mozilla-central",
      "GECKO_HEAD_REPOSITORY": "https://hg.mozilla.org/try/",
      "TOOLTOOL_MANIFEST": "browser/config/tooltool-manifests/win32/releng.manifest",
      "GECKO_HEAD_REF": "c4f8143f2d4826ce2283f35158e4b633dae98ba5",
      "MOZ_AUTOMATION": "1"
    },
    "artifacts": [
      {
        "path": "public/build",
        "expires": "2017-08-11T19:38:51.594814Z",
        "type": "directory"
      }
    ],
    "maxRunTime": 7200,
    "command": [
    ],
    "osGroups": [],
    "mounts": [],
    "features": {
      "chainOfTrust": true
    }
  },
  "metadata": {
    "owner": "kvijayan@mozilla.com",
    "source": "https://hg.mozilla.org/try//file/c4f8143f2d4826ce2283f35158e4b633dae98ba5/taskcluster/ci/build",
    "description": "Win32 Debug ([Treeherder push](https://treeherder.mozilla.org/#/jobs?repo=try&revision=c4f8143f2d4826ce2283f35158e4b633dae98ba5))",
    "name": "build-win32/debug"
  },
  "tags": {
    "createdForUser": "kvijayan@mozilla.com"
  },
  "extra": {
    "index": {
      "rank": 1500061021
    },
    "treeherderEnv": [
      "production",
      "staging"
    ],
    "treeherder": {
      "jobKind": "build",
      "groupSymbol": "tc",
      "collection": {
        "debug": true
      },
      "machine": {
        "platform": "windows2012-32"
      },
      "groupName": "Executed by TaskCluster",
      "tier": 1,
      "symbol": "B"
    }
  }
}
"""

rrr = """
{
  "provisionerId": "aws-provisioner-v1",
  "workerType": "gecko-1-b-win2012",
  "schedulerId": "gecko-level-1",
  "taskGroupId": "QTkxKDTCTmeLGbi5iUb1Rw",
  "dependencies": [
    "QTkxKDTCTmeLGbi5iUb1Rw"
  ],
  "requires": "all-completed",
  "routes": [
    "index.gecko.v2.try.latest.firefox.win32-debug",
    "index.gecko.v2.try.pushdate.2017.07.14.20170714193701.firefox.win32-debug",
    "index.gecko.v2.try.revision.c4f8143f2d4826ce2283f35158e4b633dae98ba5.firefox.win32-debug",
    "tc-treeherder.v2.try.c4f8143f2d4826ce2283f35158e4b633dae98ba5.205176",
    "tc-treeherder-stage.v2.try.c4f8143f2d4826ce2283f35158e4b633dae98ba5.205176"
  ],
  "priority": "very-low",
  "retries": 5,
  "created": "2017-07-14T19:38:51.594Z",
  "deadline": "2017-07-15T19:38:51.594Z",
  "expires": "2017-08-11T19:38:51.594Z",
  "scopes": [],
  "payload": {
    "env": {
      "MOZ_SIMPLE_PACKAGE_NAME": "target",
      "MOZ_BUILD_DATE": "20170714193701",
      "GECKO_HEAD_REV": "c4f8143f2d4826ce2283f35158e4b633dae98ba5",
      "MOZ_SCM_LEVEL": "1",
      "GECKO_BASE_REPOSITORY": "https://hg.mozilla.org/mozilla-central",
      "GECKO_HEAD_REPOSITORY": "https://hg.mozilla.org/try/",
      "TOOLTOOL_MANIFEST": "browser/config/tooltool-manifests/win32/releng.manifest",
      "GECKO_HEAD_REF": "c4f8143f2d4826ce2283f35158e4b633dae98ba5",
      "MOZ_AUTOMATION": "1"
    },
    "maxRunTime": 7200,
    "command": [
    ],
    "osGroups": [],
    "mounts": [],
    "features": {
      "chainOfTrust": true
    }
  },
  "metadata": {
    "owner": "kvijayan@mozilla.com",
    "source": "https://hg.mozilla.org/try//file/c4f8143f2d4826ce2283f35158e4b633dae98ba5/taskcluster/ci/build",
    "description": "Win32 Debug ([Treeherder push](https://treeherder.mozilla.org/#/jobs?repo=try&revision=c4f8143f2d4826ce2283f35158e4b633dae98ba5))",
    "name": "build-win32/debug"
  },
  "tags": {
    "createdForUser": "kvijayan@mozilla.com"
  },
  "extra": {
    "index": {
      "rank": 1500061021
    },
    "treeherderEnv": [
      "production",
      "staging"
    ],
    "treeherder": {
      "jobKind": "build",
      "groupSymbol": "tc",
      "collection": {
        "debug": true
      },
      "machine": {
        "platform": "windows2012-32"
      },
      "groupName": "Executed by TaskCluster",
      "tier": 1,
      "symbol": "B"
    }
  }
}
"""

context = {'task': json.loads(ttt)}

a = jsone.render(template, context)

import pprint
print(pprint.pprint(a))
