import re


from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.config import CONFIGURATION


def insert_js_agent(response):
    if not response.is_streamed and response.headers.get("Content-Type", None) and response.headers["Content-Type"].startswith("text/html"):
        tag_policy = TCellAgent.get_policy(PolicyTypes.CSP)
        if tag_policy and tag_policy.js_agent_api_key:
            if CONFIGURATION.js_agent_api_base_url:
                replace = "\g<m><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\""  # pylint: disable=anomalous-backslash-in-string
                replace += CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\" tcellbaseurl=\""
                replace += CONFIGURATION.js_agent_api_base_url + "\"></script>"
            else:
                replace = "\g<m><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\""   # pylint: disable=anomalous-backslash-in-string
                replace += CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\"></script>"

            response_content = response.get_data(True)
            response_content = re.sub("(?P<m><head>|<head .+?>)", replace, response_content)
            from flask.wrappers import Response
            response = Response(response_content, status=response.status_code, headers=response.headers)

    return response
