from dateutil import parser
from collections import OrderedDict
from ._constants import TABLE_OUTPUT_TIME_FORMAT


# MLC transforms
def transform_mlc_resource(result_tuple):
    result, verb = result_tuple
    if result is None:
        return result
    if verb:
        return result
    to_print = {
        'Subscription': result['id'].split('/')[2],
        'Resource Group': result['id'].split('/')[4],
        'Cluster Name': result['name'],
        'Created On': result['created_on'],
        'Provisioning State': result['provisioning_state'],
        'Location': result['location'],
        'Cluster Size': result['container_service']['agent_count'] if 'container_service' in result.keys() else 'N/A'
    }
    if 'provisioning_errors' in result.keys() and result['provisioning_state'] == 'Failed':
        to_print['Provisioning Errors'] = result['provisioning_errors'][:250]
    if 'current_execution_mode' in result.keys():
        to_print['Current Mode'] = result['current_execution_mode']
    return to_print


def transform_mlc_resource_list(result_tuple):
    result_list, _ = result_tuple
    return [transform_mlc_resource((obj, False)) for obj in result_list]


# MMA transforms
def transform_mma_show(result_tuple):
    result, verb = result_tuple
    if 'resource_group' in result:
        del(result['resource_group'])
    return result


def table_transform_mma_show(result):
    return OrderedDict([('Name', result['name']),
                        ('Subscription', result['subscription']),
                        ('Resource Group', result['resourceGroup']),
                        ('Location', result['location']),
                        ('Created On', _convert_time(result['created_on']).strftime(TABLE_OUTPUT_TIME_FORMAT))])


def transform_mma_list(result_tuple):
    result_list, verb = result_tuple
    if verb:
        for result in result_list:
            if 'resource_group' in result:
                del(result['resource_group'])
        return result_list
    return [_transform_mma_list(result) for result in result_list]


def _transform_mma_list(result):
    if 'resource_group' in result:
        del(result['resource_group'])
    return result


def table_transform_mma_list(result_list):
    return [_table_transform_mma_list(result) for result in result_list]


def _table_transform_mma_list(result):
    return OrderedDict([('Name', result['name']),
                        ('Subscription', result['subscription']),
                        ('Resource Group', result['resourceGroup']),
                        ('Location', result['location']),
                        ('Created On', _convert_time(result['created_on']).strftime(TABLE_OUTPUT_TIME_FORMAT))])


# Model result transforms
def transform_model_show(result_tuple):
    result, verb = result_tuple
    if verb:
        return result
    if type(result) is list:
        return [transform_model_show((model, False)) for model in result]
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'Version': result['Version'],
        'CreatedAt': result['CreatedAt'],
        'Tags': ', '.join(result['Tags']) if result['Tags'] else ' ',
        'Description': result['Description'] or ' '
    }


def table_transform_model_show(result):
    if type(result) is list:
        return [table_transform_model_show(model) for model in result]
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('Version', result['Version']),
                        ('CreatedAt', _convert_time(result['CreatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('Tags', ', '.join(result['Tags']) if result['Tags'] else ' ')])


def transform_model_list(result_tuple):
    result_list, verb = result_tuple
    if verb:
        return result_list
    return [_transform_model_list(result) for result in result_list]


def _transform_model_list(result):
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'Version': result['Version'],
        'CreatedAt': result['CreatedAt']
    }


def table_transform_model_list(result_list):
    return [_table_transform_model_list(result) for result in result_list]


def _table_transform_model_list(result):
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('Version', result['Version']),
                        ('CreatedAt', _convert_time(result['CreatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT))])


# Manifest result transforms
def transform_manifest_show(result_tuple):
    result, verb = result_tuple
    if verb:
        return result
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'Version': result['Version'],
        'CreatedTime': result['CreatedTime'],
        'Runtime': result['TargetRuntime']['RuntimeType'],
        'WebserviceType': result['WebserviceType'],
        'Description': result['Description'] or ' ',
        'ModelIds': result['ModelIds']
    }


def table_transform_manifest_show(result):
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('Version', result['Version']),
                        ('CreatedTime', _convert_time(result['CreatedTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('WebserviceType', result['WebserviceType'])])


def transform_manifest_list(result_tuple):
    result_list, verb = result_tuple
    if verb:
        return result_list
    return[_transform_manifest_list(result) for result in result_list]


def _transform_manifest_list(result):
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'Version': result['Version'],
        'CreatedTime': result['CreatedTime']
    }


def table_transform_manifest_list(result_list):
    return[_table_transform_manifest_list(result) for result in result_list]


def _table_transform_manifest_list(result):
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('Version', result['Version']),
                        ('CreatedTime', _convert_time(result['CreatedTime']).strftime(TABLE_OUTPUT_TIME_FORMAT))])


# Image result transforms
def transform_image_show(result_tuple):
    result, verb = result_tuple
    if verb:
        return result
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'Version': result['Version'],
        'CreatedTime': result['CreatedTime'],
        'CreationState': result['CreationState'],
        'Description': result['Description'] or ' ',
        'Manifest_Name': result['Manifest']['Name'],
        'Manifest_Version': result['Manifest']['Version']
    }


def table_transform_image_show(result):
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('Version', result['Version']),
                        ('CreatedTime', _convert_time(result['CreatedTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('CreationState', result['CreationState'])])


def transform_image_list(result_tuple):
    result_list, verb = result_tuple
    if verb:
        return result_list
    return[_transform_image_list(result) for result in result_list]


def _transform_image_list(result):
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'Version': result['Version'],
        'CreatedTime': result['CreatedTime'],
        'CreationState': result['CreationState']
    }


def table_transform_image_list(result_list):
    return[_table_transform_image_list(result) for result in result_list]


def _table_transform_image_list(result):
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('Version', result['Version']),
                        ('CreatedTime', _convert_time(result['CreatedTime']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('CreationState', result['CreationState'])])


# Service result transforms
def transform_service_show(result_tuple):
    result, verb = result_tuple
    if verb or not result:
        return result
    if type(result) is list:
        return [transform_service_show((service, False)) for service in result]
    model_names_versions = ['{} [Ver. {}]'.format(model['Name'], model['Version']) for model in result['Models']]
    model_names_versions = ', '.join(model_names_versions)
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'UpdatedAt': result['UpdatedAt'],
        'Service_Type': result['Image']['Manifest']['WebserviceType'],
        'Models': model_names_versions,
        'Manifest_Name': result['Image']['Manifest']['Name'],
        'Manifest_Version': result['Image']['Manifest']['Version'],
        'Image_URL': result['Image']['ImageLocation'],
        'State': result['State']
    }


def table_transform_service_show(result):
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('UpdatedAt', _convert_time(result['UpdatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('State', result['State'])])


def transform_service_list(result_tuple):
    result_list, verb = result_tuple
    if verb:
        return result_list
    return[_transform_service_list(result) for result in result_list]


def _transform_service_list(result):
    return {
        'Name': result['Name'],
        'Id': result['Id'],
        'UpdatedAt': result['UpdatedAt'],
        'Service_Type': result['Image']['Manifest']['WebserviceType'],
        'State': result['State']
    }


def table_transform_service_list(result_list):
    return [_table_transform_service_list(result) for result in result_list]


def _table_transform_service_list(result):
    return OrderedDict([('Name', result['Name']),
                        ('Id', result['Id']),
                        ('UpdatedAt', _convert_time(result['UpdatedAt']).strftime(TABLE_OUTPUT_TIME_FORMAT)),
                        ('State', result['State'])])


def _convert_time(time_str):
    time_obj = parser.parse(time_str)
    time_obj = time_obj.replace(microsecond=0, tzinfo=None)
    return time_obj
