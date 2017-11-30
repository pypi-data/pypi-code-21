import datetime
import json
import os
import time
import dateutil
import sys
import uuid
from dateutil.relativedelta import relativedelta

from msrestazure.azure_exceptions import CloudError
from azure.cli.core.util import shell_safe_json_parse
from azure.cli.core._profile import Profile
from azure.graphrbac.models import (ApplicationCreateParameters,
                                    PasswordCredential,
                                    KeyCredential,
                                    ServicePrincipalCreateParameters)
from azure.mgmt.authorization.models import RoleAssignmentProperties
from azure.cli.core._environment import get_config_dir
from ._ml_cli_error import MlCliError

service_principal_path = os.path.join(get_config_dir(), 'acsServicePrincipal.json')


def _auth_client_factory(scope=None):
    import re
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.authorization import AuthorizationManagementClient
    subscription_id = None
    if scope:
        matched = re.match('/subscriptions/(?P<subscription>[^/]*)/', scope)
        if matched:
            subscription_id = matched.groupdict()['subscription']
    return get_mgmt_service_client(AuthorizationManagementClient,
                                   subscription_id=subscription_id)


def validate_service_principal(service_principal, client_secret):
    if service_principal:
        # --service-principal specfied, validate --client-secret was too
        if not client_secret:
            raise MlCliError('--client-secret is required if --service-principal is specified')
        _, subscription_id, _ = Profile().get_login_credentials(subscription_id=None)
        client = _graph_client_factory()
        _validate_service_principal(client, service_principal)


def _graph_client_factory(**_):
    from azure.cli.core._profile import Profile, CLOUD
    from azure.cli.core.commands.client_factory import configure_common_settings
    from azure.graphrbac import GraphRbacManagementClient
    profile = Profile()
    cred, _, tenant_id = profile.get_login_credentials(
        resource=CLOUD.endpoints.active_directory_graph_resource_id)
    client = GraphRbacManagementClient(cred,
                                       tenant_id,
                                       base_url=CLOUD.endpoints.active_directory_graph_resource_id)
    configure_common_settings(client)
    return client


def _resolve_role_id(role, scope, definitions_client):
    role_id = None
    try:
        uuid.UUID(role)
        role_id = role
    except ValueError:
        pass
    if not role_id:  # retrieve role id
        role_defs = list(definitions_client.list(scope, "roleName eq '{}'".format(role)))
        if not role_defs:
            raise MlCliError("Role '{}' doesn't exist.".format(role))
        elif len(role_defs) > 1:
            ids = [r.id for r in role_defs]
            err = "More than one role matches the given name '{}'. Please pick a value from '{}'"
            raise MlCliError(err.format(role, ids))
        role_id = role_defs[0].id
    return role_id


def _get_object_stubs(graph_client, assignees):
    from azure.graphrbac.models.get_objects_parameters import GetObjectsParameters
    params = GetObjectsParameters(include_directory_object_references=True,
                                  object_ids=assignees)
    return list(graph_client.objects.get_objects_by_object_ids(params))


def _resolve_object_id(assignee):
    client = _graph_client_factory()
    result = None
    if assignee.find('@') >= 0:  # looks like a user principal name
        result = list(
            client.users.list(filter="userPrincipalName eq '{}'".format(assignee)))
    if not result:
        result = list(client.service_principals.list(
            filter="servicePrincipalNames/any(c:c eq '{}')".format(assignee)))
    if not result:  # assume an object id, let us verify it
        result = _get_object_stubs(client, [assignee])

    # 2+ matches should never happen, so we only check 'no match' here
    if not result:
        raise MlCliError("No matches in graph database for '{}'".format(assignee))

    return result[0].object_id


def _build_role_scope(resource_group_name, scope, subscription_id):
    subscription_scope = '/subscriptions/' + subscription_id
    if scope:
        if resource_group_name:
            err = 'Resource group "{}" is redundant because scope is supplied'
            raise MlCliError(err.format(resource_group_name))
    elif resource_group_name:
        scope = subscription_scope + '/resourceGroups/' + resource_group_name
    else:
        scope = subscription_scope
    return scope


def create_role_assignment(role, assignee, resource_group_name=None, scope=None):
    return _create_role_assignment(role, assignee, resource_group_name, scope)


def _create_role_assignment(role, assignee, resource_group_name=None, scope=None,
                            # pylint: disable=too-many-arguments
                            resolve_assignee=True):
    factory = _auth_client_factory(scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions

    scope = _build_role_scope(resource_group_name, scope,
                              assignments_client.config.subscription_id)

    role_id = _resolve_role_id(role, scope, definitions_client)
    object_id = _resolve_object_id(assignee) if resolve_assignee else assignee
    properties = RoleAssignmentProperties(role_id, object_id)
    assignment_name = uuid.uuid4()
    custom_headers = None
    return assignments_client.create(scope, assignment_name, properties,
                                     custom_headers=custom_headers)


def _add_role_assignment(role, service_principal, delay=2, output=True):
    # AAD can have delays in propagating data, so sleep and retry
    if output:
        sys.stdout.write('waiting for AAD role to propagate.')
    for x in range(0, 10):
        try:
            # TODO: break this out into a shared utility library
            create_role_assignment(role, service_principal)
            break
        except CloudError as ex:
            if ex.message == 'The role assignment already exists.':
                break
            print('%s', ex.message)
        except:  # pylint: disable=bare-except
            pass
        if output:
            sys.stdout.write('.')
            time.sleep(delay + delay * x)
    else:
        return False
    if output:
        print('done')
    return True


def store_acs_service_principal(subscription_id, client_secret, service_principal,
                                config_path=service_principal_path):
    obj = {}
    if client_secret:
        obj['client_secret'] = client_secret
    if service_principal:
        obj['service_principal'] = service_principal

    fullConfig = load_acs_service_principals(config_path=config_path)
    if not fullConfig:
        fullConfig = {}
    fullConfig[subscription_id] = obj

    with os.fdopen(os.open(config_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600),
                   'w+') as spFile:
        json.dump(fullConfig, spFile)


def load_acs_service_principal(subscription_id,
                               config_path=service_principal_path):
    config = load_acs_service_principals(config_path)
    if not config:
        return None
    return config.get(subscription_id)


def _build_service_principal(client, name, url, client_secret):
    sys.stdout.write('creating service principal')
    result = create_application(client.applications, name, url, [url],
                                password=client_secret)
    service_principal = result.app_id  # pylint: disable=no-member
    for x in range(0, 10):
        try:
            create_service_principal(service_principal)
        # TODO figure out what exception AAD throws here sometimes.
        except:  # pylint: disable=bare-except
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(2 + 2 * x)
    print('done')
    return service_principal


def create_service_principal(identifier):
    return _create_service_principal(identifier)


def _create_service_principal(identifier, resolve_app=True):
    client = _graph_client_factory()

    if resolve_app:
        try:
            uuid.UUID(identifier)
            result = list(client.applications.list(filter="appId eq '{}'".format(identifier)))
        except ValueError:
            result = list(client.applications.list(
                filter="identifierUris/any(s:s eq '{}')".format(identifier)))

        if not result:  # assume we get an object id
            result = [client.applications.get(identifier)]
        app_id = result[0].app_id
    else:
        app_id = identifier

    return client.service_principals.create(ServicePrincipalCreateParameters(app_id, True))


def _build_application_creds(password=None, key_value=None, key_type=None,
                             # pylint: disable=too-many-arguments
                             key_usage=None, start_date=None, end_date=None):
    if password and key_value:
        raise MlCliError('specify either --password or --key-value, but not both.')
    if not start_date:
        start_date = datetime.datetime.utcnow()
    elif isinstance(start_date, str):
        start_date = dateutil.parser.parse(start_date)

    if not end_date:
        end_date = start_date + relativedelta(years=1)
    elif isinstance(end_date, str):
        end_date = dateutil.parser.parse(
            end_date)  # pylint: disable=redefined-variable-type

    key_type = key_type or 'AsymmetricX509Cert'
    key_usage = key_usage or 'Verify'

    password_creds = None
    key_creds = None
    if password:
        password_creds = [
            PasswordCredential(start_date, end_date, str(uuid.uuid4()), password)]
    elif key_value:
        key_creds = [KeyCredential(start_date, end_date, key_value, str(uuid.uuid4()),
                                   key_usage, key_type)]

    return (password_creds, key_creds)


def create_application(client, display_name, homepage, identifier_uris,
                       # pylint: disable=too-many-arguments
                       available_to_other_tenants=False, password=None, reply_urls=None,
                       key_value=None, key_type=None, key_usage=None, start_date=None,
                       end_date=None):
    password_creds, key_creds = _build_application_creds(password, key_value, key_type,
                                                         key_usage, start_date, end_date)

    app_create_param = ApplicationCreateParameters(available_to_other_tenants,
                                                   display_name,
                                                   identifier_uris,
                                                   homepage=homepage,
                                                   reply_urls=reply_urls,
                                                   key_credentials=key_creds,
                                                   password_credentials=password_creds)
    return client.create(app_create_param)


def _resolve_service_principal(client, identifier):
    # todo: confirm with graph team that a service principal name must be unique
    result = list(
        client.list(filter="servicePrincipalNames/any(c:c eq '{}')".format(identifier)))
    if result:
        return result[0].object_id
    try:
        uuid.UUID(identifier)
        return identifier  # assume an object id
    except ValueError:
        raise MlCliError("service principal '{}' doesn't exist".format(identifier))


def show_service_principal(client, identifier):
    object_id = _resolve_service_principal(client, identifier)
    return client.get(object_id)


def _validate_service_principal(client, sp_id):
    # discard the result, we're trusting this to throw if it can't find something
    try:
        show_service_principal(client.service_principals, sp_id)
    except Exception:
        raise MlCliError('Failed to validate service principal. '
                         'If this persists try deleting $HOME/.azure/acsServicePrincipal.json')


def load_acs_service_principals(config_path):
    if not os.path.exists(config_path):
        return None
    fd = os.open(config_path, os.O_RDONLY)
    try:
        with os.fdopen(fd) as f:
            return shell_safe_json_parse(f.read())
    except:  # pylint: disable=bare-except
        return None


def _handle_merge(existing, addition, key):
    if addition[key]:
        if existing[key] is None:
            existing[key] = addition[key]
            return

        for i in addition[key]:
            written = False
            for j in range(len(existing[key])):
                if i['name'] == existing[key][j]['name']:
                    existing[key][j] = i
                    written = True
            if not written:
                existing[key].append(i)


def merge_kubernetes_yamls(existing, addition):

    _handle_merge(existing, addition, 'clusters')
    _handle_merge(existing, addition, 'users')
    _handle_merge(existing, addition, 'contexts')
    existing['current-context'] = addition['current-context']
    return existing

