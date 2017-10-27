#!/usr/bin/env python
import time
from swf.models import Domain
from swf.querysets import WorkflowExecutionQuerySet

SWF_DOMAIN = "com.botify.saas.production.backend"

domain = Domain(SWF_DOMAIN)
qs = WorkflowExecutionQuerySet(domain)
###executions = qs.filter(tag="operation=cb_recompress")
executions = qs.filter(status="CLOSED", tag="operation=cb_recompress", close_oldest_date=int(time.time() - 900))

for exe in executions:
    print exe.workflow_id, exe.close_status
