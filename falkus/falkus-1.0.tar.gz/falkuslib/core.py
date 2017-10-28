import logging
import json
import itertools

import awsutils


FALKUS_MANIFEST_NAME = "falkus.json"


class Falkus(object):
    def __init__(self):
        self._manifest = self.load_manifest()
        awsutils.set_boto_logging_level(logging.WARNING)

    def load_manifest(self):
        with open(FALKUS_MANIFEST_NAME, "r") as infile:
            return json.load(infile)

    def execute(self, args):
        command = args.command

        command_dictionary = {
            "info": self.cmd_info,
            "aws-init-stage": self.cmd_aws_init_stage
        }
        command_dictionary.get(command)(args)

    def cmd_info(self, args):
        logging.info("falkus project: %s", self._manifest["name"])
        logging.info("manifest: %s", json.dumps(self._manifest, sort_keys=True, indent=4))

    def cmd_aws_init_stage(self, args):
        stage = args.stage
        output_path = "."
        project_name = self._manifest["name"]
        region = self._manifest["stages"][stage]["region"]
        users = self._manifest["stages"][stage]["users"]
        logging.info("initializing stage %s falkus project: %s", stage, project_name)
        account_id = awsutils.get_account_id()
        logging.info("signin url for your IAM: https://%s.signin.aws.amazon.com/console", account_id)
        for username in users:
            awsutils.create_user_with_credentials_and_key(username, output_path)
        admin_policy_name = awsutils.compose_name(project_name, stage, "AdminPolicy")
        admin_policy_arn = awsutils.compose_policy_arn(account_id, admin_policy_name)
        admin_policy = awsutils.compose_admin_policy(account_id, project_name, stage)
        admin_group_name = awsutils.compose_name(project_name, stage, "AdminGroup")

        awsutils.create_or_update_iam_managed_policy(admin_policy_arn, admin_policy_name, admin_policy)
        awsutils.create_iam_group(admin_group_name)
        awsutils.attach_policy_to_group(admin_group_name, admin_policy_arn)

        for username in users:
            awsutils.add_user_to_group(username, admin_group_name)
        awsutils.create_bucket(awsutils.compose_bucket_name(project_name, stage, "Frontend"), region, acl='public-read')
        awsutils.set_bucket_for_website(awsutils.compose_bucket_name(project_name, stage, "Frontend"))
        awsutils.create_bucket(awsutils.compose_bucket_name(project_name, stage, "User_Data"), region)
        awsutils.create_bucket(awsutils.compose_bucket_name(project_name, stage, "Backend"), region)

