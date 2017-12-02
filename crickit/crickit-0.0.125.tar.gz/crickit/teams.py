# The Teams class
class Teams:
    #empty list to store all
    # listTeams = []
    # allInit = []

    def resetTeam(self):
        self.runScore = 0
        self.overCount = 0
        self.ballCountPerOver =0

    def addRuns(self, runs=1):
        self.runScore += runs

    def resetRuns(self):
        self.runScore = 0

    def plusInningsOverCount(self):
        # if self.overCount < 20:
        self.overCount +=1
        # else:
        #     self.overCount =20

    def resetBowlingInnings(self):
        self.overCount = 0
        self.resetBallCountPerOver()

    def resetBattingInnings(self):
        self.wicketCount = 0
        self.resetRuns()
        self.playedOvers = 0

    def boldOut(self):
        self.wicketCount +=1

    def plusBallCountPerOver(self):
        self.ballCountPerOver +=1

    def resetBallCountPerOver(self):
        self.ballCountPerOver = 0

    def __init__ (self, **stats):
        self.__dict__.update(stats)
        self.ballTypes = ['wideBall'] * int(self.wideBall*100) + ["noBall"]*(int(self.noBall*100)) + ['wicketBall']*int((self.wicketBall*100)) + ['regularBall']*int((self.regularBall*100))
        self.overCount = 0
        self.playCall = "Bat"
        # Teams.listTeams.append(self)
        # Teams.allInit.append(self)

    def __repr__(self):
        return self.name


class Match:
    def __init__(self, matchID):
        self.matchID = matchID
        self.tossWinningTeam = []
        self.callingTeam = []
        self.tossResult = []
        self.battingOrder = []
        self.bowlingOrder = []
        self.playingTeams = []
        self.winningScore = 0
        self.InningsWinner = []
        self.InningsLoser = []
        self.winningTeamRuns = 0
        self.winningTeamWickets = 0
        self.losingTeamRuns = 0
        self.losingTeamWickets = 0
        self.runScoreDelta = 0
        self.wicketDelta = 0
        self.coinCalledByCallingTeam = ""

    def __repr__(self):
        return self.matchID

    def resetMatch(self):
        self.tossWinningTeam = []
        self.callingTeam = []
        self.tossResult = []
        self.battingOrder = []
        self.bowlingOrder = []
        self.winningScore = 0
        self.InningsWinner = []
        self.InningsLoser = []
        self.winningTeamRuns = 0
        self.winningTeamWickets = 0
        self.losingTeamRuns = 0
        self.losingTeamWickets = 0
        self.runScoreDelta = 0
        self.wicketDelta = 0
        self.coinCalledByCallingTeam = ""

    def matchSummary(self):
        print("{} called {}, won the toss and decided to bat. {} won against {} by {} runs and {} wickets in {} overs".format(
            self.callingTeam, self.coinCalledByCallingTeam, self.InningsWinner, self.InningsLoser, self.runScoreDelta, self.wicketDelta, "TODO"))


# India = Teams(**INDIA)
# Pakistan = Teams(**PAKISTAN)
# Zimbabwe = Teams(**ZIMBABWE)