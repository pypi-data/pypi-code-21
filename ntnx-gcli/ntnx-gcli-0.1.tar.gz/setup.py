from setuptools import setup

setup(
    name="ntnx-gcli",
    version='0.1',
    description = 'NTNX Guest OS Client tool',
    author = 'Amir Eibagi',
    author_email = 'amir.eibagi@nutanix.com',
    url = 'https://drt-it-github-prod-1.eng.nutanix.com/hackathon-2017/main-clone/tree/guest_os_client/qa/tools/guest_os_client',
    py_modules=['gcli', 'gcli_util', 'gcli_context', 'acro_gos_utility', 'gcli_logging'],
    install_requires=[
        'Click',
        'click-shell',
        'paramiko'
    ],
    entry_points='''
        [console_scripts]
        gcli=gcli:cli
    ''',
)
