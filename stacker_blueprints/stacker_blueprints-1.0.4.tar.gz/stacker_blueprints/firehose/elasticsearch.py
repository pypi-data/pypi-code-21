from troposphere import firehose, kms, Output, Ref

from .base import BaseDeliveryStream

DELIVERY_STREAM = "DeliveryStream"
ELASTICSEARCH_LOG_STREAM = "ElasticsearchLogStream"


class DeliveryStream(BaseDeliveryStream):
    def defined_variables(self):
        variables = super(DeliveryStream, self).defined_variables()

        additional = {
            "DomainArn": {
                "type": str,
                "description": "The Amazon Resource Name (ARN) of the Amazon "
                               "Elasticsearch domain that Firehose delivers "
                               "data to.",
            },
            "IndexName": {
                "type": str,
                "description": "The name of the Elasticsearch index to which "
                               "Firehose adds data for indexing.",
            },
            "IndexRotationPeriod": {
                "type": str,
                "description": "The frequency of Elasticsearch index "
                               "rotation. If you enable index rotation, "
                               "Firehose appends a portion of the UTC arrival "
                               "timestamp to the specified index name, and "
                               "rotates the appended timestamp accordingly."
            },
            "RetryDurationInSeconds": {
                "type": int,
                "description": "Retry duration for failed delivery attempts. "
                               "Must be between 0 and 7200 (2hrs). Default: "
                               "1800 seconds (30min)",
            },
            "TypeName": {
                "type": str,
                "description": "The Elasticsearch type name that Amazon ES "
                               "adds to documents when indexing data."
            },
            "S3BackupMode": {
                "type": str,
                "description": "The condition under which Firehose delivers "
                               "data to Amazon Simple Storage Service (Amazon "
                               "S3). You can send Amazon S3 all documents "
                               "(all data) or only the documents that "
                               "Firehose could not deliver to the Amazon ES "
                               "destination. Default: FailedDocumentsOnly",
                "default": "FailedDocumentsOnly",
            },
        }

        variables.update(additional)
        return variables

    def create_log_stream(self):
        t = self.template
        super(DeliveryStream, self).create_log_stream()

        self.elasticsearch_log_stream = t.add_resource(
            kms.LogStream(
                ELASTICSEARCH_LOG_STREAM,
                LogGroupName=Ref(self.log_group),
                DependsOn=self.log_group.title
            )
        )

        t.add_output(
            Output(
                "ElasticsearchLogStreamName",
                Value=Ref(self.elasticsearch_log_stream)
            )
        )

    def create_delivery_stream(self):
        t = self.template
        variables = self.get_variables()

        elasticsearch_config = firehose.ElasticsearchDestinationConfiguration(
            RoleARN=Ref(self.role),
            ClusterJDBCURL=variables['JDBCURL'],
            CopyCommand=firehose.CopyCommand(
                CopyOptions=variables["CopyOptions"],
                DataTableName=variables['TableName']
            ),
            Username=variables['Username'],
            Password=variables['Password'].ref,
            S3Configuration=self.s3_destination_config(),
            CloudWatchLoggingOptions=self.cloudwatch_logging_options(
                self.log_group,
                self.elasticsearch_log_stream
            )
        )

        t.add_resource(
            DeliveryStream(
                DELIVERY_STREAM,
                ElasticsearchDestinationConfiguration=elasticsearch_config
            )
        )

        self.delivery_stream = t.add_resource(
            firehose.DeliveryStream(
                DELIVERY_STREAM,
                S3DestinationConfiguration=self.s3_destination_config()
            )
        )
