import os
import json


def get_fixture_file_dir():
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "../files"
        )
    )


def get_client_data():
    dirname = get_fixture_file_dir()
    ret = {}
    for fname in ("native_app_client1", "confidential_app_client1",
                  "resource_server_client"):
        with open(os.path.join(dirname,
                               "auth_fixtures",
                               fname + ".json")) as f:
            ret[fname] = json.load(f)
    return ret


def get_user_data():
    dirname = get_fixture_file_dir()
    ret = {}
    for uname in ("sdktester1a", "sdktester2b", "go"):
        with open(os.path.join(dirname,
                               "auth_fixtures",
                               uname + "@globusid.org.json")) as f:
            ret[uname] = json.load(f)
    return ret
