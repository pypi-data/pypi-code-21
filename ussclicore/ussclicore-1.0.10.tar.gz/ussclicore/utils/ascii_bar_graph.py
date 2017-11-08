__author__="UShareSoft"

def print_graph(values):
        max=0
        for v in values:
                if len(v)>max:
                        max=len(v)
        for v in values:
                value = int(values[v])
                if len(v)<max:
                        newV=v+(" " * int(max-len(v)))
                        if value!=-1:
                                print newV, value*'|'+'-'*int(50-value)
                        else:
                                print newV,20*'-'+"UNLIMITED"+21*'-'
                else:
                        if value!=-1:
                                print v, value*'|'+'-'*int(50-value)
                        else:
                                print v,20*'-'+"UNLIMITED"+21*'-'
