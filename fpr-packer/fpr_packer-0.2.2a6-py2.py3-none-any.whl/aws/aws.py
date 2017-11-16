import boto3


class Image:
    def __init__(self, image):
        self.image = image

    @property
    def id(self):
        return self.image['ImageId']

    @property
    def name(self):
        return self.image['Name']


class EC2:
    @staticmethod
    def create_instance(*, id=None, pattern=None, name=None, type='t2.nano', **kwargs):
        client = boto3.client('ec2')

        if id is None:
            if pattern is None:
                raise ValueError("pattern must be defined if id isn't")

            images = client.describe_images(Filters=[{'Name': 'name', 'Values': [pattern]}], Owners=['760589174259'])
            image = Image(images['Images'][0])
            id = image.id
            if name is None:
                name = image.name


        ec2 = boto3.resource('ec2')
        subnet = list(ec2.subnets.all())[0]

        kwargs.setdefault("MinCount", 1)
        kwargs.setdefault("MaxCount", 1)

        ec2.Image(id).wait_until_exists()

        instances = ec2.create_instances(
            ImageId=id,
            InstanceType=type,
            KeyName='fpr',
            Placement={
                'AvailabilityZone': subnet.availability_zone,
            },
            SecurityGroupIds=[
                'sg-4ed6492b',
                'sg-7b7ee61e',
                'sg-0bcb9f6e',
            ],
            SubnetId=subnet.id,
            **kwargs
        )

        try:
            assert len(instances) == 1
            instance = instances[0]
            instance.create_tags(
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': name
                    },
                ]
            )
            return instance
        except:
            for inst in instances:
                inst.terminate()
            raise
