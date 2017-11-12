import argparse
import secretstorage
from kotp.kotp import KeyringOTP


def get_parser():
    parser = argparse.ArgumentParser(
        description="CLI to generate One Time Password from secrets stored "
                    "in Keyring (using seahorse password manager)"
    )
    parser.add_argument(
        '-s', '--secret',
        help="Force using secret from command line instead getting it from "
             "the password manager. (as keyring and key are mandatory set "
             "any values they will be ignored).",
        default=None,
    )
    parser.add_argument(
        '-o', '--output',
        help="Display output in console and in the clipboard (useful if you "
             "can't install xclip).",
        action='store_true',
    )
    parser.add_argument(
        '-d', '--duration',
        help="How many seconds you wants the One Time Password in your "
             "clipboard. Note that as time changing clipboard is update.d",
        default=30,
        type=int,
    )
    parser.add_argument("keyring")
    parser.add_argument("key")
    return parser


def get_secret_key(keyring, key):
    bus = secretstorage.dbus_init()
    keyrings = [
        collection for collection in secretstorage.get_all_collections(bus)
        if collection.get_label() == keyring
    ]
    if len(keyrings) != 1:
        raise RuntimeError(
            "Expect 1 keyring for the given label {},"
            " found {} keyring: {}".format(
                keyring, len(keyrings), [k.get_label() for k in keyrings]
            )
        )
    secrets = [
        item for item in keyrings[0].get_all_items() if
        item.get_label() == key
    ]
    if len(secrets) != 1:
        raise RuntimeError(
            "Expect 1 key for the given key {} in keyring {},"
            " found {} items: {}".format(
                key, keyrings[0].get_label(), len(secrets),
                [i.get_label() for i in secrets]
            )
        )
    return secrets[0].get_secret()


def get_totp(keyring, key, secret=None, output=False, duration=30):
    if not secret:
        secret=get_secret_key(keyring, key)

    KeyringOTP(secret, console_output=output, run_duration=duration).run()


def main():
    arguments = get_parser().parse_args()

    get_totp(
        arguments.keyring,
        arguments.key,
        secret=arguments.secret,
        output=arguments.output,
        duration=arguments.duration,
    )
