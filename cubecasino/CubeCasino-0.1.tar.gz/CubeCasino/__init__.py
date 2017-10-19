from pycube256 import CubeRandom

class CubeRoulette:
    def __init__(self):
        self.wheel = [0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26]
        self.colors = {0:"Green",32:"Red",15:"Black",19:"Red",4:"Black",21:"Red",2:"Black",25:"Red",17:"Black",34:"Red",6:"Black",27:"Red",13:"Black",36:"Red",11:"Black",30:"Red",8:"Black",23:"Red",10:"Black",5:"Red",24:"Black",16:"Red",33:"Black",1:"Red",20:"Black",14:"Red",31:"Black",9:"Red",22:"Black",18:"Red",29:"Black",7:"Red",28:"Black",12:"Red",35:"Black",3:"Red",26:"Black"}

    def spin_wheel(self):
        pocket = CubeRandom().choice(self.wheel)
        return pocket, self.colors[pocket]

class CubeDice:
    def __init__(self, sides=6):
        self.sides = sides
        self.min = 1

    def roll(self):
        return CubeRandom().randint(self.min,self.sides)

class CubeCoins:
    def __init__(self, coins=1):
        self.sides = ['Heads','Tails']
        self.coins = coins

    def flip(self):
        return CubeRandom().choice(self.sides)

class CubeBingo:
    def __init__(self):
        self.name = "BINGO"
        self.numbers = 75
        self.card_rows = 5
        self.card_columns = 5
        self.gen_pool()

    def gen_pool(self):
        self.pool = []
        for x in range(1,self.numbers+1):
            self.pool.append(x)

    def draw(self):
        choice = CubeRandom().choice(self.pool)
        return self.pool.pop(self.pool.index(choice))

    def gen_cards(self, num=1):
        cards = []
        card_size = self.card_rows * self.card_columns
        for card in range(num):
            card = {}
            for column in range(1,self.card_columns+1):
                col = {}
                for row in range(1,self.card_rows+1):
                    if column == 3 and row == 3:
                        col[row] = "Free"
                    else:
                        col[row] = self.pool.pop(self.pool.index(CubeRandom().choice(self.pool)))
                card[column] = col
            cards.append(card)
            self.gen_pool()
        return cards

class CubeCards:
    def __init__(self, decks=1):
        self.decks = decks
        self.cards = { 'AH':11, '2H':2, '3H':3, '4H':4, '5H':5,'6H':6, '7H':7, '8H':8, '9H':9, '10H':10, 'JH':10, 'QH':10, 'KH':10, 'AD':11, '2D':2, '3D':3, '4D':4, '5D':5,'6D':6, '7D':7, '8D':8, '9D':9, '10D':10, 'JD':10, 'QD':10, 'KD':10, 'AS':11, '2S':2, '3S':3, '4S':4, '5S':5,'6S':6, '7S':7, '8S':8, '9S':9, '10S':10, 'JS':10, 'QS':10, 'KS':10, 'AC':11, '2C':2, '3C':3, '4C':4, '5C':5,'6C':6, '7C':7, '8C':8, '9C':9, '10C':10, 'JC':10, 'QC':10, 'KC':10 }
        self.deck = []
        self.reload_deck()

    def reload_deck(self):
        for x in range(self.decks):
            for key in self.cards.keys():
                self.deck.append(key)
        self.shuffle()

    def draw(self, num=1):
        cards = []
        for x in range(num):
            if len(self.deck) == 0:
                self.reload_deck()
            cards.append(self.deck.pop(self.deck.index(CubeRandom().choice(self.deck))))
        return cards

    def shuffle(self, times=1):
        for x in range(times):
            deck = []
            for x in range(len(self.deck)):
                deck.append(self.deck.pop(self.deck.index(CubeRandom().choice(self.deck))))
            self.deck = list(deck)

class CubeKeno:
    def __init__(self, numbers=80):
        self.pool = []
        for x in range(1,numbers+1):
            self.pool.append(x)

    def picks(self, num=20):
        p = []
        for x in range(num):
            p.append(self.pool.pop(self.pool.index(CubeRandom().choice(self.pool))))
        return p

    def pick(self):
        return self.pool.pop(self.pool.index(CubeRandom().choice(self.pool)))

class CubePowerball:
    def __init__(self, num_red=26, num_white=69):
        self.num_reds = 1
        self.num_whites = 5
        self.red_balls = []
        self.white_balls = []
        for x in range(1,num_red+1):
            self.red_balls.append(x)
        for x in range(1,num_white+1):
            self.white_balls.append(x)

    def picks(self):
        whites = []
        reds = []
        for x in range(self.num_whites):
            whites.append(self.white_balls.pop(self.white_balls.index(CubeRandom().choice(self.white_balls))))
        for x in range(self.num_reds):
            reds.append(self.red_balls.pop(self.red_balls.index(CubeRandom().choice(self.red_balls))))
        return whites, reds
