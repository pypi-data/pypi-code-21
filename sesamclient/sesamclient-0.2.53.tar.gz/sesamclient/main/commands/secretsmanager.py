# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import os
import json

from ..utils import print_item, exit_with_error


def get_secrets_cmd(connection, args):
    secrets_info = connection.get_secrets()
    print(secrets_info)


def put_secrets_cmd(connection, args):
    secrets_path = args.secrets_file

    if not os.path.exists(secrets_path):
        exit_with_error("The specified path '%s' doesn't exist!" % (secrets_path,))
    with open(secrets_path, "r", encoding="utf-8") as secrets_content:
        secrets_info = connection.put_secrets(json.loads(secrets_content.read()), args.dont_encrypt)
        print_item(secrets_info, args)


def delete_secret_cmd(connection, args):
    secret_info = connection.delete_secret(args.secret_key)
    print_item(secret_info, args)
