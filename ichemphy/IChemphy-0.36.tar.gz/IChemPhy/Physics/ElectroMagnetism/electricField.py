def ElectricField():
    import numpy as np
    import math
    import matplotlib.pyplot as plt

    k=9.0 *(math.pow(10,9))

    n = int(input('Enter number of charges:'))

    for i in range(n):
        q = float(input('Enter the charge '))
        d = float(input('Enter the y-cord of the charge: '))


    
    def E(xd):
        y = 0#float(input('Enter the y-cord of the particle: '))
        x = xd

        if(d==0):
            cos_theta = x/(math.pow(x**2 + y**2, 0.5))
            sin_theta = y-d/(math.pow(x**2 + y**2, 0.5))
            E= k*q/(x**2 + y**2)
        if(d>0):
            cos_theta = x/(math.pow(x**2 + (y-d)**2, 0.5))
            sin_theta = y-d/(math.pow(x**2 + (y-d)**2, 0.5))
            E = k*q/(x**2 + (y-d)**2)
        else:
            cos_theta = x/(math.pow(x**2 + (y+d)**2, 0.5))
            sin_theta = y-d/(math.pow(x**2 + (y+d)**2, 0.5))
            E = k*q/(x**2 + (y+d)**2)
        
        E_xComponent = E*cos_theta
        E_yComponent = E*sin_theta
    
        result = list()
        result.append(E_xComponent)
        result.append(E_yComponent) 
        return result

    def effective(n,x):
        for i in range(x):
            result = E(x)
            zipped_list = zip(result)
            list= [sum(item) for item in zipped_list]
        effectiveX = list[0]
        effectiveY = list[1]
        res = math.pow(effectiveX**2+effectiveY**2,0.5)
        return res 

    xdist= np.arange(1,20,5)

    electric= list()

    for i in xdist:
        electric.append(effective(n,i))

    plt.plot(xdist, electric)
    plt.show()
