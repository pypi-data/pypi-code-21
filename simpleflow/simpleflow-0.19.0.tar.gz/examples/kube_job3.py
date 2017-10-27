

        namespace = "default"
        name = self.job_name

        meta = kubernetes.client.V1ObjectMeta()
        meta.name = name
        meta.labels = {"env": namespace}

        env_vars = [
            kubernetes.client.V1EnvVar(name=key, value=os.environ[key])
            for key in os.environ.keys()
        ]
        if "SWF_DOMAIN" not in os.environ:
            env_vars.append(
                kubernetes.client.V1EnvVar(name="SWF_DOMAIN", value=self.domain)
            )

        spec = kubernetes.client.V1JobSpec()
        spec.template = kubernetes.client.V1PodTemplateSpec()
        spec.template.metadata = kubernetes.client.V1ObjectMeta(name=name)
        spec.template.spec = kubernetes.client.V1PodSpec(
            containers=[
                kubernetes.client.V1Container(
                    name="main",
                    image="botify/botify:kubernetes",
                    image_pull_policy="Always",
                    command=None,
                    args=["--mode", "poller", "--upsimpleflow", "--git-checkout", "kubernetes", "simpleflow", "activity.execute", "--payload", b64encode(json_dumps(self.response))],
                    env=env_vars,
                ),
            ],
            image_pull_secrets=[
                kubernetes.client.V1LocalObjectReference(name="docker-hub-botifyci"),
            ],
            restart_policy="Never",
        )

        data = kubernetes.client.V1Job()
        data.api_version = "batch/v1"
        data.kind = "Job"
        data.metadata = meta
        data.spec = spec

        k8s_client = kubernetes.client.BatchV1Api()
        k8s_client.create_namespaced_job(body=data, namespace=namespace)
