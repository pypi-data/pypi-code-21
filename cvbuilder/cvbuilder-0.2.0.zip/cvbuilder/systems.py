import json

from pathlib import Path
from collections import namedtuple

LSB = namedtuple('LSB', ['id', 'name', 'version', 'version_id', 'pretty_name'])

DEBIAN = LSB(id="debian", name="Debian GNU/Linux", version_id="9", version="9 (stretch)",
             pretty_name="Debian GNU/Linux 9 (stretch)")

UBUNTU = LSB(id="ubuntu", name="Ubuntu", version_id="16.04", version="16.04.3 LTS (Xenial Xerus)",
             pretty_name="Ubuntu 16.04.3 LTS")

LINUX_MINT = LSB(id="linuxmint", name="Linux Mint", version_id="18.2", version="18.2 (Sonya)",
                 pretty_name="Linux Mint 18.2")

MANJARO = LSB(id="manjaro", name="Manjaro Linux", version_id=None, version=None, pretty_name="Manjaro Linux")

current = Path(__file__).parent


def read_os_release(os_release: Path = Path("/etc/os-release")):
    if not os_release.exists():
        os_release = Path("/etc/lsb-release")

    with os_release.open("rt") as fp:
        # for line in fp.readlines():
        #    line.split("=")
        ls = {line.split("=")[0].lower(): line.split("=")[1] for line in fp.readlines()}

    fields = LSB.__dict__.get("_fields")
    drop_chars = str.maketrans({
        "\n": "",
        "\"": ""
    })

    ls = {key: value.translate(drop_chars) for key, value in ls.items() if key in fields}

    lsb = namedtuple("lsb", ls.keys())
    # a = LSB(**ls)
    return lsb(**ls)


def get_system():
    return read_os_release()


def get_system_dependencies(system: LSB):
    config_location = current.joinpath("./config")

    if hasattr(system, "version_id"):
        config = config_location.joinpath("{}_{}.json".format(system.id, system.version_id))
    else:
        config = config_location.joinpath("./{}.json".format(system.id))

    try:
        with config.open("rt") as fp:
            dependencies = json.load(fp)
        return dependencies
    except:
        raise EnvironmentError("Unknown platform release: {}".format(system))
