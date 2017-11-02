existing = get_settings_dict()

from thingo import loadenv

for key in list(environ.keys()):
    del environ[key]

loadenv('/my/settings/env/.env', override=True)

new = get_settings_dict()
