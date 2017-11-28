#from __future__ import print_function
def ElectricField2():

    ### import numpy as np
    
    import pickle
    import matplotlib.pyplot as plt
    import numpy as np
    import math
    import matplotlib.pyplot as plt
    import collections
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.ticker import LinearLocator, FormatStrFormatter
    from IPython.display import clear_output



    from ipywidgets import interactive
    from IPython.display import display

    
    import ipywidgets as widgets

    k=9.0 *(math.pow(10,9))

    dict=collections.OrderedDict()
    dict2=collections.OrderedDict()

    n = int(input("enter number of charges "))
    x=list()
    for i in range(1,n+1):
        x.append(i)

    import numpy as np
    for i in x:
        dict['q%s_list'% i]=[]
        dict['my_qresult%s'% i]=[]
        dict['my_dresult%s'% i]=[]
    dict['q%s_list'% i]= np.array(dict['q%s_list'% i])

    %matplotlib notebook

    def on_value_change(change):
    #     clear_output()
    #     global count
    #     count = count+1
        #plt.clf()
        plt.cla()
        #plt.close()
        for i in range(1,n+1):
            dict['q%s_list'% i]=[] 
            dict['q%s_list'% i].append(dict['q%s'% i].value)
            dict['q%s_list'% i].append(dict['d%s'% i].value)
    
            #print(dict['q%s_list'% i])
        print(dict['q1_list'],dict['q2_list'],dict['q3_list'])
    
#     if count ==6*:
        

        print(dict['q1_list'],dict['q2_list'],dict['q3_list'])
        #plt.clf()
        plt.cla()
        #plt.close()  
        plot_grpah()
        plt.show()
    
        fig.canvas.draw_idle()
    
        #plt.close()



    
   
    
    fig = plt.figure(figsize=(10,4))
    for l in range(1,n+1):
    
        dict['q%s'% l] = widgets.FloatSlider(min = -0.5, max = 0.5, description =str(l)+'q')
        display(dict['q%s'% l])
        q_val=dict['q%s'% l].observe(on_value_change,names='value')
    
        dict['d%s'% l] = widgets.FloatSlider(min =-1, max = 1, description = str(l)+'d')
        display(dict['d%s'% l])
        d_val=dict['d%s'% l].observe(on_value_change,names='value')

     
    def E(lst,xd,yd):
        y = yd#float(input('Enter the y-cord of the particle: '))
        x = xd

        q=lst[0];
        d=lst[1];


        if(d==0):
            cos_theta = x/(math.pow(x**2 + y**2, 0.5))
            sin_theta = y/(math.pow(x**2 + y**2, 0.5))
            E= k*q/(x**2 + y**2)
        else:
            cos_theta = x/(math.pow(x**2 + (y-d)**2, 0.5))
            sin_theta = y-d/(math.pow(x**2 + (y-d)**2, 0.5))
            E = k*q/(x**2 + (y-d)**2)

        E_xComponent = E*cos_theta
        E_yComponent = E*sin_theta


        return [E_xComponent ,E_yComponent]  
    
    def effective2(n,x,y):
        effectiveX=0.0
        effectiveY=0.0
        for i in range(1,n+1):
            result = E(dict['q%s_list'% i],x,y)

            effectiveY +=result[1]
            effectiveX +=result[0]
            tan_theta= effectiveX/effectiveY


        res = math.pow(effectiveX**2+effectiveY**2,0.5)
        if tan_theta>0:
            res2 = math.pow(effectiveX**2+effectiveY**2,0.5)
        else:
            res2 =(-1)* math.pow(effectiveX**2+effectiveY**2,0.5)

        return [res, res2]  
    
    def plot_grpah():
        xdist= np.arange(1,8, 0.01)
        ydist= np.arange(1,8, 0.01)


        matrix = [[0 for i in range(len(xdist))] for j in range(len(ydist))]


        for i in range(len(xdist)):
            Er = list()
            matrix[i]= Er
            for j in range(len(ydist)):

                Er.append(effective2(n,xdist[i],ydist[j])[0])

        matrix = np.array(matrix)

        electric= list()
        for i in xdist:
            electric.append(effective2(n,i,j)[1])

    
    #
    
        ax = fig.add_subplot(131,projection='3d')
        X, Y = np.meshgrid(xdist, ydist)
        surf = ax.plot_surface(X, Y, matrix, cmap=cm.coolwarm,linewidth=0, antialiased=False)
    
        # Customize the z axis.
        #ax.set_zlim(-1.01, 1.01)
        ax.zaxis.set_major_locator(LinearLocator(10))
        #ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        # Add a color bar which maps values to colors.
        #fig.colorbar(surf, shrink=0.5, aspect=5)
   
        ax.set_xlabel('x co-ordinate')
        ax.set_ylabel('y co-ordinate')
        ax.set_zlabel('Electric Field')
        #plt.show()
        #plt.clf()
        #plt.cla()
        #plt.close()
        plt.subplot(132)
        plt.pcolormesh(xdist, ydist, matrix)
        ###ax.colorbar() #need a colorbar to show the intensity scale

        #plt.show()
        #plt.clf()
        #plt.cla()
        #plt.close()
        plt.subplot(133)
        plt.plot(xdist, electric)
        plt.xlabel('x co-ordinate')
        plt.ylabel('Electric field')
    
