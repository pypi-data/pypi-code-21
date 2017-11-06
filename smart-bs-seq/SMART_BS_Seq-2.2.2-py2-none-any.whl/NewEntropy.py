#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 20131207

@author: liuhongbo
'''
import math


class Entropy():
    '''
    classdocs
    '''
    sampleNum=0
    e=0.0001
    MaxMethylationLevel=1

    def __init__(self):
        '''
        Constructor
        '''
        
    def EntropyCalculate(self,dataSet):
        Sum=0; #sum of the methylation levels
        H=0;   #Entropy value
        W=1;   #Weight for entropy
        X_New=[]  #New data set
        P_New=[]  #New possibility set 
        T_New=[]  #New possibility set 
        T=self.Tukey_biweight(dataSet) #Calculate the bi-weight for each set
#         print "bi-weight T:"+str(T)

        for i in range(len(dataSet)):
            T_New.append(abs(dataSet[i]));
            if(T_New[i]<self.e):
                T_New[i]=self.e    #Extreme small value to reduce the errors induced by multiple zero values
            
        
        
        for i in range(len(dataSet)):         #Calculate the new data set and the new sum value
            X_New.append(abs(dataSet[i]-T));
            if(X_New[i]<1.0):
                X_New[i]=1.0;    #The smallest methylation level after normalization
            Sum=Sum+X_New[i];
        
#         print "Sum:"+str(Sum)
        
        for i in range(len(dataSet)):
            P_New.append(X_New[i]/Sum);
            H=H+P_New[i]*(math.log(P_New[i],len(dataSet)));  #Calculate the entropy   
        H=-H;  #minus entropy
        if H>1.000:
            H=1.000
        MaxReal=max(dataSet);  #Max value in the set
        MinReal=min(dataSet);  #Min value in the set
        Range=(MaxReal-MinReal)/(self.MaxMethylationLevel-0.0);
        W=1-Range;   #Calculate the weight
        T=round(H*W,3);  #Calculate the weighted entropy
        if T>1:
            T=1.000
        return T;    
        
    def Tukey_biweight(self,T_New):
        c=5;        #Fold parameter
        e=0.0001;  #Extreme small value parameter
        MAD=[]
        TandU=[]  #T and Q set
        W=[]  #Weight set
        Sum=0;  #Sum
        TandU.append(0);
          
        Median=self.getMedian(T_New);    #Median value
          
        
        for i in range(len(T_New)):    
            MAD.append(abs(T_New[i]-Median))  #The distance to the median value
          
        S=self.getMedian(MAD);     #the median of the distance
          
        Fenmu=c*S+e;   #Calculate the weight
        
        for i in range(1,len(T_New)+1):    
            TandU.append((T_New[i-1]-Median)/Fenmu)
            
            
            if(abs(TandU[i])<=1):
                W.append(math.pow((1-math.pow(TandU[i],2)),2));
            else:
                W.append(0);
            Sum=Sum+W[i-1];
            TandU[0]=TandU[0]+W[i-1]*T_New[i-1];
            
            
        TandU[0]=TandU[0]/Sum;
        return TandU[0]
    
    def getMedian(self,dataSet):
        newData=[];
        for i in range(len(dataSet)):    
            newData.append(dataSet[i]);
        newData.sort()  #Sort
        if(len(dataSet)%2!=0):
            return newData[len(dataSet)/2]; ## Odd value 
        else:
            return (newData[len(dataSet)/2]+newData[len(dataSet)/2-1])/2.0; ##Even value
    
    def EntropyCalculateSet(self,dbSet):
        entropy=[]
        for i in range(len(dbSet)):
            entropy.append(self.EntropyCalculate(dbSet[i]))
        return entropy
    

if __name__ == '__main__':
    dataSet1=(60,60,60,60,60,60,60,60,60,60,60)
    dataSet2=(50,50,50,50,50,50,50,50,50,50)
    dataSet3=(90,100,96,95,94,0.36,86,94,89,96)
    dataSet4=(0.5,0.22,0.21,0.22,0.48,98,0.21,0.20,0.58,0.62)
    dataSet5=(0.05,0.022,0.021,0.022,0.048,9.8,0.021,0.02,0.058,0.062)
    dataSet6=(0.0001,0.0001,0.0001,0.0001,0.01,0.0001,0.0001,0.0001,0.0001,0.0001)
    dataSet7=(70.3,60.9,52.9,33.3,0,60.6,43.3)
    #dataSetDb=dataSet1,dataSet2,dataSet3,dataSet4,dataSet5,dataSet6,dataSet7
    C1=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C2=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C3=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C4=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C5=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C6=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C7=(100,100,100,100,100,0,100,100,100,100,100,100,100,100)
    C8=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C9=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C10=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C11=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C12=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C13=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C14=(0,100,0,0,0,0,0,0,0,0,0,0,0,0)
    C15=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C16=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C17=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C18=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C19=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    C20=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C21=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C22=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C23=(50,50,50,50,50,50,50,50,50,50,50,50,50,50)
    C24=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    C25=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    C26=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    C27=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    dataSetDb=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20,C21,C22,C23,C24,C25,C26,C27
    DM2=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM3=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM4=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM5=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM6=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM7=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM8=(100,0,0,100,100,0,100,100,100,100,100,100,100,100)
    DM9=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM10=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM11=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM12=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM13=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM14=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM15=(0,100,100,0,0,0,0,0,0,0,0,0,0,0)
    DM16=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM17=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM18=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM19=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM20=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM21=(100,100,100,100,100,100,100,100,100,100,100,100,100,100)
    DM22=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM23=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM24=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM25=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM26=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    DM27=(0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    dataSetDb1=DM2,DM3,DM4,DM5,DM6,DM7,DM8,DM9,DM10,DM11,DM12,DM13,DM14,DM15,DM16,DM17,DM18,DM19,DM20,DM21,DM22,DM23,DM24,DM25,DM26,DM27
    print "W=abs(math.log(Range,2))/abs(math.log(0.01,2))"
    print "E\tH\tRange\tW\tT"
    entropy=Entropy()
    entropy.MaxMethylationLevel=100
    print entropy.EntropyCalculateSet(dataSetDb)

        