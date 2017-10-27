#!/usr/bin/env python
import kubernetes.config
import kubernetes.client

#kubernetes.config.load_incluster_config()
kubernetes.config.load_kube_config()

namespace = 'sandbox1'
name = 'test-job'
labels = {'job': 'test'}
container_command = ['echo', 'Hello World']
job_restart_policy = 'Never'

meta = kubernetes.client.V1ObjectMeta()
meta.name = name
meta.labels = {}

spec = kubernetes.client.V1JobSpec()

spec.template = kubernetes.client.V1PodTemplateSpec()
spec.template.metadata = kubernetes.client.V1ObjectMeta(name=name)
spec.template.spec = kubernetes.client.V1PodSpec(containers=[
    kubernetes.client.V1Container(name='main', image='alpine', command=['echo', 'Hello World'])
], restart_policy="OnFailure")

data = kubernetes.client.V1Job()
data.api_version = 'batch/v1'
data.kind = 'Job'
data.metadata = meta
data.spec = spec

k8s_client = kubernetes.client.BatchV1Api()
k8s_client.create_namespaced_job(body=data, namespace=namespace)
