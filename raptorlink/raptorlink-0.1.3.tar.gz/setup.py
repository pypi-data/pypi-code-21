try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='raptorlink',
    version="0.1.3",
    description = 'test plugins for submit test result to raptor server based on nosetests',
    author = 'liuchengtao',
    author_email = 'chengtao.liu@yahoo.com',
    license = 'MIT',
    long_description = """\

Extra plugins for the nose testing framework to submit test result to raptor server\n

usage:\n
>>> nosetests --with-plan-loader --plan-file <test_plan_file> --loop <loop_num> --verbose --raptor-report\n

start from command-line:
    nosetests --with-plan-loader --plan-file plan1 --loop 100 --verbose --raptor-report

""",
    packages = ['raptorlink'],
    entry_points = {
        'nose.plugins': [
            'raptor-link = raptorlink.raptorlink:RaptorPlugin'
            ],
         },
)

