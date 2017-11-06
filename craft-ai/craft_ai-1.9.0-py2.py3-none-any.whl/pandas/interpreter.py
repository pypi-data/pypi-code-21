import pandas as pd

from .. import Interpreter as VanillaInterpreter, Time
from ..errors import CraftAiBadRequestError, CraftAiNullDecisionError

def decide_from_row(tree, columns, row):
  time = Time(
    t=row.name.value // 10 ** 9, # Timestamp.value returns nanoseconds
    timezone=row.name.tz
  )
  context = {
    col: row[col] for col in columns if pd.notnull(row[col])
  }
  try:
    decision = VanillaInterpreter.decide(tree, [context, time])

    keys, values = zip(*[
      (output + "_" + key, value)
      for output, output_decision in decision["output"].items()
      for key, value in output_decision.items()
    ])

    return pd.Series(data=values, index=keys)
  except CraftAiNullDecisionError as e:
    return pd.Series(data=[e.message], index=["error"])

class Interpreter(VanillaInterpreter):
  @staticmethod
  def decide_from_contexts_df(tree, contexts_df):
    if not isinstance(contexts_df.index, pd.DatetimeIndex):
      raise CraftAiBadRequestError("Invalid dataframe given, it is not time indexed")

    return contexts_df.apply(lambda row: decide_from_row(tree,
                                                         contexts_df.columns,
                                                         row)
                             , axis=1)
