import numpy as np
import os
import madmom
import tensorflow as tf
import CSFunctions

def cross_entropy_form(pred,lab):
    out=(lab * tf.log(pred))+((1-lab)*(tf.log(1-pred)))
    return out

def cross_entropy_sig(predictions,labels):
    cost=tf.reduce_mean(-tf.reduce_sum(CSFunctions.cross_entropy_form(predictions,labels), reduction_indices=[1]))
    return cost

def mean_squared_form(pred,lab):
    out=tf.square(lab-pred)
    return out

def mean_squared(predictions,labels):
    cost=tf.reduce_mean(tf.reduce_sum(CSFunctions.mean_squared_form(predictions,labels),reduction_indices=[1]))
    return cost

def mean_squared_peak_dif_form(pred1,lab1,pred2,lab2):
    out=tf.square((lab1-lab2)-(pred1-pred2))
    return out

def HybridMS(preds,labs,batch_len,weighting):      
    stand_ms=tf.reduce_sum(CSFunctions.mean_squared_form(preds[1:-1],labs[1:-1]),reduction_indices=[1])    
    previous_ms=[(tf.reduce_sum(CSFunctions.mean_squared_peak_dif_form(preds[i],labs[i],preds[i-1],labs[i-1]))) for i in range(1,batch_len+1)]
    future_ms=[(tf.reduce_sum(CSFunctions.mean_squared_peak_dif_form(preds[i],labs[i],preds[i+1],labs[i+1]))) for i in range(1,batch_len+1)]
    total_ms=tf.reduce_mean(stand_ms+weighting*(future_ms+previous_ms))
    return total_ms

def PeakMS(preds,labs,batch_len):           
    previous_ms=[(tf.reduce_sum(CSFunctions.mean_squared_peak_dif_form(preds[i],labs[i],preds[i-1],labs[i-1]))) for i in range(1,batch_len+1)]
    future_ms=[(tf.reduce_sum(CSFunctions.mean_squared_peak_dif_form(preds[i],labs[i],preds[i+1],labs[i+1]))) for i in range(1,batch_len+1)]
    total_ms=tf.reduce_mean(future_ms+previous_ms)
    return total_ms
                
def cross_entropy_peak_dif_form(pred1,lab1,pred2,lab2):
    out=((tf.abs(lab1-lab2)*(tf.log(1-tf.abs(pred1-pred2))))+((1-tf.abs(lab1-lab2))*(tf.log(1-tf.abs(pred1-pred2)))))
    return out  

def HybridCE(preds,labs,batch_len,weighting):      
    stand_ce=-tf.reduce_sum(CSFunctions.cross_entropy_form(preds[1:-1],labs[1:-1]),reduction_indices=[1])    
    previous_ce=[(-tf.reduce_sum(CSFunctions.cross_entropy_peak_dif_form(preds[i],labs[i],preds[i-1],labs[i-1]))) for i in range(1,batch_len+1)]
    future_ce=[(-tf.reduce_sum(CSFunctions.cross_entropy_peak_dif_form(preds[i],labs[i],preds[i+1],labs[i+1]))) for i in range(1,batch_len+1)]
    total_ce=tf.reduce_mean(stand_ce+weighting*(future_ce+previous_ce))
    return total_ce

def PeakCE(preds,labs,batch_len):         
    previous_ce=[(-tf.reduce_sum(CSFunctions.cross_entropy_peak_dif_form(preds[i],labs[i],preds[i-1],labs[i-1]))) for i in range(1,batch_len+1)]
    future_ce=[(-tf.reduce_sum(CSFunctions.cross_entropy_peak_dif_form(preds[i],labs[i],preds[i+1],labs[i+1]))) for i in range(1,batch_len+1)]
    total_ce=tf.reduce_mean(future_ce+previous_ce)
    return total_ce

def meanPPmm(Track,Lambda,hop,fs,mi,ma,dif):

    m=np.mean(Track)*Lambda;
    if ma != 0:
        if m>ma:
            m=ma
    if mi != 0:
        if m<mi:
            m=mi
    TrackNew=np.zeros(len(Track)+2)
    TrackNew[1:len(Track)+1]=Track
    Track=TrackNew
    onsets=[]
    for i in range(len(Track)-2):
        if Track[i+1] > Track[i] and Track[i+1]>=Track[i+2] and Track[i+1] > m:
            onsets=np.append(onsets,i+1)
    if len(onsets) >0: 
        onsets=(onsets*hop)/float(fs)
    for i in range(1,len(onsets)):
        if abs(onsets[i]-onsets[i-1])<dif:
             np.delete(onsets,onsets[i])
  
    return onsets
 
def Fmeas(TP,FP,FN):
    if TP==0:
        if FP==0 and FN==0:
            FM=1
            Prec=1
            Rec=1
        else:
            FM=0
            Prec=0
            Rec=0            
    else:
        Prec=TP/float(TP+FP)
        Rec=TP/float(TP+FN)
        FM=2*((Prec*Rec)/float(Prec+Rec))
    return FM,Prec,Rec
            
def onsetAccuracy(peak,groundTruth,error):
       
    TP=[]
    FP=[]
    difference=[]
    if len(groundTruth.shape)>0:
        Truth=np.sort(groundTruth)
    else:
        Truth=groundTruth
    if peak!=[]:
        if len(peak.shape)>0:
            onsets=np.sort(peak)
        else:
            onsets=peak
        if len(Truth.shape)>0:
            for i in range(len(onsets)):
                counter=0
                if len(Truth) > 0:
            
                    for j in range(len(Truth)):
                        difference.append(abs(onsets[i]-Truth[j]))
                        
                    difference=np.array(difference)
                    ind=np.argmin(difference)
            
                    if difference[ind] < error:     
                        ind1=ind
                        ind2=ind+1
        
                           
                        Truth=np.concatenate((Truth[:ind1],Truth[ind2:len(Truth)]))
                        TP=np.append(TP,onsets[i])
                        counter=1
                        
                difference=[];
                if counter==0:
                    FP=np.append(FP,onsets[i])
    
        if len(Truth.shape)>0:
            FN=np.sort(Truth)
        else:
            FN=[]
    else:
        FN=range(1)
        
    return TP,FP,FN

def TrainValTestCreate(Features,Targ,GT,TrainPerc,TestPerc):
    

    leng=[]
    nums=[]
    TVtSpec=[]
    TVtTarg=[]
    TVtGT=[]
      
    leng.append(int(np.round(len(Features)*TrainPerc)))
    leng.append(int(np.round(len(Features)*TestPerc)))
    leng.append(len(Features)-leng[0]-leng[1])
    
    order=np.random.permutation(len(Features))
    nums.append(order[:leng[0]])
    nums.append(order[leng[0]:leng[0]+leng[2]])
    nums.append(order[leng[0]+leng[2]:])
    for j in range(len(nums)):
        TVtSpec.append([])
        TVtTarg.append([])
        TVtGT.append([])
        for k in nums[j]:
            TVtSpec[j].append(Features[k])
            TVtTarg[j].append(Targ[k])
            TVtGT[j].append(GT[k])
                    
    return TVtSpec, TVtTarg, TVtGT, nums
    
def signal(filenames,n_channels=1,sample_r=44100,zero_pad_shift=1024,zero_pad_hop=512):
#    signal normalised between 1 and -1 and padded
    x=[]
    for i in range(len(filenames)):
        x.append(madmom.audio.signal.Signal(filenames[i],sample_rate=sample_r,num_channels=n_channels))
        x[i]=x[i]/float(np.max(np.abs(x[i])))
        x[i]=np.pad(x[i],(zero_pad_shift,zero_pad_hop-(len(x[i])%zero_pad_hop)+zero_pad_shift),'constant',constant_values=(0,0))
    
    return x

    
def mini_batch_creation(x_len,batch_size,snippet_length,hopsize=512,mbhop=25):
#   x_len == len of wav file not spec 
    x=range((x_len/hopsize)-((x_len/hopsize)%snippet_length))
    x=[np.reshape(x,[-1,snippet_length])]
    for i in range((snippet_length/mbhop)-1):
        x.append(x[0][1:]-mbhop*(i+1))
    x=np.concatenate(x)    
    order=np.random.permutation(len(x))
    x=np.array(([x[i] for i in order]))

    return np.reshape(x[:int(np.floor(len(x)/(batch_size/snippet_length))*(batch_size/snippet_length))],[-1,batch_size])

#def sigmoid_targ_create(softmax_targ):
    
def three_targ_create_sig(TrainTarg1):
    TrainTarg=np.zeros(TrainTarg1.shape)
    for g in range(len(TrainTarg1)):
        for h in range(len(TrainTarg1[0])):
            if TrainTarg1[g,h]==1:
                TrainTarg[g,h]=1
            else:
                TrainTarg[g,h]=0
    for g in range(len(TrainTarg1)):
        for h in range(len(TrainTarg1[0])):
            if TrainTarg1[g,h]==1:
                TrainTarg[g,h]=1
                TrainTarg[g-1,h]=1
                TrainTarg[g+1,h]=1
        return TrainTarg



    


        
        
    
    
        
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
