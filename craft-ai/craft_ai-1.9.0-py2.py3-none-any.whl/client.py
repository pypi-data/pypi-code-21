# To avoid conflicts between python's own 'time' and this 'time.py'
# cf. https://stackoverflow.com/a/28854227
from __future__ import absolute_import

import json
import time

from platform import python_implementation, python_version

import requests
import six

from craftai import helpers, __version__ as pkg_version
from craftai.constants import AGENT_ID_PATTERN
from craftai.errors import CraftAiCredentialsError, CraftAiBadRequestError, CraftAiNotFoundError
from craftai.errors import CraftAiUnknownError, CraftAiInternalError, CraftAiLongRequestTimeOutError
from craftai.interpreter import Interpreter
from craftai.jwt_decode import jwt_decode

USER_AGENT = "craft-ai-client-python/{} [{} {}]".format(pkg_version,
                                                        python_implementation(),
                                                        python_version())

def current_time_ms():
  return int(round(time.time() * 1000))

class CraftAIClient(object):
  """Client class for craft ai's API"""

  def __init__(self, cfg):
    self._base_url = ""
    self._headers = {}
    self._config = {}

    try:
      self.config = cfg
    except (CraftAiCredentialsError, CraftAiBadRequestError) as e:
      raise e

  @property
  def config(self):
    return self._config

  @config.setter
  def config(self, cfg):
    cfg = cfg.copy()
    (payload, _, _, _) = jwt_decode(cfg.get("token"))
    cfg["owner"] = cfg["owner"] if "owner" in cfg else payload.get("owner")
    cfg["project"] = cfg["project"] if "project" in cfg else payload.get("project")
    cfg["url"] = cfg["url"] if "url" in cfg else payload.get("platform")

    if not isinstance(cfg.get("project"), six.string_types):
      raise CraftAiCredentialsError("""Unable to create client with no"""
                                    """ or invalid project provided.""")
    else:
      splitted_project = cfg.get("project").split("/")
      if len(splitted_project) == 2:
        cfg["owner"] = splitted_project[0]
        cfg["project"] = splitted_project[1]
      elif len(splitted_project) > 2:
        raise CraftAiCredentialsError("""Unable to create client with invalid"""
                                      """ project name.""")
    if not isinstance(cfg.get("owner"), six.string_types):
      raise CraftAiCredentialsError("""Unable to create client with no"""
                                    """ or invalid owner provided.""")
    if not isinstance(cfg.get("operationsChunksSize"), six.integer_types):
      cfg["operationsChunksSize"] = 200
    if (cfg.get("decisionTreeRetrievalTimeout") is not False and
        not isinstance(cfg.get("decisionTreeRetrievalTimeout"), six.integer_types)):
      cfg["decisionTreeRetrievalTimeout"] = 1000 * 60 * 5 # 5 minutes
    if not isinstance(cfg.get("url"), six.string_types):
      cfg["url"] = "https://beta.craft.ai"
    if cfg.get("url").endswith("/"):
      raise CraftAiBadRequestError("""Unable to create client with"""
                                   """ invalid url provided. The url"""
                                   """ should not terminate with a"""
                                   """ slash.""")
    self._config = cfg

    self._base_url = "{}/api/v1/{}/{}".format(self.config["url"],
                                              self.config["owner"],
                                              self.config["project"])

    # Headers have to be reset here to avoid multiple definitions
    # of the 'Authorization' header if config is modified
    self._headers = {}
    self._headers["Authorization"] = "Bearer " + self.config.get("token")
    self._headers["User-Agent"] = USER_AGENT

  #################
  # Agent methods #
  #################

  def create_agent(self, configuration, agent_id=""):
    # Building final headers
    ct_header = {"Content-Type": "application/json; charset=utf-8"}
    headers = helpers.join_dicts(self._headers, ct_header)

    # Building payload and checking that it is valid for a JSON
    # serialization
    payload = {"configuration": configuration}

    if agent_id != "":
      # Raises an error when agent_id is invalid
      self._check_agent_id(agent_id)

      payload["id"] = agent_id

    try:
      json_pl = json.dumps(payload)
    except TypeError as e:
      raise CraftAiBadRequestError("Invalid configuration or agent id given. {}"
                                   .format(e.__str__()))

    req_url = "{}/agents".format(self._base_url)
    resp = requests.post(req_url, headers=headers, data=json_pl)

    agent = self._decode_response(resp)

    return agent

  def get_agent(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    # No supplementary headers needed
    headers = self._headers.copy()

    req_url = "{}/agents/{}".format(self._base_url, agent_id)
    resp = requests.get(req_url, headers=headers)

    agent = self._decode_response(resp)

    return agent

  def list_agents(self):
    # No supplementary headers needed
    headers = self._headers.copy()

    req_url = "{}/agents".format(self._base_url)
    resp = requests.get(req_url, headers=headers)

    agents = self._decode_response(resp)

    return agents["agentsList"]

  def delete_agent(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)


    # No supplementary headers needed
    headers = self._headers.copy()

    req_url = "{}/agents/{}".format(self._base_url, agent_id)
    resp = requests.delete(req_url, headers=headers)

    decoded_resp = self._decode_response(resp)

    return decoded_resp

  def get_shared_agent_inspector_url(self, agent_id, timestamp=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    # No supplementary headers needed
    headers = self._headers.copy()

    req_url = "{}/agents/{}/shared".format(self._base_url, agent_id)
    resp = requests.get(req_url, headers=headers)

    url = self._decode_response(resp)

    if timestamp != None:
      return "{}?t={}".format(url["shortUrl"], str(timestamp))

    return url["shortUrl"]

  def delete_shared_agent_inspector_url(self, agent_id):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    # No supplementary headers needed
    headers = self._headers.copy()

    req_url = "{}/agents/{}/shared".format(self._base_url, agent_id)
    resp = requests.delete(req_url, headers=headers)

    decoded_resp = self._decode_response(resp)

    return decoded_resp

  ###################
  # Context methods #
  ###################

  def add_operations(self, agent_id, operations):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    # Building final headers
    ct_header = {"Content-Type": "application/json; charset=utf-8"}
    headers = helpers.join_dicts(self._headers, ct_header)

    session = requests.Session()
    offset = 0

    while True:
      next_offset = offset + self.config["operationsChunksSize"]

      try:
        json_pl = json.dumps(operations[offset:next_offset])
      except TypeError as e:
        raise CraftAiBadRequestError("Invalid configuration or agent id given. {}"
                                     .format(e.__str__()))

      req_url = "{}/agents/{}/context".format(self._base_url, agent_id)
      resp = session.post(req_url, headers=headers, data=json_pl)

      self._decode_response(resp)

      if next_offset >= len(operations):
        return {
          "message": "Successfully added %i operation(s) to the agent \"%s/%s/%s\" context."
                     % (len(operations), self.config["owner"], self.config["project"], agent_id)
        }

      offset = next_offset

  def _get_operations_list_pages(self, url, ops_list):
    if url is None:
      return ops_list

    headers = self._headers.copy()

    resp = requests.get(url, headers=headers)

    new_ops_list = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_operations_list_pages(next_page_url, ops_list + new_ops_list)

  def get_operations_list(self, agent_id, start=None, end=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    headers = self._headers.copy()

    req_url = "{}/agents/{}/context".format(self._base_url, agent_id)
    req_params = {
      "start": start,
      "end": end
    }
    resp = requests.get(req_url, params=req_params, headers=headers)

    initial_ops_list = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_operations_list_pages(next_page_url, initial_ops_list)

  def _get_state_history_pages(self, url, state_history):
    if url is None:
      return state_history

    headers = self._headers.copy()

    resp = requests.get(url, headers=headers)

    new_state_history = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_state_history_pages(next_page_url, state_history + new_state_history)

  def get_state_history(self, agent_id, start=None, end=None):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    headers = self._headers.copy()

    req_url = "{}/agents/{}/context/state/history".format(self._base_url, agent_id)
    req_params = {
      "start": start,
      "end": end
    }
    resp = requests.get(req_url, params=req_params, headers=headers)

    initial_states_history = self._decode_response(resp)
    next_page_url = resp.headers.get("x-craft-ai-next-page-url")

    return self._get_state_history_pages(next_page_url, initial_states_history)

  def get_context_state(self, agent_id, timestamp):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    headers = self._headers.copy()

    req_url = "{}/agents/{}/context/state?t={}".format(self._base_url,
                                                       agent_id,
                                                       timestamp)
    resp = requests.get(req_url, headers=headers)

    context_state = self._decode_response(resp)

    return context_state

  #########################
  # Decision tree methods #
  #########################

  def _get_decision_tree(self, agent_id, timestamp):
    headers = self._headers.copy()

    req_url = "{}/agents/{}/decision/tree?t={}".format(self._base_url,
                                                       agent_id,
                                                       timestamp)

    resp = requests.get(req_url, headers=headers)

    decision_tree = self._decode_response(resp)

    return decision_tree

  def get_decision_tree(self, agent_id, timestamp):
    # Raises an error when agent_id is invalid
    self._check_agent_id(agent_id)

    if self._config["decisionTreeRetrievalTimeout"] is False:
      # Don't retry
      return self._get_decision_tree(agent_id, timestamp)
    else:
      start = current_time_ms()
      while True:
        now = current_time_ms()
        if now - start > self._config["decisionTreeRetrievalTimeout"]:
          # Client side timeout
          raise CraftAiLongRequestTimeOutError()
        try:
          return self._get_decision_tree(agent_id, timestamp)
        except CraftAiLongRequestTimeOutError:
          # Do nothing and continue.
          continue

  @staticmethod
  def decide(tree, *args):
    return Interpreter.decide(tree, args)

  @staticmethod
  def _parse_body(response):
    try:
      return response.json()
    except:
      raise CraftAiInternalError(
        "Internal Error, the craft ai server responded in an invalid format."
      )

  @staticmethod
  def _decode_response(response):
    status_code = response.status_code

    if status_code == 200 or status_code == 201 or status_code == 204:
      return CraftAIClient._parse_body(response)
    if status_code == 202:
      raise CraftAiLongRequestTimeOutError(CraftAIClient._parse_body(response)["message"])
    if status_code == 401 or status_code == 403:
      raise CraftAiCredentialsError(CraftAIClient._parse_body(response)["message"])
    if status_code == 400:
      raise CraftAiBadRequestError(CraftAIClient._parse_body(response)["message"])
    if status_code == 404:
      raise CraftAiNotFoundError(CraftAIClient._parse_body(response)["message"])
    if status_code == 413:
      raise CraftAiBadRequestError("Given payload is too large")
    if status_code == 500:
      raise CraftAiInternalError(CraftAIClient._parse_body(response)["message"])
    if status_code == 504:
      raise CraftAiBadRequestError("Request has timed out")

    raise CraftAiUnknownError(CraftAIClient._parse_body(response)["message"])

  @staticmethod
  def _check_agent_id(agent_id):
    """Checks that the given agent_id is a valid non-empty string.

    Raises an error if the given agent_id is not of type string or if it is
    an empty string.
    """
    if (not isinstance(agent_id, six.string_types) or
        AGENT_ID_PATTERN.match(agent_id) is None):
      raise CraftAiBadRequestError("""Invalid agent id given."""
                                   """It must be a string containaing only"""
                                   """characters in \"a-zA-Z0-9_-\""""
                                   """and must be between 1 and 36 characters.""")
