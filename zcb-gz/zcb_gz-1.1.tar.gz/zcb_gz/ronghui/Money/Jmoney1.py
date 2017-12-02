   # -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 13:54:52 2017

@author: huanhuan
"""

import  re

"""
一审判决金额
"""
def Main_Judge1(i):

    def cut_judge1_Money(x):
        x1=re.search("(.*?)((加倍支付迟延履行期间的债务利息|于本判决生效之日起十日内付清,逾期不付,|如当事人未按本判决)|(\n如[果]{,1}被告)|(案件受理)|(案受理费)|(案件受理[0-9]+)|(案件保全费)|(公告费)|(财产保全费)|(本诉诉讼费)|(\n[^。，]{,3}诉讼费用)|(本案本诉部分受理费)|(受理费为)|(本案案件受理[0-9])|(本案征收受理费)|(.案受理费)|(本案诉讼受理费)|(各案受理费人民币)|(受理费[0-9]+\.?[0-9]*元)|(本案.{1,6}费})|([\r\n\t]诉讼费)|(本案一审受理费)|(本案应交纳诉讼费)|(本案本诉受理费)|(本案本诉诉讼费)|(本案的受理费)|(本案受理费)|(案件受理费)|(案件受理[0-9]{1})|([两三四五六七八九]案受理费)|(本案诉讼费)|(案件诉讼费)|(本案案件费)|(如不服从判决)|(受理费人民币)|(如不服本判决)|(本案[一二]审诉讼费)|(一审诉讼费)|(如(果)?未按(本)?判决指定的期间履行给付(金钱)?义务)|(如被告逾期不履行本判决所确定的金钱给付义务)|(审判长)|(审判员))",x,flags = re.S)
        if x1:
            x=x1.group(1)
        else:
            x=x
        return x
    """
    处理赘余信息
    多是利息
    """
    def cn2dig(cn):
        cn = cn.group()   ## 若使用re.sub调用时则需要启用此条语句。
        if set(cn[0]).issubset(set([u'零',u'0',u'〇',u'.',u','] + list(u'兆亿億萬万仟千佰百角分里厘毫元圆'))):
            cn = cn[1:]
        CN_NUM = {u'〇' : 0,u'一' : 1,u'二' : 2,u'三' : 3,u'四' : 4,u'五' : 5,u'六' : 6,u'七' : 7,u'八' : 8,u'九' : 9,
              u'零' : 0,u'壹' : 1,u'贰' : 2,u'叁' : 3,u'肆' : 4,u'伍' : 5,u'陆' : 6,u'柒' : 7,u'捌' : 8,u'玖' : 9,
              u'貮' : 2,u'两' : 2,
             }
        CN_UNIT = {u'毫' : 0.0001,u'厘' : 0.001,u'分' : 0.01,u'角' : 0.1,u'元' : 1,u'圆' : 1,
               u'十' : 10,u'拾' : 10,u'百' : 100,u'佰' : 100,u'千' : 1000,u'仟' : 1000,
               u'万' : 10000,u'萬' : 10000,u'亿' : 100000000,u'億' : 100000000,u'兆' : 1000000000000,u'美':7,
              }
        CN_DIGITS = [str(i) for i in range(10)]  # 用来判断单纯数字，当然包括小数在内 可以直接返回,如123.00元,123元
        CN_DIGITS.append(u"元")
        CN_DIGITS.append(u".")
        CN_DIGITS_C = [str(i) for i in range(10)] # 用科学计数法来存储的数字,比如12,765,89元
        CN_DIGITS_C.extend([u",",u"元",u"."])
        CN_DIG_CHAR = [str(i) for i in range(10)] # 处理数字加大小写的数字 比如：123万元，1亿元，2.3亿元
        CN_DIG_CHAR.extend([u"元",u".",u",",u"万",u"千",u"百",u"十",u"十万",u"百万",u"千万",u"亿",u"兆",u'美'])
        CN_DIG_CHAR_DICT = {u"万":10000,u"千":1000,u"百":100,u"十":10,u"十万":100000,u"百万":1000000,u"千万":10000000,u"亿":100000000,u'十亿':1000000000,u'百亿':10000000000,u'千亿':10000000000,u'万亿':1000000000000,u"兆":1000000000000,u'美':7}
        CN_ALL = list(CN_NUM.keys()) + list(CN_UNIT.keys()) # 用大写小写存储的数字
        if set(cn).issubset(set(CN_ALL)):
            lcn = list(cn)      # 将cn拆分为列表
            unit = 0 #当前的单位
            ldig = []#临时数组
            while lcn:
                cndig = lcn.pop()  # 从cn最后一个开始
                if cndig in CN_UNIT:                  # 对分离出的进行单位判断
                    unit = CN_UNIT.get(cndig)
                    if unit==10000:
                        ldig.append('w')    #标示万位
                        unit = 1
                    elif unit==100000000:
                        ldig.append('y')    #标示亿位
                        unit = 1
                    elif unit==1000000000000:#标示兆位
                        ldig.append('z')
                        unit = 1
                    elif unit==7:
                        ldig.append('d')
                        unit = 1
                else:                                ## 否则进行数字判断
                    dig = CN_NUM.get(cndig)

                    if unit:                  # 计算每一个单位的数 比如 四百部分：4*100
                        dig = dig*unit
                        unit = 0
                    ldig.append(dig)          # ldig 9 30 400 unit 10
            if unit==10:                            ## 单独处理10-19的数字因为 此时十作为的是数字而不是单位
                ldig.append(10)
            ret = 0
            tmp = 0
            while ldig:                       # 对ldig中各部分数字进行叠加
                x = ldig.pop()
                if x=='w':                   # 单独对万进行处理，因为前面不可以直接相乘，下面同理
                    tmp *= 10000
                    ret += tmp
                    tmp=0
                elif x=='y':
                    tmp *= 100000000
                    ret += tmp
                    tmp=0
                elif x=='z':
                    tmp *= 1000000000000
                    ret += tmp
                    tmp=0
                elif x=='d':
                    tmp*=7
                    ret += tmp
                    tmp=0

                else:
                    tmp += x
            ret += tmp
            return str(ret)+u'元'
        elif set(cn).issubset(set(CN_DIGITS)): ## 这种情况相当于为全为数字类型，可以直接返回
            return cn
        elif set(cn).issubset(set(CN_DIGITS_C)):
            return ''.join([i for i in list(cn) if i != ','])
        elif set(cn).issubset(set(CN_DIG_CHAR)): ## 对形如1.34万元进行转换
            if re.search(".*?(?=\d)",cn) is None:# 处理数字的前缀部分
                cn_pre = ''
            else:
                cn_pre = re.search(".*?(?=\d)",cn).group()
            cn = re.search("\d.*元",cn).group()
            cn_l = re.search("^\d[\d,\.]*\d?",cn).group() # 截取数字部分
            cn_l = ''.join([i for i in list(cn_l) if i != ',']) # 去逗号
            cn_l = float(cn_l)
            cn_m = re.search("[^\d元\.,]{1,2}",cn)
            if cn_m is None:
                return cn_pre+cn
            else:
                return cn_pre+str(cn_l*CN_DIG_CHAR_DICT.get(cn_m.group()))+"元"
        else:
           return "no"
    #####删除驳回的|以上其中的。。。|其中|连带责任的问题|
    ####数据的问题

    def Deal_repeat(x):
        x1=re.findall("驳回[^\r\n\t；；]*元[^\r\n\t;；]*",x)
        for i in x1:
            x=x.replace(i,"")
        return x
    """
    利息|违约金|复利|担保费|罚息|已支付|尚需付款|还需支付|尚需支付|还需付款|已支付
    扣除[^,。,;；]*[,。，；;] 余款[^,。,;；]*[,。，；;]
    对于单价的删除
    多案并处理
    """

    def Deal_interest(x):
        x=re.sub("(每[案件]{1}[^，。\n]*[0-9/.]*元[,，]{,1})([^。，,\n]*(计|共|共计|合计人民币|共计|总计|合计|共合|合共|总共)(人民币|)[0-9/.]+)元",lambda t:t.group(2),x)
        reg_interest="(利息|违约金|复利|担保费|罚息|尚需支付|已支付|还需支付|还需付款|尚需付款)[\(][^\(\)]*?[\)]"
        reg_Every="每.{0,3}[0-9]+\.?[0-9]*?元"
        reg_deal="(扣除|余款|已支付|还需支付)[^；;,，。]*?[，；。;,]"
        #####利息中关于本金的去重
        x1=re.search(reg_interest,x,re.S)
        while x1:
            x1=x1.group()
            x=x.replace(x1,"")
            x1=re.search(reg_interest,x,re.S)
        ####利息中的每的重复
        x2=re.search(reg_Every,x,re.S)
        while x2:
            x2=x2.group()
            x=x2.replace(x2,"")
            x2=re.search(reg_Every,x,re.S)
        ####关于扣除和余款方面的
        x3=re.search(reg_deal,x,re.S)
        while x3:
            x3=x3.group()
            x=x.replace(x3,"")
            x3=re.search(reg_deal,x,re.S)
        ####处理一些非钱的数字【名字中的刘三元,以及六圆都有可能翻译成6元这个要具体的看文书看看能不能改变】
        x4=re.search("、[0-9]元",x,re.S)
        while x4:
            x4=x4.group()
            x=x.replace(x4,"")
            x4=re.search("、[0-9]元",x,re.S)
        x5 = re.search("以(人民币|价款)?[0-9]+\.?[0-9]*元为(本金|基数|限)",x,re.S)
        while x5:
            x5 = x5.group()
            x = x.replace(x5,"")
            x5 = re.search("以(人民币)?[0-9]+\.?[0-9]*元为(本金|基数|限)",x,re.S)
        x6 = re.search("((总额)?超过|周年庆|按本金)[0-9]+\.?[0-9]*元",x,re.S)
        while x6:
            x6 = x6.group()
            x = x.replace(x6,"")
            x6 = re.search("((总额)?超过|周年庆|按总欠款|按本金|该)[0-9]+\.?[0-9]*元",x,re.S)
        x7 = re.search("至被告退还原告保证金(人民币)?[0-9]+\.?[0-9]*元之日止",x,re.S)
        while x7:
            x7 = x7.group()
            x = x.replace(x7,"")
            x7 = re.search("至被告退还原告保证金(人民币)?[0-9]+\.?[0-9]*元之日止",x,re.S)
        x8 = re.search(".*上述第一、二项相互抵顶",x,re.S)
        while x8:
            x8 = x8.group()
            x = x.replace(x8,"")
            x8 = re.search(".*上述第一、二项相互抵顶",x,re.S)
        x9 = re.search("元／",x,re.S)
        while x9:
           x9 = x9.group()
           x = x.replace(x9,"")
           x9 = re.search("元／",x,re.S)
        x10 = re.search("在(人民币)?[0-9]+\.?[0-9]*元(人民币)?的范围内",x,re.S)
        while x10:
           x10 = x10.group()
           x = x.replace(x10,"")
           x10 = re.search("在(人民币)?[0-9]+\.?[0-9]*元(人民币)?的范围(之)内",x,re.S)
        x11 = re.search("损失(人民币)?([0-9]+\.?[0-9]*元)(人民币)?之[0-9]{1,2}%即[0-9]+\.?[0-9]*元",x,re.S)
        while x11:
            x11 = x11.group(2)
            x = x.replace(x11,"")
            x11 = re.search("损失(人民币)?([0-9]+\.?[0-9]*元)(人民币)?之[0-9]{1,2}%即[0-9]+\.?[0-9]*元",x,re.S)
        x12 = re.search("租金[0-9]+\.?[0-9]*元(人民币)?从[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日起至实际支付日止的",x,re.S)
        while x12:
            x12 = x12.group()
            x = x.replace(x12,"")
            x12 = re.search("租金[0-9]+\.?[0-9]*元(人民币)?从[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日起至实际支付日止的",x,re.S)
        return x


    ###Stander
    def  Judge1Stander(x):
        x=x.replace("x","X") ####有可能出现这样的元的问题
        x=x.replace("（","(")
        x=x.replace("）",")")
        x=x.replace("[","(")
        x=x.replace("]",")")
        x=x.replace("【","(")
        x=x.replace("】",")")
        x=x.replace(";","；")
        x=x.replace("O","0")
        ####全元和半圆
        x=x.replace("．",".")
        x=x.replace(" ","")###首先除空格在除逗号
        ##这两两次变形，.的小数需要在除掉括号后再进行一步新的测试
        ####加一个逗号的去重
        x=re.sub("\d+(，)\d+",lambda x:(x.group()).replace("，",""),x)
        x=re.sub("\d+(,)\d+",lambda x:(x.group()).replace(",",""),x)
        x=re.sub("\d+(\.)\d+",lambda x:(x.group()).replace(".","_"),x)
        ####特殊的字符
        x=re.sub("\d+(\.)\d+",lambda x:(x.group()).replace("．","_"),x)
        return x
    '''
    除掉小括号、书名号
    '''
    def Delsp(i):
        t1='[；;,\.。，、：:]?[^；;,\.。，、：:\(\)]*元[^；;,\.。，、：:]*(\([^\(\)]*元[^\(]*[\)])[^\(\)]*?[；;,\.。，、：:]'
        k1='[；;,\.。，、：:]?[^；;,\.。，、：:]*(\([^\(\)]*元[^\(]*[\)])[^\(\)；;,\.。，、：:]*元[^\(\)]*?[；;,\.。，、：:]'
        reg_title="《[^《》]*元[^《]*?》"
        x=re.findall(t1,i)
        y=re.findall(k1,i)
        s=x+y
        l=len(s)
        j=0
        while  j<l:
            i=i.replace(s[j],"")
            j=j+1
        ####中括号的
        x=re.findall(reg_title,i)
        j=0
        l=len(x)
        while j<l:
            i=i.replace(x[j],"")
            j=j+1
        return i
    """
    连带问题？？？
    """

    def Deal_responsible(x):
        ####关于原来数据的重复，以及全部数据的重复
        """
        x1=re.search("(^.*?[0-9一二三四五六七八九十百千万亿]+[,，]{,1}[0-9一二三四五六七八九十百千万亿]*[美]{,1}元[^\n。]*)(.*)",x,re.S)
        xall=""
        if x1:
            xall=x1.group(1)
            x=x1.group(2)
        else:
            pass
        """
        xall=""
        x1=re.search("^.*?[元￥]{1}",x,re.S)
        if x1:
            xall=x1.group()
        ##上述赔偿款项中人民币200,000元承担连带赔偿责任
        x=re.sub("上述[^；。\n]*承担连带(赔偿|清偿|)责任","",x,flags=re.S)
        x=re.sub("对其中[^；\n。]*承担连带(赔偿|清偿|)责任","",x,flags=re.S)
        x1=re.search("上述[^，,。；\r\n\t]*连带(赔偿|责任)",x,re.S)

        while x1 :
            x1=x1.group()
            x=x.replace(x1,"")
            x1=re.search("上述[^，,。；\r\n\t]*连带(赔偿|责任)",x,re.S)
        #####关于其中的部分重复
        x6 = re.search("\(其中.*元.*?\)",x,re.S)
        while x6:
            x6 = x6.group()
            x = x.replace(x6,"")
            x6 = re.search("\(其中.*元.*?\)",x,re.S)
        x2=re.search("(其中[^，；。]*元.*?)[。；，]",x,re.S)
        while x2:
            x2=x2.group()
            x=x.replace(x2,"")
            x2=re.search("(其中[^，；。]*元.*?)[。；，]",x,re.S)
        ######关于连带责任的部分重复
        x=re.sub("(元)([^。，\n,]*在[0-9/.]+元范围内[^。，,\n]*连带(赔偿|清偿|)责任)",lambda t: t.group(1),x)
        x=re.sub("在[^。，;\n]*范围内承担连带赔偿责任","",x,flags=re.S)
        x5 = re.search("ZL[0-9Xx]+\.?[0-9Xx]*元",x,re.S)
        while x5:
            x5 = x5.group()
            x = x.replace(x5,"。")
            x5 = re.search("ZL[0-9Xx]+\.?[0-9Xx]*元",x,re.S)
        if x.count("元")<1:
            x=xall
        x=re.sub("元[^\n。，;:]*在[0-9\.]+元[^\n，。,]*负连带责任","元",x,flags=re.S)
        return x
    """
    小数点的恢复
    """
    def Trans(x):
        x=re.sub("[0-9]+(_)[0-9]+",lambda x:(x.group()).replace("_","."),x)
        return x
    """
    (美元|美金)([0-9]+\.?[0-9]*)元
    美元、美金、欧元、日元、新币、英镑
    """
    ###数据的问题==[]
    ###数据
    def deal_dollars(x):
        x1=re.search("(美元|美金)([0-9]+[\.]{,1}[0-9]*)(元)",x,re.S)
        while x1:
            x1=x1.group()
            ####完成美元的转化问题数据
            x2=str(float(x1[2:len(x1)-1])*7)+"元"
            x=x.replace(x1,x2)
            x1=re.search("(美元|美金)([0-9]+\.?[0-9]*)(元)",x,re.S)

        x1=re.search("([0-9]+[\.]{,1}[0-9]*)(美元)",x,re.S)

        while x1:
            x1=x1.group()
            ####完成美元的转化问题数据
            x2=str(float(x1[:len(x1)-2])*7)+"元"
            x=x.replace(x1,x2)
            x1=re.search("([0-9]+[\.]{,1}[0-9]*)(美元)",x,re.S)
        ###欧元的计算的问题
        x1=re.search("[0-9]+\.?[0-9]*(欧元)",x)
        while x1:
            x1=x1.group()
            x2=str(float(x1[:len(x1)-2])*7.27)
            x=x.replace(x1,x2)
            x1=re.search("[0-9]+\.?[0-9]*(欧元)",x)
        x1=re.findall("[^0-9\.]{2}[0-9]{1}元",x)
        #####除一些被告原告的有元的数据
        x1=re.findall("[^0-9\.]{2}[0-9]{1}元",x)
        for j in x1:
            x2=re.search("(损失|民币|罚款|开支)",j)
            if not x2:
                x=x.replace(j,"")
        return x
    """
    美元律师费人民币6,000元、公证费人民币3,000元、翻译费人民币500元；
    ###如果是美元或者是欧元，外国币的情况下我觉得涉外的可能性比较大
    驳回[^\n]8全部诉讼请求
    nu_money":钱的数量不详的
    """
    ###处理一下美元欧元的
    def Deal_all_money(x):
        x11=re.findall("[\r\n\t]?[^\r\t\n]*元.*?[\r\t\n]",x)
        temp=[]
        for i in x11:
            x1=re.findall("([0-9]+\.?[0-9]*)元",i)
            x2=re.findall("合计人民币|合计|共计|总计|共合|合共|计[0-9]+\.?[0-9]*|共[0-9]+\.?[0-9]*",i,re.S)
            if len(x1)>0 and len(x2)==0:
                money=round(sum((float(j)for j in x1)),3)
                temp.append(money)
            elif len(x1)==1 and len(x2)==1:
                money=round(float(x1[0]),3)
                temp.append(money)
            elif len(x1)==2 and len(x2)==2:
                money=round(sum(float(j) for j in x1),3)
                temp.append(money)
            elif len(x1)>1 and len(x2)==1:
                l=len(x2)
                if l>2:
                    l=x2[0][0]
                else:
                    l=x2[0]
                    l1=i.find("元")
                    e1=i.find(l)
                    strl="(?<="+l+")"+"([0-9]+\.?[0-9]*)元"
                    x_all_money=re.findall(strl,i)
                    if x_all_money:
                        x_all=round(float(x_all_money[0]),3)
                    else:
                        x_all=0
                    money=[round(float(j),3) for j in x1]
                    Money=round(sum(money),3)
                    if Money==x_all*2 or Money-min(money)+min(money)*10000==x_all*2 or l1<e1:

                        temp.append(x_all)
                    else:
                        money=round(sum(float(j) for j in x1),3)
                        temp.append(money)
            else:
                money=sum(float(b) for b in x1)
                money=round(money,3)
                temp.append(money)
        money=sum(temp)
        return money
    ###
    def MainJudge1(content):
        content=re.sub("[一二三四五六七八九十壹贰叁肆伍陆柒捌玖0-9]+案","",content)
        content=content.replace(",","")
        content=re.sub("([一二三四五六七八九十壹贰叁肆伍陆柒捌玖]{1}[元分厘]{1}(公司|店))","XX公司",content,flags=re.S)
        content=re.sub("([0-9]+)([,，]{1})([0-9]+元)",lambda t : t.group(1)+t.group(3),content,flags=re.S)
       # content=re.sub("[一二三四位]")
        content=cut_judge1_Money(content)
        AllMoney=""
        content=re.sub("(损失)([一二三四五六七八九十百千万零0〇壹1一贰2两二貮叁3三肆4四伍5五陆6六柒7七捌8八玖9九,\.兆亿億萬万仟千佰百十拾零0〇壹1一贰2两二貮叁3三肆4四伍5五陆6六柒7七捌8八玖9九角分里厘毫]+)([^零0〇壹1一贰2两二貮叁3三肆4四伍5五陆6六柒7七捌8八玖9九角分里厘毫美元一二三四五六七八九十百千万零0〇壹1一贰2两二貮叁3三肆4四伍5五陆6六柒7七捌8八玖9九,\.兆亿億萬万仟千佰百十拾]{1})",lambda content:content.group(2).replace(content.group(2),content.group(2)+"元"),content)
        content=content.replace("．",".")
        reg = "[零0〇壹1一贰2两二貮叁3三肆4四伍5五陆6六柒7七捌8八玖9九,\.兆亿億萬万仟千佰百十拾]{1,16}[元圆]{,1}[零0〇壹1一贰2两二貮叁3三肆4四伍5五陆6六柒7七捌8八玖9九角分里厘毫万]{0,9}[元角分里厘毫]{1}"
        content=re.sub(reg,cn2dig,content)  ####实现金钱的转化
        content=re.sub("([0-9]+)([,，]{1})([0-9\.]+美元)",lambda content:content.group(content.group(2),content.group(1)+content.group(3)),content)
        content=deal_dollars(content)####欧元和美元的问题
        x=Deal_repeat(content)####删除驳回的金钱的问题
        x=re.sub("[^\dXx美]元",lambda x: x.group().replace("元","yuan"),x) # 将元前面没有数字的去掉
        x=Judge1Stander(x)###规范文书中的一些问题
        x=Delsp(x)###除小括号和书名号的问题
        x=Trans(x) ###恢复小数点
        x=Deal_responsible(x)# 删除连带责任的
        x=Deal_interest(x)###除去一些利息的问题
        x1=re.findall("人民币[1-9]{1}[0-9\.]+[^某元0-9\.]{1}",x)
        for j in x1:
            if j:
                x=x.replace(j,j[:len(j)-1]+"元")
        #####金额的计算
        #print("文书的判决主文2",x)
        x=x.replace("人民币","")
        nu_money=re.findall("(XX|X0|某)元",x,re.S)
        money=re.findall("([0-9]+[\.]{,1}[0-9]*)元",x)####统计的元
        ##合计
        x_all=re.findall("(合计人民币|共计|总计|合计|共合|合共|共[0-9]+\.?[0-9]*?元|计[0-9]+\.?[0-9]*?元)",x)##总计的钱
        if len(nu_money)>0:
            AllMoney="不详"
        elif len(money)==0:###数据有七千多
            AllMoney="0"
        ####元的个数为1的
        elif len(money)==1:
            #print("Wrng1")
            AllMoney=str(money[0])
        ####元的个数大于1 并且没有合计的
        elif len(money)>1 and len(x_all)==0:
            money=sum(float(j) for j in money)
            money=round(money,3)
            #print("2")
            AllMoney=str(money)
        ######元的个数大于1而且含有总计的个数为1的
        elif len(money)>1 and len(x_all)==1:
            l=len(x_all)
            if l>2:
                l=x_all[0][0]
            else:
                l=x_all[0]
            l1=x.find("元")
            e1=x.find(l)
            ##3总数量
            l_money=[]
            money=re.findall("([0-9/.]+)元",x)
            tempmoney=sum(float(m) for m in money)
            Alltemp="0"
            tall=re.search("((总计|共计人民币|合计人民币|合计|共计|计|经济损失[及和]{0,1}合理费用|共|合))([0-9\.]+)(元)",x,re.S)
            if tall:
                Alltemp=tall.group(3)
                tempmoney=round(float(tempmoney),3)
                Alltemp=round(float(Alltemp),3)
                if Alltemp*2==tempmoney:
                    AllMoney=Alltemp


            if e1<l1:
                money=re.findall("([0-9]+[\.]{,1}[0-9]*)元",x)####统计的元
                AllMoney=sum(float(m) for m in money)
                AllMoney=round(AllMoney,3)
                AllMoney=str(AllMoney)

            else:
                x1=x.split('\n')
                all_="([^。\n]*)(总计|共计人民币|合计人民币|合计|共计|计|经济损失[及和]{0,1}合理费用|共|合)([0-9\.]+)元"
                #费前边的关键字
                re_pall="损失[^。元]*(违约金|律师费|合理费用|保全费|诉讼费|支出费用|技术转让费|合理的维权费|诉讼费|反诉费|服务费|管理费|分成费|支出费用|维权费)[^。]*元"
                re_aall="([一-龥]{2,}[款金额钱费]{1}|违约金|律师费|合理费用|保全费|诉讼费|支出费用|技术转让费|合理的维权费|诉讼费|反诉费|服务费|管理费|分成费|支出费用|维权费)[^。元]*损失[^。]*元"
                for j in x1:
                    count=j.count("元")
                    All=re.search(all_,j)
                    l1=j.find('元')
                    money=re.findall("([0-9]+[\.]{,1}[0-9]*)元",j)
                    if count>1 and  (re_pall or re_aall) and  All:
                        if len(l_money)==0:
                            Money=All.group(3)
                            Money=round(float(Money),3)
                            l_money.append(Money)
                        else:
                            Money=sum(float(m) for m in money)
                            Money=round(Money,3)
                            Money1=All.group(3)
                            Money1=round(float(Money1),3)
                            NewMoney=sum(float(m) for m in money)+sum(float(m) for m in l_money)
                            NewMoney=round(NewMoney,3)
                            if Money==Money1*2:
                                l_money.append(Money1)
                            elif Money1*2==NewMoney:
                                l_money=[]
                                l_money.append(Money1)
                            else:
                                l_money.append(Money)
                    else:
                          Money=sum(float(m) for m in money)
                          l_money.append(Money)
                AllMoney=sum(float(m) for m in l_money)
                AllMoney=round(AllMoney,3)
                AllMoney=str(AllMoney)
        elif len(money)==2 and len(x_all)==2:###两个合计的问题
            money=sum(float(j) for j in money)
            AllMoney=str(money)
        else:
            money=Deal_all_money(x)
            AllMoney=(str(money))
        return AllMoney
    content=i[8][2]
    money= MainJudge1(content)
    return money
