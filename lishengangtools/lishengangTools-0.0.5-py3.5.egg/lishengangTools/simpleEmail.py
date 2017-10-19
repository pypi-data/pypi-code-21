#/usr/bin/env python3
#-*- coding: utf-8 -*-
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr, formatdate
import smtplib,mimetypes,os,time
def help():
	print('''
	
	支持两种参数调用方式：

1.关键字参数调用：

if __name__=='__main__':
    From='xxxx@qq.com'
    To=['xx@xx.com','xx@xxa.com']
    Pwd='xxxx'
    Screen='测试'
    Content='test'
    Serve='smtp.qq.com'
    Subject='这是一个测试'
    BCC=['test@mmeitech.com']
    CC=['cszy2013@163.com']
    SSL=True
    Port=465
    mail=SimpleEmail(From=From,To=To,Pwd=Pwd,Screen=Screen,Content=Content,Serve=Serve,Subject=Subject,BCC=BCC,CC=CC,SSL=SSL,Port=Port)
    result=mail.send()
    if result:
        print('send success!')
    else:
        print('send failed!')
2.tuple参数调用

if __name__=='__main__':
    data={
    'From':'xx@163.com','Pwd':'xxxx','To':['xx@qq.com'],
    'Screen':'测试2','Subject':'啊哈哈',
    'Serve':'smtp@163.com','Attachment':['E://1.png','C://tm//1.txt'],
    'Content':'111222'
    }
    mail=SimpleEmail(data)
    result=mail.send()
    if result:
        print('send success!')
    else:
        print('send failed!')
本类中：
1.使用QQ邮箱的时候，密码是授权码，SSL=True，Port=465
2.使用Gmail的时候，设置TLS=True,Port=587
3.使用163，阿里云等企业邮箱的时候，无需设置端口和其他，已经默认。
	
	
	''')
class SimpleEmail(object):
    def __init__(self,*kw,From='',Screen='',Pwd='',To='',CC=[],BCC=[],Subject='',Content='',Port=25,Serve='',Attachment=[],Emailtype='HTML',SSL=False,TLS=False):
        kw1={'From':From,'Screen':Screen,'CC':CC,'Pwd':Pwd,'To':To,'BCC':BCC,'Subject':Subject,'Content':Content,'Port':Port,'Serve':Serve,'Attachment':Attachment,'Emailtype':Emailtype,'SSL':SSL,'TLS':TLS}
        if len(kw)==0:
            kw=kw1
        else:
            kw=kw[0]
            for k in kw1:
                if not k in kw:
                    kw[k]=kw1[k]
        self.From,self.Pwd,self.Serve,self.Port,self.SSL,self.To,self.BCC,self.CC,self.TLS=kw['From'],kw['Pwd'],kw['Serve'],kw['Port'],kw['SSL'],kw['To'],kw['BCC'],kw['CC'],kw['TLS']
        MIMEmain=MIMEMultipart()
        MIMEmain['Date']=formatdate()
        MIMEmain['X-Mailer']='By Python'
        MIMEmain['Message-ID']='<%s%s>' % (int(time.time()*10000000),kw['From'])
        MIMEmain['From']=formataddr((Header(kw['Screen'],'utf-8').encode(),kw['From']))
        MIMEmain['To']=', '.join(kw['To'])
        MIMEmain['Cc']=', '.join(kw['CC'])
        MIMEmain['Subject']=Header(kw['Subject'],'utf-8').encode()
        MIMEmain.attach(MIMEText(kw['Content'],kw['Emailtype'],'utf-8'))
        if isinstance(kw['Attachment'],list) and len(kw['Attachment'])>0:
            count=0
            for i in kw['Attachment']:
                with open(i,'rb') as f:
                    ext1,ext2=mimetypes.guess_type(i)
                    if ext1==None or not ext2==None:
                        ext1='application/octet-stream'
                    ext3,ext4=ext1.split('/',1)
                    mimefile=MIMEBase(ext3,ext4,filename=os.path.split(i)[1])
                    mimefile.add_header('Content-Disposition','attachment',filename=os.path.split(i)[1])
                    mimefile.add_header('Content-ID','<%s>'%count)
                    mimefile.add_header('X-Attachment-ID','%s'%count)
                    count+=1
                    mimefile.set_payload(f.read())
                    encoders.encode_base64(mimefile)
                    MIMEmain.attach(mimefile)
        self.MIMEmain=MIMEmain
    def multistyle_args():
        pass
    def send(self):
        if self.SSL:
            mail=smtplib.SMTP_SSL(self.Serve,self.Port)
        else:
            mail=smtplib.SMTP(self.Serve,self.Port)
        if self.TLS:
            mail.starttls()
        mail.login(self.From,self.Pwd)
        try:
            mail.sendmail(self.From,self.To+self.CC+self.BCC,self.MIMEmain.as_string())
            mail.quit()
        except:
            return False
        finally:
            return True