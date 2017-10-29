#!/usr/bin/env python

import logging
import json
import boto3
import random
import string
import re


def create_bucket(bucket_name, region, acl="private"):
    s3 = boto_client('s3')
    logging.info("[STARTING] creation of bucket %s in region %s with acl: %s", bucket_name, region, acl)
    try:
        resp = s3.create_bucket(ACL=acl, Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
        logging.info("[COMPLETED] creation of bucket %s in region %s with acl: %s", bucket_name, resp['Location'], acl)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        logging.info("[COMPLETED] creation of bucket %s - already created", bucket_name)


def set_bucket_for_website(bucket_name):
    logging.info("[STARTING] setting bucket %s for website", bucket_name)
    s3 = boto_client('s3')
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
    logging.info("[COMPLETED] setting bucket %s for website", bucket_name)


def add_user_to_group(username, group_name):
    logging.info("[STARTING] adding user %s to group %s", username, group_name)
    iam = boto_client("iam")
    iam.add_user_to_group(GroupName=group_name, UserName=username)
    logging.info("[DONE] adding user %s to group %s", username, group_name)


def create_user_with_credentials_and_key(username, output_path):
    iam = boto_client('iam')
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


def create_or_update_iam_managed_policy(policy_arn, policy_name, policy_dict):
    policy_str = json.dumps(policy_dict)
    iam = boto_client('iam')
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


def create_iam_group(group_name):
    iam = boto_resource('iam')
    group = iam.Group(group_name)
    try:
        group_arn = group.arn
        logging.info("the group %s already exists", group_name)
    except iam.meta.client.exceptions.NoSuchEntityException:
        logging.info("[STARTING] the group %s does not exists - creating it", group_name)
        group.create()
        logging.info("[COMPLETED] group %s created", group_name)


def attach_policy_to_group(group_name, policy_arn):
    logging.info("[STARTING] attaching policy %s to group %s", policy_arn, group_name)
    iam = boto_client('iam')
    iam.attach_group_policy(GroupName=group_name, PolicyArn=policy_arn)
    attached_policies = iam.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']
    logging.info("group %s has policies: %s", group_name, ", ".join([p['PolicyName'] for p in attached_policies]))
    logging.info("[COMPLETED] attaching policy %s to group %s", policy_arn, group_name)


def get_account_id():
    account_id = boto_resource('iam').CurrentUser().arn.split(':')[4]
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
def compose_admin_policy(account_id, project_name, stage):
    return {
        "Version": "2012-10-17",
        "Statement": [
            compose_statement("iam", "", account_id, "user/${aws:username}"),
            # compose_statement("iam", "", account_id, "role/DynamoDBAutoscaleRole"),
            compose_statement("iam", "", account_id, "role/" + compose_name(project_name, stage, "*")),
            compose_statement("dynamodb", "*", account_id, "table/" + compose_name(project_name, stage, "*")),

            compose_statement("s3", "", "", "*", actions="s3:ListAllMyBuckets"),
            compose_statement("s3", "", "", compose_bucket_name(project_name, stage, "Frontend")),
            compose_statement("s3", "", "", compose_bucket_name(project_name, stage, "User_Data")),
            compose_statement("s3", "", "", compose_bucket_name(project_name, stage, "Backend")),
            compose_statement("s3", "", "", compose_bucket_name(project_name, stage, "Frontend")+"/*"),
            compose_statement("s3", "", "", compose_bucket_name(project_name, stage, "User_Data")+"/*"),
            compose_statement("s3", "", "", compose_bucket_name(project_name, stage, "Backend")+"/*"),
            compose_statement("lambda", "*", account_id, "function:" + compose_name(project_name, stage, "*")),
            compose_statement("apigateway", "*", "", "function:" + compose_name(project_name, stage, "*")),

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


def boto_client(aws_service):
    session = boto3.Session(profile_name='admin')
    return session.client(aws_service)


def boto_resource(aws_service):
    session = boto3.Session(profile_name='admin')
    return session.resource(aws_service)


def compose_bucket_name(project_name, stage, name):
    invalid_name = compose_name(project_name, stage, name)
    dotted = re.sub("[^A-Za-z0-9]", "-", invalid_name)
    return ".".join([s.lower() for s in dotted.split("-")])


def compose_name(project_name, stage, name):
    return "_".join([project_name, stage, name])
