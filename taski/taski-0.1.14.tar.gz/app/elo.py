import random
import math
import util


orig_sorted = sorted

random.seed()
K = 16

# what is the expectation of Ra wins Rb
def expected(ra, rb):
    return 1.0 / (1 + math.pow(10, float(rb - ra)/400))

# Ra' = Ra + K(Sa - Ea)
# Ra is A's score
# Rb is B's score
# Sa (win: 1, draw: 0.5, lose: 0)
def win(ra, rb):
    ra = ra + K * (1 - expected(ra, rb))
    return ra

def draw(ra, rb):
    ra = ra + K * (0.5 - expected(ra, rb))
    return ra

def lose(ra, rb):
    ra = ra + K * (0 - expected(ra, rb))
    return ra

def natual_cmp(a, b):
    if a < b:
        return 1
    elif a == b:
        return 0
    else:
        return -1

def terminal_cmp(a, b):
    question = util.red('Which one wins? (0: draw, 1: 1 wins, 2: 2 wins)') + '\n1. %s\n2. %s\n[0/1/2]:'
    while True:
        try:
            item1 = util.green(str(a))
            item2 = util.cyan(str(b))
            r = input(question % (item1, item2))
            r = int(r)
        except (SyntaxError, NameError) as e:
            print(e)
            continue
        if r not in [0, 1, 2]:
            print("Invalid answer: %s\n" % r)
        if r == 1:
            # return something that is smaller thatn 0
            r = -r
        return r


def match(player1, player2, cmp=natual_cmp):
    r = cmp(player1, player2)

    if r == 0:
        player1["score"] = draw(player1["score"], player2["score"])
        player2["score"] = draw(player2["score"], player1["score"])
    elif r < 0:
        player1["score"] = win(player1["score"], player2["score"])
        player2["score"] = lose(player2["score"], player1["score"])
    elif r > 0:
        player1["score"] = lose(player1["score"], player2["score"])
        player2["score"] = win(player2["score"], player1["score"])

def sort(items, cmp=terminal_cmp):
    length = len(items)
    n = length
    if n < 2:
        return items

    array = []
    for item in items:
        bucket = { "score": 0, "item": item }
        array.append(bucket)

    for i in range(n):
        player1 = random.choice(array)
        player2 = random.choice(array)
        while player1 == player2:
            player2 = random.choice(array)
        match(player1, player2, cmp=cmp)

    array = sorted(array, key=lambda x: x["score"], reverse=True)

    res = []
    for bucket in array:
        res.append(bucket["item"])

    return res

def sorted(iterable, cmp=None, key=None, reverse=False, rounds=None):
    global orig_sorted
    if cmp == None:
        cmp = natual_cmp

    length = len(iterable)
    n = length
    if n < 2:
        return iterable

    if rounds is None:
        rounds = n

    array = []
    for item in iterable:
        bucket = { "score": 0, "item": item }
        array.append(bucket)

    for i in xrange(rounds):
        player1 = random.choice(array)
        player2 = random.choice(array)
        while player1 == player2:
            player2 = random.choice(array)
        match(player1, player2, cmp=cmp)

    print(array)
    array = orig_sorted(array, key=lambda x: x["score"], reverse=reverse)
    print(array)

    res = []
    for bucket in array:
        res.append(bucket["item"])

    return res

