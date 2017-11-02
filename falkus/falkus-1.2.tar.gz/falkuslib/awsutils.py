#!/usr/bin/env python

import logging
import json
import random
import string

from lws import STAGE_LOCAL

ACTION_READ = "read"
ACTION_UPDATE = "update"

TYPE_COGNITO_USER_POOL = "cognito_user_pool"
TYPE_COGNITO_USER_POOL_CLIENT = "cognito_user_pool_client"
TYPE_COGNITO_IDENTITY_POOL = "cognito_identity_pool"
TYPE_DYNAMODB_TABLE = "dynamodb_table"

RESOURCE_TYPES = [TYPE_COGNITO_USER_POOL, TYPE_COGNITO_USER_POOL_CLIENT,  TYPE_COGNITO_IDENTITY_POOL]


def aws_resource_processor(botoFactory, action, resource, variables):
    return {
        TYPE_COGNITO_USER_POOL: user_pool_processor,
        TYPE_COGNITO_USER_POOL_CLIENT: user_pool_client_processor,
        TYPE_COGNITO_IDENTITY_POOL: identity_pool_processor,
        TYPE_DYNAMODB_TABLE: dynamodb_table_processor
    }[resource["type"]](botoFactory, action, resource, variables)
                        #variables["project_name"], variables["stage"], variables["region"])


def dynamodb_table_processor(botoFactory, action, resource, variables):
    logging.info("[starting] create table")
    args = resource["args"]
    stdname = args['TableName']
    name_for_stage = botoFactory.format_name(stdname)
    args['TableName'] = name_for_stage
    ddb = botoFactory.client('dynamodb')
    try:
        table = ddb.describe_table(TableName=args['TableName'])
    except ddb.exceptions.ResourceNotFoundException:
        table = None
    if action == ACTION_UPDATE:
        if not table:
            logging.info("the table %s does not exist yet. Creating one", args['TableName'])
            ddb.create_table(**args)
        else:
            logging.warning("table %s NOT created because it was already defined. "
                            "If there is any update, it will be IGNORED.", args['TableName'])
    variables[resource["name"]] = {"TableName":args['TableName']}
    return variables


def user_pool_processor(botoFactory, action, resource, variables):
    if(botoFactory.get_stage() == STAGE_LOCAL):
        logging.info("user pool resources not supported in local execution")
        return variables
    userpool_args = resource["args"]
    stdname = userpool_args['PoolName']
    name_for_stage = botoFactory.format_name(stdname)
    userpool_args['PoolName'] = name_for_stage
    cognito_idp = botoFactory.client('cognito-idp')
    pool = get_user_pool(botoFactory, name_for_stage)
    if action == ACTION_UPDATE:
        if not pool:
            logging.info("the user pool does not exist yet. Creating one")
            cognito_idp.create_user_pool(**userpool_args)
            pool = get_user_pool(botoFactory, name_for_stage)
        else:
            logging.info("Found user pool %s - updating", pool["Id"])
            userpool_args.pop('PoolName')
            userpool_args.pop('AliasAttributes')
            userpool_args['UserPoolId'] = pool["Id"]
            cognito_idp.update_user_pool(**userpool_args)
    if pool:
        variables[resource["name"]] = {
            "Id": pool["Id"],
            "ARN": "arn:aws:cognito-idp:{}:{}:userpool/{}".format(
                variables["region"], variables["account_id"], pool["Id"]),
            "ProviderName": "cognito-idp.{}.amazonaws.com/{}".format(variables["region"], pool["Id"])
        }
    return variables


def user_pool_client_processor(botoFactory, action, resource, variables):
    if (botoFactory.get_stage() == STAGE_LOCAL):
        logging.info("user pool resources not supported in local execution")
        return variables
    cognito_idp = botoFactory.client('cognito-idp')
    client_args = resource["args"]
    client_name = client_args["ClientName"]
    client = get_user_pool_client(botoFactory, client_args["UserPoolId"], client_name)
    if action == ACTION_UPDATE:
        if not client:
            logging.info("client not found, creating it")
            cognito_idp.create_user_pool_client(**client_args)
        else:
            logging.info("found client - updating")
            client_args["ClientId"] = client["ClientId"]
            client_args.pop("GenerateSecret")
            cognito_idp.update_user_pool_client(**client_args)
    if client:
        variables[resource["name"]] = {
            "ClientId": client["ClientId"],
            "UserPoolId": client["UserPoolId"]
        }
    return variables

# TODO: missing "add ROLE": you need to create a role manually or the login won't work
# https://serverless-stack.com/chapters/create-a-cognito-identity-pool.html
#
def identity_pool_processor(botoFactory, action, resource, variables):
    if (botoFactory.get_stage() == STAGE_LOCAL):
        logging.info("identity pool resources not supported in local execution")
        return variables
    cognito = botoFactory.client('cognito-identity')
    ipool_args = resource["args"]
    stdname = ipool_args['IdentityPoolName']
    name_for_stage = botoFactory.format_name(stdname)
    ipool_args['IdentityPoolName'] = name_for_stage
    pool = get_identity_pool(botoFactory, name_for_stage)
    if action == ACTION_UPDATE:
        if not pool:
            logging.info("the identity pool does not exist yet. Creating one")
            cognito.create_identity_pool(**ipool_args)
            pool = get_identity_pool(botoFactory, name_for_stage)
        else:
            logging.info("Found identity pool %s - updating", pool["IdentityPoolId"])
            ipool_args['IdentityPoolId'] = pool["IdentityPoolId"]
            cognito.update_identity_pool(**ipool_args)
    if pool:
        variables[resource["name"]] = {
            "IdentityPoolId": pool["IdentityPoolId"],
        }


def create_user_pool(botoFactory, userpool_struct):
    if (botoFactory.get_stage() == STAGE_LOCAL):
        logging.info("user pool resources not supported in local execution")
        return
    userpool_args = userpool_struct["args"]
    stdname = userpool_args['PoolName']
    name_for_stage = botoFactory.format_name(stdname)
    userpool_args['PoolName'] = name_for_stage
    cognito_idp = botoFactory.client('cognito-idp')

    pool = get_user_pool(botoFactory, name_for_stage)
    if not pool:
        logging.info("the user pool does not exist yet. Creating one")
        cognito_idp.create_user_pool(**userpool_args)
        pool = get_user_pool(botoFactory, name_for_stage)
    else:
        logging.info("Found user pool %s - updating", pool["Id"])
        userpool_args.pop('PoolName')
        userpool_args.pop('AliasAttributes')
        userpool_args['UserPoolId'] = pool["Id"]
        cognito_idp.update_user_pool(**userpool_args)

    if "client" in userpool_struct:
        client_args = userpool_struct["client"]
        client_args["UserPoolId"] = pool["Id"]
        client_name = client_args["ClientName"]
        client = get_user_pool_client(botoFactory, pool["Id"], client_name)
        if not client:
            logging.info("client not found, creating it")
            cognito_idp.create_user_pool_client(**client_args)
        else:
            logging.info("found client - updating")
            client_args["ClientId"] = client["ClientId"]
            client_args.pop("GenerateSecret")
            cognito_idp.update_user_pool_client(**client_args)


def get_identity_pool(botoFactory, pool_name):
    cognito = botoFactory.client('cognito-identity')
    pools = [pool
             for pool in scan_paginate_result(cognito.list_identity_pools, {}, keyToExplode='IdentityPools')
             if pool['IdentityPoolName'] == pool_name]
    if len(pools) == 0:
        return None
    elif len(pools) == 1:
        return pools[0]
    else:
        logging.error("Found multiple pools named %s - you need to remove the duplicate manually")
        raise Exception("Invalid AWS state - found duplicated pools")


def get_user_pool(botoFactory, pool_name):
    cognito_idp = botoFactory.client('cognito-idp')
    pools = [pool
             for pool in scan_paginate_result(cognito_idp.list_user_pools, {}, keyToExplode='UserPools')
             if pool['Name'] == pool_name]
    if len(pools) == 0:
        return None
    elif len(pools) == 1:
        return pools[0]
    else:
        logging.error("Found multiple pools named %s - you need to remove the duplicate manually")
        raise Exception("Invalid AWS state - found duplicated pools")


def get_user_pool_client(botoFactory, pool_id, client_name):
    cognito_idp = botoFactory.client('cognito-idp')
    results = [client
                for client in scan_paginate_result(cognito_idp.list_user_pool_clients, {"UserPoolId":pool_id},
                                                   keyToExplode='UserPoolClients')
             if client['ClientName'] == client_name]
    if len(results) == 0:
        return None
    elif len(results) == 1:
        return results[0]
    else:
        logging.error("Found multiple pools named %s - you need to remove the duplicate manually")
        raise Exception("Invalid AWS state - found duplicated pools")


def scan_paginate_result(callback, args, MaxResults=20, keyToExplode=None):
    NextToken=None
    while True:
        if NextToken:
            resp = callback(MaxResults=MaxResults, NextToken=NextToken, **args)
        else:
            resp = callback(MaxResults=MaxResults, **args)
        if not keyToExplode:
            yield resp
        else:
            for el in resp[keyToExplode]:
                yield el
        if "NextToken" in resp:
            NextToken = resp["NextToken"]
        else:
            return


def create_bucket(botoFactory, bucket_name, acl="private"):
    s3 = botoFactory.client('s3')
    logging.info("[STARTING] creation of bucket %s in region %s with acl: %s", bucket_name, botoFactory.get_region(), acl)
    try:
        resp = s3.create_bucket(ACL=acl, Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': botoFactory.get_region()})
        logging.info("[COMPLETED] creation of bucket %s %s with acl: %s", bucket_name, resp['Location'], acl)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        logging.info("[COMPLETED] creation of bucket %s - already created", bucket_name)


def set_bucket_for_website(botoFactory, bucket_name):
    logging.info("[STARTING] setting bucket %s for website", bucket_name)
    s3 = botoFactory.client('s3')
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'IndexDocument': {
                'Suffix': 'index.html'
            },
            'ErrorDocument': {
                'Key': 'index.html'
            }
        }
    )
    s3.put_bucket_policy(Bucket=bucket_name,
                         Policy=json.dumps(compose_s3_website_bucket_policy(bucket_name)))
    logging.info("[COMPLETED] setting bucket %s for website", bucket_name)


def add_user_to_group(botoFactory, username, group_name):
    logging.info("[STARTING] adding user %s to group %s", username, group_name)
    iam = botoFactory.client("iam")
    iam.add_user_to_group(GroupName=group_name, UserName=username)
    logging.info("[DONE] adding user %s to group %s", username, group_name)


def create_user_with_credentials_and_key(botoFactory, username, output_path):
    iam = botoFactory.client('iam')
    try:
        logging.info("[STARTING] user creation %s", username)
        iam.create_user(UserName=username)
        logging.info("[COMPLETED] user creation %s", username)
    except iam.exceptions.EntityAlreadyExistsException:
        logging.info("[COMPLETED] user creation %s - user already existed", username)
    logging.info("[STARTING] access key creation for %s", username)
    access_keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
    if access_keys:
        logging.info("[COMPLETED] access key creation for %s - already existed", username)
    else:
        output_file_path = output_path + "/credentials_{}".format(username)
        with open(output_file_path, "w") as output_file:
            output_file.write("test access - making sure I can save the credentials")
        ak = iam.create_access_key(UserName=username)['AccessKey']
        ak_str = "[{}]\naws_access_key_id={}\naws_secret_access_key={}\n".format(
            "default", ak['AccessKeyId'], ak['SecretAccessKey']
        )
        with open(output_file_path, "w") as output_file:
            output_file.write(ak_str)
        logging.info("[COMPLETED] access key creation for %s - saved in %s", username, output_file_path)

    logging.info("[STARTING] creating password for %s to access the AWS console", username)
    try:
        iam.get_login_profile(UserName=username)['LoginProfile']
        logging.info("[COMPLETED] creating password for %s to access the AWS console - already existed", username)
    except (KeyError, iam.exceptions.NoSuchEntityException):
        output_file_path = output_path + "/temp_password_{}".format(username)
        new_password = generate_password()
        with open(output_file_path, "w") as output_file:
            output_file.write(new_password)
        iam.create_login_profile(UserName=username, Password=new_password, PasswordResetRequired=True)
        logging.info("[COMPLETED] creating password for %s to access the AWS console - saved in %s",
                     username, output_file_path)


def generate_password(size=8, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_or_update_iam_managed_policy(botoFactory, policy_arn, policy_name, policy_dict):
    policy_str = json.dumps(policy_dict)
    iam = botoFactory.client('iam')
    try:
        iam.create_policy(PolicyName=policy_name, PolicyDocument=policy_str)
        logging.info("created policy %s", policy_name)
    except iam.exceptions.EntityAlreadyExistsException:
        iam.create_policy_version(PolicyArn=policy_arn, PolicyDocument=policy_str, SetAsDefault=True)
        logging.info("created new default policy version for policy %s", policy_name)
        for v in iam.list_policy_versions(PolicyArn=policy_arn)['Versions']:
            if not v["IsDefaultVersion"]:
                iam.delete_policy_version(PolicyArn=policy_arn, VersionId=v['VersionId'])
                logging.info("removed old policy version %s %s", policy_name, v['VersionId'])


def create_iam_group(botoFactory, group_name):
    iam = botoFactory.resource('iam')
    group = iam.Group(group_name)
    try:
        group_arn = group.arn
        logging.info("the group %s already exists", group_name)
    except iam.meta.client.exceptions.NoSuchEntityException:
        logging.info("[STARTING] the group %s does not exists - creating it", group_name)
        group.create()
        logging.info("[COMPLETED] group %s created", group_name)


def attach_policy_to_group(botoFactory, group_name, policy_arn):
    logging.info("[STARTING] attaching policy %s to group %s", policy_arn, group_name)
    iam = botoFactory.client('iam')
    iam.attach_group_policy(GroupName=group_name, PolicyArn=policy_arn)
    attached_policies = iam.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']
    logging.info("group %s has policies: %s", group_name, ", ".join([p['PolicyName'] for p in attached_policies]))
    logging.info("[COMPLETED] attaching policy %s to group %s", policy_arn, group_name)


def get_account_id(botoFactory):
    account_id = botoFactory.resource('iam').CurrentUser().arn.split(':')[4]
    logging.info("the current account id is %s", account_id)
    return account_id


def set_boto_logging_level(boto_level=logging.WARNING):
    logging.getLogger('boto3').setLevel(boto_level)
    logging.getLogger('botocore').setLevel(boto_level)


def compose_policy_arn(account_id, policy_name):
    return "arn:aws:iam::{}:policy/{}".format(account_id, policy_name)


# TODO: give Autoscaling role / permissions
# http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/AutoScaling.Console.html#AutoScaling.Permissions
# http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/AutoScaling.CLI.html
# https://forums.aws.amazon.com/thread.jspa?messageID=798577
def compose_admin_policy(botoFactory, account_id, project_name, stage):
    return {
        "Version": "2012-10-17",
        "Statement": [
            compose_statement("iam", "", account_id, "user/${aws:username}"),
            # compose_statement("iam", "", account_id, "role/DynamoDBAutoscaleRole"),
            compose_statement("iam", "", account_id, "role/" + botoFactory.format_name("*")),
            compose_statement("dynamodb", "*", account_id, "table/" + botoFactory.format_name("*")),

            compose_statement("s3", "", "", "*", actions="s3:ListAllMyBuckets"),
            compose_statement("s3", "", "", botoFactory.format_bucket_name("Frontend")),
            compose_statement("s3", "", "", botoFactory.format_bucket_name("User_Data")),
            compose_statement("s3", "", "", botoFactory.format_bucket_name("Backend")),
            compose_statement("s3", "", "", botoFactory.format_bucket_name("Frontend")+"/*"),
            compose_statement("s3", "", "", botoFactory.format_bucket_name("User_Data")+"/*"),
            compose_statement("s3", "", "", botoFactory.format_bucket_name("Backend")+"/*"),
            compose_statement("lambda", "*", account_id, "function:" + botoFactory.format_name("*")),
            compose_statement("apigateway", "*", "", "function:" + botoFactory.format_name("*")),

            compose_statement("cognito-idp", "*", account_id, "userpool/*"),
            compose_statement("cognito-identity", "*", account_id, "identitypool/*"),
            compose_statement("cognito-sync", "*", account_id, "identitypool/*"),
            compose_statement("lambda", "*", account_id, "event-source-mappings:*"),
            {"Action": ["iam:PassRole"], "Effect": "Allow", "Resource": "*",
             "Condition": {"StringLike": {
                "iam:PassedToService": ["application-autoscaling.amazonaws.com", "dax.amazonaws.com"]
            }}}
        ]
    }

#  API Gateway / CloudFormation / CloudFront / CloudWatch / SES / SQS


def compose_statement(aws_service, region, account_id, path, actions="*"):
    return {"Effect": "Allow", "Action": actions,
            "Resource": "arn:aws:{}:{}:{}:{}".format(aws_service, region, account_id, path)}


def compose_s3_website_bucket_policy(bucket_name):
    return {
          "Version":"2012-10-17",
          "Statement":[{
            "Sid":"PublicReadForGetBucketObjects",
                "Effect":"Allow",
              "Principal": "*",
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::{}/*".format(bucket_name)]
            }
          ]
        }
