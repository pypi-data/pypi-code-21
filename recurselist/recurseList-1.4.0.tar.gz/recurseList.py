'''iterate print item in nested list which in another list'''
import sys

def recurseList(srcList,indent=False,level=0,target=sys.stdout):
        for item in srcList:
                if isinstance(item,list):
                        recurseList(item,indent,level+1,target)
                else:
                        if indent:
                                for i in range(level):
                                        print('\t',end='',file=target)
                        print(item,file=target)
