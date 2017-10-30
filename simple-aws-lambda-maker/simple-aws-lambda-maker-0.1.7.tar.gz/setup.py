from setuptools import setup, find_packages
from simple_aws_lambda_maker import VERSION

setup(
      name = "simple-aws-lambda-maker"
    , version = VERSION
    , packages = ['simple_aws_lambda_maker'] + ['simple_aws_lambda_maker.%s' % pkg for pkg in find_packages('simple_aws_lambda_maker')]
    , include_package_data = True

    , install_requires =
      [ "delfick_app==0.9.6"
      , "option_merge==1.6"
      , "input_algorithms==0.6.0"

      , "boto3==1.4.7"
      , "datadiff==2.0.0"
      , "PyYaml==3.12"
      , "requests==2.18.4"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.7"
        , "nose"
        , "mock==1.0.1"
        , "tox"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'salm = simple_aws_lambda_maker.executor:main'
        ]
      }

    # metadata for upload to PyPI
    , url = "https://github.com/delfick/simple-aws-lambda-maker"
    , author = "Stephen Moore"
    , author_email = "delfick755@gmail.com"
    , description = "Very simple deploy tool for aws lambda"
    , license = "MIT"
    , keywords = "aws lambda"
    )

