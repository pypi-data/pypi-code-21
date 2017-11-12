import pandas as pd

class Rollingpredict:

    def __init__(self, path):
        self.full_path = path
        
    def show_originalpath(self):
        print(self.full_path)

    def read_originalfile(self):
        self.df_original = pd.read_csv(self.full_path)
    
    def show_originalfile(self):
        print(self.df_original)
        
    def select_numcolumns(self, *columns):
        choosen_values = []
        for var in columns:
            choosen_values.append(var)
        self.df_work = self.df_original.iloc[:, choosen_values]
        
        
    def select_textcolumns(self, *columnstext):
        choosen_values = []
        for var in columnstext:
            choosen_values.append(var)
        self.df_work = self.df_original[choosen_values]