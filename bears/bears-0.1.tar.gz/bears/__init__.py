import numpy as np
from typing import List


class DataFrame(object):
    def __init__(self, data: dict = None, keys: List[str] = None, values: List[np.ndarray] = None):
        if dict is not None:
            self.keys = list(data.keys())
            self.values = list(data.values())
        else:
            self.keys = keys
            self.values = values

        for i, key in enumerate(self.keys):
            self.__dict__[key] = i

    def __len__(self):
        return self.size

    # [ [v1,v2], [v1,v2] ]
    def rows_value(self, index=None):
        if index is None:
            return self.values
        else:
            return [v[index] for v in self.values]

    # [ {'col1': v1, 'col2': v2}, {'col1': v1, 'col2': v2} ]
    def rows_dict(self, index=None):
        if index is None:
            return [{k: v} for k, v in zip(self.keys, self.values)]
        else:
            return [{k: v[index]} for k, v in zip(self.keys, self.values)]

    # {'col1': v1, 'col2': v2}
    def to_dict(self, index=None):
        if index is None:
            return {
                k: v
                for k, v in zip(self.keys, self.values)
            }
        else:
            return {
                k: v[index]
                for k, v in zip(self.keys, self.values)
            }

    # return mutable view
    # d[3] = self.row_values(3)
    # d[3:4] = sub-dataframe
    def __getitem__(self, key):
        if isinstance(key, int):
            # return {
            #     k:v[key] for (k,v) in self.data.items()
            # }
            return [val[key] for val in self.values]
        else:
            return DataFrame(
                keys=self.keys,
                values=[v[key] for v in self.values]
            )
