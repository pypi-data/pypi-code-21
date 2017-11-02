import boto3
import re


class BotoFactory(object):
    def __init__(self, project_name, stage, stage_cfg):
        self.project_name = project_name
        self.stage = stage
        self.stage_cfg = stage_cfg

    def resource(self, aws_service):
        # type: (string) -> boto3.resources.base.ServiceResource
        ep_overrides = self.stage_cfg.get("endpoint_overrides", {})
        return boto3.resource(aws_service,
                              region_name =self.stage_cfg["region"],
                              endpoint_url=ep_overrides.get(aws_service, None))

    def client(self, aws_service):
        # type: (string) -> botocore.client.BaseClient
        ep_overrides = self.stage_cfg.get("endpoint_overrides", {})
        return boto3.client(aws_service,
                            region_name =self.stage_cfg["region"],
                            endpoint_url=ep_overrides.get(aws_service, None))

    def format_name(self, name):
        return "_".join([self.project_name, self.stage, name])

    def format_bucket_name(self, name):
        invalid_name = self.format_name(name)
        dotted = re.sub("[^A-Za-z0-9]", "-", invalid_name)
        return ".".join([s.lower() for s in dotted.split("-")])

    def get_region(self):
        return self.stage_cfg["region"]

    def get_stage(self):
        return self.stage
