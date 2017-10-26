import argparse
from configAWSEnv.const import WAKEUP, SHUTDOWN
from configAWSEnv.prints import Prints

'''
parse arguments from Jenkins/CLI
action:  required action on the environment: WAKEUP/SHUTDOWN
tags (list): key value pair of AWS tag name and tag value in the format: -t tag1-val1 -t tag2=val2...
:return:
1. action
2. list of tags
'''


class Parser:

    def parse_args(self):
        prints = Prints()
        # get args: action and AWS instances tag filters
        parser = argparse.ArgumentParser(description='get the required action and AWS instance tags')
        parser.add_argument(
            '--action', '-a', metavar='string', type=str,
            help='\'WAKEUP\'/\'SHUTDOWN\' action to run on the AWS environment', required=True)
        my_dict = {}

        class StoreDictKeyPair(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                for kv in values.split(","):
                    k, v = kv.split("=")
                    my_dict[k] = v
                setattr(namespace, self.dest, my_dict)

        parser.add_argument("--tags", "-t", dest="my_dict", action=StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...")
        args = parser.parse_args()
        if not args.action in (WAKEUP, SHUTDOWN):
            prints.print_and_exit("Invalid action passed, only {} and {} are allowed".format(WAKEUP, SHUTDOWN), 2)
        action = args.action
        filters = []
        # set the filters according to bot standards
        for tag in my_dict:
            info = {
                'Name': 'tag:{}'.format(tag),
                'Values': [my_dict.get(tag)]
            }
            filters.append(info)

        return action, filters