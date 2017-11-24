import guidata

import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di

class Processing(dt.DataSet):
    """Example"""
    a = di.FloatItem("Parameter #1", default=2.3)
    b = di.IntItem("Parameter #2", min=0, max=10, default=5)
    
    
class Processing2(dt.DataSet):
    """Example"""
    def __init__(self,value1=1,value2=2):
        a = di.FloatItem("Parameter #1", default=value1)
        b = di.IntItem("Parameter #2", min=0, max=10, default=value2)
    

if __name__ == "__main__":
    # Create QApplication
    import guidata
    _app = guidata.qapplication()
    param = Processing()
    param.edit()
    
    param2=Processing2(1.5,2.5)
    param2.edit()
    