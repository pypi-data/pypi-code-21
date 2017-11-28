# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import uuid
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from azure.storage.blob import BlobPermissions
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from .model import _model_register
from ._util import TraversalFunction
from ._ml_cli_error import MlCliError

manifest_show_header_to_fn_dict = OrderedDict([('Name', TraversalFunction(('Name',))),
                                               ('Version', TraversalFunction(('Version',))),
                                               ('Id', TraversalFunction(('Id',))),
                                               ('Description', TraversalFunction(('Description',))),
                                               ('Target_Runtime', TraversalFunction(('TargetRuntime',))),
                                               ('Model_Ids', TraversalFunction(('ModelIds',)))])


def handle_model_files(model_ids, model_files, verb, context):
    if model_ids:
        model_info = model_ids
    elif model_files:
        model_info = []
        for model_file in model_files:
            model_name = os.path.basename(model_file.rstrip(os.sep))
            model_create_status, model_id = _model_register(model_file, model_name, None, None, verb, context)
            model_info.append(model_id)
    else:
        return None

    return model_info


def handle_driver_file(driver_file, verb, context):
    if os.path.isfile(driver_file):
        with open(driver_file, 'r') as scorefile:
            code = scorefile.read()
    else:
        raise MlCliError("Error: No such file {}".format(driver_file))

    az_container_name = 'amlbdpackages'
    az_blob_name = str(uuid.uuid4()) + '.py'
    bbs = BlockBlobService(account_name=context.az_account_name,
                           account_key=context.az_account_key)
    bbs.create_container(az_container_name)
    bbs.create_blob_from_text(az_container_name, az_blob_name, code,
                              content_settings=ContentSettings(content_type='application/text'))
    blob_sas = bbs.generate_blob_shared_access_signature(
        az_container_name,
        az_blob_name,
        BlobPermissions.READ,
        datetime.utcnow() + timedelta(days=30))
    upload_location = 'http://{}.blob.core.windows.net/{}/{}?{}'.format(context.az_account_name,
                                                                        az_container_name, az_blob_name, blob_sas)

    if verb:
        print("Driver uploaded to " + upload_location)

    return upload_location


def upload_runtime_properties_file(file_path, context):
    az_container_name = 'amlbdpackages'
    az_blob_name = os.path.basename(file_path)
    location = context.upload_dependency_to_azure_blob(file_path, az_container_name, az_blob_name)
    return location
