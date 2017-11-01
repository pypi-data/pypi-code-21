import click

from globus_cli.parsing import (
    common_options, endpoint_create_and_update_params, one_use_option,
    validate_endpoint_create_and_update_params, ENDPOINT_PLUS_REQPATH)
from globus_cli.services.transfer import (
    autoactivate, get_client, assemble_generic_doc)
from globus_cli.safeio import formatted_print, FORMAT_TEXT_RECORD


COMMON_FIELDS = [
    ('Message', 'message'),
    ('Endpoint ID', 'id'),
]

GCP_FIELDS = [
    ('Setup Key', 'globus_connect_setup_key'),
]


@click.command(
    "create", short_help="Create a new endpoint",
    help=("Create a new endpoint. Requires a display name and exactly one of "
          "--personal, --server, or --shared to make a Globus Connect "
          "Personal, Globus Connect Server, or shared endpoint respectively."))
@common_options
@endpoint_create_and_update_params(create=True)
@one_use_option("--personal", is_flag=True,
                help=("Create a Globus Connect Personal endpoint. "
                      "Mutually exclusive with --server and --shared. "))
@one_use_option("--server", is_flag=True,
                help=("Create a Globus Connect Server endpoint. "
                      "Mutually exclusive with --personal and --shared."))
@one_use_option("--shared", default=None, type=ENDPOINT_PLUS_REQPATH,
                metavar=ENDPOINT_PLUS_REQPATH.metavar,
                help=("Create a shared endpoint hosted on the given endpoint "
                      "and path. Mutually exclusive with --personal and "
                      "--server."))
def endpoint_create(**kwargs):
    """
    Executor for `globus endpoint create`
    """
    client = get_client()

    # get endpoint type, ensure unambiguous.
    personal = kwargs.pop("personal")
    server = kwargs.pop("server")
    shared = kwargs.pop("shared")

    if personal and (not server) and (not shared):
        endpoint_type = "personal"
    elif server and (not personal) and (not shared):
        endpoint_type = "server"
    elif shared and (not personal) and (not server):
        endpoint_type = "shared"
    else:
        raise click.UsageError(
            "Exactly one of --personal, --server, or --shared is required.")

    # validate options
    kwargs["is_globus_connect"] = personal or None
    validate_endpoint_create_and_update_params(endpoint_type, False, kwargs)

    # shared endpoint creation
    if shared:
        endpoint_id, host_path = shared
        kwargs["host_endpoint"] = endpoint_id
        kwargs["host_path"] = host_path

        ep_doc = assemble_generic_doc('shared_endpoint', **kwargs)
        autoactivate(client, endpoint_id, if_expires_in=60)
        res = client.create_shared_endpoint(ep_doc)

    # non shared endpoint creation
    else:
        # omit `is_globus_connect` key if not GCP, otherwise include as `True`
        ep_doc = assemble_generic_doc('endpoint', **kwargs)
        res = client.create_endpoint(ep_doc)

    # output
    formatted_print(res, fields=(COMMON_FIELDS + GCP_FIELDS
                    if personal else COMMON_FIELDS),
                    text_format=FORMAT_TEXT_RECORD)
