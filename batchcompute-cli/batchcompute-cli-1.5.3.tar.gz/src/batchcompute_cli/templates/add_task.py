#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

oss_host = os.environ.get('BATCH_COMPUTE_OSS_HOST')
region = os.environ.get('BATCH_COMPUTE_REGION')
cluster_id = os.environ.get('BATCH_COMPUTE_CLUSTER_ID')
worker_id = os.environ.get('BATCH_COMPUTE_WORKER_ID')

job_id = os.environ['BATCH_COMPUTE_DAG_JOB_ID']
task_id = os.environ['BATCH_COMPUTE_DAG_TASK_ID']
instance_id = os.environ['BATCH_COMPUTE_DAG_INSTANCE_ID']

print('your code goes here')