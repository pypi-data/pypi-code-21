import boto3.ec2

from configAWSEnv.prints import Prints

'''
AWS connection handlers
'''


class Connections:

    def connect_to_ec2(self):
        prints = Prints()
        try:
            ec2client = boto3.client('ec2')
        except Exception as e:
            prints.print_and_exit("failed to connect to ec2, check your boto configuration\nException: {}".format(e), 2)
        return ec2client

    def connect_to_ec2_resources(self):
        prints = Prints()
        try:
            ec2resourcers = boto3.resource('ec2')
        except Exception as e:
            prints.print_and_exit("failed to connect to ec2, check your boto configuration\nException: {}".format(e), 2)
        return ec2resourcers