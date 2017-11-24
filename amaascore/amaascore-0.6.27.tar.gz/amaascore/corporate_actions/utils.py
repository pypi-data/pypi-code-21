from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import inspect

#  All possible class names must be inserted into the globals collection.
#  If there is a better way of doing this, please suggest!
from amaascore.corporate_actions.corporate_action import CorporateAction
from amaascore.corporate_actions.dividend import Dividend
from amaascore.corporate_actions.split import Split


def json_to_corporate_action(json_corporate_action):
    # Iterate through the corp action children, converting the various JSON attributes into the relevant class type
    for (collection_name, clazz) in CorporateAction.children().items():
        children = json_corporate_action.pop(collection_name, {})
        collection = {}
        for (child_type, child_json) in children.items():
            # Handle the case where there are multiple children for a given type - e.g. links
            if isinstance(child_json, list):
                child = set()
                for child_json_in_list in child_json:
                    child.add(clazz(**child_json_in_list))
            else:
                child = clazz(**child_json)
            collection[child_type] = child
        json_corporate_action[collection_name] = collection
    clazz = globals().get(json_corporate_action.get('corporate_action_type'))
    args = inspect.getargspec(clazz.__init__)
    # Some fields are always added in, even though they're not explicitly part of the constructor
    clazz_args = args.args + clazz.amaas_model_attributes()
    # is not None is important so it includes zeros and False
    constructor_dict = {arg: json_corporate_action.get(arg) for arg in clazz_args
                        if json_corporate_action.get(arg) is not None and arg != 'self'}
    corporate_action = clazz(**constructor_dict)
    return corporate_action


def csv_filename_to_corporate_actions(filename):
    with open(filename, 'r') as f:
        corporate_actions = csv_stream_to_corporate_actions(f)
    return corporate_actions


def csv_stream_to_corporate_actions(stream):
    reader = csv.DictReader(stream)
    corporate_actions = []
    for row in reader:
        corporate_actions.append(json_to_corporate_action(row))
    return corporate_actions


def corporate_actions_to_csv(corporate_actions, filename):
    with open(filename, 'w') as csvfile:
        corporate_actions_to_csv_stream(corporate_actions=corporate_actions, stream=csvfile)


def corporate_actions_to_csv_stream(corporate_actions, stream):
    if not corporate_actions:
        return
    corporate_action_dicts = []
    for corporate_action in corporate_actions:
        corporate_action_dicts.append(corporate_action.to_json())
    fieldnames = corporate_action_dicts[0].keys()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(corporate_action_dicts)
