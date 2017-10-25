#1.4.0
def interatorArr (obj,level=0,tabFlag=False):
    for unit in obj:
        if isinstance(unit,list):
            interatorArr(unit,level+1)
        else:
            if tabFlag:
                for tab_stop in range(level):
                    print("\t",end="")
            print(unit)

