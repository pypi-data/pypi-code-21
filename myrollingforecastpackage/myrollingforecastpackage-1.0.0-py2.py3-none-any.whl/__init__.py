import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn import metrics
import numpy
import matplotlib.pyplot as plt

class Rollingpredict:

    def __init__(self, path):
        self.full_path = path
        
    def show_originalpath(self):
        print(self.full_path)

    def read_originalfile(self):
        self.df_original = pd.read_csv(self.full_path)
        self.istherecalendar = 0
        self.istherework = 0
        
        
    def read_calendaralt(self, path): 
        self.df_calendar = pd.read_csv(path, sep=';')
        self.istherecalendar = 1
       
    
    def read_calendar(self, path): 
        self.df_calendar = pd.read_csv(path)
        self.istherecalendar = 1
        
    def show_originalfile(self):
        print(self.df_original)
    
    def show_work(self):
        print(self.df_work)
    
    
    def select_numcolumns(self, *columns):
        choosen_values = []
        for var in columns:
            choosen_values.append(var)
        self.df_work = self.df_original.iloc[:, choosen_values]
        self.istherework = 1
        
    def select_textcolumns(self, *columnstext):
        choosen_values = []
        for var in columnstext:
            choosen_values.append(var)
        self.df_work = self.df_original[choosen_values]
        
        
    def reset_worktooriginal(self):
        self.df_work = self.df_original
        
        
    def autopredict_week(self, tickhour, tickday, tickweek, datecolumn, weekendcolumn, fromrow, tillrow, predictcolumn, *columns):
        self.tickweek_week = tickweek
        if self.istherework == 1:
            self.df_aftercalendar = self.df_work
        if self.istherework == 0:
            self.df_aftercalendar = self.df_original
        if self.istherecalendar == 1 and datecolumn > -1:
            a = self.df_aftercalendar.iloc[:, datecolumn]
            b = self.df_calendar.iloc[:, 0]
            isitholiday = self.df_calendar.iloc[:, 3]
            for var in range(0, self.df_aftercalendar.shape[0]):
                 if var - tickweek > 0:
                        for days in range(0, self.df_calendar.shape[0]):
                            if a[var:var + 1].item() > b[days:days + 1].item():
                                break
                            if a[var:var + 1].item() == b[days:days + 1].item() and isitholiday[days:days + 1].item() ==1 :
                                self.df_aftercalendar.iloc[var,:] = self.df_aftercalendar.iloc[var - tickweek,:] 
        choosen_columns =[]
        choosen_columns.append(predictcolumn)
        isthereweekendcolumn = 0
        if weekendcolumn > -1:
            choosen_columns.append(weekendcolumn)
            isthereweekendcolumn = 1
        for var in columns:
            choosen_columns.append(var)
        self.df_work_autoweek = self.df_aftercalendar.iloc[:, choosen_columns]
        self.numberoforigcolumns = self.df_work_autoweek.shape[1]
        for var in range(1 + isthereweekendcolumn, self.df_work_autoweek.shape[1]):
            number = self.df_work_autoweek.dtypes.index[var]
            numberstring = str(number) + str('_1')
            self.df_work_autoweek[numberstring] = self.df_work_autoweek.iloc[:, var]
        for var in range(1 + isthereweekendcolumn, self.numberoforigcolumns):
            number = self.df_work_autoweek.dtypes.index[var]
            numberstring = str(number) + str('_168')
            self.df_work_autoweek[numberstring] = self.df_work_autoweek.iloc[:, var]
        self.fromrowvalue = tickweek + tickday
        self.tillrowvalue = self.df_work_autoweek.shape[0]
        if fromrow > -1 and fromrow > tickweek + tickday and fromrow < self.df_work_autoweek.shape[0]:
            self.fromrowvalue = fromrow
        if tillrow < self.df_work_autoweek.shape[0] and tillrow >  self.fromrowvalue:
            self.tillrowvalue = tillrow
        self.y_predictedvalues_week =[]
        self.y_originalvalues_week =[]
        self.indexoriginal_predictedvalues_week =[]
        self.frombeforetick_predictedvalues_week =[]
        for var in range(0, self.tillrowvalue):
            if var + tickweek >= self.df_work_autoweek.shape[0]:
                break
            if var - self.fromrowvalue > 0 and (var - self.fromrowvalue) % tickday == 0:
                for var2 in range(0, var):
                    if var2 - tickweek >= 0:
                        for var3 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                            columnnumber = var3 + self.numberoforigcolumns
                            self.df_work_autoweek.iloc[var2,columnnumber] = self.df_work_autoweek.iloc[var2 - 1,var3 + 1 + isthereweekendcolumn]
                        for var4 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                            columnnumber2 = var4 + self.numberoforigcolumns + self.numberoforigcolumns - isthereweekendcolumn - 1
                            self.df_work_autoweek.iloc[var2,columnnumber2] = self.df_work_autoweek.iloc[var2 - tickweek,var4 + 1 + isthereweekendcolumn]
                for vartickweek in range(0, tickweek):
                    for var5 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                        columnnumber3 = var5 + self.numberoforigcolumns
                        self.df_work_autoweek.iloc[var + vartickweek,columnnumber3] = self.df_work_autoweek.iloc[var - 1,var5 + 1 + isthereweekendcolumn]
                    for var6 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                        columnnumber4 = var6 + self.numberoforigcolumns + self.numberoforigcolumns - isthereweekendcolumn - 1
                        self.df_work_autoweek.iloc[var + vartickweek,columnnumber4] = self.df_work_autoweek.iloc[var + vartickweek - tickweek,var6 + 1 + isthereweekendcolumn]
                choosen_columnstrain =[]
                if isthereweekendcolumn == 1:
                    choosen_columnstrain.append(1)
                for columnstrain in range(self.numberoforigcolumns, self.df_work_autoweek.shape[1]):
                    choosen_columnstrain.append(columnstrain)
                est = GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.10)
                self.df_temp_work_week_train = self.df_work_autoweek[tickweek:var]
                self.temp_xtrain_week_train = self.df_temp_work_week_train.iloc[:, choosen_columnstrain]
                self.temp_ytrain_week_train = self.df_temp_work_week_train.iloc[:, 0]
                
                self.df_temp_work_week_predict = self.df_work_autoweek[var:var + tickweek]
                self.temp_xforpredictweek =  self.df_temp_work_week_predict.iloc[:, choosen_columnstrain]        
                est.fit(self.temp_xtrain_week_train,self.temp_ytrain_week_train)
                self.ypred_week = est.predict(self.temp_xforpredictweek)
                
                for varpredictnum in range(0,self.ypred_week.shape[0]):
                    self.y_predictedvalues_week.append(self.ypred_week[varpredictnum])
                    self.y_originalvalues_week.append(self.df_work_autoweek.iloc[var + varpredictnum,0])
                    self.indexoriginal_predictedvalues_week.append(var + varpredictnum)
                    self.frombeforetick_predictedvalues_week.append(varpredictnum + 1)
         
        
    def manualpredict_week(self, nestimators, maxdepth, learningrate, tickhour, tickday, tickweek, datecolumn, weekendcolumn, fromrow, tillrow, predictcolumn, *columns):
        self.tickweek_week = tickweek
        if self.istherework == 1:
            self.df_aftercalendar = self.df_work
        if self.istherework == 0:
            self.df_aftercalendar = self.df_original
        if self.istherecalendar == 1 and datecolumn > -1:
            a = self.df_aftercalendar.iloc[:, datecolumn]
            b = self.df_calendar.iloc[:, 0]
            isitholiday = self.df_calendar.iloc[:, 3]
            for var in range(0, self.df_aftercalendar.shape[0]):
                 if var - tickweek > 0:
                        for days in range(0, self.df_calendar.shape[0]):
                            if a[var:var + 1].item() > b[days:days + 1].item():
                                break
                            if a[var:var + 1].item() == b[days:days + 1].item() and isitholiday[days:days + 1].item() ==1 :
                                self.df_aftercalendar.iloc[var,:] = self.df_aftercalendar.iloc[var - tickweek,:] 
        choosen_columns =[]
        choosen_columns.append(predictcolumn)
        isthereweekendcolumn = 0
        if weekendcolumn > -1:
            choosen_columns.append(weekendcolumn)
            isthereweekendcolumn = 1
        for var in columns:
            choosen_columns.append(var)
        self.df_work_autoweek = self.df_aftercalendar.iloc[:, choosen_columns]
        self.numberoforigcolumns = self.df_work_autoweek.shape[1]
        for var in range(1 + isthereweekendcolumn, self.df_work_autoweek.shape[1]):
            number = self.df_work_autoweek.dtypes.index[var]
            numberstring = str(number) + str('_1')
            self.df_work_autoweek[numberstring] = self.df_work_autoweek.iloc[:, var]
        for var in range(1 + isthereweekendcolumn, self.numberoforigcolumns):
            number = self.df_work_autoweek.dtypes.index[var]
            numberstring = str(number) + str('_168')
            self.df_work_autoweek[numberstring] = self.df_work_autoweek.iloc[:, var]
        self.fromrowvalue = tickweek + tickday
        self.tillrowvalue = self.df_work_autoweek.shape[0]
        if fromrow > -1 and fromrow > tickweek + tickday and fromrow < self.df_work_autoweek.shape[0]:
            self.fromrowvalue = fromrow
        if tillrow < self.df_work_autoweek.shape[0] and tillrow >  self.fromrowvalue:
            self.tillrowvalue = tillrow
        self.y_predictedvalues_week =[]
        self.y_originalvalues_week =[]
        self.indexoriginal_predictedvalues_week =[]
        self.frombeforetick_predictedvalues_week =[]
        for var in range(0, self.tillrowvalue):
            if var + tickweek >= self.df_work_autoweek.shape[0]:
                break
            if var - self.fromrowvalue > 0 and (var - self.fromrowvalue) % tickday == 0:
                for var2 in range(0, var):
                    if var2 - tickweek >= 0:
                        for var3 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                            columnnumber = var3 + self.numberoforigcolumns
                            self.df_work_autoweek.iloc[var2,columnnumber] = self.df_work_autoweek.iloc[var2 - 1,var3 + 1 + isthereweekendcolumn]
                        for var4 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                            columnnumber2 = var4 + self.numberoforigcolumns + self.numberoforigcolumns - isthereweekendcolumn - 1
                            self.df_work_autoweek.iloc[var2,columnnumber2] = self.df_work_autoweek.iloc[var2 - tickweek,var4 + 1 + isthereweekendcolumn]
                for vartickweek in range(0, tickweek):
                    for var5 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                        columnnumber3 = var5 + self.numberoforigcolumns
                        self.df_work_autoweek.iloc[var + vartickweek,columnnumber3] = self.df_work_autoweek.iloc[var - 1,var5 + 1 + isthereweekendcolumn]
                    for var6 in range(0, self.numberoforigcolumns - isthereweekendcolumn - 1):
                        columnnumber4 = var6 + self.numberoforigcolumns + self.numberoforigcolumns - isthereweekendcolumn - 1
                        self.df_work_autoweek.iloc[var + vartickweek,columnnumber4] = self.df_work_autoweek.iloc[var + vartickweek - tickweek,var6 + 1 + isthereweekendcolumn]
                choosen_columnstrain =[]
                if isthereweekendcolumn == 1:
                    choosen_columnstrain.append(1)
                for columnstrain in range(self.numberoforigcolumns, self.df_work_autoweek.shape[1]):
                    choosen_columnstrain.append(columnstrain)
                est = GradientBoostingRegressor(n_estimators=nestimators, max_depth=maxdepth, learning_rate=learningrate)
                self.df_temp_work_week_train = self.df_work_autoweek[tickweek:var]
                self.temp_xtrain_week_train = self.df_temp_work_week_train.iloc[:, choosen_columnstrain]
                self.temp_ytrain_week_train = self.df_temp_work_week_train.iloc[:, 0]
                
                self.df_temp_work_week_predict = self.df_work_autoweek[var:var + tickweek]
                self.temp_xforpredictweek =  self.df_temp_work_week_predict.iloc[:, choosen_columnstrain]        
                est.fit(self.temp_xtrain_week_train,self.temp_ytrain_week_train)
                self.ypred_week = est.predict(self.temp_xforpredictweek)
                
                for varpredictnum in range(0,self.ypred_week.shape[0]):
                    self.y_predictedvalues_week.append(self.ypred_week[varpredictnum])
                    self.y_originalvalues_week.append(self.df_work_autoweek.iloc[var + varpredictnum,0])
                    self.indexoriginal_predictedvalues_week.append(var + varpredictnum)
                    self.frombeforetick_predictedvalues_week.append(varpredictnum + 1)                    
    
    def autopredict_day(self, tickhour, tickday, tickweek, datecolumn, weekendcolumn, fromrow, tillrow, predictcolumn, *columns):
        self.tickweek_day = tickweek
        self.tickday_day = tickday
        if self.istherework == 1:
            self.df_aftercalendar_day = self.df_work
        if self.istherework == 0:
            self.df_aftercalendar_day = self.df_original
        if self.istherecalendar == 1 and datecolumn > -1:
            a = self.df_aftercalendar_day.iloc[:, datecolumn]
            b = self.df_calendar.iloc[:, 0]
            isitholiday = self.df_calendar.iloc[:, 3]
            for var in range(0, self.df_aftercalendar_day.shape[0]):
                 if var - tickweek > 0:
                        for days in range(0, self.df_calendar.shape[0]):
                            if a[var:var + 1].item() > b[days:days + 1].item():
                                break
                            if a[var:var + 1].item() == b[days:days + 1].item() and isitholiday[days:days + 1].item() ==1 :
                                self.df_aftercalendar_day.iloc[var,:] = self.df_aftercalendar_day.iloc[var - tickweek,:] 
        choosen_columns =[]
        choosen_columns.append(predictcolumn)
        isthereweekendcolumn = 0
        if weekendcolumn > -1:
            choosen_columns.append(weekendcolumn)
            isthereweekendcolumn = 1
        for var in columns:
            choosen_columns.append(var)
        self.df_work_auto_day = self.df_aftercalendar_day.iloc[:, choosen_columns]
        self.numberoforigcolumns_day = self.df_work_auto_day.shape[1]
        for var in range(1 + isthereweekendcolumn, self.df_work_auto_day.shape[1]):
            number = self.df_work_auto_day.dtypes.index[var]
            numberstring = str(number) + str('_1')
            self.df_work_auto_day[numberstring] = self.df_work_auto_day.iloc[:, var]
        for var in range(1 + isthereweekendcolumn, self.numberoforigcolumns_day):
            number = self.df_work_auto_day.dtypes.index[var]
            numberstring = str(number) + str('_168')
            self.df_work_auto_day[numberstring] = self.df_work_auto_day.iloc[:, var]
        self.fromrowvalue_day = tickweek + tickday
        self.tillrowvalue_day = self.df_work_auto_day.shape[0]
        if fromrow > -1 and fromrow > tickweek + tickday and fromrow < self.df_work_auto_day.shape[0]:
            self.fromrowvalue_day = fromrow
        if tillrow < self.df_work_auto_day.shape[0] and tillrow >  self.fromrowvalue_day:
            self.tillrowvalue_day = tillrow
        self.y_predictedvalues_day =[]
        self.y_originalvalues_day =[]
        self.indexoriginal_predictedvalues_day =[]
        self.frombeforetick_predictedvalues_day =[]
        self.tickhour_day = tickhour
        if tickhour < 1:
            self.tickhour_day = 1
        for var in range(0, self.tillrowvalue_day):
            if var + tickday >= self.df_work_auto_day.shape[0]:
                break
            if var - self.fromrowvalue_day > 0 and (var - self.fromrowvalue_day) % self.tickhour_day == 0:
                for var2 in range(0, var):
                    if var2 - tickweek >= 0:
                        for var3 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                            columnnumber = var3 + self.numberoforigcolumns_day
                            self.df_work_auto_day.iloc[var2,columnnumber] = self.df_work_auto_day.iloc[var2 - 1,var3 + 1 + isthereweekendcolumn]
                        for var4 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                            columnnumber2 = var4 + self.numberoforigcolumns_day + self.numberoforigcolumns_day - isthereweekendcolumn - 1
                            self.df_work_auto_day.iloc[var2,columnnumber2] = self.df_work_auto_day.iloc[var2 - tickweek,var4 + 1 + isthereweekendcolumn]
                for vartickweek in range(0, tickday):
                    for var5 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                        columnnumber3 = var5 + self.numberoforigcolumns_day
                        self.df_work_auto_day.iloc[var + vartickweek,columnnumber3] = self.df_work_auto_day.iloc[var - 1,var5 + 1 + isthereweekendcolumn]
                    for var6 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                        columnnumber4 = var6 + self.numberoforigcolumns_day + self.numberoforigcolumns_day - isthereweekendcolumn - 1
                        self.df_work_auto_day.iloc[var + vartickweek,columnnumber4] = self.df_work_auto_day.iloc[var + vartickweek - tickweek,var6 + 1 + isthereweekendcolumn]
                choosen_columnstrain =[]
                if isthereweekendcolumn == 1:
                    choosen_columnstrain.append(1)
                for columnstrain in range(self.numberoforigcolumns_day, self.df_work_auto_day.shape[1]):
                    choosen_columnstrain.append(columnstrain)
                est = GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.10)
                self.df_temp_work_day_train = self.df_work_auto_day[tickweek:var]
                self.temp_xtrain_day_train = self.df_temp_work_day_train.iloc[:, choosen_columnstrain]
                self.temp_ytrain_day_train = self.df_temp_work_day_train.iloc[:, 0]
                
                self.df_temp_work_day_predict = self.df_work_auto_day[var:var + tickday]
                self.temp_xforpredictday =  self.df_temp_work_day_predict.iloc[:, choosen_columnstrain]        
                est.fit(self.temp_xtrain_day_train,self.temp_ytrain_day_train)
                self.ypred_day = est.predict(self.temp_xforpredictday)
                
                for varpredictnum in range(0,self.ypred_day.shape[0]):
                    self.y_predictedvalues_day.append(self.ypred_day[varpredictnum])
                    self.y_originalvalues_day.append(self.df_work_auto_day.iloc[var + varpredictnum,0])
                    self.indexoriginal_predictedvalues_day.append(var + varpredictnum)
                    self.frombeforetick_predictedvalues_day.append(varpredictnum + 1)

    def manualpredict_day(self, nestimators, maxdepth, learningrate, tickhour, tickday, tickweek, datecolumn, weekendcolumn, fromrow, tillrow, predictcolumn, *columns):
        self.tickweek_day = tickweek
        self.tickday_day = tickday
        if self.istherework == 1:
            self.df_aftercalendar_day = self.df_work
        if self.istherework == 0:
            self.df_aftercalendar_day = self.df_original
        if self.istherecalendar == 1 and datecolumn > -1:
            a = self.df_aftercalendar_day.iloc[:, datecolumn]
            b = self.df_calendar.iloc[:, 0]
            isitholiday = self.df_calendar.iloc[:, 3]
            for var in range(0, self.df_aftercalendar_day.shape[0]):
                 if var - tickweek > 0:
                        for days in range(0, self.df_calendar.shape[0]):
                            if a[var:var + 1].item() > b[days:days + 1].item():
                                break
                            if a[var:var + 1].item() == b[days:days + 1].item() and isitholiday[days:days + 1].item() ==1 :
                                self.df_aftercalendar_day.iloc[var,:] = self.df_aftercalendar_day.iloc[var - tickweek,:] 
        choosen_columns =[]
        choosen_columns.append(predictcolumn)
        isthereweekendcolumn = 0
        if weekendcolumn > -1:
            choosen_columns.append(weekendcolumn)
            isthereweekendcolumn = 1
        for var in columns:
            choosen_columns.append(var)
        self.df_work_auto_day = self.df_aftercalendar_day.iloc[:, choosen_columns]
        self.numberoforigcolumns_day = self.df_work_auto_day.shape[1]
        for var in range(1 + isthereweekendcolumn, self.df_work_auto_day.shape[1]):
            number = self.df_work_auto_day.dtypes.index[var]
            numberstring = str(number) + str('_1')
            self.df_work_auto_day[numberstring] = self.df_work_auto_day.iloc[:, var]
        for var in range(1 + isthereweekendcolumn, self.numberoforigcolumns_day):
            number = self.df_work_auto_day.dtypes.index[var]
            numberstring = str(number) + str('_168')
            self.df_work_auto_day[numberstring] = self.df_work_auto_day.iloc[:, var]
        self.fromrowvalue_day = tickweek + tickday
        self.tillrowvalue_day = self.df_work_auto_day.shape[0]
        if fromrow > -1 and fromrow > tickweek + tickday and fromrow < self.df_work_auto_day.shape[0]:
            self.fromrowvalue_day = fromrow
        if tillrow < self.df_work_auto_day.shape[0] and tillrow >  self.fromrowvalue_day:
            self.tillrowvalue_day = tillrow
        self.y_predictedvalues_day =[]
        self.y_originalvalues_day =[]
        self.indexoriginal_predictedvalues_day =[]
        self.frombeforetick_predictedvalues_day =[]
        self.tickhour_day = tickhour
        if tickhour < 1:
            self.tickhour_day = 1
        for var in range(0, self.tillrowvalue_day):
            if var + tickday >= self.df_work_auto_day.shape[0]:
                break
            if var - self.fromrowvalue_day > 0 and (var - self.fromrowvalue_day) % self.tickhour_day == 0:
                for var2 in range(0, var):
                    if var2 - tickweek >= 0:
                        for var3 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                            columnnumber = var3 + self.numberoforigcolumns_day
                            self.df_work_auto_day.iloc[var2,columnnumber] = self.df_work_auto_day.iloc[var2 - 1,var3 + 1 + isthereweekendcolumn]
                        for var4 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                            columnnumber2 = var4 + self.numberoforigcolumns_day + self.numberoforigcolumns_day - isthereweekendcolumn - 1
                            self.df_work_auto_day.iloc[var2,columnnumber2] = self.df_work_auto_day.iloc[var2 - tickweek,var4 + 1 + isthereweekendcolumn]
                for vartickweek in range(0, tickday):
                    for var5 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                        columnnumber3 = var5 + self.numberoforigcolumns_day
                        self.df_work_auto_day.iloc[var + vartickweek,columnnumber3] = self.df_work_auto_day.iloc[var - 1,var5 + 1 + isthereweekendcolumn]
                    for var6 in range(0, self.numberoforigcolumns_day - isthereweekendcolumn - 1):
                        columnnumber4 = var6 + self.numberoforigcolumns_day + self.numberoforigcolumns_day - isthereweekendcolumn - 1
                        self.df_work_auto_day.iloc[var + vartickweek,columnnumber4] = self.df_work_auto_day.iloc[var + vartickweek - tickweek,var6 + 1 + isthereweekendcolumn]
                choosen_columnstrain =[]
                if isthereweekendcolumn == 1:
                    choosen_columnstrain.append(1)
                for columnstrain in range(self.numberoforigcolumns_day, self.df_work_auto_day.shape[1]):
                    choosen_columnstrain.append(columnstrain)
                est = GradientBoostingRegressor(n_estimators=nestimators, max_depth=maxdepth, learning_rate=learningrate)
                self.df_temp_work_day_train = self.df_work_auto_day[tickweek:var]
                self.temp_xtrain_day_train = self.df_temp_work_day_train.iloc[:, choosen_columnstrain]
                self.temp_ytrain_day_train = self.df_temp_work_day_train.iloc[:, 0]
                
                self.df_temp_work_day_predict = self.df_work_auto_day[var:var + tickday]
                self.temp_xforpredictday =  self.df_temp_work_day_predict.iloc[:, choosen_columnstrain]        
                est.fit(self.temp_xtrain_day_train,self.temp_ytrain_day_train)
                self.ypred_day = est.predict(self.temp_xforpredictday)
                
                for varpredictnum in range(0,self.ypred_day.shape[0]):
                    self.y_predictedvalues_day.append(self.ypred_day[varpredictnum])
                    self.y_originalvalues_day.append(self.df_work_auto_day.iloc[var + varpredictnum,0])
                    self.indexoriginal_predictedvalues_day.append(var + varpredictnum)
                    self.frombeforetick_predictedvalues_day.append(varpredictnum + 1)

                    
    def autopredict_day_24_48(self, tickhour, tickday, tickweek, datecolumn, weekendcolumn, fromrow, tillrow, predictcolumn, *columns):
        self.tickweek_day_24_48 = tickweek
        self.tickday_day_24_48 = tickday
        if self.istherework == 1:
            self.df_aftercalendar_day_24_48 = self.df_work
        if self.istherework == 0:
            self.df_aftercalendar_day_24_48 = self.df_original
        if self.istherecalendar == 1 and datecolumn > -1:
            a = self.df_aftercalendar_day_24_48.iloc[:, datecolumn]
            b = self.df_calendar.iloc[:, 0]
            isitholiday = self.df_calendar.iloc[:, 3]
            for var in range(0, self.df_aftercalendar_day_24_48.shape[0]):
                 if var - tickweek > 0:
                        for days in range(0, self.df_calendar.shape[0]):
                            if a[var:var + 1].item() > b[days:days + 1].item():
                                break
                            if a[var:var + 1].item() == b[days:days + 1].item() and isitholiday[days:days + 1].item() ==1 :
                                self.df_aftercalendar_day_24_48.iloc[var,:] = self.df_aftercalendar_day_24_48.iloc[var - tickweek,:] 
        choosen_columns =[]
        choosen_columns.append(predictcolumn)
        isthereweekendcolumn = 0
        if weekendcolumn > -1:
            choosen_columns.append(weekendcolumn)
            isthereweekendcolumn = 1
        for var in columns:
            choosen_columns.append(var)
        self.df_work_auto_day_24_48 = self.df_aftercalendar_day_24_48.iloc[:, choosen_columns]
        self.numberoforigcolumns_day_24_48 = self.df_work_auto_day_24_48.shape[1]
        for var in range(1 + isthereweekendcolumn, self.df_work_auto_day_24_48.shape[1]):
            number = self.df_work_auto_day_24_48.dtypes.index[var]
            numberstring = str(number) + str('_1')
            self.df_work_auto_day_24_48[numberstring] = self.df_work_auto_day_24_48.iloc[:, var]
        for var in range(1 + isthereweekendcolumn, self.numberoforigcolumns_day_24_48):
            number = self.df_work_auto_day_24_48.dtypes.index[var]
            numberstring = str(number) + str('_168')
            self.df_work_auto_day_24_48[numberstring] = self.df_work_auto_day_24_48.iloc[:, var]
        self.fromrowvalue_day_24_48 = tickweek + tickday
        self.tillrowvalue_day_24_48 = self.df_work_auto_day_24_48.shape[0]
        if fromrow > -1 and fromrow > tickweek + tickday and fromrow < self.df_work_auto_day_24_48.shape[0]:
            self.fromrowvalue_day_24_48 = fromrow
        if tillrow < self.df_work_auto_day_24_48.shape[0] and tillrow >  self.fromrowvalue_day_24_48:
            self.tillrowvalue_day_24_48 = tillrow
        self.y_predictedvalues_day_24_48 =[]
        self.y_originalvalues_day_24_48 =[]
        self.indexoriginal_predictedvalues_day_24_48 =[]
        self.frombeforetick_predictedvalues_day_24_48 =[]
        self.tickhour_day_24_48 = tickhour
        if tickhour < 1:
            self.tickhour_day_24_48 = 1
        for var in range(0, self.tillrowvalue_day_24_48):
            if (var + tickday + tickday) >= self.df_work_auto_day_24_48.shape[0]:
                break
            if var - self.fromrowvalue_day_24_48 > 0 and (var - self.fromrowvalue_day_24_48) % tickday == 0:
                for var2 in range(0, var):
                    if var2 - tickweek >= 0:
                        for var3 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                            columnnumber = var3 + self.numberoforigcolumns_day_24_48
                            self.df_work_auto_day_24_48.iloc[var2,columnnumber] = self.df_work_auto_day_24_48.iloc[var2 - 1,var3 + 1 + isthereweekendcolumn]
                        for var4 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                            columnnumber2 = var4 + self.numberoforigcolumns_day_24_48 + self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1
                            self.df_work_auto_day_24_48.iloc[var2,columnnumber2] = self.df_work_auto_day_24_48.iloc[var2 - tickweek,var4 + 1 + isthereweekendcolumn]
                for vartickweek in range(0, tickday + tickday):
                    for var5 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                        columnnumber3 = var5 + self.numberoforigcolumns_day_24_48
                        self.df_work_auto_day_24_48.iloc[var + vartickweek,columnnumber3] = self.df_work_auto_day_24_48.iloc[var - 1,var5 + 1 + isthereweekendcolumn]
                    for var6 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                        columnnumber4 = var6 + self.numberoforigcolumns_day_24_48 + self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1
                        self.df_work_auto_day_24_48.iloc[var + vartickweek,columnnumber4] = self.df_work_auto_day_24_48.iloc[var + vartickweek - tickweek,var6 + 1 + isthereweekendcolumn]
                choosen_columnstrain =[]
                if isthereweekendcolumn == 1:
                    choosen_columnstrain.append(1)
                for columnstrain in range(self.numberoforigcolumns_day_24_48, self.df_work_auto_day_24_48.shape[1]):
                    choosen_columnstrain.append(columnstrain)
                est = GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.10)
                self.df_temp_work_day_24_48_train = self.df_work_auto_day_24_48[tickweek:var]
                self.temp_xtrain_day_24_48_train = self.df_temp_work_day_24_48_train.iloc[:, choosen_columnstrain]
                self.temp_ytrain_day_24_48_train = self.df_temp_work_day_24_48_train.iloc[:, 0]
                
                self.df_temp_work_day_24_48_predict = self.df_work_auto_day_24_48[var + tickday:var + tickday + tickday]
                self.temp_xforpredictday_24_48 =  self.df_temp_work_day_24_48_predict.iloc[:, choosen_columnstrain]        
                est.fit(self.temp_xtrain_day_24_48_train,self.temp_ytrain_day_24_48_train)
                self.ypred_day_24_48 = est.predict(self.temp_xforpredictday_24_48)
                
                for varpredictnum in range(0,self.ypred_day_24_48.shape[0]):
                    self.y_predictedvalues_day_24_48.append(self.ypred_day_24_48[varpredictnum])
                    self.y_originalvalues_day_24_48.append(self.df_work_auto_day_24_48.iloc[var + varpredictnum + tickday,0])
                    self.indexoriginal_predictedvalues_day_24_48.append(var + varpredictnum + tickday)
                    self.frombeforetick_predictedvalues_day_24_48.append(varpredictnum + 1 + tickday)
   


    def manualpredict_day_24_48(self, nestimators, maxdepth, learningrate, tickhour, tickday, tickweek, datecolumn, weekendcolumn, fromrow, tillrow, predictcolumn, *columns):
        self.tickweek_day_24_48 = tickweek
        self.tickday_day_24_48 = tickday
        if self.istherework == 1:
            self.df_aftercalendar_day_24_48 = self.df_work
        if self.istherework == 0:
            self.df_aftercalendar_day_24_48 = self.df_original
        if self.istherecalendar == 1 and datecolumn > -1:
            a = self.df_aftercalendar_day_24_48.iloc[:, datecolumn]
            b = self.df_calendar.iloc[:, 0]
            isitholiday = self.df_calendar.iloc[:, 3]
            for var in range(0, self.df_aftercalendar_day_24_48.shape[0]):
                 if var - tickweek > 0:
                        for days in range(0, self.df_calendar.shape[0]):
                            if a[var:var + 1].item() > b[days:days + 1].item():
                                break
                            if a[var:var + 1].item() == b[days:days + 1].item() and isitholiday[days:days + 1].item() ==1 :
                                self.df_aftercalendar_day_24_48.iloc[var,:] = self.df_aftercalendar_day_24_48.iloc[var - tickweek,:] 
        choosen_columns =[]
        choosen_columns.append(predictcolumn)
        isthereweekendcolumn = 0
        if weekendcolumn > -1:
            choosen_columns.append(weekendcolumn)
            isthereweekendcolumn = 1
        for var in columns:
            choosen_columns.append(var)
        self.df_work_auto_day_24_48 = self.df_aftercalendar_day_24_48.iloc[:, choosen_columns]
        self.numberoforigcolumns_day_24_48 = self.df_work_auto_day_24_48.shape[1]
        for var in range(1 + isthereweekendcolumn, self.df_work_auto_day_24_48.shape[1]):
            number = self.df_work_auto_day_24_48.dtypes.index[var]
            numberstring = str(number) + str('_1')
            self.df_work_auto_day_24_48[numberstring] = self.df_work_auto_day_24_48.iloc[:, var]
        for var in range(1 + isthereweekendcolumn, self.numberoforigcolumns_day_24_48):
            number = self.df_work_auto_day_24_48.dtypes.index[var]
            numberstring = str(number) + str('_168')
            self.df_work_auto_day_24_48[numberstring] = self.df_work_auto_day_24_48.iloc[:, var]
        self.fromrowvalue_day_24_48 = tickweek + tickday
        self.tillrowvalue_day_24_48 = self.df_work_auto_day_24_48.shape[0]
        if fromrow > -1 and fromrow > tickweek + tickday and fromrow < self.df_work_auto_day_24_48.shape[0]:
            self.fromrowvalue_day_24_48 = fromrow
        if tillrow < self.df_work_auto_day_24_48.shape[0] and tillrow >  self.fromrowvalue_day_24_48:
            self.tillrowvalue_day_24_48 = tillrow
        self.y_predictedvalues_day_24_48 =[]
        self.y_originalvalues_day_24_48 =[]
        self.indexoriginal_predictedvalues_day_24_48 =[]
        self.frombeforetick_predictedvalues_day_24_48 =[]
        self.tickhour_day_24_48 = tickhour
        if tickhour < 1:
            self.tickhour_day_24_48 = 1
        for var in range(0, self.tillrowvalue_day_24_48):
            if (var + tickday + tickday) >= self.df_work_auto_day_24_48.shape[0]:
                break
            if var - self.fromrowvalue_day_24_48 > 0 and (var - self.fromrowvalue_day_24_48) % tickday == 0:
                for var2 in range(0, var):
                    if var2 - tickweek >= 0:
                        for var3 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                            columnnumber = var3 + self.numberoforigcolumns_day_24_48
                            self.df_work_auto_day_24_48.iloc[var2,columnnumber] = self.df_work_auto_day_24_48.iloc[var2 - 1,var3 + 1 + isthereweekendcolumn]
                        for var4 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                            columnnumber2 = var4 + self.numberoforigcolumns_day_24_48 + self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1
                            self.df_work_auto_day_24_48.iloc[var2,columnnumber2] = self.df_work_auto_day_24_48.iloc[var2 - tickweek,var4 + 1 + isthereweekendcolumn]
                for vartickweek in range(0, tickday + tickday):
                    for var5 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                        columnnumber3 = var5 + self.numberoforigcolumns_day_24_48
                        self.df_work_auto_day_24_48.iloc[var + vartickweek,columnnumber3] = self.df_work_auto_day_24_48.iloc[var - 1,var5 + 1 + isthereweekendcolumn]
                    for var6 in range(0, self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1):
                        columnnumber4 = var6 + self.numberoforigcolumns_day_24_48 + self.numberoforigcolumns_day_24_48 - isthereweekendcolumn - 1
                        self.df_work_auto_day_24_48.iloc[var + vartickweek,columnnumber4] = self.df_work_auto_day_24_48.iloc[var + vartickweek - tickweek,var6 + 1 + isthereweekendcolumn]
                choosen_columnstrain =[]
                if isthereweekendcolumn == 1:
                    choosen_columnstrain.append(1)
                for columnstrain in range(self.numberoforigcolumns_day_24_48, self.df_work_auto_day_24_48.shape[1]):
                    choosen_columnstrain.append(columnstrain)
                est = GradientBoostingRegressor(n_estimators=nestimators, max_depth=maxdepth, learning_rate=learningrate)
                self.df_temp_work_day_24_48_train = self.df_work_auto_day_24_48[tickweek:var]
                self.temp_xtrain_day_24_48_train = self.df_temp_work_day_24_48_train.iloc[:, choosen_columnstrain]
                self.temp_ytrain_day_24_48_train = self.df_temp_work_day_24_48_train.iloc[:, 0]
                
                self.df_temp_work_day_24_48_predict = self.df_work_auto_day_24_48[var + tickday:var + tickday + tickday]
                self.temp_xforpredictday_24_48 =  self.df_temp_work_day_24_48_predict.iloc[:, choosen_columnstrain]        
                est.fit(self.temp_xtrain_day_24_48_train,self.temp_ytrain_day_24_48_train)
                self.ypred_day_24_48 = est.predict(self.temp_xforpredictday_24_48)
                
                for varpredictnum in range(0,self.ypred_day_24_48.shape[0]):
                    self.y_predictedvalues_day_24_48.append(self.ypred_day_24_48[varpredictnum])
                    self.y_originalvalues_day_24_48.append(self.df_work_auto_day_24_48.iloc[var + varpredictnum + tickday,0])
                    self.indexoriginal_predictedvalues_day_24_48.append(var + varpredictnum + tickday)
                    self.frombeforetick_predictedvalues_day_24_48.append(varpredictnum + 1 + tickday)                    
                    

    def mape(self, y_true, y_pred):
        return numpy.mean(numpy.abs((numpy.array(y_true) - numpy.array(y_pred)) / numpy.array(y_true))) * 100
        
    def error_week(self):
        self.mae_week = []
        self.rmse_week = []
        self.mape_week = []
        self.temppredicted_weekanalyse = []
        self.temporiginal_weekanalyse = []
        for number in range(0, self.tickweek_week):
            for indexes in range(0,len(self.y_predictedvalues_week)):
                if self.frombeforetick_predictedvalues_week[indexes] == (number + 1):
                    self.temppredicted_weekanalyse.append(self.y_predictedvalues_week[indexes])
                    self.temporiginal_weekanalyse.append(self.y_originalvalues_week[indexes])
            self.mae_week.append(metrics.mean_absolute_error(self.temporiginal_weekanalyse,self.temppredicted_weekanalyse))
            self.rmse_week.append(numpy.sqrt(metrics.mean_squared_error(self.temporiginal_weekanalyse,self.temppredicted_weekanalyse)))
            self.mape_week.append(self.mape(self.temporiginal_weekanalyse,self.temppredicted_weekanalyse))
            self.temppredicted_weekanalyse = []
            self.temporiginal_weekanalyse = []
        self.df_auto_error_week = pd.DataFrame({'MAE': [self.mae_week[0]], 'MAPE': [self.mape_week[0]], 'RMSE': [self.rmse_week[0]]})
        for index in range(0, self.tickweek_week):
            self.df_auto_error_week.loc[index + 1] = [self.mae_week[index], self.mape_week[index], self.rmse_week[index]]
        print(self.df_auto_error_week)
    
    def showpredicted(self, startindex, endindex, showday, showday24_48, showweek):
        self.y_predictedvalues_all = []
        self.y_originalvalues_all = []
        self.indexoriginal_predictedvalues_all = []
        self.frombeforetick_predictedvalues_all = []
           
        for number in range(startindex, endindex + 1):
            if showweek > -1:
                for indexes in range(0,len(self.y_predictedvalues_week)):
                    if self.indexoriginal_predictedvalues_week[indexes] == number:
                        self.y_predictedvalues_all.append(self.y_predictedvalues_week[indexes])
                        self.y_originalvalues_all.append(self.y_originalvalues_week[indexes])
                        self.indexoriginal_predictedvalues_all.append(self.indexoriginal_predictedvalues_week[indexes])
                        self.frombeforetick_predictedvalues_all.append(self.frombeforetick_predictedvalues_week[indexes])
                    
            if showday > -1:
                for indexes in range(0,len(self.y_predictedvalues_day)):
                    if self.indexoriginal_predictedvalues_day[indexes] == number:
                        self.y_predictedvalues_all.append(self.y_predictedvalues_day[indexes])
                        self.y_originalvalues_all.append(self.y_originalvalues_day[indexes])
                        self.indexoriginal_predictedvalues_all.append(self.indexoriginal_predictedvalues_day[indexes])
                        self.frombeforetick_predictedvalues_all.append(self.frombeforetick_predictedvalues_day[indexes])
                        
            if showday24_48 > 1:        
                for indexes in range(0,len(self.y_predictedvalues_day_24_48)):
                    if self.indexoriginal_predictedvalues_day_24_48[indexes] == number:
                        self.y_predictedvalues_all.append(self.y_predictedvalues_day_24_48.append[indexes])
                        self.y_originalvalues_all.append(self.y_originalvalues_day_24_48[indexes])
                        self.indexoriginal_predictedvalues_all.append(self.indexoriginal_predictedvalues_day_24_48[indexes])
                        self.frombeforetick_predictedvalues_all.append(self.frombeforetick_predictedvalues_day_24_48[indexes])
                    
        self.df_selected_all = pd.DataFrame({'INDEXORIGINAL': [self.indexoriginal_predictedvalues_all[0]], 'ORIGINALVALUE': [self.y_originalvalues_all[0]], 'PREDICTEDVALUE': [self.y_predictedvalues_all[0]], 'TICKBEFOREPREDICTED': [self.frombeforetick_predictedvalues_all[0]]})
        for index in range(1, len(self.y_predictedvalues_all)):
            self.df_selected_all.loc[index] = [self.indexoriginal_predictedvalues_all[index], self.y_originalvalues_all[index], self.y_predictedvalues_all[index], self.frombeforetick_predictedvalues_all[index] ]               
        print(self.df_selected_all)    
        
        
    def predictedtocsv(self, startindex, endindex, showday, showday24_48, showweek, name):
        self.y_predictedvalues_all = []
        self.y_originalvalues_all = []
        self.indexoriginal_predictedvalues_all = []
        self.frombeforetick_predictedvalues_all = []
           
        for number in range(startindex, endindex + 1):
            if showweek > -1:
                for indexes in range(0,len(self.y_predictedvalues_week)):
                    if self.indexoriginal_predictedvalues_week[indexes] == number:
                        self.y_predictedvalues_all.append(self.y_predictedvalues_week[indexes])
                        self.y_originalvalues_all.append(self.y_originalvalues_week[indexes])
                        self.indexoriginal_predictedvalues_all.append(self.indexoriginal_predictedvalues_week[indexes])
                        self.frombeforetick_predictedvalues_all.append(self.frombeforetick_predictedvalues_week[indexes])
            
            if showday > -1:
                for indexes in range(0,len(self.y_predictedvalues_day)):
                    if self.indexoriginal_predictedvalues_day[indexes] == number:
                        self.y_predictedvalues_all.append(self.y_predictedvalues_day[indexes])
                        self.y_originalvalues_all.append(self.y_originalvalues_day[indexes])
                        self.indexoriginal_predictedvalues_all.append(self.indexoriginal_predictedvalues_day[indexes])
                        self.frombeforetick_predictedvalues_all.append(self.frombeforetick_predictedvalues_day[indexes])
                        
            if showday24_48 > 1:        
                for indexes in range(0,len(self.y_predictedvalues_day_24_48)):
                    if self.indexoriginal_predictedvalues_day_24_48[indexes] == number:
                        self.y_predictedvalues_all.append(self.y_predictedvalues_day_24_48.append[indexes])
                        self.y_originalvalues_all.append(self.y_originalvalues_day_24_48[indexes])
                        self.indexoriginal_predictedvalues_all.append(self.indexoriginal_predictedvalues_day_24_48[indexes])
                        self.frombeforetick_predictedvalues_all.append(self.frombeforetick_predictedvalues_day_24_48[indexes])
                    
        self.df_selected_all = pd.DataFrame({'INDEXORIGINAL': [self.indexoriginal_predictedvalues_all[0]], 'ORIGINALVALUE': [self.y_originalvalues_all[0]], 'PREDICTEDVALUE': [self.y_predictedvalues_all[0]], 'TICKBEFOREPREDICTED': [self.frombeforetick_predictedvalues_all[0]]})
        for index in range(1, len(self.y_predictedvalues_all)):
            self.df_selected_all.loc[index] = [self.indexoriginal_predictedvalues_all[index], self.y_originalvalues_all[index], self.y_predictedvalues_all[index], self.frombeforetick_predictedvalues_all[index] ]               
        self.df_selected_all.to_csv(name,index=False,header=True)    

    def error_day(self):
        self.mae_day = []
        self.rmse_day = []
        self.mape_day = []
        self.temppredicted_dayanalyse = []
        self.temporiginal_dayanalyse = []
        for number in range(0, self.tickday_day):
            for indexes in range(0,len(self.y_predictedvalues_day)):
                if self.frombeforetick_predictedvalues_day[indexes] == (number + 1):
                    self.temppredicted_dayanalyse.append(self.y_predictedvalues_day[indexes])
                    self.temporiginal_dayanalyse.append(self.y_originalvalues_day[indexes])
            self.mae_day.append(metrics.mean_absolute_error(self.temporiginal_dayanalyse,self.temppredicted_dayanalyse))
            self.rmse_day.append(numpy.sqrt(metrics.mean_squared_error(self.temporiginal_dayanalyse,self.temppredicted_dayanalyse)))
            self.mape_day.append(self.mape(self.temporiginal_dayanalyse,self.temppredicted_dayanalyse))
            self.temppredicted_dayanalyse = []
            self.temporiginal_dayanalyse = []
        self.df_auto_error_day = pd.DataFrame({'MAE': [self.mae_day[0]], 'MAPE': [self.mape_day[0]], 'RMSE': [self.rmse_day[0]]})
        for index in range(0, self.tickday_day):
            self.df_auto_error_day.loc[index + 1] = [self.mae_day[index], self.mape_day[index], self.rmse_day[index]]
        print(self.df_auto_error_day)
            
            
    def error_day_24_48(self):
        self.mae_day_24_48 = []
        self.rmse_day_24_48 = []
        self.mape_day_24_48 = []
        self.temppredicted_day_24_48_analyse = []
        self.temporiginal_day_24_48_analyse = []
        for number in range(self.tickday_day_24_48, self.tickday_day_24_48 + self.tickday_day_24_48):
            for indexes in range(0,len(self.y_predictedvalues_day_24_48)):
                if self.frombeforetick_predictedvalues_day_24_48[indexes] == (number + 1):
                    self.temppredicted_day_24_48_analyse.append(self.y_predictedvalues_day_24_48[indexes])
                    self.temporiginal_day_24_48_analyse.append(self.y_originalvalues_day_24_48[indexes])
            self.mae_day_24_48.append(metrics.mean_absolute_error(self.temporiginal_day_24_48_analyse,self.temppredicted_day_24_48_analyse))
            self.rmse_day_24_48.append(numpy.sqrt(metrics.mean_squared_error(self.temporiginal_day_24_48_analyse,self.temppredicted_day_24_48_analyse)))
            self.mape_day_24_48.append(self.mape(self.temporiginal_day_24_48_analyse,self.temppredicted_day_24_48_analyse))
            self.temppredicted_day_24_48_analyse = []
            self.temporiginal_day_24_48_analyse = []
        self.df_auto_error_day_24_48 = pd.DataFrame({'MAE': [self.mae_day_24_48[0]], 'MAPE': [self.mape_day_24_48[0]], 'RMSE': [self.rmse_day_24_48[0]]})
        for index in range(0, self.tickday_day_24_48):
            self.df_auto_error_day_24_48.loc[index + 1] = [0, 0, 0]
        for index in range(0, self.tickday_day_24_48):
            self.df_auto_error_day_24_48.loc[self.tickday_day_24_48 + index + 1] = [self.mae_day_24_48[index], self.mape_day_24_48[index], self.rmse_day_24_48[index]]
        print(self.df_auto_error_day_24_48)
            
    def error_all(self, showday, showday24_48, showweek):
        self.mae_all = []
        self.rmse_all = []
        self.mape_all = []
        self.temppredicted_allanalyse = []
        self.temporiginal_allanalyse = []
        for number in range(0, self.tickweek_week):
            if showweek > -1:
                for indexes in range(0,self.y_predictedvalues_week.shape[0]):
                    if self.frombeforetick_predictedvalues_week[indexes] == (number + 1):
                        self.temppredicted_allanalyse.append(self.y_predictedvalues_week[indexes])
                        self.temporiginal_allanalyse.append(self.y_originalvalues_week[indexes])
                        
            if showday > -1:        
                for indexes in range(0,self.y_predictedvalues_day.shape[0]):
                    if self.frombeforetick_predictedvalues_day[indexes] == (number + 1):
                        self.temppredicted_allanalyse.append(self.y_predictedvalues_day[indexes])
                        self.temporiginal_allanalyse.append(self.y_originalvalues_day[indexes]) 
                        
            if showday24_48 > -1:       
                for indexes in range(0,self.y_predictedvalues_day_24_48.shape[0]):
                    if self.frombeforetick_predictedvalues_day_24_48[indexes] == (number + 1):
                        self.temppredicted_allanalyse.append(self.y_predictedvalues_day_24_48[indexes])
                        self.temporiginal_allanalyse.append(self.y_originalvalues_day_24_48[indexes])  
                    
            self.mae_all.append(metrics.mean_absolute_error(self.temporiginal_allanalyse,self.temppredicted_allanalyse))
            self.rmse_all.append(numpy.sqrt(metrics.mean_squared_error(self.temporiginal_allanalyse,self.temppredicted_allanalyse)))
            self.mape_all.append(self.mape(self.temporiginal_allanalyse,self.temppredicted_allanalyse))
            self.temppredicted_allanalyse = []
            self.temporiginal_allanalyse = []
        self.df_auto_error_all = pd.DataFrame({'MAE': [self.mae_all[0]], 'MAPE': [self.mape_all[0]], 'RMSE': [self.rmse_all[0]]})
        for index in range(0, self.tickweek_week):
            self.df_auto_error_all.loc[index + 1] = [self.mae_all[index], self.mape_all[index], self.rmse_all[index]] 
            print(self.df_auto_error_all)
                
                

    def draw_plot_error_all(self, showmae, showrmse, showmape, name):
        temp_df_auto_error_all = self.df_auto_error_all[1:self.tickweek_week + 1]
        fig, axes = plt.subplots(figsize=(20, 8))
        if showmae > -1:
            temp_df_auto_error_all['MAE'].plot(color='blue', label='MAE')
        if showrmse > -1:
            temp_df_auto_error_all['RMSE'].plot(color='green', label='RMSE')
        if showmape > -1:
            temp_df_auto_error_all['MAPE'].plot(color='brown', label='MAPE')
            
        plt.legend(loc='best')
        plt.show()
        fig.savefig(name)                
 


    def draw_plot_error_week(self, showmae, showrmse, showmape, name):
        temp_df_auto_error_week = self.df_auto_error_week[1:self.tickweek_week + 1]
        fig, axes = plt.subplots(figsize=(20, 8))
        if showmae > -1:
            temp_df_auto_error_week['MAE'].plot(color='blue', label='MAE')
        if showrmse > -1:
            temp_df_auto_error_week['RMSE'].plot(color='green', label='RMSE')
        if showmape > -1:
            temp_df_auto_error_week['MAPE'].plot(color='brown', label='MAPE')
            
        plt.legend(loc='best')
        plt.show()
        fig.savefig(name)
        
    def draw_plot_error_day(self, showmae, showrmse, showmape, name):
        temp_df_auto_error_day = self.df_auto_error_day[1:self.tickday_day + 1]
        fig, axes = plt.subplots(figsize=(20, 8))
        if showmae > -1:
            temp_df_auto_error_day['MAE'].plot(color='blue', label='MAE')
        if showrmse > -1:
            temp_df_auto_error_day['RMSE'].plot(color='green', label='RMSE')
        if showmape > -1:
            temp_df_auto_error_day['MAPE'].plot(color='brown', label='MAPE')
            
        plt.legend(loc='best')
        plt.show()
        fig.savefig(name)
        
        
    def draw_plot_error_day_24_48(self, showmae, showrmse, showmape, name):
        temp_df_auto_error_day_24_48 = self.df_auto_error_day_24_48[self.tickday_day_24_48 + 1:self.tickday_day_24_48 + self.tickday_day_24_48 + 1]
        fig, axes = plt.subplots(figsize=(20, 8))
        if showmae > -1:
            temp_df_auto_error_day_24_48['MAE'].plot(color='blue', label='MAE')
        if showrmse > -1:
            temp_df_auto_error_day_24_48['RMSE'].plot(color='green', label='RMSE')
        if showmape > -1:
            temp_df_auto_error_day_24_48['MAPE'].plot(color='brown', label='MAPE')
            
        plt.legend(loc='best')
        plt.show()
        fig.savefig(name)

        
        
