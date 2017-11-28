import os
__version__ = '0.2.3'
__default_endpoint__ = 'https://vss-api.eis.utoronto.ca'
__history_file_path__ = os.path.join('~', '.vss', 'history')
__config_file_path__ = os.path.join('~', '.vss', 'config.json')
__default_debug_mode__ = False
__env_vars__ = {'user': 'VSS_API_USER',
                'pass': 'VSS_API_USER_PASS',
                'token': 'VSS_API_TOKEN',
                'endpoint': 'VSS_API_ENDPOINT',
                'debug': 'VSS_API_DEBUG',
                'config': 'VSS_CONFIG_FILE',
                'output': 'VSS_DEFAULT_OUTPUT'}
