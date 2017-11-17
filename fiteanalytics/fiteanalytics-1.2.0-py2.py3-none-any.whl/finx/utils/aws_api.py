# *****************************************************
# * FinX is a set of tools for Financial Data Science *
# * Copyright (C) 2017  Fite Analytics LLC            *
# *****************************************************
#
# This file is part of FinX.
#
#     FinX is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     FinX is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with FinX.  If not, see <http://www.gnu.org/licenses/>.

import boto3
import botocore

def get_client():
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    return s3

def create_s3_bucket(bucket_name):
    s3 = get_client()
    s3.create_bucket(Bucket=bucket_name)
    return None

def upload_file_to_s3_bucket(file_name,bucket_name):
    s3 = get_client()
    s3.upload_file(file_name,bucket_name,file_name)
    return None

def fetch_file_from_s3_bucket(
    bucket_name,
    file_name,
    aws_access_key_id,
    aws_secret_access_key):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    try:
        s3.Bucket(bucket_name).download_file(file_name,file_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return 'object does not exist'
        else:
            return None
    return None

def get_bucket_acl(bucket_name):
    s3 = get_client()
    result = s3.get_bucket_acl(Bucket=bucket_name)
    return result

def get_bucket_policy(bucket_name):
    s3 = get_client()
    result = s3.get_bucket_policy(Bucket=bucket_name)
    return result

def set_simple_bucket_policy(bucket_name,bucket_policy_as_json_dump):
    # see s3 example bucket policies
    s3 = get_client()
    s3.put_bucket_policy(Bucket=bucket_name,Policy=bucket_policy_as_json_dump)
    return None

def delete_bucket_policy(bucket_name):
    s3 = get_client()
    s3.delete_bucket_policy(Bucket=bucket_name)
    return None

def make_bucket_website(bucket_name,website_configuration):
    s3 = get_client()
    s3.put_bucket_website(Bucket=bucket_name,WebsiteConfiguration=website_configuration)
    return None

def delete_bucket_website(bucket_name):
    s3 = get_client()
    s3.delete_bucket_website(Bucket=bucket_name)
    return None

VALID_FUNCTION_CALLS = ['create_s3_bucket',
                        'upload_file_to_s3_bucket',
                        'fetch_file_from_s3_bucket',
                        'get_bucket_acl',
                        'get_bucket_policy',
                        'set_simple_bucket_policy',
                        'delete_bucket_policy',
                        'make_bucket_website',
                        'delete_bucket_website']

def get_function_call_params(function_call=False, valid_function_calls=False):
    function_call_to_params_map = dict()
    for function_call_key in VALID_FUNCTION_CALLS:
        fun = inspect.getfullargspec(eval(function_call_key))
        params_list = list()
        if fun.args:
            no_default = 'no inspected default'
            fun_defaults = list(fun.defaults)
            fun_defaults = [no_default] * (len(fun.args) - len(fun.defaults)) + fun_defaults
            for param, default in zip(fun.args, fun_defaults):
                if default is not no_default:
                    param = '{} (default={})'.format(param, default)
                params_list.append(param)
            if fun.varargs:
              params_list.append('*' + fun.varargs)
            if fun.varkw:
              params_list.append('**' + fun.varkw)
        if fun.kwonlydefaults:
          params_list.append('*' + fun.varargs)
          parsed_kwonly = ['{} (defaults={})'.format(key, value)
                           for key, value in fun.kwonlydefaults.items()]
          params_list.extend(parsed_kwonly)
        if not fun.args and not fun.kwonlydefaults and fun.varargs:
            params_list.append('*' + fun.varargs)
        function_call_to_params_map[function_call_key] = params_list
    if bool(valid_function_calls):
        return list(function_call_to_params_map.keys())
    if bool(function_call):
        return function_call_to_params_map[function_call]

def help(*function_calls):
    print('-------------------------------------')
    print('fiteanalytics.finx.utils.aws_api help')
    print('-------------------------------------')
    print('Functions in this package are used to interact with Amazon AWS')
    print('Use these functions to send data to and from S3!')
    print('-------------------------------------')
    valid_function_calls = get_function_call_params(valid_function_calls=True)
    if not function_calls:
        print("\033[1mValid function calls are\033[0m:\n\t\t\t• {}"
              .format("\n\t\t\t• ".join(valid_function_calls[:])))
        function_calls = valid_function_calls
    for function_call in function_calls:
        try:
            params = get_function_call_params(function_call)
            if isinstance(params, tuple) or isinstance(params, list):
                print("Parameters for \033[1m{}\033[0m:\n\t\t\t• {}"
                      .format(function_call, "\n\t\t\t• ".join(params[:])))
            else:
                print("Parameters for \033[1m{}\033[0m:\n\t\t\t• {}"
                      .format(function_call, params))
        except:
            print("\033[1mValid function calls are\033[0m:\n\t\t\t• {}"
                  .format("\n\t\t\t• ".join(valid_function_calls[:])))
            return "error: function {} does not exist".format(function_call)
