#!/usr/bin/env python
import json
from simpleflow.job import KubernetesJob
from uuid import uuid4

input = """
{
  "args": [
    "s3://com.botify.saas.production.analyses/s/scr/scribd-29337/20170906-132568/crawl-result",
    "s3://com.botify.saas.production.temp/3/crawls/132568",
    97
  ],
  "kwargs": {
    "mp": "s3://com.botify.saas.production.analyses/s/scr/scribd-29337/20170906-132568/crawl-result/metrology/sims",
    "storage_uri": "s3://com.botify.saas.production.temp/3/swf/d22edcdfee67.res",
    "task_id": "botify.cdf.features.content_quality.tasks.interfaces.cb_parse.CbParse-f8e30deec6ee0d45c40b76d6c7b9651f"
  }
}
"""

response = {
   "activityId": "activity-botify.cdf.features.content_quality.tasks.interfaces.cb_parse.CbParse-0c740140da5fbc7f802d24afe1166227",
   "activityType": {
      "name": "botify.cdf.features.content_quality.tasks.interfaces.cb_parse.CbParse",
      "version": "2.9"
   },
   "input": input,
   "startedEventId": 123,
   "taskToken": "a-very-long-token",
   "workflowExecution": {
      "runId": "workflow_id",
      "workflowId": "run/id/124325346547547474z"
   }
}

KubernetesJob.from_swf_response(response, "com.botify.saas.sandbox1.backend").schedule()
