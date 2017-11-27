#! /usr/bin/python

# Python
import argparse

# ATS
from ats.topology import loader

# Genie Diff - Allows user to do a comparison between different outputs (dictionaries)
from genie.utils.diff import Diff

# Sample Metaparser from NXOS
from parser.nxos.show_bgp import ShowBgpProcessVrfAll

# Mandatory arguments the user needs to provide
parser = argparse.ArgumentParser()

# Testbed YAML file containing connection information
parser.add_argument('-testbed_file',
                    help="Supply testbed YAML file with 'uut' specified",
                    type=str)

# Device to execute parsers on
parser.add_argument('-device',
                    help="Specify which device to execute parsers on",
                    type=str)

# Get arguments
user_args = parser.parse_known_args()[0]

# Connect to device
tb = loader.load(user_args.testbed_file)
device = tb.devices[user_args.device]
device.connect()

# Call parser with CLI context
cli_obj = ShowBgpProcessVrfAll(device=device, context='cli')
cli_parsed_output = cli_obj.parse()

# Call parser with XML context
xml_obj = ShowBgpProcessVrfAll(device=device, context='xml')
xml_parsed_output = xml_obj.parse()

# Call parser with YANG context
# Uncomment this section if your testbed YAML file contains Yang information
#yang_obj = ShowBgpProcessVrfAll(device=device, context='yang')
#yang_parsed_output = yang_obj.parse()

# Call parser with list of contexts
# Execute XML first, if all parser schema keys are not found via XML, then
# Metaparser will populate the missing keys using CLI
all_context_obj = ShowBgpProcessVrfAll(device=device, context=['xml', 'cli'])
parsed_output = all_context_obj.parse()

# Compare CLI parsed outputs vs. XML parsed output
# Ideally, the 2 should have no difference
diff1 = Diff(cli_parsed_output, xml_parsed_output)
diff1.findDiff()
assert(diff1.diffs == [])

# Compare CLI parsed outputs vs. Yang parsed output
# Ideally, the 2 should have no difference
#diff2 = Diff(cli_parsed_output, yang_parsed_output)
#diff2.findDiff()
#assert(diff2.diffs == [])

# Compare XML parsed outputs vs. Yang parsed output
# Ideally, the 2 should have no difference
#diff3 = Diff(xml_parsed_output, yang_parsed_output)
#diff3.findDiff()
#assert(diff3.diffs == [])