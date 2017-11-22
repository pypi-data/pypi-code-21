import os
import kooki

resource_dir_env = 'KOOKI_DIR'
resource_dir_default = '~/.kooki'

def get_kooki_dir():
    resource_dir = os.environ.get(resource_dir_env)

    if not resource_dir:
        resource_dir = os.path.expanduser(resource_dir_default)

    kooki_package_dir = kooki.__path__[0]
    resource_dir = os.path.join(os.path.dirname(kooki_package_dir))

    return resource_dir
