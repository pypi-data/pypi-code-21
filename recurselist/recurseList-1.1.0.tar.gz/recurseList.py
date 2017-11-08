'''iterate print item in nested list which in another list'''

def recurseList(srcList,indent):
        for item in srcList:
                if isinstance(item,list):
                        recurseList(item,indent+1)
                else:
                        for l in range(indent):
                                print('\t',end='')
                        print(item)
