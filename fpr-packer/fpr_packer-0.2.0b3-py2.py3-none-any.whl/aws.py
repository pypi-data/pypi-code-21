import os
import json
import boto3
from pathlib import Path
from subprocess import check_call, check_output, STDOUT

from fpr_packer.packer import Packer


class AWSPacker(Packer):
    def create_ec2(self, image_pattern, type='t2.nano'):
        client = boto3.client('ec2')

        images = client.describe_images(Filters=[{'Name': 'name', 'Values': [image_pattern]}], Owners=['760589174259'])
        image = images['Images'][0]
        image_id = image['ImageId']
        image_name = image['Name']

        ec2 = boto3.resource('ec2')
        subnet = list(ec2.subnets.all())[0]

        instances = ec2.create_instances(
            ImageId=image_id,
            InstanceType=type,
            KeyName='fpr',
            MinCount=1,
            MaxCount=1,
            Placement={
                'AvailabilityZone': subnet.availability_zone,
            },
            SecurityGroupIds=[
                'sg-4ed6492b',
                'sg-7b7ee61e',
                'sg-0bcb9f6e',
            ],
            SubnetId=subnet.id,
        )

        try:
            instances[0].create_tags(
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': image_name
                    },
                ]
            )
        except:
            for inst in instances:
                inst.terminate()
            raise

        return instances
