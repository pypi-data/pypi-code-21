# This file is auto-generated from bandit.idl(0.7.2-79-g2db27d7) with jenerator version 0.9.4-42-g70f7539/develop
# *** DO NOT EDIT ***


import msgpackrpc
import jubatus.common
from .types import *
from jubatus.common.types import *

class Bandit(jubatus.common.ClientBase):
  def __init__(self, host, port, name, timeout=10):
    super(Bandit, self).__init__(host, port, name, timeout)

  def register_arm(self, arm_id):
    return self.jubatus_client.call("register_arm", [arm_id], TBool(), [TString(
        )])

  def delete_arm(self, arm_id):
    return self.jubatus_client.call("delete_arm", [arm_id], TBool(), [TString(
        )])

  def select_arm(self, player_id):
    return self.jubatus_client.call("select_arm", [player_id], TString(),
        [TString()])

  def register_reward(self, player_id, arm_id, reward):
    return self.jubatus_client.call("register_reward", [player_id, arm_id,
        reward], TBool(), [TString(), TString(), TFloat()])

  def get_arm_info(self, player_id):
    return self.jubatus_client.call("get_arm_info", [player_id], TMap(TString(),
        TUserDef(ArmInfo)), [TString()])

  def reset(self, player_id):
    return self.jubatus_client.call("reset", [player_id], TBool(), [TString()])

  def clear(self):
    return self.jubatus_client.call("clear", [], TBool(), [])
