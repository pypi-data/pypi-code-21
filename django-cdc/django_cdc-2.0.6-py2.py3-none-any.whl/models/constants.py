from enum import Enum

class ServiceType(Enum):
    KINESIS="kinesis"
    SNS="sns"
    LAMBDA_KINESIS="lambda_kinesis"
    ASYNC_KAFKA_PRODUCER="async_kafka_producer"
    SYNC_KAFKA_PRODUCER="sync_kafka_producer"