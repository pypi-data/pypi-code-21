
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 09:52:24 2017

@author: Administrator
"""

import re
def MainCut1(i):
    """
    判决结果 :驳回|部分支持|全部驳回｜
    """
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
    """
    文书尾部
    """
    def Sub_Judge2(content):
        content=content.replace("(","（")
        content=content.replace(")","）")
        x1=re.search("(^.*(判决如下|判决:)[:]{0,1}).*",content)
        x2=re.search("(^[^\n]*(综上,依据《中华人民共和((?!(驳回|撤销|维持|\n)).)*|规定,如下:|(综上所述|综上).{,1}[^\n]*规定:))",content)
        if x1:
            DesBaise=x1.group(1)
            x2=content.replace(DesBaise,"")
        elif x2:
            DesBaise=x2.group(1)
            x2=content.replace(DesBaise,"")
        else:
            DesBaise=""
            x2=content
        x=x2.split("\n")
        flag=False
        Inscribe=""
        x2=""
        for j in x:
            Rex=re.search("审判长|审判员|法官助理|速录员|速记员|陪审员",j)
            if Rex:
                flag=True
            if flag:
                Inscribe+=j+"\n"
            else:
                x2+=j+"\n"

        Judgment=""
        x1=re.search("(^.*?)([一-龥]*(未按照(判决|)指定|如不服|在指定期限内|案件受理费|受理费|可以在判决书送达之日起|如未按(本|)判决|案件保全费|公告费|财产保全费|本诉诉讼费|本案诉讼受理费|(本案.{1,6}费})|[\r\n\t]诉讼费|本案应交纳诉讼费|如(果|)?未按(本|)判决指定的期间履行给付(金钱|)义务|一审诉讼费))",x2,re.S)
        if x1:
             Judgment=x1.group(1)
             footer=x2.replace(Judgment,"")
        else:
             Judgment=x2
             footer=""
        return  [DesBaise,Judgment,footer,Inscribe]


    """
    主函数
    处理一下一审分段的
    """
    def Optimization1(x):
        x=re.sub("^[\n]+","",x)
        x1=re.search("(^本院认为.*。)([^。]*(依据|依照|综上所述).*)",x)
        m=[]
        if x1:
            x=x1.group(1)
            x1=x1.group(2)
            m.append(x)
            m.append(x1)
        else:
            x=""
            x1=x
            m.append(x1)
        return m
    """
    ##对于长度不够的在经过一次分段处理
    """
    def Optimization2(x):
        x=re.sub("^[\n]+","",x)
        x1=re.search("(^[^。]{,5}(本院(经|)审理查明|本案(经|)审理查明|一审查明).*。)([^。]*(依据|依照|综上所述).*)",x)
        m=[]
        if x1:
            x1=x1.group(1)
            x2=x.replace(x1,"")
            m.append(x1)
            m.append(x2)
        else:
            x=""
            x1=x
            m.append(x1)
        return m

    """
    文书首
    """
    def Stander(x):
        x=re.sub("&gt;","",x)
        x=re.sub("&times;","×",x)
        x=x.replace("&temp;","")
        x=x.replace("&quot;","")
        x=x.replace("{C}","")
        x=x.replace("&amp;","")
        x=re.sub("&nbsp;","",x)
        x=re.sub("&ldqu0;","",x)
        x=re.sub("&lsqu0;","",x)
        x=re.sub("&rsqu0;","",x)
        x=x.replace("lt;","")
        x=x.replace("\xe3","")
        x=x.replace("\x80","")
        x=x.replace("\xc2","")
        x=x.replace("\xa0","")
        x=x.replace("\x7f","")
        x=x.replace("\u3000","")
        x=x.replace("当事人原审的意见\n","")
        x=x.replace("\t", "")
        x=x.replace("&rdqu0;","")
        x=re.sub("[  　　]+","",x)
        x=re.sub("<[^<>]+>","",x)
        x=re.sub("\(此页无正文\)","",x)
        x=re.sub("判([\n]*|[?]+|)决([\n]*|[?]+|)如([\n]*|[?]+|)下","判决如下",x)
        x=re.sub("判([\n]*)决([\n]*|):","判决:",x)
        x=re.sub("(|[\n]*)年([\n]*|)","年",x)
        x=re.sub("(\n|[\n]*)月(|[\n]*)","月",x)
        x=re.sub("[?]{3,}","\n",x)
        x=re.sub("[?]+","",x)
        x=re.sub("[‘’']","",x)
        x=re.sub("[zｚＺ]{1}[lＬｌ]{1}","ZL",x)
        x=re.sub("[\r\n]+","\n",x)
        x=re.sub("...: ","",x)
        x=x.replace("\x0b","\n")
        x=re.sub("[\r\n]+","\n",x)
        x=re.sub("[:：：:：：：]{1}",":",x)
        x=re.sub("^[\n]+","",x)
        x=re.sub("（本页无正文）","",x)
        x=re.sub("\(本页无正文\)","",x)
        x=re.sub("本判决为终审判决。","",x)
        x=re.sub("(\n)日","日",x)
        x=re.sub("审([\n]*|[?]+|)判([\n]*|[?]+|)长([\n]+|[?]+)","审判长 ",x)
        x=re.sub("代([\n]*|[?]+|)理([\n]*|[?]+|)审判长","代理审判长 ",x)
        x=re.sub("审([\n]*|[?]+|)判([\n]*|)员([\n]*|[?]+)","审判员 ",x)
        x=re.sub("代([\n]*|[?]+|)理([\n]*|[?]+|)审判员","代理审判员 ",x)
        x=re.sub("陪([\n]*|[?]+|)审([\n]*|[?]+|)员([\n]+|[?]+)","陪审员 ",x)
        x=re.sub("人([\n]*|[?]+|)民([\n]*|[?]+|)陪审员([\n]+|[?]+)","人民陪审员 ",x)
        x=re.sub("书([\n]*|[?]+|)记([\n]*|[?]+|)员([\n]+|[?]+)","书记员 ",x)
        x=re.sub("速([\n]*|[?]+)记([?]*|[\n]*)员","速记员",x)
        x=re.sub("速记员\n","速记员 ",x)
        x=re.sub("速([\n]*)录[\n]*员","速录员",x)
        x=re.sub("速录员\n","速录员",x)
        x=re.sub("法([\n]*|[?]+|)官([\n]*|[?]+|)助([\n]+|[?]+)理","法官助理  ",x)
        #清除开始赘余信息
        x1=re.search("(^签发.*?[\n])([^\n]{,30}法院)",x,re.S)
        if x1:
            x1=x1.group(1)
            x=x.replace(x1,"")
        x1=re.search("(^.*(已审理终结。|已审理完结。|已审理完毕。))([^\n]{1}.*)",x,re.S)
        if x1:
            x2=x1.group(3)
            x1=x1.group(1)
            x=x1+"\n"+x2
        x1=re.search("(^.*(已审理终结。|已审理完结。|已审理完毕。))([^\n]{1}.*)",x,re.S)
        if x1:
            x2=x1.group(3)
            x1=x1.group(1)
            x=x1+"\n"+x2
        ###对尾部文书进行基本的规范化
        x=re.sub("pt;''>","",x)
        x=re.sub("当事人二审的意见\n","",x)
        x=re.sub("\(原审判决附图一\)\(原审判决附图二\)","",x)
        x1=re.search("^((?!(法院|\n)).)*\n",x,re.S)
        ###只能整体进行不能单独的进行其他的计算
        if x1:
            tx1=x1.group()
            x=x.replace(tx1,"")
            #x=re.sub(tx1,"",x)
        #附
        x1=re.search("(附:本判决书所依据法律规定的具体条文:|附本判决书引用的主要法律条文:|附.{,1}本判决适用法律条文:|附.{,1}本判决适用法律条款:|附:本案适用的法律条款|附:本案适用的法律条款|附:本案适用的法律条款).+",x,re.S)
        if x1:
            xx=x1.group()
            x=x.replace(xx,"")
        return x
    def Deal_all(x):
        x=re.sub("\n案件相关情况|\n本案相关情况\n|\n判决结果\n|\n裁判理由与结果\n","\n",x)
        start=0
        first=1
        second=2
        three=3
        four=4
        four_1=5
        four_2=6
        rex="反诉称"
        rex1="[^0-9、]*[0-9Xx]{2,}[^0-9]{1}[^。，、]+[0-9-、Xx]+号|\([0-9]{4}\[一-龥0-9]+第[0-9]+号|初字第[0-9]+号"
        rex2="于[一-龥0-9]+年[一-龥0-9]+月[一-龥0-9]+日(公开|)[一-龥0-9\(\)]*开庭审理了本案|案由:|审理终结|审理完结|审理完毕|审理结|当庭宣告判决|依法组成合议庭|侵[害犯权]{1}[^\n。]{,30}纠纷一案|无正当理由拒不到庭|^[^，。]*被告[^。，,]{,20}(拒|)不到庭|(服务|技术)合同纠纷一案|纠纷一案"
        rex3="(判令被告:|诉请法院判令:|^原告[^。，,;；：:、?]*诉(称|):|原告[^。]*诉请:|诉请判令:|请求判决:|请求:|^原告诉请|^[^。]{,30}诉讼[.]{1}称|^[^。]*不服[^。]{,10}(裁|决)定[^。]{,10}向[^。]{,20}诉讼称|原告[^。]{,30}诉(讼|)称|诉讼请求为:|诉讼请求:|[^。，]{,10}向本院起诉要求:|原告[^\n。]{,30}(起诉认为|请求判令|诉称|诉讼请求|起诉请求)|诉称:|提出诉讼请求|请求判令:|请求.院判令|请求判令[^。，；]{,10}:|公司诉称|诉称|诉讼称|提出[^。，]{,5}诉讼请求})"
        rex4="(^被告[^，。]*辩|反诉请求:|第三人[^。，、]*述称|^被告[一-龥、]+答辩|被告[一-龥、]+拒不到庭|被告[^。，；、:]+抗辩理由是:|反诉称:|第三人[^。0-9a-zA-Z，、]*陈述意见|被告[^。]{,20}(坚持|认为)[^。]{,20}(认定|意见)|^[^。；]{,30}(辩称|辨称|答辩|答辨)|被告[^。]{,30}对原告所诉事实|被告对原告主张|被告[^。]{,30}(没有到到庭|拒不到庭)|(被告|公司)[^。，](放弃抗[辨辩]{1}|未答[辩辨]{1}|未提出答辩意见))"
        rex5="^双方有争议|^双方对以下事|^相关事实|^[^。]{,30}(^(经|)庭前准备会议|^(经|)庭前交换证据|庭审中,双方当事人对以下事实无争议:|.*本院确认如下:|.*本院组织[一-龥]+证据交换和质证|.*根据原告的当庭陈述和举证意见|.*查明如下事实:|^经过庭审|本案认定事实如下:|.*本院根据证据,认定事实如下:|经庭审确认:|经本院审理,查明事实如下:|^查明事实|.*确认本案(的|)(法律|)事实(如下|):|本院[一-龥]*认定:|经本院[一-龥]*讨论认为:|^综上,本院认定|通过[^。，、]*当庭举证、[^。]*事实可以确认:|.*本院予以认定。|.*本院予以确认。|.*经本院庭审质证|.*经庭审调查,|本院认定的事实[^,，。:；：、]*事实|.*经本院审核后认为|^根据证据审核认定的规则|.*本院[^。]*认证如下:|.*综上,本院[^。]*认定(本案|)(事实如下|):|.*经审理[^。]*事实予以认定|^根据证据审核认定[^。，],*本院[^，。:]*予以认定,|^另查明|.*归纳案件的焦点是:|.*本院[^。]*,据此确认以下事实:|.*本院认(证|定)(案件|)(意见|事实|)(如下|):|本院审查认为:|经过庭审[一-龥、]+,本院对上述证据认证如下:|.*经审理查明|根据[^。]*,本院认定的本案事实如下:|庭审中,原、被告对如下事实没有异议:|^综上所述,本院认定事实|^在本院确定的举证期|^经查,|^本院为查明案件事实,|[^。]*本院予以确认:|[^。]*本院经认证查明如下事实:|^经开庭审理,|本院[一-龥]+认定以下事实:|.*本院予以确认:|.*本院对以下事实予以确认:|^综合上述证据,本院认定的基本事实如下:|经过庭审[^。]*[一-龥，,]+确认:|本院根据[^。]*,[一-龥]+事实:|.*原告举证及被告质证如下:|^经开庭审理|另查明:|^本院根据[一-龥]+提交的证据|^本院公开开庭审理,[一-龥]+证据|本院认定的基本事实如下:|^综合分析上述证据及庭审|本院对双方的证据作如下认定:|^综合原、被告双方的举证|经审理查明:|对证据认证如下:|认证如下事实|查明以下案件事实|经庭审质证|^还查明,|本院对案件事实认定如下|本院确定以下与本案有关的事实|本院对本案证据认证如下|查明以下事实|根据[^。]{,30}(陈述|证据),本院(确认如下事实|认定事实如下|认定如下事实|确认事实如下)|查明:|本院经查|本院依法认定本案事实如下|本院确认本案事实如下|本院根据上述[^。]{,30}确认以下事实|经审理|本院经查|根据上述[^。]{,30}本院确认以下事实|经审理查明|经庭审[^。，]{,5}比对|一审查明|经审查|本院查明|本院审理查明|本案相关事实|^[^。]{,30}本院(确认如下事实|认定事实如下|认定如下事实|确认事实如下))"
        rex6="^(.{,30})(^双方争议事项为|.*双方争议的焦点在于:|.*本案[一-龥]*争议焦点在于|.*本案中,[一-龥]*争议焦点|根据[一-龥]+认证,本院确认下列事实:|^本院经审核认为|^本院认为,|综合本院对事实的认定,本案的争议焦点|本案[一-龥]*争议焦点[一-龥]+:|本案中,原被告争议的焦点|.*本案[一-龥]+争议焦点[一-龥]+:|.*本院认为:|法院一审认为|本院认证认为|本院认为|一审认为)"
        temp=x.split("\n")
        state=start
        st=""
        l=[]
        for j in temp:
            if state==start:
                x1=re.search(rex1,j)
                if x1:
                    st+=j+"\n"
                    l.append(st)
                    st=""
                    state=first
                else:
                    st+=j+"\n"
            elif state==first:
                 x1=re.search(rex2,j)
                 x2=re.search(rex3,j)
                 if x1:
                    l.append(st)
                    st=j+"\n"
                    state=second
                 elif x2:
                     l.append(st)
                     l.append('')
                     st=j+"\n"
                     state=three
                 else:
                    st+=j+"\n"
            elif state==second:
                x0=re.search(rex3,j)
                x01=re.search(rex4,j)
                Rex1=re.search("(审理终结|审理完毕|审理完结|审理完毕|审理终|审理完|审理毕|合议庭[^\n]*本院缺席审理)",j,re.S)
                ###本院审理查明
                x1=re.search(rex5,j)
                x2=re.search(rex6,j)###本院认为
                x1_t=re.search("经(审|)查[,，]{1}本院认为",j)
                Rex=re.search("反诉称|辩称:|反诉请求:",j)
                if x0 and not Rex and not Rex1:
                    l.append(st)
                    st=j+"\n"
                    state=three
                elif x01 and not Rex1 :
                    l.append(st)
                    st=''
                    l.append(st)
                    st=j+"\n"
                    state=four
                elif x1 and not x1_t and not Rex1:
                    l.append(st)
                    st=''
                    l.extend(['',''])
                    st=j+"\n"
                    state=four_1
                elif x2 and not Rex1:
                    l.append(st)
                    st=''
                    l.extend(['','',''])
                    st=j+"\n"
                    state=four_2
                else:
                    st+=j+"\n"
            elif state==three:
                x0=re.search(rex4,j)
                x1=re.search(rex5,j)
                x2=re.search(rex6,j)###本院认为
                x1_t=re.search("经(审|)查[,，]{1}本院认为",j)
                Rexx=re.search("(审理终结|审理完毕|审理完结|审理完毕|审理终|审理完|审理毕|合议庭[^\n]*本院缺席审理)",j,re.S)
                if x0 and not Rexx:
                    ###原告诉称
                    l.append(st)
                    st=j+"\n"
                    Rex=re.search("本院确认[^。，、；：:]*本案事实:",j)
                    Rex1=re.search("(本案争议焦点(是|为|):|本院认为:)",j)
                    Rex2=re.search("(^.*。)([^。]*(经审理查明|经审查|经查明))",j)
                    if Rex:
                        l.append('')
                        state=four_1
                    elif Rex1:
                        l.extend(['',''])
                        state=four_2
                    elif Rex2:
                        l.append(Rex2.group(1)+"\n")
                        st=Rex2.group(2)+"\n"
                        state=four_1
                    else:
                        state=four
                elif x1 and not x1_t:
                    l.append(st)
                    st=''
                    l.append(st)
                    st=j+"\n"
                    state=four_1
                elif x2:
                    l.append(st)
                    st=''
                    l.extend([st,st])
                    st=j+"\n"
                    state=four_2
                else:
                    st+=j+"\n"
            elif state==four:
                rex="^[^。]{,30}(.*本院[^。]*认证如下:|^本院[一-龥]*证据:|.*经庭审质证|再查明|原审查明事实：|^本案在诉讼过程中|原告[^。,、；：:]*证据|^依据[一-龥]*所确认的证据和事实|原告[^。，]*有如下异议:|为证明自己主张,[^。]*向本院提供如下证据:|.*向本院提交如下证据:|.*举证据如下:|原告[^。,，]*,向[^，。、；？:：]*提交|^原告[^。]*,[^。]*举证如下:|^原告[^。]*,[^。]*证据资料:|公司[^。]*提供了下列证据材料:|.*本院[^。，]事实(如下):|.*原告[^。，]*材料:|.*本院[^。，]*事实:|.*原告[^。，]*材料:|本院认证意见如下:|原告[^。]*质证如下:|本院[^。]*,据此确认以下事实:|原告[^。]*证据:|.*本院确认以下事实:|.*被告对原告证据质证如下:|原告提供的证据材料如下:|原告[^。，,]*提供如下证据:|^综上,本院[^，。]*事实一致|.*经本院审查|.*在原一审程序中提交的证据有:|[一-龥，,]+质证意见:|^在本案审理过程中,[一-龥]+提供[一-龥]+证据材料:|原告[^。，,;：:；]+,提交[^。，;；、]+证据材料:|^法庭质证时|^在本案审理过程中,原告[一-龥]+证据材料|^原告[^,。，、:;；]*,[^:；;,。，、]*证据:|[被原]{1}告[一-龥龥]+质证意见(如下|):|^庭审中[^。]*提交了以下证据|^原告为支持其主张,提供以下证据:|^(被|原)告质证认为|^(原告|被告|第三人)[^。，、]*提供证据如下|经审理查明:|对证据认证如下:|认证如下事实|查明以下案件事实|经庭审质证|^还查明,|本院对案件事实认定如下|本院确定以下与本案有关的事实|本院对本案证据认证如下|查明以下事实|根据[^。]{,30}(陈述|证据),本院(确认如下事实|认定事实如下|认定如下事实|确认事实如下)|查明:|本院经查|本院依法认定本案事实如下|本院确认本案事实如下|本院根据上述[^。]{,30}确认以下事实|经审理|本院经查|根据上述[^。]{,30}本院确认以下事实|经审理查明|经庭审[^。，]{,5}比对|一审查明|经审查|本院查明|本院审理查明|本案相关事实|^[^。]{,30}本院(确认如下事实|认定事实如下|认定如下事实|确认事实如下))"
                x0=re.search(rex,j)##审理查明
                x_flag=re.search(rex5,j)
                x1_t=re.search("经(审|)查[,，]{1}本院认为",j)
                x1=re.search(rex6,j)###本院认为
                if(x0 or x_flag) and not x1_t:
                    l.append(st)
                    st=j+"\n"
                    state=four_1
                elif x1:##
                    l.append(st)
                    st=''
                    l.append('')
                    st=j+"\n"
                    state=four_2
                else:
                    st+=j+'\n'
            ###审理查明
            elif state==four_1:
                x0=re.search(rex6,j)###本院认为
                if x0:
                    l.append(st)
                    state=four_2
                    st=j+'\n'
                else:
                    st+=j+'\n'
            elif state==four_2:
                st+=j+"\n"
        l.append(st)
        return l
    """
    一审分段过程
    """
    def Main_Div1(i):
        x=Stander(i[1])
        key=["标题","当事人信息","审理经过","原告诉称","被告辩称","审理查明","本院认为","判决依据","判决主文","判决尾部","落款"]
        pre_,judge,flag=Sub_Judge1(x)
        ###尾部信息的获取
        ls=Sub_Judge2(judge)
        ###金额的
        if flag:
            l=Deal_all(pre_)
            #l_1.append(l)
            if len(l)==7:
                ln=Optimization1(ls[0])
                if len(ln)==2:
                    l[6]=l[6]+"\n"+l[0]
                    ls[0]=ln[1]
                l.extend(ls)
            elif len(l)==6:
                ln=Optimization1(ls[0])
                if len(ln)==2:
                    l.append(l[0])
                    ls[0]=ln[1]
                else:
                    l.append('')
                l.extend(ls)
            elif len(l)==5:
                ln=Optimization2(ls[0])
                if len(ln)==2:
                    l.append(ln[0])
                    l.append('')
                    ls[0]=ln[1]
                else:
                    l.extend(['',''])
                l.extend(ls)
            #Optimization
            elif len(l)==4:
                ln=Optimization1(ls[0])
                ln1=Optimization2(ls[0])
                if len(ln)==2:
                    l.extend(['','',ln[0]])
                    ls[0]=ln[1]
                elif len(ln1)==2:
                    l.extend(['',ln1[0],''])
                    ls[0]=ln1[1]
                else:
                    l.extend(['','',''])
                l.extend(ls)
            elif len(l)==3:
                ln=Optimization1(ls[0])
                ln1=Optimization2(ls[0])
                if len(ln)==2:
                    l.extend(['','','',ln[0]])
                    ls[0]=ln[1]
                elif len(ln1)==2:
                    l.extend(['','',ln1[0],''])
                    ls[0]=ln1[1]
                else:
                    l.extend(['','','',''])
                l.extend(ls)
        else:
            l=['无']
        if len(l)==11:
            l1=[]
            l1.append(i[0])
            l1=l1*11
            l=list(zip(l1,key,l))
        return l

    l=Main_Div1(i)
    return l
