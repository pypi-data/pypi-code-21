import os
import sys

# from .PlayCricket import *
# from teams import Match

from crickit.PlayCricket import *

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


class matchSimulator(Match):
    def __init__(self):
        self.t1_wins = 0
        self.t2_wins = 0
        self.ties = 0

def memManage():
    India = None
    Pakistan = None

def simulateMatches(teamOne, teamTwo, n = 100):
    simulateCount = n
    simulatedMatch = matchSimulator()
    for i in range(simulateCount):
        thewinner = playMatch(teamOne, teamTwo)
        # print(thewinner)
        # winner = thewinner.name
        if thewinner == "draw":
            simulatedMatch.ties +=1
        elif thewinner.name == teamOne:
            simulatedMatch.t1_wins +=1
        elif thewinner.name == teamTwo:
            simulatedMatch.t2_wins +=1
        # prntstr =
        print("\rMatches Played.:{} | {} won: {} | {} won:{} Matches Tied: {}".format(i, teamOne, simulatedMatch.t1_wins, teamTwo, simulatedMatch.t2_wins, simulatedMatch.ties), flush=True, end='')
    # printSummary(MATCH_ID)

def printSummary(MATCH_ID):
    teamOne = MATCH_ID.battingOrder[0]
    teamTwo = MATCH_ID.battingOrder[1]
    print("\n{} won {} matches, {} won {} matches and {} matches were tied".format(teamOne, MATCH_ID.t1_wins, teamTwo, MATCH_ID.t2_wins, MATCH_ID.ties))

if __name__ == "__main__":

    theMatchID = simulateMatches("India", "Pakistan", 10)
    print("\n")

