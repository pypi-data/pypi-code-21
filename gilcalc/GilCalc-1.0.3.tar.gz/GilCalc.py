import requests,json,time,threading
class GilCalc:
    
    #quantapi.gilcalc.com 127.0.0.1
    def __init__(self,uid,usecret):
        self.__remoteip="quantapi.gilcalc.com"
        urltoken="http://{0}:10625/OAuth/Token".format(self.__remoteip)
        payload = "client_id={0}&client_secret={1}&grant_type=client_credentials"
        tokenheaders = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    }
        
        self.__client_id=uid
        self.__client_secret=usecret
        try:
            response = requests.request("POST", urltoken, data=payload.format(uid,usecret), headers=tokenheaders)
            jsonTxt=json.loads(response.text)
            self.__token=jsonTxt['access_token']
            self.__refreshtoken=jsonTxt['refresh_token']
            self.__expires_in=jsonTxt['expires_in']
            timer = threading.Timer(self.__expires_in-60, self.__RefreshToken)
            timer.start()
        except BaseException as ex:
            
            print("登录失败..")
            print(str(ex))
            return
        
        print("登录成功..")
        #刷新token 提前1分钟刷新
    def DH_Q_HF_Stock(self,secuCode,tradingDay,*columns):
        '''
         证券高频分笔行情(证券代码,交易日,交易信息列)

        '''
        
        urlapi="http://{0}:38515/api/HF/DH_Q_HF_Stock".format(self.__remoteip)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
        data={"SecuCode":secuCode,"TradingDay":tradingDay,"Fields":[x for x in columns]}
        in_json = json.dumps(data)
        
        try:
            response = requests.request("POST", urlapi, data=in_json, headers=headers)
            return json.loads(response.text)
        except BaseException as ex:
            print("DH_Q_HF_Stock请求失败..")
            print(str(ex))
    def DH_Q_HF_StockSlice(self,secuCode,tradingDay,Slice,*columns):
        '''
         证券高频分时行情(证券代码,交易日,分钟,交易信息列)

        '''
        
        urlapi="http://{0}:38515/api/HF/DH_Q_HF_StockSlice".format(self.__remoteip)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
        data={"SecuCode":secuCode,"TradingDay":tradingDay,"Slice":Slice,"Fields":[x for x in columns]}
        in_json = json.dumps(data)
        
        try:
            response = requests.request("POST", urlapi, data=in_json, headers=headers)
            return json.loads(response.text)
        except BaseException as ex:
            print("DH_Q_HF_Stock请求失败..")
            print(str(ex))
    def DH_Q_HF_Future(self,secuCode,tradingDay,*columns):
        '''
         期货高频分笔行情(期货代码,交易日,交易信息列)

        '''
        
        urlapi="http://{0}:38515/api/HF/DH_Q_HF_Future".format(self.__remoteip)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
        data={"SecuCode":secuCode,"TradingDay":tradingDay,"Fields":[x for x in columns]}
        in_json = json.dumps(data)
        
        try:
            response = requests.request("POST", urlapi, data=in_json, headers=headers)
            return json.loads(response.text)
        except BaseException as ex:
            print("DH_Q_HF_Stock请求失败..")
            print(str(ex))
    def DH_Q_HF_FutureSlice(self,secuCode,tradingDay,Slice,*columns):
        '''
         期货高频分时行情(期货代码,交易日,分钟,交易信息列)

        '''
        
        urlapi="http://{0}:38515/api/HF/DH_Q_HF_FutureSlice".format(self.__remoteip)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
        data={"SecuCode":secuCode,"TradingDay":tradingDay,"Slice":Slice,"Fields":[x for x in columns]}
        in_json = json.dumps(data)
        
        try:
            response = requests.request("POST", urlapi, data=in_json, headers=headers)
            return json.loads(response.text)
        except BaseException as ex:
            print("DH_Q_HF_Stock请求失败..")
            print(str(ex))
    def DH_Q_HF_Option(self,secuCode,tradingDay,*columns):
        '''
         期权高频分笔行情(期权代码,交易日,交易信息列)

        '''
        
        urlapi="http://{0}:38515/api/HF/DH_Q_HF_Option".format(self.__remoteip)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
        data={"SecuCode":secuCode,"TradingDay":tradingDay,"Fields":[x for x in columns]}
        in_json = json.dumps(data)
        
        try:
            response = requests.request("POST", urlapi, data=in_json, headers=headers)
            return json.loads(response.text)
        except BaseException as ex:
            print("DH_Q_HF_Stock请求失败..")
            print(str(ex))
    def DH_Q_HF_OptionSlice(self,secuCode,tradingDay,Slice,*columns):
        '''
          期权高频分时行情(期权代码,交易日,分钟,交易信息列)

        '''
        
        urlapi="http://{0}:38515/api/HF/DH_Q_HF_OptionSlice".format(self.__remoteip)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
        data={"SecuCode":secuCode,"TradingDay":tradingDay,"Slice":Slice,"Fields":[x for x in columns]}
        in_json = json.dumps(data)
        
        try:
            response = requests.request("POST", urlapi, data=in_json, headers=headers)
            return json.loads(response.text)
        except BaseException as ex:
            print("DH_Q_HF_Stock请求失败..")
            print(str(ex))
    def SingleCalc(self,funcname,*args):
        urlapi="http://{0}:38515/api/Calc/SingleCalc".format(self.__remoteip)
        arg=",".join([str(x) for x in args])
        querystring = {"Func":"{0}({1})".format(funcname,arg)}
        #print(in_json)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
         
        try:
            response = requests.request("GET", urlapi,headers=headers,params=querystring)
            return json.loads(response.text)
        except BaseException as ex:
            print("SingleCalc请求失败..")
            print(str(ex))
    def BatchCalc(self,arrexp=[]):
        payload =arrexp
        in_json = json.dumps(payload)
        #print(in_json)
        headers = {
    'authorization': "Bearer  {0}".format(self.__token),
    'content-type': "application/json",
    'accept-charset': "utf-8",
    'cache-control': "no-cache",
    }
        url="http://{0}:38515/api/Calc/BatchCalc".format(self.__remoteip)
        try:
            response = requests.request("POST", url,data=in_json, headers=headers)
            return json.loads(response.text)
        except BaseException as ex:
            print("BatchCalc请求失败..")
            print(str(ex))
    
    def __RefreshToken(self):
        urltoken="http://{0}:10625/OAuth/Token".format(self.__remoteip)
        payload = "client_id={0}&client_secret={1}&grant_type=refresh_token&refresh_token={2}"
        tokenheaders = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    }
        
        try:
            response = requests.request("POST", urltoken, data=payload.format(self.__client_id,self.__client_secret,self.__refreshtoken), headers=tokenheaders)
            jsonTxt=json.loads(response.text)
            self.__token=jsonTxt['access_token']
            self.__refreshtoken=jsonTxt['refresh_token']
            self.__expires_in=jsonTxt['expires_in']
        except BaseException as ex:
            print("更新token失败..")
            print(str(ex))
        timer = threading.Timer(self.__expires_in-60, self.__RefreshToken)
        timer.start()



        
        
        
