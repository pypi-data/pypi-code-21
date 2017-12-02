# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 09:37:36 2017
@author: Administrator
"""
from .First_sub import MainCut1
from .Second_sub import MainCut2
from .Appealmoney1 import  MainLawsuit1
from .Jmoney1 import  Main_Judge1
import re
## 一审的诉讼请求,数据
###数据
def get_first_asuit(rawdata):
    x1=re.search("(诉讼请求|请求[^。]{,6}判令|请求判决[:： ]|诉称[:：]|诉讼请求为)[^\n]*",rawdata,re.S)
    if x1:
        x1=x1.group()
    else:
        x1=""
    return x1

## 最后判决结果
def Sub_Judge1(content):
        x=content.split("\n")
        st=""
        txt=""
        flag=False
        for j in x:
            txt+=j+"\n"
            x1=re.search("(判如下|判令如下|判决:|判决如下|综上,依据《中华人民共和|规定,如下:|(综上所述|综上).{,1}.*规定:)",j)
            fx=re.search("判决[^。，；]*(附图|附页):",j)
            ###
            if x1 and not fx:
                flag=True
                st=j+"\n"
            else:
                st+=j+"\n"
        x1=re.search("审判长|审判员|书记员|速录员|陪审员|速记员|法官助理",st)
        if x1:
            pre_txt=txt.replace(st,"")
        else:
            flag=False
            pre_txt=""
        ##需要存储于记录一下入库的错误类型
        return  pre_txt,st,flag
##shu
###一审判决结果
def get_firstjudge(rawdata):
    x1=re.search("(判决(如下|)[:：:]{1}|综上,依据《中华人民共和)[^\n]*",rawdata,re.S)
    if x1:
        subjudge=x1.group()
    else:
        subjudge=""
    return subjudge
def  Get_Appeal_Judge_Money(entity,rawdata):
    if entity.nature_=="刑事":
        pre_txt,st,flag=Sub_Judge1(rawdata)
        l=[(1,'3','3')]*11
        l[8]=(1,'3',st)
        entity.Judement=l[8][2]
        Jmoney=Main_Judge1(l)
        entity.judge_money=Jmoney
        return entity
    if entity.nature_!="民事":
        return entity
    if entity.level_=="一审":
        l=MainCut1((1,rawdata))
        if len(l)==11:
            money=MainLawsuit1(l)
            if money=="不祥":
                money="-1"
            entity.appeal_money=money
            Jmoney=Main_Judge1(l)
            if Jmoney=="不祥":
                Jmoney="-1"
            entity.judge_money=Jmoney
            entity.accuser=l[2][2]+l[3][2]
            entity.Judement=l[8][2]
        else:
            l=[(1,'2','')]*11
            asuit=get_first_asuit(rawdata)
            l[3]=(1,3,asuit)
            pre_txt,st,flag=Sub_Judge1(rawdata)
            if flag:
                judgcontent=st
                l[8]=(1,"2",judgcontent)
                Jmoney=Main_Judge1(l)
            else:
                Jmoney="不详"
            entity.judge_money=Jmoney
    elif entity.level_ =="二审":
        l,flag=MainCut2((1,rawdata))
        if len(l)==17:
            money=MainLawsuit2(l)
            Jmoney=Main_Judgment2(l)
            if Jmoney=="不详":
                Jmoney="-1"
            entity.judge_money=Jmoney
            entity.appeal_money=money
            entity.Judement=l[8][1]+l[14][1]
            entity.accuser=''
        else:
            l=[(1,'2','')]*17
            pre_txt,st,flag=Sub_Judge1(rawdata)
            first_judge=get_firstjudge(rawdata)
            if flag:
                judgcontent=st
                l[14]=(1,judgcontent,'8')
                l[8]=(1,first_judge,"")
                Jmoney=Main_Judge1(l)
            else:
                Jmoney="不详"
            entity.judge_money=Jmoney
    return entity
