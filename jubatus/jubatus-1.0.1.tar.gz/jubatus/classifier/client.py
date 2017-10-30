# This file is auto-generated from classifier.idl(0.8.9-17-gd4c007f) with jenerator version 0.9.4-42-g70f7539/develop
# *** DO NOT EDIT ***


import msgpackrpc
import jubatus.common
from .types import *
from jubatus.common.types import *

class Classifier(jubatus.common.ClientBase):
  def __init__(self, host, port, name, timeout=10):
    super(Classifier, self).__init__(host, port, name, timeout)

  def train(self, data):
    return self.jubatus_client.call("train", [data], TInt(True, 4), [TList(
        TUserDef(LabeledDatum))])

  def classify(self, data):
    return self.jubatus_client.call("classify", [data], TList(TList(TUserDef(
        EstimateResult))), [TList(TDatum())])

  def get_labels(self):
    return self.jubatus_client.call("get_labels", [], TMap(TString(), TInt(
        False, 8)), [])

  def set_label(self, new_label):
    return self.jubatus_client.call("set_label", [new_label], TBool(), [TString(
        )])

  def clear(self):
    return self.jubatus_client.call("clear", [], TBool(), [])

  def delete_label(self, target_label):
    return self.jubatus_client.call("delete_label", [target_label], TBool(),
        [TString()])
