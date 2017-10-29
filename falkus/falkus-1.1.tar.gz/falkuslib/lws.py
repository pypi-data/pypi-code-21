#wrappers to make lambda web services easier to implement and decoupled from the environment (local / gamma / prod)

import logging
import simplejson as json

import boto3
import botocore
import jsonschema
import os
import re

COGNITO_USER_ID = "cognito_user_id"
COGNITO_USER_TYPE = "cognito_user_type"

STAGE_LOCAL = "Local"
STAGE_GAMMA = "Gamma"
STAGE_PRODUCTION = "Prod"

DYNAMODB = "dynamodb"

STAGE_CONFIG = {
    STAGE_LOCAL:{
        "region":"eu-west-1",
        "endpoint_overrides":{
            DYNAMODB:"http://172.17.0.1:8000"
        }
    },
    STAGE_GAMMA:{
        "region":"eu-west-1",
    },
    STAGE_PRODUCTION:{
        "region":"eu-west-1",
    }
}


HTTP_SUCCESS = 200
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401

HTTP_DELETE = "DELETE"
HTTP_GET = "GET"
HTTP_HEAD = "HEAD"
HTTP_OPTIONS = "OPTIONS"
HTTP_PATCH = "PATCH"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_METHODS = [HTTP_DELETE, HTTP_GET, HTTP_HEAD, HTTP_OPTIONS, HTTP_PATCH, HTTP_POST, HTTP_PUT]


def lambda_web_service(event, context, service_dictionary, project_name):
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,"
                                                "X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": ",".join(HTTP_METHODS)}
    try:
        http_method = event["httpMethod"].upper()
        if http_method == HTTP_HEAD:
            return {"statusCode": HTTP_SUCCESS, "headers": headers}
        if http_method == HTTP_OPTIONS:
            return {"statusCode": HTTP_SUCCESS, "headers": headers}
        lws_context = LambdaWebServiceContext(event, context, service_dictionary, project_name)
        service = service_dictionary[lws_context.get_request_path()]
        response = service(lws_context)
        json_response = json.dumps(response, sort_keys=True, indent=4)
        return {"statusCode":HTTP_SUCCESS, "body":json_response,"headers":headers}
    except LambdaWebServiceException as e:
        logging.exception("LambdaWebServiceException in web service execution")
        return {"statusCode":e.http_error_code}
    except Exception as e:
        logging.exception("generic exception in web service execution")
        return {"statusCode":HTTP_INTERNAL_SERVER_ERROR}


class LambdaWebServiceException(Exception):
    def __init__(self,
                 http_error_code = HTTP_INTERNAL_SERVER_ERROR,
                 message = "errore nel sistema",
                 message_for_user = None,
                 caused_by=None):
        self.http_error_code = http_error_code
        self.message = message
        self.message_for_user = message_for_user
        self.caused_by = caused_by


class LambdaWebServiceContext(object):
    def __init__(self, event, context, callback, project_name):
        self._project_name = project_name
        try:
            self._path = event["path"]
            self._http_method = event["httpMethod"].upper()
        except KeyError as e:
            logging.error("unexpected http request, missing "+ e.message)
            raise LambdaWebServiceException(message="unexpected http request, missing "+ e.message)
        if self._http_method == HTTP_POST:
            self._parameters = json.loads(event["body"])
        else:
            logging.error("unsupported http method " + self._http_method)
            raise LambdaWebServiceException(message="unsupported http method " + self._http_method)
        self._stage, self._stage_cfg = self._identify_current_stage()
        if self._stage == STAGE_LOCAL:
            try:
                self._user_id = self._parameters.pop(COGNITO_USER_ID)
            except KeyError:
                self._user_id = None
            try:
                self._user_type = self._parameters.pop(COGNITO_USER_TYPE)
            except KeyError:
                self._user_type = None
        else:
            # TODO: implement cognito autorization
            self._user_id = None
            self._user_type = None

    def _identify_current_stage(self):
        gamma_suffix = (self._project_name + STAGE_GAMMA).lower()
        prod_suffix = (self._project_name + STAGE_PRODUCTION).lower()
        lambda_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', "")
        lambda_name_elab = re.sub("[^A-Za-z0-9]", "", lambda_name.lower())
        logging.info("processed lambda name: %s", lambda_name_elab)
        if lambda_name_elab.startswith(gamma_suffix):
            return STAGE_GAMMA, STAGE_CONFIG[STAGE_GAMMA]
        elif lambda_name_elab.startswith(prod_suffix):
            return STAGE_PRODUCTION, STAGE_CONFIG[STAGE_PRODUCTION]
        if os.environ.get("AWS_SAM_LOCAL", "false").lower() == "true":
            logging.warn("[LOCAL_EXECUTION] assuming stage Local")
            return STAGE_LOCAL, STAGE_CONFIG[STAGE_LOCAL]
        else:
            logging.error("unable to recognize the current stage, function name = %s "
                          "expected starting with %s or %s", lambda_name_elab, gamma_suffix, prod_suffix)
            raise LambdaWebServiceException("unable to recognize the current stage")


    def get_request_path(self):
        return self._path

    def get_request(self):
        return self._parameters

    def get_user_id(self):
        return self._user_id

    def get_user_type(self):
        return self._user_type

    def aws_format_name(self, name):
        return "_".join([self._project_name, self._stage, name])

    def aws_resource(self, aws_service):
        # type: (string) -> boto3.resources.base.ServiceResource
        ep_overrides = self._stage_cfg.get("endpoint_overrides", {})
        return boto3.resource(aws_service,
                              region_name =self._stage_cfg["region"],
                              endpoint_url=ep_overrides.get(aws_service, None))

    def aws_client(self, aws_service):
        # type: (string) -> botocore.client.BaseClient
        ep_overrides = self._stage_cfg.get("endpoint_overrides", {})
        return boto3.client(aws_service,
                            region_name =self._stage_cfg["region"],
                            endpoint_url=ep_overrides.get(aws_service, None))

    def dynamodb_table(self, name):
        table_name = self.aws_format_name(name)
        logging.debug("operating on table %s", table_name)
        return self.aws_resource(DYNAMODB).Table(table_name)

    def send_email(self, subject, email_body):
        raise Exception("TODO: not supported yet.")

    def check_user_authorization(self, EXPECTED_USER_TYPE=None):
        if not self._user_id:
            raise LambdaWebServiceException(HTTP_UNAUTHORIZED,
                                            message="this service requires user authentication")
        if EXPECTED_USER_TYPE:
            if (not self._user_type) or self._user_type not in EXPECTED_USER_TYPE:
                raise LambdaWebServiceException(
                    HTTP_UNAUTHORIZED,
                    message="this service requires user type to be " + EXPECTED_USER_TYPE)


def validate_request(request, request_schema):
    try:
        jsonschema.validate(request, request_schema)
    except jsonschema.ValidationError:
        logging.exception("exception in validating a service request")
        raise LambdaWebServiceException(HTTP_BAD_REQUEST, message="invalid request")


def validate_response(response, response_schema):
    try:
        jsonschema.validate(response, response_schema)
    except jsonschema.ValidationError:
        logging.exception("exception in validating a service response")
        raise LambdaWebServiceException(HTTP_INTERNAL_SERVER_ERROR, message="invalid response")


def validate_db_item(item, item_schema):
    try:
        jsonschema.validate(item, item_schema)
    except jsonschema.ValidationError:
        logging.exception("exception in validating a db item")
        raise LambdaWebServiceException(HTTP_INTERNAL_SERVER_ERROR, message="invalid db item")


def logging_configuration(app_level=logging.INFO, boto_level=logging.WARNING):
    logging.basicConfig(level=app_level)
    logging.getLogger('boto3').setLevel(boto_level)
    logging.getLogger('botocore').setLevel(boto_level)

