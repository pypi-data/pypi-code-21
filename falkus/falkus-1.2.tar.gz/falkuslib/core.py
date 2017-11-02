import logging
import json
import jsonschema
import shutil

import sysutils
import awsutils
import os
import glob

from resource_graph_processor import ResourceGraphProcessor
from boto_factory import BotoFactory
from lws import STAGE_CONFIG, STAGE_LOCAL


FALKUS_MANIFEST_NAME = "falkus.json"

FALKUS_MANIFES_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "FalkusManifestSchema",
    "description": "Falkus manifest schema",
    "type":"object",
    "required": ["name", "stages", "src-paths", "test-paths", "frontend-path", "aws-resources-path", "build-path",
                 "runtime-dependencies", "test-dependencies",  "dependencies-local-setup-dir"],
    "properties": {
        "name": {"type": "string"},
        "stages": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "type":"object",
                    "required": ["users", "region", "type"],
                    "properties": {
                        "users": {"type": "array", "items": {"type": "string"}},
                        "region": {"type": "string"},
                        "type": {"type": "string", "enum": ["test", "production"],},
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        },
        "src-paths": {"type": "array", "items": {"type": "string"}},
        "test-paths": {"type": "array", "items": {"type": "string"}},
        "frontend-path": {"type": "string"},
        "aws-resources-path": {"type": "string"},
        "runtime-dependencies": {"type": "object"},
        "test-dependencies": {"type": "object"},
        "dependencies-local-setup-dir": {"type": "string"},
        "build-path": {"type": "string"}
    },
    "additionalProperties": False
}


class FalkusException(Exception):
    def __init__(self, message):
        super(FalkusException, self).__init__(message)


class Falkus(object):
    def __init__(self):
        self._manifest = self.load_manifest()
        awsutils.set_boto_logging_level(logging.WARNING)

    @staticmethod
    def load_manifest():
        if not os.path.isfile(FALKUS_MANIFEST_NAME):
            raise FalkusException("missing manifest file %s - not a falkus project root " % FALKUS_MANIFEST_NAME)
        try:
            with open(FALKUS_MANIFEST_NAME, "r") as infile:
                manifest = json.load(infile)
        except Exception:
            logging.exception("could not load manifest file")
            raise FalkusException("could not load manifest file")
        try:
            jsonschema.validate(manifest, FALKUS_MANIFES_SCHEMA)
        except jsonschema.ValidationError:
            logging.exception("invalid manifest file")
            raise FalkusException("invalid manifest file")
        missing_dirs = [p for p in manifest["src-paths"] if not os.path.isdir(p)]
        missing_dirs += [p for p in manifest["test-paths"] if not os.path.isdir(p)]
        if missing_dirs:
            logging.error("the following directories declared in the manifest file do not exist: %s",
                          ", ".join(missing_dirs))
            raise FalkusException("missing directories declared in manifest file")
        return manifest

    def execute(self, args):
        command = args.command

        command_dictionary = {
            "info": self.cmd_info,
            "test": self.cmd_test,
            "start-local": self.cmd_start_local,
            "aws-init-stage": self.cmd_aws_init_stage,
            "aws-create-resources": self.cmd_aws_create_resources,
            "aws-deploy": self.cmd_aws_deploy,

        }
        command_dictionary.get(command)(args)

    def cmd_info(self, args):
        logging.info("falkus project: %s", self._manifest["name"])
        logging.info("manifest: %s", json.dumps(self._manifest, sort_keys=True, indent=4))

    def cmd_test(self, args):
        import sys
        sys.path.append(self._manifest["dependencies-local-setup-dir"])
        for p in self._manifest["src-paths"]:
            sys.path.append(p)
        for p in self._manifest["test-paths"]:
            sys.path.append(p)
        import unittest
        logging.info("Running unit tests")
        tl = unittest.TestLoader()
        for p in self._manifest["test-paths"]:
            ts = tl.discover(start_dir=p, pattern="*_unit_test.py")
            unittest.TextTestRunner(verbosity=2).run(ts)
        logging.info("Running integration tests")
        for p in self._manifest["test-paths"]:
            ts = tl.discover(start_dir=p, pattern="*_integ_test.py")
            unittest.TextTestRunner(verbosity=2).run(ts)
        logging.info("test completed")

    def cmd_aws_init_stage(self, args):
        stage = args.stage
        output_path = "."
        project_name = self._manifest["name"]
        botoFactory = BotoFactory(project_name, stage, STAGE_CONFIG[stage])

        users = self._manifest["stages"][stage]["users"]
        logging.info("initializing stage %s falkus project: %s", stage, project_name)
        account_id = awsutils.get_account_id(botoFactory)
        logging.info("signin url for your IAM: https://%s.signin.aws.amazon.com/console", account_id)
        for username in users:
            awsutils.create_user_with_credentials_and_key(botoFactory, username, output_path)
        admin_policy_name = botoFactory.format_name("AdminPolicy")
        admin_policy_arn = awsutils.compose_policy_arn(account_id, admin_policy_name)
        admin_policy = awsutils.compose_admin_policy(botoFactory, account_id, project_name, stage)
        admin_group_name = botoFactory.format_name("AdminGroup")

        awsutils.create_or_update_iam_managed_policy(botoFactory, admin_policy_arn, admin_policy_name, admin_policy)
        awsutils.create_iam_group(botoFactory, admin_group_name)
        awsutils.attach_policy_to_group(botoFactory, admin_group_name, admin_policy_arn)

        for username in users:
            awsutils.add_user_to_group(botoFactory, username, admin_group_name)
        awsutils.create_bucket(botoFactory, botoFactory.format_bucket_name("Frontend"), acl='public-read')
        awsutils.set_bucket_for_website(botoFactory, botoFactory.format_bucket_name("Frontend"))
        awsutils.create_bucket(botoFactory, botoFactory.format_bucket_name("User_Data"))
        awsutils.create_bucket(botoFactory, botoFactory.format_bucket_name("Backend"))

    def cmd_start_local(self, args):
        self.prepare_dependencies_local_setup_dir()
        import subprocess
        try:
            sysutils.run_dynamodb_with_docker()
        except subprocess.CalledProcessError:
            logging.warning("could not start dynamodb, maybe it is already up on 8000, continuing")
        self.aws_create_resources(STAGE_LOCAL)
        sysutils.run_sam_local(self._manifest["frontend-path"])

    def cmd_aws_create_resources(self, args):
        self.aws_create_resources(args.stage)

    def aws_create_resources(self, stage):
        project_name = self._manifest["name"]
        # region = self._manifest["stages"][stage]["region"]
        botoFactory = BotoFactory(project_name, stage, STAGE_CONFIG[stage])
        resource_path = self._manifest["aws-resources-path"]
        self.add_runtime_sys_paths()
        rgp = ResourceGraphProcessor(
            variables={
                "project_name": project_name,
                "stage": stage,
                "region": botoFactory.get_region(),
                "account_id": awsutils.get_account_id(botoFactory)
            }).add_json_files("{}/*.json".format(resource_path))\
              .add_python_files("{}/*.py".format(resource_path));
        if stage == STAGE_LOCAL:
            rgp.keep_only_supported_resource(lambda r: r["type"] in ["dynamodb_table"])
        variables = rgp.process(lambda r,v: awsutils.aws_resource_processor(botoFactory, awsutils.ACTION_UPDATE, r, v))
        logging.info("resource created, variables: %s", str(variables))

    def add_runtime_sys_paths(self):
        import sys
        sys.path.append(self._manifest["dependencies-local-setup-dir"])
        for p in self._manifest["src-paths"]:
            sys.path.append(p)

    def prepare_dependencies_local_setup_dir(self):
        setup_dir = self._manifest["dependencies-local-setup-dir"]
        sysutils.pip_install_local_falkus(setup_dir)
        for dep, version_constraint in self._manifest["runtime-dependencies"].iteritems():
            if version_constraint == "latest":
                logging.info("installing dependencies %s%s to %s", dep, version_constraint, setup_dir)
                sysutils.pip_install(dep, setup_dir)
            else:
                logging.info("installing dependencies %s to %s latest version", dep, setup_dir)
                sysutils.pip_install(dep+version_constraint, setup_dir)

    def cmd_aws_deploy(self, args):
        build_path = self._manifest["build-path"]
        project_name = self._manifest["name"]
        stage = args.stage
        try:
            stage_info = self._manifest["stages"][stage]
        except KeyError:
            raise FalkusException("the stage {} is not defined in the manifest, check capitalization".format(stage))
        logging.info("building project in %s", build_path)
        shutil.rmtree(build_path, ignore_errors=True)
        assert not os.path.exists(build_path), "could not clean the build path " + build_path
        os.makedirs(build_path)
        self.prepare_dependencies_local_setup_dir()
        sysutils.copy_directory_content(self._manifest["dependencies-local-setup-dir"], build_path)
        for p in self._manifest["src-paths"]:
            sysutils.copy_directory_content(p, build_path)
        shutil.copy("main.py", build_path)
        shutil.copy("find_modules.py", build_path)
        shutil.copy("template.yaml", build_path)
        shutil.copy("swagger.yaml", build_path)
        logging.info("deploying to stage %s", stage)
        curdir = os.getcwd()
        try:
            os.chdir(build_path)
            backend_bucket_name = "{}.{}.backend".format(project_name.lower(), stage.lower())
            sysutils.run_sam_package(backend_bucket_name)
            cf_stack_name = "{}{}".format(project_name, stage)
            sysutils.run_sam_deploy(cf_stack_name)
        finally:
            os.chdir(curdir)
        frontend_bucket_url = "s3://{}.{}.frontend".format(project_name.lower(), stage.lower())
        sysutils.run_s3_sync(self._manifest["frontend-path"], frontend_bucket_url)
        logging.info("Deployment completed")
