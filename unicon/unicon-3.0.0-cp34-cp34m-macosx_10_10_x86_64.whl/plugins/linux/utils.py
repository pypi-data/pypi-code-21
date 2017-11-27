import re

from unicon.utils import Utils, AttributeDict

class LinuxUtils(Utils):

    def truncate_trailing_prompt(self, pattern, result, hostname=None):
        # Prompt pattern syntax is different from the generic plugin
        # The regex group match is grouped around the prompt itself
        match = re.search(pattern, result)
        if match and match.groups():
            output = result.replace(match.group(1), "")
        else:
            output = result
        return output.strip()

