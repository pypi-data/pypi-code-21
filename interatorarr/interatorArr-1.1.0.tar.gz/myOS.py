def interatorArr (obj,level):
    for unit in obj:
        if isinstance(unit,list):
            interatorArr(unit,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end="")
            print(unit)

