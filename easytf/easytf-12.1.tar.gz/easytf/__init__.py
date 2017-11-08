# -*- coding: utf-8 -*-
"""
@author: CarlSouthall

"""


from __future__ import absolute_import, division, print_function

import numpy as np
import tensorflow as tf
import os
from tensorflow.contrib import rnn            
import madmom
import muda
import jams
import CSFunctions


class CNN:
    
    def __init__(self,training_data=[], training_labels=[], validation_data=[], validation_labels=[], mini_batch_locations=[], network_save_filename=[], minimum_epoch = 5, maximum_epoch = 10, learning_rate = 0.003, n_classes = 2, optimizer='Adam', conv_filter_shapes=[[5,5,1,5],[5,5,5,10]], conv_strides=[[1,1,1,1],[1,1,1,1]], pool_window_sizes=[[1,1,2,1],[1,1,2,1]], fc_layer_sizes=[100], dropout=0.25, pad='SAME', display_accuracy='True', display_train_loss='True', frames_either_side=[[2,2],[0,0]], input_stride_size=[1,1024],save_location=[],output_act='softmax',usage='simple'):
        self.usage=usage
        if self.usage=='simple':
            self.dim=str(len(training_data.shape)-1)+'d'
        elif self.usage=='timestep':
            if len(input_stride_size)==2:
                self.dim='2d'
            elif len(input_stride_size)==3:
                self.dim='3d'
        self.frames_either_side=frames_either_side 
        self.input_stride_size=input_stride_size
        if self.usage=='simple':
            self.features=training_data
            self.val=validation_data
        elif self.usage=='timestep': 
            self.features=self.zero_pad(training_data)
            self.val=self.zero_pad(validation_data)
        self.targ=training_labels     
        self.val_targ=validation_labels
        self.minibatch_nos=mini_batch_locations
        self.filename=network_save_filename
        self.minimum_epoch=minimum_epoch
        self.maximum_epoch=maximum_epoch
        self.learning_rate=learning_rate
        self.n_classes=n_classes
        self.optimizer=optimizer
        self.conv_filter_shapes=conv_filter_shapes
        self.conv_strides=conv_strides
        self.pool_window_sizes=pool_window_sizes
        self.pool_strides=self.pool_window_sizes
        self.fc_layer_sizes=fc_layer_sizes
        self.dropout=dropout
        self.pad=pad
        self.w_conv=[]
        self.b_conv=[]
        self.h_conv=[]
        self.h_pool=[]
        self.h_drop_batch=[]
        self.batch_size=self.minibatch_nos.shape[1]
        self.num_batch=self.minibatch_nos.shape[0]
        self.conv_layer_out=[]
        self.fc_layer_out=[]
        self.w_fc=[]
        self.b_fc=[]
        self.h_fc=[]
        self.output_act=output_act
        self.display_accuracy=display_accuracy
        self.display_train_loss=display_train_loss     
        if self.dim=='2d':
            if usage=='simple':
                self.batch=np.zeros((self.batch_size,self.features.shape[1],self.features.shape[2], 1))
                self.batch_targ=np.zeros((self.batch_size,self.targ.shape[len(self.targ.shape)-1]))
            
            elif usage=='timestep':
                self.batch=np.zeros((self.batch_size,(self.frames_either_side[0][0]+self.frames_either_side[0][1])+self.input_stride_size[0],(self.frames_either_side[1][0]+self.frames_either_side[1][1])+self.input_stride_size[1],1))
                self.batch_targ=np.zeros((self.batch_size,self.targ.shape[len(self.targ.shape)-1]))
            
        elif self.dim=='3d':
            self.batch=np.zeros((self.batch_size,(self.frames_either_side[0][0]+self.frames_either_side[0][1])+self.input_stride_size[0],(self.frames_either_side[1][0]+self.frames_either_side[1][1])+self.input_stride_size[1],(self.frames_either_side[2][0]+self.frames_either_side[2][1])+self.input_stride_size[2],1))
            self.batch_targ=np.zeros((self.batch_size,self.targ.shape[3]))
        self.save_location=save_location
        
    def conv2d(self,data, weights, conv_strides, pad):
      return tf.nn.conv2d(data, weights, strides=conv_strides, padding=pad)
     
    def max_pool(self,data, max_pool_window, max_strides, pad):
      return tf.nn.max_pool(data, ksize=max_pool_window,
                            strides=max_strides, padding=pad)
    
    def conv3d(self,data, weights, conv_strides, pad):
      return tf.nn.conv3d(data, weights, strides=conv_strides, padding=pad)
     
    def max_pool3d(self,data, max_pool_window, max_strides, pad):
      return tf.nn.max_pool3d(data, ksize=max_pool_window,
                            strides=max_strides, padding=pad)
        
    def weight_init(self,weight_shape):
        weight=tf.Variable(tf.truncated_normal(weight_shape))    
        return weight
        
    def bias_init(self,bias_shape,):   
        bias=tf.Variable(tf.constant(0.1, shape=bias_shape))
        return bias
    
    def batch_dropout(self,data):
        batch_mean, batch_var=tf.nn.moments(data,[0])
        scale=tf.Variable(tf.ones(data.get_shape()))
        beta=tf.Variable(tf.zeros(data.get_shape()))
        h_poolb=tf.nn.batch_normalization(data,batch_mean,batch_var,beta,scale,1e-3)
        return tf.nn.dropout(h_poolb, self.dropout_ph)
        
    def conv_2dlayer(self,layer_num):
        self.w_conv.append(self.weight_init(self.conv_filter_shapes[layer_num]))
        self.b_conv.append(self.bias_init([self.conv_filter_shapes[layer_num][3]]))
        self.h_conv.append(tf.nn.relu(self.conv2d(self.conv_layer_out[layer_num], self.w_conv[layer_num], self.conv_strides[layer_num], self.pad) + self.b_conv[layer_num]))
        self.h_pool.append(self.max_pool(self.h_conv[layer_num],self.pool_window_sizes[layer_num],self.pool_strides[layer_num],self.pad))       
        self.conv_layer_out.append(self.batch_dropout(self.h_pool[layer_num]))
    
    def conv_3dlayer(self,layer_num):
        self.w_conv.append(self.weight_init(self.conv_filter_shapes[layer_num]))
        self.b_conv.append(self.bias_init([self.conv_filter_shapes[layer_num][4]]))
        self.h_conv.append(tf.nn.relu(self.conv3d(self.conv_layer_out[layer_num], self.w_conv[layer_num], self.conv_strides[layer_num], self.pad) + self.b_conv[layer_num]))
        self.conv_layer_out.append(self.max_pool3d(self.h_conv[layer_num],self.pool_window_sizes[layer_num],self.pool_strides[layer_num],self.pad))       
        
    def fc_layer(self,layer_num):
        if layer_num ==0:
            convout=self.conv_layer_out[len(self.conv_layer_out)-1]
            self.fc_layer_out.append(tf.reshape(convout, [self.batch_size,-1]))
            flat_shape=self.fc_layer_out[0].get_shape().as_list()
            self.w_fc.append(self.weight_init([flat_shape[1], self.fc_layer_sizes[layer_num]]))
        else:
            self.w_fc.append(self.weight_init([self.fc_layer_sizes[layer_num-1], self.fc_layer_sizes[layer_num]]))
        self.b_fc.append(self.bias_init([self.fc_layer_sizes[layer_num]]))
        self.h_fc.append(tf.nn.relu(tf.matmul(self.fc_layer_out[layer_num], self.w_fc[layer_num]) + self.b_fc[layer_num]))
        self.fc_layer_out.append(self.batch_dropout(self.h_fc[layer_num]))
        
    def create(self):
         tf.reset_default_graph()
         self.x_ph = tf.placeholder(tf.float32, shape=self.batch.shape)
         self.y_ph = tf.placeholder(tf.float32, shape=self.batch_targ.shape)
         self.dropout_ph = tf.placeholder("float32")
         self.conv_layer_out.append(self.x_ph)
         for i in xrange(len(self.conv_filter_shapes)):
             if self.dim=='2d':
                 self.conv_2dlayer(i)
             elif self.dim=='3d':
                 self.conv_3dlayer(i)
         for i in xrange(len(self.fc_layer_sizes)):
             self.fc_layer(i)
         self.w_out = self.weight_init([self.fc_layer_sizes[len(self.fc_layer_sizes)-1], self.n_classes])
         self.b_out = self.bias_init([self.n_classes])
         self.presoft=tf.matmul(self.fc_layer_out[len(self.fc_layer_out)-1], self.w_out) + self.b_out
         if  self.output_act=='softmax':   
           self.pred=tf.nn.softmax(self.presoft)
           self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.presoft, labels=self.y_ph))
         elif self.output_act=='sigmoid':
           self.pred=tf.nn.sigmoid(self.presoft)
           self.cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=self.presoft, labels=self.y_ph))
         if self.optimizer == 'GD':
                self.optimize = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate).minimize(self.cost)
         elif self.optimizer == 'Adam':
                self.optimize = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.cost) 
         elif self.optimizer == 'RMS':
                self.optimize = tf.train.RMSPropOptimizer(learning_rate=self.learning_rate).minimize(self.cost) 
         self.correct_pred = tf.equal(tf.argmax(self.pred,1), tf.argmax(self.y_ph,1))
         self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
         self.init = tf.global_variables_initializer()
         self.saver = tf.train.Saver()
         self.saver_var = tf.train.Saver(tf.trainable_variables())
         self.save_location=os.getcwd()
         if self.save_location==[]:
             self.save_location=os.getcwd()
                     
    def zero_pad(self,data):
        if self.dim=='2d':
            out_data=np.zeros((data.shape[0]+self.frames_either_side[0][0]+self.frames_either_side[0][1],data.shape[1]+self.frames_either_side[1][0]+self.frames_either_side[1][1]))
            out_data[self.frames_either_side[0][0]:data.shape[0]+self.frames_either_side[0][0],self.frames_either_side[1][0]:data.shape[1]+self.frames_either_side[1][0]]=data
        elif self.dim=='3d':
            out_data=np.zeros((data.shape[0]+self.frames_either_side[0][0]+self.frames_either_side[0][1],data.shape[1]+self.frames_either_side[1][0]+self.frames_either_side[1][1],data.shape[2]+self.frames_either_side[2][0]+self.frames_either_side[2][1]))
            out_data[self.frames_either_side[0][0]:data.shape[0]+self.frames_either_side[0][0],self.frames_either_side[1][0]:data.shape[1]+self.frames_either_side[1][0],self.frames_either_side[2][0]:data.shape[2]+self.frames_either_side[2][0]]=data
        return out_data
            
    def segment_extract(self,data,targ,seg_location):
        self.seg_location=seg_location
        if self.dim=='2d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1]],2), targ[self.seg_location[0]][self.seg_location[1]]
        elif self.dim=='3d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
                self.seg_location=np.append(self.seg_location,0)
            elif len(selg.seg_location)==2:
                self.seg_location.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1],(self.seg_location[2]*self.input_stride_size[2]):(self.seg_location[2]*self.input_stride_size[2])+self.frames_either_side[2][0]+self.frames_either_side[2][1]+self.input_stride_size[2]],3), targ[self.seg_location[0]][self.seg_location[1]][self.seg_location[2]]   
        return out

    def segment_extract_test(self,data,seg_location):      
        self.seg_location=seg_location
        if self.dim=='2d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1]],2)
        elif self.dim=='3d':
            if len(selg.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
                self.seg_location=np.append(self.seg_location,0)
            elif len(selg.seg_location)==2:
                self.location.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1],(self.seg_location[2]*self.input_stride_size[2]):(self.seg_location[2]*self.input_stride_size[2])+self.frames_either_side[2][0]+self.frames_either_side[2][1]+self.input_stride_size[2]],3)
        return out

    def train(self):
#      self.create()
      self.iteration=0
      self.epoch=0
      self.prev_val_loss=100
      self.val_loss=99
      if self.usage=='simple':
          self.val_locations=self.locations_create([self.val.shape[0]])
      elif self.usage=='timestep':
          self.val_output_dim1=int(self.val.shape[0]/self.input_stride_size[0])
          self.val_output_dim2=int(self.val.shape[1]/self.input_stride_size[1])
          if self.dim=='2d':
              self.val_locations=self.locations_create([self.val_output_dim1,self.val_output_dim2])
          elif self.dim=='3d':
              self.val_output_dim3=self.val.shape[2]/self.input_stride_size[2]
              self.val_locations=self.locations_create([self.val_output_dim1,self.val_output_dim2,self.val_output_dim3])
      with tf.Session() as sess:
        sess.run(self.init)
        while self.epoch < self.minimum_epoch or self.prev_val_loss > self.val_loss:
            for i in xrange(self.num_batch):
               for j in xrange(self.batch_size):
                   if self.usage=='simple':
                        self.batch[j]=np.expand_dims(self.features[self.minibatch_nos[i][j]],2)
                        self.batch_targ[j]=self.targ[self.minibatch_nos[i][j]]
                   elif self.usage=='timestep':
                        self.batch[j],self.batch_targ[j]=self.segment_extract(self.features,self.targ,self.minibatch_nos[i][j])
               sess.run(self.optimize, feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:self.dropout})
               self.iteration+=1
            self.epoch+=1   
            print("Epoch " + str(self.epoch))
            if self.epoch > self.minimum_epoch:
                self.loss_train=[]
                self.loss_val=[]
                if self.display_accuracy=='True':
                    self.acc_train=[]
                    self.acc_val=[]
                self.val_counter=0
                for i in xrange(int(np.floor(len(self.val_locations)/self.batch_size))):
                    if self.display_accuracy=='True':
                        for j in xrange(self.batch_size):
                            if self.usage=='simple':
                                self.batch[j]=np.expand_dims(self.val[self.val_locations[(self.batch_size*self.val_counter)+j]],2)
                                self.batch_targ[j]=self.val_targ[self.val_locations[(self.batch_size*self.val_counter)+j]]

                            elif self.usage=='timestep':
                                  self.batch[j],self.batch_targ[j]=self.segment_extract(self.val,self.val_targ,self.val_locations[self.val_counter])       
                        vl,va=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1})
                        self.loss_val.append(vl)
                        self.acc_val.append(va)
                        self.val_counter+=1        
                    else:
                        for j in xrange(self.batch_size):
                            self.batch[j],self.batch_targ[j]=self.segment_extract(self.val,self.val_targ,self.val_locations[self.val_counter])
                        self.val_counter+=1            
                        self.loss_val.append(sess.run(self.cost, feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1}))
                if  self.display_train_loss=='True': 
                    for i in xrange(self.num_batch): 
                        if self.display_accuracy=='True':
                            for j in xrange(self.batch_size):
                                if self.usage=='simple':
                                     self.batch[j]=np.expand_dims(self.features[self.minibatch_nos[i][j]],2)
                                     self.batch_targ[j]=self.targ[self.minibatch_nos[i][j]]
                                elif self.usage=='timestep':
                                     self.batch[j],self.batch_targ[j]=self.segment_extract(self.features,self.targ,self.minibatch_nos[i][j])
                            tl,ta=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1})
                            self.loss_train.append(tl)
                            self.acc_train.append(ta)
                        else:
                            for j in xrange(self.batch_size):
                                self.batch[j],self.batch_targ[j]=self.segment_extract(self.features,self.targ,self.minibatch_nos[i][j])
                            self.loss_train.append(sess.run(self.cost, feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1}))
                        
                    print("Train Minibatch Loss " + "{:.6f}".format(np.mean(np.array(self.loss_train))))
                    if self.display_accuracy=='True':
                        print("Train Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_train))))
                self.prev_val_loss=self.val_loss
                self.val_loss=np.mean(np.array(self.loss_val))              
                print("Val Minibatch Loss " + "{:.6f}".format(self.val_loss))
                if self.display_accuracy=='True':
                    print("Val Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_val))))
            if self.epoch==self.maximum_epoch:
                break
        print("Optimization Finished!")
        self.saver.save(sess, self.filename)
        
        
    def locations_create(self,sizes):
        locations=[]
        if self.dim=='2d':
            if self.usage!='simple':
                for i in xrange(sizes[0]):
                    for j in xrange(sizes[1]):
                        locations.append([i,j])
            else:
                for i in xrange(sizes[0]):
                    locations.append([i])
        elif self.dim=='3d':
            for i in xrange(sizes[0]):
                for j in xrange(sizes[1]):
                    for k in xrange(sizes[2]):
                        locations.append([i,j,k])
        self.dif=len(locations)%self.batch_size
        if self.dif!=0:
            for i in xrange(self.batch_size-self.dif):
                if self.dim=='2d':
                    if self.usage!='simple':
                        locations.append([0,0])
                    else:
                        locations.append([0])
                elif self.dim=='3d':
                    locations.append([0,0,0])        
        return np.squeeze(np.array(locations))
                   
    def implement(self,data,):
        with tf.Session() as sess:
            self.saver.restore(sess, self.save_location+'/'+self.filename)
            self.output=[]            
            for i in xrange(len(data)):
                if self.usage=='simple':
                    self.locations=self.locations_create([len(data[i])])
                    self.output.append(np.zeros((len(data[i]),self.n_classes)))
                else:
                    self.outputdim1=int(data[i].shape[0]/self.input_stride_size[0])
                    self.outputdim2=int(data[i].shape[1]/self.input_stride_size[1])
                    if self.dim=='2d':
                        self.output.append(np.zeros((self.outputdim1,self.outputdim2,self.n_classes)))
                    elif self.dim=='3d':
                        self.outputdim3=int(data[i].shape[2]/self.input_stride_size[2])
                        self.output.append(np.zeros((self.outputdim1,self.outputdim2,self.outputdim3,self.n_classes)))
                    data[i]=self.zero_pad(data[i])
                    if self.dim=='2d':
                        self.locations=self.locations_create([self.outputdim1,self.outputdim2])
                    elif self.dim=='3d':
                        self.locations=self.locations_create([self.outputdim1,self.outputdim2,self.outputdim3])
                self.counter=0
                for j in xrange(int(len(self.locations)/self.batch_size)):
                    for z in xrange(self.batch_size):
                            if self.usage=='simple':
                                self.batch[z]=np.expand_dims(data[i][self.locations[self.counter]],2)
                            else:
                                self.batch[z]=self.segment_extract_test(data[i],self.locations[self.counter])                 
                            self.counter+=1
                    batch_out=sess.run(self.pred, feed_dict={self.x_ph: self.batch, self.dropout_ph:1})
                    
                    if j == len(self.locations)/self.batch_size:
                        implement_length=self.dif
                    else:
                        implement_length=self.batch_size
                    for z in xrange(implement_length):
                        if self.usage=='simple':    
                            self.output[i][self.locations[self.counter-self.batch_size+z]]=batch_out[z]
                        else:
                            if self.dim=='2d':
                                self.output[i][self.locations[self.counter-self.batch_size+z][0],self.locations[self.counter-self.batch_size+z][1]]=batch_out[z] 
                            elif self.dim=='3d':
                                self.output[i][self.locations[self.counter-self.batch_size+z][0],self.locations[self.counter-self.batch_size+z][1],self.locations[self.counter-self.batch_size+z][2]]=batch_out[z]
            return self.output


class SA:
     
     def __init__(self,training_data=[], training_labels=[], validation_data=[], validation_labels=[], mini_batch_locations=[], network_save_filename=[], minimum_epoch=5, maximum_epoch=10, n_hidden=[100,100], n_classes=2, cell_type='LSTMP', configuration='B', attention_number=2, dropout=0.75, init_method='zero', truncated=1000, optimizer='Adam', learning_rate=0.003 ,display_train_loss='True', display_accuracy='True',save_location=[],output_act='sigmoid',snippet_length=100,aug_prob=0,hop_size=512, cost_type='CE',num_frames_either_side=0):         
         self.features=training_data
         self.targ=training_labels
         self.val=validation_data
         self.val_targ=validation_labels
         self.mini_batch_locations=mini_batch_locations
         self.filename=network_save_filename
         self.n_hidden=n_hidden
         self.n_layers=len(self.n_hidden)
         self.cell_type=cell_type
         self.dropout=dropout
         self.configuration=configuration
         self.init_method=init_method
         self.truncated=truncated
         self.optimizer=optimizer
         self.learning_rate=learning_rate
         self.n_classes=n_classes
         self.minimum_epoch=minimum_epoch
         self.maximum_epoch=maximum_epoch
         self.display_train_loss=display_train_loss
         self.num_batch=len(self.mini_batch_locations)
         self.batch_size=self.mini_batch_locations.shape[1]
         self.attention_number=attention_number
         self.display_accuracy=display_accuracy
         self.cost_type=cost_type
         self.nfes=num_frames_either_side
         if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
             self.batch=np.zeros((self.batch_size+2,84*((2*self.nfes)+1)))
             self.batch_targ=np.zeros((self.batch_size+2,self.n_classes))
         else:
            self.batch=np.zeros((self.batch_size,84*((2*self.nfes)+1)))
            self.batch_targ=np.zeros((self.batch_size,self.n_classes))
         self.save_location=save_location
         self.output_act=output_act
         self.snippet_length=snippet_length
         self.aug_prob=aug_prob
         self.hop_size=hop_size

     def cell_create(self,scope_name):
         with tf.variable_scope(scope_name):
             if self.cell_type == 'tanh':
                 cells = rnn.MultiRNNCell([rnn.BasicRNNCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             elif self.cell_type == 'LSTM': 
                 cells = rnn.MultiRNNCell([rnn.BasicLSTMCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             elif self.cell_type == 'GRU':
                 cells = rnn.MultiRNNCell([rnn.GRUCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             elif self.cell_type == 'LSTMP':
                 cells = rnn.MultiRNNCell([rnn.LSTMCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             cells = rnn.DropoutWrapper(cells, input_keep_prob=self.dropout_ph,output_keep_prob=self.dropout_ph) 
         return cells
     
     def weight_bias_init(self):
               
         if self.init_method=='zero':
            self.biases = tf.Variable(tf.zeros([self.n_classes]))           
         elif self.init_method=='norm':
               self.biases = tf.Variable(tf.random_normal([self.n_classes]))           
         if self.configuration =='B':
             if self.init_method=='zero':  
                 self.weights =tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*2, self.n_classes]))
             elif self.init_method=='norm':
                   self.weights = { '1': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes])),'2': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes]))} 
         if self.configuration =='R':
             if self.init_method=='zero':  
                 self.weights = tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes]))     
             elif self.init_method=='norm':
                   self.weights = tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes]))
                   
     def cell_create_norm(self):
         if self.cell_type == 'tanh':
             cells = rnn.MultiRNNCell([rnn.BasicRNNCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
         elif self.cell_type == 'LSTM': 
             cells = rnn.MultiRNNCell([rnn.BasicLSTMCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
         elif self.cell_type == 'GRU':
             cells = rnn.MultiRNNCell([rnn.GRUCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
         elif self.cell_type == 'LSTMP':
             cells = rnn.MultiRNNCell([rnn.LSTMCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
         cells = rnn.DropoutWrapper(cells, input_keep_prob=self.dropout_ph,output_keep_prob=self.dropout_ph) 
         return cells
     
     def weight_bias_init_norm(self):
               
         if self.init_method=='zero':
            self.biases = tf.Variable(tf.zeros([self.n_classes]))           
         elif self.init_method=='norm':
               self.biases = tf.Variable(tf.random_normal([self.n_classes]))           
         if self.configuration =='B':
             if self.init_method=='zero':  
                 self.weights = { '1': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*(((self.attention_number*2)+1)), self.n_classes])),'2': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*(((self.attention_number*2)+1)), self.n_classes]))}     
             elif self.init_method=='norm':
                   self.weights = { '1': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*(((self.attention_number*2)+1)), self.n_classes])),'2': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*(((self.attention_number*2)+1)), self.n_classes]))} 
         if self.configuration =='R':
             if self.init_method=='zero':  
                 self.weights = tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*(((self.attention_number)+1)), self.n_classes]))     
             elif self.init_method=='norm':
                   self.weights = tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*(((self.attention_number)+1)), self.n_classes]))
                 
      
     def attention_weight_init(self,num):
         if num==0:
             self.attention_weights=[tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*4,self.n_hidden[(len(self.n_hidden)-1)]*2]))]
             self.sm_attention_weights=[tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*2,self.n_hidden[(len(self.n_hidden)-1)]*2]))]
         if num>0:
             self.attention_weights.append(tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*4,self.n_hidden[(len(self.n_hidden)-1)]*2])))
             self.sm_attention_weights.append(tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*2,self.n_hidden[(len(self.n_hidden)-1)]*2])))
             
     def create(self):
       
       tf.reset_default_graph()
       self.x_ph = tf.placeholder("float32", [1, self.batch.shape[0], self.batch.shape[1]])
       self.y_ph = tf.placeholder("float32", self.batch_targ.shape)
       self.seq=tf.constant(self.truncated,shape=[1])
       self.seq2=tf.constant(self.truncated,shape=[1]) 
       self.dropout_ph = tf.placeholder("float32")
       if self.attention_number==0:
           self.fw_cell=self.cell_create_norm()
           self.weight_bias_init_norm()
       elif self.attention_number>0:
           self.fw_cell=self.cell_create('1')
           self.fw_cell2=self.cell_create('2')
           self.weight_bias_init()
       else:
           print('negative attention numbers not allowd')
       if self.configuration=='R':
           print('no attention for R models yet')
           self.outputs, self.states= tf.nn.dynamic_rnn(self.fw_cell, self.x_ph,
                                             sequence_length=self.seq,dtype=tf.float32)
           self.presoft=tf.matmul(self.outputs[0][0], self.weights) + self.biases
       elif self.configuration=='B':           
           if self.attention_number==0:
               self.bw_cell=self.cell_create_norm()
               self.outputs, self.states= tf.nn.bidirectional_dynamic_rnn(self.fw_cell, self.bw_cell, self.x_ph,
                                         sequence_length=self.seq,dtype=tf.float32)
               self.presoft=tf.matmul(self.outputs[0][0], self.weights['1']) + tf.matmul(self.outputs[1][0], self.weights['2'])+self.biases
           elif self.attention_number>0:
               self.bw_cell=self.cell_create('1')
               self.bw_cell2=self.cell_create('2')
               with tf.variable_scope('1'):
                   self.outputs, self.states= tf.nn.bidirectional_dynamic_rnn(self.fw_cell, self.bw_cell, self.x_ph,
                                                 sequence_length=self.seq,dtype=tf.float32)
                                                  
               self.first_out=tf.concat((self.outputs[0],self.outputs[1]),2)
               with tf.variable_scope('2'):
                   self.outputs2, self.states2= tf.nn.bidirectional_dynamic_rnn(self.fw_cell2, self.bw_cell2, self.first_out,
                                                     sequence_length=self.seq2,dtype=tf.float32)
               self.second_out=tf.concat((self.outputs2[0],self.outputs2[1]),2)
                
               for i in range((self.attention_number*2)+1):
                   self.attention_weight_init(i)
                    
               self.zero_pad_second_out=tf.pad(tf.squeeze(self.second_out),[[self.attention_number,self.attention_number],[0,0]])
    #               self.attention_chunks.append(self.zero_pad_second_out[j:j+attention_number*2])
               if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                   self.attention_m=[tf.tanh(tf.matmul(tf.concat((self.zero_pad_second_out[j:j+self.batch_size+2],tf.squeeze(self.first_out)),1),self.attention_weights[j])) for j in range((self.attention_number*2)+1)]
               else:
                   self.attention_m=[tf.tanh(tf.matmul(tf.concat((self.zero_pad_second_out[j:j+self.batch_size],tf.squeeze(self.first_out)),1),self.attention_weights[j])) for j in range((self.attention_number*2)+1)]
               self.attention_s=tf.nn.softmax(tf.stack([tf.matmul(self.attention_m[i],self.sm_attention_weights[i]) for i in range(self.attention_number*2+1)]),0)
               if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                   self.attention_z=tf.reduce_sum([self.attention_s[i]*self.zero_pad_second_out[i:self.batch_size+i+2] for i in range(self.attention_number*2+1)],0)
               else:
                   self.attention_z=tf.reduce_sum([self.attention_s[i]*self.zero_pad_second_out[i:self.batch_size+i] for i in range(self.attention_number*2+1)],0)
               self.presoft=tf.matmul(self.attention_z,self.weights)+self.biases

       if  self.output_act=='softmax':   
           self.pred=tf.nn.softmax(self.presoft)
           self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.presoft, labels=self.y_ph))
       elif self.output_act=='sigmoid':
           self.pred=tf.nn.sigmoid(self.presoft)
           if self.cost_type=='CE':
               self.cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=self.presoft, labels=self.y_ph))
           elif self.cost_type=='MS':
               self.cost=tf.reduce_mean(tf.losses.mean_squared_error(labels=self.y_ph,predictions=self.pred))
           elif self.cost_type=='CECS':
               self.cost=tf.reduce_mean(CSFunctions.cross_entropy_sig(predictions=self.pred,labels=self.y_ph))
           elif self.cost_type=='MSCS':
               self.cost=tf.reduce_mean(CSFunctions.mean_squared(predictions=self.pred,labels=self.y_ph))
           elif self.cost_type=='HybridCE1':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1)               
           elif self.cost_type=='HybridMS1':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1) 
           elif self.cost_type=='HybridCE2':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1/2.)               
           elif self.cost_type=='HybridMS2':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1/2.) 
           elif self.cost_type=='HybridCE3':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1/3.)               
           elif self.cost_type=='HybridMS3':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1/3.) 
           elif self.cost_type=='HybridCE4':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1/4.)               
           elif self.cost_type=='HybridMS4':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1/4.) 
           elif self.cost_type=='PeakCE':
               self.cost=CSFunctions.PeakCE(self.pred,self.y_ph,self.batch_size)  
           elif self.cost_type=='PeakMS':
               self.cost=CSFunctions.PeakMS(self.pred,self.y_ph,self.batch_size)  
               
       if self.optimizer == 'GD':
             self.optimize = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate).minimize(self.cost)
       elif self.optimizer == 'Adam':
             self.optimize = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.cost) 
       elif self.optimizer == 'RMS':
             self.optimize = tf.train.RMSPropOptimizer(learning_rate=self.learning_rate).minimize(self.cost) 
       self.correct_pred = tf.equal(tf.argmax(self.pred,1), tf.argmax(self.y_ph,1))
       self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
       self.init = tf.global_variables_initializer()
       self.saver = tf.train.Saver()
       self.saver_var = tf.train.Saver(tf.trainable_variables())
       if self.save_location==[]:
           self.save_location=os.getcwd()
           
     def augmentation(self,audio_data,aug_limit=0.5):
        if abs(np.random.randn(1))<aug_limit:
            jam = jams.JAMS()
            j_orig = muda.jam_pack(jam, _audio=dict(y=np.array(audio_data), sr=44100))
        
            pitch=int(np.round((np.random.rand(1)*2-1)*12))
            noise=(np.random.randint(1,6)/20.)
             
            pitchs = muda.deformers.LinearPitchShift(n_samples=1, lower=pitch-0.0001, upper=pitch+0.0001)
            noises = muda.deformers.BackgroundNoise(n_samples=1,files='MudaWhiteNoiseGaussian.wav',weight_min=noise-0.00001, weight_max=noise+0.00001)
         
            pipeline = muda.Pipeline(steps=[('pitch_shift', pitchs),
                                            ('noise',noises)])
            y=list(pipeline.transform(j_orig))

            y=y[0].sandbox.muda._audio['y']
        else:
            y=audio_data
        return y   
            
     def locations_create(self,size):
         self.locations=range(int(size/self.hop_size))
         self.location_new=np.reshape(self.locations,[-1,self.batch_size])     
         return self.location_new
        
     def train(self):
        
#       self.create()
       self.iteration=0
       self.epoch=0
       self.prev_val_loss=100
       self.val_loss=99
       self.val=np.concatenate((self.val,np.zeros((self.batch_size*self.hop_size)-(len(self.val)%(self.batch_size*self.hop_size)))))
       if self.output_act=='softmax':
           self.val_targ=np.concatenate((self.val_targ,np.concatenate((np.zeros(((len(self.val)/self.hop_size)-len(self.val_targ),1)),np.ones(((len(self.val)/self.hop_size)-len(self.val_targ),1))),1)))
       elif self.output_act=='sigmoid':
           self.val_targ=np.concatenate((self.val_targ,np.zeros((int((len(self.val)/self.hop_size)-len(self.val_targ)),3))))
       with tf.Session() as sess:
         sess.run(self.init)
         if self.nfes>0:
             while self.epoch < self.minimum_epoch or self.prev_val_loss > self.val_loss:
                 for i in xrange(self.num_batch):
                    for j in xrange(int(self.batch_size)):
                        start=(self.mini_batch_locations[i,j]-self.nfes)*self.hop_size
                        sc=0
                        if start<0:
                            start=0
                            sc=1
                        end=(self.mini_batch_locations[i,j]+1+self.nfes)*self.hop_size
                        ec=0
                        if end>(len(self.features)):
                            end=len(self.features)
                            ec=1
                        self.batch_wav=self.features[start:end]
                        if sc==1:
                            self.batch_wav=np.pad(self.batch_wav,[((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0],0],'constant',constant_values=[0])
                        if ec==1:
                            self.batch_wav=np.pad(self.batch_wav,[0,((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0]],'constant',constant_values=[0])
                        self.batch_wav_post_aug=self.augmentation(self.batch_wav,self.aug_prob)
                        if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                            self.batch[j+1]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                            self.batch_targ[j+1]=self.targ[self.mini_batch_locations[i,j]]
                        else:
                            self.batch[j]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                            self.batch_targ[j]=self.targ[self.mini_batch_locations[i,j]]
                     
                    sess.run(self.optimize, feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ,self.dropout_ph:self.dropout})
                                         
                    self.iteration+=1
                 print("Epoch " + str(self.epoch))
                 self.epoch+=1  
                 if self.epoch > self.minimum_epoch:
                     self.loss_train=[]
                     self.loss_val=[]
                     if self.display_accuracy=='True':
                         self.acc_train=[]
                         self.acc_val=[]
                     for i in xrange(int(len(self.val)/(self.hop_size*self.batch_size))):
                         for j in range(int(self.batch_size)):
                            start=(((i*self.batch_size)+j)-self.nfes)*self.hop_size
                            sc=0
                            if start<0:
                                start=0
                                sc=1
                            end=(((i*self.batch_size)+j)+1+self.nfes)*self.hop_size
                            ec=0
                            if end>(len(self.val)):
                                end=len(self.val)
                                ec=1
                            self.batch_wav=self.val[start:end]
                            if sc==1:
                                self.batch_wav=np.pad(self.batch_wav,[((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0],0],'constant',constant_values=[0])
                            if ec==1:
                                self.batch_wav=np.pad(self.batch_wav,[0,((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0]],'constant',constant_values=[0])
                            self.batch_wav_post_aug=self.augmentation(self.batch_wav,0)
                            if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                self.batch[j+1]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                                self.batch_targ[j+1]=self.val_targ[((i*self.batch_size)+j)]
                            else:
                                self.batch[j]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                                self.batch_targ[j]=self.val_targ[((i*self.batch_size)+j)]
                            if self.display_accuracy=='True':
                                 vl,va=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1})
                                 self.loss_val.append(vl)
                                 self.acc_val.append(va)
                            else:
                                 self.loss_val.append(sess.run(self.cost, feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1}))
                     if  self.display_train_loss=='True': 
                         for i in xrange(self.num_batch):
                             for j in range(int(self.batch_size)):
                                start=(((i*self.batch_size)+j)-self.nfes)*self.hop_size
                                sc=0
                                if start<0:
                                    start=0
                                    sc=1
                                end=(((i*self.batch_size)+j)+1+self.nfes)*self.hop_size
                                ec=0
                                if end>(len(self.features)):
                                    end=len(self.features)
                                    ec=1
                                self.batch_wav=self.features[start:end]
                                if sc==1:
                                    self.batch_wav=np.pad(self.batch_wav,[((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0],0],'constant',constant_values=[0])
                                if ec==1:
                                    self.batch_wav=np.pad(self.batch_wav,[0,((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0]],'constant',constant_values=[0])
                                self.batch_wav_post_aug=self.augmentation(self.batch_wav,0)
                                if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                    self.batch[j+1]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                                    self.batch_targ[j+1]=self.targ[((i*self.batch_size)+j)]
                                else:
                                    self.batch[j]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                                    self.batch_targ[j]=self.targ[((i*self.batch_size)+j)]
                         if self.display_accuracy=='True':
                                 tl,ta=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1})
                                 self.loss_train.append(tl)
                                 self.acc_train.append(ta)
                         else:
                                 self.loss_train.append(sess.run(self.cost, feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1}))
                             
                         print("Train Minibatch Loss " + "{:.6f}".format(np.mean(np.array(self.loss_train))))
                         if self.display_accuracy=='True':
                             print("Train Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_train))))
                     self.prev_val_loss=self.val_loss
                     self.val_loss=np.mean(np.array(self.loss_val))              
                     print("Val Minibatch Loss " + "{:.6f}".format(self.val_loss))
                     if self.display_accuracy=='True':
                         print("Val Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_val))))
                 if self.epoch==self.maximum_epoch:
                     break
             print("Optimization Finished!")
             self.saver.save(sess, self.filename)
         else:
             while self.epoch < self.minimum_epoch or self.prev_val_loss > self.val_loss:
                 for i in xrange(self.num_batch):
                    for j in xrange(int(self.batch_size/self.snippet_length)):
                        self.batch_wav=self.features[self.mini_batch_locations[i,j*self.snippet_length]*self.hop_size:((self.mini_batch_locations[i,(((j+1)*self.snippet_length)-1)]+1)*self.hop_size)]
                        self.batch_wav_post_aug=self.augmentation(self.batch_wav,self.aug_prob)
                        if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                            self.batch[(j*self.snippet_length)+1:((j+1)*self.snippet_length)+1]=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                            self.batch_targ[(j*self.snippet_length)+1:((j+1)*self.snippet_length)+1]=self.targ[self.mini_batch_locations[i,j*self.snippet_length]:self.mini_batch_locations[i,((j+1)*self.snippet_length)-1]+1]
                        else:
                            self.batch[j*self.snippet_length:(j+1)*self.snippet_length]=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                            self.batch_targ[j*self.snippet_length:(j+1)*self.snippet_length]=self.targ[self.mini_batch_locations[i,j*self.snippet_length]:self.mini_batch_locations[i,((j+1)*self.snippet_length)-1]+1]
                     
                    sess.run(self.optimize, feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ,self.dropout_ph:self.dropout})
                                         
                    self.iteration+=1
                 print("Epoch " + str(self.epoch))
                 self.epoch+=1  
                 if self.epoch > self.minimum_epoch:
                     self.loss_train=[]
                     self.loss_val=[]
                     if self.display_accuracy=='True':
                         self.acc_train=[]
                         self.acc_val=[]
                     for i in xrange(int(len(self.val)/(self.hop_size*self.batch_size))):
                         if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                             self.batch[1:self.batch_size+1]=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.val[(self.batch_size*self.hop_size)*i:(self.batch_size*self.hop_size)*(i+1)],hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                             self.batch_targ[1:self.batch_size+1]=self.val_targ[self.batch_size*i:self.batch_size*(i+1)]
                         else:
                             self.batch=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.val[(self.batch_size*self.hop_size)*i:(self.batch_size*self.hop_size)*(i+1)],hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                             self.batch_targ=self.val_targ[self.batch_size*i:self.batch_size*(i+1)]
                         if self.display_accuracy=='True':
                             vl,va=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1})
                             self.loss_val.append(vl)
                             self.acc_val.append(va)
                         else:
                             self.loss_val.append(sess.run(self.cost, feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1}))
                     if  self.display_train_loss=='True': 
                         for i in xrange(self.num_batch):
                            for j in xrange(int(self.batch_size/self.snippet_length)):
                                if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                    self.batch[(j*self.snippet_length)+1:((j+1)*self.snippet_length)+1]=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.features[self.mini_batch_locations[i,j*self.snippet_length]*self.hop_size:((self.mini_batch_locations[i,(((j+1)*self.snippet_length)-1)]+1)*self.hop_size)],hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                                    self.batch_targ[(j*self.snippet_length)+1:((j+1)*self.snippet_length)+1]=self.targ[self.mini_batch_locations[i,j*self.snippet_length]:self.mini_batch_locations[i,((j+1)*self.snippet_length)-1]+1]
                                else:    
                                    self.batch[j*self.snippet_length:(j+1)*self.snippet_length]=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.features[self.mini_batch_locations[i,j*self.snippet_length]*self.hop_size:((self.mini_batch_locations[i,(((j+1)*self.snippet_length)-1)]+1)*self.hop_size)],hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                                    self.batch_targ[j*self.snippet_length:(j+1)*self.snippet_length]=self.targ[self.mini_batch_locations[i,j*self.snippet_length]:self.mini_batch_locations[i,((j+1)*self.snippet_length)-1]+1]
                            if self.display_accuracy=='True':
                                 tl,ta=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1})
                                 self.loss_train.append(tl)
                                 self.acc_train.append(ta)
                            else:
                                 self.loss_train.append(sess.run(self.cost, feed_dict={self.x_ph: np.expand_dims(self.batch,0), self.y_ph: self.batch_targ, self.dropout_ph:1}))
                             
                         print("Train Minibatch Loss " + "{:.6f}".format(np.mean(np.array(self.loss_train))))
                         if self.display_accuracy=='True':
                             print("Train Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_train))))
                     self.prev_val_loss=self.val_loss
                     self.val_loss=np.mean(np.array(self.loss_val))              
                     print("Val Minibatch Loss " + "{:.6f}".format(self.val_loss))
                     if self.display_accuracy=='True':
                         print("Val Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_val))))
                 if self.epoch==self.maximum_epoch:
                     break
             print("Optimization Finished!")
             self.saver.save(sess, self.filename)
          
         
     def implement(self,data):
         with tf.Session() as sess:
             self.saver.restore(sess, self.save_location+'/'+self.filename)
             self.test_out=[];
             for i in range(len(data)):
                 self.test_len=int(np.ceil(len(data[i])/float(self.hop_size)))
                 self.test_features=np.concatenate((data[i],np.zeros((self.batch_size*self.hop_size)-(len(data[i])%(self.batch_size*self.hop_size)))))
                 if self.nfes>0:
                     for k in range(int(len(self.test_features)/(self.hop_size*self.batch_size))):
                         for j in range(int(self.batch_size)):
                                start=(((k*self.batch_size)+j)-self.nfes)*self.hop_size
                                sc=0
                                if start<0:
                                    start=0 
                                    sc=1
                                end=(((k*self.batch_size)+j)+1+self.nfes)*self.hop_size
                                ec=0
                                if end>(len(self.test_features)):
                                    end=len(self.test_features)
                                    ec=1
                                self.batch_wav=self.test_features[start:end]
                                if sc==1:
                                    self.batch_wav=np.pad(self.batch_wav,[((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0],0],'constant',constant_values=[0])
                                if ec==1:
                                    self.batch_wav=np.pad(self.batch_wav,[0,((1+(2*self.nfes))*self.hop_size)-tf.shape(self.batch_wav)[0]],'constant',constant_values=[0])
                                self.batch_wav_post_aug=self.augmentation(self.batch_wav,0)
                                if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                    self.batch[j+1]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                                else:
                                    self.batch[j]=np.reshape(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),[-1])
                         if k == 0:
                                 if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                     self.test_out.append(sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1})[1:self.batch_size-1])
                                 else:
                                     self.test_out.append(sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1}))                                    
                         elif k > 0:
                                if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                    self.test_out_2=sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1})[1:self.batch_size-1]
                                else:
                                    self.test_out_2=sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1})
                                self.test_out[i]=np.concatenate((self.test_out[i],self.test_out_2),axis=0)
                     self.test_out[i]=self.test_out[i][:self.test_len]
                 else:
                     for k in range(int(len(self.test_features)/(self.hop_size*self.batch_size))):
                        if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                            self.batch[1:self.batch_size+1]=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.test_features[(self.batch_size*self.hop_size)*k:(self.batch_size*self.hop_size)*(k+1)],hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                        else:
                            self.batch=madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.test_features[(self.batch_size*self.hop_size)*k:(self.batch_size*self.hop_size)*(k+1)],hop_size=512,sample_rate=44100,fmin=20,fmax=20000)
                        if k == 0:
                             if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                 self.test_out.append(sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1})[1:self.batch_size-1])
                             else:
                                 self.test_out.append(sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1}))                                    
                        elif k > 0:
                            if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                self.test_out_2=sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1})[1:self.batch_size-1]
                            else:
                                self.test_out_2=sess.run(self.pred, feed_dict={self.x_ph: np.expand_dims(self.batch,0),self.dropout_ph:1})
                            self.test_out[i]=np.concatenate((self.test_out[i],self.test_out_2),axis=0)
                     self.test_out[i]=self.test_out[i][:self.test_len]
                  
         return self.test_out


class RSACNN:
    
    def __init__(self,training_data=[], training_labels=[], validation_data=[], validation_labels=[], mini_batch_locations=[], network_save_filename=[], minimum_epoch = 5, maximum_epoch = 10, conv_filter_shapes=[[3,3,1,10],[3,3,10,20]], conv_strides=[[1,1,1,1],[1,1,1,1]], pool_window_sizes=[[1,1,2,1],[1,1,2,1]], dropout=0.75, pad='SAME', frames_either_side=[[2,2],[0,0]], input_stride_size=[1,1024],usage='timestep',n_hidden=[100,100], n_classes=3, cell_type='LSTMP', configuration='B', pc_number=2,  init_method='zero', truncated=1000, optimizer='Adam', learning_rate=0.003 ,display_train_loss='True', display_accuracy='True',save_location=[],output_act='sigmoid',aug_prob=0,cost_type='CE'):
        self.usage=usage
        if self.usage=='simple':
            self.dim=str(len(training_data.shape)-1)+'d'
        elif self.usage=='timestep':
            if len(input_stride_size)==2:
                self.dim='2d'
            elif len(input_stride_size)==3:
                self.dim='3d'
        self.frames_either_side=frames_either_side 
        self.input_stride_size=input_stride_size
        if self.usage=='simple':
            self.features=training_data
            self.val=validation_data
        elif self.usage=='timestep': 
            self.features=self.zero_pad(training_data)
            self.val=self.zero_pad(validation_data)
        self.targ=training_labels     
        self.val_targ=validation_labels
        self.minibatch_nos=mini_batch_locations
        self.filename=network_save_filename
        self.minimum_epoch=minimum_epoch
        self.maximum_epoch=maximum_epoch
        self.learning_rate=learning_rate
        self.n_classes=n_classes
        self.optimizer=optimizer
        self.conv_filter_shapes=conv_filter_shapes
        self.conv_strides=conv_strides
        self.pool_window_sizes=pool_window_sizes
        self.pool_strides=self.pool_window_sizes
        self.dropout=dropout
        self.pad=pad
        self.w_conv=[]
        self.b_conv=[]
        self.h_conv=[]
        self.h_pool=[]
        self.h_drop_batch=[]
        self.batch_size=self.minibatch_nos.shape[1]
        self.num_batch=self.minibatch_nos.shape[0]
        self.conv_layer_out=[]
        self.fc_layer_out=[]
        self.w_fc=[]
        self.b_fc=[]
        self.h_fc=[]
        self.output_act=output_act
        self.display_accuracy=display_accuracy
        self.display_train_loss=display_train_loss 
        self.cost_type=cost_type
        if self.dim=='2d':
            if usage=='simple':
                self.batch=np.zeros((self.batch_size,self.features.shape[1],self.features.shape[2], 1))
                self.batch_targ=np.zeros((self.batch_size,self.targ.shape[len(self.targ.shape)-1]))
            
            elif usage=='timestep':
                 if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                        self.batch=np.zeros((self.batch_size+2,(self.frames_either_side[0][0]+self.frames_either_side[0][1])+self.input_stride_size[0],(self.frames_either_side[1][0]+self.frames_either_side[1][1])+self.input_stride_size[1],1))
                        self.batch_targ=np.zeros((self.batch_size+2,n_classes))
                 else:
                        self.batch=np.zeros((self.batch_size,(self.frames_either_side[0][0]+self.frames_either_side[0][1])+self.input_stride_size[0],(self.frames_either_side[1][0]+self.frames_either_side[1][1])+self.input_stride_size[1],1))
                        self.batch_targ=np.zeros((self.batch_size,n_classes))
            
        elif self.dim=='3d':
            self.batch=np.zeros((self.batch_size,(self.frames_either_side[0][0]+self.frames_either_side[0][1])+self.input_stride_size[0],(self.frames_either_side[1][0]+self.frames_either_side[1][1])+self.input_stride_size[1],(self.frames_either_side[2][0]+self.frames_either_side[2][1])+self.input_stride_size[2],1))
            self.batch_targ=np.zeros((self.batch_size,self.targ.shape[3]))
        self.save_location=save_location
        self.aug_prob=aug_prob
        
               
        self.n_hidden=n_hidden
        self.n_layers=len(self.n_hidden)
        self.cell_type=cell_type
        self.configuration=configuration
        self.init_method=init_method
        self.truncated=truncated
        self.attention_number=pc_number
         
    def conv2d(self,data, weights, conv_strides, pad):
      return tf.nn.conv2d(data, weights, strides=conv_strides, padding=pad)
     
    def max_pool(self,data, max_pool_window, max_strides, pad):
      return tf.nn.max_pool(data, ksize=max_pool_window,
                            strides=max_strides, padding=pad)
    
    def conv3d(self,data, weights, conv_strides, pad):
      return tf.nn.conv3d(data, weights, strides=conv_strides, padding=pad)
     
    def max_pool3d(self,data, max_pool_window, max_strides, pad):
      return tf.nn.max_pool3d(data, ksize=max_pool_window,
                            strides=max_strides, padding=pad)
        
    def weight_init(self,weight_shape):
        weight=tf.Variable(tf.truncated_normal(weight_shape))    
        return weight
        
    def bias_init(self,bias_shape,):   
        bias=tf.Variable(tf.constant(0.1, shape=bias_shape))
        return bias
    
    def batch_dropout(self,data):
        batch_mean, batch_var=tf.nn.moments(data,[0])
        scale=tf.Variable(tf.ones(data.get_shape()))
        beta=tf.Variable(tf.zeros(data.get_shape()))
        h_poolb=tf.nn.batch_normalization(data,batch_mean,batch_var,beta,scale,1e-3)
        return tf.nn.dropout(h_poolb, self.dropout_ph)
        
    def conv_2dlayer(self,layer_num):
        self.w_conv.append(self.weight_init(self.conv_filter_shapes[layer_num]))
        self.b_conv.append(self.bias_init([self.conv_filter_shapes[layer_num][3]]))
        self.h_conv.append(tf.nn.relu(self.conv2d(self.conv_layer_out[layer_num], self.w_conv[layer_num], self.conv_strides[layer_num], self.pad) + self.b_conv[layer_num]))
        self.h_pool.append(self.max_pool(self.h_conv[layer_num],self.pool_window_sizes[layer_num],self.pool_strides[layer_num],self.pad))       
        self.conv_layer_out.append(self.batch_dropout(self.h_pool[layer_num]))
    
    def conv_3dlayer(self,layer_num):
        self.w_conv.append(self.weight_init(self.conv_filter_shapes[layer_num]))
        self.b_conv.append(self.bias_init([self.conv_filter_shapes[layer_num][4]]))
        self.h_conv.append(tf.nn.relu(self.conv3d(self.conv_layer_out[layer_num], self.w_conv[layer_num], self.conv_strides[layer_num], self.pad) + self.b_conv[layer_num]))
        self.conv_layer_out.append(self.max_pool3d(self.h_conv[layer_num],self.pool_window_sizes[layer_num],self.pool_strides[layer_num],self.pad))       
        
    def fc_layer(self,layer_num):
            if layer_num ==0:
                convout=self.conv_layer_out[len(self.conv_layer_out)-1]
                self.fc_layer_out.append(tf.reshape(convout, [self.batch_size,-1]))
                flat_shape=self.fc_layer_out[0].get_shape().as_list()
                self.w_fc.append(self.weight_init([flat_shape[1], self.fc_layer_sizes[layer_num]]))
            else:
                self.w_fc.append(self.weight_init([self.fc_layer_sizes[layer_num-1], self.fc_layer_sizes[layer_num]]))
            self.b_fc.append(self.bias_init([self.fc_layer_sizes[layer_num]]))
            self.h_fc.append(tf.nn.relu(tf.matmul(self.fc_layer_out[layer_num], self.w_fc[layer_num]) + self.b_fc[layer_num]))
            self.fc_layer_out.append(self.batch_dropout(self.h_fc[layer_num]))
    
    def reshape_layer(self):

                convout=self.conv_layer_out[len(self.conv_layer_out)-1]
                self.fc_layer_out=(tf.reshape(convout, [1,self.batch_size,-1]))
                self.flat_shape=self.fc_layer_out.get_shape().as_list()
     
    
    def create(self):
         tf.reset_default_graph()
         self.x_ph = tf.placeholder(tf.float32, shape=self.batch.shape)
         self.y_ph = tf.placeholder(tf.float32, shape=self.batch_targ.shape)
         self.dropout_ph = tf.placeholder("float32")
         self.conv_layer_out.append(self.x_ph)
         for i in xrange(len(self.conv_filter_shapes)):
             if self.dim=='2d':
                 self.conv_2dlayer(i)
             elif self.dim=='3d':
                 self.conv_3dlayer(i)
         self.reshape_layer()
         self.weight_bias_init()
         self.seq=tf.constant(self.truncated,shape=[1])
         self.seq2=tf.constant(self.truncated,shape=[1]) 
         self.fw_cell=self.cell_create('1')
         self.fw_cell2=self.cell_create('2')
         if self.configuration=='R':
            self.outputs, self.states= tf.nn.dynamic_rnn(self.fw_cell, self.fc_layer_out,
                                         sequence_length=self.seq,dtype=tf.float32)
            if self.attention_number >0:
               self.outputs_zero_padded=tf.pad(self.outputs,[[0,0],[self.attention_number,0],[0,0]])
               self.RNNout1=tf.stack([tf.reshape(self.outputs_zero_padded[:,g:g+(self.attention_number+1)],[self.n_hidden[(len(self.n_hidden)-1)]*((self.attention_number)+1)]) for g in range(self.batch_size)])
               self.presoft=tf.matmul(self.RNNout1, self.weights) + self.biases
            else: 
               self.presoft=tf.matmul(self.outputs[0][0], self.weights) + self.biases
         elif self.configuration=='B':
           self.bw_cell=self.cell_create('1')
           self.bw_cell2=self.cell_create('2')
           with tf.variable_scope('1'):
               self.outputs, self.states= tf.nn.bidirectional_dynamic_rnn(self.fw_cell, self.bw_cell, self.fc_layer_out,
                                             sequence_length=self.seq,dtype=tf.float32)
                                              
           self.first_out=tf.concat((self.outputs[0],self.outputs[1]),2)
           with tf.variable_scope('2'):
               self.outputs2, self.states2= tf.nn.bidirectional_dynamic_rnn(self.fw_cell2, self.bw_cell2, self.first_out,
                                                 sequence_length=self.seq2,dtype=tf.float32)
           self.second_out=tf.concat((self.outputs2[0],self.outputs2[1]),2)
            
           for i in range((self.attention_number*2)+1):
               self.attention_weight_init(i)
                
           self.zero_pad_second_out=tf.pad(tf.squeeze(self.second_out),[[self.attention_number,self.attention_number],[0,0]])
        #               self.attention_chunks.append(self.zero_pad_second_out[j:j+attention_number*2])
           if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
               self.attention_m=[tf.tanh(tf.matmul(tf.concat((self.zero_pad_second_out[j:j+self.batch_size+2],tf.squeeze(self.first_out)),1),self.attention_weights[j])) for j in range((self.attention_number*2)+1)]
           else:
               self.attention_m=[tf.tanh(tf.matmul(tf.concat((self.zero_pad_second_out[j:j+self.batch_size],tf.squeeze(self.first_out)),1),self.attention_weights[j])) for j in range((self.attention_number*2)+1)]
           self.attention_s=tf.nn.softmax(tf.stack([tf.matmul(self.attention_m[i],self.sm_attention_weights[i]) for i in range(self.attention_number*2+1)]),0)
           if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
               self.attention_z=tf.reduce_sum([self.attention_s[i]*self.zero_pad_second_out[i:self.batch_size+i+2] for i in range(self.attention_number*2+1)],0)
           else:
               self.attention_z=tf.reduce_sum([self.attention_s[i]*self.zero_pad_second_out[i:self.batch_size+i] for i in range(self.attention_number*2+1)],0)
           self.presoft=tf.matmul(self.attention_z,self.weights)+self.biases
         if  self.output_act=='softmax':   
           self.pred=tf.nn.softmax(self.presoft)
           self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.presoft, labels=self.y_ph))
         elif self.output_act=='sigmoid':
           self.pred=tf.nn.sigmoid(self.presoft)
           if self.cost_type=='CE':
               self.cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=self.presoft, labels=self.y_ph))
           elif self.cost_type=='MS':
               self.cost=tf.reduce_mean(tf.losses.mean_squared_error(labels=self.y_ph,predictions=self.pred))
           elif self.cost_type=='CECS':
               self.cost=tf.reduce_mean(CSFunctions.cross_entropy_sig(predictions=self.pred,labels=self.y_ph))
           elif self.cost_type=='MSCS':
               self.cost=tf.reduce_mean(CSFunctions.mean_squared(predictions=self.pred,labels=self.y_ph))
           elif self.cost_type=='HybridCE1':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1)               
           elif self.cost_type=='HybridMS1':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1) 
           elif self.cost_type=='HybridCE2':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1/2.)               
           elif self.cost_type=='HybridMS2':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1/2.) 
           elif self.cost_type=='HybridCE3':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1/3.)               
           elif self.cost_type=='HybridMS3':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1/3.) 
           elif self.cost_type=='HybridCE4':
               self.cost=CSFunctions.HybridCE(self.pred,self.y_ph,self.batch_size,1/4.)               
           elif self.cost_type=='HybridMS4':
               self.cost=CSFunctions.HybridMS(self.pred,self.y_ph,self.batch_size,1/4.) 
           elif self.cost_type=='PeakCE':
               self.cost=CSFunctions.PeakCE(self.pred,self.y_ph,self.batch_size)  
           elif self.cost_type=='PeakMS':
               self.cost=CSFunctions.PeakMS(self.pred,self.y_ph,self.batch_size)  
               
         if self.optimizer == 'GD':
             self.optimize = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate).minimize(self.cost)
         elif self.optimizer == 'Adam':
             self.optimize = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.cost) 
         elif self.optimizer == 'RMS':
             self.optimize = tf.train.RMSPropOptimizer(learning_rate=self.learning_rate).minimize(self.cost) 
         self.correct_pred = tf.equal(tf.argmax(self.pred,1), tf.argmax(self.y_ph,1))
         self.accuracy = tf.reduce_mean(tf.cast(self.correct_pred, tf.float32))
         self.init = tf.global_variables_initializer()
         self.saver = tf.train.Saver()
         self.saver_var = tf.train.Saver(tf.trainable_variables())
         if self.save_location==[]:
           self.save_location=os.getcwd()
           
    def zero_pad(self,data):
        if self.dim=='2d':
            out_data=np.zeros(data.shape[0]+self.frames_either_side[0][0]*512+self.frames_either_side[0][1]*512)
            out_data[self.frames_either_side[0][0]*512:data.shape[0]+self.frames_either_side[0][0]*512]=data
        elif self.dim=='3d':
            out_data=np.zeros((data.shape[0]+self.frames_either_side[0][0]+self.frames_either_side[0][1],data.shape[1]+self.frames_either_side[1][0]+self.frames_either_side[1][1],data.shape[2]+self.frames_either_side[2][0]+self.frames_either_side[2][1]))
            out_data[self.frames_either_side[0][0]:data.shape[0]+self.frames_either_side[0][0],self.frames_either_side[1][0]:data.shape[1]+self.frames_either_side[1][0],self.frames_either_side[2][0]:data.shape[2]+self.frames_either_side[2][0]]=data
        return out_data
            
    def segment_extract(self,data,targ,seg_location):
        self.seg_location=seg_location
        if self.dim=='2d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1]],2), targ[self.seg_location[0]][self.seg_location[1]]
        elif self.dim=='3d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
                self.seg_location=np.append(self.seg_location,0)
            elif len(self.seg_location)==2:
                self.seg_location.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1],(self.seg_location[2]*self.input_stride_size[2]):(self.seg_location[2]*self.input_stride_size[2])+self.frames_either_side[2][0]+self.frames_either_side[2][1]+self.input_stride_size[2]],3), targ[self.seg_location[0]][self.seg_location[1]][self.seg_location[2]]   
        return out

    def augmentation(self,audio_data,aug_limit=0.5):
        if abs(np.random.randn(1))<0.5:
            jam = jams.JAMS()
            j_orig = muda.jam_pack(jam, _audio=dict(y=np.array(audio_data), sr=44100))
        
            pitch=int(np.round((np.random.rand(1)*2-1)*12))
            noise=(np.random.randint(1,6)/20.)
             
            pitchs = muda.deformers.LinearPitchShift(n_samples=1, lower=pitch-0.0001, upper=pitch+0.0001)
            noises = muda.deformers.BackgroundNoise(n_samples=1,files='MudaWhiteNoiseGaussian.wav',weight_min=noise-0.00001, weight_max=noise+0.00001)
         
            pipeline = muda.Pipeline(steps=[('pitch_shift', pitchs),
                                            ('noise',noises)])
            y=list(pipeline.transform(j_orig))
    
            y=y[0].sandbox.muda._audio['y']
        else:
            y=audio_data
        return y
        
    def segment_extract_wav(self,data,targ,seg_location,aug_prob=0):
        self.seg_location=seg_location
        if self.dim=='2d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
            self.batch_wav=data[(self.seg_location[0]*self.input_stride_size[0])*512:((self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0])*512]
            self.batch_wav_post_aug=self.augmentation(self.batch_wav,aug_prob)
            out=np.expand_dims(madmom.audio.spectrogram.LogarithmicFilteredSpectrogram(self.batch_wav_post_aug,hop_size=512,sample_rate=44100,fmin=20,fmax=20000),2), targ[self.seg_location[0]][self.seg_location[1]]
        elif self.dim=='3d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
                self.seg_location=np.append(self.seg_location,0)
            elif len(self.seg_location)==2:
                self.seg_location.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1],(self.seg_location[2]*self.input_stride_size[2]):(self.seg_location[2]*self.input_stride_size[2])+self.frames_either_side[2][0]+self.frames_either_side[2][1]+self.input_stride_size[2]],3), targ[self.seg_location[0]][self.seg_location[1]][self.seg_location[2]]   
        return out

    def segment_extract__test_wav(self,data,targ,seg_location):
        self.seg_location=seg_location
        if self.dim=='2d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
            self.batch_wav=data[(self.seg_location[0]*self.input_stride_size[0])*512:((self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0])*512]
            self.batch_wav_post_aug=self.augmentation(self.batch_wav,0)
            out=np.expand_dims(madmom.audio.spectrogram.LogarithmicFilteredspectrogram(self.batch_wav_post_aug,hop_size=512,fmin=20,fmax=20000),2)
        elif self.dim=='3d':
            if len(self.seg_location.shape)<=1:
                self.seg_location=np.append(self.seg_location,0)
                self.seg_location=np.append(self.seg_location,0)
            elif len(self.seg_location)==2:
                self.seg_location.append(self.seg_location,0)
            out=np.expand_dims(data[(self.seg_location[0]*self.input_stride_size[0]):(self.seg_location[0]*self.input_stride_size[0])+self.frames_either_side[0][0]+self.frames_either_side[0][1]+self.input_stride_size[0],(self.seg_location[1]*self.input_stride_size[1]):(self.seg_location[1]*self.input_stride_size[1])+self.frames_either_side[1][0]+self.frames_either_side[1][1]+self.input_stride_size[1],(self.seg_location[2]*self.input_stride_size[2]):(self.seg_location[2]*self.input_stride_size[2])+self.frames_either_side[2][0]+self.frames_either_side[2][1]+self.input_stride_size[2]],3), targ[self.seg_location[0]][self.seg_location[1]][self.seg_location[2]]   
        return out

    def train(self):
#      self.create()
      self.iteration=0
      self.epoch=0
      self.prev_val_loss=100
      self.val_loss=99
      if self.usage=='simple':
          self.val_locations=self.locations_create([self.val.shape[0]])
      elif self.usage=='timestep':
          self.val_output_dim1=int(self.val.shape[0]/self.input_stride_size[0]/512)
          if self.dim=='2d':
              self.val_locations=self.locations_create(self.val_output_dim1)
          elif self.dim=='3d':
              self.val_output_dim3=self.val.shape[2]/self.input_stride_size[2]
              self.val_locations=self.locations_create([self.val_output_dim1,self.val_output_dim2,self.val_output_dim3])
      with tf.Session() as sess:
        sess.run(self.init)
        while self.epoch < self.minimum_epoch or self.prev_val_loss > self.val_loss:
            for i in xrange(self.num_batch):
               if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                   for j in xrange(self.batch_size-2):
                       if self.usage=='simple':
                            self.batch[j]=np.expand_dims(self.features[self.minibatch_nos[i][j]],2)
                            self.batch_targ[j]=self.targ[self.minibatch_nos[i][j]]
                       elif self.usage=='timestep':
                           
                            self.batch[j+1],self.batch_targ[j+1]=self.segment_extract_wav(self.features,self.targ,self.minibatch_nos[i][j],self.aug_prob)                    
               else:
                   for j in xrange(self.batch_size):
                       if self.usage=='simple':
                            self.batch[j]=np.expand_dims(self.features[self.minibatch_nos[i][j]],2)
                            self.batch_targ[j]=self.targ[self.minibatch_nos[i][j]]
                       elif self.usage=='timestep':
                           
                            self.batch[j],self.batch_targ[j]=self.segment_extract_wav(self.features,self.targ,self.minibatch_nos[i][j],self.aug_prob)                        
               sess.run(self.optimize, feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:self.dropout})
               self.iteration+=1
            self.epoch+=1   
            print("Epoch " + str(self.epoch))
            if self.epoch > self.minimum_epoch:
                self.loss_train=[]
                self.loss_val=[]
                if self.display_accuracy=='True':
                    self.acc_train=[]
                    self.acc_val=[]
                self.val_counter=0
                for i in xrange(int(np.floor(len(self.val_locations)/self.batch_size))):
                    if self.display_accuracy=='True':
                        if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                             for j in xrange(self.batch_size-2):
                                if self.usage=='simple':
                                    self.batch[j]=np.expand_dims(self.val[self.val_locations[(self.batch_size*self.val_counter)+j]],2)
                                    self.batch_targ[j]=self.val_targ[self.val_locations[(self.batch_size*self.val_counter)+j]]
    
                                elif self.usage=='timestep':
                                      self.batch[j+1],self.batch_targ[j+1]=self.segment_extract_wav(self.val,self.val_targ,self.val_locations[self.val_counter])                      
                        else:
                            for j in xrange(self.batch_size):
                                if self.usage=='simple':
                                    self.batch[j]=np.expand_dims(self.val[self.val_locations[(self.batch_size*self.val_counter)+j]],2)
                                    self.batch_targ[j]=self.val_targ[self.val_locations[(self.batch_size*self.val_counter)+j]]
    
                                elif self.usage=='timestep':
                                      self.batch[j],self.batch_targ[j]=self.segment_extract_wav(self.val,self.val_targ,self.val_locations[self.val_counter])       
                        vl,va=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1})
                        self.loss_val.append(vl)
                        self.acc_val.append(va)
                        self.val_counter+=1        
                    else:
                        if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                            for j in xrange(self.batch_size-2):
                                self.batch[j+1],self.batch_targ[j+1]=self.segment_extract_wav(self.val,self.val_targ,self.val_locations[self.val_counter])  
                        else:
                            for j in xrange(self.batch_size):
                                self.batch[j],self.batch_targ[j]=self.segment_extract_wav(self.val,self.val_targ,self.val_locations[self.val_counter])
                        self.val_counter+=1            
                        self.loss_val.append(sess.run(self.cost, feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1}))
                if  self.display_train_loss=='True': 
                    for i in xrange(self.num_batch): 
                        if self.display_accuracy=='True':
                            if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                for j in xrange(self.batch_size-2):
                                        if self.usage=='simple':
                                             self.batch[j]=np.expand_dims(self.features[self.minibatch_nos[i][j]],2)
                                             self.batch_targ[j]=self.targ[self.minibatch_nos[i][j]]
                                        elif self.usage=='timestep':
                                             self.batch[j+1],self.batch_targ[j+1]=self.segment_extract_wav(self.features,self.targ,self.minibatch_nos[i][j])
                            else:
                                for j in xrange(self.batch_size):
                                    if self.usage=='simple':
                                         self.batch[j]=np.expand_dims(self.features[self.minibatch_nos[i][j]],2)
                                         self.batch_targ[j]=self.targ[self.minibatch_nos[i][j]]
                                    elif self.usage=='timestep':
                                         self.batch[j],self.batch_targ[j]=self.segment_extract_wav(self.features,self.targ,self.minibatch_nos[i][j])
                            tl,ta=sess.run((self.cost,self.accuracy), feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1})
                            self.loss_train.append(tl)
                            self.acc_train.append(ta)
                        else:
                            if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                                for j in xrange(self.batch_size-2):
                                    self.batch[j+1],self.batch_targ[j+1]=self.segment_extract_wav(self.features,self.targ,self.minibatch_nos[i][j])
                            else:
                                for j in xrange(self.batch_size):
                                    self.batch[j],self.batch_targ[j]=self.segment_extract_wav(self.features,self.targ,self.minibatch_nos[i][j])
                            self.loss_train.append(sess.run(self.cost, feed_dict={self.x_ph: self.batch, self.y_ph: self.batch_targ,self.dropout_ph:1}))
                        
                    print("Train Minibatch Loss " + "{:.6f}".format(np.mean(np.array(self.loss_train))))
                    if self.display_accuracy=='True':
                        print("Train Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_train))))
                self.prev_val_loss=self.val_loss
                self.val_loss=np.mean(np.array(self.loss_val))              
                print("Val Minibatch Loss " + "{:.6f}".format(self.val_loss))
                if self.display_accuracy=='True':
                    print("Val Minibatch Accuracy " + "{:.6f}".format(np.mean(np.array(self.acc_val))))
            if self.epoch==self.maximum_epoch:
                break
        print("Optimization Finished!")
        self.saver.save(sess, self.filename)
        
        
    def locations_create(self,sizes):
        locations=[]
        if self.dim=='2d':
            if self.usage!='simple':
                for i in range(sizes):
                        locations.append(i)
            else:
                for i in range(sizes[0]):
                    locations.append([i])
        elif self.dim=='3d':
            for i in range(sizes[0]):
                for j in range(sizes[1]):
                    for k in range(sizes[2]):
                        locations.append([i,j,k])        
        return np.squeeze(np.array(locations))
                   
    def implement(self,data,):
        with tf.Session() as sess:
            self.saver.restore(sess, self.save_location+'/'+self.filename)
            self.output=[]            
            for i in xrange(len(data)):
                if self.usage=='simple':
                    self.locations=self.locations_create([len(data[i])])
                    self.output.append(np.zeros((len(data[i]),self.n_classes)))
                else:
                    self.outputdim1=int(data[i].shape[0]/self.input_stride_size[0])
                    self.outputdim2=int(data[i].shape[1]/self.input_stride_size[1])
                    if self.dim=='2d':
                        self.output.append(np.zeros((self.outputdim1,self.outputdim2,self.n_classes)))
                    elif self.dim=='3d':
                        self.outputdim3=int(data[i].shape[2]/self.input_stride_size[2])
                        self.output.append(np.zeros((self.outputdim1,self.outputdim2,self.outputdim3,self.n_classes)))
                    data[i]=self.zero_pad(data[i])
                    if self.dim=='2d':
                        self.locations=self.locations_create([self.outputdim1,self.outputdim2])
                    elif self.dim=='3d':
                        self.locations=self.locations_create([self.outputdim1,self.outputdim2,self.outputdim3])
                self.counter=0
                if self.cost_type=='HybridCE1' or self.cost_type=='HybridMS1' or self.cost_type=='PeakCE' or self.cost_type=='PeakMS' or  self.cost_type=='HybridCE2' or self.cost_type=='HybridMS2' or  self.cost_type=='HybridCE3' or self.cost_type=='HybridMS3' or  self.cost_type=='HybridC4E' or self.cost_type=='HybridMS4':
                     for j in xrange(int(len(self.locations)/(self.batch_size-2))):
                            for z in xrange(self.batch_size-2):
                                    if self.usage=='simple':
                                        self.batch[z]=np.expand_dims(data[i][self.locations[self.counter]],2)
                                    else:
                                        self.batch[z+1]=self.segment_extract_test_wav(data[i],self.locations[self.counter])                 
                                    self.counter+=1
                            batch_out=sess.run(self.pred, feed_dict={self.x_ph: self.batch, self.dropout_ph:1})
                            
                            if j == len(self.locations)/(self.batch_size-2):
                                implement_length=self.dif
                            else:
                                implement_length=self.batch_size-2
                            for z in xrange(implement_length):
                                if self.usage=='simple':    
                                    self.output[i][self.locations[self.counter-self.batch_size+z]]=batch_out[z]
                                else:
                                    if self.dim=='2d':
                                        self.output[i][self.locations[self.counter-(self.batch_size-2)+z][0],self.locations[self.counter-(self.batch_size-2)+z][1]]=batch_out[z][1:self.batch_size-1] 
                                    elif self.dim=='3d':
                                        self.output[i][self.locations[self.counter-(self.batch_size-2)+z][0],self.locations[self.counter-(self.batch_size-2)+z][1],self.locations[self.counter-(self.batch_size-2)+z][2]]=batch_out[z][1:self.batch_size-1]                
                else:    
                    for j in xrange(int(len(self.locations)/self.batch_size)):
                        for z in xrange(self.batch_size):
                                if self.usage=='simple':
                                    self.batch[z]=np.expand_dims(data[i][self.locations[self.counter]],2)
                                else:
                                    self.batch[z]=self.segment_extract_test_wav(data[i],self.locations[self.counter])                 
                                self.counter+=1
                        batch_out=sess.run(self.pred, feed_dict={self.x_ph: self.batch, self.dropout_ph:1})
                        
                        if j == len(self.locations)/self.batch_size:
                            implement_length=self.dif
                        else:
                            implement_length=self.batch_size
                        for z in xrange(implement_length):
                            if self.usage=='simple':    
                                self.output[i][self.locations[self.counter-self.batch_size+z]]=batch_out[z]
                            else:
                                if self.dim=='2d':
                                    self.output[i][self.locations[self.counter-self.batch_size+z][0],self.locations[self.counter-self.batch_size+z][1]]=batch_out[z] 
                                elif self.dim=='3d':
                                    self.output[i][self.locations[self.counter-self.batch_size+z][0],self.locations[self.counter-self.batch_size+z][1],self.locations[self.counter-self.batch_size+z][2]]=batch_out[z]
            return self.output    

    def cell_create(self,scope_name):
         with tf.variable_scope(scope_name):
             if self.cell_type == 'tanh':
                 cells = rnn.MultiRNNCell([rnn.BasicRNNCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             elif self.cell_type == 'LSTM': 
                 cells = rnn.MultiRNNCell([rnn.BasicLSTMCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             elif self.cell_type == 'GRU':
                 cells = rnn.MultiRNNCell([rnn.GRUCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             elif self.cell_type == 'LSTMP':
                 cells = rnn.MultiRNNCell([rnn.LSTMCell(self.n_hidden[i]) for i in range(self.n_layers)], state_is_tuple=True)
             cells = rnn.DropoutWrapper(cells, input_keep_prob=self.dropout_ph,output_keep_prob=self.dropout_ph) 
         return cells
     
    def weight_bias_init(self):
               
         if self.init_method=='zero':
            self.biases = tf.Variable(tf.zeros([self.n_classes]))           
         elif self.init_method=='norm':
               self.biases = tf.Variable(tf.random_normal([self.n_classes]))           
         if self.configuration =='B':
             if self.init_method=='zero':  
                 self.weights =tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*2, self.n_classes]))
             elif self.init_method=='norm':
                   self.weights = { '1': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes])),'2': tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes]))} 
         if self.configuration =='R':
             if self.init_method=='zero':  
                 self.weights = tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes]))     
             elif self.init_method=='norm':
                   self.weights = tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)], self.n_classes]))
      
    def attention_weight_init(self,num):
         if num==0:
             self.attention_weights=[tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*4,self.n_hidden[(len(self.n_hidden)-1)]*2]))]
             self.sm_attention_weights=[tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*2,self.n_hidden[(len(self.n_hidden)-1)]*2]))]
         if num>0:
             self.attention_weights.append(tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*4,self.n_hidden[(len(self.n_hidden)-1)]*2])))
             self.sm_attention_weights.append(tf.Variable(tf.random_normal([self.n_hidden[(len(self.n_hidden)-1)]*2,self.n_hidden[(len(self.n_hidden)-1)]*2])))
             
  