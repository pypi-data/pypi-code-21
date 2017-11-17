import re

from unicon.utils import Utils, AttributeDict

class NsoUtils(Utils):

    def truncate_trailing_prompt(self, con_state, result, hostname=None):
        # Prompt pattern syntax is different from the generic plugin
        # The regex group match is grouped around the prompt itself
        regex = con_state.pattern.replace('^.*', '')
        match = re.search(regex, result)
        if match and match.groups():
            output = result.replace(match.group(1), "")
        else:
            output = result
        return output.strip()

