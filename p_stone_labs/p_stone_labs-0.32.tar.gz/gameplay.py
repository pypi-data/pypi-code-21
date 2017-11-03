from os import system
from random import randint
from gtts import gTTS
import os
import datetime as dt
import pandas as pd
import time

def saySomething (whatToSay, visualOrAudio):
    if visualOrAudio == "audio":
        tts = gTTS(text=whatToSay, lang='en')
        tts.save("x.mp3")
        os.system("mpg321 -q x.mp3")
    else:
        print (whatToSay)

class GamePlay:
    playerName = ""
    guessCount = 0
    answer = 0
    solved = False
    maxNumber = 0
    mode = "visual"
    startOfPlay = pd.to_datetime(dt.datetime.now())
    endOfPlay = -1

    def __init__(self, pName, max_number, inmode):
        self.playerName = pName
        self.maxNumber = max_number
        self.answer = randint(1, self.maxNumber)
        self.mode = inmode

    def guess (self, aGuess) :

        self.guessCount += 1
        if self.answer < aGuess:
            saySomething ("Lower", self.mode)
        elif self.answer > aGuess:
            saySomething ("Higher", self.mode)
        else:
            saySomething ("Solved in %d guesses." % self.guessCount, self.mode)
            saySomething ("Congratulations " + self.playerName, self.mode)
            self.endOfPlay = dt.datetime.now()
            saySomething ("Time to solve was " + str(self.endOfPlay - self.startOfPlay) + " seconds", self.mode)
            self.solved = True

    def printGame (self):
        print ("Player Name: " + self.playerName)
        print ("Maximum Number: " + str(self.maxNumber))
        print ("Answer: " + str(self.answer))
        print ("Guesses: " + str(self.guessCount))
        print ("Start of Play: " + str(self.startOfPlay))
        print ("End of Play: " + str(self.endOfPlay))