'''iterate print item in nested list which in another list'''

def recurseList(srcList,indent=False,level=0):
        for item in srcList:
                if isinstance(item,list):
                        recurseList(item,indent,level+1)
                else:
                        if indent:
                                for i in range(level):
                                        print('\t',end='')
                        print(item)
