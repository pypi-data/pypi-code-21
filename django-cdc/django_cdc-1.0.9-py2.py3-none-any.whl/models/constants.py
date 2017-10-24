from enum import Enum

class ServiceType(Enum):
    KINESIS="kinesis"
    SNS="sns"
    LAMBDA_KINESIS="lambda_kinesis"