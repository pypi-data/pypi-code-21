from os import system
from random import randint
from gtts import gTTS
import os
import datetime as dt
import pandas as pd
import gameplay as gameplay

class Leaderboard:

    df = pd.DataFrame()

    def __init__ (self) :
        self.df = pd.read_csv("leaderboard.csv")
        self.df.StartOfPlay = pd.to_datetime(self.df.StartOfPlay) #, format="%d/%m/%Y")
        self.df.EndOfPlay = pd.to_datetime(self.df.EndOfPlay) #, format="%d/%m/%Y")

    def addGame (self, gameToAdd):
        #print (self.df)
        #gameToAdd.printGame()
        self.df.loc[len(self.df) + 1] = [len(self.df)+1,gameToAdd.playerName,gameToAdd.maxNumber,gameToAdd.answer,gameToAdd.guessCount,gameToAdd.startOfPlay,gameToAdd.endOfPlay]

        pd.DataFrame.to_csv(self.df, "leaderboard.csv", index=False)

    def printleaderboard (self):
       # pd.options.display.datetime_format.
        self.df.StartOfPlay = str(self.df.StartOfPlay)[4:15]
        print ("------------------------------------------------------------")
        print ("                    Leader Board");
        print ("------------------------------------------------------------")
        print(self.df.sort_values(by=['Guesses'])[['PlayerName', 'Answer', 'Guesses', 'MaxNumber', 'StartOfPlay', 'EndOfPlay']])
