#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.config
    ~~~~~~~~~~~~

    This module provide the global settings.

    :copyright: (c) 2017 by Ma Fei.
"""

agent = {
    "port": 9096,
    "agent_id": 0
}

agent_env_port = {
    "alpha": 9096,
    "dev": 9096,
    "prod": 9099,
}
qualityplatform = {
    "api_url": "http://qp.elenet.me/api/"
}

qualityplatform_env_api_url = {
    "alpha": "http://qp.alpha.elenet.me/api/",
    "dev": "http://adca-waimai-qualityplatform-1.vm.elenet.me/api/",
    "prod": "http://qp.elenet.me/api/",
}

sentry_url = {
    "url": "https://bdfb78f23a6a4bebb62ad2108c79a01b:d60af383987444b595ceb0d9019f6d23@sentry.elenet.me/181"
}

sentry_env_url = {
    "alpha": "https://faf72d91b8724a59823e096c9acf397a:17cdc3bffe7a45b1b01894ecf4ae6048@sentry.alpha.elenet.me/1283",
    "dev": "https://bdfb78f23a6a4bebb62ad2108c79a01b:d60af383987444b595ceb0d9019f6d23@sentry.elenet.me/181",
    "prod": "https://bdfb78f23a6a4bebb62ad2108c79a01b:d60af383987444b595ceb0d9019f6d23@sentry.elenet.me/181",
}
