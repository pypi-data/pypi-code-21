from os import system
from random import randint
from gtts import gTTS
import os
import datetime as dt
import pandas as pd
import gameplay as gameplay
import leaderboard as lb

def saySomething (whatToSay, visualOrAudio):
    if visualOrAudio == "audio":
        tts = gTTS(text=whatToSay, lang='en')
        tts.save("x.mp3")
        os.system("mpg321 -q x.mp3")
    else:
        print (whatToSay)

name = raw_input ("Enter your name: ")
max_number = int(raw_input("Enter a maximum number for the game: "))
response = raw_input("Select (V)isual or (A)udio: ")
if response == "V":
    mode = "visual"
else:
    mode = "audio"

game = gameplay.GamePlay (name, max_number, mode)

first_line = "Guess a number between 1 and %d" % max_number
saySomething (first_line, mode)

#keep looping unil we guess correctly
while (not game.solved):
    this_guess = input('?')
    game.guess(this_guess)

print ("You solved the puzzle in %d guesses." % game.guessCount)

board = lb.Leaderboard()
board.addGame (game)
board.printleaderboard()
