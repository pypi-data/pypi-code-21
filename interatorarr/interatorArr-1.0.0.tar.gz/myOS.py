#this is a test function
def interatorArr (obj):
    for unit in obj:
        if isinstance(unit,list):
            interatorArr(unit)
        else:
            print(unit)


