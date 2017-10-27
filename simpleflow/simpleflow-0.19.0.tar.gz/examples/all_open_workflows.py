#!/usr/bin/env python
import time
from swf.models import Domain
from swf.querysets import WorkflowExecutionQuerySet

SWF_DOMAIN = "com.botify.saas.production.backend"

domain = Domain(SWF_DOMAIN)
qs = WorkflowExecutionQuerySet(domain)
###executions = qs.filter(tag="operation=cb_recompress")
executions = qs.filter(status="OPEN") #, start_oldest_date=int(time.time() - 90*))

for exe in executions:
    if not exe.workflow_id.startswith("crawl_") and not exe.workflow_id.startswith("analysis_"):
        continue
    print exe.workflow_id, exe.start_timestamp
