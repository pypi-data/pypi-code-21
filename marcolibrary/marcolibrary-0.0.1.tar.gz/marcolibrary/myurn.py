import random


def prova():
    data = range(1,11)
    import random
    #random.shuffle(data)
    print data


    import random
    result = []


    for x in range (0, 10):
        num = random.randint(0, 10)
        while num in result:
            num = random.randint(0, 10)
        result.append(num)
    print result
