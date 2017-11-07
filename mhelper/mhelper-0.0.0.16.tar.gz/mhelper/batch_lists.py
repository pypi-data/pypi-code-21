from typing import Tuple


class BatchList:
    def __init__(self, data, batch_size):
        self.batch = batch_size
        self.data = list(data)
        
    def take(self):
        result = self.data[0:self.batch]
        del self.data[0:self.batch]
        return result
    
    def __bool__(self):
        return bool(self.data)
    
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        while self:
            yield self.take()


def divide_workload(index : int, count : int, quantity : int) -> Tuple[int, int]:
    partition_size = quantity / count
    
    start = index * partition_size
    
    if index == count - 1:
        end = quantity
    else:
        end  = int(start + partition_size)
        
    return int(start), end
    