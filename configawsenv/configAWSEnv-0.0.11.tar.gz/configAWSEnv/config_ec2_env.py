import boto3.ec2
from configAWSEnv.const import WAKEUP, SHUTDOWN
from configAWSEnv.connection import Connections
from configAWSEnv.parser import Parser
from configAWSEnv.prints import Prints

'''
Main ASW functionality
- Get the list of instance to run on according to the AWS filter
- Get the required action (start or stop the instances)
- Run and verify state after instance status change.
- If fails - return AWS console URL with the list of problematic instances
'''


class Config:
    def __init__(self):
        pass

    def get_ec2_instances(self, filters):

        connection = Connections()
        ec2 = connection.connect_to_ec2()

        response = ec2.describe_instances(Filters=filters)

        instances = []
        for reservation in (response["Reservations"]):
            for instance in reservation["Instances"]:
                instances.append(instance)

        return instances

    def list_instances_by_tag_value(self, action, filters):

        if action == WAKEUP:
            filters.append({'Name': 'instance-state-name', 'Values': ['{}'.format('stopped')]})
        elif action == SHUTDOWN:
            filters.append({'Name': 'instance-state-name', 'Values': ['{}'.format('running')]})

        return [instance["InstanceId"] for instance in self.get_ec2_instances(filters)]

    def configure_environment(self, action, environment):
        ec2_con = Connections()
        ec2resourcers = ec2_con.connect_to_ec2_resources()
        if len(environment) == 0:
            print("No instances found in the environment, check your tags and filters")
            return 1
        if action == WAKEUP:
            ec2resourcers.instances.filter(InstanceIds=environment).start()

            # wait till all instances start
            for instance in environment:
                ec2resourcers.Instance(instance).wait_until_running()
        elif action == SHUTDOWN:
            ec2resourcers.instances.filter(InstanceIds=environment).stop()
            # wait till all instances stop
            for instance in environment:
                ec2resourcers.Instance(instance).wait_until_stopped()
        return 0

    def validate_env_status(self, action, filters):
        prints = Prints()
        new_environment = self.list_instances_by_tag_value(action, filters)
        if len(new_environment) > 0:
            prints.print_and_exit("Failed to {} environment, "
                                  "\nsee instances with unknown status in AWS console:\n {}".format(action,
                                                                                                    self.create_aws_url(
                                                                                                        self,
                                                                                                        new_environment)),
                                  2)
        else:
            print("environment {} successfully".format(action))

        return new_environment

    def get_region(self):
        my_session = boto3.session.Session()
        return my_session.region_name

    def create_aws_url(self, bad_instances):
        # open browser with instances
        base_url = "https://console.aws.amazon.com/ec2/v2/home"
        region_prefix = "?region="
        region = self.get_region(self)
        instances_search = "#Instances:search="
        instances_ids = ""
        sort = ";sort=instanceState"
        for bad_instance in bad_instances:
            instances_ids += bad_instance + ","
        url = base_url + region_prefix + region + instances_search + instances_ids + sort
        return url


def main(*args):
    parser = Parser()
    prints = Prints()
    conf = Config()
    action, filters = parser.parse_args()
    environment = conf.list_instances_by_tag_value(action=action, filters=filters)
    if not len(environment) > 0:
        prints.print_and_exit("No instances found in the environment", 0)
    print("running on AWS region: {}".format(conf.get_region()))
    print("{} called for the following instances: {}".format(action, environment))

    conf.configure_environment(action, environment)
    conf.validate_env_status(action=action, filters=filters)
