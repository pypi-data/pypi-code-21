from six.moves import range

import pandas as pd

from .. import Client as VanillaClient
from ..errors import CraftAiBadRequestError
from .interpreter import Interpreter

def chunker(to_be_chunked_df, chunk_size):
  return (to_be_chunked_df[pos:pos + chunk_size]
          for pos in range(0, len(to_be_chunked_df), chunk_size))

class Client(VanillaClient):
  """Client class for craft ai's API using pandas dataframe types"""
  def add_operations(self, agent_id, operations):
    if isinstance(operations, pd.DataFrame):
      if not isinstance(operations.index, pd.DatetimeIndex):
        raise CraftAiBadRequestError("Invalid dataframe given, it is not time indexed")

      chunk_size = self.config["operationsChunksSize"]

      for chunk in chunker(operations, chunk_size):
        chunk_operations = [
          {
            "timestamp": row.name.value // 10 ** 9, # Timestamp.value returns nanoseconds
            "context": {
              col: row[col] for col in operations.columns if pd.notnull(row[col])
            }
          } for _, row in chunk.iterrows()
        ]
        super(Client, self).add_operations(agent_id, chunk_operations)

      return {
        "message": "Successfully added %i operation(s) to the agent \"%s/%s/%s\" context."
                   % (len(operations), self.config["owner"], self.config["project"], agent_id)
      }
    else:
      return super(Client, self).add_operations(agent_id, operations)

  def get_operations_list(self, agent_id, start=None, end=None):
    operations_list = super(Client, self).get_operations_list(agent_id, start, end)

    return pd.DataFrame(
      [operation["context"] for operation in operations_list],
      index=pd.to_datetime([operation["timestamp"] for operation in operations_list], unit="s")
    )

  def get_state_history(self, agent_id, start=None, end=None):
    state_history = super(Client, self).get_state_history(agent_id, start, end)

    return pd.DataFrame(
      [state["sample"] for state in state_history],
      index=pd.to_datetime([state["timestamp"] for state in state_history], unit="s")
    )

  @staticmethod
  def decide_from_contexts_df(tree, contexts_df):
    return Interpreter.decide_from_contexts_df(tree, contexts_df)
